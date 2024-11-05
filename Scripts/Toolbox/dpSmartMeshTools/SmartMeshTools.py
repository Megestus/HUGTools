from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from pathlib import Path
import importlib
import sys
import os

class ModItButton(QtWidgets.QPushButton):
    """自定义按钮样式类"""
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

class SmartMeshToolsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SmartMeshToolsWindow, self).__init__(parent)
        self.setWindowTitle("Smart Mesh Tools")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.mesh_tools = SmartMeshTools()
        
        # 工具配置
        self.tool_config = {
            "name": "SmartMeshTools",
            "tools": [
                {
                    "name": "Smart Combine",
                    "icon": "polyUnite.png",
                    "tooltip": "智能合并网格对象",
                    "command": self.mesh_tools.smart_combine
                },
                {
                    "name": "Smart Separate",
                    "icon": "polySeparate.png", 
                    "tooltip": "智能分离网格对象",
                    "command": self.mesh_tools.smart_separate
                },
                {
                    "name": "Smart Extract",
                    "icon": "polyChipOff.png",
                    "tooltip": "智能提取选中的面",
                    "command": lambda: self.mesh_tools.smart_extract(cmds.ls(sl=True, fl=True))
                },
                {
                    "name": "Smart Duplicate",
                    "icon": "polyDuplicateFacet.png",
                    "tooltip": "智能复制选中的面",
                    "command": lambda: self.mesh_tools.smart_duplicate_face(cmds.ls(sl=True, fl=True))
                }
            ]
        }
        
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # 创建标题栏
        title_bar = QtWidgets.QWidget()
        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        title_label = QtWidgets.QLabel("Smart Mesh Tools")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #CCCCCC;")
        
        close_button = QtWidgets.QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
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
        close_button.clicked.connect(self.close)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_button)
        
        main_layout.addWidget(title_bar)

        # 创建工具按钮网格
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(5)
        
        for i, tool in enumerate(self.tool_config["tools"]):
            # 创建按钮
            icon = QtGui.QIcon(f":{tool['icon']}")  # 使用Maya内置图标
            button = ModItButton(tool["name"], icon)
            button.setToolTip(tool["tooltip"])
            button.clicked.connect(self.create_tool_command(tool["command"]))
            
            # 在网格中放置按钮
            row = i // 2
            col = i % 2
            grid_layout.addWidget(button, row, col)
        
        main_layout.addLayout(grid_layout)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QDialog {
                background-color: #3C3C3C;
                border: 1px solid #555555;
            }
        """)

    def create_tool_command(self, command):
        """创建工具命令的包装函数"""
        def wrapper():
            try:
                result = command()
                if result:
                    print(f"操作成功: {result}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "错误", str(e))
        return wrapper

class SmartMeshTools:
    """智能网格工具核心功能类"""
    def __init__(self):
        self.custom_names = {
            'combine': True,
            'separate': True,
            'extract': True,
            'duplicate': True
        }
    
    def smart_combine(self):
        """智能合并网格对象"""
        mesh_transforms = cmds.ls(sl=True, type="transform")
        if len(mesh_transforms) < 2:
            raise RuntimeError("至少需要选择两个网格对象")
            
        sel = cmds.ls(sl=True, long=True)
        parent_groups = []
        for obj in sel:
            parent = cmds.listRelatives(obj, parent=True, fullPath=True)
            if parent:
                parent_groups.extend(parent)
                
        target_group = max(set(parent_groups), key=parent_groups.count) if parent_groups else None
        combined_name = self._generate_name("SmartCombine")
        
        cmds.polyUnite(mesh_transforms, name=combined_name)
        cmds.delete(combined_name, constructionHistory=True)
        cmds.xform(combined_name, centerPivots=True)
        
        if target_group:
            cmds.parent(combined_name, target_group)
            
        return combined_name

    def smart_separate(self):
        """智能分离网格对象"""
        sel = cmds.ls(sl=True)
        if not sel or len(sel) > 1:
            raise RuntimeError("请只选择一个网格对象")
            
        pivot = cmds.xform(sel[0], q=True, ws=True, rp=True)
        base_name = self._generate_name("SmartSeparate")
        
        cmds.polySeparate(sel[0])
        separated = cmds.ls(sl=True)
        
        results = []
        for i, obj in enumerate(separated):
            new_name = f"{base_name}_{i+1}"
            renamed = cmds.rename(obj, new_name)
            results.append(renamed)
            cmds.xform(renamed, ws=True, rp=pivot)
            
        return results

    def smart_extract(self, faces):
        """智能提取选中的面"""
        return self._extract_duplicate(faces, extract=True)
        
    def smart_duplicate_face(self, faces):
        """智能复制选中的面"""
        return self._extract_duplicate(faces, extract=False)
        
    def _extract_duplicate(self, faces, extract=True):
        if not faces:
            raise RuntimeError("请选择要处理的面")
            
        mesh = cmds.ls(faces[0].split('.')[0], long=True)[0]
        op_type = "SmartExtract" if extract else "SmartDuplicate" 
        new_name = self._generate_name(op_type)
        
        dup = cmds.duplicate(mesh, name=new_name)[0]
        
        new_faces = []
        for face in faces:
            face_id = face.split('[')[1][:-1]
            new_faces.append(f"{dup}.f[{face_id}]")
            
        all_faces = cmds.polyListComponentConversion(dup, tf=True)
        faces_to_delete = list(set(all_faces) - set(new_faces))
        if faces_to_delete:
            cmds.delete(faces_to_delete)
            
        if extract:
            cmds.delete(faces)
            
        return dup
        
    def _generate_name(self, base, index=1):
        """生成不重复的名称"""
        name = f"{base}_{index}"
        while cmds.objExists(name):
            index += 1
            name = f"{base}_{index}"
        return name

def maya_main_window():
    """获取Maya主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def show():
    """显示工具窗口"""
    global smart_mesh_window
    try:
        smart_mesh_window.close()
        smart_mesh_window.deleteLater()
    except:
        pass
        
    parent = maya_main_window()
    smart_mesh_window = SmartMeshToolsWindow(parent)
    smart_mesh_window.show()

if __name__ == "__main__":
    show()