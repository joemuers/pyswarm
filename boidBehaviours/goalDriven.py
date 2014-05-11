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


from behaviourBaseObject import BehaviourBaseObject
from resources import colours

import attributes.goalDrivenBehaviourAttributes as gdba
import boidVectors.vector2 as bv2
import boidVectors.vector3 as bv3

import random



#######################
def AgentBehaviourIsGoalDriven(agent):
    return (type(agent.state.behaviourAttributes) == gdba.GoalDrivenDataBlob)

#######################
def AgentIsChasingGoal(agent):
    return (AgentBehaviourIsGoalDriven(agent) and 
            agent.state.behaviourAttributes.currentStatus == gdba.GoalDrivenDataBlob.goalChase)

#######################
def AgentIsInBasePyramid(agent):
    return (AgentBehaviourIsGoalDriven(agent) and 
            agent.state.behaviourAttributes.currentStatus == gdba.GoalDrivenDataBlob.inBasePyramid)

#######################    
def AttributesAreGoalDriven(attributes):
    return (isinstance(attributes, gdba.GoalDrivenBehaviourAttributes))

#######################



#################################
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
    
    
    def __init__(self, goalDrivenAttributes, normalBehaviourInstance, delegate=None):
        """basePos, lipPos and finalPos must be Pymel Locator instances.
        normalBehaviourInstance = BoidBehaviourClassicBoid instance.
        """
        super(GoalDriven, self).__init__(goalDrivenAttributes, delegate)
        
        self._baseToFinalDirection = bv3.Vector3() # direction vector from baseLocator to finalLocator
        
        self._leaderPositions = []
        self._basePyramidDistanceLookup = {}
        
        self._normalBehaviour = normalBehaviourInstance
        
        # variables in the following block relate to agent's distance
        # from the baseLocator when in the basePyramid
        self._agentDistance_runningTotal = bv2.Vector2()
        self._agentDistance_average = bv2.Vector2()
        self._needsAverageDistanceCalc = False
        self._maxAgentDistance = bv2.Vector2()
        
        # variables here relate to average position taken from within
        # the basePyramid.
        self._agentPosition_runningTotal = bv3.Vector3()
        self._agentPosition_average = bv3.Vector3()
        self._needsAveragePositionCalc = False
        
        self._infectionSpreadMode = False
        self._performInfectionSpreadReset = True
        self._performCollapse = False
        
#######################        
    def __str__(self):            
        return ("<%s - pos=%s, lip=%s, final=%s, base->final=%s, infect=%s>" % 
                (super(GoalDriven, self).__str__(),
                 self.attributes.basePyramidGoal, 
                 self.attributes.wallLipGoal, 
                 self.attributes.finalGoal, 
                 self._baseToFinalDirection,
                 "Y" if self.attributes.useInfectionSpread else "N"))

#########    
    def _getMetaStr(self):
        leadersString = ', '.join([("%d" % agentId) for agentId in self.attributes.allLeaderIds])
        pyramidString = ''.join([("\t%s\n" % agent) for agent in self._basePyramidDistanceLookup])
        
        return ("<ldrs=%s, avDist=%s, maxDist=%s, avPos=%s\natLoctn=\n%s>" % 
                (leadersString,
                 self._basePyramidAverageDistance(), self._maxAgentDistance, self._basePyramidAveragePosition(), 
                 pyramidString))#, ''.join(atLipStringsList), ''.join(overStringsList)))
        
#######################        
    def onFrameUpdated(self):  # overridden BoidBehaviourBaseObject method
        """Lists of agents must be rebuild on every frame, this method clears the lists
        and sets up everything for a new frame."""
        
        if(self.attributes.useInfectionSpread):
            self._performInfectionSpreadReset = not self._infectionSpreadMode
            self._infectionSpreadMode = True
        else:
            self._infectionSpreadMode = False
            
        del self._leaderPositions[:]
        self._agentPosition_runningTotal.reset()
        self._needsAveragePositionCalc = True
        self._agentDistance_runningTotal.reset()
        self._needsAverageDistanceCalc = True
        self._maxAgentDistance.reset()
        self._basePyramidDistanceLookup.clear()
        
        # now, re-check goal location in case it's moved within the scene...  
        self._baseToFinalDirection = self.attributes.finalGoal - self.attributes.basePyramidGoal

