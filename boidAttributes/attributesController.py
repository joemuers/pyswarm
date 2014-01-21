from boidBaseObject import BoidBaseObject

import globalAttributes as ga
import agentPerceptionAttributes as apa
import agentMovementAttributes as ama
import classicBoidBehaviourAttributes as cbba
import goalDrivenBehaviourAttributes as gdba
import followPathBehaviourAttributes as fpba
import boidTools.uiBuilder as uib
import boidTools.util as util
import boidResources

import os
import weakref
import ConfigParser



_BEHAVIOURS_LIST_SECTION_NAME_ = "Behaviours List"
_BEHAVIOURS_LIST_OPTION_NAME_ = "List"
_BEHAVIOURS_LIST_DELIMITER_ = ","



##########################################
def _DefaultsAttributeValuesFilename():
    filePath = os.path.dirname(boidResources.__file__)
    return os.path.join(filePath, "attributeValueDefaults.ini")

##########################################
def _DefaultSaveLocation(particleShapeName):
    try:
        filePath = util.GetProjectRootDirectory()
        if(filePath is not None and filePath):
            filePath = os.path.join(filePath, "scripts")
            if(os.path.exists(filePath)):
                return os.path.join(filePath, ("%s_%s.ini" % (util.PackageName(), particleShapeName)))
    except:
        pass
    
    util.LogWarning("Could not find \"scripts\" folder in your Maya project database")
    return os.path.join(util.GetProjectWorkingDirectory(), ("%s_%s.ini" % (util.PackageName(), particleShapeName)))
    
##########################################



##########################################
class AttributesControllerDelegate(object):
    
    def _getParticleShapeName(self):
        raise NotImplemented
    
    def onNewBehaviourAttributesAdded(self, newBehaviourAttributes):
        raise NotImplemented
    
    def requestedAssignAgentsToBehaviour(self, behaviourAttributes):
        raise NotImplemented
    
    def requestedSelectAgentsWithBehaviour(self, behaviourAttributes, invertSelection):
        raise NotImplemented
    
    def requestedLeaderSelectForBehaviour(self, behaviourAttributes, isChangeSelectionRequest):
        raise NotImplemented
    
    def onBehaviourAttributesDeleted(self, deletedAttributes):
        raise NotImplemented
    
    def refreshInternals(self):
        raise NotImplemented
    
    def requestedQuitSwarmInstance(self):
        raise NotImplemented
    
# END OF CLASS - AttributesControllerDelegate
###########################################



##########################################
class AttributesController(BoidBaseObject):
    
    def __init__(self, delegate, sceneBounds1=None, sceneBounds2=None):
        if(not isinstance(delegate, AttributesControllerDelegate)):
            raise TypeError("Expected subclass of %s, got %s" (AttributesControllerDelegate, type(delegate)))
        else:
            self._delegate = weakref.ref(delegate)
            
            self.globalAttributes = ga.GlobalAttributes(sceneBounds1, sceneBounds2)
            self.agentMovementAttributes = ama.AgentMovementAttributes()
            self.agentPerceptionAttributes = apa.AgentPerceptionAttributes()
            defaultBehaviourTitle = cbba.ClassicBoidBehaviourAttributes.DefaultSectionTitle()
            self._defaultBehaviourAttributes = cbba.ClassicBoidBehaviourAttributes(defaultBehaviourTitle)
            
            self._behaviourAttributesList = [self._defaultBehaviourAttributes]
            self._agentSelectionWindow = None
            
            self._uiWindow = None
            self._uiComponentToAttributesLookup = {}
            self._tabLayout = None
            self._removeBehaviourMenu = None
            self._selectAgentsWithMenu = None
            self._selectAgentsNotWithMenu = None
            self._assignAgentsToMenu = None
            self._needsUiRebuild = False
            
            self._preferredSaveLocation = None            
            
#             if(not self._checkForPreviousSaveFile()):
#                 self.readDefaultAttributesFromFile()
#             self._notifyOnBehavioursListChanged()

