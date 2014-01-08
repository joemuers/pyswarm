import globalAttributes as ga
import agentPerceptionAttributes as apa
import agentMovementAttributes as ama
# import classicBoidBehaviourAttributes as cba
# import goalDrivenBehaviourAttributes as gda
# import followPathBehaviourAttributes as fpa
import boidTools.uiBuilder as uib

import os
import ConfigParser

# TODO - OS independent filepath
__DEFAULTS_FILENAME__ = "/../boidResources/boidAttributeDefaults.ini"


class AttributesController(object):
    
    def __init__(self):
        self.globalAttributes = ga.GlobalAttributes()
        self.agentMovementAttributes = ama.AgentMovementAttributes()
        self.agentPerceptionAttributes = apa.AgentPerceptionAttributes()
        
        self._behaviourAttributes = []

        self._uiWindow = None
        self._needsUiRebuild = False
        
        self.readDefaultAttributesFromFile()

#####################
    def _getUiVisible(self):
        return uib.WindowExists(self._uiWindow)
    uiVisible = property(_getUiVisible)
    
#####################
    def addNewBehaviour(self, newBehaviour):
        self.readDefaultAttributesFromFile(newBehaviour.attributes)
        self._behaviourAttributes.append(newBehaviour.attributes)
        self._needsUiRebuild = True

#####################        
    def removeBehaviour(self, behaviour):
        self._behaviourAttributes.remove(behaviour.attributes)
        self._needsUiRebuild = True

#####################
    def _allSections(self):
        sectionsList = [self.globalAttributes, self.agentMovementAttributes, self.agentPerceptionAttributes] 
        sectionsList.extend(self._behaviourAttributes)
        
        return sectionsList

#####################         
    def buildUi(self, windowTitle):
        if(not self.uiVisible or self._needsUiRebuild):
            self._uiWindow = uib.MakeWindow(windowTitle)
            
            uib.MakeMenu("File")
            uib.MakeMenuItem("Show Debug Logging", self._didSelectShowDebugLogging)
            uib.MakeMenuItem("Hide Debug Logging", self._didSelectHideDebugLogging)
            uib.MakeMenuSeparator()
            uib.MakeMenuItem("Quit", self._didSelectQuit)
            
            uib.MakeMenu("Behaviours")
            uib.MakeMenuItem("New Behaviour...", self._didSelectCreateNewBehaviour)
            uib.MakeMenuItem("Remove Behaviour...", self._didSelectRemoveBehaviour)
            
            uib.MakeBorderingLayout()
            
            generalColumnLayout = uib.MakeColumnLayout()
            self.globalAttributes.populateUiLayout()
            uib.SetAsChildLayout(generalColumnLayout)
            
            tabLayout = uib.MakeTabLayout(400)
            
            agentPropertiesScrollLayout = uib.MakeScrollLayout("Agent Attributes")
            
            movementLayout = uib.MakeFrameLayout("Agent Movement")
            self.agentMovementAttributes.populateUiLayout()
            uib.SetAsChildLayout(movementLayout)
            
            awarenessLayout = uib.MakeFrameLayout("Agent Perception")
            self.agentPerceptionAttributes.populateUiLayout()
            uib.SetAsChildLayout(awarenessLayout, agentPropertiesScrollLayout)
            
            for behaviourTab in self._behaviourAttributes:
                scrollLayout = uib.MakeScrollLayout(behaviourTab.sectionTitle())
                behaviourTab.populateUiLayout()
                uib.SetAsChildLayout(scrollLayout)
            
            uib.SetAsChildLayout(tabLayout)
            
            uib.MakeButtonStrip((("Load Defaults", self._didPressLoadDefaults, self.readDefaultAttributesFromFile.__doc__), 
                                 ("Save As Default", self._didPressSaveAsDefaults, self.writeDefaultValuesToFile.__doc__)))
            
            self._needsUiRebuild = False
            
        self._uiWindow.show()

#####################        
    def _didPressLoadDefaults(self, *args):
        if(uib.GetUserConfirmation(None, "Restore all attributes to default values?")):
            self.readDefaultAttributesFromFile()
 
#####################   
    def _didPressSaveAsDefaults(self, *args):
        if(uib.GetUserConfirmation(None, "Set default attribute values to the current values?")):
            self.writeDefaultValuesToFile()
            
##################### 
    def _didSelectShowDebugLogging(self, *args):
        print("Show BLAH.")
        
    def _didSelectHideDebugLogging(self, *args):
        print("Hide BLAH")
        
    def _didSelectQuit(self, *args):
        print("QUIT")
        
    def _didSelectCreateNewBehaviour(self, *args):
        print("ADDD")
        
    def _didSelectRemoveBehaviour(self, *args):
        print("remove")

#####################    
    def readDefaultAttributesFromFile(self, section=None, filePath=None):
        """Restore attributes to default values from file."""
        
        createNewFileIfNeeded = False
        if(filePath is None):
            createNewFileIfNeeded = True
            filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__
        
        configReader = ConfigParser.ConfigParser()
        configReader.optionxform = str  # replacing this method is necessary to make option names case-sensitive
        
        if(configReader.read(filePath)):
            print("Parsing file \'%s\' for default values..." % filePath)
            
            if(section is None):
                for sectionIterator in self._allSections():
                    sectionIterator.getDefaultsFromConfigReader(configReader)
            elif(not section.getDefaultsFromConfigReader(configReader)):
                print("Adding new section to default attributes file...")
                self.writeDefaultValuesToFile(section, filePath)
        else:
            print("Could not read default attributes file: %s" % filePath)
            if(createNewFileIfNeeded):
                print("Creating new default attributes file...")
                self.writeDefaultValuesToFile(section, filePath)

#####################    
    def writeDefaultValuesToFile(self, section=None, filePath=None):    
        """Sets current attribute values as the defualt values."""
                
        configWriter = ConfigParser.ConfigParser()
        configWriter.optionxform = str # replacing this method is necessary to make option names case-sensitive
        if(filePath is None):
            filePath = os.path.dirname(__file__) + __DEFAULTS_FILENAME__ 
        
        if(section is None):
            for sectionIterator in self._allSections():
                sectionIterator.setDefaultsToConfigWriter(configWriter)
        else:
            configWriter.read(filePath)
            section.setDefaultsToConfigWriter(configWriter)
        
        defaultsFile = open(filePath, "w")   
        configWriter.write(defaultsFile)
        defaultsFile.close()
        
        print("Wrote current attributes to defaults file:%s" % filePath)
        
    
# END OF CLASS
####################################