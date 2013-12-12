import attributesBaseObject as abo
import attributeTypes as at

import pymel.core as pm


class GeneralAttributes(abo.AttributesBaseObject):
    
    def __init__(self):
        super(GeneralAttributes, self).__init__()
        
        self._accelerationDueToGravity = at.FloatAttribute("accelerationDueToGravity", -38.0, delegate=self)
        self._useDebugColours = at.BoolAttribute("useDebugColours", True)
        self._listRebuildFrequency = at.IntAttribute("listRebuildFrequency", 5)
        
        self._accelerationDueToGravityTextField = None
        self._listRebuildFrequencyTextField = None

#####################     
    def _sectionTitle(self):
        return "General attributes"

#####################    
    def makeFrameLayout(self):
        frameLayout = at.MakeFrameLayout(self._sectionTitle())

        generalColumnLayout = pm.columnLayout()
        debugColoursCheckbox = self._useDebugColours.makeCheckboxComponent("debug colours")
        self._accelerationDueToGravityTextField = pm.floatField(max=0, value=self._accelerationDueToGravity.value, precision=3)
        self._accelerationDueToGravityTextField.changeCommand(lambda *args: 
                                                              self._accelerationDueToGravity._setValue(self._accelerationDueToGravityTextField.getValue()))
        self._listRebuildFrequencyTextField = pm.intField(min=0, value=self._listRebuildFrequency.value)
        self._listRebuildFrequencyTextField.changeCommand(lambda *args:
                                                          self._listRebuildFrequency._setValue(self._listRebuildFrequencyTextField.getValue()))
        at.SetAsChildToPrevious(generalColumnLayout)
        
        return frameLayout
    
#####################     
    def _getUseDebugColours(self):
        return self._useDebugColours.value
    def _setUseDebugColours(self, value):
        self._useDebugColours.value = value
    useDebugColours = property(_getUseDebugColours, _setUseDebugColours)    

#####################     
    def _getAccelerationDueToGravity(self):
        return self._accelerationDueToGravity.value
    def _setAccelerationDueToGravity(self, value):
        self._accelerationDueToGravity.value = value
    accelerationDueToGravity = property(_getAccelerationDueToGravity, _setAccelerationDueToGravity)

#####################     
    def _getListRebuildFrequency(self):
        return self._listRebuildFrequency.value
    def _setListRebuildFrequency(self, value):
        self._listRebuildFrequency.value = value
    listRebuildFrequency = property(_getListRebuildFrequency, _setListRebuildFrequency)
              
#####################            
    def _onAttributeChanged(self, changedAttribute):
        if(changedAttribute is self._accelerationDueToGravity):
            self._accelerationDueToGravityTextField.setValue(self._accelerationDueToGravity.value)
        elif(changedAttribute is self._listRebuildFrequency):
            self._listRebuildFrequencyTextField.setValue(self._listRebuildFrequency.value)
            
        super(GeneralAttributes, self)._onAttributeChanged(changedAttribute)
        




# END OF CLASS
####################################    