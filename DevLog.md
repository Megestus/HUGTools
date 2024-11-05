# CraesTools Maya 工具集文档

## 项目概述

CraesTools是一个Maya插件,提供UV编辑和对象重命名等功能。它采用模块化设计,易于维护和扩展。

## 项目结构

```
CraesTools/
│
├── init.py
├── CustomTools.py
│
├── ui/
│ ├── init.py
│ ├── custom_ui.py
│ └── rename_ui.py
│
└── tools/
├── init.py
├── rename_operations.py
└── uv_operations.py
```

## 核心组件说明

### CustomTools.py

这是工具集的主入口文件。它创建了主要的 UI 界面，包含多个标签页用于不同的功能。

主要类和函数：
- `CustomToolsUI`: 主 UI 类，创建整个工具集的窗口和标签页。
- `create_ui()`: 创建 UI 实例的函数。
- `get_maya_window()`: 获取 Maya 主窗口的辅助函数。

### ui/custom_ui.py

包含自定义 UI 组件和布局，主要用于 UV 编辑功能。

主要函数：
- `create_edit_tab()`: 创建 UV 编辑标签页的函数。
- `create_uv_frame()`, `create_edge_frame()`, `create_edge_display_frame()`, `create_soft_hard_frame()`: 创建各个功能框架的函数。

### ui/rename_ui.py

包含重命名工具的 UI 类。

主要类：
- `RoundedButton`: 自定义圆角按钮类。
- `RenameUI`: 重命名工具的主 UI 类，包含所有重命名相关的 UI 元素和布局。

### tools/rename_operations.py

包含所有重命名相关的操作函数。

主要函数：
- `sanitize_name()`: 清理和验证对象名称。
- `select_all()`: 选择所有对象。
- `rename_with_number()`: 使用数字或字母重命名对象。
- `remove_first_or_last_char()`: 删除第一个或最后一个字符。
- `remove_pasted()`: 删除 'pasted__' 前缀。
- `remove_chars()`: 删除指定范围的字符。
- `add_prefix_or_suffix()`: 添加前缀或后缀。
- `create_group()`: 创建新组并将选中对象放入其中。
- `search_and_replace()`: 搜索替换对象名称。

### tools/uv_operations.py

包含所有 UV 相关的操作函数。

主要函数：
- `apply_planar_projection()`: 应用平面投影。
- `select_hard_edges()`: 选择硬边。
- `uv_operations_based_on_hard_edges()`: 基于硬边执行 UV 操作。
- `apply_soft_edge_angle()`: 应用软边角度。
- `update_edge_width()`: 更新边的宽度。
- `toggle_softEdge_display()`: 切换软边显示。
- `toggle_hardedge_display()`: 切换硬边显示。
- `select_uv_border_edge()`: 选择 UV 边界。

## 使用说明

1. 将 `CraesTools` 文件夹放置在 Maya 的脚本目录中。
2. 在 Maya 的脚本编辑器中运行以下代码来启动工具：

```python
import CraesTools.CustomTools as CustomTools
from importlib import reload
reload(CustomTools)
CustomTools.create_ui()
```

3. 工具会打开一个包含多个标签页的窗口，每个标签页对应不同的功能：
   - Home: 欢迎页面
   - Editor: UV 编辑工具
        - 显示按钮
            - 显示软硬边
            - 按角度软硬边（滑条）和 应用按钮
            - 显示硬边Color
            - 显示边的宽度
        - 快捷按钮
            - 选硬边
            - 选UV边
            - 平面投影
            - 硬边的UV展开和优化

   - Rename: 重命名工具
        - 选择所有对象。
        - 使用数字或字母重命名对象。
        - 删除第一个或最后一个字符。
        - 删除 'pasted__' 前缀。
        - 删除指定范围的字符。
        - 添加前缀或后缀。
        - 创建新组并将选中对象放入其中。
        - 搜索替换对象名称。
        
   - LOD: LOD 生成工具（尚未实现）

4. 在各个标签页中使用相应的功能进行操作。

## 注意事项

- 确保 Maya 的 Python 路径中包含 `CraesTools` 文件夹的父目录。
- 如果修改了代码，需要重新加载模块才能看到更改效果。
- 部分功能可能需要选中对象才能正常工作。
- 使用重命名功能时，注意 Maya 的命名规则限制。

