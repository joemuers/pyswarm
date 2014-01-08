import boidAttributes.attributeTypes as at

import pymel.core as pm
import sys


__LEFT_COLUMN_WIDTH__ = 190
__MIDDLE_COLUMN_WIDTH__ = 75
__RIGHT_COLUMN_WIDTH__ = 140



##########################
def WindowExists(windowReference):
    return(windowReference is not None and pm.window(windowReference, exists=True))

def MakeWindow(title):
    return pm.window(title, menuBar=True)

####################



#################################################
#########             MENUS         #############
#################################################

def MakeMenu(menuTitle):
    return pm.menu(menuTitle)
    
#####################    
def MakeMenuItem(itemLabel, onSelectCommand, annotation=None):
    newMenuItem = pm.menuItem(label=itemLabel, command=onSelectCommand)
    if(annotation is not None):
        newMenuItem.setAnnotation(annotation)
    
    return newMenuItem

#####################
def MakeMenuSeparator():
    return pm.menuItem(divider=True)

#########################



#################################################
#########             LAYOUTS       #############
#################################################

def SetAsChildLayout(*childLayouts):
    for _ in childLayouts:
        pm.setParent("..")

##################### 
def MakeScrollLayout(title):
    if(title is not None):
        return pm.scrollLayout(title, childResizable=True)
    else:
        return pm.scrollLayout(childResizable=True)

#####################
def MakeBorderingLayout():
    return pm.frameLayout(labelVisible=False, borderStyle='etchedIn', marginWidth=2, marginHeight=3)

#####################
def MakeFrameLayout(title, makeCollapsable=True):
    frame = pm.frameLayout(title, borderStyle='out')
    if(makeCollapsable):
        frame.setCollapsable(True)
    return frame

#####################
def MakeTabLayout(height):
    tabs = pm.tabLayout(height=height)
    return tabs

##################### 
def MakeColumnLayout():
    return pm.columnLayout(adjustableColumn=True)

#####################    
def MakeRowLayout(numColumns, spaced=False):
    if(spaced):
        return pm.rowLayout(numberOfColumns=numColumns)
    elif(numColumns == 3):
        return pm.rowLayout(numberOfColumns=3, 
                            columnWidth3=(__LEFT_COLUMN_WIDTH__, __MIDDLE_COLUMN_WIDTH__, __RIGHT_COLUMN_WIDTH__), 
                            columnAlign=(1, 'right'), 
                            columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 10)], 
                            adjustableColumn=3)
    elif(numColumns == 2):
        return pm.rowLayout(numberOfColumns=2, 
                            columnWidth2=(__LEFT_COLUMN_WIDTH__, __MIDDLE_COLUMN_WIDTH__), 
                            columnAlign=(1, 'right'), 
                            columnAttach=[(1, 'both', 0), (2, 'both', 0)])
    elif(numColumns == 1):
        return pm.rowLayout(numberOfColumns=1, 
                            columnAlign=(1, 'left'), 
                            columnAttach=(1, 'left', __LEFT_COLUMN_WIDTH__),
                            adjustableColumn=1)
    else:
        raise TypeError  
    
#########################
def MakeFormLayout():
    return pm.formLayout()

#########################
def DistributeControlsInFormLayout(formLayout, controls):
    formLayout.attachForm(controls[0], 'left', 2)

    numControls = len(controls)   
    stepSize = formLayout.getNumberOfDivisions() / numControls
    position = stepSize
    
    for i in range(numControls - 1):
        formLayout.attachPosition(controls[i], 'right', 1, position)
        formLayout.attachPosition(controls[i + 1], 'left', 1, position)
        position += stepSize
        
    formLayout.attachForm(controls[-1], 'right', 2)
        
#########################  
def MakeButtonStrip(textCommandTupleList):
    formLayout = MakeFormLayout()
    controls = []
    
    for buttonTuple in textCommandTupleList:
        text = buttonTuple[0]
        command = buttonTuple[1]
        annotation = buttonTuple[2] if(len(buttonTuple) > 2) else None

        button = MakeButton(text, command, annotation)
        controls.append(button)
        
    DistributeControlsInFormLayout(formLayout, controls)
    SetAsChildLayout(formLayout)
    
    return formLayout
        
#########################



#################################################
#########        INPUT FIELDS       #############
#################################################   
   
def MakeSliderGroup(attribute, annotation=None):
    isFloatField = None
    groupCreationMethod = None
    
    if(issubclass(type(attribute), at.FloatAttribute)):
        isFloatField = True
        groupCreationMethod = pm.floatSliderGrp
    elif(type(attribute) == at.IntAttribute):
        isFloatField = False
        groupCreationMethod = pm.intSliderGrp
    else:
        raise TypeError("Illegal attribute type for standard input field")
    
    
    kwargs = { "label" : attribute.attributeLabel, 
               "value": attribute.value, 
               "columnAlign" : (1, "right"),
               "columnAttach" : [(1, 'both', 0), (2, 'both', 0), (3, 'both', 10)], 
               "field" : True,
               "columnWidth3" : (__LEFT_COLUMN_WIDTH__, __MIDDLE_COLUMN_WIDTH__, __RIGHT_COLUMN_WIDTH__),
               "adjustableColumn" : 3,
               "minValue" : attribute.minimumValue if(attribute.minimumValue is not None) else 0
               }

    if(isFloatField):
        kwargs["precision"] = 3

    if(attribute.maximumValue is not None):
        kwargs["maxValue"] = attribute.maximumValue
    else: # workaround for Pymel sliderGroup bug whereby 'fieldMaxValue' defaults to 100 if nothing specified
        kwargs["maxValue"] = attribute.value * 2
        kwargs["fieldMaxValue"] = float("inf") if(isFloatField) else sys.maxsize
    
    
    inputGroup = groupCreationMethod(**kwargs)
    inputGroup.changeCommand(lambda *args : attribute._setValue(inputGroup.getValue()))
    attribute.updateUiCommand = inputGroup.setValue
    attribute.uiEnableMethod = inputGroup.setEnable
    
    if(annotation is not None):
        inputGroup.setAnnotation(annotation)
    
    return inputGroup