#############################        
    def __str__(self):
        stringsList = ["Behaviours: "]
        stringsList.extend([("\"%s\", " % attributes.sectionTitle()) for attributes in self._allSections()])
        stringsList.append("  (default=\"%s\")" % self.defaultBehaviourAttributes.sectionTitle())
        
        return ''.join(stringsList)
    
    def _getMetaStr(self):
        stringsList = ["Values: "]
        stringsList.extend([("<\t%s\n>\n" % attributes.metaStr) for attributes in self._allSections()])
        
        return ''.join(stringsList)
    
#############################        
    def __getstate__(self):
        selfDict = self.__dict__.copy()
        selfDict["_delegate"] = self.delegate
        
        return selfDict
    
    def __setstate__(self, selfDict):
        self.__dict__.update(selfDict)
        if(self._delegate is not None):
            self._delegate = weakref.ref(self._delegate)
        
#############################
    def _getDelegate(self):
        return self._delegate() if(self._delegate is not None) else None
    delegate = property(_getDelegate)

#####################        
    def _getDefaultBehaviourAttributes(self):
        return self._defaultBehaviourAttributes
    defaultBehaviourAttributes = property(_getDefaultBehaviourAttributes)

#####################
    def _getUiVisible(self):
        return uib.WindowExists(self._uiWindow)
    uiVisible = property(_getUiVisible)
    
#####################
    def _allSections(self):
        sectionsList = [self.globalAttributes, self.agentMovementAttributes, self.agentPerceptionAttributes] 
        sectionsList.extend(self._behaviourAttributesList)
        
        return sectionsList
    
#####################    
    def onFrameUpdated(self):
        for attributes in self._allSections():
            attributes.onFrameUpdated()
            
#####################
    def _titleForAttributesClass(self, attributesClass):
        currentMaxIndex = -1
        defaultTitle = attributesClass.DefaultSectionTitle()
        
        for attributes in filter(lambda at: type(at) == attributesClass, self._behaviourAttributesList):
            try:
                indexSuffix = int(attributes.sectionTitle().replace(defaultTitle, ""))
                currentMaxIndex = max(indexSuffix, currentMaxIndex)
            except:
                if(currentMaxIndex == -1):
                    currentMaxIndex = 0
        
        if(currentMaxIndex >= 0):
            return ("%s%d" % (defaultTitle, currentMaxIndex + 1))
        else:
            return defaultTitle

#####################        
    def _notifyOnBehavioursListChanged(self):
        behaviourIDsList = [at.sectionTitle() for at in self._behaviourAttributesList]
        defaultId = self.defaultBehaviourAttributes.sectionTitle()
        
        for attributes in self._behaviourAttributesList:
            attributes.onBehaviourListUpdated(behaviourIDsList, defaultId)

#####################            
    def _onRequestLeaderSelectForBehaviourAttributes(self, attributes, isChangeSelectionRequest):
        self.delegate.requestedLeaderSelectForBehaviour(attributes, isChangeSelectionRequest)
            
#####################       
    def _addNewBehaviour(self, newBehaviourAttributes):
        self.restoreDefaultAttributeValuesFromFile(newBehaviourAttributes)
        self._behaviourAttributesList.append(newBehaviourAttributes)
        
        self._makeDeleteAttributesMenuItem(newBehaviourAttributes)
        self._makeSelectAgentsWithBehaviourMenuItem(newBehaviourAttributes, False)
        self._makeSelectAgentsWithBehaviourMenuItem(newBehaviourAttributes, True)
        self._makeAssignAgentsToBehaviourMenuItem(newBehaviourAttributes)
        self._makeBehaviourTab(newBehaviourAttributes)
        
        self.delegate.onNewBehaviourAttributesAdded(newBehaviourAttributes)
        self._tabLayout.setSelectTabIndex(self._tabLayout.getNumberOfChildren())
        self._notifyOnBehavioursListChanged()
 
