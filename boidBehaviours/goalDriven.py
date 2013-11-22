from behaviourBaseObject import BehaviourBaseObject

import random

import boidAttributes
from boidTools import util

import boidVectors.vector2 as bv2
import boidVectors.vector3 as bv3
from boidBaseObject import BoidBaseObject



def AgentBehaviourIsGoalDriven(agent):
    return (agent.state.behaviourSpecificState is not None and 
            type(agent.state.behaviourSpecificState) == GoalDriven._BoidGoalDrivenState)

def AgentIsChasingGoal(agent):
    return (AgentBehaviourIsGoalDriven(agent) and 
            agent.state.behaviourSpecificState.currentStatus == GoalDriven._BoidGoalDrivenState.goalChase)

def AgentIsInBasePyramid(agent):
    return (AgentBehaviourIsGoalDriven(agent) and 
            agent.state.behaviourSpecificState.currentStatus == GoalDriven._BoidGoalDrivenState.inBasePyramid)

#######################

class GoalDriven(BehaviourBaseObject):
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
    
    #################################
    class _BoidGoalDrivenState(BoidBaseObject):
        """Internal class, instances are assigned to client agent's state.behaviourSpecificState property
        and used to store individual agent data.
        """
        _invalid, normal, pending, goalChase, inBasePyramid, atWallLip, overWallLip, reachedFinalGoal = range(8)
        
        def __init__(self, useInfectionSpread):
            self.currentStatus = (GoalDriven._BoidGoalDrivenState.normal if useInfectionSpread 
                                  else GoalDriven._BoidGoalDrivenState.goalChase)
            self.didArriveAtBasePyramid = False
            self.goalChaseCountdown = -1
            
        def __str__(self):
            status = ("UNKNOWN (%d)" % self.currentStatus)
            if(self.currentStatus == GoalDriven._BoidGoalDrivenState.normal):
                status = "NORMAL"
            elif(self.currentStatus == GoalDriven._BoidGoalDrivenState.pending):
                status = "PENDING"
            elif(self.currentStatus == GoalDriven._BoidGoalDrivenState.goalChase):
                status = "GOAL_CHASE"
            elif(self.currentStatus == GoalDriven._BoidGoalDrivenState.inBasePyramid):
                status = "BASE_PYRAMID"
            elif(self.currentStatus == GoalDriven._BoidGoalDrivenState.atWallLip):
                status = "AT_LIP"
            elif(self.currentStatus == GoalDriven._BoidGoalDrivenState.overWallLip):
                status = "OVER_LIP"
            elif(self.currentStatus == GoalDriven._BoidGoalDrivenState.reachedFinalGoal):
                status = "AT_GOAL"
            
            return ("<GOAL, st=%s, arvd=%s, ctdn=%i>" % 
                    (status, "Y" if self.didArriveAtBasePyramid else "N", self.goalChaseCountdown))
    
    ## END OF NESTED CLASS _BoidGoalDrivenState
    #################################

    
    def __init__(self, basePos, lipPos, finalPos, normalBehaviourInstance, useInfectionSpread, bDelegate=None):
        """basePos, lipPos and finalPos must be Pymel Locator instances.
        normalBehaviourInstance = BoidBehaviourClassicBoid instance.
        """
        super(GoalDriven, self).__init__(bDelegate)
        
        self._baseVector = util.BoidVector3FromPymelLocator(basePos)
        self._baseLocator = None
        if(not(type(basePos) == bv3.Vector3)):
            self._baseLocator = basePos
            
        self._lipVector = util.BoidVector3FromPymelLocator(lipPos)
        self._lipLocator = None
        if(not(type(lipPos) == bv3.Vector3)):
            self._lipLocator = lipPos
            
        self._finalVector = util.BoidVector3FromPymelLocator(finalPos)
        self._finalLocator = None
        if(not(type(finalPos) == bv3.Vector3)):
            self._finalLocator = finalPos
        
        self._baseToFinalDirection = bv3.Vector3() # direction vector from baseLocator to finalLocator
        
        self._leaders = []
        self._basePyramidDistanceLookup = {}
        
        self._normalBehaviour = normalBehaviourInstance
        self.useInfectionSpread = useInfectionSpread
        
        # variables in the following block relate to agent's distance
        # from the baseLocator when in the basePyramid
        self._agentPyramidEntryThreshold = boidAttributes.goalTargetDistanceThreshold()
        self._agentDistance_runningTotal = bv2.Vector2()
        self._agentDistance_average = bv2.Vector2()
        self._needsAverageDistanceCalc = False
        self._maxAgentDistance = bv2.Vector2()
        
        # variables here relate to average position taken from within
        # the basePyramid.
        self._agentPosition_runningTotal = bv3.Vector3()
        self._agentPosition_average = bv3.Vector3()
        self._needsAveragePositionCalc = False
        
        self._performCollapse = False
        
