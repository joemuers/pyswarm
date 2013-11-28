from boidBaseObject import BoidBaseObject

import boidAttributes
from boidTools import util

import boidVectors.vector3 as bv3
import boidTools.zoneGraph as bzg
import boidAgent as ba
import boidBehaviours.classicBoid as bbc
import boidBehaviours.goalDriven as bbg
import boidBehaviours.followPath as bbf

from boidBehaviours.behaviourBaseObject import BoidBehaviourDelegate



class BoidSwarm(BoidBaseObject, BoidBehaviourDelegate):
    """Main external interface to the boid system, basically the managing object for a group of boidAgents.  
    Contains top-level logic (i.e. iterating over agents each frame & executing behaviour) and
    also manages interaction with the actual Pymel objects within Maya.
    """
    
    def __init__(self, particleShapeNode, cornerLocatorA, cornerLocatorB):
        self._particleShapeNode = particleShapeNode
        self._particleIdsOrdering = []
        self._boidAgentList = {}
        self._zoneGraph = bzg.ZoneGraph(cornerLocatorA, cornerLocatorB)        
        
        self._normalBehaviour = bbc.ClassicBoid(self._zoneGraph.lowerBoundsVector, self._zoneGraph.upperBoundsVector)
        self._priorityGoalBehaviour = None   # 
        self._secondaryGoalBehaviour = None  # boidBehaviours.GoalDriven instances
        self._curvePathBehaviour = None  # boidBehaviours.FollowPath instance
        
        self._buildParticleList()

#############################
    def __str__(self):
        if(self._boidAgentList):
            returnStrings = ["nodeName=%s, %d particles:" % (self.particleShapeName, len(self._boidAgentList))]
            returnStrings.extend([("\n\t%s" % agent) for agent in self.agentListSorted])
            
            return ''.join(returnStrings)
        else:
            return ("nodeName=%s, currently empty" % self.particleShapeName)


#############################
    def _getMetaStr(self):
        return ''.join([("\t%s\n" % agent.metaStr) for agent in self.agentListSorted])

#############################    
    def _getZoneStr(self):
        return self._zoneGraph.__str__()
    zoneStr = property(_getZoneStr)
    
    def _getZoneMetaStr(self):
        return self._zoneGraph.metaStr
    zoneMetaStr = property(_getZoneMetaStr)

#############################    
    def _getAgentListSorted(self):
        """Returns sorted list of boid agents, not too efficient - mainly for debug/console use."""
        return sorted(self._boidAgentList.values())
    agentListSorted = property(_getAgentListSorted)
    
    def agent(self, particleId):
        return self._boidAgentList[particleId]

############################# 
    def _getParticleShapeName(self):
        return self._particleShapeNode.name()
    particleShapeName = property(_getParticleShapeName)
    
#############################
    def _buildParticleList(self, fullRebuild=True):
        """Builds/rebuilds the list of boidAgents based on the current state
        of the corresponding nParticle ShapeNode.
        """
        if(fullRebuild):
            self._boidAgentList.clear()
            
            if(self._particleShapeNode.getCount() > 0):
                #particle IDs are NOT guaranteed to come in numerical order => have to use this list as reference
                self._particleIdsOrdering = util.ParticleIdsListForParticleShape(self.particleShapeName)             
                if(self._particleIdsOrdering is not None):
                    for particleId in self._particleIdsOrdering:
                        newAgent = ba.BoidAgent(int(particleId), self._normalBehaviour)
                        self._boidAgentList[newAgent.particleId] = newAgent
        else:
            numParticles = self._particleShapeNode.getCount()
            
            if(numParticles > len(self._boidAgentList)):
                # add newly created particles to the list of agents
                self._particleIdsOrdering = util.ParticleIdsListForParticleShape(self.particleShapeName)
                
                sortedIdsList = sorted(self._particleIdsOrdering)
                keysList = sorted(self._boidAgentList.keys())
                lastKey = keysList[-1] if keysList else -1
                newAgentsList = []
                
                for ptclId in reversed(sortedIdsList):
                    if(ptclId > lastKey):
                        newAgent = ba.BoidAgent(int(ptclId), self._normalBehaviour)
                        self._boidAgentList[newAgent.particleId] = newAgent   
                        newAgentsList.append(newAgent)
                    else:
                        break
                    
                self.onNewBoidsCreated(newAgentsList)
                
            elif(numParticles < len(self._boidAgentList)):
                # remove recently deleted particles from the list of agents
                self._particleIdsOrdering = util.ParticleIdsListForParticleShape(self.particleShapeName)
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
            util.KillParticle(self.particleShapeName, particleId)
        
#############################            
    def _getSingleParticleInfo(self, particleId):            
        position =  util.GetSingleParticlePosition(self.particleShapeName, particleId) 
        velocity =  util.GetSingleParticleVelocity(self.particleShapeName, particleId) 
        agent = self._boidAgentList[particleId]
        
        agent.updateCurrentVectors(bv3.Vector3(position[0], position[1], position[2]), 
                                   bv3.Vector3(velocity[0], velocity[1], velocity[2]))
        if(bbg.AgentBehaviourIsGoalDriven(agent)):
            agent._currentBehaviour.checkAgentLocation(agent)
        self._zoneGraph.updateAgentPosition(agent)
 
