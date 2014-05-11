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


import boidBaseObject as bbo
import agents.agentsController as agc
import attributes.attributesController as bat
import behaviours.behavioursController as bbc
import uiController as uic
import boidTools.util as util
import boidTools.agentSelectionWindow as asw
import boidTools.sceneInterface as scene
import resources.fileLocations as fl
import resources.packageInfo as pi

import os
import sys
try:
    import cPickle as pickle
except:
    import pickle



###########################################
_SwarmInstances_ = [] # the list of SwarmController instances active within the Maya scene

#####
def _InitialiseSwarm(particleShapeNode=None, boundingLocators=None):
    """Create new PySwarm instance.
    
    Creates a new swarm instance for the given nParticle node.
    If a swarm instance already exists for that nParticle node, it will be replaced.
    
    :param particleShapeNode: The nParticle shape node, can be: 
                                - string giving full Maya scene path to instance
                                - Pymel nParticle PyNode
                                - None (in which case the method will check for a selected nParticle node within the Maya scene).
    :param boundingLocators: *Two* locators, representing opposite corners of the bounding box for the PySwarm instance. Can be:
                                - List of strings giving full Maya paths to locator instances
                                - List of PyMel Locator Nodes
                                - None (in which case, method will look for selected Locator nodes in the scene).
    """
    
    global _SwarmInstances_
    _SceneSetup(False)  
    
    if(particleShapeNode is None): # look for selected nParticle node in Maya scene, if none passed as arguments
        selectedParticleNodes = scene.GetSelectedParticleShapeNodes()
        if(selectedParticleNodes):
            newSwarms = [_InitialiseSwarm(particleNode, boundingLocators) 
                         for particleNode in selectedParticleNodes]            
            return newSwarms if(len(newSwarms) > 1) else newSwarms[0]
        else:
            raise RuntimeError("No particle node specified - you must either select one in the scene " +
                               "or pass in a reference via the \"particleShapeNode\" argument to this method.")
    else:
        try:
            RemoveSwarmInstanceForParticle(particleShapeNode)
        except:
            pass
        
        if(isinstance(particleShapeNode, basestring)): # if a string, we assume it's a Maya path to an nParticle node...
            particleShapeNode = scene.PymelObjectFromObjectName(particleShapeNode, True, scene.ParticlePymelType())
        elif(not isinstance(particleShapeNode, scene.ParticlePymelType())): # ...otherwise it better be a PyMel node
            raise TypeError("particleShapeNode unrecognised (expected Maya object path to nParticle instance, " +
                            (" or Pymel type %s, got %s)." % (scene.ParticlePymelType(), type(particleShapeNode))))
        
        if(boundingLocators is None): # look for selected Locators in the scene, if none passed as arguments...
            selectedLocators = scene.GetSelectedLocators()
            boundingLocators = selectedLocators if(len(selectedLocators) >= 2) else None
        else: # ...otherwise, assuming is either list of Maya paths to Locators, or PyMel Locator nodes
            if(not isinstance(boundingLocators, (tuple, list)) or len(boundingLocators) < 2):
                raise ValueError("boundingLocators unrecognised (expected (Locator,Locator) tuple, or <None> - got: %s)." 
                                 % boundingLocators)
            elif(isinstance(boundingLocators[0], basestring) and isinstance(boundingLocators[1], basestring)):
                locator1 = scene.PymelObjectFromObjectName(boundingLocators[0], True, scene.LocatorPymelType())
                locator2 = scene.PymelObjectFromObjectName(boundingLocators[1], True, scene.LocatorPymelType())
                boundingLocators = (locator1, locator2)
            elif(not isinstance(boundingLocators[0], scene.LocatorPymelType()) or 
                 not isinstance(boundingLocators[1], scene.LocatorPymelType())):
                raise TypeError("boundingLocators unrecognised (expected tuple pair of Maya object paths to Locator instances, " +
                                ("tuple pair of Pymel type %s, or <None> - got (%s,%s))." 
                                 % (scene.LocatorPymelType(), type(boundingLocators[0]), type(boundingLocators[1]))))
            
        
        newSwarm = SwarmController(particleShapeNode, boundingLocators)
        _SwarmInstances_.append(newSwarm)
        newSwarm.showUI()
        
        util.LogInfo("Created new %s instance for nParticle %s" % (pi.PackageName(), newSwarm.particleShapeName))
        
        return newSwarm

