from boidBaseObject import BoidBaseObject
import boidTools.uiBuilder as uib
import boidTools.util as util
import boidResources.fileLocations as fl
import boidResources.packageInfo as pi

from abc import ABCMeta, abstractmethod
import weakref



_TOP_PANEL_COMPONENTS_WIDTH_ = 400

_CHANGE_DEFAULT_ANNOTATION_ = "\"%s\" is already the default." 
_REMOVE_BEHAVIOUR_ANNOTATION_ = "Remove this behaviour, assigned agents will revert to default behaviour."
_CANNOT_REMOVE_BEHAVIOUR_ANNOTATION_ = "Default behaviour - cannot be deleted."



###########################################
class UiControllerDelegate(object):
    __metaclass__ = ABCMeta
    
######## - File Menu   
    @abstractmethod
    def openFile(self, filePath):
        raise NotImplemented
    
    @abstractmethod
    def saveToFile(self, filePath=None):
        raise NotImplemented
    
    @abstractmethod
    def showDebugLogging(self, show):
        raise NotImplemented
  
    @abstractmethod
    def showPreferencesWindow(self):
        raise NotImplemented
    
    @abstractmethod
    def quitSwarmInstance(self):
        raise NotImplemented
    
######## - Edit Menu
    @abstractmethod
    def refreshInternals(self):
        raise NotImplemented
      
    @abstractmethod
    def restoreDefaultValues(self, behaviourId):
        raise NotImplemented
    
    @abstractmethod
    def makeValuesDefault(self, behaviourId):
        raise NotImplemented
 
######## - Behaviours Menu
    @abstractmethod
    def changeDefaultBehaviour(self, behaviourId):
        raise NotImplemented
    
    @abstractmethod
    def addNewBehaviour(self, behaviourName):
        raise NotImplemented
    
    @abstractmethod
    def removeBehaviour(self, behaviourId):
        raise NotImplemented
    
    @abstractmethod
    def removeAllBehaviours(self):
        raise NotImplemented

######## - Agents Menu
    @abstractmethod
    def makeAgentsWithBehaviourSelected(self, behaviourId, invertSelection):
        raise NotImplemented
    
    @abstractmethod
    def showAssignAgentsWindowForBehaviour(self, behaviourId):
        raise NotImplemented

# END OF CLASS - UiControllerDelegate
###########################################



########################################
class UiController(BoidBaseObject):
    
    def __init__(self, attributesController, delegate):
        if(not isinstance(delegate, UiControllerDelegate)):
            raise TypeError("Expected subclass of %s, got %s" (UiControllerDelegate, type(delegate)))
        else:
            self._delegate = weakref.ref(delegate)
            self._attributesController = attributesController
            
            self._recreateUiComponents()
            self._needsUiRebuild = False
        
########
    def __del__(self):
        self.hideUI()
        
########
    def _recreateUiComponents(self):
        self._uiWindow = None
        self._uiComponentToAttributesLookup = {}
        self._tabLayout = None
        self._changeDefaultBehaviourMenu = None
        self._removeBehaviourMenu = None
        self._selectAgentsWithMenu = None
        self._selectAgentsNotWithMenu = None
        self._assignAgentsToMenu = None

######################
    def __getstate__(self):
        state = (self.delegate, self._attributesController)
        return state

########    
    def __setstate__(self, state):
        if(state[0] is not None):
            self._delegate = weakref.ref(state[0])
        self._attributesController = state[1]
        
        self._recreateUiComponents()
        self._needsUiRebuild = True
    
########################    
    def _getDefaultBehaviourId(self):
        return self._attributesController.defaultBehaviourId
    _defaultBehaviourId = property(_getDefaultBehaviourId)
    
######################        
    def _getDelegate(self):
        return self._delegate() if(self._delegate is not None) else None
    delegate = property(_getDelegate)
        
#####################
    def _getUiVisible(self):
        return uib.WindowExists(self._uiWindow)
    uiVisible = property(_getUiVisible)
    
