from boidBehaviourBaseObject import BoidBehaviourBaseObject

import random

import boidConstants
from boidTools import boidUtil

import boidVector2 as bv2
import boidVector3 as bv3
from boidBaseObject import BoidBaseObject



class _BoidGoalDrivenState(BoidBaseObject):
    _invalid, normal, pending, goalChase, inBasePyramid, atWallLip, overWallLip, reachedFinalGoal = range(8)
    
    def __init__(self, useInfectionSpread):
        self.currentStatus = _BoidGoalDrivenState.normal if useInfectionSpread else _BoidGoalDrivenState.goalChase
        self.didArriveAtBasePyramid = False
        self.goalChaseCountdown = -1
        
    def __str__(self):
        status = "UNKNOWN"
        if(self.currentStatus == _BoidGoalDrivenState.normal):
            status = "NORMAL"
        elif(self.currentStatus == _BoidGoalDrivenState.pending):
            status = "PENDING"
        elif(self.currentStatus == _BoidGoalDrivenState.goalChase):
            status = "GOAL_CHASE"
        elif(self.currentStatus == _BoidGoalDrivenState.inBasePyramid):
            status = "BASE_PYRAMID"
        elif(self.currentStatus == _BoidGoalDrivenState.atWallLip):
            status = "AT_LIP"
        elif(self.currentStatus == _BoidGoalDrivenState.overWallLip):
            status = "OVER_LIP"
        elif(self.currentStatus == _BoidGoalDrivenState.reachedFinalGoal):
            status = "AT_GOAL"
        
        return ("<GOAL, st=%s, arvd=%s, ctdn=%i>" % 
                (status, "Y" if self.didArriveAtBasePyramid else "N", self.goalChaseCountdown))

#######################    



def agentBehaviourIsGoalDriven(agent):
    return (agent.boidState.behaviourSpecificState != None and type(agent.boidState.behaviourSpecificState) == _BoidGoalDrivenState)

def agentIsChasingGoal(agent):
    return agentBehaviourIsGoalDriven(agent) and agent.boidState.behaviourSpecificState.currentStatus == _BoidGoalDrivenState.goalChase

def agentIsInBasePyramid(agent):
    return agentBehaviourIsGoalDriven(agent) and agent.boidState.behaviourSpecificState.currentStatus == _BoidGoalDrivenState.inBasePyramid

#######################

