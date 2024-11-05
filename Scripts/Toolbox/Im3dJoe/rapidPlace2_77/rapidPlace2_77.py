##--------------------------------------------------------------------------
##
## ScriptName : rapidPlace
## Contents   : click to place screws from Libaray
## Author     : Joe Wu
## URL        : http://im3djoe.com
## Since      : 2019/11
## LastUpdate : 2024/06/
## Version    : 1.0  First version for public test
##            : 1.01 added vtc lock, screws can lock to target vtx now.
##            : 1.02 imporved vtx lock with slider
##            : 1.03 added subfolder support
##            : 1.04 added random spin
##            : 1.1  rework without normal constraint witch cuase lots of crash
##            : 1.11 remove lock, now use slider to check state,adding depth slider
##            : 1.2  import file via abc to avoid maya crash due to unknow error, eg metalray node ...ect
##            : 1.3  slider update to all in between geo
##            : 1.4  mesh type support mesh instance and gpu
##            : 1.5  multi mesh possibility? / performace fix, no pre scale for first meshSample, global checkVis to avoid self snap
##            : 1.53 multiMode works
##            : 1.55 between slider go live, added random position
##            : 1.56 slider bug fix
##            : 1.57 rePosition button
##            : 1.58 rePosition deBug
##            : 1.59 added decal for place image
##            : 1.60 fix UI bug
##            : 1.61 fixing scale too big when mesh first import
##            : 1.62 added set library path button , rename tool name to rapidPlace as it can place more then screws
##            : 1.63 added sample export button
##            : 1.64 imporve shilft / ctrl Drag to adjust rotation and scale, fix bug on multi Mode
##            : 1.67 fixed Atlas mode broken
##            : 1.7  adding rapidStamp tab
##            : 1.71 debug, after stamp error when doing next stamp
##            : 1.72 adding create tab
##            : 1.73 bug UI fix
##            : 2.03 improve UI
##            : 2.04 add remove icon UI
##            : 2.05 fix snapshot bug when batch export multi mesh, abc export support custom attribute
##            : 2.06 add hung and swing
##            : 2.07 debug update inbetween function
##            : 2.08 add stack mode, there are bugs when mix instance mode with stack mode
##            : 2.09 adding blend mode
##            : 2.10 bug fixing
##            : 2.11 improve autoBridge result ,protect corner when possible
##            : 2.12 improve project sample to surface
##            : 2.13 bug, in between targetGeo, drag reposition not work
##            : 2.14 fixed bug, drag reposition not work
##            : 2.15 improve UI performace
##            : 2.16 adding fit scale
##            : 2.17 adding sliceStamp and quick selections
##            : 2.18 improve create tag, rename folder, better snapshot size
##            : 2.19 place sample to selected faces
##            : 2.20 rePosition work when instance or gpu exist in the scene, but print warning messgae
##            : 2.21 fix missing rename folder function, export with crease info
##            : 2.22 fix display issue, reposition hotkey bug
##            : 2.23 fix UI bug
##            : 2.50 public test for blend mode , mulit mode - not work for decal and altas type of stamp
##            : 2.51 change install method
##            : 2.52 UI improve
##            : 2.53 UI improve, resizeable window, control panel splite bar
##            : 2.54 fix print command for python3
##            : 2.55 fix convertStamp cut too deep
##            : 2.56 import with shader
##            : 2.57 new cage type stamp
##            : 2.58 new snap shot with persp angle also support cage type stamp , cage wireframe toggle
##            : 2.59 export options - edge crease
##            : 2.60 fixing face normal issue
##            : 2.61 fixing stamp now bug
##            : 2.62 fixing convertStamp bug
##            : 2.63 add frame collap on/off buttons
##            : 2.64 bug fix on export boolean type stamp and convertStamp
##            : 2.65 added rename function, but still need a way to refresh icons fast
##            : 2.66 fix bug when using blend stamp mode in maya 2022
##            : 2.67 replace pymel command to reduce error in maya 2022
##            : 2.68 fixed bug when '_' used in Libarary Path
##            : 2.69 fixed bug Mesh Projection when user select offset group instead mesh
##            : 2.70 edgeMode SnapShot, dockable UI
##            : 2.71 fixed stamp blend mode, lock checker box not working
##            : 2.72 bug fix with slide stamp UI
##            : 2.73 imporve blend mode for face with curverture
##            : 2.74 imporve Mesh Projection
##            : 2.76 imporve blend mode for face with curverture by smooth guide mesh
##            : 2.77 fixed export geo does not rename to "meshSample", which break project to mesh function
## Install    : method 1
##              copy python file to user scripts folder
##              C:\Users\xxxx\Documents\maya\202X\scripts\
##
##              run the following to start the tool or drag those to shelf to make a quick button.
##
##              from rapidPlace2_75 import *
##              rapidPlace()
##--------------------------------------------------------------------------
##              method 2
##              remove '#' in the last line
##              copy and paste entire code to a pyhotn script editor
##              run it.
##--------------------------------------------------------------------------

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as OpenMaya
from maya.OpenMaya import MGlobal
import math
import os
import random
import re
import shutil


checkPlugin = mc.pluginInfo('AbcExport', query=True, l=True )
if checkPlugin != True:
    mc.loadPlugin( 'AbcExport' )
checkPlugin = mc.pluginInfo('AbcImport', query=True, l=True )
if checkPlugin != True:
    mc.loadPlugin( 'AbcImport' )

checkPlugin = mc.pluginInfo('gpuCache', query=True, l=True )
if checkPlugin != True:
    mc.loadPlugin( 'gpuCache' )

sourceCMDA = "source dagMenuProc;"
mel.eval(sourceCMDA)
sourceCMDB = "source manipMoveOrient;"
mel.eval(sourceCMDB)


def setMyLibPath():
    global meshDirectory
    if mc.scrollLayout("lib", q =1 , exists = True):
        mc.deleteUI('lib')
    setLibPath = mc.fileDialog2(fm=3, okc='selectFolder', cap='Select Libarary Folder')[0]
    meshDirectory = setLibPath
    mc.textField('libPath', edit =True, tx = meshDirectory )
    jwRefreshIcon(0)

    usd = mc.internalVar(usd=True)
    tempsavePath = usd + 'rapidPlaceLibPath'
    fileWrite = open(tempsavePath, 'w')
    fileWrite.write(meshDirectory)
    fileWrite.close()

def contorlUIToggle():
    checkState = mc.frameLayout('placeControlUI', q=1 ,cl = True)
    if checkState == 1:
        mc.scrollLayout('lib', e=1 ,h= 1000)

    else:
        mc.scrollLayout('lib', e = 1 ,h= 600)
    mc.window("jwMeshPlaceUI", e=1 ,h= 1000)

