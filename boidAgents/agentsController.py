from boidBaseObject import BoidBaseObject
import boidTools.util as util
import boidTools.sceneInterface as scene

import boidVectors.vector3 as bv3
import zoneGraph as zg
import agent as ag



##############################################
class AgentsController(BoidBaseObject):
    """Main external interface to the boid system, basically the managing object for a group of boidAgents.  
    Contains top-level logic (i.e. iterating over agents each frame & executing behaviour) and
    also manages interaction with the actual Pymel objects within Maya.
    """
    
    def __init__(self, attributesController, particleShapeNode):
        self._particleShapeNode = scene.PymelObjectFromObjectName(particleShapeNode)
        self._particleIdsOrdering = []
        self._idToAgentLookup = {}
        self._attributesController = attributesController
        self.defaultBehaviourMethod = None
        self._zoneGraph = zg.ZoneGraph(self._attributesController)        
        
#         self._buildParticleList()
        scene.AddStickinessPerParticleAttributeIfNecessary(self.particleShapeName)
        
        util.LogInfo("created new %s for nParticle %s" % (util.PackageName(), self.particleShapeName))

#############################
    def __str__(self):
        if(self._idToAgentLookup):
            returnStrings = ["nodeName=%s, %d particles:" % (self.particleShapeName, len(self._idToAgentLookup))]
            returnStrings.extend([("\n\t%s" % agent) for agent in sorted(self.allAgents)])
            
            return ''.join(returnStrings)
        else:
            return ("nodeName=%s, currently empty" % self.particleShapeName)

#############################
    def _getMetaStr(self):
        return ''.join([("\t%s\n" % agent.metaStr) for agent in sorted(self.allAgents)])

#############################
    def _getZoneStr(self):
        return self._zoneGraph.__str__()
    zoneStr = property(_getZoneStr)
    
    def _getZoneMetaStr(self):
        return self._zoneGraph.metaStr
    zoneMetaStr = property(_getZoneMetaStr)

#############################        
    def agent(self, particleId):
        return self._idToAgentLookup[particleId]

    def _getAllAgents(self):
        """Returns unordered list of all agents."""
        return self._idToAgentLookup.values()
    allAgents = property(_getAllAgents)
    
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
            self._idToAgentLookup.clear()
            
            if(self._particleShapeNode.getCount() > 0):
                #particle IDs are NOT guaranteed to come in numerical order => have to use this list as reference
                self._particleIdsOrdering = scene.ParticleIdsListForParticleShape(self.particleShapeName)             
                if(self._particleIdsOrdering is not None):
                    for particleId in self._particleIdsOrdering:
                        newAgent = ag.Agent(int(particleId), self._attributesController,
                                            self.defaultBehaviourMethod(), self._attributesController.defaultBehaviourAttributes)
                        self._idToAgentLookup[newAgent.particleId] = newAgent
        else:
            numParticles = self._particleShapeNode.getCount()
            
            if(numParticles > len(self._idToAgentLookup)):
                # add newly created particles to the list of agents
                self._particleIdsOrdering = scene.ParticleIdsListForParticleShape(self.particleShapeName)
                
                sortedIdsList = sorted(self._particleIdsOrdering)
                keysList = sorted(self._idToAgentLookup.keys())
                lastKey = keysList[-1] if keysList else -1
                newAgentsList = []
                
                for ptclId in reversed(sortedIdsList):
                    if(ptclId > lastKey):
                        newAgent = ag.Agent(int(ptclId), self._attributesController,
                                            self.defaultBehaviourMethod(), self._attributesController.defaultBehaviourAttributes)
                        self._idToAgentLookup[newAgent.particleId] = newAgent   
                        newAgentsList.append(newAgent)
                    else:
                        break
                    
                self.onNewBoidsCreated(newAgentsList)
                
            elif(numParticles < len(self._idToAgentLookup)):
                # remove recently deleted particles from the list of agents
                self._particleIdsOrdering = scene.ParticleIdsListForParticleShape(self.particleShapeName)
                particleSet = set(self._particleIdsOrdering)
                boidAgentSet = set(self._idToAgentLookup.keys())
                
                for particleId in boidAgentSet.difference(particleSet):
                    del self._idToAgentLookup[particleId]
            else:
                util.LogWarning("Possible logic error - partial rebuild of %s but with no change in particle count." 
                                % self.particleShapeName)

#############################                     
    def _killSingleParticle(self, particleId):
        """IMPORTANT - WILL NOT TAKE EFEECT UNTIL AFTER NEXT FRAME UPDATE"""
        if(particleId in self._idToAgentLookup):
            scene.KillParticle(self.particleShapeName, particleId)
        
#############################            
    def _getSingleParticleInfo(self, particleId):            
        position =  scene.GetSingleParticlePosition(self.particleShapeName, particleId) 
        velocity =  scene.GetSingleParticleVelocity(self.particleShapeName, particleId) 
        agent = self._idToAgentLookup[particleId]
        
        agent.updateCurrentVectors(bv3.Vector3(position[0], position[1], position[2]), 
                                   bv3.Vector3(velocity[0], velocity[1], velocity[2]))
        self._zoneGraph.updateAgentPosition(agent)
 
#############################
    def setStickiness(self, particleId, value):
        self._idToAgentLookup[particleId].stickinessScale = value
        scene.SetSingleParticleStickinessScale(self.particleShapeName, particleId, value) # do this right now - otherwise will wait until next frame update

