# Editor_Rename_Module.py
# Contains UI and related functions for advanced renaming

import re
import maya.cmds as cmds
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

#======UI Button Components======

class RoundedButton(QtWidgets.QPushButton):
    """
    Custom rounded button class
    
    Features:
    - Rounded design
    - Custom color and hover effect
    - Bold text
    """
    def __init__(self, text="", icon=None):
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

#======UI Main Window Component======

class Editor_Rename_Module_UI(QtWidgets.QWidget):
    """
    Main UI class for advanced renaming tool
    
    Features:
    - Create and manage UI components
    - Handle user interactions
    - Execute renaming operations
    """
    def __init__(self, parent=None):
        super(Editor_Rename_Module_UI, self).__init__(parent)
        self.setWindowTitle("Rename Module")
        
        # Set window width
        self.setFixedWidth(300)  # Set width to 300 pixels
        
        # Set window icon
        self.setWindowIcon(QtGui.QIcon(":quickRename.png"))
        
        # Set window flags to always stay on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

#======UI Components======

    def create_widgets(self):
        """
        Create all UI components
        
        Includes:
        - Select All button
        - Rename and Number group
        - Remove Characters group
        - Prefix and Suffix group
        - Search and Replace group
        """
        # Select All button
        self.select_all_btn = RoundedButton("Select All")

        # Rename and Number group
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

        # Remove Characters group
        self.remove_group = QtWidgets.QGroupBox("Remove Characters")
        self.remove_first_btn = RoundedButton("Remove First")
        self.remove_last_btn = RoundedButton("Remove Last")
        self.remove_pasted_btn = RoundedButton("Remove pasted__")
        self.remove_first_field = QtWidgets.QLineEdit("0")
        self.remove_end_field = QtWidgets.QLineEdit("3")
        self.remove_begin_btn = self.create_small_button("-")
        self.remove_all_btn = RoundedButton("Remove")
        self.remove_end_btn = self.create_small_button("-")

        # Prefix and Suffix group
        self.prefix_suffix_group = QtWidgets.QGroupBox("Prefix and Suffix")
        self.prefix_field = QtWidgets.QLineEdit("prefix_")
        self.suffix_field = QtWidgets.QLineEdit("_suffix")
        self.add_prefix_btn = RoundedButton("Add Prefix")
        self.add_suffix_btn = RoundedButton("Add Suffix")

        # Search and Replace group
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


#======UI Layouts======

    def create_layouts(self):
        """
        Create and set up UI layouts
        
        Layouts include:
        - Main layout
        - Rename and Number layout
        - Remove Characters layout
        - Prefix and Suffix layout
        - Search and Replace layout
        """
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(7)
        main_layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(self.select_all_btn)

        # Rename and Number layout
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

        # Remove Characters layout
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

        # Prefix and Suffix layout
        prefix_suffix_layout = QtWidgets.QGridLayout()
        prefix_suffix_layout.addWidget(QtWidgets.QLabel("Prefix:"), 0, 0)
        prefix_suffix_layout.addWidget(self.prefix_field, 0, 1)
        prefix_suffix_layout.addWidget(self.add_prefix_btn, 0, 2)
        prefix_suffix_layout.addWidget(QtWidgets.QLabel("Suffix:"), 1, 0)
        prefix_suffix_layout.addWidget(self.suffix_field, 1, 1)
        prefix_suffix_layout.addWidget(self.add_suffix_btn, 1, 2)
        self.prefix_suffix_group.setLayout(prefix_suffix_layout)
        main_layout.addWidget(self.prefix_suffix_group)

        # Search and Replace layout
        sr_layout = QtWidgets.QVBoxLayout()
        sr_input_layout = QtWidgets.QGridLayout()
        sr_input_layout.addWidget(QtWidgets.QLabel("Search:"), 0, 0)
        sr_input_layout.addWidget(self.search_field, 0, 1)
        sr_input_layout.addWidget(QtWidgets.QLabel("Replace:"), 1, 0)
        sr_input_layout.addWidget(self.replace_field, 1, 1)
        sr_layout.addLayout(sr_input_layout)

        # Create a horizontal layout to center the radio buttons
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

