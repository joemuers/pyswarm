from boidObject import BoidObject
import random

import boidConstants
import boidUtil
import boidVector3 as bv3
import boidState as bs


class BoidAgent(BoidObject):
    """Represents single boid instance.   
    Logic concerning boid's behaviour is contained within this class. (Internally,
    data concerning position, heading, neighbourhood & so on is in the boidState 
    container).
    
    Behaviour: Dependent on situation, in normal circumstances, behaviour governed by relatively
    straightforward implementation of Reynold's boids rules.  If currently goal-driven, behaviour
    is determined mainly by the corresponding BoidGroupTarget instance.
    Behaviour will also be affected if currently following a curve path, or at the scene's mapEdge border.
    
    Operation: Agent keeps an internal representation of the corresponding Maya nParticle's position, velocity etc, which
    must be updated on every frame (with updateCurrentVectors), desired behaviour is then calculated (updateBehaviour)
    which is output in the form of the 'desiredAcceleration' member variable.
    When the final value of the desiredAcceleration has been calculated, it can be applied to the corresponding
    Maya nParticle (commitNewBehaviour).
    
    
    Potentially confusing member variables:
        - positive/negativeGridBounds - opposing corners of the bounding grid plane over which the
                                        boid object can move.
        - desiredAcceleration - as determined by the Reynolds boid rules + some other factors...
        - needsBehaviourCalculation - True if postion/heading/circumstance has changed since last calculation, False otherwise.
        - doNotClampAcceleration - the min/max values for speed/acceleration as determined in boidConstants will *NOT*
        be applied if this flag is set.  Must be re-set on every frame update if needed.
        
        
        - sticknessScale - directly related to Maya's 'stickiness' nParticle attribute,
                           used when boid is in basePyramid pile-up to aid pyramid's
                           overall cohesion.

        - priorityGoal - (if not nil) a boidGroupTarget instance that's actively driving the agent's behaviour.
        - 'goalInfected' - agent has been given a priorityGoal, which will become active when
                            the goalInfectionCountdown hits zero.
        - inBasePyramid - agent following priorityGoal has reached base of target wall and is attempting to
                          climb up the boid-pyramid at the wall.  Note 'hasArrivedAtGoalBase' is set at this point too,
                          the distinction being that once the boid clears the wall, 'inBasePyramid' will be cleared but
                          hasArrived will still be set.
        - curvePath - agent roughly follows this path, if set.
        
        
    TODO, leave in or take out?
        - 'leader' stuff
        - jump/jostle/clamber
        
    """

    def __init__(self, particleId, negativeGridBounds = None, positiveGridBounds = None):
        self.boidState = bs.BoidState(int(particleId))
        self._negativeGridBounds = negativeGridBounds
        self._positiveGridBounds = positiveGridBounds
        
        self._desiredAcceleration = bv3.BoidVector3()
        self._needsBehaviourCalculation = True # True if postion/heading/circumstance has 
        #                                      # changed since last calculation, False otherwise.
        self._doNotClampAcceleration = False # the min/max values for speed/acceleration as determined in boidConstants will *NOT*
        #                                    # be applied if this flag is set.  Must be re-set on every frame update if needed.
        self._stickinessScale = 0.0
        self._stickinessChanged = False
        
        self._leaderGoals = None # list of boidVector3's, TODO - not currently in use...
        
        self._priorityGoal = None
        self._isAtPriorityGoal = False
        self._goalInfectionCountdown = -1 
        self.isInBasePyramid = False
        self._hasArrivedAtGoalBase = False
        self._collapsingGoal = False
        
        self._curvePath = None  # boidGroupPath instance
        self._reachedEndOfCurvePath = False
        
##################### 
    def __str__(self):
        return "<%s, stck=%.2f>" % (self.boidState, self.stickinessScale)
    
    def __eq__(self, other):
        return (self.particleId == other.particleId) if(other != None) else False
    
    def __ne__(self, other):
        return (self.particleId != other.particleId) if(other != None) else True
    
    def __lt__(self, other):
        return self.particleId < other.particleId
    
    def __gt__(self, other):
        return self.particleId > other.particleId
    
    def __hash__(self):
        return hash(self.particleId)

