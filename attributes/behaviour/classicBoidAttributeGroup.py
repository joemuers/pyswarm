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


import attributes.attributeGroupObject as ago
import attributes.attributeTypes as at
import utils.uiBuilder as uib
import utils.general as util
import vectors.vector3 as v3
import utils.agentSelectionWindow as asw

import random as rand



###########################################
class ClassicBoidDataBlob(ago._DataBlobBaseObject):
    
    def __init__(self, agent):
        super(ClassicBoidDataBlob, self).__init__(agent)
        
        self.alignmentDirectionThreshold = 0
        self.cohesionPositionThreshold = 0.0
        self.separationWeighting = 1.0
        self.alignmentWeighting = 1.0
        self.cohesionWeighting = 1.0
        
#####################
    def __str__(self):
        return ("<CLASSIC BHVR: align=%d, cohesn=%.2f>" % 
                (self.alignmentDirectionThreshold, self.cohesionPositionThreshold))
    
# END OF CLASS - ClassicBoidDataBlob
###########################################



###########################################
class ClassicBoidAttributeGroup(ago.AttributeGroupObject):
    
    @classmethod
    def BehaviourTypeName(cls):
        return "Classic Boid Behaviour"
    
#####################    
    def __init__(self, behaviourId, globalAttributeGroup):
        super(ClassicBoidAttributeGroup, self).__init__(behaviourId)
        
        self._kickstartEnabled = at.BoolAttribute("Kickstart Enabled", False, self)
        self._kickstartFrameNumber = at.IntAttribute("Frame Number", 0, minimumValue=0)
        self._kickstartAgentsText = at.StringAttribute("Agents", "")
        self._kickstartAgentsText.excludeFromDefaults = True
        self._kickstartAgents = set()
        self._kickstartMinValue = at.Vector3Attribute("Minimum", v3.Vector3())
        self._kickstartMaxValue = at.Vector3Attribute("Maximum", v3.Vector3())
        self._kickstartAgentSelectionWindow = asw.AgentSelectionWindow(globalAttributeGroup)
        self._kickstartNowButton = None
        self.kickOnNextFrame = False
        
        self._mutuallyExclusive = at.BoolAttribute("Mutually Exclusive", True, self)
        self._separationWeighting = at.FloatAttribute("Separation Weighting", 1.0, self, maximumValue=1.0)
        self._separationWeighting_Random = at.RandomizeController(self._separationWeighting)
        
        self._alignmentWeighting = at.FloatAttribute("Alignment Weighting", 1.0, self, maximumValue=1.0)
        self._alignmentWeighting_Random = at.RandomizeController(self._alignmentWeighting)
        self._alignmentDirectionThreshold = at.IntAttribute("Alignment Threshold", 30, self, maximumValue=359)
        self._alignmentDirectionThreshold_Random = at.RandomizeController(self._alignmentDirectionThreshold)
        
        self._cohesionWeighting = at.FloatAttribute("Cohesion Weighting", 1.0, self, maximumValue=1.0)
        self._cohesionWeighting_Random = at.RandomizeController(self._cohesionWeighting)
        self._cohesionPositionThreshold = at.FloatAttribute("Cohesion Threshold", 1.9, self)
        self._cohesionPositionThreshold_Random = at.RandomizeController(self._cohesionPositionThreshold)
        
        self.onValueChanged(self._mutuallyExclusive)
        self.onValueChanged(self._kickstartEnabled)
        
#######################
    def __getstate__(self):
        state = super(ClassicBoidAttributeGroup, self).__getstate__()
        
        state["_kickstartAgentSelectionWindow"] = None
        state["_kickstartNowButton"] = None
        state["globalAttributeGroup"] = self._kickstartAgentSelectionWindow._globalAttributeGroup
        
        return state
    
########
    def __setstate__(self, state):
        globalAttributeGroup = state["globalAttributeGroup"]
        del state["globalAttributeGroup"]
        
        super(ClassicBoidAttributeGroup, self).__setstate__(state)
        
        self._kickstartAgentSelectionWindow = asw.AgentSelectionWindow(globalAttributeGroup)
        
#####################
    def _getKickOnNextFrame(self):
        return self._kickOnNextFrame
    def _setKickOnNextFrame(self, value):
        if(self._kickstartNowButton is not None):
            self._kickstartNowButton.setLabel("Kick Now*" if(value) else "Kick Now")
        self._kickOnNextFrame = value
    kickOnNextFrame = property(_getKickOnNextFrame, _setKickOnNextFrame)
    
