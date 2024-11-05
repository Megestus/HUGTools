from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import maya.mel as mel
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

class QuickExportFBX_UI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(QuickExportFBX_UI, self).__init__(parent)
        
        self.setWindowTitle("Quick Export FBX")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.setMinimumWidth(400)
        
        # 获取当前Maya文件路径
        self.default_path = self.get_maya_file_path()
        
        # 创建主布局
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #444444;
            }
            QLabel {
                color: #CCCCCC;
            }
            QCheckBox {
                color: #CCCCCC;
            }
            QPushButton {
                background-color: #555555;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #666666;
                border: 1px solid #777777;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QLineEdit {
                background-color: #555555;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 3px;
            }
            QTextEdit {
                background-color: #555555;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
            }
            QGroupBox {
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0px 5px 0px 5px;
            }
            QComboBox {
                background-color: #555555;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 3px;
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

    def get_maya_file_path(self):
        """获取当前Maya文件所在目录"""
        current_file = cmds.file(query=True, sceneName=True)
        if current_file:
            # 如果文件已保存，返回文件所在目录
            return os.path.dirname(current_file)
        else:
            # 如果文件保存，返回用户文档目录
            if os.name == 'nt':  # Windows
                return os.path.expanduser("~\\Documents")
            else:  # macOS 和 Linux
                return os.path.expanduser("~/Documents")

    def create_widgets(self):
        # 路径选择部分
        self.path_label = QtWidgets.QLabel("Export Path:")
        self.path_line = QtWidgets.QLineEdit()
        # 设置默认路径
        self.path_line.setText(self.default_path)
        
        # 使用ModItButton替换原来的按钮
        self.browse_btn = ModItButton("Browse", icon=QtGui.QIcon(":fileOpen.png"))
        
        # 选项组
        self.options_group = QtWidgets.QGroupBox("Options")
        
        # 几何体选项
        self.geo_label = QtWidgets.QLabel("Geometry Options:")
        self.smooth_groups_cb = QtWidgets.QCheckBox("Smooth Groups")
        self.hard_edges_cb = QtWidgets.QCheckBox("Hard Edges")
        self.tangents_cb = QtWidgets.QCheckBox("Tangents and Binormals")
        self.smooth_mesh_cb = QtWidgets.QCheckBox("Smooth Mesh")
        self.triangulate_cb = QtWidgets.QCheckBox("Triangulate")
        self.instances_cb = QtWidgets.QCheckBox("Keep Instances")
        
        # 文件格式选项
        self.format_label = QtWidgets.QLabel("File Format:")
        self.file_type_combo = QtWidgets.QComboBox()
        self.file_type_combo.addItems(["Binary", "ASCII"])
        
        # 导出按钮
        self.export_btn = ModItButton("Export Selected Objects", icon=QtGui.QIcon(":fileNew.png"))
        self.open_folder_btn = ModItButton("Open Folder", icon=QtGui.QIcon(":folder-open.png"))
        self.export_btn.setMinimumHeight(50)
        
        # 状态显示
        self.status_text = QtWidgets.QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(60)
        self.status_text.setText("Ready")

    def create_layouts(self):
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)
        
        # 路径选择布局
        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_line)
        path_layout.addWidget(self.browse_btn)
        
        # 选项布局
        options_layout = QtWidgets.QVBoxLayout()
        
        # 几何体选项网格布局
        geo_grid = QtWidgets.QGridLayout()
        geo_grid.addWidget(self.geo_label, 0, 0, 1, 2)
        geo_grid.addWidget(self.smooth_groups_cb, 1, 0)
        geo_grid.addWidget(self.hard_edges_cb, 1, 1)
        geo_grid.addWidget(self.tangents_cb, 2, 0)
        geo_grid.addWidget(self.smooth_mesh_cb, 2, 1)
        geo_grid.addWidget(self.triangulate_cb, 3, 0)
        geo_grid.addWidget(self.instances_cb, 3, 1)
        
        # 文件格式布局
        format_layout = QtWidgets.QHBoxLayout()
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.file_type_combo)
        format_layout.addStretch()
        
        # 将所有选项添加到选项组
        options_layout.addLayout(geo_grid)
        options_layout.addLayout(format_layout)
        self.options_group.setLayout(options_layout)
        
        # 导出按钮布局
        export_layout = QtWidgets.QHBoxLayout()
        # 设置Export按钮占据更多空间
        self.export_btn.setMinimumWidth(200)  # 设置最小宽度
        export_layout.addWidget(self.export_btn, stretch=6)  # 设置stretch为7
        
        # 设置Open Folder按钮更窄
        self.open_folder_btn.setMinimumWidth(80)  # 设置最小宽度
        self.open_folder_btn.setMaximumWidth(120)  # 设置最大宽度
        export_layout.addWidget(self.open_folder_btn, stretch=4)  # 设置stretch为3
        
        # 添加所有元素到主布局
        main_layout.addLayout(path_layout)
        main_layout.addWidget(self.options_group)
        main_layout.addLayout(export_layout)
        main_layout.addWidget(self.status_text)

    def create_connections(self):
        self.browse_btn.clicked.connect(self.browse_path)
        self.open_folder_btn.clicked.connect(self.open_export_folder)
        self.export_btn.clicked.connect(self.export_objects)

    def browse_path(self):
        """选择导出路径"""
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            self.path_line.text(),
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        if directory:
            self.path_line.setText(directory)
            self.status_text.setText("Export path selected, ready to export")
            self.status_text.setStyleSheet("background-color: #555555;")

    def open_export_folder(self):
        """打开导出文件夹"""
        path = self.path_line.text()
        if not path:
            self.status_text.setText("Error: Please select export path!")
            self.status_text.setStyleSheet("background-color: #663333;")
            return
            
        if not os.path.exists(path):
            self.status_text.setText("Error: Export path does not exist!")
            self.status_text.setStyleSheet("background-color: #663333;")
            return
            
        # 根据操作系统打开文件夹
        if os.name == 'nt':  # Windows
            os.startfile(path)
        elif os.name == 'posix':  # macOS 和 Linux
            if sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', path])
            else:  # Linux
                subprocess.Popen(['xdg-open', path])

    def export_objects(self):
        """导出选中的物体"""
        # 获取导出路径
        export_path = self.path_line.text()
        if not export_path:
            self.status_text.setText("Error: Please select export path!")
            self.status_text.setStyleSheet("background-color: #663333;")
            return
            
        # 确保导出路径存在
        if not os.path.exists(export_path):
            try:
                os.makedirs(export_path)
            except Exception as e:
                self.status_text.setText(f"Error: Failed to create export directory: {str(e)}")
                self.status_text.setStyleSheet("background-color: #663333;")
                return
        
        # 获取选中的物体
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            self.status_text.setText("Error: Please select objects to export!")
            self.status_text.setStyleSheet("background-color: #663333;")
            return
        
        # 获取导出选项
        smooth_groups = self.smooth_groups_cb.isChecked()
        hard_edges = self.hard_edges_cb.isChecked()
        tangents = self.tangents_cb.isChecked()
        smooth_mesh = self.smooth_mesh_cb.isChecked()
        triangulate = self.triangulate_cb.isChecked()
        instances = self.instances_cb.isChecked()
        file_type = self.file_type_combo.currentText()
        
        total_exported = 0
        processed_groups = []
        exported_files = {}  # {组名: [文件名列表]}
        
        # 更新状态
        self.status_text.setText("Exporting...")
        
        # 遍历选中的物体
        for obj in selected_objects:
            try:
                # 检查是否是组
                is_group = False
                if cmds.objectType(obj) == "transform":
                    children = cmds.listRelatives(obj, children=True, fullPath=True) or []
                    if children:
                        child_types = [cmds.objectType(child) for child in children]
                        is_group = not all(t == 'mesh' for t in child_types)

                if is_group:
                    # 处理组
                    group_name = obj.split(":")[-1].split("|")[-1]
                    group_dir = os.path.join(export_path, group_name)
                    
                    if not os.path.exists(group_dir):
                        os.makedirs(group_dir)
                    
                    children = [child for child in (cmds.listRelatives(obj, children=True, fullPath=True, type='transform') or [])
                              if cmds.objectType(child) == 'transform']
                    
                    if children:
                        processed_groups.append(group_name)
                        exported_files[group_name] = []
                        
                        for child in children:
                            child_name = child.split(":")[-1].split("|")[-1]
                            self._export_single_object(child, group_dir, smooth_groups, hard_edges, 
                                                    tangents, smooth_mesh, triangulate, instances, file_type)
                            exported_files[group_name].append(f"{child_name}.fbx")
                            total_exported += 1
                else:
                    # 直接导出单个物体
                    obj_name = obj.split(":")[-1].split("|")[-1]
                    self._export_single_object(obj, export_path, smooth_groups, hard_edges, 
                                            tangents, smooth_mesh, triangulate, instances, file_type)
                    if "root" not in exported_files:
                        exported_files["root"] = []
                    exported_files["root"].append(f"{obj_name}.fbx")
                    total_exported += 1
                    
            except Exception as e:
                self.status_text.setText(f"Error: Failed to process {obj}: {str(e)}")
                self.status_text.setStyleSheet("background-color: #663333;")
                continue
        
        # 完成后恢复选择
        cmds.select(selected_objects)
        
        # 构建英文的完成信息
        status_message = "Export Complete:\n"
        status_message += f"Total Files Exported: {total_exported}\n"
        status_message += f"Export Path: {export_path}\n\n"
        
        # 添加组和文件信息
        for group_name, files in exported_files.items():
            if group_name == "root":
                # 直接导出到根目录的文件
                for file_name in files:
                    status_message += f"- {file_name}\n"
            else:
                # 组内的文件
                status_message += f"{group_name}\n"
                for file_name in files:
                    status_message += f"   - {file_name}\n"
        
        # 更新状态显示
        self.status_text.setText(status_message)
        self.status_text.setStyleSheet("background-color: #335533;")

    def _export_single_object(self, obj, export_path, smooth_groups, hard_edges, 
                            tangents, smooth_mesh, triangulate, instances, file_type):
        """导出单个物体的辅助函数"""
        # 选择当前物体
        cmds.select(obj, replace=True)
        
        # 删除历史记录
        cmds.delete(constructionHistory=True)
        
        # 设置FBX导出选项
        mel.eval(f'FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups -v {str(smooth_groups).lower()}')
        mel.eval(f'FBXProperty Export|IncludeGrp|Geometry|expHardEdges -v {str(hard_edges).lower()}')
        mel.eval(f'FBXProperty Export|IncludeGrp|Geometry|TangentsandBinormals -v {str(tangents).lower()}')
        mel.eval(f'FBXProperty Export|IncludeGrp|Geometry|SmoothMesh -v {str(smooth_mesh).lower()}')
        mel.eval(f'FBXProperty Export|IncludeGrp|Geometry|Triangulate -v {str(triangulate).lower()}')
        mel.eval(f'FBXProperty Export|IncludeGrp|Geometry|Instances -v {str(instances).lower()}')
        mel.eval(f'FBXProperty Export|AdvOptGrp|Fbx|AsciiFbx -v "{file_type}"')
        
        # 获取物体的短名称
        obj_name = obj.split(":")[-1].split("|")[-1]
        
        # 构建导出文件路径
        file_path = os.path.normpath(os.path.join(export_path, f"{obj_name}.fbx"))
        file_path = file_path.replace("\\", "/")
        
        # 导出FBX
        mel.eval(f'FBXExport -f "{file_path}" -s')

#====== UI Functions ======

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def show():
    """
    Display UI for the quick export module
    
    Functions:
    - Close and delete existing UI instance (if exists)
    - Create new UI instance and display
    """
    global quick_export_ui
    try:
        quick_export_ui.close()
        quick_export_ui.deleteLater()
    except:
        pass
    parent = maya_main_window()
    quick_export_ui = QuickExportFBX_UI(parent)
    quick_export_ui.show()
    quick_export_ui.raise_()
    quick_export_ui.activateWindow()

if __name__ == "__main__":
    show()
