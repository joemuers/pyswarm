from behaviourBaseObject import BehaviourBaseObject
from boidResources import colours

import boidAttributes.classicBoidBehaviourAttributes as cbba
import boidVectors.vector3 as bv3

import random



######################
def AgentBehaviourIsClassicBoid(agent):
    return (type(agent.state.behaviourAttributes) == cbba.ClassicBoidDataBlob)

######################
def AttributesAreClassicBoid(attributes):
    return isinstance(attributes, cbba.ClassicBoidBehaviourAttributes)
    
######################

    

#######################################
class ClassicBoid(BehaviourBaseObject):
    
    def __init__(self, classicBoidAttributes, attributesController):
        super(ClassicBoid, self).__init__(classicBoidAttributes)
        
        self._movementAttributes = attributesController.agentMovementAttributes
        self._globalAttributes = attributesController.globalAttributes
        
        self._doNotClampMovement = False
        
######################         
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):
        desiredAcceleration = bv3.Vector3()
        self._doNotClampMovement = False
        
        if(agent.isTouchingGround):
            agent.state.updateRegionalStatsIfNecessary(agent, nearbyAgentsList)
            movementAttributes = agent.state.movementAttributes
            
            if(self._avoidMapEdgeBehaviour(agent, desiredAcceleration)):
                self._clampMovementIfNecessary(agent, 
                                               desiredAcceleration, 
                                               movementAttributes.maxAcceleration, 
                                               movementAttributes.maxVelocity, 
                                               movementAttributes.maxTurnRate,
                                               self._movementAttributes.maxTurnRateChange,
                                               movementAttributes.preferredTurnVelocity)
            elif(self._avoidNearbyAgentsBehaviour(agent, desiredAcceleration)):
                self._clampMovementIfNecessary(agent, 
                                               desiredAcceleration, 
                                               movementAttributes.maxAcceleration, 
                                               movementAttributes.maxVelocity, 
                                               movementAttributes.maxTurnRate,
                                               self._movementAttributes.maxTurnRateChange,
                                               movementAttributes.preferredTurnVelocity)
            else:
                if(self._matchSwarmHeadingBehaviour(agent, desiredAcceleration)):
                    self._matchSwarmPositionBehaviour(agent, desiredAcceleration)   # - TODO check if we want this or not???
                elif(not self._matchSwarmPositionBehaviour(agent, desiredAcceleration) and not agent.hasNeighbours):
                    self._searchForSwarmBehaviour(agent, desiredAcceleration)
                
                self._matchPreferredVelocityIfNecessary(agent, desiredAcceleration)
                self._kickstartAgentMovementIfNecessary(agent, desiredAcceleration)
                self._clampMovementIfNecessary(agent, 
                                               desiredAcceleration, 
                                               movementAttributes.maxAcceleration, 
                                               movementAttributes.maxVelocity, 
                                               movementAttributes.maxTurnRate,
                                               self._movementAttributes.maxTurnRateChange,
                                               movementAttributes.preferredTurnVelocity)
        self._setDebugColoursForAgent(agent)
        
        return desiredAcceleration
        
