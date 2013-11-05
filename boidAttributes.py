"""Contains all numerical values for driving the main system.
Client objects should use the setter/getter methods rather than 
accessing the variables directly.

TODO - have text file with 'default' values...

A UI would interface primarily with this module..."""


_boidAttribute_DEBUG_COLOURS_ = True
_boidAttribute_preferredZoneSize = 10
_boidAttribute_gridHalfSize = 20
_boidAttribute_accnDueToGravity = -38

_boidAttribute_mainRegionSize = 4
_boidAttribute_mainRegionSizeRandom = 0.0

_boidAttribute_nearRegionSize = 1
_boidAttribute_nearRegionRandom = 0.0

_boidAttribute_collisionRegionSize = 0.2
_boidAttribute_maxVel = 5
_boidAttribute_minVel = 0.5
_boidAttribute_maxAccel = 1
_boidAttribute_maxTurnrate = 30
_boidAttribute_preferredVel = 3.5
_boidAttribute_herdAvDirectionThreshold = 30
_boidAttribute_herdAvPositionThreshold = 1.9
_boidAttribute_blindRegionAngle = 110
_boidAttribute_searchModeMaxTurnrate = 40
_boidAttribute_leaderModeWaypointThreshold = 3
_boidAttribute_priorityGoalThreshold = 0.5  # was == 2
_boidAttribute_jumpAcceleration = 65
_boidAttribute_jumpOnPileUpProbability = 0.1
_boidAttribute_jumpOnPileUpRegionSize = 1.5
_boidAttribute_pushUpwardsAccelerationHorizontal = 15
_boidAttribute_pushUpwardsAccelerationVertical = 22
_boidAttribute_goalChaseSpeed = 10
_boidAttribute_goalIncubationPeriod = 10
_boidAttribute_curveDevianceThreshold = 3
_boidAttribute_curveEndReachedThreshold = 1
_boidAttribute_curveGroupVectorMagnitude = 2



##################################
def accelerationPerFrameDueToGravity():
    """Not actively applied - used to calculate if an agent is currently touching the ground or not."""
    return _boidAttribute_accnDueToGravity

def gridHalfSize():
    return _boidAttribute_gridHalfSize

def preferredZoneSize():
    return _boidAttribute_preferredZoneSize

def setUseDebugColours(value):
    global _boidAttribute_DEBUG_COLOURS_
    _boidAttribute_DEBUG_COLOURS_ = value

def useDebugColours():
    return _boidAttribute_DEBUG_COLOURS_


##################################
def setMainRegionSize(value):
    """Sets size of boid's main perception radius"""
    global _boidAttribute_mainRegionSize
    _boidAttribute_mainRegionSize = value

def mainRegionSize(random = False):
    """Gets size of boid's main perception radius"""
    if(not random):
        return _boidAttribute_mainRegionSize
    else:
        diff = _boidAttribute_mainRegionSize * _boidAttribute_mainRegionSizeRandom
        return _boidAttribute_mainRegionSize + random.uniform(-diff, diff)

##################################
def setNearRegionSize(value):
    """Sets size of region within which other boids are considered to be 'crowding'"""
    global _boidAttribute_nearRegionSize
    _boidAttribute_nearRegionSize = value

def nearRegionSize():
    """Gets size of region within which other boids are considered to be 'crowding'"""
    return _boidAttribute_nearRegionSize

##################################
def setCollisionRegionSize(value):
    """Sets size of region within which other boids are considered to be 'colliding'"""
    global _boidAttribute_collisionRegionSize
    _boidAttribute_collisionRegionSize = value

def collisionRegionSize():
    """Sets size of region within which other boids are considered to be 'colliding'"""
    return _boidAttribute_collisionRegionSize

##################################
def setMaxVel(value):
    """Maximum velocity that boids will travel at under normal behaviour."""
    global _boidAttribute_maxVel
    _boidAttribute_maxVel = value

def maxVel():
    """Maximum velocity that boids will travel at under normal behaviour."""
    return _boidAttribute_maxVel

##################################
def setMinVel(value):
    """Minimum velocity that boids will travel at under normal behaviour."""
    global _boidAttribute_minVel
    _boidAttribute_minVel = value
    
