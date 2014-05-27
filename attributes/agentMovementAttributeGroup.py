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
class MovementAttributesDataBlob(ago._DataBlobBaseObject):
    
    def __init__(self, agent):
        super(MovementAttributesDataBlob, self).__init__(agent)
        
        self.maxVelocity = 0.0
        self.preferredVelocity = 0.0
        self.maxAcceleration = 0.0
        self.maxTurnRate = 0
        self.preferredTurnVelocity = 0.0
        self.jumpAcceleration = 0.0

#####################
    def __str__(self):
        return ("<MOVEMENT: maxVel=%.2f, prefVel=%.2f, maxAccel=%.2f, maxTurn=%.2f, prefTurn=%.2f, jump=%.2f>" %
                (self.maxVelocity, self.preferredVelocity, self.maxAcceleration,
                 self.maxTurnRate, self.preferredTurnVelocity, self.jumpAcceleration))

# END OF CLASS - MovementAttributesDataBlob
###########################################


        
##########################################
class AgentMovementAttributeGroup(ago.AttributeGroupObject):
    
    @classmethod
    def BehaviourTypeName(cls):
        return "Agent Movement"
    
######################
    def __init__(self):
        super(AgentMovementAttributeGroup, self).__init__(AgentMovementAttributeGroup.BehaviourTypeName())
        
        self._maxVelocity = at.FloatAttribute("Max Velocity", 5.0, self)
        self._maxVelocity_Random = at.RandomizeController(self._maxVelocity)
        self._minVelocity = at.FloatAttribute("Min Velocity", 0.5)
        self._preferredVelocity = at.FloatAttribute("Preferred Velocity", 3.5, self)
        self._preferredVelocity_Random = at.RandomizeController(self._preferredVelocity)
        self._maxAcceleration = at.FloatAttribute("Max Acceleration", 1.0, self)
        self._maxAcceleration_Random = at.RandomizeController(self._maxAcceleration)
        
        self._maxTurnRate = at.IntAttribute("Max Turn Rate", 5, self, maximumValue=359)
        self._maxTurnRate_Random = at.RandomizeController(self._maxTurnRate)
        self._maxTurnRateChange = at.IntAttribute("Max Turn Rate Change", 4, maximumValue=359)
        self._preferredTurnVelocity = at.FloatAttribute("Preferred Turn Velocity", 0.5, self)
        self._preferredTurnVelocity_Random = at.RandomizeController(self._preferredTurnVelocity)
        
        self._jumpAcceleration = at.FloatAttribute("Jump Acceleration", 65, self)
        self._jumpAcceleration_Random = at.RandomizeController(self._jumpAcceleration)

#####################     
    def populateUiLayout(self):
        speedFrameLayout = uib.MakeFrameLayout("Speed")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeSliderGroup(self._maxVelocity, self._getMaxVelocityForBlob.__doc__)
        uib.MakeRandomizerFields(self._maxVelocity_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._minVelocity, self._getMinVelocity.__doc__)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._preferredVelocity, self._getPreferredVelocityForBlob.__doc__)
        uib.MakeRandomizerFields(self._preferredVelocity_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._maxAcceleration, self._getMaxAccelerationForBlob.__doc__)
        uib.MakeRandomizerFields(self._maxAcceleration_Random)
        uib.SetAsChildLayout(columnLayout, speedFrameLayout)
        
        turnFrameLayout = uib.MakeFrameLayout("Turning")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeSliderGroup(self._maxTurnRate, self._getMaxTurnRateForBlob.__doc__)
        uib.MakeRandomizerFields(self._maxTurnRate_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._maxTurnRateChange, self._getMaxTurnRateChange.__doc__)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._preferredTurnVelocity, self._getPreferredTurnVelocityForBlob.__doc__)
        uib.MakeRandomizerFields(self._preferredTurnVelocity_Random)
        uib.SetAsChildLayout(columnLayout, turnFrameLayout)
        
        miscellaneousFrameLayout = uib.MakeFrameLayout("Misc.")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeSliderGroup(self._jumpAcceleration, self._getJumpAccelerationForBlob.__doc__)
        uib.MakeRandomizerFields(self._jumpAcceleration_Random)
        uib.SetAsChildLayout(columnLayout, miscellaneousFrameLayout)
        
#####################
    def _createDataBlobForAgent(self, agent):
        return MovementAttributesDataBlob(agent)
       
#####################        
    def _updateDataBlobWithAttribute(self, dataBlob, attribute):
        if(attribute is self._maxVelocity):
            dataBlob.maxVelocity = self._getMaxVelocityForBlob(dataBlob)
        elif(attribute is self._preferredVelocity):
            dataBlob.preferredVelocity = self._getPreferredVelocityForBlob(dataBlob)
        elif(attribute is self._maxAcceleration):
            dataBlob.maxAcceleration = self._getMaxAccelerationForBlob(dataBlob)
        elif(attribute is self._maxTurnRate):
            dataBlob.maxTurnRate = self._getMaxTurnRateForBlob(dataBlob)
        elif(attribute is self._preferredTurnVelocity):
            dataBlob.preferredTurnVelocity = self._getPreferredTurnVelocityForBlob(dataBlob)
        elif(attribute is self._jumpAcceleration):
            dataBlob.jumpAcceleration = self._getJumpAccelerationForBlob(dataBlob)       
        
#####################     
    def _getMinVelocity(self):
        """Agents travelling slower than this velocity under normal behaviuor will be accelerated."""
        
        return self._minVelocity.value
    minVelocity  = property(_getMinVelocity) 
    
#####################     
    def _getMaxTurnRateChange(self):
        """The maximum rate of change in how sharply an agent is turning, i.e. the angular acceleration."""
        
        return self._maxTurnRateChange.value
    maxTurnRateChange = property(_getMaxTurnRateChange)
          
#####################     
    def _getMaxVelocityForBlob(self, dataBlob):
        """Maximum velocity agents will travel at under normal behaviour."""
        
        return self._maxVelocity_Random.valueForIntegerId(dataBlob.agentId)
   
    def _getPreferredVelocityForBlob(self, dataBlob):
        """Agents will tend towards this speed under normal behaviour."""
        
        return self._preferredVelocity_Random.valueForIntegerId(dataBlob.agentId)
     
    def _getMaxAccelerationForBlob(self, dataBlob):
        """Maximum rate of change in agent velocity under normal behaviour."""
        
        return self._maxAcceleration_Random.valueForIntegerId(dataBlob.agentId)
     
    def _getMaxTurnRateForBlob(self, dataBlob):
        """Maximum rate of turn for a given agent."""
        
        return self._maxTurnRate_Random.valueForIntegerId(dataBlob.agentId)
 
    def _getPreferredTurnVelocityForBlob(self, dataBlob):
        """While turning towards a given heading, agents will tend towards this rate of turn."""
        
        return self._preferredTurnVelocity_Random.valueForIntegerId(dataBlob.agentId)
     
    def _getJumpAccelerationForBlob(self, dataBlob):
        """The initial "upwards" acceleration given to an agent when "jumping"."""
        
        return self._jumpAcceleration_Random.valueForIntegerId(dataBlob.agentId)

# END OF CLASS
########################    