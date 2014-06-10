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

"""
general module - A collection of general purpose functions. 

The general module is a loose bag of 'tool' functions for performing things like
logging, string checking, and so on.

It also contains all methods for interacting with Maya that are *not* directly
related to manipulating objects within the scene (sceneInterface.py contains all 
the scene interaction methods).

In a nutshell:
Logging, general Maya info (project file location, frame number etc), script job/node
manipulation, and some general purpose Python methods.
"""


import logging
import os
import pymel.core as pm
import pymel.core.system as sm

import pyswarm.utils.packageInfo as pi



######################################
__utilLogger__ = logging.getLogger(pi.PackageName())
__utilLogger__.setLevel(logging.DEBUG)

#####
def LogDebug(message, prefix=None):
    """
    Logs messages to Maya console with a "(dbg) prefix, filtered out if not showing debug logging.
    Should be used to log non-vital operations of potential interest when troubleshooting or developing code.
    
    :param message: message string.
    :param prefix: prefix string to message, or None.
    """
    __utilLogger__.debug(("(dbg) %s %s" % (prefix, message)) if(prefix is not None) 
                         else ("(dbg) %s" % message))
    
#####
def LogInfo(message, prefix=None):
    """
    Logs messages to Maya console.
    Should be used to give the user important information, confirm completion of big operations etc.
    
    :param message: message string.
    :param prefix: prefix string to message, or None.
    """
    __utilLogger__.info(("%s %s" % (prefix, message)) if(prefix is not None) else message)
    
#####
def LogWarning(message, prefix=None):
    """
    Logs a warning message to Maya console. Shows up highlighted and with a "warning" prefix.
    Should be used to inform the user of serious but not fatal errors, improper usages etc. 
    
    :param message: message string.
    :param prefix: prefix string to message, or None.
    """
    __utilLogger__.warning(("%s %s" % (prefix, message)) if(prefix is not None) else message)
    
#####
def LogError(message, prefix=None):
    """
    Logs an error message to Maya console. Shows up flashing red and with an "error" prefix.
    Should be used to inform the user of serious or unrecoverable errors that require attention.
    
    :param message: message string.
    :param prefix: prefix string to message, or None.
    """
    __utilLogger__.error(("%s %s" % (prefix, message)) if(prefix is not None) else message)

#####
def LogException(exception):
    """
    Logs an exception instance, shows up as an error and prints the stack trace.
    
    :param exception: The exception instance that was thrown.
    """
    __utilLogger__.exception(exception)

#####  
def LogLevelIsDebug():
    """
    Returns True if showing "LogDebug" messages in the console, False otherwise.
    """
    return __utilLogger__.level <= logging.DEBUG
    
#####
def SetLoggingLevelDebug():
    """
    "LogDebug" messages will subsequently show up in the Maya console if called.
    """
    if(__utilLogger__.level != logging.DEBUG):
        __utilLogger__.setLevel(logging.DEBUG)
        LogDebug("Logging level set - DEBUG")

#####
def SetLoggingLevelInfo():
    """
    "LogDebug" messages will be subsequently filtered out if called.
    """
    if(__utilLogger__.level != logging.INFO):
        LogDebug("Logging level set - INFO")
        __utilLogger__.setLevel(logging.INFO)

######################################



######################################  
def InitVal(value, defaultValue):
    """
    Convenience method for intialising variables.
    Returns value if it isn't None, otherwise returns default value.
    
    :param value: a value, or None.
    :param defaultValue: will be returned if 'value' is None.
    """
    return value if value is not None else defaultValue

######################################
def IsStringType(instance):
    """
    Returns True if instance is a string object (either traditional or unicode), False otherwise.
    
    :param instance: candidate object. 
    """
    return isinstance(instance, str) or isinstance(instance, unicode)

######################################



######################################
def GetProjectRootDirectory():
    """
    Returns full filepath (as a string) to root directory of the current Maya project.
    """
    return pm.workspace.getPath()

