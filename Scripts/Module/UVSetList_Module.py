import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
import maya.mel as mel
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import importlib


# UI text dictionary
UI_TEXTS = {
    'en_US': {
        # Window title
        "window_title": "UV List Editor",
        
        # Button texts
        "btn_get": "Get",
        "btn_equal": "Equal",
        "btn_not": "Not",
        
        # Label texts
        "label_total": "Total: {}",
        "label_and": "AND",
        "label_or": "OR",
        "label_help_tooltip": "Show/Hide Mode Description",
        
        # Group box titles
        "group_uv_manager": "UV Set Manager",
        "group_uv_list": "UV Set List",
        "group_obj_lists": "Object Lists",
        "group_uv_details": "UV Set Details",
        "group_uv_table": "UV Set Table",
        
        # Help text
        "help_text": """
        <b>AND Mode</b>: Objects must contain all selected UV sets
        <b>OR Mode</b>: Objects contain any of selected UV sets
        """,
        
        # Table column headers
        "column_object": "Object",
        
        # Right-click menu items
        "menu_new": "Create New UV Set",
        "menu_copy": "Copy UV Set",
        "menu_rename": "Rename UV Set",
        "menu_delete": "Delete UV Set",
        
        # Header right-click menu items
        "menu_header_rename": "Rename '{}' UV Set for All Objects",
        "menu_header_delete": "Delete '{}' UV Set from All Objects",
        
        # Dialog titles and labels
        "dialog_new_title": "Create New UV Set",
        "dialog_new_label": "Enter UV Set Name:",
        "dialog_copy_title": "Copy UV Set",
        "dialog_copy_label": "Enter New UV Set Name:",
        "dialog_rename_title": "Rename UV Set",
        "dialog_rename_label": "Enter New Name:",
        
        # Warning and error messages
        "warning_rename_failed": "Failed to rename UV set: {}",
        "warning_delete_failed": "Failed to delete UV set: {}",
        "warning_create_failed": "Failed to create UV set: {}",
        "warning_copy_failed": "Failed to copy UV set: {}",
        "warning_update_failed": "Failed to update table and lists: {}",
        "warning_rename_success": "Renamed '{}' UV set to '{}' for {} objects",
        "warning_delete_success": "Deleted '{}' UV set from {} objects",
        "warning_not_found": "UV set '{}' not found",
        
        # Debug messages
        "debug_current_selection": "Current selection: {}",
        "debug_object_list": "Processed object list: {}",
        "debug_all_uv_sets": "All UV sets: {}",
        "debug_error_get_uv": "Error getting UV sets for object {}: {}",
        "debug_error_fill_info": "Error filling UV set info for object {}: {}",
        "debug_error_process": "Error processing object {}: {}",
        
        # Header right-click menu format strings
        "menu_header_rename_format": "Rename '{}' UV Set for All Objects",
        "menu_header_delete_format": "Delete '{}' UV Set from All Objects",
        
        # Dialog texts
        "dialog_rename_header_label": "Rename '{}' UV Set for All Objects to:",
        "dialog_batch_rename_label": "Rename all '{}' UV sets to:",
        
        # Debug and error messages
        "debug_method_complete": "get_set_list method completed",
        "debug_method_failed": "get_set_list method failed: {}",
        "debug_rename_error": "Error renaming UV set for object {}: {}",
        "debug_delete_error": "Error deleting UV set {} for object {}: {}",
        
        # Default values
        "default_uvset_name": "uvSet1",
        "default_copy_name": "{}_copy",
        "tooltip_language": "Switch Language 切换语言",
    },
    'zh_CN': {
        # Window title
        "window_title": "UV List Editor",
        
        # Button texts
        "btn_get": "获取",
        "btn_equal": "相同",
        "btn_not": "不同",
        
        # Label texts
        "label_total": "总数: {}",
        "label_and": "与",
        "label_or": "或",
        "label_help_tooltip": "显示/隐藏模式说明",
        
        # Group box titles
        "group_uv_manager": "UV集管理器",
        "group_uv_list": "UV集列表",
        "group_obj_lists": "物体列表",
        "group_uv_details": "UV集详情",
        "group_uv_table": "UV集表格",
        
        # Help text
        "help_text": """
        <b>与模式</b>: 物体必须包含所有选中的UV集
        <b>或模式</b>: 物体包含任一选中的UV集
        """,
        
        # Table column headers
        "column_object": "对象",
        
        # Right-click menu items
        "menu_new": "新建UV集",
        "menu_copy": "复制UV集",
        "menu_rename": "重命名UV集",
        "menu_delete": "删除UV集",
        
        # Header right-click menu items
        "menu_header_rename": "重命名所有物体的 '{}' UV",
        "menu_header_delete": "删除所有物体的 '{}' UV集",
        
        # Dialog titles and labels
        "dialog_new_title": "新建UV集",
        "dialog_new_label": "输入UV集名称:",
        "dialog_copy_title": "复制UV集",
        "dialog_copy_label": "输入新UV集名称:",
        "dialog_rename_title": "重命名UV集",
        "dialog_rename_label": "输入新名称:",
        
        # Use English for warning and error messages
        "warning_rename_failed": "Failed to rename UV set: {}",
        "warning_delete_failed": "Failed to delete UV set: {}",
        "warning_create_failed": "Failed to create UV set: {}",
        "warning_copy_failed": "Failed to copy UV set: {}",
        "warning_update_failed": "Failed to update table and lists: {}",
        "warning_rename_success": "Renamed '{}' UV set to '{}' for {} objects",
        "warning_delete_success": "Deleted '{}' UV set from {} objects",
        "warning_not_found": "UV set '{}' not found",
        
        # Use English for debug messages
        "debug_current_selection": "Current selection: {}",
        "debug_object_list": "Processed object list: {}",
        "debug_all_uv_sets": "All UV sets: {}",
        "debug_error_get_uv": "Error getting UV sets for object {}: {}",
        "debug_error_fill_info": "Error filling UV set info for object {}: {}",
        "debug_error_process": "Error processing object {}: {}",
        
        # Header right-click menu format strings
        "menu_header_rename_format": "重命名所有物体的 '{}' UV集",
        "menu_header_delete_format": "删除所有物体的 '{}' UV集",
        
        # Dialog texts
        "dialog_rename_header_label": "将所有物体的 '{}' UV集重命名为:",
        "dialog_batch_rename_label": "将所有名为 '{}' 的UV集重命名为:",
        
        # Use English for debug and error messages
        "debug_method_complete": "get_set_list method completed",
        "debug_method_failed": "get_set_list method failed: {}",
        "debug_rename_error": "Error renaming UV set for object {}: {}",
        "debug_delete_error": "Error deleting UV set {} for object {}: {}",
        
        # Default values
        "default_uvset_name": "uvSet1",
        "default_copy_name": "{}_copy",
        "tooltip_language": "切换语言 Switch Language",
    }
}

#====== UI Components ======

