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

# 添加调试信息
print(f"Toolbox path: {toolbox_path}")

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
                    "icon": "MelToPy/icons/mao.png",            # 更新图标路径                      
                    "tooltip": "Convert MEL code to Python code",
                    "description": "A tool for converting MEL scripts to Python"
                },
                {
                    "name": "ViewCapture",                      
                    "icon": "ViewCapture/icons/boxuemao.png",   # 更新图标路径                    
                    "tooltip": "Maya Viewport Screenshot Tool",  
                    "description": "Capture high quality screenshots of Maya viewport with custom path and name"
                },
                {
                    "name": "MirrorTool",                      
                    "icon": "MirrorTool/K_Mirror_icons/ShelfIcon.png",  # 已经更新的图标路径                  
                    "tooltip": "Mirror Objects Tool",
                    "description": "Mirror objects across different axes with options"
                },
                {
                    "name": "IconView",
                    "icon": "iconview/icons/xianluomao.png",
                    "tooltip": "Maya Icon Viewer",
                    "description": "Browse and view Maya's built-in icons"
                }
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
        """
        # 使用toolbox_dir来构建图标路径
        for i, (category, tools) in enumerate(self.tool_config.items()):
            tab = self.tab_widget.widget(i)
            tab_layout = QtWidgets.QVBoxLayout(tab)
            
            grid_layout = QtWidgets.QGridLayout()
            
            for j, tool in enumerate(tools):
                # 构建完整的图标路径
                icon_path = str(toolbox_dir / tool["icon"])
                icon_path = icon_path.replace("\\", "/")
                
                # 创建按钮
                icon = QtGui.QIcon(icon_path)
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

        # 添加调试信息
        print("\n=== 图标路径信息 ===")
        for category, tools in self.tool_config.items():
            for tool in tools:
                icon_path = str(toolbox_dir / tool["icon"])
                print(f"{tool['name']}图标路径: {icon_path}")

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
                # 构建MelToPy工具路径
                mel_to_py_dir = toolbox_dir / "MelToPy"
                mel_to_py_path = mel_to_py_dir / "melToPymelUI.py"
                
                # 检查文件是否存在
                if not mel_to_py_path.exists():
                    raise FileNotFoundError(f"找不到melToPymelUI.py文件: {mel_to_py_path}")
                
                # 确保模块所在目录在系统路径中
                module_dir = str(mel_to_py_dir)
                if module_dir not in sys.path:
                    sys.path.insert(0, module_dir)

                print("\n=== 工具路径信息 ===")
                print(f"工具目录: {mel_to_py_dir}")
                print(f"主程序文件: {mel_to_py_path}")
                print(f"系统路径: {module_dir}")

                try:
                    import melToPymelUI
                    importlib.reload(melToPymelUI)
                except ImportError as ie:
                    print(f"导入melToPymelUI模块失败: {ie}")
                    print(f"当前sys.path: {sys.path}")
                    return
                
                melToPymelUI.show()
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                traceback.print_exc()
                
        elif tool_name == "ViewCapture":
            try:
                # 构建ViewCapture工具路径
                view_capture_dir = toolbox_dir / "ViewCapture"
                screen_shot_path = view_capture_dir / "screen_shot.py"
                
                # 检查文件是否存在
                if not screen_shot_path.exists():
                    raise FileNotFoundError(f"找不到screen_shot.py文件: {screen_shot_path}")
                
                # 确保模块所在目录在系统路径中
                module_dir = str(view_capture_dir)
                if module_dir not in sys.path:
                    sys.path.insert(0, module_dir)

                print("\n=== 工具路径信息 ===")
                print(f"工具目录: {view_capture_dir}")
                print(f"主程序文件: {screen_shot_path}")
                print(f"系统路径: {module_dir}")

                try:
                    import screen_shot
                    importlib.reload(screen_shot)
                except ImportError as ie:
                    print(f"导入screen_shot模块失败: {ie}")
                    print(f"当前sys.path: {sys.path}")
                    return
                
                screen_shot.show()
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                traceback.print_exc()

        elif tool_name == "MirrorTool":
            try:
                # 构建工具特定的路径
                mirror_tool_dir = toolbox_dir / "MirrorTool"
                mirror_icons_dir = mirror_tool_dir / "K_Mirror_icons"
                mel_script_path = mirror_tool_dir / "k_mirrorToolStartUI.mel"
                
                # 确保所需目录都存在
                required_dirs = {
                    "镜像工具目录": mirror_tool_dir,
                    "镜像工具图标目录": mirror_icons_dir,
                    "MEL脚本文件": mel_script_path
                }
                
                for dir_name, dir_path in required_dirs.items():
                    if not dir_path.exists():
                        raise FileNotFoundError(f"找不到{dir_name}: {dir_path}")
                
                # 设置MAYA_SCRIPT_PATH以找到MEL脚本
                mirror_tool_path_str = str(mirror_tool_dir).replace("\\", "/")
                if "MAYA_SCRIPT_PATH" in os.environ:
                    if mirror_tool_path_str not in os.environ["MAYA_SCRIPT_PATH"]:
                        os.environ["MAYA_SCRIPT_PATH"] = f"{mirror_tool_path_str};{os.environ['MAYA_SCRIPT_PATH']}"
                else:
                    os.environ["MAYA_SCRIPT_PATH"] = mirror_tool_path_str
                
                # 设置XBMLANGPATH以找到图标
                mirror_icons_path_str = str(mirror_icons_dir).replace("\\", "/")
                if "XBMLANGPATH" in os.environ:
                    if mirror_icons_path_str not in os.environ["XBMLANGPATH"]:
                        os.environ["XBMLANGPATH"] = f"{mirror_icons_path_str};{os.environ['XBMLANGPATH']}"
                else:
                    os.environ["XBMLANGPATH"] = mirror_icons_path_str
                
                print("\n=== 工具路径信息 ===")
                print(f"工具目录: {mirror_tool_dir}")
                print(f"MEL脚本文件: {mel_script_path}")
                print(f"图标目录: {mirror_icons_dir}")
                print(f"MAYA_SCRIPT_PATH: {os.environ.get('MAYA_SCRIPT_PATH')}")
                print(f"XBMLANGPATH: {os.environ.get('XBMLANGPATH')}")
                
                # 执行MEL脚本
                import maya.mel as mel
                mel.eval('source "k_mirrorToolStartUI.mel"')
                mel.eval('k_mirrorToolStartUI()')
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                traceback.print_exc()



                
        elif tool_name == "IconView":
            try:
                # 构建IconView工具路径
                icon_view_dir = toolbox_dir / "iconview"
                icon_view_path = icon_view_dir / "iconview.py"
                
                # 检查文件是否存在
                if not icon_view_path.exists():
                    raise FileNotFoundError(f"找不到iconview.py文件: {icon_view_path}")
                
                # 确保模块所在目录在系统路径中
                module_dir = str(icon_view_dir)
                if module_dir not in sys.path:
                    sys.path.insert(0, module_dir)

                print("\n=== 工具路径信息 ===")
                print(f"工具目录: {icon_view_dir}")
                print(f"主程序文件: {icon_view_path}")
                print(f"系统路径: {module_dir}")

                try:
                    import iconview
                    importlib.reload(iconview)
                except ImportError as ie:
                    print(f"导入iconview模块失败: {ie}")
                    print(f"当前sys.path: {sys.path}")
                    return
                
                iconview.create_icon_viewer()
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
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
