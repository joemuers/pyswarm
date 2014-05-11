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
import tools.uiBuilder as uib
import tools.util as util
import resources.fileLocations as fl
import resources.packageInfo as pi

from abc import ABCMeta, abstractmethod
import weakref



_TOP_PANEL_COMPONENTS_WIDTH_ = 400

_CHANGE_DEFAULT_ANNOTATION_ = "\"%s\" is already the default." 
_REMOVE_BEHAVIOUR_ANNOTATION_ = "Remove this behaviour, assigned agents will revert to default behaviour."
_CANNOT_REMOVE_BEHAVIOUR_ANNOTATION_ = "Default behaviour - cannot be deleted."



###########################################
class UiControllerDelegate(object):
    """
    Delegate class for UiController.  Intended to be set as the 'delegate' property (weak 
    reference) of a UiController instance.
    
    Provides a bunch of callbacks for many of the common UiController requests.
    Any class inheriting from UiControllerDelegate must make concrete implementations of
    *all* the methods defined.
    """
    
    __metaclass__ = ABCMeta
    
######## - File Menu   
    @abstractmethod
    def openFile(self, filePath):
        """
        Called when user selects "Open File..." option from PySwarm "File" menu.
        
        :param filePath: File path as specified by the user.
        """
        raise NotImplemented
    
    @abstractmethod
    def saveToFile(self, filePath=None):
        """
        Called when user selects "Save..." option from PySwarm "File" menu
        
        :param filePath: File path as specified by the user.
        """
        raise NotImplemented
    
    @abstractmethod
    def showDebugLogging(self, show):
        """
        Called when user selects "Show Debug Logging"/"Hide Debug Logging" from the PySwarm "File" menu.
        
        :param show: True = "Show Debug Logging", False = "Hide Debug Logging"
        """
        raise NotImplemented
  
    @abstractmethod
    def showPreferencesWindow(self):
        """
        Called when user selects "Preferences..." option from PySwarm "File" menu.
        """
        raise NotImplemented
    
    @abstractmethod
    def quitSwarmInstance(self):
        """
        Called when user selects "Quit" option from PySwarm "File" menu.
        """
        raise NotImplemented
    
######## - Edit Menu
    @abstractmethod
    def refreshInternals(self):
        """
        Called when user selects "Refresh Internals" option from PySwarm "Edit" menu
        """
        raise NotImplemented
      
    @abstractmethod
    def restoreDefaultValues(self, behaviourId):
        """
        Called when user selects "Restore Default Values" option from PySwarm "Edit" menu, or presses
        the "Load Defaults" button on a behaviour instance.
        
        :param behaviourId: Behaviour ID of corresponding behaviour if "Load Defaults" button pressed, or
                            None if "Restore Default Values" option selected (indicates *all* behaviours should be restored).
        """
        raise NotImplemented
    
    @abstractmethod
    def makeValuesDefault(self, behaviourId):
        """
        Called when user selects "Make Values Default" option from PySwarm "Edit" menu.
        
        :param behaviourId: Currently, this is always None.
        """
        raise NotImplemented
 
######## - Behaviours Menu
    @abstractmethod
    def changeDefaultBehaviour(self, behaviourId):
        """
        User selected a behaviour instance from the "Change Default" sub-menu in PySwarm "Behaviours" menu.
        
        :param behaviourId: Behaviour ID of corresponding behaviour.
        """
        raise NotImplemented
    
    @abstractmethod
    def addNewBehaviour(self, behaviourName):
        """
        User selected a behaviour type from the "Create New Behaviour" sub-menu in PySwarm "Behaviours" menu.
        
        :param behaviourName: Behaviour type name that the user selected.
        """
        raise NotImplemented
    
    @abstractmethod
    def removeBehaviour(self, behaviourId):
        """
        User selected a behaviour instance from the "Remove Behaviour" sub-menu in PySwarm "Behaviours" menu.
        
        :param behaviourId: Behaviour ID of corresponding behaviour.
        """
        raise NotImplemented
    
    @abstractmethod
    def removeAllBehaviours(self):
        """
        User selected "Remove All Behaviours" from PySwarm "Behaviours" menu.
        """
        raise NotImplemented

