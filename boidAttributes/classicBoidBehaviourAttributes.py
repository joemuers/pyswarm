import attributesBaseObject as abo
import attributeTypes as at
import boidTools.uiBuilder as uib



###########################################
class ClassicBoidDataBlob(abo.DataBlobBaseObject):
    
    def __init__(self, agent):
        super(ClassicBoidDataBlob, self).__init__(agent)
        
        self.alignmentDirectionThreshold = 0
        self.cohesionPositionThreshold = 0.0
        
#####################
    def __str__(self):
        return ("<CLASSIC BHVR: align=%d, cohesn=%.2f>" % 
                (self.alignmentDirectionThreshold, self.cohesionPositionThreshold))
    
# END OF CLASS - ClassicBoidDataBlob
###########################################



###########################################
class ClassicBoidBehaviourAttributes(abo.AttributesBaseObject):
    
    def __init__(self):
        super(ClassicBoidBehaviourAttributes, self).__init__()
        
        self._alignmentDirectionThreshold = at.IntAttribute("Alignment Threshold", 30, self, maximumValue=359)
        self._alignmentDirectionThreshold_Random = at.RandomizerAttribute(self._alignmentDirectionThreshold)
        self._cohesionPositionThreshold = at.FloatAttribute("Cohesion Threshold", 1.9, self)
        self._cohesionPositionThreshold_Random = at.RandomizerAttribute(self._cohesionPositionThreshold)

#####################         
    def sectionTitle(self):
        return "Classic Boid Behaviour"
    
#####################
    def populateUiLayout(self):
        uib.MakeSliderGroup(self._alignmentDirectionThreshold)
        uib.MakeRandomizerGroup(self._alignmentDirectionThreshold_Random)
        
        uib.MakeSeparator()
        
        uib.MakeSliderGroup(self._cohesionPositionThreshold)
        uib.MakeRandomizerGroup(self._cohesionPositionThreshold_Random)
        
#####################
    def _createDataBlobForAgent(self, agent):
        return ClassicBoidDataBlob(agent)
    
#####################
    def _updateDataBlobWithAttribute(self, dataBlob, attribute):
        if(attribute is self._alignmentDirectionThreshold):
            dataBlob.alignmentDirectionThreshold = self._getAlignmentDirectionThresholdForBlob(dataBlob)
        elif(attribute is self._cohesionPositionThreshold):
            dataBlob.cohesionPositionThreshold = self._getCohesionPositionThresholdForBlob(dataBlob)

#####################         
    def _getAlignmentDirectionThresholdForBlob(self, dataBlob):
        return self._alignmentDirectionThreshold_Random.getRandomizedValueForIntegerId(dataBlob.agentId)
        
    def _getCohesionPositionThresholdForBlob(self, dataBlob):
        return self._cohesionPositionThreshold_Random.getRandomizedValueForIntegerId(dataBlob.agentId)

# END OF CLASS
##############################    
