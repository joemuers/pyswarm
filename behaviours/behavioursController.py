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
from behaviourBaseObject import BehaviourDelegate

import classicBoid as cb
import goalDriven as gd
import followPath as fp



#######################################
class BehavioursController(PyswarmObject, BehaviourDelegate):
    
    def __init__(self, attributeGroupsController):
        self._attributeGroupsController = attributeGroupsController
        self._behavioursLookup = {}
        defaultAttributes = attributeGroupsController.getBehaviourAttributesWithId(attributeGroupsController.defaultBehaviourId)
        self.createBehaviourForNewAttributes(defaultAttributes)
        
#############################
    def _getDefaultBehaviour(self):
        return self.behaviourWithId(self._attributeGroupsController.defaultBehaviourId)
    defaultBehaviour = property(_getDefaultBehaviour)
         
#############################    
    def onFrameUpdated(self):
        for behaviour in self._behavioursLookup.itervalues():
            behaviour.onFrameUpdated()
            
########
    def onCalculationsCompleted(self):
        for behaviour in self._behavioursLookup.itervalues():
            behaviour.onCalculationsCompleted()
         
#############################    
    def behaviourWithId(self, behaviourId):
        return self._behavioursLookup[behaviourId]
       
########
    def createBehaviourForNewAttributes(self, newAttributes):
        if(cb.AttributesAreClassicBoid(newAttributes)):
            newBehaviour = cb.ClassicBoid(newAttributes, self._attributeGroupsController)
        elif(gd.AttributesAreGoalDriven(newAttributes)):
            newBehaviour = gd.GoalDriven(newAttributes, self.defaultBehaviour, self)
        elif(fp.AttributesAreFollowPath(newAttributes)):
            newBehaviour = fp.FollowPath(newAttributes, self.defaultBehaviour, self)
        else:
            raise RuntimeError("Cannot create new behavior, unrecognised attribute type: %s" % type(newAttributes))
        
        self._behavioursLookup[newBehaviour.behaviourId] = newBehaviour
    
########
    def removeBehaviourWithId(self, behaviourId):
        deletedBehaviour = self._behavioursLookup.pop(behaviourId)
        
        return deletedBehaviour

#############################        
    def onBehaviourEndedForAgent(self, agent, behaviour, followOnBehaviourID):
        if(followOnBehaviourID is not None):
            followOnBehaviour = self._behavioursLookup[followOnBehaviourID]
            followOnBehaviour.assignAgent(agent)
        
    
# END OF CLASS
###############################################