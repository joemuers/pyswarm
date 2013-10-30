'''Contains all numerical values for driving the main system.
Client objects should use the setter/getter methods rather than 
accessing the variables directly.

TODO - have text file with 'default' values...

A UI would interface primarily with this module...'''

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
    """Not actively applied - used to calculate if an agent is currently touching the ground or not."""
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
    """Sets size of region within which other boids are considered to be 'crowding'"""
    global _boidConstant_nearRegionSize
    _boidConstant_nearRegionSize = value

def nearRegionSize():
    """Gets size of region within which other boids are considered to be 'crowding'"""
    return _boidConstant_nearRegionSize

##################################
def setCollisionRegionSize(value):
    """Sets size of region within which other boids are considered to be 'colliding'"""
    global _boidConstant_collisionRegionSize
    _boidConstant_collisionRegionSize = value

def collisionRegionSize():
    """Sets size of region within which other boids are considered to be 'colliding'"""
    return _boidConstant_collisionRegionSize

##################################
def setMaxVel(value):
    """Maximum velocity that boids will travel at under normal behaviour."""
    global _boidConstant_maxVel
    _boidConstant_maxVel = value

def maxVel():
    """Maximum velocity that boids will travel at under normal behaviour."""
    return _boidConstant_maxVel

##################################
def setMinVel(value):
    """Minimum velocity that boids will travel at under normal behaviour."""
    global _boidConstant_minVel
    _boidConstant_minVel = value
    
def minVel():
    """Minimum velocity that boids will travel at under normal behaviour."""
    return _boidConstant_minVel
##################################

def setMaxAccel(value):
    """Maximum acceleration that boids will apply under normal behaviour."""
    global _boidConstant_maxAccel
    _boidConstant_maxAccel = value

def maxAccel():
    """Maximum acceleration that boids will apply under normal behaviour."""
    return _boidConstant_maxAccel

##################################
def setPreferredVel(value):
    """'Cruising speed' that boids will tend towards under normal behaviour."""
    global _boidConstant_preferredVel
    _boidConstant_preferredVel = value

def preferredVel():
    """'Cruising speed' that boids will tend towards under normal behaviour."""
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
    """Acceleration applied to execute a 'jump' event."""
    global _boidConstant_jumpAcceleration
    _boidConstant_jumpAcceleration = value

def jumpAcceleration():
    """Acceleration applied to execute a 'jump' event."""
    return _boidConstant_jumpAcceleration

##################################
def setJumpOnPileUpProbability(value):
    """Probability that, upon joining a basePyramid, boid will 'jump' instead of just joining at the bottom."""
    global _boidConstant_jumpOnPileUpProbability
    _boidConstant_jumpOnPileUpProbability = value
    
def jumpOnPileUpProbability():
    """Probability that, upon joining a basePyramid, boid will 'jump' instead of just joining at the bottom."""
    return _boidConstant_jumpOnPileUpProbability

def setJumpOnPileUpRegionSize(value):
    """Distance from basePyramid at which boids will 'jump' (if they are to do so)."""
    global _boidConstant_jumpOnPileUpRegionSize
    _boidConstant_jumpOnPileUpRegionSize = value
    
def jumpOnPileUpRegionSize():
    """Distance from basePyramid at which boids will 'jump' (if they are to do so)."""
    return _boidConstant_jumpOnPileUpRegionSize

##################################
def setPushUpwardsAcclerationHorizontal(value):
    """Acceleration applied by each boid in the horizontal direction (directed towards
    the baseLocator of the priority goal) after having joined the basePyramid."""
    global _boidConstant_pushUpwardsAccelerationHorizontal
    _boidConstant_pushUpwardsAccelerationHorizontal = value
    
def pushUpwardsAccelerationHorizontal():
    """Acceleration applied by each boid in the horizontal direction (directed towards
    the baseLocator of the priority goal) after having joined the basePyramid."""
    return _boidConstant_pushUpwardsAccelerationHorizontal

def setPushUpwardsAccelerationVertical(value):
    """Acceleration applied by each boid in the vertical direction after having joined the basePyramid."""
    global _boidConstant_pushUpwardsAccelerationVertical
    _boidConstant_pushUpwardsAccelerationVertical = value    
        
def pushUpwardsAccelerationVertical():
    """Acceleration applied by each boid in the vertical direction after having joined the basePyramid."""
    return _boidConstant_pushUpwardsAccelerationVertical

##################################
def setGoalChaseSpeed(value):
    """Speed at which agents will travel towards the basePyramid (circumstances allowing) when following goal-driven behaviour."""
    global _boidConstant_goalChaseSpeed
    _boidConstant_goalChaseSpeed = value
    
def goalChaseSpeed():
    """Speed at which agents will travel towards the basePyramid (circumstances allowing) when following goal-driven behaviour."""
    return _boidConstant_goalChaseSpeed

##################################
def setGoalIncubationPeriod(value):
    """'Goal-infected' agents will wait this many frames before actively following goal-driven behaviour."""
    global _boidConstant_goalIncubationPeriod
    _boidConstant_goalIncubationPeriod = value
    
def goalIncubationPeriod():
    """'Goal-infected' agents will wait this many frames before actively following goal-driven behaviour."""
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
    """Scalar magnitude of motion vector that will be applied to agent's overall velocity when following a curve."""
    global _boidConstant_curveGroupVectorMagnitude
    _boidConstant_curveGroupVectorMagnitude = value
    
def curveGroupVectorMagnitude():
    """Scalar magnitude of motion vector that will be applied to agent's overall velocity when following a curve."""
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

