from boidBaseObject import BoidBaseObject

import boidAgents.agentsController as bac
import boidAttributes.attributesController as bat
import boidBehaviours.behavioursController as bbc
import boidTools.agentSelectionWindow as asw
import boidTools.util as util


###########################################
_SwarmInstances_ = []

#############################
def InitialiseSwarm(particleShapeNode=None, sceneBounds1=None, sceneBounds2=None):
    """Creates a new swarm instance for the given particle node.
    If a swarm already exists for that particle node, it will be replaced.
    """
    if(particleShapeNode is None):
        particleShapeNode = util.GetSelectedParticleShapeNode()
        if(particleShapeNode is None):
            raise RuntimeError("No particle node specified - you must either select one in the scene \
or pass in a reference via the \"particleShapeNode\" argument to this method.")
    
    try:
        RemoveSwarmInstanceForParticle(particleShapeNode)
    except:
        pass
    
    newSwarm = SwarmController(particleShapeNode, sceneBounds1, sceneBounds2)
    _SwarmInstances_.append(newSwarm)
    
    return newSwarm

#############################
def Show():
    """Will make the UIs visible (if not already) for all existing swarm instances."""
    for swarmInstance in _SwarmInstances_:
        swarmInstance.showUI()

#############################
def GetSwarmInstanceForParticle(particleShapeNode):
    """Gets the corresponding swarm instance for the given particle node,
    if it exists (otherwise returns None).
    """
    pymelShapeNode = util.PymelObjectFromObjectName(particleShapeNode, True)
    for swarmController in _SwarmInstances_:
        if(pymelShapeNode.name() == swarmController.particleShapeName):
            return swarmController
        
    return None

#############################
def RemoveSwarmInstanceForParticle(particleShapeNode):
    RemoveSwarmInstance(GetSwarmInstanceForParticle(particleShapeNode))

#############################        
def RemoveSwarmInstance(swarmInstance):
    if(swarmInstance in _SwarmInstances_):
        swarmInstance.hideUI()
        _SwarmInstances_.remove(swarmInstance)
        
        util.LogInfo("%s instance %s deleted." % (util.PackageName(), swarmInstance.particleShapeName))
    elif(swarmInstance is not None and isinstance(swarmInstance, SwarmController)):
        swarmInstance.hideUI()
        util.LogWarning("Attempt to delete unregistered swarm instance - likely causes:\n\
swarmController module as been reloaded, leaving \'orphan\' instances, or,\n\
an instance has been created indepedently by the user.\n\
It is recommended that swarm management is done only via the module methods provided.")
    else:
        raise TypeError("Got %s of type %s (expected %s)." % (swarmInstance, type(swarmInstance), SwarmController))

#############################        
def _OnFrameUpdated():
    for swarmInstance in _SwarmInstances_:
        swarmInstance.onFrameUpdated()
        
        
if(__name__ == "__main__"):
    print "TODO - add Maya script node to run _OnFrameUpdated()"

#############################



##########################################
class SwarmController(BoidBaseObject, bat.AttributesControllerDelegate):
    
    def __init__(self, particleShapeNode, sceneBounds1=None, sceneBounds2=None):
        if(not isinstance(particleShapeNode, util.GetParticleType())):
            raise TypeError("Cannot create swarm with this node type (expected %s, got %s)." %
                            util.GetParticleType(), type(particleShapeNode))
            
        if(sceneBounds1 is None and sceneBounds2 is None):
            locatorsList = util.GetSelectedLocators()
            if(len(locatorsList) >= 2):
                sceneBounds1 = locatorsList[0]
                sceneBounds2 = locatorsList[1]
        
        self._attributesController = bat.AttributesController(self, sceneBounds1, sceneBounds2)
        self._agentsController = bac.AgentsController(self._attributesController, particleShapeNode)
        self._behavioursController = bbc.BehavioursController(self._attributesController, self._agentsController)
        self._agentsController._buildParticleList()
        
        if(not self._attributesController._checkForPreviousSaveFile()):
            self._attributesController.restoreDefaultAttributeValuesFromFile()
        self._attributesController._notifyOnBehavioursListChanged()
        
        self._behaviourAssignmentSelectionWindow = asw.AgentSelectionWindow(self._agentsController)
        self._leaderAgentsSelectionWindow = asw.AgentSelectionWindow(self._agentsController)
        
        self.showUI()

#############################        
    def __str__(self):
        return self._agentsController.__str__()
    
    def _getMetaStr(self):
        return self._agentsController.metaStr

#############################    
    def _getParticleShapeName(self):
        return self._agentsController.particleShapeName
    particleShapeName = property(_getParticleShapeName)

#############################    
    def _getAttributesController(self):
        return self._attributesController
    attributesController = property(_getAttributesController)
        
#############################    
    def showUI(self):
        self._attributesController.buildUi(("%s - %s" % (util.PackageName(), self.particleShapeName)))

#############################            
    def hideUI(self):
        self._attributesController.hideUI()
        self._behaviourAssignmentSelectionWindow.closeWindow()
        slef._leaderAgentsSelectionWindow.closeWindow()
 