#######################
    def onAgentUpdated(self, agent):
        """Checks current location of agent to determine appropriate list it should be put
        into (which then determines corresponding behaviour).
        """
        self._normalBehaviour.onAgentUpdated(agent)
        
        baseToAgentVec = agent.currentPosition - self.attributes.basePyramidGoal
        agentAttributes = agent.state.behaviourAttributes
        agentStatus = self._effectiveGoalStatusForAgent(agent)
        
        if(abs(self._baseToFinalDirection.angleTo(baseToAgentVec)) < 90):
            # boid agent has cleared the wall...
            if(self._baseToFinalDirection.magnitudeSquared(True) < baseToAgentVec.magnitudeSquared(True)):
                # reached final goal
                agentStatus = gdba.GoalDrivenDataBlob.reachedFinalGoal
            else:
                # still on top of wall moving towards final goal
                agentStatus = gdba.GoalDrivenDataBlob.overWallLip
        else:
            if(agent.currentPosition.y >= (self.attributes.wallLipGoal.y - 0.1)): # TODO - make this check more robust.
                # agent has reached top of the wall, now will move twds final goal
                agentStatus = gdba.GoalDrivenDataBlob.atWallLip
            elif(baseToAgentVec.magnitudeSquared(True) < agentAttributes.pyramidJoinAtDistance **2):
                # agent is close enough to be considered as being at the basePyramid
                agentStatus = gdba.GoalDrivenDataBlob.inBasePyramid
            else:
                # agent is still some distance away & will simply chase the baseLocator/leader for now
                
                if(agentAttributes.didArriveAtBasePyramid and 
                   agent.state.perceptionAttributes.neighbourhoodSize < baseToAgentVec.magnitude()):
                    # if miles away, may as well just start over afresh
                    agentAttributes.didArriveAtBasePyramid = False
                
                if(not agentAttributes.didArriveAtBasePyramid):
                    if(self._infectionSpreadMode and self.attributes.agentIsLeader(agent.agentId)):
                        # agent has been designated as a leader
                        self._leaderPositions.append(agent.currentPosition)
                        agentStatus = gdba.GoalDrivenDataBlob.goalChase
                    elif(agentStatus == gdba.GoalDrivenDataBlob._uninitialised):
                        # newly assigned/reset agent => initialise accordingly
                        if(self._infectionSpreadMode): agentStatus = gdba.GoalDrivenDataBlob.normal
                        else: agentStatus = gdba.GoalDrivenDataBlob.goalChase
                    elif(agentStatus == gdba.GoalDrivenDataBlob.pending):
                        # agent has been 'infected' - check the countdown
                        agentAttributes.goalChaseCountdown -= 1
                        if(agentAttributes.goalChaseCountdown < 0):
                            agentStatus = gdba.GoalDrivenDataBlob.goalChase
                    else:
                        agentStatus = gdba.GoalDrivenDataBlob.goalChase
                elif(agentStatus > gdba.GoalDrivenDataBlob.inBasePyramid):
                    agentStatus = gdba.GoalDrivenDataBlob.goalChase
                    
        self._setGoalStatusForAgent(agent, agentStatus, baseToAgentVec)
        self._setDebugColourForAgent(agent)

#######################
    def getDesiredAccelerationForAgent(self, agent, nearbyAgentsList):  # overridden BoidBehaviourBaseObject method
        """Returns corresponding acceleration for the agent as determined by calculated behaviour.
        Client agents should call this method on each frame update and modify their own desiredAcceleration accordingly.
        """
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
                agent.state.updateRegionalStatsIfNecessary(agent, nearbyAgentsList)
                
                if(not self._performCollapse and self._atBasePyramidBorderBehaviour(agent, desiredAcceleration)):
                    return desiredAcceleration
                elif(self._goalChaseBehaviour(agent, desiredAcceleration)):
                    return desiredAcceleration
                else:
                    self._startGoalChaseCountdownIfNecessary(agent)
                    return self._normalBehaviour.getCompoundDesiredAcceleration(agent, nearbyAgentsList)
                
        return desiredAcceleration

#######################
    def _overWallLipBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == gdba.GoalDrivenDataBlob.overWallLip or 
           self._goalStatusForAgent(agent) == gdba.GoalDrivenDataBlob.reachedFinalGoal):
            
            targetVelocity = bv3.Vector3(self._baseToFinalDirection.x, 0, self._baseToFinalDirection.z)
            targetVelocity.normalise(agent.state.behaviourAttributes.goalChaseSpeed)
            desiredAcceleration.resetToVector(targetVelocity - agent.currentVelocity)
            if(desiredAcceleration.magnitude() > agent.state.movementAttributes.maxAcceleration):
                desiredAcceleration.normalise(agent.state.movementAttributes.maxAcceleration)
            
            return True
        else:
            return False