def jwMeshPlaceUI():
    if mc.window("jwMeshPlaceUI", exists = True):
        mc.deleteUI("jwMeshPlaceUI")
    if mc.dockControl('rapidPlaceDock',q=1,ex=1):
        mc.deleteUI('rapidPlaceDock',control=1)
    global meshDirectory
    usd = mc.internalVar(usd=True)
    tempsavePath = usd + 'rapidPlaceLibPath'
    if os.path.exists(tempsavePath):
        readPath = open(tempsavePath, 'r').read()
        meshDirectory = readPath
    else:
        meshDirectory = 'select your Library Path :)'
    global sampleFileChoice
    sampleFileChoice = []
    global SycList
    SycList = []
    mayaHSize = mc.window('MayaWindow', q=1, h=1)
    jwMeshPlaceUI = mc.window("jwMeshPlaceUI",title = "Rapid Place v2.77", w=480, s = 1, mxb = False,bgc = [0.2, 0.2, 0.2])
    mc.paneLayout(configuration= "horizontal2",ps=(1,10,95))
    mc.frameLayout(labelVisible= False)
    mc.scrollLayout('RPSC',h=(mayaHSize*0.9))
    tabs = mc.tabLayout('rapidTab',cc='jwRefreshIcon(0)',imh=50)
    mc.columnLayout('        Place         ')
    mc.paneLayout(configuration= "horizontal2",ps=(1,50,50))
    mc.columnLayout('PlaceTab')
    mc.rowColumnLayout(nc=3,cw=[(1,80),(2,20),(3,250)])
    mc.text(l ='              Type')
    mc.text(l ='')
    mc.radioButtonGrp('meshImportType', nrb=3, sl=1, labelArray3=['Mesh', 'Instance', 'GPU Cache'], cw = [(1,70),(2,80) ,(3,150)],cc='finishTool()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=6,cw=[(1,80),(2,20),(3,130),(4,40),(5,10),(6,120)])
    mc.text(l ='              Mode')
    mc.text(l ='')
    mc.radioButtonGrp('snapType', nrb=2, sl=1, labelArray2=['Surface', 'Swing'], cw = [(1,60),(2,80)],cc='snapModeToggle()')
    mc.text(l ='     Stack')
    mc.text(l ='')
    mc.radioButtonGrp('stackType', nrb=2, sl=1, labelArray2=['Off', 'On'], cw = [(1,60),(2,80)],cc='stackTypeToggle()')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2, 20),(3,250),(4,50)])
    mc.text(l ='          Rotation')
    mc.text(l ='')
    mc.floatSliderGrp( 'meshRotSlide' ,w= 250, precision= 1, v = 0, field= 1, min= -180, max= 180,dc='updateRotate()',cc='updateRotate()')
    mc.button('jwResetRot', l= 'reset',  c= 'jwMeshResetRot()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=7 ,cw=[(1,100),(2,50),(3,50),(4,50),(5,50),(6,50),(7,50)])
    mc.text(l ='')
    mc.button('jwRotA', l= "-90", c= 'jwMeshSetRot(-90)')
    mc.button('jwRotB', l= "-45", c= 'jwMeshSetRot( -45)')
    mc.button('jwRotC', l= "-30", c= 'jwMeshSetRot( -30)')
    mc.button('jwRotD', l= "30",  c= 'jwMeshSetRot( 30)')
    mc.button('jwRotE', l= "45",  c= 'jwMeshSetRot( 45)')
    mc.button('jwRotF', l= "90",  c= 'jwMeshSetRot( 90)')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2, 20),(3,250),(4,50)])
    mc.text(l ='          Random')
    mc.text(l ='')
    mc.floatSliderGrp( 'randomRotSlide' ,w= 250, precision = 0, v = 0, field= 1, min= 0, max= 360,dc='updateRotateRandom()',cc='updateRotateRandom()')
    mc.button('jwResetRandomRot', l= 'reset',  c= 'jwMeshResetRandomRot()')
    mc.text('swingText', l ='          Swing')
    mc.text(l ='')
    mc.floatSliderGrp( 'randomSwingSlide' ,w= 250, precision = 0, v = 0, field= 1, min= 0, max= 90,dc='updateSwingRandom()',cc='updateSwingRandom()')
    mc.button('jwResetSwingSlide', l= 'reset', en=0, c= 'jwMeshResetSwingSlide()')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2,20),(3,250),(4,50)])
    mc.text(l ='              Scale')
    mc.text(l ='')
    mc.floatSliderGrp( 'meshScaleSlide' ,v = 1,  precision= 1, field= 1, min= 0.1, max= 5, dc='updateScale()',cc='updateScale()')
    mc.button('meshScaleReset', l= 'reset',  c= 'jwMeshResetScale()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2, 20),(3,250),(4,50)])
    mc.text(l ='          Random')
    mc.text(l ='')
    mc.floatSliderGrp( 'randomScaleSlide' ,w= 250, precision = 2, v = 0, field= 1, min= 0, max= 1,dc='updateRandomScale()',cc='updateRandomScale()')
    mc.button('jwResetRandomScale', l= 'reset',  c= 'jwMeshResetRandomScale()')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2,20),(3,250),(4,50)])
    mc.text(l ='            Between')
    mc.text(l ='')
    mc.floatSliderGrp( 'meshBetweenSlide' ,v = 0,  precision= 0,  field= 1, min= 0, max= 10,cc='updateBetween()')
    mc.button('meshBetweenReset', l= 'reset',  c= 'jwMeshResetBetween()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2,20),(3,250),(4,50)])
    mc.text(l ='    Random Pos')
    mc.text(l ='')
    mc.floatSliderGrp( 'meshBetweenRandomSlide' ,v = 0,  precision= 2,  field= 1, min= 0, max= 1,dc='updateBetweenRandom()',cc='updateBetweenRandom()')
    mc.button('meshBetweenRandomReset', l= 'reset',  c= 'jwMeshResetBetweenRandom()')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2,20),(3,250),(4,50)])
    mc.text(l ='              Depth')
    mc.text(l ='')
    mc.floatSliderGrp( 'meshDepthSlide' ,v = 0,  precision= 2, field= 1, min= -1, max= 5,dc='updateDepth()',cc='updateDepth()')
    mc.button('meshDepthReset', l= 'reset',  c= 'jwMeshResetDepth()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2,20),(3,250),(4,50)])
    mc.text(l ='               Snap')
    mc.text(l ='')
    mc.floatSliderGrp( 'snapVSlider' ,v = 0,  precision= 2, field= 1, min= 0, max= 5)
    mc.button('snapVReset', l= 'reset',  c= 'jwMeshResetSnapV()')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=6,cw=[(1,80),(2,20),(3,190),(4,50),(5,10),(6,50)])
    mc.text(l ='     MultiMode')
    mc.text(l ='')
    mc.radioButtonGrp('meshMultiMode', nrb=2, sl=1, labelArray2=['Off', 'On'], cw = [(1,70),(2,80)],cc='multiButtonToggle()')
    mc.button('multiCleanButton',l= 'Clean', en=False, c= 'iconLightOff()')
    mc.text(l ='')
    mc.button('goMultiButton',  l= 'GO', en=False,  c= 'goPressMulti()')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=6,cw=[(1,80),(2,20),(3,90),(4,10),(5,90),(6,10)])
    mc.text(l ='     Quick Tool')
    mc.text(l ='')
    mc.button('rePostioinButton',  l= 'Drag rePosition', en=True,  c= 'moveIt()')
    mc.text(l ='')
    mc.button('projectMeshButtonA',  l= 'Mesh Projection', en=True,  c= 'projectMesh()')
    mc.text(l ='')
    mc.text(l ='',h=20)
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=4,cw=[(1,380),(2,20),(3,5),(4,20)])
    mc.text(l ='')
    mc.button(l= '+',c= 'frameCollap(0)')
    mc.text(l ='')
    mc.button(l= '-',c= 'frameCollap(1)')
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.frameLayout('splitBar',labelVisible= False)
    mc.scrollLayout('lib')
    mc.frameLayout('libIcons', bgc =[0.265, 0.265, 0.265])
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    #######################################################################################################
    mc.columnLayout('        Stamp         ')
    mc.separator(height= 10, style= 'in')
    mc.columnLayout('StampTab')
    mc.rowColumnLayout(nc=5,cw=[(1,80),(2,20),(3,160),(4,70),(5,60)])
    mc.text(l ='              Mode')
    mc.text(l ='')
    mc.radioButtonGrp('stampType', nrb=2, sl=1, labelArray2=['Boolean', 'Blend'], cw = [(1,100),(2,10)],cc='stampModeToggle()' )
    mc.checkBox('deformState', label= "Deform" , en=False,cc='stampCurvatureToggle()')
    mc.checkBox('borderState', label= "Border", en=False )
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=7 ,cw=[(1,80),(2,20),(3,50),(4,50),(5,60),(6,90),(7,50)])
    mc.text('lockText',l ='              Lock',en=False)
    mc.text(l ='')
    mc.checkBox('lockRot', label= "Rot" , en=False, cc='stampLockUpdate()')
    mc.checkBox('lockScale', label= "Scale" , en=False, cc='stampLockUpdate()')
    mc.checkBox('lockOffset', label= "Offset" , en=False, cc='stampLockUpdate()')
    mc.checkBox('lockCurvature', label= "Curvature" , en=False, cc='stampLockUpdate()')
    mc.button('lockAllButton', l= 'all',  c= 'stampLockAllToggle()', en=False)
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2, 20),(3,250),(4,50)])
    mc.text(l ='          Rotation')
    mc.text(l ='')
    mc.floatSliderGrp( 'stampRotSlide' ,w= 250, precision= 1, v = 0, field= 1, min= -180, max= 180,dc='jwStampUpdateRot()',cc='jwStampUpdateRot()')
    mc.button('jwResetRotStamp', l= 'reset',  c= 'jwStampResetRot()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=7 ,cw=[(1,100),(2,50),(3,50),(4,50),(5,50),(6,50),(7,50)])
    mc.text(l ='')
    mc.button('jwRotStampA', l= "-90", c= 'jwStampSetRot(-90)')
    mc.button('jwRotStampB', l= "-45", c= 'jwStampSetRot( -45)')
    mc.button('jwRotStampC', l= "-30", c= 'jwStampSetRot( -30)')
    mc.button('jwRotStampD', l= "30",  c= 'jwStampSetRot( 30)')
    mc.button('jwRotStampE', l= "45",  c= 'jwStampSetRot( 45)')
    mc.button('jwRotStampF', l= "90",  c= 'jwStampSetRot( 90)')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2,20),(3,250),(4,50)])
    mc.text(l ='             Scale W')
    mc.text(l ='')
    mc.floatSliderGrp( 'stampScaleSlide' ,v = 1,  precision= 1, field= 1, min= 0.1, max= 5, dc='jwStampUpdateScale()',cc='jwStampUpdateScale()')
    mc.button('stampScaleReset', l= 'reset',  c= 'jwStampResetScale()')
    mc.text(l ='             Scale H')
    mc.text(l ='')
    mc.floatSliderGrp( 'stampScaleHSlide' ,v = 1,  precision= 1, field= 1, min= 0.1, max= 5, dc='jwStampUpdateHScale()',cc='jwStampUpdateHScale()',en=0)
    mc.button('stampScaleHToggle', l= 'on',bgc=[.2,.2,0.2], c= 'jwstampScaleHToggle()')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2,20),(3,250),(4,50)])
    mc.text('offsetText',l ='            Offset', en=False)
    mc.text(l ='')
    mc.intSliderGrp( 'bridfeOffsetSlide' ,field= 1,v = 1, min= 1, max= 20, fmx=40,en=False)
    mc.button('bridfeOffsetReset', l= 'reset',  c= 'jwStampResetOffset()', en=False)
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2,20),(3,250),(4,50)])
    mc.text('curvatureText',l ='        Curvature', en=False)
    mc.text(l ='')
    mc.floatSliderGrp( 'curvatureSlide' ,v = 1,  precision= 1, field= 1, min= 0.001, max= 2, en=False)
    mc.button('curvatureReset', l= 'reset',  c= 'jwMeshResetCurvaturelide()', en=False)
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=13,cw=[(1,80),(2,20),(3,90),(4,10),(5,90),(6,10),(7,20),(8,10),(9,20),(10,10),(11,20),(12,10),(13,20)])
    mc.text(l ='     Quick Tool')
    mc.text(l ='')
    mc.button('stampIt',  l= 'Stamp Now', en=True,  c= 'convertStamp()')
    mc.text(l ='')
    mc.button('projectMeshButtonB',  l= 'Mesh Projection', en=True,  c= 'projectMesh()')
    mc.text(l ='')
    mc.button('qs2',  l= 'x2', en=True,  c= 'jwMeshQsel("S2")')
    mc.text(l ='')
    mc.button('qs3',  l= 'x3', en=True,  c= 'jwMeshQsel("S3")')
    mc.text(l ='')
    mc.button('qs4',  l= 'x4', en=True,  c= 'jwMeshQsel("S4")')
    mc.text(l ='')
    mc.button('qs6',  l= 'x6', en=True,  c= 'jwMeshQsel("S6")')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2,20),(3,250),(4,50)])
    mc.text(l ='             ')
    mc.text(l ='')
    mc.intSliderGrp( 'stampSliceSlide' ,v = 10,  field= 1, min= 2, max= 20)
    mc.button('stampSliceButton', l= 'Slice',  c= 'sliceStamp()')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=4,cw=[(1,380),(2,20),(3,5),(4,20)])
    mc.text(l ='')
    mc.button(l= '+',c= 'frameCollap(0)')
    mc.text(l ='')
    mc.button(l= '-',c= 'frameCollap(1)')
    mc.setParent( '..' )
    mc.scrollLayout('libS')
    mc.frameLayout('libIconsA', lv = 0 ,bgc =[0.265, 0.265, 0.265])
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    #######################################################################################################
    mc.columnLayout('        Create        ', adjustableColumn=0)
    mc.rowLayout(nc=3 ,cw=[(1,400),(2,7),(3,45)])
    mc.columnLayout('iconCM')
    mc.iconTextButton('snapIcon',style =  "iconOnly", image1 = 'file.svg', bgc = [0.21,0.21,0.21], en=1, w =400, h =400)
    mc.setParent( '..' )
    mc.text(l ='')
    mc.columnLayout()
    mc.button('setupStage', l='TOP', c='setStage()',en=1, w =35, h =35)
    mc.button('setupPerspStage', l='PRESP', c='setPerspStage()',en=1, w =35, h =35)
    mc.button('setupEdgeStage', l='EDGE', c='setEdgeStage()',en=1, w =35, h =35)
    mc.iconTextButton('snapshot',style =  "iconOnly", image1 = 'snapshot.svg', c='snapShotUpdate()',en=1, w =35, h =35)
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.rowLayout(nc=5 ,cw=[(1,50),(2,50),(3,120),(4,120),(5,30)])
    mc.iconTextButton('newFolder',style =  "iconOnly", image1 = 'xgNewGroup_200.png', c='checkeNewFolder()',en=1, w =50, h =50)
    mc.iconTextButton('renameOldFolder',style =  "iconOnly", image1 = 'text.png', c='renameFolderUI()',en=1, w =50, h =50)
    mc.optionMenu('catName', w=120, h =50,bgc = [0.24,0.24,0.24],cc = 'updateCat()')
    mc.menuItem( label= 'Place' )
    mc.menuItem( label= 'Stamp' )
    mc.optionMenu('subFolderName', w=120, h =50,bgc = [0.24,0.24,0.24])
    mc.button('exportLiblButton',w=100, h=50,bgc=[0,0.6,0], l= 'Export', en=True,  c= 'sampleExportGo()')
    updateCat()
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=7,cw=[(1,80),(2,20),(3,140),(4,20),(5,70),(6,20),(7,100)])
    mc.text(l ='     Export Type')
    mc.text(l ='')
    mc.radioButtonGrp('exportType', nrb=2, sl=1, labelArray2=['normal', 'boolean'], cw = [(1,60),(2,70)])
    mc.text(l ='|')
    mc.text(l ='   Edge Crease')
    mc.text(l ='')
    mc.radioButtonGrp('creaseType', nrb=2, sl=1, labelArray2=['On', 'Off'], cw = [(1,40),(2,60)])
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=9,cw=[(1,80),(2,20),(3,70),(4,10),(5,70),(6,10),(7,70),(8,10),(9,70)])
    mc.text(l ='       Quick Tool')
    mc.text(l ='')
    mc.button('scaleStampButton',  l= 'fit Scale', en=True,  c= 'autoScaleFit()')
    mc.text(l ='')
    mc.button('evenBorderButton',  l= 'even Border', en=True,  c= 'evenBoarder()')
    mc.text(l ='')
    mc.button('makeBorderButton',  l= 'make Border', en=True,  c= 'makeBorder()')
    mc.text(l ='')
    mc.button('toggleCageButton',  l= 'toggle Cage', en=True,  c= 'cageWireFrameToggle()')
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    #######################################################################################################
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.frameLayout(labelVisible= False)
    mc.columnLayout(bgc =[0.1, 0.1, 0.1])
    mc.rowLayout(nc=3 ,cw=[(1,350),(2,6),(3,80)])
    mc.intSliderGrp( 'iconSize', cw3=[100, 40, 250], label = '   Icon Size         ',  field= 1, min= 1, max= 10, v = 5 ,cc= 'jwRefreshIcon(0)', dc= 'jwRefreshIcon(0)')
    mc.text(l ='')
    mc.button('killModeButton', w = 80, l= 'Edit',  c= 'toggleRemoveMode()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=5,cw=[(1,80),(2,20),(3,250),(4,10),(5,80)])
    mc.text('libraryPathText' , l ='     Library Path')
    mc.text(l ='')
    mc.textField('libPath', editable=False, tx = meshDirectory )
    mc.text(l ='')
    mc.button('setLiblButton',  l= 'Set', en=True,  c= 'setMyLibPath()')
    mc.text(l ='',h=5)
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.showWindow(jwMeshPlaceUI)
    allowedAreas = ['right', 'left']
    mc.dockControl('rapidPlaceDock', l='rapidPlaceDock 2.77', area='right', content = 'jwMeshPlaceUI',  allowedArea= allowedAreas, fcc = 'floatRPUIsize()')

def floatRPUIsize():
    checkState = mc.dockControl('rapidPlaceDock', q=1 ,fl=1)
    mayaHSize = mc.window('MayaWindow', q=1, h=1)
    if checkState == 0:
        mc.scrollLayout('RPSC',e=1,h=(mayaHSize*0.9))
    else:
        mc.scrollLayout('RPSC',e=1,h=570)
        mc.dockControl('rapidPlaceDock', e=1 ,h=570)

def stampLockUpdate():
    checkList =['lockRot','lockScale','lockOffset','lockCurvature']
    tick  = 0
    for c in checkList:
        state = mc.checkBox(c,q=1,v=1)
        if state == True:
            tick  = tick + 1
    if  not tick == 4 :
        mc.button('lockAllButton',e=1, l= 'all')
    else:
        mc.button('lockAllButton',e=1, l= 'off')

def stampLockAllToggle():
    checkList =['lockRot','lockScale','lockOffset','lockCurvature']
    tick  = 0
    for c in checkList:
        state = mc.checkBox(c,q=1,v=1)
        if state == True:
            tick  = tick + 1
    if  not tick == 4 :
        for c in checkList:
            mc.checkBox(c ,e=1,v=1)
        mc.button('lockAllButton',e=1, l= 'off')
    else:
        for c in checkList:
            mc.checkBox(c ,e=1,v=0)
            mc.button('lockAllButton',e=1, l= 'all')


def stampCurvatureToggle():
    state = mc.checkBox('deformState',q=True, v=True)
    if state == True:
        mc.floatSliderGrp( 'curvatureSlide' ,e=1, en=1)
        mc.button('curvatureReset',e=1, en=1)
    elif state == False:
        mc.floatSliderGrp( 'curvatureSlide' ,e=1, en=0)
        mc.button('curvatureReset',e=1, en=0)

def stampModeToggle():
    checkState = mc.radioButtonGrp('stampType',q=True, sl =True )
    state = mc.checkBox('deformState',q=True, v=True)
    if checkState == 1 :
        mc.text('offsetText',e=1, en=0)
        mc.intSliderGrp( 'bridfeOffsetSlide' ,e=1, en=0)
        mc.button('bridfeOffsetReset',e=1, en=0)
        mc.text('curvatureText',e=1, en=0)
        mc.floatSliderGrp( 'curvatureSlide' ,e=1, en=0)
        mc.button('curvatureReset',e=1, en=0)
        mc.text('lockText',e=1, en=0)
        mc.checkBox('lockRot',e=1, en=0)
        mc.checkBox('lockScale',e=1, en=0)
        mc.checkBox('lockOffset',e=1, en=0)
        mc.checkBox('lockCurvature',e=1, en=0)
        mc.checkBox('deformState',e=1, en=0)
        mc.checkBox('borderState',e=1, en=0)
        mc.button('stampIt',e=1, en=1)
        mc.button('lockAllButton',e=1, en=0)
        mc.intSliderGrp( 'stampSliceSlide',e=1, en=1)
        mc.button('stampSliceButton',e=1, en=1)
    else:
        mc.text('offsetText',e=1, en=1)
        mc.intSliderGrp( 'bridfeOffsetSlide',e=1, en=1)
        mc.button('bridfeOffsetReset',e=1, en=1)
        mc.text('curvatureText',e=1, en=1)
        mc.text('lockText',e=1, en=1)
        mc.checkBox('lockRot',e=1, en=1)
        mc.checkBox('lockScale',e=1, en=1)
        mc.checkBox('lockOffset',e=1, en=1)
        mc.checkBox('lockCurvature',e=1, en=1)
        mc.checkBox('deformState' ,e=1, en=1)
        mc.checkBox('borderState',e=1, en=1)
        mc.button('stampIt',e=1, en=0)
        mc.button('lockAllButton',e=1, en=1)
        mc.intSliderGrp( 'stampSliceSlide',e=1, en=0)
        mc.button('stampSliceButton',e=1, en=0)
        stampCurvatureToggle()

def jwstampScaleHToggle():
    state = mc.button('stampScaleHToggle', q=True, bgc=True)
    if not state[0] == 0:
        mc.button('stampScaleHToggle',l='off', e=True, bgc=[0,0,0])
        mc.floatSliderGrp( 'stampScaleHSlide',e=1,en=1)
    else:
        mc.button('stampScaleHToggle', l= 'on', e=True, bgc=[.2,.2,0.2])
        wState = mc.floatSliderGrp( 'stampScaleSlide',q=True,v=True)
        mc.floatSliderGrp( 'stampScaleHSlide',e=1,en=0,v=wState)
    jwStampUpdateScale()

def stackTypeToggle():
    checkState = mc.radioButtonGrp('stackType',q=True, sl =True )
    mc.setToolTo('selectSuperContext')
    if checkState == 1 :
        mc.radioButtonGrp('meshImportType',e=1 ,en=1)
    else:
        mc.radioButtonGrp('meshImportType',e=1 ,en=0 ,sl =1)

def jwMeshResetCurvaturelide():
    mc.floatSliderGrp( 'curvatureSlide'  ,e=1, v = 1)

def jwMeshResetSwingSlide():
    mc.floatSliderGrp( 'randomSwingSlide' ,e=1, v = 0)

def snapModeToggle():
    checkState = mc.radioButtonGrp('snapType',q=True, sl =True )
    if checkState == 1:
        mc.floatSliderGrp( 'randomSwingSlide' ,e=1, en=0)
        mc.button('jwResetSwingSlide',e=1, en=0)
        mc.text('swingText' ,e=1, en=0)
    else:
        mc.floatSliderGrp( 'randomSwingSlide' ,e=1, en=1)
        mc.button('jwResetSwingSlide',e=1, en=1)
        mc.text('swingText' ,e=1, en=1)

def toggleRemoveMode():
    currentTabs = mc.tabLayout('rapidTab',q=1,st=1)
    if currentTabs != 'Create':
        mc.MoveTool()
        deSelect()
        check = mc.button('killModeButton', q =1 , bgc = 1)
        if check[0] == 1:
            mc.button('killModeButton', e=True, bgc =[0.2 , 0.2, 0.2])
            mc.columnLayout('Place', e=1 , bgc = [0.2, 0.2, 0.2])
            mc.columnLayout('Stamp', e=1 , bgc = [0.2, 0.2, 0.2])
            mc.columnLayout('Create', e=1 , bgc = [0.2, 0.2, 0.2])
            lockUI(1)
            snapModeToggle()
            removeEmptyFolderUI()
            stackTypeToggle()
            stampModeToggle()
        else:
            mc.button('killModeButton', e=True, bgc =[1, 0.2, 0.2])
            mc.columnLayout('Place', e=1 , bgc = [0, 0, 0])
            mc.columnLayout('Stamp', e=1 , bgc = [0, 0, 0])
            mc.columnLayout('Create', e=1 ,  bgc = [0, 0, 0])
            lockUI(0)

def lockUI(state):
    list=['stampSliceButton','qs2','qs3','qs4','qs6','jwResetRot','jwRotA','jwRotB','jwRotC','jwRotD','jwRotE','jwRotF','jwResetRandomRot','meshScaleReset','jwResetRandomScale','meshBetweenReset','meshBetweenRandomReset'
    ,'meshDepthReset','snapVReset','multiCleanButton','goMultiButton','rePostioinButton','projectMeshButtonA','projectMeshButtonB','jwResetRotStamp','bridfeOffsetReset','stampScaleHToggle'
    ,'jwRotStampA','jwRotStampB','jwRotStampC','jwRotStampD','jwRotStampE','jwRotStampF','stampScaleReset','stampIt','exportLiblButton','setLiblButton','jwResetSwingSlide','stampIt','lockAllButton']

    for l in list:
        mc.button(l, e=True,en=state)

    floatList = ['randomSwingSlide','meshRotSlide' ,'randomRotSlide' ,'randomScaleSlide' ,'meshScaleSlide','meshBetweenSlide' ,'meshBetweenRandomSlide' ,'meshDepthSlide' , 'snapVSlider'
    ,'stampRotSlide' , 'stampScaleSlide', 'stampScaleHSlide','curvatureSlide',]

    for f in floatList:
        mc.floatSliderGrp(f, e=True,en=state)

    intList = ['bridfeOffsetSlide','stampSliceSlide']

    for i in intList:
        mc.intSliderGrp(i, e=True,en=state)


    iconTextList = ['snapIcon','snapshot','newFolder']
    for i in iconTextList:
        mc.iconTextButton(i,e=True,en=state)

    optionMenuList = ['catName','subFolderName']
    for o in optionMenuList:
        mc.optionMenu(o,e=True,en=state)

    radioList = ['meshMultiMode','meshImportType','stackType','snapType','stampType']
    for r in radioList:
        mc.radioButtonGrp(r,e=True,en=state)

    checkBoxList = ['lockRot','lockScale','lockOffset','lockCurvature','deformState','borderState']
    for h in checkBoxList:
        mc.checkBox(h,e=True,en=state)

    mc.intSliderGrp( 'iconSize',e=1, en =state)
    mc.text('libraryPathText' ,e=1 , en =state)
    mc.textField('libPath',e=1, en =state)


def checkeNewFolder():
    if mc.window("newfolderUI", exists = True):
        mc.deleteUI("newfolderUI")
    newfolderUI = mc.window("newfolderUI",title = " ", w=300,mxb = False, s = 1 ,bgc = [0.2, 0.2, 0.2  ])
    mc.frameLayout(labelVisible= False)
    mc.text(l ='' ,h=5)
    mc.rowColumnLayout(nc=4,cw=[(1,70),(2,100),(3,15),(4,80)])
    mc.text(l="New Folder" , h = 5)
    mc.textField('folderName', width= 60)
    mc.text(l ='')
    mc.button('createFolderButton',  l= 'Create',  c= 'createNewFolder()')
    mc.text(l ='')
    mc.showWindow(newfolderUI)

def createNewFolder():
    global meshDirectory
    selected = mc.optionMenu('catName', q=True,v=True)
    new = mc.textField('folderName', q=True, tx = True)
    targetPath = meshDirectory  + '/'  + selected + '/' +  new
    if os.path.exists(targetPath):
        print( 'folder exist!')
    else:
        os.makedirs(targetPath)
        updateCat()
        mc.deleteUI("newfolderUI")
        mc.optionMenu('subFolderName', e=True, v = new )

def renameFolderUI():
    global meshDirectory
    catg = mc.optionMenu('catName', q=True,v=True)
    subf = mc.optionMenu('subFolderName', q=True, v=True)
    if mc.window("newfolderUI", exists = True):
        mc.deleteUI("newfolderUI")
    newfolderUI = mc.window("newfolderUI",title = " ", w=300,mxb = False, s = 1 ,bgc = [0.2, 0.2, 0.2  ])
    mc.frameLayout(labelVisible= False)
    mc.text(l ='' ,h=10)
    mc.rowColumnLayout(nc=5,cw=[(1,180),(2,100),(3,15),(4,80),(5,10)])
    mc.text('folderInfo', l=('rename    "' + subf + ' in ' + catg +    '"    to  ') )
    mc.textField('folderName', width= 60)
    mc.text(l ='')
    mc.button('renameFolderButton',  l= 'go!',  c= 'renameFolderGo()')
    mc.text(l ='')
    mc.text(l ='')
    mc.showWindow(newfolderUI)

def renameFolderGo():
    global meshDirectory
    global UIfirstRun
    new = mc.textField('folderName', q=True, tx = True)
    if new:
        oldName =  mc.text('folderInfo', q = True , l= True )
        catg = oldName.split('"')[1].split(' ')[2]
        oldSubf = oldName.split('"')[1].split(' ')[0]
        oldPath = meshDirectory  + '/'  + catg + '/' +  oldSubf
        if os.path.exists(oldPath):
            newPath = meshDirectory  + '/'  + catg + '/' +  new
            if os.path.exists(newPath):
                print( 'rename folder exist!')
            else:
                os.rename(oldPath,newPath)
                updateCat()
                if catg == 'Place':
                    mc.tabLayout('rapidTab',e=1,sti=1)
                elif catg == 'Stamp':
                    mc.tabLayout('rapidTab',e=1,sti=2)
                UIfirstRun = 0
                jwRefreshIcon(0)
                frameAllOn()
                mc.deleteUI("newfolderUI")
        else:
             print( 'selected folder does not exist!')



def updateCat():
    selected = mc.optionMenu('catName', q=True,v=True)
    updateMenu(selected)

def updateMenu(type):
    menu = mc.optionMenu('subFolderName', q=True,itemListLong=True)
    if menu:
        mc.deleteUI(menu, menuItem=True)
    global meshDirectory
    checkDir = os.path.isdir(meshDirectory)
    if checkDir == True :
        subFolder = next(os.walk(meshDirectory+'/'+type+'/'))[1]
        subFolder = sorted(subFolder)
        for s in subFolder:
            if 'decal' in s:
                pass
            elif 'atlas' in s:
                pass
            else:
                mc.menuItem( parent = ( 'subFolderName'), label = s )


def removeEmptyFolder():
    global meshDirectory
    global UIfirstRun
    UIfirstRun = 0
    checkDir = (meshDirectory+'/Place/')
    subFolder = next(os.walk(checkDir))[1]
    if 'decal' in subFolder:
        subFolder.remove('decal')
    if 'atlas' in subFolder:
        subFolder.remove('atlas')
    for s in subFolder:
        checkSub = os.listdir(checkDir +'/' + s + '/')
        if not checkSub:
            os.rmdir((checkDir +'/' + s + '/'))
    checkDir = (meshDirectory+'/Stamp/')
    subFolder = next(os.walk(checkDir))[1]
    for s in subFolder:
        checkSub = os.listdir(checkDir +'/' + s + '/')
        if not checkSub:
            os.rmdir((checkDir +'/' + s + '/'))
    if mc.window("removeIconUI", exists = True):
        mc.deleteUI("removeIconUI")
    jwRefreshIcon(0)
    updateCat()


def checkEmptyFolder():
    global meshDirectory
    checkDir = (meshDirectory+'/Place/')
    subFolder = next(os.walk(checkDir))[1]
    listEmptyFolder = []

    if 'decal' in subFolder:
        subFolder.remove('decal')
    if 'atlas' in subFolder:
        subFolder.remove('atlas')

    for s in subFolder:
        checkSub = os.listdir(checkDir +'/' + s + '/')
        if not checkSub:
            listEmptyFolder.append(s)


    checkDir = (meshDirectory+'/Stamp/')
    subFolder = next(os.walk(checkDir))[1]
    for s in subFolder:
        checkSub = os.listdir(checkDir +'/' + s + '/')
        if not checkSub:
            listEmptyFolder.append(s)


    return listEmptyFolder


def removeEmptyFolderUI():
    check = checkEmptyFolder()
    if check:
        collectList = ', '.join(check)
        if mc.window("removeIconUI", exists = True):
            mc.deleteUI("removeIconUI")
        removeIconUI = mc.window("removeIconUI",title = " ", w=300 , h = 100 ,mxb = False, s =0 ,bgc = [0.2, 0.2, 0.2  ])
        mc.columnLayout()
        mc.rowLayout(nc=2 ,cw=[(1,20),(2,150)])
        mc.text(l ='')
        mc.columnLayout()
        mc.text(l =' ')
        mc.text(l = collectList)
        mc.text(l ='')

        if len(collectList) > 1:
            mc.text(l= 'folders are empty, ')
        else:
            mc.text(l= 'folder is empty, ')
        mc.text(l ='')
        mc.text(l= 'Would you like to remove?')
        mc.text(l ='',h=50)
        mc.rowLayout(nc=4 ,cw=[(1,35),(2,80),(3,15),(4,80)])
        mc.text(l ='')
        mc.button(w=80, h=50, l= 'Remove', en=True,  c ="removeEmptyFolder()")
        mc.text(l ='')
        mc.button( w =80,h=50,l= 'Cancle', en=True,  c= 'closeIconUI()')
        mc.setParent( '..' )
        mc.text(l ='')
        mc.showWindow(removeIconUI)


def removeIcon(meshName):
    name = meshName.split('/')[-1].split('.')[0]
    png = meshName.split('.')[0]+'.png'
    if mc.window("removeIconUI", exists = True):
        mc.deleteUI("removeIconUI")
    removeIconUI = mc.window("removeIconUI",title = " ", w=400 , h = 200 ,mxb = False, s =0 ,bgc = [0.2, 0.2, 0.2  ])
    mc.columnLayout()
    mc.rowLayout(nc=3 ,cw=[(1,200),(2,45),(3,45)])
    mc.iconTextButton('snapIcon',style =  "iconOnly", image1 = png, w =200, h =200)
    mc.columnLayout()
    mc.rowLayout(nc=3 ,cw=[(1,80),(2,2),(3,40)])
    mc.text(l= '    Mesh Name: ')
    mc.text(l ='')
    mc.textField('getOldIconName',tx= name,ed=0)
    mc.setParent( '..' )
    mc.rowLayout(nc=3 ,cw=[(1,80),(2,2),(3,40)])
    mc.text(l= '    New Name: ')
    mc.text(l ='')
    mc.textField('getNewIconName',tx= ' ',tcc= 'activeRenameBotton()')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.text(l ='')
    mc.text(l ='')
    mc.rowLayout(nc=5 ,cw=[(1,40),(2,2),(3,40),(4,2),(5,20)])
    mc.button(w=70, h=50, l= 'Delete', en=True,  bgc = (0.7, 0.5, 0.1),  c ='killIcon("' + meshName + '")')
    mc.text(l ='')
    mc.button('reNameIconButton',w=70, h=50, l= 'Rename', en=False,  bgc = (0.2, 0.2 ,0.2),  c ='reNameIcon("' + meshName + '")')
    mc.text(l ='')
    mc.button(w =20,h=50,l= 'X', en=True,  c= 'closeIconUI()')
    mc.showWindow(removeIconUI)

def activeRenameBotton():
    getOld = mc.textField('getNewIconName',q=1, tx=1)
    if getOld:
        mc.button('reNameIconButton',e=1, en=True,  bgc = (0.3, 0.5 ,0.1))
    else:
        mc.button('reNameIconButton',e=1, en=False, bgc = (0.2, 0.2 ,0.2))


def reNameIcon(meshName):
    getNew = mc.textField('getNewIconName',q=1, tx=1)
    getNew.strip()
    getOld = mc.textField('getOldIconName',q=1, tx=1)
    dir = meshName.split('/')
    path = ('/'.join(dir[0:-1]))
    oldFile = path + '/'+ getOld.strip() + '.abc'
    oldPng = path + '/'+ getOld.strip() + '.png'
    newFile = path + '/'+ getNew.strip() + '.abc'
    newPng = path + '/'+ getNew.strip() + '.png'
    if os.path.isfile(oldFile):
        if oldFile is not newFile:
            if not os.path.isfile(newFile):
                os.rename(oldFile, newFile)
    if os.path.isfile(oldPng):
        if oldPng is not newPng:
            if not os.path.isfile(newPng):
                os.rename(oldPng, newPng)
    closeIconUI()
    jwRefreshIcon(1)


def closeIconUI():
    if mc.window("removeIconUI", exists = True):
        mc.deleteUI("removeIconUI")


def killIcon(meshName):
    png = meshName.split('.')[0]+'.png'

    if os.path.isfile(meshName):
        os.remove(meshName)
    if os.path.isfile(png):
        os.remove(png)
    closeIconUI()
    jwRefreshIcon(0)


def snapShotUpdate():
    cleanList = ('unWantFace','tempStampGrp','sampleBox*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
    selSampleLong = mc.ls(sl=1,fl=1,l=1)
    if selSampleLong:
        selSample = selSampleLong[0].split('|')[1]
        get = mel.eval('rootOf '+selSample)
        cageChild =  mc.listRelatives(get,typ='transform',c=True)
        checkExportType = mc.radioButtonGrp('exportType', q=1, sl=1)
        edgeMode = []
        if mc.attributeQuery('edgeMode', node = get, ex=True ):
            edgeMode = mc.getAttr(get+'.edgeMode')
        if cageChild:
            selSampleLong = mc.ls(sl=1,fl=1,l=1)
            if selSampleLong:
                selSample = selSampleLong[0].split('|')[1]
                get = mel.eval('rootOf '+selSample)
                cageChild =  mc.listRelatives(get,typ='transform',c=True)
                if cageChild:
                    tempGeo = mc.duplicate(get,rr=1)
                    mc.select(tempGeo)
                    tempChild =  mc.listRelatives(typ='transform',c=True,f=True)
                    mc.group(tempChild)
                    mc.parent(w=1)
                    mc.rename('tempStampGrp')
                    if edgeMode == 1:
                        cageBox = mc.polyCube(w=5, h=3, d=3, sx=1, sy=1, sz=1, ax=(0, 1, 0), ch=0, n= 'cageBBox')
                        mc.setAttr("cageBBox.translateY", -1.5)
                        mc.setAttr("cageBBox.translateZ", -1)
                        mc.rename('sampleBox')
                        mc.makeIdentity(apply=True, t= 1, r= 1, s= 1,n= 0)
                        mc.polyCBoolOp('sampleBox',tempGeo[0], op= 2 , ch= 0 , preserveColor = 0, classification= 1, name = 'sampleBox')
                        new=mc.ls(sl=1)
                        mc.select(new, 'tempStampGrp')
                    else:
                        mc.lattice(tempGeo[0],divisions=(2,2,2), objectCentered=True, ldv=(2,2,2), n='templattice')
                        cCenter = mc.xform('templatticeLattice', q=1, t=1)
                        cRrotate =  mc.xform('templatticeLattice' , q=1, ro=1)
                        cScale  = mc.xform('templatticeLattice' , q=1, r=1,s=1)
                        cageBox = mc.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), ch=0, n= 'cageBBox')
                        if cScale[0]<5:
                            cScale[0] = 5
                        if cScale[2]<5:
                            cScale[2] = 5
                        mc.xform(cageBox[0], t=( cCenter[0], cCenter[1], cCenter[2]),ro = ( cRrotate[0], cRrotate[1], cRrotate[2]),s= ( cScale[0], cScale[1], cScale[2]))
                        mc.rename('sampleBox')
                        mc.makeIdentity(apply=True, t= 1, r= 1, s= 1,n= 0)
                        mc.setAttr('sampleBox.scale',1.1,1.1,1.1)
                        bbcoord=mc.xform('sampleBox', q=1, bb=1,ws=1)
                        oldcoord=mc.xform('sampleBox', q=1, piv=1,ws=1)
                        mc.xform(ws=1, piv= (oldcoord[0], bbcoord[4], oldcoord[2]))
                        mc.move(0, (-1* bbcoord[4]), 0,'sampleBox')
                        mc.select('sampleBox.f[0]','sampleBox.f[2:5]')
                        mc.sets(name= "unWantFace", text="unWantFace")
                        mc.polyCBoolOp('sampleBox',tempGeo[0], op= 2 , ch= 1 , preserveColor = 0, classification= 1, name = 'sampleBox')
                        new=mc.ls(sl=1)
                        mc.parent(new,'tempStampGrp')
                        mc.select('unWantFace')
                        mc.delete(new, ch=1)
                        mc.delete()
                        mc.select('tempStampGrp')
        else:
            if checkExportType == 2:
                selSampleLong = mc.ls(sl=1,fl=1,l=1)
                if selSampleLong:
                    selSample = selSampleLong[0].split('|')[1]
                    get = mel.eval('rootOf '+selSample)
                    tempGeo = mc.duplicate(get,rr=1)
                    mc.group()
                    mc.rename('tempStampGrp')
                    if edgeMode == 1:
                        cageBox = mc.polyCube(w=5, h=3, d=3, sx=1, sy=1, sz=1, ax=(0, 1, 0), ch=0, n= 'cageBBox')
                        mc.setAttr("cageBBox.translateY", -1.5)
                        mc.setAttr("cageBBox.translateZ", -1)
                        mc.rename('sampleBox')
                        mc.makeIdentity(apply=True, t= 1, r= 1, s= 1,n= 0)
                        mc.polyCBoolOp('sampleBox',tempGeo[0], op= 2 , ch= 0 , preserveColor = 0, classification= 1, name = 'sampleBox')
                        new=mc.ls(sl=1)
                        mc.select(new)
                    else:
                        mc.lattice(tempGeo[0],divisions=(2,2,2), objectCentered=True, ldv=(2,2,2), n='templattice')
                        cCenter = mc.xform('templatticeLattice', q=1, t=1)
                        cRrotate =  mc.xform('templatticeLattice' , q=1, ro=1)
                        cScale  = mc.xform('templatticeLattice' , q=1, r=1,s=1)
                        cageBox = mc.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), ch=0, n= 'cageBBox')
                        if cScale[0]<5:
                            cScale[0] = 5
                        if cScale[2]<5:
                            cScale[2] = 5
                        mc.xform(cageBox[0], t=( cCenter[0], cCenter[1], cCenter[2]),ro = ( cRrotate[0], cRrotate[1], cRrotate[2]),s= ( cScale[0], cScale[1], cScale[2]))
                        mc.rename('sampleBox')
                        mc.makeIdentity(apply=True, t= 1, r= 1, s= 1,n= 0)
                        mc.setAttr('sampleBox.scale',1.1,1.1,1.1)
                        bbcoord=mc.xform('sampleBox', q=1, bb=1,ws=1)
                        oldcoord=mc.xform('sampleBox', q=1, piv=1,ws=1)
                        mc.xform(ws=1, piv= (oldcoord[0], bbcoord[4], oldcoord[2]))
                        mc.move(0, (-1* bbcoord[4]), 0,'sampleBox')
                        mc.select('sampleBox.f[0]','sampleBox.f[2:5]')
                        mc.sets(name= "unWantFace", text="unWantFace")
                        mc.polyCBoolOp('sampleBox',tempGeo[0], op= 2 , ch= 1 , preserveColor = 0, classification= 1, name = 'sampleBox')
                        new=mc.ls(sl=1)
                        mc.parent(new,'tempStampGrp')
                        mc.select('unWantFace')
                        mc.delete(new, ch=1)
                        mc.delete()
                        mc.select('tempStampGrp')
    mc.isolateSelect( 'modelPanel4', state=1 )
    visCmd = 'toggleAutoLoad modelPanel4 true;'
    mel.eval(visCmd)
    libPath = mc.textField('libPath', q =1 , tx = True )
    if mc.iconTextButton("snapIcon", q =1 , exists = True):
        mc.deleteUI('snapIcon')
    mc.setParent('iconCM')
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()
    cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
    mc.camera(cameraTrans ,e=True, displayFilmGate = False, displayResolution = False, overscan =1.3)
    mc.camera(cameraTrans, e=True, filmFit = 'overscan')
    mc.setAttr((camPath+'.overscan'), 1.05)
    mc.setAttr((camPath+'.preScale'), 1.5)
    mc.setAttr('defaultRenderGlobals.imageFormat', 32)
    exportTempImagePath = libPath + '/tempSnapShot.png'
    mc.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
    mc.modelEditor('modelPanel4',e = True, grid = False, manipulators =False, sel =False,wos=False)
    mc.colorManagementPrefs(e=True, cmEnabled= 0)
    mc.playblast(os=True, st= 1, et= 1, qlt= 100, v =0, wh=[400, 400], p= 100, fo=True, fmt= "image", orn= 0 ,cf = exportTempImagePath)
    mc.modelEditor('modelPanel4',e = True, grid = True, manipulators =True, sel =True)
    mc.iconTextButton('snapIcon',style =  "iconOnly", image1 = exportTempImagePath, en=1, bgc = [0.21,0.21,0.21],w =400, h =400)
    mc.setAttr((camPath+'.preScale'), 1)
    mc.colorManagementPrefs(e=True, cmEnabled= 1)
    mc.isolateSelect( 'modelPanel4',loadSelected = True)
    mc.isolateSelect( 'modelPanel4', state=1)
    visCmd = 'toggleAutoLoad modelPanel4 false;'
    mel.eval(visCmd)
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
    mc.select(selSampleLong)
    mc.isolateSelect( 'modelPanel4', state=0)

