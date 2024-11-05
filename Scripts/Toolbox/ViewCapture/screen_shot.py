from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import os
import sys
import subprocess

class ModItButton(QtWidgets.QPushButton):
    def __init__(self, text="", icon=None, parent=None):
        super(ModItButton, self).__init__(text, parent)
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

class ScreenCaptureUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ScreenCaptureUI, self).__init__(parent)
        self.setWindowTitle("Screen Capture")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        
        # 定义分辨率预设
        self.resolution_presets = {
            "1x (1920x1080)": (1920, 1080),
            "2x (3840x2160)": (3840, 2160),
            "3x (5760x3240)": (5760, 3240)
        }
        
        self.setup_ui()
        
        # 设置窗口样式
        self.setStyleSheet("""
            QDialog {
                background-color: #444444;
            }
            QLabel {
                color: #CCCCCC;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #555555;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox {
                background-color: #555555;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(:/arrowDown.png);
                width: 12px;
                height: 12px;
            }
        """)
        
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Path row
        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(QtWidgets.QLabel("Path"))
        self.path_field = QtWidgets.QLineEdit()
        path_layout.addWidget(self.path_field)
        browse_btn = ModItButton("Browse", icon=QtGui.QIcon(":fileOpen.png"))
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_btn)
        
        # Name row
        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(QtWidgets.QLabel("Name"))
        self.name_field = QtWidgets.QLineEdit()
        name_layout.addWidget(self.name_field)
        reload_btn = ModItButton("Reload", icon=QtGui.QIcon(":refresh.png"))
        reload_btn.clicked.connect(self.reload_path)
        name_layout.addWidget(reload_btn)
        
        # Resolution row
        res_layout = QtWidgets.QHBoxLayout()
        res_layout.addWidget(QtWidgets.QLabel("Resolution"))
        self.resolution_combo = QtWidgets.QComboBox()
        self.resolution_combo.addItems(self.resolution_presets.keys())
        res_layout.addWidget(self.resolution_combo)
        
        # Capture and Open Folder buttons layout
        button_layout = QtWidgets.QHBoxLayout()
        
        # Capture button
        capture_btn = ModItButton("Capture", icon=QtGui.QIcon(":snapshot.png"))
        capture_btn.clicked.connect(self.capture)
        capture_btn.setMinimumHeight(40)
        capture_btn.setMinimumWidth(200)
        button_layout.addWidget(capture_btn, stretch=6)
        
        # Open Folder button
        open_folder_btn = ModItButton("Open Folder", icon=QtGui.QIcon(":folder-open.png"))
        open_folder_btn.clicked.connect(self.open_folder)
        open_folder_btn.setMinimumHeight(40)
        open_folder_btn.setMinimumWidth(80)
        open_folder_btn.setMaximumWidth(120)
        button_layout.addWidget(open_folder_btn, stretch=4)
        
        # Add all layouts
        layout.addLayout(path_layout)
        layout.addLayout(name_layout)
        layout.addLayout(res_layout)
        layout.addLayout(button_layout)
        
        # 初始化默认路径
        self.reload_path()
        
    def browse_path(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory")
        if directory:
            self.path_field.setText(directory)
            
    def reload_path(self):
        workspace = cmds.workspace(q=True, dir=True)
        self.path_field.setText(workspace)
        
        selection = cmds.ls(sl=True)
        if selection:
            self.name_field.setText(selection[0])
            
    def capture(self):
        path = self.path_field.text()
        name = self.name_field.text()
        
        if not path:
            cmds.warning("Please set a valid path")
            return
            
        # 获取选择的分辨率
        resolution_key = self.resolution_combo.currentText()
        width, height = self.resolution_presets[resolution_key]
        
        # 构建文件名（添加分辨率信息）
        resolution_suffix = resolution_key.split()[0]  # 获取"1x"/"2x"/"3x"部分
        file_path = os.path.join(path, f"{name}_{resolution_suffix}.jpg")
        
        try:
            # 设置图像格式为JPG
            cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
            
            # 执行截图
            cmds.playblast(
                st=1,
                et=1,
                v=0,
                fmt="image",
                qlt=100,
                p=100,
                w=width,
                h=height,
                fp=0,
                cf=file_path
            )
            
            # 使用inViewMessage显示消息
            message = f'<span style="color:#FFA500;">Screenshot saved:<br>{file_path}<br>Resolution: {width}x{height}</span>'
            cmds.inViewMessage(amg=message, pos='botRight', fade=True, fst=200, fad=100)
            
            # 同时打印信息到脚本编辑器
            print("\n=== Screenshot Information ===")
            print(f"File saved: {file_path}")
            print(f"Resolution: {width}x{height}")
            print(f"Format: JPG")
            
        except Exception as e:
            cmds.warning(f"Error capturing screenshot: {str(e)}")

    def open_folder(self):
        """打开导出文件夹"""
        path = self.path_field.text()
        if not path:
            cmds.warning("Please set a valid path")
            return
            
        if not os.path.exists(path):
            cmds.warning("Path does not exist")
            return
            
        # 根据操作系统打开文件夹
        if os.name == 'nt':  # Windows
            os.startfile(path)
        elif os.name == 'posix':  # macOS 和 Linux
            if sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', path])
            else:  # Linux
                subprocess.Popen(['xdg-open', path])

_screen_capture_dialog = None





#====== UI Functions ======

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def show():
    """
    Display UI for the editor rename module
    
    Functions:
    - Close and delete existing UI instance (if exists)
    - Create new UI instance and display
    """
    global creen_capture_ui
    try:
        creen_capture_ui.close()
        creen_capture_ui.deleteLater()
    except:
        pass
    parent = maya_main_window()
    creen_capture_ui = ScreenCaptureUI(parent)
    creen_capture_ui.show()
    creen_capture_ui.raise_()
    creen_capture_ui.activateWindow()


if __name__ == "__main__":
    show()