#####
def InitialiseSwarm(particleShapeNode=None, boundingLocators=None):
    return util.SafeEvaluate(True, _InitialiseSwarm, particleShapeNode, boundingLocators)
InitialiseSwarm.__doc__ = _InitialiseSwarm.__doc__ 

#############################
def Show():
    """
    Will make the UIs visible (if not already) for all existing swarm instances.
    """
    global _SwarmInstances_
    for swarmInstance in _SwarmInstances_:
        swarmInstance.showUI()

#############################
def GetSwarmInstanceForParticle(particleShapeNode):
    """
    Gets the corresponding swarm instance for the given particle node,
    if it exists (otherwise returns None).
    
    :param particleShapeNode: Full Maya path, or PyMel node, for nParticle shape node.
    """
    global _SwarmInstances_
    pymelShapeNode = scene.PymelObjectFromObjectName(particleShapeNode, True)
    for swarmController in _SwarmInstances_:
        if(pymelShapeNode.name() == swarmController.particleShapeName):
            return swarmController
        
    util.LogError("No %s instance exists for %s" (pi.PackageName(), particleShapeNode))

##############################
def RemoveSwarmInstanceForParticle(particleShapeNode):
    """
    Deletes PySwarm instance for given nParticle node, if it exists.
    The nParticle node itself is not affected.
    
    :param particleShapeNode: Full Maya path, or PyMel node, for nParticle shape node.
    """
    RemoveSwarmInstance(GetSwarmInstanceForParticle(particleShapeNode))

#####
def _RemoveSwarmInstance(swarmInstance):
    """
    Deletes the given PySwarm instance from the Maya scene.
    
    :param swarmInstance: a SwarmController instance.
    """
    global _SwarmInstances_
    
    if(swarmInstance in _SwarmInstances_):
        swarmInstance.hideUI()
        _SwarmInstances_.remove(swarmInstance)
        name = swarmInstance.particleShapeName
        swarmInstance._decommision()
        
        util.LogInfo("%s instance for %s deleted." % (pi.PackageName(), name))
    elif(swarmInstance is not None and isinstance(swarmInstance, SwarmController)):
        swarmInstance.hideUI()
        swarmInstance._decommision()
        
        util.LogWarning("Attempt to delete unregistered swarm instance - likely causes:\n"
                        "swarmController module as been reloaded after the initial import, leaving \'orphan\' instances, or,\n"
                        "an instance has been created indepedently by the user.\n"
                        "It is recommended that swarm management is done only via the swarmController module methods provided.")
    elif(str(type(swarmInstance) == str(SwarmController))):
        raise RuntimeError("%s module-level variables missing - likely due to module being reloaded. "
                           "Recommend you close down & re-initialise completely." 
                           % pi.PackageName())
    else:
        raise TypeError("Got %s of type %s (expected %s)." % (swarmInstance, type(swarmInstance), SwarmController))

#####
def RemoveSwarmInstance(swarmInstance):
    return util.SafeEvaluate(True, _RemoveSwarmInstance, swarmInstance)
RemoveSwarmInstance.__doc__ = _RemoveSwarmInstance.__doc__

#####
def RemoveAllSwarmInstances():
    """
    Removes every active PySwarm instance within the current scene.
    """
    for swarmInstance in _SwarmInstances_[:]:
        RemoveSwarmInstance(swarmInstance)

#############################         
_PICKLE_PROTOCOL_VERSION_ = 2 # Safer to stick to constant version rather than using "highest"

#####
def _SaveSceneToFile(fileLocation=None):
    """
    Saves all active PySwarm instances to a file.
    
    This will save the current state of all active PySwarm instances to a file, attribute settings, preferences,
    agent parameters, basically everything.  Note that it will not save any part of the Maya scene - just the 
    PySwarm setup. Ideally this will be done each time you save your Maya scene, in order to keep everything in sync. 
    
    It's probably worth noting that this used Pickle - which is great, but also a little picky in terms of what can
    be saved and what can't.  If you are extending this code and this method is throwing errors, read up on what can be 
    Pickled and what can't (it's usually lambda's and weakref's that cause problems).
    
    :param fileLocation: desired file location as string, or None (in which case the 'default' location will be used).
    """
    global _PICKLE_PROTOCOL_VERSION_
    global _SwarmInstances_
    
    fileLocation = util.InitVal(fileLocation, fl.SaveFileLocation())
    saveFile = open(fileLocation, "wb")
    try:
        pickle.dump(_SwarmInstances_, saveFile, _PICKLE_PROTOCOL_VERSION_)
        saveFile.close()
        util.LogInfo("Saved %s scene to file %s" % (pi.PackageName(), fileLocation))
    except Exception, e:
        saveFile.close()
        os.remove(saveFile.name)
        util.LogError("Could not save PySwarm scene - Pickling error: %s" % e)
    
