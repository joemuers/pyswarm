import attributesBaseObject as abo
import attributeTypes as at


class AgentAwarenessAttributes(abo.AttributesBaseObject):
    
    def __init__(self):
        super(AgentAwarenessAttributes, self).__init__()
        
        self._mainRegionSize = at.FloatAttribute("mainRegionSize", 4.0, "mainRegionSize_Random", 0.0, self)
        self._nearRegionSize = at.FloatAttribute("nearRegionSize", 1.0, "nearRegionSize_Random", 0.0, self)
        self._collisionRegionSize = at.FloatAttribute("collisionRegionSize", 0.1, "collisionRegionSize_Random", 0.0, self)
        self._blindRegionAngle = at.IntAttribute("blindRegionAngle", 110, "blindRegionAngle_Random", 0.0, self)
        self._forwardVisionAngle = at.IntAttribute("forwardVisionAngle", 90, "forwardVisionAngle_Random", 0.0, self)   
 
#####################    
    def _sectionTitle(self):
        return "Agent awareness"

##################### 
    def makeFrameLayout(self):
        mainFrame = at.MakeFrameLayout(self._sectionTitle())
        
        mainRegionSizeLayout = self._mainRegionSize.makeFrameLayout("neighbourhood area", "radius", 0)
        at.SetAsChildToPrevious(mainRegionSizeLayout)
        
        nearRegionSizeLayout = self._nearRegionSize.makeFrameLayout("near region area", "radius", 0)
        at.SetAsChildToPrevious(nearRegionSizeLayout)
        
        collisionRegionSizeLayout = self._collisionRegionSize.makeFrameLayout("collision size", "radius", 0)
        at.SetAsChildToPrevious(collisionRegionSizeLayout)
        
        blindRegionAngleLayout = self._blindRegionAngle.makeFrameLayout("blind region", "angle", 0, 359)
        at.SetAsChildToPrevious(blindRegionAngleLayout)
        
        forwardVisionAngleLayout = self._forwardVisionAngle.makeFrameLayout("forward vision", "angle", 0, 359)
        at.SetAsChildToPrevious(forwardVisionAngleLayout)
        
        return mainFrame
        
    
#####################         
    def _getMainRegionSize(self):
        return self._mainRegionSize.value
    def _setMainRegionSize(self, value):
        self._mainRegionSize.value = value
        newValue = self._mainRegionSize.value

        self._mainRegionTextField.setValue(newValue)
        if(newValue > self._mainRegionSlider.getMaxValue()):
            self._mainRegionSlider.setMaxValue(newValue * 1.5)
        self._mainRegionSlider.setValue(newValue)
    mainRegionSize = property(_getMainRegionSize, _setMainRegionSize)

#####################     
    def _getMainRegionSize_Random(self):
        return self._mainRegionSize.randomizerValue
    def _setMainRegionSize_Random(self, value):
        self._mainRegionSize.randomizerValue = value
    mainRegionSize_Random = property(_getMainRegionSize_Random, _setMainRegionSize_Random)

#####################     
    def _getNearRegionSize(self):
        return self._nearRegionSize.value
    def _setNearRegionSize(self, value):
        self._nearRegionSize.value = value
    nearRegionSize = property(_getNearRegionSize, _setNearRegionSize)

#####################     
    def _getNearRegionSize_Random(self):
        return self._nearRegionSize.randomizerValue
    def _setNearRegionSize_Random(self, value):
        self._nearRegionSize.randomizerValue = value
    nearRegionSize_Random = property(_getNearRegionSize_Random, _setNearRegionSize_Random)

#####################     
    def _getCollisionRegionSize(self):
        return self._collisionRegionSize.value
    def _setCollisionRegionSize(self, value):
        self._collisionRegionSize.value = value
    collisionRegionSize = property(_getCollisionRegionSize, _setCollisionRegionSize)

#####################     
    def _getCollisionRegionSize_Random(self):
        return self._collisionRegionSize.randomizerValue
    def _setCollisionRegionSize_Random(self, value):
        self._collisionRegionSize.randomizerValue = value
    collisionRegionSize_Random = property(_getCollisionRegionSize_Random, _setCollisionRegionSize_Random)
 
#####################         
    def _getBlindRegionAngle(self):
        return self._blindRegionAngle.value
    def _setBlindRegionAngle(self, value):
        newValue = int(value)
        if(newValue < 0 or 360 < newValue):
            raise ValueError("Angle attribute must be between 0 and 360 (got %s)" % value)
        else:
            self._blindRegionAngle.value = newValue
    blindRegionAngle = property(_getBlindRegionAngle, _setBlindRegionAngle)

#####################     
    def _getBlindRegionAngle_Random(self):
        return self._blindRegionAngle.randomizerValue
    def _setBlindRegionAngle_Random(self, value):
        self._blindRegionAngle.randomizerValue = value
    blindRegionAngle_Random = property(_getBlindRegionAngle_Random, _setBlindRegionAngle_Random)

#####################     
    def _getForwardVisionAngle(self):
        return self._forwardVisionAngle.value
    def _setForwardVisionAngle(self, value):
        newValue = int(value)
        if(newValue < 0 or 360 < newValue):
            raise ValueError("Angle attribute must be between 0 and 360 (got %s)" % value)
        else:
            self._forwardVisionAngle.value = newValue
    forwardVisionAngle = property(_getForwardVisionAngle, _setForwardVisionAngle)

#####################     
    def _getForwardVisionAngle_Random(self):
        return self._forwardVisionAngle.randomizerValue
    def _setForwardVisionAngle_Random(self, value):
        self._forwardVisionAngle.randomizerValue = value
    forwardVisionAngle_Random = property(_getForwardVisionAngle_Random, _setForwardVisionAngle_Random)
    

# END OF CLASS
###############################    