#######################        
    def _atWallLipBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == gdba.GoalDrivenDataBlob.atWallLip):
            desiredAcceleration.x = self._baseToFinalDirection.x
            desiredAcceleration.z = self._baseToFinalDirection.z
            desiredAcceleration.normalise(agent.state.behaviourAttributes.goalChaseSpeed) # TODO - misleading place to use goalChaseSpeed, should use something else??
            desiredAcceleration.y = self._basePyramidPushUpwardsMagnitudeVertical()
            
            return True
        else:
            return False

#######################
    def _inBasePyramidBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == gdba.GoalDrivenDataBlob.inBasePyramid):        
            directionToGoal = self.attributes.basePyramidGoal - agent.currentPosition
            horizontalComponent = directionToGoal.horizontalVector()
            horizontalComponent.normalise(self._basePyramidPushUpwardsMagnitudeHorizontal())
            
            desiredAcceleration.x = horizontalComponent.u
            desiredAcceleration.z = horizontalComponent.v
            
            if(not self._performCollapse):
                desiredAcceleration.y = self._basePyramidPushUpwardsMagnitudeVertical()
                
                distance = self._basePyramidDistanceLookup[agent]
                if(distance < self._basePyramidAverageDistance()):
                    diff = self._basePyramidAverageDistance().magnitude() - distance.magnitude()
                    proportion = diff / self._basePyramidAverageDistance().magnitude()
                    stickinessValue = 2 * proportion
                    agent.stickinessScale = stickinessValue
            else:
                desiredAcceleration.invert()
            
            return True
        else:
            return False
        
#######################
    def _atBasePyramidBorderBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == gdba.GoalDrivenDataBlob.goalChase and agent.isCrowded):
            joinPyramidDistanceSquared = agent.state.behaviourAttributes.pyramidJoinAtDistance **2
            goalChaseSpeedSquared = agent.state.behaviourAttributes.goalChaseSpeed **2
            
            for nearbyAgent in agent.state.crowdedList:
                # as the basePyramid grows in size, it's perceived 'boundary' (i.e. the position at which agents are said 
                # to have joined the pyramid and can start their 'climbing' behaviour) is not fixed. So to determine it, we
                # look at other agents in the immediate vicinity and see if they themselves are in the pyramid.
                if(self._goalStatusForAgent(nearbyAgent) == gdba.GoalDrivenDataBlob.inBasePyramid and 
                   (nearbyAgent.currentPosition.distanceSquaredFrom(agent.currentPosition) < joinPyramidDistanceSquared) and
                   (nearbyAgent.currentVelocity.magnitudeSquared(True) < goalChaseSpeedSquared or # TODO - should comp-to nearbyAgent's *own* GC speed..
                    agent.currentVelocity.magnitudeSquared(True) < goalChaseSpeedSquared or 
                    abs(nearbyAgent.currentVelocity.angleTo(agent.currentVelocity)) > 90) ):
                    # TODO - just expand the goal's radius here...
                    # play around with this algorithm if agents get added in a strange manner...
                    returnVal = self._goalChaseBehaviour(agent, desiredAcceleration) 
                    self._setGoalStatusForAgent(agent, gdba.GoalDrivenDataBlob.inBasePyramid)
                    
                    return returnVal
        return False
    
#######################  
    def _goalChaseBehaviour(self, agent, desiredAcceleration):
        if(self._goalStatusForAgent(agent) == gdba.GoalDrivenDataBlob.goalChase):
            maxAcceleration = agent.state.movementAttributes.maxAcceleration
            directionVec = self._goalChaseAttractorPositionForAgent(agent) - agent.currentPosition
            directionVec.normalise(maxAcceleration)
            desiredAcceleration.resetToVector(directionVec)      
            
            # push away from nearby agents??
            behaviourAttributes = agent.state.behaviourAttributes
            if(not behaviourAttributes.didArriveAtBasePyramid and agent.isCrowded):   # note that we move AWAY from the avPos here
                differenceVector = agent.currentPosition - agent.state.avCrowdedPosition
                differenceVector.normalise(maxAcceleration) # TODO - dodgy algorithm here??
                desiredAcceleration.add(differenceVector)    
            elif(behaviourAttributes.didArriveAtBasePyramid):
                # Agents in a basePyramid sometimes get pushed to the corners and get
                # stuck there, which is not desirable. This corrects that behaviour.
                angle = abs(directionVec.angleTo(self._baseToFinalDirection))
                if(angle > 82):
                    desiredAcceleration.subtract(self._baseToFinalDirection, True)
                    
            self._clampDesiredAccelerationIfNecessary(agent, 
                                                      desiredAcceleration, 
                                                      maxAcceleration, 
                                                      behaviourAttributes.goalChaseSpeed)
            return True
        else:
            return False