## 插件架构分析

### 整体结构

插件采用模块化设计,主要分为三个部分:
- CustomTools.py: 主入口文件
- ui/: 包含所有UI相关的代码
- tools/: 包含所有功能实现的代码

### UI和tools的联系

- UI模块(ui/)定义界面布局和用户交互元素
- tools模块(tools/)包含实际的功能实现
- UI模块通过导入tools模块的函数,将用户操作与实际功能连接起来

### 主插件(CustomTools.py)的作用

- 创建主窗口和标签页
- 导入并整合ui和tools模块
- 管理整体界面布局和切换逻辑

### 功能模块划分

- UV编辑功能: ui/custom_ui.py 和 tools/uv_operations.py
- 重命名功能: ui/rename_ui.py 和 tools/rename_operations.py

### 数据流

用户操作 -> UI模块 -> tools模块 -> Maya操作 -> 结果反馈

### 扩展性

这种模块化设计使得添加新功能变得简单,只需在ui和tools中添加相应模块,然后在CustomTools.py中集成即可。

这种架构设计使得代码结构清晰,易于维护和扩展。每个模块都有明确的职责,UI和功能实现分离,有利于团队协作和后续开发。

## 详细架构分析

### UI和功能的分离与联系

UI模块定义了界面,而功能实现在tools模块中。这种分离使得代码更易于维护和扩展。

例如,在rename_ui.py中:

```python
from ..tools import rename_operations

class RenameUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        # ...
        self.rename_number_btn.clicked.connect(self.rename_with_number)

    def rename_with_number(self):
        new_name = self.rename_field.text()
        start_number = int(self.start_value_field.text())
        padding = int(self.padding_value_field.text())
        use_numbers = self.number_radio.isChecked()
        rename_operations.rename_with_number(new_name, start_number, padding, use_numbers)
```

这里,UI类(RenameUI)通过调用rename_operations.py中的函数来执行实际的重命名操作。

### 主插件(CustomTools.py)的集成作用

CustomTools.py作为主入口,整合了所有UI和功能模块。它创建主窗口并管理不同功能页面的切换。

```python
from .ui import custom_ui, rename_ui
from .tools import uv_operations, rename_operations

class CustomToolsUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_window()):
        # ...
        self.edit_tab = custom_ui.create_edit_tab()
        self.rename_tab = rename_ui.RenameUI()
        # ...

    def create_connections(self):
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
```

这里,CustomToolsUI类创建了不同的功能标签页,并管理它们的切换。

### 功能模块的实现

每个功能模块(如rename_operations.py和uv_operations.py)包含了相关的Maya操作函数。

例如,在rename_operations.py中:

```python
import maya.cmds as cmds

def rename_with_number(new_name, start_number, padding, use_numbers):
    selection = cmds.ls(selection=True, long=True)
    for i, obj in enumerate(selection):
        if use_numbers:
            suffix = str(start_number + i).zfill(padding)
        else:
            suffix = letters[i % 26] * (1 + i // 26)
        new_obj_name = sanitize_name(f"{new_name}_{suffix}")
        cmds.rename(obj, new_obj_name)
```

这个函数直接与Maya API交互,执行实际的重命名操作。

### 数据流详解

- 用户在UI中输入参数并点击按钮
- UI类收集参数并调用相应的tools模块函数
- tools模块函数使用Maya命令执行操作
- 操作结果通过Maya反馈给用户(如场景更新或警告消息)

### 扩展性示例

要添加新功能,例如一个新的UV工具:
1. 在tools/中创建新的Python文件(如new_uv_tool.py)
2. 在ui/中创建对应的UI文件(如new_uv_ui.py)
3. 在CustomTools.py中导入新模块并添加到主界面

```python
from .ui import new_uv_ui
from .tools import new_uv_tool

class CustomToolsUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_window()):
        # ...
        self.new_uv_tab = new_uv_ui.NewUVUI()
        self.tab_widget.addTab(self.new_uv_tab, "New UV Tool")
```

这种模块化和分层的设计使得插件易于理解、维护和扩展。每个组件都有明确的职责,同时通过清晰的接口相互协作。

