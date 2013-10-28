import boidConstants
import boidUtil
import boidVector2 as bv2
import boidVector3 as bv3


import random


class BoidGroupTarget(object):
    
    def __init__(self, basePos, lipPos, finalPos, bDelegate = None):
        self._delegate = bDelegate
                
        self._baseVector = boidUtil.boidVectorFromLocator(basePos)
        self._baseLocator = None
        if(not type(basePos) == bv3.BoidVector3):
            self._baseLocator = basePos
            
        self._lipVector = boidUtil.boidVectorFromLocator(lipPos)
        self._lipLocator = None
        if(not type(lipPos) == bv3.BoidVector3):
            self._lipLocator = lipPos
            
        self._finalVector = boidUtil.boidVectorFromLocator(finalPos)
        self._finalLocator = None
        if(not type(finalPos) == bv3.BoidVector3):
            self._finalLocator = finalPos
            
        self._baseToFinalDirection = bv3.BoidVector3()

        self._leaders = []
                    
        self._boidDistanceLookup = {}
        self._atTheLipLookup = set()
        self._overTheWallLookup = set()
        
        self._pushUpwardsVector = bv2.BoidVector2()
        
        self._boidDistanceRunningTotal = bv2.BoidVector2()
        self._boidDistanceAverage = bv2.BoidVector2()
        self._needsAverageDistanceCalc = False
        self._maxBoidDistance = bv2.BoidVector2()
        
        self._boidPositionRunningTotal = bv3.BoidVector3()
        self._boidPositionAverage = bv3.BoidVector3()
        self._needsAveragePositionCalc = False
        
        self.performCollapse = False
        
#######################        
    def __str__(self):
        leadersStr = ""
        for boid in self._leaders:
            leadersStr += ("%d," % boid.particleId)
        listStr = ""
        for boid, distance in sorted(self._boidDistanceLookup.iteritems()):
            listStr += ("\t%s - dist=%s (mag=%.4f)\n" % (boid, distance, distance.magnitude()))
        atLipStr = ""
        for boid in self._atTheLipLookup:
            atLipStr += ("\t%s\n" % boid)
        overStr = ""
        for boid in self._overTheWallLookup:
            overStr += ("\t%s\n" % boid)
            
        return ("<pos=%s, lip=%s, final=%s, ldrs=%s, climbVector=%s, avDist=%s, maxDist=%s, avPos=%s, atLoctn=\n%s\natLip=\n%s\nover=\n%s>" % 
                (self._baseVector, self._lipVector, self._finalVector, leadersStr,
                 self._pushUpwardsVector, self.distanceAverage, self._maxBoidDistance, self.positionAverage, 
                 listStr, atLipStr, overStr))

#######################
    def attractorPositionForBoid(self, boid):
        returnValue = None
        numLeaders = len(self._leaders)

        if(boid._hasArrivedAtGoalBase or numLeaders == 0 or boid in self._leaders):
            returnValue = self._baseVector
        elif(numLeaders == 1):
            returnValue = self._leaders[0].currentPosition
        else:
            candidateLeader = None
            minDist = boid.currentPosition.distanceFrom(self._baseVector)
            for leader in self._leaders:
                candidateDist = boid.currentPosition.distanceFrom(leader.currentPosition)
                if(candidateDist < minDist):
                    minDist = candidateDist
                    candidateLeader = leader
            
            if(candidateLeader != None):
                returnValue = candidateLeader.currentPosition
            else:
                returnValue = self._baseVector
                
        if(self.performCollapse):
            returnValue.invert()        
        
        return returnValue
            
        
#######################
    def _getDistanceAverage(self):
        if(self._needsAverageDistanceCalc and len(self._boidDistanceLookup) > 0):
            self._boidDistanceAverage.resetVec(self._boidDistanceRunningTotal)
            self._boidDistanceAverage.divide(len(self._boidDistanceLookup))
            self._needsAverageDistanceCalc = False
        return self._boidDistanceAverage
    distanceAverage = property(_getDistanceAverage)
    
    def _getPositionAverage(self):
        if(self._needsAveragePositionCalc and len(self._boidDistanceLookup) > 0):
            self._boidPositionAverage.resetVec(self._boidPositionRunningTotal)
            self._boidPositionAverage.divide(len(self._boidDistanceLookup))
            self._needsAveragePositionCalc = False
        return self._boidPositionAverage
    positionAverage = property(_getPositionAverage)