#######################        
    def __str__(self):            
        return ("GOAL - pos=%s, lip=%s, final=%s, infect=%s" % 
                (self._baseVector, self._lipVector, self._finalVector, "Y" if self.useInfectionSpread else "N"))
    
#######################
    def _getMetaStr(self):
        leaderStringsList = [("%d," % agent.particleId) for agent in self._leaders]
        pyramidStringsList = [("\t%s\n" % agent) for agent in self._basePyramidDistanceLookup]
        
        return ("<ldrs=%s, avDist=%s, maxDist=%s, avPos=%s\natLoctn=\n%s\natLip=\n%s\nover=\n%s>" % 
                ("".join(leaderStringsList),
                 self._basePyramidAverageDistance(), self._maxAgentDistance, self._basePyramidAveragePosition(), 
                 ''.join(pyramidStringsList)))#, ''.join(atLipStringsList), ''.join(overStringsList)))
        
####################### 
    def makeLeader(self, agent):
        if(not agent in self._leaders):
            self._leaders.append(agent)
            self._setGoalStatusForAgent(agent, GoalDriven._BoidGoalDrivenState.goalChase)
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
        return GoalDriven._BoidGoalDrivenState(self.useInfectionSpread)
            
#######################        
    def onFrameUpdate(self):  # overridden BoidBehaviourBaseObject method
        """Lists of agents must be rebuild on every frame, this method clears the lists
        and sets up everything for a new frame."""
        
        self._agentPyramidEntryThreshold = max((boidAttributes.goalTargetDistanceThreshold(), 
                                                self._maxAgentDistance.u))
        self._agentPosition_runningTotal.reset()
        self._needsAveragePositionCalc = True
        self._agentDistance_runningTotal.reset()
        self._needsAverageDistanceCalc = True
        self._maxAgentDistance.reset()
        self._basePyramidDistanceLookup.clear()
        
        # now, re-check Maya objects in case they've moved within the scene...
        if(self._baseLocator is not None):
            self._baseVector = util.BoidVector3FromPymelLocator(self._baseLocator)
        if(self._lipLocator is not None):
            self._lipVector = util.BoidVector3FromPymelLocator(self._lipLocator)        
        if(self._finalLocator is not None):
            self._finalLocator = util.BoidVector3FromPymelLocator(self._finalLocator)   
        self._baseToFinalDirection = self._finalVector - self._baseVector

#######################
    def checkAgentLocation(self, agent):
        """Checks current location of agent to determine appropriate list it should be put
        into (which then determines corresponding behaviour).
        """
        baseToAgentVec = agent.currentPosition - self._baseVector
        
        newStatus = self._goalStatusForAgent(agent)
        
        if(abs(self._baseToFinalDirection.angleFrom(baseToAgentVec)) < 90):
            # boid agent has cleared the wall...
            if(self._baseToFinalDirection.magnitudeSquared(True) < baseToAgentVec.magnitudeSquared(True)):
                # reached final goal
                newStatus = GoalDriven._BoidGoalDrivenState.reachedFinalGoal
            else:
                # still on top of wall moving towards final goal
                newStatus = GoalDriven._BoidGoalDrivenState.overWallLip
        else:
            if(agent.currentPosition.y >= (self._lipVector.y - 0.1)): # TODO - make this check more robust.
                # agent has reached top of the wall, now will move twds final goal
                newStatus = GoalDriven._BoidGoalDrivenState.atWallLip
            elif(baseToAgentVec.magnitudeSquared(True) < self._agentPyramidEntryThreshold **2):
                # agent is close enough to be considered as being at the basePyramid
                newStatus = GoalDriven._BoidGoalDrivenState.inBasePyramid
            elif(self._goalStatusForAgent(agent) >= GoalDriven._BoidGoalDrivenState.inBasePyramid):
                # agent is still some distance away is will simply chase the baseLocator/leader for now
                newStatus = GoalDriven._BoidGoalDrivenState.goalChase
                
                behaviourStatus = agent.state.behaviourSpecificState
                if(behaviourStatus.didArriveAtBasePyramid and 
                   baseToAgentVec.magnitude() > boidAttributes.mainRegionSize()):
                    # if miles away, may as well just start over afresh
                    behaviourStatus.didArriveAtBasePyramid = False
                
        self._setGoalStatusForAgent(agent, newStatus, baseToAgentVec)
        