def sampleExportGo():
    checkExportType = mc.radioButtonGrp('exportType', q=1, sl=1)
    tempList = mc.ls(sl=1,fl=1,l=1)
    cleanList=[]
    for t in tempList:
        getTop = mel.eval('rootOf '+ t)
        cleanList.append(getTop)
    exportMesh = list(set(cleanList))
    type = mc.optionMenu('catName' ,q =True, v=True)
    sub = mc.optionMenu('subFolderName' ,q =True, v=True)
    libPath = mc.textField('libPath', q =1 , tx = True )
    if len(exportMesh) > 0:
        checkSnapshot = mc.iconTextButton('snapIcon',q=True, image1 = True)
        if checkSnapshot == 'file.svg':
            print( 'please create a snapshot before export!')
        else:
            targetPath = libPath  + '/'  + type + '/' +  sub
            creaseOP = mc.radioButtonGrp('creaseType', q=1,  sl=1)
            if not os.path.exists(targetPath):
                os.makedirs(targetPath)
            for e in exportMesh:
                mc.select(e)
                snapShotUpdate()
                mc.FreezeTransformations()
                mc.xform(ws = True, piv =[0 ,0 ,0])
                cleanName =  e.replace('|','')
                iconPath = libPath + '/' + type + '/' + sub + '/' + cleanName + '.png'
                abcPath  = libPath + '/' + type + '/' + sub + '/' + cleanName + '.abc'
                if os.path.exists(abcPath):
                    print( 'meshName exist!!! please rename your mesh')
                else:
                    children = mc.listRelatives(e, fullPath=True)
                    #add crease attribute
                    if creaseOP == 1:
                        if not mc.attributeQuery('SubDivisionMesh', node = children[0], ex=True ):
                            mc.addAttr(children[0], ln='SubDivisionMesh',  at= 'bool')
                            mc.setAttr((children[0]+'.SubDivisionMesh'),e=True, keyable=True)
                        mc.setAttr((children[0]+'.SubDivisionMesh'),1)
                    if checkExportType == 2:
                        if not mc.attributeQuery('booleanMesh', node = children[0], ex=True ):
                            mc.addAttr(children[0], ln='booleanMesh',  at= 'bool')
                            mc.setAttr((children[0]+'.booleanMesh'),e=True, keyable=True)
                        mc.setAttr((children[0]+'.booleanMesh'),1)
                    children.append(e)
                    listAtt = mc.listAttr(children,ud=True)
                    command = []
                    if listAtt:
                        listAtt = set(listAtt)
                        command = '-attr ' +  ' -attr  '.join(listAtt) + ' '
                    else:
                        command = ' '
                    #make abc
                    mc.rename(e, 'meshSample')
                    root = "-root " + 'meshSample'
                    CMD =  ' AbcExport -j "-frameRange 1 1 -uvWrite -dataFormat ogawa ' + command  + root + ' -file ' + abcPath + '"'
                    mel.eval(CMD)
                    #make icon
                    libPath = mc.textField('libPath', q =1 , tx = True )
                    exportTempImagePath = libPath + '/tempSnapShot.png'
                    shutil.move(exportTempImagePath, iconPath)
                    if type == 'Place':
                        mc.tabLayout('rapidTab',e=1,sti=1)
                    elif type == 'Stamp':
                        mc.tabLayout('rapidTab',e=1,sti=2)
                    jwRefreshIcon(0)
                    mc.rename('meshSample',e)
                    mc.select(cl=1)
    else:
        print( 'please select one mesh!')



def jwAtlasWindow(filePath):
    getGridSize = filePath.split('_')[-1].split('.')[0].split('x')
    iconName = filePath.split('/')[-1].split('.')[0]
    windowMax = 700
    iconSize = windowMax / int(getGridSize[0])
    libPath = mc.textField('libPath', q =1 , tx = True )
    iconEmpty =  libPath + "/iconButton.png"
    iconOn =  libPath + "/iconButtonOn.png"

    if mc.window("decalSheetWin", exists = True):
        mc.deleteUI("decalSheetWin")
    decalSheetWin = mc.window("decalSheetWin",title = "decalSheet",w = windowMax,h = windowMax, mxb = False, s = 1 ,bgc = [0.2, 0.2, 0.2  ])
    mc.formLayout()
    mc.iconTextButton(w= windowMax, h = windowMax, en= 1,style= "iconOnly", image1 = filePath)
    mc.gridLayout(numberOfColumns = int(getGridSize[0]), cellWidthHeight =  [iconSize, iconSize])
    girdRange = int(getGridSize[0])*int(getGridSize[1])
    for i in range(1,(girdRange+1)):
        runCmd = 'goPress("' + filePath  + "@" + str(i) + '")'
        mc.iconTextButton((iconName + '_button_'+ str(i)), w =iconSize, h = iconSize,  style = "iconOnly", image1 =iconEmpty ,hi=iconOn,c =runCmd)

    mc.showWindow(decalSheetWin)

def removeGo():
    libPath = mc.textField('libPath', q =1 , tx = True )
    exportTempImagePath = libPath + '/tempSnapShot.png'
    if os.path.exists(exportTempImagePath):
        os.remove(exportTempImagePath)



def frameAllOn():
    global frameCollection
    mc.tabLayout('rapidTab',e=1,sti=2)
    for f in frameCollection:
        mc.frameLayout((f+'FL'), e = True , cl =False)
    mc.tabLayout('rapidTab',e=1,sti=1)

def checkDirX():
    global meshDirectory
    fileList = []
    for root, files, files in os.walk(meshDirectory):
        for f in files:
            fileList.append(os.path.join(root,f))
    return len(fileList)


def jwRefreshIcon(mode):
    global folderCheck
    global UIfirstRun
    currentTabs = mc.tabLayout('rapidTab',q=1,st=1)
    refreshUI = 1
    if mode == 0:
        refreshUI = 0
        if UIfirstRun == 0:
            UIfirstRun = 1
            refreshUI = 1

        else:
            checkNew = checkDirX()
            if folderCheck != checkNew:
                folderCheck = checkNew
                refreshUI = 1

            currentRow = 0
            if currentTabs == 'Place':
                checkExist = mc.gridLayout('libIconsA', q= True, exists=True)
                if checkExist:
                    currentRow = mc.gridLayout('libIconsA', q= True, numberOfColumns=True)

            elif currentTabs == 'Stamp':
                checkExist = mc.gridLayout('libIconsB', q= True, exists=True)
                if checkExist:
                    currentRow = mc.gridLayout('libIconsB', q= True, numberOfColumns=True)

            rowNumber = mc.intSliderGrp('iconSize' ,q=1, v=1 )

            if rowNumber != currentRow:
                refreshUI = 1
    if currentTabs != 'Create':
        if refreshUI == 1:
            global meshDirectory
            global frameCollection
            frameCollection = []
            frameState = []
            type = ['Place','Stamp']
            for t in type:
                checkDirectory = meshDirectory + '/' + t +  '/'
                subFolder = next(os.walk(checkDirectory))[1]
                for s in subFolder:
                    frameCollection.append(s)
                    checkState = mc.frameLayout(s+'FL', q = True , ex =True)
                    if checkState == 1:
                        checkState = mc.frameLayout(s+'FL', q = True , cl = True)
                        if checkState == 0:
                            frameState.append(s)
            if meshDirectory:
                if currentTabs == 'Place':
                    currentSel = mc.ls(sl=1,fl=1)
                    checkDirectory = meshDirectory + '/Place/'
                    checkDirTab = os.path.isdir(checkDirectory)
                    subFolder = next(os.walk(checkDirectory))[1]

                    if 'decal' in subFolder:
                        subFolder.remove('decal')
                    if 'atlas' in subFolder:
                        subFolder.remove('atlas')
                    if mc.scrollLayout("lib", q =1 , exists = True):
                        mc.deleteUI('lib')
                    mc.setParent('splitBar')
                    mc.scrollLayout('lib',  w = 450  ,h= 1000)
                    iconsCollection = []
                    iconPath = []
                    rowNumber = mc.intSliderGrp('iconSize' ,q=1, v=1 )
                    wide =  (420.0 /rowNumber)
                    high = (wide*1.3)
                    subFolder = sorted(subFolder)
                    for s in subFolder:
                        checkSubDir = os.path.isdir(checkDirectory+'/'+s)
                        if checkSubDir == True:
                            if s in  frameState:
                                mc.frameLayout((str(s) + 'FL'), label= s ,cll = True, cl = False, cc ='iconLightOff()',w=430)
                            else:
                                mc.frameLayout((str(s) + 'FL'), label= s ,cll = True, cl = True, cc ='iconLightOff()',w=430)
                            mc.gridLayout('libIconsA', numberOfColumns = rowNumber, cellWidthHeight = [wide, high])
                            iconsCollection = mc.getFileList(folder = (checkDirectory+'/'+s) , filespec = '*.png')
                            iconsCollection.sort()
                            for i in iconsCollection:
                                iconPath = checkDirectory + s + '/' + i;
                                mc.columnLayout((i + '_column'), h = wide)
                                samplePath = iconPath.replace('png','abc')
                                runCmd = 'goPress("' + samplePath + '")'
                                mc.symbolButton((s +'_' + i + '_button'),  w = wide, h = wide, image = iconPath, c = runCmd)
                                mc.text(w = wide, al = 'center', l = i.replace('.png',''))
                                mc.setParent( '..' )
                            mc.setParent( '..' )
                            mc.setParent( '..' )
                        else:
                            pass

                    # add decal
                    checkDecalDir = os.path.isdir(checkDirectory+'/decal')
                    if checkDecalDir == True:

                        if mc.objExists('tempResCheck'):
                            mc.delete('tempResCheck')
                        fileNode = mc.createNode("file")
                        mc.rename(fileNode, 'tempResCheck')

                        if 'decal' in  frameState:
                            mc.frameLayout('decalFL', label= 'decal' ,cll = True, cl = False , cc ='iconLightOff()',w=430)
                        else:
                            mc.frameLayout('decalFL', label= 'decal' ,cll = True, cl = True, cc ='iconLightOff()',w=430)
                        mc.gridLayout('libIconsA', numberOfColumns = rowNumber, cellWidthHeight = [wide, high])
                        iconsCollection = mc.getFileList(folder = (checkDirectory+'/decal') , filespec = '*.png')

                        for i in iconsCollection:
                            iconPath = checkDirectory + '/decal' + '/' + i;
                            samplePath = iconPath.replace('png','abc')
                            runCmd = 'goPress("' + samplePath + '")'
                            mc.setAttr ("tempResCheck.fileTextureName", iconPath, type="string")
                            wPixels = mc.getAttr("tempResCheck.osx")
                            hPixels = mc.getAttr("tempResCheck.osy")
                            ratio = 0
                            newW = 0
                            newH = 0
                            shrinkV = 0.3
                            offsetGap = 0
                            mc.columnLayout((i + '_column'), h = wide)
                            mc.rowColumnLayout(nc=2,cw=[(1,(wide*0.2))])
                            mc.text(' ')
                            mc.columnLayout()

                            if wPixels >= hPixels:
                                ratio =  hPixels / wPixels
                                newW = wide * (1-shrinkV)
                                newH = ratio*newW
                                offsetGap = newW*(1 - ratio)*0.55
                                if offsetGap < 1:
                                    offsetGap = 1
                                mc.text(' ',h = offsetGap)
                                mc.symbolButton(('decal_' + i + '_button'),  w = newW, h = newH, image = iconPath, c = runCmd)
                                mc.text(' ',h = (offsetGap))
                            else:
                                ratio =  wPixels / hPixels
                                newH = wide*(1-shrinkV)
                                newW = ratio*newH
                                offsetGap = wide*(1 - ratio)*shrinkV
                                if offsetGap < 1:
                                    offsetGap = 1
                                mc.rowColumnLayout((i + '_column'),nc=2,cw=[(1,offsetGap),(2,newW)])
                                mc.text(' ',h = (newW*shrinkV*0.5))
                                mc.symbolButton(('decal_' + i + '_button'), h = newH, image = iconPath, c = runCmd)
                                mc.setParent( '..' )
                                mc.text(' ',h = (newW*shrinkV*0.5))
                            mc.setParent( '..' )
                            mc.setParent( '..' )
                            mc.text(w = (wide*(1+(shrinkV*0.5))), l = i.replace('.png',''))
                            mc.setParent( '..' )


                        mc.setParent( '..' )
                        mc.setParent( '..' )
                        if mc.objExists('tempResCheck'):
                            mc.delete('tempResCheck')
                        # add atlas
                        checkDecalDir = os.path.isdir(checkDirectory+'/atlas')
                        if checkDecalDir == True:
                            iconsCollection = []
                            iconPath = []
                            rowNumber = mc.intSliderGrp('iconSize' ,q=1, v=1 )
                            wide =  (420.0 /rowNumber)
                            high = (wide*1.3)
                            if 'atlas' in  frameState:
                                mc.frameLayout('atlasFL', label= 'atlas' ,cll = True, cl = False,cc ='iconLightOff()',w=430)
                            else:
                                mc.frameLayout('atlasFL', label= 'atlas' ,cll = True, cl = True, cc ='iconLightOff()',w=430)


                            mc.gridLayout('libIconsA', numberOfColumns = rowNumber, cellWidthHeight = [wide, high])
                            iconsCollection = mc.getFileList(folder = (checkDirectory+'/atlas/') , filespec = '*.png')
                            iconsCollection.sort()
                            for i in iconsCollection:
                                iconPath = checkDirectory + '/'+ 'atlas' + '/' + i;
                                mc.columnLayout((i + '_column'), h = wide)
                                runCmd =('jwAtlasWindow ("' + iconPath + '")')
                                mc.symbolButton(('atlas' +'_' + i + '_button'),  w = wide, h = wide, image = iconPath, c = runCmd)
                                mc.text(w = wide, al = 'center', l = i.replace('.png',''))
                                mc.setParent( '..' )
                    if currentSel:
                        mc.select(currentSel)

                elif currentTabs == 'Stamp':
                    checkDirectory = meshDirectory + '/Stamp/'
                    checkDirTab = os.path.isdir(checkDirectory)
                    subFolder = next(os.walk(checkDirectory))[1]

                    if mc.scrollLayout("libS", q =1 , exists = True):
                        mc.deleteUI('libS')
                    mc.setParent('StampTab')
                    mc.scrollLayout('libS', w = 450 ,h= 802)
                    iconsCollection = []
                    iconPath = []
                    rowNumber = mc.intSliderGrp('iconSize' ,q=1, v=1 )
                    wide =  (420.0 /rowNumber)
                    high = (wide*1.3)
                    subFolder = sorted(subFolder)
                    for s in subFolder:
                        checkSubDir = os.path.isdir(checkDirectory+'/'+s)
                        if checkSubDir == True:
                            if s in  frameState:
                                mc.frameLayout((str(s) + 'FL'), label= s ,cll = True, cl = False,cc ='iconLightOff()',w=430)
                            else:
                                mc.frameLayout((str(s) + 'FL'), label= s ,cll = True, cl = True, cc ='iconLightOff()',w=430)
                            mc.gridLayout('libIconsB', numberOfColumns = rowNumber, cellWidthHeight = [wide, high])
                            iconsCollection = mc.getFileList(folder = (checkDirectory+'/'+s) , filespec = '*.png')
                            iconsCollection.sort()
                            for i in iconsCollection:
                                iconPath = checkDirectory + '/'+ s + '/' + i;
                                mc.columnLayout((i + '_column'), h = wide)
                                samplePath = iconPath.replace('png','abc')
                                runCmd = 'goStamp("' + samplePath + '")'
                                mc.symbolButton((s +'_' + i + '_button'),  w = wide, h = wide, image = iconPath, c = runCmd)
                                mc.text(w = wide, al = 'center', l = i.replace('.png',''))
                                mc.setParent( '..' )
                        mc.setParent( '..' )
                        mc.setParent( '..' )

                    mc.setParent( '..' )
                    mc.setParent( '..' )


                else:
                    print('Directory does not exist!!!')
        else:
            removeGo()
            mc.iconTextButton('snapIcon',e=True, image1 = 'file.svg')
    else:
        check = mc.button('killModeButton', q =1 , bgc = 1)
        if check[0] == 1:
            mc.button('killModeButton', e=True, bgc =[0.2 , 0.2, 0.2])
            mc.columnLayout('Place', e=1 , bgc = [0.2, 0.2, 0.2])
            mc.columnLayout('Stamp', e=1 , bgc = [0.2, 0.2, 0.2])
            mc.columnLayout('Create', e=1 , bgc = [0.2, 0.2, 0.2])
            lockUI(1)
            snapModeToggle()
            removeEmptyFolderUI()
            stackTypeToggle()
            stampModeToggle()

def checkFaceNormal(faceName):
    face_normals_text = mc.polyInfo(faceName, faceNormals=True)[0]
    face_normals = [float(digit) for digit in re.findall(r'-?\d*\.\d*', face_normals_text)]
    return face_normals


def faceAngleBetween(faceA,faceB):
    angleA = checkFaceNormal(faceA)
    angleB = checkFaceNormal(faceB)
    getAngle = mc.angleBetween( euler=True, v1=angleA, v2=angleB)
    angleCheck = pow((getAngle[0]+getAngle[1]+getAngle[2])**2,0.5)
    return angleCheck


def selectFlatFace():
    checkFace = mc.ls(sl=1,fl=1,l=1)
    collect = []
    done = []
    checkPass = []
    checkPass = checkFace
    done.append(checkFace[0])
    while len(checkPass) > 0:
        edges = mc.polyListComponentConversion(checkPass, ff=True, te=True)
        collect = mc.polyListComponentConversion(edges, fe=True, tf=True, bo=True)
        newFace = [a for a in collect if a not in done]
        #newFace = list(set(newFace))
        nonFlat = []
        for o in newFace:
            get = faceAngleBetween(checkFace[0],o)
            if get > 0.1:
                nonFlat.append(o)

        checkPass = list(set(newFace)-set(nonFlat))
        done = done + checkPass

    mc.select(done)

def projectMesh():
    currentTabs = mc.tabLayout('rapidTab',q=1,st=1)
    sel = mc.ls(sl=1,fl=1,l=True)
    for s in sel:
        if 'meshSample' not in s:
           s = s + '|meshSample'
        if mc.objExists(s):
            lastSnapMesh = mc.getAttr(s+'.targetGeo')
            shapeNode = mc.listRelatives(s, fullPath=True , c=True )
            checkNodeType = mc.nodeType(shapeNode)
            if checkNodeType != 'gpuCache':
                if currentTabs == 'Stamp':
                #face flat surface
                    mc.select(s)
                    mc.ConvertSelectionToEdgePerimeter()
                    mc.ConvertSelectionToFaces()
                    selectFlatFace()
                    fList = mc.ls(sl=1,fl=1)
                    if not mc.attributeQuery('flatList', node = s, ex=True ):
                        mc.addAttr(s, ln='flatList',  dt= 'string')
                        mc.setAttr((s+'.flatList'),e=True, keyable=True)
                    listToStr = ' '.join(map(str, fList))
                    mc.setAttr((s + '.flatList'),listToStr,type="string")
                ######################################################
                tempY = mc.getAttr(s + '.translateY')
                mc.setAttr((s + '.translateY'), 0)
                mc.select(s)
                mc.pickWalk(d='up')
                transNode = mc.ls(sl=1,fl=1)
                tempSampleRotY = mc.getAttr(s + '.rotateY')
                mc.setAttr((s+ '.rotateY'), 0)
                attrList = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ']
                storeDate = []
                for a in attrList:
                    info = mc.getAttr(transNode[0] + '.' + a)
                    mc.setAttr((transNode[0] + '.' + a),0)
                    storeDate.append(info)
                bbox = mc.xform(s,q=True,bb=True)
                bw = pow(((bbox[3]-bbox[0])**2),0.5)*1.05
                bh = pow(((bbox[5]-bbox[2])**2),0.5)*1.05
                mc.polyPlane(w=bw, h=bh, sx=10, sy=10, ax=(0,1,0) ,cuv=2, ch=1)
                mc.rename('guideMesh')
                mc.select(s)
                latt =mc.lattice(divisions=(10, 2, 10), objectCentered=True, ldv=(10, 2, 10))
                mc.select('guideMesh',add=True)
                mc.CreateWrap()
                mc.setAttr("wrap1.maxDistance",10)
                mc.setAttr("wrap1.exclusiveBind",0)
                mc.parent('guideMesh',latt,'guideMeshBase',transNode[0])
                for a in range(len(attrList)):
                    mc.setAttr((transNode[0] + '.' + attrList[a]), storeDate[a])
                mc.setAttr((s+ '.rotateY'),tempSampleRotY)
                mc.setAttr((latt[2]+ '.rotateY'),tempSampleRotY)
                mc.setAttr('guideMesh.rotateY',tempSampleRotY)
                mc.transferAttributes(lastSnapMesh, 'guideMesh', transferPositions = 1, searchMethod = 3 )
                mc.select(s)
                mc.delete(ch=True)
                if mc.objExists('guideMesh'):
                    mc.delete('guideMesh')
                if mc.objExists('guideMeshBase'):
                    mc.delete('guideMeshBase')
                mc.setAttr((s + '.translateY'), tempY)
                #final touch, snap boarder again
                if currentTabs == 'Stamp':
                    mc.polySelectConstraint(mode =3, type = 0x8000 ,where =1)
                    mc.polySelectConstraint(m =0)
                    sampleBorder = mc.ls(sl=1,fl=1)
                    if sampleBorder:
                        mc.transferAttributes(lastSnapMesh, sampleBorder, transferPositions = 1, searchMethod = 3 )
                        mc.select(s)
                        mc.delete(ch=True)
def multiButtonToggle():
    checkState = mc.radioButtonGrp('meshMultiMode',  q =True , sl= True)
    iconLightOff()
    if checkState == 1:
        mc.button('goMultiButton',  e =True , en = False)
        mc.button('multiCleanButton',  e =True , en = False)

    else:
        mc.button('goMultiButton',  e =True , en = True)
        mc.button('multiCleanButton',  e =True , en = True)


def screenVisPoly():
    commonList= []
    view = omui.M3dView.active3dView()
    om.MGlobal.selectFromScreen(0, 0, view.portWidth(), view.portHeight(), om.MGlobal.kReplaceList)
    objects = om.MSelectionList()
    sel = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(objects)
    #restore selection
    om.MGlobal.setActiveSelectionList(sel, om.MGlobal.kReplaceList)
    #return the objects as strings
    fromScreen = []
    objects.getSelectionStrings(fromScreen)
    shapesOnScreen = mc.listRelatives(fromScreen, shapes=True,f=True)
    meshList = mc.ls(type='mesh',l=True)#only polygon
    if len(meshList)>0 and shapesOnScreen is not None:
        commonList = list(set(meshList) & set(shapesOnScreen))
        return commonList
    else:
        commonList = []
        return commonList

def checkScreenRes():
    global lastPanelActive
    windowUnder = mc.getPanel(withFocus=True)
    if 'modelPanel' not in windowUnder:
        windowUnder = lastPanelActive
        if 'modelPanel' not in windowUnder:
            windowUnder = 'modelPanel4'
    viewNow = omui.M3dView()
    omui.M3dView.getM3dViewFromModelEditor(windowUnder, viewNow)
    screenW = omui.M3dView.portWidth(viewNow)
    screenH = omui.M3dView.portHeight(viewNow)
    return screenW,screenH

def checkWorldSpaceToImageSpace(cameraName, worldPoint):
    resWidth,resHeight = checkScreenRes()
    selList = om.MSelectionList()
    selList.add(cameraName)
    dagPath = om.MDagPath()
    selList.getDagPath(0,dagPath)
    dagPath.extendToShape()
    camInvMtx = dagPath.inclusiveMatrix().inverse()
    fnCam = om.MFnCamera(dagPath)
    mFloatMtx = fnCam.projectionMatrix()
    projMtx = om.MMatrix(mFloatMtx.matrix)
    mPoint = om.MPoint(worldPoint[0],worldPoint[1],worldPoint[2]) * camInvMtx * projMtx;
    x = (mPoint[0] / mPoint[3] / 2 + .5) * resWidth
    y = (mPoint[1] / mPoint[3] / 2 + .5) * resHeight

    return [x,y]

def finishTool():
    restoreSelVis()
    #mc.MoveTool()
    mc.select(cl=True)
    iconLightOff()

def restoreSelVis():
    mc.modelEditor('modelPanel1', e=True, sel=True)
    mc.modelEditor('modelPanel2', e=True, sel=True)
    mc.modelEditor('modelPanel3', e=True, sel=True)
    mc.modelEditor('modelPanel4', e=True, sel=True)

def hideSelVis():
    pass
    #mc.modelEditor('modelPanel1', e=True, sel=False)
    #mc.modelEditor('modelPanel2', e=True, sel=False)
    #mc.modelEditor('modelPanel3', e=True, sel=False)
    #mc.modelEditor('modelPanel4', e=True, sel=False)



def updateBetween():
    #update between numbers
    global headMesh
    global tailMesh
    global betweenList
    global combineSelPool
    global SycList
    global betweenList
    global betweenList3DPos
    betweenList3DPos = []
    checkToolMode = mc.currentCtx()
    if checkToolMode == 'Click2dTo3dCtx' and len(headMesh) > 0 and len(tailMesh) > 0:
        goStrightLine = mc.floatSliderGrp('meshBetweenSlide', q=True, v=True)
        meshTypeState = mc.radioButtonGrp('meshImportType', q=True , sl=True)
        randomY = mc.floatSliderGrp( 'randomRotSlide' ,q=1,v=True)
        silderScale = mc.floatSliderGrp( 'meshScaleSlide' ,q=1,v=True)
        randomScale = mc.floatSliderGrp( 'randomScaleSlide' ,q=1,v=True)

        view = omui.M3dView.active3dView()
        cam = om.MDagPath()
        view.getCamera(cam)
        camPath = cam.fullPathName()
        cameraTrans = mc.listRelatives(camPath,type='transform',p=True)

        #get 2d position of head and tail mesh
        attList = ['translateX','translateY','translateZ']
        attListRecord =['ptX','ptY','ptZ']

        for a in range(len(attList)):
            attListRecord[a] = mc.getAttr(headMesh+'.'+attList[a])
        head2D = checkWorldSpaceToImageSpace(cameraTrans[0], (attListRecord[0],attListRecord[1],attListRecord[2]))

        for b in range(len(attList)):
            attListRecord[b] = mc.getAttr(tailMesh+'.'+attList[b])
        tail2D = checkWorldSpaceToImageSpace(cameraTrans[0], (attListRecord[0],attListRecord[1],attListRecord[2]))

        #remove betweenList from SycList
        betweenMeshList = []
        for l in betweenList:
            if mc.objExists(l):
                meshUnder = mc.listRelatives(l,c=True, typ = 'transform',f=True)
                betweenMeshList.append(meshUnder[0])
                mc.delete(l)

        SycList = list(set(SycList) - set(betweenMeshList))
        SycList = list(set(SycList))
        betweenList = []
        betweenListShape = []
        #get in between element
        if goStrightLine > 0:
            for i in range(int(goStrightLine)):

                randomNumber = random.randint(0,(len(combineSelPool)-1))
                mc.select(combineSelPool[randomNumber])
                newBetweenDulpi = mc.ls(sl=True,fl=True,l=True)
                if meshTypeState == 2:
                    #only instance mesh not tranform node
                    newNode = mc.duplicate(newBetweenDulpi[0],rr=True)
                    mc.select(newNode)
                    mc.pickWalk(d='Down')
                    meshNode = mc.ls(sl=True,l=True)
                    mc.select(newBetweenDulpi[0])
                    mc.pickWalk(d='Down')
                    mc.instance()
                    mc.delete(meshNode)
                    intNode = mc.ls(sl=True,l=True)
                    mc.parent(intNode,newNode)
                    intNode = mc.ls(sl=True,l=True)
                    mc.rename(meshNode[0].split('|')[-1])
                    mc.pickWalk(d='up')
                else:
                    mc.duplicate(newBetweenDulpi[0])

                selBetween = mc.ls(sl=True,fl=True,l=True)
                meshNodeB = mc.listRelatives(selBetween[0],c=True, typ = 'transform',f=True)

                if randomY > 0:
                    randomNumber = random.uniform(0,randomY)
                    mc.setAttr((meshNodeB[0]+'.rotateY'),int(randomNumber))

                silderScale = mc.floatSliderGrp( 'meshScaleSlide' ,q=1,v=True)
                randomScale = mc.floatSliderGrp( 'randomScaleSlide' ,q=1,v=True)
                if (randomScale > 0):
                    randomNumber = random.uniform((-1*randomScale),randomScale)
                    mc.setAttr((meshNodeB[0]+'.scaleX'),(randomNumber+silderScale))
                    mc.setAttr((meshNodeB[0]+'.scaleY'),(randomNumber+silderScale))
                    mc.setAttr((meshNodeB[0]+'.scaleZ'),(randomNumber+silderScale))
                SycList.append(meshNodeB[0])
                betweenShape = mc.listRelatives(selBetween[0], fullPath=True ,c=True)
                betweenList.append(selBetween[0])
                betweenListShape.append(betweenShape[0])

            # caculate new inBetween position
            for c in range(int(goStrightLine)):
                disX = (tail2D[0] - head2D[0])/(goStrightLine+1)
                disY = (tail2D[1] - head2D[1])/(goStrightLine+1)
                nextX =   tail2D[0] -(disX*(c+1) )
                nextY =   tail2D[1] -(disY*(c+1))
                wx,wy,wz,hitmesh,hitFace = getPosition(nextX,nextY)
                if wx != []:
                    pos3D = (wx,wy,wz)
                    betweenList3DPos.append(pos3D)
                    mc.setAttr((betweenList[c] + '.translateX'), wx)
                    mc.setAttr((betweenList[c] + '.translateY'), wy)
                    mc.setAttr((betweenList[c] + '.translateZ'), wz)
                    hitFaceName = (hitmesh + '.f[' + str(hitFace) +']')
                    rx, ry, rz = checkFaceAngle(hitFaceName)
                    mc.setAttr((betweenList[c] + '.rotateX'), rx)
                    mc.setAttr((betweenList[c] + '.rotateY'), ry)
                    mc.setAttr((betweenList[c] + '.rotateZ'), rz)

            updateDepth()
            updateScale()
            updateRandomScale()
            mc.select(cl=True)


