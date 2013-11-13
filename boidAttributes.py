"""Contains all numerical values for driving the main system.
Client objects should use the setter/getter methods rather than 
accessing the variables directly.

TODO - have text file with 'default' values...

A UI would interface primarily with this module..."""
import os
import sys
import ConfigParser

__DEFAULT_FILENAME__ = "/boidAttributeDefaults.ini"
__sectionTitle__ = "BoidAttributes - default values"
__attributePrefix__ = "_boidAttribute_"
__boolAttribute__, __intAttribute__, __floatAttribute__, __stringAttribute__ = range(4)


_boidAttribute_USE_DEBUG_COLOURS_ = (True, __boolAttribute__)
_boidAttribute_ACCN_DUE_TO_GRAVITY_ = (-38, __floatAttribute__)

_boidAttribute_MAIN_REGION_SIZE_ = (4, __floatAttribute__)
_boidAttribute_MAIN_REGION_SIZE_Random = (0.0, __floatAttribute__)
_boidAttribute_NEAR_REGION_SIZE_ = (1, __floatAttribute__)
_boidAttribute_NEAR_REGION_Random = (0.0, __floatAttribute__)
_boidAttribute_COLLISION_REGION_SIZE_ = (0.2, __floatAttribute__)

_boidAttribute_LIST_REBUILD_FREQUENCY_ = (5, __intAttribute__)

_boidAttribute_MAX_VELOCITY_ = (5, __floatAttribute__)
_boidAttribute_MIN_VELOCITY_ = (0.5, __floatAttribute__)
_boidAttribute_MAX_ACCELERATION_ = (1, __floatAttribute__)
_boidAttribute_MAX_TURNRATE_ = (30, __intAttribute__)
_boidAttribute_PREFERRED_VELOCITY_ = (3.5, __floatAttribute__)
_boidAttribute_HERD_AVG_DIRECTION_THRSHLD_ = (30, __intAttribute__)
_boidAttribute_HERD_AVG_POSITION_THRSHLD_ = (1.9, __floatAttribute__)
_boidAttribute_BLIND_REGION_ANGLE_ = (110, __intAttribute__)
_boidAttribute_SEARCH_MODE_MAX_TURNRATE_ = (40, __intAttribute__)
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



def readDefaultValuesFromFile(filePath=None):
    createNewFileIfNeeded = False
    if(filePath is None):
        createNewFileIfNeeded = True
        filePath = os.path.dirname(__file__) + __DEFAULT_FILENAME__

    moduleName = __name__
    if(moduleName == '__main__'):
        moduleFileName = sys.modules[moduleName].__file__
        moduleName = os.path.splitext(os.path.basename(moduleFileName))[0]
    module = sys.modules[moduleName]

    configReader = ConfigParser.ConfigParser()
    configReader.optionxform = str  # replacing this method makes option names case-sensitive
    filesRead = configReader.read(filePath)
    
    if(filesRead):
        for section in configReader.sections():
            for attributeNameStr, attributeValueStr in configReader.items(section):
                if(not attributeNameStr.startswith(__attributePrefix__)):
                    print("WARNING - found none-%s attribute \'%s\' in file \'%s\', ignoring..." %
                          (__attributePrefix__, attributeNameStr, filePath))
                else:
                    attributeTuple = getattr(module, attributeNameStr)
                    if(attributeTuple[1] == __floatAttribute__):
                        attributeTuple = (float(attributeValueStr), attributeTuple[1])
                    elif(attributeTuple[1] == __intAttribute__):
                        attributeTuple = (int(attributeValueStr), attributeTuple[1])
                    elif(attributeTuple[1] == __boolAttribute__):
                        attributeTuple = (bool(attributeValueStr), attributeTuple[1])
                    else: # it's a string if we're here.
                        attributeTuple = (attributeValueStr, attributeTuple[1])
                    print("Restored default: %s = %s" % (attributeNameStr, attributeValueStr))
    else:
        print("Could not read default attributes file: %s" % filePath)
        if(createNewFileIfNeeded):
            print("Creating new default attributes file...")
            writeDefaultValuesToFile(filePath)