#######################
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):  # overridden BoidBehaviourBaseObject method
        """Returns corresponding acceleration for the agent as determined by calculated behaviour.
        Client agents should call this method on each frame update and modify their own desiredAcceleration accordingly."""
        
        desiredAcceleration = bv3.Vector3()
        agent.stickinessScale = 0 # reset on each frame, as may have been set on previous iteration

        if(agent.isTouchingGround):
            if(self._overWallLipBehaviour(agent, desiredAcceleration)):
                return desiredAcceleration
            elif(self._atWallLipBehaviour(agent, desiredAcceleration)):
                return desiredAcceleration
            elif(self._inBasePyramidBehaviour(agent, desiredAcceleration)):
                return desiredAcceleration
            else:
                agent.state.updateRegionalStatsIfNecessary(agent, nearbyAgentsList,
                                                           boidAttributes.mainRegionSize(),
                                                           boidAttributes.nearRegionSize(),
                                                           boidAttributes.collisionRegionSize(),
                                                           boidAttributes.blindRegionAngle(),
                                                           boidAttributes.forwardVisionRegionAngle())
                
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
        if(self._goalStatusForAgent(agent) == GoalDriven._BoidGoalDrivenState.overWallLip or 
           self._goalStatusForAgent(agent) == GoalDriven._BoidGoalDrivenState.reachedFinalGoal):
            
            targetVelocity = bv3.Vector3(self._baseToFinalDirection.x, 0, self._baseToFinalDirection.z)
            targetVelocity.normalise(boidAttributes.goalChaseSpeed())
            desiredAcceleration.resetVec(targetVelocity - agent.currentVelocity)
            if(desiredAcceleration.magnitude() > boidAttributes.maxAccel()):
                desiredAcceleration.normalise(boidAttributes.maxAccel())
            
            return True
        else:
            return False

#######################        
    def _atWallLipBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == GoalDriven._BoidGoalDrivenState.atWallLip):
            desiredAcceleration.x = self._baseToFinalDirection.x
            desiredAcceleration.z = self._baseToFinalDirection.z
            desiredAcceleration.normalise(boidAttributes.goalChaseSpeed()) # TODO - misleading place to use goalChaseSpeed, should use something else??
            desiredAcceleration.y = self._basePyramidPushUpwardsMagnitudeVertical()
            
            return True
        else:
            return False

#######################
    def _inBasePyramidBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == GoalDriven._BoidGoalDrivenState.inBasePyramid):        
            directionToGoal = self._baseVector - agent.currentPosition
            horizontalComponent = directionToGoal.horizontalVector()
            horizontalComponent.normalise(self._basePyramidPushUpwardsMagnitudeHorizontal())
            
            distance = self._basePyramidDistanceLookup[agent]
            if(distance < self._basePyramidAverageDistance()):
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
        if(self._goalStatusForAgent(agent) == GoalDriven._BoidGoalDrivenState.goalChase and agent.isCrowded):
            goalThresholdDistanceSquared = boidAttributes.goalTargetDistanceThreshold() **2
            goalChaseSpeedSquared = boidAttributes.goalChaseSpeed() **2
            
            for nearbyAgent in agent.state.crowdedList:
                # as the basePyramid grows in size, it's perceived 'boundary' (i.e. the position at which agents are said 
                # to have joined the pyramid and can start their 'climbing' behaviour) is not fixed. So to determine it, we
                # look at other agents in the immediate vicinity and see if they themselves are in the pyramid.
                if(self._goalStatusForAgent(nearbyAgent) == GoalDriven._BoidGoalDrivenState.inBasePyramid and 
                   (nearbyAgent.currentPosition.distanceSquaredFrom(agent.currentPosition) < goalThresholdDistanceSquared) and
                   (nearbyAgent.currentVelocity.magnitudeSquared(True) < goalChaseSpeedSquared or 
                    agent.currentVelocity.magnitudeSquared(True) < goalChaseSpeedSquared or 
                    abs(nearbyAgent.currentVelocity.angleFrom(agent.currentVelocity)) > 90) ):
                    # TODO - just expand the goal's radius here...
                    self._registerAgentAtBasePyramid(agent)
                    return self._goalChaseBehaviour(agent, desiredAcceleration)
        return False
    
