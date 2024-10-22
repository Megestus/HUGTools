import importlib
import maya.cmds as cmds
import maya.mel as mel
import re
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import webbrowser
import os
import sys
import locale

# Define constants
HUGTOOL_VERSION = "1.0.1"
HUGTOOL_ICON = "MainUI.png"
HUGTOOL_TITLE = "HUGTOOL"
HUGTOOL_HELP_URL = "https://megestus.github.io/HUGTools/"

def get_script_path():
    """
    Get the directory path of the current script
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import other modules
import Toolbox.Editor_Rename_Module as Editor_Rename_Module
import Toolbox.Quick_Rename_Module as Quick_Rename_Module
import Toolbox.UVSetEditor_Module as UVSetEditor_Module
import Toolbox.NormalEdit_Module as NormalEdit_Module

# Function to get the system encoding
def get_system_encoding():
    return sys.getdefaultencoding()

# Function to choose the language based on system settings
def choose_language():
    encoding = get_system_encoding()
    system_language, _ = locale.getdefaultlocale()
    
    if encoding.lower() == 'utf-8' and system_language.startswith('zh'):
        return 'zh_CN'
    else:
        return 'en_US'

# Language dictionary
LANG = {
    'en_US': {
        "Display Control": "Display Control",
        "Normal": "Normal",
        "Normal Size:": "Normal Size:",
        "NormalEdit": "NormalEdit",
        "Edge Display Control": "Edge Display Control",
        "Soft": "Soft",
        "Hard": "Hard",
        "Select Hard Edges": "Select Hard Edges",
        "Select UV Border Edge": "Select UV Border Edge",
        "Planar Projection": "Planar Projection",
        "UV Layout by Hard Edges": "UV Layout by Hard Edges",
        "Crease Control": "Crease Control",
        "Crease Editor": "Crease Editor",
        "Create Crease Set by Name": "Create Crease Set by Name",
        "Crease V2": "Crease V2",
        "Crease V5": "Crease V5",
        "Toolbox": "Toolbox",
        "QuickRename": "QuickRename",
        "Rename": "Rename",
        "UVSetSwap": "UVSetSwap",
        "document": "document",
        "Help": "Help",
        "Switch Language": "Switch Language"
    },
    'zh_CN': {
        "Display Control": "显示控制",
        "Normal": "法线",
        "Normal Size:": "法线大小：",
        "NormalEdit": "法线编辑器",
        "Edge Display Control": "边显示控制",
        "Soft": "软边",
        "Hard": "硬边",
        "Select Hard Edges": "选择硬边",
        "Select UV Border Edge": "选择UV边界边",
        "Planar Projection": "平面投影",
        "UV Layout by Hard Edges": "基于硬边的UV布局",
        "Crease Control": "折痕控制",
        "Crease Editor": "折痕编辑器",
        "Create Crease Set by Name": "按名称创建折痕集",
        "Crease V2": "折痕 V2",
        "Crease V5": "折痕 V5",
        "Toolbox": "工具箱",
        "QuickRename": "快速重命名",
        "Rename": "重命名",
        "UVSetSwap": "UV集交换",
        "document": "文档",
        "Help": "帮助",
        "Switch Language": "切换语言"
    }
}

# Choose the current language
CURRENT_LANG = choose_language()

class HUGToolsUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(HUGToolsUI, self).__init__(parent)
        self.setWindowTitle(HUGTOOL_TITLE)
        self.setMinimumWidth(280)

        # Set window icon
        icon_path = os.path.join(get_script_path(), "Icons", HUGTOOL_ICON)
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        else:
            print(f"Warning: Icon file '{icon_path}' does not exist.")

        # Set window flags to always stay on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        # Initialize toggle_state
        self.toggle_state = False
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # Create help button
        self.help_btn = QtWidgets.QPushButton(LANG[CURRENT_LANG]["document"])
        self.help_btn.setToolTip(LANG[CURRENT_LANG]["Help"])
        self.help_btn.setFixedSize(60, 20)
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: gray;
                font-weight: bold;
            }
            QPushButton:hover {
                color: black;
            }
        """)

        # Create language switch button
        self.lang_btn = QtWidgets.QPushButton("EN" if CURRENT_LANG == 'zh_CN' else "中")
        self.lang_btn.setToolTip(LANG[CURRENT_LANG]["Switch Language"])
        self.lang_btn.setFixedSize(30, 20)
        self.lang_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: gray;
                font-weight: bold;
            }
            QPushButton:hover {
                color: black;
            }
        """)

        # Normal display module
        self.display_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Display Control"])
        self.toggle_normal_display_btn = RoundedButton("Normal", icon=QtGui.QIcon(":polyNormalSetToFace.png"))
        self.toggle_normal_display_btn.setMinimumSize(100, 40)
        self.toggle_normal_display_btn.setToolTip("Toggle normal display")
        self.normal_size_label = QtWidgets.QLabel("Normal Size:")
        self.normal_size_field = QtWidgets.QDoubleSpinBox()
        self.normal_size_field.setValue(0.4)
        self.normal_size_field.setRange(0.01, 10.0)
        self.normal_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.normal_size_slider.setRange(1, 1000)
        self.normal_size_slider.setValue(40)
        self.open_NormalEdit_btn = RoundedButton("NormalEdit", icon=QtGui.QIcon(":nodeGrapherModeAllLarge.png"))
        self.open_NormalEdit_btn.setToolTip("Open Normal Edit window") 


        # Edge display module
        self.edge_display_group = QtWidgets.QGroupBox("Edge Display Control")
        self.toggle_softEdge_btn = RoundedButton("Soft", icon=QtGui.QIcon(":polySoftEdge.png"))
        self.toggle_softEdge_btn.setMinimumSize(80, 40)
        self.toggle_softEdge_btn.setToolTip("Toggle soft edge display")
        self.toggle_hardedge_btn = RoundedButton("Hard", icon=QtGui.QIcon(":polyHardEdge.png"))
        self.toggle_hardedge_btn.setMinimumSize(80, 40)
        self.toggle_hardedge_btn.setToolTip("Toggle hard edge display")

        # select module
        self.select_hardedges_btn = RoundedButton(LANG[CURRENT_LANG]["Select Hard Edges"], icon=QtGui.QIcon(":UVTkEdge.png"))
        self.select_hardedges_btn.setToolTip("Select all hard edges on the mesh")
        self.select_uvborder_btn = RoundedButton(LANG[CURRENT_LANG]["Select UV Border Edge"], icon=QtGui.QIcon(":selectTextureBorders.png"))
        self.select_uvborder_btn.setToolTip("Select UV border edges")
        self.planar_projection_btn = RoundedButton(LANG[CURRENT_LANG]["Planar Projection"], icon=QtGui.QIcon(":polyCameraUVs.png"))
        self.planar_projection_btn.setToolTip("Apply planar UV projection")
        self.uvlayout_hardedges_btn = RoundedButton(LANG[CURRENT_LANG]["UV Layout by Hard Edges"], icon=QtGui.QIcon(":polyLayoutUV.png"))
        self.uvlayout_hardedges_btn.setToolTip("Perform UV layout based on hard edges")

        # crease module
        self.crease_set_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Crease Control"])
        self.open_crease_editor_btn = RoundedButton(LANG[CURRENT_LANG]["Crease Editor"], icon=QtGui.QIcon(":polyCrease.png"))
        self.create_fixed_crease_set_btn = RoundedButton(LANG[CURRENT_LANG]["Create Crease Set by Name"], icon=QtGui.QIcon(":polyCrease.png"))

        self.crease_1_btn = RoundedButton(LANG[CURRENT_LANG]["Crease V2"], icon=QtGui.QIcon(":polyCrease.png"))
        self.crease_3_btn = RoundedButton(LANG[CURRENT_LANG]["Crease V5"], icon=QtGui.QIcon(":polyCrease.png"))

        #toolbox
        self.Toolbox_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Toolbox"])
        self.Toolbox_QuickRename_btn = RoundedButton(LANG[CURRENT_LANG]["QuickRename"], icon=QtGui.QIcon(":annotation.png"))
        self.Toolbox_Rename_btn = RoundedButton(LANG[CURRENT_LANG]["Rename"], icon=QtGui.QIcon(":quickRename.png"))
        self.Toolbox_UVset_btn = RoundedButton(LANG[CURRENT_LANG]["UVSetSwap"], icon=QtGui.QIcon(":polyUVSetEditor.png"))





#======UI layout======
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(7)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # display control group layout
        display_layout = QtWidgets.QVBoxLayout()
        normal_display_layout = QtWidgets.QHBoxLayout()
        normal_display_layout.addWidget(self.toggle_normal_display_btn)
        normal_display_layout.addWidget(self.normal_size_label)
        normal_display_layout.addWidget(self.normal_size_field)
        display_layout.addLayout(normal_display_layout)
        display_layout.addWidget(self.normal_size_slider)
        display_layout.addWidget(self.open_NormalEdit_btn)
        self.display_group.setLayout(display_layout)

        # edge display control group layout
        edge_display_layout = QtWidgets.QVBoxLayout()
        edge_toggle_layout = QtWidgets.QHBoxLayout()
        edge_toggle_layout.addWidget(self.toggle_softEdge_btn)
        edge_toggle_layout.addWidget(self.toggle_hardedge_btn)
        edge_display_layout.addLayout(edge_toggle_layout)

        edge_display_layout.addWidget(self.select_hardedges_btn)
        edge_display_layout.addWidget(self.select_uvborder_btn)
        edge_display_layout.addWidget(self.planar_projection_btn)
        edge_display_layout.addWidget(self.uvlayout_hardedges_btn)

        self.edge_display_group.setLayout(edge_display_layout)

        # crease control group layout
        crease_layout = QtWidgets.QVBoxLayout()
        crease_layout.addWidget(self.open_crease_editor_btn)
        crease_layout.addWidget(self.create_fixed_crease_set_btn)

        # create a horizontal layout to hold the two Crease buttons
        crease_buttons_layout = QtWidgets.QHBoxLayout()
        crease_buttons_layout.addWidget(self.crease_1_btn)
        crease_buttons_layout.addWidget(self.crease_3_btn)

        # add horizontal layout to crease control group layout
        crease_layout.addLayout(crease_buttons_layout)

        self.crease_set_group.setLayout(crease_layout) 

        #toolbox group layout
        Toolbox_layout = QtWidgets.QVBoxLayout()
        Toolbox_layout.addWidget(self.Toolbox_QuickRename_btn)
        Toolbox_layout.addWidget(self.Toolbox_Rename_btn)
        Toolbox_layout.addWidget(self.Toolbox_UVset_btn)
        self.Toolbox_group.setLayout(Toolbox_layout)

        # add groups to main layout
        main_layout.addWidget(self.display_group)
        main_layout.addWidget(self.edge_display_group)
        main_layout.addWidget(self.crease_set_group)
        main_layout.addWidget(self.Toolbox_group)

        # create bottom layout
        bottom_layout = QtWidgets.QHBoxLayout()
        
        # add version information label
        version_label = QtWidgets.QLabel(f"v{HUGTOOL_VERSION}")
        version_label.setStyleSheet("color: gray; font-size: 10px;")
        bottom_layout.addWidget(version_label)
        
        # add a space, push the help and language buttons to the right
        bottom_layout.addStretch()
        
        # add help and language buttons
        bottom_layout.addWidget(self.help_btn)
        bottom_layout.addWidget(self.lang_btn)

        # add bottom layout to main layout
        main_layout.addLayout(bottom_layout)


#======UI connections====== 

    def create_connections(self):
        # connect normal display control
        self.toggle_normal_display_btn.clicked.connect(self.toggle_normal_display)
        self.normal_size_field.valueChanged.connect(self.set_normal_size_from_field)
        self.normal_size_slider.valueChanged.connect(self.set_normal_size_from_slider)
        self.open_NormalEdit_btn.clicked.connect(self.open_normal_edit)

        # connect other buttons
        self.toggle_softEdge_btn.clicked.connect(self.toggle_softEdge_display)
        self.toggle_hardedge_btn.clicked.connect(self.toggle_hardedge_display)
        self.select_uvborder_btn.clicked.connect(self.SelectUVBorderEdge)
        self.select_hardedges_btn.clicked.connect(self.select_hard_edges)
        self.uvlayout_hardedges_btn.clicked.connect(self.UVLayout_By_hardEdges)
        self.planar_projection_btn.clicked.connect(self.apply_planar_projection)

        self.create_fixed_crease_set_btn.clicked.connect(self.create_fixed_crease_set)
        self.open_crease_editor_btn.clicked.connect(self.open_crease_set_editor)
        self.crease_1_btn.clicked.connect(partial(self.apply_crease_preset, 1))
        self.crease_3_btn.clicked.connect(partial(self.apply_crease_preset, 3))

        self.Toolbox_QuickRename_btn.clicked.connect(self.quick_rename)
        self.Toolbox_Rename_btn.clicked.connect(self.rename_edit)
        self.Toolbox_UVset_btn.clicked.connect(self.UVset_swap) 

        # connect help button
        self.help_btn.clicked.connect(self.show_help)

        # connect language switch button
        self.lang_btn.clicked.connect(self.toggle_language)


#======function modules======
    

    #normal display module

    def set_normal_size_from_field(self, value):
        self.normal_size_slider.setValue(int(value * 100))
        self.set_normal_size(value)

    def set_normal_size_from_slider(self, value):
        size = value / 100.0
        self.normal_size_field.blockSignals(True)
        self.normal_size_field.setValue(size)
        self.normal_size_field.blockSignals(False)
        self.set_normal_size(size)

    def set_normal_size(self, value):
        cmds.polyOptions(sn=value)

    # toggle normal display
    def toggle(self):
        sel = cmds.ls(sl=True)
        if sel:
            new_size = self.normal_size_field.value()
            display_state = cmds.polyOptions(q=True, dn=True)[0]
            cmds.polyOptions(dn=not display_state, pt=True, sn=new_size)
        else:
            cmds.warning("No object selected!")




    # in the file top add this global variable
    toggle_state = False

    def toggle_softEdge_display(self):
        """
        Toggle soft edge display state
        
        Function:
        - Switch between displaying all edges and only soft edges
        """
        if self.toggle_state:
            cmds.polyOptions(allEdges=True)
            message = "All Edges"
        else:
            cmds.polyOptions(softEdge=True)
            message = "Soft Edges"
        
        self.toggle_state = not self.toggle_state
        cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)

    def toggle_hardedge_display(self):
        """
        Toggle hard edge display state
        
        Function:
        - Switch between displaying all edges and only hard edges
        """
        if self.toggle_state:
            cmds.polyOptions(allEdges=True)
            message = "All Edges"
        else:
            cmds.polyOptions(hardEdge=True)
            message = "Hard Edges"
        
        self.toggle_state = not self.toggle_state
        cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)


    def toggle_normal_display(self):
        sel = cmds.ls(sl=True)
        if sel:
            new_size = self.normal_size_field.value()
            display_state = cmds.polyOptions(q=True, dn=True)[0]
            cmds.polyOptions(dn=not display_state, pt=True, sn=new_size)
            message = "Normals On" if not display_state else "Normals Off"
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.warning("No object selected!")


    



    def SelectUVBorderEdge(*args):
        """
        Select UV border edges
        
        Function:
        - Select UV border edges
        - Switch to edge selection mode
        """
        cmds.SelectUVBorderComponents()
        cmds.selectMode(component=True)
        cmds.selectType(edge=True)
        cmds.inViewMessage(amg='<span style="color:#FFA500;">UV Border Edges</span>', pos='botRight', fade=True, fst=10, fad=1)


    def select_hard_edges(*args):
        """
        Select all hard edges of the currently selected object
        
        Function:
        - Switch to object mode
        - Select all hard edges
        - Return the list of selected hard edges
        """
        cmds.selectMode(object=True)

        selection = cmds.ls(selection=True, objectsOnly=True)
        if not selection:
            cmds.warning("No polygon object selected. Please select one or more polygon meshes.")
            return []
        
        cmds.select(clear=True)
        for obj in selection:
            cmds.select(obj, add=True)
        
        cmds.polySelectConstraint(mode=3, type=0x8000, smoothness=1)
        hard_edges = cmds.ls(selection=True, flatten=True)
        cmds.polySelectConstraint(mode=0)
        
        if hard_edges:
            cmds.inViewMessage(amg='<span style="color:#FFA500;">Hard Edges Selected</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.inViewMessage(amg='<span style="color:#FFA500;">No Hard Edges Found</span>', pos='botRight', fade=True, fst=10, fad=1)
        
        return hard_edges

    def UVLayout_By_hardEdges(self):
        """
        Perform a series of UV operations based on hard edges - optimize, unfold, and layout
        
        Functions:
        - Apply planar projection to selected objects
        - Select hard edges and perform UV cuts
        - Unfold, layout, and optimize UVs
        """

        cmds.selectMode(object=True)  # Force switch to object mode

        selection = cmds.ls(selection=True, objectsOnly=True)
        if not selection:
            cmds.warning("No polygon object selected. Please select one or more polygon meshes.")
            return

        for obj in selection:
            uv_sets = cmds.polyUVSet(obj, query=True, allUVSets=True)
            if not uv_sets:
                cmds.warning(f"{obj} has no valid UV sets. Skipping this object.")
                continue

            try:
                cmds.select(f"{obj}.f[*]", r=True)
                cmds.polyProjection(type='Planar', md='p')

                cmds.select(obj)
                hard_edges = self.select_hard_edges()
                if not hard_edges:
                    cmds.warning(f"{obj} has no hard edges. Skipping UV cut and unfold steps.")
                    continue

                cmds.select(hard_edges)
                cmds.polyMapCut(ch=1)
                cmds.u3dUnfold(obj, ite=1, p=0, bi=1, tf=1, ms=1024, rs=0)
                cmds.u3dLayout(obj, res=256, scl=1, spc=0.03125, mar=0.03125, box=(0, 1, 0, 1))
                cmds.u3dOptimize(obj, ite=1, pow=1, sa=1, bi=0, tf=1, ms=1024, rs=0)
            except Exception as e:
                cmds.warning(f"Error processing {obj}: {str(e)}")
            finally:
                cmds.select(obj)

        cmds.polySelectConstraint(sm=0)  # Reset selection mode
        cmds.selectMode(object=True)  # Ensure we end in object mode
        cmds.select(selection)
        cmds.undoInfo(cck=True)
        cmds.warning("UV operations based on hard edges completed.")

    def apply_planar_projection(self):
        """
        Apply planar projection to selected polygon objects
        
        Functions:
        - Select faces and apply planar projection
        - Handle exceptions and restore selection mode
        """
        cmds.selectMode(object=True)  # Force switch to object mode
        
        selection = cmds.ls(selection=True, objectsOnly=True)
        if selection:
            try:
                faces = [f"{obj}.f[*]" for obj in selection]
                cmds.select(faces, r=True)
                cmds.polyProjection(type='Planar', md='p')
                cmds.undoInfo(cck=True)
            except Exception as e:
                cmds.warning(f"Error applying planar projection: {e}")
            finally:
                cmds.polySelectConstraint(sm=0)  # Reset selection mode, ensure all edges can be selected
                cmds.select(selection, r=True)
                cmds.selectMode(object=True)  # Ensure we end in object mode
        else:
            cmds.warning("No polygon object selected. Please select one or more polygon meshes.")



    # ===============crease set functions==============  


    def get_object_name(self):
        """
        Get the name of the object to which the currently selected edges belong,
        and determine the crease set name based on rules
        """
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            return ""
        
        # Get the first selected item
        first_selected = selection[0]
        
        # If an edge is selected, extract the object name
        if '.e[' in first_selected:
            obj_name = first_selected.split('.')[0]
        else:
            obj_name = first_selected
        
        # Use regular expression to match the part before _Lb, _La, or _temp
        match = re.match(r"(.+?)(?:_Lb|_La|_temp)?$", obj_name)
        if match:
            base_name = match.group(1)
        else:
            base_name = obj_name
        
        # If the base name doesn't have _Lb, _La, or _temp suffix, add _set suffix
        if base_name == obj_name:
            return f"{base_name}_set"
        else:
            return base_name

    def create_fixed_crease_set(self):
        """
        Create or update a crease set with a fixed crease value of 5
        
        Functions:
        - Create a new crease set or update an existing one when edges are selected
        - Automatically generate crease set name based on object naming rules
        - Add selected edges to the crease set
        - Apply a fixed crease value of 5 to all edges in the crease set
        
        Usage:
        1. Select one or more edges
        2. Click the "Create Crease Set by Name" button
        
        Notes:
        - If no edges are selected, a warning message will be displayed
        - If a matching crease set already exists, it will be used
        - A confirmation message will be displayed upon completion
        """
        selection = cmds.ls(selection=True, flatten=True)
        if not selection:
            cmds.warning("No object selected. Please select one or more edges.")
            return

        # Filter out edges
        edges = [edge for edge in selection if '.e[' in edge]
        
        if not edges:
            cmds.warning("No edges selected. Please select one or more edges.")
            return

        base_name = self.get_object_name()
        
        # Find all potentially matching crease sets
        all_crease_sets = cmds.ls(type="creaseSet")
        matching_crease_sets = [cs for cs in all_crease_sets if cs.startswith(base_name)]

        if matching_crease_sets:
            crease_set_name = matching_crease_sets[0]
            cmds.warning(f"Using existing crease set: {crease_set_name}")
        else:
            # Create a new creaseSet node
            crease_set_name = cmds.createNode('creaseSet', name=base_name)
            cmds.warning(f"Created new crease set: {crease_set_name}")

        edges_added = False
        for edge in edges:
            # Check if this edge is already in the crease set
            existing_edges = cmds.sets(crease_set_name, query=True) or []
            if edge not in existing_edges:
                # Add the new edge to the crease set
                cmds.sets(edge, add=crease_set_name)
                edges_added = True

        if edges_added:
            # Apply a fixed crease value of 5 to the entire crease set
            all_edges = cmds.sets(crease_set_name, query=True) or []
            cmds.polyCrease(all_edges, value=5.0)
            cmds.select(crease_set_name)
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">Updated crease set: {crease_set_name}, crease value set to 5, but needs refresh</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">No new edges added to crease set: {crease_set_name}</span>', pos='botRight', fade=True, fst=10, fad=1)

    def open_crease_set_editor(self):
        """
        Open Maya's Crease Set Editor
        """
        try:
            mel.eval('python ("from maya.app.general import creaseSetEditor; creaseSetEditor.showCreaseSetEditor()")')
        except Exception as e:
            cmds.warning(f"Unable to open Crease Set Editor: {str(e)}")
            # If the above method fails, consider opening the regular component editor or displaying an error message
            # cmds.ComponentEditor()

    def apply_crease_preset(self, presetnum):
        """
        Apply crease preset
        
        Functions:
        - Apply specified crease preset to selected objects or edges
        - Update smooth level and display settings
        """
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(selection=True, long=True, flatten=True)
            
            if not sel:
                cmds.warning("No objects or edges selected.")
                return

            processed_objects = {}

            for obj in sel:
                try:
                    # Check if it's an edge component
                    if '.e[' in obj:
                        mesh = obj.split('.')[0]
                        if mesh not in processed_objects:
                            processed_objects[mesh] = []
                        processed_objects[mesh].append(obj)
                    elif cmds.objectType(obj) == 'transform':
                        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
                        for shape in shapes:
                            if cmds.objectType(shape) == 'mesh':
                                processed_objects[shape] = None
                    elif cmds.objectType(obj) == 'mesh':
                        processed_objects[obj] = None
                except Exception as e:
                    cmds.warning(f"Error processing object {obj}: {str(e)}")

            for mesh, edges in processed_objects.items():
                self.apply_crease_to_mesh(mesh, presetnum, edges)

            cmds.select(sel, replace=True)
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">Applied Crease Preset {presetnum}</span>', pos='botRight', fade=True, fst=10, fad=1)
        finally:
            cmds.undoInfo(closeChunk=True)

    def apply_crease_to_mesh(self, mesh, presetnum, specific_edges=None):
        """
        Apply crease to a single mesh or specific edges
        
        Functions:
        - Apply crease value
        - Set smooth level
        - Set display smooth mesh
        """
        try:
            crease_value = {1: 2.0, 2: 3.0, 3: 5.0}.get(presetnum, 0.0)
            
            if specific_edges:
                # Apply crease value to specific edges
                cmds.polyCrease(specific_edges, value=crease_value)
            else:
                # Apply crease value to all edges
                cmds.polyCrease(f"{mesh}.e[*]", value=crease_value)
            
            # Query crease values for all edges
            all_crease_values = cmds.polyCrease(f"{mesh}.e[*]", query=True, value=True) or [0]
            max_crease = max(all_crease_values)
            
            # Set smooth level
            smooth_level = max(int(max_crease) + 1, 1)
            cmds.setAttr(f'{mesh}.smoothLevel', smooth_level)
            
            # Set display smooth mesh
            cmds.setAttr(f'{mesh}.displaySmoothMesh', 2)
        except Exception as e:
            cmds.warning(f"Error processing mesh {mesh}: {str(e)}")





    #external function modules

    def open_normal_edit(self):
        importlib.reload(NormalEdit_Module)
        NormalEdit_Module.show_ui()


    #============toolbox function modules===============


    def rename_edit(self):
        importlib.reload(Editor_Rename_Module)
        Editor_Rename_Module.show()

    def UVset_swap(self):
        importlib.reload(UVSetEditor_Module)
        UVSetEditor_Module.show()

    def quick_rename(self):
        importlib.reload(Quick_Rename_Module)
        Quick_Rename_Module.show()




    def show_help(self):
        # Open the help URL in the default web browser
        webbrowser.open(HUGTOOL_HELP_URL)

    def toggle_language(self):
        global CURRENT_LANG
        CURRENT_LANG = 'en_US' if CURRENT_LANG == 'zh_CN' else 'zh_CN'
        self.lang_btn.setText("EN" if CURRENT_LANG == 'zh_CN' else "中")
        self.retranslate_ui()
        
        QtWidgets.QToolTip.showText(
            self.lang_btn.mapToGlobal(QtCore.QPoint(0, -30)),
            "Language switched" if CURRENT_LANG == 'en_US' else "语言已切换",
            self.lang_btn
        )

    def retranslate_ui(self):
        # Update all UI elements with the new language
        self.setWindowTitle(HUGTOOL_TITLE)
        self.help_btn.setText(LANG[CURRENT_LANG]["document"])
import importlib
import maya.cmds as cmds
import maya.mel as mel
import re
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import webbrowser
import os
import sys
import locale

# Define version constant
HUGTOOL_VERSION = "1.0.1"

def get_script_path():
    """
    Get the directory path of the current script
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import other modules
import Toolbox.Editor_Rename_Module as Editor_Rename_Module
import Toolbox.Quick_Rename_Module as Quick_Rename_Module
import Toolbox.UVSetEditor_Module as UVSetEditor_Module
import Toolbox.NormalEdit_Module as NormalEdit_Module