#############################
    def setStickiness(self, particleId, value):
        self._boidAgentList[particleId].stickinessScale = value
        util.SetSingleParticleStickinessScale(self.particleShapeName, particleId, value) # do this right now - otherwise will wait until next frame update

#############################
    def fullUpdate(self):       
        """Performs one full iteration of updating all boidAgent behaviour.
        Should be called from Maya once per frame update.
        """
        self._resetHelperObjects()
        self._getAllParticlesInfo()
        self._calculateAgentsBehaviour()
        self._updateAllParticles()

#############################
    def _resetHelperObjects(self):
        if(self._priorityGoalBehaviour is not None):
            self._priorityGoalBehaviour.onFrameUpdate()
            
        if(self._secondaryGoalBehaviour is not None):
            self._secondaryGoalBehaviour.onFrameUpdate()
            
        if(self._curvePathBehaviour is not None):
            self._curvePathBehaviour.onFrameUpdate()

#############################
    def _getAllParticlesInfo(self, queryExtraInfo=False):
        """Updates all boidAgent instances with position, velocity and derived
        information from their corresponding Maya-side particle instances.
        """
        numParticles = self._particleShapeNode.getCount()
        if(numParticles == 0):
            self._buildParticleList(True)
        elif(numParticles != len(self._boidAgentList)):
            self._buildParticleList(False)
        #elif(numParticles < len(self._boidAgentList)):
            #print("XXXXXXXXXX WARNING - MISSING PARTICLES IN LIST!!!, REBUILDING FROM SCRATCH... XXXXX")
            #self._buildParticleList(True)
        
        if(numParticles > 0):
            positions = util.ParticlePositionsListForParticleShape(self.particleShapeName)
            velocities = util.ParticleVelocitiesListForParticleShape(self.particleShapeName)
            
            if(len(positions) < numParticles * 3):
                #repeated call here because of shitty Maya bug whereby sometimes only get first item in request for goalsU...
                positions = util.ParticlePositionsListForParticleShape(self.particleShapeName) 
    
            for i in range(0, numParticles):
                j = i * 3
                particleId = self._particleIdsOrdering[i]
                agent = self._boidAgentList[particleId]
                
                agent.updateCurrentVectors(bv3.Vector3(positions[j], positions[j+1], positions[j+2]),
                                           bv3.Vector3(velocities[j], velocities[j+1], velocities[j+2]))
                if(bbg.AgentBehaviourIsGoalDriven(agent)):
                    agent._currentBehaviour.checkAgentLocation(agent)
                self._zoneGraph.updateAgentPosition(agent)
                
            if(queryExtraInfo):
                self._queryExtraInfo()

#############################
    def _queryExtraInfo(self):
        stickinessScales = util.StickinessScalesListForParticleShape(self.particleShapeName)
        for index, stickiness in enumerate(stickinessScales):
            particleId = self._particleIdsOrdering[index]
            self._boidAgentList[particleId]._stickinessScale = stickiness

#############################
    def _calculateAgentsBehaviour(self):     
        """Iterates through all agents & calculates desired behaviour based on boids rules."""
        for agent in self._boidAgentList.itervalues():
            regionGenerator = self._zoneGraph.nearbyAgentsIterableForAgent(agent)
            agent.calculateDesiredBehaviour(regionGenerator)

#############################
    def _updateAllParticles(self):
        """Iterates though all agents & executes previously calculated behaviour.
        Note that this must be done subsequently to the calculations and on a separate iteration
        because it would otherwise affect the actual calculations.
        """
        for agent in self._boidAgentList.itervalues():
            self.setDebugColour(agent)
            agent.commitNewBehaviour(self._particleShapeNode.name())
            
