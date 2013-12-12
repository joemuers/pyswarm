import attributesBaseObject as abo
import attributeTypes as at



class AgentMovementAttributes(abo.AttributesBaseObject):
    
    def __init__(self):
        super(AgentMovementAttributes, self).__init__()
        
        self._maxVelocity = at.FloatAttribute("maxVelocity", 5.0, "maxVelocity_Random", 0.0, self)
        self._minVelocity = at.FloatAttribute("minVelocity", 0.5)
        self._preferredVelocity = at.FloatAttribute("preferredVelocity", 3.5, "preferredVelocity_Random", 0.0, self)
        self._maxAcceleration = at.FloatAttribute("maxAcceleration", 1.0, "maxAcceleration_Random", 0.0, self)
        self._maxTurnRate = at.IntAttribute("maxTurnRate", 5, "maxTurnRate_Random", 0.0, self)
        self._maxTurnRateChange = at.IntAttribute("maxTurnRateChange", 4)
        self._preferredTurnVelocity = at.FloatAttribute("preferredTurnVelocity", 0.5, "preferredTurnVelocity_Random", 0.0, self)
        self._jumpAcceleration = at.FloatAttribute("jumpAcceleration", 65, "jumpAcceleration_Random", 0.0, self)
        
##################### 
    def _sectionTitle(self):
        return "Agent movement"
    
#####################
    def makeFrameLayout(self):
        mainFrame = at.MakeFrameLayout(self._sectionTitle())

        velocityFrame = at.MakeFrameLayout("Velocity")
        maxVelFrame = self._maxVelocity.makeFrameLayout("Max Velocity", "velocity", 0)
        at.SetAsChildToPrevious(maxVelFrame)
        minVelFrame = self._minVelocity.makeFrameLayout("Min Velocity", "velocity", 0)
        at.SetAsChildToPrevious(minVelFrame)
        prefVelFrame = self._preferredVelocity.makeFrameLayout("Preferred velocity", "velocity", 0)
        at.SetAsChildToPrevious(prefVelFrame, velocityFrame)
        
        maxAccelFrame = self._maxAcceleration.makeFrameLayout("Max acceleration", "acceleration scalar", 0)
        at.SetAsChildToPrevious(maxAccelFrame)
        
        turningFrame = at.MakeFrameLayout("Turning")
        maxTurnFrame = self._maxTurnRate.makeFrameLayout("Max turn rate", "degrees", 0, 360)
        maxTurnChange = self._maxTurnRateChange.makeRowLayout("max rate of change", 0, 360)
        at.SetAsChildToPrevious(maxTurnChange, maxTurnFrame)
        preferredTurnFrame = self._preferredTurnVelocity.makeFrameLayout("Preferred turn velocity", "velocity", 0)
        at.SetAsChildToPrevious(preferredTurnFrame, turningFrame)
        jumpFrame = self._jumpAcceleration.makeFrameLayout("Jump accleration", "magnitude", 0)
        at.SetAsChildToPrevious(jumpFrame)
        
        return mainFrame

#####################     
    def _getMaxVelocity(self):
        return self._maxVelocity.value
    def _setMaxVelocity(self, value):
        self._maxVelocity.value = value
    maxVelocity = property(_getMaxVelocity, _setMaxVelocity)

#####################     
    def _getMaxVelocity_Random(self):
        return self._maxVelocity.randomizerValue
    def _setMaxVelocity_Random(self, value):
        self._maxVelocity.randomizerValue = value
    maxVelocity_Random = property(_getMaxVelocity_Random, _setMaxVelocity_Random)

#####################     
    def _getMinVelocity(self):
        return self._minVelocity.value
    def _setMinVelocity(self, value):
        self._minVelocity.value = value
    minVelocity = property(_getMinVelocity, _setMinVelocity)

#####################     
    def _getPreferredVelocity(self):
        return self._preferredVelocity.value
    def _setPreferredVelocity(self, value):
        self._preferredVelocity.value = value
    preferredVelocity = property(_getPreferredVelocity, _setPreferredVelocity)

#####################     
    def _getPreferredVelocity_Random(self):
        return self._preferredVelocity.randomizerValue
    def _setPreferredVelocity_Random(self, value):
        self._preferredVelocity.randomizerValue = value
    preferredVelocity_Random = property(_getPreferredVelocity_Random, _setPreferredVelocity_Random)

#####################     
    def _getMaxAcceleration(self):
        return self._maxAcceleration.value
    def _setMaxAcceleration(self, value):
        self._maxAcceleration.value = value
    maxAcceleration = property(_getMaxAcceleration, _setMaxAcceleration)

#####################     
    def _getMaxAcceleration_Random(self):
        return self._maxAcceleration.randomizerValue
    def _setMaxAcceleration_Random(self, value):
        self._maxAcceleration.randomizerValue = value
    maxAcceleration_Random = property(_getMaxAcceleration_Random, _setMaxAcceleration_Random)

#####################     
    def _getMaxTurnRate(self):
        return self._maxTurnRate.value
    def _setMaxTurnRate(self, value):
        self._maxTurnRate.value = value
    maxTurnRate = property(_getMaxTurnRate, _setMaxTurnRate)

#####################     
    def _getMaxTurnRate_Random(self):
        return self._maxTurnRate.randomizerValue
    def _setMaxTurnRate_Random(self, value):
        self._maxTurnRate.randomizerValue = value
    maxTurnRate_Random = property(_getMaxTurnRate_Random, _setMaxTurnRate_Random)

#####################     
    def _getMaxTurnRateChange(self):
        return self._maxTurnRateChange.value
    def _setMaxTurnRateChange(self, value):
        self._maxTurnRateChange.value = value
    maxTurnRateChange = property(_getMaxTurnRateChange, _setMaxTurnRateChange)

##################### 
    def _getPreferredTurnVelocity(self):
        return self._preferredTurnVelocity.value
    def _setPreferredTurnVelocity(self, value):
        self._preferredTurnVelocity.value = value
    preferredTurnVelocity = property(_getPreferredTurnVelocity, _setPreferredTurnVelocity)

#####################     
    def _getPreferredTurnVelocity_Random(self):
        return self._preferredTurnVelocity.randomizerValue
    def _setPreferredTurnVelocity_Random(self, value):
        self._preferredTurnVelocity.randomizerValue = value
    preferredTurnVelocity_Random = property(_getPreferredTurnVelocity_Random, _setPreferredTurnVelocity_Random)
    
#####################     
    def _getJumpAcceleration(self):
        return self._jumpAcceleration.value
    def _setJumpAcceleration(self, value):
        self._jumpAcceleration.value = value
    jumpAcceleration = property(_getJumpAcceleration, _setJumpAcceleration)

#####################     
    def _getJumpAcceleration_Random(self):
        return self._jumpAcceleration.randomizerValue
    def _setJumpAcceleration_Random(self, value):
        self._jumpAcceleration.randomizerValue = value
    jumpAcceleration_Random = property(_getJumpAcceleration_Random, _setJumpAcceleration_Random)
    

# END OF CLASS
########################    