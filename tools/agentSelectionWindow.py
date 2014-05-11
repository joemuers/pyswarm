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


from pyswarmObject import PyswarmObject

import uiBuilder as uib
import tools.util as util
import tools.sceneInterface as scene



########################
_UpdateRadioButtonsAnnotation_ = "Add = Final selection will be added to the previously existing selection.\n\
Set = Final selection will replace the previously existing selection."

_TextFieldAnnotation_ = "Comma-separated list of particle IDs, range format = \"x-y\", wildcard = \"*\"\n\
eg. \"*-3, 6, 9, 10-13\" gives the selection: 0,1,2,3,6,9,10,11,12,13.\n\
NB. Agent IDs relate directly to Maya's particle IDs."

_SelectionRadioButtonsAnnotation_ = "Listed IDs = Takes selection from listed IDs in the text box, above.\n\
In-Scene = Takes selection from individually selected particles within the scene.\n\
All = Selects all the agents in the scene.\n\
None = Clears the selection."


_LeftColumnWidth_ = 100

########################



#########################################
class AgentSelectionWindow(PyswarmObject):
    
    __invalid__, __textInputSelection__, __sceneSelection__, __selectAll__, __selectNone__ = range(5)
    __SelectionOptionStrings__ = ["<N/A>", "Listed IDs", "In-Scene", "All", "None"]
    
    __invalid__, __addSelection__, __setSelection__ = range(3)
    __UpdateTypeStrings__ = ["<N/A>", "Add", "Set"]
    
    
#####################    
    def __init__(self, globalAttributes):
        self._globalAttributes = globalAttributes
        self._currentlySelectedAgentsList = []
        self._originallySelectedAgentsSet = set()
        self._fullAgentsList = []
        
        self._window = None
        self._updateTypeRadioButtons = None
        self._textInput = None
        self._selectionMethodRadioButtons = None
        self._selectedOption = AgentSelectionWindow.__invalid__
        self._selectionMadeCommand = None
        
        self.dataBlob = None # For client use only - not used internally

########
    def __del__(self):
        self.closeWindow()
         
#####################       
    def __str__(self):
        return ("<AgentSelectionWindow: \"%s\", particleShape:\"%s\">" % 
                (self._window.getTitle() if(self._window is not None) else "<Not Visible>", 
                 self._particleShapeName))

########    
    def _getMetaStr(self):
        selectedAgentsStr = ', '.join([("%d" % agentId) for agentId in self._currentlySelectedAgentsList])
        return ("<SelectionMethod=%s, selectedText=\"%s\", endCmd=%s, selection: %s>" %
                (AgentSelectionWindow.__SelectionOptionStrings__[self._selectedOption],
                 self._getSelectionString(), self._selectionMadeCommand, selectedAgentsStr))

#####################
    def _getParticleShapeName(self):
        return self._globalAttributes.particleShapeNode.name()
    _particleShapeName = property(_getParticleShapeName)

#####################  
    def _getSelectionList(self):
        return self._currentlySelectedAgentsList
    selectionList = property(_getSelectionList)

#########
    def _getOriginalSelection(self):
        return self._originallySelectedAgentsSet
    originalSelection = property(_getOriginalSelection)
    
#####################    
    def show(self, windowTitle, currentlySelectedAgentIdsList, selectionMadeCommand, validSelectionIdsList=None):            
        if(not uib.WindowIsVisible(self._window)):
        
            self._currentlySelectedAgentsList = list(currentlySelectedAgentIdsList) # important to take a copy here - avoids modifying the original prematurely
            self._originallySelectedAgentsSet = set(currentlySelectedAgentIdsList)
            if(validSelectionIdsList is not None):
                self._fullAgentsList = sorted(validSelectionIdsList)
            else:
                self._fullAgentsList = sorted(scene.ParticleIdsListForParticleShape(self._particleShapeName))
            
            self._window = uib.MakeWindow(windowTitle)#, (450,80))
            formLayout = uib.MakeFormLayout()
            
            borderLayout = uib.MakeBorderingLayout()
            columnLayout = uib.MakeColumnLayout()
            self._textInput = uib.MakeTextInputField("Agent IDs:", 
                                                     self._okButtonWasPressed,
                                                     self._getSelectionString(), 
                                                     leftColumnWidth=_LeftColumnWidth_, 
                                                     annotation=_TextFieldAnnotation_)[1]
            self._selectionMethodRadioButtons = uib.MakeRadioButtonGroup("Selection Method:", 
                                                                         AgentSelectionWindow.__SelectionOptionStrings__[1:], 
                                                                         self._onSelectionRadioButtonChange,
                                                                         vertical=False,
                                                                         leftColumnWidth=_LeftColumnWidth_,
                                                                         annotation=_SelectionRadioButtonsAnnotation_)
            self._selectionMethodRadioButtons.setSelect(AgentSelectionWindow.__textInputSelection__)
            self._selectedOption = AgentSelectionWindow.__textInputSelection__
            
            self._updateTypeRadioButtons = uib.MakeRadioButtonGroup("Update Type:",
                                                                    AgentSelectionWindow.__UpdateTypeStrings__[1:],
                                                                    None,
                                                                    vertical=True,
                                                                    leftColumnWidth=_LeftColumnWidth_,
                                                                    annotation=_UpdateRadioButtonsAnnotation_)
            uib.SetAsChildLayout(columnLayout, borderLayout)
            
            buttonStripLayout = uib.MakeButtonStrip((("OK", self._okButtonWasPressed), ("Cancel", self.closeWindow)))[0]
            self._selectionMadeCommand = selectionMadeCommand
            uib.SetAsChildLayout(buttonStripLayout)
            
            uib.DistributeButtonedWindowInFormLayout(formLayout, borderLayout, buttonStripLayout)
            
        self._window.show()
        
