import random
import weakref



#####################

class SingleAttributeDelegate(object):
    
    def _onAttributeChanged(self, attribute):
        raise NotImplemented

# END OF CLASS - SingleAttributeDelegate
####################################



##################################################### 
class _SingleAttributeBaseObject(object):
    """Base class for attribute types."""
    
    def __init__(self, attributeLabel, value, delegate=None):
        self._attributeLabel = attributeLabel
        self._value = value
        
        if(delegate is None):
            self._delegate = None
        elif(not hasattr(delegate, "_onAttributeChanged")):
            raise TypeError("Delegate is of type %s" % type(delegate))
        else:
            self._delegate = weakref.ref(delegate)
        
        self.updateUiCommand = None
        self.uiEnableMethod = None

#####################   
    def _getValue(self):
        return self._value
    def _setValue(self, value):
        newValue = self.getValueFromInput(value)
        if(newValue != self.value):
            self._value = newValue
            
            self._updateInputUiComponents()
            self._updateDelegate()
            print("set %s=%s" % (self._attributeLabel, newValue))
    value = property(_getValue, _setValue)

#####################    
    def _getDelegate(self):
        return self._delegate() if(self._delegate is not None) else None
    delegate = property(_getDelegate)

#####################    
    def _getAttributeLabel(self):
        return self._attributeLabel
    attributeLabel = property(_getAttributeLabel)

#####################    
    def getValueFromInput(self, inputValue):
        raise NotImplemented("Unrecognised attribute type")
    
#####################    
    def _updateInputUiComponents(self):
        if(self.updateUiCommand is not None):
            self.updateUiCommand(self.value)
            
#####################        
    def setEnabled(self, enabled):
        if(self.uiEnableMethod is not None):
            self.uiEnableMethod(enabled)

#####################            
    def _updateDelegate(self):
        if(self._delegate is not None):
            self._delegate()._onAttributeChanged(self)   
    
# END OF CLASS - _SingleAttributeBaseObject
######################################



##################################################### 
class IntAttribute(_SingleAttributeBaseObject):
    
    def __init__(self, attributeLabel, value, delegate=None, minimumValue=None, maximumValue=None):
        super(IntAttribute, self).__init__(attributeLabel, value, delegate)
        
        self._minimumValue = minimumValue
        self._maximumValue = maximumValue
 
#####################        
    def _getMinimumValue(self):
        return self._minimumValue
    minimumValue = property(_getMinimumValue)

#####################    
    def _getMaximumValue(self):
        return self._maximumValue
    maximumValue = property(_getMaximumValue)
 
#####################    
    def _getValue(self):
        return self._value
    def _setValue(self, value):
        newValue = self.getValueFromInput(value)
        if((self.minimumValue is not None and newValue < self.minimumValue) or 
           (self.maximumValue is not None and self.maximumValue < newValue)):
            self._updateInputUiComponents()
            raise ValueError("Value (%s) is out of bounds, range=%s to %s" % (value, self.minimumValue, self.maximumValue))
        else:
            super(IntAttribute, self)._setValue(newValue)
    value = property(_getValue, _setValue)

#####################   
    def getValueFromInput(self, inputValue):
        return int(inputValue)

# END OF CLASS - IntAttribute
######################################



##################################################### 
class FloatAttribute(IntAttribute):
            
    def getValueFromInput(self, inputValue):
        return float(inputValue)

# END OF CLASS - FloatAttribute
######################################



##################################################### 
class RandomizerAttribute(FloatAttribute):
    
    #static variables
    _intToRandomLookup = []
    _previousState = None
    
    @staticmethod
    def _RandomValueForInt(intKey):
        if(not RandomizerAttribute._intToRandomLookup):
            random.seed(0)
        elif(RandomizerAttribute._previousState is not None):
            random.setstate(RandomizerAttribute._previousState)
            RandomizerAttribute._previousState = None
            
        while(len(RandomizerAttribute._intToRandomLookup) <= intKey):
            RandomizerAttribute._intToRandomLookup.append(random.uniform(-1.0, 1.0))
            
        return RandomizerAttribute._intToRandomLookup[intKey]

#####################    
    def __init__(self, parentAttribute):
        if(type(parentAttribute) != IntAttribute and type(parentAttribute) != FloatAttribute):
            raise TypeError("Attempt to create randomizer for non-valueType attribute")
        elif(parentAttribute._delegate is None):
            print("WARNING - delegate attribute for randomized attribute \'%s\' is None" % parentAttribute.attributeLabel)
        
        super(RandomizerAttribute, self).__init__(parentAttribute.attributeLabel + " Randomize", 0, parentAttribute.delegate, 0.0, 1.0)
        self._parentAttribute = parentAttribute
        