def updateBetweenRandom():
    #update between numbers
    global betweenList
    global betweenList3DPos
    checkToolMode = mc.currentCtx()
    silderRandomPos = mc.floatSliderGrp( 'meshBetweenRandomSlide' ,q=1,v=True)

    if checkToolMode == 'Click2dTo3dCtx' and len(headMesh) > 0 and len(tailMesh) > 0:
        view = omui.M3dView.active3dView()
        cam = om.MDagPath()
        view.getCamera(cam)
        camPath = cam.fullPathName()
        cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
        # caculate new inBetween position
        if len(betweenList)>0:
        #get 2d position
             for e in range(len(betweenList)):
                pox  = str(betweenList3DPos[e]).replace('(','').replace(')','').split(',')[0]
                poy  = str(betweenList3DPos[e]).replace('(','').replace(')','').split(',')[1]
                poz  = str(betweenList3DPos[e]).replace('(','').replace(')','').split(',')[2]
                pos2D = checkWorldSpaceToImageSpace(cameraTrans[0], (float(pox),float(poy),float(poz)))
                randomNumberX = random.uniform((-1*silderRandomPos),silderRandomPos)
                randomNumberY = random.uniform((-1*silderRandomPos),silderRandomPos)
                nextX =   pos2D[0]*(1+(randomNumberX*0.1))
                nextY =   pos2D[1]*(1+(randomNumberY*0.1))
                wx,wy,wz,hitmesh,hitFace = getPosition(nextX,nextY)
                try: #in case it outside snap mesh
                    mc.setAttr((betweenList[e] + '.translateX'), wx)
                    mc.setAttr((betweenList[e] + '.translateY'), wy)
                    mc.setAttr((betweenList[e] + '.translateZ'), wz)
                    hitFaceName = (hitmesh + '.f[' + str(hitFace) +']')
                    rx, ry, rz = checkFaceAngle(hitFaceName)
                    mc.setAttr((betweenList[e] + '.rotateX'), rx)
                    mc.setAttr((betweenList[e] + '.rotateY'), ry)
                    mc.setAttr((betweenList[e] + '.rotateZ'), rz)
                except:
                    pass

def updateRandomScale():
    randomScale = mc.floatSliderGrp('randomScaleSlide' , q=True, v=True)
    scaleXXX = mc.floatSliderGrp('meshScaleSlide', q=True, v=True)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            if mc.objExists(s):
                if randomScale > 0:
                    randomNumber = random.uniform((scaleXXX-randomScale),(scaleXXX+randomScale))
                    mc.setAttr((s+'.scaleX'),randomNumber)
                    mc.setAttr((s+'.scaleY'),randomNumber)
                    mc.setAttr((s+'.scaleZ'),randomNumber)
                else:
                    mc.setAttr((s+'.scaleX'),scaleXXX)
                    mc.setAttr((s+'.scaleY'),scaleXXX)
                    mc.setAttr((s+'.scaleZ'),scaleXXX)

def updateScale():
    scaleXXX = mc.floatSliderGrp('meshScaleSlide', q=True, v=True)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            if mc.objExists(s):
                if mc.objExists(s):
                    mc.setAttr((s+'.scaleX'),scaleXXX)
                    mc.setAttr((s+'.scaleY'),scaleXXX)
                    mc.setAttr((s+'.scaleZ'),scaleXXX)

def updateDepth():
    depthXXX = mc.floatSliderGrp('meshDepthSlide', q=True, v=True)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            if mc.objExists(s):
                mc.setAttr((s+'.translateY'),depthXXX)

def updateRotate():
    rotXXX = mc.floatSliderGrp('meshRotSlide', q=True, v=True)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            if mc.objExists(s):
                mc.setAttr((s+'.rotateY'),rotXXX)

def jwMeshSetRot(angle):
    global SycList
    if len(SycList)>0:
        mc.floatSliderGrp('meshRotSlide', e=True, v=angle)
        for s in SycList:
            if mc.objExists(s):
                mc.setAttr((s+'.rotateY'),angle)

def updateRotateRandom():
    randomY = mc.floatSliderGrp( 'randomRotSlide' ,q=1,v=True)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            if mc.objExists(s):
                randomNumber = random.uniform(0,randomY)
                mc.setAttr((s+'.rotateY'),int(randomNumber))


def updateSwingRandom():
    randomXZ = mc.floatSliderGrp( 'randomSwingSlide' ,q=1,v=True)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            offsetNode = mc.listRelatives(s,type='transform',p=True)
            if mc.objExists(offsetNode[0]):
                randomNumberX = random.uniform(0,randomXZ)
                mc.setAttr((offsetNode[0]+'.rotateX'),int(randomNumberX))
                randomNumberZ = random.uniform(0,randomXZ)
                mc.setAttr((offsetNode[0]+'.rotateZ'),int(randomNumberZ))

def killInitalSample():
    iconLightOff()


def offPressPlace():
    global tempCmd
    global betweenList
    global betweenList3DPos
    betweenList3DPos = []

    for e in betweenList:
        attList = ['translateX','translateY','translateZ']
        attListRecord =['ptX','ptY','ptZ']
        for a in range(len(attList)):
            attListRecord[a] = mc.getAttr(e +'.'+attList[a])
        pos3D = (attListRecord[0],attListRecord[1],attListRecord[2])
        betweenList3DPos.append(pos3D )
    mc.refresh(cv=True,f=True)
    deSelect()

def getPosition(SX,SY):
    global betweenListShape
    global checkVisList
    pos = om.MPoint()
    dir = om.MVector()
    hitpoint = om.MFloatPoint()
    omui.M3dView().active3dView().viewToWorld(int(SX), int(SY), pos, dir)
    pos2 = om.MFloatPoint(pos.x, pos.y, pos.z)
    #current camera
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()

    cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
    cameraPosition = mc.xform(cameraTrans,q=1,ws=1,rp=1)

    checkHit = 0
    finalMesh = []
    finalX = []
    finalY = []
    finalZ = []

    shortDistance = 10000000000
    distanceBetween = 1000000000

    hitFacePtr = om.MScriptUtil().asIntPtr()
    hitFace = []
    checkList = []

    checkStackMode  = mc.radioButtonGrp('stackType',q=True, sl =True )
    shapesNodestOnly = []
    try:
        shapesList = mc.listRelatives(betweenListShape,ad=True,f=True)
        shapesNodestOnly =  mc.ls(shapesList,type='shape',l=1,fl=1)
    except:
        pass
    if checkStackMode == 1:
        checkList = checkVisList
        try:
            checkList =  list(set(checkVisList)-set(shapesNodestOnly))
        except:
            pass
    else:
        checkList = screenVisPoly()
        checkList =  list(set(checkList)-set(shapesNodestOnly))

    for mesh in checkList:
        selectionList = om.MSelectionList()
        selectionList.add(mesh)
        dagPath = om.MDagPath()
        selectionList.getDagPath(0, dagPath)
        fnMesh = om.MFnMesh(dagPath)

        intersection = fnMesh.closestIntersection(
        om.MFloatPoint(pos2),
        om.MFloatVector(dir),
        None,
        None,
        False,
        om.MSpace.kWorld,
        99999,
        False,
        None,
        hitpoint,
        None,
        hitFacePtr,
        None,
        None,
        None)

        if intersection:
            x = hitpoint.x
            y = hitpoint.y
            z = hitpoint.z
            distanceBetween = math.sqrt( ((float(cameraPosition[0]) - x)**2)  + ((float(cameraPosition[1]) - y)**2) + ((float(cameraPosition[2]) - z)**2))
            if distanceBetween < shortDistance:
                shortDistance = distanceBetween
                finalMesh = mesh
                finalX = x
                finalY = y
                finalZ = z
                hitFace = om.MScriptUtil(hitFacePtr).asInt()

    return finalX, finalY, finalZ ,finalMesh ,hitFace
    mc.refresh(cv=True,f=True)

def onPressPlace():
    global ctx
    global betweenListShape
    betweenListShape = []
    global SycList
    SycList = []
    global sampleFileChoice
    global selectionPool
    global combineSelPool
    global pressFirstTime
    global betweenFirstTime
    betweenFirstTime = 1
    global screenX,screenY
    global headMesh
    headMesh = []
    global tailMesh
    global lastSnapMesh
    global currentScaleRecord
    global currentRotRecord
    tailMesh = []
    checkSnapState = mc.radioButtonGrp('snapType',q=True, sl =True )
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY
    meshTypeState = mc.radioButtonGrp('meshImportType', q=True , sl=True)
    try:
        if pressFirstTime == 1:
            #check samplePool still item, if yes random select one
            #multiMode
            newChoice = []
            if len(sampleFileChoice) > 1:
                randomNumber = random.randint(0,(len(sampleFileChoice)-1))
                newChoice = sampleFileChoice[randomNumber]
                sampleFileChoice.remove(newChoice)
                selectionPool.append(newChoice)

            else:
                newChoice = sampleFileChoice[0]
                sampleFileChoice.remove(newChoice)
                selectionPool.append(newChoice)
                pressFirstTime = 0

            #combine two list for selection###bug
            combineSelPool = list(set(sampleFileChoice + selectionPool))
            mc.select(newChoice)
        else:
            newNodeA = []
            randomNumber = random.randint(0,(len(combineSelPool)-1))
            newChoiceA = combineSelPool[randomNumber]
            if meshTypeState == 2:
                #only instance mesh not tranform node
                newNodeA = mc.duplicate(newChoiceA,rr=True)
                mc.select(newNodeA)
                mc.pickWalk(d='Down')
                meshNode = mc.ls(sl=True,l=True)
                mc.select(newChoiceA)
                mc.pickWalk(d='Down')
                mc.instance()
                mc.delete(meshNode)
                intNode = mc.ls(sl=True,l=True)
                mc.parent(intNode,newNodeA)
                mc.rename(meshNode[0].split('|')[-1])
                mc.pickWalk(d='up')
            else:
                newNodeA = mc.duplicate(newChoiceA,rr=True)
            mc.select(newNodeA)

        tempSel = mc.ls(sl=1,type='transform')


        wx,wy,wz,hitmesh,hitFace= getPosition(screenX,screenY)
        lastSnapMesh = hitmesh
        mc.setAttr((tempSel[0] + '.translateX'), wx)
        mc.setAttr((tempSel[0] + '.translateY'), wy)
        mc.setAttr((tempSel[0] + '.translateZ'), wz)
        hitFaceName = (hitmesh + '.f[' + str(hitFace) +']')

        if checkSnapState == 1:
            rx, ry, rz = checkFaceAngle(hitFaceName)
            mc.setAttr((tempSel[0] + '.rotateX'), rx)
            mc.setAttr((tempSel[0] + '.rotateY'), ry)
            mc.setAttr((tempSel[0] + '.rotateZ'), rz)

        mc.setAttr((tempSel[0]+'.scaleX'),1)
        mc.setAttr((tempSel[0]+'.scaleY'),1)
        mc.setAttr((tempSel[0]+'.scaleZ'),1)
        currentScaleX = mc.floatSliderGrp('meshScaleSlide', q=True, v=True)
        currnetRotY =  mc.floatSliderGrp('meshRotSlide', q=True, v=True)
        currentDepth = mc.floatSliderGrp('meshDepthSlide', q=True, v=True)
        mc.pickWalk(tempSel[0], direction='down')
        meshNode  = mc.ls(sl=1,type='transform',l=1)
        #meshNode = mc.listRelatives(tempSel[0],c=True, typ = 'transform',f=True)
        SycList.append(meshNode[0])
        mc.setAttr((meshNode[0]+'.scaleX'),currentScaleX)
        mc.setAttr((meshNode[0]+'.scaleY'),currentScaleX)
        mc.setAttr((meshNode[0]+'.scaleZ'),currentScaleX)
        mc.floatSliderGrp('meshScaleSlide', e=True, v = currentScaleX)
        currentScaleRecord = currentScaleX
        mc.setAttr((meshNode[0]+'.rotateY'),currnetRotY)
        currentRotRecord = currnetRotY
        mc.setAttr((meshNode[0]+'.translateY'),currentDepth)
        randomY = mc.floatSliderGrp( 'randomRotSlide' ,q=1,v=True)
        if (randomY > 0):
            randomNumber = random.uniform(0,randomY)
            mc.setAttr((meshNode[0]+'.rotateY'),int(randomNumber))
            currentRotRecord = int(randomNumber)
        silderScale = mc.floatSliderGrp( 'meshScaleSlide' ,q=1,v=True)
        randomScale = mc.floatSliderGrp( 'randomScaleSlide' ,q=1,v=True)
        if (randomScale > 0):
            randomNumber = random.uniform((-1*randomScale),randomScale)
            mc.setAttr((meshNode[0]+'.scaleX'),(randomNumber+silderScale))
            mc.setAttr((meshNode[0]+'.scaleY'),(randomNumber+silderScale))
            mc.setAttr((meshNode[0]+'.scaleZ'),(randomNumber+silderScale))
            currentScaleRecord = (randomNumber+silderScale)
        randomSwing = mc.floatSliderGrp( 'randomSwingSlide' ,q=1,v=True)
        if randomSwing > 0:
            offsetNode = mc.listRelatives(meshNode[0],type='transform',p=True)
            randomNumberX = random.uniform(-1*randomSwing,randomSwing)
            mc.setAttr((offsetNode[0]+'.rotateX'),int(randomNumberX))
            randomNumberZ = random.uniform(-1*randomSwing,randomSwing)
            mc.setAttr((offsetNode[0]+'.rotateZ'),int(randomNumberZ))

        mc.select(tempSel)

        #######################################################################

        transNode=mc.listRelatives(lastSnapMesh,type='transform',p=True,f=True)
        mc.setAttr((meshNode[0] + '.targetGeo'),transNode[0],type="string")

       #########################################################################
    except:
        pass

    mc.refresh(cv=True,f=True)



def onDragPlace():
    global tempCmd
    tempCmd = []
    global ctx
    global pressFirstTime
    global betweenFirstTime
    global screenX,screenY
    global betweenList
    global betweenListShape
    global checkVisList
    global combineSelPool
    global SycList
    global headMesh
    global tailMesh
    global lastPanelActive
    global lastSnapMesh
    global currentScaleRecord
    global currentRotRecord
    checkSnapState = mc.radioButtonGrp('snapType',q=True, sl =True )
    lastPanelActive = mc.getPanel(underPointer=True)
    currentSX = 0
    currnetSY = 0
    goStrightLine = mc.floatSliderGrp('meshBetweenSlide', q=True, v=True)
    randomY = mc.floatSliderGrp( 'randomRotSlide' ,q=1,v=True)
    meshTypeState = mc.radioButtonGrp('meshImportType', q=True , sl=True)
    selSample = []
    selSample = mc.ls(sl=True,fl=True,l=True)
    headMesh = selSample[0]
    if len(selSample)>0:
        if (goStrightLine > 0):
            if betweenFirstTime == 1:
                #need to give one sample to first position
                attList = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ']
                attListRecord =['ptX','ptY','ptZ','prX','prY','prZ','psX','psY','psZ']
                for a in range(len(attList)):
                    attListRecord[a] = mc.getAttr(selSample[0]+'.'+attList[a])
                #pick up sample if multiMode
                if len(combineSelPool)>1:
                        randomNumber = random.randint(0,(len(combineSelPool)-1))
                        mc.select(combineSelPool[randomNumber])
                else:
                    mc.select(selSample[0])
                keepItMesh = mc.ls(sl=1,fl=1)
                #make a copy
                if meshTypeState == 2:
                    #only instance mesh not tranform node
                    newKeepNode = mc.duplicate(keepItMesh[0],rr=True)
                    mc.select(newKeepNode)
                    mc.pickWalk(d='Down')
                    meshKeepNode = mc.ls(sl=True,l=True)
                    mc.select(keepItMesh[0])
                    mc.pickWalk(d='Down')
                    mc.instance()
                    mc.delete(meshKeepNode)
                    intKeepNode = mc.ls(sl=True,l=True)
                    mc.parent(intKeepNode,newKeepNode)
                    intKeepNode = mc.ls(sl=True,l=True)
                    mc.rename(meshKeepNode[0].split('|')[-1])
                    mc.pickWalk(d='up')
                else:
                    mc.duplicate(keepItMesh[0])
                #restore position
                checkKeepNode = mc.ls(sl=1,fl=1)
                for b in range(len(attList)):
                    mc.setAttr((checkKeepNode[0]+'.'+attList[b]),attListRecord[b])
                checkKeepNodeChild = mc.listRelatives(checkKeepNode[0],c=True, typ = 'transform',f=True)
                SycList.append(checkKeepNodeChild[0])

                meshNodeA = mc.listRelatives(selSample[0],c=True, typ = 'transform',f=True)

                SycList.append(meshNodeA[0])
                if randomY > 0:
                    randomNumber = random.uniform(0,randomY)
                    mc.setAttr((meshNodeA[0]+'.rotateY'),int(randomNumber))

                tailMesh = checkKeepNode[0]
                betweenList = []
                betweenListShape = []
                #get in between element
                for i in range(int(goStrightLine)):
                    if len(combineSelPool)>1:
                        randomNumber = random.randint(0,(len(combineSelPool)-1))
                        mc.select(combineSelPool[randomNumber])
                    else:
                        mc.select(selSample[0])

                    newBetweenDulpi = mc.ls(sl=True,fl=True,l=True)
                    if meshTypeState == 2:
                        #only instance mesh not tranform node
                        newNode = mc.duplicate(newBetweenDulpi[0],rr=True)
                        mc.select(newNode)
                        mc.pickWalk(d='Down')
                        meshNode = mc.ls(sl=True,l=True)
                        mc.select(newBetweenDulpi[0])
                        mc.pickWalk(d='Down')
                        mc.instance()
                        mc.delete(meshNode)
                        intNode = mc.ls(sl=True,l=True)
                        mc.parent(intNode,newNode)
                        intNode = mc.ls(sl=True,l=True)
                        mc.rename(meshNode[0].split('|')[-1])
                        mc.pickWalk(d='up')
                    else:
                        mc.duplicate(newBetweenDulpi[0])

                    selBetween = mc.ls(sl=True,fl=True,l=True)
                    meshNodeB = mc.listRelatives(selBetween[0],c=True, typ = 'transform',f=True)
                    silderScale = mc.floatSliderGrp( 'meshScaleSlide' ,q=1,v=True)
                    randomScale = mc.floatSliderGrp( 'randomScaleSlide' ,q=1,v=True)
                    randomSwing = mc.floatSliderGrp( 'randomSwingSlide' ,q=1,v=True)
                    if (randomScale > 0):
                        randomNumber = random.uniform((-1*randomScale),randomScale)
                        newScale = (randomNumber+silderScale)
                        #bug calucation done but update not fast enough to show, evalDeferred works but not great
                        cmdx = 'mc.setAttr("' + meshNodeB[0] +'.scaleX",' + str(newScale) + ')'
                        mc.evalDeferred(cmdx)
                        cmdy = 'mc.setAttr("' + meshNodeB[0] +'.scaleY",' + str(newScale) + ')'
                        mc.evalDeferred(cmdy)
                        cmdz = 'mc.setAttr("' + meshNodeB[0] +'.scaleZ",' + str(newScale) + ')'
                        mc.evalDeferred(cmdz)


                    if randomY > 0:
                        randomNumber = random.uniform(0,randomY)
                        mc.setAttr((meshNodeB[0]+'.rotateY'),int(randomNumber))

                    if randomSwing > 0:
                        offsetNode = mc.listRelatives(meshNodeB[0],type='transform',p=True)
                        randomNumberX = random.uniform(-1*randomSwing,randomSwing)
                        mc.setAttr((offsetNode[0]+'.rotateX'),int(randomNumberX))
                        randomNumberZ = random.uniform(-1*randomSwing,randomSwing)
                        mc.setAttr((offsetNode[0]+'.rotateZ'),int(randomNumberZ))

                    SycList.append(meshNodeB[0])
                    betweenShape = mc.listRelatives(selBetween[0], fullPath=True ,c=True)
                    betweenList.append(selBetween[0])
                    betweenListShape.append(betweenShape[0])
                    betweenFirstTime = 0
        else:
            betweenListShape = []

        modifiers = mc.getModifiers()
        SycList = list(set(SycList))
        if (modifiers == 4):
            #print 'ctrl Press'

            vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
            distanceA = (vpX - screenX)
            rotateCheck = (distanceA)

            rotateRun = currentRotRecord + rotateCheck
            if rotateRun > 360 :
                rotateRun = 360
            elif rotateRun < -360 :
                rotateRun = -360
            getR = int(rotateRun / 15)*15
            if rotateRun != getR:
                rotateRun = getR
            mc.floatSliderGrp( 'meshRotSlide', e=1 ,v = rotateRun )
            if len(SycList)>0:
                for s in SycList:
                    mc.setAttr((s+'.rotateY'),rotateRun)
            #mc.refresh(f=True)

        elif(modifiers == 1):

            #print 'shift selSample'
            vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
            distanceB = vpX - screenX
            scaleCheck = distanceB / 100
            scaleRun = currentScaleRecord + scaleCheck
            if scaleRun > 5:
                scaleRun = 5
            elif scaleRun < 0:
                scaleRun = 0.1

            mc.floatSliderGrp( 'meshScaleSlide', e=1 ,v = scaleRun )
            if len(SycList)>0:
                for s in SycList:
                    mc.setAttr((s+ '.scaleX'),scaleRun)
                    mc.setAttr((s+ '.scaleY'),scaleRun)
                    mc.setAttr((s+ '.scaleZ'),scaleRun)
            #mc.refresh(cv=True,f=True)
        else:
            vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
            currentSX = vpX
            currentSY = vpY
            pos = om.MPoint()
            dir = om.MVector()
            hitpoint = om.MFloatPoint()
            omui.M3dView().active3dView().viewToWorld(int(vpX), int(vpY), pos, dir)
            pos2 = om.MFloatPoint(pos.x, pos.y, pos.z)

            #current camera
            view = omui.M3dView.active3dView()
            cam = om.MDagPath()
            view.getCamera(cam)
            camPath = cam.fullPathName()

            cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
            cameraPosition = mc.xform(cameraTrans,q=1,ws=1,rp=1)

            checkHit = 0
            finalMesh = []
            finalX = 0
            finalY = 0
            finalZ = 0
            shortDistance = 10000000000
            distanceBetween = 1000000000

            checkList=[]
            meshNode = mc.listRelatives(selSample, fullPath=True ,c=True)
            myShape = mc.listRelatives(meshNode, shapes=True,f=True)

            shapesList = mc.listRelatives(betweenListShape,ad=True,f=True)
            shapesNodestOnly =  mc.ls(shapesList,type='shape',l=1,fl=1)


            if myShape == None:#gpu
                checkList =  list(set(checkVisList))
            else:
                checkStackMode  = mc.radioButtonGrp('stackType',q=True, sl =True )
                if checkStackMode == 1:
                    checkList =  list(set(checkVisList)-set(myShape)-set(shapesNodestOnly))
                else:
                    checkList = screenVisPoly()
                    checkList.remove(myShape[0])
                    SycListShape = mc.listRelatives(SycList, shapes=True,f=True)
                    checkList = list(set(checkList) - set(shapesNodestOnly)- set(SycListShape))
            hitFacePtr = om.MScriptUtil().asIntPtr()
            hitFace = []
            for mesh in checkList:
                selectionList = om.MSelectionList()
                selectionList.add(mesh)
                dagPath = om.MDagPath()
                selectionList.getDagPath(0, dagPath)
                fnMesh = om.MFnMesh(dagPath)
                intersection = fnMesh.closestIntersection(
                om.MFloatPoint(pos2),
                om.MFloatVector(dir),
                None,
                None,
                False,
                om.MSpace.kWorld,
                99999,
                False,
                None,
                hitpoint,
                None,
                hitFacePtr,
                None,
                None,
                None)
                if intersection:
                    x = hitpoint.x
                    y = hitpoint.y
                    z = hitpoint.z
                    distanceBetween = math.sqrt( ((float(cameraPosition[0]) - x)**2)  + ((float(cameraPosition[1]) - y)**2) + ((float(cameraPosition[2]) - z)**2))
                    if distanceBetween < shortDistance:
                        shortDistance = distanceBetween
                        finalMesh = mesh
                        hitFace = om.MScriptUtil(hitFacePtr).asInt()
                        hitFaceName = (finalMesh + '.f[' + str(hitFace) +']')
                        #buggy when this is done after it return incorrect information
                        if checkSnapState == 1:
                            rx, ry, rz = checkFaceAngle(hitFaceName)
                            mc.setAttr((selSample[0] + '.rotateX'), rx)
                            mc.setAttr((selSample[0] + '.rotateY'), ry)
                            mc.setAttr((selSample[0] + '.rotateZ'), rz)
                        finalX = x
                        finalY = y
                        finalZ = z
                    lastSnapMesh = finalMesh
                    #######################################################################
                    childNode =   mc.listRelatives(selSample[0],type='transform',ad=True,f=True)
                    transNode=mc.listRelatives(lastSnapMesh,type='transform',p=True,f=True)
                    for c in childNode:
                        mc.setAttr((c + '.targetGeo'),transNode[0],type="string")
                   #########################################################################
                    mc.setAttr((selSample[0] + '.translateX'), finalX)
                    mc.setAttr((selSample[0] + '.translateY'), finalY)
                    mc.setAttr((selSample[0] + '.translateZ'), finalZ)
                    hitFaceName = (finalMesh + '.f[' + str(hitFace) +']')

                    lockVtxCheck = mc.floatSliderGrp('snapVSlider', q=True, v=True)
                    if (lockVtxCheck > 0):
                        cvX = 0
                        cvY = 0
                        cvZ = 0
                        shortDistanceCheck = 10000
                        checkCVDistance = 10000
                        mostCloseDist = lockVtxCheck
                        hitFaceName = (finalMesh + '.f[' + str(hitFace) +']')
                        cvList = (mc.polyInfo(hitFaceName , fv=True )[0]).split(':')[-1].split('    ')
                        cvList = [x for x in cvList if x.strip()]
                        mostCloseCVPoint = []
                        for v in cvList:
                            checkNumber = ''.join([n for n in v.split('|')[-1] if n.isdigit()])
                            if len(checkNumber) > 0:
                                cvPoint = (finalMesh + '.vtx[' + str(checkNumber) +']')
                                cvPosition = mc.pointPosition(cvPoint)
                                checkCVDistance = math.sqrt( ((float(cvPosition[0]) - finalX)**2)  + ((float(cvPosition[1]) - finalY)**2) + ((float(cvPosition[2]) - finalZ)**2))
                                if checkCVDistance < shortDistanceCheck:
                                    shortDistanceCheck = checkCVDistance
                                    cvX = float(cvPosition[0])
                                    cvY = float(cvPosition[1])
                                    cvZ = float(cvPosition[2])
                                    mostCloseCVPoint = cvPoint
                        if shortDistanceCheck < mostCloseDist:
                            mc.setAttr((selSample[0] + '.translateX'), cvX)
                            mc.setAttr((selSample[0] + '.translateY'), cvY)
                            mc.setAttr((selSample[0] + '.translateZ'), cvZ)
                            #get average normal angle from suround faces
                            if checkSnapState == 1:
                                rX,rY,rZ = avgVertexNormalAngle(cvPoint)
                                mc.setAttr(selSample[0]+'.rotateX', rX)
                                mc.setAttr(selSample[0]+'.rotateY', rY)
                                mc.setAttr(selSample[0]+'.rotateZ', rZ)

                    silderRandomPos = mc.floatSliderGrp( 'meshBetweenRandomSlide' ,q=1,v=True)
                    # caculate new inBetween position
                    for a in range(int(goStrightLine)):
                        disX = (screenX - currentSX)/(goStrightLine+1)
                        disY = (screenY - currentSY)/(goStrightLine+1)
                        nextX = 0
                        nextY = 0
                        if silderRandomPos > 0:
                            randomNumberX = random.uniform((-1*silderRandomPos),silderRandomPos)
                            randomNumberY = random.uniform((-1*silderRandomPos),silderRandomPos)
                            nextX =   (screenX -(disX*(a+1) ))*(1+(randomNumberX*0.1))
                            nextY =   (screenY -(disY*(a+1))) *(1+(randomNumberY*0.1))

                        else:
                            nextX =   screenX -(disX*(a+1))
                            nextY =   screenY -(disY*(a+1))
                        wx,wy,wz,hitmesh,hitFace = getPosition(nextX,nextY)
                        if wx != []:
                            #######################################################################
                            childNode =   mc.listRelatives(betweenList[a],type='transform',ad=True,f=True)
                            transNode=mc.listRelatives(hitmesh,type='transform',p=True,f=True)
                            for c in childNode:
                                mc.setAttr((c + '.targetGeo'),transNode[0],type="string")
                            #########################################################################
                            mc.setAttr((betweenList[a] + '.translateX'), wx)
                            mc.setAttr((betweenList[a] + '.translateY'), wy)
                            mc.setAttr((betweenList[a] + '.translateZ'), wz)
                            if checkSnapState == 1:
                                hitFaceName = (hitmesh + '.f[' + str(hitFace) +']')
                                rx, ry, rz = checkFaceAngle(hitFaceName)
                                mc.setAttr((betweenList[a] + '.rotateX'), rx)
                                mc.setAttr((betweenList[a] + '.rotateY'), ry)
                                mc.setAttr((betweenList[a] + '.rotateZ'), rz)

        mc.select(selSample[0])
        updateDepth()
        updateScale()
        mc.refresh(cv=True,f=True)


