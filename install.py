# -*- coding: utf-8 -*-
# Import necessary modules
import os
import sys
import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets, QtGui, QtCore
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import webbrowser
import importlib
import locale

# Define constants for the toolbox
TOOLBOX_NAME = "HUGTools"
TOOLBOX_VERSION = "1.1.2 Beta"  # Update this to match HUGTOOL_VERSION in HUGTools_main.py
TOOLBOX_ICON = "MainUI.png"
TOOLBOX_MAIN_MODULE = "HUGTools_main"
TOOLBOX_HELP_URL = "https://megestus.github.io/HUGTools/"  

# Define button style
BUTTON_STYLE = """
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

# Dictionary for language translations
LANG = {
    'en_US': {
        # English translations
        'install': "Install",
        'uninstall': "Uninstall",
        'create_new_shelf': "Whether to Create new shelf",
        'confirm_install': "Confirm Installation",
        'confirm_install_msg': "Are you sure you want to install {}?",
        'new_shelf_msg': "(A new shelf will be created)",
        'current_shelf_msg': "(Will be added to the current shelf)",
        'confirm_uninstall': "Confirm Uninstallation",
        'confirm_uninstall_msg': "Are you sure you want to uninstall {}?",
        'install_success': "Installation Successful",
        'install_success_msg': "{} has been successfully installed!",
        'uninstall_success': "Uninstallation Successful",
        'uninstall_success_msg': "{} has been successfully uninstalled!",
        'reinstall': "Reinstall",
        'confirm_reinstall': "Confirm Reinstallation",
        'confirm_reinstall_msg': "Are you sure you want to reinstall {}? This will uninstall the current version first.",
        'reinstall_success': "Reinstallation Successful",
        'reinstall_success_msg': "{} has been successfully reinstalled!"
    },
    'zh_CN': {
        # Chinese translations
        'install': "安装",
        'uninstall': "卸载",
        'create_new_shelf': "是否创建新工具架",
        'confirm_install': "确认安装",
        'confirm_install_msg': "您确定要安装 {} 吗？",
        'new_shelf_msg': "（将创建新工具架）",
        'current_shelf_msg': "（将添加到当前工具架）",
        'confirm_uninstall': "确认卸载",
        'confirm_uninstall_msg': "您确定要卸载 {} 吗？",
        'install_success': "安装成功",
        'install_success_msg': "{} 已成功安装！",
        'uninstall_success': "卸载成功",
        'uninstall_success_msg': "{} 已成功卸载！",
        'reinstall': "重新安装",
        'confirm_reinstall': "确认重新安装",
        'confirm_reinstall_msg': "您确定要重新安装 {} 吗？这将先卸载当前版本。",
        'reinstall_success': "重新安装成功",
        'reinstall_success_msg': "{} 已成功重新安装！"
    }
}

# Choose the current language
CURRENT_LANG = choose_language()

# Function to get Maya's main window
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

# Custom button class with rounded corners
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

# Main installation dialog class
class InstallDialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(InstallDialog, self).__init__(parent)
        self.setWindowTitle(f"{TOOLBOX_NAME} {LANG[CURRENT_LANG]['install']}")
        self.setFixedSize(220, 150)  # window size  
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowContextHelpButtonHint)

        # Set window icon
        icon_path = os.path.join(get_script_path(), "Icons", TOOLBOX_ICON)
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        else:
            print(f"Warning: Icon file '{icon_path}' does not exist.")

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    # Create UI widgets
    def create_widgets(self):
        self.new_shelf_toggle = QtWidgets.QCheckBox(LANG[CURRENT_LANG]['create_new_shelf'])
        self.new_shelf_toggle.setChecked(False)
        self.install_button = RoundedButton(LANG[CURRENT_LANG]['install'] + " " + TOOLBOX_NAME)
        self.uninstall_button = RoundedButton(LANG[CURRENT_LANG]['uninstall'] + " " + TOOLBOX_NAME)
        self.reinstall_button = RoundedButton(LANG[CURRENT_LANG]['reinstall'] + " " + TOOLBOX_NAME)  

    # Create UI layouts
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 2, 10, 1)
        main_layout.setSpacing(8)
        
        toggle_layout = QtWidgets.QHBoxLayout()
        toggle_layout.setContentsMargins(2, 4, 10, 1)
        toggle_layout.setSpacing(5)

        self.toggle_button = QtWidgets.QPushButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
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
        
        label = QtWidgets.QLabel(LANG[CURRENT_LANG]['create_new_shelf'])
        label.setStyleSheet("font-size: 11px; padding: 0px; margin: 0px;")
        
        toggle_layout.addWidget(self.toggle_button)
        toggle_layout.addWidget(label)
        toggle_layout.addStretch()
        
        main_layout.addLayout(toggle_layout)
        main_layout.addWidget(self.install_button)
        main_layout.addWidget(self.reinstall_button)  
        main_layout.addWidget(self.uninstall_button)

        self.install_button.setFixedHeight(30)
        self.reinstall_button.setFixedHeight(30)
        self.uninstall_button.setFixedHeight(30)

        # Add some elastic space
        main_layout.addStretch(1)

    # Connect UI elements to their respective functions
    def create_connections(self):
        self.install_button.clicked.connect(self.install)
        self.uninstall_button.clicked.connect(self.uninstall)
        self.reinstall_button.clicked.connect(self.reinstall)

    # Handle WhatsThis events
    def event(self, event):
        if event.type() == QtCore.QEvent.EnterWhatsThisMode:
            QtWidgets.QWhatsThis.leaveWhatsThisMode()
            self.open_help_url()
            return True
        return QtWidgets.QDialog.event(self, event)

    # Open help URL in web browser
    def open_help_url(self):
        webbrowser.open(TOOLBOX_HELP_URL)
        QtWidgets.QApplication.restoreOverrideCursor()

    # Handle close event
    def closeEvent(self, event):
        super(InstallDialog, self).closeEvent(event)

    # Handle help event
    def helpEvent(self, event):
        self.open_help_url()
        event.accept()

    # Create a styled message box
    def create_styled_message_box(self, title, text):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
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

    # Handle install button click
    def install(self):
        new_shelf = self.toggle_button.isChecked()
        msg_box = self.create_styled_message_box(
            LANG[CURRENT_LANG]['confirm_install'],
            LANG[CURRENT_LANG]['confirm_install_msg'].format(TOOLBOX_NAME) + 
            (LANG[CURRENT_LANG]['new_shelf_msg'] if new_shelf else LANG[CURRENT_LANG]['current_shelf_msg'])
        )
        result = msg_box.exec_()
        
        if result == QtWidgets.QMessageBox.Yes:
            self.close()
            install_toolbox(new_shelf)

    # Handle uninstall button click
    def uninstall(self):
        msg_box = self.create_styled_message_box(
            LANG[CURRENT_LANG]['confirm_uninstall'],
            LANG[CURRENT_LANG]['confirm_uninstall_msg'].format(TOOLBOX_NAME)
        )
        result = msg_box.exec_()
        
        if result == QtWidgets.QMessageBox.Yes:
            self.close()
            uninstall_toolbox()

    # Handle reinstall button click
    def reinstall(self):
        msg_box = self.create_styled_message_box(
            LANG[CURRENT_LANG]['confirm_reinstall'],
            LANG[CURRENT_LANG]['confirm_reinstall_msg'].format(TOOLBOX_NAME)
        )
        result = msg_box.exec_()
        
        if result == QtWidgets.QMessageBox.Yes:
            self.close()
            uninstall_toolbox(show_message=False)
            install_toolbox(self.new_shelf_toggle.isChecked(), show_message=False)
            
            # Show only one reinstallation success message
            success_msg_box = QtWidgets.QMessageBox()
            success_msg_box.setWindowTitle(LANG[CURRENT_LANG]['reinstall_success'])
            success_msg_box.setText(LANG[CURRENT_LANG]['reinstall_success_msg'].format(TOOLBOX_NAME))
            success_msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            
            for button in success_msg_box.buttons():
                button.setStyleSheet(BUTTON_STYLE)
            
            success_msg_box.exec_()

# Get the script path
def get_script_path():
    mel_command = f'whatIs "{TOOLBOX_NAME}"'
    result = mel.eval(mel_command)
    if result.startswith("Mel procedure found in: "):
        return os.path.dirname(result.split(": ", 1)[1])
    
    for path in sys.path:
        possible_path = os.path.join(path, "install.py")
        if os.path.exists(possible_path):
            return os.path.dirname(possible_path)
    
    return os.getcwd()

# Create or update the .mod file
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
    
    if os.path.exists(mod_file_path):
        with open(mod_file_path, 'r') as f:
            existing_content = f.read()
        if existing_content.strip() == mod_content.strip():
            print(f"Correct {TOOLBOX_NAME}.mod file already exists, no update needed")
            return
    
    with open(mod_file_path, "w") as f:
        f.write(mod_content)
    print(f"{TOOLBOX_NAME}.mod file created/updated")

# Clean existing buttons from shelves
def clean_existing_buttons():
    if cmds.shelfLayout(TOOLBOX_NAME, exists=True):
        buttons = cmds.shelfLayout(TOOLBOX_NAME, query=True, childArray=True) or []
        for btn in buttons:
            if cmds.shelfButton(btn, query=True, exists=True):
                label = cmds.shelfButton(btn, query=True, label=True)
                if label == TOOLBOX_NAME:
                    cmds.deleteUI(btn)
                    print(f"Deleted existing {TOOLBOX_NAME} button: {btn}")

# Install the toolbox
def install_toolbox(new_shelf=True, show_message=True):
    current_path = get_script_path()
    scripts_path = os.path.join(current_path, "Scripts")
    
    create_mod_file()
    
    if not os.path.exists(scripts_path):
        os.makedirs(scripts_path)
    
    main_script = os.path.join(scripts_path, f"{TOOLBOX_NAME}_main.py")
    if not os.path.exists(main_script):
        cmds.error(f"Error: {TOOLBOX_NAME}_main.py file does not exist at {main_script}")
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
    
    icon_path = os.path.join(current_path, "Icons", TOOLBOX_ICON)
    if not os.path.exists(icon_path):
        print(f"Warning: Custom icon file '{icon_path}' does not exist, using default icon.")
        icon_path = "commandButton.png"
    else:
        print(f"Using custom icon: {icon_path}")
    
    # Command to be executed when the shelf button is clicked
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
    
    # Create the shelf button
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
    
    if show_message:
        # Show installation success message
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(LANG[CURRENT_LANG]['install_success'])
        msg_box.setText(LANG[CURRENT_LANG]['install_success_msg'].format(TOOLBOX_NAME))
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        
        for button in msg_box.buttons():
            button.setStyleSheet(BUTTON_STYLE)
        
        msg_box.exec_()
    
    # Verify installation
    try:
        import_module = __import__(TOOLBOX_MAIN_MODULE)
        print(f"{TOOLBOX_NAME} module imported successfully")
    except ImportError as e:
        print(f"Unable to import {TOOLBOX_NAME} module: {e}")
        print("sys.path:", sys.path)
        print("Scripts folder contents:", os.listdir(scripts_path))

# Uninstall the toolbox
def uninstall_toolbox(show_message=True):
    maya_app_dir = cmds.internalVar(userAppDir=True)
    mod_file_path = os.path.join(maya_app_dir, "modules", f"{TOOLBOX_NAME}.mod")
    
    if os.path.exists(mod_file_path):
        os.remove(mod_file_path)
        print(f"{TOOLBOX_NAME}.mod file removed")
    
    if cmds.shelfLayout(TOOLBOX_NAME, exists=True):
        cmds.deleteUI(TOOLBOX_NAME, layout=True)
        print(f"{TOOLBOX_NAME} shelf removed")
    
    all_shelves = cmds.shelfTabLayout("ShelfLayout", query=True, childArray=True)
    for shelf in all_shelves:
        shelf_buttons = cmds.shelfLayout(shelf, query=True, childArray=True) or []
        for btn in shelf_buttons:
            if cmds.shelfButton(btn, query=True, exists=True):
                label = cmds.shelfButton(btn, query=True, label=True)
                if label == TOOLBOX_NAME:
                    cmds.deleteUI(btn)
                    print(f"{TOOLBOX_NAME} button removed: {btn}")
    
    current_path = get_script_path()
    scripts_path = os.path.join(current_path, "Scripts")
    if scripts_path in sys.path:
        sys.path.remove(scripts_path)
        print(f"{scripts_path} removed from sys.path")
    
    if show_message:
        # Show uninstallation success message
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(LANG[CURRENT_LANG]['uninstall_success'])
        msg_box.setText(LANG[CURRENT_LANG]['uninstall_success_msg'].format(TOOLBOX_NAME))
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        
        for button in msg_box.buttons():
            button.setStyleSheet(BUTTON_STYLE)
        
        msg_box.exec_()

class MayaVerObj:
    def __init__(self):
        self.num = None 
        self.extnum = 0

def get_maya_version():
    verstring = cmds.about(v=True)
    
    splited = verstring.split()
    num = None 
    extnum = 0
    
    for r in splited:
        if r.startswith("20"):
            num = int(r)
            break
    
    for i, r in enumerate(splited):
        if r.lower() in ["extension", "ext"]:
            for j in range(i+1, len(splited)):
                if splited[j].isdigit():
                    extnum = int(splited[j])
                    break
            break
    
    if not num:
        raise Exception("Can't get Maya version")
    
    mayavobj = MayaVerObj()
    mayavobj.num = num 
    mayavobj.extnum = extnum 
    return mayavobj

def check_maya_version():
    maya_ver = get_maya_version()
    return maya_ver.num >= 2022

def read_file_with_fallback(file_path, encodings=['utf-8', 'gbk', 'cp437', 'iso-8859-1']):
    for encoding in encodings:
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                return content.decode(encoding)
        except UnicodeDecodeError:
            print(f'Failed to decode with {encoding}')
            continue
        except Exception as e:
            print(f'Error reading file with {encoding}: {str(e)}')
            continue
    raise UnicodeDecodeError('Unable to decode the file with the given encodings')

# Main execution
if __name__ == "__main__":
    maya_ver = get_maya_version()
    if check_maya_version():
        try:
            install_dialog.close()
            install_dialog.deleteLater()
        except:
            pass
        install_dialog = InstallDialog()
        install_dialog.show()
    else:
        # Show error message for unsupported Maya version
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.setWindowTitle("Unsupported Maya Version")
        msg_box.setText(f"{TOOLBOX_NAME} requires Maya 2022 or later. Your version: {maya_ver.num}.{maya_ver.extnum}")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec_()

