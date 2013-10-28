import boidConstants
import boidVector3 as bv3


class BoidState(object):
    
    def __init__(self, particleId):
        self._particleId = particleId
        self._position = bv3.BoidVector3()
        self._velocity = bv3.BoidVector3()
        self._acceleration = bv3.BoidVector3()
        
        self._isTouchingGround = False
        self.isInBasePyramid = False
        self.hasReachedGoal = False
        
        self.nearbyList = []
        self.crowdedList = []
        self.collisionList = []
        self._avPosition = bv3.BoidVector3()
        self._avVelocity = bv3.BoidVector3()
        self._avCrowdedPos = bv3.BoidVector3()
        self._avCollisionDirection = bv3.BoidVector3()        
        
###################        
    def __str__(self):
        return ("id=%d, pos=%s, vel=%s, acln=%s, TG=%s" % 
                (self._particleId, self._position, self._velocity, self._acceleration, "Y" if(self._isTouchingGround) else "N"))
    
################### 
    def metaStr(self):
        nearList = ""
        for nearbyBoid in self.nearbyList:
            nearList += ("%d," % nearbyBoid.particleId)
        crowdList = ""
        for crowdingBoid in self.crowdedList:
            crowdList += ("%d," % crowdingBoid.particleId)
        collisionList = ""
        for collidedBoid in self.collisionList:
            collisionList += ("%d," % collidedBoid.particleId)
        
        return ("id=%d, avP=%s, avV=%s, avCP=%s, nr=%s, cr=%s, col=%s" % 
                (self._particleId, self._avPosition, self._avVelocity, self._avCrowdedPos, nearList, crowdList, collisionList))       
    
#####################
    def getParticleId(self):
        return self._particleId
    particleId = property(getParticleId)

    def _getPosition(self):
        return self._position
    position = property(_getPosition)

    def _getVelocity(self):
        return self._velocity
    velocity = property(_getVelocity)

    def _getAcceleration(self):
        return self._acceleration
    acceleration = property(_getAcceleration)
    
    def _getIsTouchingGround(self):
        return self._isTouchingGround
    isTouchingGround = property(_getIsTouchingGround)   
    
    def _getAvPosition(self):
        return self._avPosition
    avPosition = property(_getAvPosition)
    
    def _getAvVelocity(self):
        return self._avVelocity
    avVelocity = property(_getAvVelocity)
    
    def _getAvCrowdedPosition(self):
        return self._avCrowdedPos
    avCrowdedPosition = property(_getAvCrowdedPosition)
    
    def _getHasNeighbours(self):
        return (len(self.nearbyList) > 0)
    hasNeighbours = property(_getHasNeighbours)
    
    def _getIsCrowded(self):
        return (len(self.crowdedList) > 0)
    isCrowded = property(_getIsCrowded)        
    
    def _getIsCollided(self):
        return (len(self.collisionList) > 0)
    isCollided = property(_getIsCollided)
    
    def _getAvCollisionDirection(self):
        return self._avCollisionDirection
    avCollisionDirection = property(_getAvCollisionDirection)    
    
#####################           
    def updateCurrentVectors(self, position, velocity):
        self._position.resetVec(position)
        self._acceleration = velocity - self._velocity
        self._velocity.resetVec(velocity)
        
        if(self._acceleration.y < boidConstants.accelerationPerFrameDueToGravity()):
            self._isTouchingGround = False
        else:
            self._isTouchingGround = True

#################################       
    def withinRadiusOfPoint(self, otherPosition, radius):
        if(self._position.distanceFrom(otherPosition) < radius):
            return True
        else:
            return False
        
################################# 
    def angleToLocation(self, location):
        directionVec = location - self._position
        return self._velocity.angleFrom(directionVec)
       
##############################
    def notifyJump(self):
        self._isTouchingGround = False

##############################        
    def resetLists(self):
        del self.nearbyList[:]
        self._avVelocity.reset()
        self._avPosition.reset()
        del self.crowdedList[:]
        self._avCrowdedPos.reset()
        del self.collisionList[:]
        self._avCollisionDirection.reset()    
                
##############################
    def buildNearbyList(self, otherBoids, neighbourhoodSize, crowdedRegionSize, collisionRegionSize):
        self.resetLists()
        visibleAreaAngle = 180 - (boidConstants.blindRegionAngle() / 2)
            
        
        for otherBoid in otherBoids:
            otherBoidState = otherBoid.boidState
            
            if(otherBoidState.particleId != self._particleId and
               otherBoidState.isTouchingGround and
               self.withinRadiusOfPoint(otherBoidState.position, neighbourhoodSize) and
               abs(self.angleToLocation(otherBoidState.position)) < visibleAreaAngle):
                
                self.nearbyList.append(otherBoid)
                self._avVelocity.add(otherBoidState.velocity)
                self._avPosition.add(otherBoidState.position)

                if(self.withinRadiusOfPoint(otherBoidState.position, crowdedRegionSize)):
                    self.crowdedList.append(otherBoid)
                    self._avCrowdedPos.add(otherBoidState.position)
                    
                    if(self.withinRadiusOfPoint(otherBoidState.position, collisionRegionSize)):
                        directionOfCollisionVec = otherBoidState.position - self._position
                        if(abs(self._velocity.angleFrom(directionOfCollisionVec)) < 90):
                            self._isCollided = True
                            self.collisionList.append(otherBoid)
                            self._avCollisionDirection.add(otherBoidState.position)
        
        numNeighbours = len(self.nearbyList)
        if(numNeighbours > 0):
            self._avVelocity.add(self._velocity)
            self._avVelocity.divide(numNeighbours + 1)
            self._avPosition.add(self._position)
            self._avPosition.divide(numNeighbours + 1)
        else:
            self._avVelocity.resetVec(self._velocity)
            self._avPosition.resetVec(self._position)

        crowdedSize = len(self.crowdedList)
        if(crowdedSize > 0):
            self._avCrowdedPos.divide(crowdedSize)
        else:
            self._avCrowdedPos.resetVec(self._position)
            
        if(len(self.collisionList) > 0):
            self._avCollisionDirection.divide(len(self.collisionList))
