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


import os.path as osp

import pyswarm.utils.general as util
import pyswarm.resources

import pyswarm.utils.packageInfo as pi



_UserProvidedFilePath_ = None
_SAVE_FILE_EXTENSION_ = ".pkl"
_DEFAULT_VALUES_FILENAME_ = "attributeValueDefaults.ini"

_BADGE_IMAGE_ = "swarmTitle_square.jpg" # 
_BADGE_IMAGE_PIXEL_WIDTH_ = 150         # IMPORTANT - update the pixel width if you change the image.



#############################
def SetSaveLocation(filePath):
    global _UserProvidedFilePath_
    
    if(_UserProvidedFilePath_ != filePath):
        _UserProvidedFilePath_ = filePath
        
        util.LogInfo("Set save-file path to: %s" % (_UserProvidedFilePath_ 
                                                    if(HaveUserProvidedSavePath()) else
                                                    "Auto-generated."))

####
def HaveUserProvidedSavePath():
    if(_UserProvidedFilePath_ is not None and _UserProvidedFilePath_):
        return True
    else:
        return False

####
def SaveFileLocation():
    if(HaveUserProvidedSavePath()):
        filePath = _UserProvidedFilePath_
    else:
        filePath = osp.join(SaveFolderLocation(), 
                            ("%s_%s%s" % (util.GetCurrentSceneName(), pi.PackageName(), SaveFileExtension())))
        
    return osp.normpath(filePath)

#####
def _AutoGeneratedSavePath():
    folderPath = util.GetProjectRootDirectory()
    if(folderPath is not None and folderPath):
        folderPath = osp.join(folderPath, "scripts" + osp.sep)
        if(osp.exists(folderPath)):
            return folderPath
    else:
        raise RuntimeError("Could not find \"scripts\" folder in your Maya project database. ")
                
#####
def SaveFolderLocation():
    try:
        if(HaveUserProvidedSavePath()):
            folderPath = osp.split(_UserProvidedFilePath_)[0]
            if(folderPath is not None and folderPath):
                return folderPath
            else:
                raise RuntimeError("\"%s\" is not a valid filepath. " % _UserProvidedFilePath_)
        else:
            return _AutoGeneratedSavePath()
    except RuntimeError as e:
        util.LogWarning(e + ("Using path:" % util.GetProjectWorkingDirectory()))
    
    return util.GetProjectWorkingDirectory()

#####
def SaveFileExtension():
    return _SAVE_FILE_EXTENSION_

##########################################
def DefaultAttributeValuesLocation():
    filePath = osp.dirname(pyswarm.resources.__file__)
    filePath = osp.normpath(osp.join(filePath, _DEFAULT_VALUES_FILENAME_))
    
    if(not osp.exists(filePath)):
        raise IOError("Could not find defaults file at: %s" % filePath)
    else:
        return filePath
    
##########################################
def LogoImageLocation():
    filePath = osp.dirname(pyswarm.resources.__file__)
    filePath = osp.normpath(osp.join(filePath, _BADGE_IMAGE_))

    if(not osp.exists(filePath)):
        raise IOError("Could not find image at: %s" % filePath)
    else:
        return filePath

##########################################
def LogoImagePixelWidth():
    return _BADGE_IMAGE_PIXEL_WIDTH_


# END OF MODULE
#############################################