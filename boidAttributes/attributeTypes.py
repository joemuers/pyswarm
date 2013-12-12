import random
import weakref
import pymel.core as pm




def MakeFrameLayout(title, makeCollapsable=True):
    frame = pm.frameLayout(title)
    if(makeCollapsable):
        frame.setCollapsable(True)
    return frame

def SetAsChildToPrevious(*args):
    for _ in range(len(args)):
        pm.setParent("..")

#####################

class SingleAttributeDelegate(object):
    
    def _onAttributeChanged(self, attribute):
        raise NotImplemented

# END OF CLASS - SingleAttributeDelegate
####################################


class _SingleAttributeBaseObject(object):
    
    def __init__(self, attributeName, value, randomizerName=None, randomizerValue=0, delegate=None):
        self._attributeName = attributeName
        self._value = value
        
        if(delegate is None):
            self._delegate = None
        elif(not hasattr(delegate, "_onAttributeChanged")):
            raise TypeError("Delegate is of type %s" % type(delegate))
        else:
            self._delegate = weakref.ref(delegate)
            
        self._randomizerName = randomizerName
        self._randomizerValue = randomizerValue
        self._randomizerUiField = None
        self._randomizerUiSlider = None
 
#####################   
    def _getValue(self):
        if(self._randomizerValue == 0):
            return self._value
        else:
            diff = self._randomizerValue * self._value
            return self.getValueFromInput(self._value + random.uniform(-diff, diff))
    def _setValue(self, value):
        newValue = self.getValueFromInput(value)
        if(newValue != self._value):
            self._value = newValue
            
            self._updateInputUiComponents()
            self._updateDelegate()
    value = property(_getValue, _setValue)

#####################    
    def _getRandomizerValue(self):
        return self._randomizerValue
    def _setRandomizerValue(self, value):
        newValue = float(value)
        if(newValue < 0 or 1 < newValue):
            raise ValueError("Randomizer value must be between 0 and 1 (got %s)" % value)
        else:
            self._randomizerValue = newValue

            self._updateRandomizerUiComponents()
            self._updateDelegate()
    randomizerValue = property(_getRandomizerValue, _setRandomizerValue)

#####################
    def _getHasRandomizer(self):
        return (self.randomizerName is not None)
    hasRandomizer = property(_getHasRandomizer)

#####################    
    def _getHasRandomizerUiRow(self):
        return (self._randomizerUiField is not None and self._randomizerUiSlider is not None)
    hasRandomizerUiRow = property(_getHasRandomizerUiRow)

#####################    
    def _getAttributeName(self):
        return self._attributeName
    attributeName = property(_getAttributeName)

#####################    
    def _getRandomizerName(self):
        return self._randomizerName
    randomizerName = property(_getRandomizerName)

#####################     
    def makeRowLayout(self, title, minValue=None, maxValue=None):
        raise NotImplemented

#####################     
    def makeRandomizerRowLayout(self):
        if(self.hasRandomizer):
            rowLayout = self._standardRowLayout()
            
            pm.text("Randomize")
            
            self._randomizerUiField = pm.floatField(min=0.0, max=1.0, precision=2, value=self.randomizerValue)
            self._randomizerUiField.changeCommand(lambda *args: self._setRandomizerValue(self._randomizerUiField.getValue()))
            
            self._randomizerUiSlider = pm.floatSlider(min=0.0, max=1.0, value=self.randomizerValue)
            self._randomizerUiSlider.dragCommand(lambda *args: self._randomizerUiField.setValue(self._randomizerUiSlider.getValue()))
            self._randomizerUiSlider.changeCommand(lambda *args: self._setRandomizerValue(self._randomizerUiField.getValue()))
            
            return rowLayout
        else:
            raise RuntimeError("Request for randomizer rowLayout on attribute with no randomizer.")
 
#####################         
    def makeFrameLayout(self, title, fieldTitle, minValue=None, maxValue=None):
        frameLayout = MakeFrameLayout(title)
        
        attributeRow = self.makeRowLayout(fieldTitle, minValue, maxValue)
        SetAsChildToPrevious(attributeRow)
        if(self.hasRandomizer):
            randomizerRow = self.makeRandomizerRowLayout()
            SetAsChildToPrevious(randomizerRow)
        return frameLayout

#####################    
    def _standardRowLayout(self, numColumns=3):
        if(numColumns == 3):
            return pm.rowLayout(numberOfColumns=3, columnWidth3=(120, 50, 150), columnAlign=(1, 'right'), 
                                columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 10)])
        elif(numColumns == 2):
            return pm.rowLayout(numberOfColumns=2, columnWidth2=(170, 150), columnAlign=(1, 'right'), 
                                columnAttach=[(1, 'both', 0), (2, 'both', 0)])
            

#####################    
    def getValueFromInput(self, inputValue):
        raise NotImplemented("Unrecognised attribute type")
    
#####################    
    def _updateInputUiComponents(self):
        # override if necessary...
        pass