#####
def GetProjectWorkingDirectory():
    """
    Returns full filepath (as a string) to directory containing the current Maya scene file.
    (i.e. usually the 'scenes' folder in the project database).
    """
    return pm.workspace.getcwd()

#####
def GetCurrentSceneName():
    """
    Returns the name only (*not* the full path) of the current Maya scene.
    (i.e. last name that scene was saved as).
    """
    sceneFile = sm.sceneName()
    sceneFile = os.path.split(sceneFile)[1]
    
    return os.path.splitext(sceneFile)[0]
######################################



######################################
def GetCurrentFrameNumber():
    """
    Returns the current frame number of the Maya scene, as an integer.
    """
    return int(pm.currentTime(query=True))

#####
def ScenePlaybackInProgress():
    """
    Returns True if the Maya scene is currently 'playing', False otherwise.
    """
    return pm.play(query=True, state=True)
    
#####
def StopPlayback():
    """
    Stops playback of the current Maya scene (if currently in progress).
    """
    pm.play(state=False)

######################################



######################################
def LaunchWebPage(url):
    """
    Launches the given URL in an external web browser (note - may not work on Linux platforms).
    
    :param url: string - the URL of some website.
    """
    pm.launch(web=url)

######################################



######################################
# Important note for the below - PySwarm makes use of both Maya's 'script jobs' (which are a relatively obscure mechanism
# for triggering events in given situations) and 'script nodes' (which are the things you see in the Expression Editor), as
# such it is important to be aware of the distinction between the two to avoid confusion.

__SaveSceneScriptJobNumber__ = -1 # local reference number for automatically generated script job that saves PySwarm to a file. 
#####
def SceneSavedScriptJobExists():
    """
    Returns True if a script job has already been added to the Maya scene which will save PySwarm to
    a file automatically when the Maya scene is saved; or False otherwise. 
    """
    global __SaveSceneScriptJobNumber__
    return __SaveSceneScriptJobNumber__ != -1

#####
def AddSceneSavedScriptJobIfNecessary(saveMethod):
    """
    Will add a script job, if one doesn't exist already, which saves PySwarm to a file automatically when the Maya scene is saved.
    The script job will be removed automatically when the scene is closed.
    
    :param saveMethod: reference to a bound method that will save PySwarm to a file (will be invoked by the script job).
    """
    global __SaveSceneScriptJobNumber__
    
    _ClearSceneSavedScriptJobReference()
    
    methodName = saveMethod.__name__
    scriptJobsList = pm.scriptJob(listJobs=True)
    for scriptJobString in scriptJobsList:
        if(methodName in scriptJobString):
            __SaveSceneScriptJobNumber__ = int(scriptJobString.split(':')[0])
            LogDebug("Found existing \"SceneSaved\" script job (#%d)" % __SaveSceneScriptJobNumber__)
            break
    
    if(not SceneSavedScriptJobExists()):
        __SaveSceneScriptJobNumber__ = pm.scriptJob(event=("SceneSaved", saveMethod), killWithScene=True)
        LogInfo("Registered \"SceneSaved\" script job (job #%d)" % __SaveSceneScriptJobNumber__)

#####        
def RemoveSceneSavedScriptJob():
    """
    Removes the 'save PySwarm to file' script job from the Maya scene, if one exists already.
    """
    global __SaveSceneScriptJobNumber__
    
    if(SceneSavedScriptJobExists()):
        if(pm.scriptJob(exists=__SaveSceneScriptJobNumber__)):
            pm.scriptJob(kill=__SaveSceneScriptJobNumber__)
            LogInfo("Removed \"SceneSaved\" script job #%d" % __SaveSceneScriptJobNumber__)
            _ClearSceneSavedScriptJobReference()
        else:
            badRef = __SaveSceneScriptJobNumber__
            _ClearSceneSavedScriptJobReference()
            raise RuntimeError("Cannot remove \"SavedScene\" script job #%d - reference number no longer valid!" % badRef)
    else:
        LogWarning("No \"SceneSaved\" script job currently registered.")