#####################
    def populateUiLayout(self):
        frameLayout = uib.MakeFrameLayout("Kickstart")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeCheckboxGroup(self._kickstartEnabled)
        uib.MakeSimpleIntField(self._kickstartFrameNumber)
        uib.MakePassiveTextField(self._kickstartAgentsText, self._didPressKickstartAgentSelect)
        uib.MakeVectorField(self._kickstartMaxValue)
        uib.MakeVectorField(self._kickstartMinValue)
        buttonTitle = "Kick Now" if(not self.kickOnNextFrame) else "Kick Now*"
        self._kickstartNowButton = uib.MakeButtonStandalone("Kick Now", self._didPressKickstartNow)[1]
        self._kickstartNowButton.setEnable(self._kickstartEnabled.value)
        uib.SetAsChildLayout(columnLayout, frameLayout)
        
        frameLayout = uib.MakeFrameLayout("Seperation")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeCheckboxGroup(self._mutuallyExclusive)
        uib.MakeSliderGroup(self._separationWeighting)
        uib.MakeRandomizerFields(self._separationWeighting_Random)
        uib.SetAsChildLayout(columnLayout, frameLayout)
        
        frameLayout = uib.MakeFrameLayout("Alignment")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeSliderGroup(self._alignmentWeighting)
        uib.MakeRandomizerFields(self._alignmentWeighting_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._alignmentDirectionThreshold)
        uib.MakeRandomizerFields(self._alignmentDirectionThreshold_Random)
        uib.SetAsChildLayout(columnLayout, frameLayout)
        
        frameLayout = uib.MakeFrameLayout("Cohesion")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeSliderGroup(self._cohesionWeighting)
        uib.MakeRandomizerFields(self._cohesionWeighting_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._cohesionPositionThreshold)
        uib.MakeRandomizerFields(self._cohesionPositionThreshold_Random)
        uib.SetAsChildLayout(columnLayout, frameLayout)
        
#####################
    def _didPressKickstartNow(self, *args):
        self.kickOnNextFrame = True
     
#########   
    def _didPressKickstartAgentSelect(self, *args):
        self._kickstartAgentSelectionWindow.show("Select Agents to Kickstart", 
                                                 self._kickstartAgents, 
                                                 self._onKickstartAgentSelectionComplete, 
                                                 self._dataBlobs.keys())
        
#########
    def _onKickstartAgentSelectionComplete(self, selectionWindow, selectedAgentsList, selectionDisplayString):
        self._kickstartAgentsText.value = selectionDisplayString
        self._kickstartAgents = set(selectedAgentsList)
        
#####################    
    def onFrameUpdated(self):
        if(self._kickstartEnabled and util.GetCurrentFrameNumber() == self._kickstartFrameNumber.value):
            self.kickOnNextFrame = True
            
########
    def onCalculationsCompleted(self):
        self.kickOnNextFrame = False
        
#####################
    def _createDataBlobForAgent(self, agent):
        return ClassicBoidDataBlob(agent)
    
#####################
    def _updateDataBlobWithAttribute(self, dataBlob, attribute):
        if(attribute is self._separationWeighting):
            dataBlob.separationWeighting = self._getSeparationWeightingForBlob(dataBlob)
        elif(attribute is self._alignmentWeighting):
            dataBlob.alignmentWeighting = self._getAlignmentWeightingForBlob(dataBlob)
        elif(attribute is self._alignmentDirectionThreshold):
            dataBlob.alignmentDirectionThreshold = self._getAlignmentDirectionThresholdForBlob(dataBlob)
        elif(attribute is self._cohesionWeighting):
            dataBlob.cohesionWeighting = self._getCohesionWeightingForBlob(dataBlob)
        elif(attribute is self._cohesionPositionThreshold):
            dataBlob.cohesionPositionThreshold = self._getCohesionPositionThresholdForBlob(dataBlob)

#####################
    def onValueChanged(self, changedAttribute):
        super(ClassicBoidAttributeGroup, self).onValueChanged(changedAttribute)
        
        if(changedAttribute is self._mutuallyExclusive):
            separationWeightingEnabled = not self._mutuallyExclusive.value
            self._separationWeighting.setEnabled(separationWeightingEnabled)
            self._separationWeighting_Random.setEnabled(separationWeightingEnabled)
        elif(changedAttribute is self._kickstartEnabled):
            enabled = self._kickstartEnabled.value
            self._kickstartFrameNumber.setEnabled(enabled)
            self._kickstartMinValue.setEnabled(enabled)
            self._kickstartMaxValue.setEnabled(enabled)
            if(self._kickstartNowButton is not None):
                self._kickstartNowButton.setEnable(enabled)
            self._kickstartAgentsText.setEnabled(enabled)
            if(not enabled):
                self.kickOnNextFrame = False

#####################
    def shouldKickstartAgent(self, agentId):
        return (self.kickOnNextFrame and agentId in self._kickstartAgents)
    
########
    def getKickstartVector(self):
        x = rand.uniform(self._kickstartMinValue.x, self._kickstartMaxValue.x)
        y = rand.uniform(self._kickstartMinValue.y, self._kickstartMaxValue.y)
        z = rand.uniform(self._kickstartMinValue.z, self._kickstartMaxValue.z)
        
        return v3.Vector3(x, y, z)

#####################         
    def _getSeparationIsMutuallyExclusive(self):
        return self._mutuallyExclusive.value
    separationIsMutuallyExclusive = property(_getSeparationIsMutuallyExclusive)
    
########
    def _getSeparationWeightingForBlob(self, dataBlob):
        return self._separationWeighting_Random.valueForIntegerId(dataBlob.agentId)

########
    def _getAlignmentWeightingForBlob(self, dataBlob):
        return self._alignmentDirectionThreshold_Random.valueForIntegerId(dataBlob.agentId)
    
########
    def _getAlignmentDirectionThresholdForBlob(self, dataBlob):
        return self._alignmentDirectionThreshold_Random.valueForIntegerId(dataBlob.agentId)

########
    def _getCohesionWeightingForBlob(self, dataBlob):
        return self._cohesionWeighting_Random.valueForIntegerId(dataBlob.agentId)
    
########        
    def _getCohesionPositionThresholdForBlob(self, dataBlob):
        return self._cohesionPositionThreshold_Random.valueForIntegerId(dataBlob.agentId)

# END OF CLASS
##############################    
