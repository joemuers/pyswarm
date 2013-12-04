from behaviourBaseObject import BehaviourBaseObject

import random

import boidAttributes

import boidVectors.vector3 as bv3


_CLASSIC_BEHAVIOUR_ID = "CLASSIC"


def AgentBehaviourIsClassicBoid(agent):
    return (agent.state.behaviourSpecificState is not None and 
            agent.state.behaviourSpecificState.__str__() == _CLASSIC_BEHAVIOUR_ID)


#######################################
class ClassicBoid(BehaviourBaseObject):
    
    def __init__(self, negativeGridBounds, positiveGridBounds):
        super(ClassicBoid, self).__init__()
        
        self._negativeGridBounds = negativeGridBounds
        self._positiveGridBounds = positiveGridBounds
        
        self._doNotClampMovement = False

######################       
    def __str__(self):
        return ("%s - %s" % (_CLASSIC_BEHAVIOUR_ID, super(ClassicBoid, self).__str__()))

######################
    def createBehaviourSpecificStateObject(self):
        return _CLASSIC_BEHAVIOUR_ID  # just return something that can identify the behaviour itself
        
######################         
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):
        desiredAcceleration = bv3.Vector3()
        self._doNotClampMovement = False
        
        if(agent.isTouchingGround):
            agent.state.updateRegionalStatsIfNecessary(agent, nearbyAgentsList,
                                                       boidAttributes.MainRegionSize(),
                                                       boidAttributes.NearRegionSize(),
                                                       boidAttributes.CollisionRegionSize(),
                                                       boidAttributes.BlindRegionAngle(),
                                                       boidAttributes.ForwardVisionRegionAngle())
            
            if(self._avoidMapEdgeBehaviour(agent, desiredAcceleration)):
                self._clampMovementIfNecessary(agent, 
                                               desiredAcceleration, 
                                               boidAttributes.MaxAcceleration(), 
                                               boidAttributes.MaxVelocity(), 
                                               boidAttributes.MaxTurnRate(),
                                               boidAttributes.MaxTurnAngularAcceleration(),
                                               boidAttributes.PreferredTurnVelocity())
                
                return desiredAcceleration
            elif(self._avoidNearbyAgentsBehaviour(agent, desiredAcceleration)):
                self._clampMovementIfNecessary(agent, 
                                               desiredAcceleration, 
                                               boidAttributes.MaxAcceleration(), 
                                               boidAttributes.MaxVelocity(), 
                                               boidAttributes.MaxTurnRate(),
                                               boidAttributes.MaxTurnAngularAcceleration(),
                                               boidAttributes.PreferredTurnVelocity())
                
                return desiredAcceleration
            elif(self._matchSwarmHeadingBehaviour(agent, desiredAcceleration)):
                self._matchSwarmPositionBehaviour(agent, desiredAcceleration)   # - TODO check if we want this or not???
            elif(not self._matchSwarmPositionBehaviour(agent, desiredAcceleration) and not agent.hasNeighbours):
                self._searchForSwarmBehaviour(agent, desiredAcceleration)
            
            self._matchPreferredVelocityIfNecessary(agent, desiredAcceleration)
            self._kickstartAgentMovementIfNecessary(agent, desiredAcceleration)
            self._clampMovementIfNecessary(agent, 
                                           desiredAcceleration, 
                                           boidAttributes.MaxAcceleration(), 
                                           boidAttributes.MaxVelocity(), 
                                           boidAttributes.MaxTurnRate(),
                                           boidAttributes.MaxTurnAngularAcceleration(),
                                           boidAttributes.PreferredTurnVelocity())
            
        return desiredAcceleration
        
######################         
    def _avoidMapEdgeBehaviour(self, agent, desiredAcceleration):
        madeChanges = False
        if(self._negativeGridBounds is not None and self._positiveGridBounds is not None):
            if(agent.currentPosition.x < self._negativeGridBounds.u and agent.currentVelocity.x < boidAttributes.MaxVelocity()):
                desiredAcceleration.x += boidAttributes.MaxAcceleration() 
                madeChanges = True
            elif(self._positiveGridBounds.u < agent.currentPosition.x and -(boidAttributes.MaxVelocity()) < agent.currentVelocity.x):
                desiredAcceleration.x -= boidAttributes.MaxAcceleration()
                madeChanges = True
            
            if(agent.currentPosition.z < self._negativeGridBounds.v and agent.currentVelocity.z < boidAttributes.MaxVelocity()):
                desiredAcceleration.z += boidAttributes.MaxAcceleration() 
                madeChanges = True
            elif(self._positiveGridBounds.v < agent.currentPosition.z and -(boidAttributes.MaxVelocity()) < agent.currentVelocity.z):
                desiredAcceleration.z -= boidAttributes.MaxAcceleration()
                madeChanges = True
        
        return madeChanges
        