##################################   
def writeDefaultValuesToFile(filePath=None):
    if(filePath is None):
        filePath = os.path.dirname(__file__) + __DEFAULT_FILENAME__
        
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
            configWriter.set(__sectionTitle__, attributeName, attributeTuple[0])
    
    defaultsFile = open(filePath, "w")   
    configWriter.write(defaultsFile)
    defaultsFile.close()
    
    print("Wrote current attributes to defaults file:%s" % filePath)

##################################
def accelerationPerFrameDueToGravity():
    """Not actively applied - used to calculate if an agent is currently touching the ground or not."""
    return _boidAttribute_ACCN_DUE_TO_GRAVITY_[0]

def setUseDebugColours(value):
    global _boidAttribute_USE_DEBUG_COLOURS_
    _boidAttribute_USE_DEBUG_COLOURS_ = (value, _boidAttribute_USE_DEBUG_COLOURS_[1])

def useDebugColours():
    return _boidAttribute_USE_DEBUG_COLOURS_[0]

##################################
def listRebuildFrequency():
    """Number of frames skipped between each refresh of agent-to-agent spatial relationships."""
    return _boidAttribute_LIST_REBUILD_FREQUENCY_[0]

def setListRebuildFrequency(value):
    """Sets number of frames skipped between each refresh of agent-to-agent spatial relationships."""
    global _boidAttribute_LIST_REBUILD_FREQUENCY_
    _boidAttribute_LIST_REBUILD_FREQUENCY_ = (int(value), _boidAttribute_LIST_REBUILD_FREQUENCY_[1])

##################################
def setMainRegionSize(value):
    """Sets size of boid's main perception radius"""
    global _boidAttribute_MAIN_REGION_SIZE_
    _boidAttribute_MAIN_REGION_SIZE_ = (value, _boidAttribute_MAIN_REGION_SIZE_[1])

def mainRegionSize(random=False):
    """Gets size of boid's main perception radius"""
    if(not random):
        return _boidAttribute_MAIN_REGION_SIZE_[0]
    else:
        diff = _boidAttribute_MAIN_REGION_SIZE_[0] * _boidAttribute_MAIN_REGION_SIZE_Random[0]
        return _boidAttribute_MAIN_REGION_SIZE_[0] + random.uniform(-diff, diff)

##################################
def setNearRegionSize(value):
    """Sets size of region within which other boids are considered to be 'crowding'"""
    global _boidAttribute_NEAR_REGION_SIZE_
    _boidAttribute_NEAR_REGION_SIZE_ = (value, _boidAttribute_NEAR_REGION_SIZE_[1])

def nearRegionSize():
    """Gets size of region within which other boids are considered to be 'crowding'"""
    return _boidAttribute_NEAR_REGION_SIZE_[0]

##################################
def setCollisionRegionSize(value):
    """Sets size of region within which other boids are considered to be 'colliding'"""
    global _boidAttribute_COLLISION_REGION_SIZE_
    _boidAttribute_COLLISION_REGION_SIZE_ = (value, _boidAttribute_COLLISION_REGION_SIZE_[1])

def collisionRegionSize():
    """Sets size of region within which other boids are considered to be 'colliding'"""
    return _boidAttribute_COLLISION_REGION_SIZE_[0]

##################################
def setMaxVel(value):
    """Maximum velocity that boids will travel at under normal behaviour."""
    global _boidAttribute_MAX_VELOCITY_
    _boidAttribute_MAX_VELOCITY_ = (value, _boidAttribute_MAX_VELOCITY_[1])

def maxVel():
    """Maximum velocity that boids will travel at under normal behaviour."""
    return _boidAttribute_MAX_VELOCITY_[0]

##################################
def setMinVel(value):
    """Minimum velocity that boids will travel at under normal behaviour."""
    global _boidAttribute_MIN_VELOCITY_
    _boidAttribute_MIN_VELOCITY_ = (value, _boidAttribute_MIN_VELOCITY_[1])
    
def minVel():
    """Minimum velocity that boids will travel at under normal behaviour."""
    return _boidAttribute_MIN_VELOCITY_[0]
##################################

def setMaxAccel(value):
    """Maximum acceleration that boids will apply under normal behaviour."""
    global _boidAttribute_MAX_ACCELERATION_
    _boidAttribute_MAX_ACCELERATION_ = (value, _boidAttribute_MAX_ACCELERATION_[1])

