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


from boidBaseObject import BoidBaseObject

import globalAttributes as ga
import agentPerceptionAttributes as apa
import agentMovementAttributes as ama
import classicBoidBehaviourAttributes as cbba
import goalDrivenBehaviourAttributes as gdba
import followPathBehaviourAttributes as fpba
import boidTools.util as util
import boidResources.fileLocations as fl

import ConfigParser



##########################################
class AttributesController(BoidBaseObject):
    
    def __init__(self, particleShapeNode, saveSceneMethod, boundingLocators=None):
        
        self._globalAttributes = ga.GlobalAttributes(particleShapeNode, saveSceneMethod, boundingLocators)
        self._agentMovementAttributes = ama.AgentMovementAttributes()
        self._agentPerceptionAttributes = apa.AgentPerceptionAttributes()
        
        defaultBehaviourId = cbba.ClassicBoidBehaviourAttributes.BehaviourTypeName()
        defaultBehaviourAttributes = cbba.ClassicBoidBehaviourAttributes(defaultBehaviourId, self._globalAttributes)
        self._behaviourAttributesList = [defaultBehaviourAttributes]        
        self._globalAttributes.setDefaultBehaviourAttributes(defaultBehaviourAttributes)
        
        self.restoreDefaultAttributeValuesFromFile()
        self._notifyOnBehavioursListChanged()

#############################        
    def __str__(self):
        stringsList = ["Behaviours: "]
        stringsList.extend([("\"%s\", " % attributes.behaviourId) for attributes in self._allSections()])
        stringsList.append("  (default=\"%s\")" % self.defaultBehaviourId)
        
        return ''.join(stringsList)
 
#######   
    def _getMetaStr(self):
        stringsList = ["Values: "]
        stringsList.extend([("<\t%s\n>\n" % attributes.metaStr) for attributes in self._allSections()])
        
        return ''.join(stringsList)
 
#####################   
    def _getGlobalAttributes(self):
        return self._globalAttributes
    globalAttributes = property(_getGlobalAttributes)

#####################    
    def _getDefaultBehaviourId(self):
        return self._globalAttributes.defaultBehaviourId
    defaultBehaviourId = property(_getDefaultBehaviourId)
    
########
    def _getAgentMovementAttributes(self):
        return self._agentMovementAttributes
    agentMovementAttributes = property(_getAgentMovementAttributes)
    
########
    def _getAgentPerceptionAttributes(self):
        return self._agentPerceptionAttributes
    agentPerceptionAttributes = property(_getAgentPerceptionAttributes)

########
    def getBehaviourAttributesWithId(self, behaviourId):
        for attributes in self._behaviourAttributesList:
            if(attributes.behaviourId == behaviourId):
                return attributes
        
        raise ValueError("Unrecognised behaviour id: %s" % behaviourId)

#####################
    def _allSections(self):
        sectionsList = [self.globalAttributes, self.agentMovementAttributes, self.agentPerceptionAttributes] 
        sectionsList.extend(self._behaviourAttributesList)
        
        return sectionsList
 
#####################   
    def behaviourTypeNamesList(self):
        return sorted(self._getBehaviourTypeNameToConstructorLookup().keys())
    
#####################    
    def onFrameUpdated(self):
        for attributes in self._allSections():
            attributes.onFrameUpdated()
            
########
    def onCalculationsCompleted(self):
        for attributes in self._allSections():
            attributes.onCalculationsCompleted()

#####################            
    def showPreferencesWindow(self):
        self.globalAttributes.showGlobalPreferencesWindow()
            
#####################
    def _getNewBehaviourIdForAttibutesClass(self, attributesClass):
        currentMaxIndex = -1
        titleStem = attributesClass.BehaviourTypeName()
        
        for attributes in filter(lambda attbs: type(attbs) == attributesClass, self._behaviourAttributesList):
            try:
                indexSuffix = int(attributes.behaviourId.replace(titleStem, ""))
                currentMaxIndex = max(indexSuffix, currentMaxIndex)
            except:
                if(currentMaxIndex == -1):
                    currentMaxIndex = 0
        
        if(currentMaxIndex >= 0):
            return ("%s_%d" % (titleStem, currentMaxIndex + 1))
        else:
            return titleStem

#####################        
    def _notifyOnBehavioursListChanged(self):
        behaviourIDsList = [at.behaviourId for at in self._behaviourAttributesList]
        defaultBehaviourId = self.defaultBehaviourId
        
        for attributes in self._behaviourAttributesList:
            attributes.onBehaviourListUpdated(behaviourIDsList, defaultBehaviourId)
            
#####################       
    def _addNewBehaviourAttributes(self, newBehaviourAttributes):
        self.restoreDefaultAttributeValuesFromFile(newBehaviourAttributes)
        self._behaviourAttributesList.append(newBehaviourAttributes)
        
        self._notifyOnBehavioursListChanged()
 
#####################      
    def _getBehaviourTypeNameToConstructorLookup(self):
        """IMPORTANT - All defined behaviours *must* be included in this method!"""
        lookup = { cbba.ClassicBoidBehaviourAttributes.BehaviourTypeName() : self.addClassicBoidAttributes,
                   gdba.GoalDrivenBehaviourAttributes.BehaviourTypeName() : self.addGoalDrivenAttributes,
                   fpba.FollowPathBehaviourAttributes.BehaviourTypeName() : self.addFollowPathAttributes }
        
        return lookup