#######################  
    def _goalChaseBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == GoalDriven._BoidGoalDrivenState.goalChase):
            directionVec = self._goalChaseAttractorPositionForAgent(agent) - agent.currentPosition
            directionVec.normalise(boidAttributes.maxAccel())
            desiredAcceleration.resetVec(directionVec)      
            
            # push away from nearby agents??
            currentState = agent.state.behaviourSpecificState
            if(not currentState.didArriveAtBasePyramid and agent.isCrowded):   # note that we move AWAY from the avPos here
                differenceVector = agent.currentPosition - agent.state.avCrowdedPosition
                differenceVector.normalise(boidAttributes.maxAccel()) # TODO - dodgy algorithm here??
                desiredAcceleration.add(differenceVector)    
            elif(currentState.didArriveAtBasePyramid):
                # Agents in a basePyramid sometimes get pushed to the corners and get
                # stuck there, which is not desirable. This corrects that behaviour.
                angle = abs(directionVec.angleFrom(self._baseToFinalDirection))
                if(angle > 82):
                    desiredAcceleration.subtract(self._baseToFinalDirection, True)
                    
            self._clampDesiredAccelerationIfNecessary(agent, 
                                                     desiredAcceleration, 
                                                     boidAttributes.maxAccel(), 
                                                     boidAttributes.goalChaseSpeed())
            return True
        else:
            return False
 
#######################   
    def _decrementGoalChaseCountdownIfNecessary(self, agent):
        if(self._goalStatusForAgent(agent) == GoalDriven._BoidGoalDrivenState.pending):
            agent.state.behaviourSpecificState.goalChaseCountdown -= 1
            if(agent.state.behaviourSpecificState.goalChaseCountdown <= 0):
                self._setGoalStatusForAgent(agent, GoalDriven._BoidGoalDrivenState.goalChase)
                return True

        return False

    def _startGoalChaseCountdownIfNecessary(self, agent):
        if(self._goalStatusForAgent(agent) == GoalDriven._BoidGoalDrivenState.normal):
            nearestNeighbour = None
            nearestNeighbourDistanceSquared = float('inf')                    
            for nearbyAgent in agent.state.nearbyList:
                if(nearbyAgent._currentBehaviour is self):
                    distance = agent.currentPosition - nearbyAgent.currentPosition
                    if(distance.magnitudeSquared() < nearestNeighbourDistanceSquared):
                        nearestNeighbour = nearbyAgent
                        nearestNeighbourDistanceSquared = distance.magnitudeSquared()
                        
            if(nearestNeighbour is not None and # TODO - this check could also be against == state.pending...??
               self._goalStatusForAgent(nearbyAgent) >= GoalDriven._BoidGoalDrivenState.goalChase):
                self._setGoalStatusForAgent(agent, GoalDriven._BoidGoalDrivenState.pending)
                return True
            
        return False

#######################
    def _registerAgentAtBasePyramid(self, agent, distanceVector=None):
        """Registers agent as having arrived at the basePyramid, behaviour
        for the agent will be switched from 'goalChase' to basePyramid 'push-up' behaviour.
        """
        if(not agent in self._basePyramidDistanceLookup):
            
            if(distanceVector is None):
                distanceVector = agent.currentPosition - self._baseVector
            self._agentDistance_runningTotal.u += distanceVector.magnitude(True)
            self._agentDistance_runningTotal.v += distanceVector.y
            self._needsAverageDistanceCalc = True         
            
            if(distanceVector.magnitude(True) > self._maxAgentDistance.u):
                self._maxAgentDistance.u = distanceVector.magnitude(True)
            if(distanceVector.y > self._maxAgentDistance.v):
                self._maxAgentDistance.v = distanceVector.y
            
            self._agentPosition_runningTotal.add(agent.currentPosition)
            self._needsAveragePositionCalc = True   
            
            self._basePyramidDistanceLookup[agent] = distanceVector
          