######## - Agents Menu
    @abstractmethod
    def makeAgentsWithBehaviourSelected(self, behaviourId, invertSelection):
        """
        User chose a behaviour instance from either "Select Agents With" or "Select Agents Without" sub-menus
        in PySwarm "Agents" menu, or pressed the "Select Agents" button on a behaviour instance.
        
        :param behaviourId:  Behaviour ID of corresponding behaviour.
        :param invertSelection: True = "Select Agents With"/"Select Agents", False = "Select Agents Without"
        """
        raise NotImplemented
    
    @abstractmethod
    def showAssignAgentsWindowForBehaviour(self, behaviourId):
        """
        User chose a behaviour instance from "Assign Agents To:" sub-menu in PySwarm "Agents" menu, or
        pressed the "Assign Agents..." button on a behaviour instance."
        
        :param behaviourId: Behaviour ID of corresponding behaviour.
        """
        raise NotImplemented
    
######## - Other
    @abstractmethod
    def quickSceneSetup(self):
        """
        User pressed the "Quick Setup" button (on the "Agent Attributes" tab).
        """
        raise NotImplemented

# END OF CLASS - UiControllerDelegate
###########################################


#===================================================================================


########################################
class UiController(PyswarmObject):
    """
    Unsurprisingly, UiController is the class responsible for handling all the UI elements of PySwarm.
    It builds the UI elements on request, handles memory, callbacks and so on, and cleans up the UI 
    components when needed.
    Note that it is only the UI handling logic contained here, it is a "dumb" window into the workings of
    other classes.  Button presses, user actions and so on are registered but are *not* actioned in 
    this class. Instead, event occurances are passed on to a UiControllerDelegate instance through the 
    corresponding callbacks, or are passed through to the attributes controller.  
    
    Generally, tracks the attributes controller instance to keep a handle on when behaviours are created, 
    deleted etc. and updates the attriubtes controller when the user makes a value change. 
    """
    
    def __init__(self, attributesController, delegate):
        """
        :param attributesController: an instantiated AttributesController instance
        :param delegate: an instantiated UiControllerDelegate instance, will be held as a weak reference.
        """
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
        """
        Nulls out the UI components, => will be rebuilt when needed.
        """
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
        else:
            self._delegate = None
        self._attributesController = state[1]
        
        self._recreateUiComponents()
        self._needsUiRebuild = True
    
########################    
    def _getDefaultBehaviourId(self):
        """
        Returns behaviour ID string of the current 'default' behaviour.
        """
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
        """
        Adds a new behaviour attributes set to the UI (i.e. a new behaviour tab).
        Builds all the necessary UI components and hooks them up to the relevant attributes.
        
        :param newBehaviourAttributes: behaviour attributes (AttributesBaseObject subclass).
        """
        self._makeDeleteBehaviourMenuItem(newBehaviourAttributes)
        self._makeSelectAgentsWithBehaviourMenuItem(newBehaviourAttributes, False)
        self._makeSelectAgentsWithBehaviourMenuItem(newBehaviourAttributes, True)
        self._makeChangeDefaultBehaviourMenuItem(newBehaviourAttributes)
        self._makeAssignAgentsToBehaviourMenuItem(newBehaviourAttributes)
        self._makeBehaviourTab(newBehaviourAttributes)
        
        self._tabLayout.setSelectTabIndex(self._tabLayout.getNumberOfChildren())
        
#####################        
    def removeBehaviourFromUI(self, behaviourAttributes):
        """
        Removes all UI components related to the given behaviour attributes set (i.e. deletes the behaviour tab).
        
        :param behaviourAttributes: behaviour attributes (AttributesBaseObject subclass).
        """
        behaviourId = behaviourAttributes.behaviourId
        
        for uiComponent in self._uiComponentToAttributesLookup[behaviourId]:
            try:
                uib.DeleteComponent(uiComponent)
            except:
                pass
        del self._uiComponentToAttributesLookup[behaviourId]
        
