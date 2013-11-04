from boidBehaviourBaseObject import BoidBehaviourBaseObject

import random

import boidConstants

import boidVector3 as bv3


_normalBehaviourID = "NORMAL"


def agentBehaviourIsNormal(agent):
    return (agent.boidState.behaviourSpecificState != None and agent.boidState.behaviourSpecificState.__str__() == _normalBehaviourID)


#######################################
class BoidBehaviourNormal(BoidBehaviourBaseObject):
    
    def __init__(self, negativeGridBounds, positiveGridBounds):
        super(BoidBehaviourNormal, self).__init__()
        
        self._negativeGridBounds = negativeGridBounds
        self._positiveGridBounds = positiveGridBounds

######################       
    def __str__(self):
        return ("NORMAL - %s" % super(BoidBehaviourNormal, self).__str__())

######################
    def createBehaviourSpecificStateObject(self):
        return _normalBehaviourID  # just give something to identify the behaviour itself
        
######################         
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):
        desiredAcceleration = bv3.BoidVector3()
        
        if(agent.isTouchingGround):
            agent.boidState.buildNearbyList(nearbyAgentsList,
                                           boidConstants.mainRegionSize(),
                                           boidConstants.nearRegionSize(),
                                           boidConstants.collisionRegionSize())
            
            
            if(self._avoidMapEdgeBehaviour(agent, desiredAcceleration)):
                self.clampDesiredAccelerationIfNecessary(agent, 
                                                     desiredAcceleration, 
                                                     boidConstants.maxAccel(), 
                                                     boidConstants.maxVel())
                return desiredAcceleration
            elif(self._avoidNearbyAgentsBehaviour(agent, desiredAcceleration)):
                self.clampDesiredAccelerationIfNecessary(agent, 
                                                     desiredAcceleration, 
                                                     boidConstants.maxAccel(), 
                                                     boidConstants.maxVel())
                return desiredAcceleration
            elif(self._matchSwarmHeadingBehaviour(agent, desiredAcceleration)):
                self._matchSwarmPositionBehaviour(agent, desiredAcceleration)   # - TODO check if we want this or not???
            elif(self._matchSwarmPositionBehaviour(agent, desiredAcceleration)):
                self._searchForSwarmBehaviour(agent, desiredAcceleration)
            
            self._matchPreferredVelocityIfNecessary(agent, desiredAcceleration)
            self._kickstartAgentMovementIfNecessary(agent, desiredAcceleration)
            self.clampDesiredAccelerationIfNecessary(agent, 
                                                     desiredAcceleration, 
                                                     boidConstants.maxAccel(), 
                                                     boidConstants.maxVel())
            
        return desiredAcceleration
        
######################         
    def _avoidMapEdgeBehaviour(self, agent, desiredAcceleration):
        madeChange = False
        if(self._negativeGridBounds != None and self._positiveGridBounds != None):
            if(agent.currentPosition.x < self._negativeGridBounds.u and agent.currentVelocity.x < boidConstants.maxVel()):
                desiredAcceleration.x = boidConstants.maxAccel() 
                madeChange = True
            elif(self._positiveGridBounds.u < agent.currentPosition.x and -(boidConstants.maxVel() ) < agent.currentVelocity.x):
                desiredAcceleration.x = -(boidConstants.maxAccel() )
                madeChange = True
            
            if(agent.currentPosition.z < self._negativeGridBounds.v and agent.currentVelocity.z < boidConstants.maxVel()):
                desiredAcceleration.z = boidConstants.maxAccel() 
                madeChange = True
            elif(self._positiveGridBounds.v < agent.currentPosition.z and -(boidConstants.maxVel() ) < agent.currentVelocity.z):
                desiredAcceleration.z = -(boidConstants.maxAccel() )
                madeChange = True
        
        return madeChange
        
