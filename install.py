import os
import sys
import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets, QtGui, QtCore
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import webbrowser
import importlib

TOOLBOX_NAME = "HUGTools"
TOOLBOX_VERSION = "1.0.0"
TOOLBOX_ICON = "MainUI.png"
TOOLBOX_MAIN_MODULE = "HUGTools_main"
TOOLBOX_HELP_URL = "https://megestus.github.io/HUGweb/"  

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class RoundedButton(QtWidgets.QPushButton):
    def __init__(self, text):
        super(RoundedButton, self).__init__(text)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #D0D0D0;
                color: #303030;
                border-radius: 10px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
            """
        )

class InstallDialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(InstallDialog, self).__init__(parent)
        self.setWindowTitle(f"{TOOLBOX_NAME} 安装程序")
        self.setFixedSize(220, 120)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowContextHelpButtonHint)

        # 设置窗口图标
        icon_path = os.path.join(get_script_path(), "Icons", TOOLBOX_ICON)
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        else:
            print(f"警告：图标文件 '{icon_path}' 不存在。")

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.new_shelf_toggle = QtWidgets.QCheckBox("创建新工具架")
        self.new_shelf_toggle.setChecked(False)  # 默认不选中
        self.install_button = RoundedButton("安装 " + TOOLBOX_NAME)
        self.uninstall_button = RoundedButton("卸载 " + TOOLBOX_NAME)

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 2, 10, 5)
        main_layout.setSpacing(5)
        
        toggle_layout = QtWidgets.QHBoxLayout()
        toggle_layout.setSpacing(5)

        # 创建开关按钮
        self.toggle_button = QtWidgets.QPushButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)  # 默认不选中
        self.toggle_button.setFixedSize(20, 20)
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                background-image: url(:/UVTkVerticalToggleOn.png);
                background-repeat: no-repeat;
                background-position: center;
                background-size: contain;
            }
            QPushButton:checked {
                background-image: url(:/UVTkVerticalToggleOff.png);
            }
            """
        )
        
        label = QtWidgets.QLabel("创建新工具架")
        label.setStyleSheet("font-size: 11px; padding: 0px; margin: 0px;")
        
        toggle_layout.addWidget(self.toggle_button)
        toggle_layout.addWidget(label)
        toggle_layout.addStretch()
        
        main_layout.addLayout(toggle_layout)
        main_layout.addWidget(self.install_button)
        main_layout.addWidget(self.uninstall_button)

        self.install_button.setFixedHeight(30)
        self.uninstall_button.setFixedHeight(30)

    def create_connections(self):
        self.install_button.clicked.connect(self.install)
        self.uninstall_button.clicked.connect(self.uninstall)
        # 移除这行，因为QDialog没有helpRequested信号
        # self.helpRequested.connect(self.open_help_url)

    def event(self, event):
        if event.type() == QtCore.QEvent.EnterWhatsThisMode:
            QtWidgets.QWhatsThis.leaveWhatsThisMode()
            self.open_help_url()
            return True
        return QtWidgets.QDialog.event(self, event)

    def open_help_url(self):
        webbrowser.open(TOOLBOX_HELP_URL)
        QtWidgets.QApplication.restoreOverrideCursor()  # 恢复正常的鼠标光标

    def closeEvent(self, event):
        # 直接调用父类的closeEvent
        super(InstallDialog, self).closeEvent(event)

    # 添加一个新方法来处理帮助请求
    def helpEvent(self, event):
        self.open_help_url()
        event.accept()

    def create_styled_message_box(self, title, text):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        # 设置按钮样式
        button_style = """
        QPushButton {
            background-color: #B0B0B0;
            color: #303030;
            border-radius: 10px;
            padding: 5px;
            font-weight: bold;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #C0C0C0;
        }
        QPushButton:pressed {
            background-color: #A0A0A0;
        }
        """
        
        for button in msg_box.buttons():
            button.setStyleSheet(button_style)
        
        return msg_box

    def install(self):
        new_shelf = self.toggle_button.isChecked()
        msg_box = self.create_styled_message_box(
            "确认安装",
            f"确定要安装 {TOOLBOX_NAME} 吗？" + ("（将创建新工具架）" if new_shelf else "（将添加到当前工具架）")
        )
        result = msg_box.exec_()
        
        if result == QtWidgets.QMessageBox.Yes:
            self.close()
            install_toolbox(new_shelf)

    def uninstall(self):
        msg_box = self.create_styled_message_box(
            "确认卸载",
            f"确定要卸载 {TOOLBOX_NAME} 吗？"
        )
        result = msg_box.exec_()
        
        if result == QtWidgets.QMessageBox.Yes:
            self.close()
            uninstall_toolbox()