#####################         
    def _clampIfNecessary(self, returnValue):
        if(self._parentAttribute._minimumValue is not None and returnValue < self._parentAttribute.minimumValue):
            return self._parentAttribute.minimumValue
        elif(self._parentAttribute._maximumValue is not None and returnValue > self._parentAttribute.maximumValue):
            return self._parentAttribute.maximumValue
        else:
            return returnValue
        
#####################         
    def _getRandomizedValue(self):
        if(self.value != 0):
            if(RandomizerAttribute._intToRandomLookup and RandomizerAttribute._previousState is not None):
                RandomizerAttribute._previousState = random.getstate()
                
            diff = self._parentAttribute.value * self.value
            result = self._parentAttribute.getValueFromInput(self._parentAttribute.value + random.uniform(-diff, diff))
            
            return self._clampIfNecessary(result)
        else:
            return self._parentAttribute.value
    randomizedValue = property(_getRandomizedValue)

#####################    
    def getRandomizedValueForIntegerId(self, integerId):
        if(self.value != 0):
            diff = self._parentAttribute.value * self.value * RandomizerAttribute._RandomValueForInt(integerId)
            result = self._parentAttribute.getValueFromInput(self._parentAttribute.value + diff)
            
            return self._clampIfNecessary(result)
        else:
            return self._parentAttribute.value
    
#####################            
    def _updateDelegate(self):
        super(RandomizerAttribute, self)._updateDelegate()
        self._parentAttribute._updateDelegate()  

# END OF CLASS - RandomizerAttribute
######################################    



##################################################### 
class RandomizeController(_SingleAttributeBaseObject):
    __OptionStrings__ = ["Off", "By Agent ID", "Pure Random"]
    __Off__, __ById__, __PureRandom__ = range(3)
    
    @staticmethod
    def StringForOption(option):
        return RandomizeController.__OptionStrings__[option]
    @staticmethod
    def OptionForString(optionString):
        return RandomizeController.__OptionStrings__.index(optionString)

#####################     
    def __init__(self, parentAttribute):
        if(type(parentAttribute) != IntAttribute and type(parentAttribute) != FloatAttribute):
            raise TypeError("Attempt to create randomizeController for non-valueType attribute")
        elif(parentAttribute.delegate is None):
            print("WARNING - delegate attribute for randomized attribute \'%s\' is None" % parentAttribute.attributeLabel)

        super(RandomizeController, self).__init__(parentAttribute.attributeLabel + " Input", 
                                                  RandomizeController.__Off__, 
                                                  parentAttribute.delegate)
        
        self._randomizerAttribute = RandomizerAttribute(parentAttribute)
        self._parentAttribute = parentAttribute
        
#####################
    def _getValue(self):
        return RandomizeController.StringForOption(self._value)
    def _setValue(self, value):
        super(RandomizeController, self)._setValue(value)
    value = property(_getValue, _setValue)   
 
#####################   
    def getValueFromInput(self, inputValue):
        return RandomizeController.OptionForString(inputValue) 
    
    def _updateInputUiComponents(self):
        super(RandomizeController, self)._updateInputUiComponents()
        self._randomizerAttribute.setEnabled(self._value != RandomizeController.__Off__)
 
#####################        
    def valueForIntegerId(self, integerId):
        if(self._value == RandomizeController.__Off__):
            return self._parentAttribute.value
        elif(self._value == RandomizeController.__ById__):
            return self._randomizerAttribute.getRandomizedValueForIntegerId(integerId)
        elif(self._value == RandomizeController.__PureRandom__):
            return self._randomizerAttribute.randomizedValue
        else:
            raise RuntimeError("Selected has unrecognized enum value: %s" % self._value)
        
#####################            
    def _updateDelegate(self):
        super(RandomizeController, self)._updateDelegate()
        self._parentAttribute._updateDelegate()  

# END OF CLASS - RandomizeController
######################################



#####################################################        
class BoolAttribute(_SingleAttributeBaseObject):
    
    def getValueFromInput(self, inputValue):
        return bool(inputValue)

# END OF CLASS - BoolAttribute
######################################



#####################################################         
class StringAttribute(_SingleAttributeBaseObject):
    
    def getValueFromInput(self, inputValue):
        return str(inputValue)
    
# END OF CLASS - StringAttribute
######################################