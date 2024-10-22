import importlib
import maya.cmds as cmds
import maya.mel as mel
import re
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
import webbrowser
import os


def get_script_path():
    """
    获取当前脚本所在的目录路径
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 导入其他模块
import Toolbox.Editor_Rename_Module as Editor_Rename_Module
import Toolbox.Quick_Rename_Module as Quick_Rename_Module
import Toolbox.UVSetEditor_Module as UVSetEditor_Module
import Toolbox.NormalEdit_Module as NormalEdit_Module

#======UI按钮组件======

class RoundedButton(QtWidgets.QPushButton):
    """
    自定义圆角按钮类
    
    特性:
    - 圆角设计
    - 自定义颜色和悬停效果
    - 粗体文字
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

#======UI主窗口组件======

class HUGToolsUI(QtWidgets.QWidget):
    """
    快速创建工具的主UI类
    
    功能:
    - 创建和管理UI组件
    - 处理用户互动
    - 执行创建操作
    """
    def __init__(self, parent=None):
        super(HUGToolsUI, self).__init__(parent)
        self.setWindowTitle("HUGTOOL")
        self.setMinimumWidth(280)

        # 设置窗口图标
        icon_path = os.path.join(get_script_path(), "Icons", "MainUI.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        else:
            print(f"警告：图标文件 '{icon_path}' 不存在。")

        # 设置窗口标志使其始终置顶
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        # 初始化toggle_state
        self.toggle_state = False
        
        # 初始化语言状态
        self.is_chinese = True
        
        # 初始化翻译字典
        self.translations = {
            "en": {
                "Display Control": "Display Control",
                "Normal": "Normal",
                "Normal Size:": "Normal Size:",
                "NormalEdit": "NormalEdit",
                "Edge Display Control": "Edge Display Control",
                "Soft": "Soft",
                "Hard": "Hard",
                "Select Hard Edges": "Select Hard Edges",
                "Select UV Border Edge": "Select UV Border Edge",
                "Planar Projection": "Planar Projection",
                "UV Layout by Hard Edges": "UV Layout by Hard Edges",
                "Crease Control": "Crease Control",
                "Crease Editor": "Crease Editor",
                "Create Crease Set by Name": "Create Crease Set by Name",
                "Crease V2": "Crease V2",
                "Crease V5": "Crease V5",
                "Toolbox": "Toolbox",
                "QuickRename": "QuickRename",
                "Rename": "Rename",
                "UVSetSwap": "UVSetSwap",
                "document": "document",
                "Help": "Help",
                "Switch Language": "Switch Language"
            },
            "zh": {
                "Display Control": "显示控制",
                "Normal": "法线",
                "Normal Size:": "法线大小：",
                "NormalEdit": "法线编辑",
                "Edge Display Control": "边显示控制",
                "Soft": "软边",
                "Hard": "硬边",
                "Select Hard Edges": "选择硬边",
                "Select UV Border Edge": "选择UV边界边",
                "Planar Projection": "平面投影",
                "UV Layout by Hard Edges": "基于硬边的UV布局",
                "Crease Control": "折痕控制",
                "Crease Editor": "折痕编辑器",
                "Create Crease Set by Name": "按名称创建折痕集",
                "Crease V2": "折痕 V2",
                "Crease V5": "折痕 V5",
                "Toolbox": "工具箱",
                "QuickRename": "快速重命名",
                "Rename": "重命",
                "UVSetSwap": "UV集交换",
                "document": "文档",
                "Help": "帮助",
                "Switch Language": "切换语言"
            }
        }
        
        self.current_language = "en"  # 默认语言为英语
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

#======UI组件======

    def create_widgets(self):
        # 创建帮助按钮
        self.help_btn = QtWidgets.QPushButton("document")
        self.help_btn.setToolTip("帮助")
        self.help_btn.setFixedSize(60, 20)
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: gray;
                font-weight: bold;
            }
            QPushButton:hover {
                color: black;
            }
        """)

        # 创建语言切换按钮
        self.lang_btn = QtWidgets.QPushButton("EN")
        self.lang_btn.setToolTip("切换语言")
        self.lang_btn.setFixedSize(30, 20)
        self.lang_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: gray;
                font-weight: bold;
            }
            QPushButton:hover {
                color: black;
            }
        """)

        # 法线显示模块
        self.display_group = QtWidgets.QGroupBox("Display Control")
        self.toggle_normal_display_btn = RoundedButton("Normal", icon=QtGui.QIcon(":polyNormalSetToFace.png"))
        self.toggle_normal_display_btn.setMinimumSize(100, 40)
        self.toggle_normal_display_btn.setToolTip("Toggle normal display")
        self.normal_size_label = QtWidgets.QLabel("Normal Size:")
        self.normal_size_field = QtWidgets.QDoubleSpinBox()
        self.normal_size_field.setValue(0.4)
        self.normal_size_field.setRange(0.01, 10.0)
        self.normal_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.normal_size_slider.setRange(1, 1000)
        self.normal_size_slider.setValue(40)
        self.open_NormalEdit_btn = RoundedButton("NormalEdit", icon=QtGui.QIcon(":nodeGrapherModeAllLarge.png"))
        self.open_NormalEdit_btn.setToolTip("Open Normal Edit window") 


        # 边显示模块
        self.edge_display_group = QtWidgets.QGroupBox("Edge Display Control")
        self.toggle_softEdge_btn = RoundedButton("Soft", icon=QtGui.QIcon(":polySoftEdge.png"))
        self.toggle_softEdge_btn.setMinimumSize(80, 40)
        self.toggle_softEdge_btn.setToolTip("Toggle soft edge display")
        self.toggle_hardedge_btn = RoundedButton("Hard", icon=QtGui.QIcon(":polyHardEdge.png"))
        self.toggle_hardedge_btn.setMinimumSize(80, 40)
        self.toggle_hardedge_btn.setToolTip("Toggle hard edge display")

        # 选择执行模块
        self.select_hardedges_btn = RoundedButton("Select Hard Edges", icon=QtGui.QIcon(":UVTkEdge.png"))
        self.select_hardedges_btn.setToolTip("Select all hard edges on the mesh")
        self.select_uvborder_btn = RoundedButton("Select UV Border Edge", icon=QtGui.QIcon(":selectTextureBorders.png"))
        self.select_uvborder_btn.setToolTip("Select UV border edges")
        self.planar_projection_btn = RoundedButton("Planar Projection", icon=QtGui.QIcon(":polyCameraUVs.png"))
        self.planar_projection_btn.setToolTip("Apply planar UV projection")
        self.uvlayout_hardedges_btn = RoundedButton("UV Layout by Hard Edges", icon=QtGui.QIcon(":polyLayoutUV.png"))
        self.uvlayout_hardedges_btn.setToolTip("Perform UV layout based on hard edges")

        # 折痕模块
        self.crease_set_group = QtWidgets.QGroupBox("Crease Control")
        self.open_crease_editor_btn = RoundedButton("Crease Editor", icon=QtGui.QIcon(":polyCrease.png"))
        self.create_fixed_crease_set_btn = RoundedButton("Create Crease Set by Name", icon=QtGui.QIcon(":polyCrease.png"))

        self.crease_1_btn = RoundedButton("Crease V2", icon=QtGui.QIcon(":polyCrease.png"))
        self.crease_3_btn = RoundedButton("Crease V5", icon=QtGui.QIcon(":polyCrease.png"))


        #工具箱
        self.Toolbox_group = QtWidgets.QGroupBox("Toolbox")
        self.Toolbox_QuickRename_btn = RoundedButton("QuickRename", icon=QtGui.QIcon(":annotation.png"))
        self.Toolbox_Rename_btn = RoundedButton("Rename", icon=QtGui.QIcon(":quickRename.png"))
        self.Toolbox_UVset_btn = RoundedButton("UVSetSwap", icon=QtGui.QIcon(":polyUVSetEditor.png"))





