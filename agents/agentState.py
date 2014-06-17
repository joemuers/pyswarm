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


from pyswarm.pyswarmObject import PyswarmObject
import pyswarm.vectors.vector3 as v3
import pyswarm.utils.general as util



#############################################
class AgentState(PyswarmObject):
    """Internal to Agent, i.e. each Agent instance "has" an agentState member.  
    Essentially just a data container with information on the corresponding agent, regarding:
        - current position
        - current heading/acceleration
        - lists of other agents within the agent's neighbourhood, along with the 
          corresponding average position and heading of those nearby agents.
          
    Depending on their proximity, other agents within the neighbourhood are 
    "nearby" (simply within perceivable range), "crowded" (within close proximity) 
    or "collided" (so close as to be considered to have collided with this agent).
    
    Potentially confusing member variables:
        - "inFreefall" = True if agent is jumping/falling, ie not under normal locomotion, False otherwise.
    """
    
    def __init__(self, particleId, attributeGroupsController):
        self._agentId = int(particleId)
        self._position = v3.Vector3()
        self._velocity = v3.Vector3()
        self._acceleration = v3.Vector3()
        
        self._isInFreefall = True
        
        self._nearbyList = []        # 
        self._crowdedList = []       #
        self._collisionList = []     # lists of agent instances
        self._avPosition = v3.Vector3()
        self._avVelocity = v3.Vector3()
        self._avCrowdedPos = v3.Vector3()
        self._avCollisionDirection = v3.Vector3()    
        self._reciprocalNearbyChecks = set() 
        self._nearbyWeightedTotal = 0.0
        self._crowdingWeightedTotal = 0.0
        self._otherAgentWeightingLookup = {}
        
        self._framesUntilNextRebuild = 0
        self._needsFullListsRebuild = True 
        self._needsAveragesRecalc = False
        
        self._movementAttributes = attributeGroupsController.agentMovementAttributeGroup.getDataBlobForAgent(self)
        self._perceptionAttributes = attributeGroupsController.agentPerceptionAttributeGroup.getDataBlobForAgent(self)
        self._perceptionAttributeGroup = attributeGroupsController.agentPerceptionAttributeGroup
        self.behaviourAttributes = None  # data 'blob' for client behaviours to store instance-level data - not used internally
        self._globalAttributeGroup = attributeGroupsController.globalAttributeGroup
        
###################        
    def __str__(self):
        return ("id=%d, pos=%s, vel:(hdgH=%d, hdgV=%d, spd=%.2f), acln:(hdgH=%d, hdgV=%d, spd=%.2f), inFF=%s" % 
                (self._agentId, self._position, 
                 self._velocity.degreeHeading(), self._velocity.degreeHeadingVertical(), self._velocity.magnitude(),
                 self._acceleration.degreeHeading(), self._acceleration.degreeHeadingVertical(), self._acceleration.magnitude(),
                 "Y" if(self._isInFreefall) else "N"))
    
################### 
    def _getDebugStr(self):
        nearStringsList = [("%d," % nearbyAgent.agentId) for nearbyAgent in self.nearbyList]
        crowdStringsList = [("%d," % crowdingAgent.agentId) for crowdingAgent in self.crowdedList]
        collisionStringsList = [("%d," % collidingAgent.agentId) for collidingAgent in self.collisionList]
        
        return ("id=%d, avP=%s, avV=:(hdgH=%d, hdgV=%d, spd=%.2f), avCP=%s, nextRbld=%d\n\t\tbhvrAtrbts=%s, nr=%s, cr=%s, col=%s" % 
                (self._agentId, self._avPosition, 
                 self._avVelocity.degreeHeading(), self._avVelocity.degreeHeadingVertical(), self._avVelocity.magnitude(), 
                 self._avCrowdedPos, self._framesUntilNextRebuild, self.behaviourAttributes,
                 ''.join(nearStringsList), ''.join(crowdStringsList), ''.join(collisionStringsList)))       
    
