from boidBaseObject import BoidBaseObject
from behaviourBaseObject import BehaviourDelegate

import classicBoid as cb
import goalDriven as gd
import followPath as fp


##### TODO - mechanism for deleting a behaviour (& reassigning enlisted agents)
## - poss algorithm: change agent-has-behaviour to behaviour-has-agents??



#######################################
class BehavioursController(BoidBaseObject, BehaviourDelegate):
    
    def __init__(self, attributesController, agentsController):
        self._attributesController = attributesController
        self._agentsController = agentsController
        self._attributesBehavioursLookup = {}
        self.createBehaviourForNewAttributes(attributesController.defaultBehaviourAttributes)
        
        agentsController.defaultBehaviourMethod = self._getDefaultBehaviour
        
#############################
    def _getDefaultBehaviour(self):
        return self.behaviourForAttributes(self._attributesController.defaultBehaviourAttributes)
    defaultBehaviour = property(_getDefaultBehaviour)
 
#############################
    def createBehaviourForNewAttributes(self, newAttributes):
        newBehaviour = None
        if(cb.AttributesAreClassicBoid(newAttributes)):
            newBehaviour = cb.ClassicBoid(newAttributes, self._attributesController)
        elif(gd.AttributesAreGoalDriven(newAttributes)):
            newBehaviour = gd.GoalDriven(newAttributes, self.defaultBehaviour, self)
        elif(fp.AttributesAreFollowPath(newAttributes)):
            newBehaviour = fp.FollowPath(newAttributes, self.defaultBehaviour, self)
        
        if(newBehaviour is not None):
            self._attributesBehavioursLookup[newAttributes] = newBehaviour
            return True
        else:
            return False
        
#############################    
    def onFrameUpdated(self):
        for behaviour in self._attributesBehavioursLookup.itervalues():
            behaviour.onFrameUpdated()
    
#############################    
    def behaviourForAttributes(self, attributes):
        return self._attributesBehavioursLookup[attributes]

#############################    
    def removeBehaviourForAttributes(self, behaviourAttributes):
        deletedBehaviour = self.behaviourForAttributes(behaviourAttributes)
        del self._attributesBehavioursLookup[behaviourAttributes]
        
        return deletedBehaviour

#############################        
    def onBehaviourEndedForAgent(self, agent, behaviour, followOnBehaviourID):
        if(followOnBehaviourID is not None):
            for behaviour in self._attributesBehavioursLookup.itervalues():
                if(behaviour.behaviourId == followOnBehaviourID):
                    agent.setNewBehaviour(behaviour, behaviour.attributes)
        
    
# END OF CLASS
###############################################