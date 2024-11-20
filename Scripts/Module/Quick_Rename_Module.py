# Quick_Rename_Module.py
# Contains custom layer related UI and function functions
import maya.mel as mel
import re
import maya.cmds as cmds
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
#====== UI Button Components ======

class RoundedButton(QtWidgets.QPushButton):
    """
    Custom rounded button class
    
    Features:
    - Rounded design
    - Custom color and hover effect
    - Bold text
    """
    def __init__(self, text="", icon=None):
        super(RoundedButton, self).__init__(text)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(24, 24))
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #D0D0D0;
                color: #303030;
                border-radius: 10px;
                padding: 5px;
                font-weight: bold;
                text-align: center;
                
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
            """
        )

#====== UI Main Window Component ======

class Quick_Rename_Module_UI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Quick_Rename_Module_UI, self).__init__(parent)
        self.setWindowTitle("Quick_Rename_Module")
        self.setMinimumWidth(280)
        
        # Set window icon
        self.setWindowIcon(QtGui.QIcon(":annotation.png"))

        # Set window flags to always stay on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

#====== UI Components ======

    def create_widgets(self):

        # Quick prefix suffix group
        self.quick_prefix_suffix_group = QtWidgets.QGroupBox("Quickuffix")
        self.quick_prefix_suffix_btns = [
            # RoundedButton("SM_"),
            RoundedButton("_La"),
            RoundedButton("_Lb"),
            RoundedButton("_Hi"),
            RoundedButton("_Temp")
        ]

        # Quick group options group
        self.quick_group_group = QtWidgets.QGroupBox("QuickGroup")
        self.quick_group_buttons = [
            RoundedButton("La_mesh"),
            RoundedButton("Lb_mesh"),
            RoundedButton("Hires"),
            RoundedButton("Retopo"),
            RoundedButton("Temp_mesh"),
            RoundedButton("Concept")
        ]

        # Quick display layer options group
        self.quick_layer_group = QtWidgets.QGroupBox("QuickLayer")
        self.quick_layer_buttons = [
            RoundedButton("La"),
            RoundedButton("Lb"),
            RoundedButton("Hi"),
            RoundedButton("RetopoMesh"),
            RoundedButton("Temp"),
            RoundedButton("Mesh")
        ]

        
        self.bottom_group = QtWidgets.QGroupBox("Quick Tools")
        self.bottom_buttons = [
            RoundedButton("Remove pasted__"),
            RoundedButton("Mirror L_R"),
        ]

#====== UI Layout ======

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Quick_Prefix_Suffix layout
        quick_prefix_suffix_layout = QtWidgets.QGridLayout()
        for i, btn in enumerate(self.quick_prefix_suffix_btns):
            quick_prefix_suffix_layout.addWidget(btn, i // 3, i % 3)
        self.quick_prefix_suffix_group.setLayout(quick_prefix_suffix_layout)
        main_layout.addWidget(self.quick_prefix_suffix_group)
        
        # QuickGroup layout
        quick_group_layout = QtWidgets.QVBoxLayout()
        quick_group_buttons_layout = QtWidgets.QGridLayout()
        
        for i, btn in enumerate(self.quick_group_buttons):
            row = i // 3
            col = i % 3
            quick_group_buttons_layout.addWidget(btn, row, col)
        
        quick_group_layout.addLayout(quick_group_buttons_layout)
        self.quick_group_group.setLayout(quick_group_layout)
        
        # QuickLayer layout
        quick_layer_layout = QtWidgets.QVBoxLayout()
        quick_layer_buttons_layout = QtWidgets.QGridLayout()
        
        for i, btn in enumerate(self.quick_layer_buttons):
            row = i // 3
            col = i % 3
            quick_layer_buttons_layout.addWidget(btn, row, col)
        
        quick_layer_layout.addLayout(quick_layer_buttons_layout)
        self.quick_layer_group.setLayout(quick_layer_layout)
        
        # Add two option groups to the main layout
        main_layout.addWidget(self.quick_group_group)
        main_layout.addWidget(self.quick_layer_group)

        
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.bottom_buttons[0])
        bottom_layout.addWidget(self.bottom_buttons[1])
        self.bottom_group.setLayout(bottom_layout)
        main_layout.addWidget(self.bottom_group)

#====== UI and Function Connections ======

    def create_connections(self):
        # Add connections for QuickGroup buttons
        for btn in self.quick_group_buttons:
            btn.clicked.connect(partial(create_group, btn.text()))
        
        # Add connections for QuickLayer buttons
        for btn in self.quick_layer_buttons:
            btn.clicked.connect(partial(create_display_layer_group, btn.text()))
        
        # Add connections for quick prefix suffix buttons
        for btn in self.quick_prefix_suffix_btns:
            text = btn.text()
            if text.startswith("_"):  # If it starts with an underscore, consider it as a suffix
                btn.clicked.connect(partial(add_prefix_or_suffix, text, True))
            else:  # Otherwise consider it as a prefix
                btn.clicked.connect(partial(add_prefix_or_suffix, text, False))

        # Add connections for bottom buttons
        self.bottom_buttons[0].clicked.connect(pasted_Del)  # Connect "Remove pasted__" button
        self.bottom_buttons[1].clicked.connect(L_R)         # Connect "L_R" button

#====== Functions ======


def add_prefix_or_suffix(text, is_suffix):
    """
    Add prefix or suffix to selected objects
    
    Parameters:
    text (str): The prefix or suffix text to add
    is_suffix (bool): If True, add as suffix; if False, add as prefix
    
    Functions:
    - Check if there are selected objects
    - Add specified prefix or suffix to each selected object
    - Use sanitize_name function to clean new name
    - Try to rename object, display warning if failed
    - Display prompt message in Maya view after operation
    """
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("No object selected")
        return
    for obj in selection:
        new_name = f"{obj}{text}" if is_suffix else f"{text}{obj}"
        new_name = sanitize_name(new_name)
        try:
            cmds.rename(obj, new_name)
        except RuntimeError as e:
            cmds.warning(f"Unable to rename {obj}: {str(e)}")
    cmds.inViewMessage(amg=f'<span style="color:#fbca82;">Added {"suffix" if is_suffix else "prefix"}: {text}</span>', pos='botRight', fade=True)


def create_group(group_name):
    """
    Create a new group and put selected objects into it
    
    Parameters:
    group_name (str): Name of the new group to create
    
    Functions:
    - Check if there are selected objects
    - Use sanitize_name function to clean group name
    - Create a new empty group
    - Put selected objects into the newly created group
    - Display prompt message in Maya view after operation
    """
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("No object selected")
        return
    group_name = sanitize_name(group_name)
    group = cmds.group(name=group_name, empty=True)
    cmds.parent(selection, group)
    cmds.inViewMessage(amg=f'<span style="color:#fbca82;">Created group: {group_name}</span>', pos='botRight', fade=True)

def create_display_layer_group(layer_name=None):
    """
    Create a new display layer and add selected objects to that layer
    
    Parameters:
    layer_name (str, optional): Name of the new display layer to create. If not provided, a name will be automatically generated.
    
    Functions:
    - Get currently selected objects
    - If no layer name is provided, automatically generate one
    - Create a new empty display layer
    - If there are selected objects, add them to the newly created display layer
    - Maintain original object selection state
    - Display prompt message in Maya view after operation
    """
    selection = cmds.ls(selection=True)
    
    if not layer_name:
        layer_name = f"CustomLayer_{len(cmds.ls(type='displayLayer'))}"
    
    new_layer = cmds.createDisplayLayer(name=layer_name, empty=True)
    
    if selection:
        cmds.editDisplayLayerMembers(new_layer, selection)
        cmds.select(selection)  # Maintain original selection
    
    cmds.inViewMessage(amg=f'<span style="color:#fbca82;">Created display layer: {layer_name}</span>', pos='botRight', fade=True)

def sanitize_name(name):
    """
    Clean and validate object name
    
    Parameters:
    name (str): Name to be cleaned
    
    Returns:
    str: Cleaned name
    
    Functions:
    - Clean and validate input name
    - Ensure name complies with Maya naming rules
    - Custom name cleaning logic can be added here
    
    Note: Current function just returns the original name, you can add specific cleaning logic as needed
    """
    # Name cleaning logic can be added here if needed
    return name

def pasted_Del():
    mel.eval('searchReplaceNames "pasted__" "/" "hierarchy"')


def L_R():
    """
    Duplicate and mirror selected objects with '_L_' to create '_R_' versions
    
    Functions:
    - Freeze transformations
    - Duplicate selected objects
    - Mirror on X axis
    - Rename to '_R_' version
    """
    # Use semicolons to separate multiple MEL commands
    mel.eval('FreezeTransformations;' 
            'makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;'
            'ResetTransformations;'
            'duplicate -rr;'
            'scale -r -1 1 1;'
            'FreezeTransformations;'
            'makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;'
            'searchReplaceNames "_L_" "_R_" "hierarchy";')









#====== UI Functions ======

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def show():
    """
    Display UI for the editor rename module
    
    Functions:
    - Close and delete existing UI instance (if exists)
    - Create new UI instance and display
    """
    global rename_window_ui
    try:
        rename_window_ui.close()
        rename_window_ui.deleteLater()
    except:
        pass
    parent = maya_main_window()
    rename_window_ui = Quick_Rename_Module_UI(parent)
    rename_window_ui.show()
    rename_window_ui.raise_()
    rename_window_ui.activateWindow()


if __name__ == "__main__":
    show()
