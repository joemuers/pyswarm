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


"""
Colours used by agent objects for the 'debugColour' property.
Tuples are RGB values.
"""



#################################################
#######    BEHAVIOUR DEBUG COLOURS   ############
#################################################


DefaultColour = (0, 0, 0)

##########################
Normal_NotTouchingGround = (0.2, 0.2, 0.2)

Normal_IsCollided = (1, 0, 0)

Normal_IsCrowded = (0.65, 0,  0)

Normal_HasNeighbours = (0, 0.8, 0)

Normal_NoNeighbours = (0, 0, 1)

##########################
WorldWarZ_IsLeader = (1, 1, 1)

WorldWarZ_ChasingGoal = (1, 1, 0)

def WorldWarZ_InBasePyramid(agent):
    return agent.stickinessScale / 2

WorldWarZ_OverTheWall = (0, 0.3, 0)

WorldWarZ_ReachedGoal = (0, 0.7, 0)

###########################
FollowPath_OnPath = (0.5, 0.5, 0)

###########################



#################################################
#######    STATUS TEXTFIELD COLOURS   ###########
#################################################


def _GetDefaultTextfieldBackground(brighten=0.0):
    import pymel.core as pm
    win = pm.window()
    row = pm.rowLayout()
    txtField = pm.textField()
    backgroundColour = tuple(txtField.getBackgroundColor())
    backgroundColour = (backgroundColour[0] + brighten, backgroundColour[1] + brighten, backgroundColour[2] + brighten)
    
    pm.deleteUI(win)
    return backgroundColour

#############################
StatusTextfieldBackground_Default = _GetDefaultTextfieldBackground(0.1)

StatusTextfieldBackground_Error = (0.8, 0, 0)



# END OF MODULE
###########################################