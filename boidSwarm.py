from boidBaseObject import BoidBaseObject

import boidAttributes
from boidTools import util

import boidVector.vector3 as bv3
import boidTools.zoneGraph as bzg
import boidAgent as ba
import boidBehaviour.classicBoid as bbc
import boidBehaviour.goalDriven as bbg
import boidBehaviour.followPath as bbf

from boidBehaviour.behaviourBaseObject import BoidBehaviourDelegate
from boidBehaviour.goalDriven import agentBehaviourIsGoalDriven,\
agentIsInBasePyramid, agentIsChasingGoal



class BoidSwarm(BoidBaseObject, BoidBehaviourDelegate):
    """Main external interface to the boid system, basically the managing object for a group of boidAgents.  
    Contains top-level logic (i.e. iterating over agents each frame & executing behaviour) and
    also manages interaction with the actual Pymel objects within Maya.
    """
    
    def __init__(self, particleShapeNode, negativeIndicesCornerLocator, positiveIndicesCornerLocator):
        self._particleShapeNode = particleShapeNode
        self._particleIdsOrdering = []
        self._boidAgentList = {}
        self._zoneGraph = bzg.ZoneGraph(negativeIndicesCornerLocator, positiveIndicesCornerLocator)        
        
        self._normalBehaviour = bbc.ClassicBoid(self._zoneGraph.lowerBoundsVector, self._zoneGraph.upperBoundsVector)
        self._priorityGoalBehaviour = None   # 
        self._secondaryGoalBehaviour = None  # boidBehaviourGoalDriven instances
        self._curvePathBehaviour = None  # boidBehaviourFollowPath instance
        
        self._buildParticleList()

#############################
    def __str__(self):
        length = len(self._boidAgentList)
        if(length > 0):
            ret = "nodeName=%s, %d particles:" % (self._particleShapeNode.name(), length)
            for boid in sorted(self._boidAgentList.itervalues()):
                ret += "\n\t" + boid.__str__()
            return ret
        else:
            return "empty"


#############################
    def metaStr(self):
        ret = ""
        for agent in sorted(self._boidAgentList.itervalues()):
            ret += '\t' + agent.metaStr() + '\n'
        return ret

#############################    
    def zoneStr(self):
        return self._zoneGraph.__str__()

#############################    
    def _getAgentList(self):
        """Returns sorted list of boid agents, not too efficient - mainly for debug/console use."""
        return sorted(self._boidAgentList.values())
    agentList = property(_getAgentList)
    
    def agent(self, particleId):
        return self._boidAgentList[particleId]

############################# 
    def _getParticleShapeName(self):
        return self._particleShapeNode.name()
    particleShapeName = property(_getParticleShapeName)
    
#############################
    def _buildParticleList(self, fullRebuild = True):
        """Builds/rebuilds the list of boidAgents based on the current state
        of the corresponding nParticleShapeNode."""
        
        lowerBounds = self._zoneGraph.lowerBoundsVector
        upperBounds = self._zoneGraph.upperBoundsVector
        
        
        if(fullRebuild):
            self._boidAgentList.clear()
            
            if(self._particleShapeNode.getCount() > 0):
                #particle IDs are NOT guaranteed to come in numerical order => have to use this list as reference
                self._particleIdsOrdering = util.getParticleIdsList(self.particleShapeName)             
                if(self._particleIdsOrdering  != None):
                    for ptclId in self._particleIdsOrdering:
                        newAgent = ba.BoidAgent(int(ptclId), self._normalBehaviour, lowerBounds, upperBounds)
                        self._boidAgentList[newAgent.particleId] = newAgent
        else:
            numParticles = self._particleShapeNode.getCount()
            
            if(numParticles > len(self._boidAgentList)):
                # add newly created particles to the list of agents
                self._particleIdsOrdering = util.getParticleIdsList(self.particleShapeName)
                
                sortedIdsList = sorted(self._particleIdsOrdering)
                keysList = sorted(self._boidAgentList.keys())
                numKeys = len(keysList)
                lastKey = keysList[numKeys-1] if numKeys > 0 else -1
                newAgentsList = []
                
                for ptclId in reversed(sortedIdsList):
                    if(ptclId > lastKey):
                        newAgent = ba.BoidAgent(int(ptclId), self._normalBehaviour, lowerBounds, upperBounds)
                        self._boidAgentList[newAgent.particleId] = newAgent   
                        newAgentsList.append(newAgent)
                    else:
                        break
                    
                self.onNewBoidsCreated(newAgentsList)
                
            elif(numParticles < len(self._boidAgentList)):
                # remove recently deleted particles from the list of agents
                self._particleIdsOrdering = util.getParticleIdsList(self.particleShapeName)
                particleSet = set(self._particleIdsOrdering)
                boidAgentSet = set(self._boidAgentList.keys())
                
                for particleId in boidAgentSet.difference(particleSet):
                    del self._boidAgentList[particleId]
            else:
                print("XXXXX WARNING - PARTIAL REBUILD WITH NO DIFFERENCE IN PARTICLE COUNT")

                    
