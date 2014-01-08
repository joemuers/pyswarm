import attributesBaseObject as abo
import attributeTypes as at
import boidTools.uiBuilder as uib



##########################################
class MovementAttributesDataBlob(abo.DataBlobBaseObject):
    
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
class AgentMovementAttributes(abo.AttributesBaseObject):
    
    def __init__(self):
        super(AgentMovementAttributes, self).__init__()
        
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
    def sectionTitle(self): 
        return "Agent Movement"

#####################     
    def populateUiLayout(self):
        
        speedFrameLayout = uib.MakeFrameLayout("Speed")
        uib.MakeSliderGroup(self._maxVelocity, self._getMaxVelocityForBlob.__doc__)
        uib.MakeRandomizerFields(self._maxVelocity_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._minVelocity)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._preferredVelocity)
        uib.MakeRandomizerFields(self._preferredVelocity_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._maxAcceleration)
        uib.MakeRandomizerFields(self._maxAcceleration_Random)
        uib.SetAsChildLayout(speedFrameLayout)
        
        turnFrameLayout = uib.MakeFrameLayout("Turning")
        uib.MakeSliderGroup(self._maxTurnRate)
        uib.MakeRandomizerFields(self._maxTurnRate_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._maxTurnRateChange)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._preferredTurnVelocity)
        uib.MakeRandomizerFields(self._preferredTurnVelocity_Random)
        uib.SetAsChildLayout(turnFrameLayout)
        
        uib.MakeSliderGroup(self._jumpAcceleration)
        uib.MakeRandomizerFields(self._jumpAcceleration_Random)
        
#####################
    def _createDataBlobForAgent(self, agent):
        return MovementAttributesDataBlob(agent)

# #####################        
#     def _updateDataBlob(self, dataBlob):
#         agentId = dataBlob.agentId
#         
#         dataBlob.maxVelocity = self._getMaxVelocityForId(agentId)
#         dataBlob.preferredVelocity = self._getPreferredVelocityForId(agentId)
#         dataBlob.maxAcceleration = self._getMaxAccelerationForId(agentId)
#         dataBlob.maxTurnRate = self._getMaxTurnRateForId(agentId)
#         dataBlob.preferredTurnVelocity = self._getPreferredTurnVelocityForId(agentId)
#         dataBlob.jumpAcceleration = self._getJumpAccelerationForId(agentId)
        
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
        return self._minVelocity.value
    minVelocity  = property(_getMinVelocity) 
    
#####################     
    def _getMaxTurnRateChange(self):
        return self._maxTurnRateChange.value
    maxTurnRateChange = property(_getMaxTurnRateChange)
          
#####################     
    def _getMaxVelocityForBlob(self, dataBlob):
        """Maximum velocity that agents will travel at under normal behaviour."""
        return self._maxVelocity_Random.valueForIntegerId(dataBlob.agentId)
   
    def _getPreferredVelocityForBlob(self, dataBlob):
        return self._preferredVelocity_Random.valueForIntegerId(dataBlob.agentId)
     
    def _getMaxAccelerationForBlob(self, dataBlob):
        return self._maxAcceleration_Random.valueForIntegerId(dataBlob.agentId)
     
    def _getMaxTurnRateForBlob(self, dataBlob):
        return self._maxTurnRate_Random.valueForIntegerId(dataBlob.agentId)
 
    def _getPreferredTurnVelocityForBlob(self, dataBlob):
        return self._preferredTurnVelocity_Random.valueForIntegerId(dataBlob.agentId)
     
    def _getJumpAccelerationForBlob(self, dataBlob):
        return self._jumpAcceleration_Random.valueForIntegerId(dataBlob.agentId)

# END OF CLASS
########################    