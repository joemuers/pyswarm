import classicBoid as cb
import goalDriven as gd
import followPath as fp

import weakref


##### TODO - mechanism for deleting a behaviour (& reassigning enlisted agents)
## - poss algorithm: change agent-has-behaviour to behaviour-has-agents??

class BehavioursControllerDelegate(object):
    
    def _onBehaviourDeleted(self, behaviour):
        raise NotImplemented

# END OF CLASS - BehavioursControllerDelegate
############################################


####################
class BehavioursController:
    
    def __init__(self, attributesController, negativeGridBounds, positiveGridBounds, delegate):
        if(delegate is not None and not issubclass(type(delegate), BehavioursControllerDelegate)):
            raise TypeError("Delegate must be subclass of BehavioursControllerDelegate.")
        
        self._attributesController = attributesController
        self._defaultBehaviour = cb.ClassicBoid(attributesController, negativeGridBounds, positiveGridBounds)
        self._behaviours = [self._defaultBehaviour]
        self._attributesController.addNewBehaviour(self._defaultBehaviour)
        self._delegate = weakref.ref(delegate)
        
#############################
    def _getDefaultBehaviour(self):
        return self._defaultBehaviour
    defaultBehaviour = property(_getDefaultBehaviour)
    
#############################        
    def _getDelegate(self):
        return self._delegate() if(self._delegate is not None) else None
    delegate = property(_getDelegate)

#############################    
    def _getAttributesController(self):
        return self._attributesController
    attributesController = property(_getAttributesController)
 
 ##
 ## TODO - handle default creation for diff behaviours
 ##
 
#############################       
    def createClassicBoidBehaviour(self, negativeGridBounds, positiveGridBounds):
        newBehaviour = cb.ClassicBoid(negativeGridBounds, positiveGridBounds)
        self._behaviours.append(newBehaviour)
        self._attributesController.addNewBehaviour(newBehaviour)
        if(self._attributesController.uiVisible):
            self._attributesController.buildUi()
        
        return newBehaviour

#############################    
    def createGoalDrivenBehaviour(self, basePos, lipPos, finalPos, useInfectionSpread, delegate=None):
        newBehaviour = gd.GoalDriven(basePos, lipPos, finalPos, self._defaultBehaviour, useInfectionSpread, delegate)
        self._behaviours.append(newBehaviour)
        self._attributesController.addNewBehaviour(newBehaviour)
        if(self._attributesController.uiVisible):
            self._attributesController.buildUi()
        
        return newBehaviour

#############################    
    def createFollowPathBehaviour(self, curve, delegate=None):
        newBehaviour = fp.FollowPath(curve, delegate)
        self._behaviours.append(newBehaviour)
        self._attributesController.addNewBehaviour(newBehaviour)
        if(self._attributesController.uiVisible):
            self._attributesController.buildUi()
        
        return newBehaviour

#############################    
    def onFrameUpdated(self):
        for behaviour in self._behaviours:
            behaviour.onFrameUpdated()
    
#############################
    def behaviourForIndex(self, index):
        return self._behaviours[index]
    
    def behaviourForAttributes(self, attributes):
        for behaviour in self._behaviours:
            if(attributes is behaviour.attributes):
                return behaviour
    
        raise ValueError("No behaviour found with attributes: %s" % attributes)

#############################    
    def removeBehaviour(self, behaviour):
        self._behaviours.remove(behaviour)
        self._attributesController.removeBehaviour(behaviour)
        # TODO - is this the best design...??
        if(self._delegate is not None):
            self.delegate._onBehaviourDeleted(behaviour)
        
        
    
# END OF CLASS
###############################################