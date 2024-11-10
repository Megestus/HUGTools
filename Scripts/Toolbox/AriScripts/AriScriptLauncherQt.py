# -*- coding: utf-8 -*-
import os
import sys
import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets, QtGui, QtCore
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import webbrowser
import json

def maya_main_window():
    """获取Maya主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class RoundedButton(QtWidgets.QPushButton):
    """自定义圆角按钮类"""
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

class CommandButton(QtWidgets.QWidget):
    """命令按钮组件"""
    def __init__(self, command, icon, description, has_options=False, launcher=None, parent=None):
        super(CommandButton, self).__init__(parent)
        self.command = command
        self.description = description
        self.has_options = has_options
        self.launcher = launcher
        self.setup_ui(command, icon, description)
        self.create_context_menu()
        
    def setup_ui(self, command, icon, description):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        
        # 图标按钮 - 不设置工具提示
        self.icon_button = QtWidgets.QPushButton()
        self.icon_button.setIcon(QtGui.QIcon(icon))
        self.icon_button.setIconSize(QtCore.QSize(32, 32))
        self.icon_button.setFixedSize(32, 32)
        self.icon_button.setToolTip("")  # 清除工具提示
        
        # 命令名称标签
        self.name_label = QtWidgets.QLabel(command)  # 显示原始命令名
        self.name_label.setStyleSheet("color: #D0D0D0; font-weight: bold;")
        
        if self.launcher:
            # 获取工具配置信息
            tool_info = self.launcher.tool_configs.get(command, {})
            tooltip_name = tool_info.get("提示名称", "")
            cn_desc = tool_info.get("中文描述", "")
            en_desc = tool_info.get("英文描述", "")
            
            # 只为标签设置工具提示
            tooltip = f"{tooltip_name}\n{cn_desc}\n{en_desc}" if tooltip_name else (f"{cn_desc}\n{en_desc}" if cn_desc or en_desc else command)
            self.name_label.setToolTip(tooltip)
            
            # 移除整体组件的工具提示
            self.setToolTip("")
        
        # Options按钮
        if self.has_options:
            self.options_button = QtWidgets.QPushButton()
            self.options_button.setIcon(QtGui.QIcon(":nodeGrapherModeAllLarge.png"))
            self.options_button.setIconSize(QtCore.QSize(32, 32))
            self.options_button.setFixedSize(32, 32)
            self.options_button.setToolTip(f"{command} Options")
            self.options_button.clicked.connect(self.execute_options)
        
        # 添加到布局
        layout.addWidget(self.icon_button)
        layout.addWidget(self.name_label, 1)
        if self.has_options:
            layout.addWidget(self.options_button)

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = QtWidgets.QMenu(self)
        
        # 添加到工具架 - 使用星星图标
        add_shelf_action = QtWidgets.QAction(self)
        add_shelf_action.setText("Add to Shelf")
        add_shelf_action.setIcon(QtGui.QIcon(":SE_FavoriteStar.png"))  # 星星图标
        add_shelf_action.triggered.connect(self.add_to_shelf)
        self.context_menu.addAction(add_shelf_action)
        
        # 帮助文档 - 使用帮助图标
        help_action = QtWidgets.QAction(self)
        help_action.setText("Help")
        help_action.setIcon(QtGui.QIcon(":help.png"))  # 帮助图标
        help_action.triggered.connect(self.show_help)
        self.context_menu.addAction(help_action)
        
        # 打开目录 - 使用文件夹图标
        open_dir_action = QtWidgets.QAction(self)
        open_dir_action.setText("Open Directory")
        open_dir_action.setIcon(QtGui.QIcon(":fileOpen.png"))  # 文件夹图标
        open_dir_action.triggered.connect(self.open_directory)
        self.context_menu.addAction(open_dir_action)
        
    def contextMenuEvent(self, event):
        """显示右键菜单"""
        self.context_menu.exec_(event.globalPos())

    def execute_command(self):
        """执行MEL命令"""
        try:
            mel.eval(f'{self.command}()')
        except Exception as e:
            cmds.warning(f"执行命令失败 [{self.command}]: {str(e)}")

    def add_to_shelf(self):
        """添加到工具架"""
        try:
            shelf_layout = mel.eval('$tmpVar=$gShelfTopLevel')
            active_shelf = cmds.shelfTabLayout(shelf_layout, q=True, selectTab=True)
            
            # 获取图标路径
            icon_path = self.launcher.get_icon_path(self.command)
            
            # 创建工具架按钮
            cmds.shelfButton(
                parent=active_shelf,
                image=icon_path,  # 使用图标路径而不是Qt图标对象
                label=self.command,
                command=f"{self.command}()",
                annotation=self.description,
                style='iconOnly',
                width=32,
                height=32
            )
            
            # 如果有Options版本，添加双击命令
            if self.has_options:
                cmds.shelfButton(
                    shelf_button,
                    edit=True,
                    doubleClickCommand=f"{self.command}Options"
                )
                
        except Exception as e:
            cmds.warning(f"添加到工具架失败: {str(e)}")

    def show_help(self):
        """显示帮助文档"""
        try:
            if self.launcher and self.command in self.launcher.tool_urls:
                url = self.launcher.tool_urls[self.command]
                if url and url.lower() != "null":
                    webbrowser.open(url)
                else:
                    cmds.warning(f"没有找到 {self.command} 的帮助文档")
        except Exception as e:
            cmds.warning(f"打开帮助文档失败: {str(e)}")

    def open_directory(self):
        """打开脚本所在目录"""
        try:
            script_dir = os.path.join(os.path.dirname(__file__), "AriScripts", "scripts")
            if os.path.exists(script_dir):
                os.startfile(script_dir)
        except Exception as e:
            cmds.warning(f"打开目录失败: {str(e)}")

    def execute_options(self):
        """执行Options命令"""
        try:
            # 先检查Options命令是否存在
            options_command = f"{self.command}Options"
            # 使用catch执行mel命令，这样可以避免错误提示
            exists_check = f'catch(eval("{options_command}"));'
            result = mel.eval(exists_check)
            
            if result != 0:  # 如果命令不存在
                cmds.warning(f"该工具没有Options设置: {options_command}")
                return
                
            # 如果命令存在则执行
            mel.eval(f'{self.command}Options')
            
        except Exception as e:
            cmds.warning(f"执行Options命令失败 [{self.command}]: {str(e)}")

class AriScriptLauncherUI(QtWidgets.QDialog):
    """主窗UI类"""
    def __init__(self, launcher, parent=maya_main_window()):
        super(AriScriptLauncherUI, self).__init__(parent)
        self.launcher = launcher  # 保存launcher引用
        self.setWindowTitle("AriScriptLauncher")
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        
        # 修改窗口样式
        self.setStyleSheet("""
            QDialog {
                background-color: #383838;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                color: #D0D0D0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QLabel {
                color: #D0D0D0;
            }
            QLineEdit {
                background-color: #2B2B2B;  /* 深背景 */
                color: #D0D0D0;            /* 浅色文字 */
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                selection-background-color: #4B4B4B;  /* 选中文本的背景色 */
            }
            QLineEdit:focus {
                border: 1px solid #6B6B6B;  /* 获得焦点时的边框颜色 */
            }
            QLineEdit::placeholder {
                color: #808080;  /* 占位符文字颜色 */
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#scrollContents {
                background-color: #383838;
            }
            QPushButton {
                background-color: #454545;
                color: #D0D0D0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
        """)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
        # 自动加载工具列表
        self.reload_tools()  # 添加这行，在窗口创建完成后自动加载工具

    def create_widgets(self):
        """创建所有UI组件"""
        # 帮助按钮
        self.help_button = QtWidgets.QPushButton()
        self.help_button.setIcon(QtGui.QIcon(":help.png"))
        self.help_button.setFixedSize(20, 20)
        self.help_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #505050;
                border-radius: 10px;
            }
        """)
        self.help_button.setToolTip("显示帮助信息")
        
        # 搜索框
        self.search_field = QtWidgets.QLineEdit()
        self.search_field.setPlaceholderText("Search...")
        
        # 工具列表区域
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        
        # 重载按钮
        self.reload_button = QtWidgets.QPushButton("Reload")

    def create_layouts(self):
        """创建布局"""
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # 搜索栏布局 - 添加帮助按钮
        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.help_button)
        search_layout.addWidget(self.search_field)
        
        # 添加到布局
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.reload_button)

    def create_connections(self):
        """创建信号连接"""
        # 搜索框
        self.search_field.textChanged.connect(self.filter_commands)
        
        # 重载按钮
        self.reload_button.clicked.connect(self.reload_tools)
        
        # 帮助按钮连接
        self.help_button.clicked.connect(self.show_help)

    def show_help(self):
        """显示帮助窗口"""
        try:
            # 创建并显示帮助窗口
            help_dialog = HelpDialog(self)
            
            # 设置窗口样式
            help_dialog.setStyleSheet("""
                QWidget {
                    background-color: #383838;
                    color: #D0D0D0;
                }
                QTextEdit {
                    background-color: #2B2B2B;
                    color: #D0D0D0;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px;
                }
                QPushButton {
                    background-color: #454545;
                    color: #D0D0D0;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 6px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QPushButton:pressed {
                    background-color: #353535;
                }
            """)
            
            help_dialog.show()  # 使用show()而不是exec_()
            
        except Exception as e:
            cmds.warning(f"显示帮助窗口失败: {str(e)}")

    def filter_commands(self, text):
        """过滤命令列表"""
        text = text.lower()
        show_next_separator = False  # 用于控制是否显示下一个分隔线
        
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            
            if isinstance(widget, CommandButton):
                # 检查命令按钮是否匹配搜索文本
                is_visible = text in widget.command.lower() or text in widget.description.lower()
                widget.setVisible(is_visible)
                show_next_separator = is_visible  # 如果当前按钮可见，则显示下一个分隔线
                
            elif isinstance(widget, QtWidgets.QFrame):  # 分隔线
                widget.setVisible(show_next_separator)
                show_next_separator = False  # 重置标志

    def browse_directory(self, dir_type):
        """浏览目录"""
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.script_path.text() if dir_type == "script" else self.icon_path.text()
        )
        if path:
            if dir_type == "script":
                self.script_path.setText(path)
            else:
                self.icon_path.setText(path)
            self.reload_tools()

    def open_directory(self, dir_type):
        """打开目录"""
        path = self.script_path.text() if dir_type == "script" else self.icon_path.text()
        if os.path.exists(path):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))

    def reload_tools(self):
        """重新加载工具列表"""
        # 清除现有列表
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 重新加载工具
        if self.launcher:
            self.launcher.get_mel_list()
            # 添加工具按钮
            for command in self.launcher.mel_list:
                if not command.endswith("Options"):
                    self.add_command_button(command)

    def add_command_button(self, command):
        """添加命令按钮"""
        try:
            # 获取描述和图标
            description = self.launcher.tool_descriptions.get(command, "")
            icon_path = self.launcher.get_icon_path(command)
            
            # 检查是否有Options版本
            has_options = f"{command}Options" in self.launcher.mel_list
            
            # 创建按钮 - 传入launcher
            button = CommandButton(
                command=command, 
                icon=icon_path, 
                description=description, 
                has_options=has_options,
                launcher=self.launcher  # 传入launcher引用
            )
            self.scroll_layout.addWidget(button)
            
            # 添加分隔线
            separator = QtWidgets.QFrame()
            separator.setFrameShape(QtWidgets.QFrame.HLine)
            separator.setFrameShadow(QtWidgets.QFrame.Sunken)
            separator.setStyleSheet("background-color: #555555;")
            self.scroll_layout.addWidget(separator)
            
        except Exception as e:
            cmds.warning(f"添加命令钮失败 [{command}]: {str(e)}")

    def setStyleSheet(self, style):
        # 扩展样式表以包含工具提示样式
        extended_style = style + """
            QToolTip {
                background-color: #2B2B2B;
                color: #D0D0D0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
            }
            QMenu {
                background-color: #383838;
                color: #D0D0D0;
                border: 1px solid #555555;
            }
            QMenu::item {
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background-color: #505050;
            }
            QScrollBar:vertical {
                background-color: #2B2B2B;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: #2B2B2B;
            }
        """
        super(AriScriptLauncherUI, self).setStyleSheet(extended_style)

    def toggle_directory_content(self, checked):
        """处理目录组的折叠/展开"""
        self.directory_content.setVisible(checked)
        # 调整窗口大小以适应内容
        self.adjustSize()

