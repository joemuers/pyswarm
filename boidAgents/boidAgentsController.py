from boidBaseObject import BoidBaseObject
from boidBehaviours.behaviourBaseObject import BoidBehaviourDelegate
from boidTools import util

import boidVectors.vector3 as bv3
import boidTools.zoneGraph as bzg
import boidAgent as ba



##############################################
class BoidAgentsController(BoidBaseObject, BoidBehaviourDelegate):
    """Main external interface to the boid system, basically the managing object for a group of boidAgents.  
    Contains top-level logic (i.e. iterating over agents each frame & executing behaviour) and
    also manages interaction with the actual Pymel objects within Maya.
    """
    
    def __init__(self, behaviourController, particleShapeNode, lowerBoundsVector, upperBoundsVector):
        self._particleShapeNode = particleShapeNode
        self._particleIdsOrdering = []
        self._boidAgentList = {}
        self._attributesController = behaviourController.attributesController
        self._behaviourController = behaviourController
        self._zoneGraph = bzg.ZoneGraph(self._attributesController, lowerBoundsVector, upperBoundsVector)        
        
        self._buildParticleList()
        
        util.LogInfo("created new %s for nParticle %s" % (util.PackageName(), self.particleShapeName))
        self.showUI()

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
    def showUI(self):
        self._attributesController.buildUi(("%s - %s" % (util.PackageName(), self.particleShapeName)))
        
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
                        newAgent = ba.BoidAgent(int(particleId), self._attributesController, self._behaviourController)
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
                        newAgent = ba.BoidAgent(int(ptclId), self._attributesController, self._behaviourController)
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
                util.LogWarning("Possible logic error - partial rebuild of %s but with no change in particle count." 
                                % self.particleShapeName)

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
        self._zoneGraph.updateAgentPosition(agent)
 
#############################
    def setStickiness(self, particleId, value):
        self._boidAgentList[particleId].stickinessScale = value
        util.SetSingleParticleStickinessScale(self.particleShapeName, particleId, value) # do this right now - otherwise will wait until next frame update

#############################
    def onFrameUpdated(self):       
        """Performs one full iteration of updating all boidAgent behaviour.
        Should be called from Maya once per frame update.
        """
        self._getAllParticlesInfo()
        self._calculateAgentsBehaviour()
        self._updateAllParticles()

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
    
            for i in xrange(numParticles):
                j = i * 3
                particleId = self._particleIdsOrdering[i]
                agent = self._boidAgentList[particleId]
                
                agent.updateCurrentVectors(bv3.Vector3(positions[j], positions[j+1], positions[j+2]),
                                           bv3.Vector3(velocities[j], velocities[j+1], velocities[j+2]))
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
            util.SetParticleColour(self.particleShapeName, agent.particleId, 0)
            
    def setDebugColour(self, agent):
        if(self._attributesController.globalAttributes.useDebugColours):
            util.SetParticleColour(self.particleShapeName, agent.particleId, agent.debugColour)
            
#             
#             if(bbg.AgentIsInBasePyramid(agent)):
#                 stickiness = agent.stickinessScale / 2
#                 util.SetParticleColour(self.particleShapeName, particleId, stickiness, stickiness, stickiness)
#             elif(not agent.isTouchingGround):
#                 util.SetParticleColour(self.particleShapeName, particleId, 0.2, 0.2, 0.2)
#             elif(bbg.AgentBehaviourIsGoalDriven(agent) and agent.currentBehaviour.agentIsLeader(agent)):
#                 util.SetParticleColour(self.particleShapeName, particleId, 1, 1, 1)
#             elif(bbg.AgentIsChasingGoal(agent)):
#                 util.SetParticleColour(self.particleShapeName, particleId, 1, 1, 0)
#             elif(bbf.agentBehaviourIsFollowPath(agent)):
#                 util.SetParticleColour(self.particleShapeName, particleId, 0.5, 0.5, 0)
#             elif(agent.isCollided):
#                 util.SetParticleColour(self.particleShapeName, particleId, 1, 0, 0)            
#             elif(agent.isCrowded):
#                 util.SetParticleColour(self.particleShapeName, particleId, 0.65, 0, 0)
#             elif(agent.hasNeighbours):
#                 util.SetParticleColour(self.particleShapeName, particleId, 0, 0.8, 0)
#             else:
#                 util.SetParticleColour(self.particleShapeName, particleId, 0, 0, 1)        

#############################
    def _updateSingleParticle(self, particleId):
        singleParticle = self._boidAgentList[particleId]
        self.setDebugColour(singleParticle)
        singleParticle.commitNewBehaviour(self._particleShapeNode.name())
        
#############################         
    def makeAgentsFollowBehaviour(self, agentIdsList, behaviour):
        for agentId in agentIdsList:
            self._boidAgentList[agentId].setNewBehaviour(behaviour)

    def makeAllAgentsFollowBehaviour(self, behaviour):
        for agent in self._boidAgentList.itervalues():
            agent.setNewBehaviour(behaviour)
   
#############################
    def onBehaviourEndedForAgent(self, agent, behaviour):  #from BoidBehaviourDelegate
        # TODO - use this to chain stuff together...
        util.LogDebug("%s agent #%d, ended behaviour: %s" % (self.particleShapeName, agent.particleId, behaviour))
 
#############################       
    def onNewBoidsCreated(self, newBoidsList):
        #TODO - use this? or delete??
#         if(self._curvePathBehaviour is not None):
#             for newBoid in newBoidsList:
#                 newBoid.makeFollowCurvePath(self._curvePathBehaviour)
        util.LogDebug("newBoids: %s" % newBoidsList, self.particleShapeName)
        return

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