def runIt():
    global ctx
    ctx = 'Click2dTo3dCtx'
    # Delete dragger context if it already exists
    if mc.draggerContext(ctx, exists=True):
        mc.deleteUI(ctx)
    # Create dragger context and set it to the active tool
    mc.draggerContext(ctx, pressCommand = onPressPlace, rc = offPressPlace, dragCommand = onDragPlace, fnz = finishTool, name=ctx, cursor='crossHair',undoMode='step')
    mc.setToolTo(ctx)

def placeToSel():
    global storeSampleMeshPath
    global selAnyList
    global SycList
    SycList=[]
    meshTypeState = mc.radioButtonGrp('meshImportType', q=True , sl=True)
    checkSnapState = mc.radioButtonGrp('snapType',q=True, sl =True )
    tempSel = mc.ls(sl=1,type='transform',l=True)
    offsetNodeSample=mc.listRelatives(tempSel,type='transform',p=True)
    #check select type
    meshSel = mc.filterExpand(selAnyList,expand=True ,sm=12)
    faceSel = mc.filterExpand(selAnyList,expand=True ,sm=34,fp=True)
    #check gpu
    listAllNode = mc.listRelatives(selAnyList,type='gpuCache',c=True,f=True)
    if listAllNode:
        parentNode = mc.listRelatives(listAllNode,type='transform',ap=True,f=True)
        if meshSel:
            meshSel.extend(parentNode)
        else:
            meshSel=parentNode

    if faceSel:
        for i in range(len(faceSel)):
            newNode =[]
            if i > 0:
                if meshTypeState != 2:
                    newNode = mc.duplicate(offsetNodeSample,rr=True)
                else:
                    newNode =mc.instance( offsetNodeSample, leaf=True )
            else:
                newNode.append(offsetNodeSample[0])
            info = getFacePivotInfo(faceSel[i])
            try:
                mc.setAttr((newNode[0] + '.translateX'), info[0])
                mc.setAttr((newNode[0] + '.translateY'), info[1])
                mc.setAttr((newNode[0] + '.translateZ'), info[2])
                mc.setAttr((newNode[0] + '.scaleX'), 1)
                mc.setAttr((newNode[0] + '.scaleY'), 1)
                mc.setAttr((newNode[0] + '.scaleZ'), 1)
                if checkSnapState == 1:
                    mc.setAttr((newNode[0] + '.rotateX'), info[3])
                    mc.setAttr((newNode[0] + '.rotateY'), info[4])
                    mc.setAttr((newNode[0] + '.rotateZ'), info[5])

                currentScaleX = mc.floatSliderGrp('meshScaleSlide', q=True, v=True)
                currnetRotY =  mc.floatSliderGrp('meshRotSlide', q=True, v=True)
                currentDepth = mc.floatSliderGrp('meshDepthSlide', q=True, v=True)
                mc.pickWalk(newNode[0], direction='down')
                meshNode  = mc.ls(sl=1,type='transform',l=1)

                SycList.append(meshNode[0])
                mc.setAttr((meshNode[0]+'.scaleX'),currentScaleX)
                mc.setAttr((meshNode[0]+'.scaleY'),currentScaleX)
                mc.setAttr((meshNode[0]+'.scaleZ'),currentScaleX)
                mc.floatSliderGrp('meshScaleSlide', e=True, v = currentScaleX)
                currentScaleRecord = currentScaleX
                mc.setAttr((meshNode[0]+'.rotateY'),currnetRotY)
                currentRotRecord = currnetRotY
                mc.setAttr((meshNode[0]+'.translateY'),currentDepth)
                randomY = mc.floatSliderGrp( 'randomRotSlide' ,q=1,v=True)
                if (randomY > 0):
                    randomNumber = random.uniform(0,randomY)
                    mc.setAttr((meshNode[0]+'.rotateY'),int(randomNumber))
                    currentRotRecord = int(randomNumber)
                silderScale = mc.floatSliderGrp( 'meshScaleSlide' ,q=1,v=True)
                randomScale = mc.floatSliderGrp( 'randomScaleSlide' ,q=1,v=True)
                if (randomScale > 0):
                    randomNumber = random.uniform((-1*randomScale),randomScale)
                    mc.setAttr((meshNode[0]+'.scaleX'),(randomNumber+silderScale))
                    mc.setAttr((meshNode[0]+'.scaleY'),(randomNumber+silderScale))
                    mc.setAttr((meshNode[0]+'.scaleZ'),(randomNumber+silderScale))
                    currentScaleRecord = (randomNumber+silderScale)
                randomSwing = mc.floatSliderGrp( 'randomSwingSlide' ,q=1,v=True)
                if randomSwing > 0:
                    offsetNode = mc.listRelatives(meshNode[0],type='transform',p=True)
                    randomNumberX = random.uniform(-1*randomSwing,randomSwing)
                    mc.setAttr((offsetNode[0]+'.rotateX'),int(randomNumberX))
                    randomNumberZ = random.uniform(-1*randomSwing,randomSwing)
                    mc.setAttr((offsetNode[0]+'.rotateZ'),int(randomNumberZ))

                    mc.select(tempSel)
                #########################################################################

                childTransNodeList = mc.listRelatives(newNode[0],type='transform',ad=True,f=True)
                childTransNodeList.append(newNode[0])
                snapMeshName = faceSel[i].split('.')[0]
                for c in childTransNodeList:
                    if not mc.attributeQuery('targetGeo', node = c, ex=True ):
                        mc.addAttr(c, ln='targetGeo',  dt= 'string')
                        mc.setAttr((c+'.targetGeo'),e=True, keyable=True)
                    mc.setAttr((c + '.targetGeo'),snapMeshName,type="string")
               #########################################################################

            except:
                pass

        if meshTypeState == 3:
            mc.gpuCache(e=True, refresh=True)
        else:
            mc.refresh(cv=True,f=True)
    if meshSel:
        checkSample = 0
        #filter none sample mesh
        for j in range(len(meshSel)):
            if not mc.attributeQuery('targetGeo', node = meshSel[j], ex=True ):
                meshSel.remove(meshSel[j])

        for j in range(len(meshSel)):
            sampleA = meshSel[j]
            if mc.objExists(sampleA):
                if mc.attributeQuery('targetGeo', node = sampleA, ex=True ):
                    offsetNode = mc.listRelatives(sampleA,type='transform',ap=True,f=True)
                    checkGrpStructure = offsetNode[0].split('|')
                    if len(checkGrpStructure) > 2:
                        sampleA = offsetNode[0]
                        offsetNode = mc.listRelatives(sampleA,type='transform',ap=True,f=True)

                    checkSample = 1
                    storeAttr = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ','targetGeo']
                    sampleData = []
                    offsetData = []
                    for x in range(len(storeAttr)):
                        v = mc.getAttr( sampleA + '.' +  storeAttr[x])
                        sampleData.append(v)

                    for x in range(len(storeAttr)-1):
                        v = mc.getAttr( offsetNode[0] + '.' + storeAttr[x])
                        offsetData.append(v)
                    newNode =[]
                    if j > 0:
                        if meshTypeState != 2:
                            newNode = mc.duplicate(offsetNodeSample,rr=True)
                        else:
                            newNode =mc.instance( offsetNodeSample, leaf=True )
                    else:
                        newNode.append(offsetNodeSample[0])


                    #########################################################################
                    childTransNodeList = mc.listRelatives(newNode[0],type='transform',ad=True,f=True)
                    for c in childTransNodeList:
                        if not mc.attributeQuery('targetGeo', node = c, ex=True ):
                            mc.addAttr(c, ln='targetGeo',  dt= 'string')
                            mc.setAttr((c+'.targetGeo'),e=True, keyable=True)
                        mc.setAttr((c + '.targetGeo'),sampleData[-1],type="string")
                    #########################################################################

                    for x in range(len(storeAttr)-1):
                        mc.setAttr((newNode[0] + '.' + storeAttr[x]),offsetData[x])

                    sampleNode = mc.listRelatives(newNode[0],type='transform',c=True,f=True)
                    SycList.append(sampleNode[0])
                    for x in range(len(storeAttr)-1):
                        mc.setAttr((sampleNode[0] + '.' + storeAttr[x]),sampleData[x])
                    mc.delete(offsetNode)

        if checkSample == 0:
            mc.delete(offsetNodeSample)
            mc.evalDeferred('iconLightOff()')
            goPress(storeSampleMeshPath)

def goPress(sampleMesh):
    global storeSampleMeshPath
    storeSampleMeshPath = sampleMesh
    check = mc.button('killModeButton', q =1 , bgc = 1)
    if check[0] == 1:
        removeIcon(sampleMesh)
    else:
        global selAnyList
        selAnyList = mc.ls(sl=1,fl=1,l=1)
        global sampleFileChoice
        global pressFirstTime
        global betweenFirstTime
        global screenX,screenY
        global betweenList
        global betweenListShape
        global checkVisList
        global selectionPool
        global combineSelPool
        screenX = 0
        screenY = 0
        betweenList = []
        betweenListShape = []
        betweenFirstTime = 1
        pressFirstTime = 1
        selectionPool = []
        combineSelPool = []
        checkVisList = screenVisPoly()
        #need to check if it is a decal, disable Instance , GPU, or MultiMode
        if len(sampleFileChoice)>0:
            for s in sampleFileChoice:
                if mc.objExists(str(s)):
                    checkStateX = mc.getAttr(s+'.translateX')
                    checkStateY = mc.getAttr(s+'.translateY')
                    checkStateZ = mc.getAttr(s+'.translateZ')
                    if checkStateX == 0 and  checkStateY == 0 and checkStateZ == 0:
                        mc.delete(s)
        if '/decal/' in sampleMesh:
            mc.radioButtonGrp('meshMultiMode', e=True, sl = 0)
            mc.button('goMultiButton',  e =True , en = False)
            mc.button('multiCleanButton',  e =True , en = False)
            iconNameCheck = sampleMesh.split('/')[-1].replace('.abc','')
            path = sampleMesh.replace('.abc','.png')
            fileNode = mc.createNode("file")
            mc.rename(fileNode, iconNameCheck+'_image')
            mc.setAttr ((iconNameCheck+'_image.fileTextureName'), path, type="string")
            wPixels = mc.getAttr(iconNameCheck+'_image.osx') / 10.0
            hPixels = mc.getAttr(iconNameCheck+'_image.osy') / 10.0

            if wPixels > hPixels:
                newW = 4
                newH = hPixels/wPixels*4
            else:
                newH = 4
                newW = wPixels/hPixels*4

            polyNode = mc.polyPlane(w=newW, h=newH, sx=4, sy=4,name=iconNameCheck)
            sgNode = []
            if mc.objExists((iconNameCheck+'_shader'))==0:
                lambertNode = mc.shadingNode("lambert", asShader=1)
                mc.rename(lambertNode,(iconNameCheck+'_shader'))
                mc.connectAttr((iconNameCheck+'_image.outColor'), (iconNameCheck+'_shader.color'))
                sgNode = mc.sets(renderable=1, noSurfaceShader=1, empty=1, name=iconNameCheck+'SG')
                mc.connectAttr(iconNameCheck+'_shader.color', sgNode+".surfaceShader",f=1)
                mc.connectAttr((iconNameCheck+'_image.outTransparency'),(iconNameCheck+'_shader.transparency'),f=True)
                mc.sets(polyNode, e=1, fe=sgNode)

            mc.select(polyNode)
            mc.hyperShade(assign =  (iconNameCheck+'_shader'))
            #mc.sets(e =True,forceElement= (iconNameCheck+'SG'))
            sampleName = (sampleMesh.split('/')[-1]).split('.')[0]
            mc.CreateEmptyGroup()
            mc.rename(sampleName + '_offset')
            checkName=mc.ls(sl=True)
            mc.parent(polyNode,checkName)
            mc.xform(ws=1, a=1 ,piv =[0, 0, 0])
            tempSel = mc.ls(sl=True,type='transform')
            mc.select(tempSel[0])
            sampleFileChoice = checkName
            mc.setAttr((sampleFileChoice[0]+'.scaleX'),0)
            mc.setAttr((sampleFileChoice[0]+'.scaleY'),0)
            mc.setAttr((sampleFileChoice[0]+'.scaleZ'),0)
            mc.floatSliderGrp( 'meshDepthSlide',e=True ,v = 0.1)
            preIcon = 'decal_'+ iconNameCheck +'_png_button'
            cmd = 'mc.symbolButton("'+preIcon+'", e=1, ebg =1, bgc=[0, 0.4, 0.5]) '
            mc.evalDeferred(cmd)
            if len(selAnyList)>0:
                placeToSel()
            else:
                runIt()
            hideSelVis()
            #create plane with radtio
        elif '/atlas/' in sampleMesh:
            mc.radioButtonGrp('meshMultiMode', e=True, sl = 0)
            mc.button('goMultiButton',  e =True , en = False)
            mc.button('multiCleanButton',  e =True , en = False)
            path = sampleMesh.split('@')[0]
            iconOrder = sampleMesh.split('@')[1]
            iconNameCheck = path.split('/')[-1].replace('.png','').split('_')[0]
            fileNode = mc.createNode("file")
            mc.rename(fileNode, iconNameCheck+'_image')
            mc.setAttr ((iconNameCheck+'_image.fileTextureName'), path, type="string")
            mc.setAttr(iconNameCheck + '_image.colorSpace', 'Raw', type='string')
            polyNode = mc.polyPlane(w=4, h=4, sx=4, sy=4,name = iconNameCheck + '_' + str(iconOrder) + '_0')
            sgNode = []
            if mc.objExists((iconNameCheck+'_shader'))==0:
                lambertNode = mc.shadingNode("lambert", asShader=1)
                mc.rename(lambertNode,(iconNameCheck+'_shader'))
                mc.connectAttr((iconNameCheck+'_image.outColor'), (iconNameCheck+'_shader.color'))
                sgNode = mc.sets(renderable=1, noSurfaceShader=1, empty=1, name=iconNameCheck+'SG')
                mc.connectAttr(iconNameCheck+'_shader.color', sgNode+".surfaceShader",f=1)
                mc.connectAttr((iconNameCheck+'_image.outTransparency'),(iconNameCheck+'_shader.transparency'),f=True)
                mc.sets(polyNode, e=1, fe=sgNode)
            mc.select(polyNode)
            mc.hyperShade(assign =  (iconNameCheck+'_shader'))
            #mc.sets(e =True,forceElement= (iconNameCheck+'SG'))
            sampleName = (sampleMesh.split('/')[-1]).split('.')[0]
            mc.CreateEmptyGroup()
            mc.rename(sampleName + '_offset')
            checkName=mc.ls(sl=True)
            mc.parent(polyNode,checkName)
            mc.xform(ws=1, a=1 ,piv =[0, 0, 0])
            tempSel = mc.ls(sl=True,type='transform')
            mc.select(tempSel[0])
            sampleFileChoice = checkName
            mc.setAttr((sampleFileChoice[0]+'.scaleX'),0)
            mc.setAttr((sampleFileChoice[0]+'.scaleY'),0)
            mc.setAttr((sampleFileChoice[0]+'.scaleZ'),0)
            mc.floatSliderGrp( 'meshDepthSlide',e=True ,v = 0.1)
            # solve UV
            gridSize = path.split('/')[-1].replace('.png','').split('_')[-1].split('x')
            orderNo = int(iconOrder)
            gridS = int(gridSize[0])
            UVSize = 1.0/gridS
            uvV = 0
            uvU = 0
            uvU = orderNo % gridS
            uvV = orderNo // gridS
            if uvU == 0:
                uvU = gridS
                uvV = uvV -1
            moveV = 1.0 -( (uvV+1) * (1.0/gridS) )
            moveU = ( uvU - 1 ) * ( 1.0 / gridS)
            cmd = 'mc.polyEditUV("' + tempSel[0] + '.map[*]",u= '+ str(moveU) + ', v = '+ str(moveV) + ', pu=0 ,pv= 0, su= ' + str(UVSize) +', sv= ' + str(UVSize) + ')'
            mc.evalDeferred(cmd)
            #preIcon = 'decal_'+ iconNameCheck +'_png_button'
            #cmd = 'mc.symbolButton("'+preIcon+'", e=1, ebg =1, bgc=[0, 0.4, 0.5]) '
            #mc.evalDeferred(cmd)
            if len(selAnyList)>0:
                placeToSel()
            else:
                runIt()
            hideSelVis()
            #create plane with radtio
        else:
            multiMeshMode = mc.radioButtonGrp('meshMultiMode',q=True, sl=True)
            if multiMeshMode == 2:
                iconNameCheck = sampleMesh.split('/')[-1].replace('.abc','_png')
                subFolder = sampleMesh.split('/')[-2]
                preIcon = subFolder+'_'+ iconNameCheck+'_button'
                #get icon state
                checkState = mc.symbolButton(preIcon, q=1, ebg =True)
                if checkState == 1:
                    mc.symbolButton(preIcon, e=1, ebg =0, bgc=[0 ,0.3, 0.7])
                else:
                    mc.symbolButton(preIcon, e=1, ebg =1, bgc=[0.7 ,0.3, 0.3])
            else:
                iconLightOff()
                sampleName = (sampleMesh.split('/')[-1]).split('.')[0]
                mc.CreateEmptyGroup()
                mc.rename(sampleName + '_offset')
                checkName=mc.ls(sl=True)
                meshTypeState = mc.radioButtonGrp('meshImportType', q=True , sl=True)
                if meshTypeState == 3:#gpu
                    cacheName = sampleName
                    cachePath = sampleMesh
                    cacheNode = mc.createNode('gpuCache',name = cacheName+'Cache')
                    mc.setAttr(cacheNode+'.cacheFileName',cachePath,type='string')
                    mc.parent(cacheNode,checkName)
                else:
                    command = 'AbcImport -mode import -reparent '+ checkName[0] + ' ' + '"' + sampleMesh + '"'
                    newNode = mel.eval(command)
                    mc.xform(ws=1, a=1 ,piv =[0, 0, 0])
                    mc.pickWalk(d="down")
                    tempSel = mc.ls(sl=True,type='transform',l=True)
                    folderName = (sampleMesh.split('/')[-2])
                    getShader = mc.getFileList(folder = (meshDirectory+'/Place' +'/'+ folderName) , filespec = '*.ma')
                    if len(getShader) == 1:
                        if mc.objExists(folderName +'_SHD') == 0:
                            importShader = mc.file( (meshDirectory+'/Place' +'/'+ folderName + '/'+ getShader[0]), i=1, rnn=1, type="mayaAscii", ignoreVersion=1, ra=1, mergeNamespacesOnClash=0, pr=1 )
                            checkShader = []
                            supportType = ['blinn','lambert','RedshiftMaterial','aiStandardSurface']
                            for i  in importShader:
                                nodeTy = mc.nodeType(i)
                                for s in supportType:
                                    if nodeTy == s:
                                        checkShader = i
                            if checkShader:
                                mc.rename(checkShader,(folderName+'_SHD'))
                                sgNode = mc.sets(renderable=1, noSurfaceShader=1, empty=1, name=(folderName+'_SG'))
                                mc.connectAttr((folderName+'_SHD.outColor'), sgNode+".surfaceShader",f=1)
                        mc.sets(tempSel, e=1, fe=(folderName+'_SG'))
                    mc.select(tempSel)
                tempSel = mc.ls(sl=True,type='transform',l=True)
                mc.select(tempSel[0])
                sampleFileChoice = checkName
                mc.setAttr((sampleFileChoice[0]+'.scaleX'),0)
                mc.setAttr((sampleFileChoice[0]+'.scaleY'),0)
                mc.setAttr((sampleFileChoice[0]+'.scaleZ'),0)
                #heightLight Icon
                iconNameCheck = sampleMesh.split('/')[-1].replace('.abc','_png')
                subFolder = sampleMesh.split('/')[-2]
                preIcon = subFolder+'_'+ iconNameCheck+'_button'
                cmd = 'mc.symbolButton("'+preIcon+'", e=1, ebg =1, bgc=[0, 0.4, 0.5]) '
                mc.evalDeferred(cmd)
                if len(selAnyList)>0:
                    placeToSel()
                else:
                    runIt()
                hideSelVis()
        if sampleFileChoice:
            if mc.objExists(sampleFileChoice[0]):
                childNode =   mc.listRelatives(sampleFileChoice[0],type='transform',ad=True,f=True)
                for c in childNode:
                    if not mc.attributeQuery('targetGeo', node = c, ex=True ):
                        mc.addAttr(c, ln='targetGeo',  dt= 'string')
                        mc.setAttr((c+'.targetGeo'),e=True, keyable=True)

def goPressMulti():
    global sampleFileChoice
    global pressFirstTime
    global betweenFirstTime
    global screenX,screenY
    global betweenList
    global betweenListShape
    sampleFileChoice = []
    screenX = 0
    screenY = 0
    betweenList = []
    betweenListShape = []
    betweenFirstTime = 1
    pressFirstTime = 1
    listAssetSelect = whatIsOn()

    for l in listAssetSelect:
        sampleMesh = l
        sampleName = (sampleMesh.split('/')[-1]).split('.')[0]
        mc.CreateEmptyGroup()
        mc.rename(sampleName + '_offset')
        checkName=mc.ls(sl=True)
        meshTypeState = mc.radioButtonGrp('meshImportType', q=True , sl=True)
        if meshTypeState == 3:#gpu
            cacheName = sampleName
            cachePath = sampleMesh
            cacheNode = mc.createNode('gpuCache',name = cacheName+'Cache')
            mc.setAttr(cacheNode+'.cacheFileName',cachePath,type='string')
            mc.parent(cacheNode,checkName)
        else:
            command = 'AbcImport -mode import -reparent '+ checkName[0] + ' ' + '"' + sampleMesh + '"'
            newNode = mel.eval(command)
            mc.xform(ws=1, a=1 ,piv =[0, 0, 0])
            mc.pickWalk(d="down")
            tempSel = mc.ls(sl=True,type='transform',l=True)
            folderName = (sampleMesh.split('/')[-2])
            getShader = mc.getFileList(folder = (meshDirectory+'/Place' +'/'+ folderName) , filespec = '*.ma')
            if len(getShader) == 1:
                if mc.objExists(folderName +'_SHD') == 0:
                    importShader = mc.file( (meshDirectory+'/Place' +'/'+ folderName + '/'+ getShader[0]), i=1, rnn=1, type="mayaAscii", ignoreVersion=1, ra=1, mergeNamespacesOnClash=0, pr=1 )
                    checkShader = []
                    supportType = ['blinn','lambert','RedshiftMaterial','aiStandardSurface']
                    for i  in importShader:
                        nodeTy = mc.nodeType(i)
                        for s in supportType:
                            if nodeTy == s:
                                checkShader = i
                    if checkShader:
                        mc.rename(checkShader,(folderName+'_SHD'))
                        sgNode = mc.sets(renderable=1, noSurfaceShader=1, empty=1, name=(folderName+'_SG'))
                        mc.connectAttr((folderName+'_SHD.outColor'), sgNode+".surfaceShader",f=1)
                mc.sets(tempSel, e=1, fe=(folderName+'_SG'))
            mc.select(tempSel)
        tempSel = mc.ls(sl=True,type='transform')
        mc.select(tempSel[0])
        mc.setAttr((tempSel[0]+'.scaleX'),0)
        mc.setAttr((tempSel[0]+'.scaleY'),0)
        mc.setAttr((tempSel[0]+'.scaleZ'),0)
        sampleFileChoice.append(checkName[0])
        childNode =   mc.listRelatives(checkName[0],type='transform',ad=True,f=True)
        for c in childNode:
            if not mc.attributeQuery('targetGeo', node = c, ex=True ):
                mc.addAttr(c, ln='targetGeo',  dt= 'string')
                mc.setAttr((c+'.targetGeo'),e=True, keyable=True)
    runIt()
    hideSelVis()