class BoidBehaviourGoalDriven(BoidBehaviourBaseObject):
    """Represents a goal towards which client agents are drawn.
    The idea is that the goal is at a section of wall, and you get a
    'World War Z' style pile-up at the wall, with the agents at the top
    of the pile-up coming over the wall.
    
    Behaviour: affected agents are initially drawn to the base section of 
    the wall, accelerating to 'goalChase' speed.  
    Upon reaching the base of the wall, they attempt to scale up it - as 
    more agents arrive, the collective mass forms a 'World War Z'-style 
    pyramid shaped pile-up which I've dubbed a 'basePyramid'.
    Once the basePyramid is of sufficient size, the agents at the top 
    are able to go over the wall and are considered to have reached their goal.
    
    Operation:  the groupTarget is represented by three Maya Locators:
    - baseLocator: point at the base of the wall towards which agents
                   are drawn in the initial goal-chase stage.  
                   The baseLocator also forms the centre point of the basePyramid.
    - lipLocator: point at the near-side top of the wall towards which agents
                  in the basePyramid attempt to reach.  Should be directly
                  above the baseLocator.
    - finalLocator: point at the far-side top of the wall towards which agents will move
                    once they have cleared the lipLocator (i.e. reached the top of the wall).
                    Once agents reach the finalLocator they are considered to have reached
                    their goal.
    'Infection spread' means that agents will initially follow 'normal' behaviour but, when coming into
    contact with another agent that is actively goal-driven, will themselves become actively goal-driven
    after a specified incubation period. 
    There is also the concept of 'leaders' whereby if certain agents are designated as leaders, they
    will be drawn to the baseLocator as normal but all non-leader agents will instead be drawn towards the
    leader's current position.  Once the leader reaches the basePyramid, other agents will revert 
    to normal behaviour. This, together with the goal-infection/incubation period algorithm, can produce 
    a nice 'streaming' effect of agents moving towards the goal. 
    
    Logic for client agent's behaviour is primarily in this class - client agents must query 
    the groupTarget on each frame to get their desiredAcceleration.
    """
    
    def __init__(self, basePos, lipPos, finalPos, normalBehaviourInstance, useInfectionSpread, bDelegate = None):
        """basePos, lipPos and finalPos must be Pymel Locator instances.
        normalBehaviourInstance = BoidBehaviourNormal instance."""
        
        super(BoidBehaviourGoalDriven, self).__init__(bDelegate)
        
        self._baseVector = boidUtil.boidVectorFromLocator(basePos)
        self._baseLocator = None
        if(not(type(basePos) == bv3.BoidVector3)):
            self._baseLocator = basePos
            
        self._lipVector = boidUtil.boidVectorFromLocator(lipPos)
        self._lipLocator = None
        if(not(type(lipPos) == bv3.BoidVector3)):
            self._lipLocator = lipPos
            
        self._finalVector = boidUtil.boidVectorFromLocator(finalPos)
        self._finalLocator = None
        if(not(type(finalPos) == bv3.BoidVector3)):
            self._finalLocator = finalPos
        
        self._baseToFinalDirection = bv3.BoidVector3() # direction vector from baseLocator to finalLocator
        
        self._leaders = []
        self._basePyramidDistanceLookup = {}
        self._atTheLipLookup = set()     # not used any more, but 
        self._overTheWallLookup = set()  # useful for debugging
        
        self._normalBehaviour = normalBehaviourInstance
        self._useInfectionSpread = useInfectionSpread
        
        # variables in the following block relate to agent's distance
        # from the baseLocator when in the basePyramid
        self._agentDistance_runningTotal = bv2.BoidVector2()
        self._agentDistance_average = bv2.BoidVector2()
        self._needsAverageDistanceCalc = False
        self._maxAgentDistance = bv2.BoidVector2()
        
        # variables here relate to average position taken from within
        # the basePyramid.
        self._agentPosition_runningTotal = bv3.BoidVector3()
        self._agentPosition_average = bv3.BoidVector3()
        self._needsAveragePositionCalc = False
        
        self._performCollapse = False
        
#######################        
    def __str__(self):            
        return ("GOAL - pos=%s, lip=%s, final=%s, infect=%s" % 
                (self._baseVector, self._lipVector, self._finalVector, "Y" if self.useInfectionSpread else "N"))
    
#######################
    def metaStr(self):
        leadersStr = ""
        for agent in self._leaders:
            leadersStr += ("%d," % agent.particleId)
        listStr = ""
        for agent, distance in sorted(self._basePyramidDistanceLookup.iteritems()):
            listStr += ("\t%s - dist=%s (mag=%.4f)\n" % (agent, distance, distance.magnitude()))
        atLipStr = ""
        for agent in self._atTheLipLookup:
            atLipStr += ("\t%s\n" % agent)
        overStr = ""
        for agent in self._overTheWallLookup:
            overStr += ("\t%s\n" % agent)
            
        return ("<ldrs=%s, avDist=%s, maxDist=%s, avPos=%s, atLoctn=\n%s\natLip=\n%s\nover=\n%s>" % 
                (leadersStr,
                 self._basePyramidAverageDistance(), self._maxAgentDistance, self._basePyramidAveragePosition(), 
                 listStr, atLipStr, overStr))
        
####################### 
    def _getUseInfectionSpread(self):
        return self._useInfectionSpread
    def _setUseInfectionSpread(self, value):
        self._useInfectionSpread = value
    useInfectionSpread = property(_getUseInfectionSpread, _setUseInfectionSpread)

####################### 
    def makeLeader(self, agent):
        if(not agent in self._leaders):
            self._leaders.append(agent)
            return True
        else:
            return False
        
    def unMakeLeader(self, agent):
        if(agent in self._leaders):
            self._leaders.remove(agent)
            return True
        else:
            return False
        
    def agentIsLeader(self, agent):
        return (agent in self._leaders)
        
#######################
    def createBehaviourSpecificStateObject(self):  # overridden BoidBehaviourBaseObject method
        return _BoidGoalDrivenState(self.useInfectionSpread)
            