#############################
    def refreshInternals(self):
        self._zoneGraph.rebuildMapIfNecessary()
        self._getAllParticlesInfo()
        
#############################
    def onFrameUpdated(self):       
        """Performs one full iteration of updating all boidAgent behaviour.
        Should be called from Maya once per frame update.
        """
        self._zoneGraph.rebuildMapIfNecessary()
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
        elif(numParticles != len(self._idToAgentLookup)):
            self._buildParticleList(False)
        #elif(numParticles < len(self._idToAgentLookup)):
            #print("XXXXXXXXXX WARNING - MISSING PARTICLES IN LIST!!!, REBUILDING FROM SCRATCH... XXXXX")
            #self._buildParticleList(True)
        
        if(numParticles > 0):
            positions = scene.ParticlePositionsListForParticleShape(self.particleShapeName)
            velocities = scene.ParticleVelocitiesListForParticleShape(self.particleShapeName)
            
            if(len(positions) < numParticles * 3):
                #repeated call here because of shitty Maya bug whereby sometimes only get first item in request for goalsU...
                positions = scene.ParticlePositionsListForParticleShape(self.particleShapeName) 
    
            for i in xrange(numParticles):
                j = i * 3
                particleId = self._particleIdsOrdering[i]
                agent = self._idToAgentLookup[particleId]
                
                agent.updateCurrentVectors(bv3.Vector3(positions[j], positions[j+1], positions[j+2]),
                                           bv3.Vector3(velocities[j], velocities[j+1], velocities[j+2]))
                self._zoneGraph.updateAgentPosition(agent)
                
            if(queryExtraInfo):
                self._queryExtraInfo()

#############################
    def _queryExtraInfo(self):
        stickinessScales = scene.StickinessScalesListForParticleShape(self.particleShapeName)
        for index, stickiness in enumerate(stickinessScales):
            particleId = self._particleIdsOrdering[index]
            self._idToAgentLookup[particleId]._stickinessScale = stickiness

#############################
    def _calculateAgentsBehaviour(self):     
        """Iterates through all agents & calculates desired behaviour based on boids rules."""
        for agent in self._idToAgentLookup.itervalues():
            regionGenerator = self._zoneGraph.nearbyAgentsIterableForAgent(agent)
            agent.calculateDesiredBehaviour(regionGenerator)

#############################
    def _updateAllParticles(self):
        """Iterates though all agents & executes previously calculated behaviour.
        Note that this must be done subsequently to the calculations and on a separate iteration
        because it would otherwise affect the actual calculations.
        """
        for agent in self._idToAgentLookup.itervalues():
            self.setDebugColour(agent)
            agent.commitNewBehaviour(self._particleShapeNode.name())
            
#############################            
    def _paintBlack(self):
        for agent in self._idToAgentLookup.itervalues:
            scene.SetParticleColour(self.particleShapeName, agent.particleId, 0)
            
    def setDebugColour(self, agent):
        if(self._attributesController.globalAttributes.useDebugColours):
            scene.SetParticleColour(self.particleShapeName, agent.particleId, agent.debugColour)     

#############################
    def _updateSingleParticle(self, particleId):
        singleParticle = self._idToAgentLookup[particleId]
        self.setDebugColour(singleParticle)
        singleParticle.commitNewBehaviour(self._particleShapeNode.name())
        
#############################         
    def getAgentsFollowingBehaviour(self, behaviour):
        returnList = []
        
        for agent in self._idToAgentLookup.itervalues():
            if(agent._currentBehaviour is behaviour):
                returnList.append(agent)
                
        return returnList

#############################    
    def makeAgentsFollowBehaviour(self, agentsList, behaviour, attributes):
        for agent in agentsList:
            try:
                if(isinstance(agent, ag.Agent)):
                    agent.setNewBehaviour(behaviour, attributes)
                elif(type(agent) == int):
                    self._idToAgentLookup[agent].setNewBehaviour(behaviour, attributes)
                else:
                    raise TypeError("Unrecognised agent %s of type %s" % (agent, type(agent)))
            except TypeError as e:
                print e
                
    def makeAllAgentsFollowBehaviour(self, behaviour, attributes):
        for agent in self._idToAgentLookup.itervalues():
            agent.setNewBehaviour(behaviour, attributes)

#############################       
    def onNewBoidsCreated(self, newBoidsList):
        #TODO - use this? or delete??
#         if(self._pathCurveBehaviour is not None):
#             for newBoid in newBoidsList:
#                 newBoid.makeFollowCurvePath(self._pathCurveBehaviour)
        util.LogDebug("newBoids: %s" % newBoidsList, self.particleShapeName)
        return

#############################  
    def makeJump(self, particleId):
        """Makes agent with corresponding particleId 'jump'"""
        self._getSingleParticleInfo(particleId)
        agent = self._idToAgentLookup[particleId]
        agent._desiredAcceleration.reset()
        agent._jump()
        agent.commitNewBehaviour(self._particleShapeNode.name())
        
#############################        
    def closestAgentToPoint(self, x, y, z, ignoreVertical=False):
        """Helper method intended for use in Maya's Script Editor."""
        target = bv3.Vector3(x, y, z)
        closestAgent = None
        closestDistance = None
        
        for agent in self._idToAgentLookup.itervalues():
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
        target = scene.Vector3FromLocator(locator)
        return self.closestAgentToPoint(target.x, target.y, target.z, ignoreVertical)
    
    
### END OF CLASS 
################################################################################
