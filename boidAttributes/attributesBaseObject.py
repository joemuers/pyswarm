import attributeTypes as at

import weakref



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
class AttributesBaseObject(at.SingleAttributeDelegate):
    
    @classmethod
    def DefaultSectionTitle(cls):
        raise NotImplemented("Method should return default title for each subclass.")
        return ""

#####################    
    def __init__(self, sectionTitle):
        self._sectionTitle = sectionTitle
        self._dataBlobs = []
        self._listeners = []
        self._inBulkUpdate = False

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
        self._inBulkUpdate = True
        
        print("Reading default values for section \"%s\"..." % self.DefaultSectionTitle())
        
        attributeLookup = {}
        for attributeName in dir(self):
            attribute = getattr(self, attributeName)
            if(issubclass(type(attribute), at._SingleAttributeBaseObject) and not attribute.excludeFromDefaults):
                attributeLookup[attribute.attributeLabel] = attribute
        
        attributeReadCount = 0
        try:
            for attributeLabel, attributeValueStr in configReader.items(self.DefaultSectionTitle()):
                try:
                    attributeLookup[attributeLabel].value = attributeValueStr
                    attributeReadCount += 1
                except Exception as e:
                    print("WARNING - could not read attribute: %s (%s), ignoring..." % (attributeLabel, e))
                else:
                    print("Re-set attribute value: %s = %s" % (attributeLabel, attributeValueStr))
        except Exception as e:
            print("ERROR - %s" % e)
                
        self._inBulkUpdate = False
        
        self._notifyListeners(None)
        
        return (attributeReadCount > 0 and attributeReadCount == len(attributeLookup))

#####################    
    def setDefaultsToConfigWriter(self, configWriter):
        print("Saving default values for section \"%s\"..." % self.sectionTitle())
        
        try:
            if(configWriter.has_section(self.DefaultSectionTitle())):
                configWriter.remove_section(self.DefaultSectionTitle())
                print("Replacing previous values...")
            
            configWriter.add_section(self.DefaultSectionTitle())
        except Exception as e:
            print("ERROR - %s" % e)
        else:
            for attributeName in dir(self):
                attribute = getattr(self, attributeName)
                
                if(issubclass(type(attribute), at._SingleAttributeBaseObject) and not attribute.excludeFromDefaults):
                    try:
                        configWriter.set(self.sectionTitle(), attribute.attributeLabel, attribute.value)
                        print("Changed default attribute value: %s = %s" % (attribute.attributeLabel, attribute.value))
                    except Exception as e:
                        print("WARNING - Could not write attribute to defaults file: %s (%s)" % (attributeName, e))

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