#####
def SaveSceneToFile(fileLocation=None):
    return util.SafeEvaluate(True, _SaveSceneToFile, fileLocation)
SaveSceneToFile.__doc__ = _SaveSceneToFile.__doc__
    
#####
def _LoadSceneFromFile(fileLocation=None):
    """
    Loads a previously saved PySwarm state from a file (i.e. from a previous 'SaveSceneToFile' operation).
    
    :param fileLocation: path to a previous save, or None, in which case the 'default' location will be checked.
    """
    global _SwarmInstances_
    
    fileLocation = util.InitVal(fileLocation, fl.SaveFileLocation())
    if(os.path.exists(fileLocation)):
        try:
            readFile = open(fileLocation, "rb")
            
            while(_SwarmInstances_): # it's VERY IMPORTANT to tear down the UI components *first* before rebuilding new ones because,
                _SwarmInstances_.pop().hideUI() # in another little Pymel quirk, they are referenced by "handle" and not pointer address
                                                # which means that the wires get crossed if we create the new before deleting the old
            newInstances = pickle.load(readFile)
        except Exception as e:
            util.LogWarning("Cannot restore %s session - error \"%s\" while reading file: %s" % 
                            (pi.PackageName(), e, fileLocation))
            raise e
        
        
        for swarmInstance in newInstances:
            swarmInstance.showUI()
            _SwarmInstances_.append(swarmInstance)
            
        util.LogInfo("Opened %s scene from file %s" % (pi.PackageName(), fileLocation))
    else:
        raise ValueError("Cannot open file %s" % fileLocation)

#####
def LoadSceneFromFile(fileLocation=None):
    return util.SafeEvaluate(True, _LoadSceneFromFile, fileLocation)
LoadSceneFromFile.__doc__ = _LoadSceneFromFile.__doc__

#############################        
def _OnFrameUpdated():
    """
    Processes one iteration of a frame-number change in the Maya scene.
    
    Updates all current PySwarm instances with current Maya scene info, processes it, then updates the Maya scene.
    Should be called once every time the frame number changes in the Maya scene.
    """
    global _SwarmInstances_
    for swarmInstance in _SwarmInstances_:
        swarmInstance._onFrameUpdated()

###########################################
_HaveRunSceneSetup = False # static to ensure that _SceneSetup operations are not duplicated

#####
def _SceneSetup(calledExternally=True):
    """
    Configures the current Maya scene to work properly, and automatically, with PySwarm.
    
    Adds script nodes (which can be viewed in Maya's expression editor) and script jobs (which can be viewed
    using the Mel command 'scriptJob') which will automatically save/load the PyMel instances when the Maya
    scene is saved/opened, and will automatically update each time the scene frame number is changed. 
    
    :param calledExternally: should be False if called from the automotically generated script nodes, True otherwise.
    """
    global _HaveRunSceneSetup
    
    if(not _HaveRunSceneSetup):
        moduleSelf = sys.modules[__name__]
        util.AddScriptNodesIfNecessary(moduleSelf, _SceneSetup, _OnFrameUpdated, _SceneTeardown)
        util.AddSceneSavedScriptJobIfNecessary(SaveSceneToFile)
        
        try:
            _LoadSceneFromFile()
            util.LogInfo("Scene setup complete.")
        except:
            message = ("Scene setup complete.\n\t\t\tNo previous %s scene file found" % pi.PackageName())
            if(not calledExternally):
                message += '.'
            else:
                message += (" - run %s method %s to create a swarm instance." % (__name__, InitialiseSwarm.__name__))
            util.LogInfo(message)
            
        _HaveRunSceneSetup = True

#####
def _SceneTeardown():
    """
    Should be called when the Maya scene is closed, will close & clean up the PySwarm UI and auto-generated script jobs.
    """
    global _HaveRunSceneSetup
    
    util.OnSceneTeardown()
    for swarmInstance in _SwarmInstances_:
        swarmInstance.hideUI()
    
    util.LogInfo("Cleaned up resources.")
    _HaveRunSceneSetup = False

