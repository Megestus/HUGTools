from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds

class MirrorToolUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MirrorToolUI, self).__init__(parent)
        self.setWindowTitle("Mirror Tool")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # 创建轴向选择组
        axis_group = QtWidgets.QGroupBox("Mirror Axis")
        axis_layout = QtWidgets.QHBoxLayout()
        
        self.axis_x = QtWidgets.QRadioButton("X")
        self.axis_y = QtWidgets.QRadioButton("Y")
        self.axis_z = QtWidgets.QRadioButton("Z")
        self.axis_x.setChecked(True)  # 默认选择X轴
        
        axis_layout.addWidget(self.axis_x)
        axis_layout.addWidget(self.axis_y)
        axis_layout.addWidget(self.axis_z)
        axis_group.setLayout(axis_layout)
        layout.addWidget(axis_group)
        
        # 创建选项
        self.mirror_geom = QtWidgets.QCheckBox("Mirror Geometry")
        self.mirror_geom.setChecked(True)
        layout.addWidget(self.mirror_geom)
        
        self.mirror_behavior = QtWidgets.QCheckBox("Mirror Behavior")
        layout.addWidget(self.mirror_behavior)
        
        # 创建按钮
        mirror_btn = QtWidgets.QPushButton("Mirror")
        mirror_btn.clicked.connect(self.mirror_objects)
        mirror_btn.setStyleSheet("""
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
        layout.addWidget(mirror_btn)
        
    def mirror_objects(self):
        # 获取选中的对象
        selection = cmds.ls(sl=True)
        if not selection:
            cmds.warning("Please select objects to mirror")
            return
            
        # 获取选择的轴向
        axis = 'x' if self.axis_x.isChecked() else 'y' if self.axis_y.isChecked() else 'z'
        
        try:
            for obj in selection:
                # 执行镜像操作
                if self.mirror_geom.isChecked():
                    # 镜像几何体
                    mirrored = cmds.duplicate(obj, name=f"{obj}_mirrored")[0]
                    cmds.scale(-1 if axis == 'x' else 1, 
                             -1 if axis == 'y' else 1, 
                             -1 if axis == 'z' else 1, 
                             mirrored)
                    
                if self.mirror_behavior.isChecked():
                    # 镜像行为（如变形器、约束等）
                    cmds.mirrorJoint(obj, mirrorYZ=axis=='x', mirrorXZ=axis=='y', mirrorXY=axis=='z')
            
            cmds.select(selection)  # 恢复原始选择
            
        except Exception as e:
            cmds.warning(f"Error during mirror operation: {str(e)}")

_mirror_tool_dialog = None

def show():
    global _mirror_tool_dialog
    
    if _mirror_tool_dialog:
        try:
            _mirror_tool_dialog.close()
            _mirror_tool_dialog.deleteLater()
        except:
            pass
            
    parent = QtWidgets.QApplication.activeWindow()
    _mirror_tool_dialog = MirrorToolUI(parent=parent)
    _mirror_tool_dialog.show()
    return _mirror_tool_dialog 