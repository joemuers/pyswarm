from boidBaseObject import BoidBaseObject

import boidAttributes
import boidVector.vector3 as bv3


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
        self._needsListsRebuild = True 
        
        self._behaviourSpecificState = None  # data 'blob' for client objects, not used internally
        
###################        
    def __str__(self):
        return ("id=%d, pos=%s, vel=%s, acln=%s, TG=%s" % 
                (self._particleId, self._position, self._velocity, self._acceleration, "Y" if(self._isTouchingGround) else "N"))
    
################### 
    def metaStr(self):
        nearList = ""
        for nearbyAgent in self.nearbyList:
            nearList += ("%d," % nearbyAgent.particleId)
        crowdList = ""
        for crowdingAgent in self.crowdedList:
            crowdList += ("%d," % crowdingAgent.particleId)
        collisionList = ""
        for collidingAgent in self.collisionList:
            collisionList += ("%d," % collidingAgent.particleId)
        
        return ("id=%d, avP=%s, avV=%s, avCP=%s, nr=%s, cr=%s, col=%s, bhvr=%s" % 
                (self._particleId, self._avPosition, self._avVelocity, 
                 self._avCrowdedPos, nearList, crowdList, collisionList,
                 self._behaviourSpecificState))       
    
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
        return (len(self.nearbyList) > 0)
    hasNeighbours = property(_getHasNeighbours)
    
    def _getIsCrowded(self):
        return (len(self.crowdedList) > 0)
    isCrowded = property(_getIsCrowded)        
    
    def _getIsCollided(self):
        return (len(self.collisionList) > 0)
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
    
    def _getBehaviourSpecificState(self):
        return self._behaviourSpecificState 
    def _setBehaviourSpecificState(self, value):
        self._behaviourSpecificState = value
    behaviourSpecificState = property(_getBehaviourSpecificState, _setBehaviourSpecificState)
    
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
        
        self._resetLists()

#################################       
    def withinRadiusOfPoint(self, otherPosition, radius):
        if(self._position.distanceFrom(otherPosition) < radius):
            return True
        else:
            return False
        
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
    def _resetLists(self):
        """Resets lists of nearby, crowded and collided agents."""
        
        del self.nearbyList[:]
        self._avVelocity.reset()
        self._avPosition.reset()
        del self.crowdedList[:]
        self._avCrowdedPos.reset()
        del self.collisionList[:]
        self._avCollisionDirection.reset()  
        
        self._needsListsRebuild = True
        
##############################
    def buildNearbyList(self, otherAgents, neighbourhoodSize, crowdedRegionSize, collisionRegionSize, forceUpdate = False):
        """Builds up nearby, crowded and collided lists.
        @param otherAgents List: list of other agents, all of which will be checked for proximity.
        @param neighbourhoodSize Float: distance below which other agents considered to be "nearby".
        @param crowdedRegionSize Float: ditto with "crowded".
        @param collisionRegionSize Float: ditto with "collided".
        """
        
        if(forceUpdate):
            self._resetLists()
        
        if(self._needsListsRebuild):
            visibleAreaAngle = 180 - (boidAttributes.blindRegionAngle() / 2)
            
            for otherAgent in otherAgents:
                otherAgentState = otherAgent.state
                
                if(otherAgentState.particleId != self._particleId and
                   otherAgentState.isTouchingGround and
                   self.withinRadiusOfPoint(otherAgentState.position, neighbourhoodSize) and
                   abs(self.angleToLocation(otherAgentState.position)) < visibleAreaAngle):
                    
                    #otherBoid is "nearby" if we're here
                    self.nearbyList.append(otherAgent)
                    self._avVelocity.add(otherAgentState.velocity)
                    self._avPosition.add(otherAgentState.position)
    
                    if(self.withinRadiusOfPoint(otherAgentState.position, crowdedRegionSize)):
                        #"crowded" if we're here
                        self.crowdedList.append(otherAgent)
                        self._avCrowdedPos.add(otherAgentState.position)
                        
                        if(self.withinRadiusOfPoint(otherAgentState.position, collisionRegionSize)):
                            directionOfCollisionVec = otherAgentState.position - self._position
                            if(abs(self._velocity.angleFrom(directionOfCollisionVec)) < 90):
                                #"collided" if we're here
                                self._isCollided = True
                                self.collisionList.append(otherAgent)
                                self._avCollisionDirection.add(otherAgentState.position)
            
            numNeighbours = len(self.nearbyList)
            if(numNeighbours > 0):
                self._avVelocity.add(self._velocity)
                self._avVelocity.divide(numNeighbours + 1)
                self._avPosition.add(self._position)
                self._avPosition.divide(numNeighbours + 1)
            else:
                self._avVelocity.resetVec(self._velocity)
                self._avPosition.resetVec(self._position)
    
            crowdedSize = len(self.crowdedList)
            if(crowdedSize > 0):
                self._avCrowdedPos.divide(crowdedSize)
            else:
                self._avCrowdedPos.resetVec(self._position)
                
            if(len(self.collisionList) > 0):
                self._avCollisionDirection.divide(len(self.collisionList))
        
        self._needsListsRebuild = False
