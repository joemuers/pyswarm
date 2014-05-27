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


import ConfigParser

from pyswarm.pyswarmObject import PyswarmObject
import pyswarm.utils.general as util
import pyswarm.utils.fileLocations as fl

import pyswarm.attributes.globalAttributeGroup as ga
import pyswarm.attributes.agentPerceptionAttributeGroup as apa
import pyswarm.attributes.agentMovementAttributeGroup as ama

import pyswarm.attributes.behaviour.classicBoidAttributeGroup as cb
import pyswarm.attributes.behaviour.worldWarZAttributeGroup as wwz
import pyswarm.attributes.behaviour.followPathAttributeGroup as fp



##########################################
class AttributeGroupsController(PyswarmObject):
    
    def __init__(self, particleShapeNode, saveSceneMethod, boundingLocators=None):
        
        self._globalAttributeGroup = ga.GlobalAttributeGroup(particleShapeNode, saveSceneMethod, boundingLocators)
        self._agentMovementAttributeGroup = ama.AgentMovementAttributeGroup()
        self._agentPerceptionAttributeGroup = apa.AgentPerceptionAttributeGroup()
        
        defaultBehaviourId = cb.ClassicBoidAttributeGroup.BehaviourTypeName()
        defaultBehaviourAttributeGroup = cb.ClassicBoidAttributeGroup(defaultBehaviourId, self._globalAttributeGroup)
        self._behaviourAttributeGroupsList = [defaultBehaviourAttributeGroup]        
        self._globalAttributeGroup.setDefaultBehaviourAttributeGroup(defaultBehaviourAttributeGroup)
        
        self.restoreDefaultAttributeValuesFromFile()
        self._notifyOnBehavioursListChanged()

#############################        
    def __str__(self):
        stringsList = ["Behaviours: "]
        stringsList.extend([("\"%s\", " % attributes.behaviourId) for attributes in self._allAttributeGroups()])
        stringsList.append("  (default=\"%s\")" % self.defaultBehaviourId)
        
        return ''.join(stringsList)
 
#######   
    def _getMetaStr(self):
        stringsList = ["Values: "]
        stringsList.extend([("<\t%s\n>\n" % attributes.metaStr) for attributes in self._allAttributeGroups()])
        
        return ''.join(stringsList)
 
#####################   
    def _getGlobalAttributeGroup(self):
        return self._globalAttributeGroup
    globalAttributeGroup = property(_getGlobalAttributeGroup)

#####################    
    def _getDefaultBehaviourId(self):
        return self._globalAttributeGroup.defaultBehaviourId
    defaultBehaviourId = property(_getDefaultBehaviourId)
    
########
    def _getAgentMovementAttributeGroup(self):
        return self._agentMovementAttributeGroup
    agentMovementAttributeGroup = property(_getAgentMovementAttributeGroup)
    
########
    def _getAgentPerceptionAttributeGroup(self):
        return self._agentPerceptionAttributeGroup
    agentPerceptionAttributeGroup = property(_getAgentPerceptionAttributeGroup)

########
    def getBehaviourAttributeGroupWithId(self, behaviourId):
        for attributes in self._behaviourAttributeGroupsList:
            if(attributes.behaviourId == behaviourId):
                return attributes
        
        raise ValueError("Unrecognised behaviour id: %s" % behaviourId)

#####################
    def _allAttributeGroups(self):
        groupsList = [self.globalAttributeGroup, self.agentMovementAttributeGroup, self.agentPerceptionAttributeGroup] 
        groupsList.extend(self._behaviourAttributeGroupsList)
        
        return groupsList
 
#####################   
    def behaviourTypeNamesList(self):
        return sorted(self._getBehaviourTypeNameToConstructorLookup().keys())
    
#####################    
    def onFrameUpdated(self):
        for attributes in self._allAttributeGroups():
            attributes.onFrameUpdated()
            
########
    def onCalculationsCompleted(self):
        for attributes in self._allAttributeGroups():
            attributes.onCalculationsCompleted()

#####################            
    def showPreferencesWindow(self):
        self.globalAttributeGroup.showGlobalPreferencesWindow()
            
#####################
    def _getNewBehaviourIdForAttibutesClass(self, attributesClass):
        currentMaxIndex = -1
        titleStem = attributesClass.BehaviourTypeName()
        
        for attributes in filter(lambda attbs: type(attbs) == attributesClass, self._behaviourAttributeGroupsList):
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
        behaviourIDsList = [at.behaviourId for at in self._behaviourAttributeGroupsList]
        defaultBehaviourId = self.defaultBehaviourId
        
        for attributes in self._behaviourAttributeGroupsList:
            attributes.onBehaviourListUpdated(behaviourIDsList, defaultBehaviourId)
            
#####################       
    def _addNewBehaviourAttributeGroup(self, newBehaviourAttributeGroup):
        self.restoreDefaultAttributeValuesFromFile(newBehaviourAttributeGroup)
        self._behaviourAttributeGroupsList.append(newBehaviourAttributeGroup)
        
        self._notifyOnBehavioursListChanged()
 
#####################      
    def _getBehaviourTypeNameToConstructorLookup(self):
        """IMPORTANT - All defined behaviours *must* be included in this method!"""
        lookup = { cb.ClassicBoidAttributeGroup.BehaviourTypeName() : self.addClassicBoidAttributeGroup,
                   wwz.WorldWarZAttributeGroup.BehaviourTypeName() : self.addWorldWarZAttributeGroup,
                   fp.FollowPathAttributeGroup.BehaviourTypeName() : self.addFollowPathAttributeGroup }
        
        return lookup

