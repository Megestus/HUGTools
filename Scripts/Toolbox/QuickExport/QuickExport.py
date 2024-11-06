# -*- coding: utf-8 -*-

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
        
        # 添加导出格式单选框
        self.format_group = QtWidgets.QGroupBox("Export Format")
        self.format_button_group = QtWidgets.QButtonGroup(self)  # 创建按钮组
        self.fbx_format_rb = QtWidgets.QRadioButton("FBX")
        self.obj_format_rb = QtWidgets.QRadioButton("OBJ")
        # 将单选框添加到按钮组
        self.format_button_group.addButton(self.fbx_format_rb)
        self.format_button_group.addButton(self.obj_format_rb)
        # 默认选中FBX
        self.fbx_format_rb.setChecked(True)
        
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
        
        # 导出格式单选框布局
        format_layout = QtWidgets.QHBoxLayout()
        format_layout.addWidget(self.fbx_format_rb)
        format_layout.addWidget(self.obj_format_rb)
        format_layout.addStretch()
        self.format_group.setLayout(format_layout)
        
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
        main_layout.addWidget(self.format_group)  # 添加格式选择组
        main_layout.addLayout(export_layout)
        main_layout.addWidget(self.status_text)

    def create_connections(self):
        self.browse_btn.clicked.connect(self.browse_path)
        self.open_folder_btn.clicked.connect(self.open_export_folder)
        self.export_btn.clicked.connect(self.export_objects)
        # 连接单选框信号
        self.format_button_group.buttonClicked.connect(self._handle_format_change)

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

    def _check_nested_groups(self, obj):
        """检查是否存在嵌套组"""
        if cmds.objectType(obj) == "transform":
            children = cmds.listRelatives(obj, children=True, fullPath=True) or []
            for child in children:
                if cmds.objectType(child) == "transform":
                    grandchildren = cmds.listRelatives(child, children=True, fullPath=True) or []
                    if grandchildren and any(cmds.objectType(gc) == "transform" for gc in grandchildren):
                        return True
        return False

    def export_objects(self):
        """导出选中的物体"""
        # 获取导出路径
        export_path = self.path_line.text()
        if not export_path:
            self.status_text.setText("Error: Please select export path!")
            self.status_text.setStyleSheet("background-color: #663333;")
            return
        
        # 获取选中的对象
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            self.status_text.setText("Error: Please select objects to export!")
            self.status_text.setStyleSheet("background-color: #663333;")
            return
        
        # 检查是否有嵌套组
        for obj in selected_objects:
            if self._check_nested_groups(obj):
                self.status_text.setText("Error: Nested groups are not supported!\nExample:\nRetopo\n  └─low\n      └─cube.fbx\n\nPlease select single-level groups only.")
                self.status_text.setStyleSheet("background-color: #663333;")
                return
        
        # 初始化导出文件记录字典
        exported_files = {"root": []}
        
        # 检查选择的导出格式
        try:
            if self.fbx_format_rb.isChecked():
                total_exported = self._export_fbx(selected_objects, export_path, exported_files)
            else:  # OBJ format
                total_exported = self._export_obj(selected_objects, export_path, exported_files)
                
            # 构建完成信息
            status_message = "Export Complete:\n"
            status_message += f"Total Files Exported: {total_exported}\n"
            status_message += f"Export Path: {export_path}\n\n"
            
            # 添加文件信息
            for group_name, files in exported_files.items():
                if files:
                    if group_name == "root":
                        for file_name in files:
                            status_message += f"- {file_name}\n"
                    else:
                        status_message += f"{group_name}/\n"
                        for file_name in files:
                            status_message += f"   - {file_name}\n"
            
            self.status_text.setText(status_message)
            self.status_text.setStyleSheet("background-color: #335533;")
            
        except Exception as e:
            self.status_text.setText(f"Error: {str(e)}")
            self.status_text.setStyleSheet("background-color: #663333;")

    def _export_obj(self, objects, export_path, exported_files):
        """导出OBJ格式文件"""
        total_exported = 0
        processed_groups = []
        
        for obj in objects:
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
                    
                    # 创建组文件夹
                    if not os.path.exists(group_dir):
                        os.makedirs(group_dir)
                    
                    # 获取组内的所有子对象
                    children = [child for child in (cmds.listRelatives(obj, children=True, fullPath=True, type='transform') or [])
                              if cmds.objectType(child) == 'transform']
                    
                    if children:
                        processed_groups.append(group_name)
                        exported_files[group_name] = []
                        
                        # 导出每个子对象
                        for child in children:
                            try:
                                # 选择当前子对象
                                cmds.select(child, replace=True)
                                
                                # 获取子对象名称
                                child_name = child.split(":")[-1].split("|")[-1]
                                
                                # 构建导出文件路径
                                file_path = os.path.normpath(os.path.join(group_dir, f"{child_name}.obj"))
                                file_path = file_path.replace("\\", "/")
                                
                                # 使用默认设置导出OBJ
                                cmds.file(file_path, force=True, exportSelected=True, type="OBJexport", pr=True)
                                
                                exported_files[group_name].append(f"{child_name}.obj")
                                total_exported += 1
                                
                            except Exception as e:
                                raise Exception(f"导出组 {group_name} 中的 {child_name} 时出错: {str(e)}")
                else:
                    # 导出单个对象
                    cmds.select(obj, replace=True)
                    obj_name = obj.split(":")[-1].split("|")[-1]
                    
                    # 构建导出文件路径
                    file_path = os.path.normpath(os.path.join(export_path, f"{obj_name}.obj"))
                    file_path = file_path.replace("\\", "/")
                    
                    # 使用默认设置导出OBJ
                    cmds.file(file_path, force=True, exportSelected=True, type="OBJexport", pr=True)
                    
                    exported_files["root"].append(f"{obj_name}.obj")
                    total_exported += 1
                    
            except Exception as e:
                raise Exception(f"处理 {obj} 时出错: {str(e)}")
        
        return total_exported

    def _export_fbx(self, objects, export_path, exported_files):
        """导出FBX格式文件"""
        total_exported = 0
        processed_groups = []
        
        for obj in objects:
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
                            try:
                                # 选择当前子对象
                                cmds.select(child, replace=True)
                                
                                # 获取子对象名称
                                child_name = child.split(":")[-1].split("|")[-1]
                                
                                # 构建导出文件路径
                                file_path = os.path.normpath(os.path.join(group_dir, f"{child_name}.fbx"))
                                file_path = file_path.replace("\\", "/")
                                
                                # 使用默认设置导出FBX
                                cmds.file(file_path, force=True, exportSelected=True, type="FBX export", pr=True)
                                
                                exported_files[group_name].append(f"{child_name}.fbx")
                                total_exported += 1
                            
                            except Exception as e:
                                raise Exception(f"导出组 {group_name} 中的 {child_name} 时出错: {str(e)}")
                else:
                    # 导出单个对象
                    cmds.select(obj, replace=True)
                    obj_name = obj.split(":")[-1].split("|")[-1]
                    
                    # 构建导出文件路径
                    file_path = os.path.normpath(os.path.join(export_path, f"{obj_name}.fbx"))
                    file_path = file_path.replace("\\", "/")
                    
                    # 使用默认设置导出FBX
                    cmds.file(file_path, force=True, exportSelected=True, type="FBX export", pr=True)
                    
                    exported_files["root"].append(f"{obj_name}.fbx")
                    total_exported += 1
                    
            except Exception as e:
                raise Exception(f"处理 {obj} 时出错: {str(e)}")
        
        return total_exported

    def _handle_format_change(self, button):
        """处理格式选择变化"""
        pass  # 由于移除了选项组，这个函数现在不需要做任何事

    def export_obj(self):
        # 首先获取选中的对象
        selected_objects = cmds.ls(selection=True)
        
        if not selected_objects:
            cmds.warning("请先选择要导出的对象！")
            return
            
        # 获取导出路径
        file_path = cmds.fileDialog2(fileFilter="OBJ Files (*.obj)", dialogStyle=2, fileMode=0)
        
        if not file_path:
            return
            
        file_path = file_path[0]
        
        try:
            # 导出选中的对象为OBJ
            cmds.file(file_path, 
                     force=True, 
                     exportSelected=True, 
                     type="OBJ",
                     preserveReferences=True)
            
            cmds.confirmDialog(title="成功", message="OBJ导出成功！", button=["确定"])
        except Exception as e:
            cmds.confirmDialog(title="错误", message=f"导出OBJ时出错: {str(e)}", button=["确定"])

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
