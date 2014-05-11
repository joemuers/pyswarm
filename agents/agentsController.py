#
# PySwarm, a swarming simulation tool for Autodesk Maya
#
# created 2013-2014
#
# @author: Joe Muers  (joemuers@hotmail.com)
# 
# All rights reserved.
#
# ------------------------------------------------------------


from pyswarmObject import PyswarmObject
import tools.util as util
import tools.sceneInterface as scene

import vectors.vector3 as v3
import zoneGraph as zg
import agent as ag



_CALCULATIONS_PER_UPDATE_REPORT_ = 20



##############################################
class AgentsController(PyswarmObject):
    """Main external interface to the pyswarm system, basically the managing object for a group of agents.  
    Contains top-level logic (i.e. iterating over agents each frame & executing behaviour) and
    also manages interaction with the actual Pymel objects within Maya.
    """
    
    def __init__(self, attributesController, behavioursController):
        self._globalAttributes = attributesController.globalAttributes
        self._particleIdsOrdering = []
        self._idToAgentLookup = {}
        self._attributesController = attributesController
        self._behavioursController = behavioursController
        self._zoneGraph = zg.ZoneGraph(self._attributesController)     
        
        scene.AddStickinessPerParticleAttributeIfNecessary(self._particleShapeName)

#############################
    def __str__(self):
        if(self._idToAgentLookup):
            returnStrings = ["nodeName=%s, %d particles:" % (self._particleShapeName, len(self._idToAgentLookup))]
            returnStrings.extend([("\n\t%s" % agent) for agent in sorted(self.allAgents)])
            
            return ''.join(returnStrings)
        else:
            return ("nodeName=%s, currently empty" % self._particleShapeName)

########
    def _getMetaStr(self):
        return ''.join([("\t%s\n" % agent.metaStr) for agent in sorted(self.allAgents)])

#############################
    def _getZoneStr(self):
        return self._zoneGraph.__str__()
    zoneStr = property(_getZoneStr)
 
########    
    def _getZoneMetaStr(self):
        return self._zoneGraph.metaStr
    zoneMetaStr = property(_getZoneMetaStr)

#############################        
    def agent(self, agentId):
        return self._idToAgagentId[agentId]

########
    def _getAllAgents(self):
        """Returns unordered list of all agents."""
        return self._idToAgentLookup.values()
    allAgents = property(_getAllAgents)
    
############################# 
    def _getParticleShapeName(self):
        return self._globalAttributes.particleShapeNode.name()
    _particleShapeName = property(_getParticleShapeName)

########
    def _getParticleCount(self):
        return self._globalAttributes.particleShapeNode.getCount()
    _particleCount = property(_getParticleCount)
    
#############################
    def refreshInternals(self):
        self._zoneGraph.rebuildMapIfNecessary()
        self._getAllParticlesInfo()
        
#############################
    def setStickiness(self, agentId, value):
        self._idToAgentLookup[agentId].stickinessScale = value
        scene.SetSingleParticleStickinessScale(self._particleShapeName, agentId, value)  # do this right now - otherwise will wait until next frame update
        
#############################                     
    def _killSingleParticle(self, agentId):
        """IMPORTANT - WILL NOT TAKE EFEECT UNTIL AFTER NEXT FRAME UPDATE"""
        if(agentId in self._idToAgentLookup):
            scene.KillParticle(self._particleShapeName, agentId)
        
#############################
    def onFrameUpdated(self):       
        """Performs one full iteration of updating all agent behaviour.
        Should be called from Maya once per frame update.
        """
        self._globalAttributes.setStatusReadoutWorking(2, "Startup")
        self._zoneGraph.rebuildMapIfNecessary()

        self._getAllParticlesInfo()
        self._globalAttributes.setStatusReadoutWorking(5)
        
        numberOfAgents = len(self._idToAgentLookup)
        numberOfProgressUpdates = ((numberOfAgents / _CALCULATIONS_PER_UPDATE_REPORT_) 
                                   if(numberOfAgents >= _CALCULATIONS_PER_UPDATE_REPORT_) else 1)
        progressUpdateStepSize = 90 / numberOfProgressUpdates
        self._calculateAgentsBehaviour(5, progressUpdateStepSize)
        
        self._globalAttributes.setStatusReadoutWorking(95, "Updating...")
        self._updateAllParticles()
        
        self._globalAttributes.setStatusReadoutWorking(100, "Done!")
        