#####################      
    def addBehaviourForIdentifier(self, behaviourIdentifier):
        if(behaviourIdentifier == cbba.ClassicBoidBehaviourAttributes.DefaultSectionTitle()):
            return self.addClassicBoidAttributes()
        elif(behaviourIdentifier == gdba.GoalDrivenBehaviourAttributes.DefaultSectionTitle()):
            return self.addGoalDrivenAttributes()
        elif(behaviourIdentifier == fpba.FollowPathBehaviourAttributes.DefaultSectionTitle()):
            return self.addFollowPathAttributes()
        else:
            raise ValueError("Unrecognised behaviour identifier \"%s\"" % behaviourIdentifier)
             
    def addClassicBoidAttributes(self):
        sectionTitle = self._titleForAttributesClass(cbba.ClassicBoidBehaviourAttributes)
        newBehaviourAttributes = cbba.ClassicBoidBehaviourAttributes(sectionTitle)
        self._addNewBehaviour(newBehaviourAttributes)
        
        return newBehaviourAttributes
    
    def addGoalDrivenAttributes(self, wallLipGoal=None, basePyramidGoalHeight=None, finalGoal=None):
        sectionTitle = self._titleForAttributesClass(gdba.GoalDrivenBehaviourAttributes)
        newBehaviourAttributes = gdba.GoalDrivenBehaviourAttributes(sectionTitle, self._onRequestLeaderSelectForBehaviourAttributes,
                                                                    wallLipGoal, basePyramidGoalHeight, finalGoal)
        self._addNewBehaviour(newBehaviourAttributes)
        
        return newBehaviourAttributes
    
    def addFollowPathAttributes(self, pathCurve=None):
        sectionTitle = self._titleForAttributesClass(fpba.FollowPathBehaviourAttributes)
        newBehaviourAttributes = fpba.FollowPathBehaviourAttributes(sectionTitle, pathCurve)
        self._addNewBehaviour(newBehaviourAttributes)
        
        return newBehaviourAttributes

#####################        
    def removeBehaviour(self, behaviourAttributes, getUserConfirmation=False):
        if(not getUserConfirmation or 
           uib.GetUserConfirmation("Remove Behaviour", ("Delete behaviour \"%s\"?" % behaviourAttributes.sectionTitle()))):
            
            if(behaviourAttributes is self.defaultBehaviourAttributes):
                raise ValueError("Default behaviour \"%s\" cannot be deleted." % self.defaultBehaviourAttributes.sectionTitle())
            else:
                self._behaviourAttributesList.remove(behaviourAttributes)
                for uiComponent in self._uiComponentToAttributesLookup[behaviourAttributes]:
                    uib.DeleteComponent(uiComponent)
                del self._uiComponentToAttributesLookup[behaviourAttributes]
                
                self.delegate.onBehaviourAttributesDeleted(behaviourAttributes)
                self._notifyOnBehavioursListChanged()
                
                if(getUserConfirmation):
                    util.LogInfo("Removed behaviour \"%s\"" % behaviourAttributes.sectionTitle())

#####################                
    def removeAllBehaviours(self, getUserConfirmation=True):
        if(not getUserConfirmation or
           uib.GetUserConfirmation("Remove All Behaviours", 
                                   ("Delete all behaviours (default behaviour \"%s\" will not be deleted)?" 
                                    % self.defaultBehaviourAttributes.sectionTitle()))):
            for behaviour in self._behaviourAttributesList:
                if(behaviour is not self.defaultBehaviourAttributes):
                    self.removeBehaviour(behaviour, False)
                    
            if(getUserConfirmation):
                util.LogInfo("All non-default behaviours deleted.")

#####################         
    def buildUi(self, windowTitle):
        if(self._needsUiRebuild):
            if(uib.WindowExists(self._uiWindow)):
                uib.DestroyWindow(self._uiWindow)
            self._needsUiRebuild = False
        
        if(not self.uiVisible):
            self._uiWindow = uib.MakeWindow(windowTitle)
            
            self._buildUiMenuBar()
            self._buildUiMainPanel()
            
            self._needsUiRebuild = False
        
        self._uiWindow.show()

