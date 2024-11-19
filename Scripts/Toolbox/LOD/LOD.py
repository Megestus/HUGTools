import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

# Define constants
TOOL_TITLE = "LOD Tool"
BUTTON_HEIGHT = 32
WINDOW_MIN_WIDTH = 200
BUTTON_STYLE = """
    QPushButton {
        background-color: #2B2B2B;
        color: #CCCCCC;
        border-radius: 4px;
        padding: 5px;
        font-weight: bold;
        text-align: center;
        font-size: 11px;
        border: 1px solid #1E1E1E;
    }
    QPushButton:hover {
        background-color: #3D3D3D;
        border: 1px solid #5A5A5A;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #232323;
        border: 1px solid #1E1E1E;
        color: #A0A0A0;
    }
"""

# 添加状态按钮样式
STATE_BUTTON_STYLE = """
    QPushButton {
        background-color: #2B2B2B;
        color: #CCCCCC;
        border-radius: 4px;
        padding: 5px;
        font-weight: bold;
        font-size: 10px;
        border: 1px solid #1E1E1E;
        min-width: 50px;
        max-width: 50px;
        height: 25px;
    }
    QPushButton:hover {
        background-color: #3D3D3D;
        border: 1px solid #5A5A5A;
    }
    QPushButton:pressed {
        background-color: #232323;
    }
"""

class RoundedButton(QtWidgets.QPushButton):
    """
    Custom dark themed button class
    
    Features:
    - Modern dark design
    - Subtle hover effects
    - Professional appearance
    """
    def __init__(self, text=""):
        super(RoundedButton, self).__init__(text)
            
        # Set unified size policy
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setMinimumSize(100, BUTTON_HEIGHT)
        self.setFixedHeight(BUTTON_HEIGHT)
        
        # Apply custom style
        self.setStyleSheet(BUTTON_STYLE)

def maya_main_window():
    """Return Maya's main window as a Qt widget"""
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QWidget)

class StateButton(QtWidgets.QPushButton):
    """Custom button class with right-click menu support"""
    def __init__(self, text=""):
        super(StateButton, self).__init__(text)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set size policy
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setMinimumSize(50, 25)
        self.setMaximumSize(50, 25)
    
    def show_context_menu(self, pos):
        """Show the context menu"""
        menu = QtWidgets.QMenu(self)
        action = menu.addAction(f"Apply to All Levels")
        action.triggered.connect(self.apply_to_all)
        menu.exec_(self.mapToGlobal(pos))
    
    def apply_to_all(self):
        """Apply the state to all LOD levels"""
        try:
            state = {"USE": 0, "SHOW": 1, "HIDE": 2}[self.text()]
            self.set_all_lod_states(state)
        except Exception as e:
            cmds.warning(f"Error applying state to all levels: {str(e)}")
    
    def set_all_lod_states(self, state):
        """Set all LOD levels to the specified state"""
        try:
            lod_groups = cmds.ls(type="lodGroup", long=True)
            if not lod_groups:
                cmds.warning("No LOD groups found in the scene")
                return
            
            for group in lod_groups:
                children = cmds.listRelatives(group, children=True)
                if children:
                    for i in range(len(children)):
                        cmds.setAttr(f"{group}.displayLevel[{i}]", state)
            
            # 显示状态提示
            state_messages = {
                0: "Using",
                1: "Showing",
                2: "Hiding"
            }
            message = f"{state_messages[state]} all LOD levels"
            cmds.inViewMessage(
                amg=f'<span style="color:#48AAB5">{message}</span>', 
                pos='topCenter', 
                fade=True, 
                fst=1.5
            )
            
        except Exception as e:
            cmds.warning(f"Error setting all LOD states: {str(e)}")

class LODToolWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(LODToolWindow, self).__init__(parent)
        
        # Window setup
        self.setWindowTitle(TOOL_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(WINDOW_MIN_WIDTH)
        
        # Set window background color
        self.setStyleSheet("""
            QDialog {
                background-color: #383838;
                color: #CCCCCC;
            }
            QLabel {
                color: #CCCCCC;
                font-size: 11px;
            }
            QComboBox {
                background-color: #2B2B2B;
                color: #CCCCCC;
                border: 1px solid #1E1E1E;
                border-radius: 3px;
                padding: 3px;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 1px solid #5A5A5A;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(:/arrowDown.png);
            }
        """)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    #======UI Creation======
    def create_widgets(self):
        """Create all UI widgets"""
        # LOD Level Controls
        self.lod_step_label = QtWidgets.QLabel("LOD Level:")
        
        # 创建水平布局来包含标签和数值显示
        self.level_display = QtWidgets.QLabel("1")
        self.level_display.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 11px;
                background-color: #2B2B2B;
                border: 1px solid #1E1E1E;
                border-radius: 3px;
                padding: 3px 8px;
                min-width: 20px;
                text-align: center;
            }
        """)
        
        # 创建滑动条
        self.lod_step_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.lod_step_slider.setMinimum(1)
        self.lod_step_slider.setMaximum(1)  # 初始设置为1，后续会动态更新
        self.lod_step_slider.setValue(1)
        self.lod_step_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #1E1E1E;
                height: 4px;
                background: #2B2B2B;
                margin: 2px 0;
                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                background: #CCCCCC;
                border: 1px solid #1E1E1E;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }

            QSlider::handle:horizontal:hover {
                background: #FFFFFF;
            }
        """)

        # 添加定时器用于检查LOD组变化
        self.update_timer = QtCore.QTimer(self)
        self.update_timer.setInterval(500)  # 每500ms检查一次
        self.update_timer.timeout.connect(self.update_slider_range)
        self.update_timer.start()

        # Main Control Buttons
        self.create_lod_btn = RoundedButton("CREATE LOD")
        self.use_lods_btn = RoundedButton("USE LODs")
        self.fix_lods_btn = RoundedButton("FIX LODs")
        self.display_all_btn = RoundedButton("SHOW ALL")
        
        # Rename Buttons
        self.del_la1_btn = RoundedButton("DEL La1")
        self.del_la2_btn = RoundedButton("DEL Lb1")
        self.del_la3_btn = RoundedButton("DEL Lc1")
        
        # Set tooltips
        self.lod_step_slider.setToolTip("Drag to change LOD level")
        self.create_lod_btn.setToolTip("Create LOD group from selected objects\nCreates a new LOD hierarchy")
        self.use_lods_btn.setToolTip("Enable LOD display mode\nActivates level of detail visualization")
        self.fix_lods_btn.setToolTip("Fix LOD threshold values\nRecalculates and applies correct threshold settings")
        self.display_all_btn.setToolTip("Display all LOD levels simultaneously\nShows all levels for comparison")
        self.del_la1_btn.setToolTip("Replace '_La1' with '_La'\nCleans up naming convention")
        self.del_la2_btn.setToolTip("Replace '_Lb1' with '_Lb'\nCleans up naming convention")
        self.del_la3_btn.setToolTip("Replace '_Lc1' with '_Lc'\nCleans up naming convention")

        # 添加LOD显示控制按钮组
        self.display_control_layout = QtWidgets.QHBoxLayout()
        
        # 创建三个状态按钮
        self.lod_state_use = StateButton("USE")
        self.lod_state_show = StateButton("SHOW")
        self.lod_state_hide = StateButton("HIDE")
        
        # 设置按钮样式和工具提示
        for btn in [self.lod_state_use, self.lod_state_show, self.lod_state_hide]:
            btn.setStyleSheet(STATE_BUTTON_STYLE)
        
        # 设置工具提示
        self.lod_state_use.setToolTip("Left Click: Use current LOD level (0)\nRight Click: Use all LOD levels")
        self.lod_state_show.setToolTip("Left Click: Show current LOD level (1)\nRight Click: Show all LOD levels")
        self.lod_state_hide.setToolTip("Left Click: Hide current LOD level (2)\nRight Click: Hide all LOD levels")

        # 添加Break LOD按钮
        self.break_lod_btn = RoundedButton("BREAK LOD")
        self.break_lod_btn.setToolTip("Break selected LOD groups\nMaintains hierarchy and names")

    def create_layouts(self):
        """Create and setup all layouts"""
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # LOD Level Layout
        level_layout = QtWidgets.QHBoxLayout()
        level_layout.addWidget(self.lod_step_label)
        level_layout.addWidget(self.lod_step_slider)
        level_layout.addWidget(self.level_display)
        main_layout.addLayout(level_layout)
        
        # 添加显示控制按钮组
        state_layout = QtWidgets.QHBoxLayout()
        state_layout.addWidget(self.lod_state_use)
        state_layout.addWidget(self.lod_state_show)
        state_layout.addWidget(self.lod_state_hide)
        state_layout.setSpacing(4)
        main_layout.addLayout(state_layout)
        
        # Add spacing line
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("background-color: #2B2B2B;")
        main_layout.addWidget(line)
        
        # Add main control buttons
        main_layout.addWidget(self.create_lod_btn)
        main_layout.addWidget(self.use_lods_btn)
        main_layout.addWidget(self.fix_lods_btn)
        main_layout.addWidget(self.display_all_btn)
        main_layout.addWidget(self.break_lod_btn)  # 添加Break LOD按钮
        
        # Add another spacing line
        line2 = QtWidgets.QFrame()
        line2.setFrameShape(QtWidgets.QFrame.HLine)
        line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        line2.setStyleSheet("background-color: #2B2B2B;")
        main_layout.addWidget(line2)
        
        # Add rename buttons
        main_layout.addWidget(self.del_la1_btn)
        main_layout.addWidget(self.del_la2_btn)
        main_layout.addWidget(self.del_la3_btn)

    def create_connections(self):
        """Create all widget connections"""
        # 连接滑动条值变化信号
        self.lod_step_slider.valueChanged.connect(self.on_slider_value_changed)
        self.create_lod_btn.clicked.connect(nepre_create_dejima_lod)
        self.use_lods_btn.clicked.connect(nepre_dejima_use_lod)
        self.fix_lods_btn.clicked.connect(nepre_dejima_fix_lod)
        self.display_all_btn.clicked.connect(nepre_dejima_display_all)
        self.del_la1_btn.clicked.connect(lambda: cmds.searchReplaceNames("_La1", "_La", "hierarchy"))
        self.del_la2_btn.clicked.connect(lambda: cmds.searchReplaceNames("_Lb1", "_Lb", "hierarchy"))
        self.del_la3_btn.clicked.connect(lambda: cmds.searchReplaceNames("_Lc1", "_Lc", "hierarchy"))
        
        # 连接显示状态按钮的左键点击
        self.lod_state_use.clicked.connect(lambda: self.set_current_lod_state(0))
        self.lod_state_show.clicked.connect(lambda: self.set_current_lod_state(1))
        self.lod_state_hide.clicked.connect(lambda: self.set_current_lod_state(2))

        # 连接Break LOD按钮
        self.break_lod_btn.clicked.connect(break_lod_group)

    def update_slider_range(self):
        """更新滑动条范围基于当前LOD组的层级数量"""
        try:
            lod_groups = cmds.ls(type="lodGroup", long=True)
            max_levels = 1  # 默认最小值为1
            
            if lod_groups:
                for obj in lod_groups:
                    groups = cmds.listRelatives(obj, children=True)
                    if groups:
                        max_levels = max(max_levels, len(groups))
            
            # 只有当最大值发生变化时才更新滑动条
            if self.lod_step_slider.maximum() != max_levels:
                current_value = min(self.lod_step_slider.value(), max_levels)
                self.lod_step_slider.setMaximum(max_levels)
                self.lod_step_slider.setValue(current_value)
                self.level_display.setText(f"{current_value}/{max_levels}")
            
        except Exception as e:
            cmds.warning(f"Error updating slider range: {str(e)}")

    def on_slider_value_changed(self, value):
        """处理滑动条值变化"""
        max_value = self.lod_step_slider.maximum()
        self.level_display.setText(f"{value}/{max_value}")  # 显示当前值和最大值
        nepre_dejima_display_lod(value)

    def showEvent(self, event):
        """窗口显示时更新滑动条范围"""
        super().showEvent(event)
        self.update_slider_range()

    def closeEvent(self, event):
        """窗口关闭时停止定时器"""
        self.update_timer.stop()
        super().closeEvent(event)

    def set_current_lod_state(self, state):
        """
        设置当前选中LOD级别的显示状态
        
        Args:
            state (int): 显示状态 (0=使用LOD, 1=显示, 2=隐藏)
        """
        try:
            current_level = self.lod_step_slider.value() - 1  # 转换为0基索引
            lod_groups = cmds.ls(type="lodGroup", long=True)
            
            if not lod_groups:
                cmds.warning("No LOD groups found in the scene")
                return
                
            for group in lod_groups:
                children = cmds.listRelatives(group, children=True)
                if children and current_level < len(children):
                    cmds.setAttr(f"{group}.displayLevel[{current_level}]", state)
            
            # 显示状态提示
            state_messages = {
                0: "Using LOD level",
                1: "Showing LOD level",
                2: "Hiding LOD level"
            }
            message = f"{state_messages[state]} {current_level + 1}"
            cmds.inViewMessage(
                amg=f'<span style="color:#48AAB5">{message}</span>', 
                pos='topCenter', 
                fade=True, 
                fst=1.5
            )
            
        except Exception as e:
            cmds.warning(f"Error setting LOD state: {str(e)}")

