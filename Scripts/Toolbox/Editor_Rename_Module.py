# Editor_Rename_Module.py
# 包含高级重命名功能的UI和相关函数

import re
import maya.cmds as cmds
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui


#======UI按钮组件======

class RoundedButton(QtWidgets.QPushButton):
    """
    自定义圆角按钮类
    
    特性:
    - 圆角设计
    - 自定义颜色和悬停效果
    - 粗体文字
    """
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

class Editor_Rename_Module_UI(QtWidgets.QWidget):
    """
    高级重命名工具的主UI类
    
    功能:
    - 创建和管理UI组件
    - 处理用户交互
    - 执行重命名操作
    """
    def __init__(self, parent=None):
        super(Editor_Rename_Module_UI, self).__init__(parent)
        self.setWindowTitle("Rename Module")
        
        # 设置窗口宽度
        self.setFixedWidth(300)  # 将宽度设置为300像素
        
        # 设置窗口图标

        self.setWindowIcon(QtGui.QIcon(":quickRename.png"))
        
        # 设置窗口标志，使其始终置顶
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)    
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

#======UI组件======

    def create_widgets(self):
        """
        创建所有UI组件
        
        包括:
        - 选择所有按钮
        - 重命名和编号组
        - 删除字符组
        - 前缀后缀组
        - 搜索和替换组
        """
        # 选择所有按钮
        self.select_all_btn = RoundedButton("Select All")

        # 重命名和编号组
        self.rename_group = QtWidgets.QGroupBox("Rename and Number")
        self.rename_field = QtWidgets.QLineEdit()
        self.rename_field.setPlaceholderText("Enter new name")
        self.start_value_field = QtWidgets.QLineEdit("1")
        self.padding_value_field = QtWidgets.QLineEdit("2")
        self.number_check = QtWidgets.QButtonGroup()
        self.number_radio = QtWidgets.QRadioButton("Numbers")
        self.letter_radio = QtWidgets.QRadioButton("Letters")
        self.number_check.addButton(self.number_radio)
        self.number_check.addButton(self.letter_radio)
        self.number_radio.setChecked(True)
        self.rename_number_btn = RoundedButton("Rename and Sort")

        # 删除字符组
        self.remove_group = QtWidgets.QGroupBox("Remove Characters")
        self.remove_first_btn = RoundedButton("Remove First")
        self.remove_last_btn = RoundedButton("Remove Last")
        self.remove_pasted_btn = RoundedButton("Remove pasted__")
        self.remove_first_field = QtWidgets.QLineEdit("0")
        self.remove_end_field = QtWidgets.QLineEdit("3")
        self.remove_begin_btn = self.create_small_button("-")
        self.remove_all_btn = RoundedButton("Remove")
        self.remove_end_btn = self.create_small_button("-")

        # 前缀后缀组
        self.prefix_suffix_group = QtWidgets.QGroupBox("Prefix and Suffix")
        self.prefix_field = QtWidgets.QLineEdit("prefix_")
        self.suffix_field = QtWidgets.QLineEdit("_suffix")
        self.add_prefix_btn = RoundedButton("Add Prefix")
        self.add_suffix_btn = RoundedButton("Add Suffix")

        # 搜索和替换组
        self.search_replace_group = QtWidgets.QGroupBox("Search and Replace")
        self.search_field = QtWidgets.QLineEdit()
        self.replace_field = QtWidgets.QLineEdit()
        self.sr_check = QtWidgets.QButtonGroup()
        self.sr_selected = QtWidgets.QRadioButton("Selected")
        self.sr_hierarchy = QtWidgets.QRadioButton("Hierarchy")
        self.sr_all = QtWidgets.QRadioButton("All")
        self.sr_check.addButton(self.sr_selected, 0)
        self.sr_check.addButton(self.sr_hierarchy, 1)
        self.sr_check.addButton(self.sr_all, 2)
        self.sr_selected.setChecked(True)
        self.sr_apply_btn = RoundedButton("Apply")