# END OF MODULE METHODS
#========================================================



#========================================================
class SwarmController(bbo.BoidBaseObject, uic.UiControllerDelegate):
    """
    Essentially the entry point for PySwarm, each SwarmController instance corresponds to an nParticle node 
    within the Maya scene, and presents a public API for controlling more or less everything that PySwarm 
    can do via code, should you wish to do so (though using the UI is recommended).
    
    The SwarmController is responsible for coordinating all the different "sub"controllers (agents controller, 
    ui controller, et cetera) together and passing information between them.
    
    SwarmControllers should not be instantiated directly unless you know what you're doing.  Instead, you should
    use the module-level methods defined above - InitialiseSwarm, GetSwarmInstanceForParticle, 
    RemoveSwarmInstance and so on, to create or access the PySwarm instances in your scene.
    """
    
    def __init__(self, particleShapeNode, boundingLocators=None):
        """
        The bounding locators represent opposite corners of a bounding box the this PySwarm instance.
        
        :param particleShapeNode: nParticle shape node, must be either full Maya path (string), or a PyMel PyNode object.
        :param boundingLocators: *two* locators as either full Maya path or PyMel Locator objects, or None for default bounding box.
        """
        super(SwarmController, self).__init__()
        
        self._attributesController = bat.AttributesController(particleShapeNode, SaveSceneToFile, boundingLocators)
        self._behavioursController = bbc.BehavioursController(self._attributesController)
        self._agentsController = agc.AgentsController(self._attributesController, self._behavioursController)
        self._uiController = uic.UiController(self._attributesController, self)
        self._behaviourAssignmentSelectionWindow = asw.AgentSelectionWindow(self._attributesController.globalAttributes)
        
        self._agentsController._buildParticleList()

#############################        
    def __str__(self):
        return self._agentsController.__str__()

########    
    def _getMetaStr(self):
        return self._agentsController.metaStr

#############################    
    def __getstate__(self):
        state = super(SwarmController, self).__getstate__()
        state["_behaviourAssignmentSelectionWindow"] = None
        
        return state

########        
    def __setstate__(self, state):
        super(SwarmController, self).__setstate__(state)
        self._behaviourAssignmentSelectionWindow = asw.AgentSelectionWindow(self._globalAttributes)
                                                                            
        self.showUI()

#############################
    def _getGlobalAttributes(self):
        return self._attributesController.globalAttributes
    _globalAttributes = property(_getGlobalAttributes)
    
#############################    
    def _getParticleShapeName(self):
        return self._globalAttributes.particleShapeNode.name()
    particleShapeName = property(_getParticleShapeName)

#############################    
    def _getAttributesController(self):
        return self._attributesController
    attributesController = property(_getAttributesController)
    
#############################        
    def _onFrameUpdated(self):
        """
        Processes one iteration of a frame-number change in the Maya scene.
        
        Reads info from the scene & updates internal state, process the info, then updates the nParticle
        instance within the scene with the results. 
        """
        try:
            self._globalAttributes.setStatusReadoutWorking(1, "Reading...")
            
            self._attributesController.onFrameUpdated()
            
            if(self._globalAttributes.enabled):
                self._behavioursController.onFrameUpdated()
                self._agentsController.onFrameUpdated()
            
            self._globalAttributes.setStatusReadoutIdle()
            
            self._attributesController.onCalculationsCompleted()
            self._behavioursController.onCalculationsCompleted()
            self._agentsController.onCalculationsCompleted()
            
        except Exception as e:
            self._globalAttributes.setStatusReadoutError()
            util.StopPlayback()
            util.LogException(e)

#############################    
    def enable(self):
        """
        Re-enables if previously disabled (when disabled, will *not* process or update when the 
        Maya scene frame number changes). 
        """
        if(not self._globalAttributes.enabled):
            self._globalAttributes.enabled = True
            util.LogInfo("updates are now ACTIVE.", self.particleShapeName)
        else:
            util.LogWarning("updates already enabled.", self.particleShapeName)

########
    def disable(self):
        """
        If disabled, will *not* process or update when the Maya scene frame number changes.
        Can be re-enabled with the 'enable' method.
        """
        self._globalAttributes.enabled = False
        util.LogInfo("updates DISABLED.", self.particleShapeName)
        
