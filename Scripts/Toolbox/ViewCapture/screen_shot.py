import os
import sys
import json
import subprocess
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

#====== UI Button Components ======
class ModItButton(QtWidgets.QPushButton):
    def __init__(self, text="", icon=None, parent=None):
        super(ModItButton, self).__init__(text, parent)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(20, 20))
        
        # 设置统一的按钮大小
        self.setMinimumHeight(30)
        self.setMinimumWidth(80)
        
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #D0D0D0;
                color: #303030;
                border-radius: 3px;
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

#====== UI Main Window Component ======
class ScreenCaptureUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ScreenCaptureUI, self).__init__(parent)
        self.setWindowTitle("Screen Capture")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        
        # 初始化设置
        self._initialize_settings()
        # 设置UI
        self.setup_ui()
        # 应用样式
        self._apply_stylesheet()

    #====== UI Components ======
    def _initialize_settings(self):
        """初始化设置和路径"""
        self.DIR = os.path.dirname(__file__)
        self.SETTING_PATH = os.path.join(self.DIR, "json", "screen_shot_setting.json")
        
        # 确保json目录存在
        json_dir = os.path.join(self.DIR, "json")
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        
        self.setting_data = {}
        self.resolution_presets = {
            "1x (1920x1080)": (1920, 1080),
            "2x (3840x2160)": (3840, 2160),
            "3x (5760x3240)": (5760, 3240)
        }

    def _apply_stylesheet(self):
        """应用UI样式"""
        self.setStyleSheet("""
            QDialog { background-color: #444444; }
            QLabel { color: #CCCCCC; font-weight: bold; }
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
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow {
                image: url(:/arrowDown.png);
                width: 12px;
                height: 12px;
            }
        """)

    #====== UI Layout ======
    def setup_ui(self):
        """设置UI布局"""
        self._setup_menu()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # 减小外边距
        layout.setSpacing(8)  # 减小组件间距
        
        layout.addLayout(self._create_camera_layout())
        layout.addLayout(self._create_path_layout())
        layout.addLayout(self._create_name_layout())
        layout.addLayout(self._create_resolution_layout())
        layout.addSpacing(3)  # 减小底部按钮前的额外间距
        layout.addLayout(self._create_button_layout())
        
        # 连接信号
        self._connect_signals()
        
        self.reload_path()
        if os.path.exists(self.SETTING_PATH):
            self.import_settings(self.SETTING_PATH)

    def _setup_menu(self):
        """设置菜单栏"""
        pass  # 不再需要菜单栏

    def _create_path_layout(self):
        """创建路径行布局"""
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(5)
        
        # 标签行
        label = QtWidgets.QLabel("Export Path")
        label.setStyleSheet("color: #CCCCCC; font-weight: bold; font-size: 12px;")
        layout.addWidget(label)
        
        # 输入行
        input_layout = QtWidgets.QHBoxLayout()
        self.path_field = QtWidgets.QLineEdit()
        self.path_field.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #666666;
            }
            QLineEdit:focus {
                border: 1px solid #666666;
            }
        """)
        input_layout.addWidget(self.path_field)
        
        self.browse_btn = ModItButton("Browse", icon=QtGui.QIcon(":fileOpen.png"))
        input_layout.addWidget(self.browse_btn)
        layout.addLayout(input_layout)
        
        return layout

    def _create_name_layout(self):
        """创建名称行布局"""
        layout = QtWidgets.QHBoxLayout()
        
        # 添加文字标签
        label = QtWidgets.QLabel("File Name")
        label.setStyleSheet("color: #CCCCCC; font-weight: bold;")
        label.setMinimumWidth(80)  # 设置固定宽度确保对齐
        layout.addWidget(label)
        
        # 输入框
        self.name_field = QtWidgets.QLineEdit()
        self.name_field.setText("Screenshot")
        self.name_field.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #666666;
            }
            QLineEdit:focus {
                border: 1px solid #666666;
            }
        """)
        layout.addWidget(self.name_field)
        
        # 按钮
        self.reload_btn = ModItButton("Get object name", icon=QtGui.QIcon(":refresh.png"))
        layout.addWidget(self.reload_btn)
        
        return layout

    def _create_resolution_layout(self):
        """创建分辨率行布局"""
        layout = QtWidgets.QHBoxLayout()
        
        # 添加文字标签
        label = QtWidgets.QLabel("Resolution")
        label.setStyleSheet("color: #CCCCCC; font-weight: bold;")
        label.setMinimumWidth(80)  # 设置固定宽度确保对齐
        layout.addWidget(label)
        
        # 下拉框
        self.resolution_combo = QtWidgets.QComboBox()
        self.resolution_combo.addItems(self.resolution_presets.keys())
        self.resolution_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox:hover {
                border: 1px solid #666666;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(:/arrowDown.png);
                width: 12px;
                height: 12px;
            }
        """)
        layout.addWidget(self.resolution_combo)
        
        return layout

    def _create_button_layout(self):
        """创建按钮行布局"""
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(8)  # 减小按钮之间的间距
        
        self.capture_btn = ModItButton("Capture", icon=QtGui.QIcon(":snapshot.png"))
        self.open_folder_btn = ModItButton("Open Folder", icon=QtGui.QIcon(":folder-open.png"))
        
        layout.addWidget(self.capture_btn, stretch=6)
        layout.addWidget(self.open_folder_btn, stretch=4)
        
        return layout

    def _create_camera_layout(self):
        """创建相机预设切换滑条布局"""
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(5)
        
        # 创建滑条容器
        control_container = QtWidgets.QWidget()
        control_container.setStyleSheet("""
            QWidget {
                background-color: #333333;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        control_layout = QtWidgets.QHBoxLayout(control_container)
        control_layout.setContentsMargins(5, 2, 5, 2)
        
        # 创建滑条
        self.camera_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.camera_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #555555;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #D0D0D0;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #E0E0E0;
            }
        """)
        control_layout.addWidget(self.camera_slider, stretch=1)  # 添加拉伸因子
        
        # 添加预设名称标签
        self.camera_label = QtWidgets.QLabel()
        self.camera_label.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-weight: bold;
                padding: 2px;
                min-width: 100px;
            }
        """)
        self.camera_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        control_layout.addWidget(self.camera_label)
        
        # 添加设置按钮
        settings_btn = ModItButton("Settings", icon=QtGui.QIcon(":gear.png"))
        settings_btn.clicked.connect(self.open_camera_settings)
        control_layout.addWidget(settings_btn)
        
        layout.addWidget(control_container)
        
        # 更新相机预设列表并设置滑条范围
        self.update_camera_presets()
        
        # 连接滑条值变化信号
        self.camera_slider.valueChanged.connect(self.on_camera_preset_changed)
        
        return layout

    #====== UI and Function Connections ======
    def _connect_signals(self):
        """连接信号和槽"""
        self.browse_btn.clicked.connect(self.browse_path)
        self.reload_btn.clicked.connect(self.reload_path)
        self.capture_btn.clicked.connect(self.capture)
        self.open_folder_btn.clicked.connect(self.open_folder)

    #====== Functions ======
    def browse_path(self):
        """浏览文件夹路径"""
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.path_field.setText(directory)

    def reload_path(self):
        """重新加载路径和名称"""
        workspace = cmds.workspace(q=True, dir=True)
        self.path_field.setText(workspace)
        
        selection = cmds.ls(sl=True)
        if selection:
            self.name_field.setText(selection[0])
        else:
            self.name_field.setText("Screenshot")

    def get_next_available_filename(self, base_path, base_name="Screenshot"):
        """获取下一个可用的文件名"""
        index = 1
        while True:
            resolution_key = self.resolution_combo.currentText()
            resolution_suffix = resolution_key.split()[0]
            filename = f"{base_name}_{index:03d}_{resolution_suffix}.jpg"
            full_path = os.path.join(base_path, filename)
            
            if not os.path.exists(full_path):
                return full_path, filename
            index += 1

    def capture(self):
        """捕获截图"""
        path = self.path_field.text()
        name = self.name_field.text() or "Screenshot"
        
        if not path:
            cmds.warning("Please set a valid path")
            return
            
        resolution_key = self.resolution_combo.currentText()
        width, height = self.resolution_presets[resolution_key]
        file_path, filename = self.get_next_available_filename(path, name)
        
        try:
            cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
            cmds.playblast(
                st=1, et=1, v=0, fmt="image", qlt=100, p=100,
                w=width, h=height, fp=0, cf=file_path
            )
            
            message = f'<span style="color:#FFA500;">Screenshot saved:<br>{filename}<br>Resolution: {width}x{height}</span>'
            cmds.inViewMessage(amg=message, pos='botRight', fade=True, fst=200, fad=100)
            
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
            
        if os.name == 'nt':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])

    def open_camera_settings(self):
        """打开相机预设窗口"""
        try:
            self.camera_preset_window = CameraPresetWindow(self)
            self.camera_preset_window.show()
        except Exception as e:
            cmds.warning(f"Error opening camera settings: {str(e)}")

    def import_settings(self, path):
        """导入设置"""
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self.setting_data = json.load(f)
                    
                # 应用设置
                if "resolution" in self.setting_data:
                    index = self.resolution_combo.findText(self.setting_data["resolution"])
                    if index >= 0:
                        self.resolution_combo.setCurrentIndex(index)
                        
                if "path" in self.setting_data:
                    self.path_field.setText(self.setting_data["path"])
                    
        except Exception as e:
            cmds.warning(f"Failed to load settings: {str(e)}")

    def update_camera_presets(self):
        """更新相机预设列表"""
        # 获取所有保存的相机预设
        presets_file = os.path.join(os.path.dirname(__file__), "json", "camera_presets.json")
        self.camera_presets = []
        self.preset_names = []
        
        if os.path.exists(presets_file):
            try:
                with open(presets_file, 'r') as f:
                    presets = json.load(f)
                    self.camera_presets = list(presets.values())
                    self.preset_names = list(presets.keys())
            except Exception as e:
                cmds.warning(f"Failed to load camera presets: {str(e)}")
        
        # 设置滑条范围
        self.camera_slider.setMinimum(0)
        self.camera_slider.setMaximum(max(0, len(self.camera_presets) - 1))
        
        # 更新相机标签
        self.on_camera_preset_changed(self.camera_slider.value())

    def on_camera_preset_changed(self, value):
        """处理相机预设切换"""
        if 0 <= value < len(self.camera_presets):
            preset_data = self.camera_presets[value]
            preset_name = self.preset_names[value]
            
            # 更新标签显示
            self.camera_label.setText(preset_name)
            
            # 切换当前视图相机位置
            panel = cmds.getPanel(withFocus=True)
            if cmds.getPanel(typeOf=panel) == 'modelPanel':
                try:
                    camera = cmds.modelPanel(panel, query=True, camera=True)
                    # 设置相机位置和旋转
                    cmds.xform(camera, worldSpace=True, translation=preset_data["position"])
                    cmds.xform(camera, worldSpace=True, rotation=preset_data["rotation"])
                except Exception as e:
                    cmds.warning(f"Failed to switch camera preset: {str(e)}")