def minVel():
    """Minimum velocity that boids will travel at under normal behaviour."""
    return _boidAttribute_minVel
##################################

def setMaxAccel(value):
    """Maximum acceleration that boids will apply under normal behaviour."""
    global _boidAttribute_maxAccel
    _boidAttribute_maxAccel = value

def maxAccel():
    """Maximum acceleration that boids will apply under normal behaviour."""
    return _boidAttribute_maxAccel

##################################
def setPreferredVel(value):
    """'Cruising speed' that boids will tend towards under normal behaviour."""
    global _boidAttribute_preferredVel
    _boidAttribute_preferredVel = value

def preferredVel():
    """'Cruising speed' that boids will tend towards under normal behaviour."""
    return _boidAttribute_preferredVel

##################################
def setMaxTurnrate(value):
    """Sets max amount will change direction, per frame, to match herd (in degrees)"""
    global _boidAttribute_maxTurnrate
    _boidAttribute_maxTurnrate = value

def maxTurnrate():
    """Gets max amount will change direction, per frame, to match herd (in degrees)"""
    return _boidAttribute_maxTurnrate

##################################
def setAvDirectionThreshold(value):
    """Sets max deviation from herd avVelocity without changing direction (in degrees)"""
    global _boidAttribute_herdAvDirectionThreshold
    _boidAttribute_herdAvDirectionThreshold = value

def avDirectionThreshold():
    """Gets max deviation from herd avVelocity without changing direction(in degrees)"""
    return _boidAttribute_herdAvDirectionThreshold

##################################
def setAvPositionTreshold(value):
    """Sets max distance from avPosition without attempting to shuffle inwards"""
    global _boidAttribute_herdAvPositionThreshold
    _boidAttribute_herdAvPositionThreshold = value
    
def avPositionThreshold():
    """Gets max distance from avPosition without attempting to shuffle inwards"""
    return _boidAttribute_herdAvPositionThreshold

##################################
def setBlindRegionAngle(value):
    """Sets angle (in degrees, negative is anti-clockwise) of area 'behind' each boid considered a blind spot"""
    global _boidAttribute_blindRegionAngle
    _boidAttribute_blindRegionAngle = value

def blindRegionAngle():
    """Gets angle (in degrees, negative is anti-clockwise) of area 'behind' each boid considered a blind spot"""
    return _boidAttribute_blindRegionAngle

##################################
def setSearchModeMaxTurnrate(value):
    """Sets max amount will change direction, per frame, when searching for herd (in degrees)"""
    global _boidAttribute_searchModeMaxTurnrate
    _boidAttribute_searchModeMaxTurnrate = value

def searchModeMaxTurnrate():
    """Gets max amount will change direction, per frame, when searching for herd (in degrees)"""
    return _boidAttribute_searchModeMaxTurnrate

##################################
def setLeaderWaypointThreshold(value):
    """Sets min distance from waypoint at which it is considered as 'reached'"""
    global _boidAttribute_leaderModeWaypointThreshold
    _boidAttribute_leaderModeWaypointThreshold = value
    
def leaderWaypointThreshold():
    """Gets min distance from waypoint at which it is considered as 'reached'"""
    return _boidAttribute_leaderModeWaypointThreshold

##################################
def setPriorityGoalThreshold(value):
    """Sets min distance from priority goal at which it's considered as 'reached'"""
    global _boidAttribute_priorityGoalThreshold
    _boidAttribute_priorityGoalThreshold = value
    
def priorityGoalThreshold():
    """Gets min distance from priority goal at which it's considered as 'reached'"""
    return _boidAttribute_priorityGoalThreshold

##################################
def setJumpAcceleration(value):
    """Acceleration applied to execute a 'jump' event."""
    global _boidAttribute_jumpAcceleration
    _boidAttribute_jumpAcceleration = value

def jumpAcceleration():
    """Acceleration applied to execute a 'jump' event."""
    return _boidAttribute_jumpAcceleration

##################################
def setJumpOnPileUpProbability(value):
    """Probability that, upon joining a basePyramid, boid will 'jump' instead of just joining at the bottom."""
    global _boidAttribute_jumpOnPileUpProbability
    _boidAttribute_jumpOnPileUpProbability = value
    
