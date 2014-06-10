#
# PySwarm, a swarming simulation tool for Autodesk Maya
#
# created 2013-2014
#
# @author: Joe Muers  (joemuers@hotmail.com)
# 
# All rights reserved.
#
# ------------------------------------------------------------


from pyswarm.utils import sceneInterface
import pyswarm.attributes.behaviour.followPathAttributeGroup as fp
import pyswarm.vectors.vector3 as v3

from pyswarm.behaviours.behaviourBaseObject import BehaviourBaseObject



#######################
def AgentBehaviourIsFollowPath(agent):
    return (type(agent.state.behaviourAttributes) == fp.FollowPathDataBlob)

#######################
def AttributesAreFollowPath(attributeGroup):
    return (isinstance(attributeGroup, fp.FollowPathAttributeGroup))

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
    
    def __init__(self, followPathAttrbutes, normalBehaviorInstance, delegate):
        """Arguments as follows:
        @param curve pymel.core.nodetypes.NurbsCurve: the curve path
        @param delegate BehaviourDelegate: *MUST* be BehaviourDelegate object (or None). Will be notified as agents
                                                reach end of curve path.
        @param taperStartMult Float: multiplier determining curve width at start.
        @param taperEndMult Float: multiplier determining curve width at end (width along the curve is interpolated start->end)
        """
        super(FollowPath, self).__init__(followPathAttrbutes, delegate)
        
        self._startVector = v3.Vector3()
        self._endParam = 0
        self._endVector = v3.Vector3()
        
        self._currentlyFollowingSet = set()
        
        self._normalBehaviour = normalBehaviorInstance
        
        self.onFrameUpdated()

################################       
    def __str__(self):
        return ("<%s: - tpSt=%.2f, tpEnd=%.2f, inf=%2.f>" % 
                (super(FollowPath, self).__str__(),
                 self.attributeGroup.taperStart, 
                 self.attributeGroup.taperEnd, 
                 self.attributeGroup.pathInfluenceMagnitude))
        
#############################
    def _getDebugStr(self):
        agentStringsList = [("\n\t%s" % agent) for agent in self._currentlyFollowingSet]
        
        return ("<crv=%s, strt=%s, end=%s (prm=%.2f), following:%s>" % 
                (self._pathCurve, self._startVector, self._endVector, self._endParam, ''.join(agentStringsList)))

######################
    def _getPathCurve(self):
        return self.attributeGroup.pathCurve
    _pathCurve = property(_getPathCurve)

################################      
    def _getCurrentFollowCount(self):
        return len(self._currentlyFollowingSet)
    currentFollowCount = property(_getCurrentFollowCount)
    
################################ 
    def onFrameUpdated(self):  # overridden BehaviourBaseObject method
        """Re-checks curve points from Maya in case the curve has moved..."""
        if(self._pathCurve is not None):
            self._startVector = sceneInterface.Vector3FromPymelPoint(self._pathCurve.getPointAtParam(0.0, space='world'))
            self._endParam = self._pathCurve.findParamFromLength(self._pathCurve.length())
            endPoint = self._pathCurve.getPointAtParam(self._endParam, space='world')
            self._endVector = sceneInterface.Vector3FromPymelPoint(endPoint)    
            
#################################
    def onAgentUpdated(self, agent):
        self._normalBehaviour.onAgentUpdated(agent)    
 
################################          
    def getDesiredAccelerationForAgent(self, agent, nearbyAgents):  # overridden BehaviourBaseObject method
        """Returns corresponding acceleration for the agent as determined by calculated behaviour.
        Client agents should call this method on each frame update and modify their own desiredAcceleration accordingly.
        """
        desiredAcceleration = v3.Vector3()
        
        if(self._pathCurve is not None and agent.isTouchingGround):  
            pymelLocationVector = sceneInterface.PymelPointFromVector3(agent.currentPosition)
            pymelClosestCurvePoint = self._pathCurve.closestPoint(pymelLocationVector, space='world')
            pyswarmCurveClosestPoint = sceneInterface.Vector3FromPymelPoint(pymelClosestCurvePoint)
            behaviourAttributes = agent.state.behaviourAttributes
            movementAttributes = agent.state.movementAttributes
            
            if(pyswarmCurveClosestPoint.distanceSquaredFrom(self._endVector) < behaviourAttributes.goalDistanceThreshold **2):
                self.endCurveBehaviourForAgent(agent)
            else:
                self._currentlyFollowingSet.add(agent)
                
                currentParamValue = self._pathCurve.getParamAtPoint(pymelClosestCurvePoint, space='world')
                lengthAlongCurve = currentParamValue / self._endParam
                fromStartWidth = (1 - lengthAlongCurve) * behaviourAttributes.pathDevianceThreshold * self.attributeGroup.taperStart
                fromEndWidth = lengthAlongCurve * behaviourAttributes.pathDevianceThreshold * self.attributeGroup.taperEnd
                finalWidth = fromStartWidth + fromEndWidth
                
                if(pyswarmCurveClosestPoint.distanceSquaredFrom(agent.currentPosition) > finalWidth **2):
                    desiredAcceleration += (pyswarmCurveClosestPoint - agent.currentPosition)
                    desiredAcceleration.normalise(movementAttributes.maxAcceleration)
                else:
                    tangent = self._pathCurve.tangent(currentParamValue, space='world')
                    pyswarmTangentVector = sceneInterface.Vector3FromPymelVector(tangent)
                    
                    desiredAcceleration += pyswarmTangentVector
                    desiredAcceleration.normalise(self.attributeGroup.pathInfluenceMagnitude)
            
            if(self.attributeGroup.pathInfluenceMagnitude < 1.0):
                normalDesiredAcceleration = self._normalBehaviour.getCompoundDesiredAcceleration(agent, nearbyAgents)
                normalBehaviourInfluence = 1 - self.attributeGroup.pathInfluenceMagnitude
                normalDesiredAcceleration *= normalBehaviourInfluence
                desiredAcceleration *= self.attributeGroup.pathInfluenceMagnitude
                desiredAcceleration.add(normalDesiredAcceleration)
            
            self._matchPreferredVelocityIfNecessary(agent, desiredAcceleration)
            self._clampDesiredAccelerationIfNecessary(agent, 
                                         desiredAcceleration, 
                                         movementAttributes.maxAcceleration, 
                                         movementAttributes.maxVelocity)
        
        return desiredAcceleration
    
################################   
    def endCurveBehaviourForAgent(self, agent):
        if(agent in self._currentlyFollowingSet):
            self._currentlyFollowingSet.remove(agent)     
            self._notifyDelegateBehaviourEndedForAgent(agent, self.attributeGroup.followOnBehaviourID)
            
# END OF CLASS
###################################