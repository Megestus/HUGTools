import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets, QtGui, QtCore
from functools import partial

class RoundedButton(QtWidgets.QPushButton):
    def __init__(self, text, icon=None):
        super(RoundedButton, self).__init__(text)
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

class VertsNormalUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(VertsNormalUI, self).__init__(parent)
        self.setWindowTitle("Normal Editor")
        self.setFixedWidth(300)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # Display Control Group
        self.display_group = QtWidgets.QGroupBox("Display Control")
        self.display_btn = RoundedButton("Normal", icon=QtGui.QIcon(":polyNormalSetToFace.png"))
        self.display_btn.setMinimumSize(100, 40)
        self.display_btn.setToolTip("Toggle normal display")

        self.normal_size_label = QtWidgets.QLabel("Normal Size:")
        self.normal_size_field = QtWidgets.QDoubleSpinBox()
        self.normal_size_field.setValue(0.4)
        self.normal_size_field.setRange(0.01, 10.0)
        self.normal_size_field.setToolTip("Set the size of displayed normals")
        self.normal_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.normal_size_slider.setRange(1, 1000)
        self.normal_size_slider.setValue(40)
        self.normal_size_slider.setToolTip("Adjust the size of displayed normals")

        # Normal Lock Group
        self.lock_group = QtWidgets.QGroupBox("Normal Lock")
        self.lock_btn = RoundedButton("Lock Normal", icon=QtGui.QIcon(":polyNormalLock.png"))
        self.lock_btn.setToolTip("Lock the current normal direction")
        self.unlock_btn = RoundedButton("Unlock Normal", icon=QtGui.QIcon(":polyNormalUnlock.png"))
        self.unlock_btn.setToolTip("Unlock the normal direction")

        # Quick Set and Average Group
        self.quick_set_average_group = QtWidgets.QGroupBox("Quick Set")
        self.quick_set_buttons = []
        for axis in ["+X", "+Y", "+Z", "-X", "-Y", "-Z"]:
            btn = RoundedButton(axis)
            btn.setToolTip(f"Set normal direction to {axis}")
            self.quick_set_buttons.append(btn)

        self.average_buttons = []
        for axis in ["X", "Y", "Z"]:
            btn = RoundedButton(f"Average {axis}")
            btn.setToolTip(f"Average normals along the {axis} axis")
            self.average_buttons.append(btn)

        self.average_normals_btn = RoundedButton("Average Normals")
        self.average_normals_btn.setToolTip("Average all selected normals")

        # Manual Set Group
        self.manual_set_group = QtWidgets.QGroupBox("Normal Edit")
        self.get_normal_btn = RoundedButton("Get Normal", icon=QtGui.QIcon(":polyNormalDisplay.png"))
        self.get_normal_btn.setToolTip("Get the normal direction of selected vertex or face")
        self.normal_fields = [QtWidgets.QLineEdit() for _ in range(3)]
        for field in self.normal_fields:
            field.setToolTip("Enter a value for the normal component")
        self.set_normal_btn = RoundedButton("Set Normal")
        self.set_normal_btn.setToolTip("Set the normal direction for selected vertices")

        # Transfer Normal Group
        self.transfer_group = QtWidgets.QGroupBox("Transfer Normal")
        self.get_mesh_btn = RoundedButton("Get Mesh", icon=QtGui.QIcon(":polySelectObject.png"))
        self.get_mesh_btn.setToolTip("Select the source mesh for normal transfer")
        self.mesh_name_field = QtWidgets.QLineEdit()
        self.mesh_name_field.setReadOnly(True)
        self.mesh_name_field.setToolTip("Displays the name of the selected source mesh")
        self.transfer_normal_btn = RoundedButton("Transfer Normal")
        self.transfer_normal_btn.setToolTip("Transfer normals from source mesh to selected objects")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Display Control Layout
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

        # Normal Lock Layout
        lock_layout = QtWidgets.QHBoxLayout()
        lock_layout.addWidget(self.lock_btn)
        lock_layout.addWidget(self.unlock_btn)
        self.lock_group.setLayout(lock_layout)

        # Quick Set and Average Layout
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

        # Manual Set Layout
        manual_set_layout = QtWidgets.QVBoxLayout()
        manual_set_layout.addWidget(self.get_normal_btn)
        normal_fields_layout = QtWidgets.QHBoxLayout()
        for field in self.normal_fields:
            normal_fields_layout.addWidget(field)
        manual_set_layout.addLayout(normal_fields_layout)
        manual_set_layout.addWidget(self.set_normal_btn)
        self.manual_set_group.setLayout(manual_set_layout)

        # Transfer Normal Layout
        transfer_layout = QtWidgets.QVBoxLayout()
        transfer_layout.addWidget(self.get_mesh_btn)
        transfer_layout.addWidget(self.mesh_name_field)
        transfer_layout.addWidget(self.transfer_normal_btn)
        self.transfer_group.setLayout(transfer_layout)

        # Add all groups to main layout
        main_layout.addWidget(self.display_group)
        main_layout.addWidget(self.lock_group)
        main_layout.addWidget(self.quick_set_average_group)
        main_layout.addWidget(self.manual_set_group)
        main_layout.addWidget(self.transfer_group)

    def create_connections(self):
        self.display_btn.clicked.connect(self.toggle_normal_display)
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
        cmds.inViewMessage(amg=f'<span style="color:#FFA500;">Normal Size: {value:.2f}</span>', pos='botRight', fade=True, fst=10, fad=1)

    def toggle_normal_display(self):
        sel = cmds.ls(sl=True)
        if sel:
            new_size = self.normal_size_field.value()
            display_state = cmds.polyOptions(q=True, dn=True)[0]
            cmds.polyOptions(dn=not display_state, pt=True, sn=new_size)
            message = "Normals On" if not display_state else "Normals Off"
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.warning("No object selected!")

    def get_verts_normal(self):
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            if cmds.objectType(sel[0]) == "mesh":
                normal = cmds.polyNormalPerVertex(sel[0], q=True, xyz=True)[:3]
                for i, field in enumerate(self.normal_fields):
                    field.setText(f"{normal[i]:.5g}")  # Use g format, display 5 significant digits
            elif cmds.objectType(sel[0]) == "meshFace":
                normal = self.get_face_normal(sel[0])
                for i, field in enumerate(self.normal_fields):
                    field.setText(f"{normal[i]:.5g}")  # Use g format, display up to 5 significant digits
            else:
                cmds.warning("Please select a vertex or face!")
        else:
            cmds.warning("No object selected!")

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
            cmds.warning("No object selected!")

    def get_mesh(self):
        sel = cmds.ls(sl=True)
        if sel:
            self.mesh_name_field.setText(sel[0])
        else:
            cmds.warning("No object selected!")

    def set_normal(self):
        source_name = self.mesh_name_field.text()
        if source_name:
            sel = cmds.ls(sl=True)
            for s in sel:
                cmds.transferAttributes(source_name, s, transferNormals=1)
                cmds.delete(s, ch=True)
        else:
            cmds.warning("Please get the normal first!")

    def flatten(self, axis_index):
        """
        Flatten function: Set the normal component of selected vertices to 0 on the specified axis
        
        :param axis_index: Index of the axis to flatten (0=X, 1=Y, 2=Z)
        """
        axes = ["x", "y", "z"]
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            for s in sel:
                # Get current normal
                n = cmds.polyNormalPerVertex(s, q=True, xyz=True)[:3]
                # Set the component of the specified axis to 0
                n[axis_index] = 0
                # Apply new normal
                cmds.polyNormalPerVertex(s, xyz=n)
            
            # Update display
            for obj in set(s.split('.')[0] for s in sel):
                cmds.polyOptions(obj, point=True)
        else:
            cmds.warning("No object selected!")

    def unlock_normal(self):
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            cmds.polyNormalPerVertex(ufn=True)
        else:
            cmds.warning("No object selected!")

    def lock_normal(self):
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            cmds.polyNormalPerVertex(fn=True)
        else:
            cmds.warning("No object selected!")

    def quick_set_normal(self, index):
        """
        Quick set normal function: Set the normal of selected vertices to the specified world coordinate axis direction
        
        :param index: Index of the normal direction to set (0=+X, 1=+Y, 2=+Z, 3=-X, 4=-Y, 5=-Z)
        """
        axes = [
            (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (-1, 0, 0), (0, -1, 0), (0, 0, -1)
        ]
        normal = axes[index]
        
        sel = cmds.ls(sl=True, fl=True)
        if not sel:
            cmds.warning("No object selected!")
            return

        # Convert selection to vertices
        vertices = cmds.polyListComponentConversion(sel, tv=True)
        vertices = cmds.filterExpand(vertices, sm=31)  # sm=31 represents vertices

        if not vertices:
            cmds.warning("Unable to get vertices!")
            return

        # Set normal
        for vertex in vertices:
            cmds.polyNormalPerVertex(vertex, xyz=normal)

        # Update display
        affected_objects = set(vert.split('.')[0] for vert in vertices)
        for obj in affected_objects:
            cmds.polyOptions(obj, point=True)

        cmds.select(sel, r=True)  # Restore original selection
        cmds.inViewMessage(amg='Normal set completed', pos='midCenter', fade=True)

    def average_normals(self):
        """
        Average the normals of selected vertices
        """
        sel = cmds.ls(sl=True, fl=True)
        if sel:
            # Convert selection to vertices
            vertices = cmds.polyListComponentConversion(sel, tv=True)
            vertices = cmds.filterExpand(vertices, sm=31)  # sm=31 represents vertices
            
            if not vertices:
                cmds.warning("Unable to get vertices!")
                return
            
            # Check if normals are locked, if so, unlock them
            for vertex in vertices:
                if cmds.polyNormalPerVertex(vertex, q=True, freezeNormal=True):
                    cmds.polyNormalPerVertex(vertex, ufn=True)
            
            # Use polyAverageNormal command
            cmds.polyAverageNormal(vertices)
            cmds.inViewMessage(amg='Normals averaged', pos='midCenter', fade=True)
        else:
            cmds.warning("No object selected!")

def show_ui():
    window_name = "VertsNormalUIWindow"
    if cmds.window(window_name, exists=True):
        # Get current window position
        existing_window = QtWidgets.QApplication.activeWindow()
        pos = existing_window.pos()
        # Close existing window
        cmds.deleteUI(window_name)
    else:
        # If window doesn't exist, set default position
        pos = QtCore.QPoint(200, 200)
    
    ui = VertsNormalUI()
    ui.setObjectName(window_name)
    
    # Set window position
    ui.move(pos)
    
    ui.show()

if __name__ == "__main__":
    show_ui()
