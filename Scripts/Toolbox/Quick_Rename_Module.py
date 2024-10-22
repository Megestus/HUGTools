# Quick_Rename_Module.py
# 包含自定义层相关的UI和功能函数

import re
import maya.cmds as cmds
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui


#======UI按钮组件======

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

#======UI主窗口组件======

class Quick_Rename_Module_UI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Quick_Rename_Module_UI, self).__init__(parent)
        self.setWindowTitle("Quick_Rename_Module")
        self.setMinimumWidth(280)
        
        # 设置窗口图标
        self.setWindowIcon(QtGui.QIcon(":annotation.png"))

        # 设置窗口标志，使其始终置顶
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

#======UI组件======

    def create_widgets(self):

        # 快速前缀后缀组
        self.quick_prefix_suffix_group = QtWidgets.QGroupBox("Quickuffix")
        self.quick_prefix_suffix_btns = [
            # RoundedButton("SM_"),
            RoundedButton("_La"),
            RoundedButton("_Lb"),
            RoundedButton("_Hi"),
            RoundedButton("_Temp")
        ]

        # 快速打组选项组
        self.quick_group_group = QtWidgets.QGroupBox("QuickGroup")
        self.quick_group_buttons = [
            RoundedButton("La_mesh"),
            RoundedButton("Lb_mesh"),
            RoundedButton("Hires"),
            RoundedButton("Retopo"),
            RoundedButton("temp_mesh"),
            RoundedButton("Concept")
        ]

        # 快速显示层选项组
        self.quick_layer_group = QtWidgets.QGroupBox("QuickLayer")
        self.quick_layer_buttons = [
            RoundedButton("La"),
            RoundedButton("Lb"),
            RoundedButton("Hi"),
            RoundedButton("RetopoMesh"),
            RoundedButton("Temp"),
            RoundedButton("Mesh")
        ]

