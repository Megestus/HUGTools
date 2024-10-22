import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets, QtGui, QtCore
from functools import partial

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

class VertsNormalUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(VertsNormalUI, self).__init__(parent)
        self.setWindowTitle("法线工具")
        self.setFixedWidth(300)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # 显示控制组
        self.display_group = QtWidgets.QGroupBox("显示控制")
        self.display_btn = QtWidgets.QToolButton()
        self.display_btn.setIcon(QtGui.QIcon(":polyNormalSetToFace.png"))
        self.display_btn.setIconSize(QtCore.QSize(32, 32))
        self.display_btn.setToolTip("法线显示切换")

        self.normal_size_label = QtWidgets.QLabel("法线长短:")
        self.normal_size_field = QtWidgets.QDoubleSpinBox()
        self.normal_size_field.setValue(0.4)
        self.normal_size_field.setRange(0.01, 10.0)
        self.normal_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.normal_size_slider.setRange(1, 1000)
        self.normal_size_slider.setValue(40)

        # 法线锁定组
        self.lock_group = QtWidgets.QGroupBox("法线锁定")
        self.lock_btn = RoundedButton("锁定法线")
        self.unlock_btn = RoundedButton("解锁法线")

        # 快速设置和平均化组
        self.quick_set_average_group = QtWidgets.QGroupBox("快速设置")
        self.quick_set_buttons = []
        for axis in ["+X", "+Y", "+Z", "-X", "-Y", "-Z"]:
            btn = RoundedButton(axis)
            self.quick_set_buttons.append(btn)

        self.average_buttons = []
        for axis in ["X", "Y", "Z"]:
            btn = RoundedButton(f"平均化 {axis}")
            self.average_buttons.append(btn)

        self.average_normals_btn = RoundedButton("平均法线")

        # 手动设置组
        self.manual_set_group = QtWidgets.QGroupBox("法线编辑")
        self.get_normal_btn = RoundedButton("获取法线")
        self.normal_fields = [QtWidgets.QLineEdit() for _ in range(3)]
        self.set_normal_btn = RoundedButton("设置法线")

        # 传输法线组
        self.transfer_group = QtWidgets.QGroupBox("传输法线")
        self.get_mesh_btn = RoundedButton("获取网格")
        self.mesh_name_field = QtWidgets.QLineEdit()
        self.mesh_name_field.setReadOnly(True)
        self.transfer_normal_btn = RoundedButton("传输法线")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 显示控制布局
        display_layout = QtWidgets.QHBoxLayout()
        display_layout.addWidget(self.display_btn)
        
        size_layout = QtWidgets.QHBoxLayout()
        size_layout.addWidget(self.normal_size_label)
        size_layout.addWidget(self.normal_size_field)
        
        display_layout.addLayout(size_layout)
        
        display_main_layout = QtWidgets.QVBoxLayout()
        display_main_layout.addLayout(display_layout)
        display_main_layout.addWidget(self.normal_size_slider)
        
        self.display_group.setLayout(display_main_layout)

        # 法线锁定布局
        lock_layout = QtWidgets.QHBoxLayout()
        lock_layout.addWidget(self.lock_btn)
        lock_layout.addWidget(self.unlock_btn)
        self.lock_group.setLayout(lock_layout)

        # 快速设置和平均化布局
        quick_set_average_layout = QtWidgets.QVBoxLayout()
        
        quick_set_layout = QtWidgets.QGridLayout()
        for i, btn in enumerate(self.quick_set_buttons):
            quick_set_layout.addWidget(btn, i // 3, i % 3)
        quick_set_average_layout.addLayout(quick_set_layout)

        average_layout = QtWidgets.QHBoxLayout()
        for btn in self.average_buttons:
            average_layout.addWidget(btn)
        quick_set_average_layout.addLayout(average_layout)

        quick_set_average_layout.addWidget(self.average_normals_btn)
        
        self.quick_set_average_group.setLayout(quick_set_average_layout)

        # 手动设置布局
        manual_set_layout = QtWidgets.QVBoxLayout()
        manual_set_layout.addWidget(self.get_normal_btn)
        normal_fields_layout = QtWidgets.QHBoxLayout()
        for field in self.normal_fields:
            normal_fields_layout.addWidget(field)
        manual_set_layout.addLayout(normal_fields_layout)
        manual_set_layout.addWidget(self.set_normal_btn)
        self.manual_set_group.setLayout(manual_set_layout)

        # 传输法线布局
        transfer_layout = QtWidgets.QVBoxLayout()
        transfer_layout.addWidget(self.get_mesh_btn)
        transfer_layout.addWidget(self.mesh_name_field)
        transfer_layout.addWidget(self.transfer_normal_btn)
        self.transfer_group.setLayout(transfer_layout)

        # 将所有组添加到主布局
        main_layout.addWidget(self.display_group)
        main_layout.addWidget(self.lock_group)
        main_layout.addWidget(self.quick_set_average_group)  # 新的组合组
        main_layout.addWidget(self.manual_set_group)
        main_layout.addWidget(self.transfer_group)

    def create_connections(self):
        self.display_btn.clicked.connect(self.toggle)
        self.normal_size_field.valueChanged.connect(self.set_normal_size_from_field)
        self.normal_size_slider.valueChanged.connect(self.set_normal_size_from_slider)
        self.lock_btn.clicked.connect(self.lock_normal)
        self.unlock_btn.clicked.connect(self.unlock_normal)

        for i, btn in enumerate(self.quick_set_buttons):
            btn.clicked.connect(partial(self.quick_set_normal, i))

        for i, btn in enumerate(self.average_buttons):
            btn.clicked.connect(partial(self.flatten, i))

        self.get_normal_btn.clicked.connect(self.get_verts_normal)
        self.set_normal_btn.clicked.connect(self.set_verts_normal)
        self.get_mesh_btn.clicked.connect(self.get_mesh)
        self.transfer_normal_btn.clicked.connect(self.set_normal)
        self.average_normals_btn.clicked.connect(self.average_normals)

    def set_normal_size_from_field(self, value):
        self.normal_size_slider.setValue(int(value * 100))
        self.set_normal_size(value)

    def set_normal_size_from_slider(self, value):
        size = value / 100.0
        self.normal_size_field.blockSignals(True)
        self.normal_size_field.setValue(size)
        self.normal_size_field.blockSignals(False)
        self.set_normal_size(size)

    def set_normal_size(self, value):
        cmds.polyOptions(sn=value)

    # 切换显示法线
    def toggle(self):
        sel = cmds.ls(sl=True)
        if sel:
            new_size = self.normal_size_field.value()
            display_state = cmds.polyOptions(q=True, dn=True)[0]
            cmds.polyOptions(dn=not display_state, pt=True, sn=new_size)
        else:
            cmds.warning("未选择任何对象！")

    def get_verts_normal(self):
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            if cmds.objectType(sel[0]) == "mesh":
                normal = cmds.polyNormalPerVertex(sel[0], q=True, xyz=True)[:3]
                for i, field in enumerate(self.normal_fields):
                    field.setText(f"{normal[i]:.5g}")  # 使用 g 格式，显示5位有效数字
            elif cmds.objectType(sel[0]) == "meshFace":
                normal = self.get_face_normal(sel[0])
                for i, field in enumerate(self.normal_fields):
                    field.setText(f"{normal[i]:.5g}")  # 使用 g 格式，最多显示5位有效数字
            else:
                cmds.warning("请选择顶点或面！")
        else:
            cmds.warning("未选择任何对象！")

    def set_verts_normal(self):
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            normal = [float(field.text()) for field in self.normal_fields]
            if cmds.objectType(sel[0]) == "mesh":
                cmds.polyNormalPerVertex(xyz=normal)
            else:
                vtx_list = cmds.polyListComponentConversion(sel, tv=True)
                vtx_list = cmds.filterExpand(vtx_list, sm=31)
                cmds.polyNormalPerVertex(vtx_list, xyz=normal)
        else:
            cmds.warning("未选择任何对象！")

    def get_mesh(self):
        sel = cmds.ls(sl=True)
        if sel:
            self.mesh_name_field.setText(sel[0])
        else:
            cmds.warning("未选择任何对象！")

    def set_normal(self):
        source_name = self.mesh_name_field.text()
        if source_name:
            sel = cmds.ls(sl=True)
            for s in sel:
                cmds.transferAttributes(source_name, s, transferNormals=1)
                cmds.delete(s, ch=True)
        else:
            cmds.warning("请先获取法线！")

    def flatten(self, axis_index):
        """
        平坦化函数：将选中顶点的法线在指定轴上的分量设置为0
        
        :param axis_index: 要平坦化的轴索引（0=X, 1=Y, 2=Z）
        """
        axes = ["x", "y", "z"]
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            for s in sel:
                # 获取当前法线
                n = cmds.polyNormalPerVertex(s, q=True, xyz=True)[:3]
                # 将指定轴的分量设置为0
                n[axis_index] = 0
                # 应用新的法线
                cmds.polyNormalPerVertex(s, xyz=n)
            
            # 更新显示
            for obj in set(s.split('.')[0] for s in sel):
                cmds.polyOptions(obj, point=True)
        else:
            cmds.warning("未选择任何对象！")

    def unlock_normal(self):
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            cmds.polyNormalPerVertex(ufn=True)
        else:
            cmds.warning("未选任何对象！")

    def lock_normal(self):
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            cmds.polyNormalPerVertex(fn=True)
        else:
            cmds.warning("选择任何对象！")

    def quick_set_normal(self, index):
        """
        快速设置法线函数：将选中顶点的法线设置为指定的世界坐标轴方向
        
        :param index: 要设置的法线方向索引（0=+X, 1=+Y, 2=+Z, 3=-X, 4=-Y, 5=-Z）
        """
        axes = [
            (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (-1, 0, 0), (0, -1, 0), (0, 0, -1)
        ]
        normal = axes[index]
        
        sel = cmds.ls(sl=True, fl=True)
        if not sel:
            cmds.warning("未选择任何对象！")
            return

        # 转换选择为顶点
        vertices = cmds.polyListComponentConversion(sel, tv=True)
        vertices = cmds.filterExpand(vertices, sm=31)  # sm=31 表示顶点

        if not vertices:
            cmds.warning("无法获取顶点！")
            return

        # 设置法线
        for vertex in vertices:
            cmds.polyNormalPerVertex(vertex, xyz=normal)

        # 更新显示
        affected_objects = set(vert.split('.')[0] for vert in vertices)
        for obj in affected_objects:
            cmds.polyOptions(obj, point=True)

        cmds.select(sel, r=True)  # 恢复原始选择
        cmds.inViewMessage(amg='线设置完成', pos='midCenter', fade=True)

    def average_normals(self):
        """
        平均选中顶点的法线
        """
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            # 转换选择为顶点
            vertices = cmds.polyListComponentConversion(sel, tv=True)
            vertices = cmds.filterExpand(vertices, sm=31)  # sm=31 表示顶点
            
            if not vertices:
                cmds.warning("无法获取顶点！")
                return
            
            # 检查法线是否被锁定，如果被锁定，先解锁
            for vertex in vertices:
                if cmds.polyNormalPerVertex(vertex, q=True, freezeNormal=True):
                    cmds.polyNormalPerVertex(vertex, ufn=True)
            
            # 使用 polyAverageNormal 命令
            cmds.polyAverageNormal(vertices)
            cmds.inViewMessage(amg='法线已平均化', pos='midCenter', fade=True)
        else:
            cmds.warning("未选择任何对象！")

def show_ui():
    window_name = "VertsNormalUIWindow"
    if cmds.window(window_name, exists=True):
        # 获取当前窗口位置
        existing_window = QtWidgets.QApplication.activeWindow()
        pos = existing_window.pos()
        # 关闭现有窗口
        cmds.deleteUI(window_name)
    else:
        # 如果窗口不存在，设置默认位置
        pos = QtCore.QPoint(200, 200)
    
    ui = VertsNormalUI()
    ui.setObjectName(window_name)
    
    # 设置窗口位置
    ui.move(pos)
    
    ui.show()

if __name__ == "__main__":
    show_ui()
