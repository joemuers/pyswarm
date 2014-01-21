from boidBaseObject import BoidBaseObject
import attributeTypes as at
import boidTools.uiBuilder as uib
import boidTools.util as util

import weakref



########################################
class AttributesListener(object):
    
    def onAttributeChanged(self, sectionObject, attributeName):
        raise NotImplemented

#END OF CLASS - AttributesListener
########################################



########################################
class DataBlobBaseObject(object):
    """Convenience class to provide common agentId accessor for dataBlob objects.
    """
    def __init__(self, agent):
        self._agentId = agent.particleId

#####################        
    def _getAgentId(self):
        return self._agentId
    agentId = property(_getAgentId)

#END OF CLASS - AttributesListener
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
        if(self._followOnBehaviourMenu is not None):
            self._defaultBehaviourID = defaultBehaviourId
            self._followOnBehaviourIDs = filter(lambda nm: nm != self.sectionTitle(), behaviourIDsList)
            
            while(self._followOnBehaviourMenuItems):
                uib.DeleteComponent(self._followOnBehaviourMenuItems.pop())
            uib.SetParentMenuLayout(self._followOnBehaviourMenu)
            for behaviourID in self._followOnBehaviourIDs:
                self._followOnBehaviourMenuItems.append(uib.MakeMenuSubItem(behaviourID))
                
            if(self._followOnBehaviour.value not in self._followOnBehaviourIDs):
                self._followOnBehaviour.value = self._defaultBehaviourID
            else:
                self._followOnBehaviour._updateInputUiComponents()
                
# END OF CLASS - FollowOnBehaviourAtrributeInterface
########################################



########################################
class AttributesBaseObject(BoidBaseObject, at.SingleAttributeDelegate):
    
    @classmethod
    def DefaultSectionTitle(cls):
        raise NotImplemented("Method should return default title for each subclass.")
        return ""

#####################    
    def __init__(self, sectionTitle):
        super(AttributesBaseObject, self).__init__()
        
        self._sectionTitle = sectionTitle
        self._dataBlobs = []
        self._listeners = []
        self._inBulkUpdate = False

#####################
    def __str__(self):
        return ("Behaviour :%s" % self.sectionTitle())
    
    def _getMetaStr(self):
        stringsList = [("%s=%s, " % (attribute.attributeLabel, attribute.value)) 
                       for attribute in self._allAttributes()]
        return ''.join(stringsList)
 
 #####################   
    def __getstate__(self):
        selfDict = self.__dict__.copy()
        strongDataBlobRefs = [blobRef() for blobRef in self._dataBlobs]
        selfDict["_dataBlobs"] = strongDataBlobRefs
        strongListenerRefs = [ref() for ref in self._listeners]
        selfDict["_listeners"] = strongListenerRefs
        
        return selfDict
    
    def __setstate__(self, selfDict):
        strongDataBlobRefs = selfDict["_dataBlobs"]
        weakDataBlobRefs = [weakref.ref(blobRef, self._removeDeadBlobReference) for blobRef in strongDataBlobRefs]
        selfDict["_dataBlobs"] = weakDataBlobRefs
        strongListenerRefs = selfDict["_listeners"]
        weakListenerRefs = [weakref.ref(listenerRef, self._removeDeadListenerReference) for listenerRef in strongListenerRefs]
        selfDict["_listeners"] = weakListenerRefs
        
        self.__dict__.update(selfDict)
        
#####################    
    def populateUiLayout(self):
        raise NotImplemented

#####################     
    def _createDataBlobForAgent(self, agent):
        raise NotImplemented
    
#####################
    def _updateDataBlobWithAttribute(self, dataBlob, attribute):
        raise NotImplemented

#####################    
    __ALLATTRIBUTES_RECURSIVE_CHECK__ = ["metaStr"] # list of attributes (i.e. property accessors) which also call
    #                                               # "_allAttributes" - they must be skipped to avoid a recursive loop
    def _allAttributes(self):
        attributesList = []
        for attributeName in filter(lambda atNm: 
                                    atNm not in AttributesBaseObject.__ALLATTRIBUTES_RECURSIVE_CHECK__, 
                                    dir(self)):
            try:
                
                attribute = getattr(self, attributeName)
                if(isinstance(attribute, at._SingleAttributeBaseObject)):
                    attributesList.append(attribute)
                    
            except RuntimeError as e:
                if(attributeName not in AttributesBaseObject.__ALLATTRIBUTES_RECURSIVE_CHECK__):
                    AttributesBaseObject.__ALLATTRIBUTES_RECURSIVE_CHECK__.append(attributeName)
                    
                    errorString = ("Found possible recursive loop for class property \"%s\" - properties \
which use the _allAttributes method should be added to the \"__ALLATTRIBUTES_RECURSIVE_CHECK__\" list.  \
Recommend this is hard-coded rather than done at runtime."
% attributeName)
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