#############################                     
    def _killSingleParticle(self, particleId):
        """IMPORTANT - WILL NOT TAKE EFEECT UNTIL AFTER NEXT FRAME UPDATE"""
        if(particleId in self._boidAgentList):
            util.killParticle(self.particleShapeName, particleId)
        

#############################            
    def _getSingleParticleInfo(self, particleId):            
        position =  util.getSingleParticlePosition(self.particleShapeName, particleId) 
        velocity =  util.getSingleParticleVelocity(self.particleShapeName, particleId) 
        agent = self._boidAgentList[particleId]
        
        agent.updateCurrentVectors(bv3.Vector3(position[0], position[1], position[2]), 
                                   bv3.Vector3(velocity[0], velocity[1], velocity[2]))
        if(agentBehaviourIsGoalDriven(agent)):
            agent._currentBehaviour.checkAgentLocation(agent)
        self._zoneGraph.updateAgentPosition(agent)
 
#############################
    def setStickiness(self, particleId, value):
        self._boidAgentList[particleId].stickinessScale = value
        util.setStickinessScale(self.particleShapeName, particleId, value) # do this right now - otherwise will wait until next frame update

#############################
    def fullUpdate(self):       
        """Performs one full iteration of updating all boidAgent behaviour.
        Should be called from Maya once per frame update."""
        
        self._resetHelperObjects()
        self._getAllParticlesInfo()
        self._calculateBoidsBehaviour()
        self._updateAllParticles()

#############################
    def _resetHelperObjects(self):
        self._zoneGraph.resetZones()
        
        if(self._priorityGoalBehaviour != None):
            self._priorityGoalBehaviour.resetAverages()
            
        if(self._secondaryGoalBehaviour != None):
            self._secondaryGoalBehaviour.resetAverages()
            
        if(self._curvePathBehaviour != None):
            self._curvePathBehaviour.recheckCurvePoints()

#############################
    def _getAllParticlesInfo(self, queryExtraInfo = False):
        """Updates all boidAgent instances with position, velocity and derived
        information from their corresponding Maya-side particle instances."""
        
        numParticles = self._particleShapeNode.getCount()
        if(numParticles == 0):
            self._buildParticleList(True)
        elif(numParticles != len(self._boidAgentList)):
            self._buildParticleList(False)
        #elif(numParticles < len(self._boidAgentList)):
            #print("XXXXXXXXXX WARNING - MISSING PARTICLES IN LIST!!!, REBUILDING FROM SCRATCH... XXXXX")
            #self._buildParticleList(True)
        
        if(numParticles > 0):
            positions = util.getParticlePositionsList(self.particleShapeName)
            velocities = util.getParticleVelocitiesList(self.particleShapeName)
            
            if(len(positions) < numParticles * 3):
                #repeated call here because of shitty Maya bug whereby sometimes only get first item in request for goalsU...
                positions = util.getParticlePositionsList(self.particleShapeName) 
    
            for i in range(0, numParticles):
                j = i * 3
                particleId = self._particleIdsOrdering[i]
                agent = self._boidAgentList[particleId]
                
                agent.updateCurrentVectors(bv3.Vector3(positions[j], positions[j+1], positions[j+2]),
                                           bv3.Vector3(velocities[j], velocities[j+1], velocities[j+2]))
                if(agentBehaviourIsGoalDriven(agent)):
                    agent._currentBehaviour.checkAgentLocation(agent)
                self._zoneGraph.updateAgentPosition(agent)
                
            if(queryExtraInfo):
                self._queryExtraInfo()

