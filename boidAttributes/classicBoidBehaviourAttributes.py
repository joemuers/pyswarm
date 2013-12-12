import attributesBaseObject as abo
import attributeTypes as at


class ClassicBoidBehaviourAttributes(abo.AttributesBaseObject):
    
    def __init__(self):
        super(ClassicBoidBehaviourAttributes, self).__init__()
        
        self._herdAverageDirectionThreshold = at.IntAttribute("herdAverageDirectionThreshold", 30, 
                                                              "herdAverageDirectionThreshold_Random", 0.0, self)
        self._herdAveragePositionThreshold = at.FloatAttribute("herdAveragePositionThreshold", 1.9, 
                                                               "herdAveragePositionThreshold_Random", 0.0, self)

#####################         
    def _sectionTitle(self):
        return "Classic Boid behaviour"
    
#####################    
    def makeFrameLayout(self):
        thresholdsFrame = at.MakeFrameLayout(self._sectionTitle())
        
        directionFrame = self._herdAverageDirectionThreshold.makeFrameLayout("Direction threshold", "max degrees", 0, 359)
        at.SetAsChildToPrevious(directionFrame)
        positionFrame = self._herdAveragePositionThreshold.makeFrameLayout("Position threshold", "max distance", 0)
        at.SetAsChildToPrevious(positionFrame)
        
        return thresholdsFrame

#####################         
    def _getHerdAverageDirectionThreshold(self):
        return self._herdAverageDirectionThreshold.value
    def _setHerdAverageDirectionThreshold(self, value):
        self._herdAverageDirectionThreshold.value = value
    herdAverageDirectionThreshold = property(_getHerdAverageDirectionThreshold, _setHerdAverageDirectionThreshold)

#####################         
    def _getHerdAverageDirectionThreshold_Random(self):
        return self._herdAverageDirectionThreshold.randomizerValue
    def _setHerdAverageDirectionThreshold_Random(self, value):
        self._herdAverageDirectionThreshold.randomizerValue = value
    herdAverageDirectionThreshold_Random = property(_getHerdAverageDirectionThreshold_Random, _setHerdAverageDirectionThreshold_Random)

#####################         
    def _getHerdAveragePositionThreshold(self):
        return self._herdAveragePositionThreshold.value
    def _setHerdAveragePositionThreshold(self, value):
        self._herdAveragePositionThreshold.value = value
    herdAveragePositionThreshold = property(_getHerdAveragePositionThreshold, _setHerdAveragePositionThreshold)

#####################     
    def _getHerdAveragePositionThreshold_Random(self):
        return self._herdAveragePositionThreshold.randomizerValue
    def _setHerdAveragePositionThreshold_Random(self, value):
        self._herdAveragePositionThreshold.randomizerValue = value
    herdAveragePositionThreshold_Random = property(_getHerdAveragePositionThreshold_Random, _setHerdAveragePositionThreshold_Random)

# END OF CLASS
##############################    
