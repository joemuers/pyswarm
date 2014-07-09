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


import random

from pyswarm.utils import colours
import pyswarm.attributes.behaviour.classicBoidAttributeGroup as cb
import pyswarm.vectors.vector3 as v3

from pyswarm.behaviours.behaviourBaseObject import BehaviourBaseObject



######################
def AgentBehaviourIsClassicBoid(agent):
    return (type(agent.state.behaviourAttributes) == cb.ClassicBoidDataBlob)

######################
def AttributesAreClassicBoid(attributeGroup):
    return isinstance(attributeGroup, cb.ClassicBoidAttributeGroup)
    
######################

    

#######################################
class ClassicBoid(BehaviourBaseObject):
    
    
    def __init__(self, classicBoidAttributeGroup, attributeGroupsController):
        super(ClassicBoid, self).__init__(classicBoidAttributeGroup)
        
        self._movementAttributeGroup = attributeGroupsController.agentMovementAttributeGroup
        self._globalAttributeGroup = attributeGroupsController.globalAttributeGroup
        
        self._doNotClampMovement = False
        
######################         
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):
        if(self.attributeGroup.shouldKickstartAgent(agent.agentId)):
            return self.attributeGroup.getKickstartVector()
        else:
            desiredAcceleration = v3.Vector3()
            self._doNotClampMovement = False
            
            if(not agent.isInFreefall):
                agent.state.updateRegionalStatsIfNecessary(agent, nearbyAgentsList)
                movementAttributes = agent.state.movementAttributes
                
                if(self._avoidMapEdgeBehaviour(agent, desiredAcceleration)): # avoiding map edge trumps "normal" behaviour
                    self._clampMovementIfNecessary(agent,                    # => don't do anything else if we're doing this.
                                                   desiredAcceleration, 
                                                   movementAttributes.maxAcceleration, 
                                                   movementAttributes.maxVelocity, 
                                                   movementAttributes.maxTurnRate,
                                                   self._movementAttributeGroup.maxTurnRateChange,
                                                   movementAttributes.preferredTurnVelocity)
                elif(self._avoidNearbyAgentsBehaviour(agent, desiredAcceleration)):
                    self._clampMovementIfNecessary(agent, 
                                                   desiredAcceleration, 
                                                   movementAttributes.maxAcceleration, 
                                                   movementAttributes.maxVelocity, 
                                                   movementAttributes.maxTurnRate,
                                                   self._movementAttributeGroup.maxTurnRateChange,
                                                   movementAttributes.preferredTurnVelocity)
                else:
                    behaviourAttributes = agent.state.behaviourAttributes
                    tempVector = v3.Vector3()
                    weightingTotal = 0
                    
                    if(self._avoidNearbyAgentsBehaviour(agent, tempVector)):
                        desiredAcceleration.add(tempVector * behaviourAttributes.separationWeighting)
                        weightingTotal += behaviourAttributes.separationWeighting
                        tempVector.reset()
                    
                    if(self._matchSwarmHeadingBehaviour(agent, tempVector)):
                        desiredAcceleration.add(tempVector * behaviourAttributes.alignmentWeighting)
                        weightingTotal += behaviourAttributes.alignmentWeighting
                        tempVector.reset()
                        
                    if(self._matchSwarmPositionBehaviour(agent, tempVector)):   # - TODO check if we want this or not???
                        desiredAcceleration.add(tempVector * behaviourAttributes.cohesionWeighting)
                        weightingTotal += behaviourAttributes.cohesionWeighting
                        
                    if(weightingTotal > 0):
                        desiredAcceleration.divide(weightingTotal)
                    elif(not agent.hasNeighbours):
                        self._searchForSwarmBehaviour(agent, desiredAcceleration)
                    
                    self._matchPreferredVelocityIfNecessary(agent, desiredAcceleration)
                    self._kickstartAgentMovementIfNecessary(agent, desiredAcceleration)
                    self._clampMovementIfNecessary(agent, 
                                                   desiredAcceleration, 
                                                   movementAttributes.maxAcceleration, 
                                                   movementAttributes.maxVelocity, 
                                                   movementAttributes.maxTurnRate,
                                                   self._movementAttributeGroup.maxTurnRateChange,
                                                   movementAttributes.preferredTurnVelocity)
            self._setDebugColoursForAgent(agent)
            
            return desiredAcceleration
        
