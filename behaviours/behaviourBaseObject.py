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


from pyswarmObject import PyswarmObject

import vectors.vector3 as v3

from abc import ABCMeta, abstractmethod
import weakref



###################################
class BehaviourDelegate(object):
    """Client objects can subclass BehaviourDelegate and pass themself as a delegate
    to the behaviourBaseObject if they require a notification when behaviour completes."""
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def onBehaviourEndedForAgent(self, agent, behaviour, followOnBehaviourID):
        raise NotImplementedError

# END OF CLASS - BehaviourDelegate
###################################



####################################
class BehaviourBaseObject(PyswarmObject):
    
    __metaclass__ = ABCMeta
    
##########################
    def __init__(self, attributeGroup, delegate=None):
        if(delegate is not None and not isinstance(delegate, BehaviourDelegate)): 
            raise TypeError
        else:
            self._delegate = weakref.ref(delegate) if(delegate is not None) else None
            self._attributeGroup = attributeGroup

##########################
    def __str__(self):
        return ("<Behaviour: \"%s\">" % self.behaviourId)
    
#############################        
    def __getstate__(self):
        state = super(BehaviourBaseObject, self).__getstate__()
        state["_delegate"] = self.delegate
        
        return state

########    
    def __setstate__(self, selfDict):
        self.__dict__.update(selfDict)
        if(self._delegate is not None):
            self._delegate = weakref.ref(self._delegate)

##########################            
    def _getAttributeGroup(self):
        return self._attributeGroup
    attributeGroup = property(_getAttributeGroup)
    
##########################
    def _getBehaviourId(self):
        return self._attributeGroup.behaviourId
    behaviourId = property(_getBehaviourId)

##########################    
    def _getDelegate(self):
        return self._delegate() if(self._delegate is not None) else None
    delegate = property(_getDelegate)
    
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
    
########
    def onCalculationsCompleted(self):
        """Called each time the swarm instance finishes calculating updates
        for the current frame.
        Override in subclasses if needed."""
        pass
 
##########################   
    def onAgentUpdated(self, agent):
        """Called when an agent's internal state has been updated. Override if needed."""
        pass  # default does nothing

##########################    
    def assignAgent(self, agent):
        if(agent.currentBehaviour is not self):
            agent.currentBehaviour = self
            
            try:
                agent.state.behaviourAttributes.onUnassigned()
            except:
                pass
            agent.state.behaviourAttributes = self.attributeGroup.getDataBlobForAgent(agent)

##########################    
    @abstractmethod
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):
        """Must be implemented by subclasses to calculate behaviour as appropriate.
        Should return a Vector3.
        """
        raise NotImplementedError

########    
    def getCompoundDesiredAcceleration(self, agent, nearbyAgentsList):
        if(agent.currentBehaviour is not self):
            agentPrimaryBehaviour = agent.currentBehaviour
            agentPrimaryAttributes = agent.state.behaviourAttributes
            
            agent.currentBehaviour = self
            ownAttributes = self.attributeGroup.getDataBlobForAgent(agent)
            agent.state.behaviourAttributes = ownAttributes

            result = self.getDesiredAccelerationForAgent(agent, nearbyAgentsList)
            
            agent.currentBehaviour = agentPrimaryBehaviour
            agent.state.behaviourAttributes = agentPrimaryAttributes
            try:
                ownAttributes.onUnassigned()
            except:
                pass
            
            return result
        else:
            return self.getDesiredAccelerationForAgent(agent, nearbyAgentsList)
            
################################
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
        desiredVelocity = v3.Vector3(agent.currentVelocity)
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