#####################
    def updateDefaultBehaviourInUI(self, oldDefaultId, newDefaultId):
        """
        Updates UI to reflect the changing of the 'default' behaviour from one behaviour instance to another.
        
        :param oldDefaultId: Behaviour ID of the instance that is now no longer the default.
        :param newDefaultId: Behaviour ID of the instance that has just been made the default.
        """
        for uiComponent in self._uiComponentToAttributesLookup[oldDefaultId]:
            # here, we go through all UI components linked to the previous default behaviour and
            # re-enabling ability to delete it, and silencing "cannot delete default" annotations...
            parent = uiComponent.getParent()
            if(parent == self._changeDefaultBehaviourMenu or parent == self._removeBehaviourMenu):
                uiComponent.setEnable(True)
                uiComponent.setAnnotation("")
            elif(parent == self._tabLayout):
                self._tabLayout.setTabLabel((uiComponent, oldDefaultId))
            elif(uiComponent.getAnnotation() == _CANNOT_REMOVE_BEHAVIOUR_ANNOTATION_):
                uiComponent.setEnable(True)
                uiComponent.setAnnotation(_REMOVE_BEHAVIOUR_ANNOTATION_)
                
        for uiComponent in self._uiComponentToAttributesLookup[newDefaultId]:
            # ...and here we do the opposite, for the newly-made default behaviour we disable
            # ability to delete it, and enable annotations to say as much.
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
        """
        Hides the UI components. 
        
        Note we must actually trash the PyMel UI component instances because they are held onto 
        within Maya by a weird system of string handles which can screw things up if we don't do this.
        """
        if(self.uiVisible):
            uib.DestroyWindowIfNecessary(self._uiWindow)
            self._recreateUiComponents()
            self._needsUiRebuild = False  
            
#####################         
    def buildUi(self):
        """
        Shows the UI components.
        
        Rebuilds the UI components if needed, and then makes them visible.
        """
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
        """
        Builds the menu strip and all it's sub-menus; observing the current set of existing behaviour instances.
        Hooks up all the callbacks and all that stuff.
        """
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
        """
        Adds an item to the "Change Default Behaviour" sub-menu, under "Behaviours" menu.
        
        :param attributes: behaviour attributes set (AttributesBaseObject subclass).
        """
        behaviourId = attributes.behaviourId
        uib.SetParentMenuLayout(self._changeDefaultBehaviourMenu)
        
        menuItem = uib.MakeMenuItem(behaviourId, lambda *args: self._didSelectChangeDefaultBehaviour(behaviourId))
        if(behaviourId == self._defaultBehaviourId): # if it's the default behaviour, grey it out & add an annotation.
            menuItem.setAnnotation(_CHANGE_DEFAULT_ANNOTATION_ % behaviourId)
            menuItem.setEnable(False)
        self._linkUiComponentToBehaviourId(menuItem, behaviourId)
        
########
    def _makeCreateBehaviourMenuItem(self, behaviourTypeName):
        """
        Adds an item to the "Create New Behaviour" sub-menu, under "Behaviours" menu.
        
        :param behaviourTypeName: Behaviour type name of corresponding behaviour class.
        """
        uib.MakeMenuItem(behaviourTypeName, lambda *args: self._didSelectAddNewBehaviour(behaviourTypeName))

########
    def _makeDeleteBehaviourMenuItem(self, attributes):
        """
        Adds an item to the "Remove Behaviour" sub-menu, under "Behaviours" menu.
        
        :param attributes: corresponding behaviour attributes set (AttributesBaseObject subclass).
        """
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
        """
        Adds an item to either "Select Agents With" or "Select Agents Without" sub-menus, under "Agents" menu.
        
        :param attributes: corresponding behaviour attributes set (AttributesBaseObject subclass).
        :param inverted: True = "Select Agents Without", False = "Select Agents With" 
        """
        behaviourId = attributes.behaviourId
        uib.SetParentMenuLayout(self._selectAgentsWithMenu if(not inverted) else self._selectAgentsNotWithMenu)
        menuItem = uib.MakeMenuItem(behaviourId, 
                                    lambda *args: self.delegate.makeAgentsWithBehaviourSelected(behaviourId, inverted))
        self._linkUiComponentToBehaviourId(menuItem, behaviourId)

########
    def _makeAssignAgentsToBehaviourMenuItem(self, attributes):
        """
        Adds an item to "Assign Agents To" sub-menu, under "Agents" menu.
        
        :param attributes:  corresponding behaviour attributes set (AttributesBaseObject subclass).
        """
        behaviourId = attributes.behaviourId
        uib.SetParentMenuLayout(self._assignAgentsToMenu)
        menuItem = uib.MakeMenuItem(("%s..." % behaviourId),
                                    lambda *args: self.delegate.showAssignAgentsWindowForBehaviour(behaviourId))
        self._linkUiComponentToBehaviourId(menuItem, behaviourId)