#####################
    def _getAgentId(self):
        return self._agentId
    agentId = property(_getAgentId)

    def _getPosition(self):
        return self._position
    position = property(_getPosition)

    def _getVelocity(self):
        return self._velocity
    velocity = property(_getVelocity)

    def _getAcceleration(self):
        return self._acceleration
    acceleration = property(_getAcceleration)
    
    def _getIsInFreefall(self):
        """True if agent is jumping/falling & not under own locomotion, False otherwise."""
        return self._isInFreefall
    isInFreefall = property(_getIsInFreefall)   
    
    def _getAvPosition(self):
        return self._avPosition
    avPosition = property(_getAvPosition)
    
    def _getAvVelocity(self):
        return self._avVelocity
    avVelocity = property(_getAvVelocity)
    
    def _getAvCrowdedPosition(self):
        return self._avCrowdedPos
    avCrowdedPosition = property(_getAvCrowdedPosition)
    
    def _getHasNeighbours(self):
        if(self.nearbyList): return True
        else: return False
    hasNeighbours = property(_getHasNeighbours)
    
    def _getIsCrowded(self):
        if(self.crowdedList): return True
        else: return False
    isCrowded = property(_getIsCrowded)        
    
    def _getIsCollided(self):
        if(self.collisionList): return True
        else: return False
    isCollided = property(_getIsCollided)
    
    def _getAvCollisionDirection(self):
        return self._avCollisionDirection
    avCollisionDirection = property(_getAvCollisionDirection)   
    
    def _getNearbyList(self):
        return self._nearbyList
    nearbyList = property(_getNearbyList)
    
    def _getCrowdedList(self):
        return self._crowdedList
    crowdedList = property(_getCrowdedList)
    
    def _getCollisionList(self):
        return self._collisionList
    collisionList = property(_getCollisionList)
    
    def _getMovementAttributes(self):
        return self._movementAttributes
    movementAttributes = property(_getMovementAttributes)
    
    def _getPerceptionAttributes(self):
        return self._perceptionAttributes
    perceptionAttributes = property(_getPerceptionAttributes)
    
#####################           
    def updateCurrentVectors(self, position, velocity):
        """Updates internal state from corresponding vectors."""
        self._position.resetToVector(position)
        self._acceleration = velocity - self._velocity
        self._velocity.resetToVector(velocity)
        
#         if(self._globalAttributeGroup.movementIsThreeDimensional):
#             self._isInFreefall = False
#         el
        if(self._acceleration.y >= self._globalAttributeGroup.accelerationDueToGravity):
            self._isInFreefall = False
        else:
            self._isInFreefall = True
        
        self._onFrameUpdated()

#################################
    def withinCrudeRadiusOfPoint(self, otherPosition, radius):
        if(abs(self._position.x - otherPosition.x) > radius):   # Crude check intended to cut down 
            return False                                        # on the number of calls to vector3.distanceFrom
        elif(abs(self._position.z - otherPosition.z) > radius): # in the 'Precise' check
            return False                                        # (which involves a relatively
        elif(abs(self._position.y - otherPosition.y) > radius): # expensive squareRoot operation).
            return False                                        # i.e. Essentially used as a kind 
        else:                                                   # of "Prune & Sweep".                                              
            return True

#################################       
    def withinPreciseRadiusOfPoint(self, otherPosition, radius):
        if(self._position.distanceSquaredFrom(otherPosition) > radius **2):
            return False
        else:
            return True

#################################        
    def withinRadiusOfPoint(self, otherPosition, radius):
        return (self.withinCrudeRadiusOfPoint(otherPosition, radius) and
                self.withinPreciseRadiusOfPoint(otherPosition, radius))
        
################################# 
    def angleToLocation(self, location):
        """Angle, in degrees, of given location with respect to current heading."""
        directionVec = location - self._position
        return self._velocity.angleTo(directionVec)
       
##############################
    def notifyJump(self):
        """Should be called if agent is to be made to jump."""
        self._isInFreefall = True

##############################    
    def _resetListsAndAverages(self):
        del self.nearbyList[:]
        del self.crowdedList[:]
        del self.collisionList[:]
        self._reciprocalNearbyChecks.clear()
        self._otherAgentWeightingLookup.clear()
        self._resetAverages()
        
        self._needsFullListsRebuild = True
    
    def _resetAverages(self):
        self._avVelocity.reset()
        self._avPosition.reset()
        self._avCrowdedPos.reset()
        self._avCollisionDirection.reset()  
        self._nearbyWeightedTotal = 0.0
        self._crowdingWeightedTotal = 0.0
    
        self._needsAveragesRecalc = True

############################## 
    @staticmethod    
    def _getWeightingInverseSquareDistance(distanceVector):
        try:
            return (1.0 / float(distanceVector.magnitudeSquared()))
        except ZeroDivisionError:
            util.LogWarning("Please check your Maya scene - 2 particles have identical locations!")
            return 1000
 
########   
    @staticmethod
    def _getWeightingLinearDistance(distanceVector, maxDistance):
        return ((maxDistance - distanceVector.magnitude()) / maxDistance)

########
    @staticmethod    
    def _getWeightingAngular(angle, forwardAngle, blindAngle):
        if(angle < forwardAngle):
            return 1
        else:
            variableRange = blindAngle - forwardAngle
            return (float(variableRange - (angle - forwardAngle)) / variableRange)
    