######################                  
    def _avoidNearbyAgentsBehaviour(self, agent, desiredAcceleration):
        if(agent.isCollided):  # Problem here - we're driving the velocity directly... should be done by Maya really
            ######### might not really need this if particle self-collisions are working properly... ??
            stopVector = bv3.Vector3(agent.currentVelocity)
            stopVector.invert()
            
            desiredAcceleration.resetToVector(agent.state.avCollisionDirection)
            desiredAcceleration.invert()
            desiredAcceleration.normalise(boidAttributes.MaxAcceleration())
            desiredAcceleration.add(stopVector)
            #  self._desiredAcceleration.y = 0
            self._doNotClampMovement = True
            
            return True
        
        elif(agent.isCrowded):   # note that we move AWAY from the avPos here
            differenceVector = agent.currentPosition - agent.state.avCrowdedPosition
            desiredAcceleration.add(differenceVector)

            return True

        else:
            return False
            
####################### 
    def _matchSwarmHeadingBehaviour(self, agent, desiredAcceleration):
        # just change the heading here, *not* the speed...
        if(agent.hasNeighbours):
            desiredRotationAngle = agent.currentVelocity.angleTo(agent.state.avVelocity)
            desiredAngleMagnitude = abs(desiredRotationAngle)
            
            if(desiredAngleMagnitude > boidAttributes.AvDirectionThreshold()):
                desiredVelocity = bv3.Vector3(agent.currentVelocity)
                desiredVelocity.rotateInHorizontal(desiredRotationAngle)
                desiredAcceleration.add(desiredVelocity - agent.currentVelocity)
                    
                return True

        return False

#############################
    def _matchSwarmPositionBehaviour(self, agent, desiredAcceleration):
        if(agent.hasNeighbours):
            distanceFromSwarmAvrgSquared = agent.currentPosition.distanceSquaredFrom(agent.state.avPosition)
            
            if(boidAttributes.AvPositionThreshold() **2 < distanceFromSwarmAvrgSquared):
                differenceVector = agent.state.avPosition - agent.currentPosition
                desiredAcceleration.add(differenceVector)
                
                return True

        return False

###################### 
    def _searchForSwarmBehaviour(self, agent, desiredAcceleration):
        ## TODO - change this algorithm??
        if(not agent.hasNeighbours):
            if(agent.currentVelocity.isNull()):
                desiredAcceleration.reset(boidAttributes.MaxAcceleration(), 0, 0)
                rotation = random.uniform(-179, 179)
                desiredAcceleration.rotateInHorizontal(rotation)
            else:
                desiredRotationAngle = random.uniform(-boidAttributes.MaxTurnRate(), boidAttributes.MaxTurnRate())
                desiredDirection = bv3.Vector3(agent.currentVelocity)
                desiredDirection.rotateInHorizontal(desiredRotationAngle)
                desiredAcceleration.resetToVector(agent.currentVelocity - desiredDirection)         
            
            return True

        return False            

######################             
    def _matchPreferredVelocityIfNecessary(self, agent, desiredAcceleration):
        """Will increase desiredAcceleration if agent is travelling/accelerating below 
        the preferred minimum values.
        """
        madeChanges = False
        
        if(agent.currentVelocity.magnitude() < boidAttributes.PreferredVelocity() and 
           desiredAcceleration.magnitude() < boidAttributes.MaxAcceleration()):
            if(desiredAcceleration.isNull()):
                desiredAcceleration.resetToVector(agent.currentVelocity)
                desiredAcceleration.normalise(boidAttributes.MaxAcceleration())
                
                madeChanges = True
            else:
                accelerationMagnitude = desiredAcceleration.magnitude()
                if(accelerationMagnitude < boidAttributes.MaxAcceleration()):
                    desiredAcceleration *= (boidAttributes.MaxAcceleration() / accelerationMagnitude)
                    
                    madeChanges = True
        
        return madeChanges

######################                     
    def _kickstartAgentMovementIfNecessary(self, agent, desiredAcceleration):
        """Occasionally a group of stationary agents can influence each other to remain still,
        collectively getting stuck.  This method corrects this behaviour.
        """
        magAccel = desiredAcceleration.magnitude()
        
        if(magAccel < boidAttributes.MinVelocity() and 
           agent.currentVelocity.magnitude() < boidAttributes.MinVelocity() and 
           agent.hasNeighbours and not agent.isCollided and not agent.isCrowded):
            desiredAcceleration.reset(boidAttributes.MaxAcceleration(), 0, 0)
            desiredHeading = random.uniform(-179, 179)
            desiredAcceleration.rotateInHorizontal(desiredHeading)
            
            return True
        
        return False

######################
    def _clampMovementIfNecessary(self, agent, desiredAcceleration, maxAcceleration, maxVelocity, maxTurnRate, maxAngularAcceleration, maxTurnVelocity):
        if(not self._doNotClampMovement):
            return super(ClassicBoid, self)._clampMovementIfNecessary(agent, desiredAcceleration, maxAcceleration, maxVelocity, maxTurnRate, maxAngularAcceleration, maxTurnVelocity)
        else:
            self._doNotClampMovement = False
            return False
        
        
        
# END OF CLASS 
##################################