######################         
    def _avoidMapEdgeBehaviour(self, agent, desiredAcceleration):
        madeChanges = False
        
        lowerGridBounds = self._globalAttributes.lowerBounds
        upperGridBounds = self._globalAttributes.upperBounds
        movementAttributes = agent.state.movementAttributes
        
        if(agent.currentPosition.x < lowerGridBounds.u and agent.currentVelocity.x < movementAttributes.maxVelocity):
            desiredAcceleration.x += movementAttributes.maxAcceleration 
            madeChanges = True
        elif(upperGridBounds.u < agent.currentPosition.x and -(movementAttributes.maxVelocity) < agent.currentVelocity.x):
            desiredAcceleration.x -= movementAttributes.maxAcceleration
            madeChanges = True
        
        if(agent.currentPosition.z < lowerGridBounds.v and agent.currentVelocity.z < movementAttributes.maxVelocity):
            desiredAcceleration.z += movementAttributes.maxAcceleration 
            madeChanges = True
        elif(upperGridBounds.v < agent.currentPosition.z and -(movementAttributes.maxVelocity) < agent.currentVelocity.z):
            desiredAcceleration.z -= movementAttributes.maxAcceleration
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
            desiredAcceleration.normalise(agent.state.movementAttributes.maxAcceleration)
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
            
            if(desiredAngleMagnitude > agent.state.behaviourAttributes.alignmentDirectionThreshold):
                desiredVelocity = bv3.Vector3(agent.currentVelocity)
                desiredVelocity.rotateInHorizontal(desiredRotationAngle)
                desiredAcceleration.add(desiredVelocity - agent.currentVelocity)
                    
                return True

        return False

#############################
    def _matchSwarmPositionBehaviour(self, agent, desiredAcceleration):
        if(agent.hasNeighbours):
            distanceFromSwarmAvrgSquared = agent.currentPosition.distanceSquaredFrom(agent.state.avPosition)
            
            if(agent.state.behaviourAttributes.cohesionPositionThreshold **2 < distanceFromSwarmAvrgSquared):
                differenceVector = agent.state.avPosition - agent.currentPosition
                desiredAcceleration.add(differenceVector)
                
                return True

        return False

###################### 
    def _searchForSwarmBehaviour(self, agent, desiredAcceleration):
        ## TODO - change this algorithm??
        if(not agent.hasNeighbours):
            movementAttributes = agent.state.movementAttributes
            
            if(agent.currentVelocity.isNull()):
                desiredAcceleration.reset(movementAttributes.maxAcceleration, 0, 0)
                rotation = random.uniform(-179, 179)
                desiredAcceleration.rotateInHorizontal(rotation)
            else:
                desiredRotationAngle = random.uniform(-movementAttributes.maxTurnRate, movementAttributes.maxTurnRate)
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
        movementAttributes = agent.state.movementAttributes
        
        if(agent.currentVelocity.magnitude() < movementAttributes.preferredVelocity and 
           desiredAcceleration.magnitude() < movementAttributes.maxAcceleration):
            if(desiredAcceleration.isNull()):
                desiredAcceleration.resetToVector(agent.currentVelocity)
                desiredAcceleration.normalise(movementAttributes.maxAcceleration)
                
                madeChanges = True
            else:
                accelerationMagnitude = desiredAcceleration.magnitude()
                if(accelerationMagnitude < movementAttributes.maxAcceleration):
                    desiredAcceleration *= (movementAttributes.maxAcceleration / accelerationMagnitude)
                    
                    madeChanges = True
        
        return madeChanges

######################                     
    def _kickstartAgentMovementIfNecessary(self, agent, desiredAcceleration):
        """Occasionally a group of stationary agents can influence each other to remain still,
        collectively getting stuck.  This method corrects this behaviour.
        """
        magAccel = desiredAcceleration.magnitude()
        
        if(magAccel < self._movementAttributes.minVelocity and 
           agent.currentVelocity.magnitude() < self._movementAttributes.minVelocity and 
           agent.hasNeighbours and not agent.isCollided and not agent.isCrowded):
            desiredAcceleration.reset(agent.state.movementAttributes.maxAcceleration, 0, 0)
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

######################
    def _setDebugColoursForAgent(self, agent):
        if(not agent.isTouchingGround):
            agent.debugColour = colours.Normal_NotTouchingGround
        elif(agent.isCollided):
            agent.debugColour = colours.Normal_IsCollided
        elif(agent.isCrowded):
            agent.debugColour = colours.Normal_IsCrowded
        elif(agent.hasNeighbours):
            agent.debugColour = colours.Normal_HasNeighbours
        else:
            agent.debugColour = colours.Normal_NoNeighbours
        
        
# END OF CLASS 
##################################