def get_script_path():
    # 使用 MEL 命令获取脚本路径
    mel_command = f'whatIs "{TOOLBOX_NAME}"'
    result = mel.eval(mel_command)
    if result.startswith("Mel procedure found in: "):
        return os.path.dirname(result.split(": ", 1)[1])
    
    # 如果 MEL 方法失败，尝试通过 Python 路径查找
    for path in sys.path:
        possible_path = os.path.join(path, "install.py")
        if os.path.exists(possible_path):
            return os.path.dirname(possible_path)
    
    # 如果都失败，返回当前工作目录
    return os.getcwd()

def create_mod_file():
    current_path = get_script_path()
    maya_app_dir = cmds.internalVar(userAppDir=True)
    modules_dir = os.path.join(maya_app_dir, "modules")
    
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
    
    mod_content = f"""+ {TOOLBOX_NAME} {TOOLBOX_VERSION} {current_path}
scripts: {os.path.join(current_path, "Scripts")}
"""
    
    mod_file_path = os.path.join(modules_dir, f"{TOOLBOX_NAME}.mod")
    
    # 检查是否已存在相同内容的 mod 文件
    if os.path.exists(mod_file_path):
        with open(mod_file_path, 'r') as f:
            existing_content = f.read()
        if existing_content.strip() == mod_content.strip():
            print(f"已存在正确的 {TOOLBOX_NAME}.mod 文件，无需更新")
            return
    
    # 创建或更新 mod 文件
    with open(mod_file_path, "w") as f:
        f.write(mod_content)
    print(f"已创建/更新 {TOOLBOX_NAME}.mod 文")

def clean_existing_buttons():
    if cmds.shelfLayout(TOOLBOX_NAME, exists=True):
        buttons = cmds.shelfLayout(TOOLBOX_NAME, query=True, childArray=True) or []
        for btn in buttons:
            if cmds.shelfButton(btn, query=True, exists=True):
                label = cmds.shelfButton(btn, query=True, label=True)
                if label == TOOLBOX_NAME:
                    cmds.deleteUI(btn)
                    print(f"已删除现有的 {TOOLBOX_NAME} 按钮: {btn}")

