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


from pyswarmObject import PyswarmObject
from attributes.attributeGroupObject import AttributesListener
import vectors.vector3 as v3
import tools.util as util

import itertools

#############################
class _Zone(PyswarmObject):
    
    def __init__(self, xMin, xMax, zMin, zMax):
        self.regionalSetsList = [set()]
        self.regionIterable = _ZoneRegionIteratable(self.regionalSetsList)
        
        self._xMin = xMin
        self._xMax = xMax
        self._zMin = zMin
        self._zMax = zMax
    
    ################    
    def __str__(self):
        return ("<xMin=%.2f, xMax=%.2f, zMin=%.2f, zMax=%.2f>" %
                (self._xMin, self._xMax, self._zMin, self._zMax))    
        
    ################
    def _getMetaStr(self):
        agentStringsList = [("\n\t%s" % agent) for agent in self.agentSet]
        return ("<xMin=%.2f, xMax=%.2f, zMin=%.2f, zMax=%.2f, count=%d\nagents=%s \n>" %
                (self._xMin, self._xMax, self._zMin, self._zMax, len(self.agentSet), "".join(agentStringsList)))    
        
    ################    
    def _getAgentSet(self):
        return self.regionalSetsList[0]
    agentSet = property(_getAgentSet)
    
    ################    
    def setNeighbouringZones(self, neighboursList):
        del self.regionalSetsList[1:]
        
        for zone in neighboursList:
            self.regionalSetsList.append(zone.agentSet)
    
    ################        
    def addNeighbouringZone(self, neighbour):
        if(neighbour not in self.regionalSetsList):
            self.regionalSetsList.append(neighbour.agentSet)
        else:
            raise ValueError
    
    ################
    def addNewAgent(self, agent):
        self.agentSet.add(agent)
    
    ################
    def removeAgent(self, agent):
        self.agentSet.remove(agent)

# END OF CLASS _Zone
##############################



##############################
class _ZoneRegionIteratable(object):
    
    def __init__(self, regionList):
        self._regionList = regionList

    def __iter__(self):
        return itertools.chain.from_iterable(self._regionList)

# END OF CLASS _ZoneRegionIterable
#############################
    
    
    
#############################
class ZoneGraph(PyswarmObject, AttributesListener):
    
    def __init__(self, attributeGroupsController):
        self._currentFrameIteration = 0
        
        self._globalAttributes = attributeGroupsController.globalAttributes
        self._lowerBoundsVector = v3.Vector3(self._globalAttributes.lowerBounds)
        self._upperBoundsVector = v3.Vector3(self._globalAttributes.upperBounds)
        self._globalAttributes.addListener(self)
        
        self._perceptionAttributes = attributeGroupsController.agentPerceptionAttributeGroup
        self._zoneSize = self._perceptionAttributes.maxNeighbourhoodSize
        self._perceptionAttributes.addListener(self)
        
        self._needsRebuild = True
        
        self._zoneSizeReciprocal = 0.0
        self._xZoneOrigin = 0.0
        self._zZoneOrigin = 0.0
        self._resolutionX = 0.0
        self._resolutionZ = 0.0
        
        self._zoneMap = []
        self._previousKeyLookup = {}
        self._useSpatialHashing = True
        
        self.rebuildMapIfNecessary()

########################################            
    def _makeZonesNeighbours(self, zoneA, zoneB):
        zoneA.addNeighbouringZone(zoneB)
        zoneB.addNeighbouringZone(zoneA)

########################################        
    def rebuildMapIfNecessary(self):
        if(self._needsRebuild):
            zoneSize = self._zoneSize
            sizeX = self._upperBoundsVector.x - self._lowerBoundsVector.x
            sizeZ = self._upperBoundsVector.z - self._lowerBoundsVector.z
            resolutionX = int((sizeX / zoneSize) + 1)
            resolutionZ = int((sizeZ / zoneSize) + 1)
            overspillX = ((resolutionX * zoneSize) - sizeX) / 2
            overspillZ = ((resolutionZ * zoneSize) - sizeZ) / 2
            
            self._zoneSizeReciprocal = 1.0 / float(zoneSize)
            self._xZoneOrigin = self._lowerBoundsVector.x - overspillX
            self._zZoneOrigin = self._lowerBoundsVector.z - overspillZ
            self._resolutionX = resolutionX
            self._resolutionZ = resolutionZ
            
            self._zoneMap = []
            self._previousKeyLookup = {}
            self._useSpatialHashing = True
            
            if(resolutionX == 1 and resolutionZ == 1):
                self._useSpatialHashing = False
                self._zoneMap = []
                
                util.LogWarning("Grid too small or agent neighbourhood region too large. Agent lookups will NOT be optimised.")
            else:
                zMinBase = self._zZoneOrigin
                zMaxBase = zMinBase + zoneSize
                xMin = self._xZoneOrigin
                xMax = xMin + zoneSize
                
                for xIndex in range(resolutionX): # enclosing iteration == x-axis
                    zMin = zMinBase
                    zMax = zMaxBase
                    currentRowZ = []
                    previousRowZ = self._zoneMap[xIndex-1] if(xIndex > 0) else None
                    
                    for zIndex in range(resolutionZ):  # nested iteration == z-axis
                        newZone = _Zone(xMin, xMax, zMin, zMax)
                        if(previousRowZ is not None):
                            if(zIndex > 0): 
                                self._makeZonesNeighbours(newZone, previousRowZ[zIndex-1])
                                
                            self._makeZonesNeighbours(newZone, previousRowZ[zIndex])
    
                            if(zIndex < resolutionZ-1): 
                                self._makeZonesNeighbours(newZone, previousRowZ[zIndex+1])
                        if(zIndex > 0):
                            self._makeZonesNeighbours(newZone, currentRowZ[zIndex-1])
                        
                        zMin += zoneSize
                        zMax += zoneSize
                        
                        currentRowZ.append(newZone)
                    
                    self._zoneMap.append(currentRowZ)
                    xMin += zoneSize
                    xMax += zoneSize
                            
                util.LogDebug("Rebuilt ZoneGraph - res= %dx%d (zone size=%.2f)\nX=%.2f to %2f,Z=%.2f to %.2f" %
                    (self._resolutionX, self._resolutionZ, self._zoneSize, 
                     self._xZoneOrigin, xMax - zoneSize, self._zZoneOrigin, zMax - zoneSize))
                
                self._needsRebuild = False