class RoundedButton(QtWidgets.QPushButton):
    """Custom rounded button class"""
    def __init__(self, text="", icon=None, is_toolbar=False):
        super(RoundedButton, self).__init__(text)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(24, 24))
            
        if is_toolbar:
            # 工栏按钮样式
            self.setStyleSheet("""
                QPushButton {
                    background-color: #353535;
                    color: #CCCCCC;
                    border: 1px solid #555555;
                    border-radius: 12px;
                    padding: 4px 8px;
                    font-size: 11px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #404040;
                    border-color: #666666;
                }
                QPushButton:pressed {
                    background-color: #303030;
                    border-color: #777777;
                }
            """)
        else:
            # 普通按钮样式
            self.setStyleSheet("""
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
            """)

class UVSetTableItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text=""):
        super(UVSetTableItem, self).__init__(text)
        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)

#====== UI Main Window Component ======

class UVSetList_Module_UI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UVSetList_Module_UI, self).__init__(parent)
        self.current_language = "en_US"  # 默认使用英文
        self.texts = UI_TEXTS[self.current_language]  # 默认使用英文字典
        self.setWindowTitle(self.texts["window_title"])
        self.setObjectName("UVSetList_Module_UI")
        self.object_list = []
        self._updating = False
        self.swap_source_uv = None  # 添加用于存储要交换的源UV集
        self.swap_source_obj = None  # 添加用于存储源对象
        self.swap_mode = None  # 添加用于存储操作模式（swap或reorder）
        self.setup_ui()
        self.create_connections()

#====== UI Layout ======

    def setup_ui(self):
        # 创建主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # 创建顶部工具栏
        toolbar_layout = QtWidgets.QHBoxLayout()
        toolbar_layout.setSpacing(4)
        
        # Maya UV Set Editor按钮
        self.editor_btn = RoundedButton(" UV Set Editor", QtGui.QIcon(":polyUVSetEditor.png"), is_toolbar=True)
        self.editor_btn.setToolTip("Open Maya UV Set Editor")
        self.editor_btn.clicked.connect(self.open_editor)
        
        # UV Editor按钮
        self.uv_editor_btn = RoundedButton("UV Editor", QtGui.QIcon(":textureEditor.png"), is_toolbar=True)
        self.uv_editor_btn.setToolTip("Open UV Editor")
        self.uv_editor_btn.clicked.connect(self.open_uv_editor)
        
        # Transfer Attributes按钮
        self.transfer_btn = RoundedButton("Transfer", QtGui.QIcon(":polyTransfer.png"), is_toolbar=True)
        self.transfer_btn.setToolTip("Open Transfer Attributes")
        self.transfer_btn.clicked.connect(self.open_TransferAttributes)
        
        # 语言切换按钮
        self.lang_btn = RoundedButton("CN/EN", None, is_toolbar=True)
        self.lang_btn.setToolTip(self.texts["tooltip_language"])
        
        # 添加按钮到工具栏
        toolbar_layout.addWidget(self.editor_btn)
        toolbar_layout.addWidget(self.uv_editor_btn)
        toolbar_layout.addWidget(self.transfer_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.lang_btn)
        
        # 将工具栏添加到主布局
        main_layout.addLayout(toolbar_layout)
        
        # Initialize all UI components
        self.set_list = QtWidgets.QListWidget()
        self.set_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        
        self.equal_list = QtWidgets.QListWidget()
        self.equal_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        
        self.not_list = QtWidgets.QListWidget()
        self.not_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        
        self.object_table = QtWidgets.QTableWidget()
        self.object_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.object_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.object_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.and_radio = QtWidgets.QRadioButton(self.texts["label_and"])
        self.or_radio = QtWidgets.QRadioButton(self.texts["label_or"])
        self.and_radio.setChecked(True)
        
        self.total_label = QtWidgets.QLabel(self.texts["label_total"].format(0))
        self.get_btn = RoundedButton(self.texts["btn_get"])
        
        self.equal_count = QtWidgets.QLabel("0")
        self.not_count = QtWidgets.QLabel("0")
        
        # Create all layouts
        lists_layout = QtWidgets.QHBoxLayout()
        
        # Equal list layout
        equal_layout = QtWidgets.QVBoxLayout()
        equal_header = QtWidgets.QHBoxLayout()
        equal_btn = RoundedButton(self.texts["btn_equal"])
        equal_btn.setObjectName("equal_btn")
        equal_btn.clicked.connect(lambda: self.select_all_from_list(self.equal_list))
        equal_header.addWidget(equal_btn)
        equal_header.addStretch()
        equal_header.addWidget(self.equal_count)
        equal_layout.addLayout(equal_header)
        equal_layout.addWidget(self.equal_list)
        
        # Not list layout
        not_layout = QtWidgets.QVBoxLayout()
        not_header = QtWidgets.QHBoxLayout()
        not_btn = RoundedButton(self.texts["btn_not"])
        not_btn.setObjectName("not_btn")
        not_btn.clicked.connect(lambda: self.select_all_from_list(self.not_list))
        not_header.addWidget(not_btn)
        not_header.addStretch()
        not_header.addWidget(self.not_count)
        not_layout.addLayout(not_header)
        not_layout.addWidget(self.not_list)
        
        # Add Equal and Not lists to horizontal layout
        lists_layout.addLayout(equal_layout)
        lists_layout.addLayout(not_layout)
        
        # Create Get button and counter layout
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addWidget(self.get_btn)
        
        # Create splitter window
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        left_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        # Add group box to left panel
        left_group = QtWidgets.QGroupBox()
        left_layout = QtWidgets.QVBoxLayout(left_group)
        
        # UV set list group box
        uv_set_group = QtWidgets.QGroupBox(self.texts["group_uv_list"])
        top_layout = QtWidgets.QVBoxLayout(uv_set_group)
        top_layout.addWidget(self.set_list)
        top_layout.addLayout(bottom_layout)
        
        # Equal/Not list group box
        list_group = QtWidgets.QGroupBox(self.texts["group_obj_lists"])
        list_layout = QtWidgets.QVBoxLayout(list_group)
        
        # Add mode selection
        mode_layout = QtWidgets.QHBoxLayout()
        mode_layout.addWidget(self.and_radio)
        mode_layout.addWidget(self.or_radio)
        
        # Create help button
        help_btn = QtWidgets.QPushButton()
        help_btn.setIcon(QtGui.QIcon(":help.png"))
        help_btn.setFixedSize(24, 24)
        help_btn.setToolTip(self.texts["label_help_tooltip"])
        help_btn.setCheckable(True)
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 12px;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 10);
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 30);
                border-radius: 12px;
            }
        """)
        mode_layout.addWidget(help_btn)
        mode_layout.addStretch()
        list_layout.addLayout(mode_layout)
        
        # Create help text
        self.help_text = QtWidgets.QLabel(self.texts["help_text"])
        self.help_text.setObjectName("help_text")
        self.help_text.setWordWrap(True)
        self.help_text.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                padding: 4px;
                border-radius: 2px;
                font-size: 10px;
                color: #cccccc;
            }
        """)
        self.help_text.hide()
        list_layout.addWidget(self.help_text)
        help_btn.toggled.connect(self.help_text.setVisible)
        
        # Add separator line
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        list_layout.addWidget(line)
        
        # Add Equal/Not lists
        list_layout.addLayout(lists_layout)
        
        # Add group boxes to left splitter
        left_splitter.addWidget(uv_set_group)
        left_splitter.addWidget(list_group)
        left_layout.addWidget(left_splitter)
        
        # Add group box to right side
        right_group = QtWidgets.QGroupBox()
        right_layout = QtWidgets.QVBoxLayout(right_group)
        
        # Table group box
        table_group = QtWidgets.QGroupBox(self.texts["group_uv_table"])
        table_layout = QtWidgets.QVBoxLayout(table_group)
        table_layout.addWidget(self.object_table)
        right_layout.addWidget(table_group)
        
        # Add splitter window
        splitter.addWidget(left_group)
        splitter.addWidget(right_group)
        main_layout.addWidget(splitter)
        
        # Set splitter factors
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        left_splitter.setStretchFactor(0, 4)
        left_splitter.setStretchFactor(1, 1)
        
        # Set window size
        self.resize(640, 480)
        
        # 更新列表样式
        list_style = """
            QListWidget {
                background-color: #2B2B2B;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #4B4B4B;
            }
            QListWidget::item:hover {
                background-color: #3B3B3B;
            }
        """
        
        self.set_list.setStyleSheet(list_style)
        self.equal_list.setStyleSheet(list_style)
        self.not_list.setStyleSheet(list_style)

        # 更新表格样式
        self.object_table.setStyleSheet("""
            QTableWidget {
                background-color: #2B2B2B;
                color: #CCCCCC;
                gridline-color: #444444;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3A7CA8;
            }
            QHeaderView::section {
                background-color: #353535;
                color: #CCCCCC;
                border: 1px solid #444444;
                padding: 4px;
            }
        """)

        # 更新分组框样式
        group_style = """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #666666;
                border-radius: 5px;
                margin-top: 0.5em;
                padding-top: 0.5em;
                font-size: 11px;
                color: #CCCCCC;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """

        # 更新单选按钮样式
        radio_style = """
            QRadioButton {
                color: #CCCCCC;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #555555;
                background-color: #2B2B2B;
                border-radius: 7px;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #555555;
                background-color: #FFFFFF;
                border-radius: 7px;
            }
        """
        
        self.and_radio.setStyleSheet(radio_style)
        self.or_radio.setStyleSheet(radio_style)

        # 更新帮助文本样式
        self.help_text.setStyleSheet("""
            QLabel {
                background-color: #2B2B2B;
                color: #CCCCCC;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #555555;
                font-size: 11px;
            }
        """)

        # 设置窗口整体样式
        self.setStyleSheet("""
            QDialog {
                background-color: #373737;
            }
            QLabel {
                color: #CCCCCC;
            }
        """)

        # Set table properties
        self.object_table.setSortingEnabled(False)
        self.object_table.setAlternatingRowColors(True)
        self.object_table.setShowGrid(True)
        self.object_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.object_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.object_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        # 确保表头也设置了上下文菜单策略
        header = self.object_table.horizontalHeader()
        header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_header_context_menu)

