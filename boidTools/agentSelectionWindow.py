from boidBaseObject import BoidBaseObject

import uiBuilder as uib
import util as util



########################
_TextFieldAnnotation_ = "Comma-separated list of particle IDs, range format = \"x-y\", wildcard = \"*\"\n\
eg. \"*-3, 6, 9, 10-13\" gives the selection: 0,1,2,3,6,9,10,11,12,13.\n\
NB. Agent IDs relate directly to Maya's particle IDs."

_RadioButtonsAnnotation_ = "Listed IDs = Takes selection from listed IDs in the text box, above.\n\
In-Scene = Takes selection from individually selected particles within the scene.\n\
All = Selects all the agents in the scene.\n\
None = Clears the selection."

########################



#########################################
class AgentSelectionWindow(BoidBaseObject):
    
    __invalid__, __textInputSelection__, __sceneSelection__, __selectAll__, __selectNone__ = range(5)
    __SelectionOptionStrings__ = ["<N/A>", "Listed IDs", "In-Scene", "All", "None"]
    
#####################    
    def __init__(self, agentsController):
        self._agentsController = agentsController
        self._currentlySelectedList = []
        self._maxIdValue = 0
        
        self._window = None
        self._textInput = None
        self._radioButtons = None
        self._selectedOption = AgentSelectionWindow.__invalid__
        self._selectionMadeCommand = None
        
        self.dataBlob = None # For client use only - not used internally
 
#####################       
    def __str__(self):
        return ("<AgentSelectionWindow: \"%s\", particleShape:\"%s\">" % 
                (self._window.getTitle() if(self._window is not None) else "<Not Visible>", 
                 self._particleShapeName))
    
    def _getMetaStr(self):
        selectedAgentsStr = ''.join([("\t%s\n" % agent) for agent in self._currentlySelectedList])
        return ("<SelectionMethod=%s, selectedText=\"%s\", endCmd=%s, selection:\n\t%s>" %
                (AgentSelectionWindow.__SelectionOptionStrings__[self._selectedOption],
                 self.getSelectionString(), self._selectionMadeCommand, selectedAgentsStr))

#####################     
    def _getParticleShapeName(self):
        return self._agentsController.particleShapeName
    _particleShapeName = property(_getParticleShapeName)
 
#####################   
    def _getIdToAgentLookup(self):
        return self._agentsController._idToAgentLookup
    _idToAgentLookup = property(_getIdToAgentLookup)

#####################  
    def _getSelectionList(self):
        return self._currentlySelectedList
    selectionList = property(_getSelectionList)

#####################    
    def show(self, windowTitle, currentlySelectedAgentsList, selectionMadeCommand):
        if(self._selectedOption != AgentSelectionWindow.__invalid__):
            util.LogWarning("Overwriting previous agent selection session.")
            
        self.closeWindow()
        
        self._currentlySelectedList = currentlySelectedAgentsList[:] # important to take a copy here - avoids modifying the original prematurely
        self._maxIdValue = sorted(self._idToAgentLookup.keys())[-1]
        
        self._window = uib.MakeWindow(windowTitle, (450,80))
        borderLayout = uib.MakeBorderingLayout()
        columnLayout = uib.MakeColumnLayout()
        
        self._textInput = uib.MakeTextInputField("Agent IDs:", 
                                                 self.getSelectionString(), 
                                                 leftColumnWidth=100, 
                                                 annotation=_TextFieldAnnotation_)
        self._radioButtons = uib.MakeRadioButtonGroup("Selection Method:", 
                                                      AgentSelectionWindow.__SelectionOptionStrings__[1:], 
                                                      self._onRadioButtonChange,
                                                      leftColumnWidth=100,
                                                      annotation=_RadioButtonsAnnotation_)
        self._radioButtons.setSelect(AgentSelectionWindow.__textInputSelection__)
        self._selectedOption = AgentSelectionWindow.__textInputSelection__
        
        uib.SetAsChildLayout(columnLayout, borderLayout)
        
        uib.MakeButtonStrip((("OK", self._okButtonWasPressed), ("Cancel", self.closeWindow)))
        self._selectionMadeCommand = selectionMadeCommand
        
        self._window.show()
        
