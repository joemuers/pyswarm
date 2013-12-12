"""Contains all numerical values for driving the main system.
Client objects should use the setter/getter methods rather than 
accessing the variables directly.

IMPORTANT - all attribute names must have the '_boidAttribute_' prefix in order
to be compatible with the 'readDefaultValuesFromFile' and 'writeDefaultValuesToFile' methods.
"""
import os
import sys
import ConfigParser
import random


__DEFAULTS_FILENAME__ = "/boidAttributeDefaults_new.ini"
__sectionTitle__ = "BoidAttributes - default values"
__attributePrefix__ = "_boidAttribute_"
__boolAttribute__, __intAttribute__, __floatAttribute__, __stringAttribute__, __notDefined__ = range(5)


class BoidAttributesController(object):
    
    def __init__(self):
        self._generalSection = GeneralAttributesSection()
        self._sections = [self._generalSection]
            
    def readDefaultAttributesFromFile(self, filePath=None):
        createNewFileIfNeeded = False
        if(filePath is None):
            createNewFileIfNeeded = True
            filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__
        
        configReader = ConfigParser.ConfigParser()
        configReader.optionxform = str  # replacing this method makes option names case-sensitive
        
        if(configReader.read(filePath)):
            print("Parsing file \'%s\' for default values..." % filePath)
            for section in self._sections:
                section.getDefaultsFromConfigReader(configReader)
        else:
            print("Could not read default attributes file: %s" % filePath)
            if(createNewFileIfNeeded):
                print("Creating new default attributes file...")
                self.WriteDefaultValuesToFile(filePath)
    
    def writeDefaultValuesToFile(self, filePath=None):            
        configWriter = ConfigParser.ConfigParser()
        configWriter.optionxform = str # replacing this method makes option names case-sensitive
        
        for section in self._sections:
            section.setDefaultsToConfigWriter(configWriter)
        
        if(filePath is None):
            filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__ 
        defaultsFile = open(filePath, "w")   
        configWriter.write(defaultsFile)
        defaultsFile.close()
        
        print("Wrote current attributes to defaults file:%s" % filePath)
        

class BoidAttributesListener(object):
    
    def onAttributeChanged(self, sectionObject, attributeName):
        raise NotImplemented
    
    def onDestroy(self):
        ## Must remove itself as a listener here to avoid memory leaks...
        raise NotImplemented



class _BoidAttributesBaseObject(object):
    
    def __init__(self):
        self._listeners = []
    
    def getDefaultsFromConfigReader(self, configReader):
        for attributeNameStr, attributeValueStr in configReader.items(self._sectionTitle()):
            try:
                attributeType = self._attributeTypeForAttributeName(attributeNameStr)
                if(attributeType == __floatAttribute__):
                    setattr(self, attributeNameStr, float(attributeValueStr))
                elif(attributeType == __intAttribute__):
                    setattr(self, attributeNameStr, int(attributeValueStr))
                elif(attributeType == __boolAttribute__):
                    setattr(self, attributeNameStr, bool(attributeValueStr))
                elif(attributeType == __stringAttribute__):
                    setattr(self, attributeNameStr, attributeValueStr)
                else:
                    raise TypeError("Unrecognised attribute type.")
            except Exception as e:
                print("WARNING - could not read attribute: %s (%s), ignoring..." % (attributeNameStr, e))
            else:
                print("Re-set attribute value: %s = %s" % (attributeNameStr, attributeValueStr))
    
    def setDefaultsToConfigWriter(self, configWriter):
        configWriter.add_section(self._sectionTitle())
    
        for attributeNameStr in dir(self):
            if(self._attributeTypeForAttributeName(attributeNameStr) != __notDefined__):
                try:
                    attributeValue = getattr(self, attributeNameStr)
                    configWriter.set(self._sectionTitle(), attributeNameStr, attributeValue)
                    print("Changed default attribute value: %s = %s" % (attributeNameStr, attributeValue))
                except Exception as e:
                    print("WARNING - Could not write attribute to defaults file: %s (%s)" % (attributeNameStr, e))
        
    def _sectionTitle(self):
        raise NotImplemented
    
    def _attributeTypeForAttributeName(self, attributeNameString):
        raise NotImplemented
        
    def addListener(self, listener):
        if(type(listener) != BoidAttributesListener):
            raise TypeError
        else:
            self._listeners.append(listener)
        
    def removeListener(self, listener):
        self._listeners.remove(listener)    
        
    def _notifyListeners(self, changedAttributeName):
        for listener in self._listeners:
            listener.onAttributeChanged(self, changedAttributeName)
    

class GeneralAttributesSection(_BoidAttributesBaseObject):
    
    def __init__(self):
        super(GeneralAttributesSection, self).__init__()
        
        self.accelerationDueToGravity = -38
        self._useDebugColours = True
    
    def _getUseDebugColours(self):
        return self._useDebugColours
    def _setUseDebugColours(self, value):
        if(self._useDebugColours != value):
            self._useDebugColours = value
            self._notifyListeners("useDebugColours")
    useDebugColours = property(_getUseDebugColours, _setUseDebugColours)
    
    def _attributeTypeForAttributeName(self, attributeNameString):
        if(attributeNameString == "accelerationDueToGravity"):
            return __floatAttribute__
        elif(attributeNameString == "useDebugColours"):
            return __boolAttribute__
        else:
            return __notDefined__
    
    def _sectionTitle(self):
        return "General attributes"
    

    
