import boidResources.packageInfo as pi

import logging
import os
import pymel.core as pm



######################################
__utilLogger__ = logging.getLogger(pi.PackageName())
__utilLogger__.setLevel(logging.DEBUG)

#####
def LogDebug(message, prefix=None):
    __utilLogger__.debug(("(dbg) %s %s" % (prefix, message)) if(prefix is not None) 
                         else ("(dbg) %s" % message))
    
#####
def LogInfo(message, prefix=None):
    __utilLogger__.info(("%s %s" % (prefix, message)) if(prefix is not None) else message)
    
#####
def LogWarning(message, prefix=None):
    __utilLogger__.warning(("%s %s" % (prefix, message)) if(prefix is not None) else message)
    
#####
def LogError(message, prefix=None):
    __utilLogger__.error(("%s %s" % (prefix, message)) if(prefix is not None) else message)

#####
def LogException(exception):
    __utilLogger__.exception(exception)

#####  
def LogLevelIsDebug():
    return __utilLogger__.level <= logging.DEBUG
    
#####
def SetLoggingLevelDebug():
    if(__utilLogger__.level != logging.DEBUG):
        __utilLogger__.setLevel(logging.DEBUG)
        LogDebug("Logging level set - DEBUG")

#####
def SetLoggingLevelInfo():
    if(__utilLogger__.level != logging.INFO):
        LogDebug("Logging level set - INFO")
        __utilLogger__.setLevel(logging.INFO)

######################################



######################################  
def InitVal(value, defaultValue):
    return value if value is not None else defaultValue

######################################
def IsStringType(instance):
    return isinstance(instance, str) or isinstance(instance, unicode)

######################################



######################################
def GetProjectRootDirectory():
    return pm.workspace.getPath()

#####
def GetProjectWorkingDirectory():
    return pm.workspace.getcwd()

#####
def GetCurrentSceneName():
    sceneFile = pm.system.sceneName()
    sceneFile = os.path.split(sceneFile)[1]
    
    return os.path.splitext(sceneFile)[0]
######################################



######################################
def GetCurrentFrameNumber():
    return int(pm.currentTime(query=True))

#####
def ScenePlaybackInProgress():
    return pm.play(query=True, state=True)
    
#####
def StopPlayback():
    pm.play(state=False)

######################################



######################################
def LaunchWebPage(url):
    pm.launch(web=url)

######################################



######################################
__SaveSceneScriptJobNumber__ = -1
#####
def SceneSavedScriptJobExists():
    global __SaveSceneScriptJobNumber__
    return __SaveSceneScriptJobNumber__ != -1

#####
def AddSceneSavedScriptJobIfNecessary(saveMethod):
    global __SaveSceneScriptJobNumber__
    
    ClearSceneSavedScriptJobReference()
    
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
    global __SaveSceneScriptJobNumber__
    
    if(SceneSavedScriptJobExists()):
        if(pm.scriptJob(exists=__SaveSceneScriptJobNumber__)):
            pm.scriptJob(kill=__SaveSceneScriptJobNumber__)
            LogInfo("Removed \"SceneSaved\" script job #%d" % __SaveSceneScriptJobNumber__)
            ClearSceneSavedScriptJobReference()
        else:
            badRef =__SaveSceneScriptJobNumber__
            ClearSceneSavedScriptJobReference()
            raise RuntimeError("Cannot remove \"SavedScene\" script job #%d - reference number no longer valid!" % badRef)
    else:
        LogWarning("No \"SceneSaved\" script job currently registered.")

#####        
def ClearSceneSavedScriptJobReference():
    global __SaveSceneScriptJobNumber__
    __SaveSceneScriptJobNumber__ = -1

######################################            
def _ScriptNodeExists(scriptNodeName, isBefore):
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
    swarmControllerModuleName = moduleReference.__name__
    modulePath = os.path.dirname(moduleReference.__file__)
    moduleHandle = ("__%s_IMPORT_FOR_SCRIPTNODE_UPDATES__" % pi.PackageName().upper())
    headerPadding = '#' * len(pi.PackageName())
    scriptHeaderString = ("\
####################%s#######################\n\
# Auto-generated by %s, please do not edit!!#\n\
####################%s#######################\n\n" % (headerPadding, pi.PackageName(), headerPadding))
    
    if(not _ScriptNodeExists("pySwarmOnSceneOpen", True)):
        pathString = ("import sys\nif(\"%s\" not in sys.path): sys.path.append(\"%s\")" % (modulePath, modulePath))
        importString = ("if(\"%s\" not in globals()): globals()[\"%s\"] = \
__import__(\"%s\", globals(), locals(), [\"%s\"], -1)" % 
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
    """This nasty little piece of hackery is necessary because the Pymel version of evalDeferred is not
    usable from a object-oriented environment - all you get is a string literal to be executed
    from within the main module. 
    As such, this is the only way to provided the same functionality for bound methods from within
    modules and classes (Method adds this module to main, then evaluates bound methods via _MakeDeferredEvaluations).
    """
    global __DeferredEvaluationsQueue__
    global __ModuleHandle__
    global __DeferredEvaluationMethodString__
    
    if(not callable(boundMethod)):
        raise TypeError("Non-callable object \"%s\" passed to EvalDeferred." % boundMethod)
    else:
        if(not __DeferredEvaluationsQueue__):
            importString = ("if(\"%s\" not in globals()): globals()[\"%s\"] = \
__import__(\"%s\", globals(), locals(), [\"%s\"], -1)" % 
                            (__ModuleHandle__, __ModuleHandle__, __name__, __name__))
            pm.evalDeferred(importString)
            pm.evalDeferred(__DeferredEvaluationMethodString__)
        
        __DeferredEvaluationsQueue__.append((boundMethod, args, kwargs))
    
######
def _MakeDeferredEvaluations():    
    global __DeferredEvaluationsQueue__
    
    for commandTuple in __DeferredEvaluationsQueue__:
        method, arguments, keywords = commandTuple
        method(*arguments, **keywords)
    
    del __DeferredEvaluationsQueue__[:]
    
######################################
def SafeEvaluate(verboseErrorLog, method, *args, **kwargs):
    try:
        return method(*args, **kwargs)
    except Exception as e:
        if(verboseErrorLog):
            LogException(e)
        else:
            LogWarning("%s error: %s" % (method.__name__, e))
        

# END OF MODULE
##########################################################