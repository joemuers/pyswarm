import attributesBaseObject as abo
import attributeTypes as at



class FollowPathBehaviourAttributes(abo.AttributesBaseObject):
    
    def __init__(self):
        super(FollowPathBehaviourAttributes, self).__init__()
        
        self._pathDevianceThreshold = at.FloatAttribute("pathDevianceThreshold", 3.0, 
                                                        "pathDevianceThreshold_Random", 0.0, self)
        self._endReachedDistanceThreshold = at.FloatAttribute("endReachedDistanceThreshold", 1.0, 
                                                              "endReachedDistanceThreshold_Random", 0.0, self)
        self._pathInfluenceMagnitude = at.FloatAttribute("pathInfluenceMagnitude", 2.0)

#####################         
    def _sectionTitle(self):
        return "Follow path behaviour"
    
#####################
    def makeFrameLayout(self):
        pathFrame = at.MakeFrameLayout(self._sectionTitle())
        
        pathDevianceFrame = self._pathDevianceThreshold.makeFrameLayout("Path deviance", "distance", 0)
        at.SetAsChildToPrevious(pathDevianceFrame)
        endReachedFrame = self._endReachedDistanceThreshold.makeFrameLayout("End reached threshold", "distance", 0)
        at.SetAsChildToPrevious(endReachedFrame)
        influenceMagFrame = self._pathInfluenceMagnitude.makeFrameLayout("Path influence", "magnitude", 0)
        at.SetAsChildToPrevious(influenceMagFrame)
        
        return pathFrame

#####################     
    def _getPathDevianceThreshold(self):
        return self._pathDevianceThreshold.value
    def _setPathDevianceThreshold(self, value):
        self._pathDevianceThreshold.value = value
    pathDevianceThreshold = property(_getPathDevianceThreshold, _setPathDevianceThreshold)

#####################     
    def _getPathDevianceThreshold_Random(self):
        return self._pathDevianceThreshold.randomizerValue
    def _setPathDevianceThreshold_Random(self, value):
        self._pathDevianceThreshold.randomizerValue = value
    pathDevianceThreshold_Random = property(_getPathDevianceThreshold_Random, _setPathDevianceThreshold_Random)

#####################     
    def _getEndReachedDistanceThreshold(self):
        return self._endReachedDistanceThreshold.value
    def _setEndReachedDistanceThreshold(self, value):
        self._endReachedDistanceThreshold.value = value
    endReachedDistanceThreshold = property(_getEndReachedDistanceThreshold, _setEndReachedDistanceThreshold)

#####################     
    def _getEndReachedDistanceThreshold_Random(self):
        return self._endReachedDistanceThreshold.randomizerValue
    def _setEndReachedDistanceThreshold_Random(self, value):
        self._endReachedDistanceThreshold.randomizerValue = value
    endReachedDistanceThreshold_Random = property(_getEndReachedDistanceThreshold_Random, _setEndReachedDistanceThreshold_Random)

#####################     
    def _getPathInfluenceMagnitude(self):
        return self._pathDevianceThreshold.value
    def _setPathInfluenceMagnitude(self, value):
        self._pathDevianceThreshold.value = value
    pathInfluenceMagnitude = property(_getPathInfluenceMagnitude, _setPathInfluenceMagnitude)
    
# END OF CLASS
################################    