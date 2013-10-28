
_boidConstant_DEBUG_COLOURS_ = True
_boidConstant_preferredZoneSize = 10
_boidConstant_gridHalfSize = 20
_boidConstant_accnDueToGravity = -38

_boidConstant_mainRegionSize = 4
_boidConstant_mainRegionSizeRandom = 0.0

_boidConstant_nearRegionSize = 1
_boidConstant_nearRegionRandom = 0.0

_boidConstant_collisionRegionSize = 0.2
_boidConstant_maxVel = 5
_boidConstant_minVel = 0.5
_boidConstant_maxAccel = 1
_boidConstant_maxTurnrate = 30
_boidConstant_preferredVel = 3.5
_boidConstant_herdAvDirectionThreshold = 30
_boidConstant_herdAvPositionThreshold = 1.9
_boidConstant_blindRegionAngle = 110
_boidConstant_searchModeMaxTurnrate = 40
_boidConstant_leaderModeWaypointThreshold = 3
_boidConstant_priorityGoalThreshold = 0.5  # was == 2
_boidConstant_jumpAcceleration = 65
_boidConstant_jumpOnPileUpProbability = 0.1
_boidConstant_jumpOnPileUpRegionSize = 1.5
_boidConstant_pushUpwardsAccelerationHorizontal = 15
_boidConstant_pushUpwardsAccelerationVertical = 22
_boidConstant_goalChaseSpeed = 10
_boidConstant_goalIncubationPeriod = 10
_boidConstant_curveDevianceThreshold = 3
_boidConstant_curveEndReachedThreshold = 1
_boidConstant_curveGroupVectorMagnitude = 2



##################################
def accelerationPerFrameDueToGravity():
    return _boidConstant_accnDueToGravity

def gridHalfSize():
    return _boidConstant_gridHalfSize

def preferredZoneSize():
    return _boidConstant_preferredZoneSize

def setUseDebugColours(value):
    global _boidConstant_DEBUG_COLOURS_
    _boidConstant_DEBUG_COLOURS_ = value

def useDebugColours():
    return _boidConstant_DEBUG_COLOURS_


##################################
def setMainRegionSize(value):
    """Sets size of boid's main perception radius"""
    global _boidConstant_mainRegionSize
    _boidConstant_mainRegionSize = value

def mainRegionSize(random = False):
    """Gets size of boid's main perception radius"""
    if(not random):
        return _boidConstant_mainRegionSize
    else:
        diff = _boidConstant_mainRegionSize * _boidConstant_mainRegionSizeRandom
        return _boidConstant_mainRegionSize + random.uniform(-diff, diff)

##################################
def setNearRegionSize(value):
    global _boidConstant_nearRegionSize
    _boidConstant_nearRegionSize = value

def nearRegionSize(random = False):
    return _boidConstant_nearRegionSize

##################################
def setCollisionRegionSize(value):
    global _boidConstant_collisionRegionSize
    _boidConstant_collisionRegionSize = value

def collisionRegionSize():
    return _boidConstant_collisionRegionSize

##################################
def setMaxVel(value):
    global _boidConstant_maxVel
    _boidConstant_maxVel = value

def maxVel():
    return _boidConstant_maxVel

##################################
def setMinVel(value):
    global _boidConstant_minVel
    _boidConstant_minVel = value
    
def minVel():
    return _boidConstant_minVel
##################################

def setMaxAccel(value):
    global _boidConstant_maxAccel
    _boidConstant_maxAccel = value

def maxAccel():
    return _boidConstant_maxAccel

##################################
def setPreferredVel(value):
    global _boidConstant_preferredVel
    _boidConstant_preferredVel = value

def preferredVel():
    return _boidConstant_preferredVel

##################################
def setMaxTurnrate(value):
    """Sets max amount will change direction, per frame, to match herd (in degrees)"""
    global _boidConstant_maxTurnrate
    _boidConstant_maxTurnrate = value

def maxTurnrate():
    """Gets max amount will change direction, per frame, to match herd (in degrees)"""
    return _boidConstant_maxTurnrate

##################################
def setAvDirectionThreshold(value):
    """Sets max deviation from herd avVelocity without changing direction (in degrees)"""
    global _boidConstant_herdAvDirectionThreshold
    _boidConstant_herdAvDirectionThreshold = value

def avDirectionThreshold():
    """Gets max deviation from herd avVelocity without changing direction(in degrees)"""
    return _boidConstant_herdAvDirectionThreshold

##################################
def setAvPositionTreshold(value):
    """Sets max distance from avPosition without attempting to shuffle inwards"""
    global _boidConstant_herdAvPositionThreshold
    _boidConstant_herdAvPositionThreshold = value
    
def avPositionThreshold():
    """Gets max distance from avPosition without attempting to shuffle inwards"""
    return _boidConstant_herdAvPositionThreshold

##################################
def setBlindRegionAngle(value):
    """Sets angle (in degrees, negative is anti-clockwise) of area 'behind' each boid considered a blind spot"""
    global _boidConstant_blindRegionAngle
    _boidConstant_blindRegionAngle = value

def blindRegionAngle():
    """Gets angle (in degrees, negative is anti-clockwise) of area 'behind' each boid considered a blind spot"""
    return _boidConstant_blindRegionAngle

##################################
def setSearchModeMaxTurnrate(value):
    """Sets max amount will change direction, per frame, when searching for herd (in degrees)"""
    global _boidConstant_searchModeMaxTurnrate
    _boidConstant_searchModeMaxTurnrate = value

