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
    
    def __init__(self, particleShapeNode, sceneBounds1=None, sceneBounds2=None):
#         self._leaderSelectMethod = leaderSelectMethod
        
        self._globalAttributes = ga.GlobalAttributes(particleShapeNode, sceneBounds1, sceneBounds2)
        self._agentMovementAttributes = ama.AgentMovementAttributes()
        self._agentPerceptionAttributes = apa.AgentPerceptionAttributes()
        
        defaultBehaviourId = cbba.ClassicBoidBehaviourAttributes.BehaviourTypeName()
        self.defaultBehaviourAttributes = cbba.ClassicBoidBehaviourAttributes(defaultBehaviourId)
        
        self._behaviourAttributesList = [self.defaultBehaviourAttributes]
        
        self.restoreDefaultAttributeValuesFromFile()
        self._notifyOnBehavioursListChanged()

#############################        
    def __str__(self):
        stringsList = ["Behaviours: "]
        stringsList.extend([("\"%s\", " % attributes.behaviourId) for attributes in self._allSections()])
        stringsList.append("  (default=\"%s\")" % self.defaultBehaviourAttributes.behaviourId)
        
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
    
########
    def _getAgentMovementAttributes(self):
        return self._agentMovementAttributes
    agentMovementAttributes = property(_getAgentMovementAttributes)
    
########
    def _getAgentPerceptionAttributes(self):
        return self._agentPerceptionAttributes
    agentPerceptionAttributes = property(_getAgentPerceptionAttributes)

########
    def behaviourAttributesForId(self, behaviourId):
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

#####################            
    def showPreferencesWindow(self):
        self.globalAttributes.showGlobalPreferencesWindow()
            
#####################
    def _getNewBehaviourIdForAttibutesClass(self, attributesClass):
        currentMaxIndex = -1
        titleStem = attributesClass.BehaviourTypeName() + '_'
        
        for attributes in filter(lambda at: at is not self.defaultBehaviourAttributes and 
                                 type(at) == attributesClass, 
                                 self._behaviourAttributesList):
            try:
                indexSuffix = int(attributes.behaviourId.replace(titleStem, ""))
                currentMaxIndex = max(indexSuffix, currentMaxIndex)
            except:
                pass
        
        return ("%s%d" % (titleStem, currentMaxIndex + 1))

#####################        
    def _notifyOnBehavioursListChanged(self):
        behaviourIDsList = [at.behaviourId for at in self._behaviourAttributesList]
        defaultId = self.defaultBehaviourAttributes.behaviourId
        
        for attributes in self._behaviourAttributesList:
            attributes.onBehaviourListUpdated(behaviourIDsList, defaultId)

#####################            
#     def _onRequestLeaderSelect(self, requestingAttributes, isChangeRequest):
#         self._leaderSelectMethod(requestingAttributes.behaviourId, isChangeRequest)
            
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
        newBehaviourAttributes = cbba.ClassicBoidBehaviourAttributes(behaviourId)
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
        if(isinstance(behaviourAttributes, str)):
            behaviourAttributes = self.behaviourAttributesForId(behaviourAttributes)
        
        if(behaviourAttributes is self.defaultBehaviourAttributes):
            raise ValueError("Default behaviour \"%s\" cannot be deleted." % self.defaultBehaviourAttributes.behaviourId)
        else:
            self._behaviourAttributesList.remove(behaviourAttributes)
            self._notifyOnBehavioursListChanged()
            
        return behaviourAttributes
    
#####################
    def purgeRepositories(self):
        for attributes in self._allSections():
            attributes.purgeDataBlobRepository()
        
#####################   
    def restoreDefaultAttributeValuesFromFile(self, section=None):
        if(isinstance(section, str)):
            section = self.behaviourAttributesForId(section)
            
        configReader = ConfigParser.ConfigParser()
        configReader.optionxform = str 
        filePath = fl.DefaultAttributeValuesLocation()      
          
        if(configReader.read(filePath)):
            util.LogDebug("Parsing file \'%s\' for default values..." % filePath)
            
            if(section is None):
                for sectionIterator in self._allSections():
                    sectionIterator.getDefaultsFromConfigReader(configReader)
            elif(not section.getDefaultsFromConfigReader(configReader)):
                util.LogInfo("Found new attributes - writing \"%s\" section to defaults file..." % section.BehaviourTypeName())
                self.makeCurrentAttributeValuesDefault(section)
        else:
            util.LogWarning("Could not find default attribute values file %s, creating a new one..." % filePath)
            self.makeCurrentAttributeValuesDefault()
            
        util.LogDebug("Finished parsing default values.")
    
########
    def makeCurrentAttributeValuesDefault(self, section=None):
        if(isinstance(section, str)):
            section = self.behaviourAttributesForId(section)
            
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