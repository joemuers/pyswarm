from behaviourBaseObject import BehaviourBaseObject
from boidTools import util

import boidAttributes.followPathBehaviourAttributes as fpba
import boidVectors.vector3 as bv3



#######################
def agentBehaviourIsFollowPath(agent):
    return (type(agent.state.behaviourAttributes) == fpba.FollowPathDataBlob)

#######################



##########################################
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
    
    def __init__(self, curve, normalBehaviorInstance, delegate=None):
        """Arguments as follows:
        @param curve pymel.core.nodetypes.NurbsCurve: the curve path
        @param delegate BoidBehaviourDelegate: *MUST* be BoidBehaviourDelegate object (or None). Will be notified as boids
                                                reach end of curve path.
        @param taperStartMult Float: multiplier determining curve width at start.
        @param taperEndMult Float: multiplier determining curve width at end (width along the curve is interpolated start->end)
        """
        super(FollowPath, self).__init__(delegate)
        
        self._curve = curve
        self._startVector = util.BoidVector3FromPymelPoint(curve.getPointAtParam(0.0))
        self._endParam = curve.findParamFromLength(curve.length())
        endPoint = curve.getPointAtParam(self._endParam)
        self._endVector = util.BoidVector3FromPymelPoint(endPoint)
        
        self._currentlyFollowingSet = set()
        
        self._normalBehaviour = normalBehaviorInstance

################################       
    def __str__(self):
        return ("FOLLOW-PATH: - tpSt=%.2f, tpEnd=%.2f, inf=%2.f" % 
                (self.attributes.taperStart, self.attributes.taperEnd, self.attributes.pathInfluenceMagnitude))
        
#############################
    def _getMetaStr(self):
        agentStringsList = [("\n\t%s" % agent) for agent in self._currentlyFollowingSet]
        
        return ("<crv=%s, strt=%s, end=%s (prm=%.2f), following:%s>" % 
                (self._curve, self._startVector, self._endVector, self._endParam, ''.join(agentStringsList)))

######################
    def _createBehaviourAttributes(self):
        return fpba.FollowPathBehaviourAttributes()

################################      
    def _getCurrentFollowCount(self):
        return len(self._currentlyFollowingSet)
    currentFollowCount = property(_getCurrentFollowCount)
    
    def _getStartPoint(self):
        return self._startVector
    startPoint = property(_getStartPoint)
    
    def _getEndPoint(self):
        return self._endVector
    endPoint = property(_getEndPoint)
    
################################ 
    def onFrameUpdated(self):  # overridden BoidBehaviourBaseObject method
        """Re-checks curve points from Maya in case the curve has moved..."""
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
            behaviourAttributes = agent.state.behaviourAttributes
            movementAttributes = agent.state.movementAttributes
            
            if(boidCurveClosestPoint.distanceSquaredFrom(self._endVector) < behaviourAttributes.goalDistanceThreshold **2):
                self.endCurveBehaviourForAgent(agent)
            else:
                self._currentlyFollowingSet.add(agent)
                
                currentParamValue = self._curve.getParamAtPoint(pymelClosestCurvePoint, space='world')
                lengthAlongCurve = currentParamValue / self._endParam
                fromStartWidth = (1 - lengthAlongCurve) * behaviourAttributes.pathDevianceThreshold * self.attributes.taperStart
                fromEndWidth = lengthAlongCurve * behaviourAttributes.pathDevianceThreshold * self.attributes.taperEnd
                finalWidth = fromStartWidth + fromEndWidth
                
                if(boidCurveClosestPoint.distanceSquaredFrom(agent.currentPosition) > finalWidth **2):
                    desiredAcceleration += (boidCurveClosestPoint - agent.currentPosition)
                    desiredAcceleration.normalise(movementAttributes.maxAcceleration)
                else:
                    tangent = self._curve.tangent(currentParamValue, space='world')
                    boidTangentVector = util.BoidVector3FromPymelVector(tangent)
                    
                    desiredAcceleration += boidTangentVector
                    desiredAcceleration.normalise(self.attributes.pathInfluenceMagnitude)
            
            if(self.attributes.pathInfluenceMagnitude < 1.0):
                normalDesiredAcceleration = self._normalBehaviour.getDesiredAccelerationForAgent(agent, nearbyAgents)
                normalBehaviourInfluence = 1 - self.attributes.pathInfluenceMagnitude
                normalDesiredAcceleration *= normalBehaviourInfluence
                desiredAcceleration *= self.attributes.pathInfluenceMagnitude
                desiredAcceleration.add(normalDesiredAcceleration)
            
            self._clampDesiredAccelerationIfNecessary(agent, 
                                         desiredAcceleration, 
                                         movementAttributes.maxAcceleration, 
                                         movementAttributes.maxVelocity)
        
        return desiredAcceleration
    
    ################################   
    def endCurveBehaviourForAgent(self, agent):
#         boid.reachedEndOfCurvePath = True
        
        if(agent in self._currentlyFollowingSet):
            self._currentlyFollowingSet.remove(agent)     
            self._notifyDelegateBehaviourEndedForAgent(agent)
            
# END OF CLASS
###################################