#======UI布局======
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(7)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 显示控制组布局
        display_layout = QtWidgets.QVBoxLayout()
        normal_display_layout = QtWidgets.QHBoxLayout()
        normal_display_layout.addWidget(self.toggle_normal_display_btn)
        normal_display_layout.addWidget(self.normal_size_label)
        normal_display_layout.addWidget(self.normal_size_field)
        display_layout.addLayout(normal_display_layout)
        display_layout.addWidget(self.normal_size_slider)
        display_layout.addWidget(self.open_NormalEdit_btn)
        self.display_group.setLayout(display_layout)

        # 边显示控制组布局
        edge_display_layout = QtWidgets.QVBoxLayout()
        edge_toggle_layout = QtWidgets.QHBoxLayout()
        edge_toggle_layout.addWidget(self.toggle_softEdge_btn)
        edge_toggle_layout.addWidget(self.toggle_hardedge_btn)
        edge_display_layout.addLayout(edge_toggle_layout)

        edge_display_layout.addWidget(self.select_hardedges_btn)
        edge_display_layout.addWidget(self.select_uvborder_btn)
        edge_display_layout.addWidget(self.planar_projection_btn)
        edge_display_layout.addWidget(self.uvlayout_hardedges_btn)

        self.edge_display_group.setLayout(edge_display_layout)

        # 折痕控制组布局
        crease_layout = QtWidgets.QVBoxLayout()
        crease_layout.addWidget(self.open_crease_editor_btn)
        crease_layout.addWidget(self.create_fixed_crease_set_btn)

        # 创建一个水平布局来容纳两个Crease按钮
        crease_buttons_layout = QtWidgets.QHBoxLayout()
        crease_buttons_layout.addWidget(self.crease_1_btn)
        crease_buttons_layout.addWidget(self.crease_3_btn)

        # 将水平布局添加到折痕控制组布局中
        crease_layout.addLayout(crease_buttons_layout)

        self.crease_set_group.setLayout(crease_layout) 

        #工箱组布局
        Toolbox_layout = QtWidgets.QVBoxLayout()
        Toolbox_layout.addWidget(self.Toolbox_QuickRename_btn)
        Toolbox_layout.addWidget(self.Toolbox_Rename_btn)
        Toolbox_layout.addWidget(self.Toolbox_UVset_btn)
        self.Toolbox_group.setLayout(Toolbox_layout)

        # 将组添加到主布局
        main_layout.addWidget(self.display_group)
        main_layout.addWidget(self.edge_display_group)
        main_layout.addWidget(self.crease_set_group)
        main_layout.addWidget(self.Toolbox_group)

        # 创建底部布局
        bottom_layout = QtWidgets.QHBoxLayout()
        
        # 添加版本信息标签
        version_label = QtWidgets.QLabel("v1.0.0")  # 替换为你的实际版本号
        version_label.setStyleSheet("color: gray; font-size: 10px;")
        bottom_layout.addWidget(version_label)
        
        # 添加弹空间，将帮助和语言按钮推到右侧
        bottom_layout.addStretch()
        
        # 添加帮助和语言按钮
        bottom_layout.addWidget(self.help_btn)
        bottom_layout.addWidget(self.lang_btn)

        # 将底部布局添加到主布局
        main_layout.addLayout(bottom_layout)


