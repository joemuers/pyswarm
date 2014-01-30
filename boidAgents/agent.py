from boidBaseObject import BoidBaseObject
from boidTools import sceneInterface

import boidVectors.vector3 as bv3
import agentState as agt
import boidResources.colours as brc



#####################################
class Agent(BoidBaseObject):
    """Represents single agent instance.   
    Logic concerning agent's behaviour is contained within this class. (Internally,
    data concerning position, heading, neighbourhood & so on is in the boidAgentState 
    container).
    
    Behaviour: Dependent on situation, in normal circumstances, behaviour governed by relatively
    straightforward implementation of Reynold's boids rules.  If currently goal-driven, behaviour
    is determined mainly by the corresponding boidBehaviours.goalDriven instance.
    Behaviour will also be affected if currently following a curve path, or at the scene's mapEdge border.
    
    Operation: Agent keeps an internal representation of the corresponding Maya nParticle's position, velocity etc, which
    must be updated on every frame (with updateCurrentVectors), desired behaviour is then calculated (calculateDesiredBehaviour method)
    - this is determined by the currently set 'behaviour' object (which might be normal boid-rules, or something different) and 
    is output in the form of the 'desiredAcceleration' member variable.
    When the final value of the desiredAcceleration has been calculated, it can be applied to the corresponding
    Maya nParticle (commitNewBehaviour method).
    
    
    Potentially confusing member variables:
        - positive/negativeGridBounds - opposing corners of the bounding grid plane over which the
                                        agent object can move.
        - desiredAcceleration - as determined by the current behaviour's rules.
        - needsBehaviourCalculation - True if postion/heading/circumstance has changed since last calculation, False otherwise.
        - needsBehaviourCommit - True if desiredAcceleration has been calculated since last frame update.
        
        - sticknessScale - directly related to Maya's 'stickiness' nParticle attribute.
                           Used primarily when agent is in basePyramid pile-up, to aid pyramid's
                           overall cohesion.
        
        
    TODO, leave in or take out?
        - 'leader' stuff
        - jump/jostle/clamber
        
    """

    def __init__(self, particleId, attributesController, startingBehaviour):
        self.state = agt.AgentState(int(particleId), attributesController)
        
        self.currentBehaviour = None
        
        self._desiredAcceleration = bv3.Vector3()
        self._needsBehaviourCalculation = False # True if position/heading/circumstance has 
        #                                       # changed since last calculation, False otherwise.
        self._needsBehaviourCommit = False  # True if behaviour has been updated since last commit, False otherwise.

        self._stickinessScale = -1.0
        self._stickinessChanged = False
        
        self.debugColour = brc.DefaultColour
        
        startingBehaviour.assignAgent(self)

##################### 
    def __str__(self):
        return "<%s, stck=%.2f, bhvr=\"%s\">" % (self.state, self.stickinessScale, self.currentBehaviour.behaviourId)
    
########
    def _getMetaStr(self):          
        return ("<%s, desiredAccel=%s>" % (self.state.metaStr, self._desiredAcceleration))
 
#####################   
    def __eq__(self, other):
        return (self.particleId == other.particleId) if(other is not None) else False
    
    def __ne__(self, other):
        return (self.particleId != other.particleId) if(other is not None) else True
    
    def __lt__(self, other):
        return self.particleId < other.particleId
    
    def __gt__(self, other):
        return self.particleId > other.particleId
    
    def __hash__(self):
        return hash(self.particleId)

#####################
    def _getParticleId(self):
        return self.state.particleId
    particleId = property(_getParticleId)

    def _getCurrentPosition(self):
        return self.state.position
    currentPosition = property(_getCurrentPosition)
    
    def _getCurrentVelocity(self):
        return self.state.velocity
    currentVelocity = property(_getCurrentVelocity)
    
    def _getCurrentAcceleration(self):
        return self.state.acceleration
    currentAcceleration = property(_getCurrentAcceleration)
    
    def _getStickinessScale(self):
        return self._stickinessScale
    def _SetSingleParticleStickinessScale(self, value):
        if(value != self._stickinessScale):
            self._stickinessScale= value
            self._stickinessChanged = True
    stickinessScale = property(_getStickinessScale, _SetSingleParticleStickinessScale) 
    
    def _getHasNeighbours(self):
        return self.state.hasNeighbours
    hasNeighbours = property(_getHasNeighbours)
    
    def _getIsCrowded(self):
        return self.state.isCrowded
    isCrowded = property(_getIsCrowded)
    
    def _getIsCollided(self):
        return self.state.isCollided
    isCollided = property(_getIsCollided)
    
    def _getIsTouchingGround(self):
        return self.state.isTouchingGround
    isTouchingGround = property(_getIsTouchingGround)
    
##################### 
    def updateCurrentVectors(self, position, velocity):
        """Updates internal state from corresponding vectors."""
        self.state.updateCurrentVectors(position, velocity)
        self._needsBehaviourCalculation = True         
        self._needsBehaviourCommit = False
        
        self.debugColour = brc.DefaultColour
        
        self.currentBehaviour.onAgentUpdated(self)
           
###########################
    def calculateDesiredBehaviour(self, otherAgentsList, forceUpdate=False):
        """Calculates desired behaviour and updates desiredAccleration accordingly."""
        if(self._needsBehaviourCalculation or forceUpdate):     
            self._desiredAcceleration = self.currentBehaviour.getDesiredAccelerationForAgent(self, otherAgentsList)
            
            self._needsBehaviourCalculation = False
            self._needsBehaviourCommit = True

##############################
    def _jump(self):
        if(self.isTouchingGround):
            self._desiredAcceleration.y += self.state.movementAttributes.jumpAcceleration
            self.state.notifyJump()
            self._needsBehaviourCommit = True
            return True
        else:
            return False

    def _stop(self):
        self._desiredAcceleration.resetToVector(self.currentVelocity, False)
        self._desiredAcceleration.invert()
        self._needsBehaviourCommit = True

######################  
    def commitNewBehaviour(self, particleShapeName):      
        """Updates agent's corresponding Maya nParticle with current internal state."""
        if(self._needsBehaviourCommit):
            desiredVelocity = bv3.Vector3(self.currentVelocity)
            desiredVelocity.add(self._desiredAcceleration)
            
            sceneInterface.SetSingleParticleVelocity(particleShapeName, self.particleId, desiredVelocity)
            
            if(self._stickinessChanged):
                sceneInterface.SetSingleParticleStickinessScale(particleShapeName, self.particleId, self.stickinessScale)
                self._stickinessChanged = False
            
            self._needsBehaviourCommit = False
     
        #pm.particle(particleShapeName, e=True, at="velocityU", id=self._particleId, fv=self._velocity.u)
        #pm.particle(particleShapeName, e=True, at="velocityV", id=self._particleId, fv=self._velocity.v)


# END OF CLASS - Agent
################################################################################