#############################
    def _queryExtraInfo(self):
        stickinessScales = util.getStickinessScalesList(self.particleShapeName)
        for i in range(0, len(stickinessScales)):
            particleId = self._particleIdsOrdering[i]
            self._boidAgentList[particleId]._stickinessScale = stickinessScales[i]

#############################
    def _calculateBoidsBehaviour(self):     
        """Iterates through all agents & calculates desired behaviour based on boids rules."""
           
        for agent in self._boidAgentList.itervalues():
            regionList = self._zoneGraph.regionListForAgent(agent)
            agent.updateBehaviour(regionList)

#############################
    def _updateAllParticles(self):
        """Iterates though all agents & executes previously calculated behaviour.
        Note that this must be done subsequently to the calculations and on a separate iteration
        because it would otherwise affect the actual calculations."""
        
        for agent in self._boidAgentList.itervalues():
            self.setDebugColour(agent)
            agent.commitNewBehaviour(self._particleShapeNode.name())
            
#############################            
    def _paintBlack(self):
        for agent in self._boidAgentList.itervalues:
            util.setParticleColour(self.particleShapeName, agent.particleId, 0, 0, 0)
            
    def setDebugColour(self, agent):
        if(boidAttributes.useDebugColours()):
            particleId = agent.particleId
            
            if(agentIsInBasePyramid(agent)):
                stickiness = agent.stickinessScale / 2
                util.setParticleColour(self.particleShapeName, particleId, stickiness, stickiness, stickiness)
            elif(not agent.isTouchingGround):
                util.setParticleColour(self.particleShapeName, particleId, 0.2, 0.2, 0.2)
            elif(agent.isCollided):
                util.setParticleColour(self.particleShapeName, particleId, 1, 0, 0)
            elif(agentIsChasingGoal(agent)):
                util.setParticleColour(self.particleShapeName, particleId, 1, 1, 0)
            elif(agent.isCrowded):
                util.setParticleColour(self.particleShapeName, particleId, 0.65, 0, 0)
            elif(agentBehaviourIsGoalDriven(agent) and agent.currentBehaviour.agentIsLeader(agent)):
                util.setParticleColour(self.particleShapeName, particleId, 1, 1, 1)
            elif(agent.hasNeighbours):
                util.setParticleColour(self.particleShapeName, particleId, 0, 0.8, 0)
            else:
                util.setParticleColour(self.particleShapeName, particleId, 0, 0, 1)        

#############################
    def _updateSingleParticle(self, particleId):
        singleParticle = self._boidAgentList[particleId]
        self.setDebugColour(singleParticle)
        singleParticle.commitNewBehaviour(self._particleShapeNode.name())
        
#############################
    def onBehaviourEndedForAgent(self, agent, behaviour):  #from BoidBehaviourDelegate
        # TODO - use this to chain stuff together...
        print("agent #%d, ended behaviour: %s" % (agent.particleId, behaviour))
        