#======LOD Functions======
def nepre_create_dejima_lod():
    """
    Create LOD group from selected objects
    
    Functions:
    - Parent objects to world
    - Create LOD group
    - Setup LOD thresholds
    - Rename groups and meshes
    """
    sel = cmds.ls(selection=True, long=True)
    try:
        cmds.parent(sel, world=True)
    except:
        pass
    
    cmds.LevelOfDetailGroup()
    sel = cmds.ls(selection=True, long=True)
    
    for obj in sel:
        cmds.setAttr(f"{obj}.useScreenHeightPercentage", 0)
        obj_type = cmds.nodeType(obj)
        lod_name = ""
        
        if obj_type == "lodGroup":
            groups = cmds.listRelatives(obj, children=True)
            
            for group in groups:
                meshes = cmds.listRelatives(group, children=True)
                mesh = meshes[0]
                name_len = len(mesh)
                prefix = mesh[0:name_len-2]
                prefix = prefix.replace("Mesh_", "_")
                lod_name = f"{prefix}Lx"
                mesh_name = mesh.replace("Mesh_", "_")
                cmds.rename(group, mesh_name)
            
            for i in range(len(groups)-1):
                cmds.setAttr(f"{obj}.threshold[{i}]", (i*3+3))
            
            print(f"{lod_name}\n")
            cmds.rename(obj, lod_name)