#####################
    def _getSelectionString(self):        
        if(self._currentlySelectedAgentsList):
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
            for agentId in self._currentlySelectedAgentsList:
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
        #####
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
                    subTokens = map(lambda tkn: tkn.strip(), token.split('-'))
                    if(len(subTokens) != 1 and len(subTokens) != 2):
                        raise ValueError
                    else:
                        maxIdValue = self._fullAgentsList[-1]
                        tokenRange = _getRangeFromSubTokens(subTokens, maxIdValue)
                        for i in xrange(tokenRange[0], tokenRange[1] + 1):
                            newSelection.add(i)
                
                del self._currentlySelectedAgentsList[:]
                for agentId in newSelection.intersection(set(self._fullAgentsList)):
                    self._currentlySelectedAgentsList.append(agentId)
            except:
                return False
        
        return True

#####################    
    def _updateSelectionFromSceneIfNecessary(self):
        if(self._selectedOption == AgentSelectionWindow.__sceneSelection__):
            selectedParticleIds = scene.GetSelectedParticles(self._particleShapeName)
            del self._currentlySelectedAgentsList[:]
            self._currentlySelectedAgentsList.extend(sorted(selectedParticleIds))
            self._textInput.setText(self._getSelectionString())

#####################             
    def _updateSelectionWithOriginalSelectionIfNecessary(self):
        if(self._updateTypeRadioButtons.getSelect() == AgentSelectionWindow.__addSelection__ and
           self._originallySelectedAgentsSet):
            fullSelection = self._originallySelectedAgentsSet.union(self._currentlySelectedAgentsList)
            if(len(fullSelection) > len(self._currentlySelectedAgentsList)):
                del self._currentlySelectedAgentsList[:]
                self._currentlySelectedAgentsList.extend(fullSelection)
                self._currentlySelectedAgentsList.sort()
    
#####################    
    def _onSelectionRadioButtonChange(self, *args):
        if(self._selectionMethodRadioButtons.getSelect() != self._selectedOption):
            self._selectedOption = self._selectionMethodRadioButtons.getSelect()
            
            if(self._selectedOption == AgentSelectionWindow.__textInputSelection__):
                self._textInput.setEditable(True)
            elif(self._selectedOption == AgentSelectionWindow.__sceneSelection__):
                self._updateSelectionFromSceneIfNecessary()
                self._textInput.setEditable(False)
            elif(self._selectedOption == AgentSelectionWindow.__selectAll__): 
                del self._currentlySelectedAgentsList[:]
                self._currentlySelectedAgentsList.extend(self._fullAgentsList)
                self._textInput.setText(self._getSelectionString())
                self._textInput.setEditable(False)
            elif(self._selectedOption == AgentSelectionWindow.__selectNone__): 
                del self._currentlySelectedAgentsList[:]
                self._textInput.setText("")
                self._textInput.setEditable(False)
      
#####################        
    def _okButtonWasPressed(self, *args):
        if(self._updateSelectionFromStringIfNecessary()):
            self._updateSelectionFromSceneIfNecessary()
            self._updateSelectionWithOriginalSelectionIfNecessary()
            self._selectionMadeCommand(self, self._currentlySelectedAgentsList, self._getSelectionString())
        else:
            util.LogError("Invalid input - selection not changed")
            
        self.closeWindow()          
    
#####################        
    def closeWindow(self, *args):
        util.EvalDeferred(uib.DestroyWindowIfNecessary, self._window)
        
        del self._currentlySelectedAgentsList[:]
        self._originallySelectedAgentsSet.clear()
        self._window = None
        self._textInput = None
        self._selectionMethodRadioButtons = None
        self._selectedOption = AgentSelectionWindow.__invalid__


# END OF CLASS - AgentSelectionWindow
########################################