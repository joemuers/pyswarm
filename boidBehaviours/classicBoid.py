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
        
        self._doNotClampAcceleration = False

######################       
    def __str__(self):
        return ("%s - %s" % (_CLASSIC_BEHAVIOUR_ID, super(ClassicBoid, self).__str__()))

######################
    def createBehaviourSpecificStateObject(self):
        return _CLASSIC_BEHAVIOUR_ID  # just give something to identify the behaviour itself
        
######################         
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):
        desiredAcceleration = bv3.Vector3()
        self._doNotClampAcceleration = False
        
        if(agent.isTouchingGround):
            agent.state.buildNearbyList(agent, nearbyAgentsList,
                                        boidAttributes.mainRegionSize(),
                                        boidAttributes.nearRegionSize(),
                                        boidAttributes.collisionRegionSize())
            
            if(self._avoidMapEdgeBehaviour(agent, desiredAcceleration)):
                self.clampDesiredAccelerationIfNecessary(agent, 
                                                         desiredAcceleration, 
                                                         boidAttributes.maxAccel(), 
                                                         boidAttributes.maxVel())
                return desiredAcceleration
            elif(self._avoidNearbyAgentsBehaviour(agent, desiredAcceleration)):
                self.clampDesiredAccelerationIfNecessary(agent, 
                                                         desiredAcceleration, 
                                                         boidAttributes.maxAccel(), 
                                                         boidAttributes.maxVel())
                return desiredAcceleration
            elif(self._matchSwarmHeadingBehaviour(agent, desiredAcceleration)):
                self._matchSwarmPositionBehaviour(agent, desiredAcceleration)   # - TODO check if we want this or not???
            elif(not self._matchSwarmPositionBehaviour(agent, desiredAcceleration) and not agent.hasNeighbours):
                self._searchForSwarmBehaviour(agent, desiredAcceleration)
             
            self._matchPreferredVelocityIfNecessary(agent, desiredAcceleration)
            self._kickstartAgentMovementIfNecessary(agent, desiredAcceleration)
            self.clampDesiredAccelerationIfNecessary(agent, 
                                                     desiredAcceleration, 
                                                     boidAttributes.maxAccel(), 
                                                     boidAttributes.maxVel())
            
        return desiredAcceleration
        
######################         
    def _avoidMapEdgeBehaviour(self, agent, desiredAcceleration):
        madeChange = False
        if(self._negativeGridBounds is not None and self._positiveGridBounds is not None):
            if(agent.currentPosition.x < self._negativeGridBounds.u and agent.currentVelocity.x < boidAttributes.maxVel()):
                desiredAcceleration.x = boidAttributes.maxAccel() 
                madeChange = True
            elif(self._positiveGridBounds.u < agent.currentPosition.x and -(boidAttributes.maxVel() ) < agent.currentVelocity.x):
                desiredAcceleration.x = -(boidAttributes.maxAccel() )
                madeChange = True
            
            if(agent.currentPosition.z < self._negativeGridBounds.v and agent.currentVelocity.z < boidAttributes.maxVel()):
                desiredAcceleration.z = boidAttributes.maxAccel() 
                madeChange = True
            elif(self._positiveGridBounds.v < agent.currentPosition.z and -(boidAttributes.maxVel() ) < agent.currentVelocity.z):
                desiredAcceleration.z = -(boidAttributes.maxAccel() )
                madeChange = True
        
        return madeChange
        
######################                  
    def _avoidNearbyAgentsBehaviour(self, agent, desiredAcceleration):
        if(agent.isCollided):  # Problem here - we're driving the velocity directly... should be done by Maya really
            ######### might not really need this if particle self-collisions are working properly... ??
            stopVector = bv3.Vector3(agent.currentVelocity)
            stopVector.invert()
            
            desiredAcceleration.resetVec(agent.state.avCollisionDirection)
            desiredAcceleration.invert()
            desiredAcceleration.normalise(boidAttributes.maxAccel())
            desiredAcceleration.add(stopVector)
            #  self._desiredAcceleration.y = 0
            self._doNotClampAcceleration = True
            
            return True
        
        elif(agent.isCrowded):   # note that we move AWAY from the avPos here
            differenceVector = agent.currentPosition - agent.state.avCrowdedPosition
            desiredAcceleration.resetVec(differenceVector)

            return True

        else:
            return False
            
