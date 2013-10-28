import boidConstants
import boidUtil
import boidVector3 as bv3
import boidZoneGraph as bzg
import boidAgent as ba
import boidGroupTarget as bgt
import boidGroupPath as bgp




class BoidSwarm(object):
    
    def __init__(self, particleShapeNode, negativeIndicesCornerLocator, positiveIndicesCornerLocator):
        self._particleShapeNode = particleShapeNode
        self._particleIdsOrdering = []
        self.boidsList = {}
        self._zoneGraph = bzg.BoidZoneGraph(negativeIndicesCornerLocator, positiveIndicesCornerLocator)
        self._zoneGraph.useEarlyHitListLookup = True
        self._buildParticleList()

        self._priorityGoal = None
        self._secondaryGoal = None

        self._curvePath = None

#############################
    def __str__(self):
        length = len(self.boidsList)
        if(length > 0):
            ret = "nodeName=%s, %d particles:" % (self._particleShapeNode.name(), length)
            for boid in sorted(self.boidsList.itervalues()):
                ret += "\n\t" + boid.__str__()
            return ret
        else:
            return "empty"


#############################
    def metaStrings(self):
        ret = ""
        for boid in sorted(self.boidsList.itervalues()):
            ret += '\t' + boid.metaStr() + '\n'
        return ret

#############################    
    def zoneString(self):
        return self._zoneGraph.__str__()

############################# 
    def _getParticleShapeName(self):
        return self._particleShapeNode.name()
    particleShapeName = property(_getParticleShapeName)
    
#############################
    def _buildParticleList(self, fullRebuild = True):
        lowerBounds = self._zoneGraph.lowerBoundsVector              # XXXXXXXXXXXXXXXXXXXXXXXX
        upperBounds = self._zoneGraph.upperBoundsVector # XXXXXXXXXXXXXXXXXXXx
        
        
        if(fullRebuild):
            self.boidsList.clear()
            
            if(self._particleShapeNode.getCount() > 0):
                self._particleIdsOrdering = boidUtil.getParticleIdsList(self.particleShapeName)             
                if(self._particleIdsOrdering  != None):
                    for ptclId in self._particleIdsOrdering:
                        newBoid = ba.BoidAgent(int(ptclId), lowerBounds, upperBounds)
                        self.boidsList[newBoid.particleId] = newBoid
        else:
            numParticles = self._particleShapeNode.getCount()
            
            if(numParticles > len(self.boidsList)):
                self._particleIdsOrdering = boidUtil.getParticleIdsList(self.particleShapeName)
                
                sortedIdsList = sorted(self._particleIdsOrdering)
                keysList = sorted(self.boidsList.keys())
                numKeys = len(keysList)
                lastKey = keysList[numKeys-1] if numKeys > 0 else -1
                newBoids = []
                
                for ptclId in reversed(sortedIdsList):
                    if(ptclId > lastKey):
                        newBoid = ba.BoidAgent(int(ptclId), lowerBounds, upperBounds)
                        self.boidsList[newBoid.particleId] = newBoid   
                        newBoids.append(newBoid)
                    else:
                        break
                    
                self.onNewBoidsCreated(newBoids)
                
            elif(numParticles < len(self.boidsList)):
                self._particleIdsOrdering = boidUtil.getParticleIdsList(self.particleShapeName)
                particleSet = set(self._particleIdsOrdering)
                boidSet = set(self.boidsList.keys())
                
                for particleId in boidSet.difference(particleSet):
                    del self.boidsList[particleId]
            else:
                print("XXXXX WARNING - PARTIAL REBUILD WITH NO DIFFERENCE IN PARTICLE COUNT")

                    
#############################                     
    def _killSingleParticle(self, particleId):
        """IMPORTANT - WILL NOT TAKE EFEECT UNTIL AFTER NEXT FRAME UPDATE"""
        if(particleId in self.boidsList):
            boidUtil.killParticle(self.particleShapeName, particleId)
        