class RegionCharacteristicsSection(_BoidAttributesBaseObject):
    
    def __init__(self):
        super(RegionCharacteristicsSection, self).__init__()
        
        self._mainRegionSize = 4.0
        self._mainRegionSize_Random = 0.0
        self._nearRegionSize = 1.0
        self._collisionRegionSize = 0.1
        self._collisionRegionSize_Random = 0.0
        self._blindRegionAngle = 110
        self._blindRegionAngle_Random = 0.0
        self._forwardVisionAngle = 90
        self._forwardVisionAngle_Random = 0.0
        
    def _getMainRegionSize(self):
        if(self._mainRegionSize_Random == 0):
            return self._mainRegionSize
        else:
            diff = self._mainRegionSize_Random * self._mainRegionSize
            return self._mainRegionSize + random.uniform(-diff, diff)
    def _setMainRegionSize(self, value):
        if(value != self._mainRegionSize):
            self._mainRegionSize = value
            self._notifyListeners("mainRegionSize")
    mainRegionSize = property(_getMainRegionSize, _setMainRegionSize)
    
    def _getMainRegionSize_Random(self):
        return self._mainRegionSize_Random
    def _setMainRegionSize_Random(self, value):
        if(value < 0 or 0 < value):
            raise ValueError
        elif(value != self._mainRegionSize_Random):
            self._mainRegionSize_Random = value
            self._notifyListeners("mainRegionSize_Random")
    mainRegionSize_Random = property(_getMainRegionSize_Random, _setMainRegionSize_Random)
    
    def _getNearRegionSize(self):
        if(self._nearRegionSize_Random == 0):
            return self._nearRegionSize
        else:
            diff = self._nearRegionSize_Random * self._nearRegionSize
            return self._nearRegionSize + random.uniform(-diff, diff)
    def _setNearRegionSize(self, value):
        if(value != self._nearRegionSize):
            self._nearRegionSize = value
            self._notifyListeners("nearRegionSize")
    nearRegionSize = property(_getNearRegionSize, _setNearRegionSize)
    
    def _getNearRegionSize_Random(self):
        return self._nearRegionSize_Random
    def _setNearRegionSize_Random(self, value):
        if(value < 0 or 0 < value):
            raise ValueError
        elif(value != self._nearRegionSize_Random):
            self._nearRegionSize_Random = value
            self._notifyListeners("nearRegionSize_Random")
    nearRegionSize_Random = property(_getNearRegionSize_Random, _setNearRegionSize_Random)
    
    def _getCollisionRegionSize(self):
        if(self._collisionRegionSize_Random == 0):
            return self._collisionRegionSize
        else:
            diff = self._collisionRegionSize_Random * self._collisionRegionSize
            return self._collisionRegionSize + random.uniform(-diff, diff)
    def _setCollisionRegionSize(self, value):
        if(value != self._collisionRegionSize):
            self._collisionRegionSize = value
            self._notifyListeners("collisionRegionSize")
    collisionRegionSize = property(_getCollisionRegionSize, _setCollisionRegionSize)
    
    def _getCollisionRegionSize_Random(self):
        return self._collisionRegionSize_Random
    def _setCollisionRegionSize_Random(self, value):
        if(value < 0 or 0 < value):
            raise ValueError
        elif(value != self._collisionRegionSize_Random):
            self._collisionRegionSize_Random = value
            self._notifyListeners("collisionRegionSize_Random")
    collisionRegionSize_Random = property(_getCollisionRegionSize_Random, _setCollisionRegionSize_Random)
        
    def _getBlindRegionAngle(self):
        if(self._blindRegionAngle_Random == 0):
            return self._blindRegionAngle
        else:
            diff = self._blindRegionAngle_Random * self._blindRegionAngle
            return self._blindRegionAngle + random.uniform(-diff, diff)
    def _setBlindRegionAngle(self, value):
        if(value  != self._blindRegionAngle):
            self._blindRegionAngle = value
            self._notifyListeners("blindRegionAngle")
    blindRegionAngle = property(_getBlindRegionAngle, _setBlindRegionAngle)
    
    def _getBlindRegionAngle_Random(self):
        return self._blindRegionAngle_Random
    def _setBlindRegionAngle_Random(self, value):
        if(value != self._blindRegionAngle_Random):
            self._blindRegionAngle_Random = value
            self._notifyListeners("blindRegionAngle_Random")
    blindRegionAngle_Random = property(_getBlindRegionAngle_Random, _setBlindRegionAngle_Random)
    
    def _getForwardVisionAngle(self):
        if(self._forwardVisionAngle_Random == 0):
            return self._forwardVisionAngle
        else:
            diff = self._forwardVisionAngle_Random * self._forwardVisionAngle
            return self._forwardVisionAngle + random.uniform(-diff, diff)
    def _setForwardVisionAngle(self, value):
        if(value  != self._forwardVisionAngle):
            self._forwardVisionAngle = value
            self._notifyListeners("forwardVisionAngle")
    blindRegionAngle = property(_getForwardVisionAngle, _setForwardVisionAngle)
    
    def _getForwardVisionAngle_Random(self):
        return self._forwardVisionAngle_Random
    def _setForwardVisionAngle_Random(self, value):
        if(value != self._forwardVisionAngle_Random):
            self._forwardVisionAngle_Random = value
            self._notifyListeners("forwardVisionAngle_Random")
    blindRegionAngle_Random = property(_getForwardVisionAngle_Random, _setForwardVisionAngle_Random)
    
    def _attributeTypeForAttributeName(self, attributeNameString):
        if(attributeNameString == "mainRegionSize"):
            return __floatAttribute__
        elif(attributeNameString == "mainRegionSize_Random"):
            return __floatAttribute__
        elif(attributeNameString == "nearRegionSize"):
            return __floatAttribute__
        elif(attributeNameString == "nearRegionSize_Random"):
            return __floatAttribute__
        elif(attributeNameString == "collisionRegionSize"):
            return __floatAttribute__
        elif(attributeNameString == "collisionRegionSize_Random"):
            return __floatAttribute__
        elif(attributeNameString == "blindRegionAngle"):
            return __intAttribute__
        elif(attributeNameString == "blindRegionAngle_Random"):
            return __floatAttribute__
        elif(attributeNameString == "forwardVisionAngle"):
            return __intAttribute__
        elif(attributeNameString == "forwardVisionAngle_Random"):
            return __floatAttribute__
        else:
            return __notDefined__
        
    def _sectionTitle(self):
        return "Region characteristics"
    

        
        