########
    def _decommision(self):
        """
        Kind of a destructor, cleans up internal resources used by this SwarmController instance.
        """
        self._attributesController = None
        self._behavioursController = None
        self._agentsController = None
        self._uiController = None
        self._behaviourAssignmentSelectionWindow  = None
        
########
    def showUI(self):
        """
        Shows the PySwarm UI for this swarm instance, if not showing already.
        """
        self._uiController.buildUi()

########            
    def hideUI(self):
        """
        Hides the PySwarm UI for this swarm instance, if not hidden already.
        """
        self._uiController.hideUI()
        self._behaviourAssignmentSelectionWindow.closeWindow()
 
########       
    def openFile(self, filePath):
        """
        Will load a PySwarm scene from the given file.  Note - will load *entire* PySwarm state, i.e. for multiple
        instances if they exist, not just this instance in isolation.
        
        :param filePath: path to previously saved PySwarm state. 
        """
        util.EvalDeferred(LoadSceneFromFile, filePath)

######## 
    def saveToFile(self, filePath=None):
        """
        Saves current PySwarm state to the given filepath.  Will save the *entire* PySwarm state, i.e. for multiple
        instance if they exist, not just this one in isolation.
        
        :param filePath: path to save the state, or None to use 'default' location.
        """
        SaveSceneToFile(filePath)
        
########
    def showDebugLogging(self, show):
        """
        Enables/disables verbose debug logging to the Maya script editor.  If disabled, warnings
        and errors will still show up. 
        
        :param show: True == enable dubug logging, False == disable debug logging.
        """
        if(show):
            util.SetLoggingLevelDebug()
        else:
            util.SetLoggingLevelInfo()
        
########
    def showPreferencesWindow(self):
        """
        Shows the user preferences UI window.
        """
        self._attributesController.showPreferencesWindow()
 
########
    def quitSwarmInstance(self):
        """
        Removes this SwarmController instance from the Maya scene.  The corresponding nParticle node
        in the scene will not be affected.
        """
        util.EvalDeferred(RemoveSwarmInstance, self)
        
########
    def refreshInternals(self):
        """
        Re-reads information from the Maya scene and updates the internal state. 
        """
        self._attributesController.onFrameUpdated()
        self._behavioursController.onFrameUpdated()
        self._agentsController.refreshInternals()
        
        self._attributesController.purgeRepositories()
        
        util.LogInfo("Refreshed internal state...")

########        
    def restoreDefaultValues(self, behaviourId=None):
        """
        Will change attribute values back the their defaults, similar to Maya's 'reset settings'.
        
        :param behaviourId: Specific behaviour ID to only reset attributes for that behaviour, or 
                            None to reset all behaviours. 
        """
        self._attributesController.restoreDefaultAttributeValuesFromFile(behaviourId)
        
########
    def makeValuesDefault(self, behaviourId=None):
        """
        Makes the current attribute values the default ones, i.e. subsequent calls to 'restoreDefaultValues'
        will reset attributes values to how they are now.
        
        Note that if multiple instances for a given behaviour type exist, values will be taken from the 
        one that was created first. 
        
        :param behaviourId: Specific behaviour ID to only set attributes values for that behaviour, or 
                            None to set attribute all behaviours (note that any behaviour types not currently
                            instantiated will not be affected). 
        """
        util.LogDebug("Re-setting default attribute values with current values...")
        self._attributesController.makeCurrentAttributeValuesDefault(behaviourId)
        
########
    def changeDefaultBehaviour(self, behaviourId):
        """
        Sets the given behaviour to be the default.
        
        :param behaviourId: Behaviour ID of behaviour instance to be the default. 
        """
        oldDefaultBehaviourId = self._globalAttributes.defaultBehaviourId
        if(self._attributesController.changeDefaultBehaviour(behaviourId)):
            self._uiController.updateDefaultBehaviourInUI(oldDefaultBehaviourId, self._globalAttributes.defaultBehaviourId)
        
########       
    def addNewBehaviour(self, behaviourTypeName):
        """
        Creates a new behaviour instance of the given type. 
        
        :param behaviourTypeName: Behaviour type, e.g. "ClassicBoid", "FollowPath".
        """
        newBehaviour = self._attributesController.addBehaviourForTypeName(behaviourTypeName)
        if(newBehaviour is not None):
            self._onNewBehaviourAttributesAdded(newBehaviour)
            