#######################        
    def _deRegisterAgentFromBasePyramid(self, agent):
        """Should be called when agent leaves/falls out of basePyramid, switches out
        of 'push-up' behaviour
        """
        if(agent in self._basePyramidDistanceLookup):            
            distanceVec = agent.currentPosition - self._baseVector
            self._agentDistance_runningTotal.u -= distanceVec.magnitude(True)
            self._agentDistance_runningTotal.v -= distanceVec.y
            self._needsAverageDistanceCalc = True  
            
            self._agentPosition_runningTotal.subtract(agent.currentPosition)
            self._needsAveragePositionCalc = True       
            
            del self._basePyramidDistanceLookup[agent]

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
        return boidAttributes.pushUpwardsAccelerationHorizontal()
        #return self._pushUpwardsVector.v
    
    def _basePyramidPushUpwardsMagnitudeVertical(self):
        """Acceleration applied by each boid in the vertical direction (towards 
        the lipLocator) after having joined the basePyramid."""
        return boidAttributes.pushUpwardsAccelerationVertical()
        #return self._pushUpwardsVector.u
        
#######################
    def _goalChaseAttractorPositionForAgent(self, agent):
        """Returns position (Vector3) towards which the boidAgent should be made to move
        towards (when following goalChase behaviour)."""
        
        returnValue = None
        numLeaders = len(self._leaders)

        if(agent.state.behaviourSpecificState.didArriveAtBasePyramid or 
           numLeaders == 0 or self.agentIsLeader(agent)):
            returnValue = self._baseVector
        elif(numLeaders == 1):
            returnValue = self._leaders[0].currentPosition
        else:
            candidateLeader = None
            minDistanceSquared = agent.currentPosition.distanceSquaredFrom(self._baseVector)
            for leader in self._leaders:
                candidateDistanceSquared = agent.currentPosition.distanceSquaredFrom(leader.currentPosition)
                if(candidateDistanceSquared < minDistanceSquared):
                    minDistanceSquared = candidateDistanceSquared
                    candidateLeader = leader
            
            if(candidateLeader is not None):
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
        
        if(distance > boidAttributes.goalTargetDistanceThreshold() and
           distance < boidAttributes.goalTargetDistanceThreshold() + boidAttributes.jumpOnPyramidDistanceThreshold() and 
           random.uniform(0, 1.0) < boidAttributes.jumpOnPyramidProbability()):
            return True
        else:
            return False

#######################        
    def _goalStatusForAgent(self, agent):
        if(AgentBehaviourIsGoalDriven(agent)):
            return agent.state.behaviourSpecificState.currentStatus
        else:
            raise TypeError
            return GoalDriven._BoidGoalDrivenState._invalid
    
    def _setGoalStatusForAgent(self, agent, status, distanceVector=None):
        if(status != self._goalStatusForAgent(agent)):
            agent.state.behaviourSpecificState.currentStatus = status
            
            if(status == GoalDriven._BoidGoalDrivenState.pending):
                agent.state.behaviourSpecificState.goalChaseCountdown = boidAttributes.goalIncubationPeriod()
            else:
                if(status >= GoalDriven._BoidGoalDrivenState.inBasePyramid):
                    if(agent in self._leaders):
                        self._leaders.remove(agent)
                    if(status == GoalDriven._BoidGoalDrivenState.reachedFinalGoal):
                        self._notifyDelegateBehaviourEndedForAgent(agent)
                    agent.state.behaviourSpecificState.didArriveAtBasePyramid = True
                agent.state.behaviourSpecificState.goalChaseCountdown = -1
                
        if(status == GoalDriven._BoidGoalDrivenState.inBasePyramid):
            self._registerAgentAtBasePyramid(agent, distanceVector)
        else:
            self._deRegisterAgentFromBasePyramid(agent)
        
        
# END OF CLASS - BoidBehaviourGoalDriven
#######################


    
        