def avgVertexNormalAngle(vertexName):
    shapeNode = mc.listRelatives(vertexName, fullPath=True , parent=True )
    transformNode = mc.listRelatives(shapeNode[0], fullPath=True , parent=True )
    faceList = (mc.polyInfo(vertexName , vf=True )[0]).split(':')[-1].split('    ')
    faceList = [x for x in faceList if x.strip()]
    getMeAngle=[]
    sumX = 0
    sumY = 0
    sumZ = 0
    for f in faceList:
        checkNumber = ''.join([n for n in f.split('|')[-1] if n.isdigit()])
        if len(checkNumber) > 0:
            rx, ry, rz = checkFaceAngle((transformNode[0] + '.f[' + str(checkNumber) +']'))
            sumX = sumX + rx
            sumY = sumY + ry
            sumZ = sumZ + rz
    avgX =  sumX /len(faceList)
    avgY =  sumY /len(faceList)
    avgZ =  sumZ /len(faceList)
    return avgX, avgY, avgZ

def checkFaceAngle(faceName):
    shapeNode = mc.listRelatives(faceName, fullPath=True , parent=True )
    transformNode = mc.listRelatives(shapeNode[0], fullPath=True , parent=True )
    obj_matrix = OpenMaya.MMatrix(mc.xform(transformNode, query=True, worldSpace=True, matrix=True))
    face_normals_text = mc.polyInfo(faceName, faceNormals=True)[0]
    face_normals = [float(digit) for digit in re.findall(r'-?\d*\.\d*', face_normals_text)]
    v = OpenMaya.MVector(face_normals) * obj_matrix
    upvector = OpenMaya.MVector (0,1,0)
    getHitNormal = v
    quat = OpenMaya.MQuaternion(upvector, getHitNormal)
    quatAsEuler = OpenMaya.MEulerRotation()
    quatAsEuler = quat.asEulerRotation()
    rx, ry, rz = math.degrees(quatAsEuler.x), math.degrees(quatAsEuler.y), math.degrees(quatAsEuler.z)
    return rx, ry, rz

def getEdgeRingGroup():
    selEdges = mc.ls(sl=1, fl=1)
    trans = selEdges[0].split('.')[0]
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

    retEdges = []
    for f in fEdges:
        collectList = []
        for x in f:
            getCom = trans + '.e[' + str(x) + ']'
            collectList.append(getCom)

        retEdges.append(collectList)

    return retEdges
