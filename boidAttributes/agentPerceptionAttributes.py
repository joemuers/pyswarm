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
    
    def __init__(self):
        super(AgentPerceptionAttributes, self).__init__()
        
        self._neighbourhoodSize = at.FloatAttribute("Neighbourhood Size", 4.0, self)
        self._neighbourhoodSize_Random = at.RandomizerAttribute(self._neighbourhoodSize)
        self._nearRegionSize = at.FloatAttribute("Near Region Size", 1.0, self)
        self._nearRegionSize_Random = at.RandomizerAttribute(self._nearRegionSize)
        self._collisionRegionSize = at.FloatAttribute("Collision Region Size", 0.1, self)
        self._collisionRegionSize_Random = at.RandomizerAttribute(self._collisionRegionSize)
        
        self._blindRegionAngle = at.IntAttribute("Blind Region Angle", 110, self, maximumValue=359)
        self._blindRegionAngle_Random = at.RandomizerAttribute(self._blindRegionAngle)
        self._forwardVisionAngle = at.IntAttribute("Forward Vision Angle", 90, self, maximumValue=359)
        self._forwardVisionAngle_Random = at.RandomizerAttribute(self._forwardVisionAngle)   

#####################    
    def sectionTitle(self):
        return "Agent Awareness"

##################### 
    def populateUiLayout(self):
        
        uib.MakeSliderGroup(self._neighbourhoodSize)
        uib.MakeRandomizerGroup(self._neighbourhoodSize_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._nearRegionSize)
        uib.MakeRandomizerGroup(self._nearRegionSize_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._collisionRegionSize)
        uib.MakeRandomizerGroup(self._collisionRegionSize_Random)
        uib.MakeSeparator()
        
        uib.MakeSliderGroup(self._blindRegionAngle)
        uib.MakeRandomizerGroup(self._blindRegionAngle_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._forwardVisionAngle)
        uib.MakeRandomizerGroup(self._blindRegionAngle_Random)
        
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
        return self._neighbourhoodSize.value + (self._neighbourhoodSize.value * self._neighbourhoodSize_Random.value)
    maxNeighbourhoodSize = property(_getMaxNeighbourhoodSize)

#####################
    def _getNeighbourhoodSizeForBlob(self, dataBlob):
        return self._neighbourhoodSize_Random.getRandomizedValueForIntegerId(dataBlob.agentId)
    
    def _getNearRegionSizeForBlob(self, dataBlob):
        return self._nearRegionSize_Random.getRandomizedValueForIntegerId(dataBlob.agentId)
    
    def _getCollisionRegionSizeForBlob(self, dataBlob):
        return self._collisionRegionSize_Random.getRandomizedValueForIntegerId(dataBlob.agentId)
        
    def _getBlindRegionAngleForBlob(self, dataBlob):
        return self._blindRegionAngle_Random.getRandomizedValueForIntegerId(dataBlob.agentId)
    
    def _getForwardVisionAngleForBlob(self, dataBlob):
        return self._forwardVisionAngle_Random.getRandomizedValueForIntegerId(dataBlob.agentId)

# END OF CLASS
###############################    
