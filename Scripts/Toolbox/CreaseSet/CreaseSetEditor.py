import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import re

def get_maya_main_window():
    """获取Maya主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class CreaseSetEditor(QtWidgets.QDialog):
    """CreaseSet编辑器"""

    # 定义语言字典作为类的静态变量
    language_dict = {
        "en": {
            "window_title": "CreaseSet Clean",
            "crease_set_list": "CreaseSet Node List",
            "crease_set_level": "level",
            "crease_set_EdgeNumber": "Edge N",
            "quick_execute": "Quick Execute",
            "quick_set_btn": "Quick Set Crease Level",
            "select_edges_btn": "Select CreaseSet Edges to Soft/Hard Edge",
            "prefix_merge_btn": "Merge by Prefix",
            "prefix_rename_btn": "Rename by Prefix",
            "split_crease_set_btn": "Split CreaseSet",
            "clean_crease_set_btn": "Clean CreaseSet",
            "toggle_lang_tip": "Switch to Chinese",
            "quick_set_tip": "Quickly set the crease level for all CreaseSets in the list",
            "select_edges_tip": "Select all edges associated with the selected CreaseSet",
            "prefix_merge_tip": "Merge selected CreaseSets into one based on prefix, default is _M, In addition, recognizes _Lb and _Lc",
            "prefix_rename_tip": "Rename selected CreaseSets based on object prefix, default is _R, In addition, recognizes _Lb and _Lc",
            "split_crease_set_tip": "Split selected CreaseSet into multiple sets by object",
            "clean_crease_set_tip": "Remove CreaseSets that have no members"
        },
        "zh": {
            "window_title": "CreaseSet 清理",
            "crease_set_list": "CreaseSet 节点列表",
            "crease_set_level": "折痕级别",
            "crease_set_EdgeNumber": "边数量",
            "quick_execute": "快捷执行",
            "quick_set_btn": "一键设置折痕级别",
            "select_edges_btn": "选择CreaseSet边进行软硬边",
            "prefix_merge_btn": "根据前缀合并",
            "prefix_rename_btn": "根据前缀重命名",
            "split_crease_set_btn": "拆分CreaseSet",
            "clean_crease_set_btn": "清理CreaseSet",
            "toggle_lang_tip": "切换到英文",
            "quick_set_tip": "快速设置列表中所有CreaseSet的折痕级别",
            "select_edges_tip": "选择与选定CreaseSet相关的所有边",
            "prefix_merge_tip": "根据前缀合并选定的CreaseSet，默认是_M，另外，还能识别Lb和Lc",
            "prefix_rename_tip": "根据对象前缀重命名选定的CreaseSet，默认是_R，另外，还能识别Lb和Lc",
            "split_crease_set_tip": "按对象将选定的CreaseSet拆分为多个",
            "clean_crease_set_tip": "删除没有成员的CreaseSet"
        }
    }

    def __init__(self, parent=None, language="en"):
        super(CreaseSetEditor, self).__init__(parent or get_maya_main_window())
        
        self.language = language
        self.setWindowTitle(self.language_dict[self.language]["window_title"])
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setFixedSize(300, 500)
        self.setObjectName('creaseSetEditor')
        
        self.selection_callback = None
        self.create_ui()

    def create_ui(self):
        """创建UI组件并设置信号和槽"""
        
        # 按钮样式
        button_style = """
            QPushButton {
                background-color: #D0D0D0;
                border: none;
                border-radius: 4px;
                padding: 5px;
                color: black;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
        """

        # 切换语言按钮样式
        toggle_button_style = """
            QPushButton {
                background-color: transparent; /* 透明背景 */
                border: 1px solid #C0C0C0; /* 边框颜色 */
                border-radius: 20px; /* 圆形按钮 */
                width: 24px;
                height: 24px;
                font-size: 10px;
                color: white;
                position: absolute; /* 固定位置 */
                top: 10px; /* 距离顶部10px */
                right: 10px; /* 距离右侧10px */
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1); /* 悬停时轻微背景 */
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2); /* 按下时轻微背景 */
            }
        """

        main_layout = QtWidgets.QGridLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # 获取语言文本
        lang = self.language_dict[self.language]

        # CreaseSet列表
        crease_set_group = QtWidgets.QGroupBox(lang["crease_set_list"])
        crease_set_layout = QtWidgets.QVBoxLayout(crease_set_group)

        self.crease_set_tree = QtWidgets.QTreeWidget()
        self.crease_set_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.crease_set_tree.setRootIsDecorated(False)
        self.crease_set_tree.setHeaderLabels([lang["crease_set_list"], lang["crease_set_level"], lang["crease_set_EdgeNumber"]])
        self.crease_set_tree.setColumnWidth(0, 140)
        self.crease_set_tree.setColumnWidth(1, 60)
        self.crease_set_tree.setColumnWidth(2, 40)
        self.crease_set_tree.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        crease_set_layout.addWidget(self.crease_set_tree)

        # 一键设置折痕级别
        quick_set_layout = QtWidgets.QHBoxLayout()
        self.quick_set_btn = QtWidgets.QPushButton(lang["quick_set_btn"])
        self.quick_set_btn.setStyleSheet(button_style)
        self.quick_set_btn.setFixedWidth(150)  # 在布局中单独设置按钮宽度
        self.quick_set_btn.setToolTip(lang["quick_set_tip"])  # 设置悬停提示
        self.quick_set_level_spin = QtWidgets.QDoubleSpinBox()
        self.quick_set_level_spin.setRange(0.0, 10.0)
        self.quick_set_level_spin.setSingleStep(0.1)
        self.quick_set_level_spin.setValue(5.0)

        # 添加语言切换按钮
        self.toggle_lang_btn = QtWidgets.QPushButton("CN" if self.language == "en" else "EN")
        self.toggle_lang_btn.setStyleSheet(toggle_button_style)
        self.toggle_lang_btn.setToolTip(self.language_dict[self.language]["toggle_lang_tip"])
        self.toggle_lang_btn.clicked.connect(self.toggle_language)

        quick_set_layout.addWidget(self.quick_set_btn)
        quick_set_layout.addWidget(self.quick_set_level_spin)
        quick_set_layout.addWidget(self.toggle_lang_btn)

        # 将一键设置折痕级别添加到CreaseSet列表布局下方
        crease_set_layout.addLayout(quick_set_layout)

        main_layout.addWidget(crease_set_group, 0, 0, 1, 3)

        # 快捷执行
        quick_exec_group = QtWidgets.QGroupBox(lang["quick_execute"])
        quick_exec_layout = QtWidgets.QGridLayout(quick_exec_group)

        # 添加按钮
        self.select_edges_btn = QtWidgets.QPushButton(lang["select_edges_btn"])
        self.select_edges_btn.setStyleSheet(button_style)
        self.select_edges_btn.setToolTip(lang["select_edges_tip"])  # 设置悬停提示

        self.prefix_merge_btn = QtWidgets.QPushButton(lang["prefix_merge_btn"])
        self.prefix_merge_btn.setStyleSheet(button_style)
        self.prefix_merge_btn.setToolTip(lang["prefix_merge_tip"])  # 设置悬停提示

        self.prefix_rename_btn = QtWidgets.QPushButton(lang["prefix_rename_btn"])
        self.prefix_rename_btn.setStyleSheet(button_style)
        self.prefix_rename_btn.setToolTip(lang["prefix_rename_tip"])  # 设置悬停提示

        self.split_crease_set_btn = QtWidgets.QPushButton(lang["split_crease_set_btn"])
        self.split_crease_set_btn.setStyleSheet(button_style)
        self.split_crease_set_btn.setToolTip(lang["split_crease_set_tip"])  # 设置悬停提示

        self.clean_crease_set_btn = QtWidgets.QPushButton(lang["clean_crease_set_btn"])
        self.clean_crease_set_btn.setStyleSheet(button_style)
        self.clean_crease_set_btn.setToolTip(lang["clean_crease_set_tip"])  # 设置悬停提示

        # 添加到快捷执行布局 (2x2)
        quick_exec_layout.addWidget(self.select_edges_btn, 0, 0, 1, 2)
        quick_exec_layout.addWidget(self.prefix_merge_btn, 1, 0)
        quick_exec_layout.addWidget(self.prefix_rename_btn, 1, 1)
        quick_exec_layout.addWidget(self.split_crease_set_btn, 2, 0)
        quick_exec_layout.addWidget(self.clean_crease_set_btn, 2, 1)  

        main_layout.addWidget(quick_exec_group, 1, 0, 1, 3)

        # 创建右键菜单
        self.crease_set_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.crease_set_tree.customContextMenuRequested.connect(self.show_context_menu)

        # 设置信号和槽
        self.select_edges_btn.clicked.connect(self.select_crease_edges)
        self.quick_set_btn.clicked.connect(self.quick_set_crease_level)
        self.crease_set_tree.itemChanged.connect(self.rename_crease_set)
        self.prefix_merge_btn.clicked.connect(self.prefix_merge_selected_sets)
        self.prefix_rename_btn.clicked.connect(self.prefix_rename_selected_sets)
        self.split_crease_set_btn.clicked.connect(self.split_crease_set_by_object)
        self.clean_crease_set_btn.clicked.connect(self.clean_empty_crease_sets)
        self.add_selection_callback()

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QtWidgets.QMenu()
        action1 = menu.addAction("Action 1")
        action2 = menu.addAction("Action 2")
        action = menu.exec_(self.crease_set_tree.viewport().mapToGlobal(position))
        if action == action1:
            print("Action 1 selected")
        elif action == action2:
            print("Action 2 selected")

    def toggle_language(self):
        """切换语言"""
        self.language = "zh" if self.language == "en" else "en"
        self.setWindowTitle(self.language_dict[self.language]["window_title"])
        self.toggle_lang_btn.setText("CN" if self.language == "en" else "EN")
        self.toggle_lang_btn.setToolTip(self.language_dict[self.language]["toggle_lang_tip"])
        self.update_ui_texts()

    def update_ui_texts(self):
        """更新UI文本"""
        lang = self.language_dict[self.language]
        self.quick_set_btn.setText(lang["quick_set_btn"])
        self.quick_set_btn.setToolTip(lang["quick_set_tip"])  # 更新悬停提示

        self.select_edges_btn.setText(lang["select_edges_btn"])
        self.select_edges_btn.setToolTip(lang["select_edges_tip"])  # 更新悬停提示

        self.prefix_merge_btn.setText(lang["prefix_merge_btn"])
        self.prefix_merge_btn.setToolTip(lang["prefix_merge_tip"])  # 更新悬停提示

        self.prefix_rename_btn.setText(lang["prefix_rename_btn"])
        self.prefix_rename_btn.setToolTip(lang["prefix_rename_tip"])  # 更新悬停提示

        self.split_crease_set_btn.setText(lang["split_crease_set_btn"])
        self.split_crease_set_btn.setToolTip(lang["split_crease_set_tip"])  # 更新悬停提示

        self.clean_crease_set_btn.setText(lang["clean_crease_set_btn"])
        self.clean_crease_set_btn.setToolTip(lang["clean_crease_set_tip"])  # 更新悬停提示

        self.crease_set_tree.setHeaderLabels([lang["crease_set_list"], lang["crease_set_level"], lang["crease_set_EdgeNumber"]])

    def add_selection_callback(self):
        """添加选择变化的回调"""
        self.selection_callback = cmds.scriptJob(
            event=["SelectionChanged", self.refresh_crease_sets],
            protected=True
        )

    def remove_selection_callback(self):
        """移除选择变化的回调"""
        if self.selection_callback is not None:
            cmds.scriptJob(kill=self.selection_callback, force=True)
            self.selection_callback = None

    def get_members_in_crease_set(self, crease_set_name):
        """
        获取指定CreaseSet中的所有边。

        参数:
        crease_set_name (str): CreaseSet的名称

        返回:
        list: CreaseSet中的边列表
        """
        # 检查CreaseSet是否存在
        if not cmds.objExists(crease_set_name):
            cmds.warning(f"CreaseSet '{crease_set_name}' 不存在。")
            return []

        # 获取CreaseSet中的边
        members = cmds.sets(crease_set_name, query=True)

        if members is None:
            cmds.warning(f"CreaseSet '{crease_set_name}' 中没有边。")
            return []

        expanded_members = []
        for member in members:
            if ':' in member:
                # 解析范围
                base, indices = member.split('[')
                start, end = map(int, indices[:-1].split(':'))
                expanded_members.extend([f"{base}[{i}]" for i in range(start, end + 1)])
            else:
                expanded_members.append(member)

        return expanded_members

    def refresh_crease_sets(self):
        """刷新CreaseSet列表"""
        self.crease_set_tree.clear()
        
        # 获取所有CreaseSet节点
        all_crease_sets = cmds.ls(type='objectSet') or []
        
        # 获取当前选定的对象
        selected_objects = cmds.ls(sl=True, long=True)
        selected_object_names = {obj.split("|")[-1] for obj in selected_objects}

        for cs in all_crease_sets:
            try:
                if cmds.attributeQuery('creaseLevel', node=cs, exists=True):
                    # 使用新函数获取CreaseSet的边
                    members = self.get_members_in_crease_set(cs)
                    
                    # 获取折痕级别
                    crease_level = cmds.getAttr(f"{cs}.creaseLevel")
                    
                    # 创建树项
                    item = QtWidgets.QTreeWidgetItem(self.crease_set_tree)
                    item.setText(0, cs)  # 设置名称
                    item.setText(1, f"{crease_level:.2f}")  # 设置折痕级别
                    item.setText(2, str(len(members)))  # 设置边数量
                    item.setData(0, QtCore.Qt.UserRole, cs)  # 存储原始名称

                    # 检查CreaseSet是否与选定对象相关
                    related = any(member.split('.')[0] in selected_object_names for member in members)
                    if related:
                        # 设置背景颜色为灰蓝色
                        item.setBackground(0, QtGui.QBrush(QtGui.QColor("#414d5a")))
                        item.setBackground(1, QtGui.QBrush(QtGui.QColor("#344d5a")))
                        item.setBackground(2, QtGui.QBrush(QtGui.QColor("#414d5a")))

                    # 只允许名称列可编辑
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

            except Exception as e:
                cmds.warning(f"处理CreaseSet {cs} 时出错: {str(e)}")

    def select_crease_edges(self):
        """选择当前CreaseSet中的边并设置硬边/软边"""

        # 获取当前选定的对象
        selected_objects = cmds.ls(sl=True, long=True)
        selected_object_names = {obj.split("|")[-1] for obj in selected_objects}

        # 自动选择与选定对象相关的CreaseSet节点
        if not self.crease_set_tree.selectedItems():
            all_crease_sets = cmds.ls(type='objectSet') or []
            for cs in all_crease_sets:
                if not cmds.attributeQuery('creaseLevel', node=cs, exists=True):
                    continue

                members = cmds.sets(cs, q=True) or []
                related = any(member.split('.')[0] in selected_object_names for member in members)
                if related:
                    # 自动选择相关的CreaseSet节点
                    for i in range(self.crease_set_tree.topLevelItemCount()):
                        item = self.crease_set_tree.topLevelItem(i)
                        if item.data(0, QtCore.Qt.UserRole) == cs:
                            item.setSelected(True)
                            break

        # 继续执行原有逻辑
        selected_items = self.crease_set_tree.selectedItems()
        if not selected_items:
            cmds.inViewMessage(amg='<span style="color:#fbca82;">请先选择CreaseSet节点</span>', pos='botRight', fade=True)
            return

        try:
            cmds.undoInfo(openChunk=True)
            cmds.select(clear=True)
            all_edges_to_select = []

            # 获取所有模型对象
            all_objects = cmds.ls(type='mesh', long=True)
            all_object_edges = cmds.polyListComponentConversion(all_objects, toEdge=True)
            all_object_edges = cmds.ls(all_object_edges, flatten=True)

            # 将所有边设置为软边
            cmds.polySoftEdge(all_object_edges, angle=180, ch=True)

            for item in selected_items:
                crease_set = item.data(0, QtCore.Qt.UserRole)
                all_members = cmds.sets(crease_set, q=True) or []

                # 从成员中提取对象名称并选择相关边
                for member in all_members:
                    obj_name = member.split('.')[0]
                    if ':' in member:
                        # 解析范围
                        base, indices = member.split('[')
                        start, end = map(int, indices[:-1].split(':'))
                        edges = [f"{base}[{i}]" for i in range(start, end + 1)]
                    else:
                        edges = [member]
                    all_edges_to_select.extend(edges)

            if all_edges_to_select:
                cmds.select(all_edges_to_select, replace=True)
                cmds.selectType(edge=True)

                # 打印选中的边
                print("选中的边:", all_edges_to_select)

                # 设置选中边为硬边
                cmds.polySoftEdge(all_edges_to_select, angle=0, ch=True)

            else:
                cmds.inViewMessage(amg='<span style="color:#fbca82;">未找到相关的边</span>', pos='botRight', fade=True)

        except Exception as e:
            cmds.inViewMessage(amg=f'<span style="color:#fbca82;">选择边时出错: {str(e)}</span>', pos='botRight', fade=True)
        finally:
            cmds.undoInfo(closeChunk=True)
            self.refresh_crease_sets()

    def update_crease_level_display(self):
        """更新显示的折痕级别值"""
        selected_items = self.crease_set_tree.selectedItems()
        if len(selected_items) == 1:
            # 如果只选择了一个项目，显示其折痕级别
            crease_set = selected_items[0].data(0, QtCore.Qt.UserRole)
            try:
                level = cmds.getAttr(f"{crease_set}.creaseLevel")
                self.crease_level_spin.setValue(level)
            except Exception as e:
                cmds.warning(f"获取折痕级别失败: {str(e)}")

    def quick_set_crease_level(self):
        """快速设置所有列表中CreaseSet的折痕级别为用户指定的值"""
        root = self.crease_set_tree.invisibleRootItem()
        all_items = []
        for i in range(root.childCount()):
            all_items.append(root.child(i))
        
        if not all_items:
            cmds.inViewMessage(amg='<span style="color:#fbca82;">列表中没有CreaseSet节点</span>', pos='botRight', fade=True)
            return
        
        # 获取用户指定的折痕级别
        new_level = self.quick_set_level_spin.value()
        
        try:
            # 开始撤销块
            cmds.undoInfo(openChunk=True)
            
            # 为列表中的所有CreaseSet设置折痕级别为用户指定的值
            for item in all_items:
                crease_set = item.data(0, QtCore.Qt.UserRole)
                cmds.setAttr(f"{crease_set}.creaseLevel", new_level)
                
                # 更新显示文本
                item.setText(1, f"{new_level:.2f}")
            
            cmds.inViewMessage(amg=f'<span style="color:#fbca82;">已将列表中的 {len(all_items)} 个CreaseSet的折痕级别设置为 {new_level}</span>', pos='botRight', fade=True)
            
        except Exception as e:
            cmds.inViewMessage(amg=f'<span style="color:#fbca82;">设置折痕级别失败: {str(e)}</span>', pos='botRight', fade=True)
        finally:
            # 结束撤销块
            cmds.undoInfo(closeChunk=True)

    def log_warning(self, message, show_in_console=True):
        # """自定义警告日志记录"""
        # if show_in_console:
        #     cmds.warning(message)
        # else:
        #     print(message)  # 或者将信息记录到文件中
        pass

    
    def rename_crease_set(self, item, column):
        """重命名CreaseSet节点"""
        if column != 0:  # 只处理名称列的编辑
            return

        try:
            # 获取原始名称和新名称
            old_name = item.data(0, QtCore.Qt.UserRole)
            new_name = item.text(0)

            # 如果名称没有改变，直接返回
            if new_name == old_name:
                return

            # 检查新名称是否合法
            if not self.is_valid_name(new_name):
                self.log_warning(f"新名称 '{new_name}' 包含不合法字符，请使用其他名称", show_in_console=False)
                item.setText(0, old_name)  # 恢复原名称
                return

            # 检查新名称是否已存在
            if cmds.objExists(new_name):
                self.log_warning(f"名称 '{new_name}' 已存在，请使用其他名称", show_in_console=False)
                item.setText(0, old_name)  # 恢复原名称
                return

            # 重命名节点
            renamed = cmds.rename(old_name, new_name)

            # 更新存储的数据
            item.setData(0, QtCore.Qt.UserRole, renamed)
            item.setText(0, renamed)

            self.log_warning(f"已将 {old_name} 重命名为 {renamed}", show_in_console=False)

        except Exception as e:
            self.log_warning(f"重命名失败: {str(e)}", show_in_console=False)
            item.setText(0, old_name)  # 恢复原名称

    def is_valid_name(self, name):
        """检查名称是否合法"""
        # 这里可以添加更多的合法性检查逻辑
        return all(c.isalnum() or c in "_-" for c in name)

    def closeEvent(self, event):
        """关闭窗口时的处理"""
        self.remove_selection_callback()
        try:
            super(CreaseSetEditor, self).closeEvent(event)
        except TypeError:
            pass  # 忽略TypeError异常

    def merge_selected_sets(self):
        """将选中的CreaseSet中的边合并到一个新的CreaseSet中"""
        selected_items = self.crease_set_tree.selectedItems()
        if len(selected_items) < 2:
            cmds.warning("请至少选择两个CreaseSet进行合并")
            return

        # 获取当前选择的物体
        selection = cmds.ls(sl=True, long=True)
        if not selection:
            cmds.warning("请先选择物体")
            return

        # 尝试从选中物体中提取前缀
        prefix = None
        for obj in selection:
            match = re.match(r"(.+?)_(?:Lb|Lc)", obj.split("|")[-1])
            if match:
                prefix = match.group(1)
                break

        # 使用提取的前缀或默认名称
        new_set_name = prefix if prefix else "CreaseSet_M"

        # 检查名称是否已存在，并添加后缀
        base_name = new_set_name
        suffix = 1
        while cmds.objExists(new_set_name):
            new_set_name = f"{base_name}_{suffix}"
            suffix += 1

        # 合并逻辑与之前相同
        self.perform_merge(selected_items, new_set_name)

    def select_new_crease_set(self, new_crease_set):
        """选择新创建的CreaseSet"""
        for i in range(self.crease_set_tree.topLevelItemCount()):
            item = self.crease_set_tree.topLevelItem(i)
            if item.data(0, QtCore.Qt.UserRole) == new_crease_set:
                item.setSelected(True)
                self.crease_set_tree.setCurrentItem(item)
                break

    def select_merged_objects(self, edges):
        """选择合并后的模型对象"""
        
        # 提取对象名称
        objects = list(set(edge.split('.')[0] for edge in edges))
        cmds.select(objects, replace=True)

    def prefix_merge_selected_sets(self):
        """根据前缀合并选中的CreaseSet中的边到一个新的CreaseSet中"""
        selected_items = self.crease_set_tree.selectedItems()
        if len(selected_items) < 2:
            cmds.inViewMessage(amg='<span style="color:#fbca82;">请至少选择两个CreaseSet进行合并</span>', pos='botRight', fade=True)
            return

        try:
            cmds.undoInfo(openChunk=True)

            # 从选定的CreaseSet中提取对象名称
            object_names = set()
            for item in selected_items:
                crease_set = item.data(0, QtCore.Qt.UserRole)
                members = cmds.sets(crease_set, q=True) or []
                object_names.update(member.split('.')[0] for member in members)

            if not object_names:
                cmds.inViewMessage(amg='<span style="color:#fbca82;">选定的CreaseSet中没有有效的对象名称</span>', pos='botRight', fade=True)
                return

            # 使用提取的对象名称进行合并
            for obj_name in object_names:
                match = re.match(r"(.+?)_(?:Lb|Lc)", obj_name)
                prefix = match.group(1) if match else obj_name

                new_set_name = f"{prefix}_CreaseSet_M"
                base_name = new_set_name
                suffix = 1
                while cmds.objExists(new_set_name):
                    new_set_name = f"{base_name}_{suffix}"
                    suffix += 1

                self.perform_merge(selected_items, new_set_name)

        except Exception as e:
            cmds.inViewMessage(amg=f'<span style="color:#fbca82;">合并失败: {str(e)}</span>', pos='botRight', fade=True)
        finally:
            cmds.undoInfo(closeChunk=True)

    def perform_merge(self, selected_items, new_set_name):
        """执行合并操作"""
        # 获取所有选中的边
        all_edges_to_merge = []
        for item in selected_items:
            crease_set = item.data(0, QtCore.Qt.UserRole)
            members = cmds.sets(crease_set, q=True) or []

            # 遍历每个成员，检查是否是边
            for member in members:
                if '.e[' in member:  # 确保是边
                    all_edges_to_merge.append(member)

                # 从原始CreaseSet中移除这些边
            if all_edges_to_merge:
                cmds.sets(all_edges_to_merge, remove=crease_set)

            # 检查原始CreaseSet是否为空
            remaining_members = cmds.sets(crease_set, q=True) or []
            if not remaining_members:
                cmds.delete(crease_set)
                cmds.inViewMessage(amg=f'<span style="color:#fbca82;">CreaseSet {crease_set} 已被删除，因为它已为空</span>', pos='botRight', fade=True)

        # 去重
        all_edges_to_merge = list(set(all_edges_to_merge))

        if not all_edges_to_merge:
            cmds.inViewMessage(amg='<span style="color:#fbca82;">未找到相关的边进行合并</span>', pos='botRight', fade=True)
            return

        # 创建新的CreaseSet节点
        new_crease_set = cmds.createNode('creaseSet', name=new_set_name)
        cmds.sets(all_edges_to_merge, forceElement=new_crease_set)

        # 设置新CreaseSet的折痕等级为5
        cmds.setAttr(f"{new_crease_set}.creaseLevel", 5.0)

        cmds.inViewMessage(amg=f'<span style="color:#fbca82;">已将 {len(all_edges_to_merge)} 条边合并到新的CreaseSet: {new_crease_set}，并设置折痕等级为5</span>', pos='botRight', fade=True)

        # 刷新CreaseSet列表
        self.refresh_crease_sets()

        # 重新选择新创建的CreaseSet
        self.select_new_crease_set(new_crease_set)

        # 选择合并后的模型对象
        self.select_merged_objects(all_edges_to_merge)

    def prefix_rename_selected_sets(self):
        """根据前缀重命名选中的CreaseSet"""
        selected_items = self.crease_set_tree.selectedItems()
        if not selected_items:
            cmds.inViewMessage(amg='<span style="color:#fbca82;">请先选择CreaseSet节点</span>', pos='botRight', fade=True)
            return

        try:
            cmds.undoInfo(openChunk=True)

            for item in selected_items:
                old_name = item.data(0, QtCore.Qt.UserRole)
                members = cmds.sets(old_name, q=True) or []

                # 从成员中提取对象名称
                object_names = {member.split('.')[0] for member in members}

                if not object_names:
                    cmds.inViewMessage(amg=f'<span style="color:#fbca82;">CreaseSet \'{old_name}\' 中没有有效的对象名称</span>', pos='botRight', fade=True)
                    continue

                for obj_name in object_names:
                    # 提取前缀
                    match = re.match(r"(.+?)_(Lc|Lb)$", obj_name)
                    if match:
                        new_name = match.group(1)
                    else:
                        cmds.inViewMessage(amg=f'<span style="color:#fbca82;">对象 \'{obj_name}\' 没有_Lc或_Lb后缀，使用默认后缀_R</span>', pos='botRight', fade=True)
                        new_name = f"{obj_name}_R"

                    base_name = new_name
                    suffix = 1
                    while cmds.objExists(new_name):
                        new_name = f"{base_name}_{suffix}"
                        suffix += 1

                    renamed = cmds.rename(old_name, new_name)
                    item.setData(0, QtCore.Qt.UserRole, renamed)
                    item.setText(0, renamed)

                    cmds.inViewMessage(amg=f'<span style="color:#fbca82;">已将 {old_name} 重命名为 {renamed}</span>', pos='botRight', fade=True)

        except Exception as e:
            cmds.inViewMessage(amg=f'<span style="color:#fbca82;">重命名失败: {str(e)}</span>', pos='botRight', fade=True)
        finally:
            cmds.undoInfo(closeChunk=True)

    def split_crease_set_by_object(self):
        """将选中的CreaseSet按对象名称拆分为不同的CreaseSet"""
        selected_items = self.crease_set_tree.selectedItems()
        if not selected_items:
            cmds.inViewMessage(amg='<span style="color:#fbca82;">请先选择CreaseSet节点</span>', pos='botRight', fade=True)
            return

        try:
            cmds.undoInfo(openChunk=True)

            for item in selected_items:
                original_crease_set = item.data(0, QtCore.Qt.UserRole)
                members = cmds.sets(original_crease_set, q=True) or []

                object_groups = {}
                for member in members:
                    obj_name = member.split('.')[0]
                    if obj_name not in object_groups:
                        object_groups[obj_name] = []
                    object_groups[obj_name].append(member)

                for obj_name, edges in object_groups.items():
                    new_set_name = f"{obj_name}_CreaseSet"
                    base_name = new_set_name
                    suffix = 1
                    while cmds.objExists(new_set_name):
                        new_set_name = f"{base_name}_{suffix}"
                        suffix += 1

                    new_crease_set = cmds.createNode('creaseSet', name=new_set_name)
                    cmds.sets(edges, forceElement=new_crease_set)
                    cmds.setAttr(f"{new_crease_set}.creaseLevel", 5.0)
                    cmds.sets(edges, remove=original_crease_set)

                remaining_members = cmds.sets(original_crease_set, q=True) or []
                if not remaining_members:
                    cmds.delete(original_crease_set)
                    cmds.inViewMessage(amg=f'<span style="color:#fbca82;">CreaseSet {original_crease_set} 已被删除，因为它已为空</span>', pos='botRight', fade=True)

        except Exception as e:
            cmds.inViewMessage(amg=f'<span style="color:#fbca82;">拆分CreaseSet时出错: {str(e)}</span>', pos='botRight', fade=True)
        finally:
            cmds.undoInfo(closeChunk=True)
            self.refresh_crease_sets()

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QtWidgets.QMenu()

        select_action = menu.addAction("选择所有成员")
        select_action.triggered.connect(self.select_set_members_from_menu)

        menu.exec_(self.crease_set_tree.viewport().mapToGlobal(position))

    def select_set_members_from_menu(self):
        """从右键菜单选择CreaseSet的所有成员"""
        selected_items = self.crease_set_tree.selectedItems()
        if not selected_items:
            cmds.warning("请先选择CreaseSet节点")
            return

        for item in selected_items:
            self.select_set_members(item, 0)

    def select_set_members(self, item, column):
        """选择列表中选中CreaseSet的所有成员"""
        # 获取CreaseSet名称
        crease_set = item.data(0, QtCore.Qt.UserRole)
        
        # 获取CreaseSet中的所有边
        members = self.get_members_in_crease_set(crease_set)
        
        if members:
            cmds.select(members, replace=True)
            cmds.warning(f"已选择CreaseSet '{crease_set}' 中的 {len(members)} 条边")
        else:
            cmds.warning(f"CreaseSet '{crease_set}' 中没有边")
            
    def clean_empty_crease_sets(self):
        """清理没有成员的CreaseSet"""
        all_crease_sets = cmds.ls(type='objectSet') or []
        for crease_set in all_crease_sets:
            members = cmds.sets(crease_set, query=True) or []
            if not members:
                cmds.delete(crease_set)
                cmds.inViewMessage(amg=f'<span style="color:#fbca82;">删除空的CreaseSet: {crease_set}</span>', pos='botRight', fade=True)
def show():
    """显示工具窗口"""
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == 'creaseSetEditor':
            widget.close()
            widget.deleteLater()
    
    try:
        dialog = CreaseSetEditor(parent=get_maya_main_window())
        dialog.show()
        return dialog
    except Exception as e:
        cmds.warning(f"创建CreaseSet编辑器失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    show() 