#######################        
    def onFrameUpdate(self):  # overridden BoidBehaviourBaseObject method
        """Lists of agents must be rebuild on every frame, this method clears the lists
        and sets up everything for a new frame."""
        
        self._agentPosition_runningTotal.reset()
        self._needsAveragePositionCalc = True
        self._agentDistance_runningTotal.reset()
        self._needsAverageDistanceCalc = True
        self._maxAgentDistance.reset()
        self._basePyramidDistanceLookup.clear()
        self._overTheWallLookup.clear()
        
        # now, re-check Maya objects in case they've moved within the scene...
        if(self._baseLocator != None):
            self._baseVector = boidUtil.boidVectorFromLocator(self._baseLocator)
        if(self._lipLocator != None):
            self._lipVector = boidUtil.boidVectorFromLocator(self._lipLocator)        
        if(self._finalLocator != None):
            self._finalLocator = boidUtil.boidVectorFromLocator(self._finalLocator)   
        self._baseToFinalDirection = self._finalVector - self._baseVector

#######################
    def checkAgentLocation(self, agent):
        """Checks current location of agent to determine appropriate list it should be put
        into (which then determines corresponding behaviour)."""
        
        baseToAgentVec = agent.currentPosition - self._baseVector
        
        if(abs(self._baseToFinalDirection.angleFrom(baseToAgentVec)) < 90):
            # boid agent has cleared the wall...
            
            if(self._baseToFinalDirection.magnitude(True) < baseToAgentVec.magnitude(True)):
                # reached final goal
                self._deRegisterAgentFromBasePyramid(agent, _BoidGoalDrivenState.reachedFinalGoal)
                self._notifyDelegateBehaviourEndedForAgent(agent)
            else:
                # still on top of wall moving towards final goal
                self._deRegisterAgentFromBasePyramid(agent, _BoidGoalDrivenState.overWallLip)
            
            self._overTheWallLookup.add(agent)
            return True
        else:
            if(agent.currentPosition.y >= (self._lipVector.y - 0.1)):
                # agent has reached top of the wall, now will move twds final goal
                self._deRegisterAgentFromBasePyramid(agent, _BoidGoalDrivenState.atWallLip)
                self._atTheLipLookup.add(agent)
                
                return True
            elif(baseToAgentVec.magnitude() < boidConstants.priorityGoalThreshold()):
                # agent is close enough to be considered as being at the basePyramid
                self._registerAgentAtBasePyramid(agent)
                
                return True
            else:
                # agent is still some distance away is will simply chase the baseLocator/leader for now
                if(self._goalStatusForAgent(agent) >= _BoidGoalDrivenState.inBasePyramid):
                    self._deRegisterAgentFromBasePyramid(agent, _BoidGoalDrivenState.goalChase)
                
                behaviourStatus = agent.boidState.behaviourSpecificState
                if(behaviourStatus.didArriveBasePyramid and baseToAgentVec.magnitude() > (boidConstants.priorityGoalThreshold() * 4)):
                    # if miles away, may as well just start over afresh
                    behaviourStatus.didArriveBasePyramid = False
                
                return False
        

#######################
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):  # overridden BoidBehaviourBaseObject method
        """Returns corresponding acceleration for the agent as determined by calculated behaviour.
        Client agents should call this method on each frame update and modify their own desiredAcceleration accordingly."""
        
        desiredAcceleration = bv3.BoidVector3()
        agent.stickinessScale = 0 # reset on each frame, as may have been set on previous iteration

        if(agent.isTouchingGround):
            if(self._overWallLipBehaviour(agent, desiredAcceleration)):
                return desiredAcceleration
            elif(self._atWallLipBehaviour(agent, desiredAcceleration)):
                return desiredAcceleration
            elif(self._inBasePyramidBehaviour(agent, desiredAcceleration)):
                return desiredAcceleration
            else:
                agent.boidState.buildNearbyList(nearbyAgentsList,
                                               boidConstants.mainRegionSize(),
                                               boidConstants.nearRegionSize(),
                                               boidConstants.collisionRegionSize())
                
                if(self._atBasePyramidBorderBehaviour(agent, desiredAcceleration)):
                    return desiredAcceleration
                elif(self._goalChaseBehaviour(agent, desiredAcceleration)):
                    return desiredAcceleration
                elif(self._decrementGoalChaseCountdownIfNecessary(agent)):
                    self._goalChaseBehaviour(agent, desiredAcceleration)
                else:
                    self._startGoalChaseCountdownIfNecessary(agent)
                    return self._normalBehaviour.getDesiredAccelerationForAgent(agent, nearbyAgentsList)
                
        return desiredAcceleration