# Function to get the system encoding
def get_system_encoding():
    return sys.getdefaultencoding()

# Function to choose the language based on system settings
def choose_language():
    encoding = get_system_encoding()
    system_language, _ = locale.getdefaultlocale()
    
    if encoding.lower() == 'utf-8' and system_language.startswith('zh'):
        return 'zh_CN'
    else:
        return 'en_US'

# Language dictionary
LANG = {
    'en_US': {
        "Display Control": "Display Control",
        "Normal": "Normal",
        "Normal Size:": "Normal Size:",
        "NormalEdit": "NormalEdit",
        "Edge Display Control": "Edge Display Control",
        "Soft": "Soft",
        "Hard": "Hard",
        "Select Hard Edges": "Select Hard Edges",
        "Select UV Border Edge": "Select UV Border Edge",
        "Planar Projection": "Planar Projection",
        "UV Layout by Hard Edges": "UV Layout by Hard Edges",
        "Crease Control": "Crease Control",
        "Crease Editor": "Crease Editor",
        "Create Crease Set by Name": "Create Crease Set by Name",
        "Crease V2": "Crease V2",
        "Crease V5": "Crease V5",
        "Toolbox": "Toolbox",
        "QuickRename": "QuickRename",
        "Rename": "Rename",
        "UVSetSwap": "UVSetSwap",
        "document": "document",
        "Help": "Help",
        "Switch Language": "Switch Language"
    },
    'zh_CN': {
        "Display Control": "显示控制",
        "Normal": "法线",
        "Normal Size:": "法线大小：",
        "NormalEdit": "法线编辑",
        "Edge Display Control": "边显示控制",
        "Soft": "软边",
        "Hard": "硬边",
        "Select Hard Edges": "选择硬边",
        "Select UV Border Edge": "选择UV边界边",
        "Planar Projection": "平面投影",
        "UV Layout by Hard Edges": "基于硬边的UV布局",
        "Crease Control": "折痕控制",
        "Crease Editor": "折痕编辑器",
        "Create Crease Set by Name": "按名称创建折痕集",
        "Crease V2": "折痕 V2",
        "Crease V5": "折痕 V5",
        "Toolbox": "工具箱",
        "QuickRename": "快速重命名",
        "Rename": "重命名",
        "UVSetSwap": "UV集交换",
        "document": "文档",
        "Help": "帮助",
        "Switch Language": "切换语言"
    }
}

