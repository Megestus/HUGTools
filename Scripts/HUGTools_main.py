import importlib
import maya.cmds as cmds
import maya.mel as mel
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import webbrowser
import os
import sys
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from pathlib import Path
from Toolbox.LOD import LOD
import subprocess

# Define constants
HUGTOOL_VERSION = "1.3.0 Beta"
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
    - Unified size policy
    """
    def __init__(self, text="", icon=None):
        super(RoundedButton, self).__init__(text)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(24, 24))
            
        # Set unified size policy for all RoundedButton instances
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setMinimumSize(100, 40)
        self.setFixedHeight(38)
        
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
    Get the Scripts directory path of the HUGTools using Path object
    """
    current_file = Path(__file__).resolve()
    scripts_dir = current_file.parent
    return scripts_dir

# Import other modules
import Module.Editor_Rename_Module as Editor_Rename_Module
import Module.Quick_Rename_Module as Quick_Rename_Module
import Module.NormalEdit_Module as NormalEdit_Module
import Module.UnBevel_Module as UnBevel_Module
import Module.UVSetList_Module as UVSetList_Module
from Toolbox.QuickExport import QuickExport
from Toolbox.ViewCapture import screen_shot
from Toolbox.AriScripts import AriScriptLauncherQt


# based on system encoding, default use english
CURRENT_LANG = 'en_US'

