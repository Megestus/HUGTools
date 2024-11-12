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
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

# Define constants
HUGTOOL_VERSION = "1.2.2 Beta"
HUGTOOL_ICON = "HUG3.png"
HUGTOOL_TITLE = "HUGTOOL"
HUGTOOL_HELP_URL = "https://megestus.github.io/HUGTools/"

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

def get_script_path():
    """
    Get the directory path of the current script
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import other modules
import Module.Editor_Rename_Module as Editor_Rename_Module
import Module.Quick_Rename_Module as Quick_Rename_Module
import Module.UVSetEditor_Module as UVSetEditor_Module
import Module.NormalEdit_Module as NormalEdit_Module
import Module.More_Tools_Module as More_Tools_Module
import Module.UnBevel_Module as UnBevel_Module
from Toolbox.QuickExport import QuickExport
from Toolbox.ViewCapture import screen_shot

# Function to get the system encoding
def get_system_encoding():
    encoding = sys.getdefaultencoding()
    if encoding.lower() == 'ascii':
        # in some Windows systems, the default encoding may be reported as ASCII
        # but it may actually be using CP437 or other encodings
        import locale
        encoding = locale.getpreferredencoding()
    return encoding

# based on system encoding, default use english
CURRENT_LANG = 'en_US'

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
        "MapBorders":"MapBorders",
        "Select Hard Edges": "Hard Edges",
        "Select UV Border Edge": "UV Border",
        "Planar Projection": "Planar UV",
        "UV Layout by Hard Edges": "UV Layout",
        "Editor": "Editor",
        "Crease Editor": "Crease Editor",
        "Create Crease Set by Name": "Create Crease Set by Name",
        "Crease V2": "Crease V2",
        "Crease V5": "Crease V5",
        "Toolbox": "Toolbox",
        "QuickRename": "QuickRename",
        "Rename": "Rename",
        "UVSetSwap": "UVSetSwap",
        "QuickExport": "QuickExport",
        "ScreenShot": "ScreenShot",
        "document": "document",
        "Help": "Help",
        "Switch Language": "Switch Language",
        "More": "More",
        "More Tools": "More Tools",
        "QuickRename_tip": "Quick rename tool for batch renaming objects",
        "Rename_tip": "Advanced rename editor with more options",
        "UVSetSwap_tip": "UV set editor for managing and swapping UV sets",
        "QuickExport_tip": "Quick export tool for exporting objects",
        "ScreenShot_tip": "Capture viewport screenshots",
        "More_tip": "More independent tools",
        "Select Control": "Select Control",
        "Crease": "Crease",
        "Crease_tip": "Toggle crease edge display",
        "UnBevel": "UnBevel",
        "UnBevel_tip": "Tool for unbeveling edges",
        "Distance": "Distance",
        "Distance_tip": "Calculate edge length",
        "EdgeToCurve": "Edge2Curve",
        "EdgeToCurve_tip": "Convert edges to NURBS curves",
        "UV Editor": "UV Editor",
        "UV Editor_tip": "Open UV Editor window",
        "Please select edges": "Please select edges",
        "Please select edges to measure": "Please select edges to measure",
        "Length": "Length",
    },
    'zh_CN': {
        "Display Control": "显示控制",
        "Normal": "法线",
        "Normal Size:": "法线大小",
        "NormalEdit": "法线编辑器",
        "Edge Display Control": "边显示控制",
        "Soft": "软边",
        "Hard": "硬边",
        "MapBorders":"UV边界",
        "Select Hard Edges": "选择硬边",
        "Select UV Border Edge": "选择UV边界边",
        "Planar Projection": "平面投影",
        "UV Layout by Hard Edges": "基于硬边UV布局",
        "Editor": "编辑器",
        "Crease Editor": "折痕编辑器",
        "Create Crease Set by Name": "按名称创建折痕集",
        "Crease V2": "折痕 V2",
        "Crease V5": "折痕 V5",
        "Toolbox": "工具箱",
        "QuickRename": "快速重命名",
        "Rename": "重命名",
        "UVSetSwap": "UV集交换",
        "QuickExport": "快速导出",
        "ScreenShot": "截图",
        "document": "文档",
        "Help": "帮助",
        "Switch Language": "切换语言",
        "More": "更多",
        "More Tools": "更多工具",
        "QuickRename_tip": "批量重命名工具",
        "Rename_tip": "高级重命名编辑器",
        "UVSetSwap_tip": "UV集编辑器，用于管理和交换UV集",
        "QuickExport_tip": "快速导出工具",
        "ScreenShot_tip": "视口截图工具",
        "More_tip": "更多独立工具",
        "Select Control": "选择控制",
        "Crease": "折边",
        "Crease_tip": "切换折边显示",
        "UnBevel": "倒角还原",
        "UnBevel_tip": "边缘倒角还原工具",
        "Distance": "测距",
        "Distance_tip": "计算边长",
        "EdgeToCurve": "边转曲线",
        "EdgeToCurve_tip": "将边转换为NURBS曲线",
        "UV Editor": "UV编辑器",
        "UV Editor_tip": "打开UV编辑器窗口",
        "Please select edges": "请选择边",
        "Please select edges to measure": "请选择要测量的边",
        "Length": "长度",

    }
}

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class HUGToolsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(HUGToolsWindow, self).__init__(parent)
        self.setWindowTitle(HUGTOOL_TITLE)
        self.setMinimumWidth(280)

        # set window icon
        icon_path = os.path.join(get_script_path(), "Icons", HUGTOOL_ICON)
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        else:
            print(f"Warning: Icon file '{icon_path}' does not exist.")

        # set window flags to always stay on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        
        # initialize toggle_state
        self.toggle_state = False
        self.crease_edge_state = False  
        
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
        self.lang_btn = QtWidgets.QPushButton("EN" if CURRENT_LANG == 'zh_CN' else "ZH")
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

        # Edge display module
        self.toggle_softEdge_btn = RoundedButton("Soft", icon=QtGui.QIcon(":polySoftEdge.png"))
        self.toggle_softEdge_btn.setMinimumSize(80, 40)
        self.toggle_softEdge_btn.setToolTip("Toggle soft edge display")
        self.toggle_hardedge_btn = RoundedButton("Hard", icon=QtGui.QIcon(":polyHardEdge.png"))
        self.toggle_hardedge_btn.setMinimumSize(80, 40)
        self.toggle_hardedge_btn.setToolTip("Toggle hard edge display")
        self.toggle_crease_edge_btn = RoundedButton(LANG[CURRENT_LANG]["Crease"], icon=QtGui.QIcon(":polyCrease.png"))
        self.toggle_crease_edge_btn.setMinimumSize(80, 40)
        self.toggle_crease_edge_btn.setToolTip(LANG[CURRENT_LANG]["Crease_tip"])
        self.toggle_set_display_map_borders_btn = RoundedButton(LANG[CURRENT_LANG]["MapBorders"], icon=QtGui.QIcon(":UVEditorTextureBorder.png"))    ## not truee
        self.toggle_set_display_map_borders_btn.setMinimumSize(80, 40)
        self.toggle_softEdge_btn.setToolTip("Toggle MapBorders edge display")

        # select module
        self.select_group = QtWidgets.QGroupBox("Select Control")
        self.select_hardedges_btn = RoundedButton(LANG[CURRENT_LANG]["Select Hard Edges"], icon=QtGui.QIcon(":UVTkEdge.png"))
        self.select_hardedges_btn.setToolTip("Select all hard edges on the mesh")
        self.select_uvborder_btn = RoundedButton(LANG[CURRENT_LANG]["Select UV Border Edge"], icon=QtGui.QIcon(":selectTextureBorders.png"))
        self.select_uvborder_btn.setToolTip("Select UV border edges")
        self.planar_projection_btn = RoundedButton(LANG[CURRENT_LANG]["Planar Projection"], icon=QtGui.QIcon(":polyCameraUVs.png"))
        self.planar_projection_btn.setToolTip("Apply planar UV projection")
        self.uvlayout_hardedges_btn = RoundedButton(LANG[CURRENT_LANG]["UV Layout by Hard Edges"], icon=QtGui.QIcon(":polyLayoutUV.png"))
        self.uvlayout_hardedges_btn.setToolTip("Perform UV layout based on hard edges")
        self.edge_to_curve_btn = RoundedButton(LANG[CURRENT_LANG]["EdgeToCurve"], icon=QtGui.QIcon(":polyEdgeToCurves.png"))
        self.edge_to_curve_btn.setToolTip(LANG[CURRENT_LANG]["EdgeToCurve_tip"])

        # crease module
        self.editor_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Editor"])
        self.open_NormalEdit_btn = RoundedButton(LANG[CURRENT_LANG]["NormalEdit"], icon=QtGui.QIcon(":nodeGrapherModeAllLarge.png"))
        self.open_NormalEdit_btn.setToolTip("Open Normal Edit window")
        self.open_crease_editor_btn = RoundedButton(LANG[CURRENT_LANG]["Crease Editor"], icon=QtGui.QIcon(":polyCrease.png"))
        self.open_uv_editor_btn = RoundedButton(LANG[CURRENT_LANG]["UV Editor"], icon=QtGui.QIcon(":textureEditor.png"))
        self.open_uv_editor_btn.setToolTip(LANG[CURRENT_LANG]["UV Editor_tip"])

        # ===  this function is under development ===
        # self.create_fixed_crease_set_btn = RoundedButton(LANG[CURRENT_LANG]["Create Crease Set by Name"], icon=QtGui.QIcon(":polyCrease.png"))
        # self.crease_1_btn = RoundedButton(LANG[CURRENT_LANG]["Crease V2"], icon=QtGui.QIcon(":polyCrease.png"))
        # self.crease_3_btn = RoundedButton(LANG[CURRENT_LANG]["Crease V5"], icon=QtGui.QIcon(":polyCrease.png"))


        #toolbox
        self.Toolbox_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Toolbox"])
        self.Toolbox_QuickRename_btn = RoundedButton(LANG[CURRENT_LANG]["QuickRename"], icon=QtGui.QIcon(":annotation.png"))
        self.Toolbox_QuickRename_btn.setToolTip(LANG[CURRENT_LANG]["QuickRename_tip"])
        self.Toolbox_Rename_btn = RoundedButton(LANG[CURRENT_LANG]["Rename"], icon=QtGui.QIcon(":quickRename.png"))
        self.Toolbox_Rename_btn.setToolTip(LANG[CURRENT_LANG]["Rename_tip"])
        self.Toolbox_UVset_btn = RoundedButton(LANG[CURRENT_LANG]["UVSetSwap"], icon=QtGui.QIcon(":polyUVSetEditor.png"))
        self.Toolbox_UVset_btn.setToolTip(LANG[CURRENT_LANG]["UVSetSwap_tip"])
        self.Toolbox_QuickExport_btn = RoundedButton(LANG[CURRENT_LANG]["QuickExport"], icon=QtGui.QIcon(":sourceScript.png"))
        self.Toolbox_QuickExport_btn.setToolTip(LANG[CURRENT_LANG]["QuickExport_tip"])
        self.Toolbox_UnBevel_btn = RoundedButton(LANG[CURRENT_LANG]["UnBevel"], icon=QtGui.QIcon(":polyBevel.png"))
        self.Toolbox_UnBevel_btn.setToolTip(LANG[CURRENT_LANG]["UnBevel_tip"])
        self.Toolbox_ScreenShot_btn = RoundedButton(LANG[CURRENT_LANG]["ScreenShot"], icon=QtGui.QIcon(":out_snapshot.png"))
        self.Toolbox_ScreenShot_btn.setToolTip(LANG[CURRENT_LANG]["ScreenShot_tip"])
        self.Toolbox_More_btn = RoundedButton(LANG[CURRENT_LANG]["More"], icon=QtGui.QIcon(":loadPreset.png"))
        self.Toolbox_More_btn.setToolTip(LANG[CURRENT_LANG]["More_tip"])
        self.Toolbox_CalcDistance_btn = RoundedButton("Distance", icon=QtGui.QIcon(":distanceDim.png"))
        self.Toolbox_CalcDistance_btn.setToolTip("Calculate edge length")
        self.Toolbox_CalcDistance_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.Toolbox_CalcDistance_btn.setMinimumSize(100, 40)
        self.Toolbox_CalcDistance_btn.setFixedHeight(40)

        # set size policy and size for all toolbox buttons
        toolbox_buttons = [
            self.Toolbox_QuickRename_btn,
            self.Toolbox_Rename_btn,
            self.Toolbox_UVset_btn,
            self.Toolbox_QuickExport_btn,
            self.Toolbox_ScreenShot_btn,
            self.Toolbox_UnBevel_btn,
            self.Toolbox_More_btn,
            self.Toolbox_CalcDistance_btn
        ]
        
        for btn in toolbox_buttons:
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            btn.setMinimumSize(100, 40)
            btn.setFixedHeight(40)  # fixed height to 40





#======UI layout======
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(7)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # display control group layout
        display_layout = QtWidgets.QVBoxLayout()
        
        # Normal controls
        normal_display_layout = QtWidgets.QHBoxLayout()
        normal_display_layout.addWidget(self.toggle_normal_display_btn)
        normal_display_layout.addWidget(self.normal_size_label)
        normal_display_layout.addWidget(self.normal_size_field)
        display_layout.addLayout(normal_display_layout)
        display_layout.addWidget(self.normal_size_slider)
        
        # Edge display controls
        edge_toggle_layout = QtWidgets.QGridLayout()
        edge_toggle_layout.addWidget(self.toggle_softEdge_btn, 0, 0)
        edge_toggle_layout.addWidget(self.toggle_hardedge_btn, 0, 1)
        edge_toggle_layout.addWidget(self.toggle_crease_edge_btn, 1, 0)
        edge_toggle_layout.addWidget(self.toggle_set_display_map_borders_btn, 1, 1)
        display_layout.addLayout(edge_toggle_layout)
        
        self.display_group.setLayout(display_layout)

        # select control group layout
        select_layout = QtWidgets.QGridLayout()
        select_layout.addWidget(self.select_hardedges_btn, 0, 0)
        select_layout.addWidget(self.select_uvborder_btn, 0, 1)
        select_layout.addWidget(self.edge_to_curve_btn, 1, 0)
        select_layout.addWidget(self.planar_projection_btn, 1, 1)
        select_layout.addWidget(self.uvlayout_hardedges_btn, 2, 0)
        self.select_group.setLayout(select_layout)

        # crease control group layout
        editor_layout = QtWidgets.QVBoxLayout()
        editor_layout.addWidget(self.open_NormalEdit_btn)
        editor_layout.addWidget(self.open_crease_editor_btn)
        editor_layout.addWidget(self.open_uv_editor_btn)
        self.editor_group.setLayout(editor_layout)

        #toolbox group layout
        Toolbox_layout = QtWidgets.QGridLayout()
        Toolbox_layout.addWidget(self.Toolbox_QuickRename_btn, 0, 0)
        Toolbox_layout.addWidget(self.Toolbox_Rename_btn, 0, 1)
        Toolbox_layout.addWidget(self.Toolbox_QuickExport_btn, 1, 0)
        Toolbox_layout.addWidget(self.Toolbox_UVset_btn, 1, 1)
        Toolbox_layout.addWidget(self.Toolbox_UnBevel_btn, 2, 0)
        Toolbox_layout.addWidget(self.Toolbox_ScreenShot_btn, 2, 1)
        Toolbox_layout.addWidget(self.Toolbox_CalcDistance_btn, 3, 0)
        Toolbox_layout.addWidget(self.Toolbox_More_btn, 3, 1)

        self.Toolbox_group.setLayout(Toolbox_layout)

        # add groups to main layout
        main_layout.addWidget(self.display_group)
        main_layout.addWidget(self.editor_group)
        main_layout.addWidget(self.select_group)
        main_layout.addWidget(self.Toolbox_group)

        # change bottom layout
        bottom_layout = QtWidgets.QHBoxLayout()
        
        # create icon label
        icon_label = QtWidgets.QLabel()
        icon_path = os.path.join(get_script_path(), "Icons", HUGTOOL_ICON)
        if os.path.exists(icon_path):
            icon = QtGui.QPixmap(icon_path).scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            icon_label.setPixmap(icon)
        else:
            print(f"Warning: Icon file '{icon_path}' does not exist.")
        
        # add icon label to bottom layout
        bottom_layout.addWidget(icon_label)
        
        # add version information label
        version_label = QtWidgets.QLabel(f"v{HUGTOOL_VERSION}")
        version_label.setStyleSheet("color: gray; font-size: 10px;")
        bottom_layout.addWidget(version_label)
        
        # add a stretchable space to push the help and language buttons to the right
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
        self.toggle_crease_edge_btn.clicked.connect(self.toggle_crease_edge_display)
        self.toggle_set_display_map_borders_btn.clicked.connect(self.toggle_set_display_map_borders)

        # select buttons
        self.select_uvborder_btn.clicked.connect(self.SelectUVBorderEdge2)
        self.select_hardedges_btn.clicked.connect(self.select_hard_edges)
        self.uvlayout_hardedges_btn.clicked.connect(self.UVLayout_By_hardEdges)
        self.planar_projection_btn.clicked.connect(self.apply_planar_projection)


        self.open_crease_editor_btn.clicked.connect(self.open_crease_set_editor)
        self.open_uv_editor_btn.clicked.connect(self.open_uv_editor)

        # ===  this function is under development ===
        # self.create_fixed_crease_set_btn.clicked.connect(self.create_fixed_crease_set)
        # self.crease_1_btn.clicked.connect(partial(self.apply_crease_preset, 1))
        # self.crease_3_btn.clicked.connect(partial(self.apply_crease_preset, 3))

        self.Toolbox_QuickRename_btn.clicked.connect(self.quick_rename)
        self.Toolbox_Rename_btn.clicked.connect(self.rename_edit)
        self.Toolbox_UVset_btn.clicked.connect(self.UVset_swap) 
        self.Toolbox_QuickExport_btn.clicked.connect(self.quick_export)
        self.Toolbox_ScreenShot_btn.clicked.connect(self.screen_shot)
        self.Toolbox_UnBevel_btn.clicked.connect(self.unbevel_tool)
        self.Toolbox_More_btn.clicked.connect(self.show_more_tools)
        self.Toolbox_CalcDistance_btn.clicked.connect(self.calculate_distance)

        # connect help button
        self.help_btn.clicked.connect(self.show_help)

        # connect language switch button
        self.lang_btn.clicked.connect(self.toggle_language)

        # connect edge to curve button
        self.edge_to_curve_btn.clicked.connect(self.convert_edge_to_curve)





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

    # ======= toggle display module ======= 

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


    def toggle_crease_edge_display(self):
        self.crease_edge_state = not self.crease_edge_state
        if self.crease_edge_state:
            cmds.polyOptions(displayCreaseEdge=True)
            message = "Crease Edges On"
        else:
            cmds.polyOptions(displayCreaseEdge=False)
            message = "Crease Edges Off"
        
        cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)



    #  new add border display
    #  border_size
    # def set_display_borders(enable=True, border_size=None,):
    #     if border_size is not None:
    #         cmds.polyOptions(displayBorder=enable, sb=border_size)
    #     else:
    #         cmds.polyOptions(displayBorder=enable)

    # def toggle_adjust_border_size(value):
    #     """Adjusts the border size based on slider value."""
    #     set_display_borders(True, border_size=value)

    def toggle_set_display_map_borders(*args):
        current_state = cmds.polyOptions(q=True, displayMapBorder=True,)[0]
        cmds.polyOptions(displayMapBorder=not current_state)
        # message = "Map Borders On" if not current_state else "Map Borders Off"
        # cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)




    # ======= select module ======= 

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
        cmds.polySelectConstraint(sm=0)


    def SelectUVBorderEdge2(*args):
        """
        Ues MEL Select UV border edges
    
        """
        mel.eval('''
            // 选择当前选择的对象的UV边界
            expandPolyGroupSelection;
            // 根据需要调整UV边界的硬边属性
            polyUVBorderHard;
            // 选择UV边界组件
            selectUVBorderComponents {} "" 1 ;
        ''')
        cmds.inViewMessage(amg='<span style="color:#FFA500;">UV Border Edges</span>', pos='botRight', fade=True, fst=10, fad=1)



    def select_hard_edges(*args):
        """
        Select all hard edges of the currently selected object
        """
        cmds.polySelectConstraint(m=3, t=0x8000, sm=1)
        sels = cmds.ls(sl=1)
        cmds.polySelectConstraint(sm=0)   # Reset selection mode, ensure all edges can be selected
        
        if sels:
            message = '<span style="color:#FFA500;">Hard Edges Selected</span>'
            cmds.inViewMessage(amg=message, pos='botRight', fade=True, fst=10, fad=1)
        
        cmds.select(sels)
        # switch to edge selection mode
        cmds.selectMode(component=True)
        cmds.selectType(edge=True)


    def convert_edge_to_curve(self):
        """Convert selected edges to NURBS curves and move pivot to center"""
        try:
            # check selection
            selection = cmds.ls(selection=True, flatten=True)
            edges = [edge for edge in selection if '.e[' in edge]
            
            if not edges:
                cmds.warning("Please select edges to convert")
                return
                
            # execute conversion
            curves = mel.eval('polyToCurve -form 2 -degree 3 -conformToSmoothMeshPreview 1')
            
            if curves:
                # select new created curves
                cmds.select(curves)
                
                # move pivot to center of curves
                for curve in curves:
                    # get curve's bounding box
                    bbox = cmds.exactWorldBoundingBox(curve)
                    # calculate center point
                    center_x = (bbox[0] + bbox[3]) / 2
                    center_y = (bbox[1] + bbox[4]) / 2
                    center_z = (bbox[2] + bbox[5]) / 2
                    # move pivot to center point
                    cmds.xform(curve, pivots=[center_x, center_y, center_z])
                
                message = "Converted to curves and centered pivot"
                cmds.inViewMessage(amg=f'<span style="color:#48AAB5">{message}</span>', 
                                 pos='topCenter', fade=True, fst=3)
        except Exception as e:
            cmds.warning(f"Error converting edges to curves: {str(e)}")






    def UVLayout_By_hardEdges(self):
        """
        Perform a series of UV operations based on hard edges - optimize, unfold, and layout
        """
        cmds.selectMode(object=True)  # Force switch to object mode

        selection = cmds.ls(selection=True, objectsOnly=True)
        if not selection:
            cmds.inViewMessage(
                amg='<span style="color:#FFA500;">请选择一条或多条边</span>', 
                pos='botRight',
                fade=True,
                fst=10, 
                fad=1
            )
            return

        for obj in selection:
            uv_sets = cmds.polyUVSet(obj, query=True, allUVSets=True)
            if not uv_sets:
                cmds.warning(f"{obj} has no valid UV sets. Skipping this object.")
                continue

            try:
                # 1. apply planar projection
                cmds.select(f"{obj}.f[*]", r=True)
                cmds.polyProjection(type='Planar', md='p')

                # 2. select hard edges
                cmds.select(obj)
                cmds.polySelectConstraint(m=3, t=0x8000, sm=1)
                hard_edges = cmds.ls(selection=True, flatten=True)
                cmds.polySelectConstraint(sm=0)  # reset selection constraint

                if not hard_edges:
                    cmds.warning(f"{obj} has no hard edges. Skipping UV cut and unfold steps.")
                    continue

                # 3. cut uv along hard edges
                cmds.select(hard_edges)
                cmds.polyMapCut(ch=1)

                # 4. unfold and layout uv
                cmds.select(obj)
                cmds.u3dUnfold(ite=1, p=0, bi=1, tf=1, ms=1024, rs=0)
                cmds.u3dLayout(res=256, scl=1, spc=0.03125, mar=0.03125, box=(0, 1, 0, 1))
                cmds.u3dOptimize(ite=1, pow=1, sa=1, bi=0, tf=1, ms=1024, rs=0)

            except Exception as e:
                cmds.warning(f"Error processing {obj}: {str(e)}")
            finally:
                cmds.select(obj)

        # final cleanup
        cmds.polySelectConstraint(sm=0)  # reset selection constraint
        cmds.selectMode(object=True)  # ensure ending in object mode

        # display completion message
        message = '<span style="color:#FFA500;">UV layout completed</span>'
        cmds.inViewMessage(amg=message, pos='botRight', fade=True, fst=10, fad=1)


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


    def open_uv_editor(self):
        """Open UV Editor window"""
        try:
            mel.eval('TextureViewWindow')
        except Exception as e:
            cmds.warning(f"Error opening UV Editor: {str(e)}")




    #============toolbox function modules===============

    def quick_rename(self):
        importlib.reload(Quick_Rename_Module)
        Quick_Rename_Module.show()


    def rename_edit(self):
        importlib.reload(Editor_Rename_Module)
        Editor_Rename_Module.show()

    def UVset_swap(self):
        importlib.reload(UVSetEditor_Module)
        UVSetEditor_Module.show()


    def quick_export(self):
        importlib.reload(QuickExport)
        QuickExport.show()

    def screen_shot(self):
        importlib.reload(screen_shot)
        screen_shot.show()

    def unbevel_tool(self):
        """Launch UnBevel tool UI"""
        importlib.reload(UnBevel_Module)
        UnBevel_Module.show_ui()

    def calculate_distance(self):
        """Calculate the total length of selected edges"""
        # Get selected edges
        selection = cmds.ls(selection=True, flatten=True)
        if not selection:
            cmds.inViewMessage(
                amg=f'<span style="color:#FFA500;">{LANG[CURRENT_LANG]["Please select edges"]}</span>', 
                pos='botRight',
                fade=True,
                fst=10, 
                fad=1
            )
            return
            
        # Filter for edges only
        edges = [edge for edge in selection if '.e[' in edge]
        if not edges:
            cmds.warning(LANG[CURRENT_LANG]["Please select edges to measure"])
            return
            
        # Calculate total length
        total_length = 0
        unit = cmds.currentUnit(q=True, linear=True)
        
        try:
            for edge in edges:
                # Create temporary curve from edge
                temp_curve = cmds.createNode('curveFromMeshEdge')
                mesh = edge.split('.')[0]
                edge_id = edge.split('[')[1].split(']')[0]
                
                cmds.setAttr(f"{temp_curve}.ihi", 1)
                cmds.connectAttr(f"{mesh}.worldMesh[0]", f"{temp_curve}.inputMesh")
                cmds.setAttr(f"{temp_curve}.edgeIndex[0]", int(edge_id))
                
                # Create curve info node to get length
                curve_info = cmds.createNode('curveInfo')
                cmds.connectAttr(f"{temp_curve}.outputCurve", f"{curve_info}.inputCurve")
                
                # Get length
                length = cmds.getAttr(f"{curve_info}.arcLength")
                total_length += length
                
                # Clean up temporary nodes
                cmds.delete(temp_curve, curve_info)
                
            # Display result
            message = f'{LANG[CURRENT_LANG]["Length"]}: <hl>{total_length:.3f}</hl> {unit}'
            cmds.inViewMessage(amg=f'<span style="color:#48AAB5">{message}</span>', pos='topCenter', fade=True, fst=3)
            
        except Exception as e:
            cmds.warning(f"Error calculating length: {str(e)}")

    def show_more_tools(self):
        importlib.reload(More_Tools_Module)
        More_Tools_Module.show()







    def show_help(self):
        # Specify the URL of the website you want to open
        help_url = "https://megestus.github.io/HUGTools/"
        webbrowser.open(help_url)

    def toggle_language(self):
        global CURRENT_LANG
        CURRENT_LANG = 'en_US' if CURRENT_LANG == 'zh_CN' else 'zh_CN'
        self.lang_btn.setText("EN" if CURRENT_LANG == 'zh_CN' else "CN")
        self.retranslate_ui()
        
        QtWidgets.QToolTip.showText(
            self.lang_btn.mapToGlobal(QtCore.QPoint(0, -30)),
            "Language switched" if CURRENT_LANG == 'en_US' else "语言已切换",
            self.lang_btn
        )

    def retranslate_ui(self):
        # update all UI elements
        self.setWindowTitle("HUGTOOL")
        self.help_btn.setText(LANG[CURRENT_LANG]["document"])
        self.help_btn.setToolTip(LANG[CURRENT_LANG]["Help"])
        self.lang_btn.setToolTip(LANG[CURRENT_LANG]["Switch Language"])
        
        # update all group boxes, labels and buttons
        self.display_group.setTitle(LANG[CURRENT_LANG]["Display Control"])
        self.toggle_normal_display_btn.setText(LANG[CURRENT_LANG]["Normal"])
        self.normal_size_label.setText(LANG[CURRENT_LANG]["Normal Size:"])
        self.open_NormalEdit_btn.setText(LANG[CURRENT_LANG]["NormalEdit"])
        
        self.editor_group.setTitle(LANG[CURRENT_LANG]["Editor"])
        self.open_crease_editor_btn.setText(LANG[CURRENT_LANG]["Crease Editor"])
        self.open_uv_editor_btn.setText(LANG[CURRENT_LANG]["UV Editor"])
        
        # more controls 
        # self.create_fixed_crease_set_btn.setText(LANG[CURRENT_LANG]["Create Crease Set by Name"])
        # self.crease_1_btn.setText(LANG[CURRENT_LANG]["Crease V2"])
        # self.crease_3_btn.setText(LANG[CURRENT_LANG]["Crease V5"])
        
        self.Toolbox_group.setTitle(LANG[CURRENT_LANG]["Toolbox"])
        self.Toolbox_QuickRename_btn.setText(LANG[CURRENT_LANG]["QuickRename"])
        self.Toolbox_Rename_btn.setText(LANG[CURRENT_LANG]["Rename"])
        self.Toolbox_UVset_btn.setText(LANG[CURRENT_LANG]["UVSetSwap"])
        self.Toolbox_QuickExport_btn.setText(LANG[CURRENT_LANG]["QuickExport"])
        self.Toolbox_ScreenShot_btn.setText(LANG[CURRENT_LANG]["ScreenShot"])
        self.Toolbox_UnBevel_btn.setText(LANG[CURRENT_LANG]["UnBevel"])
        self.Toolbox_More_btn.setText(LANG[CURRENT_LANG]["More"])
        self.Toolbox_CalcDistance_btn.setText(LANG[CURRENT_LANG]["Distance"])
        self.Toolbox_CalcDistance_btn.setToolTip(LANG[CURRENT_LANG]["Distance_tip"])

        self.select_group.setTitle(LANG[CURRENT_LANG]["Select Control"])
        self.select_hardedges_btn.setText(LANG[CURRENT_LANG]["Select Hard Edges"])
        self.select_uvborder_btn.setText(LANG[CURRENT_LANG]["Select UV Border Edge"])
        self.planar_projection_btn.setText(LANG[CURRENT_LANG]["Planar Projection"])
        self.uvlayout_hardedges_btn.setText(LANG[CURRENT_LANG]["UV Layout by Hard Edges"])

        # more controls tooltip
        self.Toolbox_QuickRename_btn.setToolTip(LANG[CURRENT_LANG]["QuickRename_tip"])
        self.Toolbox_Rename_btn.setToolTip(LANG[CURRENT_LANG]["Rename_tip"])
        self.Toolbox_UVset_btn.setToolTip(LANG[CURRENT_LANG]["UVSetSwap_tip"])
        self.Toolbox_QuickExport_btn.setToolTip(LANG[CURRENT_LANG]["QuickExport_tip"])
        self.Toolbox_ScreenShot_btn.setToolTip(LANG[CURRENT_LANG]["ScreenShot_tip"])
        self.Toolbox_UnBevel_btn.setToolTip(LANG[CURRENT_LANG]["UnBevel_tip"])
        self.Toolbox_More_btn.setToolTip(LANG[CURRENT_LANG]["More_tip"])
        self.Toolbox_CalcDistance_btn.setToolTip(LANG[CURRENT_LANG]["Distance_tip"])

        self.toggle_crease_edge_btn.setText(LANG[CURRENT_LANG]["Crease"])
        self.toggle_crease_edge_btn.setToolTip(LANG[CURRENT_LANG]["Crease_tip"])

        self.edge_to_curve_btn.setText(LANG[CURRENT_LANG]["EdgeToCurve"])
        self.edge_to_curve_btn.setToolTip(LANG[CURRENT_LANG]["EdgeToCurve_tip"])

        self.open_uv_editor_btn.setText(LANG[CURRENT_LANG]["UV Editor"])
        self.open_uv_editor_btn.setToolTip(LANG[CURRENT_LANG]["UV Editor_tip"])




def show():
    global hug_tools_window
    try:
        hug_tools_window.close()
        hug_tools_window.deleteLater()
    except:
        pass
    parent = maya_main_window()
    hug_tools_window = HUGToolsWindow(parent)
    hug_tools_window.show()
    hug_tools_window.raise_()
    hug_tools_window.activateWindow()

if __name__ == "__main__":
    show()







