from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds
import os

class ScreenCaptureUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ScreenCaptureUI, self).__init__(parent)
        self.setWindowTitle("Screen Capture")
        self.setMinimumWidth(400)
        
        # 定义分辨率预设
        self.resolution_presets = {
            "1x (1920x1080)": (1920, 1080),
            "2x (3840x2160)": (3840, 2160),
            "3x (5760x3240)": (5760, 3240)
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QtWidgets.QGridLayout(self)
        
        # Path row
        layout.addWidget(QtWidgets.QLabel("Path"), 0, 0)
        self.path_field = QtWidgets.QLineEdit()
        layout.addWidget(self.path_field, 0, 1)
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_path)
        layout.addWidget(browse_btn, 0, 2)
        
        # Name row
        layout.addWidget(QtWidgets.QLabel("Name"), 1, 0)
        self.name_field = QtWidgets.QLineEdit()
        layout.addWidget(self.name_field, 1, 1)
        reload_btn = QtWidgets.QPushButton("Reload")
        reload_btn.clicked.connect(self.reload_path)
        layout.addWidget(reload_btn, 1, 2)
        
        # Resolution row
        layout.addWidget(QtWidgets.QLabel("Resolution"), 2, 0)
        self.resolution_combo = QtWidgets.QComboBox()
        self.resolution_combo.addItems(self.resolution_presets.keys())
        layout.addWidget(self.resolution_combo, 2, 1)
        
        # Capture buttons row
        buttons_layout = QtWidgets.QHBoxLayout()
        capture_btn = QtWidgets.QPushButton("Capture")
        capture_btn.clicked.connect(self.capture)
        capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #4B4B4B;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
        """)
        buttons_layout.addWidget(capture_btn)
        
        layout.addLayout(buttons_layout, 3, 0, 1, 3)
        
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
            
            cmds.confirmDialog(
                title="Success",
                message=f"Screenshot saved to:\n{file_path}\nResolution: {width}x{height}",
                button=["OK"]
            )
            
        except Exception as e:
            cmds.warning(f"Error capturing screenshot: {str(e)}")

_screen_capture_dialog = None

def show():
    global _screen_capture_dialog
    
    if _screen_capture_dialog:
        try:
            _screen_capture_dialog.close()
            _screen_capture_dialog.deleteLater()
        except:
            pass
            
    parent = QtWidgets.QApplication.activeWindow()
    _screen_capture_dialog = ScreenCaptureUI(parent=parent)
    _screen_capture_dialog.show()
    return _screen_capture_dialog 