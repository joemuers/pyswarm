from boidBaseObject import BoidBaseObject

import boidVectors.vector3 as bv3

import weakref



class BehaviourDelegate(object):
    """Client objects can subclass BehaviourDelegate and pass the corresponding object
    to the behaviourBaseObject if they require a notification when behaviour completes."""
    
    def onBehaviourEndedForAgent(self, agent, behaviour, followOnBehaviourID):
        raise NotImplementedError

###################################

class BehaviourBaseObject(BoidBaseObject):
    
    def __init__(self, attributes, delegate=None):
        if(delegate is not None and not isinstance(delegate, BehaviourDelegate)): 
            raise TypeError
        else:
            self._delegate = weakref.ref(delegate) if(delegate is not None) else None
            self._attributes = attributes

##########################
    def __str__(self):
        return ("<Behaviour: \"%s\">" % self.behaviourId)

##########################            
    def _getAttributes(self):
        return self._attributes
    attributes = property(_getAttributes)
    
##########################
    def _getBehaviourId(self):
        return self._attributes.sectionTitle()
    behaviourId = property(_getBehaviourId)

##########################    
    def delegate(self):
        return self._delegate() if(self._delegate is not None) else None
 
##########################
    def _notifyDelegateBehaviourEndedForAgent(self, agent, followOnBehaviourID):
        """Should be called by subclasses to notify the delegate (if one exists)
        when an agent has finished the prescribed behaviour pattern.
        """
        if(self.delegate is not None):
            self.delegate.onBehaviourEndedForAgent(agent, self, followOnBehaviourID)
  
##########################          
    def onFrameUpdated(self):
        """Can be implemented by subclasses if necessary, to set up everything for a new frame."""
        pass  # default does nothing
 
##########################   
    def onAgentUpdated(self, agent):
        """Called when an agent's internal state has been updated. Override if needed."""
        pass  # default does nothing

##########################    
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):
        """Must be implemented by subclasses to calculate behaviour as appropriate.
        Should return a Vector3.
        """
        raise NotImplementedError

##########################    
    def getBehaviourSpecificAttributesForAgent(self, agent):
        """This object will be set to an agent state's 'behaviourAttributes' property when
        a behaviour is first assigned to the agent.
        For each behaviourBaseObject subclass, if the operation of the behaviour requires the
        agent objects to carry bespoke per-agent information, then the getNewDataBlobForAgent 
        method (within it's corresponding **attributesBaseObject** subclass) should be implemented to return an 
        appropriate data container object.
        """
        return self.attributes.getNewDataBlobForAgent(agent)

##########################
    def _clampMovementIfNecessary(self, agent, desiredAcceleration, maxAcceleration, maxVelocity, maxTurnRate, maxTurnAngleRateOfChange, maxTurnVelocity):
        if(self._clampRotationIfNecessary(agent, desiredAcceleration, maxAcceleration, maxTurnRate, maxTurnAngleRateOfChange, maxTurnVelocity)):
            return True
        elif(self._clampDesiredAccelerationIfNecessary(agent, desiredAcceleration, maxAcceleration, maxVelocity)):
            return True
        else:
            return False