def jumpOnPileUpProbability():
    """Probability that, upon joining a basePyramid, boid will 'jump' instead of just joining at the bottom."""
    return _boidAttribute_jumpOnPileUpProbability

def setJumpOnPileUpRegionSize(value):
    """Distance from basePyramid at which boids will 'jump' (if they are to do so)."""
    global _boidAttribute_jumpOnPileUpRegionSize
    _boidAttribute_jumpOnPileUpRegionSize = value
    
def jumpOnPileUpRegionSize():
    """Distance from basePyramid at which boids will 'jump' (if they are to do so)."""
    return _boidAttribute_jumpOnPileUpRegionSize

##################################
def setPushUpwardsAcclerationHorizontal(value):
    """Acceleration applied by each boid in the horizontal direction (directed towards
    the baseLocator of the priority goal) after having joined the basePyramid."""
    global _boidAttribute_pushUpwardsAccelerationHorizontal
    _boidAttribute_pushUpwardsAccelerationHorizontal = value
    
def pushUpwardsAccelerationHorizontal():
    """Acceleration applied by each boid in the horizontal direction (directed towards
    the baseLocator of the priority goal) after having joined the basePyramid."""
    return _boidAttribute_pushUpwardsAccelerationHorizontal

def setPushUpwardsAccelerationVertical(value):
    """Acceleration applied by each boid in the vertical direction after having joined the basePyramid."""
    global _boidAttribute_pushUpwardsAccelerationVertical
    _boidAttribute_pushUpwardsAccelerationVertical = value    
        
def pushUpwardsAccelerationVertical():
    """Acceleration applied by each boid in the vertical direction after having joined the basePyramid."""
    return _boidAttribute_pushUpwardsAccelerationVertical

##################################
def setGoalChaseSpeed(value):
    """Speed at which agents will travel towards the basePyramid (circumstances allowing) when following goal-driven behaviour."""
    global _boidAttribute_goalChaseSpeed
    _boidAttribute_goalChaseSpeed = value
    
def goalChaseSpeed():
    """Speed at which agents will travel towards the basePyramid (circumstances allowing) when following goal-driven behaviour."""
    return _boidAttribute_goalChaseSpeed

##################################
def setGoalIncubationPeriod(value):
    """'Goal-infected' agents will wait this many frames before actively following goal-driven behaviour."""
    global _boidAttribute_goalIncubationPeriod
    _boidAttribute_goalIncubationPeriod = value
    
def goalIncubationPeriod():
    """'Goal-infected' agents will wait this many frames before actively following goal-driven behaviour."""
    return _boidAttribute_goalIncubationPeriod

##################################
def setCurveDevianceThreshold(value):
    """Sets distance from nearest point on curve beyond which boid will be pulled back towards the curve"""
    global _boidAttribute_curveDevianceThreshold
    _boidAttribute_curveDevianceThreshold = value

def curveDevianceThreshold():
    """Gets distance from nearest point on curve beyond which boid will be pulled back towards the curve"""
    return _boidAttribute_curveDevianceThreshold

def setCurveEndReachedThreshold(value):
    """Sets proximity to end point - MEASURED FROM THE NEAREST CURVE POINT, NOT THE BOID'S ACTUAL POSITION - at which destination is considered reached"""
    global _boidAttribute_curveEndReachedThreshold
    _boidAttribute_curveEndReachedThreshold = value
    
def curveEndReachedThreshold():
    """Gets proximity to end point - MEASURED FROM THE NEAREST CURVE POINT, NOT THE BOID'S ACTUAL POSITION - at which destination is considered reached"""
    return _boidAttribute_curveEndReachedThreshold

def setCurveGroupVectorMagnitude(value):
    """Scalar magnitude of motion vector that will be applied to agent's overall velocity when following a curve."""
    global _boidAttribute_curveGroupVectorMagnitude
    _boidAttribute_curveGroupVectorMagnitude = value
    
def curveGroupVectorMagnitude():
    """Scalar magnitude of motion vector that will be applied to agent's overall velocity when following a curve."""
    return _boidAttribute_curveGroupVectorMagnitude

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