def nepre_dejima_use_lod():
    """Enable LOD display mode for all LOD groups"""
    lod_groups = cmds.ls(type="lodGroup", long=True)
    for obj in lod_groups:
        groups = cmds.listRelatives(obj, children=True)
        lods = len(groups)
        for i in range(lods):
            cmds.setAttr(f"{obj}.displayLevel[{i}]", 0)

def nepre_dejima_display_lod(num):
    """
    Display specific LOD level
    
    Args:
        num (int): LOD level to display (1-based index)
    """
    lod_groups = cmds.ls(type="lodGroup", long=True)
    for obj in lod_groups:
        groups = cmds.listRelatives(obj, children=True)
        lods = len(groups)
        for i in range(lods):
            toggle = 1 if i == num-1 else 2
            if num > lods and i == lods-1:
                toggle = 1
            cmds.setAttr(f"{obj}.displayLevel[{i}]", toggle)

def nepre_dejima_fix_lod():
    """Fix LOD threshold values by reapplying them"""
    lod_groups = cmds.ls(type="lodGroup", long=True)
    for obj in lod_groups:
        groups = cmds.listRelatives(obj, children=True)
        lods = len(groups)-1
        for i in range(lods):
            dist = cmds.getAttr(f"{obj}.threshold[{i}]")
            cmds.setAttr(f"{obj}.threshold[{i}]", dist)

def nepre_dejima_display_all():
    """Display all LOD levels simultaneously"""
    lod_groups = cmds.ls(type="lodGroup", long=True)
    for obj in lod_groups:
        groups = cmds.listRelatives(obj, children=True)
        lods = len(groups)
        for i in range(lods):
            cmds.setAttr(f"{obj}.displayLevel[{i}]", 1)

def break_lod_group():
    """
    Break selected LOD groups and maintain hierarchy
    
    Functions:
    - Ungroup LOD group while keeping children
    - Maintain original hierarchy
    - Keep original names
    """
    try:
        # 获取选中的LOD组（使用长名称避免重名问题）
        selected = cmds.ls(selection=True, type="transform", long=True) or []
        lod_groups = [obj for obj in selected if cmds.nodeType(obj) == "lodGroup"]
        
        if not lod_groups:
            cmds.warning("Please select LOD groups to break")
            return
            
        for lod_group in lod_groups:
            # 获取所有子物体（使用长名称）
            children = cmds.listRelatives(lod_group, children=True, type="transform", fullPath=True) or []
            if not children:
                continue
                
            # 获取LOD组的父物体（使用长名称）
            parent = cmds.listRelatives(lod_group, parent=True, fullPath=True)
            
            # 将子物体移到LOD组的层级
            for child in children:
                try:
                    if parent:
                        cmds.parent(child, parent[0])
                    else:
                        cmds.parent(child, world=True)
                except Exception as e:
                    cmds.warning(f"Error parenting {child}: {str(e)}")
                    continue
            
            # 删除空的LOD组
            try:
                cmds.delete(lod_group)
            except Exception as e:
                cmds.warning(f"Error deleting LOD group {lod_group}: {str(e)}")
        
        # 显示成功消息
        message = f"Successfully broke {len(lod_groups)} LOD group(s)"
        cmds.inViewMessage(
            amg=f'<span style="color:#48AAB5">{message}</span>', 
            pos='topCenter', 
            fade=True, 
            fst=1.5
        )
        
    except Exception as e:
        cmds.warning(f"Error breaking LOD groups: {str(e)}")

#======Window Management======
def show_lod_window():
    """Show the LOD tool window"""
    global lod_window
    try:
        lod_window.close()
        lod_window.deleteLater()
    except:
        pass
    
    lod_window = LODToolWindow()
    lod_window.show()

if __name__ == "__main__":
    show_lod_window()
