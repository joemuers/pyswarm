import attributesBaseObject as abo
import attributeTypes as at



class GoalDrivenBehaviourAttributes(abo.AttributesBaseObject):
    
    def __init__(self):
        super(GoalDrivenBehaviourAttributes, self).__init__()
        
        self._goalBehaviourIncubationPeriod = at.IntAttribute("goalBehaviourIncubationPeriod", 10, 
                                                              "goalBehaviourIncubationPeriod_Random", 0.0, self)
        self._goalChaseSpeed = at.FloatAttribute("goalChaseSpeed", 10, 
                                                 "goalChaseSpeed_Random", 0.0, self)
        self._goalTargetDistanceThreshold = at.FloatAttribute("goalTargetDistanceThreshold", 0.5)
        self._jumpOnPyramidProbability = at.FloatAttribute("jumpOnPyramidProbability", 0.1)
        self._jumpOnPyramidDistanceThreshold = at.FloatAttribute("jumpOnPyramidDistanceThreshold", 1.5, 
                                                                 "jumpOnPyramidDistanceThreshold_Random", 0.0, self)
        self._basePyramidUpwardsForce = at.FloatAttribute("basePyramidUpwardsForce", 22)
        self._basePyramidInwardsForce = at.FloatAttribute("basePyramidInwardsForce", 15)
 
#####################        
    def _sectionTitle(self):
        return "Goal-driven behaviour"

#####################
    def makeFrameLayout(self):
        mainFrame = at.MakeFrameLayout(self._sectionTitle())
        
        goalFrame = at.MakeFrameLayout("chase stage attributes")
        behaviourFrame = self._goalBehaviourIncubationPeriod.makeFrameLayout("Incubation period", "frames", 0)
        at.SetAsChildToPrevious(behaviourFrame)
        chaseSpeedFrame = self._goalChaseSpeed.makeFrameLayout("Chase speed", "magnitude", 0)
        at.SetAsChildToPrevious(chaseSpeedFrame)
        targetDistanceFrame = self._goalTargetDistanceThreshold.makeFrameLayout("Goal target distance", "distance", 0) #TODO - seperate form??
        at.SetAsChildToPrevious(targetDistanceFrame, goalFrame)
        
        pyramidFrame = at.MakeFrameLayout("Join pyramid")
        jumpProbabilityRow = self._jumpOnPyramidProbability.makeRowLayout("jump probability", 0, 1)
        at.SetAsChildToPrevious(jumpProbabilityRow)
        jumpDistanceFrame = self._jumpOnPyramidDistanceThreshold.makeFrameLayout("From distance", "distance", 0)
        at.SetAsChildToPrevious(jumpDistanceFrame, pyramidFrame)
        
        baseVectorsFrame = at.MakeFrameLayout("Base pyramid pressure")
        upwardsVec = self._basePyramidUpwardsForce.makeRowLayout("upwards force", 0)
        at.SetAsChildToPrevious(upwardsVec)
        horizontalVec = self._basePyramidInwardsForce.makeRowLayout("horizontal force", 0)
        at.SetAsChildToPrevious(horizontalVec, baseVectorsFrame)
        
        return mainFrame

#####################     
    def _getGoalTargetDistanceThreshold(self):
        return self._goalTargetDistanceThreshold.value
    def _setGoalTargetDistanceThreshold(self, value):
        self._goalTargetDistanceThreshold.value = value
    goalTargetDistanceThreshold = property(_getGoalTargetDistanceThreshold, _setGoalTargetDistanceThreshold)

#####################     
    def _getJumpOnPyramidProbability(self):
        return self._jumpOnPyramidProbability.value
    def _setJumpOnPyramidProbability(self, value):
        newValue = float(value)
        if(newValue < 0 or 1 < newValue):
            raise ValueError("Probability value => must be between 0 and 1 (got %s)" % value)
        else:
            self._jumpOnPyramidProbability.value = newValue
    jumpOnPyramidProbability = property(_getJumpOnPyramidProbability, _setJumpOnPyramidProbability)

#####################     
    def _getJumpOnPyramidDistanceThreshold(self):
        return self._jumpOnPyramidDistanceThreshold.value
    def _setJumpOnPyramidDistanceThreshold(self, value):
        self._jumpOnPyramidDistanceThreshold.value = value
    jumpOnPyramidDistanceThreshold = property(_getJumpOnPyramidDistanceThreshold, _setJumpOnPyramidDistanceThreshold)

#####################     
    def _getJumpOnPyramidDistanceThreshold_Random(self):
        return self._jumpOnPyramidDistanceThreshold.randomizerValue
    def _setJumpOnPyramidDistanceThreshold_Random(self, value):
        self._jumpOnPyramidDistanceThreshold.randomizerValue = value
    jumpOnPyramidDistanceThreshold_Random = property(_getJumpOnPyramidDistanceThreshold_Random, _setJumpOnPyramidDistanceThreshold_Random)

#####################     
    def _getBasePyramidUpwardsForce(self):
        return self._basePyramidUpwardsForce.value
    def _setBasePyramidUpwardsForce(self, value):
        self._basePyramidUpwardsForce.value = value
    basePyramidUpwardsForce = property(_getBasePyramidUpwardsForce, _setBasePyramidUpwardsForce)

#####################     
    def _getBasePyramidInwardsForce(self):
        return self._basePyramidInwardsForce.value
    def _setBasePyramidInwardsForce(self, value):
        self._basePyramidInwardsForce.value = value
    basePyramidInwardsForce = property(_getBasePyramidInwardsForce, _setBasePyramidInwardsForce)

#####################     
    def _getGoalChaseSpeed(self):
        return self._goalChaseSpeed.value
    def _setGoalChaseSpeed(self, value):
        self._goalChaseSpeed.value = value
    goalChaseSpeed = property(_getGoalChaseSpeed, _setGoalChaseSpeed)

#####################     
    def _getGoalChaseSpeed_Random(self):
        return self._goalChaseSpeed.randomizerValue
    def _setGoalChaseSpeed_Random(self, value):
        self._goalChaseSpeed.randomizerValue = value
    goalChaseSpeed_Random = property(_getGoalChaseSpeed_Random, _setGoalChaseSpeed_Random)

#####################     
    def _getGoalBehaviourIncubationPeriod(self):
        return self._goalBehaviourIncubationPeriod.value
    def _setGoalBehaviourIncubationPeriod(self, value):
        self._goalBehaviourIncubationPeriod.value = value
    goalBehaviourIncubationPeriod = property(_getGoalBehaviourIncubationPeriod, _setGoalBehaviourIncubationPeriod)

#####################     
    def _getGoalBehaviourIncubationPeriod_Random(self):
        return self._goalBehaviourIncubationPeriod.randomizerValue
    def _setGoalBehaviourIncubationPeriod_Random(self, value):
        self._goalBehaviourIncubationPeriod.randomizerValue = value
    goalBehaviourIncubationPeriod_Random = property(_getGoalBehaviourIncubationPeriod_Random, _setGoalBehaviourIncubationPeriod_Random)
    
    
# END OF CLASS
##################################    