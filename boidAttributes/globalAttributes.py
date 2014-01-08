import attributesBaseObject as abo
import attributeTypes as at
import boidTools.uiBuilder as uib


class GlobalAttributes(abo.AttributesBaseObject):
    
    def __init__(self):
        super(GlobalAttributes, self).__init__()
        
        self._enabled = at.BoolAttribute("Enabled", True)
        self._accelerationDueToGravity = at.FloatAttribute("Acceleration Due To Gravity", -38.0, 
                                                           minimumValue=float("-inf"), maximumValue=0)
        self._listRebuildFrequency = at.IntAttribute("List Rebuild Frequency", 5)
        self._useDebugColours = at.BoolAttribute("Debug Colour Particles", True)

#####################     
    def sectionTitle(self):
        return "Global Attributes"

#####################    
    def populateUiLayout(self):
        uib.MakeCheckboxGroup(self._enabled, None) 
        uib.MakeFieldGroup(self._accelerationDueToGravity)
        uib.MakeFieldGroup(self._listRebuildFrequency)
        uib.MakeCheckboxGroup(self._useDebugColours, "Enable")

#####################  
    def _getEnabled(self):
        return self._enabled.value
    def _setEnabled(self, value):
        self._enabled = value
    enabled = property(_getEnabled, _setEnabled)  

#####################     
    def _getAccelerationDueToGravity(self):
        return self._accelerationDueToGravity.value
    accelerationDueToGravity = property(_getAccelerationDueToGravity)

#####################     
    def _getListRebuildFrequency(self):
        return self._listRebuildFrequency.value
    listRebuildFrequency = property(_getListRebuildFrequency)

#####################     
    def _getUseDebugColours(self):
        return self._useDebugColours.value
    useDebugColours = property(_getUseDebugColours)  


# END OF CLASS
####################################    