# Choose the current language
CURRENT_LANG = choose_language()

class HUGToolsUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(HUGToolsUI, self).__init__(parent)
        self.setWindowTitle("HUGTOOL")
        self.setMinimumWidth(280)

        # Set window icon
        icon_path = os.path.join(get_script_path(), "Icons", "MainUI.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        else:
            print(f"Warning: Icon file '{icon_path}' does not exist.")

        # Set window flags to always stay on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        # Initialize toggle_state
        self.toggle_state = False
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # Create help button
        self.help_btn = QtWidgets.QPushButton(LANG[CURRENT_LANG]["document"])
        self.help_btn.setToolTip(LANG[CURRENT_LANG]["Help"])
        self.help_btn.setFixedSize(60, 20)
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: gray;
                font-weight: bold;
            }
            QPushButton:hover {
                color: black;
            }
        """)

        # Create language switch button
        self.lang_btn = QtWidgets.QPushButton("EN" if CURRENT_LANG == 'zh_CN' else "中")
        self.lang_btn.setToolTip(LANG[CURRENT_LANG]["Switch Language"])
        self.lang_btn.setFixedSize(30, 20)
        self.lang_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: gray;
                font-weight: bold;
            }
            QPushButton:hover {
                color: black;
            }
        """)

        # Normal display module
        self.display_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Display Control"])
        self.toggle_normal_display_btn = RoundedButton("Normal", icon=QtGui.QIcon(":polyNormalSetToFace.png"))
        self.toggle_normal_display_btn.setMinimumSize(100, 40)
        self.toggle_normal_display_btn.setToolTip("Toggle normal display")
        self.normal_size_label = QtWidgets.QLabel("Normal Size:")
        self.normal_size_field = QtWidgets.QDoubleSpinBox()
        self.normal_size_field.setValue(0.4)
        self.normal_size_field.setRange(0.01, 10.0)
        self.normal_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.normal_size_slider.setRange(1, 1000)
        self.normal_size_slider.setValue(40)
        self.open_NormalEdit_btn = RoundedButton("NormalEdit", icon=QtGui.QIcon(":nodeGrapherModeAllLarge.png"))
        self.open_NormalEdit_btn.setToolTip("Open Normal Edit window") 


        # Edge display module
        self.edge_display_group = QtWidgets.QGroupBox("Edge Display Control")
        self.toggle_softEdge_btn = RoundedButton("Soft", icon=QtGui.QIcon(":polySoftEdge.png"))
        self.toggle_softEdge_btn.setMinimumSize(80, 40)
        self.toggle_softEdge_btn.setToolTip("Toggle soft edge display")
        self.toggle_hardedge_btn = RoundedButton("Hard", icon=QtGui.QIcon(":polyHardEdge.png"))
        self.toggle_hardedge_btn.setMinimumSize(80, 40)
        self.toggle_hardedge_btn.setToolTip("Toggle hard edge display")

        # select module
        self.select_hardedges_btn = RoundedButton(LANG[CURRENT_LANG]["Select Hard Edges"], icon=QtGui.QIcon(":UVTkEdge.png"))
        self.select_hardedges_btn.setToolTip("Select all hard edges on the mesh")
        self.select_uvborder_btn = RoundedButton(LANG[CURRENT_LANG]["Select UV Border Edge"], icon=QtGui.QIcon(":selectTextureBorders.png"))
        self.select_uvborder_btn.setToolTip("Select UV border edges")
        self.planar_projection_btn = RoundedButton(LANG[CURRENT_LANG]["Planar Projection"], icon=QtGui.QIcon(":polyCameraUVs.png"))
        self.planar_projection_btn.setToolTip("Apply planar UV projection")
        self.uvlayout_hardedges_btn = RoundedButton(LANG[CURRENT_LANG]["UV Layout by Hard Edges"], icon=QtGui.QIcon(":polyLayoutUV.png"))
        self.uvlayout_hardedges_btn.setToolTip("Perform UV layout based on hard edges")

        # crease module
        self.crease_set_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Crease Control"])
        self.open_crease_editor_btn = RoundedButton(LANG[CURRENT_LANG]["Crease Editor"], icon=QtGui.QIcon(":polyCrease.png"))
        self.create_fixed_crease_set_btn = RoundedButton(LANG[CURRENT_LANG]["Create Crease Set by Name"], icon=QtGui.QIcon(":polyCrease.png"))

        self.crease_1_btn = RoundedButton(LANG[CURRENT_LANG]["Crease V2"], icon=QtGui.QIcon(":polyCrease.png"))
        self.crease_3_btn = RoundedButton(LANG[CURRENT_LANG]["Crease V5"], icon=QtGui.QIcon(":polyCrease.png"))

        #toolbox
        self.Toolbox_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Toolbox"])
        self.Toolbox_QuickRename_btn = RoundedButton(LANG[CURRENT_LANG]["QuickRename"], icon=QtGui.QIcon(":annotation.png"))
        self.Toolbox_Rename_btn = RoundedButton(LANG[CURRENT_LANG]["Rename"], icon=QtGui.QIcon(":quickRename.png"))
        self.Toolbox_UVset_btn = RoundedButton(LANG[CURRENT_LANG]["UVSetSwap"], icon=QtGui.QIcon(":polyUVSetEditor.png"))





