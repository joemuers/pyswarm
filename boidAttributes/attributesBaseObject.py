import attributeTypes as at

import weakref


class AttributesListener(object):
    
    def onAttributeChanged(self, sectionObject, attributeName):
        raise NotImplemented

#END OF CLASS - AttributesListener
########################################


class AttributesBaseObject(at.SingleAttributeDelegate):
    
    def __init__(self):
        self._listeners = []
        self._notificationsEnabled = True

#####################    
    def makeFrameLayout(self):
        raise NotImplemented
        
#####################        
    def getDefaultsFromConfigReader(self, configReader):
        self._notificationsEnabled = False
        
        print("Reading default values for section \"%s\"..." % self._sectionTitle())
        
        try:
            for attributeNameStr, attributeValueStr in configReader.items(self._sectionTitle()):
                try:
                    setattr(self, attributeNameStr, attributeValueStr)
                except Exception as e:
                    print("WARNING - could not read attribute: %s (%s), ignoring..." % (attributeNameStr, e))
                else:
                    print("Re-set attribute value: %s = %s" % (attributeNameStr, attributeValueStr))
        except Exception as e:
            print("ERROR - %s" % e)
                
        self._notificationsEnabled = True
        self._notifyListeners(None)

#####################    
    def setDefaultsToConfigWriter(self, configWriter):
        print("Saving default values for section \"%s\"..." % self._sectionTitle())
        
        try:
            configWriter.add_section(self._sectionTitle())
        except Exception as e:
            print("ERROR - %s" % e)
        else:
            for attributeNameStr in dir(self):
                attributeCandidate = getattr(self, attributeNameStr)
                
                if(issubclass(type(attributeCandidate), at._SingleAttributeBaseObject)):
                    try:
                        attributeValue = attributeCandidate._value  # - don't use the property accessor, as randomizer may affect the value
                        attributeAccessorName = attributeCandidate.attributeName # - but we want the accessor saved to the .ini file
                        configWriter.set(self._sectionTitle(), attributeAccessorName, attributeValue)
                        print("Changed default attribute value: %s = %s" % (attributeAccessorName, attributeValue))
                        
                        if(attributeCandidate.hasRandomizer):
                            configWriter.set(self._sectionTitle(), attributeCandidate.randomizerName, attributeCandidate.randomizerValue)
                            print("Changed default attribute value: %s = %s" % 
                                  (attributeCandidate.randomizerName, attributeCandidate.randomizerValue))
                    except Exception as e:
                        print("WARNING - Could not write attribute to defaults file: %s (%s)" % (attributeNameStr, e))

#####################    
    def _sectionTitle(self):
        raise NotImplemented

#####################    
    def addListener(self, listener):
        if(type(listener) != AttributesListener):
            raise TypeError
        else:
            self._listeners.append(weakref.ref(listener, self._removeDeadReference))

#####################    
    def removeListener(self, listener):
        toRemove = None
        for listenerRef in self._listeners:
            if listenerRef() is listener:
                toRemove = listenerRef
                break
        self._listeners.remove(toRemove)    

#####################    
    def _removeDeadReference(self, deadReference):
        self._listeners.remove(deadReference)

#####################        
    def _notifyListeners(self, changedAttributeName):
        if(self._notificationsEnabled):
            for listenerRef in self._listeners:
                listenerRef().onAttributeChanged(self, changedAttributeName)

#####################            
    def _onAttributeChanged(self, changedAttribute): # overridden SingleAttributeDelegate method
        self._notifyListeners(changedAttribute.attributeName)


# END OF CLASS
#############################