class ClassicBoidCharacteristicsSection(_BoidAttributesBaseObject):
    
    def __init__(self):
        super(ClassicBoidCharacteristicsSection, self).__init__()
        
        self._herdAverageDirectionThreshold = 30
        self._herdAverageDirectionThreshold_Random = 0.0
        self._headAveragePositionThreshold = 1.9
        self._headAveragePositionThreshold_Random = 0.0
        
    def _getHerdAverageDirectionThresholdSize(self):
        if(self._herdAverageDirectionThresholdSize_Random == 0):
            return self._herdAverageDirectionThresholdSize
        else:
            diff = self._herdAverageDirectionThresholdSize_Random * self._herdAverageDirectionThresholdSize
            return self._herdAverageDirectionThresholdSize + random.uniform(-diff, diff)
    def _setHerdAverageDirectionThresholdSize(self, value):
        if(value != self._herdAverageDirectionThresholdSize):
            self._herdAverageDirectionThresholdSize = value
            self._notifyListeners("herdAverageDirectionThresholdSize")
    herdAverageDirectionThresholdSize = property(_getHerdAverageDirectionThresholdSize, _setHerdAverageDirectionThresholdSize)
        
    def _getHerdAverageDirectionThresholdSize_Random(self):
        return self._herdAverageDirectionThresholdSize_Random
    def _setHerdAverageDirectionThresholdSize_Random(self, value):
        if(value < 0 or 0 < value):
            raise ValueError
        elif(value != self._herdAverageDirectionThresholdSize_Random):
            self._herdAverageDirectionThresholdSize_Random = value
            self._notifyListeners("herdAverageDirectionThresholdSize_Random")
    herdAverageDirectionThresholdSize_Random = property(_getHerdAverageDirectionThresholdSize_Random, _setHerdAverageDirectionThresholdSize_Random)
        
    def _getHerdAveragePositionThresholdSize(self):
        if(self._herdAveragePositionThresholdSize_Random == 0):
            return self._herdAveragePositionThresholdSize
        else:
            diff = self._herdAveragePositionThresholdSize_Random * self._herdAveragePositionThresholdSize
            return self._herdAveragePositionThresholdSize + random.uniform(-diff, diff)
    def _setHerdAveragePositionThresholdSize(self, value):
        if(value != self._herdAveragePositionThresholdSize):
            self._herdAveragePositionThresholdSize = value
            self._notifyListeners("herdAveragePositionThresholdSize")
    herdAveragePositionThresholdSize = property(_getHerdAveragePositionThresholdSize, _setHerdAveragePositionThresholdSize)
        
    def _getHerdAveragePositionThresholdSize_Random(self):
        return self._herdAveragePositionThresholdSize_Random
    def _setHerdAveragePositionThresholdSize_Random(self, value):
        if(value < 0 or 0 < value):
            raise ValueError
        elif(value != self._herdAveragePositionThresholdSize_Random):
            self._herdAveragePositionThresholdSize_Random = value
            self._notifyListeners("herdAveragePositionThresholdSize_Random")
    herdAveragePositionThresholdSize_Random = property(_getHerdAveragePositionThresholdSize_Random, _setHerdAveragePositionThresholdSize_Random)
    
    def _attributeTypeForAttributeName(self, attributeNameString):
        if(attributeNameString == "herdAveragePositionThresholdSize"):
            return __intAttribute__
        elif(attributeNameString == "herdAveragePositionThresholdSize_Random"):
            return __floatAttribute__
        else:
            return __notDefined__
        
    def _sectionTitle(self):
        return "Classic boid"
    
    
    
