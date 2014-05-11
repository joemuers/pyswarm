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


import attributeGroupObject as ago
import attributeTypes as at
import tools.util as util
import tools.uiBuilder as uib
import tools.sceneInterface as scene
import tools.agentSelectionWindow as asw



###########################################
class GoalDrivenDataBlob(ago._DataBlobBaseObject):
    
    _uninitialised, normal, pending, goalChase, inBasePyramid, atWallLip, overWallLip, reachedFinalGoal = range(8)
    
#####################    
    def __init__(self, agent):
        super(GoalDrivenDataBlob, self).__init__(agent)
        
        self.incubationPeriod = 0
        self.goalChaseSpeed = 0.0
        
        self.pyramidJoinAtDistance = 0.0
        self.pyramidJumpOnDistance = 0.0
        
        self.currentStatus = GoalDrivenDataBlob._uninitialised
        
        self.didArriveAtBasePyramid = False
        self.goalChaseCountdown = -1

#####################        
    def __str__(self):
        status = ("UNKNOWN (%d)" % self.currentStatus)
        if(self.currentStatus == GoalDrivenDataBlob.normal):
            status = "NORMAL"
        elif(self.currentStatus == GoalDrivenDataBlob.pending):
            status = "PENDING"
        elif(self.currentStatus == GoalDrivenDataBlob.goalChase):
            status = "GOAL_CHASE"
        elif(self.currentStatus == GoalDrivenDataBlob.inBasePyramid):
            status = "BASE_PYRAMID"
        elif(self.currentStatus == GoalDrivenDataBlob.atWallLip):
            status = "AT_LIP"
        elif(self.currentStatus == GoalDrivenDataBlob.overWallLip):
            status = "OVER_LIP"
        elif(self.currentStatus == GoalDrivenDataBlob.reachedFinalGoal):
            status = "AT_GOAL"
        
        return ("<GOAL-DRIVEN BHVR: incubtn=%d, goalChs=%.2f, pyrmdJoin=%.2f, pyrmdJmp=%.2f, status=%s, arvd=%s, cntdwn=%d>" %
                (self.incubationPeriod, self.goalChaseSpeed, self.pyramidJoinAtDistance, self.pyramidJumpOnDistance,
                 status, "Y" if self.didArriveAtBasePyramid else "N", self.goalChaseCountdown))

# END OF CLASS - GoalDrivenDataBlob
###########################################



###########################################
class GoalDrivenBehaviourAttributes(ago.AttributeGroupObject, ago._FollowOnBehaviourAttributeInterface):

    @classmethod
    def BehaviourTypeName(cls):
        return "Goal-Driven Behaviour"
    
#####################    
    def __init__(self, behaviourId, globalAttributes, wallLipGoal=None, basePyramidGoalHeight=None, finalGoal=None):
        super(GoalDrivenBehaviourAttributes, self).__init__(behaviourId)
        
        self._globalAttributes = globalAttributes
        
        if(basePyramidGoalHeight is not None and type(basePyramidGoalHeight) != float):
            pyramidBaseVector = scene.Vector3FromLocator(basePyramidGoalHeight)
            if(pyramidBaseVector is not None):
                basePyramidGoalHeight = pyramidBaseVector.y
        
        self._wallLipGoal = at.LocationAttribute("Wall Lip Goal", util.InitVal(wallLipGoal, (0, 5, 0)), self)
        basePyramidLocation = (self._wallLipGoal.x, util.InitVal(basePyramidGoalHeight, 0), self._wallLipGoal.z)
        self._basePyramidGoal = at.LocationAttribute("Base Pyramid Goal", basePyramidLocation, self)
        self._finalGoal = at.LocationAttribute("Final Goal", util.InitVal(finalGoal, (0 ,5, 5)), self)
        self._wallLipGoal.excludeFromDefaults = True
        self._basePyramidGoal.excludeFromDefaults = True
        self._finalGoal.excludeFromDefaults = True
        
        self._useInfectionSpread = at.BoolAttribute("Use Infection Spread", False, self)
        
        self._leadersText = at.StringAttribute("Leader Agents", "")
        self._leadersText.excludeFromDefaults = True
        self._selectCurrentLeadersButtonEnable = None                            # should *not* be
        self._leaderSelectionWindow = asw.AgentSelectionWindow(globalAttributes) # included in Pickle save
        self._leaderAgentIds = set()
        
        self._incubationPeriod = at.IntAttribute("Incubation Period", 10, self)
        self._incubationPeriod_Random = at.RandomizeController(self._incubationPeriod)
        self._goalChaseSpeed = at.FloatAttribute("Goal Chase Speed", 10, self)
        self._goalChaseSpeed_Random = at.RandomizeController(self._goalChaseSpeed)
        
        self._pyramidJoinAtDistance = at.FloatAttribute("Join-At Distance", 0.5, self)
        self._pyramidJoinAtDistance_Random = at.RandomizeController(self._pyramidJoinAtDistance)
        self._pyramidJumpOnDistance = at.FloatAttribute("Jump-On-At Distance", 1, self)
        self._pyramidJumpOnDistance_Random = at.RandomizeController(self._pyramidJumpOnDistance)
        self._pyramidJumpOnProbability = at.FloatAttribute("Jump-On Probability", 0.1, self, minimumValue=0, maximumValue=1)
        self._pyramidPushUpwardsForce = at.FloatAttribute("Push-Upwards Force", 22)
        self._pyramidPushInwardsForce = at.FloatAttribute("Push-Inwards Force", 15)
        
        self.onValueChanged(self._useInfectionSpread) # required to ensure enabled/disabled states are up to date
 