#############################            
    def _getSingleParticleInfo(self, particleId):            
        position =  boidUtil.getSingleParticlePosition(self.particleShapeName, particleId) 
        velocity =  boidUtil.getSingleParticleVelocity(self.particleShapeName, particleId) 
        
        self.boidsList[particleId].updateCurrentVectors(bv3.BoidVector3(position[0], position[1], position[2]), 
                                                         bv3.BoidVector3(velocity[0], velocity[1], velocity[2]))
        self._zoneGraph.updateBoidPosition(self.boidsList[particleId])
 
    def setStickiness(self, particleId, value):
        self.boidsList[particleId].stickinessScale = value
        boidUtil.setStickinessScale(self.particleShapeName, particleId, value) # do this right now - otherwise will wait until next frame update

#############################
    def fullUpdate(self):       
        self._getAllParticlesInfo()
        self._calculateBoidsBehaviour()
        self._updateAllParticles()

#############################
    def _getAllParticlesInfo(self, queryExtraInfo = False):
        self._zoneGraph.resetZones()
        
        if(self._priorityGoal != None):
            self._priorityGoal.resetAverages()
            
        if(self._secondaryGoal != None):
            self._secondaryGoal.resetAverages()
            
        if(self._curvePath != None):
            self._curvePath.recheckCurvePoints()
            
        numParticles = self._particleShapeNode.getCount()
        if(numParticles == 0):
            self._buildParticleList(True)
        elif(numParticles != len(self.boidsList)):
            self._buildParticleList(False)
        #elif(numParticles < len(self.boidsList)):
            #print("XXXXXXXXXX WARNING - MISSING PARTICLES IN LIST!!!, REBUILDING FROM SCRATCH... XXXXX")
            #self._buildParticleList(True)
        
        if(numParticles > 0):
            positions = boidUtil.getParticlePositionsList(self.particleShapeName)
            velocities = boidUtil.getParticleVelocitiesList(self.particleShapeName)
            
            if(len(positions) < numParticles * 3):
                #repeated call here because of shitty Maya bug whereby sometimes only get first item in request for goalsU...
                positions = boidUtil.getParticlePositionsList(self.particleShapeName) 
    
            for i in range(0, numParticles):
                j = i * 3
                particleId = self._particleIdsOrdering[i]
                boid = self.boidsList[particleId]
                
                boid.updateCurrentVectors(bv3.BoidVector3(positions[j], positions[j+1], positions[j+2]),
                                          bv3.BoidVector3(velocities[j], velocities[j+1], velocities[j+2]))
                self._zoneGraph.updateBoidPosition(boid)
                
            if(queryExtraInfo):
                self._queryExtraInfo()

#############################
    def _queryExtraInfo(self):
        stickinessScales = boidUtil.getStickinessScalesList(self.particleShapeName)
        for i in range(0, len(stickinessScales)):
            particleId = self._particleIdsOrdering[i]
            self.boidsList[particleId]._stickinessScale = stickinessScales[i]

#############################
    def _calculateBoidsBehaviour(self):        
        for boid in self.boidsList.itervalues():
            regionList = self._zoneGraph.regionListForBoid(boid)
            boid.updateBehaviour(regionList)

#############################            
    def _paintBlack(self):
        for boid in self.boidsList.itervalues:
            boidUtil.setParticleColour(self.particleShapeName, boid.particleId, 0, 0, 0)
            
    def setDebugColour(self, boid):
        if(boidConstants.useDebugColours()):
            particleId = boid.particleId
            
            if(boid.isInBasePyramid):
                stickiness = boid.stickinessScale / 2
                boidUtil.setParticleColour(self.particleShapeName, particleId, stickiness, stickiness, stickiness)
            elif(not boid.isTouchingGround):
                boidUtil.setParticleColour(self.particleShapeName, particleId, 0.2, 0.2, 0.2)
            elif(boid.isCollided):
                boidUtil.setParticleColour(self.particleShapeName, particleId, 1, 0, 0)
            elif(boid.isFollowingPriorityGoal):
                boidUtil.setParticleColour(self.particleShapeName, particleId, 1, 1, 0)
            elif(boid.isCrowded):
                boidUtil.setParticleColour(self.particleShapeName, particleId, 0.65, 0, 0)
            elif(boid.isLeader):
                boidUtil.setParticleColour(self.particleShapeName, particleId, 1, 1, 1)
            elif(boid.hasNeighbours):
                boidUtil.setParticleColour(self.particleShapeName, particleId, 0, 0.8, 0)
            else:
                boidUtil.setParticleColour(self.particleShapeName, particleId, 0, 0, 1)        
  
