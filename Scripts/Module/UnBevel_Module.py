##--------------------------------------------------------------------------
##
## ScriptName : UnBevel Module
## Contents   : UnBevel tool for Maya
## Author     : Megesuts
## Credits    : Special thanks to Joe Wu (http://im3djoe.com) for the original unBevel code
## LastUpdate : 2024/03
##
##--------------------------------------------------------------------------

#====== Imports ======
import maya.cmds as mc
import maya.mel as mel
import math
import re
import maya.api.OpenMaya as om2
from PySide2 import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance



#====== Global Variables ======
viewPortCount = 0
lockCount = 50
screenX = 0
screenY = 0
ppData = []
vLData = []
cLData = []
cumulative_fractions = []

#====== UI Class ======
class RoundedButton(QtWidgets.QPushButton):
    """Custom rounded button class"""
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

class UnBevelUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UnBevelUI, self).__init__(parent)
        self.setWindowTitle("UnBevel Tool")
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.current_language = 'en'
        
        # 定义UI文本字典
        self.ui_text = {
            'en': {
                'window_title': "UnBevel Tool",
                'instructions': "Instructions",
                'tools': "Expand Edge",
                'info_text': ("UnBevel Tool Instructions:\n"
                             "1. Select at least three edge loop\n"
                             "2. Click UnBevel\n"
                             "3. Middle click and drag or \n    drag the parameter slider to resize bevel"),
                'tooltip': ("Hotkeys while dragging:\n"
                          "+ Alt: unbevel with steps 0.1\n"
                          "+ Ctrl + Shift: instant remove bevel\n"
                          "+ Shift: falloff A side\n"
                          "+ Ctrl: falloff B side\n"
                          "+ Ctrl + Shift + Alt: super slow"),
                'select_u': "Vertical ",
                'select_v': "Horizontal ",
                'threshold': "Threshold: {}°",
                'expand_layers': "Expand: {}",
                'unbevel_value': "UnBevel Value:",
                'falloff_a_value': "Falloff A value:",
                'falloff_b_value': "Falloff B value:",
                'apply': "Apply",
                'unbevel': "UnBevel",
                'select_u_tip': "Expand selection vertically based on selected edges",
                'select_v_tip': "Expand selection horizontally based on selected edges"
            },
            'cn': {
                'window_title': "UnBevel 工具",
                'instructions': "使用说明",
                'tools': "拓展边",
                'info_text': ("UnBevel 工具说明：\n"
                             "1. 选择至少三个连续的边环\n"
                             "2. 点击反倒角\n"
                             "3. 中键点击拖动 或 拖拽参数滑条\n   以调整倒角大小"),
                'tooltip': ("快捷键说明：\n"
                          "+ Alt: 以 0.1 的步长移除倒角\n"
                          "+ Ctrl + Shift: 立即移除倒角\n"
                          "+ Shift: A 侧衰减\n"
                          "+ Ctrl: B 侧衰减\n"
                          "+ Ctrl + Shift + Alt: 超慢速模式"),
                'select_u': "垂直方向",
                'select_v': "水平方向",
                'threshold': "平行度阈值: {}°",
                'expand_layers': "扩展层数: {}",
                'unbevel_value': "UnBevel 值:",
                'falloff_a_value': "A侧衰减值:",
                'falloff_b_value': "B侧衰减值:",
                'apply': "应用",
                'unbevel': "反倒角",
                'select_u_tip': "基于选中的边沿垂直方向拓展选择",
                'select_v_tip': "基于选中的边沿水平方向拓展选择"
            }
        }
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def get_text(self, key, *args):
        """获取当前语言的文本"""
        text = self.ui_text[self.current_language][key]
        if args:
            return text.format(*args)
        return text
        
    def update_all_texts(self):
        """更新所有UI文本"""
        self.setWindowTitle(self.get_text('window_title'))
        
        # 更新信息标签
        if self.current_language == 'en':
            self.info_label_en.setText(self.get_text('info_text'))
            self.info_label_en.show()
            self.info_label_cn.hide()
        else:
            self.info_label_cn.setText(self.get_text('info_text'))
            self.info_label_cn.show()
            self.info_label_en.hide()
            
        # 更新按钮和工具提示
        self.init_btn.setToolTip(self.get_text('tooltip'))
        self.select_u_btn.setText(self.get_text('select_u'))
        self.select_v_btn.setText(self.get_text('select_v'))
        
        # 更新滑块标签
        self.update_threshold_label()
        self.update_repeat_label()
        
        # 更新组标题
        self.info_group.setTitle(self.get_text('instructions'))
        self.tool_group.setTitle(self.get_text('tools'))
        
        # 更新其他标签文本
        self.unbevel_value_label.setText(self.get_text('unbevel_value'))
        self.falloff_a_text_label.setText(self.get_text('falloff_a_value'))
        self.falloff_b_text_label.setText(self.get_text('falloff_b_value'))
        self.apply_btn.setText(self.get_text('apply'))
        
        # 更新UnBevel按钮文本
        self.init_btn.setText(self.get_text('unbevel'))
        
        # 更新按钮工具提示
        self.select_u_btn.setToolTip(self.get_text('select_u_tip'))
        self.select_v_btn.setToolTip(self.get_text('select_v_tip'))

    def toggle_language(self):
        """切换语言"""
        self.current_language = 'cn' if self.current_language == 'en' else 'en'
        self.update_all_texts()
        self.update_lang_button_text()

    def update_threshold_label(self):
        """更新阈值标签"""
        value = self.threshold_slider.value()
        self.threshold_label.setText(self.get_text('threshold', value))

    def update_repeat_label(self):
        """更新重复次数标签"""
        value = self.repeat_slider.value()
        self.repeat_label.setText(self.get_text('expand_layers', value))

    def create_widgets(self):
        # create language switch button with rounded style
        self.lang_btn = QtWidgets.QPushButton()
        self.lang_btn.setFixedSize(24, 24)  # 减小尺寸
        self.lang_btn.setStyleSheet("""
            QPushButton {
                background-color: #353535;  /* 更暗的背景色 */
                color: #999999;             /* 更柔和的文字颜色 */
                border: 1px solid #555555;  /* 更细的边框 */
                border-radius: 12px;        /* 圆形按钮 */
                font-weight: bold;
                font-size: 10px;            /* 更小的字体 */
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
        self.update_lang_button_text()

        # create information label with fixed height
        self.info_label_en = QtWidgets.QLabel(self.get_text('info_text'))
        self.info_label_en.setStyleSheet("color: #999999;")
        self.info_label_en.setMinimumHeight(80)  # 设置固定最小高度
        self.info_label_en.setAlignment(QtCore.Qt.AlignTop)  # 文本顶部对齐

        # create Chinese information label with fixed height
        self.info_label_cn = QtWidgets.QLabel(self.get_text('info_text'))
        self.info_label_cn.setStyleSheet("color: #999999;")
        self.info_label_cn.setMinimumHeight(80)  # 设置固定最小高度
        self.info_label_cn.setAlignment(QtCore.Qt.AlignTop)  # 文本顶部对齐
        self.info_label_cn.hide()

        # create initialize button with tooltip
        self.init_btn = RoundedButton(self.get_text('unbevel'), icon=QtGui.QIcon(":polyBevel.png"))
        self.init_btn.setMinimumHeight(40)
        self.init_btn.setToolTip(self.get_text('tooltip'))

        # add UnBevel value slider and label
        self.unbevel_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.unbevel_slider.setMinimum(0)
        self.unbevel_slider.setMaximum(1000)
        self.unbevel_slider.setValue(1000)
        
        self.unbevel_value_label = QtWidgets.QLabel(self.get_text('unbevel_value'))
        self.value_label = QtWidgets.QLabel("100.0")
        self.value_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # add falloff sliders
        self.falloff_a_value_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.falloff_a_value_slider.setMinimum(0)
        self.falloff_a_value_slider.setMaximum(1000)
        self.falloff_a_value_slider.setValue(1000)
        self.falloff_a_value_label = QtWidgets.QLabel("100.0")
        self.falloff_a_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.falloff_a_text_label = QtWidgets.QLabel(self.get_text('falloff_a_value'))
        
        self.falloff_b_value_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.falloff_b_value_slider.setMinimum(0)
        self.falloff_b_value_slider.setMaximum(1000)
        self.falloff_b_value_slider.setValue(1000)
        self.falloff_b_value_label = QtWidgets.QLabel("100.0")
        self.falloff_b_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.falloff_b_text_label = QtWidgets.QLabel(self.get_text('falloff_b_value'))

        # add apply button
        self.apply_btn = RoundedButton("Apply")
        self.apply_btn.setMinimumHeight(35)

        # 添加边选择按
        self.select_u_btn = RoundedButton(self.get_text('select_u'))
        self.select_u_btn.setToolTip(self.get_text('select_u_tip'))
        
        self.select_v_btn = RoundedButton(self.get_text('select_v'))
        self.select_v_btn.setToolTip(self.get_text('select_v_tip'))
        
        # 添加阈值滑块（用于U方向边选择）
        self.threshold_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.threshold_slider.setMinimum(5)
        self.threshold_slider.setMaximum(90)
        self.threshold_slider.setValue(45)
        self.threshold_slider.setSingleStep(5)
        self.threshold_slider.setPageStep(5)
        self.threshold_slider.setTickInterval(5)
        self.threshold_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.threshold_label = QtWidgets.QLabel(self.get_text('threshold', 45))
        
        # 添加重复次数滑块（用于V方向边选择）
        self.repeat_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.repeat_slider.setMinimum(1)
        self.repeat_slider.setMaximum(10)
        self.repeat_slider.setValue(1)
        self.repeat_slider.setSingleStep(1)
        self.repeat_slider.setPageStep(1)
        self.repeat_slider.setTickInterval(1)
        self.repeat_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.repeat_label = QtWidgets.QLabel(self.get_text('expand_layers', 1))

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(7)

        # create information group with fixed height
        self.info_group = QtWidgets.QGroupBox(self.get_text('instructions'))
        self.info_group.setMinimumHeight(120)
        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(5)
        
        # 创建水平布局来放置说明文本和语言切换按钮
        text_button_layout = QtWidgets.QHBoxLayout()
        text_button_layout.setSpacing(5)
        
        # 添加说明文本
        text_widget = QtWidgets.QWidget()
        text_layout = QtWidgets.QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)
        text_layout.addWidget(self.info_label_en)
        text_layout.addWidget(self.info_label_cn)
        text_button_layout.addWidget(text_widget)
        
        # 添加语言切换按钮
        text_button_layout.addWidget(self.lang_btn)
        text_button_layout.setAlignment(self.lang_btn, QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        
        # 将水平布局添加到信息组布局中
        info_layout.addLayout(text_button_layout)
        self.info_group.setLayout(info_layout)

        # create tool group
        self.tool_group = QtWidgets.QGroupBox(self.get_text('tools'))
        tool_layout = QtWidgets.QVBoxLayout()
        
        # 添加边选择控件
        edge_select_layout = QtWidgets.QVBoxLayout()
        
        # U方向边选择
        u_layout = QtWidgets.QHBoxLayout()
        u_layout.addWidget(self.select_u_btn)
        u_layout.addWidget(self.threshold_label)
        u_layout.addWidget(self.threshold_slider)
        edge_select_layout.addLayout(u_layout)
        
        # V方向边选择
        
        v_layout = QtWidgets.QHBoxLayout()
        v_layout.addWidget(self.select_v_btn)
        v_layout.addWidget(self.repeat_label)
        v_layout.addWidget(self.repeat_slider)
        edge_select_layout.addLayout(v_layout)
        
        tool_layout.addLayout(edge_select_layout)
        
        # 添加分隔线
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        tool_layout.addWidget(line)
        
        # add UnBevel button
        tool_layout.addWidget(self.init_btn)
        
        # add UnBevel value slider
        slider_layout = QtWidgets.QHBoxLayout()
        slider_layout.addWidget(self.unbevel_value_label)
        slider_layout.addWidget(self.unbevel_slider)
        slider_layout.addWidget(self.value_label)
        tool_layout.addLayout(slider_layout)
        
        # add falloff A slider
        falloff_a_layout = QtWidgets.QHBoxLayout()
        falloff_a_layout.addWidget(self.falloff_a_text_label)
        falloff_a_layout.addWidget(self.falloff_a_value_slider)
        falloff_a_layout.addWidget(self.falloff_a_value_label)
        tool_layout.addLayout(falloff_a_layout)
        
        # add falloff B slider
        falloff_b_layout = QtWidgets.QHBoxLayout()
        falloff_b_layout.addWidget(self.falloff_b_text_label)
        falloff_b_layout.addWidget(self.falloff_b_value_slider)
        falloff_b_layout.addWidget(self.falloff_b_value_label)
        tool_layout.addLayout(falloff_b_layout)
        
        # add apply button
        tool_layout.addWidget(self.apply_btn)
        
        self.tool_group.setLayout(tool_layout)

        # add to main layout
        main_layout.addWidget(self.info_group)
        main_layout.addWidget(self.tool_group)

    def create_connections(self):
        # add language switch button connection
        self.lang_btn.clicked.connect(self.toggle_language)
        
        
        self.init_btn.clicked.connect(unBevel)
        self.unbevel_slider.valueChanged.connect(self.update_unbevel_value)
        self.apply_btn.clicked.connect(self.apply_and_close)
        
        # 添加边选择按钮的连接
        self.select_u_btn.clicked.connect(self.select_u_direction_edges)
        self.select_v_btn.clicked.connect(self.select_v_direction_edges)
        
        # 添加滑块值变化的连接
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        self.repeat_slider.valueChanged.connect(self.update_repeat_label)
        
        # add falloff slider connections
        self.falloff_a_value_slider.valueChanged.connect(self.update_falloff_a_value)
        self.falloff_b_value_slider.valueChanged.connect(self.update_falloff_b_value)

    def update_unbevel_value(self):
        value = self.unbevel_slider.value() / 10.0
        self.value_label.setText(f"{value:.1f}")
        
        # update model
        global lockCount, viewPortCount
        lockCount = value
        viewPortCount = value
        
        if hasattr(mc, 'refresh'):
            falloff_a = self.falloff_a_value_slider.value() / 10.0
            falloff_b = self.falloff_b_value_slider.value() / 10.0
            
            for i in range(len(ppData)):
                # 计算当前引的衰减因子
                fraction = i / (len(ppData) - 1) if len(ppData) > 1 else 0.5
                falloff = falloff_a + (falloff_b - falloff_a) * fraction
                
                for v in range(len(vLData[i])):
                    moveX = ppData[i][0] - (cLData[i][v][0] * lockCount * (falloff / 100.0))
                    moveY = ppData[i][1] - (cLData[i][v][1] * lockCount * (falloff / 100.0))
                    moveZ = ppData[i][2] - (cLData[i][v][2] * lockCount * (falloff / 100.0))
                    mc.move(moveX, moveY, moveZ, vLData[i][v], absolute=1, ws=1)
            mc.refresh(f=True)
        
    def apply_and_close(self):
        """apply current settings and switch to object mode, also set hard edges"""
        global vLData
        
        # merge vertices
        flattenList = []
        for v in vLData:
            for x in range(len(v)):
                flattenList.append(v[x])
                
        # get original selected edges (before merging)
        meshName = flattenList[0].split('.')[0]
        original_edges = mc.ls('saveSel', fl=True)
        
        # execute merging
        mc.polyMergeVertex(flattenList, d=0.001, am=0, ch=0)
        
        
        # handle selection set
        if mc.objExists('saveSel'):
            mc.select('saveSel')
            mc.delete('saveSel')
        
        # switch to object mode
        mc.selectMode(object=True)
        mc.setToolTo('selectSuperContext')

    def update_lang_button_text(self):
        """update language switch button text"""
        self.lang_btn.setText('CN' if self.current_language == 'en' else 'EN')  # 改为 CN/EN

    def log(self, message):
        """志输出函数"""
        print(message)  # 可以根据需要修改为其他输出方式



## ========== select edge Functions ==========  ##

    ### === U方向边选择函数 === ###
    def select_u_direction_edges(self):
        """选择U方向（平行）的边"""
        try:
            selection = mc.ls(selection=True, flatten=True)
            if not selection:
                self.log("请先选择")
                return
                
            # 确保选择的是边
            if not any(edge for edge in selection if '.e[' in edge):
                self.log("请选择边")
                return
                
            # 保存当前所有选中的边
            current_edges = set(selection)
            mesh = selection[0].split('.')[0]
            
            # 获取所有选中边的相邻边
            all_next_edges = set()
            for current_edge in current_edges:
                # 获取当前边的顶点
                vertices = mc.polyListComponentConversion(current_edge, fromEdge=True, toVertex=True)
                vertices = mc.ls(vertices, flatten=True)
                vertex_positions = [mc.pointPosition(v) for v in vertices]
                
                # 计算当前边的向向量
                edge_vector = [
                    vertex_positions[1][0] - vertex_positions[0][0],
                    vertex_positions[1][1] - vertex_positions[0][1],
                    vertex_positions[1][2] - vertex_positions[0][2]
                ]
                
                # 获取相邻边
                for vertex in vertices:
                    # 获取与顶点相连的所有边
                    connected_edges = mc.polyListComponentConversion(vertex, fromVertex=True, toEdge=True)
                    connected_edges = set(mc.ls(connected_edges, flatten=True))
                    # 移除当前边和已选的边
                    connected_edges = connected_edges - current_edges - all_next_edges
                    
                    for edge in connected_edges:
                        # 获取相邻边的顶点
                        next_vertices = mc.polyListComponentConversion(edge, fromEdge=True, toVertex=True)
                        next_vertices = mc.ls(next_vertices, flatten=True)
                        next_positions = [mc.pointPosition(v) for v in next_vertices]
                        
                        # 计算相邻边的方向向量
                        next_vector = [
                            next_positions[1][0] - next_positions[0][0],
                            next_positions[1][1] - next_positions[0][1],
                            next_positions[1][2] - next_positions[0][2]
                        ]
                        
                        # 计算向量的点积
                        dot_product = sum(a * b for a, b in zip(edge_vector, next_vector))
                        # 计算向量的长度
                        length1 = sum(x * x for x in edge_vector) ** 0.5
                        length2 = sum(x * x for x in next_vector) ** 0.5
                        # 计算夹角的余弦值
                        cos_angle = dot_product / (length1 * length2) if length1 * length2 != 0 else 0
                        
                        # 获取当前阈值
                        threshold_degrees = self.threshold_slider.value()
                        threshold = abs(threshold_degrees / 90.0)  # 转换为余弦值
                        
                        # 如果边平行（夹角接近0°或180°）
                        if abs(abs(cos_angle) - 1) < threshold:
                            # 检查是否与已选边共享顶点
                            if any(v in vertices for v in next_vertices):
                                all_next_edges.add(edge)
                                self.log(f"添加平行边: {edge} (夹角余弦值: {cos_angle})")
            
            # 添加新找到的边到当前选择
            if all_next_edges:
                self.log(f"\n最终添加的边: {list(all_next_edges)}")
                mc.select(list(current_edges))  # 先选择当前所边
                for edge in all_next_edges:
                    mc.select(edge, add=True)  # 添加新边到选择
            else:
                self.log("没有找到符合条件的相邻边")
                mc.select(list(current_edges))  # 保持当前选择
                
            self.log("\n已沿U方向选择边")
            
        except Exception as e:
            self.log(f"选择边失败: {str(e)}")
            import traceback
            self.log(f"错误详情:\n{traceback.format_exc()}")
        finally:
            mc.polySelectConstraint(mode=0)  # 确重置选择约束
    ### === U方向边选择函数结束 === ###

    ### === V方向边选择函数 === ###
    def select_v_direction_edges(self):
        """选择V方向（垂直/横向）的边"""
        selection = mc.ls(selection=True, flatten=True)
        if not selection:
            self.log("请先选择边")
            return
            
        # 确保选择的是边
        if not any(edge for edge in selection if '.e[' in edge):
            self.log("请选择边")
            return
            
        try:
            # 取重复次数
            repeat_count = self.repeat_slider.value()
            
            # 存储原始选择
            original_selection = list(selection)
            processed_edges = set()
            next_edges = set()
            
            # 处理每条边
            for current_edge in selection:
                # 获取相连的面
                faces = mc.polyListComponentConversion(current_edge, tf=True)
                faces = mc.filterExpand(faces, selectionMask=34)
                
                if not faces:
                    continue
                    
                # 对每个面获取下一条边
                for face in faces:
                    next_edge = self.get_next_edge(current_edge, face, mode=1)
                    if next_edge and next_edge not in processed_edges:
                        next_edges.add(next_edge)
                        processed_edges.add(next_edge)
            
            # 重复指定次数
            current_level = next_edges
            for i in range(repeat_count - 1):
                if not current_level:
                    break
                    
                next_level = set()
                for edge in current_level:
                    faces = mc.polyListComponentConversion(edge, tf=True)
                    faces = mc.filterExpand(faces, selectionMask=34)
                    
                    for face in faces:
                        next_edge = self.get_next_edge(edge, face, mode=1)
                        if next_edge and next_edge not in processed_edges:
                            next_level.add(next_edge)
                            processed_edges.add(next_edge)
                
                current_level = next_level
            
            # 选择所有找到的边
            if processed_edges:
                mc.select(original_selection)
                mc.select(list(processed_edges), add=True)
                self.log(f"\n已添加横向边 (重复{repeat_count}次)")
            else:
                self.log("没有找到符合条件的相邻边")
                mc.select(original_selection)
            
        except Exception as e:
            self.log(str(e))
            mc.select(selection)  # 恢复原始选择
            
    ### === V方向边选择函数结束 === ###

    def get_next_edge(self, current_edge, face, mode=0):
        """获取下一条边
        
        Args:
            current_edge: 当前边
            face: 当前面
            mode: 模式（0=环形，1=横向）
            
        Returns:
            str: 下一条边的称，果没找到则返回None
        """
        try:
            # 获取面的所有边
            face_edges = mc.ls(mc.polyListComponentConversion(face, te=True), fl=True)
            if not face_edges:
                return None
                
            # 获取当前边的顶点
            current_vertices = mc.ls(mc.polyListComponentConversion(current_edge, tv=True), fl=True)
            if not current_vertices:
                return None
                
            # 遍历面的所有边
            for edge in face_edges:
                if edge == current_edge:
                    continue
                    
                # 获取边的顶点
                edge_vertices = mc.ls(mc.polyListComponentConversion(edge, tv=True), fl=True)
                if not edge_vertices:
                    continue
                    
                # 检查是否共享顶点
                shared_vertices = set(current_vertices) & set(edge_vertices)
                if len(shared_vertices) > 0:
                    continue
                    
                # 根据模式返回边
                if mode == 0:  # 环形模式
                    return edge
                else:  # 横向模式
                    # 获取当前边的方向量
                    current_pos1 = mc.pointPosition(current_vertices[0])
                    current_pos2 = mc.pointPosition(current_vertices[1])
                    current_vector = [
                        current_pos2[0] - current_pos1[0],
                        current_pos2[1] - current_pos1[1],
                        current_pos2[2] - current_pos1[2]
                    ]
                    
                    # 获取候选边的方向量
                    edge_pos1 = mc.pointPosition(edge_vertices[0])
                    edge_pos2 = mc.pointPosition(edge_vertices[1])
                    edge_vector = [
                        edge_pos2[0] - edge_pos1[0],
                        edge_pos2[1] - edge_pos1[1],
                        edge_pos2[2] - edge_pos1[2]
                    ]
                    
                    # 计算向量的点积
                    dot_product = sum(a * b for a, b in zip(current_vector, edge_vector))
                    # 计算向量的长度
                    length1 = sum(x * x for x in current_vector) ** 0.5
                    length2 = sum(x * x for x in edge_vector) ** 0.5
                    # 计算夹角的余弦值
                    if length1 * length2 == 0:
                        continue
                    cos_angle = dot_product / (length1 * length2)
                    
                    # 果边平行（夹角接近0°或180°）
                    if abs(abs(cos_angle) - 1) < 0.1:  # 允许10度的误差
                        return edge
                        
            return None
            
        except Exception as e:
            self.log(f"获取下一条边时出错: {str(e)}")
            return None

    def update_falloff_a_value(self):
        """更新A侧衰减值"""
        value = self.falloff_a_value_slider.value() / 10.0
        self.falloff_a_value_label.setText(f"{value:.1f}")
        self.update_unbevel_value()  # 更新模型
        
    def update_falloff_b_value(self):
        """更新B侧衰减值"""
        value = self.falloff_b_value_slider.value() / 10.0
        self.falloff_b_value_label.setText(f"{value:.1f}")
        self.update_unbevel_value()  # 更新模型











#====== Core Functions ======
# copied from unBevel1.54.py
def unBevelPress():
    global viewPortCount, lockCount, screenX, screenY
    viewPortCount = 0
    lockCount = 50
    vpX, vpY, _ = mc.draggerContext('unBevelCtx', query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY
    
    mc.headsUpDisplay('HUDunBevelStep',
                     section=3,
                     block=1,
                     blockSize='large',
                     label='unBevel',
                     labelFontSize='large',
                     command=currentStep,
                     atr=1,
                     ao=1)

def unBevelDrag():
    global viewPortCount, lockCount, screenX, screenY, ppData, vLData, cLData
    modifiers = mc.getModifiers()
    vpX, vpY, _ = mc.draggerContext('unBevelCtx', query=True, dragPoint=True)
    
    if modifiers == 5:  # Shift + Ctrl
        for i in range(len(ppData)):
            mc.scale(0, 0, 0, vLData[i], cs=1, r=1, p=(ppData[i][0], ppData[i][1], ppData[i][2]))
        viewPortCount = 0
    else:
        if screenX > vpX:
            lockCount -= 5
        else:
            lockCount += 5
            
        screenX = vpX
        
        if lockCount > 0:
            for i in range(len(ppData)):
                for v in range(len(vLData[i])):
                    moveX = ppData[i][0] - (cLData[i][v][0] * lockCount)
                    moveY = ppData[i][1] - (cLData[i][v][1] * lockCount)
                    moveZ = ppData[i][2] - (cLData[i][v][2] * lockCount)
                    mc.move(moveX, moveY, moveZ, vLData[i][v], absolute=1, ws=1)
            viewPortCount = lockCount
        else:
            viewPortCount = 0.1
            
    mc.refresh(f=True)

def unBevelOff():
    global vLData
    mc.headsUpDisplay('HUDunBevelStep', rem=True)
    flattenList = []
    for v in vLData:
        for x in range(len(v)):
            flattenList.append(v[x])
            
    mc.polyMergeVertex(flattenList, d=0.001, am=0, ch=0)
    mc.select('saveSel')
    meshName = flattenList[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.setToolTo('selectSuperContext')
    
    if mc.objExists('saveSel'):
        mc.delete('saveSel')


def unBevel():
    #checCurrentkHUD =  mc.headsUpDisplay(lh=1)
    #if checCurrentkHUD is not None:
    #    for t in checCurrentkHUD:
    #        mc.headsUpDisplay(t, rem=1)
    global ppData
    global vLData
    global cLData
    global cumulative_fractions
    global storeUniBevelCountA
    global storeUniBevelCountB
    storeUniBevelCountA = 100
    storeUniBevelCountB = 100
    ppData = []
    vLData = []
    cLData = []
    cumulative_fractions = []
    selEdge = mc.filterExpand(expand=True ,sm=32)
    if selEdge:
        if mc.objExists('saveSel'):
            mc.delete('saveSel')
        mc.sets(name="saveSel", text= "saveSel")
        sortGrp =  getEdgeRingGroup()
        for e in sortGrp:
            pPoint,vList,cList = unBevelEdgeLoop(e)  
            ppData.append(pPoint)
            vLData.append(vList)
            cLData.append(cList)
        mc.select(selEdge)
        selEdges = mc.ls(sl=1,fl=1)
        tVer = mc.ls(mc.polyListComponentConversion(selEdges, tv=True), fl=True)
        tFac = mc.ls(mc.polyListComponentConversion(tVer, tf=True,internal=1), fl=True)
        tEdg = mc.ls(mc.polyListComponentConversion(tFac, te=True,internal=1), fl=True)
        findLoop = list(set(tEdg) - set(selEdge))
        goodLoop = []
        if findLoop:
            oneLoop = mc.polySelectSp(findLoop[0],q=1, loop=1)
            oneLoop = mc.ls(oneLoop,fl=1)
            goodLoop = list(set(oneLoop) & set(tEdg))
        else:
            goodLoop = selEdges
        goodLoop = mc.ls(goodLoop,fl=1)
        getCircleState, getVOrder = vtxLoopOrderCheck(goodLoop)
        distances = calculate_edge_distances(getVOrder)
        distances.insert(0, 0)
        total_distance = sum(distances)
        cumulative_fractions = []
        cumulative_sum = 0
        for distance in distances:
            cumulative_sum += distance
            fraction = cumulative_sum / total_distance
            cumulative_fractions.append(round(fraction, 3))    

        global ctx
        ctx = 'unBevelCtx'
        # Delete dragger context if it already exists
        if mc.draggerContext(ctx, exists=True):
            mc.deleteUI(ctx)
        # Create dragger context and set it to the active tool
        mc.draggerContext(ctx, pressCommand = unBevelPress, rc = unBevelOff, dragCommand = unBevelDrag, name=ctx, cursor='crossHair',undoMode='step')
        mc.setToolTo(ctx)

def unBevelOff():
    # 删除UI窗口
    if mc.window('unBevelWindow', exists=True):
        mc.deleteUI('unBevelWindow')
        
    mc.headsUpDisplay( 'HUDunBevelStep',rem=True)
    global vLData
    flattenList = []
    for v in vLData:
        for x in range(len(v)):
            flattenList.append(v[x])   
    mc.polyMergeVertex(flattenList, d=0.001, am=0, ch=0)
    mc.select('saveSel')
    meshName = flattenList[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName +'", "edge");'
    mel.eval(cmd)
    mc.setToolTo('selectSuperContext')
    if mc.objExists('saveSel'):
            mc.delete('saveSel')

def currentStep():
    global viewPortCount
    if viewPortCount >= 1:
        getPercent = viewPortCount/100.0
    elif viewPortCount < 1 and viewPortCount >0:
        getPercent = 0.1
    elif viewPortCount == 0:
        getPercent = 0
    getNumber= '%.2f' % getPercent
    return getNumber
            
def unBevelPress():
    global storeUniBevelCountA
    global storeUniBevelCountB
    global ctx
    global screenX,screenY
    global lockCount
    global storeCount
    global viewPortCount
    viewPortCount = 0
    lockCount = 50
    storeCount = 0
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY
    lockX = vpX
    mc.headsUpDisplay( 'HUDunBevelStep', section=3, block=1, blockSize='large', label='unBevel', labelFontSize='large', command=currentStep, atr=1,ao=1)
    
def unBevelDrag():
    global storeUniBevelCountA
    global storeUniBevelCountB
    global storeCount
    global viewPortCount
    global ppData
    global vLData
    global screenX,screenY
    global lockCount
    global cLData
    global setCurrent
    global cumulative_fractions
    movePN = 0
    modifiers = mc.getModifiers()
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
    if(modifiers == 5):
        for i in range(len(ppData)):
            mc.scale(0,0,0, vLData[i], cs=1, r=1, p= (ppData[i][0],ppData[i][1],ppData[i][2]))
        viewPortCount = 0
    elif(modifiers == 8):
        if screenX > vpX:
            lockCount = lockCount -1
        else:
            lockCount = lockCount + 1
        screenX = vpX
        if lockCount > 0:
            getX = int(lockCount / 10)*10
            if storeCount != getX:
                storeCount = getX
                for i in range(len(ppData)):
                    for v in range(len(vLData[i])):
                        moveX = ppData[i][0] - (cLData[i][v][0]* lockCount)
                        moveY = ppData[i][1] - (cLData[i][v][1]* lockCount)
                        moveZ = ppData[i][2] - (cLData[i][v][2]* lockCount)
                        mc.move(moveX,moveY,moveZ,vLData[i][v], absolute = 1, ws = 1 )
            viewPortCount = storeCount
        else:
            viewPortCount = 0.1
    else:
        if (modifiers == 13):
            if screenX > vpX:
                lockCount = lockCount - 0.1
            else:
                lockCount = lockCount + 0.1
        else:
            if screenX > vpX:
                lockCount = lockCount -5
            else:
                lockCount = lockCount + 5
        screenX = vpX
        if lockCount > 0:
            if(modifiers == 1):
                lockCountA = lockCount
                lockCountB = storeUniBevelCountB
                for i in range(len(ppData)):
                    for v in range(len(vLData[i])):
                        moveX = ppData[i][0] - (cLData[i][v][0] * (lockCountB + ((lockCountA - lockCountB) * cumulative_fractions[i])))
                        moveY = ppData[i][1] - (cLData[i][v][1] * (lockCountB + ((lockCountA - lockCountB) * cumulative_fractions[i])))
                        moveZ = ppData[i][2] - (cLData[i][v][2] * (lockCountB + ((lockCountA - lockCountB) * cumulative_fractions[i])))
                        mc.move(moveX, moveY, moveZ, vLData[i][v], absolute=1, ws=1)
                storeUniBevelCountA = lockCount
            elif (modifiers == 4):
                lockCountA = storeUniBevelCountA
                lockCountB = lockCount
                for i in range(len(ppData)-1):
                    for v in range(len(vLData[i])):
                        moveX = ppData[i][0] - (cLData[i][v][0] * (lockCountB + ((lockCountA - lockCountB) * cumulative_fractions[i])))
                        moveY = ppData[i][1] - (cLData[i][v][1] * (lockCountB + ((lockCountA - lockCountB) * cumulative_fractions[i])))
                        moveZ = ppData[i][2] - (cLData[i][v][2] * (lockCountB + ((lockCountA - lockCountB) * cumulative_fractions[i])))
                        mc.move(moveX, moveY, moveZ, vLData[i][v], absolute=1, ws=1)
                storeUniBevelCountB = lockCount
            else:
                storeUniBevelCountA = lockCount
                storeUniBevelCountB = lockCount
                for i in range(len(ppData)):
                    for v in range(len(vLData[i])):
                        moveX = ppData[i][0] - (cLData[i][v][0]* lockCount)
                        moveY = ppData[i][1] - (cLData[i][v][1]* lockCount)
                        moveZ = ppData[i][2] - (cLData[i][v][2]* lockCount)
                        mc.move(moveX, moveY, moveZ, vLData[i][v], absolute=1, ws=1)
            viewPortCount = lockCount
        else:
            viewPortCount = 0.1
    mc.refresh(f=True)


def unBevelEdgeRing():
    selEdge = mc.filterExpand(expand=True ,sm=32)
    if selEdge:
        if mc.objExists('saveSel'):
            mc.delete('saveSel')
        mc.sets(name="saveSel", text= "saveSel")
        sortGrp =  getEdgeRingGroup()
        for e in sortGrp:
            unBevelEdgeLoop(e)    
        mc.select(selEdge)
        mc.ConvertSelectionToVertices()
        mc.polyMergeVertex(d=0.001, am=0, ch=1)
        mc.select('saveSel')
        mc.delete('saveSel')

def unBevelEdgeLoop(edgelist):
    getCircleState, listVtx = vtxLoopOrderCheck(edgelist)
    checkA = angleBetweenThreeP(listVtx[1],listVtx[0],listVtx[-1])
    angleA = math.degrees(checkA)
    checkB = angleBetweenThreeP(listVtx[-2],listVtx[-1],listVtx[0])
    angleB = math.degrees(checkB)
    angleC = 180 - angleA -angleB
    distanceC = distanceBetween(listVtx[0],listVtx[-1])
    distanceA = distanceC / math.sin(math.radians(angleC)) * math.sin(math.radians(angleA))
    distanceB = distanceC / math.sin(math.radians(angleC)) * math.sin(math.radians(angleB))
    oldDistA = distanceBetween(listVtx[-2],listVtx[-1])
    oldDistB = distanceBetween(listVtx[0],listVtx[1])
    scalarB = distanceB / oldDistB 
    pA = mc.pointPosition(listVtx[0], w =1)
    pB = mc.pointPosition(listVtx[1], w =1)
    newP = [0,0,0]
    newP[0] = ((pB[0]-pA[0])*scalarB) + pA[0]
    newP[1] = ((pB[1]-pA[1])*scalarB) + pA[1]
    newP[2] = ((pB[2]-pA[2])*scalarB) + pA[2]
    listVtx = listVtx[1:-1]
    storeDist = []
    for l in listVtx:
        sotreXYZ = [0,0,0]
        p=mc.xform(l,q=True,t=True,ws=True)
        sotreXYZ[0] = (newP[0] -p[0])/100
        sotreXYZ[1] = (newP[1] -p[1])/100
        sotreXYZ[2] = (newP[2] -p[2])/100
        storeDist.append(sotreXYZ)
    return newP,listVtx,storeDist
    
def distanceBetween(p1,p2):
    pA = mc.pointPosition(p1, w=1)
    pB = mc.pointPosition(p2, w=1)
    dist = math.sqrt(((pA[0] - pB[0])**2) + ((pA[1] - pB[1])**2) + ((pA[2] - pB[2])**2))
    return dist
    
def angleBetweenThreeP(pA, pB, pC):
    a = mc.pointPosition(pA, w=1)
    b = mc.pointPosition(pB, w=1)
    c = mc.pointPosition(pC, w=1)
    # Create vectors from points
    ba = [aa-bb for aa,bb in zip(a,b)]
    bc = [cc-bb for cc,bb in zip(c,b)]
    # Normalize vector
    nba = math.sqrt(sum((x**2.0 for x in ba)))
    ba = [x/nba for x in ba]
    nbc = math.sqrt(sum((x**2.0 for x in bc)))
    bc = [x/nbc for x in bc]
    # Calculate scalar from normalized vectors
    scalar = sum((aa*bb for aa,bb in zip(ba,bc)))
    # calculate the angle in radian
    angle = math.acos(scalar)
    return angle



def vtxLoopOrderCheck(edgelist):
    selEdges = edgelist
    shapeNode = mc.listRelatives(selEdges[0], fullPath=True, parent=True)
    transformNode = mc.listRelatives(shapeNode[0], fullPath=True, parent=True)
    edgeNumberList = []
    for a in selEdges:
        checkNumber = a.split('.')[1].split('\n')[0].split(' ')
        for c in checkNumber:
            findNumber = ''.join([ n for n in c.split('|')[-1] if n.isdigit() ])
            if findNumber:
                edgeNumberList.append(findNumber)

    getNumber = []
    for s in selEdges:
        evlist = mc.polyInfo(s, ev=True)
        checkNumber = evlist[0].split(':')[1].split('\n')[0].split(' ')
        for c in checkNumber:
            findNumber = ''.join([ n for n in c.split('|')[-1] if n.isdigit() ])
            if findNumber:
                getNumber.append(findNumber)

    dup = set([ x for x in getNumber if getNumber.count(x) > 1 ])
    getHeadTail = list(set(getNumber) - dup)
    checkCircleState = 0
    if not getHeadTail:
        checkCircleState = 1
        getHeadTail.append(getNumber[0])
    vftOrder = []
    vftOrder.append(getHeadTail[0])
    count = 0
    while len(dup) > 0 and count < 1000:
        checkVtx = transformNode[0] + '.vtx[' + vftOrder[-1] + ']'
        velist = mc.polyInfo(checkVtx, ve=True)
        getNumber = []
        checkNumber = velist[0].split(':')[1].split('\n')[0].split(' ')
        for c in checkNumber:
            findNumber = ''.join([ n for n in c.split('|')[-1] if n.isdigit() ])
            if findNumber:
                getNumber.append(findNumber)

        findNextEdge = []
        for g in getNumber:
            if g in edgeNumberList:
                findNextEdge = g

        edgeNumberList.remove(findNextEdge)
        checkVtx = transformNode[0] + '.e[' + findNextEdge + ']'
        findVtx = mc.polyInfo(checkVtx, ev=True)
        getNumber = []
        checkNumber = findVtx[0].split(':')[1].split('\n')[0].split(' ')
        for c in checkNumber:
            findNumber = ''.join([ n for n in c.split('|')[-1] if n.isdigit() ])
            if findNumber:
                getNumber.append(findNumber)

        gotNextVtx = []
        for g in getNumber:
            if g in dup:
                gotNextVtx = g

        dup.remove(gotNextVtx)
        vftOrder.append(gotNextVtx)
        count += 1

    if checkCircleState == 0:
        vftOrder.append(getHeadTail[1])
    elif vftOrder[0] == vftOrder[1]:
        vftOrder = vftOrder[1:]
    elif vftOrder[0] == vftOrder[-1]:
        vftOrder = vftOrder[0:-1]
    finalList = []
    for v in vftOrder:
        finalList.append(transformNode[0] + '.vtx[' + v + ']')

    return (checkCircleState, finalList)

        
def getEdgeRingGroup():
    selEdges = mc.ls(sl=1,fl=1)
    tVer = mc.ls(mc.polyListComponentConversion(selEdges, tv=True), fl=True)
    tFac = mc.ls(mc.polyListComponentConversion(tVer, tf=True,internal=1), fl=True)
    tEdg = mc.ls(mc.polyListComponentConversion(tFac, te=True,internal=1), fl=True)
    findLoop = list(set(tEdg) - set(selEdges))
    oneLoop = []
    if findLoop:
        oneLoop = mc.polySelectSp(findLoop[0],q=1, loop=1)
    else:
        oneLoop = selEdges
    oneLoop = mc.ls(oneLoop,fl=1)
    getCircleState, getVOrder = vtxLoopOrderCheck(oneLoop)
    trans = selEdges[0].split(".")[0]
    e2vInfos = mc.polyInfo(selEdges, ev=True)
    e2vDict = {}
    fEdges = []
    for info in e2vInfos:
        evList = [ int(i) for i in re.findall('\\d+', info) ]
        e2vDict.update(dict([(evList[0], evList[1:])]))
    while True:
        try:
            startEdge, startVtxs = e2vDict.popitem()
        except:
            break
        edgesGrp = [startEdge]
        num = 0
        for vtx in startVtxs:
            curVtx = vtx
            while True:
                
                nextEdges = []
                for k in e2vDict:
                    if curVtx in e2vDict[k]:
                        nextEdges.append(k)
                if nextEdges:
                    if len(nextEdges) == 1:
                        if num == 0:
                            edgesGrp.append(nextEdges[0])
                        else:
                            edgesGrp.insert(0, nextEdges[0])
                        nextVtxs = e2vDict[nextEdges[0]]
                        curVtx = [ vtx for vtx in nextVtxs if vtx != curVtx ][0]
                        e2vDict.pop(nextEdges[0])
                    else:
                        break
                else:
                    break
            num += 1
        fEdges.append(edgesGrp)
    retEdges =[]
    for f in fEdges:
        collectList=[]
        for x in f:
            getCom= (trans +".e["+ str(x) +"]")
            collectList.append(getCom)
        retEdges.append(collectList)
    newOrderList = []    
    for g in getVOrder:
        for e in retEdges:
            tVV = mc.ls(mc.polyListComponentConversion(e, tv=True), fl=True,l=1)
            if g in tVV:
                newOrderList.append(e)
    return newOrderList

def get_vertex_position(vertex_name):
    sel_list = om2.MSelectionList()
    sel_list.add(vertex_name)
    dag_path, component = sel_list.getComponent(0)
    vtx_iter = om2.MItMeshVertex(dag_path, component)
    position = vtx_iter.position(om2.MSpace.kWorld)
    return position

def calculate_edge_distances(vertex_list):
    distances = []
    for i in range(len(vertex_list) - 1):
        vtx1 = get_vertex_position(vertex_list[i])
        vtx2 = get_vertex_position(vertex_list[i + 1])
        distance = (vtx2 - vtx1).length()
        distances.append(distance)
    return distances







def show():
    """execute UnBevel"""
    global ppData, vLData, cLData, cumulative_fractions
    ppData = []
    vLData = []
    cLData = []
    cumulative_fractions = []
    
    selEdge = mc.filterExpand(expand=True, sm=32)
    if selEdge:
        if mc.objExists('saveSel'):
            mc.delete('saveSel')
        mc.sets(name="saveSel", text="saveSel")
        sortGrp = getEdgeRingGroup()
        
        for e in sortGrp:
            pPoint, vList, cList = unBevelEdgeLoop(e)
            ppData.append(pPoint)
            vLData.append(vList)
            cLData.append(cList)
            
        # create drag and drop context
        if mc.draggerContext('unBevelCtx', exists=True):
            mc.deleteUI('unBevelCtx')
            
        mc.draggerContext(
            'unBevelCtx',
            pressCommand=unBevelPress,
            dragCommand=unBevelDrag,
            releaseCommand=unBevelOff,
            name='unBevelCtx',
            cursor='crossHair',
            undoMode='step'
        )
        
        mc.setToolTo('unBevelCtx')

#====== UI Functions ======
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def show_ui():
    """display UnBevel tool UI window"""
    global unbevel_window
    try:
        unbevel_window.close()
        unbevel_window.deleteLater()
    except:
        pass
    
    parent = maya_main_window()
    unbevel_window = UnBevelUI(parent)
    unbevel_window.show()

#====== Main ======
if __name__ == "__main__":
    show_ui()
