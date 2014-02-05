from boidBaseObject import BoidBaseObject

import boidVectors.vector3 as bv3
import boidTools.util as util
import boidTools.sceneInterface as scene

from abc import ABCMeta, abstractmethod
import random
import weakref



#####################
class SingleAttributeDelegate(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def onValueChanged(self, attribute):
        raise NotImplemented

# END OF CLASS - SingleAttributeDelegate
####################################



##################################################### 
class _SingleAttributeBaseObject(BoidBaseObject):
    """Base class for attribute types."""
    
    __metaclass__ = ABCMeta
    
####################
    def __init__(self, attributeLabel, value, delegate=None):
        self._attributeLabel = attributeLabel
        self._value = self._getValueFromInput(value)
        
        if(delegate is None):
            self._delegate = None                      # can't use isinstance here, as delegate sometimes doesn't have a type
        elif(not hasattr(delegate, 'onValueChanged')): # if still within it's __init__ method.
            raise TypeError("Delegate %s is of type: %s (expected SingleAttributeDelegate)" % (delegate, type(delegate)))
        else:
            self._delegate = weakref.ref(delegate)
        
        self.updateUiCommand = None
        self._uiEnableMethod = None
        self._isUiEnabled = True
        
        self.logValueChanges = True
        
        self.excludeFromDefaults = False

#####################         
    def __str__(self):
        return str(self.value)

########
    def _getMetaStr(self):
        return ("<label=%s, delegate=%s, exclude=%s, updateUi=%s, uiEnable=%s>" %
                (self._attributeLabel, self.delegate, self.excludeFromDefaults,
                 self.updateUiCommand, self.uiEnableMethod))
        
#############################        
    def __getstate__(self):
        state = super(_SingleAttributeBaseObject, self).__getstate__()
        state["_delegate"] = self.delegate
        state["updateUiCommand"] = None
        state["uiEnableMethod"] = None
        
        return state
  
########  
    def __setstate__(self, state):
        super(_SingleAttributeBaseObject, self).__setstate__(state)
        
        if(self._delegate is not None):
            self._delegate = weakref.ref(self._delegate) 
        
#####################   
    def _getValue(self):
        return self._value
    def _setValue(self, value):
        newValue = self._getValueFromInput(value)
        if(self._validateValue(newValue)):
            self._updateValue(newValue)
    value = property(_getValue, _setValue)
 
########
    @abstractmethod
    def _getValueFromInput(self, inputValue):
        """Must be able to handle both string and 'normal' object representations."""
        raise NotImplemented("Unrecognised attribute type")

########
    def _validateValue(self, newValue):
        """Override if needed - should return true if value should be updated with new
        value (and listeners notified and so on), false otherwise.
        """
        return (newValue != self.value)
 
########
    def _updateValue(self, newValue):
        """Override if needed - updates value with newValue, updates listeners and updates UI components."""
        oldValue = self._value
        self._value = newValue
        self._updateInputUiComponents()
        self._updateDelegate()
        
        if(self.logValueChanges):
            util.LogInfo("Attribute value changed: %s=%s (was: %s)" % (self._attributeLabel, newValue, oldValue))

#####################           
    def _getUiEnableMethod(self):
        return self._uiEnableMethod
    def _setUiEnableMethod(self, value):
        self._uiEnableMethod = value
        if(value is not None):
            self._uiEnableMethod(self._isUiEnabled)
    uiEnableMethod = property(_getUiEnableMethod, _setUiEnableMethod)
    
#####################    
    def _getDelegate(self):
        return self._delegate() if(self._delegate is not None) else None
    delegate = property(_getDelegate)

#####################    
    def _getAttributeLabel(self):
        return self._attributeLabel
    attributeLabel = property(_getAttributeLabel)

#####################     
    def _getNestedAttribute(self):
        """Override if attribute has a seperate, internal (i.e. created internally, not passed in)
        attribute that needs to be preserved when the attributes are saved."""
        return None
    nestedAttribute = property(lambda obj:obj._getNestedAttribute()) # lambda construct means subclasses only have to 
    #                                                                # implement _getNestedAttribute for accessor to work.
#####################    
    def _updateInputUiComponents(self):
        if(self.updateUiCommand is not None):
            try:
                self.updateUiCommand(self.value)
            except RuntimeError:
                self.updateUiCommand = None
            except:
                pass
 
#####################
    def setEnabled(self, enabled):
        if(self.uiEnableMethod is not None):
            try:
                self.uiEnableMethod(enabled)
            except RuntimeError:
                self.uiEnableMethod = None
            except:
                pass
        elif(self.updateUiCommand is not None):
            util.LogWarning("uiEnableMethod not defined for attribute \"%s\", ignoring..." % self._attributeLabel)

        self._isUiEnabled = enabled

#####################            
    def _updateDelegate(self):
        if(self._delegate is not None):
            self._delegate().onValueChanged(self)   
    
# END OF CLASS - _SingleAttributeBaseObject
######################################



##################################################### 
class IntAttribute(_SingleAttributeBaseObject):
    
    def __init__(self, attributeLabel, value, delegate=None, minimumValue=None, maximumValue=None):
        self._minimumValue = minimumValue
        self._maximumValue = maximumValue
        
        super(IntAttribute, self).__init__(attributeLabel, value, delegate)
        
#####################        
    def _getMetaStr(self):
        return ("%s minVal=%s, maxVal=%s" % 
                (super(IntAttribute, self)._getMetaStr(), self._minimumValue, self._maximumValue))
 
#####################        
    def _getMinimumValue(self):
        return self._minimumValue
    def _setMinimumValue(self, value):
        self._minimumValue = value
        if(value is not None and self.value < value):
            self.value = value
        else:
            self._updateInputUiComponents()
    minimumValue = property(_getMinimumValue, _setMinimumValue)

########
    def _getMaximumValue(self):
        return self._maximumValue
    def _setMaximumValue(self, value):
        self._maximumValue = value
        if(value is not None and value < self.value):
            self.value = value
        else:
            self._updateInputUiComponents()
    maximumValue = property(_getMaximumValue, _setMaximumValue)
 
#####################    
    def _validateValue(self, newValue):
        if((self.minimumValue is not None and newValue < self.minimumValue) or 
           (self.maximumValue is not None and self.maximumValue < newValue)):
            self._updateInputUiComponents()
            raise ValueError("Value (%s) is out of bounds, range=%s to %s" % (newValue, self.minimumValue, self.maximumValue))
        else:
            return super(IntAttribute, self)._validateValue(newValue)

#####################   
    def _getValueFromInput(self, inputValue):
        return int(inputValue)

# END OF CLASS - IntAttribute
######################################



##################################################### 
class FloatAttribute(IntAttribute):
            
    def _getValueFromInput(self, inputValue):
        return float(inputValue)

# END OF CLASS - FloatAttribute
######################################



##################################################### 
class RandomizerAttribute(FloatAttribute):
    
    #static variables
    _GlobalIntToRandomLookup = []
    _RandomSequencePreviousState = None
    
    @staticmethod
    def _RandomValueForInt(intKey):
        if(not RandomizerAttribute._RandomSequencePreviousState):
            random.seed(0)
        elif(RandomizerAttribute._RandomSequencePreviousState is not None):
            random.setstate(RandomizerAttribute._RandomSequencePreviousState)
            RandomizerAttribute._RandomSequencePreviousState = None
            
        while(len(RandomizerAttribute._GlobalIntToRandomLookup) <= intKey):
            RandomizerAttribute._GlobalIntToRandomLookup.append(random.uniform(-1.0, 1.0))
            
        return RandomizerAttribute._GlobalIntToRandomLookup[intKey]

#####################    
    def __init__(self, parentAttribute):
        if(type(parentAttribute) != IntAttribute and type(parentAttribute) != FloatAttribute):
            raise TypeError("Attempt to create randomizer for non-valueType attribute")
        elif(parentAttribute._delegate is None):
            util.LogWarning("Delegate attribute for randomized attribute \'%s\' is None" % parentAttribute.attributeLabel)
        
        super(RandomizerAttribute, self).__init__(parentAttribute.attributeLabel + " Randomize", 0, parentAttribute.delegate, 0.0, 1.0)
        self._localIntToRandomLookup = {}
        self._parentAttribute = parentAttribute
        
#####################         
    def _clampIfNecessary(self, returnValue):
        """Returns randomised value from the parent attribute that respects any minimum and maximum values."""
        if(self._parentAttribute._minimumValue is not None and returnValue < self._parentAttribute.minimumValue):
            return self._parentAttribute.minimumValue
        elif(self._parentAttribute._maximumValue is not None and returnValue > self._parentAttribute.maximumValue):
            return self._parentAttribute.maximumValue
        else:
            return returnValue
        
#####################
    def getLocalRandomizedValueForIntegerId(self, integerId):
        if(self.value != 0):
            if(RandomizerAttribute._GlobalIntToRandomLookup and RandomizerAttribute._RandomSequencePreviousState is not None):
                RandomizerAttribute._RandomSequencePreviousState = random.getstate()
            
            randomValue = self._localIntToRandomLookup.get(integerId)
            if(randomValue is None):
                randomValue = random.uniform(-1.0, 1.0)
                self._localIntToRandomLookup[integerId] = randomValue
                
            diff = self._parentAttribute.value * self.value * randomValue
            result = self._parentAttribute._getValueFromInput(self._parentAttribute.value + diff)
            
            return self._clampIfNecessary(result)
        else:
            return self._parentAttribute.value

#####################    
    def getGlobalRandomizedValueForIntegerId(self, integerId):
        if(self.value != 0):
            diff = self._parentAttribute.value * self.value * RandomizerAttribute._RandomValueForInt(integerId)
            result = self._parentAttribute._getValueFromInput(self._parentAttribute.value + diff)
            
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
            util.LogWarning("Delegate attribute for randomized attribute \'%s\' is None" % parentAttribute.attributeLabel)

        super(RandomizeController, self).__init__(parentAttribute.attributeLabel + " Input", 
                                                  RandomizeController.__Off__, 
                                                  parentAttribute.delegate)
        
        self._randomizerAttribute = RandomizerAttribute(parentAttribute)
        self._parentAttribute = parentAttribute

#####################        
    def __str__(self):
        return ("opt=%s, mult=%s" % (super(RandomizeController, self).__str__(), self._randomizerAttribute.__str__()))
    
########
    def _getMetaStr(self):
        return ("<opt=%s, mult=%s>" % (super(RandomizeController, self)._getMetaStr(), self._randomizerAttribute.metaStr))

#####################    
    def _getNestedAttribute(self):
        return self._randomizerAttribute
        
#####################
    def _getValue(self):
        return RandomizeController.StringForOption(self._value)
    def _setValue(self, value):
        super(RandomizeController, self)._setValue(value)
    value = property(_getValue, _setValue)   
 
#####################   
    def _getRandomizeMultiplierValue(self):
        return self._randomizerAttribute.value
    randomizeMultiplierAttribute = property(_getRandomizeMultiplierValue)
 
#####################   
    def _validateValue(self, newValue):
        if(newValue >= RandomizeController.__Off__ and newValue <= RandomizeController.__PureRandom__):
            return newValue != self._value
        else:
            raise ValueError("Invalid value: %d (must be in the range %d - %d)" % 
                             (newValue, RandomizeController.__Off__, RandomizeController.__PureRandom__))

######################
    def _getValueFromInput(self, inputValue):
        if(isinstance(inputValue, basestring)):
            return RandomizeController.OptionForString(inputValue)
        elif(isinstance(inputValue, int)):
            return inputValue
        else:
            raise TypeError("Got %s, expected %s or %s" % (type(inputValue), str, int)) 

#####################    
    def _updateInputUiComponents(self):
        super(RandomizeController, self)._updateInputUiComponents()
        if(self._randomizerAttribute.uiEnableMethod is not None):
            self._randomizerAttribute.setEnabled(self._value != RandomizeController.__Off__)
        
########
    def setEnabled(self, enabled):
        super(RandomizeController, self).setEnabled(enabled)
        self._randomizerAttribute.setEnabled(enabled and self._value != RandomizeController.__Off__)
 
#####################        
    def valueForIntegerId(self, integerId):
        if(self._value == RandomizeController.__Off__):
            return self._parentAttribute.value
        elif(self._value == RandomizeController.__ById__):
            return self._randomizerAttribute.getGlobalRandomizedValueForIntegerId(integerId)
        elif(self._value == RandomizeController.__PureRandom__):
            return self._randomizerAttribute.getLocalRandomizedValueForIntegerId(integerId)
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
    
    def _getValueFromInput(self, inputValue):
        if(isinstance(inputValue, basestring)):
            return inputValue != str(False)
        else:
            return bool(inputValue)

# END OF CLASS - BoolAttribute
######################################




#####################################################         
class StringAttribute(_SingleAttributeBaseObject):
    
    def _getValueFromInput(self, inputValue):
        return str(inputValue)
    
# END OF CLASS - StringAttribute
######################################



#####################################################
class MayaObjectAttribute(_SingleAttributeBaseObject):
    
    def __init__(self, *args, **kwargs):
        self.objectType = None
        self.allowNoneType = True
        
        super(MayaObjectAttribute, self).__init__(*args, **kwargs)

#####################        
    def _getMetaStr(self):
        return ("%s, objType=%s" % (super(MayaObjectAttribute, self)._getMetaStr(), self.objectType))

#####################     
    def getRawAttribute(self):
        return self._value

#####################    
    def _getValueFromInput(self, inputValue):
        if(inputValue is None or inputValue == str(None)):
            if(self.allowNoneType):
                return None
            else:
                raise ValueError("Got <None> type for attribute %s" % self.attributeLabel)
        else:
            returnValue = scene.PymelObjectFromObjectName(inputValue, bypassTransformNodes=False) 
            
            if(returnValue is None):
                raise TypeError("Got none-Pymel type: %s for attribute %s" % (type(returnValue), self.attributeLabel))
            elif(self.objectType == None):
                self.objectType = type(returnValue)
            elif(not isinstance(returnValue, self.objectType)):
                raise TypeError("Got type: %s for attribute %s (expected %s)" % 
                                (type(returnValue), self.attributeLabel, self.objectType))
            
            return returnValue
    
# END OF CLASS - MayaObjectAttribute
#######################################



#####################################################
class LocationAttribute(MayaObjectAttribute):
    """Recommended that the verifyLocatorIfNecessary method is called periodically
    to ensure that the current value is updated with the current position of
    the locator (if one is currently bound to the attribute).
    """
    
    def __init__(self, *args, **kwargs):
        self._boundLocator = None
        
        super(LocationAttribute, self).__init__(*args, **kwargs)

#####################        
    def _getMetaStr(self):
        return ("%s, boundLctr=%s" % (super(LocationAttribute, self)._getMetaStr(), self._boundLocator))
 
#####################        
    def _getObjectType(self):
        return scene.LocatorPymelType()
    def _setObjectType(self, value):
        pass
    objectType = property(_getObjectType, _setObjectType)
    
########
    def _getAllowNoneType(self):
        return True
    def _setAllowNoneType(self, value):
        pass
    allowNoneType = property(_getAllowNoneType, _setAllowNoneType)
    
########
    def getRawAttribute(self):
        return self._boundLocator
    
#####################    
    def _getHasBoundLocator(self):
        return self._boundLocator is not None
    hasBoundLocator = property(_getHasBoundLocator)

#####################        
    def verifyLocatorIfNecessary(self):
        """Recommended that this method is periodically called to ensure attribute
        is correctly updated with any changes in the bound locator's location.
        """
        if(self.hasBoundLocator):
            self.value = self._boundLocator

#####################            
    def clearBoundLocator(self):
        self.value = None

#####################      
    def _getX(self):
        return self._value.x      
    def _setX(self, xValue):
        self.value = (xValue, self._value.y, self._value.z)
    x = property(_getX, _setX)

########
    def _getY(self):
        return self._value.y        
    def _setY(self, yValue):
        self.value = (self._value.x, yValue, self._value.z)
    y = property(_getY, _setY)
        
########
    def _getZ(self):
        return self._value.z
    def _setZ(self, zValue):
        self.value = (self._value.x, self._value.y, zValue)
    z = property(_getZ, _setZ)

#####################    
    def _updateInputUiComponents(self):
        super(LocationAttribute, self)._updateInputUiComponents()
        self.setEnabled(not self.hasBoundLocator)

#####################    
    def _getValueFromInput(self, inputValue):
        result = scene.Vector3FromLocator(inputValue)
        if(result is not None):
            self._boundLocator = inputValue
        else:
            if(inputValue is None):
                result = self._value
                if(self.hasBoundLocator):
                    self._boundLocator = None
                    self._updateInputUiComponents() # do this here as it will be skipped by the normal mechanism
            else:
                self._boundLocator = None
                if(isinstance(inputValue, bv3.Vector3)):
                    result = inputValue
                elif(isinstance(inputValue, list) or isinstance(inputValue, tuple)):
                    result = bv3.Vector3(inputValue[0], inputValue[1], inputValue[2])
                else:
                    raise TypeError("Location input value received value %s, of type: %s" % (inputValue, type(inputValue)))
        return result

# END OF CLASS - LocationAttribute
######################################



######################################
class Vector3Attribute(_SingleAttributeBaseObject):
        
    def _getX(self):
        return self._value.x      
    def _setX(self, xValue):
        self.value = (xValue, self._value.y, self._value.z)
    x = property(_getX, _setX)

########
    def _getY(self):
        return self._value.y        
    def _setY(self, yValue):
        self.value = (self._value.x, yValue, self._value.z)
    y = property(_getY, _setY)
        
########
    def _getZ(self):
        return self._value.z
    def _setZ(self, zValue):
        self.value = (self._value.x, self._value.y, zValue)
    z = property(_getZ, _setZ)
    
#####################
    def _getValueFromInput(self, inputValue):
        
        if(isinstance(inputValue, bv3.Vector3)):
            return inputValue
        elif(isinstance(inputValue, basestring)):
            result = bv3.Vector3()
            result.setValueFromString(inputValue)
            return result
        elif(isinstance(inputValue, list) or isinstance(inputValue, tuple)):
            result = bv3.Vector3()
            result.valueAsTuple = inputValue
            return result
        else:
            raise TypeError("Got %s, expected %s or %s" % (type(inputValue), bv3.Vector3, basestring))
            
# END OF CLASS - Vector3Attribute
######################################           
            
            
            
            