def searchModeMaxTurnrate():
    """Gets max amount will change direction, per frame, when searching for herd (in degrees)"""
    return _boidConstant_searchModeMaxTurnrate

##################################
def setLeaderWaypointThreshold(value):
    """Sets min distance from waypoint at which it is considered as 'reached'"""
    global _boidConstant_leaderModeWaypointThreshold
    _boidConstant_leaderModeWaypointThreshold = value
    
def leaderWaypointThreshold():
    """Gets min distance from waypoint at which it is considered as 'reached'"""
    return _boidConstant_leaderModeWaypointThreshold

##################################
def setPriorityGoalThreshold(value):
    """Sets min distance from priority goal at which it's considered as 'reached'"""
    global _boidConstant_priorityGoalThreshold
    _boidConstant_priorityGoalThreshold = value
    
def priorityGoalThreshold():
    """Gets min distance from priority goal at which it's considered as 'reached'"""
    return _boidConstant_priorityGoalThreshold

##################################
def setJumpAcceleration(value):
    global _boidConstant_jumpAcceleration
    _boidConstant_jumpAcceleration = value

def jumpAcceleration():
    return _boidConstant_jumpAcceleration

##################################
def setJumpOnPileUpProbability(value):
    global _boidConstant_jumpOnPileUpProbability
    _boidConstant_jumpOnPileUpProbability = value
    
def jumpOnPileUpProbability():
    return _boidConstant_jumpOnPileUpProbability

def setJumpOnPileUpRegionSize(value):
    global _boidConstant_jumpOnPileUpRegionSize
    _boidConstant_jumpOnPileUpRegionSize = value
    
def jumpOnPileUpRegionSize():
    return _boidConstant_jumpOnPileUpRegionSize

##################################
def setPushUpwardsAcclerationHorizontal(value):
    global _boidConstant_pushUpwardsAccelerationHorizontal
    _boidConstant_pushUpwardsAccelerationHorizontal = value
    
def pushUpwardsAccelerationHorizontal():
    return _boidConstant_pushUpwardsAccelerationHorizontal

def setPushUpwardsAccelerationVertical(value):
    global _boidConstant_pushUpwardsAccelerationVertical
    _boidConstant_pushUpwardsAccelerationVertical = value    
        
def pushUpwardsAccelerationVertical():
    return _boidConstant_pushUpwardsAccelerationVertical

##################################
def setGoalChaseSpeed(value):
    global _boidConstant_goalChaseSpeed
    _boidConstant_goalChaseSpeed = value
    
def goalChaseSpeed():
    return _boidConstant_goalChaseSpeed

##################################
def setGoalIncubationPeriod(value):
    global _boidConstant_goalIncubationPeriod
    _boidConstant_goalIncubationPeriod = value
    
def goalIncubationPeriod():
    return _boidConstant_goalIncubationPeriod

##################################
def setCurveDevianceThreshold(value):
    """Sets distance from nearest point on curve beyond which boid will be pulled back towards the curve"""
    global _boidConstant_curveDevianceThreshold
    _boidConstant_curveDevianceThreshold = value

def curveDevianceThreshold():
    """Gets distance from nearest point on curve beyond which boid will be pulled back towards the curve"""
    return _boidConstant_curveDevianceThreshold

def setCurveEndReachedThreshold(value):
    """Sets proximity to end point - MEASURED FROM THE NEAREST CURVE POINT, NOT THE BOID'S ACTUAL POSITION - at which destination is considered reached"""
    global _boidConstant_curveEndReachedThreshold
    _boidConstant_curveEndReachedThreshold = value
    
def curveEndReachedThreshold():
    """Gets proximity to end point - MEASURED FROM THE NEAREST CURVE POINT, NOT THE BOID'S ACTUAL POSITION - at which destination is considered reached"""
    return _boidConstant_curveEndReachedThreshold

def setCurveGroupVectorMagnitude(value):
    global _boidConstant_curveGroupVectorMagnitude
    _boidConstant_curveGroupVectorMagnitude = value
    
def curveGroupVectorMagnitude():
    return _boidConstant_curveGroupVectorMagnitude

##################################

def printValues():
    print("mainR=%.4f, nearR=%.4f, collR=%.4f maxVl=%.4f, minVl=%.4f, maxAc=%.4f, prefV=%.4f, \n\
maxTn=%d, avDir=%d\navPos=%.4f, blindRgn=%d, searchModeTn=%d, leaderWaypt=%.4f\n\
prtyGl=%.4f, jump=%.4f, jmpProb=%.2f, jmpRgn=%.2f, pushHztl=%.4f, pushVtcl=%.4f, goalSpd=%.4f, goalInbtn=%d\n\
crvDevThsld=%.4f, crvEndThrsld=%.4f, curveGrpMag=%.4f" %
          (mainRegionSize(), nearRegionSize(), collisionRegionSize(), maxVel(), minVel(), maxAccel(), preferredVel(),
          maxTurnrate(), avDirectionThreshold(), avPositionThreshold(), blindRegionAngle(),
          searchModeMaxTurnrate(), leaderWaypointThreshold(), priorityGoalThreshold(), jumpAcceleration(), jumpOnPileUpProbability(), jumpOnPileUpRegionSize(),
          pushUpwardsAccelerationHorizontal(), pushUpwardsAccelerationVertical(), goalChaseSpeed(), goalIncubationPeriod(),
          curveDevianceThreshold(), curveEndReachedThreshold(), curveGroupVectorMagnitude()))


##########################################################################################

