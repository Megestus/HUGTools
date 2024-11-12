import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
import maya.mel as mel

class UVSetTableItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text=""):
        super(UVSetTableItem, self).__init__(text)
        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)

class UVSetListQt(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UVSetListQt, self).__init__(parent)
        self.setWindowTitle("UV集列表工具")
        self.setObjectName("UVSetListQt")
        self.object_list = []  # 存储对象列表
        self._updating = False  # 添加标志位防止循环调用
        self.setup_ui()
        
    def setup_ui(self):
        # 初始化所有UI组件
        self.set_list = QtWidgets.QListWidget()
        self.set_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.set_list.itemSelectionChanged.connect(self.get_objects_from_sets)
        
        self.equal_list = QtWidgets.QListWidget()
        self.equal_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.equal_list.itemSelectionChanged.connect(lambda: self.select_objects_from_list(self.equal_list))
        
        self.not_list = QtWidgets.QListWidget()
        self.not_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.not_list.itemSelectionChanged.connect(lambda: self.select_objects_from_list(self.not_list))
        
        self.object_table = QtWidgets.QTableWidget()
        self.object_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.object_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.object_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.object_table.itemChanged.connect(self.rename_uv_set)
        self.object_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.object_table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.and_radio = QtWidgets.QRadioButton("AND")
        self.or_radio = QtWidgets.QRadioButton("OR")
        self.and_radio.setChecked(True)
        self.and_radio.toggled.connect(self.on_mode_changed)
        self.or_radio.toggled.connect(self.on_mode_changed)
        
        self.total_label = QtWidgets.QLabel("Total: 0")
        self.get_btn = QtWidgets.QPushButton("Get")
        self.get_btn.clicked.connect(self.get_set_list)
        
        self.equal_count = QtWidgets.QLabel("0")
        self.not_count = QtWidgets.QLabel("0")
        
        # 创建所有布局
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # 创建Equal/Not列表的布局
        lists_layout = QtWidgets.QHBoxLayout()
        
        # Equal列表部分
        equal_layout = QtWidgets.QVBoxLayout()
        equal_header = QtWidgets.QHBoxLayout()
        equal_btn = QtWidgets.QPushButton("Equal")
        equal_btn.clicked.connect(lambda: self.select_all_from_list(self.equal_list))
        equal_header.addWidget(equal_btn)
        equal_header.addStretch()
        equal_header.addWidget(self.equal_count)
        equal_layout.addLayout(equal_header)
        equal_layout.addWidget(self.equal_list)
        
        # Not列表部分
        not_layout = QtWidgets.QVBoxLayout()
        not_header = QtWidgets.QHBoxLayout()
        not_btn = QtWidgets.QPushButton("Not")
        not_btn.clicked.connect(lambda: self.select_all_from_list(self.not_list))
        not_header.addWidget(not_btn)
        not_header.addStretch()
        not_header.addWidget(self.not_count)
        not_layout.addLayout(not_header)
        not_layout.addWidget(self.not_list)
        
        # 添加Equal和Not列表到水平布局
        lists_layout.addLayout(equal_layout)
        lists_layout.addLayout(not_layout)
        
        # 创建Get按钮和计数器布局
        bottom_layout = QtWidgets.QHBoxLayout()
        
        # 添加UV编辑器按钮
        self.editor_btn = QtWidgets.QPushButton()
        self.editor_btn.setIcon(QtGui.QIcon(":polyUVSetEditor.png"))
        self.editor_btn.setFixedSize(20, 20)  # 修改按钮尺寸
        self.editor_btn.clicked.connect(self.open_editor)
        bottom_layout.addWidget(self.editor_btn)
        
        # 添加Total标签和Get按钮
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addWidget(self.get_btn)
        
        # 创建分割窗口
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        left_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        # 左侧面板添加组框
        left_group = QtWidgets.QGroupBox("UV Set Manager")
        left_layout = QtWidgets.QVBoxLayout(left_group)
        
        # UV集列表组框
        uv_set_group = QtWidgets.QGroupBox("UV Set List")
        top_layout = QtWidgets.QVBoxLayout(uv_set_group)
        top_layout.addWidget(self.set_list)
        top_layout.addLayout(bottom_layout)
        
        # Equal/Not列表组框
        list_group = QtWidgets.QGroupBox("Object Lists")
        list_layout = QtWidgets.QVBoxLayout(list_group)
        
        # 添加模式选择到顶部
        mode_layout = QtWidgets.QHBoxLayout()
        mode_layout.addWidget(self.and_radio)
        mode_layout.addWidget(self.or_radio)
        
        # 创建帮助按钮
        help_btn = QtWidgets.QPushButton()
        help_btn.setIcon(QtGui.QIcon(":help.png"))  # 使用Maya内置的帮助图标
        help_btn.setFixedSize(20, 20)
        help_btn.setCheckable(True)
        help_btn.setToolTip("显示/隐藏模式说明")  # 添加工具提示
        mode_layout.addWidget(help_btn)
        mode_layout.addStretch()
        list_layout.addLayout(mode_layout)
        
        # 创建说明文本区域
        help_text = QtWidgets.QLabel("""
        <b>AND模式</b>: 必须包含所有选中UV集的物体
        <b>OR模式</b>: 包含任一选中UV集的物体
        """)
        help_text.setWordWrap(True)
        help_text.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                padding: 4px;
                border-radius: 2px;
                font-size: 10px;
                color: #cccccc;
            }
        """)
        help_text.hide()  # 初始时隐藏
        
        # 添加到布局
        list_layout.addWidget(help_text)
        
        # 连接折叠按钮的信号
        help_btn.toggled.connect(help_text.setVisible)
        
        # 添加分隔线
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        list_layout.addWidget(line)
        
        # 添加Equal/Not列表
        list_layout.addLayout(lists_layout)
        
        # 将组框添加到左侧分割器
        left_splitter.addWidget(uv_set_group)
        left_splitter.addWidget(list_group)
        left_layout.addWidget(left_splitter)
        
        # 右侧面板添加组框
        right_group = QtWidgets.QGroupBox("UV Set Details")
        right_layout = QtWidgets.QVBoxLayout(right_group)
        
        # 表格组框
        table_group = QtWidgets.QGroupBox("UV Set Table")
        table_layout = QtWidgets.QVBoxLayout(table_group)
        table_layout.addWidget(self.object_table)
        right_layout.addWidget(table_group)
        
        # 组装主布局
        main_layout.setContentsMargins(4, 4, 4, 4)  # 设置更紧凑的边距
        main_layout.setSpacing(4)  # 设置更紧凑的间距
        main_layout.addLayout(main_layout)
        
        # 添加分割窗口
        splitter.addWidget(left_group)
        splitter.addWidget(right_group)
        main_layout.addWidget(splitter)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        left_splitter.setStretchFactor(0, 4)
        left_splitter.setStretchFactor(1, 1)
        
        # 设置窗口大小
        self.resize(640, 480)  # 设置窗口大小
        
        # 设置组框样式，减小边距和标题大小
        style = """
        QGroupBox {
            font-weight: bold;
            border: 1px solid #666666;
            border-radius: 2px;
            margin-top: 0.4em;
            padding-top: 0.4em;
            font-size: 11px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 2px 0 2px;
        }
        """
        
        # 应用样式到所有组框
        for group in [left_group, right_group, uv_set_group, list_group, table_group]:
            group.setStyleSheet(style)
    
    def get_set_list(self):
        """获取所选对象的UV集列表"""
        try:
            # 保存当前选择
            current_selection = cmds.ls(selection=True)
            print(f"当前选择对象: {current_selection}")  # 调试信息
            
            self.set_list.clear()
            self.object_table.clear()
            
            # 获取选中的对象
            selection = current_selection if current_selection else []
            objects = cmds.polyListComponentConversion(selection)
            self.object_list = []
            
            for obj in objects:
                if cmds.objectType(obj) == "mesh":
                    transform = cmds.listRelatives(obj, parent=True, type="transform")[0]
                    self.object_list.append(transform)
                elif cmds.objectType(obj) == "transform":
                    self.object_list.append(obj)
            
            print(f"处理后的对象列表: {self.object_list}")  # 调试信息
            
            # 更新总数显示
            self.total_label.setText(f"Total: {len(self.object_list)}")
            
            # 获取所有UV集
            all_sets = set()
            for obj in self.object_list:
                try:
                    sets = cmds.polyUVSet(obj, query=True, allUVSets=True) or []
                    all_sets.update(sets)
                except Exception as e:
                    print(f"获取对象 {obj} 的UV集时出错: {str(e)}")  # 调试信息
            
            print(f"所有UV集: {all_sets}")  # 调试信息
            
            # 添加到UV集列表
            for set_name in sorted(all_sets):
                self.set_list.addItem(set_name)
            
            # 设置表格列
            self.object_table.setColumnCount(len(all_sets) + 1)
            headers = ["对象"] + list(sorted(all_sets))
            self.object_table.setHorizontalHeaderLabels(headers)
            
            # 设置表头样式
            header = self.object_table.horizontalHeader()
            header.setStyleSheet("QHeaderView::section { background-color: #3a3a3a; color: white; }")
            
            # 填充表格
            self.object_table.setRowCount(len(self.object_list))
            for row, obj in enumerate(self.object_list):
                # 设置对象名称（不可编辑）
                obj_item = QtWidgets.QTableWidgetItem(obj)
                obj_item.setFlags(obj_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.object_table.setItem(row, 0, obj_item)
                
                try:
                    obj_sets = cmds.polyUVSet(obj, query=True, allUVSets=True) or []
                    for col, set_name in enumerate(headers[1:], start=1):
                        if set_name in obj_sets:
                            item = UVSetTableItem(set_name)
                            self.object_table.setItem(row, col, item)
                        else:
                            item = UVSetTableItem("")
                            self.object_table.setItem(row, col, item)
                except Exception as e:
                    print(f"填充对象 {obj} 的UV集信息时出错: {str(e)}")
            
            self.object_table.resizeColumnsToContents()
            
            # 恢复选择
            if current_selection:
                cmds.select(current_selection)
            
            print("get_set_list 方法执行完��")  # 调试信息
        except Exception as e:
            cmds.warning(f"get_set_list 方法执行失败: {str(e)}")
            print(f"get_set_list 方法执行失败: {str(e)}")  # 调试信息
    
    def get_objects_from_sets(self):
        """根据选中的UV集更新对象列表和表格选择"""
        if self._updating:
            return
            
        self._updating = True
        try:
            selected_sets = [item.text() for item in self.set_list.selectedItems()]
            
            # 清空两个列表
            self.equal_list.clear()
            self.not_list.clear()
            
            # 高亮显示表格中对应的列
            self.object_table.clearSelection()
            for col in range(self.object_table.columnCount()):
                header_text = self.object_table.horizontalHeaderItem(col).text()
                if header_text in selected_sets:
                    # 选择整列
                    for row in range(self.object_table.rowCount()):
                        self.object_table.item(row, col).setSelected(True)
            
            if not selected_sets:
                # 如果没有选中的UV集，所有对象都显在not列表中
                for obj in self.object_list:
                    self.not_list.addItem(obj)
                self.equal_count.setText("0")
                self.not_count.setText(str(len(self.object_list)))
                return
            
            equal_objects = []
            not_objects = []
            
            for obj in self.object_list:
                try:
                    obj_sets = cmds.polyUVSet(obj, query=True, allUVSets=True) or []
                    
                    # 根据AND/OR模式判断是否匹配
                    if self.and_radio.isChecked():
                        # AND模式：必须包含所有选中的UV集
                        if all(s in obj_sets for s in selected_sets):
                            equal_objects.append(obj)
                        else:
                            not_objects.append(obj)
                    else:
                        # OR模式：包含任一选中的UV集
                        if any(s in obj_sets for s in selected_sets):
                            equal_objects.append(obj)
                        else:
                            not_objects.append(obj)
                            
                except Exception as e:
                    print(f"处理对象 {obj} 时出错: {str(e)}")
                    not_objects.append(obj)
            
            # 更新列表
            for obj in equal_objects:
                self.equal_list.addItem(obj)
            for obj in not_objects:
                self.not_list.addItem(obj)
            
            # 更新计数
            self.equal_count.setText(str(len(equal_objects)))
            self.not_count.setText(str(len(not_objects)))
            
        finally:
            self._updating = False
    
    def on_table_selection_changed(self):
        """处理表格选择变化"""
        if self._updating:
            return
            
        self._updating = True
        try:
            selected_items = self.object_table.selectedItems()
            selected_rows = set()
            selected_cols = set()
            
            # 获取选中的行和列
            for item in selected_items:
                selected_rows.add(item.row())
                selected_cols.add(item.column())
            
            # 更新UV集列表的选择
            self.set_list.clearSelection()
            for col in selected_cols:
                if col > 0:  # 跳过第一列（对象名称列）
                    header_text = self.object_table.horizontalHeaderItem(col).text()
                    items = self.set_list.findItems(header_text, QtCore.Qt.MatchExactly)
                    if items:
                        items[0].setSelected(True)
            
            # 选择Maya场景中的对象并更新Equal/Not列表
            objects_to_select = [self.object_table.item(row, 0).text() for row in selected_rows]
            if objects_to_select:
                cmds.select(objects_to_select)
                
                # 更新Equal/Not列表的选择
                self.equal_list.clearSelection()
                self.not_list.clearSelection()
                
                for i in range(self.equal_list.count()):
                    item = self.equal_list.item(i)
                    if item.text() in objects_to_select:
                        item.setSelected(True)
                        
                for i in range(self.not_list.count()):
                    item = self.not_list.item(i)
                    if item.text() in objects_to_select:
                        item.setSelected(True)
            else:
                cmds.select(clear=True)
                self.equal_list.clearSelection()
                self.not_list.clearSelection()
                
        finally:
            self._updating = False
    
    def rename_uv_set(self, item):
        """命名UV集"""
        if item.column() == 0:  # 忽略对象名称列
            return
            
        obj_name = self.object_table.item(item.row(), 0).text()
        old_name = self.object_table.horizontalHeaderItem(item.column()).text()
        new_name = item.text()
        
        if new_name and new_name != old_name:
            try:
                cmds.polyUVSet(obj_name, rename=True, uvSet=old_name, newUVSet=new_name)
                # 重新获取列表
                self.get_set_list()
            except Exception as e:
                cmds.warning(f"重命名UV集失败: {str(e)}")
                item.setText(old_name)  # 恢复原名称
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.object_table.itemAt(pos)
        if not item:
            return
            
        if item.column() == 0:  # 对象���不显示菜单
            return
            
        menu = QtWidgets.QMenu(self)
        
        # 获取当前对象和UV集名称
        obj_name = self.object_table.item(item.row(), 0).text()
        uv_set = self.object_table.horizontalHeaderItem(item.column()).text()
        
        # 添加菜单项
        new_action = menu.addAction("新建UV集")
        copy_action = menu.addAction("复制UV集")
        rename_action = menu.addAction("重命名UV集")
        menu.addSeparator()
        delete_action = menu.addAction("删除UV集")
        
        # 执行菜单
        action = menu.exec_(self.object_table.viewport().mapToGlobal(pos))
        
        if action == new_action:
            self.create_new_uv_set(obj_name)
        elif action == copy_action:
            self.copy_uv_set(obj_name, uv_set)
        elif action == rename_action:
            self.show_rename_dialog(item)
        elif action == delete_action:
            self.delete_uv_set(item)

    def create_new_uv_set(self, obj_name):
        """创建新的UV集"""
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle("新建UV集")
        dialog.setLabelText("输入UV集名称:")
        dialog.setTextValue("uvSet1")
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.textValue()
            if new_name:
                try:
                    # 保存当前状态
                    current_objects = self.object_list.copy()
                    selected_objects = cmds.ls(selection=True)
                    
                    # 创建UV集
                    cmds.polyUVSet(obj_name, create=True, uvSet=new_name)
                    
                    # 更新UI但保持对象列表
                    self.object_list = current_objects
                    self.update_table_and_lists()
                    
                    # 恢复选择
                    if selected_objects:
                        cmds.select(selected_objects)
                        
                except Exception as e:
                    cmds.warning(f"创建UV集失败: {str(e)}")

    def copy_uv_set(self, obj_name, source_uv_set):
        """复制UV集"""
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle("复制UV集")
        dialog.setLabelText("输入新UV集名称:")
        dialog.setTextValue(f"{source_uv_set}_copy")
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.textValue()
            if new_name:
                try:
                    # 保存当前状态
                    current_objects = self.object_list.copy()
                    selected_objects = cmds.ls(selection=True)
                    
                    # 复制UV集
                    cmds.polyUVSet(obj_name, copy=True, uvSet=source_uv_set, newUVSet=new_name)
                    
                    # 更新UI但保持对象列表
                    self.object_list = current_objects
                    self.update_table_and_lists()
                    
                    # 恢复选择
                    if selected_objects:
                        cmds.select(selected_objects)
                        
                except Exception as e:
                    cmds.warning(f"复制UV集失败: {str(e)}")

    def show_rename_dialog(self, item):
        """显示重命名对话框"""
        obj_name = self.object_table.item(item.row(), 0).text()
        old_name = self.object_table.horizontalHeaderItem(item.column()).text()
        
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle("重命名UV集")
        dialog.setLabelText("输入新名称:")
        dialog.setTextValue(old_name)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.textValue()
            if new_name and new_name != old_name:
                try:
                    # 保存当前状态
                    current_objects = self.object_list.copy()
                    selected_objects = cmds.ls(selection=True)
                    
                    # 重命名UV集
                    cmds.polyUVSet(obj_name, rename=True, uvSet=old_name, newUVSet=new_name)
                    
                    # 更新UI但保持对象列表
                    self.object_list = current_objects
                    self.update_table_and_lists()
                    
                    # 恢复选择
                    if selected_objects:
                        cmds.select(selected_objects)
                        
                except Exception as e:
                    cmds.warning(f"重命名UV集失败: {str(e)}")

    def delete_uv_set(self, item):
        """删除UV集"""
        obj_name = self.object_table.item(item.row(), 0).text()
        uv_set = self.object_table.horizontalHeaderItem(item.column()).text()
        
        try:
            # 保存当前所有对象
            current_objects = self.object_list.copy()
            
            # 删除UV集
            cmds.polyUVSet(obj_name, delete=True, uvSet=uv_set)
            
            # 保存当前选择状态
            selected_objects = cmds.ls(selection=True)
            
            # 重新获取列表，但使用保存的对象列表
            self.object_list = current_objects
            
            # 更新表格和UV集列表
            self.update_table_and_lists()
            
            # 恢复选择
            if selected_objects:
                cmds.select(selected_objects)
                
        except Exception as e:
            cmds.warning(f"删除UV集失败: {str(e)}")

    def update_table_and_lists(self):
        """更新表格和UV集列表，但保持对象列表不变"""
        try:
            # 清空UV集列表和表格
            self.set_list.clear()
            self.object_table.clear()
            
            # 获取所有UV集
            all_sets = set()
            for obj in self.object_list:
                try:
                    sets = cmds.polyUVSet(obj, query=True, allUVSets=True) or []
                    all_sets.update(sets)
                except Exception as e:
                    print(f"获取对象 {obj} 的UV集时出错: {str(e)}")
            
            # 更新UV集列表
            for set_name in sorted(all_sets):
                self.set_list.addItem(set_name)
            
            # 设置表格列
            self.object_table.setColumnCount(len(all_sets) + 1)
            headers = ["对象"] + list(sorted(all_sets))
            self.object_table.setHorizontalHeaderLabels(headers)
            
            # 设置表头样式
            header = self.object_table.horizontalHeader()
            header.setStyleSheet("QHeaderView::section { background-color: #3a3a3a; color: white; }")
            
            # 填充表格
            self.object_table.setRowCount(len(self.object_list))
            for row, obj in enumerate(self.object_list):
                # 设置对象名称
                obj_item = QtWidgets.QTableWidgetItem(obj)
                obj_item.setFlags(obj_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.object_table.setItem(row, 0, obj_item)
                
                try:
                    obj_sets = cmds.polyUVSet(obj, query=True, allUVSets=True) or []
                    for col, set_name in enumerate(headers[1:], start=1):
                        if set_name in obj_sets:
                            item = UVSetTableItem(set_name)
                            self.object_table.setItem(row, col, item)
                        else:
                            item = UVSetTableItem("")
                            self.object_table.setItem(row, col, item)
                except Exception as e:
                    print(f"填充对象 {obj} 的UV集信息时出错: {str(e)}")
            
            self.object_table.resizeColumnsToContents()
            
            # 更新总数显示
            self.total_label.setText(f"Total: {len(self.object_list)}")
            
            # 触发UV集选择更新
            self.get_objects_from_sets()
            
        except Exception as e:
            cmds.warning(f"更新表格和列表失败: {str(e)}")
    
    def open_editor(self):
        """打开UV编辑器"""
        mel.eval('UVSetEditor')

    def select_objects_from_list(self, list_widget):
        """从列表中选择对象"""
        if self._updating:
            return
            
        self._updating = True
        try:
            selected_items = list_widget.selectedItems()
            if selected_items:
                # 取消另一个列表的选择
                other_list = self.not_list if list_widget == self.equal_list else self.equal_list
                other_list.clearSelection()
                
                # 选择对象
                objects_to_select = [item.text() for item in selected_items]
                cmds.select(objects_to_select)
                
                # 同步表格选择
                self.object_table.clearSelection()
                for row in range(self.object_table.rowCount()):
                    obj_name = self.object_table.item(row, 0).text()
                    if obj_name in objects_to_select:
                        self.object_table.selectRow(row)
        finally:
            self._updating = False

    def select_all_from_list(self, list_widget):
        """选择列表中的所有对象"""
        all_items = [list_widget.item(i).text() for i in range(list_widget.count())]
        if all_items:
            cmds.select(all_items)

    def edit_header(self, logical_index):
        """编辑表头（批量重命名UV集）"""
        if logical_index == 0:  # 不允许编辑"对象"列
            return
        
        old_name = self.object_table.horizontalHeaderItem(logical_index).text()
        new_name, ok = QtWidgets.QInputDialog.getText(self, "编辑UV集名称", "输入新的UV集名称:", text=old_name)
        
        if ok and new_name and new_name != old_name:
            try:
                # 保存当前状态
                current_objects = self.object_list.copy()
                selected_objects = cmds.ls(selection=True)
                
                # 更新所有选中对象的UV集名称
                selected_rows = set(item.row() for item in self.object_table.selectedItems())
                for row in selected_rows:
                    obj_name = self.object_table.item(row, 0).text()
                    cmds.polyUVSet(obj_name, rename=True, uvSet=old_name, newUVSet=new_name)
                
                # 更新UI但保持对象列表
                self.object_list = current_objects
                self.update_table_and_lists()
                
                # 恢复选择
                if selected_objects:
                    cmds.select(selected_objects)
                    
            except Exception as e:
                cmds.warning(f"重命名UV集失败: {str(e)}")

    def update_uv_set_list(self):
        # 更新左侧的UV集列表
        self.set_list.clear()
        for col in range(1, self.object_table.columnCount()):
            uv_set = self.object_table.horizontalHeaderItem(col).text()
            self.set_list.addItem(uv_set)

    def delete_uv_set_column(self, column_index):
        uv_set = self.object_table.horizontalHeaderItem(column_index).text()
        reply = QtWidgets.QMessageBox.question(self, '删除UV集', 
                                               f"确定要删除UV集 '{uv_set}' 吗？\n这将从所有选中对象中删该UV集。",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                                               QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                # 从所有选中对象中删除UV集
                selected_rows = set(item.row() for item in self.object_table.selectedItems())
                for row in selected_rows:
                    obj_name = self.object_table.item(row, 0).text()
                    cmds.polyUVSet(obj_name, delete=True, uvSet=uv_set)
                
                # 从表格中删除列
                self.object_table.removeColumn(column_index)
                
                # 更新UV集列表
                self.update_uv_set_list()
            except Exception as e:
                cmds.warning(f"删除UV集失败: {str(e)}")

    def on_mode_changed(self):
        """处理AND/OR模式切换"""
        if self._updating:
            return
            
        self._updating = True
        try:
            # 保存当前选择状态
            selected_objects = cmds.ls(selection=True)
            
            # 重新计算Equal/Not列表
            self.get_objects_from_sets()
            
            # 恢复选择状态
            if selected_objects:
                cmds.select(selected_objects)
                
        finally:
            self._updating = False

def show():
    """显示窗口"""
    # 获取Maya主窗口
    maya_window = QtWidgets.QApplication.activeWindow()
    
    # 关闭已存在的窗口
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == "UVSetListQt":
            widget.close()
            widget.deleteLater()
    
    # 创建并显示新窗口
    window = UVSetListQt(maya_window)
    window.show()