########
    def addBehaviourForTypeName(self, behaviourTypeName):
        typeNameToConstructorLookup = self._getBehaviourTypeNameToConstructorLookup()
        
        if(behaviourTypeName in typeNameToConstructorLookup):
            return typeNameToConstructorLookup[behaviourTypeName]()
        else:
            raise ValueError("Unrecognised behaviour type name: %s" % behaviourTypeName)
 
########       
    def addClassicBoidAttributes(self):
        behaviourId = self._getNewBehaviourIdForAttibutesClass(cbba.ClassicBoidBehaviourAttributes)
        newBehaviourAttributes = cbba.ClassicBoidBehaviourAttributes(behaviourId, self._globalAttributes)
        self._addNewBehaviourAttributes(newBehaviourAttributes)
        
        return newBehaviourAttributes
 
########   
    def addGoalDrivenAttributes(self, wallLipGoal=None, basePyramidGoalHeight=None, finalGoal=None):
        behaviourId = self._getNewBehaviourIdForAttibutesClass(gdba.GoalDrivenBehaviourAttributes)
        newBehaviourAttributes = gdba.GoalDrivenBehaviourAttributes(behaviourId, self._globalAttributes,
                                                                    wallLipGoal, basePyramidGoalHeight, finalGoal)
        self._addNewBehaviourAttributes(newBehaviourAttributes)
        
        return newBehaviourAttributes

########    
    def addFollowPathAttributes(self, pathCurve=None):
        behaviourId = self._getNewBehaviourIdForAttibutesClass(fpba.FollowPathBehaviourAttributes)
        newBehaviourAttributes = fpba.FollowPathBehaviourAttributes(behaviourId, pathCurve)
        self._addNewBehaviourAttributes(newBehaviourAttributes)
        
        return newBehaviourAttributes

########
    def removeBehaviour(self, behaviourAttributes):
        if(isinstance(behaviourAttributes, basestring)):
            behaviourAttributes = self.getBehaviourAttributesWithId(behaviourAttributes)
        
        if(behaviourAttributes.behaviourId == self.defaultBehaviourId):
            raise ValueError("Default behaviour \"%s\" cannot be deleted." % self.defaultBehaviourId)
        else:
            self._behaviourAttributesList.remove(behaviourAttributes)
            self._notifyOnBehavioursListChanged()
            
        return behaviourAttributes
    
#####################
    def changeDefaultBehaviour(self, newDefaultBehaviourId):
        if(newDefaultBehaviourId == self.defaultBehaviourId):
            util.LogWarning("\"%s\" is already the default - no changes made." % newDefaultBehaviourId)
            return False
        else:
            newDefaultBehaviourAttributes = self.getBehaviourAttributesWithId(newDefaultBehaviourId)
            self._globalAttributes.setDefaultBehaviourAttributes(newDefaultBehaviourAttributes)
            self._notifyOnBehavioursListChanged()
            
            return True
    
#####################
    def purgeRepositories(self):
        for attributes in self._allSections():
            attributes.purgeDataBlobRepository()
        
#####################   
    def restoreDefaultAttributeValuesFromFile(self, section=None):
        if(isinstance(section, basestring)):
            section = self.getBehaviourAttributesWithId(section)
            
        configReader = ConfigParser.ConfigParser()
        configReader.optionxform = str 
        filePath = fl.DefaultAttributeValuesLocation()      
          
        if(configReader.read(filePath)):
            util.LogDebug("Parsing file \'%s\' for default values..." % filePath)
            
            sectionsList = self._allSections() if(section is None) else [section]
            for sectionIterator in sectionsList:
                result = sectionIterator.getDefaultsFromConfigReader(configReader)
                if(not result):
                    util.LogInfo("Found new attributes - writing \"%s\" section to defaults file..." % sectionIterator.BehaviourTypeName())
                    self.makeCurrentAttributeValuesDefault(sectionIterator)
        else:
            util.LogWarning("Could not find default attribute values file %s, creating a new one..." % filePath)
            self.makeCurrentAttributeValuesDefault()
            
        util.LogDebug("Finished parsing default values.")
    
########
    def makeCurrentAttributeValuesDefault(self, section=None):
        if(isinstance(section, basestring)):
            section = self.getBehaviourAttributesWithId(section)
            
        filePath = fl.DefaultAttributeValuesLocation()
        configWriter = ConfigParser.ConfigParser()
        configWriter.optionxform = str
        configWriter.read(filePath)
        writtenAttributeTypesSet = set()
        
        if(section is None):
            for sectionIterator in self._allSections():
                sectionType = type(sectionIterator)
                
                if(sectionType not in writtenAttributeTypesSet):
                    sectionIterator.setDefaultsToConfigWriter(configWriter)
                    writtenAttributeTypesSet.add(sectionType)
                else:
                    util.LogInfo("Found multiple instances of behaviour type: \"%s\". \
Default values taken from first instance only." % sectionIterator.BehaviourTypeName())
        else:
            section.setDefaultsToConfigWriter(configWriter)
                
        defaultsFile = open(filePath, "w")   
        configWriter.write(defaultsFile)
        defaultsFile.close()
        
        util.LogInfo("Saved default values to file: %s." % filePath)
        
    
# END OF CLASS
####################################