#======UI布局======

    def create_layouts(self):
        """
        创建和设置UI布局
        
        布局包括:
        - 主布局
        - 重命名和编号布局
        - 删除字符布局
        - 前缀后缀布局
        - 搜索和替换布局
        """
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(7)
        main_layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(self.select_all_btn)

        # 重命名和编号布局
        rename_layout = QtWidgets.QGridLayout()
        rename_layout.addWidget(QtWidgets.QLabel("Rename:"), 0, 0)
        rename_layout.addWidget(self.rename_field, 0, 1, 1, 3)
        rename_layout.addWidget(QtWidgets.QLabel("Start:"), 1, 0)
        rename_layout.addWidget(self.start_value_field, 1, 1)
        rename_layout.addWidget(QtWidgets.QLabel("Padding:"), 1, 2)
        rename_layout.addWidget(self.padding_value_field, 1, 3)
        rename_layout.addWidget(self.number_radio, 2, 0, 1, 2)
        rename_layout.addWidget(self.letter_radio, 2, 2, 1, 2)
        rename_layout.addWidget(self.rename_number_btn, 3, 0, 1, 4)
        self.rename_group.setLayout(rename_layout)
        main_layout.addWidget(self.rename_group)

        # 删除字符布局
        remove_layout = QtWidgets.QGridLayout()
        remove_layout.addWidget(self.remove_first_btn, 0, 0, 1,2)
        remove_layout.addWidget(self.remove_last_btn, 0, 3, 1, 3)
        remove_layout.addWidget(self.remove_pasted_btn, 1, 0, 1, 5)
        remove_layout.addWidget(self.remove_first_field, 2, 0, 1, 1)
        remove_layout.addWidget(self.remove_begin_btn, 2, 1, 1, 1)
        remove_layout.addWidget(self.remove_all_btn, 2, 2, 1, 1)
        remove_layout.addWidget(self.remove_end_btn, 2, 3, 1, 1)
        remove_layout.addWidget(self.remove_end_field, 2, 4, 1, 1)
        self.remove_group.setLayout(remove_layout)
        main_layout.addWidget(self.remove_group)

        # 前缀后缀布局
        prefix_suffix_layout = QtWidgets.QGridLayout()
        prefix_suffix_layout.addWidget(QtWidgets.QLabel("Prefix:"), 0, 0)
        prefix_suffix_layout.addWidget(self.prefix_field, 0, 1)
        prefix_suffix_layout.addWidget(self.add_prefix_btn, 0, 2)
        prefix_suffix_layout.addWidget(QtWidgets.QLabel("Suffix:"), 1, 0)
        prefix_suffix_layout.addWidget(self.suffix_field, 1, 1)
        prefix_suffix_layout.addWidget(self.add_suffix_btn, 1, 2)
        self.prefix_suffix_group.setLayout(prefix_suffix_layout)
        main_layout.addWidget(self.prefix_suffix_group)

        # 搜索和替换布局
        sr_layout = QtWidgets.QVBoxLayout()
        sr_input_layout = QtWidgets.QGridLayout()
        sr_input_layout.addWidget(QtWidgets.QLabel("Search:"), 0, 0)
        sr_input_layout.addWidget(self.search_field, 0, 1)
        sr_input_layout.addWidget(QtWidgets.QLabel("Replace:"), 1, 0)
        sr_input_layout.addWidget(self.replace_field, 1, 1)
        sr_layout.addLayout(sr_input_layout)

        # 创建一个水平布局来居中放置单选按钮
        sr_radio_layout = QtWidgets.QHBoxLayout()
        sr_radio_layout.addStretch()
        sr_radio_layout.addWidget(self.sr_selected)
        sr_radio_layout.addWidget(self.sr_hierarchy)
        sr_radio_layout.addWidget(self.sr_all)
        sr_radio_layout.addStretch()
        sr_layout.addLayout(sr_radio_layout)

        sr_layout.addWidget(self.sr_apply_btn)
        self.search_replace_group.setLayout(sr_layout)
        main_layout.addWidget(self.search_replace_group)

