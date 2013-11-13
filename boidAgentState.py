from boidBaseObject import BoidBaseObject

import boidAttributes
import boidVectors.vector3 as bv3


class BoidAgentState(BoidBaseObject):
    """Internal to BoidAgent, i.e. each BoidAgent instance "has" a boidAgentState member.  
    Essentially just a data container with information on the corresponding agent, regarding:
        - current position
        - current heading/acceleration
        - lists of other agents within the agent's neighbourhood, along with the 
          corresponding average position and heading of those nearby agents.
          
    Depending on their proximity, other agents within the neighbourhood are 
    "nearby" (simply within perceivable range), "crowded" (within close proximity) 
    or "collided" (so close as to be considered to have collided with this agent).
    
    Potentially confusing member variables:
        - "touchingGround" = True if agent is not jumping/falling, False otherwise.
    """
    
    def __init__(self, particleId):
        self._particleId = particleId
        self._position = bv3.Vector3()
        self._velocity = bv3.Vector3()
        self._acceleration = bv3.Vector3()
        
        self._isTouchingGround = False
        
        self._nearbyList = []        # 
        self._crowdedList = []       #
        self._collisionList = []     # lists of boidAgent instances
        self._avPosition = bv3.Vector3()
        self._avVelocity = bv3.Vector3()
        self._avCrowdedPos = bv3.Vector3()
        self._avCollisionDirection = bv3.Vector3()    
        self._reciprocalNearbyChecks = set() 
        
        self._framesUntilNextRebuild = 0
        self._needsFullListsRebuild = True 
        self._needsAveragesRecalc = False
        
        self.behaviourSpecificState = None  # data 'blob' for client objects, not used internally
        
###################        
    def __str__(self):
        return ("id=%d, pos=%s, vel=%s, acln=%s, TG=%s" % 
                (self._particleId, self._position, self._velocity, self._acceleration, "Y" if(self._isTouchingGround) else "N"))
    
################### 
    def _getMetaStr(self):
        nearStringsList = [("%d," % nearbyAgent.particleId) for nearbyAgent in self.nearbyList]
        crowdStringsList = [("%d," % crowdingAgent.particleId) for crowdingAgent in self.crowdedList]
        collisionStringsList = [("%d," % collidingAgent.particleId) for collidingAgent in self.collisionList]
        
        return ("id=%d, avP=%s, avV=%s, avCP=%s, nr=%s, cr=%s, col=%s, bhvr=%s" % 
                (self._particleId, self._avPosition, self._avVelocity, 
                 self._avCrowdedPos, ''.join(nearStringsList), ''.join(crowdStringsList), ''.join(collisionStringsList),
                 self.behaviourSpecificState))       
    
#####################
    def getParticleId(self):
        return self._particleId
    particleId = property(getParticleId)

    def _getPosition(self):
        return self._position
    position = property(_getPosition)

    def _getVelocity(self):
        return self._velocity
    velocity = property(_getVelocity)

    def _getAcceleration(self):
        return self._acceleration
    acceleration = property(_getAcceleration)
    
    def _getIsTouchingGround(self):
        """True if agent is not jumping/falling, False otherwise."""
        return self._isTouchingGround
    isTouchingGround = property(_getIsTouchingGround)   
    
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
    
#####################           
    def updateCurrentVectors(self, position, velocity):
        """Updates internal state from corresponding vectors."""
        self._position.resetVec(position)
        self._acceleration = velocity - self._velocity
        self._velocity.resetVec(velocity)
        
        if(self._acceleration.y < boidAttributes.accelerationPerFrameDueToGravity()):
            self._isTouchingGround = False
        else:
            self._isTouchingGround = True
        
        self._onFrameUpdate()

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
        if(self._position.distanceFrom(otherPosition) > radius):
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
        return self._velocity.angleFrom(directionVec)
       
##############################
    def notifyJump(self):
        """Should be called if agent is to be made to jump."""
        self._isTouchingGround = False

##############################    
    def _resetListsAndAverages(self):
        del self.nearbyList[:]
        del self.crowdedList[:]
        del self.collisionList[:]
        self._reciprocalNearbyChecks.clear()
        self._resetAverages()
        
        self._needsFullListsRebuild = True
    
    def _resetAverages(self):
        self._avVelocity.reset()
        self._avPosition.reset()
        self._avCrowdedPos.reset()
        self._avCollisionDirection.reset()  
    
        self._needsAveragesRecalc = True
        
##############################        
    def _onFrameUpdate(self):
        """Resets stats of nearby, crowded and collided agents."""
        if(self._framesUntilNextRebuild <= 0 or not self.nearbyList):
            self._resetListsAndAverages()
        else:
            self._framesUntilNextRebuild -= 1
            self._resetAverages()
        
##############################
    def updateRegionalStatsIfNecessary(self, parentAgent, otherAgents, neighbourhoodSize, 
                                       crowdedRegionSize, collisionRegionSize, forceUpdate=False):
        """Builds up nearby, crowded and collided lists (if needed), recalculates averages for each.
        @param otherAgents List: list of other agents, all of which will be checked for proximity.
        @param neighbourhoodSize Float: distance below which other agents considered to be "nearby".
        @param crowdedRegionSize Float: ditto with "crowded".
        @param collisionRegionSize Float: ditto with "collided".
        """
        if(forceUpdate):
            self._framesUntilNextRebuild = 0
            self._onFrameUpdate()
        
        if(self._needsFullListsRebuild):
            self._recalculateListsAndAverages(parentAgent, otherAgents, neighbourhoodSize,
                                              crowdedRegionSize, collisionRegionSize)
            self._needsFullListsRebuild = False
            self._needsAveragesRecalc = False
            
            self._framesUntilNextRebuild = boidAttributes.listRebuildFrequency() if not self.isCrowded else 0
            
        elif(self._needsAveragesRecalc):
            self._recalculateAverages()
            self._needsAveragesRecalc = False
            
