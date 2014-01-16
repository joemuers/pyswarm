import attributesBaseObject as abo
import boidTools.uiBuilder as uib
import attributeTypes as at



##########################################
class PerceptionAttributesDataBlob(abo.DataBlobBaseObject):
    
    def __init__(self, agent):
        super(PerceptionAttributesDataBlob, self).__init__(agent)
        
        self.neighbourhoodSize = 0.0
        self.nearRegionSize = 0.0
        self.collisionRegionSize = 0.0
        
        self.blindRegionAngle = 0
        self.forwardVisionAngle = 0

#####################    
    def __str__(self):
        return ("<PERCEPTION: neighbSize=%.2f, nearSize=%.2f, collSize=%.2f, blindAng=%d, forwdAng=%d>" %
                (self.neighbourhoodSize, self.nearRegionSize, self.collisionRegionSize,
                 self.blindRegionAngle, self.forwardVisionAngle))

# END OF CLASS - MovementAttributesDataBlob
###########################################



##########################################
class AgentPerceptionAttributes(abo.AttributesBaseObject):
 
    @classmethod
    def DefaultSectionTitle(cls):
        return "Agent Awareness"
 
#####################   
    def __init__(self):
        super(AgentPerceptionAttributes, self).__init__(AgentPerceptionAttributes.DefaultSectionTitle())
        
        self._neighbourhoodSize = at.FloatAttribute("Neighbourhood Size", 4.0, self)
        self._neighbourhoodSize_Random = at.RandomizeController(self._neighbourhoodSize)
        self._nearRegionSize = at.FloatAttribute("Near Region Size", 1.0, self)
        self._nearRegionSize_Random = at.RandomizeController(self._nearRegionSize)
        self._collisionRegionSize = at.FloatAttribute("Collision Region Size", 0.1, self)
        self._collisionRegionSize_Random = at.RandomizeController(self._collisionRegionSize)
        
        self._blindRegionAngle = at.IntAttribute("Blind Region Angle", 110, self, maximumValue=359)
        self._blindRegionAngle_Random = at.RandomizeController(self._blindRegionAngle)
        self._forwardVisionAngle = at.IntAttribute("Forward Vision Angle", 90, self, maximumValue=359)
        self._forwardVisionAngle_Random = at.RandomizeController(self._forwardVisionAngle)   

##################### 
    def populateUiLayout(self):
        regionSizeFrame = uib.MakeFrameLayout("Region Size")
        
        uib.MakeSliderGroup(self._neighbourhoodSize)
        uib.MakeRandomizerFields(self._neighbourhoodSize_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._nearRegionSize)
        uib.MakeRandomizerFields(self._nearRegionSize_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._collisionRegionSize)
        uib.MakeRandomizerFields(self._collisionRegionSize_Random)
        uib.SetAsChildLayout(regionSizeFrame)
        
        fieldOfVisionFrame = uib.MakeFrameLayout("Field of Vision")
        uib.MakeSliderGroup(self._blindRegionAngle)
        uib.MakeRandomizerFields(self._blindRegionAngle_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._forwardVisionAngle)
        uib.MakeRandomizerFields(self._forwardVisionAngle_Random)
        uib.SetAsChildLayout(fieldOfVisionFrame)
        
#####################        
    def _createDataBlobForAgent(self, agent):
        return PerceptionAttributesDataBlob(agent)

#####################    
    def _updateDataBlobWithAttribute(self, dataBlob, attribute):
        if(attribute is self._neighbourhoodSize):
            dataBlob.neighbourhoodSize = self._getNeighbourhoodSizeForBlob(dataBlob)
        elif(attribute is self._nearRegionSize):
            dataBlob.nearRegionSize = self._getNearRegionSizeForBlob(dataBlob)
        elif(attribute is self._collisionRegionSize):
            dataBlob.collisionRegionSize = self._getCollisionRegionSizeForBlob(dataBlob)
        elif(attribute is self._blindRegionAngle):
            dataBlob.blindRegionAngle = self._getBlindRegionAngleForBlob(dataBlob)
        elif(attribute is self._forwardVisionAngle):
            dataBlob.forwardVisionAngle = self._getForwardVisionAngleForBlob(dataBlob)

#####################         
    def _getMaxNeighbourhoodSize(self):
        return (self._neighbourhoodSize.value + 
                (self._neighbourhoodSize.value * self._neighbourhoodSize_Random.randomizeMultiplierAttribute))
    maxNeighbourhoodSize = property(_getMaxNeighbourhoodSize)

#####################
    def _getNeighbourhoodSizeForBlob(self, dataBlob):
        return self._neighbourhoodSize_Random.valueForIntegerId(dataBlob.agentId)
    
    def _getNearRegionSizeForBlob(self, dataBlob):
        return self._nearRegionSize_Random.valueForIntegerId(dataBlob.agentId)
    
    def _getCollisionRegionSizeForBlob(self, dataBlob):
        return self._collisionRegionSize_Random.valueForIntegerId(dataBlob.agentId)
        
    def _getBlindRegionAngleForBlob(self, dataBlob):
        return self._blindRegionAngle_Random.valueForIntegerId(dataBlob.agentId)
    
    def _getForwardVisionAngleForBlob(self, dataBlob):
        return self._forwardVisionAngle_Random.valueForIntegerId(dataBlob.agentId)

# END OF CLASS
###############################    