########
    def _calculateWeighting(self, distanceVector, regionSize, angle, forwardAngle, blindAngle):
        percetionAttributeGroup = self._perceptionAttributeGroup
        if(percetionAttributeGroup.useInverseSquareWeighting):
            proximityWeighting = AgentState._getWeightingInverseSquareDistance(distanceVector)
        elif(percetionAttributeGroup.useLinearWeighting):
            proximityWeighting = AgentState._getWeightingLinearDistance(distanceVector, regionSize)
        elif(percetionAttributeGroup.useNoWeighting):
            proximityWeighting = 0
        else:
            raise RuntimeError("Unrecognised proximity weighting option.")
        
        return (proximityWeighting +
                AgentState._getWeightingAngular(angle, forwardAngle, blindAngle)) 
             
##############################        
    def _onFrameUpdated(self):
        """Resets stats of nearby, crowded and collided agents."""
        if(self._framesUntilNextRebuild <= 0 or not self.nearbyList):
            self._resetListsAndAverages()
        else:
            self._framesUntilNextRebuild -= 1
            self._resetAverages()
        
##############################
    def updateRegionalStatsIfNecessary(self, parentAgent, otherAgents, forceUpdate=False):
        """Builds up nearby, crowded and collided lists (if needed), recalculates averages for each.
        @param otherAgents List: list of other agents, all of which will be checked for proximity.
        @param neighbourhoodSize Float: distance below which other agents considered to be "nearby".
        @param crowdedRegionSize Float: ditto with "crowded".
        @param collisionRegionSize Float: ditto with "collided".
        """
        
        
        
        if(forceUpdate):
            self._framesUntilNextRebuild = 0
            self._onFrameUpdated()
        
        if(self._needsFullListsRebuild):
            self._recalculateListsAndAverages(parentAgent, otherAgents, 
                                              self.perceptionAttributes.neighbourhoodSize,
                                              self.perceptionAttributes.nearRegionSize, 
                                              self.perceptionAttributes.collisionRegionSize, 
                                              self.perceptionAttributes.blindRegionAngle, 
                                              self.perceptionAttributes.forwardVisionAngle)
            self._needsFullListsRebuild = False
            self._needsAveragesRecalc = False
            
            self._framesUntilNextRebuild = self._globalAttributeGroup.listRebuildFrequency if not self.isCrowded else 0
            
        elif(self._needsAveragesRecalc):
            self._recalculateAverages()
            self._needsAveragesRecalc = False
    
##############################
    def _recalculateListsAndAverages(self, parentAgent, otherAgents, neighbourhoodSize, 
                                       crowdedRegionSize, collisionRegionSize, blindRegionAngle, forwardRegionAngle):
        """Rebuilds from scratch using the corresponding list of candidate agents and region radii sizes.
        ***ASSUMES BOTH LISTS AND AVERAGES HAVE PREVIOUSLY BEEN RESET***
        """
        visibleAreaAngle = 180 - (blindRegionAngle * 0.5)
        forwardAreaAngle = forwardRegionAngle * 0.5
        neighbourhoodRegionSquared = neighbourhoodSize **2
        crowdedRegionSquared = crowdedRegionSize **2
        collisionRegionSquared = collisionRegionSize **2
        
        for otherAgent in otherAgents:
            otherAgentParticleId = otherAgent.agentId
            otherAgentState = otherAgent.state
            otherAgentPosition = otherAgentState.position
            
            if(otherAgentParticleId != self._agentId and
               not otherAgentState.isInFreefall and
               otherAgentParticleId not in self._reciprocalNearbyChecks and
               self.withinCrudeRadiusOfPoint(otherAgentPosition, neighbourhoodSize)):
                
                directionToOtherAgent = otherAgentPosition - self._position # slightly more efficient than using self.withinPreciseRadius,
                distanceToOtherAgentSquared = directionToOtherAgent.magnitudeSquared(True) # as this way we can reuse locally created Vectors
                if(distanceToOtherAgentSquared < neighbourhoodRegionSquared):
                    angleToOtherAgent = abs(self._velocity.angleTo(directionToOtherAgent, True))
                    
                    if(angleToOtherAgent < visibleAreaAngle):
                        # otherAgent is "nearby" if we're here
                        self.nearbyList.append(otherAgent)
                        weighting = self._calculateWeighting(directionToOtherAgent, neighbourhoodSize, 
                                                             angleToOtherAgent, forwardAreaAngle, visibleAreaAngle)
                        self._otherAgentWeightingLookup[otherAgentParticleId] = weighting
                        
                        self._avVelocity.add(otherAgentState.velocity * weighting)
                        self._avPosition.add(otherAgentPosition * weighting)
                        self._nearbyWeightedTotal += weighting
                        
                        if(distanceToOtherAgentSquared < crowdedRegionSquared):
                            # "crowded" if we're here
                            self.crowdedList.append(otherAgent)
                            self._avCrowdedPos.add(otherAgentPosition * weighting)
                            self._crowdingWeightedTotal += weighting
                            
                            if(distanceToOtherAgentSquared < collisionRegionSquared and angleToOtherAgent < 90):
                                # "collided" if we're here
                                self._isCollided = True
                                self.collisionList.append(otherAgent)
                                self._avCollisionDirection.add(otherAgentPosition)
                    
                    directionToOtherAgent.invert()
                    otherAgentState._makeReciprocalCheck(parentAgent, distanceToOtherAgentSquared, directionToOtherAgent)
                    
            elif(otherAgentParticleId != self._agentId and not otherAgent.isInFreefall):
                otherAgentState._makeReciprocalCheck(parentAgent)
            # end - for loop
        
        if(self.nearbyList):
            self._avVelocity.divide(self._nearbyWeightedTotal)
            self._avPosition.divide(self._nearbyWeightedTotal)
            
            if(self.crowdedList):
                self._avCrowdedPos.divide(self._crowdingWeightedTotal)
                if(self.collisionList):
                    self._avCollisionDirection.divide(len(self.collisionList))
        else:
            self._avVelocity.resetToVector(self._velocity)
            self._avPosition.resetToVector(self._position)