#====== UI and Function Connections ======

    def create_connections(self):
        self.set_list.itemSelectionChanged.connect(self.get_objects_from_sets)
        self.equal_list.itemSelectionChanged.connect(lambda: self.select_objects_from_list(self.equal_list))
        self.not_list.itemSelectionChanged.connect(lambda: self.select_objects_from_list(self.not_list))
        self.object_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.object_table.itemChanged.connect(self.rename_uv_set)
        self.object_table.customContextMenuRequested.connect(self.show_context_menu)
        self.and_radio.toggled.connect(self.on_mode_changed)
        self.or_radio.toggled.connect(self.on_mode_changed)
        # Add Get button connection
        self.get_btn.clicked.connect(self.get_set_list)
        self.object_table.horizontalHeader().customContextMenuRequested.connect(self.show_header_context_menu)
        # Add table cell click event connection
        self.object_table.cellClicked.connect(self.on_table_cell_clicked)
        # Add header click event connection
        self.object_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        # 确保只连接一次语言切换按钮
        try:
            self.lang_btn.clicked.disconnect()  # 断开之前的连接
        except:
            pass
        self.lang_btn.clicked.connect(self.toggle_language)

#====== UV Set Management Functions ======

    def get_set_list(self):
        """Get UV set list for selected objects"""
        try:
            # Save current selection
            current_selection = cmds.ls(selection=True)
            
            self.set_list.clear()
            self.object_table.clear()
            
            # Get selected objects
            selection = current_selection if current_selection else []
            objects = cmds.polyListComponentConversion(selection)
            self.object_list = []
            
            # Process objects
            for obj in objects:
                if cmds.objectType(obj) == "mesh":
                    transform = cmds.listRelatives(obj, parent=True, type="transform")[0]
                    self.object_list.append(transform)
                elif cmds.objectType(obj) == "transform":
                    self.object_list.append(obj)
            
            # Update total count display
            self.total_label.setText(f"Total: {len(self.object_list)}")
            
            # Get all UV sets and maintain order
            all_sets = []
            # Use first object as reference for UV set order
            if self.object_list:
                reference_obj = self.object_list[0]
                reference_sets = cmds.polyUVSet(reference_obj, query=True, allUVSets=True) or []
                all_sets.extend(reference_sets)
                
                # Collect UV sets from other objects
                for obj in self.object_list[1:]:
                    try:
                        sets = cmds.polyUVSet(obj, query=True, allUVSets=True) or []
                        # Only add new UV sets
                        for set_name in sets:
                            if set_name not in all_sets:
                                all_sets.append(set_name)
                    except Exception as e:
                        print(f"Error getting UV sets for object {obj}: {str(e)}")
            
            # Add to UV set list
            for set_name in all_sets:
                self.set_list.addItem(set_name)
            
            # Set table columns
            self.object_table.setColumnCount(len(all_sets) + 1)
            headers = [self.texts["column_object"]] + all_sets  # Use a list to maintain order
            self.object_table.setHorizontalHeaderLabels(headers)
            
            # Set header style
            header = self.object_table.horizontalHeader()
            header.setStyleSheet("QHeaderView::section { background-color: #3a3a3a; color: white; }")
            
            # Fill table
            self.object_table.setRowCount(len(self.object_list))
            for row, obj in enumerate(self.object_list):
                # Set object name (non-editable)
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
                    print(f"Error filling UV set info for object {obj}: {str(e)}")
            
            self.object_table.resizeColumnsToContents()
            
            # Restore selection
            if current_selection:
                cmds.select(current_selection)
            
            print("get_set_list method completed")  # Debug info
        except Exception as e:
            cmds.warning(f"get_set_list method failed: {str(e)}")
            print(f"get_set_list method failed: {str(e)}")  # Debug info
    
    def create_new_uv_set(self, obj_name):
        """Create a new UV set"""
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle(self.texts["dialog_new_title"])
        dialog.setLabelText(self.texts["dialog_new_label"])
        dialog.setTextValue("uvSet1")
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.textValue()
            if new_name:
                try:
                    # Save current state
                    current_objects = self.object_list.copy()
                    selected_objects = cmds.ls(selection=True)
                    
                    # Create UV set
                    cmds.polyUVSet(obj_name, create=True, uvSet=new_name)
                    
                    # New UI but keep object list
                    self.object_list = current_objects
                    self.update_table_and_lists()
                    
                    # Restore selection
                    if selected_objects:
                        cmds.select(selected_objects)
                        
                except Exception as e:
                    cmds.warning(f"Failed to create UV set: {str(e)}")

    def copy_uv_set(self, obj_name, source_uv_set):
        """Copy UV set"""
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle(self.texts["dialog_copy_title"])
        dialog.setLabelText(self.texts["dialog_copy_label"])
        dialog.setTextValue(f"{source_uv_set}_copy")
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.textValue()
            if new_name:
                try:
                    # Save current state
                    current_objects = self.object_list.copy()
                    selected_objects = cmds.ls(selection=True)
                    
                    # Copy UV set
                    cmds.polyUVSet(obj_name, copy=True, uvSet=source_uv_set, newUVSet=new_name)
                    
                    # Update UI but keep object list
                    self.object_list = current_objects
                    self.update_table_and_lists()
                    
                    # Restore selection
                    if selected_objects:
                        cmds.select(selected_objects)
                        
                except Exception as e:
                    cmds.warning(f"Failed to copy UV set: {str(e)}")

    def rename_uv_set(self, item):
        """Rename UV set"""
        if item.column() == 0:  # Ignore object name column
            return
            
        obj_name = self.object_table.item(item.row(), 0).text()
        old_name = self.object_table.horizontalHeaderItem(item.column()).text()
        new_name = item.text()
        
        if new_name and new_name != old_name:
            try:
                cmds.polyUVSet(obj_name, rename=True, uvSet=old_name, newUVSet=new_name)
                # Re-fetch list
                self.get_set_list()
            except Exception as e:
                cmds.warning(f"Failed to rename UV set: {str(e)}")
                item.setText(old_name)  # Restore original name
    
    def delete_uv_set(self, item):
        """Delete UV set"""
        obj_name = self.object_table.item(item.row(), 0).text()
        uv_set = self.object_table.horizontalHeaderItem(item.column()).text()
        
        try:
            # Save current state
            current_objects = self.object_list.copy()
            
            # Delete UV set
            cmds.polyUVSet(obj_name, delete=True, uvSet=uv_set)
            
            # Save current selection state
            selected_objects = cmds.ls(selection=True)
            
            # Re-fetch list but use the saved object list
            self.object_list = current_objects
            
            # Update table and UV set list
            self.update_table_and_lists()
            
            # Restore selection
            if selected_objects:
                cmds.select(selected_objects)
                
        except Exception as e:
            cmds.warning(f"Failed to delete UV set: {str(e)}")