########
    def onCalculationsCompleted(self):
        pass

#############################
    def _buildParticleList(self, fullRebuild=True):
        """Builds/rebuilds the list of agents based on the current state
        of the corresponding nParticle ShapeNode.
        """
        if(fullRebuild):
            self._idToAgentLookup.clear()
            
            if(self._particleCount > 0):
                # particle IDs are NOT guaranteed to come in numerical order => have to use this list as reference
                self._particleIdsOrdering = scene.ParticleIdsListForParticleShape(self._particleShapeName)
                startingBehaviour = self._behavioursController.defaultBehaviour
                if(self._particleIdsOrdering is not None):
                    for particleId in self._particleIdsOrdering:
                        newAgent = ag.Agent(particleId, self._attributesController, startingBehaviour)
                        self._idToAgentLookup[newAgent.agentId] = newAgent
        else:
            numParticles = self._particleCount
            
            if(numParticles > len(self._idToAgentLookup)):
                # add newly created particles to the list of agents
                self._particleIdsOrdering = scene.ParticleIdsListForParticleShape(self._particleShapeName)
                
                sortedIdsList = sorted(self._particleIdsOrdering)
                keysList = sorted(self._idToAgentLookup.keys())
                lastKey = keysList[-1] if keysList else -1
                newAgentsList = []
                startingBehaviour = self._behavioursController.defaultBehaviour
                
                for ptclId in reversed(sortedIdsList):
                    if(ptclId > lastKey):
                        newAgent = ag.Agent(int(ptclId), self._attributesController, startingBehaviour)
                        self._idToAgentLookup[newAgent.agentId] = newAgent   
                        newAgentsList.append(newAgent)
                    else:
                        break
                    
                self.onNewAgentsCreated(newAgentsList)
                
            elif(numParticles < len(self._idToAgentLookup)):
                # remove recently deleted particles from the list of agents
                self._particleIdsOrdering = scene.ParticleIdsListForParticleShape(self._particleShapeName)
                particleSet = set(self._particleIdsOrdering)
                agentSet = set(self._idToAgentLookup.keys())
                
                for agentId in agentSet.difference(particleSet):
                    del self._idToAgentLookup[agentId]
            else:
                util.LogWarning("Possible logic error - partial rebuild of %s but with no change in particle count." 
                                % self._particleShapeName)
            
#############################            
    def _getSingleParticleInfo(self, particleId):            
        position = scene.GetSingleParticlePosition(self._particleShapeName, particleId) 
        velocity = scene.GetSingleParticleVelocity(self._particleShapeName, particleId) 
        agent = self._idToAgentLookup[particleId]
        
        agent.updateCurrentVectors(v3.Vector3(position[0], position[1], position[2]),
                                   v3.Vector3(velocity[0], velocity[1], velocity[2]))
        self._zoneGraph.updateAgentPosition(agent)
 
#########
    def _getAllParticlesInfo(self, queryExtraInfo=False):
        """Updates all agent instances with position, velocity and derived
        information from their corresponding Maya-side particle instances.
        """
        numParticles = self._particleCount
        if(numParticles == 0):
            self._buildParticleList(True)
        elif(numParticles != len(self._idToAgentLookup)):
            self._buildParticleList(False)
        # elif(numParticles < len(self._idToAgentLookup)):
            # print("XXXXXXXXXX WARNING - MISSING PARTICLES IN LIST!!!, REBUILDING FROM SCRATCH... XXXXX")
            # self._buildParticleList(True)
        
        if(numParticles > 0):
            positions = scene.ParticlePositionsListForParticleShape(self._particleShapeName)
            velocities = scene.ParticleVelocitiesListForParticleShape(self._particleShapeName)
            
            if(len(positions) < numParticles * 3):
                # repeated call here because of shitty Maya bug whereby sometimes only get first item in request for goalsU...
                positions = scene.ParticlePositionsListForParticleShape(self._particleShapeName) 
    
            for i in xrange(numParticles):
                j = i * 3
                particleId = self._particleIdsOrdering[i]
                agent = self._idToAgentLookup[particleId]
                
                agent.updateCurrentVectors(v3.Vector3(positions[j], positions[j + 1], positions[j + 2]),
                                           v3.Vector3(velocities[j], velocities[j + 1], velocities[j + 2]))
                self._zoneGraph.updateAgentPosition(agent)
                
            if(queryExtraInfo):
                self._queryExtraInfo()