##############################        
    def _recalculateAverages(self):
        """Recalculates regional averages only - 
        ***ASSUMES AVERAGES HAVE BEEN RESET AND THAT REGIONAL LISTS ARE UP TO DATE.***
        """
        if(self.nearbyList):
            for otherAgent in self.nearbyList:
                weighting = self._otherAgentWeightingLookup[otherAgent.agentId]
                self._avVelocity.add(otherAgent.currentVelocity * weighting)
                self._avPosition.add(otherAgent.currentPosition * weighting)
                self._nearbyWeightedTotal += weighting
            
            self._avVelocity.divide(self._nearbyWeightedTotal)
            self._avPosition.divide(self._nearbyWeightedTotal)
            
            if(self.crowdedList):
                for otherAgent in self._crowdedList:
                    weighting = self._otherAgentWeightingLookup[otherAgent.agentId]
                    self._avCrowdedPos.add(otherAgent.currentPosition * weighting)
                    self._crowdingWeightedTotal += weighting
                    
                self._avCrowdedPos.divide(self._crowdingWeightedTotal)
                
                if(self.collisionList):
                    for otherAgent in self._crowdedList:
                        self._avCollisionDirection.add(otherAgent.currentPosition)
                        
                    self._avCollisionDirection.divide(len(self.collisionList))      

##############################
    def _makeReciprocalCheck(self, otherAgent, distanceToOtherAgentSquared=0, directionToOtherAgent=None):
        """Use this method where possible to avoid duplicating regional distance-checks that have already been made."""
        self._reciprocalNearbyChecks.add(otherAgent.agentId)
        
        if(directionToOtherAgent is not None):
            perceptionAttributes = otherAgent.state.perceptionAttributes
            neighbourhoodRegion = perceptionAttributes.neighbourhoodSize
            
            if(distanceToOtherAgentSquared < neighbourhoodRegion **2):
                angleToOtherAgent = abs(self._velocity.angleTo(directionToOtherAgent, True))
                visibleAreaAngle = 180 - (perceptionAttributes.blindRegionAngle * 0.5)
                
                if(angleToOtherAgent < visibleAreaAngle):
                    otherAgentPosition = otherAgent.currentPosition
                    
                    self.nearbyList.append(otherAgent)
                    
                    forwardAreaAngle = perceptionAttributes.forwardVisionAngle * 0.5
                    weighting = self._calculateWeighting(directionToOtherAgent, neighbourhoodRegion, 
                                                         angleToOtherAgent, forwardAreaAngle, visibleAreaAngle)
                    self._otherAgentWeightingLookup[otherAgent.agentId] = weighting
                            
                    self._avVelocity.add(otherAgent.currentVelocity * weighting)
                    self._avPosition.add(otherAgentPosition * weighting)
                    self._nearbyWeightedTotal += weighting
                    
                    if(distanceToOtherAgentSquared < perceptionAttributes.nearRegionSize **2):
                        self.crowdedList.append(otherAgent)
                        self._avCrowdedPos.add(otherAgentPosition * weighting)
                        self._crowdingWeightedTotal += weighting
                        
                        if(distanceToOtherAgentSquared < perceptionAttributes.collisionRegionSize **2
                            and angleToOtherAgent < 90):
                            #"collided" if we're here
                            self._isCollided = True
                            self.collisionList.append(otherAgent)
                            self._avCollisionDirection.add(otherAgentPosition)
                        
                        
# END OF CLASS
##############################