########
    def addBehaviourForTypeName(self, behaviourTypeName):
        typeNameToConstructorLookup = self._getBehaviourTypeNameToConstructorLookup()
        
        if(behaviourTypeName in typeNameToConstructorLookup):
            return typeNameToConstructorLookup[behaviourTypeName]()
        else:
            raise ValueError("Unrecognised behaviour type name: %s" % behaviourTypeName)
 
########       
    def addClassicBoidAttributeGroup(self):
        behaviourId = self._getNewBehaviourIdForAttibutesClass(cb.ClassicBoidAttributeGroup)
        newBehaviourAttributeGroup = cb.ClassicBoidAttributeGroup(behaviourId, self._globalAttributeGroup)
        self._addNewBehaviourAttributeGroup(newBehaviourAttributeGroup)
        
        return newBehaviourAttributeGroup
 
########   
    def addWorldWarZAttributeGroup(self, wallLipGoal=None, basePyramidGoalHeight=None, finalGoal=None):
        behaviourId = self._getNewBehaviourIdForAttibutesClass(wwz.WorldWarZAttributeGroup)
        newBehaviourAttributeGroup = wwz.WorldWarZAttributeGroup(behaviourId, self._globalAttributeGroup,
                                                                    wallLipGoal, basePyramidGoalHeight, finalGoal)
        self._addNewBehaviourAttributeGroup(newBehaviourAttributeGroup)
        
        return newBehaviourAttributeGroup

########    
    def addFollowPathAttributeGroup(self, pathCurve=None):
        behaviourId = self._getNewBehaviourIdForAttibutesClass(fp.FollowPathAttributeGroup)
        newBehaviourAttributeGroup = fp.FollowPathAttributeGroup(behaviourId, pathCurve)
        self._addNewBehaviourAttributeGroup(newBehaviourAttributeGroup)
        
        return newBehaviourAttributeGroup

########
    def removeBehaviour(self, behaviourAttributeGroup):
        if(isinstance(behaviourAttributeGroup, basestring)):
            behaviourAttributeGroup = self.getBehaviourAttributeGroupWithId(behaviourAttributeGroup)
        
        if(behaviourAttributeGroup.behaviourId == self.defaultBehaviourId):
            raise ValueError("Default behaviour \"%s\" cannot be deleted." % self.defaultBehaviourId)
        else:
            self._behaviourAttributeGroupsList.remove(behaviourAttributeGroup)
            self._notifyOnBehavioursListChanged()
            
        return behaviourAttributeGroup
    
#####################
    def changeDefaultBehaviour(self, newDefaultBehaviourId):
        if(newDefaultBehaviourId == self.defaultBehaviourId):
            util.LogWarning("\"%s\" is already the default - no changes made." % newDefaultBehaviourId)
            return False
        else:
            newDefaultBehaviourAttributeGroup = self.getBehaviourAttributeGroupWithId(newDefaultBehaviourId)
            self._globalAttributeGroup.setDefaultBehaviourAttributeGroup(newDefaultBehaviourAttributeGroup)
            self._notifyOnBehavioursListChanged()
            
            return True
    
#####################
    def purgeRepositories(self):
        for attributes in self._allAttributeGroups():
            attributes.purgeDataBlobRepository()
        
#####################   
    def restoreDefaultAttributeValuesFromFile(self, group=None):
        if(isinstance(group, basestring)):
            group = self.getBehaviourAttributeGroupWithId(group)
            
        configReader = ConfigParser.ConfigParser()
        configReader.optionxform = str 
        filePath = fl.DefaultAttributeValuesLocation()      
          
        if(configReader.read(filePath)):
            util.LogDebug("Parsing file \'%s\' for default values..." % filePath)
            
            groupsList = self._allAttributeGroups() if(group is None) else [group]
            for groupIterator in groupsList:
                result = groupIterator.getDefaultsFromConfigReader(configReader)
                if(not result):
                    util.LogInfo("Found new attributes - writing \"%s\" group to defaults file..." 
                                 % groupIterator.BehaviourTypeName())
                    self.makeCurrentAttributeValuesDefault(groupIterator)
        else:
            util.LogWarning("Could not find default attribute values file %s, creating a new one..." % filePath)
            self.makeCurrentAttributeValuesDefault()
            
        util.LogDebug("Finished parsing default values.")
    
########
    def makeCurrentAttributeValuesDefault(self, group=None):
        if(isinstance(group, basestring)):
            group = self.getBehaviourAttributeGroupWithId(group)
            
        filePath = fl.DefaultAttributeValuesLocation()
        configWriter = ConfigParser.ConfigParser()
        configWriter.optionxform = str
        configWriter.read(filePath)
        writtenAttributeTypesSet = set()
        
        if(group is None):
            for groupIterator in self._allAttributeGroups():
                groupType = type(groupIterator)
                
                if(groupType not in writtenAttributeTypesSet):
                    groupIterator.setDefaultsToConfigWriter(configWriter)
                    writtenAttributeTypesSet.add(groupType)
                else:
                    util.LogInfo("Found multiple instances of behaviour type: \"%s\". "
                                 "Default values taken from first instance only." 
                                 % groupIterator.BehaviourTypeName())
        else:
            group.setDefaultsToConfigWriter(configWriter)
                
        defaultsFile = open(filePath, "w")   
        configWriter.write(defaultsFile)
        defaultsFile.close()
        
        util.LogInfo("Saved default values to file: %s." % filePath)
        
    
# END OF CLASS
####################################