class AgentMovementAttributes(_BoidAttributesBaseObject):
    
    def __init__(self):
        super(AgentMovementAttributes, self).__init__()
        
        self._maxVelocity = 5.0
        self._minVelocity = 0.5
        self._preferredVelocity = 3.5
        self._maxAcceleration = 1
        self._maxTurnRate = 5
        self._maxTurnRateChange = 4
        self._preferredTurnVelocity = 0.5
        
    
    
 
################################## 

_boidAttribute_USE_DEBUG_COLOURS_ = (True, __boolAttribute__)
_boidAttribute_ACCN_DUE_TO_GRAVITY_ = (-38, __floatAttribute__)

_boidAttribute_LIST_REBUILD_FREQUENCY_ = (5, __intAttribute__)

_boidAttribute_MAIN_REGION_SIZE_ = (4, __floatAttribute__)
_boidAttribute_MAIN_REGION_SIZE_Random = (0.0, __floatAttribute__)
_boidAttribute_NEAR_REGION_SIZE_ = (1, __floatAttribute__)
_boidAttribute_NEAR_REGION_Random = (0.0, __floatAttribute__)
_boidAttribute_COLLISION_REGION_SIZE_ = (0.2, __floatAttribute__)

_boidAttribute_MAX_VELOCITY_ = (5, __floatAttribute__)
_boidAttribute_MIN_VELOCITY_ = (0.5, __floatAttribute__)
_boidAttribute_PREFERRED_VELOCITY_ = (3.5, __floatAttribute__)
_boidAttribute_MAX_ACCELERATION_ = (1, __floatAttribute__)
_boidAttribute_MAX_TURN_RATE_ = (5, __intAttribute__)
_boidAttribute_MAX_TURN_ANGULAR_ACCLN_ = (4, __intAttribute__)
_boidAttribute_PREFERRED_TURN_VELOCITY_  = (0.5, __floatAttribute__)

_boidAttribute_HERD_AVG_DIRECTION_THRSHLD_ = (30, __intAttribute__)
_boidAttribute_HERD_AVG_POSITION_THRSHLD_ = (1.9, __floatAttribute__)
_boidAttribute_BLIND_REGION_ANGLE_ = (110, __intAttribute__)
_boidAttribute_FORWARD_VISION_ANGLE_ = (90, __intAttribute__)

_boidAttribute_LDR_MODE_WAYPOINT_THRSHLD_ = (3, __floatAttribute__)

_boidAttribute_GOAL_TARGET_DISTANCE_THRSHLD_ = (0.5, __floatAttribute__)
_boidAttribute_JUMP_ACCELERATION_ = (65, __floatAttribute__)
_boidAttribute_JUMP_ON_PYRAMID_PROBABILITY_ = (0.1, __floatAttribute__)
_boidAttribute_JUMP_ON_PYRAMID_DISTANCE_THRSHLD_ = (1.5, __floatAttribute__)
_boidAttribute_PUSH_UPWARDS_ACCN_HORIZONTAL_ = (15, __floatAttribute__)
_boidAttribute_PUSH_UPWARDS_ACCN_VERTICAL_ = (22, __floatAttribute__)
_boidAttribute_GOAL_CHASE_SPEED_ = (10, __floatAttribute__)
_boidAttribute_GOAL_INCUBATION_PERIOD_ = (10, __floatAttribute__)

_boidAttribute_CURVE_DEVIANCE_THRSHLD_ = (3, __floatAttribute__)
_boidAttribute_CURVE_END_REACHED_DISANCE_THRSHLD_ = (1, __floatAttribute__)
_boidAttribute_CURVE_GROUP_VECTOR_MAGNITUDE_ = (2, __floatAttribute__)

################################## 