#====== UI Functions ======
def maya_main_window():
    """获取Maya主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def show():
    """显示UI"""
    global screen_capture_ui
    try:
        screen_capture_ui.close()
        screen_capture_ui.deleteLater()
    except:
        pass
    
    parent = maya_main_window()
    screen_capture_ui = ScreenCaptureUI(parent)
    screen_capture_ui.show()
    screen_capture_ui.raise_()
    screen_capture_ui.activateWindow()

# 在文件中添加新的相机预设窗口类
class CameraPresetWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CameraPresetWindow, self).__init__(parent)
        self.setWindowTitle("Camera Presets")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setMinimumWidth(300)
        self.setup_ui()
        self.load_presets()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # 减小外边距
        layout.setSpacing(8)  # 减小组件间距

        # 预设列表
        self.preset_list = QtWidgets.QListWidget()
        self.preset_list.setStyleSheet("""
            QListWidget {
                background-color: #555555;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #666666;
            }
            QListWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(self.preset_list)
        
        # 主要按钮布局
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(8)  # 减小按钮间距
        self.save_btn = ModItButton("Save Current", icon=QtGui.QIcon(":save.png"))
        self.delete_btn = ModItButton("Delete", icon=QtGui.QIcon(":delete.png"))
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_btn)
        layout.addLayout(button_layout)

        # 导入导出按钮布局
        io_button_layout = QtWidgets.QHBoxLayout()
        io_button_layout.setSpacing(8)  # 减小按钮间距
        self.export_btn = ModItButton("Export Presets", icon=QtGui.QIcon(":fileOpen.png"))
        self.import_btn = ModItButton("Import Presets", icon=QtGui.QIcon(":fileOpen.png"))
        
        io_button_layout.addWidget(self.export_btn)
        io_button_layout.addWidget(self.import_btn)
        layout.addLayout(io_button_layout)

        # 连接信号
        self.save_btn.clicked.connect(self.save_camera_preset)
        self.delete_btn.clicked.connect(self.delete_camera_preset)
        self.export_btn.clicked.connect(self.export_presets)
        self.import_btn.clicked.connect(self.import_presets)

    def save_camera_preset(self):
        """保存当前相机预设"""
        panel = cmds.getPanel(withFocus=True)
        if cmds.getPanel(typeOf=panel) != 'modelPanel':
            cmds.warning("Please select a viewport first")
            return

        camera = cmds.modelPanel(panel, query=True, camera=True)
        
        # 获取相机属性
        pos = cmds.xform(camera, query=True, worldSpace=True, translation=True)
        rot = cmds.xform(camera, query=True, worldSpace=True, rotation=True)
        
        # 修改默认预设名称格式
        name, ok = QtWidgets.QInputDialog.getText(
            self, 'Save Camera Preset', 'Enter preset name:',
            QtWidgets.QLineEdit.Normal, f"CameraPreset_{self.preset_list.count() + 1}")
        
        if ok and name:
            preset_data = {
                "position": pos,
                "rotation": rot,
                "camera": camera
            }
            
            # 保存到json文件
            presets_file = os.path.join(os.path.dirname(__file__), "json", "camera_presets.json")
            presets = {}
            if os.path.exists(presets_file):
                with open(presets_file, 'r') as f:
                    presets = json.load(f)
            
            presets[name] = preset_data
            
            with open(presets_file, 'w') as f:
                json.dump(presets, f, indent=4)
            
            self.load_presets()

    def load_camera_preset(self):
        """加载选中的相机预设"""
        current_item = self.preset_list.currentItem()
        if not current_item:
            cmds.warning("Please select a preset to load")
            return

        preset_name = current_item.text()
        presets_file = os.path.join(os.path.dirname(__file__), "json", "camera_presets.json")
        
        if os.path.exists(presets_file):
            with open(presets_file, 'r') as f:
                presets = json.load(f)
                
            if preset_name in presets:
                preset_data = presets[preset_name]
                panel = cmds.getPanel(withFocus=True)
                
                if cmds.getPanel(typeOf=panel) == 'modelPanel':
                    camera = cmds.modelPanel(panel, query=True, camera=True)
                    
                    # 设置相机位置和旋转
                    cmds.xform(camera, worldSpace=True, translation=preset_data["position"])
                    cmds.xform(camera, worldSpace=True, rotation=preset_data["rotation"])
                else:
                    cmds.warning("Please select a viewport first")

    def delete_camera_preset(self):
        """删除选中的相机预设"""
        current_item = self.preset_list.currentItem()
        if not current_item:
            cmds.warning("Please select a preset to delete")
            return

        preset_name = current_item.text()
        presets_file = os.path.join(os.path.dirname(__file__), "json", "camera_presets.json")
        
        if os.path.exists(presets_file):
            with open(presets_file, 'r') as f:
                presets = json.load(f)
            
            if preset_name in presets:
                del presets[preset_name]
                
                with open(presets_file, 'w') as f:
                    json.dump(presets, f, indent=4)
                
                self.load_presets()

    def load_presets(self):
        """加载所有相机预设到列表中"""
        self.preset_list.clear()
        presets_file = os.path.join(os.path.dirname(__file__), "json", "camera_presets.json")
        
        if os.path.exists(presets_file):
            with open(presets_file, 'r') as f:
                presets = json.load(f)
            
            for preset_name in presets:
                self.preset_list.addItem(preset_name)

    def export_presets(self):
        """导出相机预设到文件"""
        presets_file = os.path.join(os.path.dirname(__file__), "json", "camera_presets.json")
        if not os.path.exists(presets_file):
            cmds.warning("No presets to export")
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Camera Presets",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(presets_file, 'r') as source:
                    presets = json.load(source)
                    
                with open(file_path, 'w') as target:
                    json.dump(presets, target, indent=4)
                    
                cmds.inViewMessage(
                    amg='<span style="color:#98FB98;">Camera presets exported successfully</span>',
                    pos='topCenter',
                    fade=True,
                    fst=1000,
                    fet=250
                )
            except Exception as e:
                cmds.warning(f"Failed to export presets: {str(e)}")

    def import_presets(self):
        """从文件导入相机预设"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Import Camera Presets",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as source:
                    imported_presets = json.load(source)
                    
                presets_file = os.path.join(os.path.dirname(__file__), "json", "camera_presets.json")
                existing_presets = {}
                
                if os.path.exists(presets_file):
                    with open(presets_file, 'r') as target:
                        existing_presets = json.load(target)
                
                # 合并预设
                existing_presets.update(imported_presets)
                
                with open(presets_file, 'w') as target:
                    json.dump(existing_presets, target, indent=4)
                
                self.load_presets()  # 刷新预设列表
                
                cmds.inViewMessage(
                    amg='<span style="color:#98FB98;">Camera presets imported successfully</span>',
                    pos='topCenter',
                    fade=True,
                    fst=1000,
                    fet=250
                )
            except Exception as e:
                cmds.warning(f"Failed to import presets: {str(e)}")

if __name__ == "__main__":
    show()