#######################
    def _overWallLipBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == _BoidGoalDrivenState.overWallLip or 
           self._goalStatusForAgent(agent) == _BoidGoalDrivenState.reachedFinalGoal):
            
            targetVelocity = bv3.BoidVector3(self._baseToFinalDirection.x, 0, self._baseToFinalDirection.z)
            targetVelocity.normalise(boidConstants.goalChaseSpeed())
            desiredAcceleration.resetVec(targetVelocity - agent.currentVelocity)
            if(desiredAcceleration.magnitude() > boidConstants.maxAccel()):
                desiredAcceleration.normalise(boidConstants.maxAccel())
            
            return True
        else:
            return False

#######################        
    def _atWallLipBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == _BoidGoalDrivenState.atWallLip):
            desiredAcceleration.x = self._baseToFinalDirection.x
            desiredAcceleration.z = self._baseToFinalDirection.z
            desiredAcceleration.normalise(boidConstants.goalChaseSpeed()) # misleading place to use goalChaseSpeed, should use something else??
            desiredAcceleration.y = self._basePyramidPushUpwardsMagnitudeVertical()
            
            return True
        else:
            return False

#######################
    def _inBasePyramidBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == _BoidGoalDrivenState.inBasePyramid):        
            directionToGoal = self._baseVector - agent.currentPosition
            horizontalComponent = directionToGoal.horizontalVector()
            horizontalComponent.normalise(self._basePyramidPushUpwardsMagnitudeHorizontal())
            
            distance = self._basePyramidDistanceLookup[agent]
            if(distance.magnitude() < self._basePyramidAverageDistance().magnitude()):
                diff = self._basePyramidAverageDistance().magnitude() - distance.magnitude()
                proportion = diff / self._basePyramidAverageDistance().magnitude()
                stickinessValue = 2 * proportion
                agent.stickinessScale = stickinessValue
                
            desiredAcceleration.x = horizontalComponent.u
            desiredAcceleration.z = horizontalComponent.v
            
            if(not self._performCollapse):
                desiredAcceleration.y = self._basePyramidPushUpwardsMagnitudeVertical()
            else:
                desiredAcceleration.invert()
                
            return True
        else:
            return False
        
#######################
    def _atBasePyramidBorderBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == _BoidGoalDrivenState.goalChase and agent.isCrowded):
            for nearbyAgent in agent.boidState.crowdedList:
                # as the basePyramid grows in size, it's perceived 'boundary' (i.e. the position at which agents are said 
                # to have joined the pyramid and can start their 'climbing' behaviour) is not fixed. So to determine it, we
                # look at other agents in the immediate vicinity and see if they themselves are in the pyramid.
                if(self._goalStatusForAgent(nearbyAgent) == _BoidGoalDrivenState.inBasePyramid and 
                   (nearbyAgent.currentPosition.distanceFrom(self.currentPosition) < boidConstants.priorityGoalThreshold()) and
                   (nearbyAgent.currentVelocity.magnitude(True) < boidConstants.goalChaseSpeed() or 
                    agent.currentVelocity.magnitude(True) < boidConstants.goalChaseSpeed() or 
                    abs(nearbyAgent.currentVelocity.angleFrom(agent.currentVelocity)) > 90) ):
                   
                    self._registerAgentAtBasePyramid(agent)
                    return self._inBasePyramidBehaviour(agent, desiredAcceleration)
        return False
    
#######################  
    def _goalChaseBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == _BoidGoalDrivenState.goalChase):
            directionVec = self._goalChaseAttractorPositionForAgent(agent) - agent.currentPosition
            directionVec.normalise(boidConstants.maxAccel())
            desiredAcceleration.resetVec(directionVec)      
            
            # push away from nearby agents??
            currentState = agent.boidState.behaviourSpecificState
            if(not currentState.didArriveAtBasePyramid and agent.isCrowded):   # note that we move AWAY from the avPos here
                differenceVector = agent.currentPosition - agent.boidState.avCrowdedPosition
                differenceVector.normalise(boidConstants.maxAccel())
                desiredAcceleration.add(differenceVector)    
            elif(currentState.didArriveAtBasePyramid):
                # Agents in a basePyramid sometimes get pushed to the corners and get
                # stuck there, which is not desirable. This corrects that behaviour.
                angle = abs(directionVec.angleFrom(self._baseToFinalDirection))
                if(angle > 82):
                    desiredAcceleration.subtract(self._baseToFinalDirection, True)
                    
            self.clampDesiredAccelerationIfNecessary(agent, 
                                                     desiredAcceleration, 
                                                     boidConstants.maxAccel(), 
                                                     boidConstants.goalChaseSpeed())
            
            
            # TODO - Not really sure what I was doing with this bit below...???