#####################       
    def addNewBehaviourToUI(self, newBehaviourAttributes):        
        self._makeDeleteBehaviourMenuItem(newBehaviourAttributes)
        self._makeSelectAgentsWithBehaviourMenuItem(newBehaviourAttributes, False)
        self._makeSelectAgentsWithBehaviourMenuItem(newBehaviourAttributes, True)
        self._makeChangeDefaultBehaviourMenuItem(newBehaviourAttributes)
        self._makeAssignAgentsToBehaviourMenuItem(newBehaviourAttributes)
        self._makeBehaviourTab(newBehaviourAttributes)
        
        self._tabLayout.setSelectTabIndex(self._tabLayout.getNumberOfChildren())
        
#####################        
    def removeBehaviourFromUI(self, behaviourAttributes):
        behaviourId = behaviourAttributes.behaviourId
        
        for uiComponent in self._uiComponentToAttributesLookup[behaviourId]:
            try:
                uib.DeleteComponent(uiComponent)
            except:
                pass
        del self._uiComponentToAttributesLookup[behaviourId]
        
#####################
    def updateDefaultBehaviourInUI(self, oldDefaultId, newDefaultId):
        for uiComponent in self._uiComponentToAttributesLookup[oldDefaultId]:
            parent = uiComponent.getParent()
            if(parent == self._changeDefaultBehaviourMenu or parent == self._removeBehaviourMenu):
                uiComponent.setEnable(True)
                uiComponent.setAnnotation("")
            elif(parent == self._tabLayout):
                self._tabLayout.setTabLabel((uiComponent, oldDefaultId))
            elif(uiComponent.getAnnotation() == _CANNOT_REMOVE_BEHAVIOUR_ANNOTATION_):
                uiComponent.setEnable(True)
                uiComponent.setAnnotation(_CANNOT_REMOVE_BEHAVIOUR_ANNOTATION_)
                
        for uiComponent in self._uiComponentToAttributesLookup[newDefaultId]:
            parent = uiComponent.getParent()
            if(parent == self._changeDefaultBehaviourMenu):
                uiComponent.setEnable(False)
                uiComponent.setAnnotation(_CHANGE_DEFAULT_ANNOTATION_ % newDefaultId)
            elif(parent == self._removeBehaviourMenu):
                uiComponent.setEnable(False)
                uiComponent.setAnnotation(_CANNOT_REMOVE_BEHAVIOUR_ANNOTATION_)
            elif(parent == self._tabLayout):
                self._tabLayout.setTabLabel((uiComponent, newDefaultId + '*'))
            elif(uiComponent.getAnnotation() == _REMOVE_BEHAVIOUR_ANNOTATION_):
                uiComponent.setEnable(False)
                uiComponent.setAnnotation(_CANNOT_REMOVE_BEHAVIOUR_ANNOTATION_)
    
#####################        
    def hideUI(self):
        if(self.uiVisible):
            uib.DestroyWindowIfNecessary(self._uiWindow)
            self._recreateUiComponents()
            self._needsUiRebuild = False  
            
#####################         
    def buildUi(self):
        if(self._needsUiRebuild):
            self.hideUI()
        
        if(not self.uiVisible):
            particleName = self._attributesController.globalAttributes.particleShapeNode.name()
            self._uiWindow = uib.MakeWindow(("%s - %s" % (pi.PackageName(), particleName)))
            
            self._buildUiMenuBar()
            self._buildUiMainPanel()
            
            self._needsUiRebuild = False
        
        self._uiWindow.show()
            