########
    def removeBehaviour(self, behaviourId):
        """
        Removes the behaviour instance with the given behaviour ID.  Though if you try 
        to delete the default behaviour, it will have no effect.
        
        :param behaviourId: Behaviour ID of behaviour instance to be deleted. 
        """
        deletedAttributes = self._attributesController.removeBehaviour(behaviourId)
        if(deletedAttributes is not None):
            self._onBehaviourAttributesDeleted(deletedAttributes)
        else:
            util.LogWarning("Could not remove behaviour \"%s\"" % behaviourId)

########           
    def removeAllBehaviours(self):
        """
        Removes all current behaviour instances except for the default. 
        """
        for behaviourId in self._attributesController.behaviourTypeNamesList():
            self.removeBehaviour(behaviourId)

########          
    def makeAgentsWithBehaviourSelected(self, behaviourId, invertSelection):
        """
        Will make all agents that are currently following the given behaviour selected within
        the Maya scene (useful for quickly identifying agents following a behaviour in Maya's viewport).
        
        :param behaviourId: Behaviour ID of the behaviour instance.
        :param invertSelection: if False, all agents *not* following the behaviour will be selected.
        """
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        currentSelection = self._agentsController.getAgentsFollowingBehaviour(behaviour)
        if(invertSelection):
            allAgents = set(self._agentsController.allAgents)
            currentSelection = list(allAgents.difference(set(currentSelection)))
        
        particleIds = [agent.agentId for agent in currentSelection]
        scene.SelectParticlesInList(particleIds, self.particleShapeName) 
        
########
    def showAssignAgentsWindowForBehaviour(self, behaviourId):
        """
        Shows the UI window for assigning agents to a given behaviour.
        
        :param behaviourId: Behaviour ID of the behaviour instance.
        """
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        currentSelection = [agent.agentId for agent in self._agentsController.getAgentsFollowingBehaviour(behaviour)]
        
        self._behaviourAssignmentSelectionWindow.dataBlob = behaviourId
        self._behaviourAssignmentSelectionWindow.show("Assign agents to \"%s\"" % behaviourId, 
                                                      currentSelection, self._onAgentSelectionCompleted)  
        
########
    def quickSceneSetup(self):
        """
        Quickly configures the swarm instance with some basic 'vanilla' settings that should get the PySwarm 
        setup up & running with the current Maya scene (these settings can be changed in the preferences).  
        """
        scene.QuickSceneSetup(self.particleShapeName, 
                              self._globalAttributes.quickSetupEnableSelfCollide, self._globalAttributes.quickSetupDisableFriction,
                              self._globalAttributes.quickSetupDisableIgnoreGravity, self._globalAttributes.quickSetupChangeRenderType,
                              self._globalAttributes.quickSetupEnableGroundPlane, self._globalAttributes.quickSetupChangeSpaceScale,
                              self._globalAttributes.quickSetupTranslateAbovePlane)

########
    def assignAgentsToBehaviour(self, agentIdsList, behaviourId):
        """
        Assigns the given agents to the given behaviour instance. 
        
        :param agentIdsList: List of agent IDs (as integers), or Agent instances.
        :param behaviourId: Behaviour ID of the behaviour instance.
        """
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        self._agentsController.makeAgentsFollowBehaviour(agentIdsList, behaviour)
 
########    
    def getAssignedAgentIdsForBehaviour(self, behaviourId):
        """
        Returns sorted list of agent IDs (as integers) of Agents current assigned to the given behaviour instance.
        
        :param behaviourId: Behaviour ID of the behaviour instance.
        """
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        return [agent.agentId 
                for agent in sorted(self._agentsController.getAgentsFollowingBehaviour(behaviour))]
            
#############################                  
    def addClassicBoidBehaviour(self):
        """
        Creates a behaviour instance of type ClassicBoid. 
        """
        newBehaviour = self._attributesController.addClassicBoidAttributes()
        self._onNewBehaviourAttributesAdded(newBehaviour)
        
########
    def addGoalDrivenBehaviour(self, wallLipGoal=None, basePyramidGoalHeight=None, finalGoal=None):
        """
        Creates a behaviour instance of type GoalDriven.
        
        :param wallLipGoal: Locator (Maya path, or PyMel Locator) giving location of intermediate 'wall-lip' goal.
        :param basePyramidGoalHeight: Height, in Maya scene units, from ground-level base of wall to wall-lip goal.
        :param finalGoal: Locator giving location of final beyond-the-wall goal.
        """
        newBehaviour = self._attributesController.addGoalDrivenAttributes(wallLipGoal, basePyramidGoalHeight, finalGoal)
        self._onNewBehaviourAttributesAdded(newBehaviour)
        
