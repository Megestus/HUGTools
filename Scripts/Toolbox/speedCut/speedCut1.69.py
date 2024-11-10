##--------------------------------------------------------------------------
##
## ScriptName : SpeedCut
## Contents   : tool set for speed up maya boolean opeeration
## Author     : Joe Wu
## URL        : http://im3djoe.com
## Since      : 2019/08
## LastUpdate : 2021/09/23
## Version    : 1.0  First version for public test
##            : 1.1  developing union function, bevel manager
##            : 1.2  for multi mesh use
##            : 1.21 imporve Bevel Manger
##            : 1.22 add live Drag Position and shift/ctrl change rotation
##            : 1.23 bug fix and improve NonBevel function in bevel Manger
##            : 1.24 check liveSnap object and smapleLocator is not exist when create cutter,small viusal imporvement.
##            : 1.25 added few quick tool for edge control.
##            : 1.26 added reTarget, to swtich different base mesh
##            : 1.27 testing scrapeCutter
##            : 1.28 adding optionMenu for switch between different baseMesh
##            : 1.29 shelt + for scale, ctrl + for rotation , UI, pre - Scale Slider
##            : 1.30 rework Control section
##            : 1.31 rework symmetry section
##            : 1.32 symmetry debug
##            : 1.36 symmetry color cage
##            : 1.36 rework Live Draw
##            : 1.36 rework Cutter Aligment
##            : 1.36 rework Pattern
##            : 1.37 fixing bug with freeze obj space symmtery, cutter does not mirror
##            : 1.38 fixing bug cage color, baseMesh menu
##            : 1.40 fixing bug baseMesh menu,finalize button
##            : 1.40 fixing bug symmtery and bake cutter bug
##            : 1.41 improve undo and repeat
##            : 1.42 bug fix reconnect shape where cutter's World Matrix was not fully disconnect to inputMat
##            : 1.43 imporve control slider , but undo still not work well
##            : 1.44 improve rotate toggle, now became three button with direction
##            : 1.45 improve symmtry button, toggle axis on/off
##            : 1.46 hotkey to snap face center
##            : 1.47 fixed bug symmetry doesn't restore after Bake/Restore
##            : 1.48 improve snap boarder
##            : 1.49 test in python 3
##            : 1.50 bug fix where 3,5,6 sides cutter not load
##            : 1.51 remove pymel
##            : 1.52 adding after cut and change union opertation order
##            : 1.53 imporved UI, better show between operation types, vis between different base mesh grp, assign color for different mesh grp
##            : 1.54 fix bugs, show loop cutters error when non cutter item selected, Freeze Pattern do not apply to correct operation, when toggle Pattern type, cutter gap disappear
##            : 1.55 fix more bugs in bevel manager, bug at Finalize base mesh and Resotre cutter
##            : 1.56 fix bug when change cutter Type, also work for multi selection
##            : 1.57 added cutter to new mesh grp, bug fix with fixBoolNodeConnection
##            : 1.58 fix how detect boolean node exist avoid fail while cutter create, fix bug create New Grp with Pattern
##            : 1.59 resizeable UI
##            : 1.60 group color match layer color
##            : 1.61 fix bug when create New Grp
##            : 1.62 more bug fix with create New Grp and assign color
##            : 1.63 fixing bug for prebox not created in baseMesh center
##            : 1.64 adding rdMirror
##            : 1.65 improve rdMirror UI
##            : 1.66 improve dock UI
##            : 1.67 fix bug dock UI bug in mata 2022+
##            : 1.68 support add multi meshes to cutter
##            : 1.69 small bug in python 3
## Other Note : test in maya 2020.2 windows enviroment
##
##
## Install    : copy and paste script into a python tab in maya script editor
##--------------------------------------------------------------------------


import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as mc
import math
import maya.api.OpenMaya as OpenMaya
import maya.mel as mel
import re
from collections import OrderedDict
import random