def maxAccel():
    """Maximum acceleration that boids will apply under normal behaviour."""
    return _boidAttribute_MAX_ACCELERATION_[0]

##################################
def setPreferredVel(value):
    """'Cruising speed' that boids will tend towards under normal behaviour."""
    global _boidAttribute_PREFERRED_VELOCITY_
    _boidAttribute_PREFERRED_VELOCITY_ = (value, _boidAttribute_PREFERRED_VELOCITY_[1])

def preferredVel():
    """'Cruising speed' that boids will tend towards under normal behaviour."""
    return _boidAttribute_PREFERRED_VELOCITY_[0]

##################################
def setMaxTurnrate(value):
    """Sets max amount will change direction, per frame, to match herd (in degrees)"""
    global _boidAttribute_MAX_TURNRATE_
    _boidAttribute_MAX_TURNRATE_ = (value, _boidAttribute_MAX_TURNRATE_[1])

def maxTurnrate():
    """Gets max amount will change direction, per frame, to match herd (in degrees)"""
    return _boidAttribute_MAX_TURNRATE_[0]

##################################
def setAvDirectionThreshold(value):
    """Sets max deviation from herd avVelocity without changing direction (in degrees)"""
    global _boidAttribute_HERD_AVG_DIRECTION_THRSHLD_
    _boidAttribute_HERD_AVG_DIRECTION_THRSHLD_ = (value, _boidAttribute_HERD_AVG_DIRECTION_THRSHLD_[1])

def avDirectionThreshold():
    """Gets max deviation from herd avVelocity without changing direction(in degrees)"""
    return _boidAttribute_HERD_AVG_DIRECTION_THRSHLD_[0]

##################################
def setAvPositionTreshold(value):
    """Sets max distance from avPosition without attempting to shuffle inwards"""
    global _boidAttribute_HERD_AVG_POSITION_THRSHLD_
    _boidAttribute_HERD_AVG_POSITION_THRSHLD_ = (value, _boidAttribute_HERD_AVG_POSITION_THRSHLD_[1])
    
def avPositionThreshold():
    """Gets max distance from avPosition without attempting to shuffle inwards"""
    return _boidAttribute_HERD_AVG_POSITION_THRSHLD_[0]

##################################
def setBlindRegionAngle(value):
    """Sets angle (in degrees, negative is anti-clockwise) of area 'behind' each boid considered a blind spot"""
    global _boidAttribute_BLIND_REGION_ANGLE_
    _boidAttribute_BLIND_REGION_ANGLE_ = (value, _boidAttribute_BLIND_REGION_ANGLE_[1])

def blindRegionAngle():
    """Gets angle (in degrees, negative is anti-clockwise) of area 'behind' each boid considered a blind spot"""
    return _boidAttribute_BLIND_REGION_ANGLE_[0]

##################################
def setSearchModeMaxTurnrate(value):
    """Sets max amount will change direction, per frame, when searching for herd (in degrees)"""
    global _boidAttribute_SEARCH_MODE_MAX_TURNRATE_
    _boidAttribute_SEARCH_MODE_MAX_TURNRATE_ = (value, _boidAttribute_SEARCH_MODE_MAX_TURNRATE_[1])

def searchModeMaxTurnrate():
    """Gets max amount will change direction, per frame, when searching for herd (in degrees)"""
    return _boidAttribute_SEARCH_MODE_MAX_TURNRATE_[0]

##################################
def setLeaderWaypointThreshold(value):
    """Sets min distance from waypoint at which it is considered as 'reached'"""
    global _boidAttribute_LDR_MODE_WAYPOINT_THRSHLD_
    _boidAttribute_LDR_MODE_WAYPOINT_THRSHLD_ = (value, _boidAttribute_LDR_MODE_WAYPOINT_THRSHLD_[1])
    
def leaderWaypointThreshold():
    """Gets min distance from waypoint at which it is considered as 'reached'"""
    return _boidAttribute_LDR_MODE_WAYPOINT_THRSHLD_[0]