#======UI and Function Connections======

    def create_connections(self):
        """
        Connect UI components to corresponding functions
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
        """Select all objects in the scene"""
        cmds.select(ado=True, hi=True)

    def rename_with_number(self):
        """
        Rename selected objects based on user input
        
        Features:
            - Get user input for new name, start number, and padding digits
            - Call _rename_with_number method to execute renaming
        """
        new_name = self.rename_field.text()
        start_number = int(self.start_value_field.text())
        padding = int(self.padding_value_field.text())
        use_numbers = self.number_radio.isChecked()
        self._rename_with_number(new_name, start_number, padding, use_numbers)

    def _rename_with_number(self, new_name, start_number, padding, use_numbers):
        """
        Rename objects using numbers or letters
        
        Parameters:
        new_name (str): New base name
        start_number (int): Starting number
        padding (int): Number of padding digits
        use_numbers (bool): Whether to use numbers (False uses letters)
        
        Features:
        - Add incrementing numbers or letters suffix to selected objects
        - Use sanitize_name method to ensure names are valid
        """
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            cmds.warning("No objects selected")
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
                cmds.warning(f"Unable to rename {obj}: {str(e)}")

    def remove_chars(self, remove_type):
        """
        Remove characters from object names within a specified range
        
        Parameters:
        remove_type (str): Removal type ("begin", "end", "all")
        
        Features:
        - Delete characters based on user input start and end positions
        - Use sanitize_name method to ensure new names are valid
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
                cmds.warning(f"Unable to rename {obj}: {str(e)}")

    def search_and_replace(self):
        """
        Search and replace text in object names
        
        Features:
        - Get user input for search text and replace text
        - Determine search range (selected, hierarchy, or all)
        - Call _search_and_replace method to execute replacement
        """
        search_text = self.search_field.text()
        replace_text = self.replace_field.text()
        search_method = self.sr_check.checkedId()
        self._search_and_replace(search_text, replace_text, search_method)

    def _search_and_replace(self, search_text, replace_text, search_method):
        """
        Execute search and replace operation
        
        Parameters:
        search_text (str): Text to search
        replace_text (str): Replace text
        search_method (int): Search method (0: Selected, 1: Hierarchy, 2: All)
        
        Features:
        - Select objects based on search method
        - Search and replace text in object names
        - Use sanitize_name method to ensure new names are valid
        - Recursively process all child objects in the hierarchy
        """
        def rename_recursive(obj_list):
            renamed_objects = []
            for obj in obj_list:
                # Check if the object still exists
                if not cmds.objExists(obj):
                    continue
                
                # Get the short name of the object
                short_name = obj.split('|')[-1]
                
                # Skip shape nodes
                if cmds.objectType(obj) == "shape":
                    continue
                
                if search_text in short_name:
                    new_name = self.sanitize_name(short_name.replace(search_text, replace_text))
                    try:
                        renamed = cmds.rename(obj, new_name)
                        renamed_objects.append(renamed)
                        obj = renamed  # Update the object's path name
                    except RuntimeError as e:
                        cmds.warning(f"Unable to rename {obj}: {str(e)}")
                
                # Recursively process child objects
                children = cmds.listRelatives(obj, children=True, fullPath=True) or []
                renamed_objects.extend(rename_recursive(children))
            
            return renamed_objects

        if search_method == 0:  # Selected
            selection = cmds.ls(selection=True, long=True)
        elif search_method == 1:  # Hierarchy
            selection = cmds.ls(selection=True, dag=True, long=True)
        else:  # All
            selection = cmds.ls(dag=True, long=True)

        renamed_objects = rename_recursive(selection)

        # Update selection (if any objects were renamed)
        if renamed_objects:
            cmds.select(renamed_objects, replace=True)
        else:
            cmds.select(clear=True)

        cmds.inViewMessage(amg=f'<span style="color:#fbca82;">Renamed {len(renamed_objects)} objects</span>', pos='botRight', fade=True)

    def create_small_button(self, text):
        """
        Create a small button
        
        Parameters:
        text (str): Button text
        
        Returns:
        QPushButton: Created small button
        """
        btn = QtWidgets.QPushButton(text)
        btn.setFixedSize(20, 20)
        return btn

    def add_prefix_or_suffix(self, is_suffix):
        """
        Add prefix or suffix to selected objects
        
        Parameters:
        is_suffix (bool): If True, add suffix; if False, add prefix
        
        Features:
        - Get user input for prefix or suffix text
        - Add prefix or suffix to selected objects
        - Use sanitize_name method to ensure new names are valid
        - Only process the short name of objects, not affecting their position in the hierarchy
        """
        text = self.suffix_field.text() if is_suffix else self.prefix_field.text()
        selection = cmds.ls(selection=True, long=True)
        renamed_objects = []
        for obj in selection:
            # Get the short name of the object
            short_name = obj.split('|')[-1]
            # Create new name
            new_name = self.sanitize_name(f"{short_name}{text}" if is_suffix else f"{text}{short_name}")
            try:
                # Use long name for renaming, but only change the last part
                renamed = cmds.rename(obj, new_name)
                renamed_objects.append(renamed)
            except RuntimeError as e:
                cmds.warning(f"Unable to rename {short_name}: {str(e)}")

        # Update selection
        if renamed_objects:
            cmds.select(renamed_objects, replace=True)
        else:
            cmds.select(clear=True)

        # Display operation completion message
        cmds.inViewMessage(amg=f'<span style="color:#fbca82;">Added {"suffix" if is_suffix else "prefix"}: {text}</span>', pos='botRight', fade=True)

    def remove_first_or_last_char(self, remove_first):
        """
        Remove the first or last character of object names
        
        Parameters:
        remove_first (bool): If True, remove the first character; if False, remove the last character
        
        Features:
        - Remove specified character from selected object names
        - Use sanitize_name method to ensure new names are valid
        """
        selection = cmds.ls(selection=True)
        for obj in selection:
            new_name = obj[1:] if remove_first else obj[:-1]
            new_name = self.sanitize_name(new_name)
            try:
                cmds.rename(obj, new_name)
            except RuntimeError as e:
                cmds.warning(f"Unable to rename {obj}: {str(e)}")

    def remove_pasted(self):
        """
        Remove 'pasted__' prefix from object names
        
        Features:
        - Process transform nodes and shape nodes
        - Remove 'pasted__' prefix
        - Use sanitize_name method to ensure new names are valid
        """
        # First process transform nodes
        transform_nodes = cmds.ls("pasted__*", long=True, transforms=True)
        for obj in transform_nodes:
            new_name = self.sanitize_name(obj.split("|")[-1][8:])  # Remove "pasted__" prefix
            try:
                cmds.rename(obj, new_name)
            except RuntimeError as e:
                cmds.warning(f"Unable to rename transform node {obj}: {str(e)}")
        
        # Then process shape nodes
        shape_nodes = cmds.ls("pasted__*", long=True, shapes=True)
        for shape in shape_nodes:
            parent = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
            parent_name = cmds.ls(parent, shortNames=True)[0]
            new_shape_name = f"{parent_name}Shape"
            try:
                cmds.rename(shape, new_shape_name)
            except RuntimeError as e:
                cmds.warning(f"Unable to rename shape node {shape}: {str(e)}")

    @staticmethod
    def sanitize_name(name):
        """
        Clean and validate object names
        
        Parameters:
        name (str): Name to be cleaned
        
        Returns:
        str: Cleaned name
        
        Features:
        - Replace illegal characters
        - Ensure name doesn't start with a number
        - Return a valid Maya object name
        """
        name = name.replace(':', '_')
        name = re.sub(r'[^\w|]', '_', name)
        if name[0].isdigit():
            name = '_' + name
        return name



#======Functions======

def test_duplicate_name(obj_name):
    """
    Test for duplicate names
    
    Parameters:
    obj_name (str): Object name to test
    
    Returns:
    str: Short name of the object
    
    Features:
    - Extract short name from full path
    - Handle potential exceptions
    """
    try:
        return obj_name.split("|")[-1]
    except:
        return obj_name
    




#======UI Functions======


def maya_main_window():
    """获取Maya主窗口作为父窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)



def show():
    """
    Display the Editor Rename Module UI
    
    Features:
    - Close and delete existing UI instance (if it exists)
    - Create new UI instance and display
    """
    global rename_window_ui
    try:
        rename_window_ui.close()
        rename_window_ui.deleteLater()
    except:
        pass
    
    parent = maya_main_window()
    rename_window_ui = Editor_Rename_Module_UI(parent)
    rename_window_ui.show()


if __name__ == "__main__":
    show()
