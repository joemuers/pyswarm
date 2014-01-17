from boidBaseObject import BoidBaseObject

import globalAttributes as ga
import agentPerceptionAttributes as apa
import agentMovementAttributes as ama
import classicBoidBehaviourAttributes as cbba
import goalDrivenBehaviourAttributes as gdba
import followPathBehaviourAttributes as fpba
import boidTools.uiBuilder as uib
import boidTools.util as util

import os
import weakref
import ConfigParser



# TODO - OS independent filepath
__DEFAULTS_FILENAME__ = "/../boidResources/boidAttributeDefaults.ini"



##########################################
class AttributesControllerDelegate(object):
    
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
            raise TypeError
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
            
            self.readDefaultAttributesFromFile()
            self._notifyOnBehavioursListChanged()

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
        self.readDefaultAttributesFromFile(newBehaviourAttributes)
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
    def addClassicBoidAttributes(self):
        sectionTitle = self._titleForAttributesClass(cbba.ClassicBoidBehaviourAttributes)
        newBehaviourAttributes = cbba.ClassicBoidBehaviourAttributes(sectionTitle)
        self._addNewBehaviour(newBehaviourAttributes)
        
        return newBehaviourAttributes
    
    def addGoalDrivenAttributes(self, wallLipGoal, basePyramidGoalHeight, finalGoal):
        sectionTitle = self._titleForAttributesClass(gdba.GoalDrivenBehaviourAttributes)
        newBehaviourAttributes = gdba.GoalDrivenBehaviourAttributes(sectionTitle, self._onRequestLeaderSelectForBehaviourAttributes,
                                                                    wallLipGoal, basePyramidGoalHeight, finalGoal)
        self._addNewBehaviour(newBehaviourAttributes)
        
        return newBehaviourAttributes
    
    def addFollowPathAttributes(self, pathCurve):
        sectionTitle = self._titleForAttributesClass(fpba.FollowPathBehaviourAttributes)
        newBehaviourAttributes = fpba.FollowPathBehaviourAttributes(sectionTitle, pathCurve)
        self._addNewBehaviour(newBehaviourAttributes)
        
        return newBehaviourAttributes

#####################    
    def onFrameUpdated(self):
        for attributes in self._allSections():
            attributes.onFrameUpdated()

#####################        
    def removeBehaviour(self, behaviourAttributes, getUserConfirmation=False):
        if(not getUserConfirmation or 
           uib.GetUserConfirmation("Remove Behaviour", ("Delete behaviour \"%s\"?" % behaviourAttributes.sectionTitle()))):
            
            self._behaviourAttributesList.remove(behaviourAttributes)
            for uiComponent in self._uiComponentToAttributesLookup[behaviourAttributes]:
                uib.DeleteComponent(uiComponent)
            del self._uiComponentToAttributesLookup[behaviourAttributes]
            
            self.delegate.onBehaviourAttributesDeleted(behaviourAttributes)
            self._notifyOnBehavioursListChanged()

#####################
    def _allSections(self):
        sectionsList = [self.globalAttributes, self.agentMovementAttributes, self.agentPerceptionAttributes] 
        sectionsList.extend(self._behaviourAttributesList)
        
        return sectionsList

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
        
        uib.MakeButtonStrip((("Load Defaults", self._didPressLoadDefaults, self.readDefaultAttributesFromFile.__doc__), 
                             ("Save As Default", self._didPressSaveAsDefaults, self.writeDefaultValuesToFile.__doc__)))

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
            self.readDefaultAttributesFromFile()
 
#####################   
    def _didPressSaveAsDefaults(self, *args):
        if(uib.GetUserConfirmation("Save Defaults", "Set default attribute values to the current values?")):
            self.writeDefaultValuesToFile()
            
##################### 
    def _didSelectShowDebugLogging(self, *args):
        print("Show BLAH.")
        
    def _didSelectHideDebugLogging(self, *args):
        print("Hide BLAH")
        
    def _didSelectRefreshInternals(self, *args):
        self.delegate.refreshInternals()
        
    def _didSelectShowPreferences(self, *args):
        self.globalAttributes.showGlobalPreferencesWindow()
        
    def _didSelectQuit(self, *args):
        if(uib.GetUserConfirmation("Quit", ("This will remove this %s instance from your scene.\nAre you sure?" 
                                            % util.PackageName()))):
            self.delegate.requestedQuitSwarmInstance()

#####################    
    def readDefaultAttributesFromFile(self, section=None, filePath=None):
        """Restore attributes to default values from file."""
        
        createNewFileIfNeeded = False
        if(filePath is None):
            createNewFileIfNeeded = True
            filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__
        
        configReader = ConfigParser.ConfigParser()
        configReader.optionxform = str  # replacing this method is necessary to make option names case-sensitive
        
        if(configReader.read(filePath)):
            print("Parsing file \'%s\' for default values..." % filePath)
            
            if(section is None):
                for sectionIterator in self._allSections():
                    sectionIterator.getDefaultsFromConfigReader(configReader)
            elif(not section.getDefaultsFromConfigReader(configReader)):
                print("Adding new section to default attributes file...")
                self.writeDefaultValuesToFile(section, filePath)
        else:
            print("Could not read default attributes file: %s" % filePath)
            if(createNewFileIfNeeded):
                print("Creating new default attributes file...")
                self.writeDefaultValuesToFile(section, filePath)

#####################    
    def writeDefaultValuesToFile(self, section=None, filePath=None):    
        """Sets current attribute values as the defualt values."""
                
        configWriter = ConfigParser.ConfigParser()
        configWriter.optionxform = str # replacing this method is necessary to make option names case-sensitive
        if(filePath is None):
            filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__ 
        
        if(section is None):
            for sectionIterator in self._allSections():
                sectionIterator.setDefaultsToConfigWriter(configWriter)
        else:
            configWriter.read(filePath)
            section.setDefaultsToConfigWriter(configWriter)
        
        defaultsFile = open(filePath, "w")   
        configWriter.write(defaultsFile)
        defaultsFile.close()
        
        print("Wrote current attributes to defaults file:%s" % filePath)
        
    
# END OF CLASS
####################################