#####################       
    def __getstate__(self):
        state = super(GoalDrivenBehaviourAttributes, self).__getstate__()
        
        state["_selectCurrentLeadersButtonEnable"] = None
        state["_leaderSelectionWindow"] = None
        
        return state

########
    def __setstate__(self, state):
        super(GoalDrivenBehaviourAttributes, self).__setstate__(state)
        
        self._leaderSelectionWindow = asw.AgentSelectionWindow(self._globalAttributes)
        self._selectCurrentLeadersButtonEnable = None
        
####################
    def _getNumberOfLeaders(self):
        return len(self._leaderAgentIds)
    numberOfLeaders = property(_getNumberOfLeaders)
    
########
    def makeLeader(self, agentId):
        if(agentId in self._dataBlobs):
            dataBlob = self._dataBlobs[agentId]
            self._leaderAgentIds.add(agentId)
            
            if(not dataBlob.didArriveAtBasePyramid):
                util.LogInfo("Agent %d made leader for behaviour \"%s\"" % (agentId, self.behaviourId))
                return True
            else:
                util.LogWarning("Agent #%d as leader will have no effect - has already progressed to Pyramid-Join stage." % agentId)
                return False
        else:
            raise ValueError("Cannot make leader - agent #%d is not assigned to behaviour \"%s\"" % 
                             (agentId, self.behaviourId))
    
########
    def unmakeLeader(self, agentId):
        if(agentId in self._dataBlobs):
            if(agentId in self._leaderAgentIds):
                self._leaderAgentIds.remove(agentId)
            else:
                util.LogWarning("Agent #%d is not currently a leader agent." % agentId)
        else:
            raise ValueError("Cannot un-make leader - agent #%d is not assigned to behaviour \"%s\"" % 
                             (agentId, self.behaviourId))
         
########   
    def agentIsLeader(self, agentId):
        return (agentId in self._leaderAgentIds)
    
########
    def allLeaderIds(self):
        return sorted(self._leaderAgentIds)
                
#####################
    def populateUiLayout(self):
        uib.MakeLocationField(self._wallLipGoal, True)
        basePyramidGoalField = uib.MakeLocationField(self._basePyramidGoal)
        basePyramidGoalField.setEnable1(False)
        basePyramidGoalField.setEnable3(False)
        uib.MakeLocationField(self._finalGoal, True)
        
        goalChaseFrameLayout = uib.MakeFrameLayout("Goal-Chase Stage")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeCheckboxGroup(self._useInfectionSpread)
        uib.MakePassiveTextField(self._leadersText, self._didPressSelectLeaderAgents)
        selectButtonRow = uib.MakeButtonStandalone("Scene Select", self._didPressSelectLeadersInScene)[0]
        self._selectCurrentLeadersButtonEnable = selectButtonRow.setEnable
        self._selectCurrentLeadersButtonEnable(self._useInfectionSpread.value)
        uib.MakeSliderGroup(self._incubationPeriod)
        uib.MakeRandomizerFields(self._incubationPeriod_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._goalChaseSpeed)
        uib.MakeRandomizerFields(self._goalChaseSpeed_Random)
        uib.SetAsChildLayout(columnLayout, goalChaseFrameLayout)
        
        pyramidJoinFrameLayout = uib.MakeFrameLayout("Pyramid-Join Stage")
        columnLayout = uib.MakeColumnLayout()
        uib.MakeSliderGroup(self._pyramidJoinAtDistance)
        uib.MakeRandomizerFields(self._pyramidJoinAtDistance_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._pyramidJumpOnDistance)
        uib.MakeRandomizerFields(self._pyramidJumpOnDistance_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._pyramidJumpOnProbability)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._pyramidPushUpwardsForce)
        uib.MakeSliderGroup(self._pyramidPushInwardsForce)
        uib.SetAsChildLayout(columnLayout, pyramidJoinFrameLayout)

        finalStageFrameLayout = uib.MakeFrameLayout("Final Stage")
        columnLayout = uib.MakeColumnLayout()
        self._makeFollowOnBehaviourOptionGroup()
        uib.SetAsChildLayout(columnLayout, finalStageFrameLayout)
        