#####################     
    def onBehaviourListUpdated(self, behaviourIDsList, defaultBehaviourId):
        """Called whenever a behaviour is added or deleted.
        Implement in subclasses if required."""
        pass
        
#####################        
    def getDefaultsFromConfigReader(self, configReader):
        return self._readAttributesFromConfigReader(configReader, self.DefaultSectionTitle(), True)
        
    def getSavedStateFromConfigReader(self, configReader):
        return self._readAttributesFromConfigReader(configReader, self.sectionTitle(), False)
    
    def _readAttributesFromConfigReader(self, configReader, sectionTitle, isDefaults):
        self._inBulkUpdate = True
        
        util.LogDebug("Reading attribute values for section \"%s\"..." % sectionTitle)
        
        attributeLookup = {}
        for attribute in filter(lambda at: not (at.excludeFromDefaults and isDefaults), self._allAttributes()):
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
                    util.LogWarning("WARNING - could not read attribute: %s (%s), ignoring..." % (attributeLabel, e))
                else:
                    util.LogDebug("Parsed attribute value: %s = %s" % (attributeLabel, attributeValueStr))
        except Exception as e:
            util.LogWarning("ERROR - %s" % e)
                
        self._inBulkUpdate = False
        
        self._notifyListeners(None)
        
        return (attributeReadCount > 0 and attributeReadCount == len(attributeLookup))

#####################    
    def setDefaultsToConfigWriter(self, configWriter):
        self._writeAttributesWithConfigWriter(configWriter, self.DefaultSectionTitle(), True)
        
    def setSavedStateWithConfigWriter(self, configWriter):
        self._writeAttributesWithConfigWriter(configWriter, self.sectionTitle(), False)
        
    def _writeAttributesWithConfigWriter(self, configWriter, sectionTitle, isDefaults):
        util.LogDebug("Writing values for section \"%s\"..." % sectionTitle)
        
        try:
            if(configWriter.has_section(sectionTitle)):
                configWriter.remove_section(sectionTitle)
                util.LogDebug("Replacing previous values...")
            
            configWriter.add_section(sectionTitle)
        except Exception as e:
            util.LogWarning("ERROR - %s" % e)
        else:
            for attribute in filter(lambda at: not (at.excludeFromDefaults and isDefaults), self._allAttributes()):
                ####
                def _saveAttribute(configWriter, sectionTitle, attribute):
                    try:
                        configWriter.set(sectionTitle, attribute.attributeLabel, attribute.value)
                        util.LogDebug("Wrote attribute value to file: %s = %s" % (attribute.attributeLabel, attribute.value))
                    except Exception as e:
                        util.LogWarning("WARNING - Could not write attribute %s to file (%s)" % (attribute.attributeLabel, e))
                ####
                
                _saveAttribute(configWriter, sectionTitle, attribute)
                if(attribute.nestedAttribute is not None):
                    _saveAttribute(configWriter, sectionTitle, attribute.nestedAttribute)
                        
#####################    
    def sectionTitle(self):
        return self._sectionTitle

#####################     
    def getNewDataBlobForAgent(self, agent):
        newBlob = self._createDataBlobForAgent(agent)
        
        for attributeName in dir(self):
            attribute = getattr(self, attributeName)
            if(issubclass(type(attribute), at._SingleAttributeBaseObject)):
                try:
                    self._updateDataBlobWithAttribute(newBlob, attribute)
                except Exception:
                    pass
                
        self._dataBlobs.append(weakref.ref(newBlob, self._removeDeadBlobReference))
        
        return newBlob

#####################               
    def _removeDeadBlobReference(self, deadReference):
        self._dataBlobs.remove(deadReference)

#####################    
    def addListener(self, listener):
        if(not isinstance(listener, AttributesListener)):
            raise TypeError("Tried to add listener %s of type %s" % (listener, type(listener)))
        else:
            self._listeners.append(weakref.ref(listener, self._removeDeadListenerReference))

#####################    
    def removeListener(self, listener):
        toRemove = None
        for listenerRef in self._listeners:
            if listenerRef() is listener:
                toRemove = listenerRef
                break
        self._listeners.remove(toRemove)    

#####################    
    def _removeDeadListenerReference(self, deadReference):
        self._listeners.remove(deadReference)

#####################        
    def _notifyListeners(self, changedAttributeName):
        if(not self._inBulkUpdate):
            for listenerRef in self._listeners:
                listenerRef().onAttributeChanged(self, changedAttributeName)

#####################            
    def onValueChanged(self, changedAttribute): # overridden SingleAttributeDelegate method
#         if(not self._inBulkUpdate):
        for blobRef in self._dataBlobs:
            self._updateDataBlobWithAttribute(blobRef(), changedAttribute)
        
        self._notifyListeners(changedAttribute.attributeLabel)


# END OF CLASS
#############################