######################                  
    def _avoidNearbyAgentsBehaviour(self, agent, desiredAcceleration):
        if(agent.isCollided):  # Problem here - we're driving the velocity directly... should be done by Maya really
            ######### might not really need this if particle self-collisions are working properly... ??
            stopVector = bv3.BoidVector3(agent.currentVelocity)
            stopVector.invert()
            
            desiredAcceleration.resetVec(agent.boidState.avCollisionDirection)
            desiredAcceleration.invert()
            desiredAcceleration.normalise(boidConstants.maxAccel())
            desiredAcceleration.add(stopVector)
            #  self._desiredAcceleration.y = 0
            
            return True
        
        elif(agent.isCrowded):   # note that we move AWAY from the avPos here
            differenceVector = agent.currentPosition - agent.boidState.avCrowdedPosition
            desiredAcceleration.resetVec(differenceVector)

            return True

        else:
            return False
            
####################### 
    def _matchSwarmHeadingBehaviour(self, agent, desiredAcceleration):
        # just change the heading here, *not* the speed...
        if(agent.hasNeighbours):
            desiredRotationAngle = agent.currentVelocity.angleFrom(agent.boidState.avVelocity)
            angleMag = abs(desiredRotationAngle)
            
            if(angleMag > boidConstants.avDirectionThreshold()):
                if(angleMag > boidConstants.maxTurnrate()):
                    desiredRotationAngle = boidConstants.maxTurnrate() if(desiredRotationAngle > 0) else -(boidConstants.maxTurnrate())
                
                desiredDirection = bv3.BoidVector3(agent.currentVelocity)
                desiredDirection.rotateInHorizontal(desiredRotationAngle)
                desiredAcceleration.resetVec(desiredDirection - agent.currentVelocity)
                    
                return True

        return False

#############################
    def _matchSwarmPositionBehaviour(self, agent, desiredAcceleration):
        if(agent.hasNeighbours):
            distanceFromSwarmAvrg = agent.currentPosition.distanceFrom(agent.boidState.avPosition)
            
            if(boidConstants.avPositionThreshold() < distanceFromSwarmAvrg):
                differenceVector = agent.boidState.avPosition - agent.currentPosition
                desiredAcceleration.resetVec(differenceVector)
                
                return True

        return False

###################### 
    def _searchForSwarmBehaviour(self, agent, desiredAcceleration):
        ## TODO - change this algorithm??
        if(not agent.hasNeighbours):
            if(agent.currentVelocity.isNull()):
                desiredAcceleration.reset(boidConstants.maxAccel(), 0, 0)
                rotation = random.uniform(-179, 179)
                desiredAcceleration.rotateInHorizontal(rotation)
            else:
                desiredRotationAngle = random.uniform(-boidConstants.searchModeMaxTurnrate(), boidConstants.searchModeMaxTurnrate())
                desiredDirection = bv3.BoidVector3(agent.currentVelocity)
                desiredDirection.rotateInHorizontal(desiredRotationAngle)
                desiredAcceleration.resetVec(agent.currentVelocity - desiredDirection)         
            
            return True

        return False            

######################             
    def _matchPreferredVelocityIfNecessary(self, agent, desiredAcceleration):
        """Will increase desiredAcceleration if agent is travelling/accelerating below the preferred minimum values."""
        
        if(agent.currentVelocity.magnitude() < boidConstants.preferredVel() and 
           desiredAcceleration.magnitude() < boidConstants.maxAccel()):
            if(desiredAcceleration.isNull()):
                desiredAcceleration.resetVec(agent.currentVelocity)
                desiredAcceleration.normalise(boidConstants.maxAccel())
                
                return True
            else:
                magAccel = desiredAcceleration.magnitude()
                if(magAccel < boidConstants.maxAccel()):
                    desiredAcceleration *= (boidConstants.maxAccel() / magAccel)
                    
                    return True
        
        return False

######################                     
    def _kickstartAgentMovementIfNecessary(self, agent, desiredAcceleration):
        """Occasionally a group of stationary agents can influence each other to remain still,
        collectively getting stuck.  This method corrects this behaviour."""
        
        magAccel = desiredAcceleration.magnitude()
        
        if(magAccel < boidConstants.minVel() and 
           agent.currentVelocity.magnitude() < boidConstants.minVel() and 
           agent.hasNeighbours and not agent.isCollided and not agent.isCrowded):
            desiredAcceleration.reset(boidConstants.maxAccel(), 0, 0)
            desiredHeading = random.uniform(-179, 179)
            desiredAcceleration.rotateInHorizontal(desiredHeading)
            
            return True
        
        return False

# END OF CLASS 
##################################