##################################
def setGoalTargetDistanceThreshold(value):
    """Sets min distance from priority goal at which it's considered as 'reached'"""
    global _boidAttribute_GOAL_TARGET_DISTANCE_THRSHLD_
    _boidAttribute_GOAL_TARGET_DISTANCE_THRSHLD_ = (value, _boidAttribute_GOAL_TARGET_DISTANCE_THRSHLD_[1])
    
def goalTargetDistanceThreshold():
    """Gets min distance from priority goal at which it's considered as 'reached'"""
    return _boidAttribute_GOAL_TARGET_DISTANCE_THRSHLD_[0]

##################################
def setJumpAcceleration(value):
    """Acceleration applied to execute a 'jump' event."""
    global _boidAttribute_JUMP_ACCELERATION_
    _boidAttribute_JUMP_ACCELERATION_ = (value, _boidAttribute_JUMP_ACCELERATION_[1])

def jumpAcceleration():
    """Acceleration applied to execute a 'jump' event."""
    return _boidAttribute_JUMP_ACCELERATION_[0]

##################################
def setJumpOnPyramidProbability(value):
    """Probability that, upon joining a basePyramid, boid will 'jump' instead of just joining at the bottom."""
    global _boidAttribute_JUMP_ON_PYRAMID_PROBABILITY_
    _boidAttribute_JUMP_ON_PYRAMID_PROBABILITY_ = (value, _boidAttribute_JUMP_ON_PYRAMID_PROBABILITY_[1])
    
def jumpOnPyramidProbability():
    """Probability that, upon joining a basePyramid, boid will 'jump' instead of just joining at the bottom."""
    return _boidAttribute_JUMP_ON_PYRAMID_PROBABILITY_[0]

def setJumpOnPyramidDistanceThreshold(value):
    """Distance from basePyramid at which boids will 'jump' (if they are to do so)."""
    global _boidAttribute_JUMP_ON_PYRAMID_DISTANCE_THRSHLD_
    _boidAttribute_JUMP_ON_PYRAMID_DISTANCE_THRSHLD_ = (value, _boidAttribute_JUMP_ON_PYRAMID_DISTANCE_THRSHLD_[1])
    
def jumpOnPyramidDistanceThreshold():
    """Distance from basePyramid at which boids will 'jump' (if they are to do so)."""
    return _boidAttribute_JUMP_ON_PYRAMID_DISTANCE_THRSHLD_[0]

##################################
def setPushUpwardsAcclerationHorizontal(value):
    """Acceleration applied by each boid in the horizontal direction (directed towards
    the baseLocator of the priority goal) after having joined the basePyramid."""
    global _boidAttribute_PUSH_UPWARDS_ACCN_HORIZONTAL_
    _boidAttribute_PUSH_UPWARDS_ACCN_HORIZONTAL_ = (value, _boidAttribute_PUSH_UPWARDS_ACCN_HORIZONTAL_[1])
    
def pushUpwardsAccelerationHorizontal():
    """Acceleration applied by each boid in the horizontal direction (directed towards
    the baseLocator of the priority goal) after having joined the basePyramid."""
    return _boidAttribute_PUSH_UPWARDS_ACCN_HORIZONTAL_[0]

def setPushUpwardsAccelerationVertical(value):
    """Acceleration applied by each boid in the vertical direction after having joined the basePyramid."""
    global _boidAttribute_PUSH_UPWARDS_ACCN_VERTICAL_
    _boidAttribute_PUSH_UPWARDS_ACCN_VERTICAL_ = (value, _boidAttribute_PUSH_UPWARDS_ACCN_VERTICAL_[1])
        
def pushUpwardsAccelerationVertical():
    """Acceleration applied by each boid in the vertical direction after having joined the basePyramid."""
    return _boidAttribute_PUSH_UPWARDS_ACCN_VERTICAL_[0]

##################################
def setGoalChaseSpeed(value):
    """Speed at which agents will travel towards the basePyramid (circumstances allowing) when following goal-driven behaviour."""
    global _boidAttribute_GOAL_CHASE_SPEED_
    _boidAttribute_GOAL_CHASE_SPEED_ = (value, _boidAttribute_GOAL_CHASE_SPEED_[1])
    
def goalChaseSpeed():
    """Speed at which agents will travel towards the basePyramid (circumstances allowing) when following goal-driven behaviour."""
    return _boidAttribute_GOAL_CHASE_SPEED_[0]