#####################
    def _updateRandomizerUiComponents(self):
        if(self.hasRandomizerUiRow):
            self._randomizerUiField.setValue(self._randomizerValue)
            self._randomizerUiSlider.setValue(self._randomizerValue)

#####################            
    def _updateDelegate(self):
        if(self._delegate is not None):
            self._delegate()._onAttributeChanged(self)   
    
# END OF CLASS - _SingleAttributeBaseObject
######################################


class IntAttribute(_SingleAttributeBaseObject):
    
    def __init__(self, attributeName, value, randomizerName=None, randomizerValue=0, delegate=None):
        super(IntAttribute, self).__init__(attributeName, value, randomizerName, randomizerValue, delegate)
        
        self._inputUiField = None
        self._inputUiSlider = None

#####################    
    def getValueFromInput(self, inputValue):
        return int(inputValue)

#####################    
    def _getHasInputUiRow(self):
        return (self._inputUiField is not None and self._inputUiSlider is not None)
    hasInputUiRow = property(_getHasInputUiRow)

#####################    
    def _updateInputUiComponents(self):
        if(self.hasInputUiRow):
            newValue = self._value
            self._inputUiField.setValue(newValue)
            if(self._inputUiSlider.getMaxValue() < newValue):
                self._inputUiSlider.setMaxValue(2 * newValue)
            elif(newValue < self._inputUiSlider.getMinValue()):
                self._inputUiSlider.setMinValue(2 * newValue)
            self._inputUiSlider.setValue(newValue)

#####################    
    def makeRowLayout(self, text, minValue=None, maxValue=None, makeSlider=True):
        rowLayout = self._standardRowLayout()
        
        pm.text(text)
        
        kwargs = { "value" : self._value }
        if(minValue is not None):
            kwargs["min"] = minValue
        if(maxValue is not  None):
            kwargs["max"] = maxValue
        self._inputUiField = pm.intField(**kwargs)
        self._inputUiField.changeCommand(lambda *args: self._setValue(self._inputUiField.getValue()))
        
        if(makeSlider):
            if(maxValue is None):
                kwargs["max"] = self._value * 2
            self._inputUiSlider = pm.intSlider(**kwargs)
            self._inputUiSlider.dragCommand(lambda *args: self._inputUiField.setValue(self._inputUiSlider.getValue()))
            self._inputUiSlider.changeCommand(lambda *args: self._setValue(self._inputUiSlider.getValue()))
        
        return rowLayout

# END OF CLASS - IntAttribute
######################################


class FloatAttribute(IntAttribute):
       
    def getValueFromInput(self, inputValue):
        return float(inputValue)
            
#####################
    def makeRowLayout(self, text, minValue=None, maxValue=None, makeSlider=True):
        rowLayout = self._standardRowLayout()
        
        pm.text(text)
        
        kwargs = { "value" : self._value, "precision" : 3 }
        if(minValue is not None):
            kwargs["min"] = minValue
        if(maxValue is not  None):
            kwargs["max"] = maxValue
        self._inputUiField = pm.floatField(**kwargs)
        self._inputUiField.changeCommand(lambda *args: self._setValue(self._inputUiField.getValue()))
        
        if(makeSlider):
            kwargs.pop("precision")
            
            if(maxValue is None):
                kwargs["max"] = self._value * 2
            self._inputUiSlider = pm.floatSlider(**kwargs)
            self._inputUiSlider.dragCommand(lambda *args: self._inputUiField.setValue(self._inputUiSlider.getValue()))
            self._inputUiSlider.changeCommand(lambda *args: self._setValue(self._inputUiSlider.getValue()))
        
        return rowLayout

# END OF CLASS - FloatAttribute
######################################

        
class BoolAttribute(_SingleAttributeBaseObject):
    
    def __init__(self, attributeName, value, randomizerName=None, randomizerValue=0, delegate=None):
        if(randomizerName is not None or randomizerValue != 0):
            raise ValueError("Random values not applicable to boolean attributes")
        else:
            super(BoolAttribute, self).__init__(attributeName, value, randomizerName, randomizerValue, delegate)
            
            self._uiCheckbox = None
    
    def getValueFromInput(self, inputValue):
        return bool(inputValue)
    
    def _updateInputUiComponents(self):
        if(self._uiCheckbox is not None):
            self._uiCheckbox.setValue(self.value)
    
    def makeCheckboxComponent(self, text):
        self._uiCheckbox = pm.checkBox(label=text, value=self.value)
        self._uiCheckbox.changeCommand(lambda *args: self._setValue(self._uiCheckbox.getValue()))
        
        return self._uiCheckbox

# END OF CLASS - BoolAttribute
######################################

        
class StringAttribute(_SingleAttributeBaseObject):
    
    def __init__(self, attributeName, value, randomizerName=None, randomizerValue=0, delegate=None):
        if(randomizerName is not None or randomizerValue != 0):
            raise ValueError("Random values not applicable to string attributes")
        else:
            super(StringAttribute, self).__init__(attributeName, value, randomizerName, randomizerValue, delegate)
    
    def getValueFromInput(self, inputValue):
        return str(inputValue)
    
# END OF CLASS - StringAttribute
######################################