#####################        
    def _buildUiMenuBar(self):
        uib.MakeMenu("File")
        uib.MakeMenuItem("Open File...", self._didSelectOpenFile)
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Save", self._didSelectSave)
        uib.MakeMenuItem("Save As...", self._didSelectSaveAs)
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Make Values Default", self._didSelectMakeValuesDefault)
        uib.MakeMenuItem("Show Debug Logging", self._didSelectShowDebugLogging)
        uib.MakeMenuItem("Hide Debug Logging", self._didSelectHideDebugLogging)
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Refresh Internals", self._didSelectRefreshInternals)
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Preferences...", self._didSelectShowPreferences)
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Quit", self._didSelectQuit)
        
        uib.MakeMenu("Behaviours")
        createBehaviourMenu = uib.MakeMenuItemWithSubMenu("Create New Behaviour")
        uib.MakeMenuItem(cbba.ClassicBoidBehaviourAttributes.DefaultSectionTitle(), 
                         lambda *args: util.EvalDeferred(self.addClassicBoidAttributes))
        uib.MakeMenuItem(gdba.GoalDrivenBehaviourAttributes.DefaultSectionTitle(),
                         lambda *args: util.EvalDeferred(self.addGoalDrivenAttributes, None, None, None))
        uib.MakeMenuItem(fpba.FollowPathBehaviourAttributes.DefaultSectionTitle(),
                         lambda *args: util.EvalDeferred(self.addFollowPathAttributes, None))
        uib.SetAsChildMenuLayout(createBehaviourMenu)
        
        self._removeBehaviourMenu = uib.MakeMenuItemWithSubMenu("Remove Behaviour")
        for behaviourAttributes in self._behaviourAttributesList:
            self._makeDeleteAttributesMenuItem(behaviourAttributes)
        uib.SetAsChildMenuLayout(self._removeBehaviourMenu)
        uib.MakeMenuItem("Remove All Behaviours", self.removeAllBehaviours)
        
        uib.MakeMenu("Agents")
        self._selectAgentsWithMenu = uib.MakeMenuItemWithSubMenu("Select Agents With:")
        for behaviourAttributes in self._behaviourAttributesList:
            self._makeSelectAgentsWithBehaviourMenuItem(behaviourAttributes, False)
        uib.SetAsChildMenuLayout(self._selectAgentsWithMenu)
        
        self._selectAgentsNotWithMenu = uib.MakeMenuItemWithSubMenu("Select Agents Without:")
        for behaviourAttributes in self._behaviourAttributesList:
            self._makeSelectAgentsWithBehaviourMenuItem(behaviourAttributes, True)
        uib.SetAsChildMenuLayout(self._selectAgentsNotWithMenu)
         
        uib.MakeMenuSeparator()
        self._assignAgentsToMenu = uib.MakeMenuItemWithSubMenu("Assign Agents To:")
        for behaviourAttributes in self._behaviourAttributesList:
            self._makeAssignAgentsToBehaviourMenuItem(behaviourAttributes)
        uib.SetAsChildMenuLayout(self._assignAgentsToMenu)

#####################        
    def _makeSelectAgentsWithBehaviourMenuItem(self, attributes, inverted):
        uib.SetParentMenuLayout(self._selectAgentsWithMenu if(not inverted) else self._selectAgentsNotWithMenu)
        menuItem = uib.MakeMenuItem(attributes.sectionTitle(), 
                                    lambda *args: self.delegate.requestedSelectAgentsWithBehaviour(attributes, inverted))
        self._linkUiComponentToAttributes(menuItem, attributes)

#####################
    def _makeAssignAgentsToBehaviourMenuItem(self, attributes):
        uib.SetParentMenuLayout(self._assignAgentsToMenu)
        menuItem = uib.MakeMenuItem(("%s..." % attributes.sectionTitle()),
                                    lambda *args: self.delegate.requestedAssignAgentsToBehaviour(attributes))
        self._linkUiComponentToAttributes(menuItem, attributes)

#####################        
    def _makeDeleteAttributesMenuItem(self, attributes):
        uib.SetParentMenuLayout(self._removeBehaviourMenu)
        
        menuItem = uib.MakeMenuItem(attributes.sectionTitle(), 
                                    lambda *args: util.EvalDeferred(self.removeBehaviour, attributes, True))
        if(attributes is self.defaultBehaviourAttributes):
            menuItem.setAnnotation("Default behaviour - cannot be deleted.")
            menuItem.setEnable(False)
        self._linkUiComponentToAttributes(menuItem, attributes)
        
