"""
This script creates a Maya UI for setting Arnold subdivision attributes on selected objects.
It allows users to:
- Set the subdivision type (none, catclark, or linear) and specify the subdivision iterations.
- Save and load presets for subdivision settings, enabling quick use of commonly used configurations.
- Reset the UI to default values.

Key features:
1. Dropdown menus for subdivision type and saved presets.
2. IntField for specifying subdivision iterations.
3. Buttons to set subdivisions, reset options, and save new presets.
4. Presets are stored in a dictionary and can be dynamically added to the UI.

This UI is intended to make the process of managing Arnold subdivision attributes in Maya more efficient by allowing the user to apply Arnold subdivisions to multiple meshes at once
and use presets for their most used Arnold subdivision settings for quick application.
"""

import maya.cmds as cmds

# Dictionary to hold preset values
presets = {}

def UI():
    """
    Creates and displays the Maya UI for Arnold subdivisions.
    The UI includes options for selecting subdivision types, setting subdivision levels, 
    managing presets, and resetting the UI to default settings.
    """
    if cmds.window('ArnoldSubdivs', exists=1):
        cmds.deleteUI('ArnoldSubdivs')

    subdivsWindow = cmds.window('ArnoldSubdivs', w=400, h=300, mnb=0, mxb=0, sizeable=0, title='Set Arnold Subdivisions')

    mainLayout = cmds.columnLayout(w=400, h=300)

    # Text overlay
    cmds.text(label='Arnold Subdivisions', w=400, h=20, fn='boldLabelFont', bgc=(0.15, 0.15, 0.15))
    cmds.separator(h=10, style='none')

    rowLayout = cmds.rowColumnLayout(nc=3, cw=[(1, 250), (2, 70), (3, 70)], columnOffset=[(1, 'both', 5), (2, 'both', 5), (3, 'both', 10)])

    # Controls for aiSubdivs
    subOptionMenu = cmds.optionMenuGrp('subOptionMenu', label='Sub Type', cal=(1, 'left'), cw=(1, 70))
    cmds.menuItem(label='none')
    cmds.menuItem(label='catclark')
    cmds.menuItem(label='linear')

    # Set catclark as default
    cmds.optionMenuGrp(subOptionMenu, e=1, sl=2)

    subNumbtext = cmds.text(label='Subdivs', fn='plainLabelFont', align='left')
    subNumb = cmds.intField('subNumb', minValue=0, maxValue=100, value=2, w=60)

    cmds.separator(h=10, style='none')

    cmds.button(label='Set Subdivisions', w=330, h=50, parent=mainLayout, command=aiSubdivs)
    cmds.button(label='Reset Options', w=330, h=50, parent=mainLayout, command=resetSubdivs)

    cmds.columnLayout(parent=mainLayout, adjustableColumn=True)
    
    presetOptionMenu = cmds.optionMenuGrp('presetMenu', label='Presets', cal=(1, 'left'), cw=(1, 70), changeCommand=applyPreset)
    cmds.menuItem(label='none')

    # Set "none" as the default selected preset
    cmds.optionMenuGrp(presetOptionMenu, e=1, sl=1)

    cmds.button(label='Save Preset', w=330, h=50, parent=mainLayout, command=savePreset)

    cmds.rowColumnLayout(nc=2, cw=[(1, 100), (2, 300)], columnOffset=[(1, 'both', 5), (2, 'both', 10)])

    subPresetText = cmds.text(label='Preset', fn='plainLabelFont', align='left', width=100)

    cmds.textField('presetNameField', w=300, placeholderText="Enter Preset Name")

    cmds.showWindow(subdivsWindow)

def aiSubdivs(*args):
    """
    Applies the selected Arnold subdivision type and iterations to all currently selected objects.
    """
    selection = cmds.ls(sl=1)
    if len(selection) > 0:
        subType = cmds.optionMenuGrp('subOptionMenu', q=1, sl=1) - 1
        subCount = cmds.intField('subNumb', q=1, v=1)
        for obj in selection:
            if cmds.listRelatives(obj)[0] in cmds.ls(et='mesh'):
                cmds.setAttr(obj + '.aiSubdivType', subType)
                cmds.setAttr(obj + '.aiSubdivIterations', subCount)
    else:
        cmds.warning('Empty selection')

def resetSubdivs(*args):
    """
    Resets the UI to default values:
    - Subdivision type: 'none'
    - Subdivision iterations: 0
    - Preset menu: 'none'
    """
    cmds.optionMenuGrp('subOptionMenu', e=True, sl=1)
    cmds.intField('subNumb', e=True, v=0)
    cmds.optionMenuGrp('presetMenu', e=True, sl=1)

def applyPreset(*args):
    """
    Applies the selected preset to the subdivision controls (type and iterations).
    """
    presetName = cmds.optionMenuGrp('presetMenu', q=True, value=True)
    presetSettings = presets.get(presetName, {"subType": 1, "subCount": 2})
    cmds.optionMenuGrp('subOptionMenu', e=True, sl=presetSettings["subType"] + 1)
    cmds.intField('subNumb', e=True, v=presetSettings["subCount"])

def savePreset(*args):
    """
    Saves the current subdivision settings as a new preset.
    - Updates the preset dictionary.
    - Adds the new preset to the preset menu for future selection.
    """
    presetName = cmds.textField('presetNameField', q=True, text=True)
    if presetName:
        subType = cmds.optionMenuGrp('subOptionMenu', q=True, sl=True) - 1
        subCount = cmds.intField('subNumb', q=True, v=True)
        presets[presetName] = {"subType": subType, "subCount": subCount}

        cmds.menuItem(label=presetName, parent='presetMenu|OptionMenu')
        cmds.warning(f"Preset '{presetName}' saved successfully!")
    else:
        cmds.warning("Please enter a preset name.")

if __name__ == "__main__" or True:
    UI()