#         margin = 0
#         import vectors.vector3 as v3
#         vecA = v3.Vector3(zoneA._xMin + margin, 0, zoneA._zMin + margin)
#         vecB = v3.Vector3(zoneB._xMin + margin, 0, zoneB._zMin + margin)
#         
#         print("zone%s:%s NOW NEIGHBOURS zone%s:%s" % 
#               (self._spatialKeyFromVector(vecA), zoneA, self._spatialKeyFromVector(vecB), zoneB))

########################################            
    def __str__(self):
        if(self._useSpatialHashing):
            zoneStringsList = []
            for xIndex, zArray in enumerate(self._zoneMap):
                for zIndex, zone in enumerate(zArray):
                    zoneStringsList.append("(%d,%d)=%s\n" % (xIndex, zIndex, zone))
            return "".join(zoneStringsList)
        else:
            return "UNOPTIMISED... Agents list: ".join([(("%s, " % agent) for agent in self._zoneMap)])
        
########################################
    def _getMetaStr(self):
        if(self._useSpatialHashing):
            zoneStringsList = []
            for xIndex, zArray in enumerate(self._zoneMap):
                for zIndex, zone in enumerate(zArray):
                    zoneStringsList.append("(%d,%d)=%s\n" % (xIndex, zIndex, zone.metaStr))
            return "".join(zoneStringsList)
        else:
            return "UNOPTIMISED... Agents list: ".join([(("%s, " % agent) for agent in self._zoneMap)])

########################################        
    def onAttributeChanged(self, sectionObject, attributeName):
        if(sectionObject == self._globalAttributes):
            if(self._lowerBoundsVector != self._globalAttributes.lowerBounds or
               self._upperBoundsVector != self._globalAttributes.upperBounds):
                
                self._lowerBoundsVector = v3.Vector3(self._globalAttributes.lowerBounds)
                self._upperBoundsVector = v3.Vector3(self._globalAttributes.upperBounds)
                self._needsRebuild = True
        elif(sectionObject == self._perceptionAttributes):
            if(self._zoneSize != self._perceptionAttributes.maxNeighbourhoodSize):
                self._zoneSize = self._perceptionAttributes.maxNeighbourhoodSize
                self._needsRebuild = True

########################################       
    def updateAgentPosition(self, agent):
        if(self._useSpatialHashing):
            spatialKey = self._spatialKeyFromVector(agent.currentPosition)
            previousSpatialKey = self._previousKeyLookup.get(agent.agentId)
            
            if(spatialKey != previousSpatialKey):
                agentZone = self._zoneForSpatialKey(spatialKey)
                agentZone.addNewAgent(agent)
                
                if(previousSpatialKey is not None):
                    previousZone = self._zoneForSpatialKey(previousSpatialKey)
                    previousZone.removeAgent(agent)

                self._previousKeyLookup[agent.agentId] = spatialKey
            
########################################                
    def updateAllAgentPositions(self, agentsList):
        if(self._useSpatialHashing):
            for agent in agentsList:
                self.updateAgentPosition(agent)
                
########################################                
    def nearbyAgentsIterableForAgent(self, agent):
        if(self._useSpatialHashing):
            spatialKey = self._spatialKeyFromVector(agent.currentPosition)
            currentZone = self._zoneForSpatialKey(spatialKey)

            return currentZone.regionIterable
        else:
            return self._zoneMap

########################################                
    def removeAgent(self, agent):
        if(self._useSpatialHashing):
            spatialKey = self._previousKeyLookup.get(agent.agentId)
            zone = self._zoneForSpatialKey(spatialKey)
            zone.removeAgent(agent)
        else:
            self._zoneMap.remove(agent)

########################################        
    def _zoneForSpatialKey(self, key):
        xRow = self._zoneMap[key[0]]
        return xRow[key[1]]
                
########################################            
    def _spatialKeyFromVector(self, vector):
        return self._spatialKeyFromCoords(vector.x, vector.z)

########################################        
    def _spatialKeyFromCoords(self, xCoord, zCoord):
        roundingErrorCorrection = 0.00000001
        
        xNormalised = (xCoord - self._xZoneOrigin) * self._zoneSizeReciprocal
        xNormalised = int(xNormalised + roundingErrorCorrection)
        if(xNormalised < 0):    
            xNormalised = 0
        elif(xNormalised >= self._resolutionX):    
            xNormalised = self._resolutionX - 1
        
        zNormalised = (zCoord - self._zZoneOrigin)  * self._zoneSizeReciprocal
        zNormalised = int(zNormalised + roundingErrorCorrection)
        if(zNormalised < 0):    
            zNormalised = 0
        elif(zNormalised >= self._resolutionZ):    
            zNormalised = self._resolutionZ -1

        key = (xNormalised, zNormalised)
        
        return key
                       
## END OF CLASS - ZoneGraph
############################################