##################################
def setGoalIncubationPeriod(value):
    """'Goal-infected' agents will wait this many frames before actively following goal-driven behaviour."""
    global _boidAttribute_GOAL_INCUBATION_PERIOD_
    _boidAttribute_GOAL_INCUBATION_PERIOD_ = (value, _boidAttribute_GOAL_INCUBATION_PERIOD_[1])
    
def goalIncubationPeriod():
    """'Goal-infected' agents will wait this many frames before actively following goal-driven behaviour."""
    return _boidAttribute_GOAL_INCUBATION_PERIOD_[0]

##################################
def setCurveDevianceThreshold(value):
    """Sets distance from nearest point on curve beyond which boid will be pulled back towards the curve"""
    global _boidAttribute_CURVE_DEVIANCE_THRSHLD_
    _boidAttribute_CURVE_DEVIANCE_THRSHLD_ = (value, _boidAttribute_CURVE_DEVIANCE_THRSHLD_[1])

def curveDevianceThreshold():
    """Gets distance from nearest point on curve beyond which boid will be pulled back towards the curve"""
    return _boidAttribute_CURVE_DEVIANCE_THRSHLD_[0]

def setCurveEndReachedDistanceThreshold(value):
    """Sets proximity to end point - MEASURED FROM THE NEAREST CURVE POINT, NOT THE BOID'S ACTUAL POSITION - at which destination is considered reached"""
    global _boidAttribute_CURVE_END_REACHED_DISANCE_THRSHLD_
    _boidAttribute_CURVE_END_REACHED_DISANCE_THRSHLD_ = (value, _boidAttribute_CURVE_END_REACHED_DISANCE_THRSHLD_[1])
    
def curveEndReachedDistanceThreshold():
    """Gets proximity to end point - MEASURED FROM THE NEAREST CURVE POINT, NOT THE BOID'S ACTUAL POSITION - at which destination is considered reached"""
    return _boidAttribute_CURVE_END_REACHED_DISANCE_THRSHLD_[0]

def setCurveGroupVectorMagnitude(value):
    """Scalar magnitude of motion vector that will be applied to agent's overall velocity when following a curve."""
    global _boidAttribute_CURVE_GROUP_VECTOR_MAGNITUDE_
    _boidAttribute_CURVE_GROUP_VECTOR_MAGNITUDE_ = (value, _boidAttribute_USE_DEBUG_COLOURS_[1])
    
def curveGroupVectorMagnitude():
    """Scalar magnitude of motion vector that will be applied to agent's overall velocity when following a curve."""
    return _boidAttribute_CURVE_GROUP_VECTOR_MAGNITUDE_[0]

##################################

def printValues():
    print("listIntvl=%d, mainR=%.4f, nearR=%.4f, collR=%.4f maxVl=%.4f, minVl=%.4f, maxAc=%.4f, prefV=%.4f, \n\
maxTn=%d, avDir=%d\navPos=%.4f, blindRgn=%d, searchModeTn=%d, leaderWaypt=%.4f\n\
prtyGl=%.4f, jump=%.4f, jmpProb=%.2f, jmpRgn=%.2f, pushHztl=%.4f, pushVtcl=%.4f, goalSpd=%.4f, goalInbtn=%d\n\
crvDevThsld=%.4f, crvEndThrsld=%.4f, curveGrpMag=%.4f" %
          (listRebuildFrequency(), mainRegionSize(), nearRegionSize(), collisionRegionSize(), maxVel(), minVel(), maxAccel(), preferredVel(),
          maxTurnrate(), avDirectionThreshold(), avPositionThreshold(), blindRegionAngle(),
          searchModeMaxTurnrate(), leaderWaypointThreshold(), goalTargetDistanceThreshold(), jumpAcceleration(), jumpOnPyramidProbability(), jumpOnPyramidDistanceThreshold(),
          pushUpwardsAccelerationHorizontal(), pushUpwardsAccelerationVertical(), goalChaseSpeed(), goalIncubationPeriod(),
          curveDevianceThreshold(), curveEndReachedDistanceThreshold(), curveGroupVectorMagnitude()))


##########################################################################################

