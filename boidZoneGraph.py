from boidObject import BoidObject

import boidConstants
import boidUtil



class _BoidZone(BoidObject):
    """'Private' class intended for internal within BoidZoneGraph only.
    
    Represents a single zone, with links to immediate neighbours.
    
    Also, each zone contains a 'hitList', basically an optimisation. In successive frame updates,
    Agents will almost always be in the same zone as in the previous frame, or in a neighbouring
    zone.  As such, when checking if a boid is still within a certain zone or has moved to a different
    one, the original zone's hitlist should be checked first rather than iterating sequentially though
    every zone.
    """

    def __init__(self, zoneId, xMin, xMax, zMin, zMax):
        self.zoneId = zoneId
        self.boidList = []
        self._xMin = xMin
        self._xMax = xMax
        self._zMin = zMin
        self._zMax = zMax
        self._neighbouringZoneUp = None
        self._neighbouringZoneDown = None
        self._neighbouringZoneLeft = None
        self._neighbouringZoneRight = None
        
        self._earlyHitList = []

##########################        
    def __str__(self):
        listStr = ""
        for boid in self.boidList:
            listStr += ("\n\t%s" % boid)
        
        return ("<id=%d, xMin=%.4f, xMax=%.4f, zMin=%.4f, zMax=%.4f count=%d\nlist=%s\n >" % 
                (self.zoneId, self._xMin, self._xMax, self._zMin, self._zMax, len(self.boidList), listStr))

##########################        
    def neighbouringZonesStr(self):
        retStr = ("id=%d, UP=%d, RIGHT=%d, DOWN=%d, LEFT=%d" % 
                  (self.zoneId,
                  self._neighbouringZoneUp.zoneId if(self._neighbouringZoneUp != None) else -1,
                  self._neighbouringZoneRight.zoneId if(self._neighbouringZoneRight != None) else -1,
                  self._neighbouringZoneDown.zoneId if(self._neighbouringZoneDown != None) else -1,
                  self._neighbouringZoneLeft.zoneId if(self._neighbouringZoneLeft != None) else -1))
        return retStr
    
##########################            
    def buildHitList(self):
        """Constructs hitlist of neighbouring zones.
        Should only be called once, when zone system is being constructed."""
        
        del self._earlyHitList[:]
        
        self._earlyHitList.append(self)
        if(self._neighbouringZoneUp != None):
            self._earlyHitList.append(self._neighbouringZoneUp)
            if(self._neighbouringZoneUp._neighbouringZoneLeft != None):
                self._earlyHitList.append(self._neighbouringZoneUp._neighbouringZoneLeft)
            if(self._neighbouringZoneUp._neighbouringZoneRight != None):
                self._earlyHitList.append(self._neighbouringZoneUp._neighbouringZoneRight)
        if(self._neighbouringZoneLeft != None):
            self._earlyHitList.append(self._neighbouringZoneLeft)
            if(self._neighbouringZoneLeft._neighbouringZoneDown != None):
                self._earlyHitList.append(self._neighbouringZoneLeft._neighbouringZoneDown)
        if(self._neighbouringZoneDown != None):
            self._earlyHitList.append(self._neighbouringZoneDown)
            if(self._neighbouringZoneDown._neighbouringZoneRight != None):
                self._earlyHitList.append(self._neighbouringZoneDown._neighbouringZoneRight)
        if(self._neighbouringZoneRight != None):
            self._earlyHitList.append(self._neighbouringZoneRight)
            
##########################         
    def _containsVectorPosition(self, vector):
        """Returns True if vector is within the zone, False otherwise."""
        
        if(self._xMin <= vector.u and vector.u <= self._xMax):
            if(self._zMin <= vector.v and vector.v <= self._zMax):
                return True
            elif((self._neighbouringZoneUp == None and vector.v <= self._zMin) or
                 (self._neighbouringZoneDown == None and self._zMax <= vector.v)):
                return True
        elif(self._zMin <= vector.v and vector.v <= self._zMax):
            if((self._neighbouringZoneLeft == None and vector.u <= self._xMin) or
               (self._neighbouringZoneRight == None and self._xMax <= vector.u)):
                return True
        elif((self._neighbouringZoneLeft == None and vector.u <= self._xMin) and 
             ((self._neighbouringZoneUp == None and vector.v <= self._zMin) or (self._neighbouringZoneDown == None and self._zMax <= vector.v))):
            return True
        elif((self._neighbouringZoneRight == None and self._xMax <= vector.u) and 
             ((self._neighbouringZoneUp == None and vector.v <= self._zMin) or (self._neighbouringZoneDown == None and self._zMax <= vector.v))):
            return True
            
        return False

