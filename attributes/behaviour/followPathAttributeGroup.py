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


import pyswarm.utils.sceneInterface as scene
import pyswarm.ui.uiBuilder as uib
import pyswarm.attributes.attributeGroupObject as ago
import pyswarm.attributes.attributeTypes as at



###########################################
class FollowPathDataBlob(ago._DataBlobBaseObject):
    
    def __init__(self, agent):
        super(FollowPathDataBlob, self).__init__(agent)
        
        self.pathDevianceThreshold = 0.0
        self.goalDistanceThreshold = 0.0
        
#####################
    def __str__(self):
        return ("<FOLLOW-PATH BHVR: pathDev=%.2f, goalDist=%.2f>" % 
                (self.pathDevianceThreshold, self.goalDistanceThreshold))
        
# END OF CLASS - FollowPathDataBlob
###########################################



###########################################
class FollowPathAttributeGroup(ago.AttributeGroupObject, ago._FollowOnBehaviourAttributeInterface):

    @classmethod
    def BehaviourTypeName(cls):
        return "Follow Path Behaviour"

#####################    
    def __init__(self, behaviourId, pathCurve=None):
        super(FollowPathAttributeGroup, self).__init__(behaviourId)
        
        self._pathCurve = at.MayaObjectAttribute("Path Curve", pathCurve)
        if(pathCurve is None):
            self._pathCurve.objectType = scene.CurvePymelType()
        self._pathDevianceThreshold = at.FloatAttribute("Path Deviance Threshold", 3.0, self)
        self._pathDevianceThreshold_Random = at.RandomizeController(self._pathDevianceThreshold)
        self._goalDistanceThreshold = at.FloatAttribute("Goal Distance Threshold", 1.0, self)
        self._goalDistanceThreshold_Random = at.RandomizeController(self._goalDistanceThreshold)
        self._pathInfluenceMagnitude = at.FloatAttribute("Path Influence Magnitude", 0.75, minimumValue=0.0, maximumValue=1.0)
        self._startingTaper = at.FloatAttribute("Starting Taper", 0.5)
        self._endingTaper = at.FloatAttribute("Ending Taper", 2.0)
    
#####################
    def populateUiLayout(self):
        uib.MakeObjectSelectorField(self._pathCurve, annotation=self._getPathCurve.__doc__)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._pathDevianceThreshold, annotation=self._getPathDevianceThresholdForBlob.__doc__)
        uib.MakeRandomizerFields(self._pathDevianceThreshold_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._goalDistanceThreshold, annotation=self._getGoalDistanceThresholdForBlob.__doc__)
        uib.MakeRandomizerFields(self._goalDistanceThreshold_Random)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._pathInfluenceMagnitude, annotation=self._getPathInfluenceMagnitude.__doc__)
        uib.MakeSeparator()
        uib.MakeSliderGroup(self._startingTaper, annotation=self._getTaperStart.__doc__)
        uib.MakeSliderGroup(self._endingTaper, annotation=self._getTaperEnd.__doc__)
        uib.MakeSeparator()
        self._makeFollowOnBehaviourOptionGroup(annotation=self._getFollowOnBehaviourID.__doc__)
        
#####################
    def _createDataBlobForAgent(self, agent):
        return FollowPathDataBlob(agent)
 
#####################   
    def onBehaviourListUpdated(self, behaviourIDsList, defaultBehaviourId):
        self._updateFollowOnBehaviourOptions(behaviourIDsList, defaultBehaviourId)
    
#####################
    def _updateDataBlobWithAttribute(self, dataBlob, attribute):
        if(attribute is self._pathDevianceThreshold):
            dataBlob.pathDevianceThreshold = self._getPathDevianceThresholdForBlob(dataBlob)
        elif(attribute is self._goalDistanceThreshold):
            dataBlob.goalDistanceThreshold = self._getGoalDistanceThresholdForBlob(dataBlob)

#####################            
    def _getPathCurve(self):
        """Nurbs curve instance to provide a path along which agents will follow."""
        return self._pathCurve.value
    pathCurve = property(_getPathCurve)

#####################     
    def _getPathDevianceThresholdForBlob(self, dataBlob):
        """Maximum distance, perpendicular to the curve path, which agents will stray 
        from the curve before trying to move back towards it."""
        return self._pathDevianceThreshold_Random.valueForIntegerId(dataBlob.agentId)
     
    def _getGoalDistanceThresholdForBlob(self, dataBlob):
        """Distance from the end point of the curve (the "goal") at which agents will cease to follow the path of the curve."""
        return self._goalDistanceThreshold_Random.valueForIntegerId(dataBlob.agentId)

#####################     
    def _getPathInfluenceMagnitude(self):
        """Weighting of the path-following force in relation to that of the default behaviour (which is also applied
        to agents whilst following a curve path).
        0 == agents will continue to follow default behaviour and ignore the path.
        1 == agents will follow the path rigidly, without any deviation."""
        return self._pathDevianceThreshold.value
    pathInfluenceMagnitude = property(_getPathInfluenceMagnitude)

#####################    
    def _getTaperStart(self):
        """Determines the width of the path at the start of the curve, as a weighted multiplier of Path Deviance Threshold.
        A low value relative to the Ending Taper will \"funnel\" agents though a narrow gap at the start of the curve path."""
        return self._startingTaper.value
    taperStart = property(_getTaperStart)
    
    def _getTaperEnd(self):
        """Determines the width of the path at the end of the curve, as a weighted multiplier of Path Deviance Threshold.
        A low value in relative to the Starting Taper will \"funnel\" agents though a narrow gap at the end of the curve path."""
        return self._endingTaper.value
    taperEnd = property(_getTaperEnd)

#####################
    def _getFollowOnBehaviourID(self):
        """Follow Path is a \"finite\" behaviour, i.e. will end once agents reach their goal.
        Once agents reach the end of the curve, they will be switched over to the Follow-On behaviour."""
        return self._followOnBehaviour.value
    followOnBehaviourID = property(_getFollowOnBehaviourID)

    
# END OF CLASS
################################    