#======UI layout======
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(7)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # display control group layout
        display_layout = QtWidgets.QVBoxLayout()
        normal_display_layout = QtWidgets.QHBoxLayout()
        normal_display_layout.addWidget(self.toggle_normal_display_btn)
        normal_display_layout.addWidget(self.normal_size_label)
        normal_display_layout.addWidget(self.normal_size_field)
        display_layout.addLayout(normal_display_layout)
        display_layout.addWidget(self.normal_size_slider)
        display_layout.addWidget(self.open_NormalEdit_btn)
        self.display_group.setLayout(display_layout)

        # edge display control group layout
        edge_display_layout = QtWidgets.QVBoxLayout()
        edge_toggle_layout = QtWidgets.QHBoxLayout()
        edge_toggle_layout.addWidget(self.toggle_softEdge_btn)
        edge_toggle_layout.addWidget(self.toggle_hardedge_btn)
        edge_display_layout.addLayout(edge_toggle_layout)

        edge_display_layout.addWidget(self.select_hardedges_btn)
        edge_display_layout.addWidget(self.select_uvborder_btn)
        edge_display_layout.addWidget(self.planar_projection_btn)
        edge_display_layout.addWidget(self.uvlayout_hardedges_btn)

        self.edge_display_group.setLayout(edge_display_layout)

        # crease control group layout
        crease_layout = QtWidgets.QVBoxLayout()
        crease_layout.addWidget(self.open_crease_editor_btn)
        crease_layout.addWidget(self.create_fixed_crease_set_btn)

        # create a horizontal layout to hold the two Crease buttons
        crease_buttons_layout = QtWidgets.QHBoxLayout()
        crease_buttons_layout.addWidget(self.crease_1_btn)
        crease_buttons_layout.addWidget(self.crease_3_btn)

        # add horizontal layout to crease control group layout
        crease_layout.addLayout(crease_buttons_layout)

        self.crease_set_group.setLayout(crease_layout) 

        #toolbox group layout
        Toolbox_layout = QtWidgets.QVBoxLayout()
        Toolbox_layout.addWidget(self.Toolbox_QuickRename_btn)
        Toolbox_layout.addWidget(self.Toolbox_Rename_btn)
        Toolbox_layout.addWidget(self.Toolbox_UVset_btn)
        self.Toolbox_group.setLayout(Toolbox_layout)

        # add groups to main layout
        main_layout.addWidget(self.display_group)
        main_layout.addWidget(self.edge_display_group)
        main_layout.addWidget(self.crease_set_group)
        main_layout.addWidget(self.Toolbox_group)

        # create bottom layout
        bottom_layout = QtWidgets.QHBoxLayout()
        
        # add version information label
        version_label = QtWidgets.QLabel(f"v{HUGTOOL_VERSION}")
        version_label.setStyleSheet("color: gray; font-size: 10px;")
        bottom_layout.addWidget(version_label)
        
        # add a space, push the help and language buttons to the right
        bottom_layout.addStretch()
        
        # add help and language buttons
        bottom_layout.addWidget(self.help_btn)
        bottom_layout.addWidget(self.lang_btn)

        # add bottom layout to main layout
        main_layout.addLayout(bottom_layout)