#############################
    def _updateAllParticles(self):
        for boid in self.boidsList.itervalues():
            self.setDebugColour(boid)
            boid.commitNewBehaviour(self._particleShapeNode.name())

#############################
    def _updateSingleParticle(self, particleId):
        singleParticle = self.boidsList[particleId]
        self.setDebugColour(singleParticle)
        singleParticle.commitNewBehaviour(self._particleShapeNode.name())

#############################          
    def makeLeader(self, index, waypointList):
        boid = self.boidsList[index]
        boid.makeLeader(waypointList)
        
#############################          
    def unmakeLeader(self, index):
        boid = self.boidsList[index]
        boid.makeLeader(None)
        
############################# 
    def createNewGoal(self, goalVertex, lipVertex, finalGoalVertex):
        self._priorityGoal = bgt.BoidGroupTarget(goalVertex, lipVertex, finalGoalVertex, self)
        print("Make new group target - %s" % self._priorityGoal)
        
    def createSecondaryGoal(self, goalVertex, lipVertex, finalGoalVertex):
        self._secondaryGoal = bgt.BoidGroupTarget(goalVertex, lipVertex, finalGoalVertex, self)
        print("Make new secondary target - %s" % self._secondaryGoal)

    def makeGoalInfected(self, index,  makeLeader = True):
        if(self._priorityGoal == None):
            print("XXXXX WARNING - NO GOAL EXISTS XXXX")
            
        boid = self.boidsList[index]
        boid.makeGoalInfected(self._priorityGoal)
        if(makeLeader):
            self._priorityGoal.makeLeader(boid)
         
    def makeAllGoalInfected(self):
        if(self._priorityGoal == None):
            print("XXXXX WARNING - NO GOAL EXISTS XXXX")        

        for boid in self.boidsList.itervalues():
            boid.makeGoalInfected(self._priorityGoal)
            
    def makeSecondaryGoalInfected(self, index):
        if(self._secondaryGoal != None):
            boid = self.boidsList[index]
            boid.makeGoalInfected(self._secondaryGoal)    
            self._secondaryGoal.checkBoidLocation(boid)
            
    def makeNoneGoalInfected(self):
        for boid in self.boidsList.itervalues():
            boid.makeGoalInfected(None)
            
    def collapseGoal(self):
        if(self._priorityGoal != None):
            self._priorityGoal.performCollapse = True
            print("COLLAPSING GOAL...")
        return
        
#############################  
    def createNewCurvePath(self, curvePath):
        self._curvePath = bgp.BoidGroupPath(curvePath, self)
        
        print("Make new curve path - %s" % self._curvePath)
        
    def onGoalReachedForBoid(self, boid):
        print("END OR CURVE #%d" % boid.particleId)
        return
    
    def onNewBoidsCreated(self, newBoidsList):
        if(self._curvePath != None):
            for newBoid in newBoidsList:
                newBoid.makeFollowCurvePath(self._curvePath)
                
    def onBoidArrivedAtGoalDestination(self, goal, boid):
        print ("%s at destination" % boid)
        #self.makeSecondaryGoalInfected(boid.particleId)
        
        
    def makeSingleBoidFollowPath(self, particleIndex):
        if(self._curvePath == None):
            print("XXX WARNING - NO CURVE PATH EXISTS XXX")
            
        self.boidsList[particleIndex].makeFollowCurvePath(self._curvePath)
            
    def makeAllFollowPath(self):
        if(self._curvePath == None):
            print("XXX WARNING - NO CURVE PATH EXISTS XXX")        
            
        for boid in self.boidsList.itervalues():
            boid.makeFollowCurvePath(self._curvePath)
        
#############################  
    def makeJump(self, particleId):
        self._getSingleParticleInfo(particleId)
        boid = self.boidsList[particleId]
        boid._desiredAcceleration.reset()
        boid._jump()
        boid.commitNewBehaviour(self._particleShapeNode.name())

################################################################################