#             if(boid.isTouchingGround and boid.currentVelocity.magnitude() >= boidConstants.maxVel()):
#                 if(self._getShouldJump(agent)):
#                     agent._jump()
                    
            return True
        else:
            return False
 
#######################   
    def _decrementGoalChaseCountdownIfNecessary(self, agent):
        if(self._goalStatusForAgent(agent) == _BoidGoalDrivenState.pending):
            agent.boidState.behaviourSpecificState.goalChaseCountdown -= 1
            if(agent.boidState.behaviourSpecificState.goalChaseCountdown == 0):
                self._setGoalStatusForAgent(agent, _BoidGoalDrivenState.goalChase)
                return True

        return False

    def _startGoalChaseCountdownIfNecessary(self, agent):
        if(self._goalStatusForAgent(agent) == _BoidGoalDrivenState.normal):
            nearestNeighbour = None
            nearestNeighbourDistance = float('inf')                    
            for nearbyAgent in agent.boidState.nearbyList:
                if(nearbyAgent._currentBehaviour == self and
                   self._goalStatusForAgent(nearbyAgent) >= _BoidGoalDrivenState.goalChase):
                    distance = agent.currentPosition - nearbyAgent.currentPosition
                    if(distance.magnitude() < nearestNeighbourDistance):
                        nearestNeighbour = nearbyAgent
                        nearestNeighbourDistance = distance.magnitude()
                        
            if(nearestNeighbour != None):
                agent.setNewBehaviour(nearestNeighbour._currentBehaviour)
                return True
            
        return False

#######################
    def _registerAgentAtBasePyramid(self, agent):
        """Registers agent as having arrived at the basePyramid, behaviour
        for the agent will be switched from 'goalChase' to basePyramid 'push-up' behaviour."""
        
        if(not agent in self._basePyramidDistanceLookup):
            if(agent in self._leaders):
                self._leaders.remove(agent)
            
            distanceVec = agent.currentPosition - self._baseVector
            self._agentDistance_runningTotal.u += distanceVec.magnitude(True)
            self._agentDistance_runningTotal.v += distanceVec.y
            self._needsAverageDistanceCalc = True         
            
            if(distanceVec.magnitude(True) > self._maxAgentDistance.u):
                self._maxAgentDistance.u = distanceVec.magnitude(True)
            if(distanceVec.y > self._maxAgentDistance.v):
                self._maxAgentDistance.v = distanceVec.y
            
            self._agentPosition_runningTotal.add(agent.currentPosition)
            self._needsAveragePositionCalc = True   
            
            self._basePyramidDistanceLookup[agent] = distanceVec
            if(agent in self._overTheWallLookup):
                self._overTheWallLookup.remove(agent)
            if(agent in self._atTheLipLookup):
                self._atTheLipLookup.remove(agent)
        
        self._setGoalStatusForAgent(agent, _BoidGoalDrivenState.inBasePyramid)
          
    def _deRegisterAgentFromBasePyramid(self, agent, newStatus):
        """Should be called when agent leaves/falls out of basePyramid, switches out
        of 'push-up' behaviour"""
        
        if(newStatus == _BoidGoalDrivenState.inBasePyramid):
            raise TypeError
        
        if(agent in self._basePyramidDistanceLookup):            
            distanceVec = agent.currentPosition - self._baseVector
            self._agentDistance_runningTotal.u -= distanceVec.magnitude(True)
            self._agentDistance_runningTotal.v -= distanceVec.y
            self._needsAverageDistanceCalc = True  
            
            self._agentPosition_runningTotal.subtract(agent.currentPosition)
            self._needsAveragePositionCalc = True       
            
            del self._basePyramidDistanceLookup[agent]
            
        if(agent in self._overTheWallLookup):
            self._overTheWallLookup.remove(agent)
        if(agent in self._atTheLipLookup):
            self._atTheLipLookup.remove(agent)
            
        self._setGoalStatusForAgent(agent, newStatus)