#####################
    def metaStr(self):      
        waypointList = ""
        if(self.isLeader):
            for waypoint in self._leaderGoals:
                waypointList += ("%s," % waypoint)
        else:
            waypointList += "n/a"        
        return ("<%s, wp=%s, PG=%s, rch'd=%s, atBase=%s, crvPath=%s>" % 
                (self.boidState.metaStr(), 
                 waypointList, 
                 self._priorityGoal.attractorPositionForBoid(self) if (self._priorityGoal != None) else "n/a", 
                 "Y" if(self.isAtPriorityGoal) else "N", 
                 "Y" if(self.isInBasePyramid) else "N", 
                self._curvePath))

#####################
    def _getParticleId(self):
        return self.boidState.particleId
    particleId = property(_getParticleId)

    def _getCurrentPosition(self):
        return self.boidState.position
    currentPosition = property(_getCurrentPosition)
    
    def _getCurrentVelocity(self):
        return self.boidState.velocity
    currentVelocity = property(_getCurrentVelocity)
    
    def _getCurrentAcceleration(self):
        return self.boidState.acceleration
    currentAcceleration = property(_getCurrentAcceleration)
    
    def _getStickinessScale(self):
        return self._stickinessScale
    def _setStickinessScale(self, value):
        if(value != self._stickinessScale):
            self._stickinessScale= value
            self._stickinessChanged = True
    stickinessScale = property(_getStickinessScale, _setStickinessScale) 
    
    def _getHasNeighbours(self):
        return self.boidState.hasNeighbours
    hasNeighbours = property(_getHasNeighbours)
    
    def _getIsCrowded(self):
        return self.boidState.isCrowded
    isCrowded = property(_getIsCrowded)
    
    def _getIsCollided(self):
        return self.boidState.isCollided
    isCollided = property(_getIsCollided)
    
    def _getIsTouchingGround(self):
        return self.boidState.isTouchingGround
    isTouchingGround = property(_getIsTouchingGround)

    def _getIsLeader(self):
        return self._leaderGoals != None and len(self._leaderGoals) > 0
    isLeader = property(_getIsLeader)
    
    def _getIsGoalInfected(self):
        return self._goalInfectionCountdown >= 0
    isGoalInfected = property(_getIsGoalInfected)
    
    def _getIsFollowingPriorityGoal(self):
        return self._goalInfectionCountdown == 0 and self._priorityGoal != None
    isFollowingPriorityGoal = property(_getIsFollowingPriorityGoal)
    
    def _getIsInBasePyramid(self):
        """True if agent has reached the base of a priority goal and is now attempting to 'pile-up'."""
        return self.boidState.isInBasePyramid and self.isFollowingPriorityGoal
    def _setIsInBasePyramid(self, value):
        self.boidState.isInBasePyramid = value
        if(value):
            self._hasArrivedAtGoalBase = True
    isInBasePyramid = property(_getIsInBasePyramid, _setIsInBasePyramid)

    def _getIsAtPriorityGoal(self):
        return self.isFollowingPriorityGoal and self._isAtPriorityGoal
    def _setIsAtPriorityGoal(self, value):
        self._isAtPriorityGoal = value
    isAtPriorityGoal = property(_getIsAtPriorityGoal, _setIsAtPriorityGoal)
    
    def _getIsFollowingCurve(self):
        return self._curvePath != None and not self.reachedEndOfCurvePath
    isFollowingCurve = property(_getIsFollowingCurve)
    
    def _getReachedEndOfCurvePath(self):
        return self._reachedEndOfCurvePath
    def _setReachedEndOfCurvePath(self, value):
        if(not value and self._curvePath == None):
            print("XXX WARNING XXX - ATTEMPT TO SET NON-EXISTENT CURVE PATH")
        else:
            self._reachedEndOfCurvePath = value
            if(value and self._curvePath != None):
                self._curvePath.notifyNoLongerFollowing(self)
                self._curvePath = None
    reachedEndOfCurvePath = property(_getReachedEndOfCurvePath, _setReachedEndOfCurvePath)
    
#####################        
    def makeLeader(self, goalsList):
        # should throw exception if already priorityGoalDriven????
        if(goalsList != None and len(goalsList) == 0):
            self._leaderGoals = None
        else:
            self._leaderGoals = goalsList