#####################        
    def _buildUiMenuBar(self):
        uib.MakeMenu("File")
        uib.MakeMenuItem("Open File...", self._didSelectOpenFile)
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Save", lambda *args: self.delegate.saveToFile())
        uib.MakeMenuItem("Save As...", self._didSelectSaveAs)
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Show Debug Logging", lambda *args: self.delegate.showDebugLogging(True))
        uib.MakeMenuItem("Hide Debug Logging", lambda *args: self.delegate.showDebugLogging(False))
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Preferences...", lambda *args: self.delegate.showPreferencesWindow())
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Quit", self._didSelectQuit)
        
        uib.MakeMenu("Edit")
        uib.MakeMenuItem("Refresh Internals", lambda *args: self.delegate.refreshInternals())
        uib.MakeMenuSeparator()
        uib.MakeMenuItem("Restore Default Values", lambda *args: self._didSelectRestoreDefaultValues(None))
        uib.MakeMenuItem("Make Values Default", lambda *args: self._didSelectMakeValuesDefault(None))
        
        uib.MakeMenu("Behaviours")
        behaviourAttributesList = self._attributesController._behaviourAttributesList
        
        self._changeDefaultBehaviourMenu = uib.MakeMenuItemWithSubMenu("Change Default")
        for behaviourAttributes in behaviourAttributesList:
            self._makeChangeDefaultBehaviourMenuItem(behaviourAttributes)
        uib.SetAsChildMenuLayout(self._changeDefaultBehaviourMenu)

        uib.MakeMenuSeparator()
        createBehaviourMenu = uib.MakeMenuItemWithSubMenu("Create New Behaviour")
        for behaviourName in self._attributesController.behaviourTypeNamesList():
            self._makeCreateBehaviourMenuItem(behaviourName)
        uib.SetAsChildMenuLayout(createBehaviourMenu)
        
        self._removeBehaviourMenu = uib.MakeMenuItemWithSubMenu("Remove Behaviour")
        for behaviourAttributes in behaviourAttributesList:
            self._makeDeleteBehaviourMenuItem(behaviourAttributes)
        uib.SetAsChildMenuLayout(self._removeBehaviourMenu)
        
        uib.MakeMenuItem("Remove All Behaviours", self._didSelectRemoveAllBehaviours)
        
        uib.MakeMenu("Agents")
        self._selectAgentsWithMenu = uib.MakeMenuItemWithSubMenu("Select Agents With:")
        for behaviourAttributes in behaviourAttributesList:
            self._makeSelectAgentsWithBehaviourMenuItem(behaviourAttributes, False)
        uib.SetAsChildMenuLayout(self._selectAgentsWithMenu)
        
        self._selectAgentsNotWithMenu = uib.MakeMenuItemWithSubMenu("Select Agents Without:")
        for behaviourAttributes in behaviourAttributesList:
            self._makeSelectAgentsWithBehaviourMenuItem(behaviourAttributes, True)
        uib.SetAsChildMenuLayout(self._selectAgentsNotWithMenu)
         
        uib.MakeMenuSeparator()
        self._assignAgentsToMenu = uib.MakeMenuItemWithSubMenu("Assign Agents To:")
        for behaviourAttributes in behaviourAttributesList:
            self._makeAssignAgentsToBehaviourMenuItem(behaviourAttributes)
        uib.SetAsChildMenuLayout(self._assignAgentsToMenu)
        
        uib.MakeMenu("Help")
        uib.MakeMenuItem("Project Home Page...", self._didSelectShowDocs, 
                         ("NOTE - will not work on Linux... (go to: %s)" % pi.PackageHomePage()))
        uib.MakeMenuItem("About", self._didSelectAbout)

########
    def _makeChangeDefaultBehaviourMenuItem(self, attributes):
        behaviourId = attributes.behaviourId
        uib.SetParentMenuLayout(self._changeDefaultBehaviourMenu)
        
        menuItem = uib.MakeMenuItem(behaviourId, lambda *args: self._didSelectChangeDefaultBehaviour(behaviourId))
        if(behaviourId == self._defaultBehaviourId):
            menuItem.setAnnotation(_CHANGE_DEFAULT_ANNOTATION_ % behaviourId)
            menuItem.setEnable(False)
        self._linkUiComponentToBehaviourId(menuItem, behaviourId)
        
########
    def _makeCreateBehaviourMenuItem(self, behaviourTypeName):
        uib.MakeMenuItem(behaviourTypeName, lambda *args: self._didSelectAddNewBehaviour(behaviourTypeName))

########
    def _makeDeleteBehaviourMenuItem(self, attributes):
        behaviourId = attributes.behaviourId
        uib.SetParentMenuLayout(self._removeBehaviourMenu)
        
        menuItem = uib.MakeMenuItem(behaviourId, 
                                    lambda *args: self._didSelectRemoveBehaviour(behaviourId))
        if(behaviourId == self._defaultBehaviourId):
            menuItem.setAnnotation(_CANNOT_REMOVE_BEHAVIOUR_ANNOTATION_)
            menuItem.setEnable(False)
        self._linkUiComponentToBehaviourId(menuItem, behaviourId)
        