#####        
def _ClearSceneSavedScriptJobReference():
    """
    Clears local reference to the 'save PySwarm to file' script job.
    Should be called when the actual script job is deleted.
    """
    global __SaveSceneScriptJobNumber__
    __SaveSceneScriptJobNumber__ = -1

#####
def OnSceneTeardown():
    """
    Should be called when the Maya scene closes.  
    Will remove reference to the PySwarm 'save to file' script job (which should have been automatically deleted).
    """
    _ClearSceneSavedScriptJobReference()
    
######################################            
def _ScriptNodeExists(scriptNodeName, isBefore):
    """
    Returns True if the given script node already exists within the Maya scene, False otherwise. 
    
    :param scriptNodeName: Name of the script node (string)
    :param isBefore: True if it's a 'before' event script node, False if it's an 'after' event script node. 
    """
    kwargs = { "query" : True }
    if(isBefore):
        kwargs["beforeScript"] = True
    else:
        kwargs["afterScript"] = True
    
    try:
        scriptString = pm.scriptNode(scriptNodeName, **kwargs)
        if(scriptString):
            return True
        else:
            return False
    except:
        return False

#####
def AddScriptNodesIfNecessary(moduleReference, sceneSetupMethod, frameUpdateMethod, sceneCloseMethod):
    """
    Adds auto-generated script nodes to the Maya scene if they don't already exist.
    
    Adds nodes to:
    - run a method when when Maya scene opens (e.g. to restore PySwarm state from a previous save file).
    - run a method when the frame changes the Maya scene (e.g. during playback, to read & then update the scene).
    - run a method when the Maya scene is closed (e.g. to save PySwarm state to a file).
    
    :param moduleReference: module object containing the given methods (i.e. needs to be imported to run them).
    :param sceneSetupMethod: should be a bound method (within 'moduleReference') to be run when Maya scene opens.
    :param frameUpdateMethod: bound method to run when Maya frame updates within the scene.
    :param sceneCloseMethod: bound method to run when the Maya scene closes.
    """
    swarmControllerModuleName = moduleReference.__name__
    modulePath = os.path.dirname(os.path.dirname(moduleReference.__file__))
    moduleHandle = ("__%s_IMPORT_FOR_SCRIPTNODE_UPDATES__" % pi.PackageName().upper())
    headerPadding = '#' * len(pi.PackageName())
    scriptHeaderString = ("####################%s########################\n"
                          "# Auto-generated by %s, please do not edit!! #\n"
                          "####################%s########################\n\n" 
                          % (headerPadding, pi.PackageName(), headerPadding))
    
    if(not _ScriptNodeExists("pySwarmOnSceneOpen", True)):
        pathString = ("import sys\nif(\"%s\" not in sys.path): sys.path.append(\"%s\")" % (modulePath, modulePath))
        importString = ("if(\"%s\" not in globals()): globals()[\"%s\"] = "
                        "__import__(\"%s\", globals(), locals(), [\"%s\"], -1)" % 
                        (moduleHandle, moduleHandle, swarmControllerModuleName, swarmControllerModuleName))
        sceneOpenNode = pm.scriptNode(name="pySwarmOnSceneOpen", 
                                      beforeScript=("%s%s\n%s\n%s.%s()" % 
                                                    (scriptHeaderString, 
                                                     pathString,
                                                     importString,
                                                     moduleHandle, sceneSetupMethod.__name__)),  
                                      scriptType=2, sourceType='python')
        pm.evalDeferred(importString)
        
        LogDebug("Added scene-open script node \"%s\" to Maya scene." % sceneOpenNode)

    if(not _ScriptNodeExists("pySwarmOnFrameUpdate", True)):        
        frameUpdateNode = pm.scriptNode(name="pySwarmOnFrameUpdate", 
                                        beforeScript=("%s%s.%s()" % 
                                                      (scriptHeaderString,
                                                       moduleHandle, frameUpdateMethod.__name__)),  
                                        scriptType=7, sourceType='python')
        
        LogDebug("Added frame-update script node \"%s\" to Maya scene." % frameUpdateNode)
    
    if(not _ScriptNodeExists("pySwarmOnSceneClose", False)): 
        sceneCloseNode = pm.scriptNode(name="pySwarmOnSceneClose", 
                                      afterScript=("%s%s.%s()" % 
                                                   (scriptHeaderString, 
                                                    moduleHandle, sceneCloseMethod.__name__)),  
                                      scriptType=2, sourceType='python')
       
        LogDebug("Added scene-close script node \"%s\" to Maya scene." % sceneCloseNode)