##################### 
    def makeGoalInfected(self, priorityGoal):
        """Will cause agent's behaviour to be determined by the BoidGroupTarget instance passed in here."""
        
        self.makeLeader(None)
        if(self._priorityGoal != priorityGoal):
            self._priorityGoal = priorityGoal   
            self._goalInfectionCountdown = 0 if(priorityGoal != None) else -1    
            self._isAtPriorityGoal = False
            self._hasArrivedAtGoalBase = False
            self._collapsingGoal = False
    
    def _makeGoalInfectedWithIncubationPeriod(self, infectedBoid):
        self.makeGoalInfected(infectedBoid._priorityGoal)
        self._collapsingGoal = False
        if(self._priorityGoal != None):
            self._goalInfectionCountdown = boidConstants.goalIncubationPeriod()
            
    def _decrementInfectionCountdown(self):
        if(self._goalInfectionCountdown > 0):
            self._goalInfectionCountdown -= 1
        return self._goalInfectionCountdown == 0

##################### 
    def makeFollowCurvePath(self, curvePath):
        """Will make the agents behaviour influenced the the BoidGroupPath instance passed in here."""
        
        self._curvePath = curvePath
        self._reachedEndOfCurvePath = False
        
##################### 
    def updateCurrentVectors(self, position, velocity, decrementInfectionCount = True):
        """Updates internal state from corresponding vectors."""
        
        self.boidState.updateCurrentVectors(position, velocity)
        self._needsBehaviourCalculation = True
        self._isAtPriorityGoal = False
        self.isInBasePyramid = False           
        if(decrementInfectionCount):
            self._decrementInfectionCountdown()
            
        if(self.isFollowingPriorityGoal and self._priorityGoal.checkBoidLocation(self)):
            self.isInBasePyramid = True
            self.boidState.resetLists()     

###########################
    def updateBehaviour(self, boidsList, forceUpdate = False):
        """Calculates desired behaviour and updates desiredAccleration accordingly."""
        
        if(self._needsBehaviourCalculation or forceUpdate):            
            if(self.isInBasePyramid):
                self._followPriorityGoal()
            else:            
                self.boidState.buildNearbyList(boidsList,
                                               boidConstants.mainRegionSize(),
                                               boidConstants.nearRegionSize(),
                                               boidConstants.collisionRegionSize())
                
                self._desiredAcceleration.reset()
                self._doNotClampAcceleration = False
                
                if(self.isTouchingGround):
                    if(self._followPriorityGoal()):
                    #     print("AAA")
                        return
                    elif(self._avoidMapEdge()):
                    #     print("bbb")
                        return
                    elif(self._moveAsLeader()):
                    #     print("ccc")
                        return
                    elif(self._avoidNearbyBoids()):
                    #     print("ddd")
                        return
                    elif(self._matchSwarmHeading()):
                        self._matchSwarmPosition()  # - TODO check if we want this or not???
                    elif(not self._matchSwarmPosition()):
                        self._searchForSwarm()
        
                    self._followCurvePath()
                    self._matchPreferredVelocity()
                    
                elif(self.isInBasePyramid):
                    self._followPriorityGoal()
                
            self._needsBehaviourCalculation = False
        
        #boidBenchmarker.bmStop("update-setBehaviour")



######################
    def _pushAwayFromWallIfNeeded(self, directionToGoal):
        """Agents in a basePyramid sometimes get pushed to the corners and get
        stuck there, which is not desirable.  This method corrects that behaviour."""
        
        if(self._hasArrivedAtGoalBase and not self.isInBasePyramid):
            angle = abs(directionToGoal.angleFrom(self._priorityGoal._baseToFinalDirection))
            if(angle > 82):
                #         print("STUCK #%d" % self.particleId)
                self._desiredAcceleration.subtract(self._priorityGoal._baseToFinalDirection, True)
                return True

        return False