#====== UI Update Functions ======

    def update_table_and_lists(self):
        """Update table and UV set list but keep object list"""
        try:
            # Clear UV set list and table
            self.set_list.clear()
            self.object_table.clear()
            
            # Get all UV sets
            all_sets = set()
            for obj in self.object_list:
                try:
                    sets = cmds.polyUVSet(obj, query=True, allUVSets=True) or []
                    all_sets.update(sets)
                except Exception as e:
                    print(f"Error getting UV sets for object {obj}: {str(e)}")
            
            # Update UV list
            for set_name in sorted(all_sets):
                self.set_list.addItem(set_name)
            
            # Set table columns
            self.object_table.setColumnCount(len(all_sets) + 1)
            headers = [self.texts["column_object"]] + list(sorted(all_sets))
            self.object_table.setHorizontalHeaderLabels(headers)
            
            # Set header style
            header = self.object_table.horizontalHeader()
            header.setStyleSheet("QHeaderView::section { background-color: #3a3a3a; color: white; }")
            
            # Fill table
            self.object_table.setRowCount(len(self.object_list))
            for row, obj in enumerate(self.object_list):
                # Set object name
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
                    print(f"Error filling UV set info for object {obj}: {str(e)}")
            
            self.object_table.resizeColumnsToContents()
            
            # Update total count display
            self.total_label.setText(f"Total: {len(self.object_list)}")
            
            # Trigger UV set selection update
            self.get_objects_from_sets()
            
        except Exception as e:
            cmds.warning(f"Failed to update table and lists: {str(e)}")
    
    def update_uv_set_list(self):
        # Update UV set list on the left
        self.set_list.clear()
        for col in range(1, self.object_table.columnCount()):
            uv_set = self.object_table.horizontalHeaderItem(col).text()
            self.set_list.addItem(uv_set)

#====== Selection Functions ======

    def get_objects_from_sets(self):
        """Update object list and table selection based on selected UV sets"""
        if self._updating:
            return
            
        self._updating = True
        try:
            selected_sets = [item.text() for item in self.set_list.selectedItems()]
            
            # Clear two lists
            self.equal_list.clear()
            self.not_list.clear()
            
            # Highlight objects in the table corresponding to the selected columns
            self.object_table.clearSelection()
            for col in range(self.object_table.columnCount()):
                header_text = self.object_table.horizontalHeaderItem(col).text()
                if header_text in selected_sets:
                    # Select entire column but first check each item exists
                    for row in range(self.object_table.rowCount()):
                        item = self.object_table.item(row, col)
                        if item and item.text():  # Only select if item exists and has content
                            item.setSelected(True)
            
            if not selected_sets:
                # If no UV sets are selected, all objects are displayed in the not list
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
                    
                    # Determine if the object matches based on AND/OR mode
                    if self.and_radio.isChecked():
                        # AND mode: Objects must contain all selected UV sets
                        if all(s in obj_sets for s in selected_sets):
                            equal_objects.append(obj)
                        else:
                            not_objects.append(obj)
                    else:
                        # OR mode: Objects contain any of selected UV sets
                        if any(s in obj_sets for s in selected_sets):
                            equal_objects.append(obj)
                        else:
                            not_objects.append(obj)
                            
                except Exception as e:
                    print(f"Error processing object {obj}: {str(e)}")
                    not_objects.append(obj)
            
            # Update lists
            for obj in equal_objects:
                self.equal_list.addItem(obj)
            for obj in not_objects:
                self.not_list.addItem(obj)
            
            # Update counts
            self.equal_count.setText(str(len(equal_objects)))
            self.not_count.setText(str(len(not_objects)))
            
        finally:
            self._updating = False
    
    def select_objects_from_list(self, list_widget):
        """Select objects from a list"""
        if self._updating:
            return
            
        self._updating = True
        try:
            selected_items = list_widget.selectedItems()
            if selected_items:
                # Unselect the other list
                other_list = self.not_list if list_widget == self.equal_list else self.equal_list
                other_list.clearSelection()
                
                # Select objects
                objects_to_select = [item.text() for item in selected_items]
                cmds.select(objects_to_select)
                
                # Synchronize table selection
                self.object_table.clearSelection()
                for row in range(self.object_table.rowCount()):
                    obj_name = self.object_table.item(row, 0).text()
                    if obj_name in objects_to_select:
                        self.object_table.selectRow(row)
        finally:
            self._updating = False
    
    def select_all_from_list(self, list_widget):
        """Select all objects in a list"""
        all_items = [list_widget.item(i).text() for i in range(list_widget.count())]
        if all_items:
            cmds.select(all_items)
    
    def on_table_selection_changed(self):
        """Handle table selection change"""
        if self._updating:
            return
            
        self._updating = True
        try:
            # Get selected rows
            selected_rows = set(item.row() for item in self.object_table.selectedItems())
            
            # If there are selected rows
            if selected_rows:
                # Get object names corresponding to selected rows
                objects_to_select = []
                for row in selected_rows:
                    obj_name = self.object_table.item(row, 0).text()
                    objects_to_select.append(obj_name)
                
                # Select these objects in Maya
                cmds.select(objects_to_select)
                
                # Clear selection in Equal/Not lists
                self.equal_list.clearSelection()
                self.not_list.clearSelection()
        finally:
            self._updating = False