########        
    def addFollowPathBehaviour(self, pathCurve=None):
        """
        Creates a behaviour instance of type FollowPath.
        
        :param pathCurve: Nurbs curve (Maya path, or PyMel PyNode instance) giving the path to follow; or None to select it later.
        """
        newBehaviour = self._attributesController.addFollowPathAttributes(pathCurve)
        self._onNewBehaviourAttributesAdded(newBehaviour)

#############################      
    def _onNewBehaviourAttributesAdded(self, newBehaviourAttributes):
        """
        Creates a new corresponding behaviour instance for the given behaviour attributes set.
        Should be called when a new attributes set has been created.
        
        :param newBehaviourAttributes: newly created attributes instance (AttributesBoseObject subclass).
        """
        self._behavioursController.createBehaviourForNewAttributes(newBehaviourAttributes)
        self._uiController.addNewBehaviourToUI(newBehaviourAttributes)
        
        util.LogInfo("Added new behaviour \"%s\"" % newBehaviourAttributes.behaviourId)

#############################        
    def _onBehaviourAttributesDeleted(self, deletedAttributes):
        """
        Deletes the corresponding behaviour instance for the given attriutes set, and re-assigns
        any agents that were following it to the default behaviour.
        Should be called when the attributes set has been deleted.
        
        :param deletedAttributes: recently deleted attributes instance (AttributesBoseObject subclass).
        """
        deletedBehaviourId = deletedAttributes.behaviourId
        deletedBehaviour = self._behavioursController.removeBehaviourWithId(deletedBehaviourId)
        agentsFollowingOldBehaviour = self._agentsController.getAgentsFollowingBehaviour(deletedBehaviour)
        
        self._agentsController.makeAgentsFollowDefaultBehaviour(agentsFollowingOldBehaviour)
        self._uiController.removeBehaviourFromUI(deletedAttributes)
        
        util.LogInfo("Removed behaviour \"%s\"" % deletedBehaviourId)
        
##############################
    def _onAgentSelectionCompleted(self, selectionWindow, selectedAgentsList, selectionDisplayString):
        """
        Callback method for agent selection window, should be called when assignation process (using the window) completes.
        
        Assigns the agents selected via the UI window to it's corresponding behaviour instance.  Any deselected agents 
        with no explicit behaviour will be assigned to the default behaviour.
        
        :param selectionWindow: the selection window making the callback, an AgentSelectionWindow instance. 
        :param selectedAgentsList: List of agent IDs (integers) to be assigned.
        :param selectionDisplayString: String that can be used to describe the selection in any UI displays.
        """

        if(selectionWindow is self._behaviourAssignmentSelectionWindow):
            behaviourId = selectionWindow.dataBlob
            defaultBehaviourId = self._globalAttributes.defaultBehaviourId
            
            toUnassign = selectionWindow.originalSelection.difference(selectedAgentsList)
            if(toUnassign):
                if(behaviourId == defaultBehaviourId):
                    util.LogWarning("Cannot implicitly un-assign agents from default behaviour \"%s\"." % 
                                    behaviourId)
                else:
                    self._agentsController.makeAgentsFollowDefaultBehaviour(toUnassign)

            behaviour = self._behavioursController.behaviourWithId(behaviourId)            
            self._agentsController.makeAgentsFollowBehaviour(selectedAgentsList, behaviour)
            self._behaviourAssignmentSelectionWindow.dataBlob = None
            
            if(selectedAgentsList):
                util.LogInfo("The following agents are now assigned to behaviour \"%s\": %s." %
                             (behaviourId, ', '.join([str(agentId) for agentId in selectedAgentsList])))
            elif(behaviourId != defaultBehaviourId):
                util.LogInfo("All agents previously following \"%s\" now assigned to default behaviour \"%s\"." 
                             % (behaviourId, defaultBehaviourId))
                

# END OF CLASS - SwarmController
##################################




#############################
# RUN ON IMPORT METHODS
 
if(__name__ == "__main__"):
    print "TODO - add unit tests"
else:
    util.LogInfo("%s initialised." % pi.PackageName())
    _SceneSetup() # Note this must be run *after* everything else in this module has been defined.