#======UI连接====== 

    def create_connections(self):
        # 连接法线显示控制
        self.toggle_normal_display_btn.clicked.connect(self.toggle_normal_display)
        self.normal_size_field.valueChanged.connect(self.set_normal_size_from_field)
        self.normal_size_slider.valueChanged.connect(self.set_normal_size_from_slider)
        self.open_NormalEdit_btn.clicked.connect(self.open_normal_edit)

        # 连接其他按钮
        self.toggle_softEdge_btn.clicked.connect(self.toggle_softEdge_display)
        self.toggle_hardedge_btn.clicked.connect(self.toggle_hardedge_display)
        self.select_uvborder_btn.clicked.connect(self.SelectUVBorderEdge)
        self.select_hardedges_btn.clicked.connect(self.select_hard_edges)
        self.uvlayout_hardedges_btn.clicked.connect(self.UVLayout_By_hardEdges)
        self.planar_projection_btn.clicked.connect(self.apply_planar_projection)

        self.create_fixed_crease_set_btn.clicked.connect(self.create_fixed_crease_set)
        self.open_crease_editor_btn.clicked.connect(self.open_crease_set_editor)
        self.crease_1_btn.clicked.connect(partial(self.apply_crease_preset, 1))
        self.crease_3_btn.clicked.connect(partial(self.apply_crease_preset, 3))

        self.Toolbox_QuickRename_btn.clicked.connect(self.quick_rename)
        self.Toolbox_Rename_btn.clicked.connect(self.rename_edit)
        self.Toolbox_UVset_btn.clicked.connect(self.UVset_swap) 

        # 连接帮助按钮
        self.help_btn.clicked.connect(self.show_help)

        # 连接语言切换按钮
        self.lang_btn.clicked.connect(self.toggle_language)