######################################



######################################
__DeferredEvaluationsQueue__ = []
__ModuleHandle__ = ("__%s_IMPORT_FOR_DEFERRED_EVALUATION__" % pi.PackageName().upper())
__DeferredEvaluationMethodString__ = ("%s._MakeDeferredEvaluations()" % __ModuleHandle__)
#####
def EvalDeferred(boundMethod, *args, **kwargs):
    """
    Runs the given method but deferred to the end of the current run loop iteration, as opposed to being executed
    immediately.  Should be used instead of PyMel's 'evalDeferred' method.
    
    A typical use would be a UI component that wants to delete itself - where doing so immediately would put the 
    currently executing code in invalid memory. 
    
    This nasty little piece of hackery is necessary because the Pymel version of evalDeferred is not
    usable from a object-oriented environment - all you get is a string literal to be executed
    from within the main module. As such, this is the only way to provided the same functionality 
    for bound methods from within modules and classes (Method adds this module to main, then 
    evaluates bound methods via _MakeDeferredEvaluations).
    
    :param boundMethod: bound method to be run deferred; will be passed any provided 'args' and 'kwargs' arguments.
    """
    global __DeferredEvaluationsQueue__
    global __ModuleHandle__
    global __DeferredEvaluationMethodString__
    
    if(not callable(boundMethod)):
        raise TypeError("Non-callable object \"%s\" passed to EvalDeferred." % boundMethod)
    else:
        if(not __DeferredEvaluationsQueue__):
            importString = ("if(\"%s\" not in globals()): globals()[\"%s\"] = "
                            "__import__(\"%s\", globals(), locals(), [\"%s\"], -1)" % 
                            (__ModuleHandle__, __ModuleHandle__, __name__, __name__))
            pm.evalDeferred(importString)
            pm.evalDeferred(__DeferredEvaluationMethodString__)
        
        __DeferredEvaluationsQueue__.append((boundMethod, args, kwargs))
    
######
def _MakeDeferredEvaluations():    
    """
    EvalDeferred, above, queues up bound methods on __DeferredEvaluationsQueue__.  This method drains the
    queue when called.
    """
    global __DeferredEvaluationsQueue__
    
    for commandTuple in __DeferredEvaluationsQueue__:
        method, arguments, keywords = commandTuple
        method(*arguments, **keywords)
    
    del __DeferredEvaluationsQueue__[:]
    
######################################
def SafeEvaluate(verboseErrorLog, method, *args, **kwargs):
    """
    Evaluates the given bound method normally, but will catch and contain any exceptions that are thrown. 
    
    :param verboseErrorLog: True if any exceptions should have their error printed to the console in full, False for abbreviated logs.
    :param method: bound method to be executed.
    """
    try:
        return method(*args, **kwargs)
    except Exception as e:
        if(verboseErrorLog):
            LogException(e)
        else:
            LogWarning("%s error: %s" % (method.__name__, e))
        

# END OF MODULE
##########################################################