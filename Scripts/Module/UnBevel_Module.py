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
        self.current_language = 'en'  # 添加语言状态标记
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # 创建语言切换按钮
        self.lang_btn = QtWidgets.QPushButton()
        self.lang_btn.setFixedSize(24, 24)
        self.lang_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #888888;
            }
        """)
        self.update_lang_button_text()

        # 创建初始化按钮
        self.init_btn = RoundedButton("UnBevel", icon=QtGui.QIcon(":polyBevel.png"))
        self.init_btn.setMinimumHeight(40)

        # 创建说明标签
        self.info_label_en = QtWidgets.QLabel(
            "UnBevel Tool Instructions:\n"
            "1. Select at least three edge loop\n"
            "2. Click UnBevel\n"
            "3. Middle click and drag to resize bevel\n\n"
            "Hotkeys while dragging:\n"
            "+ Alt: unbevel with steps 0.1\n"
            "+ Ctrl + Shift: instant remove bevel\n"
            "+ Shift: falloff A side\n"
            "+ Ctrl: falloff B side\n"
            "+ Ctrl + Shift + Alt: super slow"
        )
        self.info_label_en.setStyleSheet("color: #666666;")

        # 创建中文说明标签
        self.info_label_cn = QtWidgets.QLabel(
            "UnBevel 工具说明：\n"
            "1. 选择至少三个连续的边环\n"
            "2. 点击UnBevel\n"
            "3. 中键点击拖动以调整倒角大小\n\n"
            "快捷键说明：\n"
            "+ Alt: 以 0.1 的步长移除倒角\n"
            "+ Ctrl + Shift: 立即移除倒角\n"
            "+ Shift: A 侧衰减\n"
            "+ Ctrl: B 侧衰减\n"
            "+ Ctrl + Shift + Alt: 超慢速模式"
        )
        self.info_label_cn.setStyleSheet("color: #666666;")
        self.info_label_cn.hide()  # 默认隐藏中文说明

        # 添加UnBevel值滑块
        self.unbevel_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.unbevel_slider.setMinimum(0)
        self.unbevel_slider.setMaximum(1000)  # 对应0-100的值乘以10
        self.unbevel_slider.setValue(1000)     # 修改为1000，对应100.0
        
        self.value_label = QtWidgets.QLabel("100.0")  # 修改默认显示值
        self.value_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # 添加应用按钮
        self.apply_btn = RoundedButton("Apply")
        self.apply_btn.setMinimumHeight(35)

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(7)

        # 创建说明组
        info_group = QtWidgets.QGroupBox("Instructions")
        info_layout = QtWidgets.QVBoxLayout()
        
        # 添加语言切换按钮到右上角
        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(self.lang_btn)
        info_layout.addLayout(title_layout)
        
        # 添加说明标签
        info_layout.addWidget(self.info_label_en)
        info_layout.addWidget(self.info_label_cn)
        info_group.setLayout(info_layout)

        # 创建工具组
        tool_group = QtWidgets.QGroupBox("Tools")
        tool_layout = QtWidgets.QVBoxLayout()
        
        # 添加UnBevel按钮
        tool_layout.addWidget(self.init_btn)
        
        # 添加滑块和值标签
        slider_layout = QtWidgets.QHBoxLayout()
        slider_layout.addWidget(QtWidgets.QLabel("UnBevel Value:"))
        slider_layout.addWidget(self.unbevel_slider)
        slider_layout.addWidget(self.value_label)
        tool_layout.addLayout(slider_layout)
        
        # 添加应用按钮
        tool_layout.addWidget(self.apply_btn)
        
        tool_group.setLayout(tool_layout)

        # 添加到主布局
        main_layout.addWidget(info_group)
        main_layout.addWidget(tool_group)

    def create_connections(self):
        # 添加语言切换按钮的连接
        self.lang_btn.clicked.connect(self.toggle_language)
        
        # 其他连接保持不变...
        self.init_btn.clicked.connect(unBevel)
        self.unbevel_slider.valueChanged.connect(self.update_unbevel_value)
        self.apply_btn.clicked.connect(self.apply_and_close)
        
    def update_unbevel_value(self):
        value = self.unbevel_slider.value() / 10.0
        self.value_label.setText(f"{value:.1f}")
        
        # 更新模型
        global lockCount, viewPortCount
        lockCount = value
        viewPortCount = value
        
        if hasattr(mc, 'refresh'):
            for i in range(len(ppData)):
                for v in range(len(vLData[i])):
                    moveX = ppData[i][0] - (cLData[i][v][0] * lockCount)
                    moveY = ppData[i][1] - (cLData[i][v][1] * lockCount)
                    moveZ = ppData[i][2] - (cLData[i][v][2] * lockCount)
                    mc.move(moveX, moveY, moveZ, vLData[i][v], absolute=1, ws=1)
            mc.refresh(f=True)
            
    def apply_and_close(self):
        """应用当前设置并切换到对象模式，同时设置硬边"""
        global vLData
        
        # 合并顶点
        flattenList = []
        for v in vLData:
            for x in range(len(v)):
                flattenList.append(v[x])
                
        # 获取原始选择的边（在合并前）
        meshName = flattenList[0].split('.')[0]
        original_edges = mc.ls('saveSel', fl=True)
        
        # 执行合并
        mc.polyMergeVertex(flattenList, d=0.001, am=0, ch=0)
        
        
        # 处理选择集
        if mc.objExists('saveSel'):
            mc.select('saveSel')
            mc.delete('saveSel')
        
        # 切换到对象模式
        mc.selectMode(object=True)
        mc.setToolTo('selectSuperContext')

    def update_lang_button_text(self):
        """更新语言切换按钮的文本"""
        self.lang_btn.setText('中' if self.current_language == 'en' else 'En')

    def toggle_language(self):
        """切换显示语言"""
        if self.current_language == 'en':
            self.info_label_en.hide()
            self.info_label_cn.show()
            self.current_language = 'cn'
        else:
            self.info_label_cn.hide()
            self.info_label_en.show()
            self.current_language = 'en'
        self.update_lang_button_text()

















#====== Core Functions ======
# 从unBevel1.54.py复制的代码
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
    pA = mc.pointPosition(p1, w =1)
    pB = mc.pointPosition(p2, w =1)
    dist = math.sqrt( ((pA[0] - pB[0])**2)  + ((pA[1] - pB[1])**2)  + ((pA[2] - pB[2])**2) )
    return dist
    
def angleBetweenThreeP(pA, pB, pC):
    a = mc.pointPosition(pA, w =1)
    b = mc.pointPosition(pB, w =1)
    c = mc.pointPosition(pC, w =1)
    # Create vectors from points
    ba = [ aa-bb for aa,bb in zip(a,b) ]
    bc = [ cc-bb for cc,bb in zip(c,b) ]
    # Normalize vector
    nba = math.sqrt ( sum ( (x**2.0 for x in ba) ) )
    ba = [ x/nba for x in ba ]
    nbc = math.sqrt ( sum ( (x**2.0 for x in bc) ) )
    bc = [ x/nbc for x in bc ]
    # Calculate scalar from normalized vectors
    scalar = sum ( (aa*bb for aa,bb in zip(ba,bc)) )
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
    """执行UnBevel"""
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
            
        # 创建拖拽上下文
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
    """显示UnBevel工具UI窗口"""
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