## 扩展模板

以下是如何向CraesTools添加新功能的模板示例。我们将创建一个简单的"物体居中"工具作为示例。

### 创建功能模块 (tools/center_object.py)

首先,在`tools`文件夹中创建一个新的Python文件来实现功能:

```python
# tools/center_object.py
import maya.cmds as cmds

def center_selected_objects():
    """将选中的物体居中到世界坐标原点"""
    selection = cmds.ls(selection=True, type="transform")
    if not selection:
        cmds.warning("请先选择要居中的物体")
        return

    for obj in selection:
        bbox = cmds.xform(obj, query=True, boundingBox=True, worldSpace=True)
        center_x = (bbox[0] + bbox[3]) / 2
        center_y = (bbox[1] + bbox[4]) / 2
        center_z = (bbox[2] + bbox[5]) / 2
        
        cmds.move(-center_x, -center_y, -center_z, obj, relative=True)
    
    cmds.select(selection)
    print(f"已将 {len(selection)} 个物体居中到世界坐标原点")
```

### 创建UI模块 (ui/center_ui.py)

然后,在`ui`文件夹中创建一个新的Python文件来定义UI:

```python
# ui/center_ui.py
from PySide2 import QtWidgets
from ..tools import center_object

class CenterObjectUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CenterObjectUI, self).__init__(parent)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.center_btn = QtWidgets.QPushButton("居中选中物体")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.center_btn)
        main_layout.addStretch()

    def create_connections(self):
        self.center_btn.clicked.connect(center_object.center_selected_objects)
```

### 集成到主插件 (CustomTools.py)

最后,在主插件文件中导入并集成新功能:

```python
# CustomTools.py
from .ui import custom_ui, rename_ui, center_ui  # 导入新的UI模块
from .tools import uv_operations, rename_operations, center_object  # 导入新的功能模块

class CustomToolsUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_window()):
        super(CustomToolsUI, self).__init__(parent)
        # ...现有代码...

        # 添加新的标签页
        self.center_tab = center_ui.CenterObjectUI()
        self.tab_widget.addTab(self.center_tab, "Center Object")

        # ...其余代码保持不变...
```

### 说明

1. **功能模块 (tools/center_object.py)**:
   - 实现核心功能逻辑
   - 使用Maya命令来操作场景
   - 提供清晰的函数接口

2. **UI模块 (ui/center_ui.py)**:
   - 创建用户界面元素
   - 设置布局
   - 连接UI元素到功能模块的函数

3. **主插件集成 (CustomTools.py)**:
   - 导入新的UI和功能模块
   - 创建新功能的标签页
   - 将新标签页添加到主界面

通过遵循这个模板,您可以轻松地向CraesTools添加新的功能,同时保持代码的组织性和可维护性。每个新功能都应该遵循这种模块化的方法,将UI和功能逻辑分离,并通过主插件文件进行集成。

## 补充说明和提醒

1. **版本控制**: 建议使用版本控制系统(如Git)来管理代码,这样可以更好地跟踪变更和协作开发。

2. **错误处理**: 在tools模块的函数中,建议添加更多的错误处理和异常捕获,以提高插件的稳定性。

3. **配置文件**: 考虑添加一个配置文件(如config.py),用于存储可能需要频繁更改的参数,如默认值、颜色设置等。

4. **日志系统**: 实现一个简单的日志系统,记录插件的操作和可能的错误,这对于调试和用户支持很有帮助。

5. **国际化**: 如果计划将插件用于国际用户,考虑实现多语言支持。

6. **性能优化**: 对于可能处理大量数据的操作(如批量重命名),考虑使用更高效的算法或数据结构。

7. **文档更新**: 在添加新功能或修改现有功能时,记得及时更新此README文档。

8. **用户反馈**: 考虑添加一个简单的用户反馈机制,收集用户的建议和报告的问题。

9. **测试**: 编写单元测试和集成测试,确保每个功能模块和整体插件的稳定性。

10. **Maya版本兼容性**: 注意检查和维护对不同Maya版本的兼容性,可能需要针对特定版本进行适配。

通过注意这些方面,您可以进一步提高CraesTools的质量、可用性和可维护性。