def jwSpeedCutUI():
    if mc.window("jwSpeedCutWin", exists = True):
        mc.deleteUI("jwSpeedCutWin")
    if mc.dockControl('speedCutDock',q=1,ex=1):
        mc.deleteUI('speedCutDock',control=1)

    mayaHSize = mc.window('MayaWindow', q=1, h=1)
    jwSpeedCutWin = mc.window("jwSpeedCutWin",title = "speedCut 1.69", mxb = False, s = 1 ,bgc = [0.2, 0.2, 0.2  ])
    mc.tabLayout(tv = 0)
    mc.columnLayout(adj=1)
    mc.rowColumnLayout(nc= 4 ,cw=[(1,180),(2,30),(3,30),(4,30)])
    mc.text(l ='')
    mc.button('SCminFrame', l= "1", c = 'SCUI("min")',  bgc = [0.24, 0.5, 0.2 ] )
    mc.button('SCmidFrame', l= "2", c = 'SCUI("mid")',  bgc = [0.2 ,0.4, 0.5 ] )
    mc.button('SCmaxFrame', l= "3", c = 'SCUI("max")',  bgc = [0.45, 0.2, 0.5 ] )
    mc.setParent( '..' )
    mc.scrollLayout('SCScrol',h=(mayaHSize*0.95))
    mc.columnLayout()
    mc.frameLayout('meshSetupFrame', cll= 1, cl= 0, label= "Mesh Setup" ,  bgc =[0.14,0.14,0.14] , w= 300)
    mc.rowColumnLayout(nc= 4 ,cw=[(1,70),(2,140),(3, 5),(4,80)])
    mc.text(l ='Base Mesh')
    mc.optionMenu('baseMeshMenu',  bgc =[0.28,0.28,0.28], bsp ='checkBaseMeshList()' ,cc='loadSymmetryState(),cageVisToggle(),showAllCutter(),updateVisLayer(),updateSnapState(),fadeOutCage(),rdMirrorUIUpdate()')
    mc.menuItem("NoBaseMeshMenu", label='No Base Mesh' )
    mc.text(l ='')
    mc.button('setBaseButton', l= "Set", c = 'checkBaseMeshList(),setCutterBaseMesh(),baseMeshColorUpdate(),updateVisLayer()' ,  bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )

    mc.rowColumnLayout(nc= 9 ,cw=[(1,70),(2,5),(3,30),(4,5),(5,30),(6,5),(7,65),(8, 5),(9,80)])
    mc.text(l ='')
    mc.text(l ='')
    mc.iconTextButton('meshLayerButton', h = 20, w = 30,  c = 'toggleLayer()', style='iconOnly', image1= 'nodeGrapherModeAll.svg' )
    mc.text(l ='')
    mc.iconTextButton('meshColorUpdateButton', h = 20, w = 30,  c = 'baseMeshColorUpdate()', style='iconOnly', image1= 'out_colorComposite_200.png' )
    mc.text(l ='')
    mc.button('reTargetButton', l= "reTarget", c = 'reTarget()',  bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('freeResultButton', l= "Finalize", c = 'freeResultMesh()',  bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.setParent( '..' )
    #######################################################################################################################################################################################
    mc.frameLayout('cutterFrame', cll= 1, cl= 0, label= "Cutter" ,  bgc = [0.14,0.14,0.14] , w= 300)
    mc.rowColumnLayout(nc=8 ,cw=[(1,40),(2, 58),(3,5),(4, 58),(5,5),(6,58),(7,5),(8,58)])
    mc.text(l ='Show',h=20)
    mc.iconTextButton(w=40,style='textOnly', l= "Selected", rpt = True, c = 'hideUnSelectedCutters()', bgc = [0.28,0.28,0.28])
    mc.text(l ='')
    mc.iconTextButton( w = 40, style='textOnly', l= "All", c = 'showAllCutter()', bgc = [0.28,0.28,0.28])
    mc.text(l ='')
    mc.iconTextButton( w = 40, style='textOnly', l= "None", c = 'hideAllCutter()', bgc = [0.28,0.28,0.28])
    mc.text(l ='',h=20)
    mc.iconTextButton( w = 40, style='textOnly', l= "Loop", rpt = True, c = 'showLastCutter()', bgc = [0.28,0.28,0.28])
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=5, cw=[(1,40),(2,50),(3,5),(4,110),(5,85)])
    mc.columnLayout()
    mc.text(l =' Cutter',h=50)
    mc.setParent( '..' )
    mc.columnLayout()
    mc.separator( height= 1, style='none' )
    mc.iconTextButton('newCutButton', h= 23 ,w = 50,  style='textOnly', l= "[ * ]", rpt = True, c = 'goPressCutter(4)', bgc = [0.28,0.28,0.28] )
    mc.separator( height= 3, style='none' )
    mc.iconTextButton('drawCutButton', h= 23 ,w = 50,  style='textOnly', l= "Draw", rpt = True, c = 'goDraw()', bgc = [0.28,0.28,0.28])
    mc.setParent( '..' )
    mc.intSliderGrp('cutterSideSlider', en=1,  vis = 0, v = 4,   min = 3,    max = 6, s = 1, cw3 = [35,40,200] , label = "side  " ,field =True )
    mc.columnLayout()
    mc.rowColumnLayout(nc=5, cw=[(1,30),(2,5),(3,30),(4,5),(5,30)])
    mc.iconTextButton('triButton', w = 30,  style='textOnly', l= "3", rpt = True, c = 'goPressCutter(3)', bgc = [0.28,0.28,0.28])
    mc.text(l ='')
    mc.iconTextButton('pentaButton', w = 30,  style='textOnly', l= "5", rpt = True, c = 'goPressCutter(5)', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.iconTextButton('hexButton', w = 30,  style='textOnly', l= "6", rpt = True, c = 'goPressCutter(6)', bgc = [0.28,0.28,0.28] )
    mc.separator( height= 1, style='none' )
    mc.setParent( '..' )
    mc.columnLayout()
    mc.iconTextButton('selCutButton', w = 100,  style='textOnly', l= "Selected", rpt = True, c = 'useOwnCutterShape()', bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.columnLayout()
    mc.iconTextButton('dulCutButton', w = 80,  style='textOnly', l= "Duplicate", rpt = True, c = 'cutterDulpicate()', bgc = [0.28,0.28,0.28] )
    mc.separator( height= 4, style='none' )
    mc.iconTextButton('comCutButton', w = 80,  style='textOnly', l= "Combine", rpt = True, c = 'combineSelCutters()', bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.columnLayout()
    mc.floatSliderGrp('cutterScaleSlider',  v = 1, min = 0.1, max = 5,  s = 0.1, cw3 = [40,50,190] , label = "Scale  " ,field =True)
    mc.floatField( 'cuterPreSize' , value=1 ,vis=0 )
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=8, cw=[(1,40),(2,58),(3,5),(4,58),(5,5),(6,58),(7,5),(8,58)])
    mc.text(l ='Opera',h=10)
    mc.button('subsButton',  l= "Difference", c = 'cutterType("subs")', bgc = [0.3, 0.5, 0.6] )
    mc.text(l ='')
    mc.button('unionButton', l= "Union", c ='cutterType("union")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('cutButton', l= "After Cut", c ='cutterType("cut")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('cutToNewMeshButton', l= "New Grp", c ='cutter2NewMeshGrp()', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.setParent( '..' )
    mc.columnLayout()
    mc.rowColumnLayout(nc=6 ,cw=[(1,40),(2, 80),(3,5),(4, 80),(5,5),(6,80)])
    mc.text(l ='Mirror',h=10)
    mc.button( w = 50, l= "X", c = 'cutterMirror("x")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button(w = 50, l= "Y", c = 'cutterMirror("y")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button(w = 50, l= "Z", c = 'cutterMirror("z")', bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    ########################################################################################################################################################################
    mc.frameLayout('controlFrame',cll= 1, cl= 0, label= "Control" ,  bgc = [0.14,0.14,0.14]  , w= 300)
    mc.rowColumnLayout(nc=6, cw=[(1,40),(2,80),(3,5),(4,80),(5,5),(6,80)])
    mc.text(l ='',h=20)
    mc.button( w = 50, l= "Bevel", c = 'QBoxBevel()', bgc = [0.28,0.28,0.28])
    mc.text(l ='')
    mc.button(w = 50, l= "Smooth", c = 'QBoxSmooth()',bgc = [0.28,0.28,0.28])
    mc.text(l ='')
    mc.button(w = 50, l= "Remove", c = 'QBoxBevelRemove()',bgc = [0.28,0.28,0.28])
    mc.setParent( '..' )
    mc.rowColumnLayout()
    mc.columnLayout()
    mc.floatSliderGrp('fractionSlider',  v = 0.2, min = 0.001, max = 1,  s = 0.01, cw3 = [55,40,180] , label = " Fraction" ,field =True,cc = 'attributeFloatSlider("fraction")',dc = 'attributeFloatSlider("fraction")')
    mc.intSliderGrp('segmentsSlider',     v = 1,   min = 1 ,    max = 10,  fmx = 20, s = 1, cw3 = [55,40,180] , label = "Segments" ,field =True ,cc= 'attributeIntSlider("segments")',dc= 'attributeIntSlider("segments")')
    mc.floatSliderGrp('depthSlider',     v = 1,   min = -1 ,   max = 1,   fmn = -3, fmx = 3, s = 1,  cw3 = [55,40,180] , label = "Depth" ,field =True,cc = 'attributeFloatSlider("depth")',dc = 'attributeFloatSlider("depth")')
    mc.setParent( '..' )
    mc.text(l ='')
    mc.separator( height=5, style='none' )
    mc.rowColumnLayout(nc=6, cw=[(1,40),(2,80),(3,5),(4,80),(5,5),(6,80)])
    mc.text(l ='',h=10)
    mc.button('makePanelButton', w = 50,  l= "Gap", c = 'makeGap()',bgc = [0.28,0.28,0.28])
    mc.text(l ='')
    mc.button('ScrapeButton', w = 50,  l= "Scrape", c = 'scrapeCutter()',bgc = [0.28,0.28,0.28])
    mc.text(l ='')
    mc.button('removePanelButton', w = 50,  l= "Remove", c = 'removeGap()',bgc = [0.28,0.28,0.28])
    mc.setParent( '..' )
    mc.rowColumnLayout()
    mc.columnLayout()
    mc.floatSliderGrp('gapSlider',   v = 0.3, min = 0.01, max = 5, fmx = 20,  s = 0.01, cw3 = [55,40,180] , label = "Gap   " ,field =True,cc='attributeGapSlider()',dc = 'attributeGapSlider()')
    mc.floatSliderGrp('scrapeSlider',  v = 0.3, min = 0.01, max = 1,  fmx = 5, s = 0.01, cw3 = [55,40,180] , label = "Scrape   " ,field =True)
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )

    #######################################################################################################################################################################################
    mc.frameLayout('meshSymmetryFrame', cll= 1, cl= 1, label= "Mesh Symmetry" ,   bgc =[0.14,0.14,0.14] , w= 300)
    buttonSize = 25
    mc.rowColumnLayout(nc=10 ,cw=[(1,70),(2,buttonSize),(3,buttonSize),(4,buttonSize),(5, buttonSize),(6,buttonSize),(7,buttonSize),(8,buttonSize),(9,buttonSize),(10,buttonSize)])
    mc.text(l ='      Direction')
    mc.text(l ='X')
    mc.button('symmXButtonP', l= "-", c ='boolSymmetry("x"' + ' ,1)' , bgc = [0.28,0.28,0.28])
    mc.button('symmXButtonN', l= "+", c ='boolSymmetry("x"' + ' ,2)' , bgc = [0.28,0.28,0.28])
    mc.text(l ='Y')
    mc.button('symmYButtonP', l= "-", c ='boolSymmetry("y"' + ' ,1)' , bgc = [0.28,0.28,0.28])
    mc.button('symmYButtonN', l= "+", c ='boolSymmetry("y"' + ' ,2)' , bgc = [0.28,0.28,0.28])
    mc.text(l ='Z')
    mc.button('symmZButtonP', l= "-", c ='boolSymmetry("z"' + ' ,1)' , bgc = [0.28,0.28,0.28])
    mc.button('symmZButtonN', l= "+", c ='boolSymmetry("z"' + ' ,2)' , bgc = [0.28,0.28,0.28])
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=6,cw=[(1,80),(2,104),(3, 6),(4,104)])
    mc.text(l ='')
    mc.button( l= "Reset", c ='boolSymmetryReset()', bgc =  [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button( l= "Freeze", c ='boolSymmetryFreeze()', bgc =  [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=6,cw=[(1,70),(2,75),(3,30),(4,57),(5,12),(6,50)])
    mc.text(l ='      Cage')
    mc.colorSliderGrp('CageColorSlider', l= '',cw = [(1,2),(2,13)], rgb=(0.5, 0, 0) ,dc = 'updateCageColor()')
    mc.iconTextButton(en = 1, w = 30,  style='iconOnly',image1='eye.png' )
    mc.floatSlider('CageTransparentSlider',min=0.1, max=1, value=0.5, step = 0.1 ,dc = 'updateCageTransparent()')
    mc.text(l ='')
    mc.button( l= 'On/Off', w = 35, bgc = [0.28,0.28,0.28],c='cageVisToggle()')
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )

    mc.frameLayout('meshRadialMirrorFrame', cll= 1, cl= 1, label= "Mesh Radial Mirror" ,   bgc =[0.14,0.14,0.14] , w= 300)
    mc.rowColumnLayout(nc=9 ,cw=[(1,70),(2,40),(3,40),(4,40),(5, 5),(6, 60),(7,20),(8,20)])
    mc.text(l ='Axis')
    mc.button('rMirrorXButton', l= "X", c ='rdMirror("x")' , bgc = [0.28,0.28,0.28])
    mc.button('rMirrorYButton', l= "Y", c ='rdMirror("y")' , bgc = [0.28,0.28,0.28])
    mc.button('rMirrorZButton', l= "Z", c ='rdMirror("z")' , bgc = [0.28,0.28,0.28])
    mc.text(l ='')
    mc.text(l ='Half')
    mc.button('rMirrorNegButton', l= "-", c ='rdMirrorHalf("n")' , bgc = [0.28,0.28,0.28])
    mc.button('rMirrorPosButton', l= "+", c ='rdMirrorHalf("p")' , bgc = [0.28,0.28,0.28])
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=3 ,cw=[(1,240),(2,15),(3,40)])
    mc.intSliderGrp('rMirrorSideSlider',  v = 1,   min = 3 ,  max = 15,  fmx = 20, s = 1, cw3 = [70,40,30] , label = "Side        " ,field =True ,cc= 'rdMirrorUpdate()',dc= 'rdMirrorUpdate()')
    mc.text(l ='')
    mc.text(l ='')
    mc.intSliderGrp('rMirrorOffsetSlider',  v = 10,   min = -20 ,  max = 20, fmn = -200, fmx = 200, s = 1, cw3 = [70,40,30] , label = "Offset        " ,field =True ,cc= 'rdMirrorOffsetUpdate()',dc= 'rdMirrorOffsetUpdate()')
    mc.text(l ='')
    mc.button(l= "Done", c ='rdMirrorOutput()' , bgc = [0.28,0.28,0.28])
    mc.setParent( '..' )
    mc.setParent( '..' )
    ########################################################################################################################################################################
    mc.frameLayout('alignmentFrame', cll= 1, cl= 1, label= "Alignment" ,  bgc = [0.14,0.14,0.14] , w= 300)
    mc.rowColumnLayout(nc=8, cw=[(1,40),(2,50),(3,5),(4,50),(5,5),(6,50),(7,10),(8,80)])
    mc.text(l ='Rotate',h=20)
    mc.iconTextButton( style='textOnly', l= "X",rpt = True, c = 'QChangeCutterDir("X")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.iconTextButton( style='textOnly', l= "Y",rpt = True, c = 'QChangeCutterDir("Y")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.iconTextButton( style='textOnly', l= "Z",rpt = True, c = 'QChangeCutterDir("Z")', bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=4, cw=[(1,40),(2,200),(3,5),(4,170),(5,50)])
    mc.text(l ='Border',h=20)
    mc.intSliderGrp('bboxDivSlider',     v = 2,   min = 1 ,    max = 10,  fmx = 20, s = 1, cw3 = [10,40,170] , label = "" ,field =True ,dc= 'borderAlginBBoxDivUpdate()')
    mc.button('borderAlginButton', l= 'On/Off', w = 50, bgc = [0.28,0.28,0.28],c='borderAlginBBoxToggle()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=8, cw=[(1,40),(2,50),(3,5),(4,50),(5,5),(6,50),(7,10),(8,80)])
    mc.text(l ='Axis',h=20)
    mc.button('toggleAxisX', l= "X", c = 'toggleAxisButton("X")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('toggleAxisY' , l= "Y", c = 'toggleAxisButton("Y")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('toggleAxisZ' , l= "Z", c = 'toggleAxisButton("Z")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='',h=20)
    mc.button('toggleAxisXYZ',  l= "XYZ", c = 'toggleAxisButton("XYZ")', bgc = [0.3, 0.5, 0.6] )
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=6, cw=[(1,40),(2,80),(3,5),(4,80),(5,5),(6,80)])
    mc.text(l ='Snap')
    mc.iconTextButton(w = 50,style='textOnly' , l= "Border", rpt = True, c = 'alignCutterToBase()', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.iconTextButton(w = 50,style='textOnly' , l= "Last Cutter", rpt = True, c = 'alignLastCutter()', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.iconTextButton(w = 50,style='textOnly' , l= "Select Cutter", rpt = True, c = 'alignSelCutter()', bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=6, cw=[(1,40),(2,80),(3,5),(4,80),(5,5),(6,80)])
    mc.text(l ='Even',h=20)
    mc.iconTextButton(w = 50,style='textOnly' , l= "left / right", rpt = True, c = 'evenObjLineUp("x")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.iconTextButton(w = 50,style='textOnly' , l= "up/ down", rpt = True, c = 'evenObjLineUp("y")', bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.setParent( '..' )
    ########################################################################################################################################################################
    mc.frameLayout('patternFrame',cll= 1, cl= 1, label= "Pattern" ,  bgc = [0.14,0.14,0.14]  , w= 300)
    mc.rowColumnLayout(nc=8, cw=[(1,40),(2,50),(3,5),(4,50),(5,5),(6,50),(7,10),(8,80)])
    mc.text(l ='Type',h=20)
    mc.button('arrayLinear', l= "Linear",  c = 'toggleArrayType()', bgc = [0.3, 0.5, 0.6] )
    mc.text(l ='')
    mc.button('arrayRadial' , l= "Radial", c = 'toggleArrayType()', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.text(l ='')
    mc.text(l ='')
    mc.button( l= "Freeze", c = 'instBake()', bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=8, cw=[(1,40),(2,50),(3,5),(4,50),(5,5),(6,50),(7,10),(8,80)])
    mc.text(l ='Axis',h=20)
    mc.button('arrayAxisX', l= "X", c = 'arrayPattrn("X")', bgc =  [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('arrayAxisY' , l= "Y", c = 'arrayPattrn("Y")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('arrayAxisZ' , l= "Z", c = 'arrayPattrn("Z")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button(  l= "Remove", c = 'removeArrayGrp()', bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.rowColumnLayout()
    mc.columnLayout()
    mc.intSliderGrp('instNumSlider',  v = 1,   min = 1,    max = 10,  fmx = 20 ,s = 1, cw3 = [55,40,180] , label = "Number" ,field =True,cc = 'instReNew()',dc = 'instReNew()' )
    mc.floatSliderGrp('disSlider', v = 1,   min = -3,    max = 3,  fmx = 20 ,fmn = -20, s = 0.01, cw3 = [55,40,180] , label = "Distance", field =True, cc ='instDistanceUpdate()',dc ='instDistanceUpdate()')
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )

    ##########################################################################################################################################################################
    mc.frameLayout('liveDrawFrame',cll= 1, cl= 1, label= "Live Draw" ,  bgc = [0.14,0.14,0.14]  , w= 300)
    mc.rowColumnLayout(nc=7 ,cw=[(1,40),(2, 78),(3,5),(4, 78),(5,5),(6,78)])
    mc.text(l ='Grid')
    mc.iconTextButton('snapGridCameraVisButton', w = 50,   style='textOnly', l= "Camera", c = 'snapGridCamera()', rpt = True, bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.iconTextButton('snapGridPointVisButton', w = 50,   style='textOnly', l= "Point", c = 'goPressDraw()', rpt = True, bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.iconTextButton('snapGridVisToggleButton', w = 50,   style='textOnly', l= "Remove", c = 'drawGirdOff()', rpt = True, bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.columnLayout()
    mc.intSliderGrp('snapGirdSize', v = 10,  min = 1, max = 50,  fmx=100 ,s = 1, cw3 = [35,40,200] , label = "Grid  " ,field =True, dc ='resizeSnapGrid()')
    mc.intSliderGrp('snapGirdRot', v = 0,   min = 0, max = 90,  s = 1, cw3 = [35,40,200], label = "Rot   " ,field =True , dc ='rotateSnapGrid()')
    mc.floatSliderGrp('snapGirdOffset',  v = 0.1,   min = 0.01,    max = 3,  fmx = 20 ,s = 0.01, cw3 = [35,40,200] , label = "Offset", field =True ,dc ='offsetSnapGrid()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=6 ,cw=[(1,40),(2, 78),(3,5),(4, 78),(5,5),(6,78)])
    mc.text(l ='Tools')
    mc.button('cureveDrawButtton', w = 50,  l= "Draw Curve", c = 'drawCurveNow()',bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('buildBlockButton', w = 50,   l= "Make Block",  c = 'makeDrawBlock()',bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.setParent( '..' )
    ##########################################################################################################################################################################
    mc.frameLayout('bakeFrame',cll= 1, cl= 1, label= "Bake" ,  bgc = [0.14,0.14,0.14]  , w= 300)
    mc.rowColumnLayout(nc=6, cw=[(1,40),(2,80),(3,5),(4,80),(5,5),(6,80)])
    mc.text(l ='',h=10)
    mc.button('bakeUnSelButton', w = 50,   l= "Unselect", c = 'bakeCutter("unselect")', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('bakeAllButton', w = 50,   l= "All", c = 'bakeCutter("all")',bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.button('bakeRestoreButton', w = 50,  l= "Restore",c = 'restoreCutterWithSymmtry()',bgc = [0.28,0.28,0.28] )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.frameLayout('meshBevelManagerFrame',cll= 1, cl= 1, label= "Mesh Bevel Manager" ,  bgc = [0.14,0.14,0.14]  , w= 300)
    mc.rowColumnLayout(nc=4 ,cw=[(1,80),(2, 185),(3,5),(4, 58)])
    mc.text(l ='',h=20)
    mc.iconTextButton('preBevelButton',  w=40,style='textOnly', l= "Bevel Manager", rpt = True, c = 'jwSpeedCutBevelMangerSetup()', bgc = [0.14, 0.14, 0.14] )
    mc.separator( height=15, style='none' )
    mc.setParent( '..' )
    mc.separator( height=15, style='none' )
    mc.showWindow(jwSpeedCutWin)
    mc.window("jwSpeedCutWin",e=True,w = 320,h = 1250)
    mc.commandEcho( state=False )
    mc.scriptEditorInfo(suppressWarnings=0,suppressInfo=0,se=0)
    checkBaseMeshList()
    allowedAreas = ['right', 'left']
    mc.dockControl('speedCutDock', l='speedCut 1.69', area='right', content = 'jwSpeedCutWin',  allowedArea= allowedAreas, fcc = 'floatSCUIsize()')
    #start with floating UI
    #mc.dockControl('speedCutDock', l='speedCut 1.69', area='right', content = 'jwSpeedCutWin',  allowedArea= allowedAreas, fcc = 'floatSCUIsize()',fl=1)


def SCUI(state):
    frameList = {'meshSetupFrame','meshSymmetryFrame','meshRadialMirrorFrame','cutterFrame','controlFrame','alignmentFrame','patternFrame','bakeFrame','liveDrawFrame','meshBevelManagerFrame'}
    midList = {'meshSetupFrame','cutterFrame','controlFrame'}
    otherList = list(set(frameList) - set(midList))
    if state == 'min':
        for f in frameList:
            mc.frameLayout(f, e=1, cl= 1)
    elif state == 'mid':
        for m in midList:
            mc.frameLayout(m, e=1, cl= 0)
        for o in otherList:
            mc.frameLayout(o, e=1, cl= 1)
    elif state == 'max':
        for f in frameList:
            mc.frameLayout(f, e=1, cl= 0)

def floatSCUIsize():
    SCUI('mid')
    checkState = mc.dockControl('speedCutDock', q=1 ,fl=1)
    mayaHSize = mc.window('MayaWindow', q=1, h=1)
    if checkState == 0:
        mc.scrollLayout('SCScrol',e=1,h=(mayaHSize*0.95))
    else:
        mc.scrollLayout('SCScrol',e=1,h=570)
        mc.dockControl('speedCutDock', e=1 ,h=570)


###################################################################################################################################################
def cutter2NewMeshGrp():
    selCut = mc.ls(sl=1,l=1)
    if len(selCut) == 1:
        myType = checkInstType()
        if myType[1] != 'new':
            instBake()
            selCut = mc.ls(sl=1,l=1)
        getOPType = mc.getAttr(selCut[0]+'.cutterOp')
        if getOPType != 'union':
            #create new box shape by adding all union cutter and base mesh
            meshNameGrp = selCut[0].split('|')[1]
            meshName = meshNameGrp.replace('BoolGrp','')
            liveCutterList = mc.ls('|'+ meshNameGrp + '|' + meshName + '_cutterGrp|boxCutter*',l=True)
            bakeCutterList = mc.ls('|'+ meshNameGrp + '|' + meshName + '_bakeStep|bakeCutter*',l=True)
            totalList =   liveCutterList +  bakeCutterList
            collectUnionShape =[]
            for t in totalList:
                checkType = mc.getAttr(t+'.cutterOp')
                if checkType == 'union':
                    collectUnionShape.append(t)
            if mc.objExists('|'+ meshNameGrp + '|' + meshName + '_bakeStep|' + meshName + '_bakeBaseMesh'):
                collectUnionShape.append('|'+ meshNameGrp + '|' + meshName + '_bakeStep|' + meshName + '_bakeBaseMesh')
            else:
                collectUnionShape.append('|'+ meshNameGrp + '|' + meshName)
            dulMesh = mc.duplicate(collectUnionShape, rr = True, un=True)
            mc.parent(dulMesh,w=1)
            selList = mc.ls(sl=1,fl=1,transforms=1,l=1)
            while len(selList) > 1:
                mc.polyCBoolOp(selList[0], selList[1], op=1, ch=1, preserveColor=0, classification=1, name=selList[0])
                mc.DeleteHistory()
                if mc.objExists(selList[1]):
                    mc.delete(selList[1])
                mc.rename(selList[0])
                selList.remove(selList[1])
            combineShape = mc.ls(sl=1)
            checkNumber = ''.join([n for n in selCut[0].split('|')[-1] if n.isdigit()])
            mc.rename(meshName + "bc" + str(checkNumber))
            shadowMesh = mc.ls(sl=1)
            checkBaseMeshList()
            mc.select(shadowMesh)
            setCutterBaseMesh()
            updateVisLayer()
            cutterShapeNode = mc.listRelatives(selCut[0], s=True, f=True )
            preCutShapeNode = mc.listRelatives(shadowMesh[0], s=True, f=True  )
            dulCombineMesh = mc.duplicate(preCutShapeNode, rr = True, un=True)
            mc.rename(dulCombineMesh, shadowMesh[0]+'_myInterMesh')
            interMeshShapeNode = mc.listRelatives(shadowMesh[0]+'_myInterMesh', s=True, f=True  )
            mc.createNode('polyCBoolOp')
            mc.rename(shadowMesh[0]+'_myInter')
            mc.connectAttr((interMeshShapeNode[0]+'.outMesh'), (shadowMesh[0]+'_myInter.inputPoly[0]'),f=True)
            mc.connectAttr((interMeshShapeNode[0]+'.worldMatrix[0]'), (shadowMesh[0]+'_myInter.inputMat[0]'),f=True)
            mc.connectAttr((cutterShapeNode[0]+'.outMesh'), (shadowMesh[0]+'_myInter.inputPoly[1]'),f=True)
            mc.connectAttr((cutterShapeNode[0]+'.worldMatrix[0]'), (shadowMesh[0]+'_myInter.inputMat[1]'),f=True)
            mc.setAttr((shadowMesh[0]+'_myInter.operation'),3)
            mc.connectAttr((shadowMesh[0]+'_myInter.output'), (preCutShapeNode[0]+'.inMesh'),f=True)
            mc.select(selCut)
            mc.sets(name = (shadowMesh[0] + 'Shadow'), text= (shadowMesh[0] + 'Shadow'))
            showAllCutter()
            baseMeshColorUpdate()
            mc.setAttr((shadowMesh[0]+".translate"),0,0,0)
            mc.setAttr((shadowMesh[0]+".rotate"),0,0,0)
            mc.setAttr((shadowMesh[0]+".scale"),1,1,1)
        else:
            print('only work for different or after cut')
    else:
        print ('select one cutter Only!')

def fixShadowLink():
    listAllShadow = mc.ls('*Shadow')
    for l in listAllShadow:
        checkNodeType = mc.nodeType(l)
        if checkNodeType == 'objectSet':
            shadowName = mc.sets(l,q=1)
            targetName = l.replace('Shadow','')
            if mc.objExists((targetName +'BoolGrp')) == 0:
                mc.delete(l)
            else:
                cutterShapeNode = mc.listRelatives(shadowName[0], s=True, f=True )
                preCutShapeNode = mc.listRelatives(targetName, s=True, f=True )
                shapes = mc.listRelatives((targetName+'_bool'), shapes=True)
                shadeEng = mc.listConnections(shapes , type = 'shadingEngine')
                materials = mc.ls(mc.listConnections(shadeEng ), materials = True)
                if mc.objExists((targetName +'_myInter')) == 0:
                    mc.createNode('polyCBoolOp')
                    mc.rename(targetName+'_myInter')
                    mc.connectAttr((preCutShapeNode[0]+'.outMesh'), (targetName+'_myInter.inputPoly[0]'),f=True)
                    mc.connectAttr((preCutShapeNode[0]+'.worldMatrix[0]'), (targetName+'_myInter.inputMat[0]'),f=True)
                    mc.connectAttr((cutterShapeNode[0]+'.outMesh'), (targetName+'_myInter.inputPoly[1]'),f=True)
                    mc.connectAttr((cutterShapeNode[0]+'.worldMatrix[0]'), (targetName+'_myInter.inputMat[1]'),f=True)
                    mc.setAttr((targetName+'_myInter.operation'),2)
                    mc.connectAttr((targetName+'_myInter.output'), (targetName+'_preSubBoxShape.inMesh'),f=True)
                else:
                    mc.connectAttr((cutterShapeNode[0]+'.outMesh'), (targetName+'_myInter.inputPoly[1]'),f=True)
                    mc.connectAttr((cutterShapeNode[0]+'.worldMatrix[0]'), (targetName+'_myInter.inputMat[1]'),f=True)
                    mc.connectAttr((targetName+'_myInter.output'), (targetName+'_preSubBoxShape.inMesh'),f=True)

                if mc.objExists(targetName+'_ShaderSG'):
                    mc.sets((targetName+'_bool'), e=True, forceElement = (targetName+'_ShaderSG'))


###################################################################################################################################################

def deSelect():
    obj_shape = mc.listRelatives(parent=True, f=True)
    obj = mc.listRelatives(obj_shape,parent=True, f=True)
    mc.select(obj)
    mc.selectMode(leaf=True)
    cmd = "changeSelectMode -object;"
    mel.eval(cmd)
    mc.select(clear=True)

def instDistanceUpdate():
    myType = checkInstType()
    if myType[1] != 'new':
        checkMaster = myType[0]
        checkDis =  mc.floatSliderGrp('disSlider',q=True, v = True  )
        checkState = mc.attributeQuery('arrayOffset',node = checkMaster,ex=True)
        if checkState == 1:
            mc.setAttr((checkMaster+'.arrayOffset'),checkDis)


def instReNew():
    myType = checkInstType()
    if myType[1] != 'new':
        instRemove()
        checkMaster = myType[0]
        currentDir = mc.getAttr(checkMaster+'.arrayDirection')

        if myType[1] == 'linear':
            instLinearAdd(currentDir)
        else:
            instRadAdd(currentDir)

def instTypeToggle():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    currentSel =mc.ls(sl=1,fl=1)
    if len(currentSel) == 1:
        #case one Linear to Radial
        myType = checkInstType()
        if myType[1] != 'new':
            getNumber = mc.getAttr(myType[0]+'.arrayNumber')
            getDis = mc.getAttr(myType[0]+'.arrayOffset')
            getDir = mc.getAttr(myType[0]+'.arrayDirection')
            mc.intSliderGrp('instNumSlider', e=True,  v = getNumber)
            mc.floatSliderGrp('disSlider',e=True, v = getDis)
            if myType[1] == 'linear':
                instRemove()
                instRadAdd(getDir)

            elif myType[1] == 'radial':
                removeRadArray()
                instLinearAdd(getDir)


def instLinearAdd(direction):
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if len(beseMesh) > 0:
        selCutterCheck = mc.ls(sl=1, fl=1, l=1, type='transform')
        if 'boxCutter' in selCutterCheck[0]:
            mc.button('arrayLinear',e=True, bgc = [0.3, 0.5, 0.6] )
            mc.button('arrayRadial',e=True, bgc = [0.28,0.28,0.28])
            myType = checkInstType()
            instRemove()
            dir = direction
            arraySample = mc.ls(sl=1,fl=1)
            sourcePivot = mc.xform(arraySample[0], q=1, ws=1 ,rp=1)
            if 'boxCutter' in arraySample[0] and len(arraySample)==1:
                bbox= mc.xform(arraySample[0], q=1, ws=1, bb=1)
                myLength = []
                if dir == 'X':
                    myLength=math.sqrt((math.pow(bbox[0]-bbox[3],2)))
                if dir == 'Y':
                    myLength=math.sqrt((math.pow(bbox[1]-bbox[4],2)))
                if dir == 'Z':
                    myLength=math.sqrt((math.pow(bbox[2]-bbox[5],2)))

                getIntNumber = []
                getDist = []

                if myType[1] == 'new':
                    getIntNumber = 2
                    getDist = 1.5
                    mc.intSliderGrp('instNumSlider', e=True,  v = 2)
                    mc.floatSliderGrp('disSlider',e=True, v = 1.5)
                else:
                    getIntNumber = mc.intSliderGrp('instNumSlider', q=True,  v = True)
                    checkState = mc.attributeQuery('arrayOffset',node = myType[0],ex=True)
                    if checkState == 1:
                        getDist = mc.getAttr(myType[0]+'.arrayOffset')
                        mc.floatSliderGrp('disSlider',e=True, v = getDist)
                #create Attr
                if not mc.attributeQuery('arrayNumber', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayNumber')

                if not mc.attributeQuery('arrayDirection', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayDirection' ,dt= 'string')

                if not mc.attributeQuery('arrayType', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayType',dt= 'string')

                if not mc.attributeQuery('arrayLength', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayLength')

                if not mc.attributeQuery('arrayOffset', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayOffset')

                if not mc.attributeQuery('arrayMaster', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayMaster'  ,dt= 'string')
                    mc.setAttr((arraySample[0]+'.arrayOffset'),1)

                mc.setAttr((arraySample[0]+'.arrayNumber'),getIntNumber)
                mc.setAttr((arraySample[0]+'.arrayDirection'),dir,type="string")
                mc.setAttr((arraySample[0]+'.arrayType'),'linear',type="string")
                mc.setAttr((arraySample[0]+'.arrayLength'),myLength)
                mc.setAttr((arraySample[0]+'.arrayMaster'),arraySample[0],type="string")

                dirA = (arraySample[0]+'.translate'+dir)
                collections=[]

                for i in range(getIntNumber-1):
                    newIns = mc.instance(arraySample[0])
                    collections.append(newIns[0])
                    if not mc.attributeQuery('arrayOrder', node = newIns[0], ex=True ):
                        mc.addAttr(newIns[0], ln='arrayOrder')
                    mc.setAttr((newIns[0]+'.arrayOrder'),(i+1))
                    mc.setAttr((arraySample[0] + '.arrayOffset'),getDist)
                    cmdTextA = (newIns[0] + '.translate' + dir + '= ' + arraySample[0] + '.arrayLength *' + arraySample[0] + '.arrayOffset *' +  newIns[0] + '.arrayOrder +'+ dirA +';')
                    mc.expression( s = cmdTextA, o = newIns[0], ae = True, uc = all)
                    attrList = {'translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ'}
                    attrList.remove(('translate' + str(dir)))
                    for a in attrList:
                        mc.connectAttr((arraySample[0]+'.' + a), (newIns[0] + '.' + a),f=True)
                parent = mc.listRelatives(arraySample[0], p=True )
                if not 'ArrayGrp' in parent[0]:
                    mc.group(arraySample[0],collections)
                    mc.rename(arraySample[0]+'ArrayGrp')

                mc.xform((arraySample[0]+'ArrayGrp') ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
                mc.setAttr( (arraySample[0]+".arrayNumber"),getIntNumber)
                mc.setAttr( (arraySample[0]+".arrayOffset"),getDist)
                mc.select((arraySample[0]+'ArrayGrp'))
                fixBoolNodeConnection()


def toggleArrayType():
    #toggle existing pattern
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    currentSel =mc.ls(sl=1,fl=1)
    checkState = mc.button('arrayLinear', q=True , bgc =True )
    if len(currentSel) == 1:
        myType = checkInstType()
        if myType[1] != 'new':
            getNumber = mc.getAttr(myType[0]+'.arrayNumber')
            getDis = mc.getAttr(myType[0]+'.arrayOffset')
            getDir = mc.getAttr(myType[0]+'.arrayDirection')
            getGap = mc.getAttr(myType[0]+'.panelGap')
            mc.intSliderGrp('instNumSlider', e=True,  v = getNumber)
            mc.floatSliderGrp('disSlider',e=True, v = getDis)
            mc.floatSliderGrp('gapSlider',e=True, v = getGap)
            if (checkState[0] < 0.285):
                removeRadArray()
                instLinearAdd(getDir)

            else:
                instRemove()
                instRadAdd(getDir)


    if (checkState[0] < 0.285):
        mc.button('arrayRadial' ,e=True, bgc = [0.28,0.28,0.28])
        mc.button('arrayLinear', e=True, bgc = [0.3, 0.5, 0.6] )
    else:
        mc.button('arrayRadial' ,e=True, bgc = [0.3, 0.5, 0.6] )
        mc.button('arrayLinear', e=True, bgc = [0.28,0.28,0.28])


def arrayPattrn(dir):
    checkState = mc.button('arrayLinear', q=True , bgc =True )
    if (checkState[0] > 0.285):#Linear
        instLinearAdd(dir)
    else:
        instRadAdd(dir)

def checkInstType():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    arraySample = []
    checkGrp = mc.ls(sl=1,fl=1,l=1)
    if 'ArrayGrp' in checkGrp[0]:
        mc.connectControl('disSlider', (''))
        allChild = mc.listRelatives(checkGrp[0], ad=True)
        getShapeNode = mc.ls(allChild,type ='shape')
        listTransNode = mc.listRelatives(getShapeNode,  p=True )
        arraySample = listTransNode
        checkMaster = mc.getAttr(arraySample[0]+'.arrayMaster')
        checkMasterType = mc.getAttr(arraySample[0]+'.arrayType')
        mc.floatSliderGrp('disSlider',e=True, en= True )
        mc.intSliderGrp('instNumSlider',e=True, en= True )
        return (checkMaster,checkMasterType)
    else:
        if mc.attributeQuery('arrayMaster', node = checkGrp[0], ex=True ):
            checkMaster = mc.getAttr(checkGrp[0]+'.arrayMaster')
            checkMasterType = mc.getAttr(checkGrp[0]+'.arrayType')
            if checkMasterType != None:
                return (checkMaster,checkMasterType)
        else:
            return ('new','new')


def removeArrayGrp():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selCutterCheck = mc.ls(sl=1, fl=1, l=1, type='transform')
    if len(selCutterCheck) == 1 and 'boxCutter' in selCutterCheck[0] and 'ArrayGrp' in selCutterCheck[0]:
        myType = checkInstType()
        mc.select(myType[0])
        if myType[1] == 'radial':
            removeRadArray()
        elif myType[1] == 'linear':
            instRemove()
            mc.parent(myType[0],(beseMesh +'_cutterGrp'))
            mc.delete(myType[0]+'ArrayGrp')
        mc.setAttr((myType[0]+'.arrayType'),'new',type="string")
        mc.setAttr((myType[0]+'.arrayMaster'),'new',type="string")


def instRadReNew():
    mc.radioButtonGrp('arrayTypeButton',e=True, sl = 2)
    myType = checkInstType()
    if myType[1] != 'radial':#lin
        instLink()
    removeRadArray()
    checkMaster = myType[0]
    if mc.attributeQuery('arrayDirection', node = checkMaster, ex=True ):
        currentDir = mc.getAttr(checkMaster+'.arrayDirection')
        instRadAdd(currentDir)
    fixBoolNodeConnection()
    instLink()

def instRadAdd(direction):
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selCutterCheck = mc.ls(sl=1, fl=1, l=1, type='transform')
    if len(beseMesh) > 0:
        if 'boxCutter' in selCutterCheck[0] :
            mc.button('arrayLinear',e=True, bgc = [0.28,0.28,0.28])
            mc.button('arrayRadial',e=True, bgc = [0.3, 0.5, 0.6])
            myType = checkInstType()
            removeArrayGrp()
            arraySample = mc.ls(sl=1,fl=1)
            dir = direction
            getIntNumber = []
            getDist = []

            if myType[1] == 'new':
                getIntNumber = 3
                getDist = 1
                mc.intSliderGrp('instNumSlider', e=True,  v = 3)
                mc.floatSliderGrp('disSlider',e=True, v = 1)
            else:
                getIntNumber = mc.intSliderGrp('instNumSlider', q=True,  v = True)
                checkState = mc.attributeQuery('arrayOffset',node = myType[0],ex=True)
                if checkState == 1:
                    getDist = mc.getAttr(myType[0]+'.arrayOffset')
                    mc.floatSliderGrp('disSlider',e=True, v = getDist)
            collection =[]

            #create Attr
            if not mc.attributeQuery('arrayNumber', node = arraySample[0], ex=True ):
                mc.addAttr(arraySample[0], ln='arrayNumber')

            if not mc.attributeQuery('arrayDirection', node = arraySample[0], ex=True ):
                mc.addAttr(arraySample[0], ln='arrayDirection' ,dt= 'string')

            if not mc.attributeQuery('arrayType', node = arraySample[0], ex=True ):
                mc.addAttr(arraySample[0], ln='arrayType',dt= 'string')

            if not mc.attributeQuery('arrayOffset', node = arraySample[0], ex=True ):
                mc.addAttr(arraySample[0], ln='arrayOffset')

            if not mc.attributeQuery('arrayMaster', node = arraySample[0], ex=True ):
                mc.addAttr(arraySample[0], ln='arrayMaster'  ,dt= 'string')
                mc.setAttr((arraySample[0]+'.arrayOffset'),1)
            if not mc.attributeQuery('arrayLength', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayLength')

            mc.setAttr((arraySample[0]+'.arrayNumber'),getIntNumber)
            mc.setAttr((arraySample[0]+'.arrayOffset'),getDist)
            mc.setAttr((arraySample[0]+'.arrayDirection'),dir,type="string")
            mc.setAttr((arraySample[0]+'.arrayType'),'radial',type="string")
            mc.setAttr((arraySample[0]+'.arrayMaster'),arraySample[0],type="string")

            bbox= mc.xform(arraySample[0], q=1, ws=1, bb=1)
            length=math.sqrt((math.pow(bbox[0]-bbox[3],2)+math.pow(bbox[1]-bbox[4],2)+math.pow(bbox[2]-bbox[5],2))/3)
            mc.setAttr((arraySample[0]+'.arrayLength'),length)

            sourcePivot = mc.xform(arraySample[0], q=1, ws=1 ,rp=1)

            rAngle = 360.0 / getIntNumber
            #inst
            collection = []
            for i in range(getIntNumber-1):
                mc.select(arraySample[0])
                mc.instance()
                newNode = mc.ls(sl=True)
                mc.select(newNode)
                mc.group()
                mc.rename(newNode[0]+'_Trans')
                mc.group()
                mc.rename(newNode[0]+'_Rot')
                collection.append(newNode[0]+'_Rot')
                mc.xform((newNode[0]+'_Rot') ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
                if dir == 'X':
                    mc.rotate((rAngle*(i)+rAngle), 0 ,0, r=True, ws=True, fo=True)
                elif dir == 'Y':
                    mc.rotate(0,(rAngle*(i)+rAngle),0, r=True, ws=True, fo=True)
                else:
                    mc.rotate(0,0,(rAngle*(i)+rAngle), r=True, ws=True, fo=True)
            # group master
            mc.select(arraySample[0])
            mc.group()
            mc.rename(arraySample[0]+'_Trans')
            mc.group()
            mc.rename(arraySample[0]+'_Rot')
            collection.append(arraySample[0]+'_Rot')
            mc.xform((arraySample[0]+'_Rot') ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))

            mc.select(collection)
            mc.group()
            mc.rename(arraySample[0]+'ArrayGrp')
            OffsetDir =[]

            if dir == 'X':
                OffsetDir = 'Y'
            elif dir == 'Y':
               OffsetDir = 'X'
            else:
              OffsetDir = 'X'

            for c in collection:
                cutterName = c.replace('_Rot', '')
                cmdTextA = (cutterName + '_Trans.translate' + OffsetDir + '= ' + arraySample[0] + '.arrayLength *' + arraySample[0] + '.arrayOffset;')
                mc.expression( s = cmdTextA, o = (arraySample[0] + '_Trans.translate'), ae = True, uc = all)
                mc.select((arraySample[0]+'ArrayGrp'))
                mc.xform((arraySample[0]+'ArrayGrp') ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
                attrList = {'translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ'}
                if cutterName != arraySample[0]:
                    for a in attrList:
                        mc.connectAttr((arraySample[0]+'.' + a), (cutterName + '.' + a),f=True)

            mc.setAttr( (arraySample[0]+".arrayNumber"),getIntNumber)
            mc.setAttr( (arraySample[0]+".arrayOffset"),getDist)
            fixBoolNodeConnection()

def removeRadArray():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
    myType = checkInstType()
    if myType[1] == 'radial':
        arraySample = myType[0]
        if mc.objExists(arraySample+'_Rot*'):
            mc.select(arraySample+'_Rot*')
            listRArray = mc.ls(sl=1,fl=1)
            mc.delete(listRArray[1:len(listRArray)])
            mc.parent(arraySample,beseMesh+'_cutterGrp')
            sourcePivot = mc.xform((arraySample+'_Rot'), q=1, ws=1 ,rp=1)
            mc.select(arraySample)
            mc.move( sourcePivot[0],sourcePivot[1],sourcePivot[2],rpr=True)
            if mc.objExists(arraySample+'ArrayGrp'):
                mc.delete(arraySample+'ArrayGrp')
        if mc.objExists(arraySample+'ArrayGrp'):
            mc.delete(arraySample+'ArrayGrp')

        shapeNode = mc.listRelatives(arraySample, s=True )
        listConnect = mc.connectionInfo((shapeNode[0]+'.outMesh'), dfs=True )
        if len(listConnect)>0:
            for a in listConnect:
                mc.disconnectAttr((shapeNode[0]+'.outMesh'), a)
        checkNumber = ''.join([n for n in arraySample.split('|')[-1] if n.isdigit()])
        mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(checkNumber)+']')),f=True)
        mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((boolNode[0]+'.inputMat['+str(checkNumber)+']')),f=True)
        mc.select(arraySample)

def instBake():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkSel = mc.ls(sl=True)
    if len(checkSel) > 0:
        myType = checkInstType()
        if myType[1] != 'new':
            opType = mc.getAttr(myType[0]+'.cutterOp')
            arraySample = myType[0]
            sourcePivot = mc.xform((arraySample+'ArrayGrp'), q=1, ws=1 ,rp=1)
            mc.select(arraySample+'ArrayGrp')
            mc.select(hi=True)
            mc.select(arraySample,d=True)
            mc.select((arraySample+'ArrayGrp'),d=True)
            cutterList = mc.ls('boxCutter*',sl=True,type='transform')
            mc.select(arraySample)
            mc.ConvertInstanceToObject()
            if myType[1] == 'radial':
                mc.parent(arraySample,(arraySample+'ArrayGrp'))
            unInstanceMesh = mc.ls(sl=1,fl=1, l=1)
            for c in cutterList:
                if '_Rot' not in c and '_Trans' not in c and 'ArrayGrp' not in c:
                    if myType[1] == 'radial':
                        mc.parent(c , (arraySample + 'ArrayGrp'))
                    mc.select(arraySample,r=True)
                    mc.duplicate()
                    newNode=mc.ls(sl=True)
                    mc.select(c,add=1)
                    mc.matchTransform(pos =True,rot=True)
                    mc.delete(c)
                    mc.rename(newNode,c)
            for c in cutterList:
                if '_Rot' in c :
                    mc.delete(c)
            mc.select(arraySample+'ArrayGrp')
            mc.select(hi=True)
            mc.select((arraySample+'ArrayGrp'),d=True)
            listNew = mc.ls('boxCutter*',sl=True,type='transform')
            for n in listNew:
                mc.rename(n,'tempCutter01')
            listBake=mc.ls('tempCutter*',s=1)
            while len(listBake) > 1:
                mc.polyCBoolOp(listBake[0], listBake[1], op=1, ch=1, preserveColor=0, classification=1, name=listBake[0])
                mc.DeleteHistory()
                if mc.objExists(listBake[1]):
                    mc.delete(listBake[1])
                mc.rename(listBake[0])
                listBake.remove(listBake[1])
            #in case cutterGrp will get delete when delete history
            if mc.objExists((beseMesh +'_cutterGrp')) == 0:
                mc.CreateEmptyGroup()
                mc.rename((beseMesh +'_cutterGrp'))
                mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))
            mc.select(listBake[0])
            useOwnCutterShape()
            newCutter = mc.ls(sl=True, fl=True)
            mc.rename(newCutter[0],arraySample)
            mc.xform(arraySample ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
            if mc.objExists(arraySample+'ArrayGrp'):
                mc.delete(arraySample+'ArrayGrp')
                mc.ogs(reset =1)
            if not mc.attributeQuery('cutterOp', node = arraySample, ex=True ):
                mc.addAttr(arraySample, ln='cutterOp',  dt= 'string')
            mc.setAttr((arraySample+'.cutterOp'),e=True, keyable=True)
            mc.setAttr((arraySample+'.cutterOp'),opType,type="string")
            mc.select(arraySample)
            fixBoolNodeConnection()
    else:
        print ('nothing selected!')

def instRemove():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    myType = checkInstType()
    if myType[1] == 'linear':
        arraySample = myType[0]
        listA = mc.listConnections(arraySample,type = 'expression')
        if listA != None:
            listA = set(listA)
            collectInst=[]
            for l in listA:
                checkConnection = mc.connectionInfo( (l+'.output[0]'), dfs=True)
                mesh = checkConnection[0].split(".")[0]
                collectInst.append(mesh)
            mc.delete(collectInst)
        shapeNode = mc.listRelatives(arraySample, s=True )
        listConnect = mc.connectionInfo((shapeNode[0]+'.outMesh'), dfs=True )
        if len(listConnect)>0:
            for a in listConnect:
                mc.disconnectAttr((shapeNode[0]+'.outMesh'), a)
        checkNumber = ''.join([n for n in arraySample.split('|')[-1] if n.isdigit()])
        if mc.objExists(beseMesh + '_mySubs') == 0:
            restoreCutterWithSymmtry()

        setType = mc.getAttr(arraySample+'.cutterOp')

        mc.connectAttr( (shapeNode[0]+".outMesh"), ((beseMesh +'_my' + setType.title() + '.inputPoly['+str(checkNumber)+']')),f=True)
        mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((beseMesh +'_my' + setType.title() +'.inputMat['+str(checkNumber)+']')),f=True)
        mc.select(arraySample)
        checkGap = mc.getAttr(arraySample + '.panelGap')
        if checkGap > 0:
            makeGap()
            mc.floatSliderGrp('gapSlider',e=True, en= True,v=checkGap )

#######################################################################################################################################################################################
#######################################################################################################################################################################################




def moveRightItem():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selListRight = mc.textScrollList('bevelList', q=True, si=True)
    checkState = mc.iconTextButton('visRight', q = True , image1 = True)
    if selListRight != None:
        if len(selListRight) > 0:
            mc.textScrollList('nonBevelList',edit = True, da = True)
            for s in selListRight:
                mc.textScrollList('bevelList',edit = True, ri = s)
                mc.textScrollList('nonBevelList',edit = True, si = s, append = s)
            sortBevelList()
            for s in selListRight:
                mc.textScrollList('nonBevelList',edit = True, si = s)
                longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
                if checkState == 'nodeGrapherSoloed.svg':
                    mc.setAttr((longName + '.visibility'), 1)
                else:
                    mc.setAttr((longName + '.visibility'), 0)
                mc.setAttr((longName+'.preBevel'),0)

def moveLeftItem():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selListLeft = mc.textScrollList('nonBevelList', q=True, si=True)
    checkState = mc.iconTextButton('visLeft', q = True , image1 = True)
    if selListLeft != None:
        if len(selListLeft) > 0:
            mc.textScrollList('bevelList',edit = True, da = True)
            for s in selListLeft:
                mc.textScrollList('nonBevelList',edit = True, ri = s)
                mc.textScrollList('bevelList',edit = True, si = s ,append = s)
            sortBevelList()
            for s in selListLeft:
                mc.textScrollList('bevelList',edit = True, si = s)
                longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
                if checkState == 'nodeGrapherSoloed.svg':
                    mc.setAttr((longName + '.visibility'), 1)
                else:
                    mc.setAttr((longName + '.visibility'), 0)
                mc.setAttr((longName+'.preBevel'),1)


def reselctList():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    currentSel = mc.ls(sl=True,l=True)
    mc.textScrollList('nonBevelList', e=True, da=True)
    selListRight = mc.textScrollList('nonBevelList', q=True, ai=True)
    if selListRight != None:
        for c in currentSel:
            shortName = c.split('|')[-1]
            for s in selListRight:
                if shortName == s:
                    mc.textScrollList('nonBevelList',edit = True, si = shortName)

    mc.textScrollList('bevelList', e=True, da=True)
    selListLeft = mc.textScrollList('bevelList', q=True, ai=True)
    if selListLeft != None:
        for c in currentSel:
            shortName = c.split('|')[-1]
            for s in selListLeft:
                if shortName == s:
                    mc.textScrollList('bevelList',edit = True, si = shortName)


def togglevisLeft():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkState = mc.iconTextButton('visLeft', q = True , image1 = True)
    selListLeft = mc.textScrollList('bevelList', q=True, ai=True)
    if checkState == 'nodeGrapherSoloed.svg':
        mc.iconTextButton('visLeft', e = True , image1 = 'circle.png')
        if selListLeft != None and len(selListLeft) > 0:
            for s in selListLeft:
                longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
                mc.setAttr((longName + '.visibility'), 0)
    else:
        mc.iconTextButton('visLeft', e = True , image1 = 'nodeGrapherSoloed.svg')
        if selListLeft != None and len(selListLeft) > 0:
            for s in selListLeft:
                longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
                mc.setAttr((longName + '.visibility'), 1)

def togglevisRight():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkState = mc.iconTextButton('visRight', q = True , image1 = True)
    selListRight = mc.textScrollList('nonBevelList', q=True, ai=True)
    if checkState == 'nodeGrapherSoloed.svg':
        mc.iconTextButton('visRight', e = True , image1 = 'circle.png')
        if selListRight != None and len(selListRight) > 0:
            for s in selListRight:
                longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
                mc.setAttr((longName + '.visibility'), 0)
    else:
        mc.iconTextButton('visRight', e = True , image1 = 'nodeGrapherSoloed.svg')
        if selListRight != None and len(selListRight) > 0:
            for s in selListRight:
                longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
                mc.setAttr((longName + '.visibility'), 1)


def selBevelList():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selList = mc.textScrollList('bevelList', q=True, si=True)
    mc.textScrollList('nonBevelList',edit = True, da = True)
    longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + selList[0]
    mc.select(longName, r=True)

def selNonBevelList():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selList = mc.textScrollList('nonBevelList', q=True, si=True)
    mc.textScrollList('bevelList',edit = True, da = True)
    longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + selList[0]
    mc.select(longName, r=True)


def visListOn():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selListLeft = mc.textScrollList('bevelList', q=True, ai=True)
    mc.iconTextButton('visLeft', e = True , image1 = 'nodeGrapherSoloed.svg')
    if selListLeft != None and len(selListLeft) > 0:
        for s in selListLeft:
            longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
            mc.setAttr((longName + '.visibility'), 1)

    selListRight = mc.textScrollList('nonBevelList', q=True, ai=True)
    mc.iconTextButton('visRight', e = True , image1 = 'nodeGrapherSoloed.svg')
    if selListRight != None and len(selListRight) > 0:
        for s in selListRight:
            longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
            mc.setAttr((longName + '.visibility'), 1)
    mc.setAttr((beseMesh+'_bakeStep.visibility'),1)


def visListOff():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selListLeft = mc.textScrollList('bevelList', q=True, ai=True)
    mc.iconTextButton('visLeft', e = True , image1 = 'circle.png')
    if selListLeft != None and len(selListLeft) > 0:
        for s in selListLeft:
            longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
            mc.setAttr((longName + '.visibility'), 0)

    selListRight = mc.textScrollList('nonBevelList', q=True, ai=True)
    mc.iconTextButton('visRight', e = True , image1 = 'circle.png')
    if selListRight != None and len(selListRight) > 0:
        for s in selListRight:
            longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + s
            mc.setAttr((longName + '.visibility'), 0)
    mc.setAttr((beseMesh+'_bakeStep.visibility'),1)



def loadBevelList():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    list = mc.ls('bakeCutter*',type='transform',l=True)
    if len(list) > 0:
        cleanList = []
        for l in list:
            if beseMesh in l:
                cleanList.append(l)
        mc.textScrollList('bevelList',edit = True, ra = True)
        mc.textScrollList('nonBevelList',edit = True, ra = True)
        for c in cleanList:
            shortName = c.split('|')[-1]
            checkState = mc.getAttr(c+'.preBevel')
            if checkState == 1:
                mc.textScrollList('bevelList',edit = True, append = shortName)
            else:
                mc.textScrollList('nonBevelList',edit = True, append = shortName)



def publishFinal():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if len(beseMesh) > 0:
        if mc.objExists(beseMesh + '_publishMesh'):
            print ('publishMesh existed!')

        else:
            if mc.objExists(beseMesh + '_preBevelMeshFinal'):
                newNode = mc.duplicate((beseMesh + '_preBevelMeshFinal'),rr = True, un=True)
                mc.rename(newNode[0],(beseMesh + '_publishMesh'))
                mc.parent((beseMesh + '_publishMesh'),w=True)
                mc.DeleteHistory()
                mc.setAttr((beseMesh+ 'BoolGrp.visibility'),0)
            else:
                if mc.objExists(beseMesh + '_preBaseMesh'):
                    newNode = mc.duplicate((beseMesh + '_preBaseMesh'),rr = True, un=True)
                    mc.rename(newNode[0],(beseMesh + '_publishMesh'))
                    mc.parent((beseMesh + '_publishMesh'),w=True)
                    mc.DeleteHistory()
                    mc.setAttr((beseMesh+ 'BoolGrp.visibility'),0)
                else:
                    print ('nothing to publish')


def preCheckBevelByVolumn():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    bbox = mc.xform(beseMesh, q=True, ws=True, bbi=True)
    disX =  math.sqrt((bbox[3] - bbox[0])*(bbox[3] - bbox[0]))
    disY =  math.sqrt((bbox[4] - bbox[1])*(bbox[4] - bbox[1]))
    disZ =  math.sqrt((bbox[5] - bbox[2])*(bbox[5] - bbox[2]))
    baseVolumn = disX * disY *disZ
    guildVolumn = baseVolumn * 0.01 # 5% of base
    #check all cutter
    mc.select((beseMesh+'_bakeStep'), hi=True)
    mc.select((beseMesh+'_bakeStep'),d=True)
    mc.select((beseMesh+'_bakeBaseMesh'),d=True)
    sel = mc.ls(sl=1,fl=1,type='transform',l=True)
    mc.select(cl=True)
    for s in sel:
        checkState = mc.getAttr(s+'.statePanel')# skip if gap or panel
        if not mc.attributeQuery('preBevel', node = s, ex=True ):
            mc.addAttr(s, ln='preBevel', at = "float" )
            mc.setAttr((s+'.preBevel'), 0)
            checkStateBevel = mc.getAttr(s+'.preBevel')# already Made as non bevel
            if checkState == 0 and checkStateBevel == 1 :
                bbox = mc.xform(s, q=True, ws=True, bbi=True)
                disX =  math.sqrt((bbox[3] - bbox[0])*(bbox[3] - bbox[0]))
                disY =  math.sqrt((bbox[4] - bbox[1])*(bbox[4] - bbox[1]))
                disZ =  math.sqrt((bbox[5] - bbox[2])*(bbox[5] - bbox[2]))
                volumn = disX * disY *disZ
                if volumn < guildVolumn:
                    mc.setAttr((s+'.preBevel'), 0)
                else:
                    mc.setAttr((s+'.preBevel'), 1)


def removeNonBevelList():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if len(beseMesh) > 0:
        removeLeftOver()
        mc.setAttr(beseMesh + '_preBevel.visibility',1)
        mc.rename((beseMesh + '_preBevel'),(beseMesh + '_preBaseMesh'))
        list = mc.listHistory((beseMesh + '_preBaseMesh'))
        for l in list:
            nodeTypeA = mc.nodeType(l)
            if nodeTypeA == 'polyBevel3':
                mc.rename(l,(beseMesh+'_edgePreBevel'))
            elif  nodeTypeA == 'polyExtrudeFace':
                mc.rename(l,(beseMesh+'_lcokFace'))
            else:
                pass
        offsetV = mc.floatSliderGrp('offsetSliderPre',q=1, v =True)
        lockV = mc.floatSliderGrp('lockFaceSliderPre',q=1, v =True)
        segV = mc.intSliderGrp('segmentSliderPre',  q=1, v =True)
        miterV = mc.intSliderGrp('miteringSliderPre', q=1,v =True)
        mc.setAttr((beseMesh+'_lcokFace.offset'),lockV)
        mc.setAttr((beseMesh+'_edgePreBevel.segments'), segV)
        mc.setAttr((beseMesh+'_edgePreBevel.mitering'), miterV)
        mc.setAttr((beseMesh+'_edgePreBevel.offset'), offsetV)
        visListOff()
        outlineClean()
        mc.button('addPreBButton',e=True,en=False)
        mc.button('removePreBButton',e=True,en=True)
        mc.button('addPreNonBButton',e=True,en=True)
        mc.button('removePreNonBButton',e=True,en=False)
        mc.floatSliderGrp('lockFaceSliderPre',e=1, en=0)
        mc.floatSliderGrp('offsetSliderPre',e=1, en=1)
        mc.intSliderGrp('segmentSliderPre',e=1, en=1)
        mc.intSliderGrp('miteringSliderPre',e=1, en=1)
        mc.connectControl('segmentSliderPre', (beseMesh+'_edgePreBevel.segments'))
        mc.connectControl('miteringSliderPre',(beseMesh+'_edgePreBevel.mitering'))
        mc.connectControl('offsetSliderPre', (beseMesh+'_edgePreBevel.offset'))
        if mc.objExists(beseMesh + '_preBevelGrp'):
            mc.delete(beseMesh + '_preBevelGrp')
        mc.select((beseMesh + '_preBaseMesh'))

def addNonBevelList():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists(beseMesh + '_boolNonBevelUnion') == 0 or mc.objExists(beseMesh + '_boolNonBevelSubs') == 0 or mc.objExists(beseMesh + '_boolNonBevelCut') == 0:
        if len(beseMesh) > 0:
            boolPreNonBevel()
            visListOff()
            #outlineClean()
            mc.intSliderGrp('segmentSliderPre',e=True,en=True)
            mc.intSliderGrp('miteringSliderPre',e=True,en=True)
            mc.button('addPreBButton',e=True,en=False)
            mc.button('removePreBButton',e=True,en=True)
            mc.button('addPreNonBButton',e=True,en=False)
            mc.button('removePreNonBButton',e=True,en=True)
            mc.button('removeLockButton', e=1, en = 0)
            mc.button('removePreBButton', e=1, en = 0)
            mc.intSliderGrp('segmentSliderPre',e=1, en=0)
            mc.intSliderGrp('miteringSliderPre',e=1, en=0)

def rebuildPreview():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if len(beseMesh) > 0:
        if mc.objExists('*preBevel*'):
            mc.delete('*preBevel*')
        if mc.objExists('*_preBaseMesh*'):
            mc.delete('*_preBaseMesh*')
        if mc.objExists('*boolNon*'):
            mc.delete('*boolNon*')
        mc.setAttr((beseMesh +'BoolGrp.visibility'),1)
        mc.setAttr((beseMesh +'_bool.visibility'),1)
        mc.button('addPreBButton',e=True,en=False)
        mc.button('removePreBButton',e=True,en=False)

def killPreview():
    rebuildPreview()
    restoreCutter()
    mc.button('addPreBButton',e=True,en=False)
    mc.button('removePreBButton',e=True,en=False)
    mc.button('addPreNonBButton',e=True,en=False)
    mc.button('removePreNonBButton',e=True,en=False)
    mc.button('removeLockButton',e=True,en=False)
    mc.button('addLockButton',e=True,en=False)
    mc.button('addCutButton',e=True,en=True)


    #if mc.window("jwSpeedCutBevelManger", exists = True):
    #    mc.deleteUI("jwSpeedCutBevelManger")


def preBevelUpdate():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if len(beseMesh) > 0:
        cutUpdate()
        lcokUpdate()
        addPreBevelEdgeRun()
        addNonBevelList()
        mc.floatSliderGrp('lockFaceSliderPre',e=1, en=1)
        mc.floatSliderGrp('offsetSliderPre', e=True, v = 1, min = 0.001, max = 1, fmx = 10)


def cutUpdate():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    offsetV = mc.floatSliderGrp('offsetSliderPre',q=1, v =True)
    lockV = mc.floatSliderGrp('lockFaceSliderPre',q=1, v =True)
    segV = mc.intSliderGrp('segmentSliderPre',  q=1, v =True)
    miterV = mc.intSliderGrp('miteringSliderPre', q=1,v =True)
    if len(beseMesh) > 0:
        loadBevelList()
        rebuildPreview()
        setPreBevelGrp()
        boolPreBevel()
        visListOff()
        #outlineClean()
        member = beseMesh + '_preBaseMesh'
        mc.select(beseMesh + '_preBaseMesh')
        mc.intSliderGrp('segmentSliderPre',e=True,en=False)
        mc.intSliderGrp('miteringSliderPre',e=True,en=False)
        mc.floatSliderGrp('lockFaceSliderPre',e=True,en=False)
        mc.floatSliderGrp('offsetSliderPre',e=True,en=False)
        mc.button('addLockButton',e=True,en=True)
        #Retop
        mc.polySelectConstraint(m=3,t=0x8000,sm=1)
        mc.polySelectConstraint(disable =True)
        triNode = mc.polyTriangulate(member,ch=0)
        quadNode = mc.polyQuad(member,a = 30, kgb = 0 ,ktb = 0, khe= 1, ws = 0, ch = 0)
        mc.delete(ch = True)
        #Clean
        mc.select(member)
        mergeNode = mc.polyMergeVertex( d = 0.01,ch = True)
        softNode = mc.polySoftEdge(angle=0.3)
        mel.eval("ConvertSelectionToEdges;")
        mc.polySelectConstraint(t=0x8000, m=3, sm=2)
        mc.polySelectConstraint(disable =True)
        selectEdges=mc.ls(sl=1,fl=1)
        if len(selectEdges)>0:
            mc.polyDelEdge(cv = True, ch = False)
        #Clean unused vertex points
        mc.select(member)
        mergeNode = mc.polyMergeVertex( d = 0.01,ch = True)
        mc.select(member)
        mc.ConvertSelectionToVertices()
        selected = mc.ls(sl=1, fl=1)
        mc.select(clear=True)
        for v in selected:
            if len( re.findall('\d+', mc.polyInfo(v,ve=True)[0]) ) == 3:
                mc.select(v,add=True)
        mc.delete(mc.ls(sl=True))
        mc.select(member)
        softNode = mc.polySoftEdge(angle=30)
        #merge very close vertex by user
        mc.select(member)
        mc.delete(ch = True)
        mc.select(member)
        mergeNode = mc.polyMergeVertex( d = 0.01,ch = 0)
        mc.button('removeLockButton', e=1, en = 0)
        mc.select(member)
        mc.button('addLockButton', e=1, en = 1)

def bevelPreviewLockFace():
    global sourceFaces
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    member = beseMesh + '_preBaseMesh'
    mc.select(member)
    mc.polySelectConstraint(m=3,t=0x8000,sm=1)
    mc.polySelectConstraint(disable =True)
    hardEdges = mc.ls(sl=1,fl=1)
    mc.DetachComponent()
    listH = mc.listHistory(member, lv=0 )
    for h in listH:
        checkNode = mc.nodeType(h)
        if checkNode == 'polySplitEdge':
            mc.rename(h,'lockStart')
    mc.select(member)
    mc.ConvertSelectionToFaces()
    sourceFaces = mc.ls(sl=1,fl=1)
    offsetData = mc.floatSliderGrp('offsetSliderPre', q=1, v = 1)
    createSupportNode = mc.polyExtrudeFacet(sourceFaces, constructionHistory =1, keepFacesTogether = 1, divisions = 1, off = offsetData, smoothingAngle = 30)
    faceLockNode = mc.rename(createSupportNode[0], (beseMesh+'_lcokFace'))
    mc.GrowPolygonSelectionRegion()
    shapeExtrude = mc.ls(sl=1,fl=1)
    mc.select(member)
    mc.ConvertSelectionToFaces()
    mc.select(shapeExtrude,d=1 )
    mc.delete()
    mc.select(member)
    mc.polyMergeVertex(d = 0.001, ch = 1)
    mc.setAttr((faceLockNode + ".offset"), offsetData)
    mc.connectControl('lockFaceSliderPre', (faceLockNode + ".offset"))
    mc.setAttr((faceLockNode + ".offset"),0.1)
    mc.polySelectConstraint(m=3,t=0x8000,sm=1)
    mc.polySelectConstraint(disable =True)
    softNode = mc.polySoftEdge(angle= 180)
    mc.rename(softNode,'preSoftEdge')
    mc.select(cl=True)

def mergeHardEdgeVex():# vertices too close
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    member = beseMesh + '_preBaseMesh'
    mc.select(member)
    mc.polySelectConstraint(m=3,t=0x8000,sm=1)
    mc.polySelectConstraint(disable =True)
    mc.ConvertSelectionToVertices()
    mc.polyMergeVertex(d= 0.1,am= 1, ch= 1)

def smoothAroundLockEdge():#relax vertices surround lock edge then snap back to bool mesh to maintain shape
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    snapMesh = beseMesh + '_bool'
    global sourceFaces
    mc.select(sourceFaces)
    mel.eval('InvertSelection')
    mc.ConvertSelectionToVertices()
    tempSel=mc.ls(sl=1,fl=1)
    mc.GrowPolygonSelectionRegion()
    mc.select(tempSel, d=1 )
    mc.polyAverageVertex(i=10)
    mc.polyAverageVertex(i=10)
    mc.select(snapMesh,add=1)
    mc.transferAttributes(transferPositions =1, transferNormals= 0, transferUVs =0, transferColors= 2, sampleSpace = 0, searchMethod = 3, flipUVs = 0, colorBorders =0)
    mc.select(cl=1)

def bevelPreviewLockFaceRemove():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    member = beseMesh + '_preBaseMesh'
    mc.select(member)
    listH = mc.listHistory(member, lv=0 )
    for h in listH:
        checkNode = mc.nodeType(h)
        if checkNode != 'mesh':
            mc.delete(h)
            if 'lockStart' in h:
                break
    mc.button('removeLockButton', e=1, en = 0)
    mc.button('addLockButton', e=1, en = 1)
    mc.button('addPreBButton', e=1, en = 0)
    mc.button('removePreBButton', e=1, en = 0)
    mc.button('addPreNonBButton', e=1, en = 0)
    mc.button('removePreNonBButton', e=1, en = 0)
    mc.connectControl('lockFaceSliderPre', (beseMesh + '_lcokFace.offset'))
    mc.select(member)
    softHardVis()

def lcokUpdate():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    offsetV = mc.floatSliderGrp('offsetSliderPre',q=1, v =True)
    lockV = mc.floatSliderGrp('lockFaceSliderPre',q=1, v =True)
    segV = mc.intSliderGrp('segmentSliderPre',  q=1, v =True)
    miterV = mc.intSliderGrp('miteringSliderPre', q=1,v =True)
    if len(beseMesh) > 0:
        bevelPreviewLockFace()
        mc.setAttr((beseMesh+'_lcokFace.offset'),lockV)
        visListOff()
        outlineClean()
        mc.select(beseMesh + '_preBaseMesh')
        mc.button('addPreBButton',e=True,en=True)
        mc.button('removePreBButton',e=True,en=False)
        mc.button('addPreNonBButton',e=True,en=False)
        mc.button('removePreNonBButton',e=True,en=False)
        mc.button('removeLockButton', e=1, en = 1)
        mc.button('addLockButton', e=1, en = 0)


def addPreBevelEdgeRun():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists(beseMesh +'_edgePreBevel') == 0:
        lockV = mc.floatSliderGrp('lockFaceSliderPre',q=1, v =True)
        addPreBevelEdge()
        visListOff()
        outlineClean()
        mc.button('addPreBButton',e=True,en=False)
        mc.button('removePreBButton',e=True,en=True)
        mc.floatSliderGrp('lockFaceSliderPre',e=True,en=False)
        mc.floatSliderGrp('offsetSliderPre',e=True,en=True , max = lockV)
        mc.button('addPreNonBButton',e=True,en=True)
        mc.button('removePreNonBButton',e=True,en=False)
        mc.button('addLockButton',e=True,en=False)
        mc.setAttr((beseMesh+'_edgePreBevel.offset'),lockV)
        mc.select(beseMesh + '_preBaseMesh')
        mc.TogglePolyDisplayEdges()
        mc.button('removeLockButton',e=1, en=0)


def removePreBevelEdgeRun():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    mc.delete(beseMesh + '_preBaseMesh')
    mc.showHidden(beseMesh + '_preBaseLock')
    mc.rename((beseMesh + '_preBaseLock') ,(beseMesh + '_preBaseMesh'))
    outlineClean()
    mc.button('addPreBButton',e=True,en=True)
    mc.button('removePreBButton',e=True,en=False)
    mc.floatSliderGrp('lockFaceSliderPre',e=True,en=True)
    mc.floatSliderGrp('offsetSliderPre',e=True,en=False)
    mc.button('addPreNonBButton',e=True,en=False)
    mc.button('removePreNonBButton',e=True,en=False)
    mc.button('removeLockButton', e=1, en = 0)
    mc.button('addLockButton', e=1, en = 0)
    mc.button('removeLockButton', e=1, en = 1)
    mc.select(beseMesh + '_preBaseMesh')
    listH = mc.listHistory((beseMesh + '_preBaseMesh'), lv=0 )
    for l in listH:
        checkType=mc.nodeType(l)
        if  checkType == "polyExtrudeFace":
            mc.connectControl('lockFaceSliderPre', (l + ".offset"))


def addPreBevelEdge():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    newGrp = mc.duplicate((beseMesh + '_preBaseMesh'),rr = True, un=True)
    if mc.objExists(beseMesh+'_preBaseLock'):
        mc.delete(beseMesh + '_preBaseLock')
    mc.rename(newGrp,(beseMesh + '_preBaseLock'))
    mc.hide(beseMesh + '_preBaseLock')
    mc.select(beseMesh + '_preBaseMesh')
    mel.eval("ConvertSelectionToEdges;")
    softNode = mc.polySoftEdge(angle=30)
    mc.polySelectConstraint(m=3,t=0x8000,sm=1)
    mc.polySelectConstraint(disable =True)
    hardEdges = mc.ls(sl=1,fl=1)
    bevelNodeNew = mc.polyBevel3(hardEdges, offset = 0.1, offsetAsFraction= 0, autoFit= 1, depth= 1, mitering= 1 ,miterAlong= 0 ,chamfer =1 ,segments= 3 ,worldSpace= 0 ,smoothingAngle= 30 ,subdivideNgons =1 ,mergeVertices= 1, mergeVertexTolerance= 0.0001, miteringAngle=180, angleTolerance =180 ,ch= 1)
    mc.rename(bevelNodeNew,(beseMesh+'_edgePreBevel'))
    mc.connectControl('segmentSliderPre', (beseMesh+'_edgePreBevel.segments'))
    mc.connectControl('miteringSliderPre',(beseMesh+'_edgePreBevel.mitering'))
    mc.connectControl('offsetSliderPre', (beseMesh+'_edgePreBevel.offset'))
    softHardVis()

def outlineClean():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkList = ['_cutterGrp','_preSubBox','_preUnionBox','_preBevelMeshUnion','_preBevelMeshSubs','_myBoolUnion','_bool','_preBaseMeshBackup' ,'_preBevelGrp','_preBaseMesh','_preBaseMeshFinal','_preBevelMeshFinal','_boolNonBevelUnion','_boolNonBevelsubs']
    for c in checkList:
        checkGrp = mc.ls((beseMesh + c), l=True)
        if len(checkGrp)>0:
            if 'BoolGrp' not in checkGrp[0]:
                mc.parent(checkGrp[0],(beseMesh +'BoolGrp'))

def removeLeftOver():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkList = ['_preBevelMeshSubs','_boolNonBevelUnion','_boolNonBevelSubs','_preBevelMeshFinal']
    for c in checkList:
        if mc.objExists(beseMesh + c):
            mc.delete(beseMesh + c)

def boolPreNonBevel():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    preBevelMesh = (beseMesh + '_preBaseMesh')
    newNode = mc.duplicate(preBevelMesh,n=(beseMesh + '_preBaseMeshBackup'),rr=1,un=1)
    mc.setAttr(beseMesh + '_preBaseMeshBackup.visibility',0)
    mc.rename(newNode, (beseMesh + '_preBevel'))
    nonBevelsList = mc.textScrollList('nonBevelList', q=True, ai=True)

    if mc.objExists(beseMesh+'_preBevelGrp') == 0:
        newGrp = mc.duplicate((beseMesh + '_bakeStep'),rr = True, un=True)
        mc.parent(newGrp,w=True)
        mc.rename(beseMesh + '_preBevelGrp')
        mc.select(hi=True)
        #rename
        listCutters = mc.ls(sl=True, type ='transform',l=True)
        for l in listCutters:
            if '_bakeBaseMesh' in l:
                mc.delete(l)
            else:
                sName = l.replace('bake','pre')
                mc.rename(l, sName.split("|")[-1])
        mc.parent((beseMesh + '_preBevelGrp'),(beseMesh + 'BoolGrp'))
        # sort operation type
    subsGrp = []
    unionGrp = []
    cutGrp = []
    for b in nonBevelsList:
        longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + b
        if mc.objExists(longName):
            checkOP = mc.getAttr(longName + '.cutterOp')
            if checkOP == 'subs':
                subsGrp.append(b)
            elif checkOP == 'union':
                unionGrp.append(b)
            elif checkOP == 'cut':
                cutGrp.append(b)

    for s in subsGrp:
        newNode =  '|' +  beseMesh  + 'BoolGrp|' +  beseMesh  + '_preBevelGrp|'+ (s.replace('bake','pre'))
        mc.polyCBoolOp(preBevelMesh, newNode, op=2, ch=1, preserveColor=0, classification=1, name= preBevelMesh)
        mc.DeleteHistory()
        mc.rename(preBevelMesh)
    for u in unionGrp:
        newNode =  '|' +  beseMesh  + 'BoolGrp|' +  beseMesh  + '_preBevelGrp|'+ (u.replace('bake','pre'))
        mc.polyCBoolOp(preBevelMesh, newNode, op=1, ch=1, preserveColor=0, classification=1, name= preBevelMesh)
        mc.DeleteHistory()
        mc.rename(preBevelMesh)
    for c in cutGrp:
        newNode =  '|' +  beseMesh  + 'BoolGrp|' +  beseMesh  + 'BoolGrp|' + beseMesh + '_preBevelGrp|'+ (c.replace('bake','pre'))
        mc.polyCBoolOp(preBevelMesh, newNode, op=2, ch=1, preserveColor=0, classification=1, name= preBevelMesh)
        mc.DeleteHistory()
        mc.rename(preBevelMesh)
    mc.rename(beseMesh + '_preBevelMeshFinal')
    mc.parent((beseMesh + '_preBevelMeshFinal') ,( beseMesh  + 'BoolGrp|'))

def boolPreBevel():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    bevelsList = mc.textScrollList('bevelList', q=True, ai=True)
    mc.parent(('|' +  beseMesh  + 'BoolGrp|'  +  beseMesh  + '_preBevelGrp|' + beseMesh + '_preBaseMesh'),w=True)
    preBevelMesh = (beseMesh + '_preBaseMesh')
    # sort operation type
    subsGrp = []
    unionGrp = []
    cutGrp = []
    for b in bevelsList:
        longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_bakeStep|' + b
        if mc.objExists(longName):
            checkOP = mc.getAttr(longName + '.cutterOp')
            if checkOP == 'subs':
                subsGrp.append(b)
            elif checkOP == 'union':
                unionGrp.append(b)
            elif checkOP == 'cut':
                cutGrp.append(b)

    for s in subsGrp:
        newNode =  '|' +  beseMesh  + 'BoolGrp|'  +  beseMesh  + '_preBevelGrp|'+ (s.replace('bake','pre'))
        mc.polyCBoolOp(preBevelMesh, newNode, op=2, ch=0, preserveColor=0, classification=1, name= preBevelMesh)
        mc.DeleteHistory()
        mc.rename(preBevelMesh)
    for u in unionGrp:
        newNode =  '|' +  beseMesh  + 'BoolGrp|'  +  beseMesh  + '_preBevelGrp|'+ (u.replace('bake','pre'))
        mc.polyCBoolOp(preBevelMesh, newNode, op=1, ch=0, preserveColor=0, classification=1, name= preBevelMesh)
        mc.DeleteHistory()
        mc.rename(preBevelMesh)
    for c in cutGrp:
        newNode =  '|' +  beseMesh  + 'BoolGrp|'  +  beseMesh  + '_preBevelGrp|'+ (c.replace('bake','pre'))
        mc.polyCBoolOp(preBevelMesh, newNode, op=2, ch=0, preserveColor=0, classification=1, name= preBevelMesh)
        mc.DeleteHistory()
        mc.rename(preBevelMesh)
    mc.parent(preBevelMesh,('|' +  beseMesh  + 'BoolGrp|'))
    mc.select(preBevelMesh)
    mel.eval('setSelectMode components Components')
    mc.selectType(smp= 0, sme= 1, smf= 0, smu = 0, pv= 0, pe = 1, pf= 0, puv= 0)
    mc.TogglePolyDisplayHardEdgesColor()

def setPreBevelGrp():
    bakeCutter('All')
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    newGrp = mc.duplicate((beseMesh + '_bakeStep'),rr = True, un=True)
    mc.parent(newGrp,w=True)
    mc.rename(beseMesh + '_preBevelGrp')
    mc.select(hi=True)
    #rename
    listCutters = mc.ls(sl=True, type ='transform',l=True)
    for l in listCutters:
        sName = l.replace('bake','pre')
        mc.rename(l, sName.split("|")[-1])
    #show
    listCutters = mc.ls(sl=True, type ='transform',l=True)
    for l in listCutters:
        mc.setAttr((l + '.visibility'),1)
    mc.setAttr((beseMesh + 'BoolGrp.visibility'),1)
    mc.setAttr((beseMesh + '_bakeStep.visibility'),1)
    mc.setAttr((beseMesh + '_bool.visibility'),0)
    mc.setAttr((beseMesh + '_preBevelGrp.visibility'),1)
    list = mc.ls('preCutter*',type='transform')
    for i in list:
        mc.setAttr((i + '.visibility'),0)
    mc.parent((beseMesh + '_preBevelGrp'),(beseMesh + 'BoolGrp'))

def sortBevelList():
    selListLeft = mc.textScrollList('bevelList', q=True, ai=True)
    if selListLeft != None:
        if len(selListLeft) > 0:
            selListLeft.sort()
            mc.textScrollList('bevelList',edit = True, ra = True)
            for s in selListLeft:
                mc.textScrollList('bevelList',edit = True, append = s)

    selListRight = mc.textScrollList('nonBevelList', q=True, ai=True)
    if selListRight != None:
        if len(selListRight) > 0:
            selListRight.sort()
            mc.textScrollList('nonBevelList',edit = True, ra = True)
            for s in selListRight:
                mc.textScrollList('nonBevelList',edit = True, append = s)



def jwSpeedCutBevelMangerSetup():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if len(beseMesh)>0:
        jwSpeedCutBevelMangerUI()
        bakeCutter('all')
        preCheckBevelByVolumn()
        loadBevelList()
        visListOn()
        mc.button('addPreBButton',e=True,en=False)
        mc.button('removePreBButton',e=True,en=False)
        mc.button('addPreNonBButton',e=True,en=False)
        mc.button('removePreNonBButton',e=True,en=False)

def softHardVis():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkState = mc.iconTextButton('edgeVis' , q = True , image1 = True)
    if mc.objExists((beseMesh + '_preBaseMesh')):
        mc.select(beseMesh + '_preBaseMesh')
        if checkState == 'nodeGrapherSoloed.svg':
            mc.iconTextButton('edgeVis' , e = True , image1 = 'circle.png')
            mc.TogglePolyDisplayEdges()
        else:
            mc.iconTextButton('edgeVis' , e = True , image1 = 'nodeGrapherSoloed.svg')
            mc.TogglePolyDisplayHardEdgesColor()
    #change to edge mode
    mel.eval('setSelectMode components Components')
    mc.selectType(smp= 0, sme= 1, smf= 0, smu = 0, pv= 0, pe = 1, pf= 0, puv= 0)



def jwSpeedCutBevelMangerUI():
    if mc.window("jwSpeedCutBevelManger", exists = True):
        mc.deleteUI("jwSpeedCutBevelManger")
    jwSpeedCutBevelManger = mc.window("jwSpeedCutBevelManger",title = "speedCut Bevel Manger",w = 400,h = 380, mxb = False, s = 1, bgc = [0.2, 0.2, 0.2  ])
    mc.columnLayout()
    mc.rowColumnLayout(nc= 1, cw = [(1, 420)])
    mc.separator( height=15, style='none' )
    mc.setParent( '..' )
    mc.rowColumnLayout(nc= 5, cw = [(1, 20),(2, 200),(3, 40),(4,10),(5, 200)])
    mc.text(l ='')
    mc.menuBarLayout()
    mc.rowColumnLayout(nc= 3, cw = [(1,50),(2,100),(3,20)])
    mc.text(l ='Bevel' ,en=False)
    mc.text(l ='')
    mc.iconTextButton('visLeft' , h = 20, style='iconOnly', image1 = 'nodeGrapherSoloed.svg',  c = 'togglevisLeft()')
    mc.setParent( '..' )
    mc.scrollLayout(h = 320)
    mc.textScrollList('bevelList',  h= 300, w =180, vis = True, ams= True, sc= 'selBevelList()')
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.columnLayout()
    mc.text(l ='',h=150)
    mc.iconTextButton('moveLeft' , w = 30, style='iconOnly', image1 = 'timeplay.png',  c = 'moveRightItem()')
    mc.text(l ='',h=10)
    mc.iconTextButton('moveRight' , w = 30, style='iconOnly', image1 = 'timerev.png',  c = 'moveLeftItem()')
    mc.text(l ='',h=10)
    mc.setParent( '..' )
    mc.text(l ='',h=10)
    mc.menuBarLayout()
    mc.rowColumnLayout(nc= 3, cw = [(1,50),(2,100),(3,20)])
    mc.text(l ='Ignore' ,en=False)
    mc.text(l ='')
    mc.iconTextButton('visRight' , h = 20, style='iconOnly', image1 = 'nodeGrapherSoloed.svg',  c = 'togglevisRight()')
    mc.setParent( '..' )
    mc.scrollLayout(h= 320)
    mc.textScrollList('nonBevelList',  h= 300, w =180, vis = True, ams= True, sc= 'selNonBevelList()')
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.separator( height=1, style='none' )
    mc.rowColumnLayout(nc=2, cw = [(1,215),(2,270)])
    mc.frameLayout(  labelVisible = 0,vis = 1)
    mc.columnLayout()
    mc.rowColumnLayout(nc=6, cw = [(1,55),(2,50),(3,3),(4,50),(5,3),(6,50)])
    mc.text(l ='All')
    mc.button('updatePreBButton', w = 50, l= "Auto",  c = 'preBevelUpdate()',bgc = [0.14, 0.14, 0.14] )
    mc.text(l ='')
    mc.button('killPreBButton', w = 50,   l= "x",  c = 'killPreview()',bgc = [0.14, 0.14, 0.14] )
    mc.text(l ='')
    mc.button('outMeshButton', w = 50,   l= "Output",  c = 'publishFinal()',bgc = [0.14, 0.14, 0.14] )
    mc.setParent( '..' )
    bSize = 76 #button
    sSize = 250#slider
    tSize = 65 #slider Text
    mc.separator( height=5, style='none' )
    mc.rowColumnLayout(nc=6, cw = [(1,55),(2,50),(3,3),(4,50),(5,3),(6,50)])
    mc.text(l ='Mesh ')
    mc.button('addCutButton', w = 50,   l= "Cut",  c = 'cutUpdate()',bgc = [0.14, 0.14, 0.14] )
    mc.text(l ='')
    mc.button('addLockButton', w = 50, en=0,  l= "Lock",  c = 'lcokUpdate()',bgc = [0.14, 0.14, 0.14] )
    mc.text(l ='')
    mc.button('removeLockButton', w = 50, en = 0,  l= "Remove",  c = 'bevelPreviewLockFaceRemove()',bgc = [0.14, 0.14, 0.14] )
    mc.setParent( '..' )
    mc.separator( height=5, style='none' )
    mc.rowColumnLayout(nc=4, cw = [(1,55),(2,bSize),(3,3),(4,bSize)])
    mc.text(l ='Bevel ')
    mc.button('addPreBButton', w = bSize,   l= "Add",  c = 'addPreBevelEdgeRun()',bgc = [0.14, 0.14, 0.14] )
    mc.text(l ='')
    mc.button('removePreBButton', w = bSize,   l= "Remove",  c = 'removePreBevelEdgeRun()',bgc = [0.14, 0.14, 0.14] )
    mc.setParent( '..' )
    mc.separator( height=5, style='none' )
    mc.rowColumnLayout(nc=4, cw = [(1,55),(2,bSize),(3,3),(4,bSize)])
    mc.text(l =' NonBevel')
    mc.button('addPreNonBButton', w = bSize,   l= "Add",  c = 'addNonBevelList()',bgc = [0.14, 0.14, 0.14] )
    mc.text(l ='')
    mc.button('removePreNonBButton', w = bSize,   l= "Remove",  c = 'removeNonBevelList()',bgc = [0.14, 0.14, 0.14] )
    mc.setParent( '..' )
    mc.separator( height=5, style='none' )
    mc.rowColumnLayout(nc=8, cw = [(1,55),(2,20),(3,9),(4,40),(5,3),(6,40),(7,3),(8,40)])
    mc.text(l =' Edge')
    mc.iconTextButton('edgeVis' , h = 20, style='iconOnly', image1 = 'circle.png',  c = 'softHardVis()')
    mc.text(l ='')
    mc.button('selContEdgeButton',  l= "Loop",  c = 'mc.SelectContiguousEdges()',bgc = [0.14, 0.14, 0.14] )
    mc.text(l ='')
    mc.button('edgeHardButton', l= "H",  c = 'mc.PolygonHardenEdge()',bgc = [0.14, 0.14, 0.14] )
    mc.text(l ='')
    mc.button('edgeSoftButton',  l= "S",  c = 'mc.PolygonSoftenEdge()',bgc = [0.14, 0.14, 0.14] )

    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.setParent( '..' )
    mc.frameLayout(  labelVisible = 0,vis = 1)
    mc.floatSliderGrp('lockFaceSliderPre', en=1, v = 0.1, min = 0.001, max = 1, fmx = 5, s = 0.01, cw3 = [tSize,40,sSize] , label = "Lock" ,field =True)
    mc.floatSliderGrp('offsetSliderPre', en=1, v = 0.1, min = 0.001, max = 1, fmx = 10, s = 0.01, cw3 = [tSize,40,sSize] , label = "Offset" ,field =True)
    mc.intSliderGrp('segmentSliderPre',  en=1, v = 2,   min = 1 ,    max = 5, s = 1,    cw3 = [tSize,40,sSize] , label = "Segments" ,field =True)
    mc.intSliderGrp('miteringSliderPre', en=1, v = 1,   min = 0, max = 3,  s = 1, cw3 = [tSize,40,sSize] , label = "Mitering " ,field =True)
    mc.setParent( '..' )
    mc.text(l ='')
    mc.separator( height=15, style='none' )
    mc.showWindow(jwSpeedCutBevelManger)
    obNum = mc.scriptJob ( p = 'jwSpeedCutBevelManger', event = ["SelectionChanged", reselctList])
##################################################################################################################

def baseMeshColorUpdate():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    shapes = mc.listRelatives((beseMesh+'_bool'), shapes=True)
    shadeEng = mc.listConnections(shapes , type = 'shadingEngine')
    if shadeEng:
        colorData ={  2 : (0.25, 0.25 , 0.25),
                      3 : (0.6 , 0.6  , 0.6 ),
                      4 : (0.61, 0    , 0.16),
                      5 : (0.0 , 0.02 , 0.38),
                      6 : (0.0 , 0    , 1   ),
                      7 : (0.0 , 0.28 , 0.1 ),
                      8 : (0.15, 0.0  , 0.26),
                      9 : (0.78, 0.0  , 0.78),
                     10 : (0.54, 0.28 , 0.2 ),
                     11 : (0.25, 0.14 , 0.12),
                     12 : (0.32 , 0.02 , 0.0 ),
                     15 : (0.0 , 0.26 , 0.6 ),
                     20 : (1.0 , 0.43 , 0.43),
                     21 : (0.9 , 0.68 , 0.47),
                     23 : (0.0 , 0.60 , 0.33),
                     24 : (0.63, 0.42 , 0.19),
                     25 : (0.62, 0.63 , 0.19),
                     26 : (0.41, 0.63 , 0.19),
                     27 : (0.19, 0.63 , 0.36),
                     28 : (0.19, 0.63 , 0.63),
                     29 : (0.19, 0.40 , 0.63),
                     30 : (0.44, 0.15 , 0.63),
                     31 : (0.63, 0.19 , 0.42),
                     }
        score = list(colorData.items())

        materials = mc.ls(mc.listConnections(shadeEng ), materials = True)
        if materials[0] == (beseMesh+'_Shader'):
            mc.sets((beseMesh+'_bool'), e=True, forceElement = 'initialShadingGroup')
            if mc.objExists(beseMesh+'_Shader'):
                mc.delete(beseMesh+'_Shader')
            if mc.objExists(beseMesh+'_ShaderSG'):
                mc.delete(beseMesh+'_ShaderSG')
            mc.setAttr((beseMesh + '_BoolResult.color'),0)
            mc.setAttr((beseMesh + "BoolGrp.useOutlinerColor"), 0)
        else:
            if mc.objExists(beseMesh+'_Shader') == 0:
                shd = mc.shadingNode('lambert', name=(beseMesh+'_Shader'), asShader=True)
                shdSG = mc.sets(name=(beseMesh+'_ShaderSG'), empty=True, renderable=True, noSurfaceShader=True)
                mc.connectAttr((shd +'.outColor'), (shdSG +'.surfaceShader'))
            colorID = random.randint(0,(len(score)-1))
            getInfo = score[colorID]

            mc.setAttr ((beseMesh +'_Shader.color'), getInfo[1][0],getInfo[1][1],getInfo[1][2], type = 'double3' )
            mc.sets((beseMesh+'_bool'), e=True, forceElement = (beseMesh+'_ShaderSG'))
            mc.setAttr((beseMesh + '_BoolResult.color'),getInfo[0])


            mc.setAttr((beseMesh + "BoolGrp.useOutlinerColor"), 1)
            mc.setAttr((beseMesh + "BoolGrp.outlinerColor"),  getInfo[1][0],getInfo[1][1],getInfo[1][2])


    else:
        mc.sets((beseMesh+'_bool'), e=True, forceElement = 'initialShadingGroup')
        mc.setAttr((beseMesh + '_BoolResult.color'),0)
        mc.setAttr((beseMesh + "BoolGrp.useOutlinerColor"), 0)




def hsv2rgb(h, s, v):
    h, s, v = [float(x) for x in (h, s, v)]
    hi = (h / 60) % 6
    hi = int(round(hi))
    f = (h / 60) - (h / 60)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    if hi == 0:
        return v, t, p
    elif hi == 1:
        return q, v, p
    elif hi == 2:
        return p, v, t
    elif hi == 3:
        return p, q, v
    elif hi == 4:
        return t, p, v
    elif hi == 5:
        return v, p, q

def toggleLayer():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkState = mc.iconTextButton('meshLayerButton', q=1, image1= True )
    if checkState == 'nodeGrapherModeSimple.svg':
        mc.iconTextButton('meshLayerButton', e=1, image1= 'nodeGrapherModeAll.svg')
        BoolGrpList = mc.ls('*BoolGrp')
        mc.showHidden(BoolGrpList)
    else:
        mc.iconTextButton('meshLayerButton', e=1, image1= 'nodeGrapherModeSimple.svg')
        BoolGrpList = mc.ls('*BoolGrp')
        mc.hide(BoolGrpList)
        mc.showHidden(beseMesh+'BoolGrp')

def updateVisLayer():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkState = mc.iconTextButton('meshLayerButton', q=1, image1= True )
    if checkState == 'nodeGrapherModeSimple.svg':
        BoolGrpList = mc.ls('*BoolGrp')
        mc.hide(BoolGrpList)
        mc.showHidden(beseMesh+'BoolGrp')
    else:
        BoolGrpList = mc.ls('*BoolGrp')
        mc.showHidden(BoolGrpList)


def cutterType(boolType):
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkButtonStateList = ['subsButton','unionButton','cutButton']
    for c in checkButtonStateList:
        buttonState = mc.button( c ,e=1,  bgc = [0.28,0.28,0.28] )
    selCutter = mc.ls(sl=1, fl=1, type='transform')
    if len(selCutter) > 0:
        selCutterCheck = mc.ls(sl=1, fl=1, l=1, type='transform')
        for s in selCutterCheck:
            checkShortName = s.split("|")
            shortName = checkShortName[-1]
            mc.select(s)
            myType = checkInstType()
            if myType[1] != 'new':
                s = myType[0]

            if 'boxCutter' in shortName:
                mc.setAttr((s+'.cutterOp'),boolType,type="string")
                shapeNode = mc.listRelatives(s, f = True, shapes=True)
                if boolType == 'union':
                    mc.setAttr( (shapeNode[0]+'.overrideColor'), 31)
                elif boolType == 'subs':
                    mc.setAttr( (shapeNode[0]+'.overrideColor'), 28)
                elif boolType == 'cut':
                    mc.setAttr( (shapeNode[0]+'.overrideColor'), 25)
                fixBoolNodeConnection()

    if boolType == 'union':
        buttonState = mc.button('unionButton',e=1,  bgc = [0.3,0.5,0.6] )
    elif boolType == 'subs':
        buttonState = mc.button('subsButton' ,e=1,  bgc = [0.3,0.5,0.6] )
    elif boolType == 'cut':
        buttonState = mc.button('cutButton' ,e=1,  bgc = [0.3,0.5,0.6] )

def fixBoolNodeConnection():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    transNode = mc.ls(sl=1,fl=1)
    myType = checkInstType()
    if myType[1] != 'new':
        transNode[0] = myType[0]

    checkNumber = ''.join([n for n in transNode[0].split('|')[-1] if n.isdigit()])
    opType = mc.getAttr(transNode[0]+'.cutterOp')
    shapeNode = mc.listRelatives(transNode[0], s=True ,f=True)
    boolNode = ''

    if 'subs' in opType:
        boolNode = beseMesh+'_mySubs'

    elif 'union' in opType:
        boolNode = beseMesh+'_myUnion'

    elif 'cut' in opType:
        boolNode = beseMesh+'_myCut'

    if len(shapeNode)>0:
        listConnect = mc.connectionInfo((shapeNode[0]+'.outMesh'), dfs=True )
        if len(listConnect)>0:
            for a in listConnect:
                mc.disconnectAttr((shapeNode[0]+'.outMesh'), a)


    start_index = 0
    while start_index < 1000:
        listConnectMa = mc.connectionInfo((shapeNode[0]+'.worldMatrix[' + str(start_index) + ']'), dfs=True )
        if len(listConnectMa) > 0:
            for a in listConnectMa:
                try:
                    mc.disconnectAttr((shapeNode[0]+'.worldMatrix[' + str(start_index) + ']'), a)
                except:
                    pass
        start_index += 1


    mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode+'.inputPoly['+str(checkNumber)+']')),f=True)
    mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((boolNode+'.inputMat['+str(checkNumber)+']')),f=True)

    if myType[1] != 'new':
        mc.select(transNode[0]+'*Grp')
        grpName = mc.ls(sl=True,fl=True)
        transformList = mc.listRelatives(grpName, c=True)
        cleanList = []
        if  myType[1] == 'radial':
            for t in transformList:
                removeUnwant = t.replace('_Rot','')
                cleanList.append(removeUnwant)
        else:
            cleanList = transformList

        cleanList.remove(transNode[0])

        for i in range(len(cleanList)):
            checkNumber = ''.join([n for n in cleanList[i].split('|')[-1] if n.isdigit()])
            mc.connectAttr( (shapeNode[0]+".worldMatrix[" + str(int(i)+ int(1)) + "]"), ((boolNode+'.inputMat['+str(checkNumber)+']')),f=True)
            mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode+'.inputPoly['+str(checkNumber)+']')),f=True)

def get_latest_free_multi_index( attr_name, start_index ):
    '''Find the latest unconnected multi index starting at the passed in index.'''
    listCuttersIndex = []
    while start_index < 100:
        if mc.connectionInfo( '{}[{}]'.format(attr_name,start_index), sfd=True ):
            listCuttersIndex.append(start_index)
        start_index += 1
    nextIndex = (listCuttersIndex[-1]+1)
    return nextIndex


def nextCutterNumber():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    cutterGrpName = beseMesh + '_cutterGrp'
    mc.select(cutterGrpName,hi=True)
    listAllCutter = mc.ls('boxCutter*',type = 'transform')
    mc.select(cl=True)
    checkNumber = 2
    if len(listAllCutter) > 0:
        newList = []
        for l in listAllCutter:
            if 'ArrayGrp' not in l:
                newList.append(l)
            else:
                grpNumber = ''.join([n for n in l.split('|')[-1] if n.isdigit()])
                newList.append(grpNumber)
        checkNumber = ''.join([n for n in newList[-1].split('|')[-1] if n.isdigit()])
        checkNumber = int(checkNumber) + 1
    return checkNumber

def get_latest_free_multi_index( attr_name, start_index ):
    '''Find the latest unconnected multi index starting at the passed in index.'''
    listCuttersIndex = []
    while start_index < 100:
        if mc.connectionInfo( '{}[{}]'.format(attr_name,start_index), sfd=True ):
            listCuttersIndex.append(start_index)
        start_index += 1
    nextIndex = (listCuttersIndex[-1]+1)
    return nextIndex

def get_next_free_multi_index( attr_name, start_index ):
    '''Find the next unconnected multi index starting at the passed in index.'''
    # assume a max of 100 connections
    while start_index < 100:
        if len( mc.connectionInfo( '{}[{}]'.format(attr_name,start_index), sfd=True ) or [] ) == 0:
            return start_index
        start_index += 1
    return 0

#################################################################################################
def goDraw():
    hideAllCutter()
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    snapMesh = beseMesh + '_bool'
    mc.optionVar(iv = ('inViewMessageEnable', 0))
    mc.makeLive(snapMesh)
    xrayOn()
    mc.evalDeferred('drawBoxRun()')


def drawBoxRun():
    mc.setToolTo( "CreatePolyCubeCtx" )
    mc.scriptJob ( runOnce=True, event = ["PostToolChanged", xrayOff])


def xrayOn():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    snapMesh = beseMesh + '_bool'
    mc.displaySurface(snapMesh , x =1)

def xrayOff():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    snapMesh = beseMesh + '_bool'
    mc.displaySurface(snapMesh , x =0)
    mc.makeLive( none=True )
    newCut = mc.ls(sl=1,tr=1)
    mc.select(newCut, r=1)
    mc.evalDeferred('useOwnCutterShape()')
    newCut = mc.ls(sl=1,tr=1)
    mc.setAttr((newCut[0]+".scaleX") ,1.01)
    mc.setAttr((newCut[0]+".scaleY") ,1.01)
    mc.setAttr((newCut[0]+".scaleZ") ,1.01)

#####################################################################################################

def rdMirrorCurrentState():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    rdMAxis = ''
    rdMPol = ''
    divSide = 3
    divOffset = 10
    bcv = mc.button('rMirrorXButton',q=1, bgc =1)
    totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
    if totalBcVX < 0.27:
        rdMAxis = 'x'
    bcv = mc.button('rMirrorYButton',q=1, bgc =1)
    totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
    if totalBcVX < 0.27:
        rdMAxis = 'y'
    bcv = mc.button('rMirrorZButton',q=1, bgc =1)
    totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
    if totalBcVX < 0.27:
        rdMAxis = 'z'
    checkV = mc.button('rMirrorPosButton', q=1 , bgc = 1)
    if checkV[0] > 0.30 :
        rdMPol = 'p'
    checkV = mc.button('rMirrorNegButton', q=1 , bgc = 1)
    if checkV[0] > 0.30 :
        rdMPol = 'n'
    divSide = mc.intSliderGrp('rMirrorSideSlider',  q=1 , v = 1)
    divOffset = mc.intSliderGrp('rMirrorOffsetSlider',  q=1 , v = 1)
    return rdMAxis, rdMPol, divSide, divOffset

def rdMirrorUIUpdate():
    answer = ['','','','']
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists((beseMesh + "_rMirrorGrp")):
        answer[0]= mc.getAttr(beseMesh + '_rMirrorGrp.rdMAxis')
        answer[1]= mc.getAttr(beseMesh + '_rMirrorGrp.rdMHalf')
        answer[2]= mc.getAttr(beseMesh + '_rMirrorGrp.rdMSide')
        answer[3]= mc.getAttr(beseMesh + '_rMirrorGrp.rdMOffset')
        rdMirrorReset()
        if answer[0] == 'x':
            mc.button('rMirrorXButton',e=1, bgc =  [0.34, 0.14, 0.14])
        elif answer[0] == 'y':
            mc.button('rMirrorYButton',e=1, bgc =  [0.14, 0.34, 0.14])
        elif answer[0] == 'z':
            mc.button('rMirrorZButton',e=1, bgc =  [0.14, 0.14, 0.34])
        if answer[1] == 'p':
            mc.button('rMirrorPosButton', e=1 , bgc = [0.3, 0.5, 0.6])
        elif answer[1] == 'n':
            mc.button('rMirrorNegButton', e=1 , bgc = [0.3, 0.5, 0.6])
        mc.intSliderGrp('rMirrorSideSlider',  e=1 , v = answer[2] )
        mc.intSliderGrp('rMirrorOffsetSlider',  e=1 , v = answer[3] )
    else:
        rdMirrorReset()

def rdMirrorReset():
    mc.button('rMirrorXButton',e=1, bgc = [0.28,0.28,0.28])
    mc.button('rMirrorYButton',e=1, bgc = [0.28,0.28,0.28])
    mc.button('rMirrorZButton',e=1, bgc = [0.28,0.28,0.28])
    mc.button('rMirrorNegButton', e=1 , bgc = [0.28,0.28,0.28])
    mc.button('rMirrorPosButton', e=1 , bgc = [0.28,0.28,0.28])
    mc.intSliderGrp('rMirrorSideSlider',  e=1 , v = 3)

def rdMirrorOffsetUpdate():
    rMirrorList = mc.ls('*_rMirrorGrp')
    offsetV = mc.intSliderGrp('rMirrorOffsetSlider',q=1,v=1)
    for r in rMirrorList:
        mc.move((-1.0*offsetV), 0, 0 ,r , a=1, os=1, wd=1)
        mc.setAttr((r + '.rdMOffset'),offsetV)

def rdMirrorOutput():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists((beseMesh + "_rMirrorGrp")):
        insList = mc.ls((beseMesh + "_ringGrp*"),fl=1)
        mc.select(beseMesh + "_ringGrp")
        collectList = []
        for i in insList:
            new = mc.duplicate((beseMesh + "_ringGrp"),rr=1)
            collectList.append(new)
            mc.select(new,i)
            mc.matchTransform(pos=1,rot=1)
        mc.delete(insList)
        mc.select(beseMesh + "_rMirrorGrp")
        mc.polyUnite(ch=0, objectPivot=1)
        mc.rename(beseMesh + "_rMirrorGeo")
        mc.delete(beseMesh + "_rMirrorGrp")
        mc.polyMergeVertex(d=0.01, am=1, ch=0)
        mc.select(beseMesh + "_rMirrorGeo")
        mc.button('rMirrorPosButton', e=1 ,bgc = [0.28,0.28,0.28])
        mc.button('rMirrorNegButton', e=1 ,bgc = [0.28,0.28,0.28])
        mc.button('rMirrorXButton',e=1, bgc = [0.28,0.28,0.28])
        mc.button('rMirrorYButton',e=1, bgc = [0.28,0.28,0.28])
        mc.button('rMirrorZButton',e=1, bgc = [0.28,0.28,0.28])
        mc.intSliderGrp('rMirrorSideSlider',  e=1 , v = 3)

def rdMirrorHalf(side):
    buttonXOn = 1
    buttonYOn = 1
    buttonZOn = 1
    bcv = mc.button('rMirrorXButton',q=1, bgc =1)
    totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
    if totalBcVX > 0.27:
        buttonXOn = 0

    bcv = mc.button('rMirrorYButton',q=1, bgc =1)
    totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
    if totalBcVX > 0.27:
        buttonYOn = 0

    bcv = mc.button('rMirrorZButton',q=1, bgc =1)
    totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
    if totalBcVX > 0.27:
        buttonZOn = 0
    if buttonXOn == 0 and buttonYOn == 0 and buttonZOn == 0:
        if mc.objExists((beseMesh + "_rMirrorGrp")):
            mc.delete((beseMesh + "_rMirrorGrp"))
    else:
        if side == 'p':
            checkV = mc.button('rMirrorPosButton', q=1 , bgc = 1)
            if checkV[0] < 0.30 :
                mc.button('rMirrorPosButton', e=1 , bgc = [0.3, 0.5, 0.6])
            else:
                mc.button('rMirrorPosButton', e=1 , bgc = [0.28,0.28,0.28])
            mc.button('rMirrorNegButton', e=1 , bgc = [0.28,0.28,0.28])
        elif side == 'n':
            checkV = mc.button('rMirrorNegButton', q=1 , bgc = 1)
            if checkV[0] < 0.30 :
                mc.button('rMirrorNegButton', e=1 , bgc = [0.3, 0.5, 0.6])
            else:
                mc.button('rMirrorNegButton', e=1 , bgc = [0.28,0.28,0.28])
            mc.button('rMirrorPosButton', e=1 , bgc = [0.28,0.28,0.28])
        rdMirrorUpdate()

def rdMirror(axis):
    currentSel = mc.ls(sl=1)
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if len(beseMesh) > 0:
        divSide =  mc.intSliderGrp('rMirrorSideSlider',  q=1 , v = 1)
        divAngle = 360.0 /  divSide
        commnadA = ''
        commnadC = ''
        commnadD = ''
        commnadG = ''
        rotV = 90 - (360.0 / divSide / 2)
        createMirror = 1
        halfOn = 0
        checkVP = mc.button('rMirrorPosButton', q=1 , bgc = 1)
        checkVN = mc.button('rMirrorNegButton', q=1 , bgc = 1)
        if (checkVP[1]+ checkVN[1]) > 0.57:
            halfOn = 1

        buttonXOn = 1
        buttonYOn = 1
        buttonZOn = 1
        bcv = mc.button('rMirrorXButton',q=1, bgc =1)
        totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
        if totalBcVX > 0.27:
            buttonXOn = 0

        bcv = mc.button('rMirrorYButton',q=1, bgc =1)
        totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
        if totalBcVX > 0.27:
            buttonYOn = 0

        bcv = mc.button('rMirrorZButton',q=1, bgc =1)
        totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
        if totalBcVX > 0.27:
            buttonZOn = 0
        if buttonXOn == 0 and buttonYOn == 0 and buttonZOn == 0:
            if mc.objExists((beseMesh + "_rMirrorGrp")):
                mc.delete((beseMesh + "_rMirrorGrp"))

        if axis == 'x':
            if buttonXOn == 1:
                if mc.objExists((beseMesh + "_rMirrorGrp")):
                    mc.delete((beseMesh + "_rMirrorGrp"))
                mc.button('rMirrorXButton',e=1, bgc = [0.28,0.28,0.28])
                createMirror = 0
            else:
                if buttonYOn == 1 or buttonZOn == 1:
                    if mc.objExists((beseMesh + "_rMirrorGrp")):
                        mc.delete((beseMesh + "_rMirrorGrp"))
                commnadA = 'polyMirrorCut 0.001 0 1;'
                commnadC = 'rotate -r  ' + str(divAngle) +  ' 0 0;'

                if halfOn == 1:
                    if checkVP[1] > 0.30:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(90) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(rotV) + ');'
                    else:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(rotV) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(90) + ');'

                else:
                    commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(rotV) + ');'
                    commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(rotV) + ');'
                mc.button('rMirrorXButton',e=1, bgc = [0.34, 0.14, 0.14])
                mc.button('rMirrorYButton',e=1, bgc = [0.28,0.28,0.28])
                mc.button('rMirrorZButton',e=1, bgc = [0.28,0.28,0.28])

        elif axis == 'y':
            if buttonYOn == 1:
                if mc.objExists((beseMesh + "_rMirrorGrp")):
                    mc.delete((beseMesh + "_rMirrorGrp"))
                mc.button('rMirrorYButton',e=1, bgc = [0.28,0.28,0.28])
                createMirror = 0
            else:
                if buttonXOn == 1 or buttonZOn == 1:
                    if mc.objExists((beseMesh + "_rMirrorGrp")):
                        mc.delete((beseMesh + "_rMirrorGrp"))
                commnadA = 'polyMirrorCut 0 0.001 1;'
                commnadC = 'rotate -r  0 ' + str(divAngle) +  ' 0;'
                if halfOn == 1:
                    if checkVP[1] > 0.30:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateY (' + str(90) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateY (-1.0 * ' + str(rotV) + ');'
                    else:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateY (' + str(rotV) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateY (-1.0 * ' + str(90) + ');'
                else:
                    commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateY (' + str(rotV) + ');'
                    commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateY (-1.0 * ' + str(rotV) + ');'
                mc.button('rMirrorXButton',e=1, bgc = [0.28,0.28,0.28])
                mc.button('rMirrorYButton',e=1, bgc = [0.14, 0.34, 0.14])
                mc.button('rMirrorZButton',e=1, bgc = [0.28,0.28,0.28])
        else:
            if buttonZOn == 1:
                if mc.objExists((beseMesh + "_rMirrorGrp")):
                    mc.delete((beseMesh + "_rMirrorGrp"))
                mc.button('rMirrorZButton',e=1, bgc = [0.28,0.28,0.28])
                createMirror = 0
            else:
                if buttonXOn == 1 or buttonYOn == 1:
                    if mc.objExists((beseMesh + "_rMirrorGrp")):
                        mc.delete((beseMesh + "_rMirrorGrp"))

                commnadA = 'polyMirrorCut 1 0 0.001;'
                commnadC = 'rotate -r 0 0 ' + str(divAngle) +  ';'

                if halfOn == 1:

                    if checkVP[1] > 0.30:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(90) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(rotV) + ');'
                    else:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(rotV) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(90) + ');'
                else:
                    commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(rotV) + ');'
                    commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(rotV) + ');'
                mc.button('rMirrorXButton',e=1, bgc = [0.28,0.28,0.28])
                mc.button('rMirrorYButton',e=1, bgc = [0.28,0.28,0.28])
                mc.button('rMirrorZButton',e=1, bgc = [0.14, 0.14, 0.34])

        if createMirror == 1:
            rmSource = beseMesh+ '_bool'
            newRing = mc.duplicate(rmSource)
            mc.rename(newRing , (beseMesh + '_ringGeo'))
            mc.connectAttr( (rmSource+'Shape.outMesh') ,(beseMesh + '_ringGeoShape.inMesh'),f=1)
            mc.select(beseMesh + '_ringGeo')
            mel.eval(commnadA)
            mc.rename(beseMesh + '_cutPlaneA')
            mc.select((beseMesh + '_ringGeo'),add=1)
            mc.matchTransform(pos=1)
            list = mc.listConnections((beseMesh + '_cutPlaneA'),t= "transform")
            mc.delete(list[0])
            mel.eval(commnadD)
            mc.select(beseMesh + '_ringGeo')
            mel.eval(commnadA)
            mc.rename(beseMesh + '_cutPlaneB')
            mc.select((beseMesh + '_ringGeo'),add=1)
            mc.matchTransform(pos=1)
            mel.eval(commnadG)
            list = mc.listConnections((beseMesh + '_cutPlaneB'),t= "transform")

            if halfOn == 1:
                mc.rename(list[0], (beseMesh + '_ringGeoMirror'))
                mc.group((beseMesh + '_ringGeo'),(beseMesh + '_ringGeoMirror'))
            else:
                mc.delete(list[0])
                mc.group((beseMesh + '_ringGeo'))
            mc.rename(beseMesh + '_ringGrp')
            getTrans = mc.xform((beseMesh + '_cutPlaneA'), q=1, piv=1, a=1, ws=1)
            mc.move(getTrans[0], getTrans[1], getTrans[2],(beseMesh + '_ringGrp.scalePivot'), (beseMesh + '_ringGrp.rotatePivot'), a=1, ws=1)
            mc.instance()
            mel.eval(commnadC)
            for i in range(divSide-2):
                mc.instance(st=1)
            mc.group((beseMesh + '_cutPlane*'),(beseMesh + '_ringGrp*'))
            mc.rename(beseMesh + "_rMirrorGrp")
            offsetV = mc.intSliderGrp('rMirrorOffsetSlider',q=1,v=1)
            mc.move((-1.0*offsetV), 0, 0 ,r=1, os=1, wd=1)
            mc.setAttr((beseMesh + '_cutPlaneA.visibility'),0)
            mc.setAttr((beseMesh + '_cutPlaneB.visibility'),0)
            mc.parent((beseMesh + "_rMirrorGrp"),(beseMesh + "BoolGrp"))
            mc.select(d=1)
            if not mc.attributeQuery('rdMAxis', node = (beseMesh + '_rMirrorGrp'), ex=True ):
                mc.addAttr((beseMesh + '_rMirrorGrp'), ln='rdMAxis' ,dt= 'string')
            if not mc.attributeQuery('rdMHalf', node = (beseMesh + '_rMirrorGrp'), ex=True ):
                mc.addAttr((beseMesh + '_rMirrorGrp'), ln='rdMHalf' ,dt= 'string')
            if not mc.attributeQuery('rdMSide', node = (beseMesh + '_rMirrorGrp'), ex=True ):
                mc.addAttr((beseMesh + '_rMirrorGrp'),at='long' , dv = 0 ,ln='rdMSide')
            if not mc.attributeQuery('rdMOffset', node = (beseMesh + '_rMirrorGrp'), ex=True ):
                mc.addAttr((beseMesh + '_rMirrorGrp'),at='long' , dv = 0 ,ln='rdMOffset')
            answer = rdMirrorCurrentState()
            mc.setAttr((beseMesh + '_rMirrorGrp.rdMAxis'), answer[0], type="string")
            mc.setAttr((beseMesh + '_rMirrorGrp.rdMHalf'), answer[1], type="string")
            mc.setAttr((beseMesh + '_rMirrorGrp.rdMSide'), answer[2])
            mc.setAttr((beseMesh + '_rMirrorGrp.rdMOffset'), answer[3])
        else:
            rdMirrorReset()
        if currentSel:
            mc.select(currentSel)
            mc.MoveTool()

def rdMirrorUpdate():
    currentSel = mc.ls(sl=1)
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if len(beseMesh) > 0:
        if mc.objExists((beseMesh + "_rMirrorGrp")):
            divSide =  mc.intSliderGrp('rMirrorSideSlider',  q=1 , v = 1)
            divAngle = 360.0 /  divSide
            commnadA = ''
            commnadC = ''
            commnadD = ''
            commnadG = ''
            rotV = 90 - (360.0 / divSide / 2)
            createMirror = 1
            halfOn = 0
            checkVP = mc.button('rMirrorPosButton', q=1 , bgc = 1)
            checkVN = mc.button('rMirrorNegButton', q=1 , bgc = 1)
            if (checkVP[1]+ checkVN[1]) > 0.57:
                halfOn = 1
            buttonXOn = 1
            buttonYOn = 1
            buttonZOn = 1
            bcv = mc.button('rMirrorXButton',q=1, bgc =1)
            totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
            if totalBcVX > 0.27:
                buttonXOn = 0
            bcv = mc.button('rMirrorYButton',q=1, bgc =1)
            totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
            if totalBcVX > 0.27:
                buttonYOn = 0
            bcv = mc.button('rMirrorZButton',q=1, bgc =1)
            totalBcVX = (bcv[0]+ bcv[1]+ bcv[2])/3
            if totalBcVX > 0.27:
                buttonZOn = 0
            if buttonXOn == 1 or buttonYOn == 1 or buttonZOn == 1:
                if mc.objExists((beseMesh + "_rMirrorGrp")):
                    mc.delete((beseMesh + "_rMirrorGrp"))
            if buttonXOn == 1:
                commnadA = 'polyMirrorCut 0.001 0 1;'
                commnadC = 'rotate -r  ' + str(divAngle) +  ' 0 0;'
                if halfOn == 1:
                    if checkVP[1] > 0.30:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(90) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(rotV) + ');'
                    else:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(rotV) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(90) + ');'
                else:
                    commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(rotV) + ');'
                    commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(rotV) + ');'
            elif buttonYOn == 1:
                commnadA = 'polyMirrorCut 0 0.001 1;'
                commnadC = 'rotate -r  0 ' + str(divAngle) +  ' 0;'
                if halfOn == 1:
                    if checkVP[1] > 0.30:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateY (' + str(90) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateY (-1.0 * ' + str(rotV) + ');'
                    else:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateY (' + str(rotV) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateY (-1.0 * ' + str(90) + ');'
                else:
                    commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateY (' + str(rotV) + ');'
                    commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateY (-1.0 * ' + str(rotV) + ');'

            elif buttonZOn == 1:
                commnadA = 'polyMirrorCut 1 0 0.001;'
                commnadC = 'rotate -r 0 0 ' + str(divAngle) +  ';'
                if halfOn == 1:
                    if checkVP[1] > 0.30:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(90) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(rotV) + ');'
                    else:
                        commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(rotV) + ');'
                        commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(90) + ');'
                else:
                    commnadD = 'setAttr '  + beseMesh + '_cutPlaneA.rotateX (-1.0 * ' + str(rotV) + ');'
                    commnadG = 'setAttr '  + beseMesh + '_cutPlaneB.rotateX (' + str(rotV) + ');'


            if createMirror == 1:
                rmSource = beseMesh+ '_bool'
                newRing = mc.duplicate(rmSource)
                mc.rename(newRing , (beseMesh + '_ringGeo'))
                mc.connectAttr( (rmSource+'Shape.outMesh') ,(beseMesh + '_ringGeoShape.inMesh'),f=1)
                mc.select(beseMesh + '_ringGeo')
                mel.eval(commnadA)
                mc.rename(beseMesh + '_cutPlaneA')
                mc.select((beseMesh + '_ringGeo'),add=1)
                mc.matchTransform(pos=1)
                list = mc.listConnections((beseMesh + '_cutPlaneA'),t= "transform")
                mc.delete(list[0])
                mel.eval(commnadD)
                mc.select(beseMesh + '_ringGeo')
                mel.eval(commnadA)
                mc.rename(beseMesh + '_cutPlaneB')
                mc.select((beseMesh + '_ringGeo'),add=1)
                mc.matchTransform(pos=1)
                mel.eval(commnadG)
                list = mc.listConnections((beseMesh + '_cutPlaneB'),t= "transform")

                if halfOn == 1:
                    mc.rename(list[0], (beseMesh + '_ringGeoMirror'))
                    mc.group((beseMesh + '_ringGeo'),(beseMesh + '_ringGeoMirror'))
                else:
                    mc.delete(list[0])
                    mc.group((beseMesh + '_ringGeo'))
                mc.rename(beseMesh + '_ringGrp')
                getTrans = mc.xform((beseMesh + '_cutPlaneA'), q=1, piv=1, a=1, ws=1)
                mc.move(getTrans[0], getTrans[1], getTrans[2],(beseMesh + '_ringGrp.scalePivot'), (beseMesh + '_ringGrp.rotatePivot'), a=1, ws=1)
                mc.instance()
                mel.eval(commnadC)
                for i in range(divSide-2):
                    mc.instance(st=1)
                mc.group((beseMesh + '_cutPlane*'),(beseMesh + '_ringGrp*'))
                mc.rename(beseMesh + "_rMirrorGrp")
                offsetV = mc.intSliderGrp('rMirrorOffsetSlider',q=1,v=1)
                mc.move((-1.0*offsetV), 0, 0 ,r=1, os=1, wd=1)
                mc.setAttr((beseMesh + '_cutPlaneA.visibility'),0)
                mc.setAttr((beseMesh + '_cutPlaneB.visibility'),0)
                mc.parent((beseMesh + "_rMirrorGrp"),(beseMesh + "BoolGrp"))
                mc.select(d=1)
                if not mc.attributeQuery('rdMAxis', node = (beseMesh + '_rMirrorGrp'), ex=True ):
                    mc.addAttr((beseMesh + '_rMirrorGrp'), ln='rdMAxis' ,dt= 'string')
                if not mc.attributeQuery('rdMHalf', node = (beseMesh + '_rMirrorGrp'), ex=True ):
                    mc.addAttr((beseMesh + '_rMirrorGrp'), ln='rdMHalf' ,dt= 'string')
                if not mc.attributeQuery('rdMSide', node = (beseMesh + '_rMirrorGrp'), ex=True ):
                    mc.addAttr((beseMesh + '_rMirrorGrp'),at='long' , dv = 0 ,ln='rdMSide')
                if not mc.attributeQuery('rdMOffset', node = (beseMesh + '_rMirrorGrp'), ex=True ):
                    mc.addAttr((beseMesh + '_rMirrorGrp'),at='long' , dv = 0 ,ln='rdMOffset')
                answer = rdMirrorCurrentState()
                mc.setAttr((beseMesh + '_rMirrorGrp.rdMAxis'), answer[0], type="string")
                mc.setAttr((beseMesh + '_rMirrorGrp.rdMHalf'), answer[1], type="string")
                mc.setAttr((beseMesh + '_rMirrorGrp.rdMSide'), answer[2])
                mc.setAttr((beseMesh + '_rMirrorGrp.rdMOffset'), answer[3])
            else:
                rdMirrorReset()

            if currentSel:
                mc.select(currentSel)
                mc.MoveTool()

#####################################################################################################
def symmetryCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    getSymX = 0
    getSymY = 0
    getSymZ = 0

    mc.setAttr((beseMesh+'.visibility'), 1)
    mirrorPivot = mc.objectCenter(beseMesh, gl=True)
    mc.setAttr((beseMesh+'.visibility'), 0)

    if mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        getSymX =  mc.getAttr(beseMesh+'.symmetryX')
    if mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        getSymY =  mc.getAttr(beseMesh+'.symmetryY')
    if mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        getSymZ =  mc.getAttr(beseMesh+'.symmetryZ')

    if getSymX != 0 or getSymY != 0 or getSymZ != 0:
        #mirror all cutter
        mc.select((beseMesh+'_bakeStep'), hi=True)
        mc.select((beseMesh+'_bakeStep'),d=True)
        mc.select((beseMesh+'_bakeBaseMesh'),d=True)
        restoreCutter = mc.ls(sl=1,fl=1,type='transform')
        for r in restoreCutter:
            if getSymX == 1:
                mc.polyMirrorFace(r, cutMesh = 1, axis = 0 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1,  ws =1, p = mirrorPivot)
            elif  getSymX == -1:
                mc.polyMirrorFace(r, cutMesh = 1, axis = 0 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =1, p = mirrorPivot)

            if getSymY == 1:
                mc.polyMirrorFace(r, cutMesh = 1, axis = 1 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1,  ws =1, p = mirrorPivot)
            elif  getSymY == -1:
                mc.polyMirrorFace(r, cutMesh = 1, axis = 1 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =1, p = mirrorPivot)

            if getSymZ == 1:
                mc.polyMirrorFace(r, cutMesh = 1, axis = 2 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1,  ws =1, p = mirrorPivot)
            elif  getSymZ == -1:
                mc.polyMirrorFace(r, cutMesh = 1, axis = 2 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1,  ws =1, p = mirrorPivot)

def fadeOutCage():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists(beseMesh+'_cageGrp'):
        mc.setAttr((beseMesh+'_cageGrp.visibility'),1)
        storeCurrent = mc.floatSlider('CageTransparentSlider',q=1 ,value=True)
        val = storeCurrent
        i = 0.005
        while val < 1:
            i += 0.005
            val = 0.5 + i
            mc.setAttr("CageShader.transparencyB", val)
            mc.setAttr("CageShader.transparencyR", val)
            mc.setAttr("CageShader.transparencyG", val)
            mc.refresh(cv=True,f=True)

        mc.setAttr((beseMesh+'_cageGrp.visibility'),0)
        mc.setAttr("CageShader.transparencyB", storeCurrent)
        mc.setAttr("CageShader.transparencyR", storeCurrent)
        mc.setAttr("CageShader.transparencyG", storeCurrent)

def updateCageColor():
    if mc.objExists('CageShader'):
        checkColor = mc.colorSliderGrp('CageColorSlider', q=True, rgb=True )
        mc.setAttr('CageShader.color', checkColor[0], checkColor[1], checkColor[2] , type= 'double3')

def updateCageTransparent():
    if mc.objExists('CageShader'):
        checkTransp = 0
        checkTransp = mc.floatSlider('CageTransparentSlider',q=True, value=True)
        mc.setAttr('CageShader.transparency', checkTransp, checkTransp, checkTransp, type= 'double3')

def cageVisToggle():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    listAllCageGrps = mc.ls('*_cageGrp')
    if mc.objExists(beseMesh+'_cageGrp'):
        checkState = mc.getAttr(beseMesh+'_cageGrp.visibility')
        mc.hide(listAllCageGrps)
        if checkState == 0:
            mc.setAttr((beseMesh+'_cageGrp.visibility'),1)
        else:
            mc.setAttr((beseMesh+'_cageGrp.visibility'),0)
    else:
        mc.hide(listAllCageGrps)

def boolSymmetryCage():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists(beseMesh +'_cageGrp'):
        mc.delete(beseMesh +'_cageGrp')
    if mc.objExists(beseMesh +'_cageA*'):
        mc.delete(beseMesh +'_cageA*')
    tempLattice = mc.lattice(beseMesh,divisions =(2, 2, 2), objectCentered = True, ldv = (2, 2 ,2))
    BBcenter = mc.xform(tempLattice[1],q =True, t=True)
    BBrotate = mc.xform(tempLattice[1],q =True, ro=True)
    BBscale  = mc.xform(tempLattice[1],q =True, r=True, s=True)
    BBcube = mc.polyCube(w =1, h =1, d =1, sx= 1, sy= 1, sz= 1, ax= (0, 1, 0), ch = 0)
    mc.xform(BBcube[0], t = (BBcenter[0], BBcenter[1],BBcenter[2]))
    mc.xform(BBcube[0], ro = (BBrotate[0], BBrotate[1],BBrotate[2]))
    mc.xform(BBcube[0], s = (BBscale[0], BBscale[1],BBscale[2]))
    mc.delete(tempLattice)
    mc.rename(BBcube[0],(beseMesh+'_cageA'))
    mc.setAttr((beseMesh+'.visibility'), 1)
    mirrorPivot = mc.objectCenter(beseMesh, gl=True)
    mc.setAttr((beseMesh+'.visibility'), 0)
    cutDir = {'X','Y','Z'}
    for c in cutDir:
        cutPlane= mc.polyCut((beseMesh + '_cageA'), ws = True, cd = c , df = True , ch =True)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), mirrorPivot[0])
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), mirrorPivot[1])
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), mirrorPivot[2])
    mc.DeleteHistory(beseMesh + '_cageA')
    mc.move(mirrorPivot[0],mirrorPivot[1],mirrorPivot[2], (beseMesh + '_cageA.scalePivot'),(beseMesh + '_cageA.rotatePivot'), absolute=True)
    mc.makeIdentity((beseMesh + '_cageA'),apply= True, t= 1, r =1, s =1, n= 0,pn=1)
    mc.setAttr((beseMesh + '_cageA.scaleX'), 1.01)
    mc.setAttr((beseMesh + '_cageA.scaleY'), 1.01)
    mc.setAttr((beseMesh + '_cageA.scaleZ'), 1.01)
    mc.setAttr((beseMesh + '_cageA.visibility'), 0)
    mc.setAttr((beseMesh + '_cageAShape.castsShadows'), 0)
    mc.setAttr((beseMesh + '_cageAShape.receiveShadows'), 0)
    mc.makeIdentity((beseMesh + '_cageA'),apply= True, t= 1, r =1, s =1, n= 0,pn=1)
    if not mc.objExists('CageShader'):
        lambertNode = mc.shadingNode("lambert", asShader=1)
        mc.rename(lambertNode,('CageShader'))
        sgNode = mc.sets(renderable=1, noSurfaceShader=1, empty=1, name= 'CageShaderSG')
        mc.connectAttr('CageShader.color', sgNode+".surfaceShader",f=1)
        mc.connectControl( 'CageColorSlider', 'CageShader.color')
        mc.colorSliderGrp('CageColorSlider', e=True, rgb=(0.5, 0, 0))
    cageColor = mc.colorSliderGrp('CageColorSlider', q=True, rgb=True)
    cageTrans = mc.floatSlider('CageTransparentSlider', q=True, value = True)
    mc.setAttr('CageShader.transparency', cageTrans,cageTrans,cageTrans, type= 'double3')
    mc.setAttr('CageShader.color',  cageColor[0],cageColor[1],cageColor[2], type= 'double3')
    mc.sets((beseMesh +'_cageA'), e=1, fe= 'CageShaderSG')
    mc.modelEditor('modelPanel4', e=True, udm=False )
    mc.CreateEmptyGroup()
    mc.rename((beseMesh +'_cageGrp'))
    mc.parent((beseMesh +'_cageA'), (beseMesh +'_cageGrp'))
    mc.parent((beseMesh +'_cageGrp'), (beseMesh +'BoolGrp'))
    if not mc.objExists('BoolSymmetryCage'):
        mc.createDisplayLayer(name = ('BoolSymmetryCage'))
    mc.editDisplayLayerMembers( ('BoolSymmetryCage'),(beseMesh +'_cageGrp'))
    mc.setAttr(('BoolSymmetryCage.displayType'),2)

    newNode = mc.duplicate((beseMesh + '_cageA'),rr=True)
    mc.setAttr((newNode[0]+'.scaleX'), -1)
    newNode = mc.duplicate((beseMesh + '_cageA'),rr=True)
    mc.setAttr((newNode[0]+'.scaleY'), -1)
    newNode = mc.duplicate((beseMesh + '_cageA'),rr=True)
    mc.setAttr((newNode[0]+'.scaleZ'), -1)
    newNode = mc.duplicate((beseMesh + '_cageA'),rr=True)
    mc.setAttr((newNode[0]+'.scaleX'), -1)
    mc.setAttr((newNode[0]+'.scaleY'), -1)
    newNode = mc.duplicate((beseMesh + '_cageA'),rr=True)
    mc.setAttr((newNode[0]+'.scaleX'), -1)
    mc.setAttr((newNode[0]+'.scaleZ'), -1)
    newNode = mc.duplicate((beseMesh + '_cageA'),rr=True)
    mc.setAttr((newNode[0]+'.scaleY'), -1)
    mc.setAttr((newNode[0]+'.scaleZ'), -1)
    newNode = mc.duplicate((beseMesh + '_cageA'),rr=True)
    mc.setAttr((newNode[0]+'.scaleX'), -1)
    mc.setAttr((newNode[0]+'.scaleY'), -1)
    mc.setAttr((newNode[0]+'.scaleZ'), -1)


    if mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        getSymX =  mc.getAttr(beseMesh+'.symmetryX')
    if mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        getSymY =  mc.getAttr(beseMesh+'.symmetryY')
    if mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        getSymZ =  mc.getAttr(beseMesh+'.symmetryZ')

    if getSymX != 0 or getSymY != 0 or getSymZ != 0:
        cageList = mc.ls((beseMesh + '_cageA*'),type='transform')

        if getSymX == 1:
            for c in cageList:
                checkX = mc.getAttr(c+'.scaleX')
                if checkX == -1:
                    mc.setAttr((c+'.visibility'),1)


        elif getSymX == -1:
            for c in cageList:
                checkX = mc.getAttr(c+'.scaleX')
                if checkX == 1:
                    mc.setAttr((c+'.visibility'),1)


        if getSymY == 1:
            for c in cageList:
                checkY = mc.getAttr(c+'.scaleY')
                if checkY == -1:
                    mc.setAttr((c+'.visibility'),1)


        elif getSymY == -1:
            for c in cageList:
                checkY = mc.getAttr(c+'.scaleY')
                if checkY == 1:
                    mc.setAttr((c+'.visibility'),1)

        if getSymZ == 1:
            for c in cageList:
                checkY = mc.getAttr(c+'.scaleZ')
                if checkY == -1:
                    mc.setAttr((c+'.visibility'),1)


        elif getSymZ == -1:
            for c in cageList:
                checkY = mc.getAttr(c+'.scaleZ')
                if checkY == 1:
                    mc.setAttr((c+'.visibility'),1)
    mc.select(cl=True)

def boolSymmetryReset():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    symmNode = mc.listConnections(mc.listHistory((beseMesh+'_bool'),af=1),type='polyMirror')
    if symmNode != None :
        if len(symmNode)>0:
            mc.delete(symmNode)

    resetBoolSymmetryUI()
    if mc.objExists(beseMesh +'_cageGrp'):
        mc.delete(beseMesh +'_cageGrp')


def resetBoolSymmetryUI():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)

    if not mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryX', at = "long" )
    mc.setAttr((beseMesh+'.symmetryX'),0)
    if not mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryY', at = "long" )
    mc.setAttr((beseMesh+'.symmetryY'),0)
    if not mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryZ', at = "long" )
    mc.setAttr((beseMesh+'.symmetryZ'),0)
    mc.button('symmXButtonP',e=True, bgc = [0.14, 0.14, 0.14])
    mc.button('symmYButtonP',e=True, bgc = [0.14, 0.14, 0.14])
    mc.button('symmZButtonP',e=True, bgc = [0.14, 0.14, 0.14])
    mc.button('symmXButtonN',e=True, bgc = [0.14, 0.14, 0.14])
    mc.button('symmYButtonN',e=True, bgc = [0.14, 0.14, 0.14])
    mc.button('symmZButtonN',e=True, bgc = [0.14, 0.14, 0.14])


def boolSymmetryFreeze():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    symmNode = mc.listConnections(mc.listHistory((beseMesh+'_bool'),af=1),type='polyMirror')
    if symmNode != None  and len(symmNode)>0:
        bakeCutter('all')
        symmetryCutter()
        symmetryBase()
        mc.select(cl=True)
        restoreCutter()
        resetBoolSymmetryUI()
        if mc.objExists(beseMesh +'_cageGrp'):
            mc.delete(beseMesh +'_cageGrp')

def symmetryBase():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    getSymX = 0
    getSymY = 0
    getSymZ = 0

    mc.setAttr((beseMesh+'.visibility'), 1)
    mirrorPivot = mc.objectCenter(beseMesh, gl=True)
    mc.setAttr((beseMesh+'.visibility'), 0)


    if mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        getSymX =  mc.getAttr(beseMesh+'.symmetryX')
    if mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        getSymY =  mc.getAttr(beseMesh+'.symmetryY')
    if mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        getSymZ =  mc.getAttr(beseMesh+'.symmetryZ')

    if getSymX != 0 or getSymY != 0 or getSymZ != 0:
        if getSymX == 1:
            mc.polyMirrorFace(beseMesh, cutMesh = 1, axis = 0 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1,  ws =1, p = mirrorPivot)
        elif  getSymX == -1:
            mc.polyMirrorFace(beseMesh, cutMesh = 1, axis = 0 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =1, p = mirrorPivot)

        if getSymY == 1:
            mc.polyMirrorFace(beseMesh, cutMesh = 1, axis = 1 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1,  ws =1, p = mirrorPivot)
        elif  getSymY == -1:
            mc.polyMirrorFace(beseMesh, cutMesh = 1, axis = 1 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =1, p = mirrorPivot)

        if getSymZ == 1:
            mc.polyMirrorFace(beseMesh, cutMesh = 1, axis = 2 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1,  ws =1, p = mirrorPivot)
        elif  getSymZ == -1:
            mc.polyMirrorFace(beseMesh, cutMesh = 1, axis = 2 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1,  ws =1, p = mirrorPivot)
        mc.DeleteHistory()

def boolSymmetry(axis,dir):
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selPoly = beseMesh+'_bool'

    if not mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryX', at = "long" )
        mc.setAttr((beseMesh+'.symmetryX'),0)
    if not mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryY', at = "long" )
        mc.setAttr((beseMesh+'.symmetryY'),0)
    if not mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryZ', at = "long" )
        mc.setAttr((beseMesh+'.symmetryZ'),0)

    mc.setAttr((beseMesh+'.visibility'), 1)
    mirrorPivot = mc.objectCenter(beseMesh, gl=True)
    mc.setAttr((beseMesh+'.visibility'), 0)


    mirrorName = []
    checkSymm = 0
    symmNode = mc.listConnections(mc.listHistory((selPoly),af=1),type='polyMirror')
    if axis == 'x' :
        checkDirState=[]
        if symmNode != None:
            for s in symmNode:
                if 'symmetryX' in s:
                    checkSymm = 1
                    checkDirState = s
        if checkSymm == 0:
            if dir == 1:
                mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 0 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                mc.setAttr((beseMesh+'.symmetryX'),1)
                mc.button('symmXButtonP',e=True, bgc = [0.34, 0.14, 0.14])
                mc.rename(mirrorName[0],(beseMesh + '_symmetryXP'))
            else:
                mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 0 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                mc.setAttr((beseMesh+'.symmetryX'),-1)
                mc.button('symmXButtonN',e=True, bgc = [0.34, 0.14, 0.14])
                mc.rename(mirrorName[0],(beseMesh + '_symmetryXN'))
        else:
            if mc.objExists((beseMesh +'_symmetryXP')):
                mc.delete(beseMesh + '_symmetryXP')
            if mc.objExists((beseMesh +'_symmetryXN')):
                mc.delete(beseMesh + '_symmetryXN')
            mc.button('symmXButtonP',e=True, bgc = [0.28,0.28,0.28])
            mc.button('symmXButtonN',e=True, bgc = [0.28,0.28,0.28])
            if dir == 1:
                if checkDirState == (beseMesh + '_symmetryXP'):# same button press, remove it
                    mc.setAttr((beseMesh+'.symmetryX'),0)
                else:
                    mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 0 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                    mc.setAttr((beseMesh+'.symmetryX'),1)
                    mc.button('symmXButtonP',e=True, bgc = [0.34, 0.14, 0.14])
                    mc.rename(mirrorName[0],(beseMesh + '_symmetryXP'))
            else:
                if checkDirState == (beseMesh + '_symmetryXN'):# same button press, remove it
                    mc.setAttr((beseMesh+'.symmetryX'),0)
                else:
                    mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 0 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                    mc.setAttr((beseMesh+'.symmetryX'),-1)
                    mc.button('symmXButtonN',e=True, bgc = [0.34, 0.14, 0.14])
                    mc.rename(mirrorName[0],(beseMesh + '_symmetryXN'))




    elif axis == 'y' :
        checkDirState=[]
        if symmNode != None:
            for s in symmNode:
                if 'symmetryY' in s:
                    checkSymm = 1
                    checkDirState = s
        if checkSymm == 0:
            if dir == 1:
                mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 1 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                mc.setAttr((beseMesh+'.symmetryY'),1)
                mc.button('symmYButtonP',e=True, bgc = [0.14, 0.34, 0.14])
                mc.rename(mirrorName[0],(beseMesh + '_symmetryYP'))
            else:
                mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 1 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                mc.setAttr((beseMesh+'.symmetryY'),-1)
                mc.button('symmYButtonN',e=True, bgc = [0.14, 0.34, 0.14])
                mc.rename(mirrorName[0],(beseMesh + '_symmetryYN'))


        else:
            if mc.objExists((beseMesh +'_symmetryYP')):
                mc.delete(beseMesh + '_symmetryYP')
            if mc.objExists((beseMesh +'_symmetryYN')):
                mc.delete(beseMesh + '_symmetryYN')
            mc.button('symmYButtonP',e=True, bgc = [0.28,0.28,0.28])
            mc.button('symmYButtonN',e=True, bgc = [0.28,0.28,0.28])
            if dir == 1:
                if checkDirState == (beseMesh + '_symmetryYP'):# same button press, remove it
                    mc.setAttr((beseMesh+'.symmetryY'),0)
                else:
                    mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 1 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                    mc.setAttr((beseMesh+'.symmetryY'),1)
                    mc.button('symmYButtonP',e=True, bgc = [0.14, 0.34, 0.14])
                    mc.rename(mirrorName[0],(beseMesh + '_symmetryYP'))
            else:
                if checkDirState == (beseMesh + '_symmetryYN'):# same button press, remove it
                    mc.setAttr((beseMesh+'.symmetryY'),0)
                else:
                    mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 1 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                    mc.setAttr((beseMesh+'.symmetryY'),-1)
                    mc.button('symmYButtonN',e=True, bgc = [0.14, 0.34, 0.14])
                    mc.rename(mirrorName[0],(beseMesh + '_symmetryYN'))


    else:
        checkDirState=[]
        if symmNode != None:
            for s in symmNode:
                if 'symmetryZ' in s:
                    checkSymm = 1
                    checkDirState = s
        if checkSymm == 0:
            if dir == 1:
                mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 2 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                mc.setAttr((beseMesh+'.symmetryZ'),1)
                mc.button('symmZButtonP',e=True, bgc = [0.14, 0.14, 0.34])
                mc.rename(mirrorName[0],(beseMesh + '_symmetryZP'))
            else:
                mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 2 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                mc.setAttr((beseMesh+'.symmetryZ'),-1)
                mc.button('symmZButtonN',e=True, bgc = [0.14, 0.14, 0.34])
                mc.rename(mirrorName[0],(beseMesh + '_symmetryZN'))

        else:
            if mc.objExists((beseMesh +'_symmetryZP')):
                mc.delete(beseMesh + '_symmetryZP')
            if mc.objExists((beseMesh +'_symmetryZN')):
                mc.delete(beseMesh + '_symmetryZN')
            mc.button('symmZButtonP',e=True, bgc = [0.28,0.28,0.28])
            mc.button('symmZButtonN',e=True, bgc = [0.28,0.28,0.28])
            if dir == 1:
                if checkDirState == (beseMesh + '_symmetryZP'):# same button press, remove it
                    mc.setAttr((beseMesh+'.symmetryZ'),0)
                else:
                    mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 2 , axisDirection = 1 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                    mc.setAttr((beseMesh+'.symmetryZ'),1)
                    mc.button('symmZButtonP',e=True, bgc = [0.14, 0.14, 0.34])
                    mc.rename(mirrorName[0],(beseMesh + '_symmetryZP'))
            else:
                if checkDirState == (beseMesh + '_symmetryZN'):# same button press, remove it
                    mc.setAttr((beseMesh+'.symmetryZ'),0)
                else:
                    mirrorName = mc.polyMirrorFace(selPoly, cutMesh = 1, axis = 2 , axisDirection = 0 , mergeMode = 1 , mergeThresholdType = 0 , mergeThreshold = 0.001 , mirrorAxis = 2, mirrorPosition= 0, smoothingAngle = 30, flipUVs = 0, ch=1, ws =True, p = mirrorPivot)
                    mc.setAttr((beseMesh+'.symmetryZ'),-1)
                    mc.button('symmZButtonN',e=True, bgc = [0.14, 0.14, 0.34])
                    mc.rename(mirrorName[0],(beseMesh + '_symmetryZN'))


    boolSymmetryCage()

def loadSymmetryState():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    symmNode = mc.listConnections(mc.listHistory((beseMesh+'_bool'),af=1),type='polyMirror')
    mc.button('symmXButtonP',e=True, bgc = [0.28, 0.28, 0.28])
    mc.button('symmYButtonP',e=True, bgc = [0.28, 0.28, 0.28])
    mc.button('symmZButtonP',e=True, bgc = [0.28, 0.28, 0.28])
    mc.button('symmXButtonN',e=True, bgc = [0.28, 0.28, 0.28])
    mc.button('symmYButtonN',e=True, bgc = [0.28, 0.28, 0.28])
    mc.button('symmZButtonN',e=True, bgc = [0.28, 0.28, 0.28])

    checkState = 0
    if symmNode != None:
        for s in symmNode:
            if 'symmetryXP' in s :
                mc.button('symmXButtonP',e=True, bgc = [0.34, 0.14, 0.14])
                checkState = 1
            elif  'symmetryXN' in s :
                mc.button('symmXButtonN',e=True, bgc = [0.34, 0.14, 0.14])
                checkState = 1
            elif  'symmetryYP' in s :
                mc.button('symmYButtonP',e=True, bgc = [0.14, 0.34, 0.14])
                checkState = 1
            elif  'symmetryYN' in s :
                mc.button('symmYButtonN',e=True, bgc = [0.14, 0.34, 0.14])
                checkState = 1
            elif  'symmetryZP' in s :
                mc.button('symmZButtonP',e=True, bgc = [0.14, 0.14, 0.34])
                checkState = 1
            elif  'symmetryZN' in s :
                mc.button('symmZButtonN',e=True, bgc = [0.14, 0.14, 0.34])
                checkState = 1


def screenRes():
    windowUnder = mc.getPanel(withFocus=True)
    if 'modelPanel' not in windowUnder:
        windowUnder = 'modelPanel4'
    viewNow = omui.M3dView()
    omui.M3dView.getM3dViewFromModelEditor(windowUnder, viewNow)
    screenW = omui.M3dView.portWidth(viewNow)
    screenH = omui.M3dView.portHeight(viewNow)
    return screenW,screenH

def worldSpaceToImageSpace(cameraName, worldPoint):
    resWidth,resHeight = screenRes()
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

def evenObjLineUp(dir):
    lineupList = mc.ls(sl=1,fl=1)
    #collect 2d posision
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()
    cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
    dataX = {}
    dataY = {}
    for l in lineupList:
        bbox = mc.xform(l, q=True, ws=True, piv=True)
        pos2D = worldSpaceToImageSpace(cameraTrans[0],(bbox[0],bbox[1],bbox[2]))
        dataX.update( {l : pos2D[0]} )
        dataY.update( {l : pos2D[1]} )

    if dir == 'x' :
        score = OrderedDict(sorted(dataX.items(), key = lambda fd: fd[1],reverse = False))
    else:
        score = OrderedDict(sorted(dataY.items(), key = lambda fd: fd[1],reverse = False))

    #use fd[0] to get name order, fd[1] to get key order
    orderList = []
    for key in score:
        orderList.append(key)
    # get distanceGap
    posStart = mc.xform(orderList[0], q=True, ws=True, piv=True)
    posEnd = mc.xform(orderList[-1], q=True, ws=True, piv=True)
    gapX = (posEnd[0] - posStart[0]) / (len(orderList) - 1)
    gapY = (posEnd[1] - posStart[1]) / (len(orderList) - 1)
    gapZ = (posEnd[2] - posStart[2]) / (len(orderList) - 1)


    rotStartX = mc.getAttr(orderList[0]+'.rotateX')
    rotStartY = mc.getAttr(orderList[0]+'.rotateY')
    rotStartZ = mc.getAttr(orderList[0]+'.rotateZ')
    rotEndX = mc.getAttr(orderList[-1]+'.rotateX')
    rotEndY = mc.getAttr(orderList[-1]+'.rotateY')
    rotEndZ = mc.getAttr(orderList[-1]+'.rotateZ')

    rotX = (rotEndX - rotStartX) /   (len(orderList) - 1)
    rotY = (rotEndY - rotStartY) /   (len(orderList) - 1)
    rotZ = (rotEndZ - rotStartZ) /   (len(orderList) - 1)



    for i in range(1,(len(orderList)-1)):
        mc.move( (posStart[0] + (i *gapX)) , (posStart[1] + (i *gapY)), (posStart[2] + (i *gapZ)), orderList[i], rpr = True ,absolute=True )
        mc.setAttr( (orderList[i] + '.rotateX'), ((i *rotX)+ rotStartX) )
        mc.setAttr( (orderList[i] + '.rotateY'), ((i *rotY)+ rotStartY) )
        mc.setAttr( (orderList[i] + '.rotateZ'), ((i *rotZ)+ rotStartZ) )


def borderAlginBBoxDivUpdate():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if not mc.objExists(beseMesh +'_borderBox'):
        borderAlginBBoxCreate()
    checkDiv =  mc.intSliderGrp('bboxDivSlider', q=True, v = True)
    mc.setAttr((beseMesh + '_bbox.subdivisionsDepth') , checkDiv)
    mc.setAttr((beseMesh + '_bbox.subdivisionsWidth') , checkDiv)
    mc.setAttr((beseMesh + '_bbox.subdivisionsHeight'), checkDiv)

def borderAlginBBoxCreate():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selStore = mc.ls(sl=True,fl=True)
    checkDiv =  mc.intSliderGrp('bboxDivSlider', q=True, v = True)
    if not mc.objExists(beseMesh +'_borderBoxGrp') and not mc.objExists(beseMesh +'_borderBox'):
        tempLattice = mc.lattice(beseMesh,divisions =(2, 2, 2), objectCentered = True, ldv = (2, 2 ,2))
        BBcenter = mc.xform(tempLattice[1],q =True, t=True)
        BBrotate = mc.xform(tempLattice[1],q =True, ro=True)
        BBscale  = mc.xform(tempLattice[1],q =True, r=True, s=True)
        BBcube = mc.polyCube(w =1, h =1, d =1, sx= checkDiv, sy= checkDiv, sz= checkDiv, ax= (0, 1, 0), ch = 1)
        mc.rename(BBcube[0],(beseMesh+'_borderBox'))
        mc.rename(BBcube[1],(beseMesh+'_bbox'))

        mc.xform((beseMesh+'_borderBox'), t = (BBcenter[0], BBcenter[1],BBcenter[2]))
        mc.xform((beseMesh+'_borderBox'), ro = (BBrotate[0], BBrotate[1],BBrotate[2]))
        mc.xform((beseMesh+'_borderBox'), s = (BBscale[0], BBscale[1],BBscale[2]))
        mc.delete(tempLattice)

        mc.group()
        mc.rename(beseMesh+'_borderBoxGrp')
        mc.parent((beseMesh+'_borderBoxGrp'), (beseMesh+'BoolGrp'))
        if not mc.objExists('BorderBox'):
            mc.createDisplayLayer(name = ('BorderBox'))
        mc.editDisplayLayerMembers( ('BorderBox'),(beseMesh+'_borderBoxGrp'))
        mc.setAttr(('BorderBox.displayType'),1)
    mc.select(selStore)

def borderAlginBBoxToggle():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selStore = mc.ls(sl=True,fl=True)
    if not mc.objExists(beseMesh +'_borderBoxGrp') and not mc.objExists(beseMesh +'_borderBox'):
        borderAlginBBoxCreate()
        mc.button('borderAlginButton',e=True, bgc =  [0.3,0.5,0.6])
        mc.makeLive(  beseMesh +'_borderBox' )
        mc.manipMoveContext('Move',e=True, snapLivePoint= True)
    else:
        mc.delete(beseMesh +'_borderBoxGrp')
        mc.button('borderAlginButton',e=True, bgc =  [0.28,0.28,0.28])
        mc.makeLive( none=True )
        mc.manipMoveContext('Move',e=True, snapLivePoint= False)
    mc.select(selStore)

def toggleAxisButton(dir):
    if dir == "X":
        checkStateX = mc.button('toggleAxisX', q=True , bgc =True )
        if (checkStateX[0] < 0.285):
            mc.button('toggleAxisX', e=True , bgc = [.3, 0, 0] )
            mc.button('toggleAxisXYZ', e=True ,bgc = [0.28,0.28,0.28]  )
        else:
             mc.button('toggleAxisX', e=True ,bgc = [0.28,0.28,0.28]  )
    if dir == "Y":
        checkStateY = mc.button('toggleAxisY', q=True , bgc =True )
        if (checkStateY[1] < 0.285):
            mc.button('toggleAxisY', e=True , bgc = [0, 0.3, 0] )
            mc.button('toggleAxisXYZ', e=True ,bgc = [0.28,0.28,0.28]  )
        else:
             mc.button('toggleAxisY', e=True ,bgc = [0.28,0.28,0.28]  )
    if dir == "Z":
        checkStateZ = mc.button('toggleAxisZ', q=True , bgc =True )
        if (checkStateZ[2] < 0.285):
            mc.button('toggleAxisZ', e=True , bgc = [0, 0, 0.3] )
            mc.button('toggleAxisXYZ', e=True ,bgc = [0.28,0.28,0.28]  )
        else:
             mc.button('toggleAxisZ', e=True ,bgc = [0.28,0.28,0.28]  )

    if dir == "XYZ":
        checkState = mc.button('toggleAxisXYZ', q=True , bgc =True )
        if (checkState[0] < 0.285):
            mc.button('toggleAxisXYZ', e=True , bgc = [0.3, 0.5, 0.6] )
            mc.button('toggleAxisX', e=True ,bgc = [0.28,0.28,0.28]  )
            mc.button('toggleAxisY', e=True ,bgc = [0.28,0.28,0.28]  )
            mc.button('toggleAxisZ', e=True ,bgc = [0.28,0.28,0.28]  )

        else:
             mc.button('toggleAxisXYZ', e=True ,bgc = [0.28,0.28,0.28]  )
             mc.button('toggleAxisX', e=True , bgc = [.3, 0, 0] )

    checkStateX = mc.button('toggleAxisX', q=True , bgc =True )
    checkStateY = mc.button('toggleAxisY', q=True , bgc =True )
    checkStateZ = mc.button('toggleAxisZ', q=True , bgc =True )
    if (checkStateX[0] < 0.285) and (checkStateY[1] < 0.285) and (checkStateZ[2] < 0.285):
        mc.button('toggleAxisXYZ', e=True , bgc = [0.3, 0.5, 0.6] )
    elif (checkStateX[0] > 0.285) and (checkStateY[1] > 0.285) and (checkStateZ[2] > 0.285):
        mc.button('toggleAxisXYZ', e=True , bgc = [0.3, 0.5, 0.6] )
        mc.button('toggleAxisX', e=True ,bgc = [0.28,0.28,0.28]  )
        mc.button('toggleAxisY', e=True ,bgc = [0.28,0.28,0.28]  )
        mc.button('toggleAxisZ', e=True ,bgc = [0.28,0.28,0.28]  )


def alignSelCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    cutterList = mc.ls(type='transform',os=1)
    if len(cutterList) == 2:
        currentX = mc.getAttr(cutterList[0]+'.translateX')
        currentY = mc.getAttr(cutterList[0]+'.translateY')
        currentZ = mc.getAttr(cutterList[0]+'.translateZ')
        mc.select(cutterList[0],cutterList[1],r=True)
        mc.MatchTranslation()
        checkState = mc.button('toggleAxisXYZ', q=True , bgc =True )
        if checkState[0] < 0.285:
            checkStateX = mc.button('toggleAxisX', q=True , bgc =True )
            if checkStateX[0] <0.285:
                mc.setAttr((cutterList[0]+'.translateX'),currentX)

            checkStateY = mc.button('toggleAxisY', q=True , bgc =True )
            if checkStateY[1] <0.285:
                mc.setAttr((cutterList[0]+'.translateY'),currentY)
            checkStateZ = mc.button('toggleAxisZ', q=True , bgc =True )
            if checkStateZ[2] <0.285:
                mc.setAttr((cutterList[0]+'.translateZ'),currentZ)
    mc.select(cutterList[0])

def alignLastCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selCutter = mc.ls(sl=1,fl=1)
    mc.select(beseMesh+'_cutterGrp')
    mc.select(hi=True)
    mc.select((beseMesh+'_cutterGrp'),d=True)
    mc.select(selCutter,d=True)
    cutterList = mc.ls(sl=1,fl=1,type='transform')
    if len(cutterList) > 0:
        lastCutter = cutterList[-1]
        for s in selCutter:
            currentX = mc.getAttr(s+'.translateX')
            currentY = mc.getAttr(s+'.translateY')
            currentZ = mc.getAttr(s+'.translateZ')
            mc.select(s,lastCutter,r=True)
            mc.MatchTranslation()
            checkState = mc.button('toggleAxisXYZ', q=True , bgc =True )
            if checkState[0] < 0.285:
                checkStateX = mc.button('toggleAxisX', q=True , bgc =True )
                if checkStateX[0] <0.285:
                    mc.setAttr((s+'.translateX'),currentX)

                checkStateY = mc.button('toggleAxisY', q=True , bgc =True )
                if checkStateY[1] <0.285:
                    mc.setAttr((s+'.translateY'),currentY)
                checkStateZ = mc.button('toggleAxisZ', q=True , bgc =True )
                if checkStateZ[2] <0.285:
                    mc.setAttr((s+'.translateZ'),currentZ)
    mc.select(selCutter)

def alignCutterToBase():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selCutters = mc.ls(sl=True,fl=True)
    if len(selCutters) > 0:
        if mc.objExists('tempSnap'):
            mc.delete('tempSnap')
        if mc.objExists(beseMesh+'_borderBox') == 0:
            borderAlginBBoxToggle()

        borderBox = beseMesh + '_borderBox'
        cvNo = mc.polyEvaluate(borderBox, v=True )

        for s in selCutters:
            checkMinDistance = 10000000
            cutterPosition = mc.xform(s, q =True, sp=True,ws=True)
            closetestPos = [0,0,0]
            currentX = mc.getAttr(s+'.translateX')
            currentY = mc.getAttr(s+'.translateY')
            currentZ = mc.getAttr(s+'.translateZ')
            for i in range(cvNo):
                cvBboxPosition = mc.pointPosition(borderBox+'.vtx[' + str(i) + ']',w=1)
                checkDistance = math.sqrt( ((cutterPosition[0] - cvBboxPosition[0])**2)  + ((cutterPosition[1] - cvBboxPosition[1])**2) + ((cutterPosition[2] - cvBboxPosition[2])**2))
                if checkDistance < checkMinDistance:
                    checkMinDistance = checkDistance
                    closetestPos = cvBboxPosition
            mc.spaceLocator( p=(closetestPos[0], closetestPos[1], closetestPos[2]),n='tempSnap')
            mc.CenterPivot()
            mc.select(s,'tempSnap',r=True)
            mc.MatchTranslation()
            mc.delete('tempSnap')
            checkState = mc.button('toggleAxisXYZ', q=True , bgc =True )
            if checkState[0] < 0.285:
                checkStateX = mc.button('toggleAxisX', q=True , bgc =True )
                if checkStateX[0] <0.285:
                    mc.setAttr((s+'.translateX'),currentX)

                checkStateY = mc.button('toggleAxisY', q=True , bgc =True )
                if checkStateY[1] <0.285:
                    mc.setAttr((s+'.translateY'),currentY)

                checkStateZ = mc.button('toggleAxisZ', q=True , bgc =True )
                if checkStateZ[2] <0.285:
                    mc.setAttr((s+'.translateZ'),currentZ)
        borderAlginBBoxToggle()
        mc.select(selCutters)

def combineSelCutters():#work with different type of OP, but mixing type may be cause unexpect result
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selList = mc.ls(sl=True,fl=True)
    restoreMissingGrps()
    getOpType = ''
    if len(selList) > 1:
        #bake array
        for s in selList:
            if mc.objExists(s):
                mc.select(s)
                myType = checkInstType()
                if myType[1] != 'new':
                    instBake()
                    newNode = mc.ls(sl=1,fl=1)
                    selList.append(newNode[0])
        subsGrp = []
        unionGrp = []
        cutGrp = []
        for b in selList:
            longName = '|' +  beseMesh  + 'BoolGrp' + '|' + beseMesh+'_cutterGrp|' + b
            if mc.objExists(longName):
                checkOP = mc.getAttr(longName + '.cutterOp')
                if checkOP == 'subs':
                    subsGrp.append(b)
                elif checkOP == 'union':
                    unionGrp.append(b)
                elif checkOP == 'cut':
                    cutGrp.append(b)
        if (len(subsGrp) + len(unionGrp) + len(cutGrp))>1:
            #union each type
            selList = subsGrp
            if len(selList)> 0:
                mc.select(selList)
                while len(selList) > 1:
                    mc.polyCBoolOp(selList[0], selList[1], op=1, ch=1, preserveColor=0, classification=1, name=selList[0])
                    mc.DeleteHistory()
                    if mc.objExists(selList[1]):
                        mc.delete(selList[1])
                    mc.rename(selList[0])
                    selList.remove(selList[1])
                mc.rename('subsMesh')

            selList = unionGrp
            if len(selList)> 0:
                mc.select(selList)
                while len(selList) > 1:
                    mc.polyCBoolOp(selList[0], selList[1], op=1, ch=1, preserveColor=0, classification=1, name=selList[0])
                    mc.DeleteHistory()
                    if mc.objExists(selList[1]):
                        mc.delete(selList[1])
                    mc.rename(selList[0])
                    selList.remove(selList[1])
                mc.rename('unionMesh')

            selList = cutGrp
            if len(selList)> 0:
                mc.select(selList)
                while len(selList) > 1:
                    mc.polyCBoolOp(selList[0], selList[1], op=1, ch=1, preserveColor=0, classification=1, name=selList[0])
                    mc.DeleteHistory()
                    if mc.objExists(selList[1]):
                        mc.delete(selList[1])
                    mc.rename(selList[0])
                    selList.remove(selList[1])
                mc.rename('cutMesh')

        if mc.objExists('subsMesh'):
            if mc.objExists('unionMesh'):
                mc.polyCBoolOp('subsMesh', 'unionMesh', op=2, ch=1, preserveColor=0, classification=1, name='outMesh')
                if mc.objExists('cutMesh'):
                    mc.polyCBoolOp('outMesh', 'cutMesh', op=1, ch=1, preserveColor=0, classification=1, name='outMesh')
            else:
                 if mc.objExists('cutMesh'):
                    mc.polyCBoolOp('subsMesh', 'cutMesh', op=1, ch=1, preserveColor=0, classification=1, name='outMesh')
            newCutter = mc.ls(sl=1,fl=1)
            mc.DeleteHistory('outMesh')
            useOwnCutterShape()
            cutterType('subs')

        else:
            if mc.objExists('unionMesh'):
                if mc.objExists('cutMesh'):
                    mc.polyCBoolOp('unionMesh', 'cutMesh', op=2, ch=1, preserveColor=0, classification=1, name='outMesh')
            newCutter = mc.ls(sl=1,fl=1)
            mc.DeleteHistory('outMesh')
            useOwnCutterShape()
            cutterType('union')

        cleanList = ['subsMesh','cutMesh','unionMesh','outMesh']
        for l in cleanList:
            if mc.objExists(l):
                mc.delete(l)
    else:
        print ('need more then one cutter!')

def recreateBool():
    #recreate bool
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)

    cleanList = ['_mySubs','_myUnion','_preSubBox','_preUnionBox','_myBoolUnion','_afterSubBox','_myBoolSub','_myCut']
    for l in cleanList:
        if mc.objExists(beseMesh + l):
            mc.delete(beseMesh + l)
    if mc.objExists((beseMesh +'_bool')) ==0:
        mc.polyCube(w = 0.0001, h=0.0001, d=0.0001 ,sx =1 ,sy= 1, sz= 1)
        mc.rename(beseMesh +'_preSubBox')

        mc.polyCube(w = 0.0001, h=0.0001, d=0.0001 ,sx =1 ,sy= 1, sz= 1)
        mc.rename(beseMesh +'_afterSubBox')

        mc.polyCube(w = 0.0001, h=0.0001, d=0.0001 ,sx =1 ,sy= 1, sz= 1)
        mc.rename(beseMesh +'_preUnionBox')

        subNode= mc.polyCBoolOp((beseMesh ), (beseMesh +'_preSubBox') , op= 2, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_bool'))
        mc.rename(subNode[0],(beseMesh +'_myBoolSub'))

        unionNode = mc.polyCBoolOp((beseMesh +'_myBoolSub'), (beseMesh +'_preUnionBox') , op= 1, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_union'))
        mc.rename(unionNode[0],(beseMesh +'_myBoolUnion'))

        subNode= mc.polyCBoolOp((beseMesh +'_myBoolUnion'), (beseMesh +'_afterSubBox') , op= 2, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_bool'))
        mc.rename(subNode[0],(beseMesh +'_bool'))

    boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1,ac=1),type='polyCBoolOp')
    boolNode = set(boolNode)

    #hack it by check '_', this is used by other group
    listClean = []
    for b in boolNode:
        if '_' not in b:
            listClean.append(b)

    if len(listClean) == 3:
        for l in listClean:
            checkOp = mc.getAttr( l +'.operation')
            if checkOp == 2:
                if mc.objExists(beseMesh +'_mySubs'):
                    mc.rename(l,(beseMesh +'_myCut'))
                else:
                    mc.rename(l,(beseMesh +'_mySubs'))
            else:
                mc.rename(l,(beseMesh +'_myUnion'))

    mc.setAttr((beseMesh + '.visibility'), 0)
    mc.setAttr((beseMesh+'Shape.intermediateObject'), 0)

    baseShapeNode = mc.listRelatives(beseMesh, f = True)
    mc.parent(baseShapeNode, beseMesh+'BoolGrp')
    mc.delete(beseMesh)
    mc.rename(beseMesh)

    mc.editDisplayLayerMembers( (beseMesh +'_BoolResult'),(beseMesh +'_bool')) # store my selection into the display layer
    mc.setAttr((beseMesh +'_BoolResult.displayType'),2)

    checkList = ['_cutterGrp','_preSubBox','_preUnionBox','_myBoolUnion','_bool', '', '_afterSubBox','_myBoolSub' ]
    for c in checkList:
        checkGrp = mc.ls((beseMesh + c), l=True)
        if 'BoolGrp' not in checkGrp[0]:
            mc.parent(checkGrp[0],(beseMesh +'BoolGrp'))

    mc.select(cl=True)
    meshBBox()

def bakeCutter(mode):
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selectedCutter = mc.ls(sl=1,fl=1)
    checkGrp = mc.ls(sl=1,fl=1,l=1)
    if mode == 'unselect' and len(selectedCutter) == 0:
        print ('nothing selected!')
    else:
        #store any symmtry
        mc.setAttr((beseMesh+'.visibility'), 1)
        mirrorPivot = mc.objectCenter(beseMesh, gl=True)
        mc.setAttr((beseMesh+'.visibility'), 0)
        getSymX = 0
        getSymY = 0
        getSymZ = 0
        if mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
            getSymX =  mc.getAttr(beseMesh+'.symmetryX')
        if mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
            getSymY =  mc.getAttr(beseMesh+'.symmetryY')
        if mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
            getSymZ =  mc.getAttr(beseMesh+'.symmetryZ')
        #flatten all cutters
        flattenAlllCutter()
        if mode == 'unselect':
            if beseMesh in checkGrp[0]:#check if cutter in current base mesh
                #getList after flattern
                cleanList = []
                for s in selectedCutter:
                    if 'ArrayGrp' in s:
                        s = s.replace("ArrayGrp", "")
                    if mc.objExists(s.split('|')[-1]):
                        cleanList.append(s.split('|')[-1])
                mc.select(cleanList)
                #disconnect from bool
                for c in cleanList:
                    shapeNode = mc.listRelatives(c, f = True, shapes=True)
                    if len(shapeNode)>0:
                        listConnect = mc.connectionInfo((shapeNode[0]+'.outMesh'), dfs=True )
                        if len(listConnect)>0:
                            for a in listConnect:
                                mc.disconnectAttr((shapeNode[0]+'.outMesh'), a)
                        listConnectMa = mc.connectionInfo((shapeNode[0]+'.worldMatrix[0]'), dfs=True )
                        if len(listConnectMa)>0:
                            for b in listConnectMa:
                                mc.disconnectAttr((shapeNode[0]+'.worldMatrix[0]'), b)
                # move to temp grp
                if mc.objExists((beseMesh +'_tempStoreGrp')) == 0:
                    mc.CreateEmptyGroup()
                    mc.rename((beseMesh +'_tempStoreGrp'))
                    mc.parent((beseMesh +'_tempStoreGrp'), (beseMesh+'BoolGrp'))
                mc.parent(cleanList , (beseMesh +'_tempStoreGrp'))

        #make bool mesh as new base mesh
        newMesh = mc.duplicate((beseMesh+'_bool'),rr=1)
        mc.delete(beseMesh+'_bool')
        #create Step up Group
        if mc.objExists((beseMesh +'_bakeStep')) == 0:
            mc.CreateEmptyGroup()
            mc.rename((beseMesh +'_bakeStep'))
            mc.parent((beseMesh +'_bakeStep'), (beseMesh+'BoolGrp'))
        mc.setAttr((beseMesh +'_bakeStep.visibility'),0)

        if mc.objExists((beseMesh +'_bakeBaseMesh')) == 0:
            #bake base mesh
            bakeMesh = mc.duplicate(beseMesh, rr=1)
            mc.delete(beseMesh)
            mc.parent(bakeMesh,(beseMesh +'_bakeStep'))
            mc.rename(bakeMesh,(beseMesh +'_bakeBaseMesh'))
            bakeShape = mc.listRelatives((beseMesh +'_bakeBaseMesh'), shapes=True,f=True)
            #mc.setAttr((bakeShape[0] + '.overrideShading'), 1)
            mc.rename(newMesh,beseMesh)
        else:
            mc.delete(beseMesh)
            mc.rename(newMesh,beseMesh)
        if mc.objExists(beseMesh +'_myBool'):
            mc.delete(beseMesh+'_myBool')
        #reNumber
        mc.select((beseMesh+'_bakeStep'), hi=True)
        mc.select((beseMesh+'_bakeStep'),(beseMesh +'_bakeBaseMesh'),d=True)
        existCutterList = mc.ls(sl=1,fl=1,type='transform')
        #start rename old cutters
        mc.select((beseMesh+'_cutterGrp'), hi=True)
        mc.select((beseMesh+'_cutterGrp'),d=True)
        oldCutterList = mc.ls(sl=1,fl=1,type='transform')
        initalIndex = len(existCutterList) + 2
        for o in oldCutterList:
            newName = ('bakeCutter' + str(initalIndex))
            mc.rename(o, newName)
            initalIndex += 1
        newList= mc.ls(sl=1,fl=1,type='transform')
        if len(newList)>0:
            mc.parent(newList,(beseMesh +'_bakeStep'))

        #unlock connection
        shape = mc.listRelatives(beseMesh, shapes=True,f=True)
        checkConnection = mc.listConnections((shape[0]+'.drawOverride'),c=1,p=1)
        if checkConnection != None:
            mc.disconnectAttr(checkConnection[1],checkConnection[0])

        #recreate bool
        recreateBool()
        mc.move(mirrorPivot[0],mirrorPivot[1],mirrorPivot[2], (beseMesh + ".scalePivot"),(beseMesh + ".rotatePivot"), absolute=True)

        if mode == 'unselect':

            #reconnect selected Cutters
            newCutterList = []
            for c in cleanList:
                mc.select(c)
                fixBoolNodeConnection()
                newC = mc.ls(sl=1)
                newCutterList.append(newC[0])

            mc.parent(newCutterList , (beseMesh +'_cutterGrp'))
            if mc.objExists((beseMesh +'_tempStoreGrp')):
                mc.delete((beseMesh +'_tempStoreGrp'))

        setCutterBaseMesh()
        if mode == 'unselect':
            mc.select(selectedCutter)

        #restore symmetry
        if not mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
            mc.addAttr(beseMesh, ln='symmetryX', at = "long" )
            mc.setAttr((beseMesh+'.symmetryX'),getSymX)
        if not mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
            mc.addAttr(beseMesh, ln='symmetryY', at = "long" )
            mc.setAttr((beseMesh+'.symmetryY'),getSymY)
        if not mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
            mc.addAttr(beseMesh, ln='symmetryZ', at = "long" )
            mc.setAttr((beseMesh+'.symmetryZ'),getSymZ)

        #checkSymmetryState
        checkSymX =  mc.getAttr(beseMesh+'.symmetryX')
        checkSymY =  mc.getAttr(beseMesh+'.symmetryY')
        checkSymZ =  mc.getAttr(beseMesh+'.symmetryZ')

        if checkSymX == 1:
            boolSymmetry('x',1)
        elif checkSymX == -1:
            boolSymmetry('x',2)

        if checkSymY == 1:
            boolSymmetry('y',1)
        elif checkSymY == -1:
            boolSymmetry('y',2)

        if checkSymZ == 1:
            boolSymmetry('z',1)
        elif checkSymZ == -1:
            boolSymmetry('z',2)

        #hide all cage
        if mc.objExists(beseMesh + '_cageGrp'):
            mc.hide(beseMesh + '_cageGrp')
        #cageList = mc.ls((beseMesh + '_cage*'),type='transform')
        #for c in cageList:
        #    mc.setAttr((c+'.visibility'),0)
    mc.optionMenu('baseMeshMenu', e = True, value = beseMesh)
    restoreMissingGrps()

def restoreCutterWithSymmtry():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    #check current
    shapes = mc.listRelatives((beseMesh+'_bool'), shapes=True)
    shadeEng = mc.listConnections(shapes , type = 'shadingEngine')
    materials = mc.ls(mc.listConnections(shadeEng ), materials = True)
    checkX1 = mc.button('symmXButtonP', q=1 , bgc = 1)
    checkX2 = mc.button('symmXButtonN', q=1 , bgc = 1)
    checkY1 = mc.button('symmYButtonP', q=1 , bgc = 1)
    checkY2 = mc.button('symmYButtonN', q=1 , bgc = 1)
    checkZ1 = mc.button('symmZButtonP', q=1 , bgc = 1)
    checkZ2 = mc.button('symmZButtonN', q=1 , bgc = 1)
    restoreCutter()
    if checkX1[0]>0.29:
        boolSymmetry("x" ,1)
    if checkX2[0]>0.29:
        boolSymmetry("x" ,2)

    if checkY1[1]>0.29:
        boolSymmetry("y" ,1)
    if checkY2[1]>0.29:
        boolSymmetry("y" ,2)

    if checkZ1[2]>0.29:
        boolSymmetry("z" ,1)
    if checkZ2[2]>0.29:
        boolSymmetry("z" ,2)
    #resotre shader
    if materials[0] == (beseMesh+'_Shader'):
        mc.sets((beseMesh+'_bool'), e=True, forceElement = (beseMesh+'_ShaderSG'))
    else:
        mc.sets((beseMesh+'_bool'), e=True, forceElement = 'initialShadingGroup')

def restoreCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists((beseMesh +'_cutterGrp')) == 0:
        mc.CreateEmptyGroup()
        mc.rename((beseMesh +'_cutterGrp'))
        mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))

    if mc.objExists((beseMesh +'_bool')) ==0:
        mc.polyCube(w = 0.01, h=0.01, d=0.01 ,sx =1 ,sy= 1, sz= 1)
        mc.rename(beseMesh +'_preSubBox')
        mc.polyCube(w = 0.01, h=0.01, d=0.01 ,sx =1 ,sy= 1, sz= 1)
        mc.rename(beseMesh +'_preUnionBox')
        unionNode = mc.polyCBoolOp(beseMesh, (beseMesh +'_preUnionBox') , op= 1, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_union'))
        mc.rename(unionNode[0],(beseMesh +'_myBoolUnion'))
        subNode= mc.polyCBoolOp((beseMesh +'_myBoolUnion'), (beseMesh +'_preSubBox') , op= 2, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_bool'))
        mc.rename(subNode[0],(beseMesh +'_bool'))
        boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1,ac=1),type='polyCBoolOp')
        boolNode = set(boolNode)

        #hack it by check '_', this is used by other group
        listClean = []
        for b in boolNode:
            if '_' not in b:
                listClean.append(b)


        if len(listClean) == 3:
            for l in listClean:
                checkOp = mc.getAttr( l +'.operation')
                if checkOp == 2:
                    if mc.objExists(beseMesh +'_mySubs'):
                        mc.rename(l,(beseMesh +'_myCut'))
                    else:
                        mc.rename(l,(beseMesh +'_mySubs'))
                else:
                    mc.rename(l,(beseMesh +'_myUnion'))

        mc.setAttr((beseMesh + '.visibility'), 0)
        baseNodes = mc.listRelatives(beseMesh, ad = True, f = True)
        baseTransNode = mc.ls(baseNodes,type = 'transform')
        baseMeshNode = mc.ls(baseNodes,type = 'mesh')
        mc.setAttr((baseMeshNode[0]+'.intermediateObject'), 0)
        mc.parent(baseMeshNode[0],(beseMesh +'BoolGrp'))
        mc.delete(beseMesh)
        mc.rename(beseMesh)

    bakeCutter('all')
    mc.delete(beseMesh+'_bool')
    mc.delete(beseMesh)
    mc.parent((beseMesh +'_bakeBaseMesh'),  (beseMesh+'BoolGrp'))
    mc.rename((beseMesh +'_bakeBaseMesh'), beseMesh)
    baseShape = mc.listRelatives((beseMesh), shapes=True,f=True)
    checkAtt =  mc.getAttr(baseShape[0] + '.overrideShading')
    if checkAtt == 0:
        mc.setAttr((baseShape[0] + '.overrideShading'), 1)
    #recreate bool
    recreateBool()
    #restore cutters
    mc.select((beseMesh+'_bakeStep'), hi=True)
    mc.select((beseMesh+'_bakeStep'),d=True)
    restoreCutterList = mc.ls(sl=1,fl=1,type='transform')
    for r in restoreCutterList:
        shapeNode = mc.listRelatives(r, f = True, shapes=True)
        mc.setAttr( (shapeNode[0]+".overrideEnabled") , 1)
        mc.setAttr( (shapeNode[0]+".overrideShading") , 0)
        mc.setAttr( (shapeNode[0]+".castsShadows") , 0)
        mc.setAttr( (shapeNode[0]+".receiveShadows") , 0)
        mc.setAttr( (shapeNode[0]+".primaryVisibility") , 0)
        mc.setAttr( (shapeNode[0]+".visibleInReflections") , 0)
        mc.setAttr( (shapeNode[0]+".visibleInRefractions") , 0)
        mc.select(r)
        fixBoolNodeConnection()
        name = r.split('|')[-1]
        checkNumber = ''.join([n for n in name.split('|')[-1] if n.isdigit()])
        mc.rename(r ,('boxCutter' + str(checkNumber)))

    if mc.objExists((beseMesh +'_cutterGrp')):
        mc.delete(beseMesh +'_cutterGrp')

    mc.rename((beseMesh +'_bakeStep'),(beseMesh +'_cutterGrp'))
    mc.select(cl=True)
    showAllCutter()
    fixShadowLink()

def flattenAlllCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    mc.select((beseMesh+'_cutterGrp'), hi=True)
    mc.select((beseMesh+'_cutterGrp'),d=True)
    if mc.objExists('bakeCutter*'):
        mc.select('bakeCutter*',d=True)
    selList = mc.ls(sl=1,fl=1,type='transform')
    if len(selList) > 1:
        #bake array
        for s in selList:
            if mc.objExists(s):
                mc.select(s)
                myType = checkInstType()
                if myType[1] != 'new':
                    instBake()
                    newNode = mc.ls(sl=1,fl=1)
                    selList.append(newNode[0])

def freeResultMesh():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists((beseMesh+'_Done')) == 0 :
        bakeCutter("all")
        resultMesh = beseMesh +'_bool'
        mc.select(resultMesh)
        mc.duplicate(rr=True)
        mc.rename(beseMesh+'_Done')
        newNode = mc.ls(sl=True,fl=True)
        shapeNew = mc.listRelatives(newNode[0], s=True )
        mc.parent(w=True)
        mc.layerButton((beseMesh +'_BoolResult'), e=True ,lv=0)
        mc.setAttr((beseMesh +'BoolGrp.visibility'),0)
        mc.disconnectAttr((beseMesh+'_BoolResult.drawInfo'), (shapeNew[0]+'.drawOverride'))
        mc.editDisplayLayerMembers('defaultLayer',newNode)
        mc.hide(beseMesh+'BoolGrp')

def drawCurveNow():
    mc.snapMode(grid=1)
    mc.CVCurveTool()

def makeDrawBlock():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    curveSel = mc.ls(sl=1,fl=1)
    if len(curveSel) == 1 :
        mc.snapMode(grid=0)
        shapeNode = mc.listRelatives(curveSel[0], f = True, shapes=True)
        checkOpen = mc.getAttr(shapeNode[0]+'.form')
        if checkOpen == 0:
            mc.closeCurve( curveSel[0], ch=True, rpo=True )

        mc.select(curveSel)
        mc.duplicate()
        mc.group(w=True)
        mc.rename('tempMirrorGrp')

        mc.parent('tempMirrorGrp','lineDrawPlaneOffset')
        mc.FreezeTransformations()
        getPresize = mc.floatField( 'cuterPreSize' , q=1, value = True)
        setScale =   mc.floatSliderGrp('cutterScaleSlider', q=1, value = True)
        mc.setAttr('tempMirrorGrp.translateZ',(getPresize*setScale*0.5*-1))

        mc.Ungroup()
        mc.select(curveSel,add=1)
        mc.FreezeTransformations()
        curveSel = mc.ls(sl=1,fl=1)
        mc.select(curveSel)
        loftNode = mc.loft(ch =1, u=1, c= 0, ar= 1, d= 3, ss= 1, rn= 0, po =1, rsn= True)
        list = mc.listConnections(loftNode, type = 'nurbsTessellate')

        mc.setAttr((list[0]+'.polygonType'), 1)
        checkCurveType = mc.getAttr(curveSel[0]+'.degree')
        if checkCurveType > 1:
            mc.setAttr((list[0]+'.format'), 0)
        else:
            mc.setAttr((list[0]+'.format'), 2)
        mc.setAttr((list[0]+'.uNumber'), 1)
        mc.setAttr((list[0]+'.vNumber'), 1)
        mc.FillHole()
        mc.delete(curveSel)
        mc.rename('drawBlock')
        blockSel = mc.listRelatives(mc.listRelatives(f = True, shapes=True), parent=1 , f=1 )
        mc.CenterPivot()
        mc.polyMergeVertex(blockSel,d = 0.01, am= 1,ch=0)
        mc.polySetToFaceNormal()
        renew = mc.listRelatives(mc.listRelatives(f = True, shapes=True), parent=1 , f=1 )
        mc.DeleteHistory()
        #fix normal direction
        checkNormalMehs = mc.ls(sl=1,fl=1,l=1)
        mc.polyExtrudeFacet(constructionHistory = 1, keepFacesTogether= 1, ltz = 0.001)
        mc.polySeparate(checkNormalMehs,ch=0)
        testMesh = mc.ls(sl=1,fl=1)

        worldFaceA = mc.polyEvaluate(testMesh[0],wa=True)
        worldFaceB = mc.polyEvaluate(testMesh[1],wa=True)
        if worldFaceA > worldFaceB:
            mc.delete(testMesh[1])
        else:
            mc.delete(testMesh[0])

        mc.parent(w=True)
        mc.delete(checkNormalMehs[0])
        mc.rename('drawBlock1')
        newBlock = mc.ls(sl=1,fl=1)
        mc.select(newBlock[0])

        #remove unwant edgeLoop
        if checkCurveType > 1:
            mc.polySelectConstraint(m=3,t=0x0008,sz=3)
            mc.polySelectConstraint(disable =True)
            ngon = mc.ls(sl=1,fl=1)
            mc.select(ngon)
            mc.ConvertSelectionToEdges()
            hardEdge = mc.ls(sl=1,fl=1)
            mc.SelectEdgeRingSp()
            mc.select(hardEdge,d=1)
            mc.polyDelEdge(cv=1)
            mc.select(newBlock[0])

        mc.parent(newBlock[0],'drawPlaneGrp')
        mc.FreezeTransformations()
        mc.CenterPivot()
        mc.parent(newBlock[0],w=True)
        mc.DeleteHistory()
        mc.ScaleTool()

def goPressDraw():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    snapMesh = (beseMesh +'_bool')
    if mc.objExists('snapLive*'):
        mc.delete('snapLive*')
    mc.duplicate(snapMesh,n='snapLive')
    mc.setAttr('snapLive.visibility',0)
    global ctxCutter
    if mc.draggerContext(ctxCutter, exists=True):
        mc.deleteUI(ctxCutter)
    mc.draggerContext(ctxCutter, pressCommand = onPressDrawGrid, dragCommand = onDragDrawGridCMD, rc = offPressDrawGrid, name=ctxCutter, cursor='crossHair',undoMode='all')
    mc.setToolTo(ctxCutter)

def onDragDrawGridCMD():
    mc.undoInfo(swf=0)
    onDragDrawGrid()
    mc.undoInfo(swf=1)

def onDragDrawGrid():
    global ctxCutter
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    vpX, vpY, _ = mc.draggerContext(ctxCutter, query=True, dragPoint=True)
    screenX = vpX
    screenY = vpY
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
    finalX = []
    finalY = []
    finalZ = []
    shortDistance = 10000000000
    distanceBetween = 1000000000
    hitFacePtr = om.MScriptUtil().asIntPtr()
    hitFace = []
    checkList = []
    checkList.append('snapLive')
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
            hitFaceName = (mesh + '.f[' + str(hitFace) +']')
            rx, ry, rz = getFaceAngle(hitFaceName)
            mc.move(finalX,finalY,finalZ,'drawPlaneGrp',absolute=1)
            tz = mc.floatSliderGrp('snapGirdOffset', q=True, v = True)
            mc.setAttr('drawPlaneGrp.rotateX', rx)
            mc.setAttr('drawPlaneGrp.rotateY', ry)
            mc.setAttr('drawPlaneGrp.rotateZ', rz)
            #mc.setAttr('lineDrawPlaneOffset.translateX', 0)
            #mc.setAttr('lineDrawPlaneOffset.translateY', 0)
            mc.setAttr('lineDrawPlaneOffset.translateZ',tz)
            mc.refresh(cv=True,f=True)

def offPressDrawGrid():
    if mc.objExists('snapLive*'):
        mc.delete('snapLive*')
    mc.setToolTo('moveSuperContext')

def onPressDrawGrid():
    global ctxCutter
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    vpX, vpY, _ = mc.draggerContext(ctxCutter, query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY
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
    finalX = []
    finalY = []
    finalZ = []
    shortDistance = 10000000000
    distanceBetween = 1000000000
    hitFacePtr = om.MScriptUtil().asIntPtr()
    hitFace = []
    checkList = []
    checkList.append('snapLive')
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
            hitFaceName = (mesh + '.f[' + str(hitFace) +']')
            rx, ry, rz = getFaceAngle(hitFaceName)
            if mc.objExists('lineDrawPlane'):
                mc.delete('lineDrawPlane')
            if mc.objExists('drawPlaneGrp'):
                mc.delete('drawPlaneGrp')
            mesh = (beseMesh +'_bool')
            bbox= mc.xform(mesh, q=1, ws=1, bb=1)
            length=math.sqrt((math.pow(bbox[0]-bbox[3],2)+math.pow(bbox[1]-bbox[4],2)+math.pow(bbox[2]-bbox[5],2))/3)
            length = int(length *1.1 )
            mc.plane(s=length, r=[0,0,0])
            mc.rename('lineDrawPlane')
            mc.group('lineDrawPlane')
            mc.rename('lineDrawPlaneOffset')
            mc.makeIdentity( apply=True, t=1, r=1, s=1, n=0, pn=1 )
            mc.group('lineDrawPlaneOffset')
            mc.rename('lineDrawPlaneOffsetFreeze')
            mc.setAttr(("lineDrawPlaneOffsetFreeze.rotateX"), -90)
            mc.group('lineDrawPlaneOffsetFreeze')
            mc.rename('drawPlaneGrp')
            mc.move(finalX,finalY,finalZ,'drawPlaneGrp',absolute=1)
            mc.setAttr('drawPlaneGrp.rotateX', rx)
            mc.setAttr('drawPlaneGrp.rotateY', ry)
            mc.setAttr('drawPlaneGrp.rotateZ', rz)

            mc.makeLive('lineDrawPlane')
            mc.snapMode(grid=1)
            resizeSnapGrid()
            offsetSnapGrid()


def resizeSnapGrid():
    if mc.objExists('lineDrawPlane'):
        gridData=  mc.intSliderGrp('snapGirdSize', q = True, v =True)
        mc.makeLive(n=True)
        mc.grid( spacing=10, d= gridData )
        mc.makeLive('lineDrawPlane')
        mc.snapMode(grid=1)

def rotateSnapGrid():
    if mc.objExists('lineDrawPlane'):
        checkRot = mc.intSliderGrp('snapGirdRot',q=True, v = True)
        mc.setAttr("lineDrawPlane.rotateZ", checkRot)

def offsetSnapGrid():
    if mc.objExists('lineDrawPlane'):
        checkOffset =  mc.floatSliderGrp('snapGirdOffset',q=True, v = True)
        mc.setAttr("lineDrawPlaneOffset.translateZ", checkOffset)

def snapGridCamera():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkOffset = mc.floatSliderGrp('snapGirdOffset', q=True, v = True)
    mc.intSliderGrp('snapGirdRot',e=True, v = 0)
    curPanel = mc.getPanel(wf=1)
    if not 'modelPanel' in curPanel:
        curPanel = 'modelPanel4'
    mc.modelEditor( curPanel,e=1, planes=1)
    curCam = mc.modelPanel(curPanel,q=1, cam=1)
    cameraPos = mc.xform(curCam,q=1,ws=1,t=1)
    orthoValue = mc.camera(curCam,q=1, o=1)
    cameraUsed=[]
    planePos=[]
    if orthoValue ==0:
        camRot = mc.camera(curCam,q=1, rot=1)
        camRotFixed = []
        for i in range(2):
            camRotTemp = camRot[i] / 360
            intOfTemp = int(camRotTemp)
            rotOver = 360 * intOfTemp
            camRotFixed.append( camRot[i] - rotOver)

        for i in range(2):
            if camRotFixed[i] < 0 :
                  camRotFixed[i]= camRotFixed[i] +360;

        cameraUsed=[]
        if (camRotFixed[0] >= 45 and camRotFixed[0] < 135):
            cameraUsed = 'buttom'
        elif (camRotFixed[0] >= 225 and camRotFixed[0] < 315):
            cameraUsed = 'top'
        elif (camRotFixed[1] < 45):
            cameraUsed = 'front'
        elif (camRotFixed[1] >= 315 ):
            cameraUsed = 'front'
        elif (camRotFixed[1] >= 45 and camRotFixed[1] < 135):
            cameraUsed = 'right'
        elif (camRotFixed[1] >= 135 and camRotFixed[1] < 225):
            cameraUsed = 'back'
        elif (camRotFixed[1] >= 225 and camRotFixed[1] < 315):
            cameraUsed = 'left'

        mesh = (beseMesh +'_bool')
        bbox= mc.xform(mesh, q=1, ws=1, bb=1)
        length=math.sqrt((math.pow(bbox[0]-bbox[3],2)+math.pow(bbox[1]-bbox[4],2)+math.pow(bbox[2]-bbox[5],2))/3)
        length = int(length *1.1 )
        meshCOORD = mc.objectCenter(mesh,gl=True)
        constructionPlanePos=[]
        if mc.objExists('lineDrawPlane'):
            mc.delete('lineDrawPlane')
        if mc.objExists('drawPlaneGrp'):
            mc.delete('drawPlaneGrp')

        if cameraUsed == 'front' or cameraUsed == 'back':
            if cameraUsed == 'front':
                    planePos = bbox[5]
            elif cameraUsed == 'back':
                if (bbox[2] - cameraPos[2]) > 0:
                    planePos = bbox[2]
            constructionPlanePos = [meshCOORD[0],meshCOORD[1],planePos]

        elif  cameraUsed == 'top' or cameraUsed == 'buttom':# check y asix
            if cameraUsed == 'top':
                planePos = bbox[4]
            elif cameraUsed == 'buttom':
                planePos = bbox[1]
            constructionPlanePos = [meshCOORD[0],planePos,meshCOORD[2]]

        elif  cameraUsed == 'left' or cameraUsed == 'right':# check x asix
            if cameraUsed == 'right':
                planePos = bbox[3]
            elif cameraUsed == 'left':
                planePos = bbox[0]
            constructionPlanePos = [planePos,meshCOORD[1],meshCOORD[2]]

        mc.plane(s=length, r=[0,0,0])
        mc.rename('lineDrawPlane')
        mc.group('lineDrawPlane')
        mc.rename('lineDrawPlaneOffset')
        mc.move(constructionPlanePos[0],constructionPlanePos[1],constructionPlanePos[2],absolute=1)
        mc.makeIdentity( apply=True, t=1, r=1, s=1, n=0, pn=1 )
        mc.group('lineDrawPlaneOffset')
        mc.rename('drawPlaneGrp')

        if cameraUsed == 'front':
            mc.setAttr("drawPlaneGrp.rotateZ", -90)
        elif cameraUsed == 'back':
            mc.setAttr("drawPlaneGrp.rotateX", 180)

        elif  cameraUsed == 'top':
            mc.setAttr("drawPlaneGrp.rotateX", -90)
        elif cameraUsed == 'buttom':
            mc.setAttr("drawPlaneGrp.rotateX", 90)

        elif  cameraUsed == 'left':
            mc.setAttr("drawPlaneGrp.rotateY", -90)
        elif cameraUsed == 'right':
            mc.setAttr("drawPlaneGrp.rotateY", 90)

        mc.makeLive('lineDrawPlane')
        mc.snapMode(grid=1)
        resizeSnapGrid()
        offsetSnapGrid()

def drawGirdOff():
    if mc.objExists('lineDrawPlane'):
        mc.delete('lineDrawPlane*')
    if mc.objExists('tempScaleOffset'):
        mc.delete('tempScaleOffset*')
    if mc.objExists('drawPlaneGrp'):
        mc.delete('drawPlaneGrp*')
    mc.snapMode(grid=0)
    mc.MoveTool()

def drawGirdOn():
    mc.CVCurveTool()
    mc.curveCVCtx(mc.currentCtx(), e=True, d=1, bez= 0)


def removeGap():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    for n in newCutter:
        if 'boxCutter' in n:
            if 'ArrayGrp' in n:
                n = n.replace('ArrayGrp','')
            extrudeNode = mc.listConnections(mc.listHistory(n,ac=1),type='polyExtrudeFace')
            if extrudeNode != None:
                mc.delete(extrudeNode)
            mc.setAttr((n+'.statePanel'),0)
            mc.setAttr((n+'.preBevel'),1)


def makeGap():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    for n in newCutter:
        if 'boxCutter' in n:
            if 'ArrayGrp' in n:
                n = n.replace('ArrayGrp','')
            extrudeNode = mc.listConnections(mc.listHistory(n,ac=1),type='polyExtrudeFace')
            if extrudeNode != None:
                mc.delete(extrudeNode)
            gapV = []
            storeX = mc.getAttr( n + '.scaleX')
            gapV = mc.floatSliderGrp('gapSlider', q=True, v = True)
            if gapV < 0.01:
                gapV = 0.01
                mc.floatSliderGrp('gapSlider', e = True, v=0.01)
            mc.setAttr((n+'.panelGap'),gapV)
            mc.setAttr((n+'.intPanelGap'),gapV)
            mc.setAttr((n+'.intScaleX'),storeX)
            mc.select(n)
            extNode = mc.polyExtrudeFacet( constructionHistory=True, keepFacesTogether = True, smoothingAngle=30, tk = gapV )
            cmdText = (extNode[0] + '.thickness = ' + n + '.intScaleX/' +  n + '.scaleX*' + str(gapV) + '*' + n + '.panelGap/' +  n + '.intPanelGap')
            mc.expression( s = cmdText, o = extNode[0], ae = True, uc = all)
            mc.setAttr((n+'.statePanel'),1)
            mc.setAttr((n+'.preBevel'),0)
    mc.select(newCutter)

def hideAllCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    getCutters = mc.ls((beseMesh+'_cutterGrp|boxCutter*'),type = 'transform',l=True)
    mc.hide(getCutters)

def showLastCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    currentOne = mc.ls(sl=True,fl=True)
    getCutters = mc.ls((beseMesh+'_cutterGrp|boxCutter*'),type = 'transform')
    checkVis = []
    if len(getCutters) > 0:
        for g in getCutters:
            checkme = mc.getAttr(g+'.visibility')
            if checkme == 1:
               checkVis.append(g)
        if len(currentOne) > 0:
            checkCutter = []
            for c in currentOne:
                if 'boxCutter' in c:
                    checkCutter.append(c)
            if len(checkCutter)>0:
                checkSel = mc.getAttr(checkCutter[0]+'.visibility')
                mc.hide(getCutters)
                if checkSel == 0:
                    mc.setAttr((checkCutter[0]+'.visibility'), 1)
                else:
                    if len(checkVis) > 1:
                        mc.select(checkCutter[0])
                        mc.showHidden(checkCutter[0])
                    elif len(checkVis) == 1:
                        preCutter = 0
                        for i in range(len(getCutters)):
                            if getCutters[i] == checkCutter[0]:
                                preCutter = i - 1
                        mc.select(getCutters[preCutter])
                        mc.showHidden(getCutters[preCutter])
                    else:
                        mc.select(getCutters[-1])
                        mc.showHidden(getCutters[-1])
        else:
            mc.hide(getCutters)
            mc.select(getCutters[-1])
            mc.showHidden(getCutters[-1])
        mc.setAttr((beseMesh+'_cutterGrp.visibility'), 1)

def showAllCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    getCutters = mc.ls((beseMesh+'_cutterGrp|boxCutter*'),type = 'transform',l=True)
    checkAllCutterGrps = mc.ls(('*_cutterGrp'),type = 'transform',l=True)
    mc.hide(checkAllCutterGrps)
    mc.showHidden(getCutters)
    if mc.objExists((beseMesh +'_cutterGrp')) == 0:
        mc.CreateEmptyGroup()
        mc.rename((beseMesh +'_cutterGrp'))
        mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))

    mc.setAttr((beseMesh+'_cutterGrp.visibility'), 1)


def hideUnSelectedCutters():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    currentSel = mc.ls(sl= True)
    getCutters = mc.ls((beseMesh+'_cutterGrp|boxCutter*'),type = 'transform',l=True)
    checkVisList = []
    for g in getCutters:
        state = mc.getAttr(g+'.visibility')
        if state == 1:
            checkVisList.append(g)
    if len(checkVisList) == len(currentSel):
        showAllCutter()
    else:
        mc.hide(getCutters)
        mc.showHidden(currentSel)
    mc.select(currentSel)

def attributeGapSlider():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    checkSlider = mc.floatSliderGrp('gapSlider',q=True, v= True )
    if len(newCutter) > 0:
        for n in newCutter:
            if 'ArrayGrp' in n:
                 n = n.replace('ArrayGrp','')
            checkGap = mc.getAttr(n +'.statePanel')
            if checkGap == 1:
                mc.setAttr((n +'.panelGap'),checkSlider)

def attributeIntSlider(attributName):
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    sliderName = (str(attributName)+'Slider')
    checkSlider = mc.intSliderGrp(sliderName,q=True, v= True )
    if len(newCutter) > 0:
        for n in newCutter:
            if 'ArrayGrp' in n:
                 n = n.replace('ArrayGrp','')
            bevelNode = mc.listConnections(mc.listHistory(n),type='polyBevel3')
            if bevelNode != None:
                mc.setAttr((bevelNode[0] +'.' + attributName),checkSlider)

def attributeFloatSlider(attributName):
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    sliderName = (str(attributName)+'Slider')
    checkSlider = mc.floatSliderGrp(sliderName,q=True, v= True )
    if len(newCutter) > 0:
        for n in newCutter:
            if 'ArrayGrp' in n:
                 n = n.replace('ArrayGrp','')
            bevelNode = mc.listConnections(mc.listHistory(n),type='polyBevel3')
            if bevelNode != None:
                mc.setAttr((bevelNode[0] +'.' + attributName),checkSlider)


def cutterMirrorOver(direction):
    listSel = mc.ls(sl=True, fl=True ,l=True)
    if len(listSel) > 0 and 'boxCutter' in listSel[0] and 'ArrayGrp' not in listSel[0]:
        mc.duplicate(rr=True, un=True)
        mc.group()
        if mc.objExists('tempPivot'):
            mc.delete('tempPivot')
        mc.rename('tempPivot')
        beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
        meshCOORD = mc.objectCenter(beseMesh,gl=True)
        mc.xform(ws=True,  pivots =[meshCOORD[0],meshCOORD[1],meshCOORD[2]])

        if direction == 'x':
            mc.setAttr( ('tempPivot.scaleX'),-1)
        if direction == 'y':
            mc.setAttr( ('tempPivot.scaleY'),-1)
        if direction == 'z':
            mc.setAttr( ('tempPivot.scaleZ'),-1)
        mc.FreezeTransformations()

        mc.select(mc.listRelatives('tempPivot', c=True, f = True, typ='transform'))
        mc.select((beseMesh+'_cutterGrp'), add=True)
        mc.parent()
        listNew = mc.ls(sl=True, fl=True ,l=True)
        fixBoolNodeConnection()

        mc.delete('tempPivot')
        for s in listSel:
            mc.setAttr((s+'.visibility'),0)
        mc.select(listNew)

def cutterMirror(axis):
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    dulCutter = []
    if len(newCutter) > 0:
        for n in newCutter:
            if 'Cutter' in n:
                mc.FreezeTransformations()
                bboxObj = mc.xform(n , q = True, ws =True, bb=True)

                mirrorMode = 0

                if axis == 'x' :
                    if bboxObj[3] > 0 and bboxObj[0] > 0:
                        mirrorMode = 1
                    elif  bboxObj[3] < 0 and bboxObj[0] < 0:
                        mirrorMode = 1

                elif axis == 'y' :
                    if bboxObj[4] > 0 and bboxObj[1] > 0:
                        mirrorMode = 1
                    elif  bboxObj[4] < 0 and bboxObj[1] < 0:
                        mirrorMode = 1

                elif axis == 'z' :
                    if bboxObj[5] > 0 and bboxObj[2] > 0:
                        mirrorMode = 1
                    elif  bboxObj[5] < 0 and bboxObj[2] < 0:
                        mirrorMode = 1

                if mirrorMode == 1:
                    mc.select(n)
                    cutterMirrorOver(axis)
                    newC = mc.ls(sl=1)
                    dulCutter.append(newC[0])
                else:

                    lengthObj=math.sqrt((math.pow(bboxObj[0]-bboxObj[3],2)+math.pow(bboxObj[1]-bboxObj[4],2)+math.pow(bboxObj[2]-bboxObj[5],2))/3)
                    closeRange = lengthObj / 100

                    bboxSel = mc.xform(n , q = True, ws =True, bb=True)
                    midX = (bboxSel[3]+bboxSel[0])/2
                    midY = (bboxSel[4]+bboxSel[1])/2
                    midZ = (bboxSel[5]+bboxSel[2])/2
                    inRangeCv = []
                    vNo = mc.polyEvaluate(n, v = True )
                    checkPoint = 0
                    if axis == 'x' :
                        checkPoint = 0
                    elif axis == 'y' :
                        checkPoint = 1
                    else:
                        checkPoint = 2
                    for i in range(vNo):
                        positionV = mc.pointPosition((n +'.vtx[' + str(i) + ']') , w = True)
                        length= math.sqrt(math.pow(positionV[checkPoint],2))
                        if length <= closeRange:
                           inRangeCv.append((n +'.vtx[' + str(i) + ']'))
                        mc.select(inRangeCv, r=True)

                    # push those point off center a bit then mirror cut
                    if axis == 'x' :
                        for n in inRangeCv:
                            posiV = mc.pointPosition(n , w = True)
                            if midX >= 0:
                                mc.move((closeRange * -1.5) , posiV[1], posiV[2], n ,absolute=1)
                            else:
                                mc.move( (closeRange * 1.5) , posiV[1], posiV[2], n ,absolute=1)
                        cutPlane= mc.polyCut(n, ws = True, cd = 'X' , df = True , ch =True)
                        mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
                        mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
                        mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
                        if midX > 0:
                            mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 90)
                            mc.polyMirrorFace(n,cutMesh =1, axis = 0, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
                        else:
                            mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), -90)
                            mc.polyMirrorFace(n,cutMesh =1, axis = 0, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)

                    if axis == 'y' :
                        for n in inRangeCv:
                            posiV = mc.pointPosition(n , w = True)
                            if midY >= 0:
                                mc.move(posiV[0], (closeRange  * -1.5) , posiV[2], n ,absolute=1)
                            else:
                                mc.move(posiV[0], (closeRange  * 1.5) , posiV[2], n ,absolute=1)
                        cutPlane= mc.polyCut(n, ws = True, cd = 'Y' , df = True , ch =True)
                        mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
                        mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
                        mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
                        if midY > 0:
                            mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'), -90)
                            mc.polyMirrorFace(n,cutMesh =1, axis = 1, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
                        else:
                            mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'), 90)
                            mc.polyMirrorFace(n,cutMesh =1, axis = 1, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)

                    if axis == 'z' :
                        for n in inRangeCv:
                            posiV = mc.pointPosition(n , w = True)
                            if midZ >= 0:
                                mc.move(posiV[0], posiV[1],(closeRange  * -1.5), n ,absolute=1)
                            else:
                                mc.move(posiV[0], posiV[1],(closeRange  * 1.5), n ,absolute=1)
                        cutPlane= mc.polyCut(n, ws = True, cd = 'Z' , df = True , ch =True)
                        mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
                        mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
                        mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
                        if midZ > 0:
                            mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 0)
                            mc.polyMirrorFace(n,cutMesh =1, axis = 2, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
                        else:
                            mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 180)
                            mc.polyMirrorFace(n,cutMesh =1, axis = 2, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
                    mc.select(n)
                    dulCutter.append(n)
                    mc.BakeNonDefHistory()
            mc.select(dulCutter)

def useOwnCutterShape():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    ownCutter = mc.ls(sl=True, fl=True ,l=True)
    restoreMissingGrps()
    o = ownCutter[0]
    if len(ownCutter) > 0:
        for o in ownCutter:
            if ('_cutterGrp') in o:
                print ('shape already been used')
            else:
                if mc.objExists(beseMesh + '_BoolResult') == 0:
                    restoreCutterWithSymmtry()
                mc.select(o)
                mc.parent(o,(beseMesh+'_cutterGrp'))
                ownCutter = mc.ls(sl=True, fl=True ,l=True)
                newNumber = nextCutterNumber()
                newName = 'boxCutter'+str(newNumber)
                mc.select(ownCutter)
                mc.rename(newName)
                newCutter = mc.ls(sl=True, fl=True)
                shapeNode = mc.listRelatives(newCutter, f = True, shapes=True)
                mc.setAttr( (shapeNode[0]+".overrideEnabled") , 1)
                mc.setAttr( (shapeNode[0]+".overrideShading") , 0)
                mc.setAttr( (shapeNode[0]+".castsShadows") , 0)
                mc.setAttr( (shapeNode[0]+".receiveShadows") , 0)
                mc.setAttr( (shapeNode[0]+".primaryVisibility") , 0)
                mc.setAttr( (shapeNode[0]+".visibleInReflections") , 0)
                mc.setAttr( (shapeNode[0]+".visibleInRefractions") , 0)
                checkButtonStateList = ['subsButton','unionButton','cutButton']
                getCurrentType = ''
                for c in checkButtonStateList:
                    buttonState = mc.button( c ,q=1,  bgc = True )
                    if buttonState[1] > 0.4:
                        getCurrentType = c
                setType = getCurrentType.replace('Button','')
                if setType == 'subs':
                    mc.setAttr( (shapeNode[0]+'.overrideColor'), 28)
                elif setType == 'union':
                    mc.setAttr( (shapeNode[0]+'.overrideColor'), 31)
                else:
                    mc.setAttr( (shapeNode[0]+'.overrideColor'), 25)
                mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((beseMesh +'_my' + setType.title() +'.inputMat['+str(newNumber)+']')),f=True)
                mc.connectAttr( (shapeNode[0]+".outMesh"), ((beseMesh +'_my' + setType.title() + '.inputPoly['+str(newNumber)+']')),f=True)

                if not mc.attributeQuery('cutterDir', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='cutterDir',  dt= 'string')
                if not mc.attributeQuery('cutterType', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='cutterType',  dt= 'string')
                mc.setAttr((newCutter[0]+'.cutterDir'),e=True, keyable=True)
                mc.setAttr((newCutter[0]+'.cutterType'),e=True, keyable=True)

                if not mc.attributeQuery('cutterOp', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='cutterOp',  dt= 'string')
                mc.setAttr((newCutter[0]+'.cutterOp'),e=True, keyable=True)
                mc.setAttr((newCutter[0]+'.cutterOp'),setType,type="string")

                if not mc.attributeQuery('statePanel', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='statePanel', at = "float" )
                if not mc.attributeQuery('panelGap', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='panelGap', at = "float" )
                if not mc.attributeQuery('intPanelGap', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='intPanelGap', at = "float" )
                if not mc.attributeQuery('intScaleX', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='intScaleX', at = "float" )

                if not mc.attributeQuery('preBevel', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='preBevel', at = "float" )

                mc.setAttr((newCutter[0]+'.statePanel'),0)
                mc.setAttr((newCutter[0]+'.preBevel'),1)
                mc.select(newCutter[0])
                mc.setAttr((newCutter[0]+'.cutterType'),'custom' ,type="string")
    else:
        print ('nothing select!')


def cutterDulpicate():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    dulCutter = mc.ls(sl=True, fl=True , l=True)
    newCutterList = []
    if len(dulCutter) > 0:
        for d in dulCutter:
            checkParent = d.split('|')
            if len(checkParent)>2 and 'boxCutter' in d and 'cutterGrp' in d:
                newNumber = nextCutterNumber()
                newName = 'boxCutter'+str(newNumber)
                mc.select(d)
                mc.duplicate(rr = True, un=True)
                mc.rename(newName)
                newCutter = mc.ls(sl=True, fl=True)
                shapeNode = mc.listRelatives(newCutter[0], f = True, shapes=True)
                mc.setAttr( (shapeNode[0]+".overrideEnabled") , 1)
                mc.setAttr( (shapeNode[0]+".overrideShading") , 0)
                mc.setAttr( (shapeNode[0]+".castsShadows") , 0)
                mc.setAttr( (shapeNode[0]+".receiveShadows") , 0)
                mc.setAttr( (shapeNode[0]+".primaryVisibility") , 0)
                mc.setAttr( (shapeNode[0]+".visibleInReflections") , 0)
                mc.setAttr( (shapeNode[0]+".visibleInRefractions") , 0)
                boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
                if boolNode != None:
                    mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((boolNode[0]+'.inputMat['+str(newNumber)+']')),f=True)
                    mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(newNumber)+']')),f=True)
                    mc.select(newCutter[0])
                    fixBoolNodeConnection()
                    newCutterList.append(newCutter[0])
            else:
                print (d + 'is not a cutter!!')
        mc.select(newCutterList)
    else:
        print ('nothing selected!')


def QChangeCutterDir(dir):
    selObj = mc.ls(sl=1, fl=1,l=True, type='transform')
    if len(selObj) == 1:

        checkMasterDir = []
        checkMasterNumber = []
        checkMasterDis = []
        arraySample = []
        myType = checkInstType()
        if 'ArrayGrp' in selObj[0]:
            myType = checkInstType()
            arraySample = myType[0]
            if myType[1] != 'new':
                checkMasterDir = mc.getAttr(arraySample+'.arrayDirection')
                checkMasterNumber = mc.getAttr(arraySample+'.arrayNumber')
                checkMasterDis = mc.getAttr(arraySample+'.arrayOffset')
                checkMasterType = myType[1]
                if myType[1] == 'radial':
                    removeRadArray()
                else:
                    instRemove()
            selObj = mc.ls(sl=1, fl=1,l=True, type='transform')
        mc.setAttr((selObj[0]+'.rotateX'), 0)
        mc.setAttr((selObj[0]+'.rotateY'), 0)
        mc.setAttr((selObj[0]+'.rotateZ'), 0)
        cutterDirection = mc.getAttr(selObj[0]+'.cutterDir')

        if dir == 'X':
            dir = 'Z'
        elif dir == 'Y':
            pass
        else:
            dir = 'X'

        parnetGrp = mc.listRelatives(selObj[0], parent =1, f=1)
        mc.group(em=True, name = (selObj[0]+'_offset'),parent = parnetGrp[0])
        newNode = mc.ls(sl=True,fl=True)
        mc.FreezeTransformations()
        sourcePivot = mc.xform(selObj[0], q=1, ws=1 ,rp=1)
        mc.xform(newNode ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
        mc.parent(selObj[0],newNode)
        mc.setAttr((newNode[0]+'.rotate' + dir), 90)
        newNode = mc.ls(sl=True,fl=True)
        parnetGrpRemove = mc.listRelatives(newNode[0], parent =1, f=1)
        mc.parent(newNode[0],parnetGrp)
        mc.delete(parnetGrpRemove)
        newNode = mc.ls(sl=True,fl=True)
        if myType[1] != 'new':
            if myType[1] == 'radial':
                instRadAdd(checkMasterDir)
            else:
                instLinearAdd(checkMasterDir)
            mc.setAttr((newNode[0]+'.arrayNumber'),checkMasterNumber)
            mc.setAttr((newNode[0]+'.arrayOffset'),checkMasterDis)

def QBoxSmooth():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    if len(newCutter) > 0:
        for n in newCutter:
            if 'Cutter' in n:
                if 'ArrayGrp' in n:
                    myType = checkInstType()
                    n = (myType[0])
            #in case gap exist
            extrudeNode = mc.listConnections(mc.listHistory(n,ac=1),type='polyExtrudeFace')
            if extrudeNode != None:
                mc.delete(extrudeNode)
            bevelNode = mc.listConnections(mc.listHistory(n,ac=1),type='polyBevel3')
            bevelType = []
            getFrac = []
            getSeg = []
            getDep = []
            mc.select(n)
            if bevelNode != None:
                mc.makeIdentity( n, apply=True, scale=True )
                #record old setting
                getFrac = mc.getAttr(bevelNode[0]+'.fraction')
                getSeg = mc.getAttr(bevelNode[0]+'.segments')
                getDep = mc.getAttr(bevelNode[0]+'.depth')
                mc.delete(bevelNode)
                mc.DeleteHistory()
            bevelNodeNew = mc.polyBevel3(n, mv = 1, mvt =0.001, fn = 1, fraction = 0.5, offsetAsFraction = 1, autoFit = 1, depth = 1, mitering = 0, miterAlong = 0, chamfer = 1,  segments = 5,  ch = 1)
            mc.floatSliderGrp('fractionSlider', e=True , v = 0.5)
            mc.intSliderGrp('segmentsSlider',   e=True , v = 5)
            mc.floatSliderGrp('depthSlider',    e=True , v = 1)
            if bevelNode != None:
                mc.setAttr((bevelNodeNew[0]+'.fraction'),getFrac)
                mc.setAttr((bevelNodeNew[0]+'.segments'),getSeg)
                mc.setAttr((bevelNodeNew[0]+'.depth'),getDep)
                mc.floatSliderGrp('fractionSlider', e=True , v = getFrac)
                mc.intSliderGrp('segmentsSlider',   e=True , v = getSeg)
                mc.floatSliderGrp('depthSlider',    e=True , v = getDep)
            mc.setAttr((n+'.cutterType'),'smooth',type="string")
            checkGapState = mc.getAttr(n+'.statePanel')
            if checkGapState == 1:
                mc.select(n)
                makeGap()
        mc.select(newCutter)

def QBoxBevel():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    if len(newCutter) > 0:
        for n in newCutter:
            if 'Cutter' in n:
                if 'ArrayGrp' in n:
                    myType = checkInstType()
                    n = (myType[0])
            #in case gap exist
            extrudeNode = mc.listConnections(mc.listHistory(n,ac=1),type='polyExtrudeFace',s=True)
            if extrudeNode != None:
                mc.delete(extrudeNode)
            bevelNode = mc.listConnections(mc.listHistory(n,ac=1),type='polyBevel3')
            bevelList = []
            bevelType = []
            getFrac = []
            getSeg = []
            getDep = []
            mc.select(n)
            mc.makeIdentity( n, apply=True, scale=True )
            if bevelNode != None:
                #record old setting
                getFrac = mc.getAttr(bevelNode[0]+'.fraction')
                getSeg = mc.getAttr(bevelNode[0]+'.segments')
                getDep = mc.getAttr(bevelNode[0]+'.depth')
                mc.delete(bevelNode)
                mc.DeleteHistory()

            mc.select(n)
            mc.polySelectConstraint(mode = 3, type = 0x0008, size=1)
            mc.polySelectConstraint(disable =True)
            triFind = mc.ls(sl=1,fl=1)
            mc.select(n)
            mc.polySelectConstraint(mode = 3, type = 0x0008, size=3)
            mc.polySelectConstraint(disable =True)
            ngonFind = mc.ls(sl=1,fl=1)

            if len(triFind) == 2 and len(ngonFind) == 0:# case is triprism
                bevelList = str(n + '.e[6:8]')

            elif len(triFind) > 0 or len(ngonFind) > 0:
                if len(triFind) > 0:
                    mc.select(triFind)
                    mc.InvertSelection()#added - usless
                else:
                    mc.select(ngonFind)
                mc.select(n)
                mc.ConvertSelectionToFaces()
                mc.select(ngonFind,d=True)
                mc.ConvertSelectionToContainedEdges()
                bevelList = mc.ls(sl=1,fl=1)
            else:#case is cube
                checkNoCustom = mc.getAttr(n+'.cutterType')
                if checkNoCustom == 'custom':
                    mc.select(str(n + '.e[4:5]'))
                    mc.select(str(n + '.e[8:9]'), add =1 )
                    bevelList = mc.ls(sl=1,fl=1)
                else:
                    bevelList = str(n + '.e[8:11]')

            bevelNodeNew = mc.polyBevel3(bevelList, mv = 1, mvt =0.001, fn = 1, fraction = 0.5, offsetAsFraction = 1, autoFit = 1, depth = 1, mitering = 0, miterAlong = 0, chamfer = 1,  segments = 5,  ch = 1)
            mc.floatSliderGrp('fractionSlider', e=True , v = 0.5)
            mc.intSliderGrp('segmentsSlider',   e=True , v = 5)
            mc.floatSliderGrp('depthSlider',    e=True , v = 1)
            if bevelNode != None:
                mc.setAttr((bevelNodeNew[0]+'.fraction'),getFrac)
                mc.setAttr((bevelNodeNew[0]+'.segments'),getSeg)
                mc.setAttr((bevelNodeNew[0]+'.depth'),getDep)
                mc.floatSliderGrp('fractionSlider', e=True , v = getFrac)
                mc.intSliderGrp('segmentsSlider',   e=True , v = getSeg)
                mc.floatSliderGrp('depthSlider',    e=True , v = getDep)
            if extrudeNode != None:
                makeGap()
            mc.setAttr((n+'.cutterType'),'bevel',type="string")
            checkGapState = mc.getAttr(n+'.statePanel')
            if checkGapState == 1:
                mc.select(n)
                makeGap()
        mc.select(newCutter)

    else:
        mc.ConvertSelectionToEdges()
        selEdges =mc.filterExpand(ex =1, sm =32)
        if len(selEdges)>0:
            geoList = mc.ls(hl=1)
            for g in geoList:
                mc.setAttr((g+'.cutterType'),'bevel',type="string")
                checkEdge = []
                for s in selEdges:
                    if g in s:
                        checkEdge.append(s)
                bevelNodeNew = mc.polyBevel3(checkEdge, mv = 1, mvt =0.001, fn = 1, fraction = 0.5, offsetAsFraction = 1, autoFit = 1, depth = 1, mitering = 0, miterAlong = 0, chamfer = 1,  segments = 5,  ch = 1)
        mc.select(geoList)
        mc.floatSliderGrp('fractionSlider', e=True , v = 0.5)
        mc.intSliderGrp('segmentsSlider',   e=True , v = 5)
        mc.floatSliderGrp('depthSlider',    e=True , v = 1)



def QBoxBevelRemove():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    if len(newCutter) > 0:
        for n in newCutter:
            if 'Cutter' in n:
                if 'ArrayGrp' in n:
                    myType = checkInstType()
                    n = (myType[0])
                checkNoCustom = mc.getAttr(n+'.cutterType')
                if checkNoCustom == 'bevel' or checkNoCustom == 'smooth':
                    mc.makeIdentity( n, apply=True, scale=True )
                    shapeNode = mc.listRelatives(n, f = True, shapes=True)
                    bevelNode = mc.listConnections(mc.listHistory(shapeNode,ac=1),type='polyBevel3')
                    if bevelNode != None:
                        checkGapState = mc.getAttr(n+'.statePanel')
                        if checkGapState == 1:
                            extrudeNode = mc.listConnections(mc.listHistory(n,ac=1),type='polyExtrudeFace')
                            if extrudeNode != None:
                                mc.delete(extrudeNode)
                        mc.delete(bevelNode)
                    mc.select(n)
                    mc.DeleteHistory()
                    mc.setAttr((n+'.cutterType'),'none',type="string")
                    checkGapState = mc.getAttr(n+'.statePanel')
                    if checkGapState == 1:
                        mc.select(n)
                        makeGap()
    mc.select(newCutter)

def scrapeCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    selCutter = mc.ls(sl=1, fl=1, type='transform')
    myType = checkInstType()
    if len(selCutter) == 1 and 'boxCutter' in selCutter[0] and  myType[1] == 'new':
        shapeNode = mc.listRelatives(selCutter[0], f = True, shapes=True)
        checkConnection = mc.listConnections(shapeNode[0]+'.worldMatrix',d=1,p=1)
        mc.disconnectAttr((shapeNode[0]+'.worldMatrix'), checkConnection[0])
        checkConnection = mc.listConnections(shapeNode[0]+'.outMesh',d=1,p=1)
        mc.disconnectAttr((shapeNode[0]+'.outMesh'), checkConnection[0])

        newNode = mc.duplicate((beseMesh+'_bool'),rr=1)
        mc.polyExtrudeFacet(newNode,constructionHistory = 1, keepFacesTogether= 1, tk = 0.1)
        mc.polySeparate(newNode, ch=0)
        testMesh = mc.ls(sl=1,fl=1)
        worldFaceA = mc.polyEvaluate(testMesh[0],wa=True)
        worldFaceB = mc.polyEvaluate(testMesh[1],wa=True)

        if worldFaceA > worldFaceB:
            mc.delete(testMesh[1])
        else:
            mc.delete(testMesh[0])
        mc.rename(selCutter[0] + '_skinMesh')

        if mc.objExists(selCutter[0] + 'skinGrp') == 0:
            mc.CreateEmptyGroup()
            mc.rename(selCutter[0] +'skinGrp')

        mc.parent((selCutter[0] + '_skinMesh'),(selCutter[0] +'skinGrp'))
        mc.delete(newNode)
        mc.ReversePolygonNormals()
        mc.DeleteHistory()


        #create intersection boolean
        subNode= mc.polyCBoolOp(selCutter[0],(selCutter[0] + '_skinMesh') , op= 3, ch= 1, preserveColor= 0, classification= 1, name= 'skinCutter')
        mc.DeleteHistory()

        #add cutter back
        extNode = mc.polyExtrudeFacet( constructionHistory=True, keepFacesTogether = True, smoothingAngle=30, tk = 1 )
        if mc.objExists((beseMesh +'_cutterGrp')) == 0:
            mc.CreateEmptyGroup()
            mc.rename((beseMesh +'_cutterGrp'))
            mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))

        mc.select('skinCutter')
        useOwnCutterShape()
        #add skin attribute
        selCutter = mc.ls(sl=1, fl=1, type='transform')
        if not mc.attributeQuery('skinOffset', node = selCutter[0], ex=True ):
            mc.addAttr(selCutter[0], ln='skinOffset', at = "float" )
            mc.setAttr((selCutter[0]+'.skinOffset'),0.5)

        mc.setAttr((selCutter[0]+'.cutterType'),'scrape',type="string")
        mc.connectAttr((selCutter[0] +'.skinOffset'), (extNode[0] +'.thickness'),f=True)
        #link slider
        mc.connectControl('scrapeSlider', (selCutter[0] +'.skinOffset'))

def addBevelDirectionAttr():
    newCutter = mc.ls(sl=True, fl=True)
    mc.setAttr((newCutter[0]+'.cutterDir'),'x',type="string")
    mc.setAttr((newCutter[0]+'.cutterType'),'bevel',type="string")

def offPressCutter():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    checkNoSnapX = mc.getAttr('sampleLoc.translateX')
    checkNoSnapY = mc.getAttr('sampleLoc.translateY')
    checkNoSnapZ = mc.getAttr('sampleLoc.translateZ')
    if checkNoSnapX !=0 and  checkNoSnapY !=0 and  checkNoSnapZ !=0:
        mc.select('sampleLoc')
        mc.pickWalk(d='down')
        newCutter = mc.ls(sl=1,fl=1)
        mc.parent(newCutter,(beseMesh+'_cutterGrp'))
    if mc.objExists('sampleLoc*'):
        mc.delete('sampleLoc*')
    if mc.objExists('snapLive*'):
        mc.delete('snapLive*')
    mc.setToolTo('moveSuperContext')

def goPressCutter(boxSide):
    global currentScaleRecord
    global currentCutterName
    hideAllCutter()
    if mc.objExists('sampleLoc*'):
        mc.delete('sampleLoc*')
    if mc.objExists('snapLive*'):
        mc.delete('snapLive*')
    #create cutter
    sideNumber = boxSide
    preRotAngle = []
    if sideNumber == 3:
        preRotAngle = 60
    elif sideNumber == 4:
        preRotAngle = 45
    elif sideNumber == 5:
        preRotAngle = 72
    elif sideNumber == 6:
        preRotAngle = 30

    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists(beseMesh + '_BoolResult') == 0:
        restoreCutterWithSymmtry()
    nextIndex = nextCutterNumber()
    member =mc.editDisplayLayerMembers((beseMesh+'_BoolResult'),q=True)
    snapMesh =[]
    if member != None:
        snapMesh = member[0]
    mc.setToolTo('moveSuperContext')
    getPresize = mc.floatField( 'cuterPreSize' , q=1, value = True)
    setScale =   mc.floatSliderGrp('cutterScaleSlider', q=1, value = True)
    mc.polyCylinder(r = getPresize, h= (1.5*getPresize) ,sx= boxSide, sy =0, sz=0, rcp= 0 , cuv =3 ,ch=1)
    mc.rename('boxCutter'+str(nextIndex))
    newCutter = mc.ls(sl=True, fl=True)
    currentCutterName = newCutter[0]
    mc.setAttr( (newCutter[0]+'.rotateY'), preRotAngle)
    mc.makeIdentity((newCutter[0]),apply =1, t = 0, r = 1, s =0, n =0, pn= 1)
    mc.setAttr( (newCutter[0]+'.scaleX'),(setScale))
    mc.setAttr( (newCutter[0]+'.scaleZ'),(setScale))
    mc.setAttr( (newCutter[0]+'.scaleY'),(setScale))
    currentScaleRecord = setScale
    #mc.CenterPivot()
    mc.group()
    mc.rename('sampleLoc')
    mc.xform(ws =True, piv =(0,0,0))
    mc.setAttr('sampleLoc.scaleX', 0.001)
    mc.setAttr('sampleLoc.scaleY', 0.001)
    mc.setAttr('sampleLoc.scaleZ', 0.001)
    refTopNode = mc.ls(sl = True,fl =True, type= 'transform')[0]
    transDownNode = mc.listRelatives('sampleLoc', c=True,f=True )
    #cutter in position
    #add attr
    shapeNode = mc.listRelatives(newCutter[0], shapes=True ,f =True)
    mc.setAttr( (shapeNode[0]+".overrideEnabled") , 1)
    mc.setAttr( (shapeNode[0]+".overrideShading") , 0)
    mc.setAttr( (shapeNode[0]+".castsShadows") , 0)
    mc.setAttr( (shapeNode[0]+".receiveShadows") , 0)
    mc.setAttr( (shapeNode[0]+".primaryVisibility") , 0)
    mc.setAttr( (shapeNode[0]+".visibleInReflections") , 0)
    mc.setAttr( (shapeNode[0]+".visibleInRefractions") , 0)

    if not mc.attributeQuery('cutterDir', node = newCutter[0], ex=True ):
        mc.addAttr(newCutter[0], ln='cutterDir',  dt= 'string')
    if not mc.attributeQuery('cutterType', node = newCutter[0], ex=True ):
        mc.addAttr(newCutter[0], ln='cutterType',  dt= 'string')
    mc.setAttr((newCutter[0]+'.cutterDir'),e=True, keyable=True)
    mc.setAttr((newCutter[0]+'.cutt erType'),e=True, keyable=True)

    if not mc.attributeQuery('cutterOp', node = newCutter[0], ex=True ):
        mc.addAttr(newCutter[0], ln='cutterOp',  dt= 'string')
    mc.setAttr((newCutter[0]+'.cutterOp'),e=True, keyable=True)

    checkButtonStateList = ['subsButton','unionButton','cutButton']
    getCurrentType = ''
    for c in checkButtonStateList:
        buttonState = mc.button( c ,q=1,  bgc = True )
        if buttonState[1] > 0.4:
            getCurrentType = c

    setType = getCurrentType.replace('Button','')
    mc.setAttr((newCutter[0]+'.cutterOp'),setType,type="string")
    if setType == 'subs':
        mc.setAttr( (shapeNode[0]+'.overrideColor'), 28)
    elif setType == 'union':
        mc.setAttr( (shapeNode[0]+'.overrideColor'), 31)
    else:
        mc.setAttr( (shapeNode[0]+'.overrideColor'), 25)

    if not mc.attributeQuery('statePanel', node = newCutter[0], ex=True ):
        mc.addAttr(newCutter[0], ln='statePanel', at = "float" )
    if not mc.attributeQuery('panelGap', node = newCutter[0], ex=True ):
        mc.addAttr(newCutter[0], ln='panelGap', at = "float" )
    if not mc.attributeQuery('intPanelGap', node = newCutter[0], ex=True ):
        mc.addAttr(newCutter[0], ln='intPanelGap', at = "float" )
    if not mc.attributeQuery('intScaleX', node = newCutter[0], ex=True ):
        mc.addAttr(newCutter[0], ln='intScaleX', at = "float" )
    if not mc.attributeQuery('preBevel', node = newCutter[0], ex=True ):
        mc.addAttr(newCutter[0], ln='preBevel', at = "float" )
    mc.setAttr((newCutter[0]+'.statePanel'),0)
    mc.setAttr((newCutter[0]+'.preBevel'),1)
    mc.select(('boxCutter'+str(nextIndex)))
    fixBoolNodeConnection()
    addBevelDirectionAttr()
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    snapMesh = (beseMesh +'_bool')
    mc.duplicate(snapMesh,n='snapLive')
    mc.setAttr('snapLive.visibility',0)
    mc.select(cl=1)
    ##### undo ######
    global ctxCutter
    ctxCutter = 'ctxCutter'
    mc.intSliderGrp('cutterSideSlider', e=1,  v = boxSide)
    if mc.draggerContext(ctxCutter, exists=True):
        mc.deleteUI(ctxCutter)
    mc.draggerContext(ctxCutter, pressCommand = onPressCutter, rc = offPressCutter, dragCommand = onDragCutterCMD, name=ctxCutter, cursor='crossHair', undoMode='all')
    mc.setToolTo(ctxCutter)


def onDragCutterCMD():
    mc.undoInfo(swf=0)
    onDragCutter()
    mc.undoInfo(swf=1)

def onDragCutter():
    global ctxCutter
    global screenX,screenY
    global currentScaleRecord
    global currentCutterName
    selSample = 'sampleLoc'
    modifiers = mc.getModifiers()
    if (modifiers == 1):
        #print 'shift Press'
        vpX, vpY, _ = mc.draggerContext(ctxCutter, query=True, dragPoint=True)
        distanceA = (vpX - screenX)
        rotateRun = (distanceA) /4
        if rotateRun > 360 :
            rotateRun = 360
        elif rotateRun < -360 :
            rotateRun = -360

        mc.setAttr((currentCutterName + '.rotateY'),rotateRun)
        mc.refresh(cv=True,f=True)

    elif(modifiers == 4):
        #print 'ctrl selSample'
        vpX, vpY, _ = mc.draggerContext(ctxCutter, query=True, dragPoint=True)
        distanceB = vpX - screenX
        scaleCheck = distanceB / 100
        scaleRun = currentScaleRecord + scaleCheck
        if scaleRun > 5:
            scaleRun = 5
        elif scaleRun < 0:
            scaleRun = 0.1
        mc.floatSliderGrp('cutterScaleSlider',  e=1 ,v = scaleRun )
        mc.setAttr(('sampleLoc.scaleX'),scaleRun)
        mc.setAttr(('sampleLoc.scaleY'),scaleRun)
        mc.setAttr(('sampleLoc.scaleZ'),scaleRun)
        mc.refresh(cv=True,f=True)
    elif(modifiers == 8):
        vpX, vpY, _ = mc.draggerContext(ctxCutter, query=True, dragPoint=True)
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
        hitFacePtr = om.MScriptUtil().asIntPtr()
        hitFace = []
        beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
        member =mc.editDisplayLayerMembers((beseMesh+'_BoolResult'),q=True)
        snapMesh = (beseMesh +'_boolShape')
        checkList = []
        checkList.append('snapLive')
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

                    hitFaceName = (mesh + '.f[' + str(hitFace) +']')

                cpX,cpY,cpZ = getPolyFaceCenter(hitFaceName)
                # bug, for some reason it doesn't like value is 0
                if cpX == 0:
                    cpX = 0.000001
                if cpY == 0:
                    cpY = 0.000001
                if cpZ == 0:
                    cpZ = 0.000001
                mc.setAttr(('sampleLoc.translateX'),cpX)
                mc.setAttr(('sampleLoc.translateY'),cpY)
                mc.setAttr(('sampleLoc.translateZ'),cpZ)
                mc.refresh(cv=True,f=True)
    else:
        vpX, vpY, _ = mc.draggerContext(ctxCutter, query=True, dragPoint=True)
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

        hitFacePtr = om.MScriptUtil().asIntPtr()
        hitFace = []
        beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
        member =mc.editDisplayLayerMembers((beseMesh+'_BoolResult'),q=True)
        snapMesh = (beseMesh +'_boolShape')
        checkList = []
        checkList.append('snapLive')
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
                    finalX = x
                    finalY = y
                    finalZ = z
                # bug, for some reason it doesn't like value is 0
                if finalX == 0:
                    finalX = 0.000001
                if finalY == 0:
                    finalY = 0.000001
                if finalZ == 0:
                    finalZ = 0.000001
                mc.setAttr('sampleLoc.translateX', finalX)
                mc.setAttr('sampleLoc.translateY', finalY)
                mc.setAttr('sampleLoc.translateZ',finalZ)
                hitFaceName = (mesh + '.f[' + str(hitFace) +']')
                rx, ry, rz = getFaceAngle(hitFaceName)
                mc.setAttr('sampleLoc.rotateX', rx)
                mc.setAttr('sampleLoc.rotateY', ry)
                mc.setAttr('sampleLoc.rotateZ', rz)
                mc.select('sampleLoc')
                mc.refresh(cv=True,f=True)



def onPressCutter():
    global ctxCutter
    global screenX,screenY
    vpX, vpY, _ = mc.draggerContext(ctxCutter, query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY
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
    finalX = []
    finalY = []
    finalZ = []
    shortDistance = 10000000000
    distanceBetween = 1000000000
    hitFacePtr = om.MScriptUtil().asIntPtr()
    hitFace = []
    checkList = []
    checkList.append('snapLive')
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
            mc.setAttr('sampleLoc.translateX', finalX)
            mc.setAttr('sampleLoc.translateY', finalY)
            mc.setAttr('sampleLoc.translateZ',finalZ)
            hitFaceName = (mesh + '.f[' + str(hitFace) +']')
            rx, ry, rz = getFaceAngle(hitFaceName)
            mc.setAttr('sampleLoc.rotateX', rx)
            mc.setAttr('sampleLoc.rotateY', ry)
            mc.setAttr('sampleLoc.rotateZ', rz)
            mc.setAttr('sampleLoc.scaleX', 1)
            mc.setAttr('sampleLoc.scaleY', 1)
            mc.setAttr('sampleLoc.scaleZ', 1)
            mc.select('sampleLoc')
            mc.refresh(cv=True,f=True)



def getFaceAngle(faceName):
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


def reTarget():
    newTarget = mc.ls(sl=1,fl=1)
    if len(newTarget) == 1:
        beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)

        #record symmetry
        getSymX = 0
        getSymY = 0
        getSymZ = 0

        if mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
            getSymX =  mc.getAttr(beseMesh+'.symmetryX')
        if mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
            getSymY =  mc.getAttr(beseMesh+'.symmetryY')
        if mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
            getSymZ =  mc.getAttr(beseMesh+'.symmetryZ')


        bakeCutter("all")
        mc.parent(newTarget, (beseMesh+'_bakeStep'))
        #mc.delete((beseMesh+'_bakeBaseMesh'))
        mc.rename((beseMesh+'_bakeBaseMesh'),(beseMesh+'_temp'))
        mc.parent((beseMesh+'_temp'),w=1)
        mc.rename(newTarget, (beseMesh+'_bakeBaseMesh'))
        mc.rename((beseMesh+'_temp'), (beseMesh+'_old'))
        restoreCutter()


        #apply to new target
        if not mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
            mc.addAttr(beseMesh, ln='symmetryX', at = "long" )
            mc.setAttr((beseMesh+'.symmetryX'),getSymX)
        if not mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
            mc.addAttr(beseMesh, ln='symmetryY', at = "long" )
            mc.setAttr((beseMesh+'.symmetryY'),getSymY)
        if not mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
            mc.addAttr(beseMesh, ln='symmetryZ', at = "long" )
            mc.setAttr((beseMesh+'.symmetryZ'),getSymZ)

        #hide all cage
        cageList = mc.ls((beseMesh + '_cage*'),type='transform')
        for c in cageList:
            mc.setAttr((c+'.visibility'),0)

        #checkSymmetryState
        checkSymX =  mc.getAttr(beseMesh+'.symmetryX')
        checkSymY =  mc.getAttr(beseMesh+'.symmetryY')
        checkSymZ =  mc.getAttr(beseMesh+'.symmetryZ')

        if checkSymX == 1:
            boolSymmetry('x',1)
        elif checkSymX == -1:
            boolSymmetry('x',2)

        if checkSymY == 1:
            boolSymmetry('y',1)
        elif checkSymY == -1:
            boolSymmetry('y',2)

        if checkSymZ == 1:
            boolSymmetry('z',1)
        elif checkSymZ == -1:
            boolSymmetry('z',2)

def getPolyFaceCenter(faceName):
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
    return centerX,centerY,centerZ

def meshBBox():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if beseMesh is not None:
        mesh = (beseMesh +'_bool')
        if mc.objExists(mesh):
            bbox= mc.xform(mesh, q=1, ws=1, bb=1)
            length=math.sqrt((math.pow(bbox[0]-bbox[3],2)+math.pow(bbox[1]-bbox[4],2)+math.pow(bbox[2]-bbox[5],2))/3)
            bestV = length / 10
            mc.floatField( 'cuterPreSize' , e=True ,value=bestV )
            loadSymmetryState()

def checkBaseMeshList():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, ils = True)
    # remove any item not exist in outliner
    if beseMesh is not None:
        for c in beseMesh:
            if not 'NoBaseMeshMenu' in c:
                meshName = c.replace('Menu','BoolGrp')
                if mc.objExists(meshName) == 0:
                    mc.deleteUI(c)
    # load any boolGrp existed in outliner
    beseMeshCheck = mc.ls('*BoolGrp',type='transform')
    if len(beseMeshCheck)>0:
        checkBaseList = mc.optionMenu('baseMeshMenu', query = True, ils = True)
        for b in beseMeshCheck:
            removeGrp = b.replace('BoolGrp','')
            checkSelMesh = mc.menuItem((removeGrp +"Menu"), q=True, ex = True)
            if checkSelMesh == 0:
                mc.menuItem((removeGrp +"Menu"), label = removeGrp ,p = 'baseMeshMenu')
    # remove noBaseMeshMenu if any boolGrp existed
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, ils = True)
    if beseMesh is not None:
        if len(beseMesh) > 1:
            checkNoBase = mc.menuItem('NoBaseMeshMenu', q=True, ex = True)
            if checkNoBase == 1:
                mc.deleteUI("NoBaseMeshMenu")
    else:
        mc.menuItem("NoBaseMeshMenu", label='No Base Mesh' ,p = 'baseMeshMenu')
    #load mesh size
    meshBBox()
    #remove empty display layer
    allLayers = mc.ls(type='displayLayer')
    for a in allLayers:
        if not 'defaultLayer' in a:
            members = mc.editDisplayLayerMembers(a,query=True)
            if members == None:
                mc.delete(a)

def updateSnapState():
        #check snap border state
    mc.makeLive( none=True )
    mc.manipMoveContext('Move',e=True, snapLivePoint= False)
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    mc.button('borderAlginButton',e=True, bgc =  [0.28,0.28,0.28])
    if mc.objExists(beseMesh +'_borderBoxGrp') and mc.objExists(beseMesh +'_borderBox'):
        mc.button('borderAlginButton',e=True, bgc =  [0.3,0.5,0.6])
        mc.makeLive(  beseMesh +'_borderBox' )
        mc.manipMoveContext('Move',e=True, snapLivePoint= True)

def restoreMissingGrps():
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if mc.objExists((beseMesh +'_cutterGrp')) == 0:
        mc.CreateEmptyGroup()
        mc.rename((beseMesh +'_cutterGrp'))
        mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))


def setCutterBaseMesh():
    beseMesh = mc.ls(sl=True,fl=True,type='transform')
    if len(beseMesh) == 1:
        mc.delete(beseMesh[0],ch=1)
        #mc.makeIdentity(beseMesh[0],apply= True, t= 1, r =1, s =1, n= 0,pn=1)
        mc.editDisplayLayerMembers('defaultLayer',beseMesh[0])
        topNode = mel.eval('rootOf '+beseMesh[0])
        meshName = []
        if 'BoolGrp' in topNode:
            removeGrp = topNode.replace('BoolGrp','')
            removeParent = removeGrp.replace('|','')
            meshName = removeParent
        else:
            meshName =  beseMesh[0]
        meshName = meshName.replace('|','')
        checkSelMesh = mc.menuItem((meshName +"Menu"), q=True, ex = True)
        if checkSelMesh == 0:
            mc.menuItem((meshName +"Menu"), label = meshName ,p = 'baseMeshMenu')
            #mc.optionMenu('baseMeshMenu|OptionMenu', q=True, v=True) # to get the name of the current value
            #mc.optionMenu('baseMeshMenu|OptionMenu', q=True, sl=True) # to get the current index
            #mc.optionMenu('baseMeshMenu|OptionMenu', e=True, sl = 3 )# to change the current value
            mc.optionMenu('baseMeshMenu', e=True, v = meshName )# to change the current value
    beseMesh = mc.optionMenu('baseMeshMenu', query = True, v = True)
    if beseMesh != 'No Base Mesh':
        if mc.objExists(beseMesh):
            checkPivot = mc.xform(beseMesh, q =True, sp=True,ws=True)
            if mc.objExists((beseMesh +'_cutterGrp')) == 0:
                mc.CreateEmptyGroup()
                mc.rename((beseMesh +'_cutterGrp'))
            if mc.objExists((beseMesh +'BoolGrp')) == 0:
                mc.CreateEmptyGroup()
                mc.rename((beseMesh +'BoolGrp'))
            if mc.objExists((beseMesh +'_bool')) ==0:
                mc.polyCube(w = 0.0001, h=0.0001, d=0.0001 ,sx =1 ,sy= 1, sz= 1)
                mc.rename(beseMesh +'_preSubBox')
                mc.polyCube(w = 0.0001, h=0.0001, d=0.0001 ,sx =1 ,sy= 1, sz= 1)
                mc.rename(beseMesh +'_afterSubBox')
                mc.polyCube(w = 0.0001, h=0.0001, d=0.0001 ,sx =1 ,sy= 1, sz= 1)
                mc.rename(beseMesh +'_preUnionBox')
                #move pre box to base mesh center prevent error
                bbox= mc.xform(beseMesh, q=1, ws=1, bb=1)
                bX = (bbox[3]-bbox[0])/2 + bbox[0]
                bY = (bbox[4]-bbox[1])/2 + bbox[1]
                bZ = (bbox[5]-bbox[2])/2 + bbox[2]
                attrList = ['translateX','translateY','translateZ']
                preBoxList = [(beseMesh +'_preSubBox'),(beseMesh +'_afterSubBox'),(beseMesh +'_preUnionBox')]
                posList = [bX,bY,bZ]
                for p in preBoxList:
                    for i in range(0,3):
                        mc.setAttr(( p + '.' + attrList[i]),posList[i])
                subNode= mc.polyCBoolOp((beseMesh ), (beseMesh +'_preSubBox') , op= 2, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_bool'))
                mc.rename(subNode[0],(beseMesh +'_myBoolSub'))
                unionNode = mc.polyCBoolOp((beseMesh +'_myBoolSub'), (beseMesh +'_preUnionBox') , op= 1, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_union'))
                mc.rename(unionNode[0],(beseMesh +'_myBoolUnion'))
                subNode= mc.polyCBoolOp((beseMesh +'_myBoolUnion'), (beseMesh +'_afterSubBox') , op= 2, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_bool'))
                mc.rename(subNode[0],(beseMesh +'_bool'))
                boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1,ac=1),type='polyCBoolOp')
                boolNode = set(boolNode)
                #hack it by check '_', this is used by other group
                listClean = []
                for b in boolNode:
                    if '_' not in b:
                        listClean.append(b)

                for l in listClean:
                    checkNodeType = mc.nodeType(l)
                    if checkNodeType == 'polyCBoolOp':
                        checkOp = mc.getAttr( l +'.operation')
                        if checkOp == 2:
                            if mc.objExists(beseMesh +'_mySubs'):
                                mc.rename(l,(beseMesh +'_myCut'))
                            else:
                                mc.rename(l,(beseMesh +'_mySubs'))
                        else:
                            mc.rename(l,(beseMesh +'_myUnion'))

                baseNodes = mc.listRelatives(beseMesh, ad = True, f = True)
                baseTransNode = mc.ls(baseNodes,type = 'transform')
                baseMeshNode = mc.ls(baseNodes,type = 'mesh')
                mc.setAttr((baseMeshNode[0]+'.intermediateObject'), 0)
                mc.parent(baseMeshNode[0],(beseMesh +'BoolGrp'),s=True)
                mc.delete(beseMesh)
                mc.pickWalk(d='up')
                mc.rename(beseMesh)
                mc.setAttr((beseMesh + '.visibility'), 0)
            if not mc.objExists((beseMesh +'_BoolResult')):
                mc.createDisplayLayer(name = (beseMesh +'_BoolResult'))
            mc.editDisplayLayerMembers( (beseMesh +'_BoolResult'),(beseMesh +'_bool')) # store my selection into the display layer
            mc.setAttr((beseMesh +'_BoolResult.displayType'),2)

            checkList = ['_cutterGrp','_preSubBox','_preUnionBox','_myBoolUnion','_bool', '', '_afterSubBox','_myBoolSub' ]
            for c in checkList:
                checkGrp = mc.ls((beseMesh + c), l=True)
                if len(checkGrp)>0:
                    if 'BoolGrp' not in checkGrp[0]:
                        mc.parent(checkGrp[0],(beseMesh +'BoolGrp'))

            mc.select(cl=True)
            mc.setAttr((beseMesh +'BoolGrp.visibility'),1)
            mc.move(checkPivot[0],checkPivot[1],checkPivot[2], (beseMesh + ".scalePivot"),(beseMesh + ".rotatePivot"), absolute=True)
            meshBBox()
    else:
        removeNotExistBaseMesh()
jwSpeedCutUI()