def ReadDefaultValuesFromFile(filePath=None):
    createNewFileIfNeeded = False
    if(filePath is None):
        createNewFileIfNeeded = True
        filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__

    moduleName = __name__
    if(moduleName == '__main__'):
        moduleFilePath = sys.modules[moduleName].__file__
        moduleName = os.path.splitext(os.path.basename(moduleFilePath))[0]
    module = sys.modules[moduleName]
    
    configReader = ConfigParser.ConfigParser()
    configReader.optionxform = str  # replacing this method makes option names case-sensitive
    
    if(configReader.read(filePath)):
        print("Parsing file \'%s\' for default values..." % filePath)
        prefixLength = len(__attributePrefix__)
        for section in configReader.sections():
            for attributeNameStr, attributeValueStr in configReader.items(section):
                try:
                    if(not attributeNameStr.startswith(__attributePrefix__)):
                        raise ValueError("No \"%s\" prefix" % __attributePrefix__)
                    else:
                        attributeTuple = getattr(module, attributeNameStr)
                        if(attributeTuple[1] == __floatAttribute__):
                            attributeTuple = (float(attributeValueStr), attributeTuple[1])
                        elif(attributeTuple[1] == __intAttribute__):
                            attributeTuple = (int(attributeValueStr), attributeTuple[1])
                        elif(attributeTuple[1] == __boolAttribute__):
                            attributeTuple = (bool(attributeValueStr), attributeTuple[1])
                        elif(attributeTuple[1] == __stringAttribute__):
                            attributeTuple = (attributeValueStr, attributeTuple[1])
                        else:
                            raise TypeError("Unrecognised attribute type.")
                except Exception as e:
                    print("WARNING - could not read attribute: %s (%s), ignoring..." % (attributeNameStr, e))
                else:
                    print("Re-set attribute value: %s = %s" % (attributeNameStr[prefixLength:], attributeValueStr))
    else:
        print("Could not read default attributes file: %s" % filePath)
        if(createNewFileIfNeeded):
            print("Creating new default attributes file...")
            WriteDefaultValuesToFile(filePath)

##################################   
def WriteDefaultValuesToFile(filePath=None):
    if(filePath is None):
        filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__
        
    moduleName = __name__
    if(moduleName == '__main__'):
        moduleFileName = sys.modules[moduleName].__file__
        moduleName = os.path.splitext(os.path.basename(moduleFileName))[0]
    module = sys.modules[moduleName]    
    
    configWriter = ConfigParser.ConfigParser()
    configWriter.optionxform = str # replacing this method makes option names case-sensitive
    configWriter.add_section(__sectionTitle__)
    
    for attributeName in dir(module):
        if(attributeName.startswith(__attributePrefix__)):
            attributeTuple = getattr(module, attributeName)
            try:
                configWriter.set(__sectionTitle__, attributeName, attributeTuple[0])
            except Exception as e:
                print("WARNING - Could not write attribute: %s (%s)" % (attributeName, e))
    
    defaultsFile = open(filePath, "w")   
    configWriter.write(defaultsFile)
    defaultsFile.close()
    
    print("Wrote current attributes to defaults file:%s" % filePath)

##################################
def AccelerationPerFrameDueToGravity():
    """Not actively applied - used to calculate if an agent is currently touching the ground or not."""
    return _boidAttribute_ACCN_DUE_TO_GRAVITY_[0]

def SetUseDebugColours(value):
    global _boidAttribute_USE_DEBUG_COLOURS_
    _boidAttribute_USE_DEBUG_COLOURS_ = (value, _boidAttribute_USE_DEBUG_COLOURS_[1])

def UseDebugColours():
    return _boidAttribute_USE_DEBUG_COLOURS_[0]

##################################
def ListRebuildFrequency():
    """Number of frames skipped between each refresh of agent-to-agent spatial relationships."""
    return _boidAttribute_LIST_REBUILD_FREQUENCY_[0]

def SetListRebuildFrequency(value):
    """Sets number of frames skipped between each refresh of agent-to-agent spatial relationships."""
    global _boidAttribute_LIST_REBUILD_FREQUENCY_
    _boidAttribute_LIST_REBUILD_FREQUENCY_ = (int(value), _boidAttribute_LIST_REBUILD_FREQUENCY_[1])

##################################
def SetMainRegionSize(value):
    """Sets size of agent's main perception radius"""
    global _boidAttribute_MAIN_REGION_SIZE_
    if(value > NearRegionSize()):
        raise ValueError("Cannot set mainRegionSize - must be larger than nearRegionSize (%.2f)" % NearRegionSize())
    
    _boidAttribute_MAIN_REGION_SIZE_[0] = value

def MainRegionSize(random=False):
    """Gets size of agent's main perception radius"""
    if(not random):
        return _boidAttribute_MAIN_REGION_SIZE_[0]
    else:
        diff = _boidAttribute_MAIN_REGION_SIZE_[0] * _boidAttribute_MAIN_REGION_SIZE_Random[0]
        return _boidAttribute_MAIN_REGION_SIZE_[0] + random.uniform(-diff, diff)

##################################
def SetNearRegionSize(value):
    """Sets size of region, as a fraction of mainRegionSize, within which other agents are considered to be 'crowding'"""
    global _boidAttribute_NEAR_REGION_SIZE_
    
    if(value > MainRegionSize()):
        raise ValueError("Cannot set nearRegionSize - must be smaller than mainRegionSize (%.2f)" % MainRegionSize())
    
    _boidAttribute_NEAR_REGION_SIZE_[0] = value

def NearRegionSize():
    """Gets size of region within which other agents are considered to be 'crowding'"""
    return _boidAttribute_NEAR_REGION_SIZE_[0]

##################################
def Set_herdAverageDirectionThreshold(value):
    """Sets size of region within which other agents are considered to be 'colliding'"""
    global _boidAttribute_COLLISION_REGION_SIZE_
    _boidAttribute_COLLISION_REGION_SIZE_ = (value, _boidAttribute_COLLISION_REGION_SIZE_[1])
    if(NearRegionSize() <= CollisionRegionSize()):
        print("WARNING - near region <= collision region size.")