########
    def _makeSelectAgentsWithBehaviourMenuItem(self, attributes, inverted):
        behaviourId = attributes.behaviourId
        uib.SetParentMenuLayout(self._selectAgentsWithMenu if(not inverted) else self._selectAgentsNotWithMenu)
        menuItem = uib.MakeMenuItem(behaviourId, 
                                    lambda *args: self.delegate.makeAgentsWithBehaviourSelected(behaviourId, inverted))
        self._linkUiComponentToBehaviourId(menuItem, behaviourId)

########
    def _makeAssignAgentsToBehaviourMenuItem(self, attributes):
        behaviourId = attributes.behaviourId
        uib.SetParentMenuLayout(self._assignAgentsToMenu)
        menuItem = uib.MakeMenuItem(("%s..." % behaviourId),
                                    lambda *args: self.delegate.showAssignAgentsWindowForBehaviour(behaviourId))
        self._linkUiComponentToBehaviourId(menuItem, behaviourId)

#####################       
    def _buildUiMainPanel(self):
        uib.MakeBorderingLayout()
        
        rowLayout = uib.MakeTopLevelRowLayout(_TOP_PANEL_COMPONENTS_WIDTH_)
        generalColumnLayout = uib.MakeColumnLayout()
        globalAttributes = self._attributesController.globalAttributes
        globalAttributes.populateUiLayout()
        globalAttributes.nameChangeCallback = (lambda name: self._uiWindow.setTitle(("%s - %s" % 
                                                                                     (pi.PackageName(), name))))
        uib.SetAsChildLayout(generalColumnLayout)
        
        uib.MakeImage(fl.LogoImageLocation(), "It's going to get you.")
        uib.SetAsChildLayout(rowLayout)
        
        self._tabLayout = uib.MakeTabLayout()
        
        self._makeAgentAttributesTab(self._attributesController.agentMovementAttributes,
                                     self._attributesController.agentPerceptionAttributes)
        
        for behaviourAttributes in self._attributesController._behaviourAttributesList:
            self._makeBehaviourTab(behaviourAttributes, (behaviourAttributes.behaviourId == self._defaultBehaviourId))
            
        uib.SetAsChildLayout(self._tabLayout)
        
########
    def _makeAgentAttributesTab(self, movementAttributes, perceptionAttributes):
        formLayout = uib.MakeFormLayout("Agent Attributes")
        scrollLayout = uib.MakeScrollLayout()
        
        movementLayout = uib.MakeFrameLayout("Agent Movement")
        movementAttributes.populateUiLayout()
        uib.SetAsChildLayout(movementLayout)
        
        awarenessLayout = uib.MakeFrameLayout("Agent Perception")
        perceptionAttributes.populateUiLayout()
        uib.SetAsChildLayout(awarenessLayout, scrollLayout)
        
        buttonStripLayout = uib.MakeButtonStrip((("Load Defaults",
                                                  lambda *args: self._didSelectRestoreAgentValues(movementAttributes.behaviourId, 
                                                                                                  perceptionAttributes.behaviourId),
                                                  "Reset agent attributes to default values."),))[0]
        
        uib.SetAsChildLayout(buttonStripLayout)
        uib.DistributeButtonedWindowInFormLayout(formLayout, scrollLayout, buttonStripLayout)
        uib.SetAsChildLayout(formLayout)
        
########
    def _makeBehaviourTab(self, behaviourAttributes, isDefaultBehaviour=False):
        behaviourId = behaviourAttributes.behaviourId
        uib.SetParentLayout(self._tabLayout)
        
        formLayout = uib.MakeFormLayout(behaviourId if(not isDefaultBehaviour) else behaviourId + '*')
        scrollLayout = uib.MakeScrollLayout()
        behaviourAttributes.populateUiLayout()
        uib.SetAsChildLayout(scrollLayout)
        
        buttonStripTuple = uib.MakeButtonStrip((("Assign Agents...", 
                                                  lambda *args: self.delegate.showAssignAgentsWindowForBehaviour(behaviourId),
                                                "Assign selection of agents to follow this behaviour."),
                                                 ("Select Agents", 
                                                  lambda *args: self.delegate.makeAgentsWithBehaviourSelected(behaviourId, False),
                                                  "Select corresponding particles of all agents following this behaviour."),
                                                 ("Load Defaults",
                                                  lambda *args: self._didSelectRestoreDefaultValues(behaviourId),
                                                  "Reset behaviour attributes to default values."),
                                                 ("Remove Behaviour",
                                                  lambda *args: self._didSelectRemoveBehaviour(behaviourId),
                                                  _REMOVE_BEHAVIOUR_ANNOTATION_)))
        buttonStripLayout, buttonsList = buttonStripTuple
        
        if(isDefaultBehaviour):
            buttonsList[3].setEnable(False)
            buttonsList[3].setAnnotation(_CANNOT_REMOVE_BEHAVIOUR_ANNOTATION_)
        
        uib.SetAsChildLayout(buttonStripLayout)
        uib.DistributeButtonedWindowInFormLayout(formLayout, scrollLayout, buttonStripLayout)
        uib.SetAsChildLayout(formLayout)
        
        self._linkUiComponentToBehaviourId(formLayout, behaviourId)
        for button in buttonsList:
            self._linkUiComponentToBehaviourId(button, behaviourId)
        
