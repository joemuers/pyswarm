from boidBaseObject import BoidBaseObject

import boidAgents.boidAgentsController as bac
import boidAttributes.attributesController as bat
import boidBehaviours.behavioursController as bbc
import boidTools.util as util



class SwarmController(BoidBaseObject, bbc.BehavioursControllerDelegate):
    
    # TODO - handle cases where args==None
    def __init__(self, particleShapeNode=None, cornerLocatorA=None, cornerLocatorB=None):
        locatorObjA = util.PymelObjectFromObjectName(cornerLocatorA)
        locatorObjB = util.PymelObjectFromObjectName(cornerLocatorB)
        boundingVectors = util.BoidVectorOrderedPairFromPymelLocators(locatorObjA, locatorObjB)
        
        self.attributesController = bat.AttributesController()
        self.behavioursController = bbc.BehavioursController(self.attributesController, 
                                                             boundingVectors[0], 
                                                             boundingVectors[1], 
                                                             self)
        self.agentsController = bac.BoidAgentsController(self.behavioursController,
                                                         util.PymelObjectFromObjectName(particleShapeNode), 
                                                         boundingVectors[0], 
                                                         boundingVectors[1])
        
#############################        
    def onFrameUpdated(self):
        if(self.attributesController.globalAttributes.enabled):
            self.behavioursController.onFrameUpdated()
            self.agentsController.onFrameUpdated()
        
#############################    
    def activate(self):
        if(not self._attributesController.globalAttributes.enabled):
            self._attributesController.globalAttributes.enabled = True
            util.LogInfo("updates are now ACTIVE.", self.agentsController.particleShapeName)
        else:
            util.LogWarning("updates already active.", self.agentsController.particleShapeName)

    def deactivate(self):
        self._attributesController.globalAttributes.enabled = False
        util.LogInfo("updates DEACTIVATED", self.agentsController.particleShapeName)
        
#############################
    def _onBehaviourDeleted(self, behaviour):
        # TODO
        bbc.BehavioursControllerDelegate._onBehaviourDeleted(self, behaviour)
        

# END OF CLASS 
##################################