##########################         
    def _addToUpNeighbour(self, boid):
        if(self._neighbouringZoneUp != None):
            self._neighbouringZoneUp.boidList.append(boid)
    
    def _addToUpLeftNeighbour(self, boid):
        if(self._neighbouringZoneUp != None):
            self._neighbouringZoneUp._addToLeftNeighbour(boid)
            
    def _addToUpRightNeighbour(self, boid):
        if(self._neighbouringZoneUp != None):
            self._neighbouringZoneUp._addToRightNeighbour(boid)     
    
    def _addToLeftNeighbour(self, boid):
        if(self._neighbouringZoneLeft != None):
            self._neighbouringZoneLeft.boidList.append(boid)
    
    def _addToRightNeighbour(self, boid):
        if(self._neighbouringZoneRight != None):
            self._neighbouringZoneRight.boidList.append(boid)
        
    def _addToDownNeighbour(self, boid):
        if(self._neighbouringZoneDown != None):
            self._neighbouringZoneDown.boidList.append(boid)
    
    def _addToDownLeftNeighbour(self, boid):
        if(self._neighbouringZoneDown != None):
            self._neighbouringZoneDown._addToLeftNeighbour(boid)
            
    def _addToDownRightNeighbour(self, boid):
        if(self._neighbouringZoneDown != None):
            self._neighbouringZoneDown._addToRightNeighbour(boid)        

##########################         
    def updateBoidPosition(self, boid):
        """Returns True if boidAgent is located within this zone, False otherwise.
        
        Will also add the agent to neighbouring zones if the agent fall in the overlap
        region between the two zones."""
        
        if(self._containsVectorPosition(boid.currentPosition)):
            self.boidList.append(boid)
            overlap = boidConstants.mainRegionSize()
            posX = boid.currentPosition.x
            posZ = boid.currentPosition.z
            
            
            if(posX < self._xMin + overlap):
                self._addToLeftNeighbour(boid)
                if(posZ < self._zMin + overlap):
                    self._addToUpNeighbour(boid)
                    self._addToUpLeftNeighbour(boid)
                    return True
                elif(posZ > self._zMax - overlap):
                    self._addToDownNeighbour(boid)
                    self._addToDownLeftNeighbour(boid)
                    return True
            elif(posX > self._xMax - overlap):
                self._addToRightNeighbour(boid)
                if(posZ < self._zMin + overlap):
                    self._addToUpNeighbour(boid)
                    self._addToUpRightNeighbour(boid)
                    return True
                elif(posZ > self._zMax - overlap):
                    self._addToDownNeighbour(boid)
                    self._addToDownRightNeighbour(boid)
                    return True     
                
            if(posZ < self._zMin + overlap):
                self._addToUpNeighbour(boid)
            elif(posZ > self._zMax - overlap):
                self._addToDownNeighbour(boid)
                
            return True
        else:
            return False

# END OF CLASS _BoidZone
##########################################################   


##########################################################   
class BoidZoneGraph(BoidObject):
    """On each frame update, every agent needs to be checked against every other agent to see 
    if they are neighbouring, crowding, colliding etc.  If this is implemented in a straightforward
    way without any optimisation then the algorithm is of Order (n ^2) - very slow.
    Zones help by dividing the grid up into regions, each of which contain a list of agents within
    that region,  which can then be used to prune the queries right down - only agents within the same region
    need to be checked against each other.
    
    Operation: on each frame update, updateAllBoidPositions should be called, this will update the 
    zones with the current agent positions on the grid.  Subsequently, for each agent, a call to
    regionListForBoid will return a list of other agents which should be checked against for proximity.
    
    TODO - bit of a crude implementation at present. Might be worth looking into doing it as a quadtree
    (or octree as option if bringing in height dimension also)...?
    """
    
    def __init__(self, negativeIndicesLocator, positiveIndicesLocator):
        """Constructs a zone system over the specified area with a zone resolution as 
        determined by boidConstants.preferredZoneSize.
        
        Negative and positive indicesLocator arguments must be Pymel Locator objects
        representing the opposing corners of the grid area which the zones are to cover."""
        
        self._zoneList = []
        self._boidZoneLookup = {}
        self._earlyHitListLookup = {}
        
        self.lowerBoundsVector = boidUtil.boidVectorFromLocator(negativeIndicesLocator)
        self.upperBoundsVector = boidUtil.boidVectorFromLocator(positiveIndicesLocator)
        
        sizeX = self.upperBoundsVector.x - self.lowerBoundsVector.x
        sizeZ = self.upperBoundsVector.z - self.lowerBoundsVector.z

        resolutionX = int(sizeX / boidConstants.preferredZoneSize())
        resolutionZ = int(sizeZ / boidConstants.preferredZoneSize())
        
        stepSizeX = sizeX / float(resolutionX)
        stepSizeZ = sizeZ / float(resolutionZ)
        
        while((stepSizeX / 2) < boidConstants.mainRegionSize() and resolutionX > 1):
            print ("WARNING - ZONE X-RESOLUTION TOO HIGH, REDUCING...")
            resolutionX -= 1
            stepSizeX = sizeX / resolutionX
        while((stepSizeZ / 2) < boidConstants.mainRegionSize() and resolutionZ > 1):
            print ("WARNING - ZONE Z-RESOLUTION TOO HIGH, REDUCING...")
            resolutionZ -= 1
            stepSizeX = sizeZ / resolutionZ        
        
        xMinBase = self.lowerBoundsVector.x
        xMaxBase = xMinBase + stepSizeX 
        zMin = self.lowerBoundsVector.z
        zMax = zMin + stepSizeZ
        zoneId = 0
        
        for i in range(0, resolutionZ):
            xMin = xMinBase
            xMax = xMaxBase
            
            for j in range(0, resolutionX):
                newZone = _BoidZone(zoneId, xMin, xMax, zMin, zMax)
                self._zoneList.append(newZone)

                if(j > 0):
                    idxA = (i*resolutionX) + j-1
                    neighbourLeft = self._zoneList[idxA]
                    neighbourLeft._neighbouringZoneRight = newZone
                    newZone._neighbouringZoneLeft = neighbourLeft
                if(i > 0):
                    idxB = ((i-1)*resolutionX) + j
                    neighbourUp = self._zoneList[idxB]
                    neighbourUp._neighbouringZoneDown = newZone
                    newZone._neighbouringZoneUp = neighbourUp
                
                xMin += stepSizeX
                xMax += stepSizeX
                zoneId += 1
                
            zMin += stepSizeZ
            zMax += stepSizeZ

        print("Created new zone graph, resolution = %dx%d (zone size=%.2fx%.2f)\nX=%.2f to %2f,Z=%.2f to %.2f" % 
              (resolutionX, resolutionZ, stepSizeX, stepSizeZ, xMinBase, xMax - stepSizeX, self.lowerBoundsVector.z, zMax - stepSizeZ))        