#####################         
    def _linkUiComponentToBehaviourId(self, component, behaviourId):
        componentList = self._uiComponentToAttributesLookup.get(behaviourId)
        if(componentList is None):
            componentList = []
            self._uiComponentToAttributesLookup[behaviourId] = componentList
        
        componentList.append(component)

#####################        
    def _didSelectOpenFile(self, *args):
        filePath = uib.GetFilePathFromUser(True, fl.SaveFolderLocation(), fl.SaveFileExtension())
        if(filePath is not None):
            util.EvalDeferred(self.delegate.openFile, filePath)
 
########           
    def _didSelectSaveAs(self, *args):
        filePath = uib.GetFilePathFromUser(False, fl.SaveFolderLocation(), fl.SaveFileExtension())
        if(filePath is not None):
            self.delegate.saveToFile(filePath)

########            
    def _didSelectRestoreAgentValues(self, movementId, perceptionId):
        if(uib.GetUserConfirmation("Load Defaults", "Restore default values to agent attributes?")):
            self.delegate.restoreDefaultValues(movementId)
            self.delegate.restoreDefaultValues(perceptionId)
    
########
    def _didSelectRestoreDefaultValues(self, behaviourId):
        message = ("Restore default values to %s?" % 
                   ("behaviour \"%s\"" % behaviourId) if(behaviourId is not None) else "all attributes")
        if(uib.GetUserConfirmation("Load Defaults", message)):
            self.delegate.restoreDefaultValues(behaviourId)

########
    def _didSelectMakeValuesDefault(self, behaviourId):
        if(behaviourId is None):
            message = "Update default values with all current attribute values?"
        else:
            message = ("Update default values with current attribute values for behaviour \"%s\"?" %
                       behaviourId)
        
        if(uib.GetUserConfirmation("Make Values Default", message)):
            self.delegate.makeValuesDefault(behaviourId)
        
########
    def _didSelectChangeDefaultBehaviour(self, behaviourId):
        util.EvalDeferred(self.delegate.changeDefaultBehaviour, behaviourId)
                  
########
    def _didSelectAddNewBehaviour(self, behaviourTypeName):
        util.EvalDeferred(self.delegate.addNewBehaviour, behaviourTypeName)
 
########
    def _didSelectRemoveBehaviour(self, behaviourId):
        if(uib.GetUserConfirmation("Remove Behaviour", ("Delete behaviour \"%s\"?" % behaviourId))):
            util.EvalDeferred(self.delegate.removeBehaviour, behaviourId)
  
########
    def _didSelectRemoveAllBehaviours(self):
        if(uib.GetUserConfirmation("Remove All Behaviours", 
                                   ("Delete all behaviours (default behaviour \"%s\" will not be deleted)?" 
                                    % self._defaultBehaviourId))):
            util.EvalDeferred(self.delegate.removeAllBehaviours)
 
########
    def _didSelectQuit(self, *args):
        if(uib.GetUserConfirmation("Quit", ("This will remove this %s instance from your scene.\nAre you sure?" 
                                            % pi.PackageName()))):
            util.EvalDeferred(self.delegate.quitSwarmInstance)
            
########
    def _didSelectShowDocs(self, *args):
        util.LaunchWebPage(pi.PackageHomePage())
    
########
    def _didSelectAbout(self, *args):
        uib.DisplayInfoBox(pi.PackageInfo(), ("%s v%s" % (pi.PackageName(), pi.VersionNumber())))
            

# END OF CLASS - UiController
########################################
            