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
uiBuilder module is a collection of functions for constructing a UI from components.

Many of the functions here are wrappers around PyMel UI creation methods with standardised
parameters, callbacks etc.  
There are also methods for building composite UI components and some convenience methods 
for UI related calls.

The module is roughly split into sections:  
 Windows, Menus, Layouts, Input Fields (biggest section by far), Miscellaneous Items.
"""

import attributes.attributeTypes as at
import utils.general as util
import utils.sceneInterface as scene
import utils.fileLocations as fl

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
    """
    Returns True if window for the given handle exists, False otherwise.
    
    :param windowReference: PyMel window reference. 
    """
    return(windowReference is not None and pm.window(windowReference, exists=True))

#####################
def WindowIsVisible(windowReference):
    """
    Returns True if window exists and is visible, False otherwise.
    
    :param windowReference: PyMel window reference. 
    """
    return (WindowExists(windowReference) and pm.window(windowReference, query=True, visible=True))

#####################
def MakeWindow(title, widthHeight=None):
    """
    Creates a new PyMel window instance.
     
    :param title: string, the display title for the window.
    :param widthHeight: a (width,height) tuple (floats), or None.
    """
    if(widthHeight is None):
        return pm.window(title, maximizeButton=False, resizeToFitChildren=True, menuBar=True)
    else:
        return pm.window(title, maximizeButton=False, resizeToFitChildren=True, menuBar=True, widthHeight=widthHeight)

#####################
def DestroyWindowIfNecessary(windowReference):
    """
    Trashes the window for the given reference, if it exists.
    
    :param windowReference: PyMel window reference. 
    """
    if(WindowExists(windowReference)):
        pm.deleteUI(windowReference, window=True)

#############################



#################################################
#########             MENUS         #############
#################################################

def SetParentMenuLayout(parentMenuLayout):
    """
    Sets the given menu layout instance to be the parent of any subsequently created menu items. 
    
    :param parentMenuLayout: PyMel menu reference. 
    """
    if(not IsCurrentMenuParent(parentMenuLayout)):
        pm.setParent(parentMenuLayout, menu=True)

#####################        
def SetAsChildMenuLayout(*childLayouts):
    """
    Sets the menu items in the argument list to be children of a previously 'setParent' menu item.
    
    Note that it's the number of objects in the list rather than the actual references that is important
    here, i.e. if you create 3 menu instances that need to be children, you could simply call this method
    with 3 random objects in the argument list and it would have the same effect. 
    """
    for _ in childLayouts:
        pm.setParent("..", menu=True)

#####################
def IsCurrentMenuParent(menuControl):
    """
    Returns True if the given menu instance is the currently set parent (i.e. will be parent to any subsequently
    created menu items).
    
    :param menuControl: PyMel reference to a menu instance.
    """
    return (menuControl == pm.currentMenuParent())

#####################
def MakeMenu(menuTitle):
    """
    Creates & returns a new menu instance.
    
    :param menuTitle: string, title for the menu.
    """
    return pm.menu(menuTitle)
    
#####################    
def MakeMenuItem(itemLabel, onSelectCommand, annotation=None):
    """
    Creates & returns a new menu item under a parent menu.
    
    :param itemLabel: string, title for the menu item.
    :param onSelectCommand: bound method to be called when item is chosen.
    :param annotation: annotation to be displayed when user hovers over the item, or None. 
    """
    newMenuItem = pm.menuItem(label=itemLabel)
    
    if(onSelectCommand is not None):
        newMenuItem.setCommand(onSelectCommand)
    if(annotation is not None):
        newMenuItem.setAnnotation(annotation)
    
    return newMenuItem

#####################
def MakeMenuItemWithSubMenu(itemLabel, annotation=None):
    """
    Creates & returns a new menu item with it's own flash-up sub menu.
    
    :param itemLabel: string, title for the menu item.
    :param annotation: annotation to be displayed when user hovers over the item, or None. 
    """
    newMenuItem = pm.menuItem(label=itemLabel, subMenu=True)
    if(annotation is not None):
        newMenuItem.setAnnotation(annotation)
    
    return newMenuItem

#####################
def MakeMenuSubItem(itemLabel):
    """
    Creates & returns a new menu sub-item under a parent menu item with sub-menu.
    
    :param itemLabel: string, title for the menu sub-item.
    """
    return pm.menuItem(label=itemLabel)

#####################
def MakeMenuSeparator():
    """
    Creates & returns a menu seperator under a parent menu or sub-menu.
    """
    return pm.menuItem(divider=True)

#########################



#################################################
#########             LAYOUTS       #############
#################################################

def SetParentLayout(parentLayout):
    """
    Sets the given layout instance to be the parent of any subsequently created menu items. 
    
    :param parentLayout: PyMel layout reference. 
    """
    if(not IsCurrentParent(parentLayout)):
        pm.setParent(parentLayout)

#####################
def SetAsChildLayout(*childLayouts):
    """
    Sets the control/layout instances in the argument list to be children of a previously 'setParent' layout.
    
    Note that it's the number of objects in the list rather than the actual references that is important
    here, i.e. if you create 3 layout instances that need to be children, you could simply call this method
    with 3 random objects in the argument list and it would have the same effect. 
    """
    for _ in childLayouts:
        pm.setParent("..")

#####################        
def IsCurrentParent(control):
    """
    Returns True if the given control instance is the currently set parent (i.e. will be parent to any subsequently
    created layout/control items).
    
    :param control: PyMel reference to a control instance.
    """
    return (control == pm.currentParent())

#####################
def MakeFormLayout(title=None):
    """
    Creates & returns a new PyMel form layout.
    
    :param title: string, title of the layout, or None.
    """
    if(title is not None):
        return pm.formLayout(title)
    else:
        return pm.formLayout()

##################### 
def MakeScrollLayout(title=None):
    """
    Creates & returns a new PyMel scroll layout.
    
    :param title:  string, title of the layout, or None.
    """
    if(title is not None):
        return pm.scrollLayout(title, childResizable=True)
    else:
        return pm.scrollLayout(childResizable=True)

#####################
def MakeBorderingLayout():
    """
    Creates & returns a plain layout with an etched border (PyMel frame layout).
    """
    return pm.frameLayout(labelVisible=False, borderStyle='etchedIn', marginWidth=2, marginHeight=3)

#####################
def MakeFrameLayout(title, makeCollapsable=True):
    """
    Creates & returns a PyMel frame layout.
    
    :param title: string, title of the layout.
    :param makeCollapsable: True = layout has a collapse/expand button, False = fixed size.
    """
    frame = pm.frameLayout(title, borderStyle='out')
    if(makeCollapsable):
        frame.setCollapsable(True)
    return frame

#####################
def MakeTabLayout(height=None):
    """
    Creates & returns a PyMel tab layout.
    
    :param height: float, specific height, or None for default.
    """
    if(height is not None):
        return pm.tabLayout(height=height)
    else:
        return pm.tabLayout()

##################### 
def MakeColumnLayout(title=None):
    """
    Creates and returns a PyMel column layout.
    
    :param title: string, title of the layout, or None.
    """
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
    """
    Creates & returns a PyMel row layout. 
    
    :param numColumns: number of columns in the layout, min=1 max=4 (<1 or >4 will raise a ValueError).
    :param leftColumnWidth: float, width of left column.
    :param middleColumnWidth: float, width of middle column, ignored if numColumns = 1.
    :param rightColumnWidth: float, width of right column, ignored if numColumsn < 3.
    :param makeAdjustable: True = right-most column (up to 3rd) will have flexible width, False = all columns fixed.
    """
    
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
    """
    Creates & returns a row layout suitable for the upper section of the UI (as opposed to the agent/behaviour attributes sections).
    2 columns, left one flexible width, right one suitable for 'swarm' image. 
    
    :param componentsSectionWidth: float, width for UI compnent (left) column.  
    """
    rowLayout = pm.rowLayout(numberOfColumns=2, 
                              adjustableColumn=1,
                              columnWidth2=(componentsSectionWidth, fl.LogoImagePixelWidth()), 
                              columnAlign=[(1, 'left'), (2, 'right')], 
                              columnAttach=[(1, 'both', 0), (2, 'right', 0)])
    
    return rowLayout

#########################
def DistributeControlsHorizontallyInFormLayout(formLayout, controls):
    """
    Lays out given controls in a horizontal 'flow' within the given form layout.
    i.e. controls given equal size and made resizable.
    
    :param formLayout: a PyMel form layout reference. 
    :param controls: list of PyMel controls (e.g. buttons).
    """
    formLayout.attachForm(controls[0], 'left', 2)

    numControls = len(controls)   
    stepSize = formLayout.getNumberOfDivisions() / numControls
    position = stepSize
    
    for i in range(numControls - 1):
        formLayout.attachPosition(controls[i], 'right', 1, position)
        formLayout.attachPosition(controls[i + 1], 'left', 1, position)
        position += stepSize
        
    formLayout.attachForm(controls[-1], 'right', 2)
    
###################
def DistributeButtonedWindowInFormLayout(formLayout, windowLayout, buttonsLayout):
    """
    Creates & returns a panel-and-buttons layout within a form layout.
    
    :param formLayout: containing PyMel form layout.
    :param windowLayout: layout containing the main panel of the window, would usually be result from MakeBorderingLayout.
    :param buttonsLayout: layout containing strip of buttons for bottom of the window, probably be result from MakeButtonStrip.
    """
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
    """
    Creates & returns a slider-and-input-field control for a given numerical attribute.
    
    :param attribute: attribute hooked up to the control - an IntAttribute or FloatAttribute instance.
    :param annotation: toolTip annotation, or None. 
    """
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
    """
    Creates & returns a simple label-and-input-field control for a given numerical attribute.
    
    :param attribute: attribute hooked up to the control - an IntAttribute or FloatAttribute instance.
    :param annotation: toolTip annotation, or None. 
    :param leftColumnWidth: float, width of label column.
    :param rightColumnWidth: float, width of input field column.
    """
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
    """
    Creates & returns a slider group for a given randomiser attribute.
    
    :param randomizerAttribute: a RandomiserAttribute instance.
    :param annotation: toolTip annotation, or None. 
    """
    inputGroup = MakeSliderGroup(randomizerAttribute, annotation)
    
    return inputGroup
    
##################### 
def MakeCheckboxStandalone(boxLabel, initialValue, extraLabel=None, changeCommand=None, 
                           leftColumnWidth=__LEFT_COLUMN_WIDTH__, annotation=None, switchLabels=False):
    """
    Creates & returns a PyMel checkbox that is not specifically linked to an attribute.
    
    :param boxLabel: string, label to right of checkbox (or to left of checkbox, with colon, if extraLabel is also defined).
    :param initialValue: bool, initial value.
    :param extraLabel: string, label to the right of the checkbox if boxLabel is also defined.  
    :param changeCommand: bound method to be executd when checkbox value changes, or None.
    :param leftColumnWidth: float, width of left-hand label.
    :param annotation: toolTip annotation, or None. 
    :param switchLabels: True = extraLabel to left (with colon) & boxLabel to right, False = vice versa.
    """
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
    """
    Creates & returns a PyMel checkbox tied to a boolean attribute.
    
    :param attribute: BoolAttribute instance. 
    :param extraLabel: extra label if both label to left with colon and label to right of checkbox are required.
    :param annotation: toolTip annotation, or None. 
    :param leftColumnWidth: float, width of left-hand label.
    :param switchLabels: True = extraLabel to left (with colon) & attribute description to right, False = vice versa.
    """
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
    """
    Creates & returns a menu group giving the the randomiser options for a given randomizeController. 
    
    :param randomizerController: RandomiseController instance. 
    :param annotation: toolTip annotation, or None. 
    """
    if(type(randomizerController) != at.RandomizeController):
        raise TypeError("Attempt to make randomizer menu from non-RandomizeController attribute.")
    
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
    """
    Creates & returns a whole attribute randomiser group (i.e. slider and options menu combined) for a given randomiseController. 
    
    :param randomizerController: RandomiseController instance. 
    :param annotation: toolTip annotation, or None (gives default annotation). 
    """
    if(annotation is None):
        annotation = ("Input modes:\n"
                      "Off = value taken directly from %s.\n"
                      "By Agent ID = value offset by constant amount (same across all attributes) - which is randomized per-agent.\n"
                      "Pure Random = value offset by constant amount, randomized per-agent *and* per-attribute." 
                      % randomizerController._parentAttribute.attributeLabel)

    optionsMenuRowLayout = MakeRandomizeOptionsMenu(randomizerController, annotation)
    randomizerSliderGroup = MakeRandomizerGroup(randomizerController._randomizerAttribute, 
                                                ("Randomness multiplier for %s" % randomizerController.attributeLabel))
    randomizerController._updateInputUiComponents()
    
    return (optionsMenuRowLayout, randomizerSliderGroup)
    
#########################
def MakeStringOptionsField(stringAttribute, optionsListStrings, annotation=None):
    """
    Creates & returns a menu with a given list of options for corresponding stringAttribute.
    
    :param stringAttribute: StringAttribute instance. 
    :param optionsListStrings: List of possible values for string attribute, will be presented as menu options. 
    :param annotation: toolTip annotation, or None. 
    """
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
    """
    Creates & returns a composite UI component, for the given MayaObjectAttribute, which allows 
    the user to select from objects in the Maya scene of a given type. 
    
    :param objectAttribute: MayaObjectAttribute instance. 
    :param annotation: toolTip annotation, or None. 
    """
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
    """
    Helper function for constructing object selector fields.  Constructs selectable list of objects in the Maya scene
    of the type determined by the MayaObjectAttribute. 
    Will be shown when user presses button linked to the parent object selection UI component. 
    
    :param objectAttribute: MayaObjectAttribute instance. 
    """
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
    """
    Creates & returns a UI component, linked to given LocationAttribute, which allows user to manually enter coordinate
    values, or select a Maya Locator within the scene to determine the location. 
    
    :param locationAttribute: LocationAttribute instance. 
    :param withButton: True = has button to show Maya Locator selection menu, False = button not available (input fields only).
    :param leftColumnWidth: float, width of label column. 
    :param annotation: toolTip annotation, or None. 
    """
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
    """
    Creates & returns an input field, linked to given Vector3Attribute, which allows user to input x,y,z values. 
    
    :param vectorAttribute: Vector3Attribute instance. 
    :param annotation: toolTip annotation, or None.
    """
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
    """
    Creates & returns PyMel textFieldButtonGroup linked to given StringAttribute.
    
    :param stringAttribute: StringAttribute instance. 
    :param buttonCallback: bound method to be called when textField button is pressed. 
    :param annotation: toolTip annotation, or None. 
    :param isEditable: True = user can input text directly, False = user cannot type in text. 
    :param leftColumnWidth: float, width of label to left of text field.
    :param rightColumnWidth: float, width of text field itself. 
    """
    
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
    """
    Creates & returns a labelled integer input field for given IntAttribute instance. 
    
    :param intAttribute: IntAttribute instance. 
    :param annotation: toolTip annotation, or None. 
    """
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
    """
    Create & returns a simple text label.
    
    :param text: string, text to display.
    :param annotation: toolTip annotation, or None. 
    """
    text = pm.text(text)
    if(annotation is not None):
        text.setAnnotation(annotation)
        
    return text

#####################
def MakeButton(text, callback, annotation=None):
    """
    Creates & returns a pressable button.
    
    :param text: string, label to display on the button.
    :param callback: bound method to be invoke when user presses button.
    :param annotation: toolTip annotation, or None. 
    """
    button = pm.button(label=text, command=callback)
    if(annotation is not None):
        button.setAnnotation(annotation)
        
    return button

#######################
def MakeButtonStandalone(label, callback, extraLabel=None, annotation=None):
    """
    Creates & returns a pressable button with optional extra text label.
    
    :param label: string, displayed on button itself.
    :param callback:  bound method to be invoke when user presses button.
    :param extraLabel: string to be displayed to left of button, or None. 
    :param annotation: toolTip annotation, or None. 
    """
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
    """
    Creates & returns a strip of pressable buttons embedded in a PyMel form layout. 
    
    :param textCommandTupleList: list of tuples of the form:
                                 (<button text>,<onPress bound method>,<optional toolTip annotation>).
    """
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
    """
    Creates & returns an editable text input field.
    
    :param label: text label to left of input field.
    :param enterCommand: bound method to be called when user presses <enter>, or None.
    :param placeholderText: text field placeholder string, or None.
    :param leftColumnWidth: float, width of label column.
    :param annotation: toolTip annotation, or None. 
    """
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
    """
    Creates a radio button group.
    
    :param label: text label for the group as a whole. 
    :param buttonTitlesTuple: tuple (or list) of titles for each button.
    :param onChangeCommand: bound method to be called when a button is selected.
    :param vertical: True = group will be laid out vertically, False = horizontally.
    :param leftColumnWidth: float, width of label column.
    :param annotation: toolTip annotation, or None. 
    """
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
    """
    Creates & returns a layout separator. 
    """
    return pm.separator(style='in')

#####################
def GetUserConfirmation(title, message):
    """
    Displays an OK/Cancel box to user.
    Returns True if OK pressed, False if Cancel.
    
    :param title: box Title.
    :param message: box body text. 
    """
    return pm.confirmBox(title, message, "OK", "Cancel")

#####################
def DisplayInfoBox(message, title=None):
    """
    Displays dismissable info box to user.
    
    :param message: box Title.
    :param title: box body text. 
    """
    pm.informBox(title, message)

#####################    
def MakeImage(imageFilePath, annotation=None):
    """
    Creates & returns a PyMel image UI component. 
    
    :param imageFilePath: full path to an image file.
    :param annotation: toolTip annotation, or None. 
    """
    if(annotation is None):
        return pm.image(image=imageFilePath)
    else:
        return pm.image(image=imageFilePath, annotation=annotation)

#####################
def MakeNodeNameField(label, shapeNode, nameChangeCommand, leftColumnWidth=__LEFT_COLUMN_WIDTH__, annotation=None):
    """
    Creates & returns a field which displays the name of the given object from the Maya scene.
    The name field will automatically update if the object is renamed.
    
    :param label: text label for the field.
    :param shapeNode: PyMel PyNode for an in-scene Maya object, who's name will be displayed in the field.
    :param nameChangeCommand: bound method to be called when object's name is changed. 
    :param leftColumnWidth: float, width of label column. 
    :param annotation: toolTip annotation, or None. 
    """
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
    """
    Creates & returns an updatable progress bar with an associated 'status readout' text label to the right.
    
    :param initialStatus: initial text for the status label.
    :param maxValue: float, max value for progress bar.
    :param leftColumnWidth: float, width for title label to left of bar (text = "Status")
    :param middleColumnWidth: float, width of progress bar.
    :param rightColumnWidth: float, width of status readout label.
    :param annotation: toolTip annotation, or None. 
    """

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
    """
    Queries user for a file path with a dialogue box and returns the result. 
    
    :param isReadOnly: True = we are opening a file, False = we want a location to save a file.  
    :param initialFolderPath: full path for starting point, or None for default. 
    :param fileExtensionMask: filter for file extension (e.g. ".zip"), or None for no filter. 
    """
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
    """
    Trashes the given PyMel UI component. 
    
    :param uiComponent: handle for PyMel UI compoenent. 
    """
    pm.deleteUI(uiComponent)


####################################################################