def vtxLoopOrder():
    selEdges = mc.ls(sl=1,fl=1)
    shapeNode = mc.listRelatives(selEdges[0], fullPath=True , parent=True )
    transformNode = mc.listRelatives(shapeNode[0], fullPath=True , parent=True )
    edgeNumberList = []
    for a in selEdges:
        checkNumber = ((a.split('.')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                edgeNumberList.append(findNumber)
    getNumber = []
    for s in selEdges:
        evlist = mc.polyInfo(s,ev=True)
        checkNumber = ((evlist[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                getNumber.append(findNumber)
    dup = set([x for x in getNumber if getNumber.count(x) > 1])
    getHeadTail = list(set(getNumber) - dup)
    vftOrder = []
    #find Head and Tail
    vftOrder.append(getHeadTail[0])
    count = 0
    while len(dup)> 0 and count < 100:
        checkVtx = transformNode[0]+'.vtx['+ vftOrder[-1] + ']'
        velist = mc.polyInfo(checkVtx,ve=True)
        getNumber = []
        checkNumber = ((velist[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                getNumber.append(findNumber)
        findNextEdge = []
        for g in getNumber:
            if g in edgeNumberList:
                findNextEdge = g
        edgeNumberList.remove(findNextEdge)
        checkVtx = transformNode[0]+'.e['+ findNextEdge + ']'
        findVtx = mc.polyInfo(checkVtx,ev=True)
        getNumber = []
        checkNumber = ((findVtx[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                getNumber.append(findNumber)
        gotNextVtx = []
        for g in getNumber:
            if g in dup:
                gotNextVtx = g
        dup.remove(gotNextVtx)
        vftOrder.append(gotNextVtx)
        count +=  1
    vftOrder.append(getHeadTail[1])
    finalList = []
    for v in vftOrder:
        finalList.append(transformNode[0]+'.vtx['+ v + ']' )
    return finalList


def jwMeshResetRot():
    mc.floatSliderGrp('meshRotSlide' ,e =1, v = 0)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            if mc.objExists(s):
                mc.setAttr((s+'.rotateY'),0)

def jwMeshResetScale():
    mc.floatSliderGrp('meshScaleSlide' ,e =1, v = 1)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            if mc.objExists(s):
                mc.setAttr((s+'.scaleX'),1)
                mc.setAttr((s+'.scaleY'),1)
                mc.setAttr((s+'.scaleZ'),1)

def jwMeshResetDepth():
    mc.floatSliderGrp('meshDepthSlide' ,e =1, v = 0)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            if mc.objExists(s):
                mc.setAttr((s+'.translateY'),0)

def jwMeshResetBetween():
    mc.floatSliderGrp('meshBetweenSlide' ,e =1, v = 0)

def jwMeshResetSnapV():
    mc.floatSliderGrp('snapVSlider' ,e =1, v = 0)

def jwMeshResetRandomRot():
    mc.floatSliderGrp('randomRotSlide' ,e =1, v = 0)
    global SycList
    if len(SycList)>0:
        for s in SycList:
            if mc.objExists(s):
                mc.setAttr((s+'.rotateY'),0)


def jwMeshResetRandomScale():
    mc.floatSliderGrp('randomScaleSlide' ,e =1, v = 0)
    updateRandomScale()


def jwMeshResetBetweenRandom():
    mc.floatSliderGrp('meshBetweenRandomSlide' ,e =1, v = 0)
    updateBetweenRandom()


def iconLightOff():
    getList = collectFullIconList()
    for g in getList:
        try:
            mc.symbolButton(g , e = True, ebg = 0, bgc=[0, 0.4, 0.5])
        except:
            pass

def collectFullIconList():
    global meshDirectory;
    fullIconList = []
    checkDir = os.path.isdir(meshDirectory)
    if checkDir == True :
        currentTabs = mc.tabLayout('rapidTab',q=1,st=1)
        subFolder = []
        if currentTabs == 'Place':
            subFolder = mc.getFileList(folder = meshDirectory+'/Place')
        elif currentTabs == 'Stamp':
            subFolder = mc.getFileList(folder = meshDirectory+'/Stamp')
        for s in subFolder:
            checkSubDir = os.path.isdir(meshDirectory+'/'+ currentTabs +'/'+s)
            if checkSubDir == True:
                iconsCollection = []
                iconPath = []
                iconsCollection = mc.getFileList(folder = (meshDirectory+'/'+ currentTabs +'/'+s) , filespec = '*.png')
                for i in iconsCollection:
                    iconPath = meshDirectory + '/'+ s + '/' + i
                    iconNameCheck = iconPath.split('/')[-1].replace('.','_')
                    subFolder = iconPath.split('/')[-2]
                    preIcon = subFolder+'_'+ iconNameCheck+'_button'
                    fullIconList.append(preIcon)
    return fullIconList


def whatIsOn():
    global meshDirectory;
    getList = collectFullIconList()
    iconOnList = []
    for g in getList:
        iconState = mc.symbolButton(g, q=True, bgc=True)
        if iconState[1]>0:
            #get file path
            subFolder = g.split('|')[-1].split('_')[0]
            assetName = g.split('|')[-1].split('_')[1:-2]
            asset = '_'.join(assetName)+'.abc'
            path = meshDirectory + '/Place/' + subFolder +'/' + asset
            iconOnList.append(path)
    return iconOnList

def meshBox2dArea(meshName):
    global lastPanelActive
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()
    cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
    xlist = []
    ylist = []
    bbox = mc.exactWorldBoundingBox(meshName)
    xmin = bbox[0]
    ymin = bbox[1]
    zmin = bbox[2]
    xmax = bbox[3]
    ymax = bbox[4]
    zmax = bbox[5]
    bboxList=[]
    cv1 =(xmin,ymin,zmin)
    bboxList.append(cv1)
    cv2 =(xmin,ymin,zmax)
    bboxList.append(cv2)
    cv3 =(xmin,ymax,zmin)
    bboxList.append(cv3)
    cv4 =(xmin,ymax,zmax)
    bboxList.append(cv4)
    cv5 =(xmax,ymin,zmin)
    bboxList.append(cv5)
    cv6 =(xmax,ymin,zmax)
    bboxList.append(cv6)
    cv7 =(xmax,ymax,zmin)
    bboxList.append(cv7)
    cv8 =(xmax,ymax,zmax)
    bboxList.append(cv8)
    for i in bboxList:
        px = float(str(i).split(',')[0].replace('(','').replace(')',''))
        py = float(str(i).split(',')[1].replace('(','').replace(')',''))
        pz = float(str(i).split(',')[2].replace('(','').replace(')',''))
        pos2d = checkWorldSpaceToImageSpace(cameraTrans[0], (px,py,pz))
        xlist.append(pos2d[0])
        ylist.append(pos2d[1])
    sorted(xlist)
    xMin = xlist[0]
    xMax = xlist[-1]
    sorted(ylist)
    yMin = ylist[0]
    yMax = ylist[-1]
    area2d = (xMax - xMin)*(yMax - yMin)
    return area2d

def moveIt():
    # for now instance will crash maya because the share same shape node,
    any = getInstances()
    if len:
        print( 'function does not support any instance and gpu cache')
    global ctx
    ctx = 'Click2dTo3dCtx'
    # Delete dragger context if it already exists
    if mc.draggerContext(ctx, exists=True):
        mc.deleteUI(ctx)
    # Create dragger context and set it to the active tool
    mc.draggerContext(ctx, pressCommand = pickMovingMesh, rc = releaseMesh, dragCommand = rePostionMesh, name=ctx, cursor='crossHair',undoMode='step')
    mc.setToolTo(ctx)


def pickMovingMesh():
    global ctx
    global SycList
    global currentScaleRecord
    global currentRotRecord
    global screenX,screenY
    currentScaleX = mc.floatSliderGrp('stampScaleSlide', q=True, v=True)
    currnetRotY =  mc.floatSliderGrp('stampRotSlide', q=True, v=True)
    currentRotRecord = currnetRotY
    currentScaleRecord = currentScaleX
    presel = mc.ls(sl=1,fl=1,l=1)
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY
    pos = om.MPoint()
    dir = om.MVector()
    hitpoint = om.MFloatPoint()
    omui.M3dView().active3dView().viewToWorld(int(vpX), int(vpY), pos, dir)
    pos2 = om.MFloatPoint(pos.x, pos.y, pos.z)
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()
    cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
    cameraPosition = mc.xform(cameraTrans,q=1,ws=1,rp=1)
    checkHit = 0
    finalMesh = []
    finalX = []
    finalY = []
    finalZ = []
    shortDistance = 10000000000
    distanceBetween = 1000000000
    hitFacePtr = om.MScriptUtil().asIntPtr()
    hitFace = []
    checkVisList = screenVisPoly()
    for mesh in checkVisList:
        selectionList = om.MSelectionList()
        selectionList.add(mesh)
        dagPath = om.MDagPath()
        selectionList.getDagPath(0, dagPath)
        fnMesh = om.MFnMesh(dagPath)

        intersection = fnMesh.closestIntersection(
        om.MFloatPoint(pos2),
        om.MFloatVector(dir),
        None,
        None,
        False,
        om.MSpace.kWorld,
        99999,
        False,
        None,
        hitpoint,
        None,
        hitFacePtr,
        None,
        None,
        None)
        if intersection:
            x = hitpoint.x
            y = hitpoint.y
            z = hitpoint.z
            distanceBetween = math.sqrt( ((float(cameraPosition[0]) - x)**2)  + ((float(cameraPosition[1]) - y)**2) + ((float(cameraPosition[2]) - z)**2))
            if distanceBetween < shortDistance:
                shortDistance = distanceBetween
                finalMesh = mesh
                finalX = x
                finalY = y
                finalZ = z
                hitFace = om.MScriptUtil(hitFacePtr).asInt()
    if len(finalMesh) > 0:
        transNode=mc.listRelatives(finalMesh,type='transform',p=True,f=True)
        if mc.attributeQuery('targetGeo', node = transNode[0], ex=True ):
            get = mel.eval('rootOf '+transNode[0])
            sampleTrans=mc.listRelatives(get,type='transform',c=True,f=True)
            SycList = []
            SycList.append(sampleTrans[0])
            mc.select(get)
            mc.refresh(cv=True,f=True)


def releaseMesh():
    pass

def rePostionMesh():
    selSample = mc.ls(sl=True,fl=True)
    if len(selSample)>0:
        global ctx
        global lastPanelActive
        global currentScaleRecord
        global currentRotRecord
        global screenX,screenY
        currentSX = 0
        currnetSY = 0
        lastPanelActive = mc.getPanel(underPointer=True)
        checkSnapState = mc.radioButtonGrp('snapType',q=True, sl =True )
        modifiers = mc.getModifiers()
        meshNode = mc.listRelatives(selSample[0],c=True, typ = 'transform',f=True)
        if (modifiers == 4):
            #print 'ctrl Press'
            vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
            distanceA = (vpX - screenX)
            rotateCheck = (distanceA)
            rotateRun = currentRotRecord + rotateCheck
            if rotateRun > 180 :
                rotateRun = 180
            elif rotateRun < -180 :
                rotateRun = -180
            getR = int(rotateRun / 15)*15
            if rotateRun != getR:
                rotateRun = getR
            mc.floatSliderGrp( 'stampRotSlide', e=1 ,v = rotateRun )
            mc.setAttr((meshNode[0]+'.rotateY'),rotateRun)
        elif(modifiers == 1):
            #print 'shift selSample'
            vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
            distanceB = vpX - screenX
            scaleCheck = distanceB / 100
            scaleRun = currentScaleRecord + scaleCheck
            if scaleRun > 5:
                scaleRun = 5
            elif scaleRun < 0.1:
                scaleRun = 0.1
            mc.floatSliderGrp( 'stampScaleSlide', e=1 ,v = scaleRun )
            mc.setAttr((meshNode[0]+'.scaleX'),scaleRun)
            mc.setAttr((meshNode[0]+'.scaleY'),scaleRun)
            mc.setAttr((meshNode[0]+'.scaleZ'),scaleRun)
        else:
            vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
            currentSX = vpX
            currentSY = vpY
            pos = om.MPoint()
            dir = om.MVector()
            hitpoint = om.MFloatPoint()
            omui.M3dView().active3dView().viewToWorld(int(vpX), int(vpY), pos, dir)
            pos2 = om.MFloatPoint(pos.x, pos.y, pos.z)
            #current camera
            view = omui.M3dView.active3dView()
            cam = om.MDagPath()
            view.getCamera(cam)
            camPath = cam.fullPathName()
            cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
            cameraPosition = mc.xform(cameraTrans,q=1,ws=1,rp=1)
            checkHit = 0
            finalMesh = []
            finalX = 0
            finalY = 0
            finalZ = 0
            shortDistance = 10000000000
            distanceBetween = 1000000000
            meshNode = mc.listRelatives(selSample, fullPath=True ,ad=True)
            myShape = mc.listRelatives(meshNode, shapes=True,f=True)
            checkVisListA = screenVisPoly()
            if myShape == None:#gpu
                checkListA =  list(set(checkVisListA))
            else:
                checkListA =  list(set(checkVisListA)-set(myShape))
            hitFacePtr = om.MScriptUtil().asIntPtr()
            hitFace = []
            for mesh in checkListA:
                selectionList = om.MSelectionList()
                selectionList.add(mesh)
                dagPath = om.MDagPath()
                selectionList.getDagPath(0, dagPath)
                fnMesh = om.MFnMesh(dagPath)
                intersection = fnMesh.closestIntersection(
                om.MFloatPoint(pos2),
                om.MFloatVector(dir),
                None,
                None,
                False,
                om.MSpace.kWorld,
                99999,
                False,
                None,
                hitpoint,
                None,
                hitFacePtr,
                None,
                None,
                None)

                if intersection:
                    x = hitpoint.x
                    y = hitpoint.y
                    z = hitpoint.z
                    distanceBetween = math.sqrt( ((float(cameraPosition[0]) - x)**2)  + ((float(cameraPosition[1]) - y)**2) + ((float(cameraPosition[2]) - z)**2))

                    if distanceBetween < shortDistance:
                        shortDistance = distanceBetween
                        finalMesh = mesh
                        hitFace = om.MScriptUtil(hitFacePtr).asInt()
                        finalX = x
                        finalY = y
                        finalZ = z

                    mc.setAttr((selSample[0] + '.translateX'), finalX)
                    mc.setAttr((selSample[0] + '.translateY'), finalY)
                    mc.setAttr((selSample[0] + '.translateZ'), finalZ)

                    #######################################################################
                    childNode =   mc.listRelatives(selSample[0],type='transform',ad=True,f=True)
                    transNode=mc.listRelatives(finalMesh,type='transform',p=True)
                    for c in childNode:
                        mc.setAttr((c + '.targetGeo'),transNode[0],type="string")
                   #########################################################################
                    if checkSnapState == 1:
                        hitFaceName = (finalMesh + '.f[' + str(hitFace) +']')
                        rx, ry, rz = checkFaceAngle(hitFaceName)
                        mc.setAttr((selSample[0] + '.rotateX'), rx)
                        mc.setAttr((selSample[0] + '.rotateY'), ry)
                        mc.setAttr((selSample[0] + '.rotateZ'), rz)
                    lockVtxCheck = mc.floatSliderGrp('snapVSlider', q=True, v=True)
                    if (lockVtxCheck > 0):
                        cvX = 0
                        cvY = 0
                        cvZ = 0
                        shortDistanceCheck = 10000
                        checkCVDistance = 10000
                        mostCloseDist = lockVtxCheck
                        hitFaceName = (finalMesh + '.f[' + str(hitFace) +']')
                        cvList = (mc.polyInfo(hitFaceName , fv=True )[0]).split(':')[-1].split('    ')
                        cvList = [x for x in cvList if x.strip()]
                        mostCloseCVPoint = []
                        for v in cvList:
                            checkNumber = ''.join([n for n in v.split('|')[-1] if n.isdigit()])
                            if len(checkNumber) > 0:
                                cvPoint = (finalMesh + '.vtx[' + str(checkNumber) +']')
                                cvPosition = mc.pointPosition(cvPoint)
                                checkCVDistance = math.sqrt( ((float(cvPosition[0]) - finalX)**2)  + ((float(cvPosition[1]) - finalY)**2) + ((float(cvPosition[2]) - finalZ)**2))
                                if checkCVDistance < shortDistanceCheck:
                                    shortDistanceCheck = checkCVDistance
                                    cvX = float(cvPosition[0])
                                    cvY = float(cvPosition[1])
                                    cvZ = float(cvPosition[2])
                                    mostCloseCVPoint = cvPoint
                        if shortDistanceCheck < mostCloseDist:
                            mc.setAttr((selSample[0] + '.translateX'), cvX)
                            mc.setAttr((selSample[0] + '.translateY'), cvY)
                            mc.setAttr((selSample[0] + '.translateZ'), cvZ)
                            #get average normal angle from suround faces
                            rX,rY,rZ = avgVertexNormalAngle(cvPoint)
                            mc.setAttr(selSample[0]+'.rotateX', rX)
                            mc.setAttr(selSample[0]+'.rotateY', rY)
                            mc.setAttr(selSample[0]+'.rotateZ', rZ)
            mc.select(selSample[0])
        mc.refresh(cv=True,f=True)


def getInstances():
    instances = []
    iterDag = om.MItDag(om.MItDag.kBreadthFirst)
    while not iterDag.isDone():
        instanced = om.MItDag.isInstanced(iterDag)
        if instanced:
            instances.append(iterDag.fullPathName())
        iterDag.next()
    return instances

def goStamp(sampleMesh):
    check = mc.button('killModeButton', q =1 , bgc = 1)
    if check[0] == 1:
        removeIcon(sampleMesh)
    else:
        checkType = mc.radioButtonGrp('stampType',q=True, sl=True )
        if checkType == 1:
            deSelect()
            global sampleFileChoice
            global currentScaleRecord
            global checkVisList
            screenX = 0
            screenY = 0
            selectionPool = []
            checkVisList = screenVisPoly()
            iconLightOff()
            sampleName = (sampleMesh.split('/')[-1]).split('.')[0]
            mc.CreateEmptyGroup()
            mc.rename(sampleName + '_offset')
            checkName=mc.ls(sl=True)
            sampleFileChoice = checkName
            meshTypeState = mc.radioButtonGrp('meshImportType', q=True , sl=True)
            command = 'AbcImport -mode import -reparent '+ checkName[0] + ' ' + '"' + sampleMesh + '"'
            newNode = mel.eval(command)
            mc.xform(ws=1, a=1 ,piv =[0, 0, 0])
            mc.pickWalk(d="down")
            tempSel = mc.ls(sl=True,type='transform',l=True)
            mc.setAttr((sampleFileChoice[0]+'.scaleX'),0)
            mc.setAttr((sampleFileChoice[0]+'.scaleY'),0)
            mc.setAttr((sampleFileChoice[0]+'.scaleZ'),0)
            #########################################################################
            if not mc.attributeQuery('targetGeo', node = tempSel[0], ex=True ):
                mc.addAttr(tempSel[0], ln='targetGeo',  dt= 'string')
                mc.setAttr((tempSel[0]+'.targetGeo'),e=True, keyable=True)
            #########################################################################
            iconNameCheck = sampleMesh.split('/')[-1].replace('.abc','_png')
            subFolder = sampleMesh.split('/')[-2]
            preIcon = subFolder+'_'+ iconNameCheck+'_button'
            cmd = 'mc.symbolButton("'+preIcon+'", e=1, ebg =1, bgc=[0, 0.4, 0.5]) '
            mc.evalDeferred(cmd)
            stampIt()
            hideSelVis()
        else:
            blendStamp(sampleMesh)

def stampIt():
    global ctx
    ctx = 'Click2dTo3dCtx'
    # Delete dragger context if it already exists
    if mc.draggerContext(ctx, exists=True):
        mc.deleteUI(ctx)
    # Create dragger context and set it to the active tool
    mc.draggerContext(ctx, pressCommand = onPressStamp, rc = offPressStamp, dragCommand = onDragStamp, name=ctx, cursor='crossHair',undoMode='step')
    mc.setToolTo(ctx)


def offPressStamp():
    global sampleFileChoice
    global lastPanelActive
    meshSelNode=mc.listRelatives(sampleFileChoice[0],type='transform',c=True,f=True)
    mc.select(meshSelNode)
    mc.setToolTo('moveSuperContext')
    if 'modelPanel' not in lastPanelActive:
        lastPanelActive = 'modelPanel4'
    mc.modelEditor(lastPanelActive, e=True, sel=True)
    iconLightOff()

def onPressStamp():
    global ctx
    global sampleFileChoice
    global checkVisList
    global screenX,screenY
    global currentScaleRecord
    global currentRotRecord
    global lastPanelActive
    lastPanelActive = mc.getPanel(underPointer=True)
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY
    meshNode = mc.listRelatives(sampleFileChoice[0],c=True, typ = 'transform',f=True)
    myShape = mc.listRelatives(meshNode, shapes=True,f=True)
    wx,wy,wz,hitmesh,hitFace= getPosition(screenX,screenY)
    lastSnapMesh = hitmesh
    mc.setAttr((sampleFileChoice[0] + '.translateX'), wx)
    mc.setAttr((sampleFileChoice[0] + '.translateY'), wy)
    mc.setAttr((sampleFileChoice[0] + '.translateZ'), wz)
    hitFaceName = (hitmesh + '.f[' + str(hitFace) +']')
    rx, ry, rz = checkFaceAngle(hitFaceName)
    mc.setAttr((sampleFileChoice[0] + '.rotateX'), rx)
    mc.setAttr((sampleFileChoice[0] + '.rotateY'), ry)
    mc.setAttr((sampleFileChoice[0] + '.rotateZ'), rz)
    mc.setAttr((sampleFileChoice[0]+'.scaleX'),1)
    mc.setAttr((sampleFileChoice[0]+'.scaleY'),1)
    mc.setAttr((sampleFileChoice[0]+'.scaleZ'),1)
    currentScaleX = mc.floatSliderGrp('stampScaleSlide', q=True, v=True)
    currnetRotY =  mc.floatSliderGrp('stampRotSlide', q=True, v=True)
    mc.setAttr((meshNode[0]+'.scaleX'),currentScaleX)
    mc.setAttr((meshNode[0]+'.scaleY'),currentScaleX)
    mc.setAttr((meshNode[0]+'.scaleZ'),currentScaleX)
    mc.setAttr((meshNode[0]+'.rotateY'),currnetRotY)
    currentRotRecord = currnetRotY
    currentScaleRecord = currentScaleX
    #########################################################################
    transNode=mc.listRelatives(lastSnapMesh,type='transform',p=True)
    meshSelNode=mc.listRelatives(sampleFileChoice[0],type='transform',c=True,f=True)
    mc.setAttr((meshSelNode[0] + '.targetGeo'),transNode[0],type="string")
    #########################################################################

    mc.refresh(cv=True,f=True)

def jwStampResetOffset():
    mc.intSliderGrp( 'bridfeOffsetSlide',e= 1,v = 1)


def jwStampResetRot():
    global sampleFileChoice
    mc.floatSliderGrp( 'stampRotSlide', e=1 ,v = 0 )
    if sampleFileChoice:
        if sampleFileChoice[0] == 'sampleLoc':
            mc.setAttr('sampleLoc.rotateY',0)
        else:
            meshNode = mc.listRelatives(sampleFileChoice[0],c=True, typ = 'transform',f=True)
            mc.setAttr((meshNode[0]+'.rotateY'),0)

def jwStampSetRot(angle):
    global sampleFileChoice
    if mc.objExists(sampleFileChoice[0]):
        if sampleFileChoice[0] == 'sampleLoc':
            mc.setAttr('sampleLoc.rotateY',angle)
        else:
            meshNode = mc.listRelatives(sampleFileChoice[0],c=True, typ = 'transform',f=True)
            mc.setAttr((meshNode[0]+'.rotateY'),angle)
            mc.floatSliderGrp( 'stampRotSlide', e=1 ,v = angle )

def jwStampUpdateRot():
    global sampleFileChoice
    if mc.objExists(sampleFileChoice[0]):
        rotXXX = mc.floatSliderGrp( 'stampRotSlide', q=1 ,v = True )
        if sampleFileChoice[0] == 'sampleLoc':
            mc.setAttr('sampleLoc.rotateY',rotXXX)
        else:
            meshNode = mc.listRelatives(sampleFileChoice[0],c=True, typ = 'transform',f=True)
            mc.setAttr((meshNode[0]+'.rotateY'),rotXXX)

def jwStampUpdateHScale():
    global sampleFileChoice
    if mc.objExists(sampleFileChoice[0]):
        scaleYYY = mc.floatSliderGrp( 'stampScaleHSlide', q=1 ,v = True )
        if sampleFileChoice[0] == 'sampleLoc':
            mc.setAttr((sampleFileChoice[0]+'.scaleY'),scaleYYY)
        else:
            meshNode = mc.listRelatives(sampleFileChoice[0],c=True, typ = 'transform',f=True)
            mc.setAttr((meshNode[0]+'.scaleY'),scaleYYY)

def jwStampUpdateScale():
    global sampleFileChoice
    scaleXXX = mc.floatSliderGrp( 'stampScaleSlide', q=1 ,v = True )
    state = mc.button('stampScaleHToggle', q=True, bgc=True)
    if not state[0] == 0:
        mc.floatSliderGrp( 'stampScaleHSlide', e=1 ,v = scaleXXX )
    if mc.objExists(sampleFileChoice[0]):
        if sampleFileChoice[0] == 'sampleLoc':
            mc.setAttr((sampleFileChoice[0]+'.scaleX'),scaleXXX)
            mc.setAttr((sampleFileChoice[0]+'.scaleZ'),scaleXXX)
            if not state[0] == 0:
                mc.setAttr((sampleFileChoice[0]+'.scaleY'),scaleXXX)
        else:
            meshNode = mc.listRelatives(sampleFileChoice[0],c=True, typ = 'transform',f=True)
            mc.setAttr((meshNode[0]+'.scaleX'),scaleXXX)
            mc.setAttr((meshNode[0]+'.scaleZ'),scaleXXX)
            if not state[0] == 0:
                mc.setAttr((meshNode[0]+'.scaleY'),scaleXXX)

def jwStampResetScale():
    global sampleFileChoice
    mc.floatSliderGrp( 'stampScaleSlide', e = 1 ,v= 1 )
    mc.floatSliderGrp( 'stampScaleHSlide', e = 1 ,v= 1 )
    if mc.objExists(sampleFileChoice[0]):
        meshNode = mc.listRelatives(sampleFileChoice[0],c=True, typ = 'transform',f=True)
        mc.setAttr((meshNode[0]+'.scaleX'),1)
        mc.setAttr((meshNode[0]+'.scaleY'),1)
        mc.setAttr((meshNode[0]+'.scaleZ'),1)

def onDragStamp():
    global ctx
    global sampleFileChoice
    global checkVisList
    global screenX,screenY
    global currentScaleRecord
    currentSX = 0
    currnetSY = 0
    meshNode = mc.listRelatives(sampleFileChoice[0],c=True, typ = 'transform',f=True)
    myShape = mc.listRelatives(meshNode, shapes=True,f=True)
    modifiers = mc.getModifiers()
    if (modifiers == 4):
        #print 'ctrl Press'
        vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
        distanceA = (vpX - screenX)
        rotateCheck = (distanceA)
        rotateRun = currentRotRecord + rotateCheck
        if rotateRun > 180 :
            rotateRun = 180
        elif rotateRun < -180 :
            rotateRun = -180
        getR = int(rotateRun / 15)*15
        if rotateRun != getR:
            rotateRun = getR
        mc.floatSliderGrp( 'stampRotSlide', e=1 ,v = rotateRun )
        mc.setAttr((meshNode[0]+'.rotateY'),rotateRun)
    elif(modifiers == 1):
        #print 'shift selSample'
        vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
        distanceB = vpX - screenX
        scaleCheck = distanceB / 100
        scaleRun = currentScaleRecord + scaleCheck
        if scaleRun > 5:
            scaleRun = 5
        elif scaleRun < 0.1:
            scaleRun = 0.1
        mc.floatSliderGrp( 'stampScaleSlide', e=1 ,v = scaleRun )
        mc.setAttr((meshNode[0]+'.scaleX'),scaleRun)
        mc.setAttr((meshNode[0]+'.scaleY'),scaleRun)
        mc.setAttr((meshNode[0]+'.scaleZ'),scaleRun)
    else:
        vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
        screenX = vpX
        screenY = vpY
        wx,wy,wz,hitmesh,hitFace= getPosition(screenX,screenY)
        lastSnapMesh = hitmesh
        mc.setAttr((sampleFileChoice[0] + '.translateX'), wx)
        mc.setAttr((sampleFileChoice[0] + '.translateY'), wy)
        mc.setAttr((sampleFileChoice[0] + '.translateZ'), wz)
        hitFaceName = (hitmesh + '.f[' + str(hitFace) +']')
        rx, ry, rz = checkFaceAngle(hitFaceName)
        mc.setAttr((sampleFileChoice[0] + '.rotateX'), rx)
        mc.setAttr((sampleFileChoice[0] + '.rotateY'), ry)
        mc.setAttr((sampleFileChoice[0] + '.rotateZ'), rz)

        transNode=mc.listRelatives(hitmesh,type='transform',p=True,f=True)
        meshSelNode=mc.listRelatives(sampleFileChoice[0],type='transform',c=True,f=True)
        mc.setAttr((meshSelNode[0] + '.targetGeo'),transNode[0],type="string")
    mc.refresh(cv=True,f=True)

def convertStamp():
    selSampleLong = mc.ls(sl=1,fl=1,l=1)
    if selSampleLong:
        selSample = selSampleLong[0].split('|')[1]
        meshNode = mc.listRelatives(selSample,type='transform',c=True,f=True)
        if len(selSample) > 0:
            mc.undoInfo( openChunk= True, cn = 'convertStamp' )
            meshSample = meshNode[0]
            cleanSceneList = {'protectFace','stampFace','quickCutterSet','sampleCutter','quickEdgeCV','quickCheckCV'}
            for c in cleanSceneList:
                if mc.objExists(c):
                    mc.delete(c)
            target = mc.getAttr(meshSample+'.targetGeo')
            targetShapeName =  mc.listRelatives(target,s=1,c=True,f=True)
            getFlatList = []
            targetCopy = []
            if  mc.attributeQuery('flatList', node = meshSample, ex=True ):
                getFlatList=mc.getAttr(meshSample+'.flatList')
                flatFace  = getFlatList.split(' ')
                mc.select(flatFace)
                mc.InvertSelection()
                mc.sets( name = 'protectFace' , text = 'protectFace')
                targetCopy = mc.duplicate(target, rr=True)
            #build cutter
            #check outter Type
            cageChild =  mc.listRelatives(meshSample,typ='transform',c=True,f=True)
            if cageChild:
                mc.group(cageChild)
                mc.parent(w=1)
                mc.rename((selSample.split('_')[0]+'Grp1'))
                mc.rename(meshSample,'sampleCutter')
                mc.select('sampleCutter')
                mc.DeleteHistory()
                mc.polyCBoolOp(target,'sampleCutter', op= 2 , ch= 1 , preserveColor = 0, classification= 1, name = (target))
                mc.delete(ch=1)
                mc.rename(target)
            else:
                shapeNode = mc.listRelatives(meshSample, fullPath=True , c=True )
                if mc.attributeQuery('booleanMesh', node = shapeNode[0], ex=True ):
                    mc.polyCBoolOp(target,meshSample, op= 2 , ch= 1 , preserveColor = 0, classification= 1, name = (target))
                    mc.delete(ch=1)
                    mc.rename(target)
                else:
                    #border type
                    mc.lattice(selSampleLong[0],divisions=(2,2,2), objectCentered=True, ldv=(2,2,2), n='templattice')
                    cCenter = mc.xform('templatticeLattice', q=1, t=1)
                    cRrotate =  mc.xform('templatticeLattice' , q=1, ro=1)
                    cScale  = mc.xform('templatticeLattice' , q=1, r=1,s=1)
                    cageBox = mc.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), ch=0, n= 'cageBBox')
                    mc.xform(cageBox[0], t=( cCenter[0], cCenter[1], cCenter[2]),ro = ( cRrotate[0], cRrotate[1], cRrotate[2]),s= ( cScale[0], cScale[1], cScale[2]))
                    mc.rename('sampleCutter')
                    mc.delete('templatticeLattice*')
                    getScaleY = mc.getAttr('sampleCutter.scaleY')
                    mc.setAttr(('sampleCutter.scaleY'),getScaleY*1.1)
                    #create sampleCutter with right edge number
                    mc.parent('sampleCutter',selSample)
                    recordRotX = mc.getAttr(selSample + '.rotateX')
                    recordRotY = mc.getAttr(selSample + '.rotateY')
                    recordRotZ = mc.getAttr(selSample + '.rotateZ')
                    mc.setAttr((selSample + '.rotateX'),0)
                    mc.setAttr((selSample + '.rotateY'),0)
                    mc.setAttr((selSample + '.rotateZ'),0)
                    mc.select(meshSample)
                    getEdgeFace = mc.duplicate(rr=1)
                    mc.ConvertSelectionToEdges()
                    mc.ConvertSelectionToEdgePerimeter()
                    mc.polyExtrudeEdge(constructionHistory = False, keepFacesTogether =True, divisions = 1, thickness = 0.1 ,smoothingAngle = 30)
                    mc.ConvertSelectionToFaces()
                    mc.InvertSelection()
                    mc.delete()
                    bbox = mc.xform('sampleCutter',q=True,bb=True,ws=1)
                    mc.select(getEdgeFace)
                    mc.ConvertSelectionToEdges()
                    mc.ConvertSelectionToEdgePerimeter()
                    elList = mc.ls(sl=1,fl=1)
                    mc.select(elList[0])
                    mc.polySelectSp(loop=1)
                    elOne = mc.xform(q=True,bb=True,ws=1)
                    firstEl = mc.ls(sl=1,fl=1)
                    mc.select(elList)
                    mc.select(firstEl,d=1)
                    elTwo = mc.xform(q=True,bb=True,ws=1)
                    topEl = []
                    bottomEl = []
                    if elOne[1] < elTwo[1]:
                        topEl = mc.ls(sl=1,fl=1)
                        bottomEl = firstEl
                        mc.scale(1, 0, 1, bottomEl, a=1, p=[0, elOne[1], 0], )
                    else:
                        bottomEl = mc.ls(sl=1,fl=1)
                        topEl = firstEl
                        mc.scale(1, 0, 1, bottomEl, a=1, p=[0, elTwo[1], 0], )
                    mc.scale(1, 0, 1, bottomEl, a=1, p=[0, bbox[1], 0], )
                    mc.select(bottomEl)
                    mc.FillHole()
                    mc.select(getEdgeFace)
                    mc.ConvertSelectionToEdges()
                    mc.ConvertSelectionToEdgePerimeter()
                    mc.ConvertSelectionToFaces()
                    mc.delete()
                    mc.select(getEdgeFace)
                    mc.ConvertSelectionToFaces()
                    mc.polyExtrudeFacet(constructionHistory = False, keepFacesTogether =True)
                    mc.scale(1, 0, 1,  a=1, p=[0, bbox[4], 0], )
                    mc.delete('sampleCutter')
                    mc.rename(getEdgeFace,'sampleCutter')
                    mc.delete('sampleCutter',ch=1)
                    mc.setAttr((selSample + '.rotateX'),recordRotX )
                    mc.setAttr((selSample + '.rotateY'),recordRotY )
                    mc.setAttr((selSample + '.rotateZ'),recordRotZ )
                    mc.select('sampleCutter')
                    mc.DeleteHistory()
                    mc.ConvertSelectionToFaces()
                    mc.sets( name = 'quickCutterSet' , text = 'quickCutterSet')
                    mc.polyCBoolOp(target,'sampleCutter', op= 2 , ch= 1 , preserveColor = 0, classification= 1, name = (target))
                    tempName = mc.ls(sl=1,fl=1)
                    mc.select('quickCutterSet')
                    newList = mc.ls(sl=True,fl=True)
                    cleanList = []
                    for n in newList:
                        if mc.objExists(n):
                            cleanList.append(n)
                    mc.select(cleanList)
                    mc.ShrinkPolygonSelectionRegion()
                    mc.ConvertSelectionToEdges()
                    mc.GrowPolygonSelectionRegion()
                    mc.polySelectConstraint(m=2, t=0x8000, sm=1 , m2a =30, m3a = 45, pp =4)
                    mc.polySelectConstraint(m =0)
                    mc.ConvertSelectionToVertices()
                    mc.sets( name = 'quickEdgeCV' , text = 'quickEdgeCV')
                    mc.select(cleanList)
                    mc.ConvertSelectionToVertexPerimeter()
                    mc.select('quickEdgeCV',d=1)
                    mc.sets( name = 'quickCheckCV' , text = 'quickCheckCV')
                    mc.select(cleanList)
                    mc.delete()
                    mc.select('quickCheckCV')
                    checkCVList = mc.ls(sl=1,fl=1)
                    mc.select('quickEdgeCV')
                    checkLockCV = mc.ls(sl=1,fl=1)
                    for c in checkCVList:
                        shorestDis = 10000
                        getCloseCV = []
                        getCloseCVPos = []
                        p1 = mc.pointPosition(c, w = True)
                        for l in checkLockCV:
                            p2 = mc.pointPosition(l, w = True)
                            length=math.sqrt((math.pow(p2[0]-p1[0],2)+math.pow(p2[1]-p1[1],2)+math.pow(p2[2]-p1[2],2))/3)
                            if length < shorestDis:
                                shorestDis = length
                                getCloseCV = l
                                getCloseCVPos = p2
                        mc.select(c)
                        mc.move(getCloseCVPos[0], getCloseCVPos[1],getCloseCVPos[2],absolute=1)
                    mc.select('quickEdgeCV','quickCheckCV')
                    mc.polyMergeVertex(d= 0.01, am = 1, ch = 0)
                    mc.delete('quickEdgeCV','quickCheckCV')
                    mc.select(meshSample)
                    mc.ConvertSelectionToFaces()
                    mc.sets( name = 'stampFace' , text = 'stampFace')
                    mc.select(tempName,meshSample)
                    mc.polyUnite(ch= 0, mergeUVSets =1, name = target)
                    testName = mc.ls(sl=1,fl=1)
                    mc.rename(testName[0],target)
                    mc.select(target)
                    #this should make merge more accurate, but cause lots error, very buggy
                    #mc.polySelectConstraint(mode =3, type = 0x8000 ,where =1)
                    #psc = 'mc.ConvertSelectionToVertices()'
                    #mc.evalDeferred(psc)
                    #mc.polySelectConstraint(m =0)
                    mergeNode = mc.polyMergeVertex(d = 0.005, am =1, ch= 0)
                    targetShapeNameNew =  mc.listRelatives(target,s=1,c=True)
                    if targetShapeNameNew != targetShapeName:
                        mc.rename(targetShapeNameNew,targetShapeName)
                    if len(getFlatList) > 0:
                        mc.select('protectFace')
                        mc.InvertSelection()
                        newListName = mc.ls(sl=1)
                        mc.transferAttributes(targetCopy[0], newListName ,pos=0, uvs = 0 , nml=1, searchMethod = 0)
                        mc.select(target)
                        mc.delete(ch=1)
                        mc.delete(targetCopy[0])
                    #need to clean up scene before use and after use
                    mc.select('stampFace')
                    current = mc.ls(sl=True)
                    mel.eval('doMenuComponentSelection("%s", "facet")' % target)
                    mc.select(current, r=True)
                    for c in cleanSceneList:
                        if mc.objExists(c):
                            mc.delete(c)
                    if mc.objExists(selSample):
                        mc.delete(selSample)
            mc.undoInfo( closeChunk = True )
        iconLightOff()
    else:
        print('please select one stamp mesh')



def deSelect():
    obj_shape = mc.listRelatives(parent=True, f=True)
    obj = mc.listRelatives(obj_shape,parent=True, f=True)
    mc.select(obj)
    mc.selectMode(leaf=True)
    cmd = "changeSelectMode -object;"
    mel.eval(cmd)
    mc.select(clear=True)



def facePivotLocator():
    faceinfo = facePivotInfo()
    mc.spaceLocator(p =(faceinfo[0],faceinfo[1],faceinfo[2]))
    mc.xform(ws=True, ro = (faceinfo[3],faceinfo[4],faceinfo[5]))


def getFacePivotInfo(faceName):
    facesSelected = mc.filterExpand(selFace,expand=True ,sm=34)
    if facesSelected:
        rx, ry, rz = checkFaceAngle(facesSelected)
        meshFaceName = faceName.split('.')[0]
        findVtx = mc.polyInfo(faceName, fv=1)
        getNumber = []
        checkNumber = ((findVtx[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                getNumber.append(findNumber)
        centerX = 0
        centerY = 0
        centerZ = 0
        for g in getNumber:
            x,y,z = mc.pointPosition((meshFaceName + '.vtx['+g + ']'),w=1)
            centerX = centerX + x
            centerY = centerY + y
            centerZ = centerZ + z

        centerX = centerX/len(getNumber)
        centerY = centerY/len(getNumber)
        centerZ = centerZ/len(getNumber)
        return centerX,centerY,centerZ,rx,ry,rz




def facePivotInfo():
    mc.manipPivot(rp=True)
    facesSelected = mc.filterExpand(expand=True ,sm=34)
    posStore = [0,0,0]
    rotStore = [0,0,0]
    if len(facesSelected) == 1:
        #mc.undoInfo(openChunk=True)
        mc.select(facesSelected)
        #make sure select face mode
        cmd = 'doMenuComponentSelection("' + facesSelected[0].split('.')[0] +'", "facet");'
        mel.eval(cmd)
        object = mc.ls(hl=1)
        cmd = 'manipMoveAlignHandleToComponent("' + facesSelected[0] + '", {"' + object[0] + '"}, {""}, "none", 0);'
        mel.eval(cmd)
        mc.BakeCustomPivot()
        rotStore = mc.xform(q=True,rotation=True)
        mc.MoveTool()
        mc.manipMoveContext('Move',edit=True, mode=10)
        posStore = mc.manipMoveContext("Move",q=True, position = True )
        #mc.undoInfo(closeChunk=True)
        #mc.undo()
        return posStore[0], posStore[1], posStore[2], rotStore[0], rotStore[1], rotStore[2]


def setFaceBoth():
    facesSelected = mc.filterExpand(expand=True ,sm=34)
    if len(facesSelected) == 1:
        setFacePivotRot()
        mc.select(facesSelected)
        setFacePivotPos()


def setFacePivotRot():
    facesSelected = mc.filterExpand(expand=True ,sm=34)
    if len(facesSelected) == 1:
        #make sure select face mode
        cmd = 'doMenuComponentSelection("' + facesSelected[0].split('.')[0] +'", "facet");'
        mel.eval(cmd)
        object = mc.ls(hl=1)
        cmd = 'manipMoveAlignHandleToComponent("' + facesSelected[0] + '", {"' + object[0] + '"}, {""}, "none", 0);'
        mel.eval(cmd)
        mc.BakeCustomPivot()
        beforeRot =mc.getAttr(object[0]+".rotate")
        mc.rotate(0, 0, 90, object[0] )
        mc.makeIdentity(apply=True, t= 0, r= 1, s= 0,n= 0)
        mc.rotate(0, 0, -90, object[0],r=1,os=1)
        mc.rotate(beforeRot[0][0], beforeRot[0][1], beforeRot[0][2], object[0],r=1,ws=1)


def setFacePivotPos():
    facesSelected = mc.filterExpand(expand=True ,sm=34)
    if len(facesSelected) == 1:
        cmd = 'doMenuComponentSelection("' + facesSelected[0].split('.')[0] +'", "facet");'
        mel.eval(cmd)
        object = mc.ls(hl=1)
        mc.manipMoveContext('Move',edit=True, mode=10)
        posStore = mc.manipMoveContext("Move",q=True, position = True )
        mc.select(object)
        mc.xform(worldSpace=True, pivots = (posStore[0],posStore[1],posStore[2]))




def restoreWorldPos():
    meshsel = mc.filterExpand(expand=True ,sm=12)
    if meshsel:
        valueBefore  = mc.getAttr(meshsel[0] + ".center")
        mc.setAttr((meshsel[0] + ".translateX"),(valueBefore[0][0]*-1))
        mc.setAttr((meshsel[0] + ".translateY"),(valueBefore[0][1]*-1))
        mc.setAttr((meshsel[0] + ".translateZ"),(valueBefore[0][2]*-1))
        mc.makeIdentity(apply=True, t= 1, r= 0, s= 0,n= 0,pn =1)
        mc.xform(ws=1, piv=(0, 0, 0))
        mc.setAttr((meshsel[0] + ".translateX"),valueBefore[0][0])
        mc.setAttr((meshsel[0] + ".translateY"),valueBefore[0][1])
        mc.setAttr((meshsel[0] + ".translateZ"),valueBefore[0][2])
        mc.DeleteHistory()



def edgeLoopSum(EdgeList):
    EdgeSizeSum = 0
    for e in EdgeList:
        vertices = mc.filterExpand((mc.polyListComponentConversion(e, tv=True)),sm = 31)
        verA = mc.xform(vertices[0], q=True, t=True, ws=True)
        verB = mc.xform(vertices[1], q=True, t=True, ws=True)
        verDistance = math.sqrt( ((verA[0]-verB[0])**2) +  ((verA[1]-verB[1])**2) + ((verA[2]-verB[2])**2))
        EdgeSizeSum = EdgeSizeSum + verDistance
    return EdgeSizeSum


def cleanMeshInsertNodes():
    mc.delete(all=1, e=1, ch=1)
    junkList = ["meshInsertGr*", "blendLo*", "sampleFace", "sampleBoarde*", "cutBoarde*", "sampleLo*"]
    for j in junkList:
        if mc.objExists(j):
            mc.delete(j)

def getSharpCorner(edgeLoop,returnType):
    shapeNode = mc.listRelatives(edgeLoop[0], fullPath=True , parent=True )
    transformNode = mc.listRelatives(shapeNode[0], fullPath=True , parent=True )
    sharpCorner = []
    sharpCornerVtx = []
    for i in range(len(edgeLoop)):

        evlistA = mc.polyInfo(edgeLoop[i],ev=True)
        cvGrpA = []
        checkNumber = ((evlistA[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                cvGrpA.append(findNumber)

        j = i+1
        if j == len(edgeLoop):
            j = 0

        evlistB = mc.polyInfo(edgeLoop[j],ev=True)
        cvGrpB = []
        checkNumber = ((evlistB[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                cvGrpB.append(findNumber)

        findCV = list(set(cvGrpA) & set(cvGrpB))
        cvGrpA.remove(findCV[0])
        cvGrpB.remove(findCV[0])
        cvList = []
        cvList.append(transformNode[0] +'.vtx[' + cvGrpA[0] +']')
        cvList.append(transformNode[0] +'.vtx[' + findCV[0] +']')
        cvList.append(transformNode[0] +'.vtx[' + cvGrpB[0] +']')
        points = []
        for cv in cvList:
            x,y,z = mc.pointPosition(cv,w=1)
            #this_point = pm.dt.Point(x, y, z)
            this_point = om.MPoint(x,y,z)
            points.append(this_point)

        vectors = [points[x+1]-points[x] for x in range(len(points)-1)]
        rad_angle = vectors[0].angle(vectors[1])
        deg_angle = math.degrees(rad_angle)
        checkangle =  '%.0f' % deg_angle

        if int(checkangle) > 80:
            sharpCorner.append(edgeLoop[i])
            sharpCorner.append(edgeLoop[j])
            sharpCornerVtx.append(cvList[1])

    if returnType == "edge":
        return sharpCorner
    elif returnType == "vtx":
        return sharpCornerVtx

def edgeLoopOrder():
    selEdges = mc.ls(sl=1,fl=1)
    edgeNoList = []
    for s in selEdges:
        no = (s.split('[')[-1]).split(']')[0]
        edgeNoList.append(no)
    shapeNode = mc.listRelatives(selEdges[0], fullPath=True , parent=True )
    transformNode = mc.listRelatives(shapeNode[0], fullPath=True , parent=True )
    loopOrder = []
    #first Edge
    edge = transformNode[0]+'.e['+ edgeNoList[0] + ']'
    loopOrder.append(edge)
    edgeNoList.remove(edgeNoList[0])
    evlist = mc.polyInfo(loopOrder[-1],ev=True)
    cvA = transformNode[0]+'.vtx['+ evlist[0].split(' ')[7] + ']'

    getNumber = []
    checkNumber = ((evlist[0].split(':')[1]).split('\n')[0]).split(' ')
    for c in checkNumber:
        findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
        if findNumber:
            getNumber.append(findNumber)

    useCV = []
    useCV.append(getNumber[0])
    count = 0
    while len(edgeNoList)> 0 and count < 500:
        evlist = mc.polyInfo(loopOrder[-1],ev=True)

        checkCV = []
        checkNumber = ((evlist[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                checkCV.append(findNumber)

        diff = []
        for u in useCV:
            for d in checkCV:
                if u == d:
                    pass
                else:
                    diff = d

        useCV.append(diff)
        newEdges = mc.polyInfo((transformNode[0]+'.vtx['+ diff + ']'), ve=True)

        check = []
        checkNumber = ((newEdges[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                check.append(findNumber)

        findEdge = list(set(edgeNoList) & set(check))
        if findEdge:
            loopOrder.append((transformNode[0] + '.e[' + str(findEdge[0]) + ']'))
            mc.select(transformNode[0] + '.e[' + str(findEdge[0]) + ']')
            edgeNoList.remove(findEdge[0])
        count +=  1
    return loopOrder

def vtxLoopOrder():
    selEdges = mc.ls(sl=1,fl=1)
    shapeNode = mc.listRelatives(selEdges[0], fullPath=True , parent=True )
    transformNode = mc.listRelatives(shapeNode[0], fullPath=True , parent=True )
    edgeNumberList = []
    for a in selEdges:
        checkNumber = ((a.split('.')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                edgeNumberList.append(findNumber)
    getNumber = []
    for s in selEdges:
        evlist = mc.polyInfo(s,ev=True)
        checkNumber = ((evlist[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                getNumber.append(findNumber)
    dup = set([x for x in getNumber if getNumber.count(x) > 1])
    getHeadTail = list(set(getNumber) - dup)
    vftOrder = []
    #find Head and Tail
    vftOrder.append(getHeadTail[0])
    count = 0
    while len(dup)> 0 and count < 100:
        checkVtx = transformNode[0]+'.vtx['+ vftOrder[-1] + ']'
        velist = mc.polyInfo(checkVtx,ve=True)
        getNumber = []
        checkNumber = ((velist[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                getNumber.append(findNumber)
        findNextEdge = []
        for g in getNumber:
            if g in edgeNumberList:
                findNextEdge = g
        edgeNumberList.remove(findNextEdge)
        checkVtx = transformNode[0]+'.e['+ findNextEdge + ']'
        findVtx = mc.polyInfo(checkVtx,ev=True)
        getNumber = []
        checkNumber = ((findVtx[0].split(':')[1]).split('\n')[0]).split(' ')
        for c in checkNumber:
            findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
            if findNumber:
                getNumber.append(findNumber)
        gotNextVtx = []
        for g in getNumber:
            if g in dup:
                gotNextVtx = g
        dup.remove(gotNextVtx)
        vftOrder.append(gotNextVtx)
        count +=  1
    vftOrder.append(getHeadTail[1])
    finalList = []
    for v in vftOrder:
        finalList.append(transformNode[0]+'.vtx['+ v + ']' )
    return finalList


def blendStamp(sampleMesh):
    global sampleFileChoice
    rotState = mc.checkBox('lockRot', q=1,v=1)
    scaleState = mc.checkBox('lockScale', q=1,v=1)
    offsetState = mc.checkBox('lockOffset', q=1,v=1)
    curvatureState = mc.checkBox('lockCurvature', q=1,v=1)
    currentSel = mc.ls(sl=1,fl=1)
    faceSel = mc.filterExpand(ex=True, sm=34)
    shape = mc.listRelatives(faceSel[0],p=True)
    transform = mc.listRelatives(shape[0],p=True)
    mc.ConvertSelectionToEdgePerimeter()
    borderEdge = mc.ls(sl=1,fl=1)
    #clean up
    cleanMeshInsertNodes()
    #import abc sample
    if not mc.objExists('ctachingImport'):
        mc.CreateEmptyGroup()
        mc.rename("ctachingImport")

    command = 'AbcImport -mode import -reparent "ctachingImport"'  ' ' + '"' + sampleMesh + '"'
    newNode = mel.eval(command)
    mc.xform(ws=1, a=1 ,piv =[0, 0, 0])
    mc.pickWalk(d="down")
    mc.parent(w=True)
    sample = mc.ls(sl=True,fl=True)
    mc.delete( "ctachingImport")
    mc.setAttr((sample[0]+'.visibility'),0)
    mc.ConvertSelectionToEdgePerimeter()
    sampleEdge = mc.ls(sl=1,fl=1)
    autoBridge = 0
    goNext = 1
    if not len(borderEdge) == len(sampleEdge):
        checkMethod = mc.confirmDialog(title='Confirm', message='edge number mismatch, continue with autoBridge?', button=['Yes','Abort'], defaultButton='Yes', cancelButton='Abort', dismissString='Abort' )

        if checkMethod == 'Abort':
            mc.delete(sample[0])
            mc.select(currentSel)
            cmd = 'doMenuComponentSelection("' + transform[0] +'", "facet");'
            mel.eval(cmd)
            goNext = 0

        elif checkMethod == 'Yes':
            autoBridge = 1

    if goNext == 1:
        mc.undoInfo( openChunk= True, cn = 'blendUndo' )
        # duplicate select face
        mc.setAttr((sample[0]+'.visibility'),1)
        mc.select(currentSel)
        dupe = mc.duplicate(transform)

        mc.ConvertSelectionToEdgePerimeter()
        mc.sets(name = 'cutBoarder', text='cutBoarder')

        newFace = []
        for f in faceSel:
            newFace.append(f.replace(transform[0],dupe[0]))
        mc.select(newFace)
        mc.InvertSelection()
        mc.delete()
        mc.select(dupe)
        mc.duplicate(smartTransform=True)
        mc.rename('undoBackup')
        mc.select(dupe)
        cmd = 'doMenuComponentSelection("' + dupe[0] +'", "edge");'
        mel.eval(cmd)
        mc.polySelectConstraint(mode=3 ,type = 0x8000, where=1)
        mc.polySelectConstraint(disable=True)
        #remove inner edges
        mc.InvertSelection()
        edgeInv = mc.ls(sl=1,fl=1)
        if edgeInv:
            mc.polyDelEdge(cv=1)
        mc.select(dupe)
        #restore world pos
        restoreWorldPos()
        #set pivot to face
        mc.ConvertSelectionToFaces()
        setFaceBoth()
        # match guide
        guideRot =mc.getAttr(dupe[0]+".rotate")
        guidePos =mc.getAttr(dupe[0]+".translate")
        mc.rotate(guideRot[0][0], guideRot[0][1], guideRot[0][2], sample[0])
        mc.move(guidePos[0][0], guidePos[0][1], guidePos[0][2], sample[0])
        # better match scale
        dupEdgeList = mc.ls(dupe[0]+'.e[*]',fl=1)
        lengthDup = edgeLoopSum(dupEdgeList)
        mc.select(sample)
        mc.ConvertSelectionToFaces()
        mc.polySelectConstraint(mode=3 ,type = 0x8000, where=1)
        borderList = mc.ls(sl=1,fl=1)
        mc.polySelectConstraint(disable=True)
        lengthSample = edgeLoopSum(borderList)
        scaleVec = lengthDup / lengthSample * 0.9
        mc.setAttr((sample[0]+'.scaleX'), scaleVec)
        mc.setAttr((sample[0]+'.scaleY'), scaleVec)
        mc.setAttr((sample[0]+'.scaleZ'), scaleVec)

        mc.sets(name = 'sampleBoarder', text='sampleBoarder')
        mc.select(sample[0]+'.f[*]')
        mc.sets(name = 'sampleFace', text='sampleFace')
        #clean and create hierarchy
        mc.group(empty=1,n='sampleLoc')
        mc.rotate(guideRot[0][0], guideRot[0][1], guideRot[0][2],'sampleLoc')
        mc.move(guidePos[0][0], guidePos[0][1], guidePos[0][2], 'sampleLoc')

        mc.delete(dupe)

        mc.group(empty=1,n='meshInsertGrp')
        mc.parent('sampleLoc','undoBackup','meshInsertGrp')
        checkDeform = mc.checkBox('deformState', q=True, v=True)
        if checkDeform == 1:
            mc.duplicate('undoBackup',smartTransform = True,n='blendMesh')
            mc.duplicate('sampleLoc',smartTransform = True,n='blendLoc')
            mc.parent('blendMesh','blendLoc')
            mc.makeIdentity('blendMesh',apply=True, t= 1, r= 1, s= 1,n= 0,pn =1)
            mc.xform('blendMesh',ws=1, piv=(guidePos[0][0], guidePos[0][1], guidePos[0][2]))
            mc.duplicate('blendMesh',smartTransform = True,n='blendMeshFlat')
            #flatten plane
            mc.select('blendMeshFlat')
            mc.ConvertSelectionToEdgePerimeter()
            mc.InvertSelection()
            edgeGridList=mc.ls(sl=1,fl=1)
            mc.select(edgeGridList[0])
            mc.SelectEdgeLoopSp()
            mc.SelectEdgeRingSp()
            gridU = mc.ls(sl=1,fl=1)
            sortGrp = getEdgeRingGroup()
            for e in sortGrp:
                mc.select(e)
                listVtx = vtxLoopOrder()
                xA, yA, zA = mc.pointPosition(listVtx[0], w=1)
                xB, yB, zB = mc.pointPosition(listVtx[-1], w=1)
                mc.curve(d=1, p=[(xA, yA, zA),(xB, yB, zB)])
                mc.rename('newguidecurve')
                mc.rebuildCurve('newguidecurve', ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=100, d=3, tol=0)
                currentU = 0
                prV = 0
                gapDist = 1.0/(len(listVtx)-1)
                for j in range(len(listVtx)-2):
                    prV = currentU + gapDist
                    currentU = prV
                    xj, yj, zj = mc.pointOnCurve('newguidecurve', pr= currentU, p=1)
                    mc.move(xj, yj, zj,listVtx[j+1] , a =True, ws=True)
                mc.delete('newguidecurve')
            mc.select(edgeGridList)
            mc.select(gridU,d=1)
            mc.SelectEdgeRingSp()
            sortGrp = getEdgeRingGroup()
            for e in sortGrp:
                mc.select(e)
                listVtx = vtxLoopOrder()
                xA, yA, zA = mc.pointPosition(listVtx[0], w=1)
                xB, yB, zB = mc.pointPosition(listVtx[-1], w=1)
                mc.curve(d=1, p=[(xA, yA, zA),(xB, yB, zB)])
                mc.rename('newguidecurve')
                mc.rebuildCurve('newguidecurve', ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=100, d=3, tol=0)
                currentU = 0
                prV = 0
                gapDist = 1.0/(len(listVtx)-1)
                for j in range(len(listVtx)-2):
                    prV = currentU + gapDist
                    currentU = prV
                    xj, yj, zj = mc.pointOnCurve('newguidecurve', pr= currentU, p=1)
                    mc.move(xj, yj, zj,listVtx[j+1] , a =True, ws=True)
                mc.delete('newguidecurve')
            rx, ry, rz = checkFaceAngle('blendMeshFlat.f[0]')
            mc.setAttr(('meshSample.rotateX'),rx)
            mc.setAttr(('meshSample.rotateY'),ry)
            mc.setAttr(('meshSample.rotateZ'),rz)
            mc.makeIdentity('blendMeshFlat',apply=True, t= 1, r= 1, s= 1,n= 0,pn =1)
            #smooth
            mc.polySmooth('blendMesh', mth=0, dv=1, c=1, kb=0, ksb=0, khe=0, kt=1, kmb=1, suv=1, sl=1, dpe=1, ps=0.1, ro=1)
            mc.polySmooth('blendMeshFlat', mth=0, dv=1, c=1, kb=0, ksb=0, khe=0, kt=1, kmb=1, suv=1, sl=1, dpe=1, ps=0.1, ro=1)
            blendName = mc.blendShape('blendMesh','blendMeshFlat' )
            mc.parent('blendMeshFlat','meshInsertGrp')
            mc.delete('blendLoc')

        #crate offsetGroup
        mc.duplicate('sampleLoc',smartTransform = True,n='sampleLoc_offset')
        mc.parent('sampleLoc','sampleLoc_offset')

        #combine mesh
        mc.delete(currentSel)
        mc.polyUnite(sample[0], transform[0], ch=0, mergeUVSets=1, centerPivot=1, name= transform[0])

        #cluster sample
        mc.cluster('sampleFace')
        getSel=mc.ls(sl=1,fl=1)
        mc.rename(getSel[0],'meshScale')
        mc.move(guidePos[0][0], guidePos[0][1], guidePos[0][2], 'meshScale.scalePivot')
        mc.move(guidePos[0][0], guidePos[0][1], guidePos[0][2], 'meshScale.rotatePivot')
        mc.parent('meshScale','sampleLoc')

        #bridge
        if autoBridge == 1:
            mc.select('sampleBoarder')
            reduceTarget = len(mc.ls(sl=1, fl=1))
            #very tricky area, if selection is square-ish, let's try protect four corner
            #other shape became too unpredictable so gave up using old method
            if reduceTarget >= 8:
                mc.select('cutBoarder')
                selEdge = edgeLoopOrder()
                removeCorner = getSharpCorner(selEdge,'edge')
                if len(removeCorner) == 8:
                    #need to remove
                    needRemove = len(selEdge) - reduceTarget
                    pickList = list(set(selEdge)-set(removeCorner))
                    #mc.select(pickList)
                    if len(pickList) > needRemove:
                        checkEdge = pickList
                    else:
                        checkEdge = selEdge

                targerGaps = len(checkEdge) - reduceTarget + 8
                gaps = len(checkEdge)* 1.0 / targerGaps
                if gaps >= 1:
                    reduceList = []
                    for i in range(targerGaps):
                        ctrlSpace = round( i * gaps)
                        reduceList.append(checkEdge[int(ctrlSpace)])

                    mc.select(reduceList)
                    #bug if not edge mode collapes fail.
                    checkList = mc.ls(sl=1,fl=1)
                    shapeNode = mc.listRelatives(checkList[0], fullPath=True , parent=True )
                    transformNode = mc.listRelatives(shapeNode[0], fullPath=True , parent=True )
                    #force edge mode
                    cmd = 'doMenuComponentSelection("' + transformNode[0] +'", "edge");'
                    mel.eval(cmd)
                    mc.select(checkList)
                    mc.PolygonCollapse()


        mc.select('cutBoarder', 'sampleBoarder')
        mc.polyBridgeEdge(ch=1, divisions=0, twist=0, taper=1, curveType=0, smoothingAngle=30, direction=0, sourceDirection=0, targetDirection=0)


        if checkDeform == 1:
            mc.select('sampleFace')
            mc.ShrinkPolygonSelectionRegion()
            mc.select('blendMeshFlat',add=True)
            mc.CreateWrap()
            mc.setAttr('wrap1.autoWeightThreshold',1)
            mc.setAttr('wrap1.maxDistance', 5)
            mc.setAttr((blendName[0]+'.blendMesh'), 1)


        #remove border Edge Loop
        borderIt = mc.checkBox('borderState', q=True,v=True )
        if borderIt == False:
            mc.select('sampleFace')
            mc.ShrinkPolygonSelectionRegion()
            mc.ConvertSelectionToEdgePerimeter()
            newloop = mc.ls(sl=1, fl=1)
            mc.GrowPolygonSelectionRegion()
            mc.select(newloop, d=True)
            mc.PolygonCollapse()


        mc.setAttr('meshInsertGrp.visibility', 0)
        mc.select('sampleFace')
        checkMeshName = mc.ls(sl=1)
        mc.rename(checkMeshName[0].split('.')[0],transform[0])
        cmd = 'doMenuComponentSelection("' + transform[0] +'", "facet");'
        mel.eval(cmd)
        mc.delete('cutBoarder', 'sampleBoarder')
        #store slider Value
        checkOffsetV = mc.intSliderGrp( 'bridfeOffsetSlide',q=1,v=1)
        checkcurvatureV = mc.floatSliderGrp( 'curvatureSlide',q=1,v=1)

        #connect to UI
        sampleFileChoice = ['sampleLoc']
        mc.connectControl('bridfeOffsetSlide', 'polyBridgeEdge1.bridgeOffset')
        mc.connectControl('curvatureSlide', 'wrap1.envelope')
        #apply lock
        if rotState == 1:
            jwStampUpdateRot()
        if scaleState == 1:
            jwStampUpdateScale()
            checkScaleH = mc.floatSliderGrp( 'stampScaleHSlide' ,q=1,en=1)
            if checkScaleH == 1:
                jwStampUpdateHScale()
        if offsetState == 1:
            mc.setAttr('polyBridgeEdge1.bridgeOffset',checkOffsetV)
        if curvatureState == 1:
            mc.setAttr('wrap1.envelope',checkcurvatureV)
        mc.undoInfo( closeChunk = True )


def jwMeshQsel(number):
    currentSel= mc.filterExpand(sm=34)
    if currentSel:
        mc.select(currentSel[0])
        if  (number == "S2"):
            mc.ConvertSelectionToVertices()
            f2v =mc.ls(sl=1,fl=1)
            mc.select(f2v[0])
            mc.ConvertSelectionToFaces()

        elif (number == "S3"):
            mc.GrowPolygonSelectionRegion()

        elif (number == "S4"):
            mc.ConvertSelectionToVertices()
            f2v =mc.ls(sl=1,fl=1)
            mc.select(f2v[0])
            mc.ConvertSelectionToFaces()
            mc.GrowPolygonSelectionRegion()
        elif (number == "S6"):
            mc.ConvertSelectionToVertices()
            f2v =mc.ls(sl=1,fl=1)
            mc.select(f2v[0])
            mc.ConvertSelectionToFaces()
            mc.GrowPolygonSelectionRegion()
            mc.GrowPolygonSelectionRegion()

def cageWireFrameToggle():
    selSampleLong = mc.ls(sl=1,fl=1,l=1)
    if selSampleLong:
        selSample = selSampleLong[0].split('|')[1]
        get = mel.eval('rootOf '+selSample)
        cageChild =  mc.listRelatives(get,typ='transform',c=True)
        if cageChild:
            getShape =  mc.listRelatives(get,s=True)

            checkState = mc.getAttr(getShape[0]+'.overrideShading')
            if checkState == 1:
                mc.setAttr((getShape[0]+'.overrideEnabled'),1)
                mc.setAttr((getShape[0]+'.overrideShading'),0)
                mc.setAttr((getShape[0]+'.overrideColor'),9)
            else:
                mc.setAttr((getShape[0]+'.overrideShading'),1)
                mc.setAttr((getShape[0]+'.overrideEnabled'),0)


def snapShotLight():
    cleanList = ('snapLight','keyA','topAmb','generalAmb')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)

    cmd = 'defaultDirectionalLight(1, 1,1,1, "0", 0,0,0, 0);'
    mel.eval(cmd)
    mc.rename('keyA')
    mc.setAttr("keyA.r", 50, 0, 180)
    mc.setAttr("keyAShape.intensity", 0.94)
    cmd = 'defaultDirectionalLight(1, 1,1,1, "0", 0,0,0, 0);'
    mel.eval(cmd)
    mc.rename('topAmb')
    mc.setAttr("topAmb.r", -100 ,-25, 0)
    mc.setAttr("topAmbShape.intensity", 0.35)
    cmd = 'defaultAmbientLight(1, 0.45, 1,1,1, "0", 0,0,0, "1");'
    mel.eval(cmd)
    mc.rename('generalAmb')
    mc.setAttr("generalAmbShape.intensity", 0.75)
    mc.group('keyA' ,'topAmb' ,'generalAmb')
    mc.rename('snapLight')


def snapCamSetup():
    view = omui.M3dView.active3dView()
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()
    cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
    mc.camera(cameraTrans ,e=True, displayFilmGate = False, displayResolution = False, overscan =1.3)
    mc.camera(cameraTrans, e=True, filmFit = 'overscan')
    mc.setAttr((camPath+'.overscan'), 1.05)
    mc.setAttr((camPath+'.preScale'), 1)
    mc.setAttr((camPath+'.focalLength'),50)
    mc.setAttr((cameraTrans[0]+'.t'),0,15,0)
    mc.setAttr((cameraTrans[0]+'.r'),-90,0,0)
    mc.modelEditor('modelPanel4',e = True, grid = True, manipulators =True, sel =True, udm= True, shadows=True, dl= 'all', displayAppearance='smoothShaded',lights = False)
    mc.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
    mc.setToolTo('selectSuperContext')


def setGframe():
    if mc.objExists('gFrame'):
        mc.delete('gFrame')
    mc.polyPlane(w=5, h=5, sx=1, sy=1, ax=(0,1,0), cuv=2, ch=0,n='gFrame')
    mc.polyExtrudeEdge('gFrame.e[*]',constructionHistory=0, keepFacesTogether=1, offset=0.3)
    mc.delete('gFrame.f[0]')
    mc.select('gFrame')

def setStage():
    selGeo = mc.filterExpand(sm = 12)
    snapCamSetup()
    setGframe()
    snapShotLight()
    if selGeo:
        mc.select(selGeo)
    snapShotUpdate()

def snapCamPerspSetup():
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()
    cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
    mc.camera(cameraTrans ,e=True, displayFilmGate = False, displayResolution = False, overscan =1.3)
    mc.camera(cameraTrans, e=True, filmFit = 'overscan')
    mc.setAttr((camPath+'.overscan'), 1.05)
    mc.setAttr((camPath+'.preScale'), 1)
    mc.setAttr((camPath+'.focalLength'),50)
    mc.setAttr((cameraTrans[0]+'.t'),2,14,8)
    mc.setAttr((cameraTrans[0]+'.r'),-60,15,0)
    mc.modelEditor('modelPanel4',e = True, grid = True, manipulators =True, sel =True, udm= True, shadows=True, dl= 'all', displayAppearance='smoothShaded',lights = False)
    mc.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
    mc.setToolTo('selectSuperContext')

def setEdgeStage():
    selGeo = mc.filterExpand(sm = 12)
    if len(selGeo)>0:
        for s in selGeo:
            get = mel.eval('rootOf '+s)
            if not mc.attributeQuery('edgeMode', node = get, ex=True ):
                mc.addAttr(get, ln='edgeMode', at = "long" )
            mc.setAttr((get+'.edgeMode'),1)
    snapCamPerspSetup()
    setGframe()
    snapShotLight()
    if selGeo:
        mc.select(selGeo)
    snapShotUpdate()

def setPerspStage():
    selGeo = mc.filterExpand(sm = 12)
    if len(selGeo)>0:
        for s in selGeo:
            get = mel.eval('rootOf '+s)
            if not mc.attributeQuery('edgeMode', node = get, ex=True ):
                mc.addAttr(get, ln='edgeMode', at = "long" )
            mc.setAttr((get+'.edgeMode'),0)
    snapCamPerspSetup()
    setGframe()
    snapShotLight()
    if selGeo:
        mc.select(selGeo)
    snapShotUpdate()

def makeBorder():
    selGeo = mc.filterExpand(sm = 12)
    if selGeo:
        mc.polySelectConstraint(mode =3, type = 0x8000 ,where =1)
        mc.polySelectConstraint(m =0)
        selEdge = mc.ls(sl=1,fl=1)
        mc.polyExtrudeEdge(kft=True,offset=0.3)
        mc.delete(all=True, e=True, ch=True)
        mc.select(selGeo)

def autoScaleFit():
    selGeo = mc.filterExpand(sm = 12)
    if selGeo:
        for s in selGeo:
            mc.makeIdentity(apply=True, t=1, r= 1, s= 1, n= 0, pn= 1)
            bbox = mc.exactWorldBoundingBox(s)
            disX = pow(((bbox[3]-bbox[0])**2),0.5)
            disZ = pow(((bbox[5]-bbox[2])**2),0.5)
            matchD = 0
            if disX > disZ:
                matchD = disX
            else:
                matchD = disZ
            targetD = 5.0
            scaleV = targetD / matchD
            mc.setAttr((s+'.s'),scaleV,scaleV,scaleV)
            mc.makeIdentity(apply=True, t=1, r= 1, s= 1, n= 0, pn= 1)

def lockConrnerVtx():
    selGeo = mc.filterExpand(sm = 12)
    if selGeo:
        mc.polySelectConstraint(mode =3, type = 0x8000 ,where =1)
        mc.polySelectConstraint(m =0)
        selEdge = mc.ls(sl=1,fl=1)
        selEdge = edgeLoopOrder()
        cornerVtx = getSharpCorner(selEdge,'vtx')
        for c in cornerVtx:
            x,y,z = mc.pointPosition(c,w=1)
            if x > 0 and z > 0:
                mc.move(2.5, 0 , 2.5 ,c, a =True, ws=True)
            elif x > 0 and z < 0:
                mc.move(2.5, 0 , -2.5 ,c, a =True, ws=True)
            elif x < 0 and z > 0:
                mc.move(-2.5, 0 , 2.5 ,c, a =True, ws=True)
            elif x < 0 and z < 0:
                mc.move(-2.5, 0 , -2.5 ,c, a =True, ws=True)
    mc.select(selGeo)

def evenBoarder():
    selGeo = mc.filterExpand(sm = 12)
    if selGeo:
        lockConrnerVtx()
        mc.polySelectConstraint(mode =3, type = 0x8000 ,where =1)
        mc.polySelectConstraint(m =0)
        selEdge = mc.ls(sl=1,fl=1)
        count = 0
        while len(selEdge)> 0 and count < 500:
            mc.select(selEdge[0])
            mc.polySelectConstraint(mode =2, type = 0x8000 ,where =1,pp=4,m3a=30)
            fixList = mc.ls(sl=1,fl=1)
            selEdge = list(set(selEdge)-set(fixList))
            getList = vtxLoopOrder()
            aX,aY,aZ = mc.pointPosition(getList[0],w=1)
            bX,bY,bZ = mc.pointPosition(getList[-1],w=1)
            getList.remove(getList[0])
            getList.remove(getList[-1])
            dX = (bX - aX) / (len(getList)+1)
            dY = (bY - aY) / (len(getList)+1)
            dZ = (bZ - aZ) / (len(getList)+1)
            for i in range(len(getList)):
                mc.move( ((i+1)*dX+aX), ((i+1)*dY+aY) , ((i+1)*dZ+aZ) ,getList[i], a =True, ws=True)
            count +=  1
        mc.select(selGeo[0])

def sliceStamp():
    sel = mc.ls(sl=1,fl=1)
    if sel:
        transNode = mc.listRelatives(sel,type='transform',p=True,f=True)
        if transNode:
            if '_offset' in transNode[0]:
                numbers = mc.intSliderGrp( 'stampSliceSlide' ,v = True,q=True)
                storeRotLocal = mc.getAttr(sel[0] + '.r')
                storeTrans = mc.getAttr(transNode[0] + '.t')
                storeRot = mc.getAttr(transNode[0] + '.r')
                mc.setAttr((transNode[0]+'.t'),0,0,0)
                mc.setAttr((transNode[0]+'.r'),0,0,0)
                mc.setAttr((sel[0]+'.r'),0,0,0)
                bbox = mc.xform(sel[0],q=True,bb=True)
                bw = pow(((bbox[3]-bbox[0])**2),0.5)/2
                bh = pow(((bbox[5]-bbox[2])**2),0.5)/2
                cuts = numbers
                gapi = bw / cuts * 2
                gapj = bh / cuts * 2
                starti = -1*bw
                startj = -1*bh
                for i in range(1,cuts,1):
                    cutPoint = (starti + (i* gapi))
                    mc.polyCut((sel[0]+'.f[*]'), ch=0, pc = (0,0,cutPoint), ro=(0,0,180), ps =(5,1))
    
                for j in range(1,cuts,1):
                    cutPoint = (startj + (j* gapj))
                    mc.polyCut((sel[0]+'.f[*]'), ch=0, pc = (cutPoint,0,0), ro=(180,90,0), ps =(5,1))
    
                mc.setAttr((transNode[0]+'.t'),storeTrans[0][0],storeTrans[0][1],storeTrans[0][2])
                mc.setAttr((transNode[0]+'.r'),storeRot[0][0],storeRot[0][1],storeRot[0][2])
                mc.setAttr((sel[0]+'.r'),storeRotLocal[0][0],storeRotLocal[0][1],storeRotLocal[0][2])
            else:
                print( 'select mesh is not a stamp')
        else:
            print( 'select mesh is not a stamp')

def frameCollap(show):
    global frameCollection
    for f in frameCollection:
        mc.frameLayout((f+'FL'), e = True , cl =show)

def rapidPlace():
    global folderCheck
    folderCheck = 0
    global UIfirstRun
    UIfirstRun = 0
    jwMeshPlaceUI()
    jwRefreshIcon(0)
    frameAllOn()
    snapModeToggle()

rapidPlace()
