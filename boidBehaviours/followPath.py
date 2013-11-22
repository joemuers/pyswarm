from behaviourBaseObject import BehaviourBaseObject

import boidAttributes
from boidTools import util

import boidVectors.vector3 as bv3



_PATH_BEHAVIOUR_ID = "PATH"

def agentBehaviourIsFollowPath(agent):
    return (agent.state.behaviourSpecificState is not None and agent.state.behaviourSpecificState.__str__() == _PATH_BEHAVIOUR_ID)


class FollowPath(BehaviourBaseObject):
    """Uni-directional curve path along which all client agents will move.
    
    Behaviour: affected agents initially pulled in towards the closest point along the curve,
    after which they are propelled along the curve.  Upon reaching the end of the curve, each 
    agent will no longer be influenced by the curve.
    Note that if an agent's initial position is closer to the end point of the curve than any 
    other point, it will have effectively reached the end straight away and apparent behaviour 
    will not have been affected.
    
    Operation: affected agents must query for the desiredAcceleration on each frame update.
    """
    
    def __init__(self, curve, normalBehaviorInstance, bDelegate=None, taperStartMult=0.5, taperEndMult=2.0):
        """Arguments as follows:
        @param curve pymel.core.nodetypes.NurbsCurve: the curve path
        @param bDelegate BoidBehaviourDelegate: *MUST* be BoidBehaviourDelegate object (or None). Will be notified as boids
                                                reach end of curve path.
        @param taperStartMult Float: multiplier determining curve width at start.
        @param taperEndMult Float: multiplier determining curve width at end (width along the curve is interpolated start->end)
        """
        super(FollowPath, self).__init__(bDelegate)
        
        self._curve = curve
        self._startVector = util.BoidVector3FromPymelPoint(curve.getPointAtParam(0.0))
        self._endParam = curve.findParamFromLength(curve.length())
        endPoint = curve.getPointAtParam(self._endParam)
        self._endVector = util.BoidVector3FromPymelPoint(endPoint)
        
        self._taperStart = taperStartMult
        self._taperEnd = taperEndMult
        
        self._currentlyFollowingList = set()
        
        self._normalBehaviour = normalBehaviorInstance
        self._curveBehaviourInfluence = 0.75

################################       
    def __str__(self):
        return ("%s - tpSt=%.2f, tpEnd=%.2f, inf=%2.f" % 
                (_PATH_BEHAVIOUR_ID, self._taperStart, self._taperEnd, self.curveBehaviourInfluence))
        
#############################
    def _getMetaStr(self):
        agentStringsList = [("\n\t%s" % agent) for agent in self._currentlyFollowingList]
        
        return ("<crv=%s, strt=%s, end=%s (prm=%.2f), following:%s>" % 
                (self._curve, self._startVector, self._endVector, self._endParam, ''.join(agentStringsList)))

######################
    def createBehaviourSpecificStateObject(self):  # overridden BoidBehaviourBaseObject method
        return _PATH_BEHAVIOUR_ID # handy for logging

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
    
    def _getCurveBehaviourInfluence(self):
        """Ratio of curve-following behaviour against normal boid-rules behaviour.
        Must take value between 0.0 and 1.0
        """
        return self._curveBehaviourInfluence
    def _setCurveBehaviourInfluence(self, value):
        if(value < 0.0 or value > 1.0):
            raise TypeError
        else:
            self._curveBehaviourInfluence = value
    curveBehaviourInfluence = property(_getCurveBehaviourInfluence, _setCurveBehaviourInfluence)
     
################################ 
    def onFrameUpdate(self):  # overridden BoidBehaviourBaseObject method
        """Re-checks curve points from Maya in case the have moved..."""
        self._startVector = util.BoidVector3FromPymelPoint(self._curve.getPointAtParam(0.0, space='world'))
        self._endParam = self._curve.findParamFromLength(self._curve.length())
        endPoint = self._curve.getPointAtParam(self._endParam, space='world')
        self._endVector = util.BoidVector3FromPymelPoint(endPoint)        
 
################################          
    def getDesiredAccelerationForAgent(self, agent, nearbyAgents):  # overridden BoidBehaviourBaseObject method
        """Returns corresponding acceleration for the agent as determined by calculated behaviour.
        Client agents should call this method on each frame update and modify their own desiredAcceleration accordingly.
        """
        desiredAcceleration = bv3.Vector3()
        
        if(agent.isTouchingGround):  
            pymelLocationVector = util.PymelPointFromBoidVector3(agent.currentPosition)
            pymelClosestCurvePoint = self._curve.closestPoint(pymelLocationVector, space='world')
            boidCurveClosestPoint = util.BoidVector3FromPymelPoint(pymelClosestCurvePoint)
            
            if(boidCurveClosestPoint.distanceSquaredFrom(self._endVector) < boidAttributes.curveEndReachedDistanceThreshold() **2):
                self.endCurveBehaviourForAgent(agent)
            else:
                self._currentlyFollowingList.add(agent)
                
                currentParamValue = self._curve.getParamAtPoint(pymelClosestCurvePoint, space='world')
                lengthAlongCurve = currentParamValue / self._endParam
                fromStartWidth = (1 - lengthAlongCurve) * boidAttributes.curveDevianceThreshold() * self._taperStart
                fromEndWidth = lengthAlongCurve * boidAttributes.curveDevianceThreshold() * self._taperEnd
                finalWidth = fromStartWidth + fromEndWidth
                
                nearStart = False
                if(boidCurveClosestPoint.distanceSquaredFrom(agent.currentPosition) > finalWidth **2):
                    desiredAcceleration += (boidCurveClosestPoint - agent.currentPosition)
                    desiredAcceleration.normalise(boidAttributes.maxAccel())
                    nearStart = True
                
                if(currentParamValue > 0 or nearStart):
                    curveParam = self._curve.getParamAtPoint(pymelClosestCurvePoint, space='world')
                    tangent = self._curve.tangent(curveParam, space='world')
                    boidTangentVector = util.BoidVector3FromPymelVector(tangent)
                    
                    desiredAcceleration += boidTangentVector
                    desiredAcceleration.normalise(boidAttributes.curveGroupVectorMagnitude())

        #TODO - implement 'normal' boidBehaviours also???     
         
         
            self._clampDesiredAccelerationIfNecessary(agent, 
                                                     desiredAcceleration, 
                                                     boidAttributes.maxAccel(), 
                                                     boidAttributes.maxVel())
            if(self.curveBehaviourInfluence < 1.0):
                normalDesiredAcceleration = self._normalBehaviour.getDesiredAccelerationForAgent(agent, nearbyAgents)
                normalBehaviourInfluence = 1 - self.curveBehaviourInfluence
                normalDesiredAcceleration *= normalBehaviourInfluence
                desiredAcceleration *= self.curveBehaviourInfluence
                desiredAcceleration.add(normalDesiredAcceleration)
        
        
        return desiredAcceleration
    
    ################################   
    def endCurveBehaviourForAgent(self, agent):
#         boid.reachedEndOfCurvePath = True
        
        if(agent in self._currentlyFollowingList):
            self._currentlyFollowingList.remove(agent)     
            self._notifyDelegateBehaviourEndedForAgent(agent)
            
# END OF CLASS
###################################