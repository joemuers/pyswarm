import boidConstants
import boidUtil
import boidVector3 as bv3


class BoidGroupPath(object):
    
    def __init__(self, curve, bDelegate = None, taperStartMult = 0.5, taperEndMult = 2.0):
        self._curve = curve
        self._startVector = boidUtil.boidVectorFromPymelPoint(curve.getPointAtParam(0.0))
        self._endParam = curve.findParamFromLength(curve.length())
        endPoint = curve.getPointAtParam(self._endParam)
        self._endVector = boidUtil.boidVectorFromPymelPoint(endPoint)
        self._goalReachedDelegate = bDelegate
        
        self._taperStart = taperStartMult
        self._taperEnd = taperEndMult
        
        self._currentlyFollowingList = set()

################################       
    def __str__(self):
        followingStr = ""
        for boid in self._currentlyFollowingList:
            followingStr += "\n\t%s" % boid
        
        return ("<crv=%s, strt=%s, end=%s (prm=%.2f), following:%s>" % (self._curve, self._startVector, self._endVector, self._endParam, followingStr))

################################      
    def _getCurrentFollowCount(self):
        return len(self._currentlyFollowingList)
    currentFollowCount = property(_getCurrentFollowCount)
    
    def _getStartPoint(self):
        return self._startVector
    startPoint = property(_getStartPoint)
    
    def _getEndPoint(self):
        return self._endVector
    endPoint = property(_getEndPoint)
    
    def notifyNoLongerFollowing(self, boid):
        if(boid in self._currentlyFollowingList):
            self._currentlyFollowingList.remove(boid)        
    
################################ 
    def recheckCurvePoints(self):
        self._startVector = boidUtil.boidVectorFromPymelPoint(self._curve.getPointAtParam(0.0, space='world'))
        self._endParam = self._curve.findParamFromLength(self._curve.length())
        endPoint = self._curve.getPointAtParam(self._endParam, space='world')
        self._endVector = boidUtil.boidVectorFromPymelPoint(endPoint)        
 
################################          
    def getDesiredAcceleration(self, boid):
        pymelLocationVector = boidUtil.pymelPointFromBoidVector(boid.currentPosition)
        pymelClosestCurvePoint = self._curve.closestPoint(pymelLocationVector, space='world')
        boidCurveClosestPoint = boidUtil.boidVectorFromPymelPoint(pymelClosestCurvePoint)
        
        desiredAcceleration = bv3.BoidVector3()
        
        if(boidCurveClosestPoint.distanceFrom(self._endVector) < boidConstants.curveEndReachedThreshold()):
            boid.reachedEndOfCurvePath = True
            self.notifyNoLongerFollowing(boid)
                
            if(self._goalReachedDelegate != None):
                self._goalReachedDelegate.onGoalReachedForBoid(boid)
        else:
            self._currentlyFollowingList.add(boid)
            
            currentParamValue = self._curve.getParamAtPoint(pymelClosestCurvePoint, space='world')
            lengthAlongCurve = currentParamValue / self._endParam
            fromStartWidth = (1- lengthAlongCurve) * boidConstants.curveDevianceThreshold() * self._taperStart
            fromEndWidth = lengthAlongCurve * boidConstants.curveDevianceThreshold() * self._taperEnd
            finalWidth = fromStartWidth + fromEndWidth
            
            nearStart = False
            if(boidCurveClosestPoint.distanceFrom(boid.currentPosition) > finalWidth):
                desiredAcceleration += (boidCurveClosestPoint - boid.currentPosition)
                desiredAcceleration.normalise(boidConstants.maxAccel())
                nearStart = True
            
            if(currentParamValue > 0 or nearStart):
                curveParam = self._curve.getParamAtPoint(pymelClosestCurvePoint, space='world')
                tangent = self._curve.tangent(curveParam, space='world')
                boidTangentVector = boidUtil.boidVectorFromPymelVector(tangent)
                
                desiredAcceleration += boidTangentVector
                desiredAcceleration.normalise(boidConstants.curveGroupVectorMagnitude())
                
        
        return desiredAcceleration