############################# 
    def createNewGoal(self, goalVertex, lipVertex, finalGoalVertex, useInfectionSpread):
        """Creates goal instance, but does NOT make it active."""
        self._priorityGoalBehaviour = bbg.GoalDriven(goalVertex, lipVertex, finalGoalVertex, 
                                                     self._normalBehaviour, useInfectionSpread, self)
        
        print("Made new priority goal - %s" % self._priorityGoalBehaviour)
        
    def createSecondaryGoal(self, goalVertex, lipVertex, finalGoalVertex, useInfectionSpread):
        self._secondaryGoalBehaviour = bbg.GoalDriven(goalVertex, lipVertex, finalGoalVertex,
                                                      self._normalBehaviour, useInfectionSpread, self)
        print("Made new secondary target - %s" % self._secondaryGoalBehaviour)

    def makeAgentGoalDriven(self, particleId,  makeLeader = True):
        """Causes agent with corresponding particleId to follow the current priorityGoal."""
        
        if(self._priorityGoalBehaviour == None):
            print("XXXXX WARNING - NO GOAL EXISTS XXXX")
            
        agent = self._boidAgentList[particleId]
        agent.setNewBehaviour(self._priorityGoalBehaviour)
        if(makeLeader):
            self._priorityGoalBehaviour.makeLeader(agent)
    
    def makeAllAgentsGoalDriven(self):
        if(self._priorityGoalBehaviour == None):
            print("XXXXX WARNING - NO GOAL EXISTS XXXX")        

        for agent in self._boidAgentList.itervalues():
            agent.setNewBehaviour(self._priorityGoalBehaviour)
            
    def makeAgentSecondaryGoalDriven(self, particleId, makeLeader = False):
        if(self._secondaryGoalBehaviour != None):
            agent = self._boidAgentList[particleId]
            agent.setNewBehaviour(self._secondaryGoalBehaviour)    
            self._secondaryGoalBehaviour.checkAgentLocation(agent)
            if(makeLeader):
                self._secondaryGoalBehaviour.makeLeader(agent)
            
    def makeNoneGoalInfected(self):
        for agent in self._boidAgentList.itervalues():
            agent.setNewBehaviour(self._normalBehaviour)
            
    def collapseGoal(self):
        """Will 'collapse' the basePyramid at the wall base of a priority goal."""
        if(self._priorityGoalBehaviour != None):
            self._priorityGoalBehaviour.performCollapse = True
            print("COLLAPSING GOAL...")
        return
        
#############################  
    def createNewCurvePath(self, curvePath):
        self._curvePathBehaviour = bbf.FollowPath(curvePath, self._normalBehaviour, self)
        
        print("Made new curve path - %s" % self._curvePathBehaviour)
        
    
    def onNewBoidsCreated(self, newBoidsList):
        #TODO - use this? or delete??
#         if(self._curvePathBehaviour != None):
#             for newBoid in newBoidsList:
#                 newBoid.makeFollowCurvePath(self._curvePathBehaviour)
        print("newBoids: %s" % newBoidsList)
        return
        
    def makeSingleAgentFollowPath(self, particleIndex):
        if(self._curvePathBehaviour == None):
            print("XXX WARNING - NO CURVE PATH EXISTS XXX")
            
        self._boidAgentList[particleIndex].setNewBehaviour(self._curvePathBehaviour)
            
    def makeAllAgentsFollowPath(self):
        if(self._curvePathBehaviour == None):
            print("XXX WARNING - NO CURVE PATH EXISTS XXX")        
            
        for agent in self._boidAgentList.itervalues():
            agent.setNewBehaviour(self._curvePathBehaviour)
        
#############################  
    def makeJump(self, particleId):
        """Makes agent with corresponding particleId 'jump'"""
        self._getSingleParticleInfo(particleId)
        agent = self._boidAgentList[particleId]
        agent._desiredAcceleration.reset()
        agent._jump()
        agent.commitNewBehaviour(self._particleShapeNode.name())
        

#############################        
    def closestAgentToPoint(self, x, y, z, ignoreVertical = False):
        """Helper method intended for use in Maya's Script Editor."""
        
        target = bv3.Vector3(x, y, z)
        closestAgent = None
        closestDistance = None
        
        
        for agent in self._boidAgentList.itervalues():
            if(closestAgent == None):
                closestAgent = agent
                closestDistance = agent.currentPosition - target
            else:
                candidateDistance = agent.currentPosition - target
                if(candidateDistance.magnitude(ignoreVertical) < closestDistance.magnitude(ignoreVertical)):
                    closestAgent = agent
                    closestDistance = candidateDistance
        
        return closestAgent
    
    def closestAgentToLocator(self, locator, ignoreVertical = False):
        """Helper method intended for use in Maya's Script Editor."""
        
        target = util.boidVectorFromLocator(locator)
        return self.closestAgentToPoint(target.x, target.y, target.z, ignoreVertical)
    
    
                    
                
### END OF CLASS 
################################################################################