#######################    
    def _getMaxHorizontalDistance(self):
        return self._maxBoidDistance.u
    maxHorizontalDistance = property(_getMaxHorizontalDistance)
    
    def _getMaxVerticalDistance(self):
        return self._maxBoidDistance.v
    maxVerticalDistance = property(_getMaxVerticalDistance)
    
#######################
    def _getPushUpwardsHorizontalMagnitude(self):
        return boidConstants.pushUpwardsAccelerationHorizontal()
        #return self._pushUpwardsVector.v
    pushUpwardsHorizontalMagnitude = property(_getPushUpwardsHorizontalMagnitude)
    
    def _getPushUpwardsVerticalMagnitude(self):
        return boidConstants.pushUpwardsAccelerationVertical()
        #return self._pushUpwardsVector.u
    pushUpwardsVerticalMagnitude = property(_getPushUpwardsVerticalMagnitude)
        
####################### 
    def makeLeader(self, boid):
        if(not boid in self._leaders):
            self._leaders.append(boid)
    
    def unMakeLeader(self, boid):
        if(boid in self._leaders):
            self._leaders.remove(boid)
            
#######################        
    def resetAverages(self):
        self._boidPositionRunningTotal.reset()
        self._needsAveragePositionCalc = True
        self._boidDistanceRunningTotal.reset()
        self._needsAverageDistanceCalc = True
        self._maxBoidDistance.reset()
        self._boidDistanceLookup.clear()
        self._overTheWallLookup.clear()
        
        if(self._baseLocator != None):
            self._baseVector = boidUtil.boidVectorFromLocator(self._baseLocator)
        if(self._lipLocator != None):
            self._lipVector = boidUtil.boidVectorFromLocator(self._lipLocator)        
        if(self._finalLocator != None):
            self._finalLocator = boidUtil.boidVectorFromLocator(self._finalLocator)   
        self._baseToFinalDirection = self._finalVector - self._baseVector

#######################
    def checkBoidLocation(self, boid):
        
        baseToBoidVec = boid.currentPosition - self._baseVector

        boid._hasArrivedAtGoalBase = True
        
        if(abs(self._baseToFinalDirection.angleFrom(baseToBoidVec)) < 90):
            self.deRegisterBoidAsArrived(boid)
            self._overTheWallLookup.add(boid)
            boid.isAtPriorityGoal = True
            
            if(self._delegate != None):
                self._delegate.onBoidArrivedAtGoalDestination(self, boid)
                
            return True
        else:
            boid.isAtPriorityGoal = False
            if(boid.currentPosition.y >= (self._lipVector.y - 0.1)):
                self.deRegisterBoidAsArrived(boid)
                self._atTheLipLookup.add(boid)
                return True
            elif(baseToBoidVec.magnitude() < boidConstants.priorityGoalThreshold()):
                if(boid in self._overTheWallLookup):
                    self._overTheWallLookup.remove(boid)
                if(boid in self._atTheLipLookup):
                    self._atTheLipLookup.remove(boid)
                self.registerBoidAsArrived(boid)
                return True
            else:
                if(baseToBoidVec.magnitude() > (boidConstants.priorityGoalThreshold() * 4)):
                    boid._hasArrivedAtGoalBase = False
                self.deRegisterBoidAsArrived(boid)
                return False
                
        
        #overTheWall = False
        #if(boid.currentPosition.y >= self._lipVector.y):
            #overTheWall = True
        #else:
            #baseToBoidVec = boid.currentPosition - self._baseVector
            
            #if(abs(self._baseToFinalDirection.angleFrom(baseToBoidVec)) < 90):
                #overTheWall = True
                
        #if(overTheWall):
            #self.deRegisterBoidAsArrived(boid)
            #self._overTheWallLookup.add(boid)
            #return True
        #elif(self._baseVector.distanceFrom(boid.currentPosition) < boidConstants.priorityGoalThreshold()):
            #if(boid in self._overTheWallLookup):
                #self._overTheWallLookup.remove(boid)
            #self.registerBoidAsArrived(boid)
            #return True
        #else:
            #self.deRegisterBoidAsArrived(boid)
            #return False