#######################
    def _basePyramidAverageDistance(self):
        """Average distance from baseLocator of agents in the basePyramid."""
        
        if(self._needsAverageDistanceCalc and len(self._basePyramidDistanceLookup) > 0):
            self._agentDistance_average.resetVec(self._agentDistance_runningTotal)
            self._agentDistance_average.divide(len(self._basePyramidDistanceLookup))
            self._needsAverageDistanceCalc = False
        return self._agentDistance_average
    
    def _basePyramidAveragePosition(self):
        """Average position of agents in the basePyramid."""
        
        if(self._needsAveragePositionCalc and len(self._basePyramidDistanceLookup) > 0):
            self._agentPosition_average.resetVec(self._agentPosition_runningTotal)
            self._agentPosition_average.divide(len(self._basePyramidDistanceLookup))
            self._needsAveragePositionCalc = False
        return self._agentPosition_average
 
    def _basePyramidMaxDistanceHorizontal(self):
        """Current largest (scalar) horizontal distance of an agent, within the basePyramid, from the baseLocator."""
        return self._maxAgentDistance.u
    
    def _basePyramidMaxDistanceVertical(self):
        """Current largest (scalar) vertical distance of an agent, within the basePyramid, from the baseLocator."""
        return self._maxAgentDistance.v
    
    def _basePyramidPushUpwardsMagnitudeHorizontal(self):
        """Acceleration applied by each boid in the horizontal direction (towards 
        the baseLocator) after having joined the basePyramid."""
        return boidConstants.pushUpwardsAccelerationHorizontal()
        #return self._pushUpwardsVector.v
    
    def _basePyramidPushUpwardsMagnitudeVertical(self):
        """Acceleration applied by each boid in the vertical direction (towards 
        the lipLocator) after having joined the basePyramid."""
        return boidConstants.pushUpwardsAccelerationVertical()
        #return self._pushUpwardsVector.u
        
        
#######################
    def _goalChaseAttractorPositionForAgent(self, agent):
        """Returns position (BoidVector3) towards which the boidAgent should be made to move
        towards (when following goalChase behaviour)."""
        
        returnValue = None
        numLeaders = len(self._leaders)

        if(agent.didArriveAtBasePyramid or numLeaders == 0 or self.agentIsLeader(agent)):
            returnValue = self._baseVector
        elif(numLeaders == 1):
            returnValue = self._leaders[0].currentPosition
        else:
            candidateLeader = None
            minDist = agent.currentPosition.distanceFrom(self._baseVector)
            for leader in self._leaders:
                candidateDist = agent.currentPosition.distanceFrom(leader.currentPosition)
                if(candidateDist < minDist):
                    minDist = candidateDist
                    candidateLeader = leader
            
            if(candidateLeader != None):
                returnValue = candidateLeader.currentPosition
            else:
                returnValue = self._baseVector
                
        if(self._performCollapse):
            returnValue.invert()        
        
        return returnValue
    
#######################
    def _getShouldJump(self, agent):
        """Returns True if agent should jump up onto basePyramid, False otherwise."""
        
        distanceVec = agent.currentPosition - self._baseVector
        distance = distanceVec.magnitude(True)
        
        if(distance > boidConstants.priorityGoalThreshold() and
           distance < boidConstants.priorityGoalThreshold() + boidConstants.jumpOnPileUpRegionSize() and 
           random.uniform(0, 1.0) < boidConstants.jumpOnPileUpProbability()):
            return True
        else:
            return False

#######################        
    def _goalStatusForAgent(self, agent):
        if(agentBehaviourIsGoalDriven(agent)):
            return agent.boidState.behaviourSpecificState.currentStatus
        else:
            return _BoidGoalDrivenState._invalid
        
    def _setGoalStatusForAgent(self, agent, status):
        agent.boidState.behaviourSpecificState.currentStatus = status
        if(status >= _BoidGoalDrivenState.inBasePyramid):
            agent.boidState.behaviourSpecificState.didArriveAtBasePyramid = True
        
        
# END OF CLASS - BoidBehaviourGoalDriven
#######################


    
        