####################### 
    def _matchSwarmHeadingBehaviour(self, agent, desiredAcceleration):
        # just change the heading here, *not* the speed...
        if(agent.hasNeighbours):
            desiredRotationAngle = agent.currentVelocity.angleFrom(agent.state.avVelocity)
            angleMag = abs(desiredRotationAngle)
            
            if(angleMag > boidAttributes.avDirectionThreshold()):
                if(angleMag > boidAttributes.maxTurnrate()):
                    desiredRotationAngle = boidAttributes.maxTurnrate() if(desiredRotationAngle > 0) else -(boidAttributes.maxTurnrate())
                
                desiredDirection = bv3.Vector3(agent.currentVelocity)
                desiredDirection.rotateInHorizontal(desiredRotationAngle)
                desiredAcceleration.resetVec(desiredDirection - agent.currentVelocity)
                    
                return True

        return False

#############################
    def _matchSwarmPositionBehaviour(self, agent, desiredAcceleration):
        if(agent.hasNeighbours):
            distanceFromSwarmAvrg = agent.currentPosition.distanceFrom(agent.state.avPosition)
            
            if(boidAttributes.avPositionThreshold() < distanceFromSwarmAvrg):
                differenceVector = agent.state.avPosition - agent.currentPosition
                desiredAcceleration.resetVec(differenceVector)
                
                return True

        return False

###################### 
    def _searchForSwarmBehaviour(self, agent, desiredAcceleration):
        ## TODO - change this algorithm??
        if(not agent.hasNeighbours):
            if(agent.currentVelocity.isNull()):
                desiredAcceleration.reset(boidAttributes.maxAccel(), 0, 0)
                rotation = random.uniform(-179, 179)
                desiredAcceleration.rotateInHorizontal(rotation)
            else:
                desiredRotationAngle = random.uniform(-boidAttributes.searchModeMaxTurnrate(), boidAttributes.searchModeMaxTurnrate())
                desiredDirection = bv3.Vector3(agent.currentVelocity)
                desiredDirection.rotateInHorizontal(desiredRotationAngle)
                desiredAcceleration.resetVec(agent.currentVelocity - desiredDirection)         
            
            return True

        return False            

######################             
    def _matchPreferredVelocityIfNecessary(self, agent, desiredAcceleration):
        """Will increase desiredAcceleration if agent is travelling/accelerating below the preferred minimum values."""
        
        if(agent.currentVelocity.magnitude() < boidAttributes.preferredVel() and 
           desiredAcceleration.magnitude() < boidAttributes.maxAccel()):
            if(desiredAcceleration.isNull()):
                desiredAcceleration.resetVec(agent.currentVelocity)
                desiredAcceleration.normalise(boidAttributes.maxAccel())
                
                return True
            else:
                magAccel = desiredAcceleration.magnitude()
                if(magAccel < boidAttributes.maxAccel()):
                    desiredAcceleration *= (boidAttributes.maxAccel() / magAccel)
                    
                    return True
        
        return False

######################                     
    def _kickstartAgentMovementIfNecessary(self, agent, desiredAcceleration):
        """Occasionally a group of stationary agents can influence each other to remain still,
        collectively getting stuck.  This method corrects this behaviour."""
        
        magAccel = desiredAcceleration.magnitude()
        
        if(magAccel < boidAttributes.minVel() and 
           agent.currentVelocity.magnitude() < boidAttributes.minVel() and 
           agent.hasNeighbours and not agent.isCollided and not agent.isCrowded):
            desiredAcceleration.reset(boidAttributes.maxAccel(), 0, 0)
            desiredHeading = random.uniform(-179, 179)
            desiredAcceleration.rotateInHorizontal(desiredHeading)
            
            return True
        
        return False

######################
    def clampDesiredAccelerationIfNecessary(self, agent, desiredAcceleration, maxAcceleration, maxVelocity):
        if(not self._doNotClampAcceleration):
            return super(ClassicBoid, self).clampDesiredAccelerationIfNecessary(agent, desiredAcceleration, maxAcceleration, maxVelocity)
        else:
            self._doNotClampAcceleration = False
            return False
        
        
        
# END OF CLASS 
##################################