#####################       
    def _buildUiMainPanel(self):
        uib.MakeBorderingLayout()
            
        generalColumnLayout = uib.MakeColumnLayout()
        self.globalAttributes.populateUiLayout()
        uib.SetAsChildLayout(generalColumnLayout)
        
        self._tabLayout = uib.MakeTabLayout(400)
        
        agentPropertiesScrollLayout = uib.MakeScrollLayout("Agent Attributes")
        
        movementLayout = uib.MakeFrameLayout("Agent Movement")
        self.agentMovementAttributes.populateUiLayout()
        uib.SetAsChildLayout(movementLayout)
        
        awarenessLayout = uib.MakeFrameLayout("Agent Perception")
        self.agentPerceptionAttributes.populateUiLayout()
        uib.SetAsChildLayout(awarenessLayout, agentPropertiesScrollLayout)
        
        for behaviourAttributes in self._behaviourAttributesList:
            self._makeBehaviourTab(behaviourAttributes)
        
        uib.SetAsChildLayout(self._tabLayout)
        
        uib.MakeButtonStrip((("Load Defaults", self._didPressLoadDefaults), #self.restoreDefaultAttributeValuesFromFile.__doc__), 
                             ("Save As Default", self._didPressSaveAsDefaults)))#, self.makeCurrentAttributeValuesDefault.__doc__)))

#####################
    def _makeBehaviourTab(self, behaviourAttributes):
        uib.SetParentLayout(self._tabLayout)
        
        scrollLayout = uib.MakeScrollLayout(behaviourAttributes.sectionTitle())
        behaviourAttributes.populateUiLayout()
        uib.SetAsChildLayout(scrollLayout)
        self._linkUiComponentToAttributes(scrollLayout, behaviourAttributes)
        
#####################         
    def _linkUiComponentToAttributes(self, component, attributes):
        componentList = self._uiComponentToAttributesLookup.get(attributes)
        if(componentList is None):
            componentList = []
            self._uiComponentToAttributesLookup[attributes] = componentList
            
        componentList.append(component)
        
#####################        
    def hideUI(self):
        if(self.uiVisible):
            uib.DestroyWindow(self._uiWindow)

#####################        
    def _didPressLoadDefaults(self, *args):
        if(uib.GetUserConfirmation("Load Defaults", "Restore all attributes to default values?")):
            self.restoreDefaultAttributeValuesFromFile()
 
#####################   
    def _didPressSaveAsDefaults(self, *args):
        if(uib.GetUserConfirmation("Save Defaults", "Set default attribute values to the current values?")):
            self.makeCurrentAttributeValuesDefault()
            
##################### 
    def _didSelectOpenFile(self, *args):
        pass
    
    def _didSelectSave(self, *args):
        pass
    
    def _didSelectSaveAs(self, *args):
        pass
    
    def _didSelectMakeValuesDefault(self, *args):
        pass

    def _didSelectShowDebugLogging(self, *args):
        util.SetLoggingLevelDebug()
        
    def _didSelectHideDebugLogging(self, *args):
        util.SetLoggingLevelInfo()
        
    def _didSelectRefreshInternals(self, *args):
        self.delegate.refreshInternals()
        
    def _didSelectShowPreferences(self, *args):
        self.globalAttributes.showGlobalPreferencesWindow()
        
    def _didSelectQuit(self, *args):
        if(uib.GetUserConfirmation("Quit", ("This will remove this %s instance from your scene.\nAre you sure?" 
                                            % util.PackageName()))):
            self.delegate.requestedQuitSwarmInstance()

#####################            
    def _checkForPreviousSaveFile(self):
        filePath = _DefaultSaveLocation(self.delegate._getParticleShapeName())
        
        if(os.path.exists(filePath) and
           uib.GetUserConfirmation(("Found %s save file: %s" % (util.PackageName(), filePath)), "Use it?")):
            self.restoreSavedStateFromFile(filePath)
            return True
        else:
            return False