######################         
    def _avoidMapEdgeBehaviour(self, agent, desiredAcceleration):
        madeChanges = False
        
        lowerGridBounds = self._globalAttributeGroup.lowerBounds
        upperGridBounds = self._globalAttributeGroup.upperBounds
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
        """
        Adds UN-WEIGHTED separation result to desiredAcceleration.
        """
        weighting = agent.behaviourAttributes.separationWeighting

        if(agent.isCollided and weighting > 0):  # Problem here - we're driving the velocity directly... should be done by Maya really
            ######### might not really need this if particle self-collisions are working properly... ??
            stopVector = v3.Vector3(agent.currentVelocity)
            stopVector.invert()
            
            avoidVector = v3.Vector3(agent.state.avCollisionDirection)
            avoidVector.resetToVector(agent.state.avCollisionDirection)
            avoidVector.invert()
            avoidVector.normalise(agent.state.movementAttributes.maxAcceleration)
            avoidVector.add(stopVector)
            
            desiredAcceleration.add(avoidVector)
            #  self._desiredAcceleration.y = 0
            self._doNotClampMovement = True
            
            return True
        
        elif(agent.isCrowded and weighting > 0):   # note that we move AWAY from the avPos here
            differenceVector = agent.currentPosition - agent.state.avCrowdedPosition
            desiredAcceleration.add(differenceVector)

            return True
        else:
            return False
            
####################### 
    def _matchSwarmHeadingBehaviour(self, agent, desiredAcceleration):
        """
        Adds UN-WEIGHTED alignment result to desiredAcceleration
        """
        weighting = agent.behaviourAttributes.alignmentWeighting
        
        if(agent.hasNeighbours and weighting > 0):
            
            if(self.attributeGroup.matchAlignmentHeadingOnly):
                desiredRotationAngle = agent.currentVelocity.angleTo(agent.state.avVelocity)
                desiredAngleMagnitude = abs(desiredRotationAngle)
                
                if(desiredAngleMagnitude > agent.behaviourAttributes.alignmentDirectionThreshold):
                    desiredVelocity = v3.Vector3(agent.currentVelocity)
                    desiredVelocity.rotateInHorizontal(desiredRotationAngle)
                    result = desiredVelocity - agent.currentVelocity
    
                    desiredAcceleration.add(result)
                        
                    return True
            else:
                desiredAcceleration.add(agent.state.avVelocity - agent.currentVelocity)

        return False

#############################
    def _matchSwarmPositionBehaviour(self, agent, desiredAcceleration):
        """
        Adds UN-WEIGHTED cohesion result to desiredAcceleration
        """
        state = agent.state
        weighting = state.behaviourAttributes.cohesionWeighting
        
        if(agent.hasNeighbours and weighting > 0):
            distanceFromSwarmAvrgSquared = agent.currentPosition.distanceSquaredFrom(state.avPosition)
            
            if(state.behaviourAttributes.cohesionPositionThreshold **2 < distanceFromSwarmAvrgSquared):
                differenceVector = state.avPosition - agent.currentPosition
                
                desiredAcceleration.add(weighting * differenceVector)
                
                return True

        return False

###################### 
    def _searchForSwarmBehaviour(self, agent, desiredAcceleration):
        """
        Adds search for neighbours result to desiredAcceleration if agent has no neighbours.
        """
        ## TODO - change this algorithm??
        if(not agent.hasNeighbours):
            movementAttributes = agent.state.movementAttributes
            
            if(agent.currentVelocity.isNull()):
                desiredAcceleration.reset(movementAttributes.maxAcceleration, 0, 0)
                rotation = random.uniform(-179, 179)
                desiredAcceleration.rotateInHorizontal(rotation)
            else:
                desiredRotationAngle = random.uniform(-movementAttributes.maxTurnRate, movementAttributes.maxTurnRate)
                desiredDirection = v3.Vector3(agent.currentVelocity)
                desiredDirection.rotateInHorizontal(desiredRotationAngle)
                desiredAcceleration.resetToVector(agent.currentVelocity - desiredDirection)         
            
            return True

        return False            

######################                     
    def _kickstartAgentMovementIfNecessary(self, agent, desiredAcceleration):
        """
        Occasionally a group of stationary agents can influence each other to remain still,
        collectively getting stuck.  This method corrects this behaviour.
        """
        magAccel = desiredAcceleration.magnitude()
        
        if(magAccel < self._movementAttributeGroup.minVelocity and 
           agent.currentVelocity.magnitude() < self._movementAttributeGroup.minVelocity and 
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
        if(agent.isInFreefall):
            agent.debugColour = colours.Normal_IsInFreefall
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