#======UI布局======

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Quick_Prefix_Suffix 布局
        quick_prefix_suffix_layout = QtWidgets.QGridLayout()
        for i, btn in enumerate(self.quick_prefix_suffix_btns):
            quick_prefix_suffix_layout.addWidget(btn, i // 3, i % 3)
        self.quick_prefix_suffix_group.setLayout(quick_prefix_suffix_layout)
        main_layout.addWidget(self.quick_prefix_suffix_group)
        
        # QuickGroup布局
        quick_group_layout = QtWidgets.QVBoxLayout()
        quick_group_buttons_layout = QtWidgets.QGridLayout()
        
        for i, btn in enumerate(self.quick_group_buttons):
            row = i // 3
            col = i % 3
            quick_group_buttons_layout.addWidget(btn, row, col)
        
        quick_group_layout.addLayout(quick_group_buttons_layout)
        self.quick_group_group.setLayout(quick_group_layout)
        
        # QuickLayer布局
        quick_layer_layout = QtWidgets.QVBoxLayout()
        quick_layer_buttons_layout = QtWidgets.QGridLayout()
        
        for i, btn in enumerate(self.quick_layer_buttons):
            row = i // 3
            col = i % 3
            quick_layer_buttons_layout.addWidget(btn, row, col)
        
        quick_layer_layout.addLayout(quick_layer_buttons_layout)
        self.quick_layer_group.setLayout(quick_layer_layout)
        
        # 将两个选项组添加到主布局
        main_layout.addWidget(self.quick_group_group)
        main_layout.addWidget(self.quick_layer_group)

#======UI与功能的连接======

    def create_connections(self):
        # 为QuickGroup按钮添加连接
        for btn in self.quick_group_buttons:
            btn.clicked.connect(partial(create_group, btn.text()))
        
        # 为QuickLayer按钮添加连接
        for btn in self.quick_layer_buttons:
            btn.clicked.connect(partial(create_display_layer_group, btn.text()))
        
        # 为快速前缀后缀按钮添加连接
        for btn in self.quick_prefix_suffix_btns:
            text = btn.text()
            if text.startswith("_"):  # 如果以下划线开头，认为是后缀
                btn.clicked.connect(partial(add_prefix_or_suffix, text, True))
            else:  # 否则认为是前缀
                btn.clicked.connect(partial(add_prefix_or_suffix, text, False))

#======功能======

def add_prefix_or_suffix(text, is_suffix):
    """
    为选中的对象添加前缀或后缀
    
    参数:
    text (str): 要添加的前缀或后缀文本
    is_suffix (bool): 如果为True，则添加后缀；如果为False，则添加前缀
    
    功能:
    - 检查是否有选中的对象
    - 为每个选中的对象添加指定的前缀或后缀
    - 使用sanitize_name函数清理新名称
    - 尝试重命名对象，如果失败则显示警告
    - 操作完成后在Maya视图中显示提示信息
    """
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("没有选择对象")
        return
    for obj in selection:
        new_name = f"{obj}{text}" if is_suffix else f"{text}{obj}"
        new_name = sanitize_name(new_name)
        try:
            cmds.rename(obj, new_name)
        except RuntimeError as e:
            cmds.warning(f"无法重命名 {obj}: {str(e)}")
    cmds.inViewMessage(amg=f'<span style="color:#fbca82;">已添加{"后缀" if is_suffix else "前缀"}: {text}</span>', pos='botRight', fade=True)


def create_group(group_name):
    """
    创建一个新组并将选中的对象放入其中
    
    参数:
    group_name (str): 新创建组的名称
    
    功能:
    - 检查是否有选中的对象
    - 使用sanitize_name函数清理组名
    - 创建一个新的空组
    - 将选中的对象放入新创建的组中
    - 操作完成后在Maya视图中显示提示信息
    """
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("没有选择对象")
        return
    group_name = sanitize_name(group_name)
    group = cmds.group(name=group_name, empty=True)
    cmds.parent(selection, group)
    cmds.inViewMessage(amg=f'<span style="color:#fbca82;">创建组: {group_name}</span>', pos='botRight', fade=True)

def create_display_layer_group(layer_name=None):
    """
    创建一个新的显示层并将选中的对象添加到该层
    
    参数:
    layer_name (str, 可选): 新创建显示层的名称。如果未提供，将自动生成一个名称。
    
    功能:
    - 获取当前选中的对象
    - 如果未提供层名，则自动生成一个
    - 创建一个新的空显示层
    - 如果有选中的对象，将它们添加到新创建的显示层中
    - 保持原有的对象选择状态
    - 操作完成后在Maya视图中显示提示信息
    """
    selection = cmds.ls(selection=True)
    
    if not layer_name:
        layer_name = f"CustomLayer_{len(cmds.ls(type='displayLayer'))}"
    
    new_layer = cmds.createDisplayLayer(name=layer_name, empty=True)
    
    if selection:
        cmds.editDisplayLayerMembers(new_layer, selection)
        cmds.select(selection)  # 保持原有选择
    
    cmds.inViewMessage(amg=f'<span style="color:#fbca82;">创建显示层: {layer_name}</span>', pos='botRight', fade=True)

def sanitize_name(name):
    """
    清理和验证对象名称
    
    参数:
    name (str): 需要清理的名称
    
    返回:
    str: 清理后的名称
    
    功能:
    - 对输入的名称进行清理和验证
    - 确保名称符合Maya的命名规则
    - 可以在这里添加自定义的名称清理逻辑
    
    注意: 当前函数只是返回原名称，您可以根据需要添加具体的清理逻辑
    """
    # 这里可以添加名称清理的逻辑，如果需要的话
    return name

#======UI函数======

def show():
    """
    显示编辑器重命名模块的UI
    
    功能:
    - 关闭并删除现有的UI实例（如果存在）
    - 创建新的UI实例并显示
    """
    global rename_window_ui
    try:
        rename_window_ui.close()
        rename_window_ui.deleteLater()
    except:
        pass
    
    rename_window_ui = Quick_Rename_Module_UI()
    rename_window_ui.show()  # 修正缩进


if __name__ == "__main__":
    show()