#####################       
    def _buildUiMainPanel(self):
        """
        Builds the main, top panel of the UI; with particle name, scene bounds, image, status bar and so on.
        """
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
        """
        Builds the left-most tab "Agent Attributes", creating it with the current values from the given attribute
        sets and hooking up the UI components to update the sets when changed by the user.
        
        :param movementAttributes: AgentMovementAttributes instance.
        :param perceptionAttributes: AgentPerceptionAttributes instance.
        """
        formLayout = uib.MakeFormLayout("Agent Attributes")
        scrollLayout = uib.MakeScrollLayout()
        
        movementLayout = uib.MakeFrameLayout("Agent Movement")
        movementAttributes.populateUiLayout()
        uib.SetAsChildLayout(movementLayout)
        
        awarenessLayout = uib.MakeFrameLayout("Agent Perception")
        perceptionAttributes.populateUiLayout()
        uib.SetAsChildLayout(awarenessLayout, scrollLayout)
        
        buttonStripLayout = uib.MakeButtonStrip((("Quick Setup",
                                                  self._didPressQuickSetup,
                                                  "Makes some initial changes to the Maya scene to get up and running."),
                                                 ("Load Defaults",
                                                  lambda *args: self._didSelectRestoreAgentValues(movementAttributes.behaviourId, 
                                                                                                  perceptionAttributes.behaviourId),
                                                  "Reset agent attributes to default values."),))[0]
        
        uib.SetAsChildLayout(buttonStripLayout)
        uib.DistributeButtonedWindowInFormLayout(formLayout, scrollLayout, buttonStripLayout)
        uib.SetAsChildLayout(formLayout)
        
########
    def _makeBehaviourTab(self, behaviourAttributes, isDefaultBehaviour=False):
        """
        Builds a new behaviour tab in the UI with the given behaviour attributes set, using the current values and
        hooking up the UI components to update the attributes as necessary.
        
        :param behaviourAttributes: behaviour attributes set (AttributesBaseObject subclass).
        :param isDefaultBehaviour: True = corresponding behaviour to the attribute set is the default, False = not the default.
        """
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
        """
        Updates UiController's internal record of UI components that are linked to the given behaviour.
        This is necessary so that we know which components to remove/change when the behaviour is deleted or updated.
         
        :param component: the PyMel UI component.
        :param behaviourId: Behaviour ID of the corresponding behaviour.
        """
        componentList = self._uiComponentToAttributesLookup.get(behaviourId)
        if(componentList is None):
            componentList = []
            self._uiComponentToAttributesLookup[behaviourId] = componentList
        
        componentList.append(component)

#####################        
    def _didSelectOpenFile(self, *args):
        """
        Called when user selects "Open File..." option from "File" menu.
        Queries user for a file path, then passes the details through to the delegate.
        """
        filePath = uib.GetFilePathFromUser(True, fl.SaveFolderLocation(), fl.SaveFileExtension())
        if(filePath is not None):
            util.EvalDeferred(self.delegate.openFile, filePath)
 
########           
    def _didSelectSaveAs(self, *args):
        """
        Called when user selects "Save As..." option from "File" menu.
        Queries user for a file path, then passes the details through to the delegate.
        """
        filePath = uib.GetFilePathFromUser(False, fl.SaveFolderLocation(), fl.SaveFileExtension())
        if(filePath is not None):
            self.delegate.saveToFile(filePath)
            
########
    def _didPressQuickSetup(self, *args):
        """
        Called when user pressed the "Quick Setup" button.
        Queries user for confirmation, then passes call through to the delegate if necessary.
        """
        if(uib.GetUserConfirmation("Quick Scene Setup", "This will set some of your nParticle attribute values within Maya "
                                   + "(friction, self collision etc) to get the swarm up and running.\n"
                                   + "***This includes changing the nucleus space scale and enabling it's ground plane.***"
                                   + "\nContinue?")):
            self.delegate.quickSceneSetup()