##########################    
    def _clampRotationIfNecessary(self, agent, desiredAcceleration, maxAcceleration, maxTurnAngle, maxTurnAngleRateOfChange, maxTurnVelocity):
        currentVelocity = agent.currentVelocity
        potentialVelocity = currentVelocity + desiredAcceleration
        madeChanges = False
        
        desiredTurnAngle = currentVelocity.angleTo(potentialVelocity)
        
        # following block of code will smooth out sudden changes in direction by checking the
        # rateOfChange (i.e. acceleration) of *angular* velocity.
        if(maxAcceleration **2 > currentVelocity.magnitudeSquared()): # TODO - this first check is fairly arbitrary... 
            previousVelocity = currentVelocity - agent.currentAcceleration
            previousTurnAngle = previousVelocity.angleTo(currentVelocity)
            desiredRateOfChange = desiredTurnAngle - previousTurnAngle
             
            if(desiredRateOfChange > maxTurnAngleRateOfChange):
                maximumAngle = previousTurnAngle + maxTurnAngleRateOfChange
                angleCorrection = maximumAngle - desiredTurnAngle # rotates potentialVelcty back to within bounds
                potentialVelocity.rotateInHorizontal(angleCorrection)
                
                accelerationMagnitude = desiredAcceleration.magnitude()
                desiredAcceleration.resetToVector(potentialVelocity)
                desiredAcceleration.subtract(currentVelocity)
                desiredAcceleration.normalise(accelerationMagnitude)
                
                desiredTurnAngle = maximumAngle
                 
#                 madeChanges = True
            elif(desiredRateOfChange < -maxTurnAngleRateOfChange):
                minimumAngle = previousTurnAngle - maxTurnAngleRateOfChange
                angleCorrection = minimumAngle - desiredTurnAngle # rotates potentialVelcty back to within bounds
                potentialVelocity.rotateInHorizontal(angleCorrection) 
                 
                accelerationMagnitude = desiredAcceleration.magnitude()
                desiredAcceleration.resetToVector(potentialVelocity)
                desiredAcceleration.subtract(currentVelocity)
                desiredAcceleration.normalise(accelerationMagnitude)
                
                desiredTurnAngle = minimumAngle
#                 madeChanges = True
        
        # this block of code restricts the turnrate to a maximum value, and slows the agent to
        # the given 'turningSpeed' if the agent is attempting to turn at or above the max rate.
        if(desiredTurnAngle > maxTurnAngle):            
            angleCorrection = maxTurnAngle - desiredTurnAngle
            potentialVelocity.rotateInHorizontal(angleCorrection)
            desiredTurnAngle = maxTurnAngle
            
            desiredAcceleration.resetToVector(potentialVelocity)
            desiredAcceleration.subtract(currentVelocity)
            self._clampDesiredAccelerationIfNecessary(agent, desiredAcceleration, maxAcceleration, maxTurnVelocity)
            
            madeChanges = True
        elif(desiredTurnAngle < -maxTurnAngle):
            angleCorrection = -maxTurnAngle - desiredTurnAngle
            potentialVelocity.rotateInHorizontal(angleCorrection)
            desiredTurnAngle = -maxTurnAngle
            
            desiredAcceleration.resetToVector(potentialVelocity)
            desiredAcceleration.subtract(currentVelocity)           
            self._clampDesiredAccelerationIfNecessary(agent, desiredAcceleration, maxAcceleration, maxTurnVelocity)
            
            madeChanges = True
            
        return madeChanges
                    
##########################    
    def _clampDesiredAccelerationIfNecessary(self, agent, desiredAcceleration, maxAcceleration, maxVelocity):
        """Reduces desired acceleration, if necessary, such that resulting
        speed/acceleration stays below the maximum values.
        Should be considered a "protected" method.
        """
        madeChanges = False
        
        # restrict acceleration to <= max value
        accelerationMagnitude = desiredAcceleration.magnitude()
        if(accelerationMagnitude > maxAcceleration): 
            desiredAcceleration *= (maxAcceleration / accelerationMagnitude)
            madeChanges = True
        
        # restrict velocity to <= max value
        desiredVelocity = bv3.Vector3(agent.currentVelocity)
        desiredVelocity.add(desiredAcceleration)
        velocityMagnitude = desiredVelocity.magnitude()
        
        if(velocityMagnitude > maxVelocity): 
            desiredVelocity *= (maxVelocity / velocityMagnitude)
            desiredVelocity.subtract(agent.currentVelocity)
            desiredAcceleration.resetToVector(desiredVelocity)
            madeChanges = True
            
        return madeChanges


# END OF CLASS
#############################