######################
    def _followPriorityGoal(self):
        """Determines desiredAcceleration if agent is currently following a BoidGroupTarget."""
        
        if(self.isFollowingPriorityGoal):
            if(self.isInBasePyramid or self.isAtPriorityGoal):
                self._desiredAcceleration.resetVec(self._priorityGoal.getDesiredAcceleration(self))
                self._doNotClampAcceleration = True
            else:
                #if(self.isCollided):
                    #for nearbyBoid in self.boidState.collidedList:
                if(self.isCrowded):
                    for nearbyBoid in self.boidState.crowdedList:
                        # as the basePyramid grows in size, it's perceived 'boundary' (i.e. the position at which agents are said 
                        # to have joined the pyramid and can start their 'climbing' behaviour) is not fixed. So to determine it, we
                        # look at other agents in the immediate vicinity and see if they themselves are in the pyramid.
                        if(nearbyBoid.isInBasePyramid and 
                           (nearbyBoid.currentPosition.distanceFrom(self.currentPosition) < boidConstants.priorityGoalThreshold()) and
                           (nearbyBoid.currentVelocity.magnitude(True) < boidConstants.goalChaseSpeed() or 
                            self.currentVelocity.magnitude(True) < boidConstants.goalChaseSpeed() or ## new line here - might break things...?
                            abs(nearbyBoid.currentVelocity.angleFrom(self.currentVelocity)) > 90)):
                           
                            self._priorityGoal.registerBoidAsArrived(self)
                            self.isInBasePyramid = True
                            self._desiredAcceleration.resetVec(self._priorityGoal.getDesiredAcceleration(self))
                            self._doNotClampAcceleration = True
                            break
                
                if(not self.isInBasePyramid):
                    self._priorityGoal.deRegisterBoidAsArrived(self)
                
                    directionVec = self._priorityGoal.attractorPositionForBoid(self) - self.currentPosition
                    directionVec.normalise(boidConstants.maxAccel())
                    self._desiredAcceleration.resetVec(directionVec)       
                    
                    # push away from nearby boids??
                    if(not self._hasArrivedAtGoalBase and self.isCrowded):   # note that we move AWAY from the avPos here
                        differenceVector = self.currentPosition - self.boidState.avCrowdedPosition
                        differenceVector.normalise(boidConstants.maxAccel())
                        self._desiredAcceleration.add(differenceVector)    
                    else:
                        self._pushAwayFromWallIfNeeded(directionVec)
                    
                    if(self.isTouchingGround and self.currentVelocity.magnitude() >= boidConstants.maxVel()):
                        if(self._priorityGoal.getShouldJump(self)):
                            self._jump()
                    
            return True
            
        else:
            if(not self.isGoalInfected):
                nearestNeighbour = None
                nearestNeighbourDistance = float('inf')                    
                for nearbyBoid in self.boidState.nearbyList:
                    if(nearbyBoid.isFollowingPriorityGoal):
                        distance = self.currentPosition - nearbyBoid.currentPosition
                        if(distance.magnitude() < nearestNeighbourDistance):
                            nearestNeighbour = nearbyBoid
                            nearestNeighbourDistance = distance.magnitude()
                            
                if(nearestNeighbour != None):
                    self._makeGoalInfectedWithIncubationPeriod(nearestNeighbour)  
                    
            return False
##############################
    def _jump(self):
        if(self.isTouchingGround):
            self._desiredAcceleration.y += boidConstants.jumpAcceleration()
            self._doNotClampAcceleration = True
            self.boidState.notifyJump()
            return True
        else:
            return False

######################            
    def _pushUpwards(self, desiredHeight, desiredDirection):
        if(self.currentPosition.y < desiredHeight or self.currentVelocity.y < -1):
                  
            if(abs(desiredDirection.angleFrom(self.currentVelocity)) > 90):
                self._desiredAcceleration.resetVec(desiredDirection)
                self._desiredAcceleration.normalise(boidConstants.maxAccel())
            self._desiredAcceleration.y += boidConstants.pushUpwardsAccelerationVertical()
            
            self._doNotClampAcceleration = True
            return True
        else:
            return False

######################
    def _jostleIfNecessary(self):
        return
        #not used at present... nParticles seems to do a good job?
        #if(self.isCrowded and not self.isAtObstacle):
            #for nearbyBoid in self.boidState.crowdedList:
                ### CHECK THIS LOGIC....
                #if(nearbyBoid.isTouchingGround):
                    #directionVec = nearbyBoid.currentPosition - self.currentPosition
                    #if(abs(self._desiredAcceleration.angleFrom(directionVec)) < 90):
                        #self._jump()
                        #break

######################  
    def _clamberIfNecessary(self):
        if(self.isInBasePyramid):#self.isCollided):
            shouldJump = True
            for nearbyBoid in self.boidState.collisionList:
                if(nearbyBoid.isInBasePyramid):
                    self.isInBasePyramid = True
                if(nearbyBoid.currentPosition.isAbove(self.currentPosition)):
                    shouldJump = False
                    #break
            
            #if(self.isInBasePyramid):
                #if(self.particleId < 10):
                    #if(shouldJump):
                        #self._jump()
                #elif(self.particleId < 15):
                    #self._pushUpwards(1.0)
                #elif(self.particleId < 30):
                    #self._pushUpwards(1.5)
                #elif(self.particleId < 45):
                    #self._pushUpwards(2.0)
                #else:
                    #self._pushUpwards(2.5)
            #if(self.isInBasePyramid and shouldJump):
                #self._jump()
            #else:
                #self._stop()