########
    def _startGoalChaseCountdownIfNecessary(self, agent):
        if(self._goalStatusForAgent(agent) == gdba.GoalDrivenDataBlob.normal):
            nearestNeighbour = None
            nearestNeighbourDistanceSquared = float('inf')                    
            for nearbyAgent in agent.state.nearbyList:
                if(nearbyAgent.currentBehaviour is self):
                    distance = agent.currentPosition - nearbyAgent.currentPosition
                    if(distance.magnitudeSquared() < nearestNeighbourDistanceSquared):
                        nearestNeighbour = nearbyAgent
                        nearestNeighbourDistanceSquared = distance.magnitudeSquared()
                        
            if(nearestNeighbour is not None and # TODO - this check could also be against == state.pending...??
               self._goalStatusForAgent(nearbyAgent) >= gdba.GoalDrivenDataBlob.goalChase):
                self._setGoalStatusForAgent(agent, gdba.GoalDrivenDataBlob.pending)
                return True
            
        return False

#######################
    def _registerAgentAtBasePyramid(self, agent, distanceVector=None):
        """Registers agent as having arrived at the basePyramid, behaviour
        for the agent will be switched from 'goalChase' to basePyramid 'push-up' behaviour.
        """
        if(not agent in self._basePyramidDistanceLookup):
            
            if(distanceVector is None):
                distanceVector = agent.currentPosition - self.attributes.basePyramidGoal
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
          
#########
    def _deRegisterAgentFromBasePyramid(self, agent):
        """Should be called when agent leaves/falls out of basePyramid, switches out
        of 'push-up' behaviour
        """
        if(agent in self._basePyramidDistanceLookup):            
            distanceVec = agent.currentPosition - self.attributes.basePyramidGoal
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
            self._agentDistance_average.resetToVector(self._agentDistance_runningTotal)
            self._agentDistance_average.divide(len(self._basePyramidDistanceLookup))
            self._needsAverageDistanceCalc = False
        return self._agentDistance_average

#########     
    def _basePyramidAveragePosition(self):
        """Average position of agents in the basePyramid."""        
        if(self._needsAveragePositionCalc and len(self._basePyramidDistanceLookup) > 0):
            self._agentPosition_average.resetToVector(self._agentPosition_runningTotal)
            self._agentPosition_average.divide(len(self._basePyramidDistanceLookup))
            self._needsAveragePositionCalc = False
        return self._agentPosition_average

######### 
    def _basePyramidMaxDistanceHorizontal(self):
        """Current largest (scalar) horizontal distance of an agent, within the basePyramid, from the baseLocator."""
        return self._maxAgentDistance.u

#########     
    def _basePyramidMaxDistanceVertical(self):
        """Current largest (scalar) vertical distance of an agent, within the basePyramid, from the baseLocator."""
        return self._maxAgentDistance.v

#########     
    def _basePyramidPushUpwardsMagnitudeHorizontal(self):
        """Acceleration applied by each boid in the horizontal direction (towards 
        the baseLocator) after having joined the basePyramid."""
        return self.attributes.basePyramidPushInwardsForce

#########     
    def _basePyramidPushUpwardsMagnitudeVertical(self):
        """Acceleration applied by each boid in the vertical direction (towards 
        the lipLocator) after having joined the basePyramid."""
        return self.attributes.basePyramidPushUpwardsForce
        
#######################
    def _goalChaseAttractorPositionForAgent(self, agent):
        """Returns position (Vector3) towards which the boidAgent should be made to move
        towards (when following goalChase behaviour)."""
        
        returnValue = None
        numLeaders = self.attributes.numberOfLeaders

        if(agent.state.behaviourAttributes.didArriveAtBasePyramid or 
           numLeaders == 0 or self.attributes.agentIsLeader(agent.agentId)):
            returnValue = self.attributes.basePyramidGoal
        elif(numLeaders == 1):
            returnValue = self._leaderPositions[0]
        else:
            candidateLeaderPosition = None
            minDistanceSquared = agent.currentPosition.distanceSquaredFrom(self.attributes.basePyramidGoal)
            for leaderPosition in self._leaderPositions:
                candidateDistanceSquared = agent.currentPosition.distanceSquaredFrom(leaderPosition)
                if(candidateDistanceSquared < minDistanceSquared):
                    minDistanceSquared = candidateDistanceSquared
                    candidateLeaderPosition = leaderPosition
            
            if(candidateLeaderPosition is not None):
                returnValue = candidateLeaderPosition
            else:
                returnValue = self.attributes.basePyramidGoal
                
        if(self._performCollapse):
            returnValue.invert()        
        
        return returnValue
    