##############################
    def _recalculateListsAndAverages(self, parentAgent, otherAgents, neighbourhoodSize, 
                                       crowdedRegionSize, collisionRegionSize):
        """Rebuilds from scratch using the corresponding list of candidate agents and region radii sizes.
        ***ASSUMES BOTH LISTS AND AVERAGES HAVE PREVIOUSLY BEEN RESET***
        """
        visibleAreaAngle = 180 - (boidAttributes.blindRegionAngle() * 0.5)
            
        for otherAgent in otherAgents:
            otherAgentParticleId = otherAgent.particleId
            otherAgentState = otherAgent.state
            otherAgentPosition = otherAgentState.position
            
            if(otherAgentParticleId != self._particleId and
               otherAgentState.isTouchingGround and
               otherAgentParticleId not in self._reciprocalNearbyChecks and
               self.withinCrudeRadiusOfPoint(otherAgentPosition, neighbourhoodSize)):
                
                directionToOtherAgent = otherAgentPosition - self._position # slightly more efficient than using self.withinRefinedRadius,
                distanceToOtherAgent = directionToOtherAgent.magnitude(True) # as this way we can reuse locally created Vectors
                if(distanceToOtherAgent < neighbourhoodSize):
                    angleToOtherAgent = abs(self._velocity.angleFrom(directionToOtherAgent, True))
                    
                    if(angleToOtherAgent < visibleAreaAngle):
                        #otherBoid is "nearby" if we're here
                        self.nearbyList.append(otherAgent)
                        self._avVelocity.add(otherAgentState.velocity, True)
                        self._avPosition.add(otherAgentPosition, True)
                        
                        if(distanceToOtherAgent < crowdedRegionSize):
                            #"crowded" if we're here
                            self.crowdedList.append(otherAgent)
                            self._avCrowdedPos.add(otherAgentPosition, True)
                            
                            if(distanceToOtherAgent < collisionRegionSize and angleToOtherAgent < 90):
                                #"collided" if we're here
                                self._isCollided = True
                                self.collisionList.append(otherAgent)
                                self._avCollisionDirection.add(otherAgentPosition, True)
                    
                    directionToOtherAgent.invert()
                    otherAgentState._makeReciprocalCheck(parentAgent, True, distanceToOtherAgent, directionToOtherAgent,
                                                         crowdedRegionSize, collisionRegionSize)

            elif(otherAgentParticleId != self._particleId and otherAgent.isTouchingGround):
                otherAgentState._makeReciprocalCheck(parentAgent)
            # end - for loop
        
        if(self.nearbyList):
            numNeighbours = len(self.nearbyList) + 1 # includes 'self'
            self._avVelocity.add(self._velocity, True)
            self._avPosition.add(self._position, True)
            self._avVelocity.divide(numNeighbours)
            self._avPosition.divide(numNeighbours)
            
            if(self.crowdedList):
                self._avCrowdedPos.divide(len(self.crowdedList))
                if(self.collisionList):
                    self._avCollisionDirection.divide(len(self.collisionList))
        else:
            self._avVelocity.resetVec(self._velocity, True)
            self._avPosition.resetVec(self._position, True)

##############################        
    def _recalculateAverages(self):
        """Recalculates regional averages only - 
        ***ASSUMES AVERAGES HAVE BEEN RESET AND THAT REGIONAL LISTS ARE UP TO DATE.***
        """
        if(self.nearbyList):
            for otherAgent in self.nearbyList:
                self._avVelocity.add(otherAgent.currentVelocity, True)
                self._avPosition.add(otherAgent.currentPosition, True)
            
            numNeighbours = len(self.nearbyList) + 1 # includes 'self'
            self._avVelocity.add(self._velocity, True)
            self._avPosition.add(self._position, True)
            self._avVelocity.divide(numNeighbours)
            self._avPosition.divide(numNeighbours)
            
            if(self.crowdedList):
                for otherAgent in self._crowdedList:
                    self._avCrowdedPos.add(otherAgent.currentPosition, True)
                self._avCrowdedPos.divide(len(self.crowdedList), True)
                
                if(self.collisionList):
                    for otherAgent in self._crowdedList:
                        self._avCollisionDirection.add(otherAgent.currentPosition, True)
                    self._avCollisionDirection.divide(len(self.collisionList), True)      

##############################
    def _makeReciprocalCheck(self, otherAgent, isNearby=False, distanceToOtherAgent = 0, 
                             directionToOtherAgent=None, crowdedRegionSize=0, collisionRegionSize=0):
        """Use this method where possible to avoid duplicating regional distance-checks that have already been made."""
        self._reciprocalNearbyChecks.add(otherAgent.particleId)
        
        if(isNearby):
            angleToOtherAgent = abs(self._velocity.angleFrom(directionToOtherAgent, True))
            if(angleToOtherAgent < 180 - (boidAttributes.blindRegionAngle() * 0.5)):
                otherAgentPosition = otherAgent.currentPosition
                
                self.nearbyList.append(otherAgent)
                self._avVelocity.add(otherAgent.currentVelocity, True)
                self._avPosition.add(otherAgentPosition, True)
                
                if(distanceToOtherAgent < crowdedRegionSize):
                    self.crowdedList.append(otherAgent)
                    self._avCrowdedPos.add(otherAgentPosition, True)
                    
                    if(distanceToOtherAgent < collisionRegionSize and angleToOtherAgent < 90):
                        #"collided" if we're here
                        self._isCollided = True
                        self.collisionList.append(otherAgent)
                        self._avCollisionDirection.add(otherAgentPosition, True)
                        
                        
# END OF CLASS
##############################