###################### 
    def _followCurvePath(self):
        if(self._curvePath != None and not self._reachedEndOfCurvePath):
            self._desiredAcceleration += self._curvePath.getDesiredAcceleration(self)
                
            return True
        else:
            return False        


###################### 
    def _avoidMapEdge(self):
        madeChange = False
        if(self._negativeGridBounds != None and self._positiveGridBounds != None):
            if(self.currentPosition.x < self._negativeGridBounds.u and self.currentVelocity.x < boidConstants.maxVel()):
                self._desiredAcceleration.x = boidConstants.maxAccel() 
                madeChange = True
            elif(self._positiveGridBounds.u < self.currentPosition.x and -(boidConstants.maxVel() ) < self.currentVelocity.x):
                self._desiredAcceleration.x = -(boidConstants.maxAccel() )
                madeChange = True
            
            if(self.currentPosition.z < self._negativeGridBounds.v and self.currentVelocity.z < boidConstants.maxVel()):
                self._desiredAcceleration.z = boidConstants.maxAccel() 
                madeChange = True
            elif(self._positiveGridBounds.v < self.currentPosition.z and -(boidConstants.maxVel() ) < self.currentVelocity.z):
                self._desiredAcceleration.z = -(boidConstants.maxAccel() )
                madeChange = True
        
        return madeChange

######################  
    def _moveAsLeader(self):
        if(self.isLeader):
            currentWaypoint = self._leaderGoals[0]
            if(self.boidState.withinRadiusOfPoint(currentWaypoint, boidConstants.leaderWaypointThreshold())):
                if(len(self._leaderGoals) > 1):
                    self._leaderGoals.pop(0)
                    
                    return self._moveAsLeader()
                else:
                    self._stop()
                    
                    return True
            else:
                directionVec = currentWaypoint - self.currentPosition
                directionVec.normalise()
                directionVec *= boidConstants.maxAccel()
                self._desiredAcceleration.resetVec(directionVec)
                
                return True
        else:
            return False
        
######################                  
    def _avoidNearbyBoids(self):
        if(self.isCollided):  # Problem here - we're driving the velocity directly... should be done by Maya really
            ######### might not really need this if particle self-collisions are working properly... ??
            self._stop()
            self._desiredAcceleration.resetVec(self.boidState.avCollisionDirection)
            self._desiredAcceleration.invert()
            self._desiredAcceleration.normalise(boidConstants.maxAccel())
            #  self._desiredAcceleration.y = 0
            
            return True
        
        elif(self.isCrowded):   # note that we move AWAY from the avPos here
            differenceVector = self.currentPosition - self.boidState.avCrowdedPosition
            self._desiredAcceleration.resetVec(differenceVector)

            return True

        return False
            
####################### 
    def _matchSwarmHeading(self):
        # just change the heading here, *not* the speed...
        if(self.hasNeighbours):
            desiredRotationAngle = self.currentVelocity.angleFrom(self.boidState.avVelocity)
            angleMag = abs(desiredRotationAngle)
            
            if(angleMag > boidConstants.avDirectionThreshold()):
                if(angleMag > boidConstants.maxTurnrate()):
                    desiredRotationAngle = boidConstants.maxTurnrate() if(desiredRotationAngle > 0) else -(boidConstants.maxTurnrate())
                
                desiredDirection = bv3.BoidVector3(self.currentVelocity)
                desiredDirection.rotateInHorizontal(desiredRotationAngle)
                self._desiredAcceleration = desiredDirection - self.currentVelocity
                    
                return True

        return False

#############################
    def _matchSwarmPosition(self):
        if(self.hasNeighbours):
            distanceFromSwarmAvrg = self.currentPosition.distanceFrom(self.boidState.avPosition)
            
            if(boidConstants.avPositionThreshold() < distanceFromSwarmAvrg):
                differenceVector = self.boidState.avPosition - self.currentPosition
                self._desiredAcceleration.resetVec(differenceVector)
                
                return True

        return False