#####################    
    def restoreSavedStateFromFile(self, filePath=None):
        isDefaultSaveLocation = False
        if(filePath is None):
            filePath = util.InitVal(filePath, _DefaultSaveLocation(self.delegate._getParticleShapeName()))
            isDefaultSaveLocation = True
        configReader = ConfigParser.ConfigParser()
        configReader.optionxform = str  # replacing this method is necessary to make option names case-sensitive
        
        if(configReader.read(filePath)):
            self.removeAllBehaviours(False)
            
            behavioursListString = configReader.get(_BEHAVIOURS_LIST_SECTION_NAME_, _BEHAVIOURS_LIST_OPTION_NAME_)
            for behaviourIdentifier in behavioursListString.split(_BEHAVIOURS_LIST_DELIMITER_):
                try:
                    self.addBehaviourForIdentifier(behaviourIdentifier)
                except ValueError as e:
                    util.LogError(e)
            
            for section in self._allSections():
                section.getSavedStateFromConfigReader()
                
            if(isDefaultSaveLocation):
                self._preferredSaveLocation = filePath
            else:
                self._preferredSaveLocation = None
        else:
            raise ValueError("Could not find file %s" % filePath)
        
#####################   
    def restoreDefaultAttributeValuesFromFile(self, section=None):
        filePath = _DefaultsAttributeValuesFilename()
        
        configReader = ConfigParser.ConfigParser()
        configReader.optionxform = str 
        
        if(configReader.read(filePath)):
            util.LogDebug("Parsing file \'%s\' for default values..." % filePath)
            
            if(section is None):
                for sectionIterator in self._allSections():
                    sectionIterator.getDefaultsFromConfigReader(configReader)
            elif(not section.getDefaultsFromConfigReader(configReader)):
                util.LogInfo("Found new behaviour type - adding \"%s\" section to defaults..." % section.sectionTitle())
                sectionIterator.makeCurrentAttributeValuesDefault(section)
        else:
            util.LogWarning("Could not find default attribute values file %s, creating a new one..." % filePath)
            self.makeCurrentAttributeValuesDefault()

#####################    
    def saveCurrentStateToFile(self, filePath=None):
        autoCreatedSaveFile = False
        if(filePath is None):
            filePath = _DefaultSaveLocation(self.delegate._getParticleShapeName())
            autoCreatedSaveFile = not os.path.exists(filePath)
            self._preferredSaveLocation = None
        else:
            self._preferredSaveLocation = filePath
        
        configWriter = ConfigParser.ConfigParser()
        configWriter.optionxform = str
        
        configWriter.add_section(_BEHAVIOURS_LIST_SECTION_NAME_)
        behaviourStrings = [bhvr.DefaultSectionTitle() for bhvr in self._behaviourAttributesList 
                            if(bhvr is not self.defaultBehaviourAttributes)]
        configWriter.set(_BEHAVIOURS_LIST_SECTION_NAME_, 
                         _BEHAVIOURS_LIST_OPTION_NAME_, 
                         _BEHAVIOURS_LIST_DELIMITER_.join(behaviourStrings))
                
        for section in self._allSections():
            section.setSavedStateWithConfigWriter(configWriter)
        
        saveFile = open(filePath, "w")   
        configWriter.write(saveFile)
        saveFile.close()
        
        util.LogInfo("Saved current attribute values to file %s." % filePath)
        if(autoCreatedSaveFile):
            uib.DisplayInfoBox(filePath, "Created new save file:")
    
#####################
    def makeCurrentAttributeValuesDefault(self, section=None):
        filePath = _DefaultsAttributeValuesFilename()
        writtenAttributeTypesSet = set()
        configWriter = ConfigParser.ConfigParser()
        configWriter.optionxform = str
        configWriter.read(filePath)
        
        if(section is not None):
            section.setDefaultsToConfigWriter(configWriter)
        else:
            for section in self._allSections():
                sectionType = type(section)
                if(sectionType not in writtenAttributeTypesSet):
                    section.setDefaultsToConfigWriter(configWriter)
                    writtenAttributeTypesSet.add(sectionType)
                else:
                    util.LogInfo("Found multiple instances of behaviour type: \"%s\". \
Default values taken from first instance only." % section.DefaultSectionTitle())
                
        defaultsFile = open(filePath, "w")   
        configWriter.write(defaultsFile)
        defaultsFile.close()
        
        util.LogInfo("Saved current attribute values as default values.")
        
    
# END OF CLASS
####################################