#####################
    def _createDataBlobForAgent(self, agent):
        return GoalDrivenDataBlob(agent)
    
#####################   
    def onBehaviourListUpdated(self, behaviourIDsList, defaultBehaviourId):
        self._updateFollowOnBehaviourOptions(behaviourIDsList, defaultBehaviourId)
    
#####################
    def onFrameUpdated(self):
        self._basePyramidGoal.verifyLocatorIfNecessary()
        self._wallLipGoal.verifyLocatorIfNecessary()
        self._finalGoal.verifyLocatorIfNecessary()

#####################        
    def onValueChanged(self, changedAttribute):
        super(GoalDrivenBehaviourAttributes, self).onValueChanged(changedAttribute)
        
        if(changedAttribute is self._wallLipGoal):
            self._basePyramidGoal.x = self._wallLipGoal.x
            self._basePyramidGoal.z = self._wallLipGoal.z
        elif(changedAttribute is self._useInfectionSpread):
            self._leadersText.setEnabled(changedAttribute.value)
            self._incubationPeriod.setEnabled(changedAttribute.value)
            self._incubationPeriod_Random.setEnabled(changedAttribute.value)
            if(self._selectCurrentLeadersButtonEnable is not None):
                self._selectCurrentLeadersButtonEnable(changedAttribute.value)

#####################            
    def _didPressSelectLeaderAgents(self, *args):
        self._leaderSelectionWindow.show(("Select leader agents for \"%s\"" % self.behaviourId),
                                          self._leaderAgentIds, 
                                          self._onLeaderSelectCompleted, 
                                          self._dataBlobs.keys())

########        
    def _onLeaderSelectCompleted(self, selectionWindow, selectedAgentsList, selectionDisplayString):
        self._leadersText.value = selectionDisplayString
        self._leaderAgentIds = set(selectedAgentsList)

########        
    def _didPressSelectLeadersInScene(self, *args):
        scene.SelectParticlesInList(self._leaderAgentIds, self._globalAttributes.particleShapeNode.name())
    
#####################
    def _updateDataBlobWithAttribute(self, dataBlob, attribute):
        if(attribute is self._incubationPeriod):
            dataBlob.incubationPeriod = self._getBehaviourIncubationPeriodForBlob(dataBlob)
        elif(attribute is self._goalChaseSpeed):
            dataBlob.goalChaseSpeed = self._getGoalChaseSpeedForBlob(dataBlob)
        elif(attribute is self._pyramidJoinAtDistance):
            dataBlob.pyramidJoinAtDistance = self._getPyramidJoinAtDistanceForBlob(dataBlob)
        elif(attribute is self._pyramidJumpOnDistance):
            dataBlob.pyramidJumpOnDistance = self._getPyramidJumpOnDistanceForBlob(dataBlob)

#####################     
    def _getBehaviourIncubationPeriodForBlob(self, dataBlob):
        return self._incubationPeriod_Random.valueForIntegerId(dataBlob.agentId)
     
    def _getGoalChaseSpeedForBlob(self, dataBlob):
        return self._goalChaseSpeed_Random.valueForIntegerId(dataBlob.agentId)
    
    def _getPyramidJoinAtDistanceForBlob(self, dataBlob):
        return self._pyramidJoinAtDistance_Random.valueForIntegerId(dataBlob.agentId)
   
    def _getPyramidJumpOnDistanceForBlob(self, dataBlob):
        return self._pyramidJumpOnDistance_Random.valueForIntegerId(dataBlob.agentId)

##################### 
    def _getBasePyramidGoal(self):
        return self._basePyramidGoal.value
    basePyramidGoal = property(_getBasePyramidGoal)
    
    def _getWallLipGoal(self):
        return self._wallLipGoal.value
    wallLipGoal = property(_getWallLipGoal)
    
    def _getFinalGoal(self):
        return self._finalGoal.value
    finalGoal = property(_getFinalGoal)
    
##################### 
    def _getUseInfectionSpread(self):
        return self._useInfectionSpread.value
    useInfectionSpread = property(_getUseInfectionSpread)
    
#####################     
    def _getPyramidJumpOnProbability(self):
        return self._pyramidJumpOnProbability.value
    pyramidJumpOnProbability = property(_getPyramidJumpOnProbability)

#####################     
    def _getBasePyramidPushUpwardsForce(self):
        return self._pyramidPushUpwardsForce.value
    basePyramidPushUpwardsForce = property(_getBasePyramidPushUpwardsForce)

#####################     
    def _getBasePyramidPushInwardsForce(self):
        return self._pyramidPushInwardsForce.value
    basePyramidPushInwardsForce = property(_getBasePyramidPushInwardsForce)
    
#####################
    def _getFollowOnBehaviourID(self):
        return self._followOnBehaviour.value
    followOnBehaviourID = property(_getFollowOnBehaviourID)
    
    
# END OF CLASS
##################################    