class AriScriptLauncher:
    """业务逻辑类"""
    def __init__(self):
        self.ui = None
        self.mel_list = []
        self.loaded_commands = set()
        
        # 从JSON文件加载工具描述
        self.load_descriptions()
        
        # 添加支持的前缀列表
        self.supported_prefixes = ["Ari", "Me_"]  # 可以在这里添加更多前缀
        
        # 初始化数据
        self.init_data()
        
    def load_descriptions(self):
        """从JSON文件加载工具描述"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config", "tool_descriptions.json")
            if not os.path.exists(config_path):
                self.create_default_config(config_path)
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 获取工具配置
            self.tool_configs = config.get('工具配置', {})
            
            # 为了保持兼容性，仍然保留原有的字典
            self.tool_descriptions = {}
            self.tool_tips = {}
            self.tool_urls = {}
            
            for tool_name, tool_info in self.tool_configs.items():
                self.tool_descriptions[tool_name] = tool_info.get('中文描述', '')
                self.tool_tips[tool_name] = tool_info.get('英文描述', '')
                self.tool_urls[tool_name] = tool_info.get('URL', '')
            
            self.mel_name_list = list(self.tool_urls.keys())
            self.mel_url_list = list(self.tool_urls.values())
            
        except Exception as e:
            cmds.warning(f"加载工具描述失败: {str(e)}")
            self.tool_configs = {}
            self.tool_descriptions = {}
            self.tool_tips = {}
            self.tool_urls = {}
            self.mel_name_list = []
            self.mel_url_list = []
        
    def create_default_config(self, config_path):
        """创建默认配置文件"""
        try:
            # 确保config目录存在
            config_dir = os.path.dirname(config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # 创建默认配置
            default_config = {
                "说明": "这是AriScripts工具集的配置文件，用于定义每个工具的描述信息。添加新工具时，请按照示例格式添加相应的配置。",
                "示例": {
                    "工具名称": {
                        "中文描述": "在这里填写工具的中文说明",
                        "英文描述": "Write tool description in English here",
                        "URL": "在这里填写工具的帮助文档链接"
                    }
                },
                "工具配置": {}
            }
            
            # 写入配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
                
            cmds.warning(f"已创建默认配置文件: {config_path}")
            
        except Exception as e:
            cmds.warning(f"创建默认配置文件失败: {str(e)}")
        
    def init_data(self):
        """初始化数据"""
        try:
            # 获取MEL列表
            self.get_mel_list()
            # 输出加载信息
            cmds.warning("数据初始化完成")
        except Exception as e:
            cmds.warning(f"初始化据失败: {str(e)}")
        
    def get_mel_list(self):
        """获取MEL脚本列表"""
        try:
            # 修改MEL脚本目录路径为scripts件夹
            scripts_dir = os.path.join(os.path.dirname(__file__), "scripts").replace("\\", "/")
            if not os.path.exists(scripts_dir):
                os.makedirs(scripts_dir)
                cmds.warning(f"创建scripts目录: {scripts_dir}")
            
            print("\n=== 目录信息 ===")
            print(f"当前文件: {__file__}")
            print(f"脚本目录: {scripts_dir}")
            
            # 获取所有MEL文件
            mel_files = []
            if os.path.exists(scripts_dir):
                # 修改文件过滤逻辑，支持多个前缀
                mel_files = [f for f in os.listdir(scripts_dir) 
                           if f.endswith('.mel') and 
                           any(f.startswith(prefix) for prefix in self.supported_prefixes)]
                print(f"找到的MEL文件: {mel_files}")
            
            # 更新MEL列表
            self.mel_list = []
            options_list = []
            
            # 分类处理MEL文件
            for mel_file in mel_files:
                command = os.path.splitext(mel_file)[0]
                if command == "AriScriptLauncher":  # 跳过启动器自身
                    continue
                    
                # 将文件内容加载到Maya中
                mel_file_path = os.path.join(scripts_dir, mel_file).replace("\\", "/")
                try:
                    # 尝试不同的编码
                    encodings = ['shift-jis', 'cp932', 'gbk', 'utf-8', 'latin1']
                    mel_content = None
                    
                    for encoding in encodings:
                        try:
                            with open(mel_file_path, 'r', encoding=encoding) as f:
                                mel_content = f.read()
                                print(f"成功使用 {encoding} 编码读取: {mel_file}")
                                break  # 如果成功读取，跳出循环
                        except UnicodeDecodeError:
                            continue
                    
                    if mel_content is None:
                        raise UnicodeDecodeError(f"无法用支持的编码读取文件: {mel_file}")
                        
                    mel.eval(mel_content)  # 加载MEL文件内容
                    print(f"成功加载MEL文件: {mel_file}")
                    
                    # 如果成功加载，添加到相应列表
                    if command.endswith("Options"):
                        options_list.append(command)
                    else:
                        self.mel_list.append(command)
                        
                except Exception as e:
                    cmds.warning(f"加载MEL文件失败 [{mel_file}]: {str(e)}")
                    continue  # 跳过这个文件，继续处理下一个
            
            # 将Options命令添加到对应的主命令后面
            for command in self.mel_list[:]:
                options_command = f"{command}Options"
                if options_command in options_list:
                    self.mel_list.append(options_command)
            
            print(f"\n=== 加载结果 ===")
            print(f"主命令列表: {self.mel_list}")
            print(f"Options命令列表: {options_list}")
            cmds.warning(f"加载了 {len(self.mel_list)} 个MEL命令")
            return self.mel_list
            
        except Exception as e:
            cmds.warning(f"获取MEL列表失败: {str(e)}")
            import traceback
            cmds.warning(traceback.format_exc())
            return []
        
    def get_icon_path(self, command):
        """获取命令的标路径"""
        try:
            # 修改图标目录路径为icons文件夹
            icon_dir = os.path.join(os.path.dirname(__file__), "icons").replace("\\", "/")
            icon_path = os.path.join(icon_dir, f"{command}.png")
            
            # 如果图标存在则返回路径，否则返回默认图标
            return icon_path if os.path.isfile(icon_path) else "commandButton.png"
        except Exception as e:
            cmds.warning(f"获取图标路径失败 [{command}]: {str(e)}")
            return "commandButton.png"
        
    def show(self):
        if not self.ui:
            self.ui = AriScriptLauncherUI(self)  # 传入self作为launcher参数
        self.ui.show()

class HelpDialog(QtWidgets.QWidget):
    """帮助窗口"""
    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        self.setWindowTitle("帮助")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setWindowFlags(QtCore.Qt.Window)
        
        # 创建主布局
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 添加"如何使用"部分
        usage_group = QtWidgets.QGroupBox("如何使用")
        usage_group.setStyleSheet(self.get_group_style())
        usage_layout = QtWidgets.QVBoxLayout(usage_group)
        
        usage_text = QtWidgets.QTextEdit()
        usage_text.setReadOnly(True)
        usage_text.setMaximumHeight(300)
        usage_text.setStyleSheet(self.get_text_style())
        usage_text.setHtml("""
            <p style="color: #D0D0D0; font-size: 13px;">基本使用说明:</p>
            <ol style="color: #D0D0D0;">
                <li>工具操作：
                    <ul>
                        <li>左键点击工具图标：直接执行对应功能</li>
                        <li>右键点击工具：打开上下文菜单
                            <ul>
                                <li>Add to Shelf：将工具添加到Maya工具架</li>
                                <li>Help：打开工具的在线帮助文档 有GIF可以看</li>
                                <li>Open Directory：打开工具所在目录</li>
                            </ul>
                        </li>
                        <li>鼠标悬停在工具名称上：显示工具的详细说明</li>
                    </ul>
                </li>
                <li>工具设置：
                    <ul>
                        <li>部分工具右侧有设置按钮（齿轮图标）</li>
                        <li>点击设置按钮可以打开工具的选项窗口</li>
                        <li>在工具架中双击工具图标也可以打开设置</li>
                    </ul>
                </li>
                <li>快速查找：
                    <ul>
                        <li>使用顶部的搜索框可以快速筛选工具</li>
                        <li>支持按工具名称和描述搜索</li>
                        <li>搜索支持中英文</li>
                    </ul>
                </li>
                <li>其他功能：
                    <ul>
                        <li>点击Reload按钮可以重新加载所有工具</li>
                        <li>点击帮助按钮（?）可以查看此帮助窗口</li>
                        <li>工具列表会记住上次的位置和大小</li>
                    </ul>
                </li>
            </ol>
        """)
        usage_layout.addWidget(usage_text)
        layout.addWidget(usage_group)
        
        # 添加"如何添加新工具"部分（可折叠）
        self.add_tool_group = QtWidgets.QGroupBox("如何添加新工具")
        self.add_tool_group.setCheckable(True)
        self.add_tool_group.setChecked(False)  # 默认折叠
        self.add_tool_group.setStyleSheet(self.get_group_style())
        
        # 创建一个容器widget来包含所有内容
        self.content_widget = QtWidgets.QWidget()
        add_tool_layout = QtWidgets.QVBoxLayout(self.content_widget)
        
        # 创建步骤说明
        steps_text = QtWidgets.QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setMaximumHeight(150)
        steps_text.setStyleSheet(self.get_text_style())
        steps_text.setHtml("""
            <p style="color: #D0D0D0;">使用步骤:</p>
            <ol style="color: #D0D0D0;">
                <li>访问作者博客: <a href="http://cgjishu.net/" style="color: #B87D4B;">http://cgjishu.net/</a></li>
                <li>找到并下载需要的插件</li>
                <li>将MEL文件放入scripts文件夹</li>
                <li>将图标文件放入icons文件夹</li>
                <li>点击Reload按钮刷新工具列表</li>
                <li>最后还可以在下方编辑工具描述进行编辑名称提示与备注</li>
            </ol>
        """)
        add_tool_layout.addWidget(steps_text)
        
        # 创建文件夹按钮组
        folders_group = QtWidgets.QGroupBox("快速打开文件夹")
        folders_group.setStyleSheet(self.get_group_style())
        folders_layout = QtWidgets.QVBoxLayout(folders_group)
        
        # Scripts文件夹按钮
        scripts_btn = QtWidgets.QPushButton("打开Scripts文件夹")
        scripts_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        scripts_btn.clicked.connect(lambda: self.open_folder("scripts"))
        scripts_btn.setStyleSheet(self.get_button_style())
        folders_layout.addWidget(scripts_btn)
        
        # Icons文件夹按钮
        icons_btn = QtWidgets.QPushButton("打开Icons文件夹")
        icons_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        icons_btn.clicked.connect(lambda: self.open_folder("icons"))
        icons_btn.setStyleSheet(self.get_button_style())
        folders_layout.addWidget(icons_btn)
        
        add_tool_layout.addWidget(folders_group)
        
        # 添加按钮组
        buttons_layout = QtWidgets.QVBoxLayout()
        
        # 添加访问博客按钮
        blog_btn = QtWidgets.QPushButton("访问作者博客")
        blog_btn.setIcon(QtGui.QIcon(":webBrowser.png"))
        blog_btn.clicked.connect(lambda: webbrowser.open("http://cgjishu.net/"))
        blog_btn.setStyleSheet(self.get_button_style())
        buttons_layout.addWidget(blog_btn)
        
        # 添加刷新按钮
        reload_btn = QtWidgets.QPushButton("刷新工具列表")
        reload_btn.setIcon(QtGui.QIcon(":refresh.png"))
        reload_btn.clicked.connect(self.reload_tools)
        reload_btn.setStyleSheet(self.get_button_style())
        buttons_layout.addWidget(reload_btn)
        
        # 添加编辑配置按钮
        config_btn = QtWidgets.QPushButton("编辑工具描述")
        config_btn.setIcon(QtGui.QIcon(":edit.png"))
        config_btn.clicked.connect(self.open_config)
        config_btn.setStyleSheet(self.get_button_style())
        buttons_layout.addWidget(config_btn)
        
        add_tool_layout.addLayout(buttons_layout)
        
        # 创建主布局
        group_layout = QtWidgets.QVBoxLayout(self.add_tool_group)
        group_layout.addWidget(self.content_widget)
        
        # 设置初始状态
        self.content_widget.setVisible(False)
        
        layout.addWidget(self.add_tool_group)
        
        # 连接折叠信号
        self.add_tool_group.toggled.connect(self.on_group_toggled)

    def get_group_style(self):
        """获取组框样式"""
        return """
            QGroupBox {
                color: #D0D0D0;
                border: 1px solid #555555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QGroupBox::indicator {
                width: 16px;
                height: 16px;
                margin-left: 2px;
            }
            QGroupBox::indicator:unchecked {
                image: url(:arrowRight.png);  /* 使用Maya内置的右箭头图标 */
            }
            QGroupBox::indicator:checked {
                image: url(:arrowDown.png);   /* 使用Maya内置的下箭头图标 */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;  /* 给图标留出空间 */
                padding: 0 5px;
            }
        """

    def on_group_toggled(self, checked):
        """处理组框折叠/展开"""
        self.content_widget.setVisible(checked)  # 显示或隐藏内容
        
        # 先调整内容大小
        self.adjustSize()
        
        # 获取当前窗口位置
        current_pos = self.pos()
        
        if checked:  # 展开时
            # 保存折叠时的窗口大小
            self.collapsed_size = self.size()
        else:  # 折叠时
            # 调整到之前保存的折叠大小
            if hasattr(self, 'collapsed_size'):
                self.resize(self.collapsed_size)
            else:
                self.adjustSize()
        
        # 保持窗口位置不变
        self.move(current_pos)

    def open_folder(self, folder_type):
        """打开指定文件夹"""
        try:
            base_dir = os.path.dirname(__file__)
            if folder_type == "scripts":
                folder_path = os.path.join(base_dir, "scripts")
            else:
                folder_path = os.path.join(base_dir, "icons")
                
            folder_path = folder_path.replace("\\", "/")
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                
            os.startfile(folder_path)
            
        except Exception as e:
            cmds.warning(f"打开{folder_type}文件夹失败: {str(e)}")

    def reload_tools(self):
        """刷新工具列表"""
        try:
            if hasattr(self.parent(), "reload_tools"):
                self.parent().reload_tools()
                cmds.warning("工具列表已刷新")
        except Exception as e:
            cmds.warning(f"刷新工具列表失败: {str(e)}")

    def get_text_style(self):
        """获取文本样式"""
        return """
            QTextEdit {
                background-color: #2B2B2B;
                color: #D0D0D0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                selection-background-color: #4B4B4B;
            }
        """

    def get_button_style(self):
        """获取按钮样式"""
        return """
            QPushButton {
                background-color: #454545;
                color: #D0D0D0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #353535;
                border-color: #B87D4B;
            }
        """

    def open_config(self):
        """打开置文件"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config", "tool_descriptions.json")
            if not os.path.exists(config_path):
                os.makedirs(os.path.dirname(config_path))
                
            os.startfile(config_path)
            
        except Exception as e:
            cmds.warning(f"打开配置文件失败: {str(e)}")

def show():
    """显示主口"""
    global ari_script_launcher
    try:
        if 'ari_script_launcher' in globals():
            if hasattr(ari_script_launcher, 'ui') and ari_script_launcher.ui:
                ari_script_launcher.ui.close()
                ari_script_launcher.ui.deleteLater()
            ari_script_launcher = None
    except:
        pass
    
    try:
        ari_script_launcher = AriScriptLauncher()
        ari_script_launcher.show()
    except Exception as e:
        cmds.warning(f"启动Qt版本启动器失败: {str(e)}")
        import traceback
        cmds.warning(traceback.format_exc())
    