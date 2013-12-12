import generalAttributes as ga
import agentAwarenessAttributes as aaa
import agentMovementAttributes as ama
import classicBoidBehaviourAttributes as cba
import goalDrivenBehaviourAttributes as gda
import followPathBehaviourAttributes as fpa
import attributeTypes as at

import os
import ConfigParser
import pymel.core as pm


__DEFAULTS_FILENAME__ = "/boidAttributeDefaults.ini"


class AttributesController(object):
    
    def __init__(self):
        self._generalAttributes = ga.GeneralAttributes()
        self._agentAwarenessAttributes = aaa.AgentAwarenessAttributes()
        self._agentMovementAttributes = ama.AgentMovementAttributes()
        self._classicBoidAttributes = cba.ClassicBoidBehaviourAttributes()
        self._goalDrivenAttributes = gda.GoalDrivenBehaviourAttributes()
        self._followPathAttributes = fpa.FollowPathBehaviourAttributes()
        
        self._sections = [self._generalAttributes, self._agentAwarenessAttributes, self._agentMovementAttributes,
                          self._classicBoidAttributes, self._goalDrivenAttributes, self._followPathAttributes]
        self._uiWindow = None

#####################         
    def buildUi(self):
        if(self._uiWindow is None or not pm.window(self._uiWindow, exists=True)):
            self._uiWindow = pm.window(title="Agents sim")
            tabLayout = pm.tabLayout()
            
            generalScrollLayout = pm.scrollLayout(self._generalAttributes._sectionTitle())
            generalLayout = self._generalAttributes.makeFrameLayout()
            at.SetAsChildToPrevious(generalLayout)
            movementLayout = self._agentMovementAttributes.makeFrameLayout()
            at.SetAsChildToPrevious(movementLayout)
            awarenessLayout = self._agentAwarenessAttributes.makeFrameLayout()
            at.SetAsChildToPrevious(awarenessLayout, generalScrollLayout)
            
            cbScrollLayout = pm.scrollLayout(self._classicBoidAttributes._sectionTitle())
            classicBoidLayout = self._classicBoidAttributes.makeFrameLayout()
            at.SetAsChildToPrevious(cbScrollLayout, classicBoidLayout)
            
            goalScrollLayout = pm.scrollLayout(self._goalDrivenAttributes._sectionTitle())
            goalFrameLayout = self._goalDrivenAttributes.makeFrameLayout()
            at.SetAsChildToPrevious(goalFrameLayout, goalScrollLayout)
            
            pathScrollLayout = pm.scrollLayout(self._followPathAttributes._sectionTitle())
            pathFrameLayout = self._followPathAttributes.makeFrameLayout()
            at.SetAsChildToPrevious(pathFrameLayout, pathScrollLayout)
            
            at.SetAsChildToPrevious(tabLayout)

        self._uiWindow.show()

#####################    
    def readDefaultAttributesFromFile(self, filePath=None):
        createNewFileIfNeeded = False
        if(filePath is None):
            createNewFileIfNeeded = True
            filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__
        
        configReader = ConfigParser.ConfigParser()
        configReader.optionxform = str  # replacing this method is necessary to make option names case-sensitive
        
        if(configReader.read(filePath)):
            print("Parsing file \'%s\' for default values..." % filePath)
            for section in self._sections:
                section.getDefaultsFromConfigReader(configReader)
        else:
            print("Could not read default attributes file: %s" % filePath)
            if(createNewFileIfNeeded):
                print("Creating new default attributes file...")
                self.WriteDefaultValuesToFile(filePath)

#####################    
    def writeDefaultValuesToFile(self, filePath=None):            
        configWriter = ConfigParser.ConfigParser()
        configWriter.optionxform = str # replacing this method is necessary to make option names case-sensitive
        
        for section in self._sections:
            section.setDefaultsToConfigWriter(configWriter)
        
        if(filePath is None):
            filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__ 
        defaultsFile = open(filePath, "w")   
        configWriter.write(defaultsFile)
        defaultsFile.close()
        
        print("Wrote current attributes to defaults file:%s" % filePath)
        
    
# END OF CLASS
####################################