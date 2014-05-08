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


import boidAttributes.attributeTypes as at
import boidTools.util as util
import boidTools.sceneInterface as scene
import boidResources.fileLocations as fl

import pymel.core as pm
import sys



__LEFT_COLUMN_WIDTH__ = 190
__MIDDLE_COLUMN_WIDTH__ = 75
__RIGHT_COLUMN_WIDTH__ = 235
__FOURTH_COLUMN_WIDTH__ = 23

__OPTIONS_MENUS_WIDTH__ = 100
__CHECKBOX_OFFSET__ = 4



#################################################
#########           WINDOWS         #############
#################################################

def WindowExists(windowReference):
    return(windowReference is not None and pm.window(windowReference, exists=True))

#####################
def WindowIsVisible(windowReference):
    return (WindowExists(windowReference) and pm.window(windowReference, query=True, visible=True))

#####################
def MakeWindow(title, widthHeight=None):
    if(widthHeight is None):
        return pm.window(title, maximizeButton=False, resizeToFitChildren=True, menuBar=True)
    else:
        return pm.window(title, maximizeButton=False, resizeToFitChildren=True, menuBar=True, widthHeight=widthHeight)

#####################
def DestroyWindowIfNecessary(windowReference):
    if(WindowExists(windowReference)):
        pm.deleteUI(windowReference, window=True)

#############################



#################################################
#########             MENUS         #############
#################################################

def SetParentMenuLayout(parentMenuLayout):
    if(not IsCurrentMenuParent(parentMenuLayout)):
        pm.setParent(parentMenuLayout, menu=True)

#####################        
def SetAsChildMenuLayout(*childLayouts):
    for _ in childLayouts:
        pm.setParent("..", menu=True)

#####################
def IsCurrentMenuParent(menuControl):
    return (menuControl == pm.currentMenuParent())

#####################
def MakeMenu(menuTitle):
    return pm.menu(menuTitle)
    
#####################    
def MakeMenuItem(itemLabel, onSelectCommand, annotation=None):
    newMenuItem = pm.menuItem(label=itemLabel)
    
    if(onSelectCommand is not None):
        newMenuItem.setCommand(onSelectCommand)
    if(annotation is not None):
        newMenuItem.setAnnotation(annotation)
    
    return newMenuItem

#####################
def MakeMenuItemWithSubMenu(itemLabel, annotation=None):
    newMenuItem = pm.menuItem(label=itemLabel, subMenu=True)
    if(annotation is not None):
        newMenuItem.setAnnotation(annotation)
    
    return newMenuItem

#####################
def MakeMenuSubItem(itemLabel):
    return pm.menuItem(label=itemLabel)

#####################
def MakeMenuSeparator():
    return pm.menuItem(divider=True)

#########################



#################################################
#########             LAYOUTS       #############
#################################################

def SetParentLayout(parentLayout):
    if(not IsCurrentParent(parentLayout)):
        pm.setParent(parentLayout)

#####################
def SetAsChildLayout(*childLayouts):
    for _ in childLayouts:
        pm.setParent("..")

#####################        
def IsCurrentParent(control):
    return (control == pm.currentParent())

#####################
def MakeFormLayout(title=None):
    if(title is not None):
        return pm.formLayout(title)
    else:
        return pm.formLayout()

##################### 
def MakeScrollLayout(title=None):
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
def MakeTabLayout(height=None):
    if(height is not None):
        return pm.tabLayout(height=height)
    else:
        return pm.tabLayout()

##################### 
def MakeColumnLayout(title=None):
    if(title is not None):
        return pm.columnLayout(title, adjustableColumn=True)
    else:
        return pm.columnLayout(adjustableColumn=True)