#======UI connections====== 

    def create_connections(self):
        # connect normal display control
        self.toggle_normal_display_btn.clicked.connect(self.toggle_normal_display)
        self.normal_size_field.valueChanged.connect(self.set_normal_size_from_field)
        self.normal_size_slider.valueChanged.connect(self.set_normal_size_from_slider)
        self.open_NormalEdit_btn.clicked.connect(self.open_normal_edit)

        # connect other buttons
        self.toggle_softEdge_btn.clicked.connect(self.toggle_softEdge_display)
        self.toggle_hardedge_btn.clicked.connect(self.toggle_hardedge_display)
        self.select_uvborder_btn.clicked.connect(self.SelectUVBorderEdge)
        self.select_hardedges_btn.clicked.connect(self.select_hard_edges)
        self.uvlayout_hardedges_btn.clicked.connect(self.UVLayout_By_hardEdges)
        self.planar_projection_btn.clicked.connect(self.apply_planar_projection)

        self.create_fixed_crease_set_btn.clicked.connect(self.create_fixed_crease_set)
        self.open_crease_editor_btn.clicked.connect(self.open_crease_set_editor)
        self.crease_1_btn.clicked.connect(partial(self.apply_crease_preset, 1))
        self.crease_3_btn.clicked.connect(partial(self.apply_crease_preset, 3))

        self.Toolbox_QuickRename_btn.clicked.connect(self.quick_rename)
        self.Toolbox_Rename_btn.clicked.connect(self.rename_edit)
        self.Toolbox_UVset_btn.clicked.connect(self.UVset_swap) 

        # connect help button
        self.help_btn.clicked.connect(self.show_help)

        # connect language switch button
        self.lang_btn.clicked.connect(self.toggle_language)