#======功能函数======
    

    #nomral显示 模块

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




    # 在文件顶部添加这个全局变量
    toggle_state = False

    def toggle_softEdge_display(self):
        """
        切换软边显示状态
        
        功能:
        - 在所有边显示和仅软边显示之间切换
        """
        if self.toggle_state:
            cmds.polyOptions(allEdges=True)
            message = "All Edges"
        else:
            cmds.polyOptions(softEdge=True)
            message = "Soft Edges"
        
        self.toggle_state = not self.toggle_state
        cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)

    def toggle_hardedge_display(self):
        """
        切换硬边显示状态
        
        功能:
        - 在所有边显示和仅硬边显示之间切换
        """
        if self.toggle_state:
            cmds.polyOptions(allEdges=True)
            message = "All Edges"
        else:
            cmds.polyOptions(hardEdge=True)
            message = "Hard Edges"
        
        self.toggle_state = not self.toggle_state
        cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)


    def toggle_normal_display(self):
        sel = cmds.ls(sl=True)
        if sel:
            new_size = self.normal_size_field.value()
            display_state = cmds.polyOptions(q=True, dn=True)[0]
            cmds.polyOptions(dn=not display_state, pt=True, sn=new_size)
            message = "Normals On" if not display_state else "Normals Off"
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">{message}</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.warning("未选择任何对象！")


    



    def SelectUVBorderEdge(*args):
        """
        选择UV边界边
        
        功能:
        - 选择UV边界件
        - 切换到边选择模式
        """
        cmds.SelectUVBorderComponents()
        cmds.selectMode(component=True)
        cmds.selectType(edge=True)
        cmds.inViewMessage(amg='<span style="color:#FFA500;">UV Border Edges</span>', pos='botRight', fade=True, fst=10, fad=1)


    def select_hard_edges(*args):
        """
        选择当前选中对象的所有硬边
        
        功能:
        - 切换到对象式
        - 选择所有硬边
        - 返回选中的硬边列表
        """
        cmds.selectMode(object=True)

        selection = cmds.ls(selection=True, objectsOnly=True)
        if not selection:
            cmds.warning("未选择多边形对象。请选择一个或多个多边形网格。")
            return []
        
        cmds.select(clear=True)
        for obj in selection:
            cmds.select(obj, add=True)
        
        cmds.polySelectConstraint(mode=3, type=0x8000, smoothness=1)
        hard_edges = cmds.ls(selection=True, flatten=True)
        cmds.polySelectConstraint(mode=0)
        
        if hard_edges:
            cmds.inViewMessage(amg='<span style="color:#FFA500;">Hard Edges Selected</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.inViewMessage(amg='<span style="color:#FFA500;">No Hard Edges Found</span>', pos='botRight', fade=True, fst=10, fad=1)
        
        return hard_edges

    def UVLayout_By_hardEdges(self):
        """
        基于硬边执行一系列UV操作-优化展开排布
        
        功能:
        - 对选中的对象执行平面投影
        - 选择硬边并进行UV切割
        - 展开、布局和优化UV
        """

        cmds.selectMode(object=True)  # 强制切换到对象模式

        selection = cmds.ls(selection=True, objectsOnly=True)
        if not selection:
            cmds.warning("未选择多边形对象。请选择一个或多个多边形网格。")
            return

        for obj in selection:
            uv_sets = cmds.polyUVSet(obj, query=True, allUVSets=True)
            if not uv_sets:
                cmds.warning(f"{obj} 没有有效的UV集。跳过此对象。")
                continue

            try:
                cmds.select(f"{obj}.f[*]", r=True)
                cmds.polyProjection(type='Planar', md='p')

                cmds.select(obj)
                hard_edges = self.select_hard_edges()
                if not hard_edges:
                    cmds.warning(f"{obj} 没有硬边。跳过UV切割和展开步骤。")
                    continue

                cmds.select(hard_edges)
                cmds.polyMapCut(ch=1)
                cmds.u3dUnfold(obj, ite=1, p=0, bi=1, tf=1, ms=1024, rs=0)
                cmds.u3dLayout(obj, res=256, scl=1, spc=0.03125, mar=0.03125, box=(0, 1, 0, 1))
                cmds.u3dOptimize(obj, ite=1, pow=1, sa=1, bi=0, tf=1, ms=1024, rs=0)
            except Exception as e:
                cmds.warning(f"处理 {obj} 时错：{str(e)}")
            finally:
                cmds.select(obj)

        cmds.polySelectConstraint(sm=0)  # 复原选择模式
        cmds.selectMode(object=True)  # 确保结束时处于对象模式
        cmds.select(selection)
        cmds.undoInfo(cck=True)
        cmds.warning("基于硬边的UV操作已完成。")

    def apply_planar_projection(self):
        """
        对选中的多边形对象应用平面投影
        
        功能:
        - 选择有面并应用平面投影
        - 处理异常并恢复选择模式
        """
        cmds.selectMode(object=True)  # 强制切到对象模式
        
        selection = cmds.ls(selection=True, objectsOnly=True)
        if selection:
            try:
                faces = [f"{obj}.f[*]" for obj in selection]
                cmds.select(faces, r=True)
                cmds.polyProjection(type='Planar', md='p')
                cmds.undoInfo(cck=True)
            except Exception as e:
                cmds.warning(f"应用平面投影时出错：{e}")
            finally:
                cmds.polySelectConstraint(sm=0)  # 复原选择模式，确保可以选择所有边
                cmds.select(selection, r=True)
                cmds.selectMode(object=True)  # 确保结束时处于对象模式
        else:
            cmds.warning("未选择多边形对象。请选择一个或多个多边形网格。")



    # ===============折痕集函数==============  
    #============== 折痕集函数 =============  


    def get_object_name(self):
        """
        获取当前选中边所属的对象名称，并根据规则决定折痕集名称
        """
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            return ""
        
        # 获取第一个选中项
        first_selected = selection[0]
        
        # 如果选中的是边，提取对象名称
        if '.e[' in first_selected:
            obj_name = first_selected.split('.')[0]
        else:
            obj_name = first_selected
        
        # 使用正则表达式匹配 _Lb, _La, 或 _temp 之前的部分
        match = re.match(r"(.+?)(?:_Lb|_La|_temp)?$", obj_name)
        if match:
            base_name = match.group(1)
        else:
            base_name = obj_name
        
        # 如果基础名称没有 _Lb, _La, 或 _temp 后缀，添加 _set 后缀
        if base_name == obj_name:
            return f"{base_name}_set"
        else:
            return base_name

    def create_fixed_crease_set(self):
        """
        创建或更新固定折痕值为5的折痕集
        
        功能:
        - 选择边时创建新的折痕集或更新现有的折痕集
        - 根据对象名称规则自动生成折痕集名称
        - 将选中的边添加到折痕集中
        - 对折痕集中的所有边应用固定的折痕值5
        
        使用方法:
        1. 选择一个或多个边
        2. 点击"选边按命名创建折痕集"按钮
        
        注意:
        - 如果没有选择边,将显示警告信息
        - 如果已存在匹配的折痕集,将使用现有的折痕集
        - 操作完成后会显示相应的提示信息
        """
        selection = cmds.ls(selection=True, flatten=True)
        if not selection:
            cmds.warning("没有选择任何对象。请选择一个或多个边。")
            return

        # 过滤出边
        edges = [edge for edge in selection if '.e[' in edge]
        
        if not edges:
            cmds.warning("没有选择任何边。请选择一个或多个边。")
            return

        base_name = self.get_object_name()
        
        # 查找所有可能匹配的折痕集
        all_crease_sets = cmds.ls(type="creaseSet")
        matching_crease_sets = [cs for cs in all_crease_sets if cs.startswith(base_name)]

        if matching_crease_sets:
            crease_set_name = matching_crease_sets[0]
            cmds.warning(f"使用现有的折痕集: {crease_set_name}")
        else:
            # 创建新的 creaseSet 节点
            crease_set_name = cmds.createNode('creaseSet', name=base_name)
            cmds.warning(f"创建新的折痕集: {crease_set_name}")

        edges_added = False
        for edge in edges:
            # 检查这条边是否已经在折痕集中
            existing_edges = cmds.sets(crease_set_name, query=True) or []
            if edge not in existing_edges:
                # 将新的边添加到折痕集
                cmds.sets(edge, add=crease_set_name)
                edges_added = True

        if edges_added:
            # 应用固定的褶皱值 5 到整个折痕集
            all_edges = cmds.sets(crease_set_name, query=True) or []
            cmds.polyCrease(all_edges, value=5.0)
            cmds.select(crease_set_name)
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">已更新折痕集: {crease_set_name}, 折痕值设为5，但需要刷新</span>', pos='botRight', fade=True, fst=10, fad=1)
        else:
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">没有新的边添加到折痕集: {crease_set_name}</span>', pos='botRight', fade=True, fst=10, fad=1)

    def open_crease_set_editor(self):
        """
        打开 Maya 的 Crease Set Editor
        """
        try:
            mel.eval('python ("from maya.app.general import creaseSetEditor; creaseSetEditor.showCreaseSetEditor()")')
        except Exception as e:
            cmds.warning(f"无法打开 Crease Set Editor: {str(e)}")
            # 如果上述方法失败，可以考虑打开常规的组件编辑器或显示错误消息
            # cmds.ComponentEditor()

    def apply_crease_preset(self, presetnum):
        """
        应用褶皱预设
        
        能:
        - 对选中的对象或边应用指定的褶皱预设
        - 更新平滑级别和显示设置
        """
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(selection=True, long=True, flatten=True)
            
            if not sel:
                cmds.warning("没有选择任何对象或边。")
                return

            processed_objects = {}

            for obj in sel:
                try:
                    # 检查是否为边组件
                    if '.e[' in obj:
                        mesh = obj.split('.')[0]
                        if mesh not in processed_objects:
                            processed_objects[mesh] = []
                        processed_objects[mesh].append(obj)
                    elif cmds.objectType(obj) == 'transform':
                        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
                        for shape in shapes:
                            if cmds.objectType(shape) == 'mesh':
                                processed_objects[shape] = None
                    elif cmds.objectType(obj) == 'mesh':
                        processed_objects[obj] = None
                except Exception as e:
                    cmds.warning(f"处理对象 {obj} 时出错: {str(e)}")

            for mesh, edges in processed_objects.items():
                self.apply_crease_to_mesh(mesh, presetnum, edges)

            cmds.select(sel, replace=True)
            cmds.inViewMessage(amg=f'<span style="color:#FFA500;">Applied Crease Preset {presetnum}</span>', pos='botRight', fade=True, fst=10, fad=1)
        finally:
            cmds.undoInfo(closeChunk=True)

    def apply_crease_to_mesh(self, mesh, presetnum, specific_edges=None):
        """
        对单个网格或特定边应用折边
        
        功能:
        - 应用褶皱值
        - 设置平滑级别
        - 设置显示平滑网格
        """
        try:
            crease_value = {1: 2.0, 2: 3.0, 3: 5.0}.get(presetnum, 0.0)
            
            if specific_edges:
                # 应用褶皱值到特定边
                cmds.polyCrease(specific_edges, value=crease_value)
            else:
                # 应用褶皱值到所有边
                cmds.polyCrease(f"{mesh}.e[*]", value=crease_value)
            
            # 查询所有边的褶皱值
            all_crease_values = cmds.polyCrease(f"{mesh}.e[*]", query=True, value=True) or [0]
            max_crease = max(all_crease_values)
            
            # 设置平滑级
            smooth_level = max(int(max_crease) + 1, 1)
            cmds.setAttr(f'{mesh}.smoothLevel', smooth_level)
            
            # 设置显示平滑网格
            cmds.setAttr(f'{mesh}.displaySmoothMesh', 2)
        except Exception as e:
            cmds.warning(f"在处理网格 {mesh} 时出错: {str(e)}")





    #外部函数模块

    def open_normal_edit(self):
        importlib.reload(NormalEdit_Module)
        NormalEdit_Module.show_ui()


    #============toolbox 函数模块===============


    def rename_edit(self):
        importlib.reload(Editor_Rename_Module)
        Editor_Rename_Module.show()

    def UVset_swap(self):
        importlib.reload(UVSetEditor_Module)
        UVSetEditor_Module.show()

    def quick_rename(self):
        importlib.reload(Quick_Rename_Module)
        Quick_Rename_Module.show()




    def show_help(self):
        # 指定你想要打开的网站 URL
        help_url = "https://megestus.github.io/HUGweb/"
        webbrowser.open(help_url)

    def toggle_language(self):
        self.current_language = "zh" if self.current_language == "en" else "en"
        self.lang_btn.setText("EN" if self.current_language == "zh" else "中")
        self.retranslate_ui()
        
        # 使用QToolTip显示语言切换信息
        QtWidgets.QToolTip.showText(
            self.lang_btn.mapToGlobal(QtCore.QPoint(0, -30)),
            "语言已切换" if self.current_language == "zh" else "Language switched",
            self.lang_btn
        )

    def retranslate_ui(self):
        lang = self.translations[self.current_language]
        
        # 更新所有UI元素的文本
        self.display_group.setTitle(lang["Display Control"])
        self.toggle_normal_display_btn.setText(lang["Normal"])
        self.normal_size_label.setText(lang["Normal Size:"])
        self.open_NormalEdit_btn.setText(lang["NormalEdit"])
        
        self.edge_display_group.setTitle(lang["Edge Display Control"])
        self.toggle_softEdge_btn.setText(lang["Soft"])
        self.toggle_hardedge_btn.setText(lang["Hard"])
        self.select_hardedges_btn.setText(lang["Select Hard Edges"])
        self.select_uvborder_btn.setText(lang["Select UV Border Edge"])
        self.planar_projection_btn.setText(lang["Planar Projection"])
        self.uvlayout_hardedges_btn.setText(lang["UV Layout by Hard Edges"])
        
        self.crease_set_group.setTitle(lang["Crease Control"])
        self.open_crease_editor_btn.setText(lang["Crease Editor"])
        self.create_fixed_crease_set_btn.setText(lang["Create Crease Set by Name"])
        self.crease_1_btn.setText(lang["Crease V2"])
        self.crease_3_btn.setText(lang["Crease V5"])
        
        self.Toolbox_group.setTitle(lang["Toolbox"])
        self.Toolbox_QuickRename_btn.setText(lang["QuickRename"])
        self.Toolbox_Rename_btn.setText(lang["Rename"])
        self.Toolbox_UVset_btn.setText(lang["UVSetSwap"])
        
        self.help_btn.setText(lang["document"])
        self.help_btn.setToolTip(lang["Help"])
        self.lang_btn.setToolTip(lang["Switch Language"])


def show():
    """
    显示HUG Tools主窗口
    
    这个函数会关闭已存在的窗口（如果有），然后创建并显示一个新的窗口
    使用全局变量main_window来保持对窗口实例的引用
    """
    global main_window
    try:
        # 尝试关闭已存在的窗口
        main_window.close()
        main_window.deleteLater()
    except:
        # 如果窗口不存在，忽略错误
        pass
    
    # 创建新的窗口实例并显示
    main_window = HUGToolsUI()
    main_window.show()

if __name__ == "__main__":
    show()