# Language dictionary
LANG = {
    'en_US': {
        # Display Control Group
        "Display Control": "Display Control",
        "Normal": "Normal",
        "Normal Size:": "Normal Size:",
        
        # Import/Export Group
        "Import/Export": "Import/Export",
        "Import OBJ": "Import",
        "Export OBJ": "Export",
        "Import FBX": "Import",
        "Export FBX": "Export",
        "Import_tip": "Import OBJ/FBX file with auto cleanup",
        "Export_tip": "Export OBJ/FBX file with group names",
        "Switch Format": "Switch Format",
        "Current Format": "Current Format: {}",
        
        # Editor Group
        "Editor": "Editor",
        "NormalEdit": "NormalEdit",
        "Crease Editor": "Crease Editor",
        "UV Editor": "UV Editor",
        "UV Editor_tip": "Open UV Editor window",
        "UV Set List": "UVsL Editor",
        "UV Set List_tip": "Open UV Set List Editor tool",
        
        # Select Control Group
        "Select Control": "Select Control",
        "Select Hard Edges": "Hard Edges",
        "Select UV Border Edge": "S/H by UvB",
        "Planar Projection": "Planar UV",
        "UV Layout by Hard Edges": "UV Layout",
        "EdgeToCurve": "Edge2Curve",
        "EdgeToCurve_tip": "Convert edges to NURBS curves",
        
        # Toolbox Group
        "Toolbox": "Toolbox",
        "QuickRename": "QuickRename",
        "QuickRename_tip": "Quick rename tool for batch renaming objects",
        "Rename": "Rename",
        "Rename_tip": "Advanced rename editor with more options",
        "QuickExport": "QuickExport",
        "QuickExport_tip": "Quick export tool for exporting objects",
        "ScreenShot": "ScreenShot",
        "ScreenShot_tip": "Capture viewport screenshots",
        "UnBevel": "UnBevel",
        "UnBevel_tip": "Tool for unbeveling edges",
        "Distance": "Distance",
        "Distance_tip": "Calculate edge length",
        "AriScript": "AriScript",
        "AriScript_tip": "open AriScript tools",
        
        # Display Controls
        "Crease_tip": "Toggle Crease Edge Display\n\nShow/Hide crease edges",
        "MapBorders": "Toggle UV Border Display\n\nShow/Hide UV borders",
        "Map Borders On": "UV Borders On",
        "Map Borders Off": "UV Borders Off",
        
        # Measurement
        "Please select edges": "Please select edges",
        "Please select edges to measure": "Please select edges to measure",
        "Length": "Length",
        
        # Bottom UI Elements
        "document": "document",
        "Help": "Help",
        "Switch Language": "Switch Language",
    },
    'zh_CN': {
        # 显示控制组
        "Display Control": "显示控制",
        "Normal": "法线",
        "Normal Size:": "法线大小",
        
        # 导入导出组
        "Import/Export": "导入/导出",
        "Import OBJ": "导入",
        "Export OBJ": "导出",
        "Import FBX": "导入",
        "Export FBX": "导出",
        "Import_tip": "导入OBJ/FBX文件并自动清理",
        "Export_tip": "导出OBJ/FBX文件并保留组名",
        "Switch Format": "切换格式",
        "Current Format": "当前格式: {}",
        
        # 编辑器组
        "Editor": "编辑器",
        "NormalEdit": "法线编辑器",
        "Crease Editor": "折痕编辑器",
        "UV Editor": "UV编辑器",
        "UV Editor_tip": "打开UV编辑器窗口",
        "UV Set List": "UV集列表器",
        "UV Set List_tip": "打开UV集列表编辑器工具",
        
        # 选择控制组
        "Select Control": "选择控制",
        "Select Hard Edges": "选择硬边",
        "Select UV Border Edge": "UV边界软硬边",
        "Planar Projection": "平面投影",
        "UV Layout by Hard Edges": "硬边UV布局",
        "EdgeToCurve": "边转曲线",
        "EdgeToCurve_tip": "将边转换为NURBS曲线",
        
        # 工具箱组
        "Toolbox": "工具箱",
        "QuickRename": "快速重命名",
        "QuickRename_tip": "批量重命名工具",
        "Rename": "重命名",
        "Rename_tip": "高级重命名编辑器",
        "QuickExport": "快速导出",
        "QuickExport_tip": "快速导出工具",
        "ScreenShot": "截图",
        "ScreenShot_tip": "视口截图工具",
        "UnBevel": "倒角还原",
        "UnBevel_tip": "边缘倒角还原工具",
        "Distance": "测距",
        "Distance_tip": "计算边长",
        "AriScript": "AriScript工具集",
        "AriScript_tip": "打开AriScript工具集",
        
        # 显示控制
        "Crease_tip": "切换折边显示",
        "MapBorders": "UV边界",
        "Map Borders On": "UV边界显示开启",
        "Map Borders Off": "UV边界显示关闭",
        
        # 测量
        "Please select edges": "请选择边",
        "Please select edges to measure": "请选择要测量的边",
        "Length": "长度",
        
        # 底部UI元素
        "document": "文档",
        "Help": "帮助",
        "Switch Language": "切换语言",
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

        # Get icon from Scripts directory
        icon_path = get_script_path() / "Icons" / HUGTOOL_ICON
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        else:
            print(f"Warning: Icon file '{icon_path}' does not exist.")

        # Set window flags to always stay on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        
        # Initialize states
        self.toggle_state = False
        self.crease_edge_state = False  
        
        self.current_format = "ZBR"  # Toggle default display
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def load_icon(self, icon_path, default_icon=":menuIconFile.png"):
        """
        Load icon from path with fallback to default Maya icon
        """
        try:
            if isinstance(icon_path, str):
                # Load all icons from Scripts directory
                full_path = get_script_path() / icon_path
                
                # Ensure path is absolute
                full_path = full_path.resolve()
                
                if full_path.exists():
                    return QtGui.QIcon(str(full_path))
                else:
                    # Silent fail, use default icon
                    return QtGui.QIcon(default_icon)
            
        except Exception as e:
            # Silent fail, use default icon
            return QtGui.QIcon(default_icon)

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
        self.toggle_normal_display_btn.setToolTip("Toggle normal display")
        self.normal_size_label = QtWidgets.QLabel("Normal Size:")
        self.normal_size_field = QtWidgets.QDoubleSpinBox()
        self.normal_size_field.setValue(0.4)
        self.normal_size_field.setRange(0.01, 10.0)
        self.normal_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.normal_size_slider.setRange(1, 1000)
        self.normal_size_slider.setValue(40)

        # Edge display module
        self.toggle_softEdge_btn = RoundedButton("", icon=QtGui.QIcon(":polySoftEdge.png"))
        self.toggle_softEdge_btn.setToolTip("Toggle Soft Edge Display\n\nShow/Hide soft edges")
        self.toggle_softEdge_btn.setFixedSize(52, 35)  # Set size button

        self.toggle_hardedge_btn = RoundedButton("", icon=QtGui.QIcon(":polyHardEdge.png"))
        self.toggle_hardedge_btn.setToolTip("Toggle Hard Edge Display\n\nShow/Hide hard edges")
        self.toggle_hardedge_btn.setFixedSize(52, 35)

        self.toggle_crease_edge_btn = RoundedButton("", icon=QtGui.QIcon(":polyCrease.png"))
        self.toggle_crease_edge_btn.setToolTip(LANG[CURRENT_LANG]["Crease_tip"])
        self.toggle_crease_edge_btn.setFixedSize(52, 35)

        self.toggle_set_display_map_borders_btn = RoundedButton("", icon=QtGui.QIcon(":UVEditorTextureBorder.png"))
        self.toggle_set_display_map_borders_btn.setToolTip(LANG[CURRENT_LANG]["MapBorders"])
        self.toggle_set_display_map_borders_btn.setFixedSize(52, 35)

        # Modify the button style to make it more suitable for displaying only icons
        icon_button_style = """
            QPushButton {
                background-color: #D0D0D0;
                border-radius: 5px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
        """
        self.toggle_softEdge_btn.setStyleSheet(icon_button_style)
        self.toggle_hardedge_btn.setStyleSheet(icon_button_style)
        self.toggle_crease_edge_btn.setStyleSheet(icon_button_style)
        self.toggle_set_display_map_borders_btn.setStyleSheet(icon_button_style)

        # select module
        self.select_group = QtWidgets.QGroupBox("Select Control")
        self.select_hardedges_btn = RoundedButton(LANG[CURRENT_LANG]["Select Hard Edges"], icon=QtGui.QIcon(":UVTkEdge.png"))
        self.select_hardedges_btn.setToolTip("Select all hard edges on the mesh")
        self.select_uvborder_btn = RoundedButton(LANG[CURRENT_LANG]["Select UV Border Edge"], icon=QtGui.QIcon(":polyCopyUVSet.png"))
        self.select_uvborder_btn.setToolTip("Soft/Hard Edges Set by UV Border")
        self.planar_projection_btn = RoundedButton(LANG[CURRENT_LANG]["Planar Projection"], icon=QtGui.QIcon(":polyCameraUVs.png"))
        self.planar_projection_btn.setToolTip("Apply planar UV projection")
        self.uvlayout_hardedges_btn = RoundedButton(LANG[CURRENT_LANG]["UV Layout by Hard Edges"], icon=QtGui.QIcon(":polyLayoutUV.png"))
        self.uvlayout_hardedges_btn.setToolTip("Perform UV layout based on hard edges")
        self.edge_to_curve_btn = RoundedButton(LANG[CURRENT_LANG]["EdgeToCurve"], icon=QtGui.QIcon(":polyEdgeToCurves.png"))
        self.edge_to_curve_btn.setToolTip(LANG[CURRENT_LANG]["EdgeToCurve_tip"])
        self.uvset_list_btn = RoundedButton(LANG[CURRENT_LANG]["UV Set List"], icon=QtGui.QIcon(":pasteUV.png"))
        self.uvset_list_btn.setToolTip(LANG[CURRENT_LANG]["UV Set List_tip"])

        # crease module
        self.editor_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Editor"])
        self.open_NormalEdit_btn = RoundedButton(LANG[CURRENT_LANG]["NormalEdit"], icon=QtGui.QIcon(":nodeGrapherModeAllLarge.png"))
        self.open_NormalEdit_btn.setToolTip("Open Normal Edit window")
        self.open_crease_editor_btn = RoundedButton(LANG[CURRENT_LANG]["Crease Editor"], icon=QtGui.QIcon(":polyCrease.png"))
        self.open_crease_editor_btn.setToolTip(LANG[CURRENT_LANG]["Crease Editor"])
        self.open_uv_editor_btn = RoundedButton(LANG[CURRENT_LANG]["UV Editor"], icon=QtGui.QIcon(":textureEditor.png"))
        self.open_uv_editor_btn.setToolTip(LANG[CURRENT_LANG]["UV Editor_tip"])

        #toolbox
        self.Toolbox_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Toolbox"])
        
        # First create all the buttons
        self.Toolbox_QuickRename_btn = RoundedButton(LANG[CURRENT_LANG]["QuickRename"], icon=QtGui.QIcon(":annotation.png"))
        self.Toolbox_Rename_btn = RoundedButton(LANG[CURRENT_LANG]["Rename"], icon=QtGui.QIcon(":quickRename.png"))
        self.Toolbox_QuickExport_btn = RoundedButton(LANG[CURRENT_LANG]["QuickExport"], icon=QtGui.QIcon(":sourceScript.png"))
        self.Toolbox_UnBevel_btn = RoundedButton(LANG[CURRENT_LANG]["UnBevel"], icon=QtGui.QIcon(":polyBevel.png"))
        self.Toolbox_ScreenShot_btn = RoundedButton(LANG[CURRENT_LANG]["ScreenShot"], icon=QtGui.QIcon(":out_snapshot.png"))
        self.Toolbox_CalcDistance_btn = RoundedButton("Distance", icon=QtGui.QIcon(":distanceDim.png"))

        # Load the MirrorTool icon using the load_icon method
        ari_icon = self.load_icon(
            "Toolbox/AriScripts/icons/AriScriptLauncher.png", 
            ":createBinFromSelectedNodes.png"
        )
        self.Toolbox_AriScriptLauncherQt_btn = RoundedButton(
            LANG[CURRENT_LANG]["AriScript"], 
            icon=ari_icon
        )

        # Add LOD tool button
        self.Toolbox_LOD_btn = RoundedButton(
            "LOD Tool", 
            icon=QtGui.QIcon(":nodeGrapherModeAllLarge.png")
        )
        self.Toolbox_LOD_btn.setToolTip("Level of Detail Tool")

        # Set tooltips for all buttons
        self.Toolbox_QuickRename_btn.setToolTip(LANG[CURRENT_LANG]["QuickRename_tip"])
        self.Toolbox_Rename_btn.setToolTip(LANG[CURRENT_LANG]["Rename_tip"])
        self.Toolbox_QuickExport_btn.setToolTip(LANG[CURRENT_LANG]["QuickExport_tip"])
        self.Toolbox_UnBevel_btn.setToolTip(LANG[CURRENT_LANG]["UnBevel_tip"])
        self.Toolbox_ScreenShot_btn.setToolTip(LANG[CURRENT_LANG]["ScreenShot_tip"])
        self.Toolbox_CalcDistance_btn.setToolTip(LANG[CURRENT_LANG]["Distance_tip"])
        self.Toolbox_AriScriptLauncherQt_btn.setToolTip(LANG[CURRENT_LANG]["AriScript_tip"])
        self.Toolbox_LOD_btn.setToolTip("Level of Detail Tool")

        # Add Import/Export group after display group
        self.import_export_group = QtWidgets.QGroupBox(LANG[CURRENT_LANG]["Import/Export"])
        self.import_obj_btn = RoundedButton(LANG[CURRENT_LANG]["Import OBJ"], icon=QtGui.QIcon(":importGeneric.png"))
        self.import_obj_btn.setToolTip(LANG[CURRENT_LANG]["Import_tip"])
        
        self.export_obj_btn = RoundedButton(LANG[CURRENT_LANG]["Export OBJ"], icon=QtGui.QIcon(":exportGeneric.png"))
        self.export_obj_btn.setToolTip(LANG[CURRENT_LANG]["Export_tip"])

        # Modify the toggle format button style
        self.switch_format_btn = QtWidgets.QPushButton(self.current_format)
        self.switch_format_btn.setFixedSize(45, 30)
        self.switch_format_btn.setToolTip(LANG[CURRENT_LANG]["Switch Format"])
        self.switch_format_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  # Enable custom right-click menu
        self.switch_format_btn.customContextMenuRequested.connect(self.show_format_context_menu)  # Connect right-click menu signal
        self.switch_format_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #aebaca;  /* border */
                border-radius: 15px;
                padding: 5px;
                color: #aebaca;  /* Text color */
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                border-color: #3CA0DB; 
                color: #3CA0DB;
                background-color: rgba(44, 130, 181, 0.1);  
            }
            QPushButton:pressed {
                border-color: #1C5276; 
                color: #1C5276;
                background-color: rgba(44, 130, 181, 0.2);
            }
        """)







#======UI layout======
    def create_layouts(self):
        """
        Create and organize UI layouts
        
        Layout structure:
        - Main vertical layout
        - Display control group
        - Import/Export group
        - Editor group
        - Select control group
        - Toolbox group
        - Bottom layout with help and language buttons
        """
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(7)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Display control group layout
        display_layout = QtWidgets.QVBoxLayout()
        
        # Normal controls
        normal_display_layout = QtWidgets.QHBoxLayout()
        normal_display_layout.addWidget(self.toggle_normal_display_btn)
        normal_display_layout.addWidget(self.normal_size_label)
        normal_display_layout.addWidget(self.normal_size_field)
        display_layout.addLayout(normal_display_layout)
        display_layout.addWidget(self.normal_size_slider)
        
        # Edge display controls
        edge_toggle_layout = QtWidgets.QHBoxLayout()
        edge_toggle_layout.addWidget(self.toggle_softEdge_btn)
        edge_toggle_layout.addWidget(self.toggle_hardedge_btn)
        edge_toggle_layout.addWidget(self.toggle_crease_edge_btn)
        edge_toggle_layout.addWidget(self.toggle_set_display_map_borders_btn)
        edge_toggle_layout.setSpacing(4)  # Set spacing between buttons
        edge_toggle_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        display_layout.addLayout(edge_toggle_layout)
        
        self.display_group.setLayout(display_layout)

        # Add Import/Export group layout
        import_export_layout = QtWidgets.QVBoxLayout()
        
        # Add horizontal layout for buttons and format switcher
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.export_obj_btn)
        buttons_layout.addWidget(self.import_obj_btn)
        buttons_layout.addWidget(self.switch_format_btn)
        
        import_export_layout.addLayout(buttons_layout)
        self.import_export_group.setLayout(import_export_layout)

        # select control group layout
        select_layout = QtWidgets.QGridLayout()
        select_layout.addWidget(self.select_hardedges_btn, 0, 0)
        select_layout.addWidget(self.select_uvborder_btn, 1, 0)
        select_layout.addWidget(self.planar_projection_btn, 0, 1)
        select_layout.addWidget(self.uvlayout_hardedges_btn, 2, 0)
        select_layout.addWidget(self.edge_to_curve_btn, 1, 1)
        select_layout.addWidget(self.Toolbox_UnBevel_btn, 2, 1)
        self.select_group.setLayout(select_layout)

        # crease control group layout
        editor_layout = QtWidgets.QGridLayout()
        editor_layout.addWidget(self.open_NormalEdit_btn, 0, 0)
        editor_layout.addWidget(self.open_crease_editor_btn, 0, 1)
        editor_layout.addWidget(self.open_uv_editor_btn, 1, 1)
        editor_layout.addWidget(self.uvset_list_btn, 1, 0)
        self.editor_group.setLayout(editor_layout)

        #toolbox group layout
        Toolbox_layout = QtWidgets.QGridLayout()
        Toolbox_layout.addWidget(self.Toolbox_QuickRename_btn, 0, 0)
        Toolbox_layout.addWidget(self.Toolbox_Rename_btn, 0, 1)
        Toolbox_layout.addWidget(self.Toolbox_QuickExport_btn, 1, 0)
        Toolbox_layout.addWidget(self.Toolbox_AriScriptLauncherQt_btn, 1, 1)
        Toolbox_layout.addWidget(self.Toolbox_LOD_btn, 2, 0)  
        Toolbox_layout.addWidget(self.Toolbox_ScreenShot_btn, 3, 0)
        Toolbox_layout.addWidget(self.Toolbox_CalcDistance_btn, 2, 1)


        # Toolbox_layout.addWidget(self.Toolbox_More_btn, 3, 0)

        self.Toolbox_group.setLayout(Toolbox_layout)

        # add groups to main layout
        main_layout.addWidget(self.display_group)
        main_layout.addWidget(self.import_export_group)  # Add between display and editor
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
        self.planar_projection_btn.clicked.connect(self.apply_planar_projection2)
        self.uvset_list_btn.clicked.connect(self.UVSetList_view)
        self.edge_to_curve_btn.clicked.connect(self.convert_edge_to_curve)

        self.open_crease_editor_btn.clicked.connect(self.open_crease_set_editor)
        self.open_uv_editor_btn.clicked.connect(self.open_uv_editor)

        self.Toolbox_QuickRename_btn.clicked.connect(self.quick_rename)
        self.Toolbox_Rename_btn.clicked.connect(self.rename_edit)
        self.Toolbox_QuickExport_btn.clicked.connect(self.quick_export)
        self.Toolbox_ScreenShot_btn.clicked.connect(self.screen_shot)
        self.Toolbox_UnBevel_btn.clicked.connect(self.unbevel_tool)
        self.Toolbox_CalcDistance_btn.clicked.connect(self.calculate_distance)
        self.Toolbox_AriScriptLauncherQt_btn.clicked.connect(self.AriScriptLauncherQt)
        self.Toolbox_LOD_btn.clicked.connect(self.show_lod_tool)
        
        # connect help button
        self.help_btn.clicked.connect(self.show_help)

        # connect language switch button
        self.lang_btn.clicked.connect(self.toggle_language)

        # Add Import/Export connections
        self.import_obj_btn.clicked.connect(self.import_obj)
        self.export_obj_btn.clicked.connect(self.export_obj)

        self.switch_format_btn.clicked.connect(self.switch_format)








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





    def toggle_set_display_map_borders(self, *args):
        """Toggle UV map border display"""
        # 检查是否有选择的对象
        selection = cmds.ls(selection=True, type="transform")
        if not selection:
            cmds.warning("No object selected!")
            return
        
        try:
            # Get current status
            current_state = cmds.polyOptions(selection, q=True, displayMapBorder=True)
            if current_state is None:
                current_state = [False]  # Default state
                
            # Switching state
            new_state = not current_state[0]
            cmds.polyOptions(selection, displayMapBorder=new_state)
            
            # Display message
            message = LANG[CURRENT_LANG]["Map Borders On"] if new_state else LANG[CURRENT_LANG]["Map Borders Off"]
            cmds.inViewMessage(
                amg=f'<span style="color:#FFA500;">{message}</span>', 
                pos='botRight',
                fade=True, 
                fst=10,
                fad=1
            )
        except Exception as e:
            cmds.warning(f"Error toggling map borders: {str(e)}")




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


    def SelectUVBorderEdge2(self, *args):
        """
        Select UV border edges for multiple objects
        
        Function:
        - Works on all selected objects
        - Selects UV border edges based on UV boundaries
        """
        # Gets the currently selected object
        selection = cmds.ls(selection=True, type="transform")
        if not selection:
            cmds.warning("No object selected!")
            return
            
        try:
            # Save current selection
            cmds.select(clear=True)
            
            for obj in selection:
                # Select current object
                cmds.select(obj, add=True)
                
                mel.eval('''
                    expandPolyGroupSelection;
                    polyUVBorderHard;
                    selectUVBorderComponents {} "" 1;
                    polyOptions -softEdge;
                ''')
                
            
            message = "已根据UV边界设置软硬边" if CURRENT_LANG == 'zh_CN' else "Soft hard Edges Set by UV Border"
            cmds.inViewMessage(
                amg=f'<span style="color:#FFA500;">{message}</span>', 
                pos='botRight', 
                fade=True, 
                fst=10, 
                fad=1
            )
                
        except Exception as e:
            error_msg = f"选择UV边界时出错: {str(e)}" if CURRENT_LANG == 'zh_CN' else f"Error selecting UV borders: {str(e)}"
            cmds.warning(error_msg)
        finally:
            # Make sure you are in edge selection mode
            cmds.selectMode(component=True)
            cmds.selectType(edge=True)



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
                cmds.inViewMessage(amg=f'<span style="color:#48AAB5">{message}</span>', pos='topCenter', fade=True, fst=3)
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




    def apply_planar_projection2(self, *args):
        """
        Apply planar projection to selected objects
        
        Functions:
        - Applies planar UV projection to selected objects
        - Handles multiple object selection
        - Maintains proper selection mode
        """
        # Get current selection
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning("请选择物体!" if CURRENT_LANG == 'zh_CN' else "Please select objects!")
            return
        
        try:
            for obj in selection:
                # Clear selection
                cmds.select(clear=True)
                # Select the object
                cmds.select(obj)
                # Select all faces of the object
                faces = f"{obj}.f[*]"
                cmds.select(faces, add=True)
                # Execute MEL command sequence
                mel.eval(f'''
                    hilite "{obj}";
                    selectMode -component;
                    select -r "{faces}";
                    polyProjection -type Planar -md p -constructionHistory 1 "{faces}";
                ''')
                
            # Display success message
            message = "已平面投射UV" if CURRENT_LANG == 'zh_CN' else "Planar UV projection applied"
            cmds.inViewMessage(
                amg=f'<span style="color:#48AAB5">{message}</span>', 
                pos='topCenter', 
                fade=True, 
                fst=3, 
                fad=1
            )
                
        except Exception as e:
            error_msg = f"UV投射时出错: {str(e)}" if CURRENT_LANG == 'zh_CN' else f"Error applying UV projection: {str(e)}"
            cmds.warning(error_msg)
        finally:
            # Restore selection
            cmds.select(selection)
            cmds.selectMode(object=True)












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




    #============input function modules===============


    def show_format_context_menu(self, position):
        """Display context menu for format switch button"""
        menu = QtWidgets.QMenu()
        
        # Add open folder option
        open_folder_action = menu.addAction("Open Export Folder")
        open_folder_action.triggered.connect(self.open_export_folder)
        
        # Show menu at mouse position
        menu.exec_(self.switch_format_btn.mapToGlobal(position))

    def open_export_folder(self):
        """Open export folder in system file browser"""
        path = "C:/temp"
        if not os.path.exists(path):
            os.makedirs(path)  # Create folder if it doesn't exist
        
        # Open folder with system default file browser
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', path])
        else:  # linux
            subprocess.Popen(['xdg-open', path])








    def switch_format(self):
        """Switch between ZBrush and Houdini format"""
        if self.current_format == "ZBR":
            self.current_format = "HDN"
            self.import_obj_btn.setText(LANG[CURRENT_LANG]["Import FBX"])
            self.export_obj_btn.setText(LANG[CURRENT_LANG]["Export FBX"])
            self.switch_format_btn.setText("HDN")
        else:
            self.current_format = "ZBR"
            self.import_obj_btn.setText(LANG[CURRENT_LANG]["Import OBJ"])
            self.export_obj_btn.setText(LANG[CURRENT_LANG]["Export OBJ"])
            self.switch_format_btn.setText("ZBR")
        
        # Update button connections
        self.import_obj_btn.clicked.disconnect()
        self.export_obj_btn.clicked.disconnect()
        
        if self.current_format == "ZBR":
            self.import_obj_btn.clicked.connect(self.import_obj)
            self.export_obj_btn.clicked.connect(self.export_obj)
        else:
            self.import_obj_btn.clicked.connect(self.import_fbx)
            self.export_obj_btn.clicked.connect(self.export_fbx)

    def import_fbx(self):
        """Import FBX file using MEL function"""
        try:
            mel_file = get_script_path() / "Toolbox" / "ImportExport" / "ImportExport.mel"
            if mel_file.exists():
                mel.eval(f'source "{str(mel_file).replace(os.sep, "/")}"')
            else:
                raise FileNotFoundError(f"MEL file not found: {mel_file}")
            
            mel.eval('Import_fbx()')
            
            message = "FBX导入成功" if CURRENT_LANG == 'zh_CN' else "FBX imported successfully"
            cmds.inViewMessage(
                amg=f'<span style="color:#48AAB5">{message}</span>', 
                pos='topCenter', 
                fade=True, 
                fst=3
            )
        except Exception as e:
            error_msg = f"导入FBX时出错: {str(e)}" if CURRENT_LANG == 'zh_CN' else f"Error importing FBX: {str(e)}"
            cmds.warning(error_msg)

    def export_fbx(self):
        """Export FBX file using MEL function"""
        try:
            mel_file = get_script_path() / "Toolbox" / "ImportExport" / "ImportExport.mel"
            if mel_file.exists():
                mel.eval(f'source "{str(mel_file).replace(os.sep, "/")}"')
            else:
                raise FileNotFoundError(f"MEL file not found: {mel_file}")
            
            mel.eval('Export_fbx()')
            
            message = "FBX导出成功" if CURRENT_LANG == 'zh_CN' else "FBX exported successfully"
            cmds.inViewMessage(
                amg=f'<span style="color:#48AAB5">{message}</span>', 
                pos='topCenter', 
                fade=True, 
                fst=3
            )
        except Exception as e:
            error_msg = f"导出FBX时出错: {str(e)}" if CURRENT_LANG == 'zh_CN' else f"Error exporting FBX: {str(e)}"
            cmds.warning(error_msg)






    def import_obj(self):
        """Import OBJ file using MEL function"""
        try:
            # Source the MEL file first
            mel_file = get_script_path() / "Toolbox" / "ImportExport" / "ImportExport.mel"
            if mel_file.exists():
                mel.eval(f'source "{str(mel_file).replace(os.sep, "/")}"')
            else:
                raise FileNotFoundError(f"MEL file not found: {mel_file}")
            
            # Call the Import function
            mel.eval('Import_obj()')
            
            message = "OBJ导入成功" if CURRENT_LANG == 'zh_CN' else "OBJ imported successfully"
            cmds.inViewMessage(
                amg=f'<span style="color:#48AAB5">{message}</span>', 
                pos='topCenter', 
                fade=True, 
                fst=3
            )
        except Exception as e:
            error_msg = f"导入OBJ时出错: {str(e)}" if CURRENT_LANG == 'zh_CN' else f"Error importing OBJ: {str(e)}"
            cmds.warning(error_msg)

    def export_obj(self):
        """Export OBJ file using MEL function"""
        try:
            # Source the MEL file first
            mel_file = get_script_path() / "Toolbox" / "ImportExport" / "ImportExport.mel"
            if mel_file.exists():
                mel.eval(f'source "{str(mel_file).replace(os.sep, "/")}"')
            else:
                raise FileNotFoundError(f"MEL file not found: {mel_file}")
            
            # Call the Export function
            mel.eval('Export_obj()')
            
            message = "OBJ导出成功" if CURRENT_LANG == 'zh_CN' else "OBJ exported successfully"
            cmds.inViewMessage(
                amg=f'<span style="color:#48AAB5">{message}</span>', 
                pos='topCenter', 
                fade=True, 
                fst=3
            )
        except Exception as e:
            error_msg = f"导出OBJ时出错: {str(e)}" if CURRENT_LANG == 'zh_CN' else f"Error exporting OBJ: {str(e)}"
            cmds.warning(error_msg)





    def show_lod_tool(self):
        """Launch LOD tool"""
        try:
            importlib.reload(LOD)
            LOD.show_lod_window()
        except Exception as e:
            cmds.warning(f"Error launching LOD tool: {str(e)}")

    def AriScriptLauncherQt(self):
        importlib.reload(AriScriptLauncherQt)
        AriScriptLauncherQt.show()

    def UVSetList_view(self):
        """Launch UV Set List tool"""
        try:
            importlib.reload(UVSetList_Module)
            UVSetList_Module.show()
            print("UV Set List tool launched successfully")  # Debugging information
        except Exception as e:
            error_msg = f"启动UV Set List工具时出错: {str(e)}" if CURRENT_LANG == 'zh_CN' else f"Error launching UV Set List tool: {str(e)}"
            cmds.warning(error_msg)
            print(f"Error details: {e}")  

    def quick_rename(self):
        importlib.reload(Quick_Rename_Module)
        Quick_Rename_Module.show()

    def rename_edit(self):
        importlib.reload(Editor_Rename_Module)
        Editor_Rename_Module.show()

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
        
        # Update tooltips only, do not set button text
        self.toggle_crease_edge_btn.setToolTip(LANG[CURRENT_LANG]["Crease_tip"])
        self.toggle_set_display_map_borders_btn.setToolTip(LANG[CURRENT_LANG]["MapBorders"])
        
        # Update text for other buttons and components
        self.editor_group.setTitle(LANG[CURRENT_LANG]["Editor"])
        self.open_crease_editor_btn.setText(LANG[CURRENT_LANG]["Crease Editor"])
        self.open_uv_editor_btn.setText(LANG[CURRENT_LANG]["UV Editor"])
        
        self.Toolbox_group.setTitle(LANG[CURRENT_LANG]["Toolbox"])
        self.Toolbox_QuickRename_btn.setText(LANG[CURRENT_LANG]["QuickRename"])
        self.Toolbox_Rename_btn.setText(LANG[CURRENT_LANG]["Rename"])
        self.Toolbox_QuickExport_btn.setText(LANG[CURRENT_LANG]["QuickExport"])
        self.Toolbox_ScreenShot_btn.setText(LANG[CURRENT_LANG]["ScreenShot"])
        self.Toolbox_UnBevel_btn.setText(LANG[CURRENT_LANG]["UnBevel"])
        self.Toolbox_CalcDistance_btn.setText(LANG[CURRENT_LANG]["Distance"])
        
        self.select_group.setTitle(LANG[CURRENT_LANG]["Select Control"])
        self.select_hardedges_btn.setText(LANG[CURRENT_LANG]["Select Hard Edges"])
        self.select_uvborder_btn.setText(LANG[CURRENT_LANG]["Select UV Border Edge"])
        self.planar_projection_btn.setText(LANG[CURRENT_LANG]["Planar Projection"])
        self.uvlayout_hardedges_btn.setText(LANG[CURRENT_LANG]["UV Layout by Hard Edges"])
        self.edge_to_curve_btn.setText(LANG[CURRENT_LANG]["EdgeToCurve"])
        self.uvset_list_btn.setText(LANG[CURRENT_LANG]["UV Set List"])
        
        # Import/Export translations
        self.import_export_group.setTitle(LANG[CURRENT_LANG]["Import/Export"])
        self.import_obj_btn.setText(LANG[CURRENT_LANG]["Import OBJ"])
        self.export_obj_btn.setText(LANG[CURRENT_LANG]["Export OBJ"])
        
        # Update button text according to current format
        if self.current_format == "ZBR":
            self.import_obj_btn.setText(LANG[CURRENT_LANG]["Import OBJ"])
            self.export_obj_btn.setText(LANG[CURRENT_LANG]["Export OBJ"])
        else:
            self.import_obj_btn.setText(LANG[CURRENT_LANG]["Import FBX"])
            self.export_obj_btn.setText(LANG[CURRENT_LANG]["Export FBX"])
        
        # all tooltips
        self.Toolbox_QuickRename_btn.setToolTip(LANG[CURRENT_LANG]["QuickRename_tip"])
        self.Toolbox_Rename_btn.setToolTip(LANG[CURRENT_LANG]["Rename_tip"])
        self.Toolbox_QuickExport_btn.setToolTip(LANG[CURRENT_LANG]["QuickExport_tip"])
        self.Toolbox_ScreenShot_btn.setToolTip(LANG[CURRENT_LANG]["ScreenShot_tip"])
        self.Toolbox_UnBevel_btn.setToolTip(LANG[CURRENT_LANG]["UnBevel_tip"])
        self.Toolbox_CalcDistance_btn.setToolTip(LANG[CURRENT_LANG]["Distance_tip"])



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







