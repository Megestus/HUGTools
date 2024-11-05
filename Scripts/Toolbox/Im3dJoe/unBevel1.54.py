##--------------------------------------------------------------------------
##
## ScriptName : unBevel
## Author     : Joe Wu
## URL        : http://im3djoe.com
## LastUpdate : 2024/10
##            : unbevel edge ring, there are limitation, it will need at least three edges to calculate unbevel point.
## Version    : 1.0  First version for public test
##            : 1.1  add slide function, can be use for reAdjust bevel size
##            : 1.11 add +shift key for instant unBevel
##            : 1.12 bug fix
##            : 1.14 bug fix in maya 2022
##            : 1.15 adding hud display and steps 0.1
##            : 1.5  adding falloff
##            : 1.51 fix headsUpDisplay bug
##            : 1.53 fixing bug when single edge loop selected
##            : 1.54 fixing bug ls not return seperate item
## Other Note : test in maya 2023.3 windows
##
## Install    : copy and paste script into a python tab in maya script editor
## how to use : select at least three edge loop (also work for multi edge ring), and run the script, recommand assign it to a hot key.
##              click and drag for resize bevel,
##              + alt  : unbevel with steps 0.1  
##              + ctrl + shift: instant remove bevel            
##              + shift: falloff A side
##              + ctrl : falloff B side
##              + ctrl + shift + alt: super slow
##--------------------------------------------------------------------------


import maya.cmds as mc
import math
import re
import maya.mel as mel
import maya.api.OpenMaya as om2


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



unBevel()