#####################
def MakeFieldGroup(attribute, annotation=None):
    isFloatField = None
    groupCreationMethod = None
    
    if(issubclass(type(attribute), at.FloatAttribute)):
        isFloatField = True
        groupCreationMethod = pm.floatFieldGrp
    elif(type(attribute) == at.IntAttribute):
        isFloatField = False
        groupCreationMethod = pm.intFieldGrp
    else:
        raise TypeError("Illegal attribute type for standard input field")
    
    kwargs = { "label" : attribute.attributeLabel, 
               "value1": attribute.value, 
               "columnAlign" : (1, "right"),
               "columnWidth2" : (__LEFT_COLUMN_WIDTH__, __MIDDLE_COLUMN_WIDTH__)
               }
    # and another shitty Pymel bug - fieldGrps cannot have min/max values!!!
    if(isFloatField):
        kwargs["precision"] = 3

    inputGroup = groupCreationMethod(**kwargs)
    inputGroup.changeCommand(lambda *args : attribute._setValue(inputGroup.getValue1()))
    attribute.updateUiCommand = inputGroup.setValue1
    attribute.uiEnableMethod = inputGroup.setEnable
    
    if(annotation is not None):
        inputGroup.setAnnotation(annotation)
    
    return inputGroup

#####################
def MakeRandomizerGroup(randomizerAttribute, annotation=None):
    inputGroup = MakeSliderGroup(randomizerAttribute, annotation)
    
    return inputGroup
    
#####################
def MakeCheckboxGroup(attribute, extraLabel, annotation=None):
    if(type(attribute) != at.BoolAttribute):
        raise TypeError("Attempt to make checkbox group from non-boolean attribute.")
    
    rowLayout = MakeRowLayout(2 if(extraLabel is not None) else 1)
    
    boxLabel = attribute.attributeLabel
    if(extraLabel is not None):
        MakeText(boxLabel + ':', annotation)
        boxLabel = extraLabel
    
    checkbox = pm.checkBox(label=boxLabel, value=attribute.value)
    checkbox.changeCommand(lambda *args: attribute._setValue(checkbox.getValue()))
    attribute.updateUiCommand = checkbox.setValue
    attribute.uiEnableMethod = checkbox.setEnable
    if(annotation is not None):
        checkbox.setAnnotation(annotation)
    
    SetAsChildLayout(rowLayout)
    
    return rowLayout

#####################
def MakeRandomizeOptionsMenu(randomizerController, annotation=None):
    if(type(randomizerController) != at.RandomizeController):
        raise TypeError("Attempt to make randomizer menu from non-randomizerController attribute.")
    
    rowLayout = MakeRowLayout(2)
    
    MakeText(randomizerController.attributeLabel, annotation)
    
    optionMenu = pm.optionMenu()
    try:
        for i in xrange(sys.maxint):
            pm.menuItem(label=at.RandomizeController.StringForOption(i))
    except Exception:
        pass
    
    optionMenu.changeCommand(lambda *args: randomizerController._setValue(optionMenu.getValue()))
    randomizerController.updateUiCommand = optionMenu.setValue
    randomizerController.uiEnableMethod = optionMenu.setEnable
    if(annotation is not None):
        optionMenu.setAnnotation(annotation)
    
    SetAsChildLayout(rowLayout)
    
    return rowLayout

#####################
def MakeRandomizerFields(randomizerController, annotation=None):
    if(annotation is None):
        annotation = ("Input modes:\n\
Off = value taken directly from %s.\n\
By Agent ID = value offset by constant amount - which is randomized per-agent.\n\
Pure Random = value offset by random amount every time it is queried." 
% randomizerController._parentAttribute.attributeLabel)

    optionsMenuRowLayout = MakeRandomizeOptionsMenu(randomizerController, annotation)
    randomizerSliderGroup = MakeRandomizerGroup(randomizerController._randomizerAttribute, 
                                                ("Randomness multiplier for %s" % randomizerController.attributeLabel))
    randomizerController._updateInputUiComponents()
    
    return (optionsMenuRowLayout, randomizerSliderGroup)
    
#####################   


#################################################
#########    MISCELLANEOUS ITEMS    #############
#################################################   

def MakeText(text, annotation=None):
    text = pm.text(text)
    if(annotation is not None):
        text.setAnnotation(annotation)
        
    return text

#####################
def MakeButton(text, callback, annotation=None):
    button = pm.button(label=text, command=callback)
    if(annotation is not None):
        button.setAnnotation(annotation)
        
    return button
    
#####################
def MakeSeparator():
    return pm.separator(style='in')

#####################
def GetUserConfirmation(title, message):
    return pm.confirmBox(title, message, "OK", "Cancel")


####################################################################