#####################
    def getSelectionString(self):        
        if(self._currentlySelectedList):
            ####
            def _appendToStringArray(stringArray, rangeStart, rangeEnd):
                if(stringArray): stringArray.append(", ")
                if(rangeStart == rangeEnd):
                    stringArray.append("%d" % rangeStart)
                else:
                    stringArray.append("%d-%d" % (rangeStart, rangeEnd))
            ####
            
            rangeStart = -1
            rangeEnd = -1
            stringArray = []
            for agent in self._currentlySelectedList:
                agentId = agent.particleId
                if(rangeStart == -1):
                    rangeStart = agentId
                    rangeEnd = agentId
                elif(agentId == rangeEnd + 1):
                    rangeEnd = agentId
                else:
                    _appendToStringArray(stringArray, rangeStart, rangeEnd)
                    rangeStart = agentId
                    rangeEnd = agentId
            if(rangeStart != -1):
                _appendToStringArray(stringArray, rangeStart, rangeEnd)
            
            return "".join(stringArray)
        else:
            return ""   
        
#####################    
    def _updateSelectionFromStringIfNecessary(self):
        ######
        def _strip(string):
            return string.strip()
        
        def _getRangeFromSubTokens(subTokens, upperBounds):
            if(len(subTokens) == 1):
                if(subTokens[0] == '*'): return (0, upperBounds)
                elif(subTokens[0].isdigit()): return (int(subTokens[0]), int(subTokens[0]))
                else: raise ValueError
            else:
                rangeStart = -1
                if(subTokens[0] == '*'): rangeStart = 0
                elif(subTokens[0].isdigit()): rangeStart = int(subTokens[0])
                else: raise ValueError
                
                if(subTokens[1] == '*'): return (rangeStart, upperBounds)
                elif(subTokens[1].isdigit()): return (rangeStart, int(subTokens[1]))
                else: raise ValueError
        ######
        
        if(self._selectedOption == AgentSelectionWindow.__textInputSelection__):
            try:
                newSelection = set()
                stringTokens = self._textInput.getText().split(',')
                for token in stringTokens:
                    subTokens = map(_strip, token.split('-'))
                    if(len(subTokens) != 1 and len(subTokens) != 2):
                        raise ValueError
                    else:
                        tokenRange = _getRangeFromSubTokens(subTokens, self._maxIdValue)
                        for i in xrange(tokenRange[0], tokenRange[1] + 1):
                            newSelection.add(i)
    
                del self._currentlySelectedList[:]
                for agentId in filter(self._idToAgentLookup.has_key, newSelection):
                    self._currentlySelectedList.append(self._idToAgentLookup[agentId])
            except:
                return False
        
        return True

#####################    
    def _updateSelectionFromSceneIfNecessary(self):
        if(self._selectedOption == AgentSelectionWindow.__sceneSelection__):
            del self._currentlySelectedList[:]
            for selectedAgentId in sorted(util.GetSelectedParticles(self._particleShapeName)):
                self._currentlySelectedList.append(self._idToAgentLookup[selectedAgentId])
            self._textInput.setText(self.getSelectionString())
    
#####################    
    def _onRadioButtonChange(self, *args):
        if(self._radioButtons.getSelect() != self._selectedOption):
            self._selectedOption = self._radioButtons.getSelect()
            
            if(self._selectedOption == AgentSelectionWindow.__textInputSelection__):
                self._textInput.setEditable(True)
            elif(self._selectedOption == AgentSelectionWindow.__sceneSelection__):
                self._updateSelectionFromSceneIfNecessary()
                self._textInput.setEditable(False)
            elif(self._selectedOption == AgentSelectionWindow.__selectAll__): 
                self._currentlySelectedList = sorted(self._idToAgentLookup.values())
                self._textInput.setText("*")
                self._textInput.setEditable(False)
            elif(self._selectedOption == AgentSelectionWindow.__selectNone__): 
                del self._currentlySelectedList[:]
                self._textInput.setText("")
                self._textInput.setEditable(False)
      
#####################        
    def _okButtonWasPressed(self, *args):
        if(self._updateSelectionFromStringIfNecessary()):
            self._updateSelectionFromSceneIfNecessary()
            self._selectionMadeCommand(self, self._currentlySelectedList, self.getSelectionString())
        else:
            util.LogError("Invalid input - selection not changed")
            
        self.closeWindow()          
    
#####################        
    def closeWindow(self, *args):
        if(uib.WindowExists(self._window)):
            util.EvalDeferred(uib.DestroyWindow, self._window)
        
        del self._currentlySelectedList[:]
        self._window = None
        self._textInput = None
        self._radioButtons = None
        self._selectedOption = AgentSelectionWindow.__invalid__


# END OF CLASS - AgentSelectionWindow
########################################