#####################    
def MakeRowLayout(numColumns, 
                  leftColumnWidth=__LEFT_COLUMN_WIDTH__, 
                  middleColumnWidth=__MIDDLE_COLUMN_WIDTH__, 
                  rightColumnWidth=__RIGHT_COLUMN_WIDTH__,
                  makeAdjustable=True):
    
    if(numColumns == 4):
        layout = pm.rowLayout(numberOfColumns=4, 
                              columnWidth4=(leftColumnWidth, middleColumnWidth, 
                                            rightColumnWidth - __FOURTH_COLUMN_WIDTH__, __FOURTH_COLUMN_WIDTH__), 
                              columnAlign=(1, 'right'), 
                              columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0), (4, 'right', 10)])
        if(makeAdjustable):
            layout.adjustableColumn(3)
        
        return layout
    if(numColumns == 3):
        layout = pm.rowLayout(numberOfColumns=3, 
                              columnWidth3=(leftColumnWidth, middleColumnWidth, rightColumnWidth), 
                              columnAlign=(1, 'right'), 
                              columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        if(makeAdjustable):
            layout.adjustableColumn(3)
        
        return layout
    elif(numColumns == 2):
        layout = pm.rowLayout(numberOfColumns=2, 
                              columnWidth2=(leftColumnWidth, rightColumnWidth), 
                              columnAlign=(1, 'right'), 
                              columnAttach=[(1, 'both', 0), (2, 'both', 0)])
        if(makeAdjustable):
            layout.adjustableColumn(2)
            
        return layout
    elif(numColumns == 1):
        layout = pm.rowLayout(numberOfColumns=1, 
                              columnAlign=(1, 'left'), 
                              columnAttach=(1, 'left', leftColumnWidth + 3))
        
        if(makeAdjustable):
            layout.adjustableColumn(1)
            
        return layout
    else:
        raise ValueError  
    
#####################
def MakeTopLevelRowLayout(componentsSectionWidth):
    rowLayout = pm.rowLayout(numberOfColumns=2, 
                              adjustableColumn=1,
                              columnWidth2=(componentsSectionWidth, fl.LogoImagePixelWidth()), 
                              columnAlign=[(1, 'left'), (2, 'right')], 
                              columnAttach=[(1, 'both', 0), (2, 'right', 0)])
    
    return rowLayout

#########################
def DistributeControlsHorizontallyInFormLayout(formLayout, controls):
    formLayout.attachForm(controls[0], 'left', 2)

    numControls = len(controls)   
    stepSize = formLayout.getNumberOfDivisions() / numControls
    position = stepSize
    
    for i in range(numControls - 1):
        formLayout.attachPosition(controls[i], 'right', 1, position)
        formLayout.attachPosition(controls[i + 1], 'left', 1, position)
        position += stepSize
        
    formLayout.attachForm(controls[-1], 'right', 2)
    
def DistributeButtonedWindowInFormLayout(formLayout, windowLayout, buttonsLayout):
    map(lambda x: formLayout.attachForm(*x), [(windowLayout, 'top', 1), 
                                              (windowLayout, 'left', 1), (windowLayout, 'right', 1),
                                              (buttonsLayout, 'bottom', 1), 
                                              (buttonsLayout, 'left', 1), (buttonsLayout, 'right', 1)])
    formLayout.attachControl(windowLayout, 'bottom', 1, buttonsLayout)
    formLayout.attachNone(buttonsLayout, 'top')
        
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
               "minValue" : util.InitVal(attribute.minimumValue, 0)
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
    
    def _updateInputGroup(inputGroup, attribute):
        inputGroup.setValue(attribute.value)
        if(attribute.minimumValue is not None):
            inputGroup.setMinValue(attribute.minimumValue)
        if(attribute.maximumValue is not None):
            inputGroup.setMaxValue(attribute.maximumValue)
            
    attribute.updateUiCommand = (lambda value: _updateInputGroup(inputGroup, attribute))
    attribute.uiEnableMethod = inputGroup.setEnable
    
    if(annotation is not None):
        inputGroup.setAnnotation(annotation)
    
    return inputGroup

#####################
def MakeFieldGroup(attribute, annotation=None, 
                   leftColumnWidth=__LEFT_COLUMN_WIDTH__, 
                   rightColumnWidth=__MIDDLE_COLUMN_WIDTH__):
    isFloatField = None
    groupCreationMethod = None
    
    if(issubclass(type(attribute), at.FloatAttribute)):
        isFloatField = True
        groupCreationMethod = pm.floatFieldGrp
    elif(type(attribute) == at.IntAttribute):
        isFloatField = False
        groupCreationMethod = pm.intFieldGrp
    else:
        raise TypeError("Illegal attribute type for standard input field. Got %s of type %s" % (attribute, type(attribute)))
    
    kwargs = { "label" : attribute.attributeLabel, 
               "value1": attribute.value, 
               "columnAlign" : (1, "right"),
               "columnWidth2" : (leftColumnWidth, rightColumnWidth)
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
    
    
def MakeCheckboxStandalone(boxLabel, initialValue, extraLabel=None, changeCommand=None, 
                           leftColumnWidth=__LEFT_COLUMN_WIDTH__, annotation=None, switchLabels=False):
    rowLayout = MakeRowLayout(2 if(extraLabel is not None) else 1, 
                              leftColumnWidth=leftColumnWidth + __CHECKBOX_OFFSET__, 
                              rightColumnWidth=__MIDDLE_COLUMN_WIDTH__ + __RIGHT_COLUMN_WIDTH__)
    
    if(extraLabel is not None):
        if(switchLabels) : boxLabel, extraLabel = extraLabel, boxLabel
        if(boxLabel): boxLabel += ':'
        MakeText(boxLabel, annotation)
        boxLabel = extraLabel
    
    checkbox = pm.checkBox(label=boxLabel, value=initialValue)
    if(changeCommand is not None):
        checkbox.changeCommand(changeCommand)
    if(annotation is not None):
        checkbox.setAnnotation(annotation)
    
    SetAsChildLayout(rowLayout)
    
    return (rowLayout, checkbox)
    
#####################
def MakeCheckboxGroup(attribute, extraLabel=None, annotation=None, leftColumnWidth=__LEFT_COLUMN_WIDTH__, switchLabels=False):
    if(type(attribute) != at.BoolAttribute):
        raise TypeError("Attempt to make checkbox group from non-boolean attribute.")
    
    rowLayout = MakeRowLayout(2 if(extraLabel is not None) else 1, 
                              leftColumnWidth=leftColumnWidth + __CHECKBOX_OFFSET__, 
                              rightColumnWidth=__MIDDLE_COLUMN_WIDTH__ + __RIGHT_COLUMN_WIDTH__)
    
    boxLabel = attribute.attributeLabel
    if(extraLabel is not None):
        if(switchLabels) : boxLabel, extraLabel = extraLabel, boxLabel
        if(boxLabel): boxLabel += ':'
        MakeText(boxLabel, annotation)
        boxLabel = extraLabel
    
    checkbox = pm.checkBox(label=boxLabel, value=attribute.value)
    
    try: # change in Pymel API from Maya 2013 to 2015: checkBox changeCommand -> setChangeCommand
        checkbox.changeCommand(lambda *args: attribute._setValue(checkbox.getValue()))
    except:
        checkbox.setChangeCommand(lambda *args: attribute._setValue(checkbox.getValue()))
        
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
    
    rowLayout = MakeRowLayout(2, rightColumnWidth=__OPTIONS_MENUS_WIDTH__, makeAdjustable=False)
    
    text = MakeText(randomizerController.attributeLabel, annotation)
    
    optionMenu = pm.optionMenu()
    try:
        for i in xrange(sys.maxint):
            pm.menuItem(label=at.RandomizeController.StringForOption(i))
    except Exception:
        pass
    
    optionMenu.changeCommand(lambda *args: randomizerController._setValue(optionMenu.getValue()))
    randomizerController.updateUiCommand = optionMenu.setValue
    randomizerController.uiEnableMethod = rowLayout.setEnable
    if(annotation is not None):
        optionMenu.setAnnotation(annotation)
    
    SetAsChildLayout(rowLayout)
    
    return rowLayout

#####################
def MakeRandomizerFields(randomizerController, annotation=None):
    if(annotation is None):
        annotation = ("Input modes:\n\
Off = value taken directly from %s.\n\
By Agent ID = value offset by constant amount (same across all attributes) - which is randomized per-agent.\n\
Pure Random = value offset by constant amount, randomized per-agent *and* per-attribute." 
% randomizerController._parentAttribute.attributeLabel)

    optionsMenuRowLayout = MakeRandomizeOptionsMenu(randomizerController, annotation)
    randomizerSliderGroup = MakeRandomizerGroup(randomizerController._randomizerAttribute, 
                                                ("Randomness multiplier for %s" % randomizerController.attributeLabel))
    randomizerController._updateInputUiComponents()
    
    return (optionsMenuRowLayout, randomizerSliderGroup)
    
#########################
def MakeStringOptionsField(stringAttribute, optionsListStrings, annotation=None):
    if(not isinstance(stringAttribute, at.StringAttribute)):
        raise TypeError("Attempted to make string options (expected:%s, got:%s)" % 
                        (at.StringAttribute, type(stringAttribute)))
    elif(stringAttribute.value not in optionsListStrings):
        raise ValueError("Initial value %s is not in options list." % stringAttribute.value)
    
    rowLayout = MakeRowLayout(2, rightColumnWidth=__OPTIONS_MENUS_WIDTH__ + 45, makeAdjustable=False)
    
    MakeText(stringAttribute.attributeLabel, annotation)
    
    optionMenu = pm.optionMenu()
    menuItemsList = []
    for option in optionsListStrings:
        menuItemsList.append(pm.menuItem(label=option))
    optionMenu.setValue(stringAttribute.value)
    
    optionMenu.changeCommand(lambda *args: stringAttribute._setValue(optionMenu.getValue()))
    stringAttribute.updateUiCommand = optionMenu.setValue
    stringAttribute.uiEnableMethod = optionMenu.setEnable
    if(annotation is not None):
        optionMenu.setAnnotation(annotation)
    
    SetAsChildLayout(rowLayout)
    
    return (optionMenu, menuItemsList)
    
#########################
def MakeObjectSelectorField(objectAttribute, annotation=None):
    if(not isinstance(objectAttribute, at.MayaObjectAttribute)):
        raise TypeError("Attempted to make object selector (expected:%s, got:%s)" % 
                        (at.MayaObjectAttribute, type(objectAttribute)))
     
    rowLayout = MakeRowLayout(2)
     
    MakeText(objectAttribute.attributeLabel, annotation)
    
    nameField = pm.textFieldButtonGrp(editable=False, buttonLabel="...", 
                                      adjustableColumn=1, columnWidth2=(150, 50))
    if(annotation is not None):
        nameField.setAnnotation(annotation)
        
    objectAttribute.updateUiCommand = (lambda val: nameField.setText(val.name() if(val is not None) else "<None>"))
    objectAttribute._updateInputUiComponents()
    nameField.buttonCommand(lambda *args: _MakeObjectSelectionList(objectAttribute)) 

    SetAsChildLayout(rowLayout)
    
    return rowLayout

#########################
def _MakeObjectSelectionList(objectAttribute):
    objectAttribute._updateInputUiComponents()
    
    allowNone = objectAttribute.allowNoneType
    
    objectType = objectAttribute.objectType
    objectList = [None] if(allowNone) else []
    objectNamesList = ["<None>"] if(allowNone) else []
    
    objectList.extend(scene.GetObjectsInSceneOfType(objectAttribute.objectType))
    objectNamesList.extend(map(lambda obj: obj.name(), objectList[1:] if(allowNone) else objectList))
    
    windowHandle = ("Select %s" % objectType.__name__)
    DestroyWindowIfNecessary(windowHandle)

    window = pm.window(windowHandle)
    formLayout = MakeFormLayout()
    
    menuPaneLayout = pm.paneLayout()
    
    def _onObjectSelect(objectAttribute, objectList, objectNamesList, objectMenu):
        index = objectNamesList.index(objectMenu.getSelectItem()[0])
        objectAttribute.value = objectList[index]
    
    objectMenu = pm.iconTextScrollList(allowMultiSelection=False, append=objectNamesList)
    if(objectAttribute.getRawAttribute() in objectList):
        objectMenu.setSelectItem(objectNamesList[objectList.index(objectAttribute.getRawAttribute())])
    objectMenu.selectCommand(lambda *args: _onObjectSelect(objectAttribute, objectList, objectNamesList, objectMenu))
    SetAsChildLayout(menuPaneLayout)
    
    buttonLayout = MakeButtonStrip( (("Close", lambda *args: DestroyWindowIfNecessary(window)), ) )[0]
    SetAsChildLayout(buttonLayout)
    
    DistributeButtonedWindowInFormLayout(formLayout, menuPaneLayout, buttonLayout)
    
    window.show()
    
#####################   
def MakeLocationField(locationAttribute, withButton=False, leftColumnWidth=__LEFT_COLUMN_WIDTH__, annotation=None):
    if(not isinstance(locationAttribute, at.LocationAttribute)):
        raise TypeError("Attempt to make location field with wrong type (expected:%s, got: %s)" % 
                        (at.LocationAttribute, type(locationAttribute)))
    
    if(not withButton):
        rowLayout = MakeRowLayout(2, leftColumnWidth=leftColumnWidth, 
                                  rightColumnWidth=__MIDDLE_COLUMN_WIDTH__ + __RIGHT_COLUMN_WIDTH__)
    else:
        rowLayout = MakeRowLayout(3, leftColumnWidth=leftColumnWidth, middleColumnWidth=__RIGHT_COLUMN_WIDTH__, 
                                  rightColumnWidth=__FOURTH_COLUMN_WIDTH__, makeAdjustable=False)
        
    MakeText(locationAttribute.attributeLabel, annotation)
    
    locationField = pm.floatFieldGrp(numberOfFields=3, precision=3, columnWidth3=(__MIDDLE_COLUMN_WIDTH__, __MIDDLE_COLUMN_WIDTH__, __MIDDLE_COLUMN_WIDTH__),
                                     value1=locationAttribute.x, value2=locationAttribute.y, value3=locationAttribute.z)
    locationField.changeCommand(lambda *args: locationAttribute._setValue(locationField.getValue()))
    locationAttribute.updateUiCommand = (lambda *args: locationField.setValue((locationAttribute.x, locationAttribute.y, locationAttribute.z, 0.0)))
    locationAttribute.uiEnableMethod = locationField.setEnable
    if(annotation is not None):
        locationField.setAnnotation(annotation)
        
    if(withButton):
        button = pm.button(label="...", annotation=("Select/clear locator for %s" % at.LocationAttribute.attributeLabel), 
                           width=__FOURTH_COLUMN_WIDTH__)
        button.setCommand(lambda *args: _MakeObjectSelectionList(locationAttribute))
        
    SetAsChildLayout(rowLayout)
    
    return locationField

#########################
def MakeVectorField(vectorAttribute, annotation=None):
    if(not isinstance(vectorAttribute, at.Vector3Attribute)):
        raise TypeError("Expected %s, got %s" % (at.Vector3Attribute, type(vectorAttribute)))
    
    rowLayout = MakeRowLayout(2)
    
    MakeText(vectorAttribute.attributeLabel, annotation)
    vectorField = pm.floatFieldGrp(numberOfFields=3, precision=3, columnWidth3=(__MIDDLE_COLUMN_WIDTH__, __MIDDLE_COLUMN_WIDTH__, __MIDDLE_COLUMN_WIDTH__),
                                   value1=vectorAttribute.x, value2=vectorAttribute.y, value3=vectorAttribute.z)
    vectorField.changeCommand(lambda *args: vectorAttribute._setValue(vectorField.getValue()))
    vectorAttribute.updateUiCommand = (lambda *args: vectorField.setValue((vectorAttribute.x, vectorAttribute.y, vectorAttribute.z, 0.0)))
    vectorAttribute.uiEnableMethod = vectorField.setEnable
    if(annotation is not None):
        vectorField.setAnnotation(annotation)
        
    SetAsChildLayout(rowLayout)
    
    return vectorField

#########################
def MakePassiveTextField(stringAttribute, buttonCallback, annotation=None, isEditable=False,
                         leftColumnWidth=__LEFT_COLUMN_WIDTH__, rightColumnWidth=__MIDDLE_COLUMN_WIDTH__ + __RIGHT_COLUMN_WIDTH__):
    
    if(not isinstance(stringAttribute, at.StringAttribute)):
        raise TypeError("Attempted to make text field (expected:%s, got:%s)" % 
                        (at.StringAttribute, type(stringAttribute)))

    rowLayout = MakeRowLayout(2, leftColumnWidth=leftColumnWidth, rightColumnWidth=rightColumnWidth)
     
    MakeText(stringAttribute.attributeLabel, annotation)
    
    buttonWidth = 50
    textField = pm.textFieldButtonGrp(editable=isEditable, text=stringAttribute.value,
                                      buttonLabel="...", buttonCommand=buttonCallback,
                                      adjustableColumn=1, 
                                      columnWidth2=(rightColumnWidth - buttonWidth, buttonWidth))
    if(annotation is not None):
        textField.setAnnotation(annotation)
    
    stringAttribute.updateUiCommand = textField.setText
    if(isEditable):
        def _setEnabled(textField, editable):
            textField.setEnableButton(editable)
            textField.setEditable(editable)
        stringAttribute.uiEnableMethod = (lambda enable: _setEnabled(textField, enable))
    else:
        stringAttribute.uiEnableMethod = textField.setEnableButton
    
    SetAsChildLayout(rowLayout)
    
    return rowLayout
    
#########################
def MakeSimpleIntField(intAttribute, annotation=None):
    if(not isinstance(intAttribute, at.IntAttribute)):
        raise TypeError("Expected %s, got %s" % (at.IntAttribute, type(intAttribute)))
    
    rowLayout = MakeRowLayout(3)
    MakeText(intAttribute.attributeLabel, annotation)
    intField = pm.intField(value=intAttribute.value)
    if(intAttribute.minimumValue is not None):
        intField.setMinValue(intAttribute.minimumValue)
    if(intAttribute.maximumValue is not None):
        intField.setMaxValue(intAttribute.maximumValue)
    if(annotation is not None):
        intField.setAnnotation(annotation)
        
    intField.changeCommand(lambda *args: intAttribute._setValue(intField.getValue()))
    
    intAttribute.updateUiCommand = intField.setValue
    intAttribute.uiEnableMethod = intField.setEnable
    
    SetAsChildLayout(rowLayout)
    
    return (rowLayout, intField)
    
#########################



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

#######################
def MakeButtonStandalone(label, callback, extraLabel=None, annotation=None):
    if(extraLabel is None):
        rowLayout = MakeRowLayout(1, makeAdjustable=False)
        button = MakeButton(label, callback, annotation)
        button.setWidth(__OPTIONS_MENUS_WIDTH__ - 10)
        
        SetAsChildLayout(rowLayout)
        
    else:
        rowLayout = MakeRowLayout(2, rightColumnWidth=__OPTIONS_MENUS_WIDTH__, makeAdjustable=False)
        MakeText(extraLabel, annotation)
        button = MakeButton(label, callback, annotation)
        button.setWidth(__OPTIONS_MENUS_WIDTH__ - 10)
        
        SetAsChildLayout(rowLayout)
        
    return (rowLayout, button)

#######################
def MakeButtonStrip(textCommandTupleList):
    formLayout = MakeFormLayout()
    controls = []
    
    for buttonTuple in textCommandTupleList:
        text = buttonTuple[0]
        command = buttonTuple[1]
        annotation = buttonTuple[2] if(len(buttonTuple) > 2) else None

        button = MakeButton(text, command, annotation)
        controls.append(button)
        
    DistributeControlsHorizontallyInFormLayout(formLayout, controls)
    SetAsChildLayout(formLayout)
    
    return (formLayout, controls)

#####################
def MakeTextInputField(label, enterCommand=None, placeholderText=None, leftColumnWidth=__LEFT_COLUMN_WIDTH__, annotation=None):
    rowLayout = MakeRowLayout(2, leftColumnWidth)

    MakeText(label, annotation)
    textField = pm.textField()
    
    if(enterCommand is not None):
        textField.enterCommand(enterCommand)
        textField.setAlwaysInvokeEnterCommandOnReturn(True)
    if(placeholderText is not None):
        textField.setText(placeholderText)
    if(annotation is not None):
        textField.setAnnotation(annotation)
        
    SetAsChildLayout(rowLayout)
    
    return (rowLayout, textField)

#####################
def MakeRadioButtonGroup(label, buttonTitlesTuple, onChangeCommand, vertical,
                         leftColumnWidth=__LEFT_COLUMN_WIDTH__, annotation=None):
    numberOfButtons = len(buttonTitlesTuple)
    if(numberOfButtons < 1 or numberOfButtons > 4):
        raise ValueError("Attempt to create radioButtonGrp with %d buttons (expected 1-4)." % numberOfButtons)
    
    buttonKwargs = { "label" : label,
                     ("labelArray%d" % numberOfButtons) : buttonTitlesTuple,
                     "numberOfRadioButtons" : numberOfButtons,
                     "columnAttach" : (2, "left", 0),
                     "vertical" : vertical,
                     "select" : 1 }
    if(onChangeCommand is not None):
        buttonKwargs["changeCommand"] = onChangeCommand
    if(annotation is not None):
        buttonKwargs["annotation"] = annotation
    
    buttonGroup = pm.radioButtonGrp(**buttonKwargs)
    
    buttonGroup.columnWidth((1, leftColumnWidth))
    for index in xrange(numberOfButtons - 1):
        buttonGroup.columnWidth((index + 2, 80))
    
    return buttonGroup

#####################
def MakeSeparator():
    return pm.separator(style='in')

#####################
def GetUserConfirmation(title, message):
    return pm.confirmBox(title, message, "OK", "Cancel")

#####################
def DisplayInfoBox(message, title=None):
    pm.informBox(title, message)

#####################    
def MakeImage(imageFilePath, annotation=None):
    if(annotation is None):
        return pm.image(image=imageFilePath)
    else:
        return pm.image(image=imageFilePath, annotation=annotation)

#####################
def MakeNodeNameField(label, shapeNode, nameChangeCommand, leftColumnWidth=__LEFT_COLUMN_WIDTH__, annotation=None):
    rowLayout = MakeRowLayout(2, leftColumnWidth=leftColumnWidth, makeAdjustable=False)
    
    MakeText(label, annotation)
    nameField = pm.nameField(object=shapeNode)
    if(nameChangeCommand is not None):
        nameField.setNameChangeCommand(nameChangeCommand)
    if(annotation):
        nameField.setAnnotation(annotation)
    SetAsChildLayout(rowLayout)

    return (rowLayout, nameField)

#####################
def MakeProgressBar(initialStatus, maxValue=100, leftColumnWidth=__LEFT_COLUMN_WIDTH__, 
                    middleColumnWidth=__MIDDLE_COLUMN_WIDTH__, rightColumnWidth=__RIGHT_COLUMN_WIDTH__, annotation=None):

    rowLayout = MakeRowLayout(3, leftColumnWidth=leftColumnWidth, middleColumnWidth=middleColumnWidth, 
                              rightColumnWidth=rightColumnWidth, makeAdjustable=False)
    
    MakeText("Status:", annotation)
    progressBar = pm.progressBar(maxValue=maxValue)
    statusLabel = pm.textField(text=initialStatus, editable=False)
#     if(barWidth is not None):
#         progressBar.setWidth(barWidth)
    if(annotation is not None):
        statusLabel.setAnnotation(annotation)
        progressBar.setAnnotation(annotation)
    
    SetAsChildLayout(rowLayout)
    
    return (rowLayout, statusLabel, progressBar)

#####################    
def GetFilePathFromUser(isReadOnly, initialFolderPath=None, fileExtensionMask=None):
    kwargs = { "mode" :  0 if(isReadOnly) else 1 }
    
    if(initialFolderPath is not None):
        mask = initialFolderPath + '*'
        if(fileExtensionMask is not None):
            mask += fileExtensionMask
        kwargs["directoryMask"] = mask
    elif(fileExtensionMask is not None):
        kwargs["directoryMask"] = "*" + fileExtensionMask
        
    return pm.fileDialog(**kwargs)

#####################
def DeleteComponent(uiComponent):
    pm.deleteUI(uiComponent)


####################################################################