import boidBaseObject as bbo

import boidVectors.vector3 as bv3



class BoidBehaviourDelegate(object):
    """Client objects can subclass BoidBehaviourDelegate and pass the corresponding object
    to the behaviourBaseObject if they require a notification when behaviour completes."""
    
    def onBehaviourEndedForAgent(self, agent, behaviour):
        raise NotImplementedError

##########################

class BehaviourBaseObject(bbo.BoidBaseObject):
    
    def __init__(self, delegate=None):
        if(delegate is not None and not isinstance(delegate, BoidBehaviourDelegate)): 
            raise TypeError
        else:
            self._delegate = delegate
    
    def _notifyDelegateBehaviourEndedForAgent(self, agent):
        """Should be called by subclasses to notify the delegate (if one exists)
        when an agent has finished the prescribed behaviour pattern.
        """
        if(self._delegate is not None):
            self._delegate.onBehaviourEndedForAgent(agent, self)
            
    def onFrameUpdate(self):
        """Can be implemented by subclasses if necessary, to set up everything for a new frame."""
        return  # default does nothing
    
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):
        """Must be implemented by subclasses to calculate behaviour as appropriate.
        Should return a Vector3.
        """
        raise NotImplementedError
    
    def createBehaviourSpecificStateObject(self):
        """This object will be set to an agent state's 'behaviourSpecificState' property when
        a behaviour is first assigned to the agent.
        Subclasses should implement this method and return an appropriate data container object
        if their operation requires the agent objects to carry bespoke information.
        """
        return None
    
    def clampDesiredAccelerationIfNecessary(self, agent, desiredAcceleration, maxAcceleration, maxVelocity):
        """Reduces desired acceleration, if necessary, such that resulting
        speed/acceleration stay below the maximum values.
        """
        madeChanges = False
        
        # restrict acceleration to <= max value
        magAccel = desiredAcceleration.magnitude()
        if(maxAcceleration < magAccel): 
            desiredAcceleration *= (maxAcceleration / magAccel)
            madeChanges = True
        
        # restrict velocity to <= max value
        desiredVelocity = bv3.Vector3(agent.currentVelocity)
        desiredVelocity.add(desiredAcceleration)
        magVel = desiredVelocity.magnitude()

        if(maxVelocity < magVel): 
            desiredVelocity *= (maxVelocity / magVel)
            desiredAcceleration.resetVec(desiredVelocity - agent.currentVelocity)
            madeChanges = True
            
        return madeChanges