#######################
    def _getShouldJump(self, agent):
        """Returns True if agent should jump up onto basePyramid, False otherwise."""
        
        distanceVec = agent.currentPosition - self.attributes.basePyramidGoal
        distance = distanceVec.magnitude(True)
        behaviourAttributes = agent.state.behaviourAttributes
        
        if(distance > behaviourAttributes.pyramidJoinAtDistance and # TODO - should add the distances here?? or not??
           distance < behaviourAttributes.pyramidJoinAtDistance + behaviourAttributes.pyramidJumpOnDistance and 
           random.uniform(0, 1.0) < self.attributes.pyramidJumpOnProbability):
            return True
        else:
            return False

#######################        
    def _goalStatusForAgent(self, agent):
        return agent.state.behaviourAttributes.currentStatus
    
########
    def _effectiveGoalStatusForAgent(self, agent):
        if(AgentBehaviourIsGoalDriven(agent)):
            currentStatus = agent.state.behaviourAttributes.currentStatus
            
            if(self._infectionSpreadMode):
                if(self._performInfectionSpreadReset and currentStatus <= gdba.GoalDrivenDataBlob.goalChase):
                    return gdba.GoalDrivenDataBlob._uninitialised
                else:
                    return currentStatus
            else:
                if(currentStatus < gdba.GoalDrivenDataBlob.goalChase): 
                    return gdba.GoalDrivenDataBlob._uninitialised
                else:
                    return currentStatus
        else:
            raise RuntimeError(("Agent %d is following behaviour %s" % (agent.agentId, agent.currentBehaviour.behaviourId)))
            return gdba.GoalDrivenDataBlob._uninitialised

#######################    
    def _setGoalStatusForAgent(self, agent, newStatus, distanceVector=None):
        if(newStatus == gdba.GoalDrivenDataBlob._uninitialised):
            raise RuntimeError("Attempted to set agent behaviour status == uninitialised")
        
        agentAttributes = agent.state.behaviourAttributes
        
        if(newStatus != agentAttributes.currentStatus):
            agentAttributes.currentStatus = newStatus
            
            if(newStatus == gdba.GoalDrivenDataBlob.pending):
                agentAttributes.goalChaseCountdown = agentAttributes.incubationPeriod
            else:
                agentAttributes.goalChaseCountdown = -1
                if(newStatus >= gdba.GoalDrivenDataBlob.inBasePyramid):
                    agentAttributes.didArriveAtBasePyramid = True
                    if(newStatus == gdba.GoalDrivenDataBlob.reachedFinalGoal):
                        self._notifyDelegateBehaviourEndedForAgent(agent, self.attributes.followOnBehaviourID)
                
        if(newStatus == gdba.GoalDrivenDataBlob.inBasePyramid):
            self._registerAgentAtBasePyramid(agent, distanceVector)
        else:
            self._deRegisterAgentFromBasePyramid(agent)

#######################            
    def _setDebugColourForAgent(self, agent):
        if(not agent.isTouchingGround):
            agent.debugColour = colours.Normal_NotTouchingGround
        else:
            status = self._goalStatusForAgent(agent)
            
            if(status == gdba.GoalDrivenDataBlob.inBasePyramid):
                agent.debugColour = colours.GoalDriven_InBasePyramid(agent)
            elif(status == gdba.GoalDrivenDataBlob.goalChase):
                if(self.attributes.useInfectionSpread and self.attributes.agentIsLeader(agent.agentId)):
                    agent.debugColour =  colours.GoalDriven_IsLeader
                else:
                    agent.debugColour = colours.GoalDriven_ChasingGoal
            elif(status == gdba.GoalDrivenDataBlob.atWallLip or status == gdba.GoalDrivenDataBlob.overWallLip):
                agent.debugColour = colours.GoalDriven_OverTheWall
            elif(status == gdba.GoalDrivenDataBlob.reachedFinalGoal):
                agent.debugColour = colours.GoalDriven_ReachedGoal
            
#######################            
    def collapsePyramid(self, performIt=True):
        self._performCollapse = performIt
        
        
# END OF CLASS - BoidBehaviourGoalDriven
#######################


    
        