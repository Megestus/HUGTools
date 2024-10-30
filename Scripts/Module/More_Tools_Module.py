from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial
import importlib
import sys
import os
import maya.cmds as cmds
import traceback

# maya window set Father-son relationship implement
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

# 修改导入语句
import os
import sys
from pathlib import Path

# 使用Path对象处理路径
current_dir = Path(__file__).resolve().parent
scripts_dir = current_dir.parent
toolbox_dir = scripts_dir / "Toolbox"

# 确保路径是字符串且使用正斜杠
toolbox_path = str(toolbox_dir).replace("\\", "/")
if toolbox_path not in sys.path:
    sys.path.append(toolbox_path)

# 直接导入melToPymelUI
import melToPymelUI

# 添加调试信息
print(f"Toolbox path: {toolbox_path}")
print(f"melToPymelUI loaded from: {melToPymelUI.__file__}")

# ----------------------
# Custom Widgets
# ----------------------

class ModItButton(QtWidgets.QPushButton):
    def __init__(self, text="", icon=None, parent=None):
        super(ModItButton, self).__init__(text, parent)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(32, 32))
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #4B4B4B;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
                border: 1px solid #666666;
            }
            QPushButton:pressed {
                background-color: #333333;
                border: 1px solid #777777;
            }
            """
        )

# ----------------------
# Main Window Class
# ----------------------

class MoreToolsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MoreToolsWindow, self).__init__(parent)
        self.setWindowTitle("More Tools")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        
        # 工具配置字典：用于定义所有工具按钮的属性
        # 结构说明：
        # {
        #     "分类名称": [
        #         {
        #             "name": "按钮名称",
        #             "icon": "图标文件名",
        #             "tooltip": "鼠标悬停提示",
        #             "description": "工具描述"  # 可选
        #         },
        #         # ... 更多工具
        #     ]
        # }
        self.tool_config = {
            "Modeling": [
                {
                    "name": "MELtoPY",                          
                    "icon": "mao.png",                          
                    "tooltip": "Convert MEL code to Python code",
                    "description": "A tool for converting MEL scripts to Python"
                },
                {
                    "name": "ViewCapture",                      
                    "icon": "boxuemao.png",                     
                    "tooltip": "Maya Viewport Screenshot Tool",  
                    "description": "Capture high quality screenshots of Maya viewport with custom path and name"
                },
                {
                    "name": "MirrorTool",                      
                    "icon": "K_Mirror_icons/ShelfIcon.png",                    
                    "tooltip": "Mirror Objects Tool",
                    "description": "Mirror objects across different axes with options"
                },
                {"name": "Tool 4", "icon": "xianluomao.png"},
            ]
            # 暂时注释掉Rigging分类
            # "Rigging": [
            #     {"name": "Tool 5", "icon": "tianyuanmao.png"},
            #     {"name": "Tool 6", "icon": "sanhuamao.png"},
            #     {"name": "Tool 7", "icon": "mimiyanmao.png"},
            #     {"name": "Tool 8", "icon": "heimao.png"},
            # ],
        }
        self.init_ui()

    # ----------------------
    # UI Initialization
    # ----------------------

    def init_ui(self):
        self.create_widgets()
        self.create_layout()
        self.setup_connections()
        self.set_styles()

    def create_widgets(self):
        self.create_title_bar()
        self.create_tab_widget()
        self.create_tool_buttons()

    def create_title_bar(self):
        self.title_bar = QtWidgets.QWidget(self)
        self.title_bar.setFixedHeight(30)
        self.title_label = QtWidgets.QLabel("More Tools", self.title_bar)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #CCCCCC;")
        self.close_button = QtWidgets.QPushButton("×", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #CCCCCC;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #FF4444;
                color: white;
            }
        """)

    def create_tab_widget(self):
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555555;
                background: #3C3C3C;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: transparent;
                border: none;
                padding: 5px;
                margin-right: 5px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #4B4B4B;
            }
        """)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "Icons")
        modeling_icon = QtGui.QIcon(os.path.join(icon_path, "Modeling.png"))
        rigging_icon = QtGui.QIcon(os.path.join(icon_path, "screenshot.png"))
        
        self.modeling_tab = QtWidgets.QWidget()
        self.rigging_tab = QtWidgets.QWidget()
        
        # Set larger icon size
        icon_size = QtCore.QSize(32, 32)
        self.tab_widget.setIconSize(icon_size)
        
        self.tab_widget.addTab(self.modeling_tab, modeling_icon, "")
        self.tab_widget.addTab(self.rigging_tab, rigging_icon, "")
        
        # 方式1：禁用第二个标签页
        self.tab_widget.setTabEnabled(1, False)
        
        # 或者方式2：完全移除第二个标签页
        # self.tab_widget.removeTab(1)
        
        # Set tooltips
        self.tab_widget.setTabToolTip(0, "Modeling")
        self.tab_widget.setTabToolTip(1, "Rigging (Coming Soon)")  # 修改提示文本

    def create_tool_buttons(self):
        """
        创建工具按钮的方法
        步骤说明：
        1. 遍历工具配置
        2. 为每个分类创建标签页
        3. 在标签页中创建按钮网格
        4. 设置按钮属性和连接事件
        """
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "Icons")
        for i, (category, tools) in enumerate(self.tool_config.items()):
            tab = self.tab_widget.widget(i)
            tab_layout = QtWidgets.QVBoxLayout(tab)
            
            grid_layout = QtWidgets.QGridLayout()
            
            for j, tool in enumerate(tools):
                # 创建按钮
                icon = QtGui.QIcon(os.path.join(icon_path, tool["icon"]))
                button = ModItButton(tool["name"], icon)
                
                # 设置按钮属性
                button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                button.setMinimumSize(100, 40)
                
                # 设置提示信息
                if "tooltip" in tool:
                    tooltip_text = tool["tooltip"]
                    if "description" in tool:
                        tooltip_text += f"\n\n{tool['description']}"
                    button.setToolTip(tooltip_text)
                
                # 连接按钮点击事件
                button.clicked.connect(
                    lambda checked=False, name=tool["name"]: self.tool_clicked(name)
                )
                
                # 在网格中放置按钮
                row = j // 2  # 每行两个按钮
                col = j % 2
                grid_layout.addWidget(button, row, col)
            
            tab_layout.addLayout(grid_layout)
            tab_layout.addStretch()

    def create_layout(self):
        self.create_title_bar_layout()
        self.create_main_layout()

    def create_title_bar_layout(self):
        title_layout = QtWidgets.QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_button)

    def create_main_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.tab_widget)

    def setup_connections(self):
        self.close_button.clicked.connect(self.close)

    def set_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #3C3C3C;
                border: none;
            }
            QLabel {
                color: #CCCCCC;
            }
        """)

    # ----------------------
    # Event Handling
    # ----------------------

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def tool_clicked(self, tool_name):
        if tool_name == "MELtoPY":
            try:
                import melToPymelUI
                importlib.reload(melToPymelUI)
                print("Module reloaded successfully")
                print(f"Available attributes: {dir(melToPymelUI)}")
                melToPymelUI.show()
            except Exception as e:
                print(f"Error loading {tool_name}:")
                traceback.print_exc()
        elif tool_name == "ViewCapture":
            try:
                from Toolbox import screen_shot
                importlib.reload(screen_shot)
                screen_shot.show()
            except Exception as e:
                print(f"Error loading {tool_name}:")
                traceback.print_exc()
        elif tool_name == "MirrorTool":
            try:
                # 设置图标路径
                icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "Icons")
                icon_path = icon_path.replace("\\", "/")
                
                # 添加到Maya的图标搜索路径
                if "XBMLANGPATH" in os.environ:
                    os.environ["XBMLANGPATH"] = f"{icon_path};{os.environ['XBMLANGPATH']}"
                else:
                    os.environ["XBMLANGPATH"] = icon_path
                    
                # 执行MEL脚本
                import maya.mel as mel
                mel.eval('source "k_mirrorToolStartUI.mel"')
                mel.eval('k_mirrorToolStartUI()')
            except Exception as e:
                print(f"Error loading {tool_name}:")
                traceback.print_exc()
        else:
            print(f"{tool_name} - In development")

# ----------------------
# Global Functions
# ----------------------

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def show():
    global more_tools_window
    try:
        more_tools_window.close()
        more_tools_window.deleteLater()
    except:
        pass
    parent = maya_main_window()
    more_tools_window = MoreToolsWindow(parent)
    more_tools_window.show()
    more_tools_window.raise_()
    more_tools_window.activateWindow()

if __name__ == "__main__":
    show()