def CollisionRegionSize():
    """Sets size of region within which other agents are considered to be 'colliding'"""
    return _boidAttribute_COLLISION_REGION_SIZE_[0]

##################################
def SetMaxVelocity(value):
    """Maximum velocity that agents will travel at under normal behaviour."""
    global _boidAttribute_MAX_VELOCITY_
    _boidAttribute_MAX_VELOCITY_ = (value, _boidAttribute_MAX_VELOCITY_[1])

def MaxVelocity():
    """Maximum velocity that agents will travel at under normal behaviour."""
    return _boidAttribute_MAX_VELOCITY_[0]

##################################
def SetMinVelocity(value):
    """Minimum velocity that agents will travel at under normal behaviour."""
    global _boidAttribute_MIN_VELOCITY_
    _boidAttribute_MIN_VELOCITY_ = (value, _boidAttribute_MIN_VELOCITY_[1])
    
def MinVelocity():
    """Minimum velocity that agents will travel at under normal behaviour."""
    return _boidAttribute_MIN_VELOCITY_[0]
##################################

def SetMaxAcceleration(value):
    """Maximum acceleration that agents will apply under normal behaviour."""
    global _boidAttribute_MAX_ACCELERATION_
    _boidAttribute_MAX_ACCELERATION_ = (value, _boidAttribute_MAX_ACCELERATION_[1])

def MaxAcceleration():
    """Maximum acceleration that agents will apply under normal behaviour."""
    return _boidAttribute_MAX_ACCELERATION_[0]

##################################
def SetPreferredVelocity(value):
    """'Cruising speed' that agents will tend towards under normal behaviour."""
    global _boidAttribute_PREFERRED_VELOCITY_
    _boidAttribute_PREFERRED_VELOCITY_ = (value, _boidAttribute_PREFERRED_VELOCITY_[1])

def PreferredVelocity():
    """'Cruising speed' that agents will tend towards under normal behaviour."""
    return _boidAttribute_PREFERRED_VELOCITY_[0]

##################################
def SetAvDirectionThreshold(value):
    """Sets max deviation from herd avVelocity without changing direction (in degrees)"""
    global _boidAttribute_HERD_AVG_DIRECTION_THRSHLD_
    _boidAttribute_HERD_AVG_DIRECTION_THRSHLD_ = (value, _boidAttribute_HERD_AVG_DIRECTION_THRSHLD_[1])

def AvDirectionThreshold():
    """Gets max deviation from herd avVelocity without changing direction(in degrees)"""
    return _boidAttribute_HERD_AVG_DIRECTION_THRSHLD_[0]

##################################
def SetAvPositionTreshold(value):
    """Sets max distance from avPosition without attempting to shuffle inwards"""
    global _boidAttribute_HERD_AVG_POSITION_THRSHLD_
    _boidAttribute_HERD_AVG_POSITION_THRSHLD_ = (value, _boidAttribute_HERD_AVG_POSITION_THRSHLD_[1])
    
def AvPositionThreshold():
    """Gets max distance from avPosition without attempting to shuffle inwards"""
    return _boidAttribute_HERD_AVG_POSITION_THRSHLD_[0]

##################################
def SetBlindRegionAngle(value):
    """Sets angle (in degrees) of area 'behind' each agent considered a blind spot"""
    global _boidAttribute_BLIND_REGION_ANGLE_
    _boidAttribute_BLIND_REGION_ANGLE_ = (value, _boidAttribute_BLIND_REGION_ANGLE_[1])

def BlindRegionAngle():
    """Gets angle (in degrees) of area 'behind' each agent considered a blind spot"""
    return _boidAttribute_BLIND_REGION_ANGLE_[0]

##################################
def SetForwardVisionRegionAngle(value):
    """Sets angle (in degrees) of area in front of each agent within which other agents will always be
    fully 'perceived' regardless of the agent's velocity."""
    global _boidAttribute_FORWARD_VISION_ANGLE_
    _boidAttribute_FORWARD_VISION_ANGLE_ = (value, _boidAttribute_FORWARD_VISION_ANGLE_[1])

def ForwardVisionRegionAngle():
    """Gets angle (in degrees) of area in front of each agent within which other agents will always be
    fully 'perceived' regardless of the agent's velocity."""
    return _boidAttribute_FORWARD_VISION_ANGLE_[0]

##################################
def SetMaxTurnRate(value):
    """Sets max amount of change in direction an agent can make **per frame** (in degrees)"""
    global _boidAttribute_MAX_TURN_RATE_
    _boidAttribute_MAX_TURN_RATE_ = (value, _boidAttribute_MAX_TURN_RATE_[1])

def MaxTurnRate():
    """Gets max amount of change in direction an agent can make **per frame** (in degrees)"""
    return _boidAttribute_MAX_TURN_RATE_[0]