###################### 
    def _searchForSwarm(self):
        ## TODO - change this algorithm
        if(not self.hasNeighbours):
            if(self.currentVelocity.isNull()):
                self._desiredAcceleration.reset(boidConstants.maxAccel(), 0, 0)
                rotation = random.uniform(-179, 179)
                self._desiredAcceleration.rotateInHorizontal(rotation)
            else:
                desiredRotationAngle = random.uniform(-boidConstants.searchModeMaxTurnrate(), boidConstants.searchModeMaxTurnrate())
                desiredDirection = bv3.BoidVector3(self.currentVelocity)
                desiredDirection.rotateInHorizontal(desiredRotationAngle)
                self._desiredAcceleration = self.currentVelocity - desiredDirection         
            
            return True

        return False            

######################             
    def _matchPreferredVelocity(self):
        if(self.currentVelocity.magnitude() < boidConstants.preferredVel() and 
           self._desiredAcceleration.magnitude() < boidConstants.maxAccel()):
            if(self._desiredAcceleration.isNull()):
                self._desiredAcceleration.resetVec(self.currentVelocity)
                self._desiredAcceleration.normalise(boidConstants.maxAccel())
            else:
                magAccel = self._desiredAcceleration.magnitude()
                if(magAccel < boidConstants.maxAccel()):
                    self._desiredAcceleration *= (boidConstants.maxAccel() / magAccel)

##############################
    def _stop(self):
        self._desiredAcceleration.resetVec(self.currentVelocity, False)
        self._desiredAcceleration.invert()


######################  
    def commitNewBehaviour(self, particleShapeName):      
        
        if(self._doNotClampAcceleration):
            desiredVelocity = bv3.BoidVector3(self.currentVelocity)
            desiredVelocity.add(self._desiredAcceleration)         
                
            boidUtil.setParticleVelocity(particleShapeName, self.particleId, desiredVelocity)
            self._doNotClampAcceleration = False       
                      
        elif(self.isTouchingGround):
            magAccel = self._desiredAcceleration.magnitude()
                    
            if(boidConstants.maxAccel() < magAccel): # restrict acceleration to <= max value
                self._desiredAcceleration *= (boidConstants.maxAccel() / magAccel)
            elif(not self.isGoalInfected and 
                 magAccel < boidConstants.minVel() and self.currentVelocity.magnitude() < boidConstants.minVel() and  #  stop from getting stuck & freezing
                 self.hasNeighbours and not self.isCollided and not self.isCrowded):
                self._desiredAcceleration.reset(boidConstants.maxAccel(), 0, 0)
                rotation = random.uniform(-179, 179)
                self._desiredAcceleration.rotateInHorizontal(rotation)  
                    
            
            desiredVelocity = bv3.BoidVector3(self.currentVelocity)
            desiredVelocity.add(self._desiredAcceleration)

            magVel = desiredVelocity.magnitude()
            maxVelocity = boidConstants.maxVel() if(not self.isFollowingPriorityGoal) else boidConstants.goalChaseSpeed()
            if(maxVelocity < magVel): # restrict velocity to <= max value
                desiredVelocity *= (maxVelocity / magVel)              
    
            if(False) : #####self.isFollowingPriorityGoal and self.isCrowded and not self.isInBasePyramid):  #NEW BIT = check this works?? (Tues eve)
                shouldPushUp = True
                for otherBoid in self.boidState.crowdedList:
                    if(otherBoid.currentPosition.y > self.currentPosition.y or 
                       otherBoid._desiredAcceleration.y >= boidConstants.pushUpwardsAccelerationVertical() or 
                       otherBoid.currentVelocity.y >= boidConstants.pushUpwardsAccelerationVertical()):
                        shouldPushUp = False
                        break
                
                if(shouldPushUp):
                    self._desiredAcceleration.y = 0
                    self._desiredAcceleration.normalise(boidConstants.pushUpwardsAccelerationHorizontal())
                    self._desiredAcceleration.y = boidConstants.pushUpwardsAccelerationVertical()  # (for reference by other boids)
                    desiredVelocity = self.currentVelocity + self._desiredAcceleration
                
            boidUtil.setParticleVelocity(particleShapeName, self.particleId, desiredVelocity) 
                        
        
        if(self._stickinessChanged):
            boidUtil.setStickinessScale(particleShapeName, self.particleId, self.stickinessScale)
            self._stickinessChanged = False
     
        #pm.particle(particleShapeName, e=True, at="velocityU", id=self._particleId, fv=self._velocity.u)
        #pm.particle(particleShapeName, e=True, at="velocityV", id=self._particleId, fv=self._velocity.v)


# end of class BoidAgent

################################################################################