#############################       
    def refreshInternals(self):
        self._attributesController.onFrameUpdated()
        self._behavioursController.onFrameUpdated()
        self._agentsController.refreshInternals()
        
        util.LogInfo("Refreshed internal state...")
        
#############################        
    def onFrameUpdated(self):
        self._attributesController.onFrameUpdated()
        
        if(self._attributesController.globalAttributes.enabled):
            self._behavioursController.onFrameUpdated()
            self._agentsController.onFrameUpdated()
        
#############################    
    def enable(self):
        if(not self._attributesController.globalAttributes.enabled):
            self._attributesController.globalAttributes.enabled = True
            util.LogInfo("updates are now ACTIVE.", self.particleShapeName)
        else:
            util.LogWarning("updates already enabled.", self.particleShapeName)

    def disable(self):
        self._attributesController.globalAttributes.enabled = False
        util.LogInfo("updates DISABLED.", self.particleShapeName)
        
#############################        
    def addClassicBoidBehaviour(self):
        self._attributesController.addClassicBoidAttributes()
        
    def addGoalDrivenBehaviour(self, wallLipGoal=None, basePyramidGoalHeight=None, finalGoal=None):
        self._attributesController.addGoalDrivenAttributes(wallLipGoal, basePyramidGoalHeight, finalGoal)
        
    def addFollowPathBehaviour(self, pathCurve=None):
        self._attributesController.addFollowPathAttributes(pathCurve)
        
#############################
    def onNewBehaviourAttributesAdded(self, newBehaviourAttributes):
        self._behavioursController.createBehaviourForNewAttributes(newBehaviourAttributes)

#############################        
    def requestedAssignAgentsToBehaviour(self, behaviourAttributes):
        behaviour = self._behavioursController.behaviourForAttributes(behaviourAttributes)
        currentSelection = self._agentsController.getAgentsFollowingBehaviour(behaviour)
        
        self._behaviourAssignmentSelectionWindow.dataBlob = behaviourAttributes
        self._behaviourAssignmentSelectionWindow.show("Assign agents to \"%s\"" % behaviourAttributes.sectionTitle(), 
                                        currentSelection, self._onAgentSelectionCompleted)

#############################        
    def requestedSelectAgentsWithBehaviour(self, behaviourAttributes, invertSelection):
        behaviour = self._behavioursController.behaviourForAttributes(behaviourAttributes)
        currentSelection = self._agentsController.getAgentsFollowingBehaviour(behaviour)
        if(invertSelection):
            allAgents = set(self._agentsController.allAgents)
            currentSelection = list(allAgents.difference(set(currentSelection)))
        
        particleIds = map(lambda agent: agent.particleId, currentSelection)
        util.SelectParticlesInList(particleIds, self.particleShapeName)    
        
#############################
    def requestedLeaderSelectForBehaviour(self, behaviourAttributes, isChangeSelectionRequest):
        behaviour = self._behavioursController.behaviourForAttributes(behaviourAttributes)
        currentSelection = behaviour.allLeaders()
        if(isChangeSelectionRequest):
            self._leaderAgentsSelectionWindow.dataBlob = behaviourAttributes
            self._leaderAgentsSelectionWindow.show("Select leader agents for \"%s\"" % behaviourAttributes.sectionTitle(),
                                               currentSelection, self._onAgentSelectionCompleted)
        else:
            particleIds = map(lambda agent: agent.particleId, currentSelection)
            util.SelectParticlesInList(particleIds, self.particleShapeName)

#############################        
    def onBehaviourAttributesDeleted(self, deletedAttributes):
        deletedBehaviour = self._behavioursController.removeBehaviourForAttributes(deletedAttributes)
        agentsFollowingOldBehaviour = self._agentsController.getAgentsFollowingBehaviour(deletedBehaviour)
        defaultAttributes = self._attributesController.defaultBehaviourAttributes
        defaultBehaviour = self._behavioursController.defaultBehaviour
        
        self._agentsController.makeAgentsFollowBehaviour(agentsFollowingOldBehaviour, defaultBehaviour, defaultAttributes)

#############################
    def requestedQuitSwarmInstance(self):
        util.EvalDeferred(RemoveSwarmInstance, self)
        
#############################        
    def _onAgentSelectionCompleted(self, selectionWindow, selectedAgentsList, selectionDisplayString):
        if(selectionWindow is self._behaviourAssignmentSelectionWindow):
            attributes = self._behaviourAssignmentSelectionWindow.dataBlob
            behaviour = self._behavioursController.behaviourForAttributes(attributes)
            
            self._agentsController.makeAgentsFollowBehaviour(selectedAgentsList, behaviour, attributes)
            self._behaviourAssignmentSelectionWindow.dataBlob = None
        elif(selectionWindow is self._leaderAgentsSelectionWindow):
            attributes = self._leaderAgentsSelectionWindow.dataBlob
            behaviour = self._behavioursController.behaviourForAttributes(attributes)
            
            for agent in selectedAgentsList:
                behaviour.makeLeader(agent)
            attributes.setLeadersAgentsTextDisplay(selectionDisplayString)
            self._leaderAgentsSelectionWindow.dataBlob = None
        

# END OF CLASS 
##################################