##################################
def SetMaxTurnAngularAcceleration(value):
    """Sets max rate of change of the turning angle an agent can make when rotating at low velocity (high value prevents
    'jitter'-like behaviour, but restricts movement)."""
    global _boidAttribute_MAX_TURN_ANGULAR_ACCLN_
    _boidAttribute_MAX_TURN_ANGULAR_ACCLN_ = (value, _boidAttribute_MAX_TURN_ANGULAR_ACCLN_[1])
    
def MaxTurnAngularAcceleration():
    """Sets max rate of change of the turning angle an agent can make when rotating at low velocity (high value prevents
    'jitter'-like behaviour, but restricts movement)."""
    return _boidAttribute_MAX_TURN_ANGULAR_ACCLN_[0]

##################################
def SetPreferredTurnVelocity(value):
    """Sets speed (i.e. velocity's magnitude) at which agents will travel whilst turning at a rate equal 
    to or above MaxTurnRate."""
    global _boidAttribute_PREFERRED_TURN_VELOCITY_ 
    _boidAttribute_PREFERRED_TURN_VELOCITY_ = (value, _boidAttribute_PREFERRED_TURN_VELOCITY_[1])
    
def PreferredTurnVelocity():
    """Gets speed (i.e. velocity's magnitude) at which agents will travel whilst turning at a rate equal 
    to or above MaxTurnRate."""
    return _boidAttribute_PREFERRED_TURN_VELOCITY_[0]
    
##################################
def SetLeaderWaypointThreshold(value):
    """Sets min distance from waypoint at which it is considered as 'reached'"""
    global _boidAttribute_LDR_MODE_WAYPOINT_THRSHLD_
    _boidAttribute_LDR_MODE_WAYPOINT_THRSHLD_ = (value, _boidAttribute_LDR_MODE_WAYPOINT_THRSHLD_[1])
    
def LeaderWaypointThreshold():
    """Gets min distance from waypoint at which it is considered as 'reached'"""
    return _boidAttribute_LDR_MODE_WAYPOINT_THRSHLD_[0]

##################################
def SetGoalTargetDistanceThreshold(value):
    """Sets min distance from priority goal at which it's considered as 'reached'"""
    global _boidAttribute_GOAL_TARGET_DISTANCE_THRSHLD_
    _boidAttribute_GOAL_TARGET_DISTANCE_THRSHLD_ = (value, _boidAttribute_GOAL_TARGET_DISTANCE_THRSHLD_[1])
    
def GoalTargetDistanceThreshold():
    """Gets min distance from priority goal at which it's considered as 'reached'"""
    return _boidAttribute_GOAL_TARGET_DISTANCE_THRSHLD_[0]

##################################
def SetJumpAcceleration(value):
    """Acceleration applied to execute a 'jump' event."""
    global _boidAttribute_JUMP_ACCELERATION_
    _boidAttribute_JUMP_ACCELERATION_ = (value, _boidAttribute_JUMP_ACCELERATION_[1])

def JumpAcceleration():
    """Acceleration applied to execute a 'jump' event."""
    return _boidAttribute_JUMP_ACCELERATION_[0]

##################################
def SetJumpOnPyramidProbability(value):
    """Probability that, upon joining a basePyramid, agent will 'jump' instead of just joining at the bottom."""
    global _boidAttribute_JUMP_ON_PYRAMID_PROBABILITY_
    _boidAttribute_JUMP_ON_PYRAMID_PROBABILITY_ = (value, _boidAttribute_JUMP_ON_PYRAMID_PROBABILITY_[1])
    
def JumpOnPyramidProbability():
    """Probability that, upon joining a basePyramid, agent will 'jump' instead of just joining at the bottom."""
    return _boidAttribute_JUMP_ON_PYRAMID_PROBABILITY_[0]

def SetJumpOnPyramidDistanceThreshold(value):
    """Distance from basePyramid at which agents will 'jump' (if they are to do so)."""
    global _boidAttribute_JUMP_ON_PYRAMID_DISTANCE_THRSHLD_
    _boidAttribute_JUMP_ON_PYRAMID_DISTANCE_THRSHLD_ = (value, _boidAttribute_JUMP_ON_PYRAMID_DISTANCE_THRSHLD_[1])
    
def JumpOnPyramidDistanceThreshold():
    """Distance from basePyramid at which agents will 'jump' (if they are to do so)."""
    return _boidAttribute_JUMP_ON_PYRAMID_DISTANCE_THRSHLD_[0]

##################################
def SetPushUpwardsAcclerationHorizontal(value):
    """Acceleration applied by each agent in the horizontal direction (directed towards
    the baseLocator of the priority goal) after having joined the basePyramid."""
    global _boidAttribute_PUSH_UPWARDS_ACCN_HORIZONTAL_
    _boidAttribute_PUSH_UPWARDS_ACCN_HORIZONTAL_ = (value, _boidAttribute_PUSH_UPWARDS_ACCN_HORIZONTAL_[1])
    
def PushUpwardsAccelerationHorizontal():
    """Acceleration applied by each agent in the horizontal direction (directed towards
    the baseLocator of the priority goal) after having joined the basePyramid."""
    return _boidAttribute_PUSH_UPWARDS_ACCN_HORIZONTAL_[0]

