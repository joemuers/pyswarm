import attributesBaseObject as abo
import attributeTypes as at
import boidTools.uiBuilder as uib
import boidTools.util as util



###########################################
class GoalDrivenDataBlob(abo.DataBlobBaseObject):
    
    _invalid, normal, pending, goalChase, inBasePyramid, atWallLip, overWallLip, reachedFinalGoal = range(8)
    
#####################    
    def __init__(self, agent):
        super(GoalDrivenDataBlob, self).__init__(agent)
        
        self.incubationPeriod = 0
        self.goalChaseSpeed = 0.0
        
        self.pyramidJoinAtDistance = 0.0
        self.pyramidJumpOnDistance = 0.0
        
        self.currentStatus = GoalDrivenDataBlob._invalid
        
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

# END OF CLASS - ClassicBoidDataBlob
###########################################



###########################################
class GoalDrivenBehaviourAttributes(abo.AttributesBaseObject):

    @classmethod
    def DefaultSectionTitle(cls):
        return "Goal-Driven Behaviour"
    
#####################    
    def __init__(self, sectionTitle, wallLipGoal=None, basePyramidGoalHeight=None, finalGoal=None):
        super(GoalDrivenBehaviourAttributes, self).__init__(sectionTitle)
        
        if(basePyramidGoalHeight is not None and type(basePyramidGoalHeight) != float):
            pyramidBaseVector = util.Vector3FromLocator(basePyramidGoalHeight)
            if(pyramidBaseVector is not None):
                basePyramidGoalHeight = pyramidBaseVector.y
                
        self._defaultBehaviourID = "<None>"
        self._followOnBehaviourIDs = [self._defaultBehaviourID]
        self._followOnBehaviourMenu = None
        self._followOnBehaviourMenuItems = None
        
        self._wallLipGoal = at.LocationAttribute("Wall Lip Goal", util.InitVal(wallLipGoal, (0, 5, 0)), self)
        basePyramidLocation = (self._wallLipGoal.x, util.InitVal(basePyramidGoalHeight, 0), self._wallLipGoal.z)
        self._basePyramidGoal = at.LocationAttribute("Base Pyramid Goal", basePyramidLocation, self)
        self._finalGoal = at.LocationAttribute("Final Goal", util.InitVal(finalGoal, (0 ,5, 5)), self)
        self._wallLipGoal.excludeFromDefaults = True
        self._basePyramidGoal.excludeFromDefaults = True
        self._finalGoal.excludeFromDefaults = True
        
        self._useInfectionSpread = at.BoolAttribute("Use Infection Spread", False)
        self._incubationPeriod = at.IntAttribute("Incubation Period", 10, self)
        self._incubationPeriod_Random = at.RandomizerAttribute(self._incubationPeriod)
        self._goalChaseSpeed = at.FloatAttribute("Goal Chase Speed", 10, self)
        self._goalChaseSpeed_Random = at.RandomizerAttribute(self._goalChaseSpeed)
        
        self._pyramidJoinAtDistance = at.FloatAttribute("Join-At Distance", 0.5, self)
        self._pyramidJoinAtDistance_Random = at.RandomizerAttribute(self._pyramidJoinAtDistance)
        self._pyramidJumpOnDistance = at.FloatAttribute("Jump-On-At Distance", 1, self)
        self._pyramidJumpOnDistance_Random = at.RandomizerAttribute(self._pyramidJumpOnDistance)
        self._pyramidJumpOnProbability = at.FloatAttribute("Jump-On Probability", 0.1, self, minimumValue=0, maximumValue=1)
        self._pyramidPushUpwardsForce = at.FloatAttribute("Push-Upwards Force", 22)
        self._pyramidPushInwardsForce = at.FloatAttribute("Push-Inwards Force", 15)
        self._followOnBehaviour = at.StringAttribute("Follow-On Behaviour", self._defaultBehaviourID)

#####################
    def populateUiLayout(self):
        uib.MakeLocationField(self._wallLipGoal)
        basePyramidGoalField = uib.MakeLocationField(self._basePyramidGoal)
        basePyramidGoalField.setEnable1(False)
        basePyramidGoalField.setEnable3(False)
        uib.MakeLocationField(self._finalGoal)
        
        goalChaseFrameLayout = uib.MakeFrameLayout("Goal-Chase Stage")
        uib.MakeCheckboxGroup(self._useInfectionSpread)
        uib.MakeSliderGroup(self._incubationPeriod)
        uib.MakeRandomizerGroup(self._incubationPeriod_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._goalChaseSpeed)
        uib.MakeRandomizerGroup(self._goalChaseSpeed_Random)
        uib.SetAsChildLayout(goalChaseFrameLayout)
        
        pyramidJoinFrameLayout = uib.MakeFrameLayout("Pyramid-Join Stage")
        uib.MakeSliderGroup(self._pyramidJoinAtDistance)
        uib.MakeRandomizerGroup(self._pyramidJoinAtDistance_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._pyramidJumpOnDistance)
        uib.MakeRandomizerGroup(self._pyramidJumpOnDistance_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._pyramidJumpOnProbability)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._pyramidPushUpwardsForce)
        uib.MakeSliderGroup(self._pyramidPushInwardsForce)
        uib.SetAsChildLayout(pyramidJoinFrameLayout)

        finalStageFrameLayout = uib.MakeFrameLayout("Final Stage")
        cmdTuple = uib.MakeStringOptionsField(self._followOnBehaviour, self._followOnBehaviourIDs)
        self._followOnBehaviourMenu, self._followOnBehaviourMenuItems = cmdTuple
        uib.SetAsChildLayout(finalStageFrameLayout)
        
#####################
    def _createDataBlobForAgent(self, agent):
        return GoalDrivenDataBlob(agent)
    
#####################   
    def onBehaviourListUpdated(self, behaviourIDsList, defaultBehaviourId):
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
        return self._behaviourIncubationPeriod_Random.getRandomizedValueForIntegerId(dataBlob.agentId)
     
    def _getGoalChaseSpeedForBlob(self, dataBlob):
        return self._goalChaseSpeed_Random.getRandomizedValueForIntegerId(dataBlob.agentId)
    
    def _getPyramidJoinAtDistanceForBlob(self, dataBlob):
        return self._pyramidJoinAtDistance_Random.getRandomizedValueForIntegerId(dataBlob.agentId)
   
    def _getPyramidJumpOnDistanceForBlob(self, dataBlob):
        return self._pyramidJumpOnDistance_Random.getRandomizedValueForIntegerId(dataBlob.agentId)

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