########            
    def _didSelectRestoreAgentValues(self, movementId, perceptionId):
        """
        User pressed "Load Defaults" button on the "Agent Attributes" tab.
        Queries user for confirmation, and passes call to delegate if required. 
        
        :param movementId: attribute ID of the AgentMovementAttributes instance.
        :param perceptionId: attribute ID of the AgentPerceptionAttributes instance.
        """
        if(uib.GetUserConfirmation("Load Defaults", "Restore default values to agent attributes?")):
            self.delegate.restoreDefaultValues(movementId)
            self.delegate.restoreDefaultValues(perceptionId)
    
########
    def _didSelectRestoreDefaultValues(self, behaviourId):
        """
        User pressed "Load Defaults" button on a behaviour instance tab.
        Queries user for confirmation, and passes call to delegate if required. 
        
        :param behaviourId: behaviour ID of behaviour corresponding to that tab.
        """
        message = ("Restore default values to %s?" % 
                   ("behaviour \"%s\"" % behaviourId) if(behaviourId is not None) else "all attributes")
        if(uib.GetUserConfirmation("Load Defaults", message)):
            self.delegate.restoreDefaultValues(behaviourId)

########
    def _didSelectMakeValuesDefault(self, behaviourId):
        """
        User selected "Make Values Default" from the PySwarm "Edit" menu.
        Queries user for confirmation, and passes call to delegate if required. 
        
        :param behaviourId: currently, always None.
        """
        if(behaviourId is None):
            message = "Update default values with all current attribute values?"
        else:
            message = ("Update default values with current attribute values for behaviour \"%s\"?" %
                       behaviourId)
        
        if(uib.GetUserConfirmation("Make Values Default", message)):
            self.delegate.makeValuesDefault(behaviourId)
        
########
    def _didSelectChangeDefaultBehaviour(self, behaviourId):
        """
        User chose option from "Change Default" sub-menu, under "Behaviours" menu.
        
        :param behaviourId: Behaviour ID of the corresponding behaviour.
        """
        util.EvalDeferred(self.delegate.changeDefaultBehaviour, behaviourId)
                  
########
    def _didSelectAddNewBehaviour(self, behaviourTypeName):
        """
        User chose option from "Create New Behaviour" sub-menu, under "Behavoiurs" menu.
        
        :param behaviourTypeName: corresponding behaviour class type name.
        """
        util.EvalDeferred(self.delegate.addNewBehaviour, behaviourTypeName)
 
########
    def _didSelectRemoveBehaviour(self, behaviourId):
        """
        User chose option from "Remove Behaviour" sub-menu, under "Behavoiurs' menu.
        Queries user for confirmation, and passes call to delegate if required. 
        
        :param behaviourId:  Behaviour ID of the corresponding behaviour.
        """
        if(uib.GetUserConfirmation("Remove Behaviour", ("Delete behaviour \"%s\"?" % behaviourId))):
            util.EvalDeferred(self.delegate.removeBehaviour, behaviourId)
  
########
    def _didSelectRemoveAllBehaviours(self):
        """
        User chose "Remove All Behaviours" option from the "Behaviours" menu.
        Queries user for confirmation, and passes call to delegate if required. 
        """
        if(uib.GetUserConfirmation("Remove All Behaviours", 
                                   ("Delete all behaviours (default behaviour \"%s\" will not be deleted)?" 
                                    % self._defaultBehaviourId))):
            util.EvalDeferred(self.delegate.removeAllBehaviours)
 
########
    def _didSelectQuit(self, *args):
        """
        User chose "Quit" option from "File" menu.
        Queries user for confirmation, and passes call to delegate if required. 
        """
        if(uib.GetUserConfirmation("Quit", ("This will remove this %s instance from your scene.\nAre you sure?" 
                                            % pi.PackageName()))):
            util.EvalDeferred(self.delegate.quitSwarmInstance)
            
########
    def _didSelectShowDocs(self, *args):
        """
        User chose "Project Home Page..." option from PySwarm "Help" menu.
        Launches project home page in external browser.
        """
        util.LaunchWebPage(pi.PackageHomePage())
    
########
    def _didSelectAbout(self, *args):
        """
        User chose "About" option from PySwarm "Help" menu.
        Displays project info in a dismissable info box.
        """
        uib.DisplayInfoBox(pi.PackageInfo(), ("%s v%s" % (pi.PackageName(), pi.VersionNumber())))
            

# END OF CLASS - UiController
########################################
            