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


from pyswarm.pyswarmObject import PyswarmObject

from pyswarm.behaviours.behaviourBaseObject import BehaviourDelegate
import pyswarm.behaviours.classicBoid as cb
import pyswarm.behaviours.worldWarZ as gd
import pyswarm.behaviours.followPath as fp



#######################################
class BehavioursController(PyswarmObject, BehaviourDelegate):
    
    def __init__(self, attributeGroupsController):
        self._attributeGroupsController = attributeGroupsController
        self._behavioursLookup = {}
        defaultAttributeGroup = attributeGroupsController.getBehaviourAttributeGroupWithId(attributeGroupsController.defaultBehaviourId)
        self.createBehaviourForNewAttributeGroup(defaultAttributeGroup)
        
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
    def createBehaviourForNewAttributeGroup(self, newAttributeGroup):
        if(cb.AttributesAreClassicBoid(newAttributeGroup)):
            newBehaviour = cb.ClassicBoid(newAttributeGroup, self._attributeGroupsController)
        elif(gd.AttributesAreWorldWarZ(newAttributeGroup)):
            newBehaviour = gd.WorldWarZ(newAttributeGroup, self.defaultBehaviour, self)
        elif(fp.AttributesAreFollowPath(newAttributeGroup)):
            newBehaviour = fp.FollowPath(newAttributeGroup, self.defaultBehaviour, self)
        else:
            raise RuntimeError("Cannot create new behavior, unrecognised attribute type: %s" % type(newAttributeGroup))
        
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