#====== Context Menu Functions ======

    def show_context_menu(self, pos):
        """Show right-click menu for table cells"""
        item = self.object_table.itemAt(pos)
        if not item:
            return
        
        menu = QtWidgets.QMenu(self)
        obj_name = self.object_table.item(item.row(), 0).text()
        
        if item.column() == 0:  # 对象名称列
            # 添加新建UV set选项
            new_action = menu.addAction(self.texts["menu_new"])
            action = menu.exec_(self.object_table.viewport().mapToGlobal(pos))
            if action == new_action:
                menu.hide()
                self.create_new_uv_set_for_object(obj_name)
        else:  # UV set列
            uv_set = self.object_table.horizontalHeaderItem(item.column()).text()
            
            if self.swap_source_uv is None:
                # 如果没有选择源UV集，按照新的顺序显示菜单项：
                new_action = menu.addAction(self.texts["menu_new"])         # 1. 新建
                copy_action = menu.addAction(self.texts["menu_copy"])       # 2. 复制
                rename_action = menu.addAction(self.texts["menu_rename"])   # 3. 重命名
                menu.addSeparator()                                         # 4. [分隔线]
                get_swap_action = menu.addAction("Get UV Set for Swap")     # 5. 获取交换
                get_reorder_action = menu.addAction("Get UV Set for Reorder") # 6. 获取重排序
                menu.addSeparator()                                         # 7. [分隔线]
                delete_action = menu.addAction(self.texts["menu_delete"])   # 8. 删除
            else:
                # 如果已经选择了源UV集，显示交换选项
                if self.swap_mode == "swap":
                    swap_action = menu.addAction(f"Swap with '{self.swap_source_uv}'")
                else:  # reorder mode
                    swap_action = menu.addAction(f"Reorder with '{self.swap_source_uv}'")
                menu.addSeparator()
                cancel_swap_action = menu.addAction("Cancel Operation")
            
            action = menu.exec_(self.object_table.viewport().mapToGlobal(pos))
            
            if self.swap_source_uv is None:
                if action == get_swap_action:
                    menu.hide()
                    self.swap_source_uv = uv_set
                    self.swap_source_obj = obj_name
                    self.swap_mode = "swap"
                    cmds.inViewMessage(
                        amg=f'<span style="color:#FFA500;">Selected \'{uv_set}\' for swap. Now select another UV set to swap with.</span>', 
                        pos='botRight', fade=True, fst=3, fad=1
                    )
                elif action == get_reorder_action:  # 新增处理
                    menu.hide()
                    self.swap_source_uv = uv_set
                    self.swap_source_obj = obj_name
                    self.swap_mode = "reorder"
                    cmds.inViewMessage(
                        amg=f'<span style="color:#FFA500;">Selected \'{uv_set}\' for reorder. Now select another UV set to reorder with.</span>', 
                        pos='botRight', fade=True, fst=3, fad=1
                    )
                elif action == new_action:
                    menu.hide()
                    self.create_new_uv_set_for_object(obj_name)
                elif action == copy_action:
                    menu.hide()
                    self.copy_uv_set(obj_name, uv_set)
                elif action == rename_action:
                    menu.hide()
                    self.show_rename_dialog(item)
                elif action == delete_action:
                    menu.hide()
                    self.delete_uv_set(item)
            else:
                if action == swap_action:
                    menu.hide()
                    if self.swap_mode == "swap":
                        self.swap_uv_sets(self.swap_source_obj, self.swap_source_uv, obj_name, uv_set)
                    else:  # reorder mode
                        self.reorder_uv_sets(self.swap_source_obj, self.swap_source_uv, obj_name, uv_set)
                    self.swap_source_uv = None
                    self.swap_source_obj = None
                    self.swap_mode = None
                elif action == cancel_swap_action:
                    menu.hide()
                    self.swap_source_uv = None
                    self.swap_source_obj = None
                    self.swap_mode = None
                    cmds.inViewMessage(
                        amg='<span style="color:#FFA500;">Operation cancelled</span>', 
                        pos='botRight', fade=True, fst=3, fad=1
                    )
        
        menu.deleteLater()

    def show_rename_dialog(self, item):
        """Show rename dialog"""
        obj_name = self.object_table.item(item.row(), 0).text()
        old_name = self.object_table.horizontalHeaderItem(item.column()).text()
        
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle(self.texts["dialog_rename_title"])
        dialog.setLabelText(self.texts["dialog_rename_label"])
        dialog.setTextValue(old_name)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.textValue()
            if new_name and new_name != old_name:
                try:
                    # Save current state
                    current_objects = self.object_list.copy()
                    selected_objects = cmds.ls(selection=True)
                    
                    # Rename UV set
                    cmds.polyUVSet(obj_name, rename=True, uvSet=old_name, newUVSet=new_name)
                    
                    # New UI but keep object list
                    self.object_list = current_objects
                    self.update_table_and_lists()
                    
                    # Restore selection
                    if selected_objects:
                        cmds.select(selected_objects)
                        
                except Exception as e:
                    cmds.warning(f"Failed to rename UV set: {str(e)}")

    def delete_uv_sets_by_name(self):
        """Delete all UV sets with the specified name"""
        # Create input dialog
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle(self.texts["menu_delete"])
        dialog.setLabelText(self.texts["dialog_new_label"])
        dialog.setTextValue("")
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            uv_set_name = dialog.textValue()
            if not uv_set_name:
                cmds.warning(self.texts["warning_create_failed"])
                return
            
            try:
                deleted_count = 0
                # Save current state
                current_objects = self.object_list.copy()
                selected_objects = cmds.ls(selection=True)
                
                # Iterate through all objects
                for row in range(self.object_table.rowCount()):
                    obj_name = self.object_table.item(row, 0).text()
                    # Get all UV sets of the object
                    uv_sets = cmds.polyUVSet(obj_name, query=True, allUVSets=True) or []
                    
                    # If the UV set with the specified name is found, delete it
                    if uv_set_name in uv_sets:
                        try:
                            cmds.polyUVSet(obj_name, delete=True, uvSet=uv_set_name)
                            deleted_count += 1
                        except Exception as e:
                            print(f"Error deleting UV set {uv_set_name} for object {obj_name}: {str(e)}")
                
                # Update UI but keep object list
                self.object_list = current_objects
                self.update_table_and_lists()
                
                # Restore selection
                if selected_objects:
                    cmds.select(selected_objects)
                
                # Display result
                if deleted_count > 0:
                    cmds.warning(f"Deleted '{uv_set_name}' UV set from {deleted_count} objects")
                else:
                    cmds.warning(f"UV set '{uv_set_name}' not found")
                
            except Exception as e:
                cmds.warning(f"Failed to delete UV sets by name: {str(e)}")

    def show_header_context_menu(self, pos):
        """Show right-click menu for header"""
        column = self.object_table.horizontalHeader().logicalIndexAt(pos)
        
        menu = QtWidgets.QMenu(self)
        
        if column == 0:  # 对象列
            # 添加新建UV set选项
            new_action = menu.addAction(self.texts["menu_new"])
            action = menu.exec_(self.object_table.horizontalHeader().viewport().mapToGlobal(pos))
            if action == new_action:
                menu.hide()
                self.create_new_uv_set_for_selected()
        else:  # UV set列
            header_item = self.object_table.horizontalHeaderItem(column)
            if not header_item:
                # 空白区域，添加新建UV set选项
                new_action = menu.addAction(self.texts["menu_new"])
                action = menu.exec_(self.object_table.horizontalHeader().viewport().mapToGlobal(pos))
                if action == new_action:
                    menu.hide()
                    self.create_new_uv_set_for_selected()
            else:
                # 现有UV set，显示重命名和删除选项
                uv_set = header_item.text()
                rename_column_action = menu.addAction(self.texts["menu_header_rename_format"].format(uv_set))
                menu.addSeparator()
                delete_column_action = menu.addAction(self.texts["menu_header_delete_format"].format(uv_set))
                
                action = menu.exec_(self.object_table.horizontalHeader().viewport().mapToGlobal(pos))
                if action == delete_column_action:
                    menu.hide()
                    self.delete_column_uv_sets(column)
                elif action == rename_column_action:
                    menu.hide()
                    self.rename_column_uv_sets(column)
        
        menu.deleteLater()

    def delete_column_uv_sets(self, column):
        """Delete all UV sets in the specified column"""
        try:
            uv_set = self.object_table.horizontalHeaderItem(column).text()
            deleted_count = 0
            
            # Save current state
            current_objects = self.object_list.copy()
            selected_objects = cmds.ls(selection=True)
            
            # Iterate through all objects
            for row in range(self.object_table.rowCount()):
                obj_name = self.object_table.item(row, 0).text()
                # Get all UV sets of the object
                uv_sets = cmds.polyUVSet(obj_name, query=True, allUVSets=True) or []
                
                # If the UV set with the specified name is found, delete it
                if uv_set in uv_sets:
                    try:
                        cmds.polyUVSet(obj_name, delete=True, uvSet=uv_set)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting UV set {uv_set} for object {obj_name}: {str(e)}")
            
            # Update UI but keep object list
            self.object_list = current_objects
            self.update_table_and_lists()
            
            # Restore selection
            if selected_objects:
                cmds.select(selected_objects)
            
            # Display result
            if deleted_count > 0:
                cmds.warning(f"Deleted '{uv_set}' UV set from {deleted_count} objects")
            else:
                cmds.warning(f"UV set '{uv_set}' not found")
                
        except Exception as e:
            cmds.warning(f"Failed to delete UV sets by name: {str(e)}")

    def batch_rename_current_uv_set(self, uv_set):
        """Batch rename the current UV set"""
        try:
            # Create rename dialog
            dialog = QtWidgets.QInputDialog(self)
            dialog.setWindowTitle(self.texts["dialog_rename_title"])
            dialog.setLabelText(self.texts["dialog_batch_rename_label"].format(uv_set))
            dialog.setTextValue(uv_set)
            
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                new_name = dialog.textValue()
                if new_name and new_name != uv_set:
                    renamed_count = 0
                    # Save current state
                    current_objects = self.object_list.copy()
                    selected_objects = cmds.ls(selection=True)
                    
                    # Iterate through all objects
                    for row in range(self.object_table.rowCount()):
                        obj_name = self.object_table.item(row, 0).text()
                        # Get all UV sets of the object
                        uv_sets = cmds.polyUVSet(obj_name, query=True, allUVSets=True) or []
                        
                        # If the UV set with the specified name is found, rename it
                        if uv_set in uv_sets:
                            try:
                                cmds.polyUVSet(obj_name, rename=True, uvSet=uv_set, newUVSet=new_name)
                                renamed_count += 1
                            except Exception as e:
                                print(f"Error renaming UV set for object {obj_name}: {str(e)}")
                    
                    # Update UI but keep object list
                    self.object_list = current_objects
                    self.update_table_and_lists()
                    
                    # Restore selection
                    if selected_objects:
                        cmds.select(selected_objects)
                    
                    # Display result
                    if renamed_count > 0:
                        cmds.warning(f"Renamed '{uv_set}' UV set to '{new_name}' for {renamed_count} objects")
                    else:
                        cmds.warning(f"UV set '{uv_set}' not found")
    
        except Exception as e:
            cmds.warning(f"Failed to batch rename UV sets: {str(e)}")

    def rename_column_uv_sets(self, column):
        """Rename all UV sets in the specified column"""
        try:
            uv_set = self.object_table.horizontalHeaderItem(column).text()
            
            # Create rename dialog
            dialog = QtWidgets.QInputDialog(self)
            dialog.setWindowTitle(self.texts["dialog_rename_title"])
            dialog.setLabelText(self.texts["dialog_rename_header_label"].format(uv_set))
            dialog.setTextValue(uv_set)
            
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                new_name = dialog.textValue()
                if new_name and new_name != uv_set:
                    # Save current state
                    current_objects = self.object_list.copy()
                    selected_objects = cmds.ls(selection=True)
                    
                    # First collect all objects that need renaming
                    objects_to_rename = []
                    for row in range(self.object_table.rowCount()):
                        obj_name = self.object_table.item(row, 0).text()
                        uv_sets = cmds.polyUVSet(obj_name, query=True, allUVSets=True) or []
                        if uv_set in uv_sets:
                            objects_to_rename.append(obj_name)
                    
                    if not objects_to_rename:
                        cmds.warning(f"UV set '{uv_set}' not found")
                        return
                    
                    # Perform renaming operation
                    try:
                        # Select objects that need renaming
                        cmds.select(objects_to_rename)
                        # Rename all selected objects' UV sets at once
                        cmds.polyUVSet(rename=True, uvSet=uv_set, newUVSet=new_name)
                        renamed_count = len(objects_to_rename)
                        cmds.warning(f"Renamed '{uv_set}' UV set to '{new_name}' for {renamed_count} objects")
                    except Exception as e:
                        cmds.warning(f"Failed to rename UV sets: {str(e)}")
                    finally:
                        # Restore original selection
                        if selected_objects:
                            cmds.select(selected_objects)
                        else:
                            cmds.select(clear=True)
                
                    # Re-fetch list instead of updating
                    self.object_list = current_objects
                    self.get_set_list()  # Use get_set_list instead of update_table_and_lists
                    
        except Exception as e:
            cmds.warning(f"Failed to rename UV sets: {str(e)}")

    def reorder_uv_sets(self, source_obj, source_uv, target_obj, target_uv):
        """重新排序两个UV集"""
        try:
            # 保存当前状态
            current_objects = self.object_list.copy()
            selected_objects = cmds.ls(selection=True)
            
            # 在源对象上执行重排序
            cmds.polyUVSet(source_obj, reorder=True, uvSet=source_uv, newUVSet=target_uv)
            
            # 如果目标对象与源对象不同，在目标对象上也执行重排序
            if target_obj != source_obj:
                cmds.polyUVSet(target_obj, reorder=True, uvSet=source_uv, newUVSet=target_uv)
            
            # 临时保存当前选择
            temp_selection = cmds.ls(selection=True)
            
            # 选择所有需要显示的对象以确保get_set_list能获取它们
            cmds.select(current_objects)
            
            # 更新UI - 使用get_set_list而不是update_table_and_lists来确保获取最新的UV集顺序
            self.get_set_list()  # 这会重新获取所有UV集并按正确顺序显示
            
            # 恢复原始选择
            if selected_objects:
                cmds.select(selected_objects)
            
            cmds.inViewMessage(
                amg=f'<span style="color:#FFA500;">Reordered UV sets \'{source_uv}\' and \'{target_uv}\'</span>', 
                pos='botRight', fade=True, fst=3, fad=1
            )
            
        except Exception as e:
            cmds.inViewMessage(
                amg=f'<span style="color:#FF0000;">Failed to reorder UV sets: {str(e)}</span>', 
                pos='botRight', fade=True, fst=3, fad=1
            )