##########################             
    def __str__(self):
        setup = ""
        ret = ""
        for zone in self._zoneList:
            setup += ("%s\n" % zone.neighbouringZonesStr())
            ret += ("%s\n" % zone)
        return ("%d zones:\n%s\n%s\nlookupCount:%d" % (len(self._zoneList), setup, ret, len(self._boidZoneLookup)))

##########################  
    def _getUseEarlyHitListLookup(self):
        """True if we can use the hitList lookup (see _BoidZone class, above), False otherwise."""
        return self._earlyHitListLookup == None
    def _setUseEarlyHitListLookup(self, value):
        if(value):
            self._earlyHitListLookup = {}
        else:
            self._earlyHitListLookup = None
    useEarlyHitListLookup = property(_getUseEarlyHitListLookup, _setUseEarlyHitListLookup)
    

##########################      
    def resetZones(self):
        for zone in self._zoneList:
            del zone.boidList[:]       

##########################              
    def updateBoidPosition(self, boid):
        """Updates the zones with the position of the given boid.
        Removing it from a previous zone if necessary, and adding it to a new one if necessary."""
        
        foundZone = False
        if(self.useEarlyHitListLookup and boid.particleId in self._earlyHitListLookup):
            hitListLookup = self._earlyHitListLookup[boid.particleId]
            for zone in hitListLookup:
                if(zone.updateBoidPosition(boid)):
                    self._boidZoneLookup[boid.particleId] = zone    
                    self._earlyHitListLookup[boid.particleId] = zone._earlyHitList
                    foundZone = True
                    break
            if(not foundZone):
                del self._earlyHitListLookup[boid.particleId]
                
        if(not foundZone):
            for zone in self._zoneList:
                if(zone.updateBoidPosition(boid)):
                    self._boidZoneLookup[boid.particleId] = zone
                    foundZone = True
                    
                    if(self.useEarlyHitListLookup):
                        self._earlyHitListLookup[boid.particleId] = zone._earlyHitList
                    break        
                
        if(not foundZone):
            print("XXXX WARNING = NOT FOUND ZONE FOR BOID %s" % boid)

 
##########################   
    def updateAllBoidPositions(self, boidsList):
        """Updates all zones with the positions of the boids in the given list."""
        
        self.resetZones()
        
        for boid in boidsList:
            self.updateBoidPosition(boid)

##########################              
    def regionListForBoid(self, boid):
        """Returns a list of other boids within the same zone (or neighbouring zones within the overlap
        area) as the boid given."""
        
        if(boid.particleId in self._boidZoneLookup):
            zone = self._boidZoneLookup[boid.particleId]    
            return zone.boidList
        else:
            print("WARNING - NO ZONE FOUND FOR BOID #%s" % boid)
            emptyList = []
            return emptyList
        
        
##########################################################   