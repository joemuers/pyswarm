import attributesBaseObject as abo
import attributeTypes as at
import boidTools.uiBuilder as uib
import boidVectors.vector3 as bv3
import boidTools.util as util



#######################################
class _PreferencesWindow(object):
    
    def __init__(self, accelerationAttribute, listRebuildAttribute):
        self._accelerationDueToGravity = at.FloatAttribute("Acceleration Due To Gravity", -38.0, 
                                                           minimumValue=float("-inf"), maximumValue=0)
        self._listRebuildFrequency = at.IntAttribute("List Rebuild Frequency", 5)
        
        self._accelerationParentAttribute = accelerationAttribute
        self._listRebuildParentAttribute = listRebuildAttribute
        
        self._window = None

#####################       
    def show(self):
        self._closeWindow()
        
        self._accelerationDueToGravity.value = self._accelerationParentAttribute.value
        self._listRebuildFrequency.value = self._listRebuildParentAttribute.value
            
        self._window = uib.MakeWindow("Global Preferences")
        borderLayout = uib.MakeBorderingLayout()
        columnLayout = uib.MakeColumnLayout()
        uib.MakeFieldGroup(self._accelerationDueToGravity)
        uib.MakeFieldGroup(self._listRebuildFrequency)
        
        uib.SetAsChildLayout(columnLayout, borderLayout)
        
        uib.MakeButtonStrip((("OK", self._okButtonWasPressed), ("Cancel", self._closeWindow)))
        
        self._window.show()

#####################        
    def _okButtonWasPressed(self, *args):
        self._accelerationParentAttribute.value = self._accelerationDueToGravity.value
        self._listRebuildParentAttribute.value = self._listRebuildFrequency.value
        self._closeWindow()

#####################        
    def _closeWindow(self, *args):
        if(uib.WindowExists(self._window)):
            util.EvalDeferred(uib.DestroyWindow, self._window)

# END OF CLASS - _PreferencesWindow
#################################### 



#######################################
class GlobalAttributes(abo.AttributesBaseObject):

    @classmethod
    def DefaultSectionTitle(cls):
        return "Global Attributes"
    
#####################    
    def __init__(self, sceneBounds1=None, sceneBounds2=None):
        super(GlobalAttributes, self).__init__(GlobalAttributes.DefaultSectionTitle())
        
        self._enabled = at.BoolAttribute("Enabled", True)
        self._sceneBounds1 = at.LocationAttribute("Scene Bounds 1", util.InitVal(sceneBounds1, (-20, -20, -20)), self)
        self._sceneBounds2 = at.LocationAttribute("Scene Bounds 2", util.InitVal(sceneBounds2, (20, 20, 20)), self)
        self._sceneBounds1.excludeFromDefaults = True
        self._sceneBounds2.excludeFromDefaults = True
        self._lowerBounds = bv3.Vector3()
        self._upperBounds = bv3.Vector3()
        self._accelerationDueToGravity = at.FloatAttribute("Acceleration Due To Gravity", -38.0, 
                                                           minimumValue=float("-inf"), maximumValue=0)
        self._listRebuildFrequency = at.IntAttribute("List Rebuild Frequency", 5)
        self._useDebugColours = at.BoolAttribute("Debug Colour Particles", True)
        
        self._preferencesWindow = _PreferencesWindow(self._accelerationDueToGravity, self._listRebuildFrequency)
        
        self._updateBoundsVectors()

#####################    
    def onFrameUpdated(self):
        self._sceneBounds1.verifyLocatorIfNecessary()
        self._sceneBounds2.verifyLocatorIfNecessary()

#####################    
    def populateUiLayout(self):
        uib.MakeCheckboxGroup(self._enabled, None) 
        uib.MakeLocationField(self._sceneBounds1)
        uib.MakeLocationField(self._sceneBounds2)
        uib.MakeCheckboxGroup(self._useDebugColours, "Enable")
        
#####################        
    def showGlobalPreferencesWindow(self):
        self._preferencesWindow.show()

#####################  
    def _getEnabled(self):
        return self._enabled.value
    def _setEnabled(self, value):
        self._enabled = value
    enabled = property(_getEnabled, _setEnabled)  
    
#####################
    def _getLowerBounds(self):
        return self._lowerBounds
    lowerBounds = property(_getLowerBounds)
    
    def _getUpperBounds(self):
        return self._upperBounds
    upperBounds = property(_getUpperBounds)
    
    def _getSceneBounds1(self):
        return self._sceneBounds1.value
    def _setSceneBounds1(self, value):
        self._sceneBounds1.value = value
    sceneBounds1 = property(_getSceneBounds1, _setSceneBounds1)
    
    def _getSceneBounds2(self):
        return self._sceneBounds2.value
    def _setSceneBounds2(self, value):
        self._sceneBounds2.value = value
    sceneBounds2 = property(_getSceneBounds2, _setSceneBounds2)

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
    
#####################
    def onValueChanged(self, changedAttribute):
        super(GlobalAttributes, self).onValueChanged(changedAttribute)
        
        if(changedAttribute is self._sceneBounds1 or changedAttribute is self._sceneBounds2):
            self._updateBoundsVectors()
    
    def _updateBoundsVectors(self):
        value1 = self._sceneBounds1.value
        value2 = self._sceneBounds2.value
        
        if(value1.x <= value2.x):
            self._lowerBounds.x = value1.x
            self._upperBounds.x = value2.x
        else:
            self._lowerBounds.x = value2.x
            self._upperBounds.x = value1.x
        if(value1.y <= value2.y):
            self._lowerBounds.y = value1.y
            self._upperBounds.y = value2.y
        else:
            self._lowerBounds.y = value2.y
            self._upperBounds.y = value1.y
        if(value1.z <= value2.z):
            self._lowerBounds.z = value1.z
            self._upperBounds.z = value2.z
        else:
            self._lowerBounds.z = value2.z
            self._upperBounds.z = value1.z

# END OF CLASS
####################################    