#====== Utility Functions ======

    def open_editor(self):
        """Open UV editor"""
        mel.eval('UVSetEditor')

    def open_uv_editor(self):
        """Open UV Editor window"""
        try:
            mel.eval('TextureViewWindow')
        except Exception as e:
            cmds.warning(f"Error opening UV Editor: {str(e)}")

    def open_TransferAttributes(self):
        """Open performTransferAttributes window"""
        mel.eval('performTransferAttributes 1;')
        

        

    def on_mode_changed(self):
        """Handle AND/OR mode switch"""
        if self._updating:
            return
            
        self._updating = True
        try:
            # Save current selection state
            selected_objects = cmds.ls(selection=True)
            
            # Re-calculate Equal/Not lists
            self.get_objects_from_sets()
            
            # Restore selection state
            if selected_objects:
                cmds.select(selected_objects)
                
        finally:
            self._updating = False

    def delete_empty_uv_sets(self):
        """Delete all empty UV sets"""
        try:
            deleted_count = 0
            for row in range(self.object_table.rowCount()):
                obj_name = self.object_table.item(row, 0).text()
                for col in range(1, self.object_table.columnCount()):
                    uv_set = self.object_table.horizontalHeaderItem(col).text()
                    # Check if UV set is empty
                    if cmds.polyUVSet(obj_name, query=True, uvSet=uv_set):
                        if not cmds.polyUVSet(obj_name, query=True, numberOfUVs=True, uvSet=uv_set):
                            cmds.polyUVSet(obj_name, delete=True, uvSet=uv_set)
                            deleted_count += 1
            
            self.update_table_and_lists()
            cmds.warning(f"Deleted {deleted_count} empty UV sets")
        except Exception as e:
            cmds.warning(f"Failed to delete empty UV sets: {str(e)}")

    def copy_uv_sets_to_selected(self):
        """Copy selected UV sets to other selected objects"""
        # Get selected UV sets
        selected_sets = set()
        for item in self.object_table.selectedItems():
            if item.column() > 0:  # Skip object name column
                selected_sets.add(self.object_table.horizontalHeaderItem(item.column()).text())
        
        if not selected_sets:
            cmds.warning(self.texts["warning_create_failed"])
            return
        
        # Get target objects
        target_objects = cmds.ls(selection=True)
        if not target_objects:
            cmds.warning(self.texts["warning_create_failed"])
            return
        
        try:
            for obj in target_objects:
                for uv_set in selected_sets:
                    # Check if target object already has a UV set with the same name
                    existing_sets = cmds.polyUVSet(obj, query=True, allUVSets=True) or []
                    if uv_set not in existing_sets:
                        cmds.polyUVSet(obj, create=True, uvSet=uv_set)
            
            self.update_table_and_lists()
            cmds.warning(f"Copied {len(selected_sets)} UV sets to {len(target_objects)} objects")
        except Exception as e:
            cmds.warning(f"Failed to copy UV sets: {str(e)}")

    def on_table_cell_clicked(self, row, column):
        """Handle table cell click event"""
        if column == 0:  # Skip object column
            return
        
        # Get object and UV set names
        obj_name = self.object_table.item(row, 0).text()
        uv_set = self.object_table.horizontalHeaderItem(column).text()
        
        # Check if cell has UV set
        cell_item = self.object_table.item(row, column)
        if cell_item and cell_item.text():
            try:
                # Select object
                cmds.select(obj_name)
                # Switch UV set
                cmds.polyUVSet(obj_name, currentUVSet=True, uvSet=uv_set)
                cmds.inViewMessage(
                    amg=f'<span style="color:#FFA500;">Switched to UV set: {uv_set}</span>', 
                    pos='botRight', fade=True, fst=3, fad=1
                )
            except Exception as e:
                cmds.inViewMessage(
                    amg=f'<span style="color:#FF0000;">Failed to switch UV set: {str(e)}</span>', 
                    pos='botRight', fade=True, fst=3, fad=1
                )

    def on_header_clicked(self, column):
        """Handle header click event"""
        if column == 0:  # Skip object column
            return
        
        # Get UV set name
        uv_set = self.object_table.horizontalHeaderItem(column).text()
        
        # Get currently selected objects
        selected_objects = cmds.ls(selection=True)
        if selected_objects:
            try:
                # Switch UV set for all selected objects
                for obj in selected_objects:
                    # Check if object has this UV set
                    uv_sets = cmds.polyUVSet(obj, query=True, allUVSets=True) or []
                    if uv_set in uv_sets:
                        cmds.polyUVSet(obj, currentUVSet=True, uvSet=uv_set)
                print(f"Switched to UV set {uv_set} for selected objects")
            except Exception as e:
                cmds.warning(f"Failed to switch UV set: {str(e)}")

    def update_language_button(self):
        """更新语言按钮显示"""
        print(f"Updating language button, current language: {self.current_language}")  # 调试信息
        self.lang_btn.setText("EN" if self.current_language == "zh_CN" else "CN")

    def toggle_language(self):
        """切换界面语言"""
        print("Toggle language called")  # 调试信息
        
        # 切换语言
        self.current_language = "zh_CN" if self.current_language == "en_US" else "en_US"
        print(f"New language: {self.current_language}")  # 调试信息
        
        # 更新文本字典
        self.texts = UI_TEXTS[self.current_language]
        
        # 更新按钮显示
        self.update_language_button()
        
        # 更新窗口标题
        self.setWindowTitle(self.texts["window_title"])
        
        # 更新按钮文本
        self.get_btn.setText(self.texts["btn_get"])
        
        # 更新相等/不相等按钮
        equal_btn = self.findChild(RoundedButton, "equal_btn")
        not_btn = self.findChild(RoundedButton, "not_btn")
        if equal_btn:
            equal_btn.setText(self.texts["btn_equal"])
        if not_btn:
            not_btn.setText(self.texts["btn_not"])
        
        # 更新标签
        self.total_label.setText(self.texts["label_total"].format(len(self.object_list)))
        self.and_radio.setText(self.texts["label_and"])
        self.or_radio.setText(self.texts["label_or"])
        
        # 更新分组框标题
        for group in self.findChildren(QtWidgets.QGroupBox):
            if group.title() == self.texts["group_uv_list"]:
                group.setTitle(self.texts["group_uv_list"])
            elif group.title() == self.texts["group_obj_lists"]:
                group.setTitle(self.texts["group_obj_lists"])
            elif group.title() == self.texts["group_uv_table"]:
                group.setTitle(self.texts["group_uv_table"])
        
        # 更新帮助文本
        self.help_text.setText(self.texts["help_text"])
        
        # 更新表格标题
        if self.object_table.columnCount() > 0:
            self.object_table.horizontalHeaderItem(0).setText(self.texts["column_object"])
        
        # 更新工具提示
        self.editor_btn.setToolTip(self.texts["tooltip_editor"] if "tooltip_editor" in self.texts else "Open UV Editor")
        self.lang_btn.setToolTip(self.texts["tooltip_language"] if "tooltip_language" in self.texts else "Switch Language")
        
        print("Language switch complete")  # 调试信息

    def create_new_uv_set_for_selected(self):
        """为选中的对象创建新的UV set"""
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            # 如果没有选中对象，使用表格中的所有对象
            selected_objects = [self.object_table.item(row, 0).text() 
                                  for row in range(self.object_table.rowCount())]
        
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle(self.texts["dialog_new_title"])
        dialog.setLabelText(self.texts["dialog_new_label"])
        dialog.setTextValue("uvSet1")
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.textValue()
            if new_name:
                try:
                    # 保存当前状态
                    current_objects = self.object_list.copy()
                    
                    # 为所有选中对象创建UV set
                    for obj in selected_objects:
                        try:
                            cmds.polyUVSet(obj, create=True, uvSet=new_name)
                            print(f"Created new UV set: {new_name} on {obj}")
                        except Exception as e:
                            print(f"Error creating UV set for {obj}: {str(e)}")
                    
                    # 更新UI
                    self.object_list = current_objects
                    self.update_table_and_lists()
                    
                    # 恢复选择
                    if selected_objects:
                        cmds.select(selected_objects)
                        
                except Exception as e:
                    cmds.warning(f"Failed to create UV set: {str(e)}")

    def create_new_uv_set_for_object(self, obj_name):
        """为指定对象创建新的UV set"""
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle(self.texts["dialog_new_title"])
        dialog.setLabelText(self.texts["dialog_new_label"])
        dialog.setTextValue("uvSet1")
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.textValue()
            if new_name:
                try:
                    # 保存当前状态
                    current_objects = self.object_list.copy()
                    selected_objects = cmds.ls(selection=True)
                    
                    # 创建UV set
                    cmds.polyUVSet(obj_name, create=True, uvSet=new_name)
                    print(f"Created new UV set: {new_name} on {obj_name}")
                    
                    # 更新UI
                    self.object_list = current_objects
                    self.update_table_and_lists()
                    
                    # 恢复选择
                    if selected_objects:
                        cmds.select(selected_objects)
                        
                except Exception as e:
                    cmds.warning(f"Failed to create UV set: {str(e)}")

    def swap_uv_sets(self, source_obj, source_uv, target_obj, target_uv):
        """交换两个UV集"""
        try:
            # 创建时UV集
            temp_uv_name = f"TempUV_{int(cmds.timerX() * 1000)}"
            
            # 保存当前状态
            current_objects = self.object_list.copy()
            selected_objects = cmds.ls(selection=True)
            
            # 在源对象上执行交换
            cmds.polyUVSet(source_obj, create=True, uvSet=temp_uv_name)
            cmds.polyUVSet(source_obj, copy=True, uvSet=source_uv, newUVSet=temp_uv_name)
            cmds.polyUVSet(source_obj, copy=True, uvSet=target_uv, newUVSet=source_uv)
            cmds.polyUVSet(source_obj, copy=True, uvSet=temp_uv_name, newUVSet=target_uv)
            cmds.polyUVSet(source_obj, delete=True, uvSet=temp_uv_name)
            
            # 如果目标对象与源对象不同，在目标对象上也执行交换
            if target_obj != source_obj:
                cmds.polyUVSet(target_obj, create=True, uvSet=temp_uv_name)
                cmds.polyUVSet(target_obj, copy=True, uvSet=source_uv, newUVSet=temp_uv_name)
                cmds.polyUVSet(target_obj, copy=True, uvSet=target_uv, newUVSet=source_uv)
                cmds.polyUVSet(target_obj, copy=True, uvSet=temp_uv_name, newUVSet=target_uv)
                cmds.polyUVSet(target_obj, delete=True, uvSet=temp_uv_name)
            
            # 更新UI
            self.object_list = current_objects
            self.update_table_and_lists()
            
            # 恢复选择
            if selected_objects:
                cmds.select(selected_objects)
            
            cmds.inViewMessage(
                amg=f'<span style="color:#FFA500;">Swapped UV sets \'{source_uv}\' and \'{target_uv}\'</span>', 
                pos='botRight', fade=True, fst=3, fad=1
            )
            
        except Exception as e:
            cmds.inViewMessage(
                amg=f'<span style="color:#FF0000;">Failed to swap UV sets: {str(e)}</span>', 
                pos='botRight', fade=True, fst=3, fad=1
            )


#====== UI Functions ======

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def show():
    """
    Display the UV Set List tool UI
    
    Function:
    - Close and delete the existing UI instance (if exists)
    - Create a new UI instance and display
    """
    global uvsetlist_window_ui
    try:
        uvsetlist_window_ui.close()
        uvsetlist_window_ui.deleteLater()
    except:
        pass
    parent = maya_main_window()
    uvsetlist_window_ui = UVSetList_Module_UI(parent)
    uvsetlist_window_ui.show()
    uvsetlist_window_ui.raise_()
    uvsetlist_window_ui.activateWindow()

if __name__ == "__main__":
    show()
