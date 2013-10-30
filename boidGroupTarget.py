from boidObject import BoidObject

import random

import boidConstants
import boidUtil
import boidVector2 as bv2
import boidVector3 as bv3


class BoidGroupTarget(BoidObject):
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
    There is also the concept of 'leaders' whereby if certain agents are designated as leaders, they
    will be drawn to the baseLocator as normal but all non-leader agents will instead be drawn towards the
    leader's current position.  Once the leader reaches the basePyramid, other agents will revert 
    to normal behaviour. This, together with the goal-infection/incubation period algorithm, produces 
    a nice 'streaming' effect of agents moving towards the goal. 
    Logic for client agent's behaviour is primarily in this class - client agents must query 
    the groupTarget on each frame to get their desiredAcceleration.
    
    """
    
    def __init__(self, basePos, lipPos, finalPos, bDelegate = None):
        self._delegate = bDelegate
                
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
            
        self._baseToFinalDirection = bv3.BoidVector3()

        self._leaders = []
                    
        self._boidDistanceLookup = {}
        self._atTheLipLookup = set()
        self._overTheWallLookup = set()
        
        self._pushUpwardsVector = bv2.BoidVector2()
        
        # variables in the following block relate to agent's distance
        # from the baseLocator
        self._boidDistance_runningTotal = bv2.BoidVector2()
        self._boidDistance_average = bv2.BoidVector2()
        self._needsAverageDistanceCalc = False
        self._maxBoidDistance = bv2.BoidVector2()
        
        # variables here relate to average position taken from within
        # the basePyramid.
        self._boidPosition_runningTotal = bv3.BoidVector3()
        self._boidPosition_average = bv3.BoidVector3()
        self._needsAveragePositionCalc = False
        
        self.performCollapse = False
        
#######################        
    def __str__(self):
        leadersStr = ""
        for boid in self._leaders:
            leadersStr += ("%d," % boid.particleId)
        listStr = ""
        for boid, distance in sorted(self._boidDistanceLookup.iteritems()):
            listStr += ("\t%s - dist=%s (mag=%.4f)\n" % (boid, distance, distance.magnitude()))
        atLipStr = ""
        for boid in self._atTheLipLookup:
            atLipStr += ("\t%s\n" % boid)
        overStr = ""
        for boid in self._overTheWallLookup:
            overStr += ("\t%s\n" % boid)
            
        return ("<pos=%s, lip=%s, final=%s, ldrs=%s, climbVector=%s, avDist=%s, maxDist=%s, avPos=%s, atLoctn=\n%s\natLip=\n%s\nover=\n%s>" % 
                (self._baseVector, self._lipVector, self._finalVector, leadersStr,
                 self._pushUpwardsVector, self.distanceAverage, self._maxBoidDistance, self.positionAverage, 
                 listStr, atLipStr, overStr))

#######################
    def attractorPositionForBoid(self, boid):
        """Returns position (BoidVector3) towards which the boidAgent should be made to move towards."""
        
        returnValue = None
        numLeaders = len(self._leaders)

        if(boid._hasArrivedAtGoalBase or numLeaders == 0 or boid in self._leaders):
            returnValue = self._baseVector
        elif(numLeaders == 1):
            returnValue = self._leaders[0].currentPosition
        else:
            candidateLeader = None
            minDist = boid.currentPosition.distanceFrom(self._baseVector)
            for leader in self._leaders:
                candidateDist = boid.currentPosition.distanceFrom(leader.currentPosition)
                if(candidateDist < minDist):
                    minDist = candidateDist
                    candidateLeader = leader
            
            if(candidateLeader != None):
                returnValue = candidateLeader.currentPosition
            else:
                returnValue = self._baseVector
                
        if(self.performCollapse):
            returnValue.invert()        
        
        return returnValue
            
        
#######################
    def _getDistanceAverage(self):
        """Average distance from baseLocator of agents in the basePyramid."""
        
        if(self._needsAverageDistanceCalc and len(self._boidDistanceLookup) > 0):
            self._boidDistance_average.resetVec(self._boidDistance_runningTotal)
            self._boidDistance_average.divide(len(self._boidDistanceLookup))
            self._needsAverageDistanceCalc = False
        return self._boidDistance_average
    distanceAverage = property(_getDistanceAverage)
    
    def _getPositionAverage(self):
        """Average position of agents in the basePyramid."""
        
        if(self._needsAveragePositionCalc and len(self._boidDistanceLookup) > 0):
            self._boidPosition_average.resetVec(self._boidPosition_runningTotal)
            self._boidPosition_average.divide(len(self._boidDistanceLookup))
            self._needsAveragePositionCalc = False
        return self._boidPosition_average
    positionAverage = property(_getPositionAverage)

#######################    
    def _getMaxHorizontalDistance(self):
        """Current largest (scalar) horizontal distance of an agent, within the basePyramid, from the baseLocator."""
        return self._maxBoidDistance.u
    maxHorizontalDistance = property(_getMaxHorizontalDistance)
    
    def _getMaxVerticalDistance(self):
        """Current largest (scalar) vertical distance of an agent, within the basePyramid, from the baseLocator."""
        return self._maxBoidDistance.v
    maxVerticalDistance = property(_getMaxVerticalDistance)
    
#######################
    def _getPushUpwardsHorizontalMagnitude(self):
        """Acceleration applied by each boid in the horizontal direction (towards 
        the baseLocator) after having joined the basePyramid."""
        return boidConstants.pushUpwardsAccelerationHorizontal()
        #return self._pushUpwardsVector.v
    pushUpwardsHorizontalMagnitude = property(_getPushUpwardsHorizontalMagnitude)
    
    def _getPushUpwardsVerticalMagnitude(self):
        """Acceleration applied by each boid in the vertical direction (towards 
        the lipLocator) after having joined the basePyramid."""
        return boidConstants.pushUpwardsAccelerationVertical()
        #return self._pushUpwardsVector.u
    pushUpwardsVerticalMagnitude = property(_getPushUpwardsVerticalMagnitude)
        
####################### 
    def makeLeader(self, boid):
        if(not boid in self._leaders):
            self._leaders.append(boid)
    
    def unMakeLeader(self, boid):
        if(boid in self._leaders):
            self._leaders.remove(boid)
            
#######################        
    def resetAverages(self):
        """Lists of agents must be rebuild on every frame, this method clears the lists
        and sets up everything for a new frame."""
        
        self._boidPosition_runningTotal.reset()
        self._needsAveragePositionCalc = True
        self._boidDistance_runningTotal.reset()
        self._needsAverageDistanceCalc = True
        self._maxBoidDistance.reset()
        self._boidDistanceLookup.clear()
        self._overTheWallLookup.clear()
        
        if(self._baseLocator != None):
            self._baseVector = boidUtil.boidVectorFromLocator(self._baseLocator)
        if(self._lipLocator != None):
            self._lipVector = boidUtil.boidVectorFromLocator(self._lipLocator)        
        if(self._finalLocator != None):
            self._finalLocator = boidUtil.boidVectorFromLocator(self._finalLocator)   
        self._baseToFinalDirection = self._finalVector - self._baseVector

#######################
    def checkBoidLocation(self, boid):
        """Checks current location of agent to determine appropriate list it should be put
        into (which then determines corresponding behaviour)."""
        
        baseToBoidVec = boid.currentPosition - self._baseVector

        boid._hasArrivedAtGoalBase = True
        
        if(abs(self._baseToFinalDirection.angleFrom(baseToBoidVec)) < 90):
            self.deRegisterBoidAsArrived(boid)
            self._overTheWallLookup.add(boid)
            boid.isAtPriorityGoal = True
            
            if(self._delegate != None):
                self._delegate.onBoidArrivedAtGoalDestination(self, boid)
                
            return True
        else:
            boid.isAtPriorityGoal = False
            if(boid.currentPosition.y >= (self._lipVector.y - 0.1)):
                self.deRegisterBoidAsArrived(boid)
                self._atTheLipLookup.add(boid)
                return True
            elif(baseToBoidVec.magnitude() < boidConstants.priorityGoalThreshold()):
                if(boid in self._overTheWallLookup):
                    self._overTheWallLookup.remove(boid)
                if(boid in self._atTheLipLookup):
                    self._atTheLipLookup.remove(boid)
                self.registerBoidAsArrived(boid)
                return True
            else:
                if(baseToBoidVec.magnitude() > (boidConstants.priorityGoalThreshold() * 4)):
                    boid._hasArrivedAtGoalBase = False
                self.deRegisterBoidAsArrived(boid)
                return False
                
        
        #overTheWall = False
        #if(boid.currentPosition.y >= self._lipVector.y):
            #overTheWall = True
        #else:
            #baseToBoidVec = boid.currentPosition - self._baseVector
            
            #if(abs(self._baseToFinalDirection.angleFrom(baseToBoidVec)) < 90):
                #overTheWall = True
                
        #if(overTheWall):
            #self.deRegisterBoidAsArrived(boid)
            #self._overTheWallLookup.add(boid)
            #return True
        #elif(self._baseVector.distanceFrom(boid.currentPosition) < boidConstants.priorityGoalThreshold()):
            #if(boid in self._overTheWallLookup):
                #self._overTheWallLookup.remove(boid)
            #self.registerBoidAsArrived(boid)
            #return True
        #else:
            #self.deRegisterBoidAsArrived(boid)
            #return False

#######################
    def registerBoidAsArrived(self, boid):
        """Registers boid as having arrived at the basePyramid, behaviour
        for the agent will now be switched from 'goalChase' to basePyramid 'push-up' behaviour."""
        
        if(not boid in self._boidDistanceLookup):
            if(boid in self._leaders):
                self._leaders.remove(boid)
            
            distanceVec = boid.currentPosition - self._baseVector
            self._boidDistance_runningTotal.u += distanceVec.magnitude(True)
            self._boidDistance_runningTotal.v += distanceVec.y
            self._needsAverageDistanceCalc = True         
            
            if(distanceVec.magnitude(True) > self._maxBoidDistance.u):
                self._maxBoidDistance.u = distanceVec.magnitude(True)
            if(distanceVec.y > self._maxBoidDistance.v):
                self._maxBoidDistance.v = distanceVec.y
            
            self._boidPosition_runningTotal.add(boid.currentPosition)
            self._needsAveragePositionCalc = True   
            
            self._boidDistanceLookup[boid] = distanceVec
            boid._hasArrivedAtGoalBase = True

#######################            
    def deRegisterBoidAsArrived(self, boid):
        """Removes agent from all lists, agent's behaviour will no longer be
        influenced by the BoidGroupTarget."""
        
        if(boid in self._boidDistanceLookup):            
            distanceVec = boid.currentPosition - self._baseVector
            self._boidDistance_runningTotal.u -= distanceVec.magnitude(True)
            self._boidDistance_runningTotal.v -= distanceVec.y
            self._needsAverageDistanceCalc = True  
            
            self._boidPosition_runningTotal.subtract(boid.currentPosition)
            self._needsAveragePositionCalc = True       
            
            del self._boidDistanceLookup[boid]
            
        if(boid in self._overTheWallLookup):
            self._overTheWallLookup.remove(boid)
        if(boid in self._atTheLipLookup):
            self._atTheLipLookup.remove(boid)
        

#######################
    def getDesiredAcceleration(self, boid):
        """Returns corresponding acceleration for the agent as determined by calculated behaviour.
        Client agents should call this method on each frame update and modify their own desiredAcceleration accordingly."""
        
        if(boid in self._overTheWallLookup):
            targetVelocity = bv3.BoidVector3(self._baseToFinalDirection.x, 0, self._baseToFinalDirection.z)
            targetVelocity.normalise(boidConstants.goalChaseSpeed())
            retVal = targetVelocity - boid.currentVelocity
            if(retVal.magnitude() > boidConstants.maxAccel()):
                retVal.normalise(boidConstants.maxAccel())
            
            print("#%d escAcln=%s" % (boid.particleId, retVal))
            
            boid.stickinessScale = 0
            return retVal
        elif(boid in self._atTheLipLookup):
            retVal = bv3.BoidVector3(self._baseToFinalDirection.x, 0, self._baseToFinalDirection.z)
            retVal.normalise(boidConstants.goalChaseSpeed()) # misleading place to use goalChaseSpeed, should use something else??
            retVal.y = self.pushUpwardsVerticalMagnitude
            
            boid.stickinessScale = 0
            return retVal
        else:        
            directionToGoal = self._baseVector - boid.currentPosition
            horizontalComponent = directionToGoal.horizontalVector()
            horizontalComponent.normalise(self.pushUpwardsHorizontalMagnitude)
            
            distance = self._boidDistanceLookup[boid]
            if(distance.magnitude() < self.distanceAverage.magnitude()):
                diff = self.distanceAverage.magnitude() - distance.magnitude()
                proportion = diff / self.distanceAverage.magnitude()
                stickinessValue = 2 * proportion
    
                boid.stickinessScale = stickinessValue
            else:
                boid.stickinessScale = 0
                
            
            if(not self.performCollapse):
                return bv3.BoidVector3(horizontalComponent.u, self.pushUpwardsVerticalMagnitude, horizontalComponent.v)
            else:
                boid.stickinessScale = 0
                retVal = bv3.BoidVector3(-(horizontalComponent.u), 0, -(horizontalComponent.v))
                
                return retVal

#######################
    def getShouldJump(self, boid):
        """Returns True if agent should jump up onto basePyramid, False otherwise."""
        
        distanceVec = boid.currentPosition - self._baseVector
        distance = distanceVec.magnitude(True)
        
        if(distance > boidConstants.priorityGoalThreshold() and
           distance < boidConstants.priorityGoalThreshold() + boidConstants.jumpOnPileUpRegionSize() and 
           random.uniform(0, 1.0) < boidConstants.jumpOnPileUpProbability()):
            return True
        else:
            return False