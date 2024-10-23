from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial
import importlib
import sys
import os
import maya.cmds as cmds
import traceback
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

# ----------------------
# Custom Widgets
# ----------------------

class ModItButton(QtWidgets.QPushButton):
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

# ----------------------
# Main Window Class
# ----------------------

class MoreToolsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MoreToolsWindow, self).__init__(parent)
        self.setWindowTitle("More Tools")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        
        self.tool_config = {
            "Modeling": [
                {"name": "Tool 1", "icon": "mao.png"},
                {"name": "Tool 2", "icon": "boxuemao.png"},
                {"name": "Tool 3", "icon": "sanhuamao.png"},
                {"name": "Tool 4", "icon": "xianluomao.png"},
            ],
            "Rigging": [
                {"name": "Tool 5", "icon": "tianyuanmao.png"},
                {"name": "Tool 6", "icon": "sanhuamao.png"},
                {"name": "Tool 7", "icon": "mimiyanmao.png"},
                {"name": "Tool 8", "icon": "heimao.png"},
            ],
        }
        self.init_ui()

    # ----------------------
    # UI Initialization
    # ----------------------

    def init_ui(self):
        self.create_widgets()
        self.create_layout()
        self.setup_connections()
        self.set_styles()

    def create_widgets(self):
        self.create_title_bar()
        self.create_tab_widget()
        self.create_tool_buttons()

    def create_title_bar(self):
        self.title_bar = QtWidgets.QWidget(self)
        self.title_bar.setFixedHeight(30)
        self.title_label = QtWidgets.QLabel("More Tools", self.title_bar)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #CCCCCC;")
        self.close_button = QtWidgets.QPushButton("×", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
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

    def create_tab_widget(self):
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555555;
                background: #3C3C3C;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: transparent;
                border: none;
                padding: 5px;
                margin-right: 5px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #4B4B4B;
            }
        """)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "Icons")
        modeling_icon = QtGui.QIcon(os.path.join(icon_path, "Modeling.png"))
        rigging_icon = QtGui.QIcon(os.path.join(icon_path, "screenshot.png"))
        
        self.modeling_tab = QtWidgets.QWidget()
        self.rigging_tab = QtWidgets.QWidget()
        
        # Set larger icon size
        icon_size = QtCore.QSize(32, 32)  # Adjust size as needed
        self.tab_widget.setIconSize(icon_size)
        
        self.tab_widget.addTab(self.modeling_tab, modeling_icon, "")
        self.tab_widget.addTab(self.rigging_tab, rigging_icon, "")
        
        # Set tooltips
        self.tab_widget.setTabToolTip(0, "Modeling")
        self.tab_widget.setTabToolTip(1, "Rigging")

    def create_tool_buttons(self):
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "Icons")
        for i, (category, tools) in enumerate(self.tool_config.items()):
            tab = self.tab_widget.widget(i)
            tab_layout = QtWidgets.QVBoxLayout(tab)
            tab_layout.setSpacing(10)
            tab_layout.setContentsMargins(10, 10, 10, 10)
            
            grid_layout = QtWidgets.QGridLayout()
            grid_layout.setSpacing(10)
            
            for j, tool in enumerate(tools):
                icon = QtGui.QIcon(os.path.join(icon_path, tool["icon"]))
                button = ModItButton(tool["name"], icon)
                button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                button.setMinimumSize(100, 40)
                button.clicked.connect(lambda checked=False, name=tool["name"]: self.tool_clicked(name))
                row = j // 2
                col = j % 2
                grid_layout.addWidget(button, row, col)
            
            tab_layout.addLayout(grid_layout)
            tab_layout.addStretch()

    def create_layout(self):
        self.create_title_bar_layout()
        self.create_main_layout()

    def create_title_bar_layout(self):
        title_layout = QtWidgets.QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_button)

    def create_main_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.tab_widget)

    def setup_connections(self):
        self.close_button.clicked.connect(self.close)

    def set_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #3C3C3C;
                border: none;
            }
            QLabel {
                color: #CCCCCC;
            }
        """)

    # ----------------------
    # Event Handling
    # ----------------------

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def tool_clicked(self, tool_name):
        message = f'<span style="color:#FFA500;">{tool_name} - In development</span>'
        cmds.inViewMessage(amg=message, pos='botRight', fade=True, fst=10, fad=1)

# ----------------------
# Global Functions
# ----------------------

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def show():
    global more_tools_window
    try:
        more_tools_window.close()
        more_tools_window.deleteLater()
    except:
        pass
    parent = maya_main_window()
    more_tools_window = MoreToolsWindow(parent)
    more_tools_window.show()
    more_tools_window.raise_()
    more_tools_window.activateWindow()

if __name__ == "__main__":
    show()