#######################
    def registerBoidAsArrived(self, boid):
        if(not boid in self._boidDistanceLookup):
            if(boid in self._leaders):
                self._leaders.remove(boid)
            
            distanceVec = boid.currentPosition - self._baseVector
            self._boidDistanceRunningTotal.u += distanceVec.magnitude(True)
            self._boidDistanceRunningTotal.v += distanceVec.y
            self._needsAverageDistanceCalc = True         
            
            if(distanceVec.magnitude(True) > self._maxBoidDistance.u):
                self._maxBoidDistance.u = distanceVec.magnitude(True)
            if(distanceVec.y > self._maxBoidDistance.v):
                self._maxBoidDistance.v = distanceVec.y
            
            self._boidPositionRunningTotal.add(boid.currentPosition)
            self._needsAveragePositionCalc = True   
            
            self._boidDistanceLookup[boid] = distanceVec
            boid._hasArrivedAtGoalBase = True

#######################            
    def deRegisterBoidAsArrived(self, boid):
        if(boid in self._boidDistanceLookup):            
            distanceVec = boid.currentPosition - self._baseVector
            self._boidDistanceRunningTotal.u -= distanceVec.magnitude(True)
            self._boidDistanceRunningTotal.v -= distanceVec.y
            self._needsAverageDistanceCalc = True  
            
            self._boidPositionRunningTotal.subtract(boid.currentPosition)
            self._needsAveragePositionCalc = True       
            
            del self._boidDistanceLookup[boid]
            
        if(boid in self._overTheWallLookup):
            self._overTheWallLookup.remove(boid)
        if(boid in self._atTheLipLookup):
            self._atTheLipLookup.remove(boid)
        

#######################
    def getDesiredAcceleration(self, boid):
        if(boid in self._overTheWallLookup):
            targetVelocity = bv3.BoidVector3(self._baseToFinalDirection.x, 0, self._baseToFinalDirection.z)
            targetVelocity.normalise(boidConstants.goalChaseSpeed())
            retVal = targetVelocity - boid.currentVelocity
            if(retVal.magnitude() > boidConstants.maxAccel()):
                retVal.normalise(boidConstants.maxAccel())
            
            print("#%d escAcln=%s" % (boid.particleId, retVal))
            
            boid.stickinessScale = 0
            return retVal
        elif(boid in self._atTheLipLookup):
            retVal = bv3.BoidVector3(self._baseToFinalDirection.x, 0, self._baseToFinalDirection.z)
            retVal.normalise(boidConstants.goalChaseSpeed()) # misleading place to use goalChaseSpeed, should use something else??
            retVal.y = self.pushUpwardsVerticalMagnitude
            
            boid.stickinessScale = 0
            return retVal
        else:        
            directionToGoal = self._baseVector - boid.currentPosition
            horizontalComponent = directionToGoal.horizontalVector()
            horizontalComponent.normalise(self.pushUpwardsHorizontalMagnitude)
            
            distance = self._boidDistanceLookup[boid]
            if(distance.magnitude() < self.distanceAverage.magnitude()):
                diff = self.distanceAverage.magnitude() - distance.magnitude()
                proportion = diff / self.distanceAverage.magnitude()
                stickinessValue = 2 * proportion
    
                boid.stickinessScale = stickinessValue
            else:
                boid.stickinessScale = 0
                
            
            if(not self.performCollapse):
                return bv3.BoidVector3(horizontalComponent.u, self.pushUpwardsVerticalMagnitude, horizontalComponent.v)
            else:
                boid.stickinessScale = 0
                retVal = bv3.BoidVector3(-(horizontalComponent.u), 0, -(horizontalComponent.v))
                
                return retVal

#######################
    def getShouldJump(self, boid):
        distanceVec = boid.currentPosition - self._baseVector
        distance = distanceVec.magnitude(True)
        
        if(distance > boidConstants.priorityGoalThreshold() and
           distance < boidConstants.priorityGoalThreshold() + boidConstants.jumpOnPileUpRegionSize() and 
           random.uniform(0, 1.0) < boidConstants.jumpOnPileUpProbability()):
            return True
        else:
            return False