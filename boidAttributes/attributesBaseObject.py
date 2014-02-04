from boidBaseObject import BoidBaseObject
import attributeTypes as at
import boidTools.util as util
import boidTools.uiBuilder as uib

from abc import ABCMeta, abstractmethod
import weakref
from ConfigParser import NoSectionError



########################################
class AttributesListener(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def onAttributeChanged(self, sectionObject, attributeName):
        raise NotImplemented

#END OF CLASS - AttributesListener
########################################


 
########################################
class _DataBlobBaseObject(object):
    """Convenience class to provide common agentId accessor for dataBlob objects.
    """
    def __init__(self, agent):
        self._agentId = agent.agentId
        self.onUnassignedCallback = None
        
#####################        
    def _getAgentId(self):
        return self._agentId
    agentId = property(_getAgentId)
    
####################
    def onUnassigned(self):
        if(self.onUnassignedCallback is not None):
            self.onUnassignedCallback(self._agentId)
     
#####################   
    def __eq__(self, other):
        return (self._agentId == other._agentId) if(other is not None) else False
     
    def __ne__(self, other):
        return (self._agentId != other._agentId) if(other is not None) else True
     
    def __lt__(self, other):
        return self._agentId < other._agentId
     
    def __gt__(self, other):
        return self._agentId > other._agentId
     
    def __hash__(self):
        return hash(self._agentId)
     
#END OF CLASS - _DataBlobBaseObject
########################################
 
 
 
########################################
class _FollowOnBehaviourAttributeInterface(object):
     
    def __init__(self, *args, **kwargs):
        super(_FollowOnBehaviourAttributeInterface, self).__init__(*args, **kwargs)
         
        self._defaultBehaviourID = "<None>"
        self._followOnBehaviourIDs = [self._defaultBehaviourID]
        self._followOnBehaviourMenu = None
        self._followOnBehaviourMenuItems = None
         
        self._followOnBehaviour = at.StringAttribute("Follow-On Behaviour", self._defaultBehaviourID)
        self._followOnBehaviour.excludeFromDefaults = True
 
#####################        
    def _makeFollowOnBehaviourOptionGroup(self):
        cmdTuple = uib.MakeStringOptionsField(self._followOnBehaviour, self._followOnBehaviourIDs)
        self._followOnBehaviourMenu, self._followOnBehaviourMenuItems = cmdTuple
 
#####################
    def _updateFollowOnBehaviourOptions(self, behaviourIDsList, defaultBehaviourId):
        self._defaultBehaviourID = defaultBehaviourId
        self._followOnBehaviourIDs = filter(lambda nm: nm != self.behaviourId, behaviourIDsList)
         
        if(self._followOnBehaviourMenu is not None):
            while(self._followOnBehaviourMenuItems):
                uib.DeleteComponent(self._followOnBehaviourMenuItems.pop())
            uib.SetParentMenuLayout(self._followOnBehaviourMenu)
            
            if(self._followOnBehaviourIDs):
                for behaviourID in self._followOnBehaviourIDs:
                    self._followOnBehaviourMenuItems.append(uib.MakeMenuSubItem(behaviourID))
                
                if(self._followOnBehaviour.value not in self._followOnBehaviourIDs):
                    if(len(self._followOnBehaviourIDs) == 1 or self.behaviourId == defaultBehaviourId):
                        self._followOnBehaviour.value = self._followOnBehaviourIDs[0]
                    else:
                        self._followOnBehaviour.value = self._defaultBehaviourID
                else:
                    self._followOnBehaviour._updateInputUiComponents()
            else:
                self._followOnBehaviour._value = None
                self._followOnBehaviourMenuItems.append(uib.MakeMenuSubItem("<None>"))
                util.LogWarning("All follow-on behaviour candidates for \"%s\" deleted." % self.behaviourId)

        elif(self._followOnBehaviour.value not in self._followOnBehaviourIDs):
            if(defaultBehaviourId != self.behaviourId):
                self._followOnBehaviour.value = self._defaultBehaviourID
            else:
                self._followOnBehaviour.value = None
             
                 
# END OF CLASS - FollowOnBehaviourAtrributeInterface
########################################
 
 
 
########################################
class AttributesBaseObject(BoidBaseObject, at.SingleAttributeDelegate):
     
    __metaclass__ = ABCMeta
     
#####################
    @classmethod
    def BehaviourTypeName(cls):
        raise NotImplemented("Method should return default title for each subclass.")
        return ""
 
#####################    
    def __init__(self, behaviourId):
        super(AttributesBaseObject, self).__init__()
         
        self._behaviourId = behaviourId
        self._dataBlobs = {}
        self._dataBlobRepository = {}
        self._listeners = set()
        self._inBulkUpdate = False
 
#####################
    def __str__(self):
        return ("Attribute set:%s" % self.behaviourId)
      
########
    def _getMetaStr(self):
        agentsString = ', '.join([("%d" % blob.agentId) for blob in sorted(self._dataBlobs.itervalues())])
        attributesString = ', '.join([("%s=%s" % (attribute.attributeLabel, attribute.value)) 
                                      for attribute in self._allAttributes()])
           
        return ("<Following: %s\n\tAttributes: %s>" % agentsString, attributesString)
   
#####################   
    def __getstate__(self):
        state = super(AttributesBaseObject, self).__getstate__()
        
        strongListenerRefs = [ref() for ref in self._listeners]
        state["_listeners"] = strongListenerRefs
           
        return state
       
########
    def __setstate__(self, state):
        super(AttributesBaseObject, self).__setstate__(state)
        
        self._listeners = set([weakref.ref(listener, self._removeDeadListenerReference) 
                               for listener in self._listeners])
                           
#####################    
    def _getBehaviourId(self):
        return self._behaviourId
    behaviourId = property(_getBehaviourId)
      
#####################    
    @abstractmethod
    def populateUiLayout(self):
        raise NotImplemented
   
#####################    
    @abstractmethod 
    def _createDataBlobForAgent(self, agent):
        raise NotImplemented
       
#########
    @abstractmethod
    def _updateDataBlobWithAttribute(self, dataBlob, attribute):
        raise NotImplemented
   
#####################    
    _ALLATTRIBUTES_RECURSIVE_CHECK_ = ["metaStr"] # list of attributes (i.e. property accessors) which also call
    #                                             # "_allAttributes" - they must be skipped to avoid a recursive loop
    def _allAttributes(self):
        attributesList = []
        for attributeName in filter(lambda atNm: 
                                    atNm not in AttributesBaseObject._ALLATTRIBUTES_RECURSIVE_CHECK_, 
                                    dir(self)):
            try:
                   
                attribute = getattr(self, attributeName)
                if(isinstance(attribute, at._SingleAttributeBaseObject)):
                    attributesList.append(attribute)
                       
            except RuntimeError as e:
                if(attributeName not in AttributesBaseObject._ALLATTRIBUTES_RECURSIVE_CHECK_):
                    AttributesBaseObject._ALLATTRIBUTES_RECURSIVE_CHECK_.append(attributeName)
                       
                    errorString = ("Found possible recursive loop for class property \"%s\" - properties \
which use the _allAttributes method should be added to the \"_ALLATTRIBUTES_RECURSIVE_CHECK_\" list.  \
Recommend this is hard-coded rather than done at runtime." % attributeName)
                    raise RuntimeError(errorString)
                else:
                    raise e
           
        return attributesList
   
#####################    
    def onFrameUpdated(self):
        """Called each time the Maya scene moves to a new frame.
        Implement in subclasses if any updates are needed.
        """
        pass
    
########
    def onCalculationsCompleted(self):
        """Called each time the swarm instance finishes calculating updates
        for the current frame.
        Override in subclasses if needed."""
        pass
   
#####################     
    def onBehaviourListUpdated(self, behaviourIDsList, defaultBehaviourId):
        """Called whenever a behaviour is added or deleted.
        Implement in subclasses if required."""
        pass
           
#####################     
    def getDataBlobForAgent(self, agent):
        agentId = agent.agentId
        if(agentId in self._dataBlobs):
            raise RuntimeError("Re-requesting dataBlob which is already assigned")
        
        newBlob = self._dataBlobRepository.pop(agentId, None)
        if(newBlob is None):
            newBlob = self._createDataBlobForAgent(agent)
            newBlob.onUnassignedCallback = self._dataBlobUnassignedCallback
            for attribute in self._allAttributes():
                self._updateDataBlobWithAttribute(newBlob, attribute)

        self._dataBlobs[agentId] = newBlob

        return newBlob
    
########
    def _dataBlobUnassignedCallback(self, agentId):
        self._dataBlobRepository[agentId] = self._dataBlobs.pop(agentId)
        
########
    def purgeDataBlobRepository(self):
        del self._dataBlobRepository[:]
        
#####################        
    def getDefaultsFromConfigReader(self, configReader):
        self._inBulkUpdate = True
        sectionTitle = self.BehaviourTypeName()
        util.LogDebug("Reading default attribute values for section \"%s\"..." % sectionTitle)
           
        attributeLookup = {}
        for attribute in filter(lambda at: not at.excludeFromDefaults, self._allAttributes()):
            attributeLookup[attribute.attributeLabel] = attribute
            if(attribute.nestedAttribute is not None):
                attributeLookup[attribute.nestedAttribute.attributeLabel] = attribute.nestedAttribute
           
        attributeReadCount = 0
        try:
            for attributeLabel, attributeValueStr in configReader.items(sectionTitle):
                try:
                    attributeLookup[attributeLabel].value = attributeValueStr
                    attributeReadCount += 1
                except Exception as e:
                    util.LogWarning("Could not read attribute: \"%s\" (Error=%s), ignoring..." % (attributeLabel, e))
                else:
                    util.LogDebug("Parsed default attribute value: %s = %s" % (attributeLabel, attributeValueStr))
        except NoSectionError as e:
            util.LogWarning("Section \"%s\" not found." % sectionTitle)
        finally:
            self._inBulkUpdate = False
                   
        self._inBulkUpdate = False
        self._notifyListeners(None)
           
        return (attributeReadCount == len(attributeLookup))
   
########
    def setDefaultsToConfigWriter(self, configWriter):
        sectionTitle = self.BehaviourTypeName()
        util.LogDebug("Adding default values for section \"%s\"..." % sectionTitle)
           
        try:
            if(configWriter.has_section(sectionTitle)):
                configWriter.remove_section(sectionTitle)
                util.LogDebug("Overwriting previous values...")
               
            configWriter.add_section(sectionTitle)
        except Exception as e:
            util.LogWarning("ERROR - %s" % e)
        else:
            for attribute in filter(lambda at: not at.excludeFromDefaults, self._allAttributes()):
                ####
                def _saveAttribute(configWriter, sectionTitle, attribute):
                    try:
                        configWriter.set(sectionTitle, attribute.attributeLabel, attribute.value)
                        util.LogDebug("Added default attribute value: %s = %s" % (attribute.attributeLabel, attribute.value))
                    except Exception as e:
                        util.LogWarning("Could not write attribute %s to file (%s)" % (attribute.attributeLabel, e))
                ####
                   
                _saveAttribute(configWriter, sectionTitle, attribute)
                if(attribute.nestedAttribute is not None):
                    _saveAttribute(configWriter, sectionTitle, attribute.nestedAttribute)
    
#####################    
    def addListener(self, listener):
        if(not isinstance(listener, AttributesListener)):
            raise TypeError("Tried to add listener %s of type %s" % (listener, type(listener)))
        else:
            self._listeners.add(weakref.ref(listener, self._removeDeadListenerReference))
    
########
    def removeListener(self, listener):
        if(listener in self._listeners):
            self._listeners.remove(listener)  
    
########
    def _removeDeadListenerReference(self, deadReference):
        self._listeners.remove(deadReference)
    
#########
    def _notifyListeners(self, changedAttributeName):
        if(not self._inBulkUpdate):
            for listenerRef in self._listeners:
                listenerRef().onAttributeChanged(self, changedAttributeName)
    
#####################            
    def onValueChanged(self, changedAttribute): # overridden SingleAttributeDelegate method
        for dataBlob in self._dataBlobs.itervalues():
            self._updateDataBlobWithAttribute(dataBlob, changedAttribute)
            
        for dataBlob in self._dataBlobRepository.itervalues():
            self._updateDataBlobWithAttribute(dataBlob, changedAttribute)
            
        self._notifyListeners(changedAttribute.attributeLabel)
    
    
# END OF CLASS
#############################