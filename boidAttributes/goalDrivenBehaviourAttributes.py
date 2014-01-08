import attributesBaseObject as abo
import attributeTypes as at
import boidTools.uiBuilder as uib



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
        
        # TODO - initiate variable value in behaviour class
#         (GoalDrivenDataBlob.normal if useInfectionSpread 
#                               else GoalDrivenDataBlob.goalChase)
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
    
    def __init__(self):
        super(GoalDrivenBehaviourAttributes, self).__init__()
        
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

#####################        
    def sectionTitle(self):
        return "Goal-Driven Behaviour"

#####################
    def populateUiLayout(self):
        
        goalChaseFrameLayout = uib.MakeFrameLayout("Goal-Chase Stage")
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
        
#####################
    def _createDataBlobForAgent(self, agent):
        return GoalDrivenDataBlob(agent)
    
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
    def _getPyramidJumpOnProbability(self):
        return self._pyramidJumpOnProbability.value
    pyramidJumpOnProbability = property(_getPyramidJumpOnProbability)

#####################     
    def _getBasePyramidPushUpwardsForce(self):
        return self._basePyramidUpwardsForce.value
    basePyramidPushUpwardsForce = property(_getBasePyramidPushUpwardsForce)

#####################     
    def _getBasePyramidPushInwardsForce(self):
        return self._basePyramidInwardsForce.value
    basePyramidPushInwardsForce = property(_getBasePyramidPushInwardsForce)
    
# END OF CLASS
##################################    