#======function modules======
    

    #normal display module

    def set_normal_size_from_field(self, value):
        self.normal_size_slider.setValue(int(value * 100))
        self.set_normal_size(value)

    def set_normal_size_from_slider(self, value):
        size = value / 100.0
        self.normal_size_field.blockSignals(True)
        self.normal_size_field.setValue(size)
        self.normal_size_field.blockSignals(False)
        self.set_normal_size(size)

    def set_normal_size(self, value):
        cmds.polyOptions(sn=value)

    # toggle normal display
    def toggle(self):
        sel = cmds.ls(sl=True)
        if sel:
            new_size = self.normal_size_field.value()
            display_state = cmds.polyOptions(q=True, dn=True)[0]
            cmds.polyOptions(dn=not display_state, pt=True, sn=new_size)
        else:
            cmds.warning("No object selected!")




    # in the file top add this global variable
    toggle_state = False

    def toggle_softEdge_display(self):
        """
        Toggle soft edge display state
        
        Function:
        - Switch between displaying all edges and only soft edges
        """
        if self.toggle_state:
            cmds.polyOptions(allEdges=True)
            message = "All Edges"
        else:
            cmds.polyOptions(softEdge=True)
            message = "Soft Edges"
        
        self.toggle_state = not self.toggle_state
        cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)

    def toggle_hardedge_display(self):
        """
        Toggle hard edge display state
        
        Function:
        - Switch between displaying all edges and only hard edges
        """
        if self.toggle_state:
            cmds.polyOptions(allEdges=True)
            message = "All Edges"
        else:
            cmds.polyOptions(hardEdge=True)
            message = "Hard Edges"
        
        self.toggle_state = not self.toggle_state
        cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)


    def toggle_normal_display(self):
        sel = cmds.ls(sl=True)
        if sel:
            new_size = self.normal_size_field.value()
            display_state = cmds.polyOptions(q=True, dn=True)[0]
            cmds.polyOptions(dn=not display_state, pt=True, sn=new_size)
            message = "Normals On" if not display_state else "Normals Off"
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.warning("No object selected!")


    



    def SelectUVBorderEdge(*args):
        """
        Select UV border edges
        
        Function:
        - Select UV border edges
        - Switch to edge selection mode
        """
        cmds.SelectUVBorderComponents()
        cmds.selectMode(component=True)
        cmds.selectType(edge=True)
        cmds.inViewMessage(amg='<span style="color:#FFA500;">UV Border Edges</span>', pos='botRight', fade=True, fst=10, fad=1)


    def select_hard_edges(*args):
        """
        Select all hard edges of the currently selected object
        
        Function:
        - Switch to object mode
        - Select all hard edges
        - Return the list of selected hard edges
        """
        cmds.selectMode(object=True)

        selection = cmds.ls(selection=True, objectsOnly=True)
        if not selection:
            cmds.warning("No polygon object selected. Please select one or more polygon meshes.")
            return []
        
        cmds.select(clear=True)
        for obj in selection:
            cmds.select(obj, add=True)
        
        cmds.polySelectConstraint(mode=3, type=0x8000, smoothness=1)
        hard_edges = cmds.ls(selection=True, flatten=True)
        cmds.polySelectConstraint(mode=0)
        
        if hard_edges:
            cmds.inViewMessage(amg='<span style="color:#FFA500;">Hard Edges Selected</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.inViewMessage(amg='<span style="color:#FFA500;">No Hard Edges Found</span>', pos='botRight', fade=True, fst=10, fad=1)
        
        return hard_edges

    def UVLayout_By_hardEdges(self):
        """
        Perform a series of UV operations based on hard edges - optimize, unfold, and layout
        
        Functions:
        - Apply planar projection to selected objects
        - Select hard edges and perform UV cuts
        - Unfold, layout, and optimize UVs
        """

        cmds.selectMode(object=True)  # Force switch to object mode

        selection = cmds.ls(selection=True, objectsOnly=True)
        if not selection:
            cmds.warning("No polygon object selected. Please select one or more polygon meshes.")
            return

        for obj in selection:
            uv_sets = cmds.polyUVSet(obj, query=True, allUVSets=True)
            if not uv_sets:
                cmds.warning(f"{obj} has no valid UV sets. Skipping this object.")
                continue

            try:
                cmds.select(f"{obj}.f[*]", r=True)
                cmds.polyProjection(type='Planar', md='p')

                cmds.select(obj)
                hard_edges = self.select_hard_edges()
                if not hard_edges:
                    cmds.warning(f"{obj} has no hard edges. Skipping UV cut and unfold steps.")
                    continue

                cmds.select(hard_edges)
                cmds.polyMapCut(ch=1)
                cmds.u3dUnfold(obj, ite=1, p=0, bi=1, tf=1, ms=1024, rs=0)
                cmds.u3dLayout(obj, res=256, scl=1, spc=0.03125, mar=0.03125, box=(0, 1, 0, 1))
                cmds.u3dOptimize(obj, ite=1, pow=1, sa=1, bi=0, tf=1, ms=1024, rs=0)
            except Exception as e:
                cmds.warning(f"Error processing {obj}: {str(e)}")
            finally:
                cmds.select(obj)

        cmds.polySelectConstraint(sm=0)  # Reset selection mode
        cmds.selectMode(object=True)  # Ensure we end in object mode
        cmds.select(selection)
        cmds.undoInfo(cck=True)
        cmds.warning("UV operations based on hard edges completed.")

    def apply_planar_projection(self):
        """
        Apply planar projection to selected polygon objects
        
        Functions:
        - Select faces and apply planar projection
        - Handle exceptions and restore selection mode
        """
        cmds.selectMode(object=True)  # Force switch to object mode
        
        selection = cmds.ls(selection=True, objectsOnly=True)
        if selection:
            try:
                faces = [f"{obj}.f[*]" for obj in selection]
                cmds.select(faces, r=True)
                cmds.polyProjection(type='Planar', md='p')
                cmds.undoInfo(cck=True)
            except Exception as e:
                cmds.warning(f"Error applying planar projection: {e}")
            finally:
                cmds.polySelectConstraint(sm=0)  # Reset selection mode, ensure all edges can be selected
                cmds.select(selection, r=True)
                cmds.selectMode(object=True)  # Ensure we end in object mode
        else:
            cmds.warning("No polygon object selected. Please select one or more polygon meshes.")



    # ===============crease set functions==============  


    def get_object_name(self):
        """
        Get the name of the object to which the currently selected edges belong,
        and determine the crease set name based on rules
        """
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            return ""
        
        # Get the first selected item
        first_selected = selection[0]
        
        # If an edge is selected, extract the object name
        if '.e[' in first_selected:
            obj_name = first_selected.split('.')[0]
        else:
            obj_name = first_selected
        
        # Use regular expression to match the part before _Lb, _La, or _temp
        match = re.match(r"(.+?)(?:_Lb|_La|_temp)?$", obj_name)
        if match:
            base_name = match.group(1)
        else:
            base_name = obj_name
        
        # If the base name doesn't have _Lb, _La, or _temp suffix, add _set suffix
        if base_name == obj_name:
            return f"{base_name}_set"
        else:
            return base_name

    def create_fixed_crease_set(self):
        """
        Create or update a crease set with a fixed crease value of 5
        
        Functions:
        - Create a new crease set or update an existing one when edges are selected
        - Automatically generate crease set name based on object naming rules
        - Add selected edges to the crease set
        - Apply a fixed crease value of 5 to all edges in the crease set
        
        Usage:
        1. Select one or more edges
        2. Click the "Create Crease Set by Name" button
        
        Notes:
        - If no edges are selected, a warning message will be displayed
        - If a matching crease set already exists, it will be used
        - A confirmation message will be displayed upon completion
        """
        selection = cmds.ls(selection=True, flatten=True)
        if not selection:
            cmds.warning("No object selected. Please select one or more edges.")
            return

        # Filter out edges
        edges = [edge for edge in selection if '.e[' in edge]
        
        if not edges:
            cmds.warning("No edges selected. Please select one or more edges.")
            return

        base_name = self.get_object_name()
        
        # Find all potentially matching crease sets
        all_crease_sets = cmds.ls(type="creaseSet")
        matching_crease_sets = [cs for cs in all_crease_sets if cs.startswith(base_name)]

        if matching_crease_sets:
            crease_set_name = matching_crease_sets[0]
            cmds.warning(f"Using existing crease set: {crease_set_name}")
        else:
            # Create a new creaseSet node
            crease_set_name = cmds.createNode('creaseSet', name=base_name)
            cmds.warning(f"Created new crease set: {crease_set_name}")

        edges_added = False
        for edge in edges:
            # Check if this edge is already in the crease set
            existing_edges = cmds.sets(crease_set_name, query=True) or []
            if edge not in existing_edges:
                # Add the new edge to the crease set
                cmds.sets(edge, add=crease_set_name)
                edges_added = True

        if edges_added:
            # Apply a fixed crease value of 5 to the entire crease set
            all_edges = cmds.sets(crease_set_name, query=True) or []
            cmds.polyCrease(all_edges, value=5.0)
            cmds.select(crease_set_name)
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">Updated crease set: {crease_set_name}, crease value set to 5, but needs refresh</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">No new edges added to crease set: {crease_set_name}</span>', pos='botRight', fade=True, fst=10, fad=1)

    def open_crease_set_editor(self):
        """
        Open Maya's Crease Set Editor
        """
        try:
            mel.eval('python ("from maya.app.general import creaseSetEditor; creaseSetEditor.showCreaseSetEditor()")')
        except Exception as e:
            cmds.warning(f"Unable to open Crease Set Editor: {str(e)}")
            # If the above method fails, consider opening the regular component editor or displaying an error message
            # cmds.ComponentEditor()

    def apply_crease_preset(self, presetnum):
        """
        Apply crease preset
        
        Functions:
        - Apply specified crease preset to selected objects or edges
        - Update smooth level and display settings
        """
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(selection=True, long=True, flatten=True)
            
            if not sel:
                cmds.warning("No objects or edges selected.")
                return

            processed_objects = {}

            for obj in sel:
                try:
                    # Check if it's an edge component
                    if '.e[' in obj:
                        mesh = obj.split('.')[0]
                        if mesh not in processed_objects:
                            processed_objects[mesh] = []
                        processed_objects[mesh].append(obj)
                    elif cmds.objectType(obj) == 'transform':
                        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
                        for shape in shapes:
                            if cmds.objectType(shape) == 'mesh':
                                processed_objects[shape] = None
                    elif cmds.objectType(obj) == 'mesh':
                        processed_objects[obj] = None
                except Exception as e:
                    cmds.warning(f"Error processing object {obj}: {str(e)}")

            for mesh, edges in processed_objects.items():
                self.apply_crease_to_mesh(mesh, presetnum, edges)

            cmds.select(sel, replace=True)
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">Applied Crease Preset {presetnum}</span>', pos='botRight', fade=True, fst=10, fad=1)
        finally:
            cmds.undoInfo(closeChunk=True)

    def apply_crease_to_mesh(self, mesh, presetnum, specific_edges=None):
        """
        Apply crease to a single mesh or specific edges
        
        Functions:
        - Apply crease value
        - Set smooth level
        - Set display smooth mesh
        """
        try:
            crease_value = {1: 2.0, 2: 3.0, 3: 5.0}.get(presetnum, 0.0)
            
            if specific_edges:
                # Apply crease value to specific edges
                cmds.polyCrease(specific_edges, value=crease_value)
            else:
                # Apply crease value to all edges
                cmds.polyCrease(f"{mesh}.e[*]", value=crease_value)
            
            # Query crease values for all edges
            all_crease_values = cmds.polyCrease(f"{mesh}.e[*]", query=True, value=True) or [0]
            max_crease = max(all_crease_values)
            
            # Set smooth level
            smooth_level = max(int(max_crease) + 1, 1)
            cmds.setAttr(f'{mesh}.smoothLevel', smooth_level)
            
            # Set display smooth mesh
            cmds.setAttr(f'{mesh}.displaySmoothMesh', 2)
        except Exception as e:
            cmds.warning(f"Error processing mesh {mesh}: {str(e)}")





    #external function modules

    def open_normal_edit(self):
        importlib.reload(NormalEdit_Module)
        NormalEdit_Module.show_ui()


    #============toolbox function modules===============


    def rename_edit(self):
        importlib.reload(Editor_Rename_Module)
        Editor_Rename_Module.show()

    def UVset_swap(self):
        importlib.reload(UVSetEditor_Module)
        UVSetEditor_Module.show()

    def quick_rename(self):
        importlib.reload(Quick_Rename_Module)
        Quick_Rename_Module.show()




    def show_help(self):
        # Specify the URL of the website you want to open
        help_url = "https://megestus.github.io/HUGTools/"
        webbrowser.open(help_url)

    def toggle_language(self):
        global CURRENT_LANG
        CURRENT_LANG = 'en_US' if CURRENT_LANG == 'zh_CN' else 'zh_CN'
        self.lang_btn.setText("EN" if CURRENT_LANG == 'zh_CN' else "中")
        self.retranslate_ui()
        
        QtWidgets.QToolTip.showText(
            self.lang_btn.mapToGlobal(QtCore.QPoint(0, -30)),
            "Language switched" if CURRENT_LANG == 'en_US' else "语言已切换",
            self.lang_btn
        )

    def retranslate_ui(self):
        # Update all UI elements with the new language
        self.setWindowTitle("HUGTOOL")
        self.help_btn.setText(LANG[CURRENT_LANG]["document"])
        self.help_btn.setToolTip(LANG[CURRENT_LANG]["Help"])
        self.lang_btn.setToolTip(LANG[CURRENT_LANG]["Switch Language"])
        
        # Update all group boxes, labels, and buttons
        self.display_group.setTitle(LANG[CURRENT_LANG]["Display Control"])
        self.toggle_normal_display_btn.setText(LANG[CURRENT_LANG]["Normal"])
        self.normal_size_label.setText(LANG[CURRENT_LANG]["Normal Size:"])
        self.open_NormalEdit_btn.setText(LANG[CURRENT_LANG]["NormalEdit"])
        
        # ... (update all other UI elements)


def show():
    global main_window
    try:
        main_window.close()
        main_window.deleteLater()
    except:
        pass
    
    main_window = HUGToolsUI()
    main_window.show()

if __name__ == "__main__":
    show()

