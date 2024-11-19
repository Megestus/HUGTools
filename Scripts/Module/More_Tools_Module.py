from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial
import importlib
import sys
import os
import maya.cmds as cmds
import maya.mel as mel
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
                background-color: #2D2D2D;
                color: #CCCCCC;
                border: 1px solid #3C3C3C;
                border-radius: 3px;
                padding: 5px;
                font: bold 9pt 'Microsoft YaHei UI';
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #353535;
                border-color: #444444;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #252525;
                border-color: #B87D4B;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #2A2A2A;
                border-color: #333333;
                color: #666666;
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
        
        # 添加帮助信息显示状态标记
        self.help_message_visible = False
        
        # 重新组织工具配置
        self.tool_config = {
            "Modeling": [
                {
                    "name": "MirrorTool",                      
                    "icon": "MirrorTool/K_Mirror_icons/ShelfIcon.png",               
                    "tooltip": "Mirror Objects Tool",
                    "description": "Mirror objects across different axes with options"
                },
                {
                    "name": "SpeedCut",
                    "icon": "Im3dJoe/icons/speedCut.png",
                    "tooltip": "Speed Cut Tool", 
                    "description": "Quick mesh cutting and modeling tool"
                },
                {
                    "name": "AriScripts",
                    "icon": "AriScripts/icons/AriScriptLauncher.png",
                    "tooltip": "Ari Scripts Launcher",
                    "description": "启动Ari脚本工具集"
                }
            ],
            "Dev": [
                {
                    "name": "MELtoPY",                          
                    "icon": "MelToPy/icons/mao.png",                    
                    "tooltip": "Convert MEL code to Python code",
                    "description": "A tool for converting MEL scripts to Python"
                },
                {
                    "name": "IconView",
                    "icon": "iconview/icons/xianluomao.png",
                    "tooltip": "Maya Icon Viewer",
                    "description": "Browse and view Maya's built-in icons"
                },
                {
                    "name": "SmartMeshTools",
                    "icon": "dpSmartMeshTools/icons/SmartMeshTools.png",
                    "tooltip": "智能网格处理工具集",
                    "description": "提供网格的智能合并、分离、提取和复制功能"
                },
                {
                    "name": "RapidPlace",
                    "icon": "Im3dJoe/rapidPlace2_77/icons/rapidPlace.png",
                    "tooltip": "Rapid Place Tool (In Development)",
                    "description": "快速放置和复制工具 - 正在修复中",
                    "disabled": True  # 禁用该工具
                },
                {
                    "name": "NitroPoly",
                    "icon": "NitroPoly/icons/NitroPoly.png",
                    "tooltip": "NitroPoly Modeling Tool (In Development)",
                    "description": "Advanced polygon modeling toolset",
                    "disabled": True
                },
                {
                    "name": "ShelfCreator",
                    "icon": "commandButton.png",  # 可以更换为你想要的图标
                    "tooltip": "工具架创建器",
                    "description": "创建和管理Maya工具架按钮"
                }
            ]
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
                background: #3C3C3C;
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                margin-right: 2px;
                color: #CCCCCC;
                min-width: 80px;
                text-align: center;
                font: normal 9pt 'Microsoft YaHei UI';
            }
            QTabBar::tab:selected {
                background: #2D2D2D;
                border-color: #666666;
                border-bottom: 2px solid #B87D4B;
                margin-top: -2px;
                padding-top: 10px;
                color: #FFFFFF;
                font: bold 9pt 'Microsoft YaHei UI';
            }
            QTabBar::tab:hover:!selected {
                background: #454545;
                border-bottom: 1px solid #B87D4B;
            }
            QTabBar::tab:disabled {
                color: #666666;
                background: #2A2A2A;
            }
        """)
        
        self.modeling_tab = QtWidgets.QWidget()
        self.rigging_tab = QtWidgets.QWidget()
        
        self.tab_widget.addTab(self.modeling_tab, "Modeling")
        self.tab_widget.addTab(self.rigging_tab, "Dev")
        
        # 更新提示文本
        self.tab_widget.setTabToolTip(0, "Modeling Tools")
        self.tab_widget.setTabToolTip(1, "Development Tools")

    def create_tool_buttons(self):
        """
        创建工具按钮的方法
        """
        for i, (category, tools) in enumerate(self.tool_config.items()):
            tab = self.tab_widget.widget(i)
            tab_layout = QtWidgets.QVBoxLayout(tab)
            
            grid_layout = QtWidgets.QGridLayout()
            
            for j, tool in enumerate(tools):
                # 检查是否使用Qt标准图标
                if tool["icon"].startswith("SP_"):
                    icon = self.style().standardIcon(getattr(QtWidgets.QStyle, tool["icon"].replace(".png", "")))
                else:
                    icon_path = str(toolbox_dir / tool["icon"])
                    icon_path = icon_path.replace("\\", "/")
                    icon = QtGui.QIcon(icon_path)
                
                # 创建按钮
                button = ModItButton(tool["name"], icon)
                
                # 设置按钮属性
                button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                button.setMinimumSize(100, 40)
                
                # 如果工具被标记为禁用,则禁用按钮
                if tool.get("disabled", False):
                    button.setEnabled(False)
                
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
                
        elif tool_name == "MirrorTool":
            try:
                # 构建工特定的路径
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
                
                print("\n=== 具路径信息 ===")
                print(f"工具录: {mirror_tool_dir}")
                print(f"MEL脚本文件: {mel_script_path}")
                print(f"图标目录: {mirror_icons_dir}")
                print(f"MAYA_SCRIPT_PATH: {os.environ.get('MAYA_SCRIPT_PATH')}")
                print(f"XBMLANGPATH: {os.environ.get('XBMLANGPATH')}")
                
                # 执MEL本
                import maya.mel as mel
                mel.eval('source "k_mirrorToolStartUI.mel"')
                mel.eval('k_mirrorToolStartUI()')
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                traceback.print_exc()



                
        elif tool_name == "IconView":
            try:
                # 构建IconView工路径
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
                
        elif tool_name == "SmartMeshTools":
            try:
                # 构建MEL脚本路径
                smart_mesh_dir = toolbox_dir / "dpSmartMeshTools"
                mel_script_path = smart_mesh_dir / "dpSmartMeshTools.mel"
                
                # 检查文件是否存在
                if not mel_script_path.exists():
                    raise FileNotFoundError(f"找不到dpSmartMeshTools.mel文件: {mel_script_path}")
                    
                # 确保MEL脚本目录在Maya脚本路径中
                mel_dir = str(smart_mesh_dir).replace("\\", "/")
                if "MAYA_SCRIPT_PATH" in os.environ:
                    if mel_dir not in os.environ["MAYA_SCRIPT_PATH"]:
                        os.environ["MAYA_SCRIPT_PATH"] = f"{mel_dir};{os.environ['MAYA_SCRIPT_PATH']}"
                else:
                    os.environ["MAYA_SCRIPT_PATH"] = mel_dir

                print("\n=== 工具路径信息 ===")
                print(f"工具目录: {smart_mesh_dir}")
                print(f"MEL脚本文件: {mel_script_path}")
                print(f"MAYA_SCRIPT_PATH: {os.environ.get('MAYA_SCRIPT_PATH')}")

                # 执行MEL脚本
                import maya.mel as mel
                mel.eval('source "dpSmartMeshTools.mel"')
                mel.eval('dpSmartMeshTools()')
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                traceback.print_exc()


                
        elif tool_name == "AriScripts":
            try:
                # 建AriScripts具路径
                ari_scripts_dir = toolbox_dir / "AriScripts"
                ari_scripts_path = ari_scripts_dir / "AriScriptLauncherQt.py"
                
                # 检查文件是否存在
                if not ari_scripts_path.exists():
                    raise FileNotFoundError(f"找不到AriScriptLauncherQt.py文件: {ari_scripts_path}")
                
                # 确保模块所在目录在系统路径中
                module_dir = str(ari_scripts_dir)
                if module_dir not in sys.path:
                    sys.path.insert(0, module_dir)

                print("\n=== 工具路径信息 ===")
                print(f"工具目录: {ari_scripts_dir}")
                print(f"主程序文件: {ari_scripts_path}")
                print(f"系统路径: {module_dir}")

                try:
                    import AriScriptLauncherQt
                    importlib.reload(AriScriptLauncherQt)
                    AriScriptLauncherQt.show()
                except ImportError as ie:
                    print(f"导入AriScriptLauncherQt模块失败: {ie}")
                    print(f"当前sys.path: {sys.path}")
                    return
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                traceback.print_exc()




        elif tool_name == "NitroPoly":
            try:
                # 构建NitroPoly工具路径
                nitro_poly_dir = toolbox_dir / "NitroPoly"
                nitro_poly_path = nitro_poly_dir / "NitroPoly.py"
                
                # 检查文件是否存在
                if not nitro_poly_path.exists():
                    raise FileNotFoundError(f"找不到NitroPoly.py文件: {nitro_poly_path}")
                
                # 确保模块所在目录在系统路径中
                module_dir = str(nitro_poly_dir)
                if module_dir not in sys.path:
                    sys.path.insert(0, module_dir)

                print("\n=== 工具路径信息 ===")
                print(f"工具目录: {nitro_poly_dir}")
                print(f"主程序文件: {nitro_poly_path}")

                try:
                    import NitroPoly
                    importlib.reload(NitroPoly)
                    NitroPoly.main()
                except ImportError as ie:
                    print(f"导入NitroPoly模块失败: {ie}")
                    print(f"当前sys.path: {sys.path}")
                    return
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                traceback.print_exc()



        elif tool_name == "SpeedCut":
            try:
                # 构建SpeedCut工具路径
                speed_cut_dir = toolbox_dir / "SpeedCut"
                speed_cut_path = speed_cut_dir / "speedCut1.69.py"
                
                # 检查文件是否存在
                if not speed_cut_path.exists():
                    raise FileNotFoundError(f"找不到speedCut1.69.py文件: {speed_cut_path}")

                print("\n=== 工具路径信息 ===")
                print(f"工具目录: {speed_cut_dir}")
                print(f"主程序文件: {speed_cut_path}")

                # 直接执行文件
                script_path = str(speed_cut_path).replace("\\", "/")
                
                # 使用 exec() 和 open() 来执行文件
                cmds.evalDeferred(
                    f'with open("{script_path}", "r", encoding="utf-8") as f: exec(f.read())'
                )
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                traceback.print_exc()


                
        elif tool_name == "RapidPlace":
            try:
                # 构建RapidPlace工具路径
                rapid_place_dir = toolbox_dir / "RapidPlace"
                rapid_place_path = rapid_place_dir / "rapidPlace.py"
                
                # 检查文件是否存在
                if not rapid_place_path.exists():
                    raise FileNotFoundError(f"找不到rapidPlace.py文件: {rapid_place_path}")
                
                # 确保模块所在目录在系统路径中
                module_dir = str(rapid_place_dir)
                if module_dir not in sys.path:
                    sys.path.insert(0, module_dir)

                print("\n=== 工具路径信息 ===")
                print(f"工具目录: {rapid_place_dir}")
                print(f"主程序文件: {rapid_place_path}")
                print(f"系统路径: {module_dir}")

                try:
                    import rapidPlace
                    importlib.reload(rapidPlace)
                    rapidPlace.rapidPlace()
                except ImportError as ie:
                    print(f"导入rapidPlace模块失败: {ie}")
                    print(f"当前sys.path: {sys.path}")
                    return
                
            except Exception as e:
                print(f"\n=== 错误信息 ===")
                print(f"加载{tool_name}时出错:")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                traceback.print_exc()


                
        elif tool_name == "ShelfCreator":
            launch_shelf_creator()

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

def launch_shelf_creator(*args):
    """启动工具架创建器"""
    try:
        # 更新导入路径
        shelf_path = r'H:/Megestus_ArtDev/ArtTool/Maya/DevTools/HUGTools/Scripts/Toolbox/Binshelf_Craete'
        if shelf_path not in sys.path:
            sys.path.insert(0, shelf_path)
            
        # 导入模块
        import shelf_creator_window
        importlib.reload(shelf_creator_window)
        
        # 显示窗口
        shelf_creator_window.show_window()
            
    except Exception as e:
        cmds.warning(f"启动工具架创建器失败: {str(e)}")
        import traceback
        cmds.warning(traceback.format_exc())

if __name__ == "__main__":
    show()