def SetPushUpwardsAccelerationVertical(value):
    """Acceleration applied by each agent in the vertical direction after having joined the basePyramid."""
    global _boidAttribute_PUSH_UPWARDS_ACCN_VERTICAL_
    _boidAttribute_PUSH_UPWARDS_ACCN_VERTICAL_ = (value, _boidAttribute_PUSH_UPWARDS_ACCN_VERTICAL_[1])
        
def PushUpwardsAccelerationVertical():
    """Acceleration applied by each agent in the vertical direction after having joined the basePyramid."""
    return _boidAttribute_PUSH_UPWARDS_ACCN_VERTICAL_[0]

##################################
def SetGoalChaseSpeed(value):
    """Speed at which agents will travel towards the basePyramid (circumstances allowing) when following goal-driven behaviour."""
    global _boidAttribute_GOAL_CHASE_SPEED_
    _boidAttribute_GOAL_CHASE_SPEED_ = (value, _boidAttribute_GOAL_CHASE_SPEED_[1])
    
def GoalChaseSpeed():
    """Speed at which agents will travel towards the basePyramid (circumstances allowing) when following goal-driven behaviour."""
    return _boidAttribute_GOAL_CHASE_SPEED_[0]

##################################
def SetGoalIncubationPeriod(value):
    """'Goal-infected' agents will wait this many frames before actively following goal-driven behaviour."""
    global _boidAttribute_GOAL_INCUBATION_PERIOD_
    _boidAttribute_GOAL_INCUBATION_PERIOD_ = (value, _boidAttribute_GOAL_INCUBATION_PERIOD_[1])
    
def GoalIncubationPeriod():
    """'Goal-infected' agents will wait this many frames before actively following goal-driven behaviour."""
    return _boidAttribute_GOAL_INCUBATION_PERIOD_[0]

##################################
def SetCurveDevianceThreshold(value):
    """Sets distance from nearest point on curve beyond which agent will be pulled back towards the curve"""
    global _boidAttribute_CURVE_DEVIANCE_THRSHLD_
    _boidAttribute_CURVE_DEVIANCE_THRSHLD_ = (value, _boidAttribute_CURVE_DEVIANCE_THRSHLD_[1])

def CurveDevianceThreshold():
    """Gets distance from nearest point on curve beyond which agent will be pulled back towards the curve"""
    return _boidAttribute_CURVE_DEVIANCE_THRSHLD_[0]

def SetCurveEndReachedDistanceThreshold(value):
    """Sets proximity to end point - MEASURED FROM THE NEAREST CURVE POINT, NOT THE AGENT'S ACTUAL POSITION - at which destination is considered reached"""
    global _boidAttribute_CURVE_END_REACHED_DISANCE_THRSHLD_
    _boidAttribute_CURVE_END_REACHED_DISANCE_THRSHLD_ = (value, _boidAttribute_CURVE_END_REACHED_DISANCE_THRSHLD_[1])
    
def CurveEndReachedDistanceThreshold():
    """Gets proximity to end point - MEASURED FROM THE NEAREST CURVE POINT, NOT THE AGENT'S ACTUAL POSITION - at which destination is considered reached"""
    return _boidAttribute_CURVE_END_REACHED_DISANCE_THRSHLD_[0]

def SetCurveGroupVectorMagnitude(value):
    """Scalar magnitude of motion vector that will be applied to agent's overall velocity when following a curve."""
    global _boidAttribute_CURVE_GROUP_VECTOR_MAGNITUDE_
    _boidAttribute_CURVE_GROUP_VECTOR_MAGNITUDE_ = (value, _boidAttribute_USE_DEBUG_COLOURS_[1])
    
def CurveGroupVectorMagnitude():
    """Scalar magnitude of motion vector that will be applied to agent's overall velocity when following a curve."""
    return _boidAttribute_CURVE_GROUP_VECTOR_MAGNITUDE_[0]

##################################

def PrintValues():
    moduleName = __name__
    if(moduleName == '__main__'):
        moduleFileName = sys.modules[moduleName].__file__
        moduleName = os.path.splitext(os.path.basename(moduleFileName))[0]
    module = sys.modules[moduleName]    
    prefixLength = len(__attributePrefix__)
    
    print("BoidAttribute values...")
    for attributeName in dir(module):
        if(attributeName.startswith(__attributePrefix__)):
            attributeTuple = getattr(module, attributeName)
            if(attributeTuple[1] == __intAttribute__):
                print("\t%s  =  %d" % (attributeName[prefixLength:], attributeTuple[0]))
            elif(attributeTuple[1] == __floatAttribute__):
                print("\t%s  =  %.4f" % (attributeName[prefixLength:], attributeTuple[0]))
            elif(attributeTuple[1] == __boolAttribute__):
                print("\t%s  =  %s" % (attributeName[prefixLength:], "True" if(attributeTuple[0]) else "False"))
            else:
                print("\t%s  =  %s" % (attributeName[prefixLength:], attributeTuple[0]))


##########################################################################################


## INITALISATION...
ReadDefaultValuesFromFile()