#############################            
    def _paintBlack(self):
        for agent in self._boidAgentList.itervalues:
            util.SetParticleColour(self.particleShapeName, agent.particleId, 0, 0, 0)
            
    def setDebugColour(self, agent):
        if(boidAttributes.UseDebugColours()):
            particleId = agent.particleId
            
            if(bbg.AgentIsInBasePyramid(agent)):
                stickiness = agent.stickinessScale / 2
                util.SetParticleColour(self.particleShapeName, particleId, stickiness, stickiness, stickiness)
            elif(not agent.isTouchingGround):
                util.SetParticleColour(self.particleShapeName, particleId, 0.2, 0.2, 0.2)
            elif(bbg.AgentBehaviourIsGoalDriven(agent) and agent.currentBehaviour.agentIsLeader(agent)):
                util.SetParticleColour(self.particleShapeName, particleId, 1, 1, 1)
            elif(bbg.AgentIsChasingGoal(agent)):
                util.SetParticleColour(self.particleShapeName, particleId, 1, 1, 0)
            elif(bbf.agentBehaviourIsFollowPath(agent)):
                util.SetParticleColour(self.particleShapeName, particleId, 0.5, 0.5, 0)
            elif(agent.isCollided):
                util.SetParticleColour(self.particleShapeName, particleId, 1, 0, 0)            
            elif(agent.isCrowded):
                util.SetParticleColour(self.particleShapeName, particleId, 0.65, 0, 0)
            elif(agent.hasNeighbours):
                util.SetParticleColour(self.particleShapeName, particleId, 0, 0.8, 0)
            else:
                util.SetParticleColour(self.particleShapeName, particleId, 0, 0, 1)        

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

    def makeAgentGoalDriven(self, particleId, makeLeader):
        """Causes agent with corresponding particleId to follow the current priorityGoal."""
        
        if(self._priorityGoalBehaviour is None):
            print("XXXXX WARNING - NO GOAL EXISTS XXXX")
            
        agent = self._boidAgentList[particleId]
        agent.setNewBehaviour(self._priorityGoalBehaviour)
        if(makeLeader):
            self._priorityGoalBehaviour.makeLeader(agent)
    
    def makeAllAgentsGoalDriven(self):
        if(self._priorityGoalBehaviour is None):
            print("XXXXX WARNING - NO GOAL EXISTS XXXX")        

        for agent in self._boidAgentList.itervalues():
            agent.setNewBehaviour(self._priorityGoalBehaviour)
            
    def makeAgentSecondaryGoalDriven(self, particleId, makeLeader=False):
        if(self._secondaryGoalBehaviour is not None):
            agent = self._boidAgentList[particleId]
            agent.setNewBehaviour(self._secondaryGoalBehaviour)    
            self._secondaryGoalBehaviour.checkAgentLocation(agent)
            if(makeLeader):
                self._secondaryGoalBehaviour.makeLeader(agent)
            
    def collapseGoal(self):
        """Will 'collapse' the basePyramid at the wall base of a priority goal."""
        if(self._priorityGoalBehaviour is not None):
            self._priorityGoalBehaviour.performCollapse = True
            print("COLLAPSING GOAL...")
        return
        
#############################  
    def createNewCurvePath(self, curvePath):
        self._curvePathBehaviour = bbf.FollowPath(curvePath, self._normalBehaviour, self)
        
        print("Made new curve path - %s" % self._curvePathBehaviour)
        
    
    def onNewBoidsCreated(self, newBoidsList):
        #TODO - use this? or delete??
#         if(self._curvePathBehaviour is not None):
#             for newBoid in newBoidsList:
#                 newBoid.makeFollowCurvePath(self._curvePathBehaviour)
        print("newBoids: %s" % newBoidsList)
        return
        
    def makeSingleAgentFollowPath(self, particleIndex):
        if(self._curvePathBehaviour is None):
            print("XXX WARNING - NO CURVE PATH EXISTS XXX")
            
        self._boidAgentList[particleIndex].setNewBehaviour(self._curvePathBehaviour)
            
    def makeAllAgentsFollowPath(self):
        if(self._curvePathBehaviour is None):
            print("XXX WARNING - NO CURVE PATH EXISTS XXX")        
            
        for agent in self._boidAgentList.itervalues():
            agent.setNewBehaviour(self._curvePathBehaviour)
        
#############################        
    def makeAgentBoidRulesDriven(self, particleIndex):
        self._boidAgentList[particleIndex].setNewBehaviour(self._normalBehaviour)
        
    def makeAllAgentsBoidRulesDriven(self):
        for agent in self._boidAgentList.itervalues():
            agent.setNewBehaviour(self._normalBehaviour)
        
#############################  
    def makeJump(self, particleId):
        """Makes agent with corresponding particleId 'jump'"""
        self._getSingleParticleInfo(particleId)
        agent = self._boidAgentList[particleId]
        agent._desiredAcceleration.reset()
        agent._jump()
        agent.commitNewBehaviour(self._particleShapeNode.name())
        

#############################        
    def closestAgentToPoint(self, x, y, z, ignoreVertical=False):
        """Helper method intended for use in Maya's Script Editor."""
        target = bv3.Vector3(x, y, z)
        closestAgent = None
        closestDistance = None
        
        for agent in self._boidAgentList.itervalues():
            if(closestAgent is None):
                closestAgent = agent
                closestDistance = agent.currentPosition - target
            else:
                candidateDistance = agent.currentPosition - target
                if(candidateDistance.magnitude(ignoreVertical) < closestDistance.magnitude(ignoreVertical)):
                    closestAgent = agent
                    closestDistance = candidateDistance
        
        return closestAgent
    
    def closestAgentToLocator(self, locator, ignoreVertical=False):
        """Helper method intended for use in Maya's Script Editor."""
        target = util.BoidVector3FromPymelLocator(locator)
        return self.closestAgentToPoint(target.x, target.y, target.z, ignoreVertical)
    
    
                    
                
### END OF CLASS 
################################################################################