#########
    def _queryExtraInfo(self):
        stickinessScales = scene.StickinessScalesListForParticleShape(self._particleShapeName)
        for index, stickiness in enumerate(stickinessScales):
            particleId = self._particleIdsOrdering[index]
            self._idToAgentLookup[particleId]._stickinessScale = stickiness

#############################
    def _calculateAgentsBehaviour(self, progressCurrentValue, progressUpdateStepSize):     
        """Iterates through all agents & calculates desired behaviour based on current PySwarm behaviour rules."""

        nextProgressUpdate = progressCurrentValue + progressUpdateStepSize
        for agent in self._idToAgentLookup.itervalues():
            regionGenerator = self._zoneGraph.nearbyAgentsIterableForAgent(agent)
            agent.calculateDesiredBehaviour(regionGenerator)
            
            progressCurrentValue += 1
            if(progressCurrentValue == nextProgressUpdate):
                self._globalAttributes.setStatusReadoutWorking(progressCurrentValue)
                nextProgressUpdate += progressUpdateStepSize
                
#############################
    def _updateSingleParticle(self, particleId):
        singleParticle = self._idToAgentLookup[particleId]
        self.setDebugColour(singleParticle)
        singleParticle.commitNewBehaviour(self._particleShapeName)
        
#########
    def _updateAllParticles(self):
        """Iterates though all agents & executes previously calculated behaviour.
        Note that this must be done subsequently to the calculations and on a separate iteration
        because it would otherwise affect the actual calculations.
        """
        for agent in self._idToAgentLookup.itervalues():
            self.setDebugColour(agent)
            agent.commitNewBehaviour(self._particleShapeName)
            
#############################            
    def _paintBlack(self):
        for agent in self._idToAgentLookup.itervalues:
            scene.SetParticleColour(self._particleShapeName, agent.agentId, 0)
  
########          
    def setDebugColour(self, agent):
        if(self._globalAttributes.useDebugColours):
            scene.SetParticleColour(self._particleShapeName, agent.agentId, agent.debugColour)     
        
#############################         
    def getAgentsFollowingBehaviour(self, behaviour):
        returnList = []
        for agent in self._idToAgentLookup.itervalues():
            if(agent.currentBehaviour is behaviour):
                returnList.append(agent)
                
        return returnList

#############################    
    def makeAgentsFollowBehaviour(self, agentsList, behaviour):
        for agent in agentsList:
            try:
                if(isinstance(agent, ag.Agent)):
                    agentObject = agent
                elif(type(agent) == int):
                    agentObject = self._idToAgentLookup[agent]
                else:
                    raise TypeError("Unrecognised agent %s of type %s" % (agent, type(agent)))
                
                behaviour.assignAgent(agentObject)
                
            except TypeError as e:
                util.LogError(e)
        
########        
    def makeAllAgentsFollowBehaviour(self, behaviour):
        for agent in self._idToAgentLookup.itervalues():
            agent.setNewBehaviour(behaviour)

########            
    def makeAgentsFollowDefaultBehaviour(self, agentsList):
        self.makeAgentsFollowBehaviour(agentsList, self._behavioursController.defaultBehaviour)

#############################       
    def onNewAgentsCreated(self, newBoidsList):
        # TODO - use this? or delete??
#         if(self._pathCurveBehaviour is not None):
#             for newBoid in newBoidsList:
#                 newBoid.makeFollowCurvePath(self._pathCurveBehaviour)
        util.LogDebug("newAgents: %s" % newBoidsList, self._particleShapeName)
        return

#############################  
    def makeJump(self, agentId):
        """Makes agent with corresponding agentId 'jump'"""
        self._getSingleParticleInfo(agentId)
        agent = self._idToAgentLookup[agentId]
        agent._desiredAcceleration.reset()
        agent._jump()
        agent.commitNewBehaviour(self._particleShapeName)
        
#############################        
    def closestAgentToPoint(self, x, y, z, ignoreVertical=False):
        """Helper method intended for use in Maya's Script Editor."""
        target = v3.Vector3(x, y, z)
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

########    
    def closestAgentToLocator(self, locator, ignoreVertical=False):
        """Helper method intended for use in Maya's Script Editor."""
        target = scene.Vector3FromLocator(locator)
        return self.closestAgentToPoint(target.x, target.y, target.z, ignoreVertical)
    
    
### END OF CLASS 
################################################################################