def install_toolbox(new_shelf=True):
    current_path = get_script_path()
    scripts_path = os.path.join(current_path, "Scripts")
    
    create_mod_file()
    
    if not os.path.exists(scripts_path):
        os.makedirs(scripts_path)
    
    main_script = os.path.join(scripts_path, f"{TOOLBOX_NAME}_main.py")
    if not os.path.exists(main_script):
        cmds.error(f"错误：{TOOLBOX_NAME}_main.py 文件不存在于 {main_script}")
        return
    
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    
    shelf_layout = mel.eval('$tmpVar=$gShelfTopLevel')
    
    if new_shelf:
        if not cmds.shelfLayout(TOOLBOX_NAME, exists=True):
            cmds.shelfLayout(TOOLBOX_NAME, parent=shelf_layout)
        parent = TOOLBOX_NAME
    else:
        current_shelf = cmds.tabLayout(shelf_layout, query=True, selectTab=True)
        parent = current_shelf
    
    clean_existing_buttons()
    
    # 更新图标路径
    icon_path = os.path.join(current_path, "Icons", TOOLBOX_ICON)
    if not os.path.exists(icon_path):
        print(f"警告：自定义图标文件 '{icon_path}' 不存在，将使用默认图标。")
        icon_path = "commandButton.png"
    else:
        print(f"使用自定义图标: {icon_path}")
    
    command = f"""
import sys
import os
import importlib

current_path = r'{current_path}'
scripts_path = os.path.join(current_path, 'Scripts')
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)
os.chdir(scripts_path)

try:
    import {TOOLBOX_NAME}_main
    importlib.reload({TOOLBOX_NAME}_main)
    {TOOLBOX_NAME}_main.show()
except ImportError as e:
    print("Error importing {TOOLBOX_NAME}:", str(e))
    print("Current path:", current_path)
    print("Scripts path:", scripts_path)
    print("sys.path:", sys.path)
    print("Contents of Scripts folder:", os.listdir(scripts_path))
"""
    
    cmds.shelfButton(
        parent=parent,
        image1=icon_path,
        label=TOOLBOX_NAME,
        command=command,
        sourceType="python",
        annotation=f"{TOOLBOX_NAME} v{TOOLBOX_VERSION}",
        noDefaultPopup=True,
        style="iconOnly"
    )
    
    # 创建安装成功的消息框
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle("安装成功")
    msg_box.setText(f"{TOOLBOX_NAME} 已成功安装！")
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    
    
    # 设置按钮样式
    button_style = """
    QPushButton {
        background-color: #B0B0B0;
        color: #303030;
        border-radius: 10px;
        padding: 5px;
        font-weight: bold;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: #C0C0C0;
    }
    QPushButton:pressed {
        background-color: #A0A0A0;
    }
    """
    
    for button in msg_box.buttons():
        button.setStyleSheet(button_style)
    
    msg_box.exec_()
    
    # 验证安装
    try:
        import_module = __import__(TOOLBOX_MAIN_MODULE)
        print(f"{TOOLBOX_NAME} 模块导入成功")
    except ImportError as e:
        print(f"无法导入 {TOOLBOX_NAME} 模块: {e}")
        print("sys.path:", sys.path)
        print("Scripts 文件夹内容:", os.listdir(scripts_path))

def uninstall_toolbox():
    maya_app_dir = cmds.internalVar(userAppDir=True)
    mod_file_path = os.path.join(maya_app_dir, "modules", f"{TOOLBOX_NAME}.mod")
    
    if os.path.exists(mod_file_path):
        os.remove(mod_file_path)
        print(f"已删除 {TOOLBOX_NAME}.mod 件")
    
    if cmds.shelfLayout(TOOLBOX_NAME, exists=True):
        cmds.deleteUI(TOOLBOX_NAME, layout=True)
        print(f"删除 {TOOLBOX_NAME} 工具架")
    
    # 检查所有工具架，删除任何 HUGTools 按钮
    all_shelves = cmds.shelfTabLayout("ShelfLayout", query=True, childArray=True)
    for shelf in all_shelves:
        shelf_buttons = cmds.shelfLayout(shelf, query=True, childArray=True) or []
        for btn in shelf_buttons:
            if cmds.shelfButton(btn, query=True, exists=True):
                label = cmds.shelfButton(btn, query=True, label=True)
                if label == TOOLBOX_NAME:
                    cmds.deleteUI(btn)
                    print(f"已删除 {TOOLBOX_NAME} 按钮: {btn}")
    
    # 从 sys.path 中移除 Scripts 路径
    current_path = get_script_path()
    scripts_path = os.path.join(current_path, "Scripts")
    if scripts_path in sys.path:
        sys.path.remove(scripts_path)
        print(f"已从 sys.path 中移除 {scripts_path}")
    
    # 创建卸载成功的消息框
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle("卸载成功")
    msg_box.setText(f"{TOOLBOX_NAME} 已成功卸载！")
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    
    # 设置按钮样式
    button_style = """
    QPushButton {
        background-color: #B0B0B0;
        color: #303030;
        border-radius: 10px;
        padding: 5px;
        font-weight: bold;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: #C0C0C0;
    }
    QPushButton:pressed {
        background-color: #A0A0A0;
    }
    """
    
    for button in msg_box.buttons():
        button.setStyleSheet(button_style)
    
    msg_box.exec_()

if __name__ == "__main__":
    try:
        install_dialog.close()
        install_dialog.deleteLater()
    except:
        pass
    install_dialog = InstallDialog()
    install_dialog.show()

