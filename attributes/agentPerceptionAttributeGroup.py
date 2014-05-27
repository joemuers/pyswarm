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


import pyswarm.ui.uiBuilder as uib

import pyswarm.attributes.attributeGroupObject as ago
import pyswarm.attributes.attributeTypes as at



##########################################
class PerceptionAttributesDataBlob(ago._DataBlobBaseObject):
    
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
class AgentPerceptionAttributeGroup(ago.AttributeGroupObject):
    
    _WeightingNone_, _WeightingLinear_, _WeightingInverseSquare_ = range(3)
    _WeightingStrings_ = ["None", "Linear", "Inverse Square"]
 
#####################
    @classmethod
    def BehaviourTypeName(cls):
        return "Agent Awareness"
 
#####################   
    def __init__(self):
        super(AgentPerceptionAttributeGroup, self).__init__(AgentPerceptionAttributeGroup.BehaviourTypeName())
        
        self._proximityWeightingOption = AgentPerceptionAttributeGroup._WeightingInverseSquare_
        self._proximityWeightingString = at.StringAttribute("Proximity Weighting", 
                                                      AgentPerceptionAttributeGroup._WeightingStrings_[self._proximityWeightingOption],
                                                      self)
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
        
        self.onValueChanged(self._neighbourhoodSize) # sets up the min/max values for regions

##################### 
    def populateUiLayout(self):
        regionSizeFrame = uib.MakeFrameLayout("Region Size")
        columnLayout = uib.MakeColumnLayout()
        
        uib.MakeStringOptionsField(self._proximityWeightingString, AgentPerceptionAttributeGroup._WeightingStrings_)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._neighbourhoodSize, self._getNeighbourhoodSizeForBlob.__doc__)
        uib.MakeRandomizerFields(self._neighbourhoodSize_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._nearRegionSize, self._getNearRegionSizeForBlob.__doc__)
        uib.MakeRandomizerFields(self._nearRegionSize_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._collisionRegionSize, self._getCollisionRegionSizeForBlob.__doc__)
        uib.MakeRandomizerFields(self._collisionRegionSize_Random)
        uib.SetAsChildLayout(columnLayout, regionSizeFrame)
        
        fieldOfVisionFrame = uib.MakeFrameLayout("Field of Vision")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeSliderGroup(self._blindRegionAngle, self._getBlindRegionAngleForBlob.__doc__)
        uib.MakeRandomizerFields(self._blindRegionAngle_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._forwardVisionAngle, self._getForwardVisionAngleForBlob.__doc__)
        uib.MakeRandomizerFields(self._forwardVisionAngle_Random)
        uib.SetAsChildLayout(columnLayout, fieldOfVisionFrame)
        
#####################        
    def _createDataBlobForAgent(self, agent):
        return PerceptionAttributesDataBlob(agent)

#########
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
    def onValueChanged(self, changedAttribute):
        super(AgentPerceptionAttributeGroup, self).onValueChanged(changedAttribute)
        
        if(changedAttribute is self._neighbourhoodSize):
            self._nearRegionSize.maximumValue = self._neighbourhoodSize.value
        elif(changedAttribute is self._nearRegionSize):
            self._collisionRegionSize.maximumValue = self._nearRegionSize.value
        elif(changedAttribute is self._proximityWeightingString):
            self._proximityWeightingOption = AgentPerceptionAttributeGroup._WeightingStrings_.index(changedAttribute.value)

#####################         
    def _getMaxNeighbourhoodSize(self):
        """Largest possible radius size for neighbourhood region of any agent in this swarm instance."""
        
        return (self._neighbourhoodSize.value + 
                (self._neighbourhoodSize.value * self._neighbourhoodSize_Random.randomizeMultiplierAttribute))
    maxNeighbourhoodSize = property(_getMaxNeighbourhoodSize)

#####################
    def _getUseNoWeighting(self):
        """Returns True if preferential weightings should *not* be applied to other agents within an agents neighbourhood region."""
        
        return self._proximityWeightingOption == AgentPerceptionAttributeGroup._WeightingNone_
    useNoWeighting = property(_getUseNoWeighting)

########    
    def _getUseLinearWeighting(self):
        """Returns True if linear weighting, based on distance, should be applied to other agents within an agent's neighbourhood region."""
        
        return self._proximityWeightingOption == AgentPerceptionAttributeGroup._WeightingLinear_
    useLinearWeighting = property(_getUseLinearWeighting)

########    
    def _getUseInverseSquareWeighting(self):
        """Returns True if weightings, derived as an inverse square of distance, should be applied 
            to other agents within an agent's neighbourhood region."""
            
        return self._proximityWeightingOption == AgentPerceptionAttributeGroup._WeightingInverseSquare_
    useInverseSquareWeighting = property(_getUseInverseSquareWeighting)
    
########
    def _getNeighbourhoodSizeForBlob(self, dataBlob):
        """Radius of agent's "neighbourhood" - the region within which it is aware of other agents and reacts to them."""
        
        return self._neighbourhoodSize_Random.valueForIntegerId(dataBlob.agentId)
    
########
    def _getNearRegionSizeForBlob(self, dataBlob):
        """Radius of region within which other agents are considered to be within very close proximity (i.e. too close) to an agent."""
        
        return self._nearRegionSize_Random.valueForIntegerId(dataBlob.agentId)
    
########
    def _getCollisionRegionSizeForBlob(self, dataBlob):
        """Radius of region within which other agents are considered to have collided with an agent."""
        
        return self._collisionRegionSize_Random.valueForIntegerId(dataBlob.agentId)
        
########
    def _getBlindRegionAngleForBlob(self, dataBlob):
        """Angle of vision *behind* an agent, within which it is unaware of other agents, regardless of proximity."""
        
        return self._blindRegionAngle_Random.valueForIntegerId(dataBlob.agentId)
    
########
    def _getForwardVisionAngleForBlob(self, dataBlob):
        """Angle of vision in front of an agent within which it will have a preferential awareness of other nearby agents."""
        return self._forwardVisionAngle_Random.valueForIntegerId(dataBlob.agentId)

# END OF CLASS
###############################    