#======UI与功能的连接======

    def create_connections(self):
        """
        将UI组件与相应的功能函数连接
        """
        self.select_all_btn.clicked.connect(self.select_all)
        self.rename_number_btn.clicked.connect(self.rename_with_number)
        self.remove_first_btn.clicked.connect(partial(self.remove_first_or_last_char, True))
        self.remove_last_btn.clicked.connect(partial(self.remove_first_or_last_char, False))
        self.remove_pasted_btn.clicked.connect(self.remove_pasted)
        self.remove_begin_btn.clicked.connect(partial(self.remove_chars, "begin"))
        self.remove_all_btn.clicked.connect(partial(self.remove_chars, "all"))
        self.remove_end_btn.clicked.connect(partial(self.remove_chars, "end"))
        self.add_prefix_btn.clicked.connect(partial(self.add_prefix_or_suffix, False))
        self.add_suffix_btn.clicked.connect(partial(self.add_prefix_or_suffix, True))
        self.sr_apply_btn.clicked.connect(self.search_and_replace)

    def select_all(self):
        """选择场景中的所有对象"""
        cmds.select(ado=True, hi=True)

    def rename_with_number(self):
        """
        根据用户输入重命名选中的对象
        
        功能:
        - 获取用户输入的新名称、起始数字和填充位数
        - 调用 _rename_with_number 方法执行重命名
        """
        new_name = self.rename_field.text()
        start_number = int(self.start_value_field.text())
        padding = int(self.padding_value_field.text())
        use_numbers = self.number_radio.isChecked()
        self._rename_with_number(new_name, start_number, padding, use_numbers)

    def _rename_with_number(self, new_name, start_number, padding, use_numbers):
        """
        使用数字或字母重命名对象
        
        参数:
        new_name (str): 新的基础名称
        start_number (int): 起始数字
        padding (int): 数字填充位数
        use_numbers (bool): 是否使用数字（False则使用字母）
        
        功能:
        - 为选中的对象添加递增的数字或字母后缀
        - 使用 sanitize_name 方法确保名称有效
        """
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            cmds.warning("没有选择对象")
            return

        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i, obj in enumerate(selection):
            if use_numbers:
                suffix = str(start_number + i).zfill(padding)
            else:
                suffix = letters[i % 26] * (1 + i // 26)
            new_obj_name = self.sanitize_name(f"{new_name}_{suffix}")
            try:
                cmds.rename(obj, new_obj_name)
            except RuntimeError as e:
                cmds.warning(f"无法重命名 {obj}: {str(e)}")

    def remove_chars(self, remove_type):
        """
        从对象名称中删除指定范围的字符
        
        参数:
        remove_type (str): 删除类型（"begin", "end", "all"）
        
        功能:
        - 根据用户输入的起始和结束位置删除字符
        - 使用 sanitize_name 方法确保新名称有效
        """
        start = int(self.remove_first_field.text())
        end = int(self.remove_end_field.text())
        selection = cmds.ls(selection=True)
        for obj in selection:
            if remove_type == "begin":
                new_name = obj[start:]
            elif remove_type == "end":
                new_name = obj[:-end] if end > 0 else obj
            else:  # "all"
                new_name = obj[start:-end] if end > 0 else obj[start:]
            new_name = self.sanitize_name(new_name)
            try:
                cmds.rename(obj, new_name)
            except RuntimeError as e:
                cmds.warning(f"无法重命名 {obj}: {str(e)}")

    def search_and_replace(self):
        """
        在对象名称中搜索和替换文本
        
        功能:
        - 获取用户输入的搜索文本和替换文本
        - 确定搜索范围（选择、层级或全部）
        - 调用 _search_and_replace 方法执行替换
        """
        search_text = self.search_field.text()
        replace_text = self.replace_field.text()
        search_method = self.sr_check.checkedId()
        self._search_and_replace(search_text, replace_text, search_method)

    def _search_and_replace(self, search_text, replace_text, search_method):
        """
        执行搜索和替换操作
        
        参数:
        search_text (str): 要搜索的文本
        replace_text (str): 替换文本
        search_method (int): 搜索方法（0:选择, 1:层级, 2:全部）
        
        功能:
        - 根据搜索方法选择对象
        - 在对象名称中搜索和替换���本
        - 使用 sanitize_name 方法确保新名称有效
        - 递归处理层级中的所有子对象
        """
        def rename_recursive(obj_list):
            renamed_objects = []
            for obj in obj_list:
                # 检查对象是否仍然存在
                if not cmds.objExists(obj):
                    continue
                
                # 获取对象的短名称
                short_name = obj.split('|')[-1]
                
                # 跳过形状节点
                if cmds.objectType(obj) == "shape":
                    continue
                
                if search_text in short_name:
                    new_name = self.sanitize_name(short_name.replace(search_text, replace_text))
                    try:
                        renamed = cmds.rename(obj, new_name)
                        renamed_objects.append(renamed)
                        obj = renamed  # 更新对象的路径名称
                    except RuntimeError as e:
                        cmds.warning(f"无法重命名 {obj}: {str(e)}")
                
                # 递归处理子对象
                children = cmds.listRelatives(obj, children=True, fullPath=True) or []
                renamed_objects.extend(rename_recursive(children))
            
            return renamed_objects

        if search_method == 0:  # 选择
            selection = cmds.ls(selection=True, long=True)
        elif search_method == 1:  # 层级
            selection = cmds.ls(selection=True, dag=True, long=True)
        else:  # All
            selection = cmds.ls(dag=True, long=True)

        renamed_objects = rename_recursive(selection)

        # 更新选择（如果有重命名的对象）
        if renamed_objects:
            cmds.select(renamed_objects, replace=True)
        else:
            cmds.select(clear=True)

        cmds.inViewMessage(amg=f'<span style="color:#fbca82;">已重命名 {len(renamed_objects)} 个对象</span>', pos='botRight', fade=True)

    def create_small_button(self, text):
        """
        创建一个小型按钮
        
        参数:
        text (str): 按钮文本
        
        返回:
        QPushButton: 创建的小型按钮
        """
        btn = QtWidgets.QPushButton(text)
        btn.setFixedSize(20, 20)
        return btn

    def add_prefix_or_suffix(self, is_suffix):
        """
        为选中的对象添加前缀或后缀
        
        参数:
        is_suffix (bool): 如果为True，则添加后缀；如果为False，则添加前缀
        
        功能:
        - 获取用户输入的前缀或后缀文本
        - 为选中的对象添加前缀或后缀
        - 使用 sanitize_name 方法确保新名称有效
        - 只处理对象的短名称，不影响其在层级中的位置
        """
        text = self.suffix_field.text() if is_suffix else self.prefix_field.text()
        selection = cmds.ls(selection=True, long=True)
        renamed_objects = []
        for obj in selection:
            # 获取对象的短名称
            short_name = obj.split('|')[-1]
            # 创建新名称
            new_name = self.sanitize_name(f"{short_name}{text}" if is_suffix else f"{text}{short_name}")
            try:
                # 使用长名称进行重命名，但只更改最后一部分
                renamed = cmds.rename(obj, new_name)
                renamed_objects.append(renamed)
            except RuntimeError as e:
                cmds.warning(f"无法重命名 {short_name}: {str(e)}")

        # 更新选择
        if renamed_objects:
            cmds.select(renamed_objects, replace=True)
        else:
            cmds.select(clear=True)

        # 显示操作完成的消息
        cmds.inViewMessage(amg=f'<span style="color:#fbca82;">已添加{"后缀" if is_suffix else "前缀"}: {text}</span>', pos='botRight', fade=True)

    def remove_first_or_last_char(self, remove_first):
        """
        删除对象名称的第一个或最后一个字符
        
        参数:
        remove_first (bool): 如果为True，则删除第一个字符；如果为False，则删除最后一个字符
        
        功能:
        - 从选中对象的名称中删除指定位置的字符
        - 使用 sanitize_name 方法确保新名称有效
        """
        selection = cmds.ls(selection=True)
        for obj in selection:
            new_name = obj[1:] if remove_first else obj[:-1]
            new_name = self.sanitize_name(new_name)
            try:
                cmds.rename(obj, new_name)
            except RuntimeError as e:
                cmds.warning(f"无法重命名 {obj}: {str(e)}")

    def remove_pasted(self):
        """
        删除对象名称中的'pasted__'前缀
        
        功能:
        - 处理变换节点和形状节点
        - 移除'pasted__'前缀
        - 使用 sanitize_name 方法确保新名称有效
        """
        # 首先处理变换节点
        transform_nodes = cmds.ls("pasted__*", long=True, transforms=True)
        for obj in transform_nodes:
            new_name = self.sanitize_name(obj.split("|")[-1][8:])  # Remove "pasted__" prefix
            try:
                cmds.rename(obj, new_name)
            except RuntimeError as e:
                cmds.warning(f"无法重命名变换节点 {obj}: {str(e)}")
        
        # 然后处理形状节点
        shape_nodes = cmds.ls("pasted__*", long=True, shapes=True)
        for shape in shape_nodes:
            parent = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
            parent_name = cmds.ls(parent, shortNames=True)[0]
            new_shape_name = f"{parent_name}Shape"
            try:
                cmds.rename(shape, new_shape_name)
            except RuntimeError as e:
                cmds.warning(f"无法重命名形状节点 {shape}: {str(e)}")

    @staticmethod
    def sanitize_name(name):
        """
        清理和验证对象名称
        
        参数:
        name (str): 需要清理的名称
        
        返回:
        str: 清理后的名称
        
        功能:
        - 替换非法字符
        - 确保名称不以数字开头
        - 返回有效的Maya对象名称
        """
        name = name.replace(':', '_')
        name = re.sub(r'[^\w|]', '_', name)
        if name[0].isdigit():
            name = '_' + name
        return name



#======功能======

def test_duplicate_name(obj_name):
    """
    测试是否有重复的名称
    
    参数:
    obj_name (str): 要测试的对象名称
    
    返回:
    str: 对象的短名称
    
    功能:
    - 从完整路径中提取对象的短名称
    - 处理可能的异常情况
    """
    try:
        return obj_name.split("|")[-1]
    except:
        return obj_name
    




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
    
    rename_window_ui = Editor_Rename_Module_UI()
    rename_window_ui.show()  # 修正缩进


if __name__ == "__main__":
    show()












