"""Colours used by agent objects for the 'debugColour' property.
Tuples are RGB values.
"""



##########################
DefaultColour = (0, 0, 0)

##########################
Normal_NotTouchingGround = (0.2, 0.2, 0.2)

Normal_IsCollided = (1, 0, 0)

Normal_IsCrowded = (0.65, 0,  0)

Normal_HasNeighbours = (0, 0.8, 0)

Normal_NoNeighbours = (0, 0, 1)

##########################
GoalDriven_IsLeader = (1, 1, 1)

GoalDriven_ChasingGoal = (1, 1, 0)

def GoalDriven_InBasePyramid(agent):
    return agent.stickinessScale / 2

GoalDriven_OverTheWall = (0, 0.3, 0)

GoalDriven_ReachedGoal = (0, 0.7, 0)

###########################
FollowPath_OnPath = (0.5, 0.5, 0)


# END OF MODULE
###########################################