# All Imports
import re
import os
import math as math
import maya.mel as mel
import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMaya as om
from functools import partial
import maya.OpenMayaUI as omu
import pymel.core.datatypes as dt

class NP():
	def __init__(self):
		self.HighEdges = []
		self.hotkeysList = [{"name":"GrowLoop","command":"import NitroPoly;NitroPoly.NP().growLoop()"},
							{"name":"ShrinkLoop","command":"import NitroPoly;NitroPoly.NP().shrinkLoop()"},
							
							{"name":"GrowRing","command":"import NitroPoly;NitroPoly.NP().growRing()"},
							{"name":"ShrinkRing","command":"import NitroPoly;NitroPoly.NP().shrinkRing()"},
							
							{"name":"DotLoop","command":"import NitroPoly;NitroPoly.NP().dotLoop()"},
							{"name":"DotRing","command":"import NitroPoly;NitroPoly.NP().dotRing()"},
							
							{"name":"SelecthardEdge","command":"import NitroPoly;NitroPoly.NP().hardEdge()"},
							{"name":"SelectUVEdge","command":"import NitroPoly;NitroPoly.NP().uvEdge()"},
							{"name":"PointToPoint","command":"import NitroPoly;NitroPoly.NP().pointTopoint()"},
							{"name":"FaceFill","command":"import NitroPoly;NitroPoly.NP().faceBorderSel()"},
							
							{"name":"CleanCombine","command":"import NitroPoly;NitroPoly.NP().CombineClean()"},
							{"name":"CleanDetach","command":"import NitroPoly;NitroPoly.NP().detatchClean()"},
							
							{"name":"UniConnect","command":"import NitroPoly;NitroPoly.NP().UniConnector()"},
							{"name":"uniRemove","command":"import NitroPoly;NitroPoly.NP().UniRemover()"},
							
							{"name":"basePivot","command":"import NitroPoly;NitroPoly.NP().basepivot()"},
							{"name":"WorldPivot","command":"import NitroPoly;NitroPoly.NP().worldPivot()"},
							{"name":"UnFreezeTransform","command":"import NitroPoly;NitroPoly.NP().UnFreezeTranslate()"},
							{"name":"MoveToOrigin","command":"import NitroPoly;NitroPoly.NP().moveToOrigin()"},
							
							{"name":"CornerRot_Plus","command":"import NitroPoly;NitroPoly.NP().corner45Plus()"},							
							{"name":"CornerRot_Minus","command":"import NitroPoly;NitroPoly.NP().corner45Minus()"},
								
							{"name":"F2Extend","command":"import NitroPoly;NitroPoly.NP().edgeExtend()"},

							{"name":"Bevel_Plus","command":"import NitroPoly;NitroPoly.NP().bevelModifierPlus()"},
							{"name":"Bevel_Minus","command":"import NitroPoly;NitroPoly.NP().bevelModifierMinus()"},																					
							
							{"name":"CornerConnect","command":"import NitroPoly;NitroPoly.NP().cornerConnect()"},
							{"name":"EndConnect","command":"import NitroPoly;NitroPoly.NP().endConnect()"},
							{"name":"DistanceConnect","command":"import NitroPoly;NitroPoly.NP().distConnect()"},
							{"name":"FlowConnect","command":"import NitroPoly;NitroPoly.NP().flowConnect()"},
							{"name":"VertEdge","command":"import NitroPoly;NitroPoly.NP().vertexToEdge()"},
							

							{"name":"Space","command":"import NitroPoly;NitroPoly.NP().spaceloop()"},
							{"name":"Straight","command":"import NitroPoly;NitroPoly.NP().straightloop()"},
							
							{"name":"Circle","command":"import NitroPoly;NitroPoly.NP().circle()"},
							{"name":"Geopoly","command":"import NitroPoly;NitroPoly.NP().geoPoly()"},
							
							{"name":"ViewPlanar","command":"import NitroPoly;NitroPoly.NP().viewPlanar()"},
							{"name":"MakePlanar","command":"import NitroPoly;NitroPoly.NP().makePlanar()"},
							
							{"name":"Center","command":"import NitroPoly;NitroPoly.NP().centerloop()"},
							{"name":"Relax","command":"import NitroPoly;NitroPoly.NP().relaxLoop()"}]

	##################
	# hot keys setting
	##################
	def hotkeyMaker(self,hotkey):
			name = hotkey['name']
			command = hotkey['command']
			try:
				cmds.runTimeCommand(name, c=command, cat='NitroPoly', cl='python')
			except:
				pass
							
	####################
	# UI Code
	####################
	def UI(self):
		if cmds.window('winModelingToolkit', exists=True) or cmds.dockControl('Nitropoly',exists=True):

			try:
				cmds.deleteUI('winModelingToolkit')
				cmds.deleteUI('Nitropoly')
				cmds.windowPref( 'winModelingToolkit', ra=True )
			except:
				pass

		#-------------------
		# UI Sizes and Color
		#-------------------
		winWidth = 370
		buttonHeight = 22
		allowedAreas = ['right', 'left']
		
		#Quick Color Function
		def color01(r,g,b):
			return (r/255.0,g/255.0,b/255.0)
		
		background = (0.5,0.5,0.5)
		frameColor =color01(39,39,47)
		
		buttonColor = color01(48,57,66)
		plusClr = color01(89,98,106)
		minClr =color01(63,72,82)
		devClr = color01(11,18,28)

		# Window and dock control creation
		WinNitroPoly = cmds.window('winModelingToolkit', title='NitroPoly 1.1', wh=[1000, 300],mxb=0,mnb=0,rtf=1)
		modelLayout = cmds.columnLayout(adjustableColumn=True,parent = 'winModelingToolkit')
		cmds.dockControl("Nitropoly",nbg=0,area='left',l="Nitropoly 2.0", content='winModelingToolkit', allowedArea=allowedAreas)

		def frameCollapseChanged(modelLayout):
			cmds.evalDeferred("cmds.window('winModelingToolkit', e=1, h=sum([eval('cmds.' + cmds.objectTypeUI(child) + '(\\'' + child + '\\', q=1, h=1)') for child in cmds.columnLayout('" + modelLayout + "', q=1, ca=1)]))")
			
		####################
		# Modiy selection
		####################
		cmds.frameLayout( label="Modify Selection",w=160, cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)),bgc=frameColor)
		cmds.separator(h=1)
		cmds.rowColumnLayout(numberOfColumns=4,columnSpacing=[(1, 8),(2, 2),(3, 5),(4, 2)])
		cmds.button(label="Grow Loop",w=85,h=buttonHeight, c=lambda x: self.growLoop(),bgc=plusClr)
		cmds.button(label="Shrink Loop", w=85,h=buttonHeight, c=lambda x: self.shrinkLoop(),bgc=minClr)
		cmds.button(label="Grow Ring",w=85,h=buttonHeight, c=lambda x: self.growRing(),bgc=plusClr)
		cmds.button(label="Shrink Ring", w=85,h=buttonHeight, c=lambda x: self.shrinkRing(),bgc=minClr)
		cmds.setParent( '..' )

		cmds.separator(h=1)
		cmds.rowColumnLayout(numberOfColumns=4,columnSpacing=[(1, 8),(2, 1),(3, 10)])
		self.intGap = cmds.intField(v=1, minValue=1, maxValue=100, step=1,w=30)
		cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
		cmds.button(label="Dot Loop",w=winWidth/2-30,h=buttonHeight, c=lambda x: self.dotLoop(),bgc=plusClr)
		cmds.button(label="Dot Ring", w=winWidth/2-36,h=buttonHeight, c=lambda x: self.dotRing(),bgc=minClr)
		cmds.setParent( '..' )
		cmds.setParent( '..' )
		
		cmds.separator(h=1)
		cmds.rowColumnLayout(numberOfColumns=4,columnSpacing=[(1, 8),(2, 2),(3, 5),(4, 2)])
		cmds.button(label="Sel hard Edge", w=85,h=buttonHeight, c=lambda x: self.hardEdge(),bgc=buttonColor)
		cmds.button(label="Sel UV Edge",w=85,h=buttonHeight, c=lambda x: self.uvEdge(),bgc=buttonColor)

		cmds.button(label="Point to Point", w=85,h=buttonHeight, c=lambda x: self.pointTopoint(),bgc=buttonColor)
		cmds.button(label="Face Fill",w=85,h=buttonHeight, c=lambda x: self.faceBorderSel(),bgc=buttonColor)
		cmds.setParent( '..' )
		cmds.separator(h=1,w=1)
		cmds.setParent( '..' )

		#######################################
		# Mesh and Uni-Connector / Uni-Remover
		#######################################
		cmds.frameLayout( label="Mesh and Uni-Connector / Uni-Remover", cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)),bgc=frameColor)
		cmds.separator(h=1)
		cmds.rowColumnLayout(numberOfColumns=4,columnSpacing=[(1, 8),(2, 2),(3, 5),(4, 2)])
		cmds.button(label='Clean Combine',h=buttonHeight,w=85,c=lambda x: self.CombineClean(),bgc=plusClr)
		cmds.button(label='Clean Detach',h=buttonHeight,w=85,c=lambda x: self.detatchClean(),bgc=minClr)
		cmds.button(label='UniConnect',h=buttonHeight,w=85,c=lambda x: self.UniConnector(),bgc=plusClr)
		cmds.button(label='UniRemove',h=buttonHeight,w=85,c=lambda x: self.UniRemover(),bgc=minClr)
		
		cmds.setParent( '..' )
		cmds.separator(h=1)
		cmds.setParent( '..' )
		cmds.setParent( '..' )
		
		##########################################
		# Pivot Tools and UnFreeze Transformations
		##########################################
		cmds.frameLayout( label="Pivot and UnFreeze Transformations", cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)),bgc=frameColor)
		cmds.separator(h=1)
		cmds.rowColumnLayout(numberOfColumns=4,columnSpacing=[(1, 8),(2, 2),(3, 5),(4, 2)])
		cmds.button(label='Base Pivot',h=buttonHeight,w=85,c=lambda x: self.basepivot(),bgc=buttonColor)
		cmds.button(label='World Pivot',h=buttonHeight,w=85,c=lambda x: self.worldPivot(),bgc=buttonColor)
		cmds.button(label='UF | Translate',h=buttonHeight,w=85,c=lambda x: self.UnFreezeTranslate(),bgc=buttonColor)	
		cmds.button(label='Move To Origin',h=buttonHeight,w=85,c=lambda x: self.moveToOrigin(),bgc=buttonColor)	
		cmds.setParent( '..' )
		cmds.separator(h=1)
		cmds.setParent( '..' )
		cmds.setParent( '..' )

		
		################
		# Topology Tools
		################				
		cmds.frameLayout( label="Topology Tools", cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)),bgc=frameColor)
		cmds.separator(h=1)
		
		cmds.rowColumnLayout(numberOfColumns=2,columnSpacing=[(1, 8),(2, 5)])
		
		cmds.button(label='转角 45 +',h=buttonHeight,w=winWidth/2-15,c=lambda *args: self.corner45(True),bgc=plusClr)
		cmds.button(label='转角 45 -',h=buttonHeight,w=winWidth/2-10,c=lambda *args: self.corner45(False),bgc=minClr)
		cmds.setParent( '..' )
		cmds.separator(h=1)

		cmds.rowColumnLayout(numberOfColumns=3,columnSpacing=[(1, 8),(2, 5),(3, 5)])
		self.F2Threshold = cmds.floatSliderGrp(v=0.001,cw2= [40,0], field = 1, minValue=0.001, maxValue=1.0, step=0.001,w=40,h=10)
		cmds.button(label='F2 Extend',h=buttonHeight,w=winWidth-65,c=lambda x: self.edgeExtend() ,bgc=buttonColor)
		cmds.setParent( '..' )
		cmds.separator(h=1)
		cmds.rowColumnLayout(numberOfColumns=3,columnSpacing=[(1, 8),(2, 5),(3, 5)])
		self.BevelThreshold = cmds.floatSliderGrp(v=0.1,cw2= [40,0], field = 1, minValue=0.02, maxValue=1.0, step=0.01,w=40,h=10)
		cmds.button(label="Bevel +",w=winWidth/2 -30,h=buttonHeight, c=lambda *args: self.bevelModifier(True),bgc=plusClr)
		cmds.button(label="Bevel -", w=winWidth/2-40,h=buttonHeight, c=lambda *args: self.bevelModifier(False),bgc=minClr)
		cmds.setParent( '..' )
		cmds.separator(h=1)
		cmds.setParent( '..' )
		cmds.setParent( '..' )

		################
		# Connect Tools
		################
		cmds.frameLayout( label="Connect Tools", w= 180, cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)),bgc=frameColor)
		cmds.separator(h=1)

		cmds.rowColumnLayout(numberOfColumns=4,columnSpacing=[(1, 8),(2, 5),(3, 5),(4, 5)])
		self.StitchThreshold = cmds.floatSliderGrp(v=0.1,cw2= [40,0], field = 1, minValue=0.02, maxValue=1.0, step=0.02,w=40,h=10)
		self.EdgeLoopNumber = cmds.textField(text="No EdgeLoop",w=100,ed=0,bgc=frameColor)
		cmds.button(label='Load Edge Loop',h=buttonHeight,w=90,c=lambda x: self.loadEdgeLoop(),bgc=plusClr)
		cmds.button(label='Cut and Stitch',h=buttonHeight,w=105,c=lambda x: self.cutAndStitch(),bgc=minClr)
		cmds.setParent( '..' )
		cmds.separator(h=1)
		
		cmds.rowColumnLayout(numberOfColumns=5,columnSpacing=[(1, 8),(2, 5),(3, 5),(4, 5),(5, 5)])

		cmds.button(label='Corner',h=buttonHeight,w=66,c=lambda x: self.cornerConnect(),bgc=buttonColor)
		cmds.button(label='Quad end',h=buttonHeight,w=66,c=lambda x: self.endConnect(),bgc=buttonColor)
		cmds.button(label='Distance',h=buttonHeight,w=66,c=lambda x: self.distConnect(),bgc=buttonColor)
		cmds.button(label='Flow',h=buttonHeight,w=66,c=lambda x: self.flowConnect(),bgc=buttonColor)
		cmds.button(label='点到边',h=buttonHeight,w=66,c=lambda x: self.vertexToEdge(),bgc=buttonColor)	
		cmds.setParent( '..' )
		
		cmds.separator(h=1)

		cmds.rowColumnLayout(numberOfColumns=3,columnSpacing=[(1, 8),(2, 5),(3, 5)])
		self.vertexNumber = cmds.textField(text="No Vertex Loaded",w=100,ed=0,bgc=frameColor)
		cmds.button(label='Load Vertex',h=buttonHeight,w=90,c=lambda x: self.loadVertex(),bgc=plusClr)
		cmds.button(label='Connect to Vertex',h=buttonHeight,w=150,c=lambda x: self.connectToVertex(),bgc=minClr)
		cmds.setParent( '..' )
		cmds.separator(h=1)
		cmds.setParent( '..' )
		cmds.setParent( '..' )

		#############
		# Loop Tools
		#############
		cmds.frameLayout( label="Loop Tools - Iterable : Click repeatedly for better result", cll=True,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)),bgc=frameColor)
		cmds.separator(h=1)
		
		cmds.rowColumnLayout(numberOfColumns=4,columnSpacing=[(1, 8),(2, 2),(3, 5),(4, 2)])
		cmds.button(label="Space",w=85,h=buttonHeight,c=lambda x: self.spaceloop(),bgc=buttonColor)
		cmds.button(label="Straight",w=85,h=buttonHeight,c=lambda x: self.straightloop(),bgc=buttonColor)
		cmds.button(label="Circle",w=85,h=buttonHeight,c=lambda x: self.circle(),bgc=buttonColor)
		cmds.button(label="Geo Poly",w=85,h=buttonHeight,c=lambda x: self.geoPoly(),bgc=buttonColor)
		cmds.setParent( '..' )
		
		cmds.rowColumnLayout(numberOfColumns=4,columnSpacing=[(1, 8),(2, 2),(3, 5),(4, 2)])
		cmds.button(label="View Planar",w=85,h=buttonHeight,c=lambda x: self.viewPlanar() ,bgc=buttonColor)
		cmds.button(label="Average Planar",w=85,h=buttonHeight,c=lambda x: self.makePlanar() ,bgc=buttonColor)
		cmds.button(label='Center',h=buttonHeight,w=85,c=lambda x: self.centerloop(),bgc=buttonColor)
		cmds.button(label='Relax',h=buttonHeight,w=85,c=lambda x:self.relaxLoop(),bgc=buttonColor)
		cmds.setParent( '..' )
		cmds.separator(h=1)
		cmds.setParent( '..' )
		cmds.setParent( '..' )

		#########
		# About
		#########
		cmds.frameLayout( label="Info",w=180, cll=0,cl=0,ec=partial(frameCollapseChanged, str(modelLayout)), cc=partial(frameCollapseChanged, str(modelLayout)),bgc=frameColor)	
		cmds.rowColumnLayout(numberOfColumns=1,columnSpacing=[(1, 0)])
		cmds.button(label=' Click here for Tool Help and Features',h=25,w=winWidth,c=lambda x:self.abt(),bgc=devClr)
		cmds.setParent( '..' )
		cmds.setParent( '..' )

		cmds.showWindow()

		# Resetting
		winHeight = 0
		for child in cmds.columnLayout(modelLayout, q=1, ca=1):
			winHeight += eval('cmds.' + cmds.objectTypeUI(child) + '("' + child + '", q=1, h=1)')
		WinNitroPoly = cmds.window("winModelingToolkit", edit=1, widthHeight=(winWidth, winHeight),s=1)
		
			
	###############
	# Util Function
	###############
	def splitString(self,comp):
		return int(str(comp).split('[')[1].split(']')[0])

	def inLineMessage(self,message,fadeTime = 3):
		pm.inViewMessage( amg='Error : <hl style=\"color:#FF0000;\">' + message + '</hl>', pos='midCenter', fade=True,bkc = 0X11550000,fit = fadeTime)
		pm.warning(message)
		
	#*****************************************
	# get Functions
	#*****************************************
	def getSandT(self,type="t"):
		try:
			"s for shape and t for Transform"
			outVal = ""
			selection = om.MSelectionList()
			om.MGlobal.getActiveSelectionList(selection)
			selection_iter = om.MItSelectionList(selection)
			obj = om.MObject()
			
			while not selection_iter.isDone():
				selection_iter.getDependNode(obj)
				dagPath = om.MDagPath.getAPathTo(obj)
				dagName = str(dagPath.fullPathName())
				if len(dagName.split("|")) >2:
					if type=="s":
						outVal = dagName.split("|")[-1]
					elif type=="t":
						outVal = dagName.split("|")[-2]
				else:
					outVal = dagName.split("|")[-1]
				selection_iter.next()
		except:
			pass
		return outVal

	def getAllSel(self):
		sel = om.MSelectionList()
		om.MGlobal.getActiveSelectionList(sel)
		names = []
		sel.getSelectionStrings(names)
		ss= cmds.ls(names,fl=1)
		return ss
		
	def isolateFirstEdge(self, sel):
		vertStartandEnd = []
		for s in sel:
			cmds.select(s)
			vert = cmds.ls(cmds.polyListComponentConversion(cmds.ls(sl=1,fl=1),fe=1,tv=1),fl=1)
			V1 = vert[0]
			edgeV = cmds.ls(cmds.polyListComponentConversion(V1,fv=1,te=1),fl=1)
			inter = list(set(sel) & set(edgeV))
			if len(inter) == 1:
				vertStartandEnd.append(V1)
			V2 = vert[1]
			edgeV = cmds.ls(cmds.polyListComponentConversion(V2,fv=1,te=1),fl=1)
			inter = list(set(sel) & set(edgeV))
			if len(inter) == 1:
				vertStartandEnd.append(V2)
			
		return vertStartandEnd

	def getOrderedSelection(self):
		'''
		Return index 0 = Edge Order
		Return index 1 = Vertex Order
		getOrderedSelection()[index]
		'''
		sel = self.getAllSel()
		orSel = sel
		allVert = cmds.ls(cmds.polyListComponentConversion(sel,tv=1),fl=1)
		vertStartandEnd = self.isolateFirstEdge(sel)
		
		#Check is a loop
		if vertStartandEnd == []:
			vertStartandEnd = self.isolateFirstEdge(orSel[:-1])
		
		vertOrder=[]
		edgeOrder=[]
		vertOrder.append(vertStartandEnd[0])
		pm.select(vertOrder)
	
		for i in range(len(sel)):
			edgeV = cmds.ls(cmds.polyListComponentConversion(str(vertOrder[-1]),fv=1,te=1),fl=1)
			inter = list(set(sel) & set(edgeV))
			if len(inter) == 1:
				edgeOrder.append(str(inter[0]))
				sel = list(filter(lambda x : x != str(inter[0]), sel))
				edgeV = cmds.ls(cmds.polyListComponentConversion(inter,fe=1,tv=1),fl=1)
				bl = list(set(edgeV) - set(vertOrder))
				vertOrder.append(str(bl[0]))
		cmds.select(orSel)
		return edgeOrder,vertOrder

	def getEdgeGroup(self):
		selEdges = self.getAllSel()
		trans = selEdges[0].split(".")[0]
		e2vInfos = cmds.polyInfo(selEdges, ev=True)
		
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
			f= map(lambda x: (trans +".e["+ str(x) +"]"), f)
			retEdges.append(f)

		return retEdges
		
	def GetEdgeDirection(self,Edge):
		#Calculating the first and last Position
		EdgeNumber = int(Edge.split("[")[-1].split("]")[0])
		EdgeConvert = pm.polyListComponentConversion(Edge,tv=1)
		pm.select(EdgeConvert)
		verts = self.getAllSel()
		V1 = pm.PyNode(verts[0]).getPosition(space = 'world')
		V2 = pm.PyNode(verts[1]).getPosition(space = 'world')
		dist = dt.length(V2 - V1)
		pm.select(Edge)
		
		#Find EdgeDirection
		cmds.polySplit( ip=[(EdgeNumber, 0.1)],ch=0)
		lastVert = str(verts[0].split(".")[0])+'.vtx['+ str(cmds.polyEvaluate(v=1)) + ']'
		pm.select(lastVert)
		lastVertPos = pm.selected(fl=1)[0].getPosition(space="world")
		pm.undo()
		pm.undo()
	
	
		FPCheck = dt.length(lastVertPos - V1)
		LPCheck = dt.length(lastVertPos - V2)
		FinalVert = [verts[0], verts[1]]
		if FPCheck > LPCheck:
			FinalVert = [verts[1], verts[0]]
			
		return FinalVert

	def RadiusSelect(self,radius):
	    # Set the Radius Selection
	    cmds.softSelect(sse=1,ssd = radius * 100)
	    
	    #Grab the selection
	    selection = om.MSelectionList()
	    softSelection = om.MRichSelection()
	    om.MGlobal.getRichSelection(softSelection)
	    softSelection.getSelection(selection)
	    dagPath = om.MDagPath()
	    component = om.MObject()
	    
	    iter = om.MItSelectionList( selection,om.MFn.kMeshVertComponent )
	    vertsList = []
	    while not iter.isDone(): 
	        iter.getDagPath( dagPath, component )
	        dagPath.pop()
	        node = dagPath.fullPathName()
	        fnComp = om.MFnSingleIndexedComponent(component)   
	     
	        for i in range(fnComp.elementCount()):
	            vertsList.append('%s.vtx[%i]' % (node, fnComp.element(i)))
	        iter.next()
	        
	    #Resetting the softselection        
	    cmds.softSelect(sse=0)
	    return vertsList
    
	def getClosestVert(self,threshold):
		sel = self.getAllSel()
		pm.select(self.RadiusSelect(threshold))
		allVerts = self.getAllSel()
		allVerts.remove(sel[0])

		V1 = cmds.xform(sel[0],q=1,ws=1,t=1)	
		distlist = {}
		for V in allVerts:
			V2 = cmds.xform(V,q=1,ws=1,t=1)
			distance = math.sqrt(sum((V1 - V2)**2 for V1, V2 in zip(V1, V2)))* threshold
			if distance < threshold:
				distlist[V] = distance
		
		closestVert= ""
		if distlist:
			closestVert = reduce(lambda x,y: x if distlist[x]<=distlist[y] else y, distlist.iterkeys())	
		return closestVert
		
	def getOppositeEdge(self):
		sel = self.getAllSel()
		V1 = cmds.ls(cmds.polyListComponentConversion(sel,tv=1),fl=1)
		E1 = cmds.ls(cmds.polyListComponentConversion(V1,te=1),fl=1)
		V2 = cmds.ls(cmds.polyListComponentConversion(E1,tv=1),fl=1)

		facelist = cmds.ls(cmds.polyListComponentConversion(sel,tf=1),fl=1)
		innerFace = []
		for f in facelist:
			toVert = cmds.ls(cmds.polyListComponentConversion(f,tv=1),fl=1)
			if len(toVert) == 6:
				innerFace.append(f)
		if len(innerFace) != 1: return
		F1 = cmds.ls(cmds.polyListComponentConversion(innerFace[0],tv=1),fl=1)
		finalVert = list(set(F1) - set(V2))
		oppositeEdge = cmds.ls(cmds.polyListComponentConversion(finalVert,te=1,internal=1),fl=1)

		return oppositeEdge

	############################
	# Selection modes
	############################
	def vertexMode(self):
		sel = self.getSandT("t")
		if sel =="":return
		mel.eval('resetPolySelectConstraint;')
		mel.eval('doMenuComponentSelection("'+ sel +'", "vertex");')
		
	def edgeMode(self):
		sel = self.getSandT("t")
		if sel =="":return
		mel.eval('resetPolySelectConstraint;')
		mel.eval('doMenuComponentSelection("'+ sel+'", "edge");')

	def borderMode(self):
		sel = self.getSandT("t")
		if sel =="":return
		self.edgeMode()
		mel.eval('polySelectConstraint -m 2 -bo 1;')
		
	def faceMode(self):
		sel = self.getSandT("t")
		if sel =="":return
		mel.eval('resetPolySelectConstraint;')
		mel.eval('doMenuComponentSelection("'+ sel +'", "facet");')

	def shellMode(self):
		sel = self.getSandT("t")
		if sel =="":return
		self.faceMode()
		pm.polySelectConstraint(shell=1)
		
	############################
	# Modify Selection
	############################
	  
	def growLoop(self):
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None: return
		
		firstSel = self.getAllSel()
		mel.eval('polySelectEdgesEveryN "edgeLoopOrBorder" 1;')
		loopEdges = self.getAllSel()
		verts = pm.polyListComponentConversion(firstSel,tv=1)
		edges = cmds.ls(pm.polyListComponentConversion(verts,fv=1,te=1),fl=1)
		edges= map(lambda x: x.encode('ascii'), edges)
		fEdges = list(set(edges) & set(loopEdges))
		pm.select(fEdges,r=1)

		
	def shrinkLoop(self):
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return
		if len(chkEdge) < 3 : return
		
		firstSel = self.getAllSel()
		pm.select(firstSel)
		mel.eval('ConvertSelectionToVertexPerimeter;')
		edges = cmds.ls(pm.polyListComponentConversion(self.getAllSel(),te=1),fl=1)
		edges= map(lambda x: x.encode('ascii'), edges)
		mel.eval('doMenuComponentSelection("'+ self.getSandT("t") +'", "edge");')
		pm.select(list(set(firstSel) - set(edges)))

		# Remove Borders
		for brdr in firstSel:
				vtx = cmds.ls(pm.polyListComponentConversion(brdr, fe=True, tv=True), fl=1 )
				bface = cmds.ls(pm.polyListComponentConversion(vtx, fv=True, tf=True), fl=1 )
				if len(bface) == 4:
					pm.select(brdr,d=1)
		
	def growRing(self):
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return
		
		firstSel = self.getAllSel()
		mel.eval('polySelectEdgesEveryN "edgeRing" 1;')
		loopEdges = self.getAllSel()
		pm.select(firstSel)
		faces = pm.polyListComponentConversion(firstSel,fe=1,tf=1)
		edges = cmds.ls(pm.polyListComponentConversion(faces,ff=1,te=1),fl=1)
		edges= map(lambda x: x.encode('ascii'), edges)
		pm.select(list(set(edges) & set(loopEdges)),r=1)

	def shrinkRing(self):
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return
		if len(chkEdge) < 3 : return
		
		firstSel = self.getAllSel()
		pm.select(firstSel)
		verts = cmds.ls(pm.polyListComponentConversion(self.getAllSel(),tv=1),fl=1)
		pm.select(verts)
		mel.eval('ConvertSelectionToEdgePerimeter;')
		edges = self.getAllSel()
		edges= map(lambda x: x.encode('ascii'), edges)
		pm.select(list(set(firstSel) - set(edges)),r=1)
		
		#Remove Border Edges
		for brdr in firstSel:
			bedge = cmds.ls(pm.polyListComponentConversion(brdr, fe=True, tf=True), fl=1 )
			if len(bedge) == 1:
				pm.select(brdr,d=1)
		
	def dotLoop(self):
		val=2
		# Value to dot
		try:
			val = cmds.intField(self.intGap,q=1,value=1) + 1
		except:
			pass
			
		if cmds.filterExpand(sm = 32, ex = True):
			mel.eval('polySelectEdgesEveryN "edgeLoopOrBorder" '+ str(val) +' ;')
			
		# If it is Faces
		elif cmds.filterExpand(sm = 34, ex = True):
			sel = self.getAllSel()
			if len(sel) != 2: 
				self.inLineMessage("Select Two adjacent Faces.")
				return
			e = pm.polyListComponentConversion(sel,te=1,internal=1)
			if e == []:
				self.inLineMessage("Select Two adjacent Faces.")
				return
				
			pm.select(e)
			mel.eval('polySelectEdgesEveryN "edgeRing" 1;')
			tempEdge = self.getAllSel()
			dotFaces = pm.ls(pm.polyListComponentConversion(tempEdge,tf=1),fl=1)
			edges = pm.polyListComponentConversion(dotFaces,te=1)
			pm.select(edges)
			finalEdges = list(set(self.getAllSel()) - set(tempEdge))
			pm.select(finalEdges[-1])
			self.dotLoop()
			postDotFace = pm.ls(pm.polyListComponentConversion(self.getAllSel(),tf=1),fl=1)
			finalFaces = list(set(postDotFace) & set(dotFaces))
			pm.select(finalFaces)


	def dotRing(self):
		val=2
		try:
			val = cmds.intField(self.intGap,q=1,value=1) + 1
		except:
			pass
			
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return		
		mel.eval('polySelectEdgesEveryN "edgeRing"'+ str(val) +';')

		
	def hardEdge(self):
		sel = self.getAllSel()
		if sel == []:return self.inLineMessage("Select Some objects.")
		sel = sel[0].split(".")[0]
		pm.select(sel + ".e[0]",r=1)
		self.edgeMode()
		mel.eval('polySelectConstraint -mode 3 -type 0x8000 -sm 1;resetPolySelectConstraint;')
		edges = self.getAllSel()
	
	def uvEdge(self):
		sel = self.getAllSel()
		if sel == []:return self.inLineMessage("Select Some objects.")
		sel = sel[0].split(".")[0]
		pm.select(sel + ".e[0]",r=1)
		self.edgeMode()

		#Select the borders
		temp = pm.ls(sel + ".map[*]")

		pm.select(temp)
		mel.eval('polySelectBorderShell 1;')
		mel.eval('PolySelectConvert 20;')
		pEdge = self.getAllSel()

		edgeDeselect = []
		for edg in pEdge:
			uvs = cmds.ls(pm.polyListComponentConversion(edg,tuv=1),fl=1)
			if len(uvs) <=2:
				edgeDeselect.append(edg)

		pm.select(edgeDeselect,d=1)
		self.edgeMode()


	def pointTopoint(self):
		if pm.filterExpand(sm=31,ex=1) is None:return
		
		trans = self.getSandT("t")
		sel = self.getAllSel()

		if len(sel) == 2:
			sv1 = int(str(sel[0]).split("[")[-1].split("]")[0])
			sv2 = int(str(sel[1]).split("[")[-1].split("]")[0])
			self.edgeMode()
			pm.select(d=1)
			shortEdge = pm.polySelect(str(trans), shortestEdgePath=(sv1,sv2))
	
	### Face Fill Section
	def growFace(self):
		sel = self.getAllSel()
		cmds.ConvertSelectionToContainedEdges()
		cmds.ConvertSelectionToEdges()
		self.growRing()
		cmds.ConvertSelectionToFaces()

	def faceBorderSel(self):
		chkFace = cmds.filterExpand(sm = 34, ex = True)
		if chkFace is None:return
			
		# Selection should have only two faces
		sel = self.getAllSel()
		if not len(sel) == 2: return
		sel = map(lambda x: x.encode('ascii'), sel)

		#Storing the object transform name
		trans = self.getSandT("t")
		s1faces = [sel[0]]
		s2faces = [sel[1]]
		cmds.progressWindow(title='Face Fill...', progress=0,max=100, status='Processing...')
		step=1
		for i in range(0,100):
			cmds.progressWindow(e=1, progress=i, status='Calculating...')
		
			cmds.select(s1faces)
			self.growFace()
			s1faces = self.getAllSel()

			pm.select(s2faces)
			self.growFace()
			s2faces = self.getAllSel()
			
			interFaces = list(set(s1faces) & set(s2faces))
			if len(interFaces) == 2:break
			
		cmds.progressWindow(endProgress=1)
		
		# Processing to make the face border
		faceBorder = []
		for i in range(0,2):
			mel.eval('polySelectSp -loop '+sel[i] +' '+interFaces[0]  +';')
			faceBorder.append(self.getAllSel())
			mel.eval('polySelectSp -loop '+sel[i] +' '+interFaces[1]  +';')
			faceBorder.append(self.getAllSel())

		faceBorder = sum(faceBorder, [])
		faceBorder = set(cmds.ls(faceBorder,fl=1))
		faceBorder= map(lambda x: x.encode('ascii'), faceBorder)

		pm.select(d=1)
		# Getting face vertex of sel 0 and 1
		s1vertsCmds = cmds.ls(cmds.polyListComponentConversion(sel[0],ff=1,tv=1),fl=1)
		s2vertsCmds = cmds.ls(cmds.polyListComponentConversion(sel[1],ff=1,tv=1),fl=1)

		# Getting one vertex from each face
		s1verts = pm.ls(cmds.polyListComponentConversion(sel[0],ff=1,tv=1),fl=1)
		s2verts = pm.ls(cmds.polyListComponentConversion(sel[1],ff=1,tv=1),fl=1)
		sv1 = s1verts[0].indices()[0]
		sv2 = s2verts[1].indices()[0]

		# Finding shotest path between two points and removing the sel vertices
		shortEdge = cmds.polySelect(str(trans), shortestEdgePath=(sv1,sv2))
		shortVert = cmds.ls(cmds.polyListComponentConversion(self.getAllSel(),fe=1,tv=1),fl=1)

		combinedVerts = cmds.ls(cmds.polyListComponentConversion(faceBorder,ff=1,tv=1),fl=1)
		vertBool = list(set(shortVert) - set(combinedVerts) )
		
		# Converting the internal verts to faces
		internalFace = cmds.ls(pm.polyListComponentConversion(vertBool,fv=1,tf=1),fl=1)
		borderBool = list(set(internalFace) - set(faceBorder))
		pm.select(borderBool)
		if len(borderBool) < 1:
			pm.select(faceBorder)
			return
		
		#Looping through to get the face selection
		for i in range(0,(len(faceBorder)/4)):
			mel.eval('PolySelectTraverse 1;')
			borderInter = list(set(self.getAllSel()) & set(faceBorder))
			borderSubs = list(set(self.getAllSel()) - set(faceBorder))
			pm.select(borderSubs)
			if len(borderInter) == len(faceBorder):
				finalFaces = list(set(borderSubs) | set(faceBorder))
				pm.select(finalFaces)
				break

	############################
	# Object Selection
	############################
	def CombineClean(self):
		"""Combine selected geometries"""
		selection = cmds.ls(sl=True, type='mesh', dag=True)
		if not selection or selection < 2: return
		
		# get full path
		meshFull = cmds.listRelatives(selection[0], p=True, f=True)
		
		# get parent
		meshParent = cmds.listRelatives(meshFull, p=True, f=True)
		
		meshInWorld = []
		if meshParent:
			meshParent0 = meshParent[0]
			meshInWorld.append(cmds.parent(meshFull, world=True)[0])
		else:
			meshInWorld = meshFull
			
		selection[0] = meshInWorld[0]
		pivots = cmds.xform(meshInWorld[0], q=True, ws=True, a=True, rotatePivot=True)
		newMesh = cmds.polyUnite(selection, o=True)
		newMeshName = cmds.rename(newMesh[0], meshInWorld[0])
		cmds.xform(newMeshName, rotatePivot=pivots)
		if meshParent:
			newMeshName = cmds.parent(newMeshName, meshParent, a=True) 
		# delete history
		cmds.delete(newMeshName, ch=True, hi='none')
	  
	def detatchClean(self):
		if pm.filterExpand(sm=34,ex=1) is None:return
		
		faces = self.getAllSel()
		if faces:
			temp = faces[0].split('.')
			if not faces or len(temp) == 1 or len(faces) == cmds.polyEvaluate(f=True):return
			temp = faces[0].split('.')
			mesh = temp[0]
			temp = cmds.duplicate(mesh, n=mesh, rr=True)
			newMesh = temp[0]
			new = cmds.ls(newMesh+'.f[*]', fl=True)
			cnt = len(new)
			ii = 0
			newFaceDelete = []
			cmds.progressWindow(title='Detaching - Please Wait', progress=0,max=cnt, status='Processing...', isInterruptable=True)
			
			for face in new:
				hit = False
				temp = new[ii].split('.')
				newFace = temp[1]
				o = 0
				cmds.progressWindow(e=1, progress=ii, status='Detatching...')
				for f in faces:					
					temp = faces[o].split('.')
					oldFace = temp[1]
					o = o+1
					if newFace == oldFace:
						hit = True
						break
				if not hit:
					newFaceDelete.append(new[ii])
				ii = ii+1

			cmds.progressWindow(endProgress=1)
			cmds.delete(newFaceDelete)
			cmds.delete(faces)
			cmds.select(newMesh)
			cmds.xform(cp=True)
	  
	def UniConnector(self):
		sel = pm.selected(fl=1)
		# Object mode
		if pm.filterExpand(sm=12) != None:
			mel.eval("dR_multiCutTool;")

		# Vertex mode 
		elif pm.filterExpand(sm=31) != None:
			totalEdge = str(pm.polyEvaluate(e=1))
			#>>>>>>>>>> Target Weld
			if len(sel) == 1:
				mel.eval('MergeVertexTool')
			elif len(sel) > 1:
				#>>>>>>>>>> Merge Verts = 0.01
				if	len(sel)==pm.polyEvaluate(v=1):
					pm.polyMergeVertex(sel,d=0.01,am=1,ch=0)
				#>>>>>>>>>> Connect Tool
				else:
					pm.polyConnectComponents(sel,ch=0)
					sedge = (str(sel[0].split(".")[0])+'.e['+ totalEdge + ":" + str(pm.polyEvaluate(e=1)) + ']')
					cmds.polySoftEdge(sedge,a=180,ch=0)
					pm.select(sel)

		#Edge mode
		elif pm.filterExpand(sm=32) != None:
			border = pm.ls(pm.polyListComponentConversion(sel, fe=True, tf=True), fl=1 )
			#>>>>>>>>>> Subdivide Edge into two
			if len(sel)==1 and len(border) > 1:
				totalVert = str(pm.polyEvaluate(v=1))
				preSel = pm.polyListComponentConversion(fe = 1, tv = 1)
				pm.polySubdivideEdge(ch = 0)
				newVerts = pm.polyListComponentConversion(fe = 1, tv = 1)
				#pm.select(cl=1)
				self.vertexMode()
				pm.select(str(preSel[0].split(".")[0])+'.vtx['+ totalVert + ":" + str(pm.polyEvaluate(v=1)) + ']')
				
			elif len(sel)>1:
				#border edge count
				outerBorder = []
				for e in sel:
					bCheck = pm.ls(pm.polyListComponentConversion(e, fe=True, tf=True), fl=1 )
					if len(bCheck) ==1:
						outerBorder.append(e)
						

				#>>>>>>>>>> Appending polygons
				if len(sel) == 2 and len(outerBorder) == 2:
					pm.polyAppend(a=[sel[0].indices()[0],sel[1].indices()[0]],ch=0)
					
				#>>>>>>>>>>	 Bridging and Caping
				elif len(sel) == len(outerBorder):
					le = pm.ls(pm.polySelectSp(l=1),fl=1)
					if le == sel:
						pm.polyCloseBorder(ch = 0)
					else:
						pm.select(sel)
						pm.polyBridgeEdge( ch=0, divisions = 0)
						
				#>>>>>>>>>>	 Connecting
				else:
					totalv = str(pm.polyEvaluate(v=1))
					
					pm.polyConnectComponents(sel,ch=0)
					sv = (str(sel[0].split(".")[0])+'.vtx['+ totalv + ":" + str(pm.polyEvaluate(v=1)) + ']')
					sedge = pm.polyListComponentConversion(sv,te = 1,internal=1)
					cmds.polySoftEdge(sedge,a=180,ch=0)
					pm.select(sedge)
		# Face mode		   
		elif pm.filterExpand(sm=34) != None:
			sel = self.getAllSel()
			cmds.polyExtrudeFacet(sel,ch=0)
			cmds.polyMoveFacet(ls=[1, 1, 1],ch=0)
			mel.eval('performPolyMove "" 0;')
		else:
			mel.eval("dR_multiCutTool;")

	  
	def UniRemover(self):
		# Selected object / components
		sel = self.getAllSel()

		# Object mode
		if pm.filterExpand(sm=12) != None:
			cmds.delete(sel)
			
		# Vertex mode 
		elif pm.filterExpand(sm=31) != None:
			#>>>>>>>>>> Target Weld
			if len(sel) == 1:
				mel.eval('DeleteVertex;')
			elif len(sel) > 1:
				mel.eval('MergeToCenter;')
			
		#Edge mode
		elif pm.filterExpand(sm=32) != None:
			#>>>>>>>>>> Collapsing Edge into one
			if len(sel)==1:
				mel.eval('polyCollapseEdge;')
		   	
			elif len(sel)>1:
				firstSel = self.getAllSel()
				mel.eval('polySelectEdgesEveryN "edgeLoopOrBorder" 1;')
				loopEdges = self.getAllSel()
				pm.select(firstSel)
				fEdges = list(set(loopEdges) - set(firstSel))
				
				if fEdges:
					mel.eval('polyCollapseEdge;')
				else:
					mel.eval('DeleteEdge;')
			pm.select(cl=1)

		# Face mode			   
		elif pm.filterExpand(sm=34) != None:
			mel.eval("polyMergeToCenter;")
			self.faceMode()
		else:
			mel.eval("dR_multiCutTool;")

	def basepivot(self):
		sel = cmds.ls(sl=1)
		for s in sel:
			bb = cmds.exactWorldBoundingBox(s)
			bottom = [(bb[0] + bb[3])*.5, bb[1], (bb[2] + bb[5])*.5]
			cmds.xform(s, piv=bottom, ws=True)
		
	def worldPivot(self):
		sel = pm.ls(sl=1)
		pm.xform(sel, piv=(0,0,0), ws=True)
	
	def UnFreezeTranslate(self):
		if pm.filterExpand(sm=12) is None:return
		selection = pm.ls(sl=1)
		for sel in selection:
			pm.makeIdentity(sel,t=1,a=1)
			pm.move(0,0,0, sel, rpr= True)
			try:
				pos = [pm.getAttr(sel+".translateX") * -1,pm.getAttr(sel+".translateY") * -1,cmds.getAttr(sel+".translateZ") * -1]
			except:
				pm.delete(ch=1)
				self.UnFreezeTranslate()
				return

				
			pm.makeIdentity(sel,t=1,a=1)
			pm.setAttr(sel+".translateX", pos[0])
			pm.setAttr(sel+".translateY", pos[1])
			pm.setAttr(sel+".translateZ", pos[2])
		
		
	def moveToOrigin(self):
		if pm.filterExpand(sm=12) is None:return
		selection = pm.ls(sl=1)
		for sel in selection:
			pm.move(0,0,0, sel, rpr= True)


	def corner45(self,dir,*args):
		mayaUnit = pm.currentUnit( q=1, l=1 )
		sel = self.getAllSel()
		# Isolating edge and faces
		ed = []
		fc = []
		for s in sel:
			if ".e[" in str(s):
				ed.append(s)
			else:
				fc.append(s)
		# Error Checking
		if len(ed)!=1 or len(fc) < 1 : return self.inLineMessage("Adjacent face(s) and single edge should be selected \n\n <i style=\"color:#00FF00;\">Use Multi selection mode</i>.")
		pm.currentUnit(linear="cm")
		pivotVert = pm.ls(pm.polyListComponentConversion(ed,tv = 1),fl=1)
		allVert = pm.ls(pm.polyListComponentConversion(fc,tv = 1),fl=1)
		
		mp = pivotVert[0].getPosition(space="world")
		lp = pivotVert[1].getPosition(space="world")
		
		ToMovePoints = list(set(allVert) - set(pivotVert))
		
		singleLoc = ToMovePoints[0].getPosition(space="world")
		
		v1 =  lp - mp
		if dir ==False:
			v1 =  mp - lp
		
		for movePoint in ToMovePoints:
			fp = movePoint.getPosition(space="world")
			# creating fake axis to find cross product
			nc = fp + v1
			fa = nc - fp
			fb = mp - fp
			len2 = dt.length(fb)
			
			# Finding the cross product for new object and moving the verts
			crs = dt.cross(dt.normal(fb),dt.normal(fa))
			pc = fp + crs * len2
			pm.move(movePoint,pc,ws=1,a=1)
		# Clearing old selection and just selecting the face(s)
		pm.select(cl=1)
		pm.select(fc)
		pm.currentUnit(linear=mayaUnit)
	
	# This is for shorcut
	def corner45Plus(self):
		self.corner45(True)
	def corner45Minus(self):
		self.corner45(False)
		
	def edgeExtend(self):
		mayaUnit = pm.currentUnit(q=1, l=1)
		
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		chkVertex = cmds.filterExpand(sm = 31, ex = True)
		
		if chkEdge:
			if len(chkEdge) !=1: return
			sel = self.getAllSel()
			pm.currentUnit(linear="cm")
			
			border = cmds.ls(pm.polyListComponentConversion(sel, tf=True), fl=1 )
			if len(sel)==1 and len(border) == 1:
				#Confirming border edge
				vConvert = cmds.ls( pm.polyListComponentConversion(sel, tv=True), fl=1)
				eConvert = cmds.ls( pm.polyListComponentConversion(vConvert,te=True), fl=1)
				bedge = []
				for e in eConvert:
					con = cmds.ls(pm.polyListComponentConversion(e,tf=True), fl=1 )
					if len(con) == 1:
						bedge.append(e)
						
				#Deselecting Original Edge and bridging
				bridgEdg = list(set(bedge) - set(sel))
				cmds.select(bridgEdg)
				cmds.polyBridgeEdge(ch=0, divisions = 0)
								
				#Isolating Edges
				bridgeE = cmds.ls( pm.polyListComponentConversion(self.getAllSel(), fe=True, tv=True), fl=1)
				NewEdges = cmds.ls( pm.polyListComponentConversion(bridgeE, fv=True, te=True,internal=1), fl=1)
				# Select the last Edge
				pm.select(list(set(list(set(NewEdges) - set(self.getAllSel())))- set(sel)))

		if chkVertex:
			if len(chkVertex) !=1: return
			verts = self.getAllSel()
			pm.currentUnit(linear="cm")
			tEdges = cmds.ls(cmds.polyListComponentConversion(verts,te=1),fl=1)
			
			brdrEdge = []
			for edg in tEdges:
				cFace = cmds.ls(cmds.polyListComponentConversion(edg,tf=1),fl=1)
				if len(cFace) == 1:
					brdrEdge.append(edg)

			if not brdrEdge: return
			
			vTable= []
			for e in brdrEdge:
				vert = cmds.ls(cmds.polyListComponentConversion(e,tv=1),fl=1)
				vTable.extend(vert)
				
			# Isolating mid and side vertices
			midVert = [x for n, x in enumerate(vTable) if x in vTable[:n]]
			sideVert = list(set(vTable) - set(midVert))

			V1 = pm.PyNode(sideVert[0]).getPosition(space="world")
			V2 = pm.PyNode(midVert[0]).getPosition(space="world")
			V3 = pm.PyNode(sideVert[1]).getPosition(space="world")
			FourthPoint = V3 + (-1 * (V2-V1))
			
			totalEdge = str(pm.polyEvaluate(e=1))
			pm.select(brdrEdge)
			self.UniConnector()
			pm.select(str(midVert[0].split(".")[0])+'.e['+ totalEdge + ":" + str(pm.polyEvaluate(e=1)) + ']')

			totalVert = str(pm.polyEvaluate(v=1))
			pm.polySubdivideEdge(ch=0)
			lastVert = str(midVert[0].split(".")[0])+'.vtx['+ totalVert + ":" + str(pm.polyEvaluate(v=1)) + ']'

			cmds.select(lastVert)
			pm.move(lastVert,FourthPoint)
			

			val=0.01
			try:
				val = cmds.floatSliderGrp(self.F2Threshold,q=1,value=1)
			except:
				pass
			
			# Weld with the default threshold 0.001
			closest = self.getClosestVert(val)
			if closest:
				CL = cmds.xform(closest,q=1,ws=1,t=1)
				cmds.move(CL[0],CL[1],CL[2],lastVert)
				mergeVerts = list([closest] +[lastVert])
				cmds.polyMergeVertex(mergeVerts,d=1,ch=0)
				
		pm.currentUnit(linear=mayaUnit)
		
	def bevelModifier(self,status,*args):
		mayaUnit = pm.currentUnit(q=1, l=1)
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None or len(chkEdge) < 3: return self.inLineMessage("Select atleast 3 continious edges.")

		# Getting the value
		diff = 0.10
		try:
			diff = cmds.floatSliderGrp(self.BevelThreshold,q=1,value=1)
		except:
			pass
		
		# If status is True then it will increment value
		if status:
			interp = 1 +  diff
		else:
			interp = 1 - diff
			
		EdgeGroup = self.getEdgeGroup()
		pm.currentUnit(linear="cm")
		mover = {}
		for edgeLoop in EdgeGroup:
			
			pm.select(edgeLoop)
			OS = self.getOrderedSelection()
			
			# Selecting and Converting to pymel
			Edges = [pm.PyNode(i) for i in OS[0]]
			Verts = [pm.PyNode(i) for i in OS[1]]
			
			if len(Edges) < 3: 
				continue
				
			#Outer End Points & Converting to pynode
			outerEdges = Edges[::len(Edges)-1]
			outerVerts = Verts[::len(Verts)-1]
			
			#Inner End Points
			innerVerts =[Verts[1],Verts[-2]]
			
			#Getting the position for inner and outer verts
			OV1 = outerVerts[0].getPosition(space="world")
			OV2 = outerVerts[1].getPosition(space="world")
			IV1 = innerVerts[0].getPosition(space="world")
			IV2 = innerVerts[1].getPosition(space="world")
			
			#Calculating Vectors
			Line1 = OV1 - OV2
			Line2 = OV1 - IV1
			Line3 = IV2 - OV2
			
			#Plane Intersection
			normal3 = dt.cross(Line1,Line2)
			normal1 = dt.cross(Line2, normal3)
			normal2 = dt.cross(Line3, normal3)
			
			#Matrix Caclulation
			mat = dt.Matrix(normal1[0],normal1[1],normal1[2],0,
							normal2[0],normal2[1],normal2[2],0,
							normal3[0],normal3[1],normal3[2],0,
							0,0,0,1)
			righteq = dt.Vector(OV1.dot(normal1),OV2.dot(normal2),OV1.dot(normal3))
			
			
			# Finally Getting the merge point and move vertex
			merge_point = mat.inverse() * righteq
			verts_to_move = Verts[1:-1]
			
			distChk = dt.length(merge_point - OV1)

			if distChk < 3000:
				for v in verts_to_move:
					mid = dt.Point((1-interp) * merge_point + interp * v.getPosition(space="world"))
					mover[v] = mid

		for v,p in mover.items():
			pm.move(p.x,p.y,p.z, v, a=1, ws=1)
				
		pm.select(EdgeGroup)
		pm.currentUnit(linear=mayaUnit)
		
	# This is for shorcut	
	def bevelModifierPlus(self):
		self.bevelModifier(True)
	def bevelModifierMinus(self):
		self.bevelModifier(False)
				
#>>>>>>>>>>>> CORNER CONNECT [START] >>>>>>>>>>>>
	def softEdgeConnect(self):
		trans = self.getSandT()
		if cmds.filterExpand(sm=32) != None or cmds.filterExpand(sm=34) != None:
			fSel = cmds.polyEvaluate(v=1)
			cmds.polyConnectComponents(ch=0)
			lastE = trans+'.vtx['+ str(fSel) + ":" + str(cmds.polyEvaluate(v=1)) + ']'
			sedge = cmds.ls(cmds.polyListComponentConversion(lastE,te=1,internal=1),fl=1)
		elif cmds.filterExpand(sm=31)!= None:
			fSel = cmds.polyEvaluate(e=1)
			cmds.polyConnectComponents(ch=0)
			sedge = trans +'.e['+ str(fSel) + ":" + str(cmds.polyEvaluate(e=1)) + ']'
		if sedge:
			cmds.polySoftEdge(sedge,a=180,ch=0)
			cmds.select(sedge)
		
		return sedge

	def getCornerEdge(self,sel):
		crnrEdg =[]
		sel = self.getAllSel()
		
		for s in sel:
			# get Vert and Edges
			s=[s]
			
			cVerts = cmds.ls(cmds.polyListComponentConversion(s,tv=1),fl=1)
			cEdges = cmds.ls(cmds.polyListComponentConversion(cVerts,te=1),fl=1)
			
			#Make Edge Group
			edgGroup = []
			for v in cVerts:
				tEdge = cmds.ls(cmds.polyListComponentConversion(v,te=1),fl=1)
				ebool = list(set(tEdge) - set(s))
				edgGroup.append(ebool)
				
			#Finding overlapping
			vOverlap =[]
			for eSel in edgGroup:
				tV = cmds.ls(cmds.polyListComponentConversion(eSel,tv=1),fl=1)
				vOverlap.extend(tV)
				
			# Bunch of conversion. God knows while reading again.
			midVert = [x for n, x in enumerate(vOverlap) if x in vOverlap[:n]]
			tconEdge = cmds.ls(cmds.polyListComponentConversion(midVert,te=1),fl=1)
			einter = list(set(tconEdge) & set(cEdges))
			backtVert = cmds.ls(cmds.polyListComponentConversion(einter,tv=1),fl=1)
			finalVert = list(set(backtVert) & set(cVerts))
			containedEdges = cmds.ls(cmds.polyListComponentConversion(finalVert,te=1,internal=1),fl=1)
			crnrEdg.extend(containedEdges)
		return crnrEdg

	def buildAngle(self,midV):
		te = cmds.ls(cmds.polyListComponentConversion(midV,te=1),fl=1)
		verts =cmds.ls(cmds.polyListComponentConversion(te,tv=1),fl=1) 
		verts = list(set(verts) - set([midV]))
		fArray =[]
		for v in verts:
			tFace = cmds.ls(cmds.polyListComponentConversion(v,tf=1),fl=1)
			fArray.extend(tFace)

		midFace = [x for n, x in enumerate(fArray) if x in fArray[:n]]
		midFaceVerts = cmds.ls(cmds.polyListComponentConversion(midFace,tv=1),fl=1)
		tEdges = cmds.ls(cmds.polyListComponentConversion(verts,te=1),fl=1)
		tVerts = cmds.ls(cmds.polyListComponentConversion(tEdges,tv=1),fl=1)

		topVert = list(set(midFaceVerts) - set(tVerts))
		if topVert==[]:return

		C1 = cmds.xform(verts[0],q=1,ws=1,t=1)
		C2 = cmds.xform(verts[1],q=1,ws=1,t=1)
		C3 = cmds.xform(topVert[0],q=1,ws=1,t=1)

		V1 = om.MVector(C1[0],C1[1],C1[2])
		V2 = om.MVector(C2[0],C2[1],C2[2])
		V3 = om.MVector(C3[0],C3[1],C3[2])

		mid = ((V2 - V1) *.5 ) + V1
		Fmid = (((V3 - mid) * .333) + mid)

		cmds.move(Fmid.x,Fmid.y,Fmid.z,midV)
		cmds.select(list([midV]+topVert))
		self.softEdgeConnect()

	def getTopVert(self,verts):
		fArray =[]
		for v in verts:
			tFace = cmds.ls(cmds.polyListComponentConversion(v,tf=1),fl=1)
			fArray.extend(tFace)
		midFace = [x for n, x in enumerate(fArray) if x in fArray[:n]]	  
		midFaceVerts = cmds.ls(cmds.polyListComponentConversion(midFace,tv=1),fl=1)
		if len(midFaceVerts) !=6:
			return None

		tEdges = cmds.ls(cmds.polyListComponentConversion(verts,te=1),fl=1)
		tVerts = cmds.ls(cmds.polyListComponentConversion(tEdges,tv=1),fl=1)

		topVert = list(set(midFaceVerts) - set(tVerts))
		return topVert
		
	def connectCorner(self):
		if cmds.filterExpand(sm=31)!= None:
			verts = self.getAllSel()
		elif cmds.filterExpand(sm=32) != None:
			selEdges = self.getAllSel()
			
			if len(selEdges) !=1:return
			verts = cmds.ls(cmds.polyListComponentConversion(selEdges,tv=1),fl=1)
			
		tEdges = cmds.ls(cmds.polyListComponentConversion(verts,te=1),fl=1)
		topVert = self.getTopVert(verts)
		
		try:
			cmds.delete(selEdges,ch=0)
		except:
			pass
			
		if topVert is None or topVert == []:
			self.softEdgeConnect()
			return
		shp = str(verts[0].split(".")[0])

		C1 = cmds.xform(verts[0],q=1,ws=1,t=1)
		C2 = cmds.xform(verts[1],q=1,ws=1,t=1)
		C3 = cmds.xform(topVert[0],q=1,ws=1,t=1)

		V1 = om.MVector(C1[0],C1[1],C1[2])
		V2 = om.MVector(C2[0],C2[1],C2[2])
		V3 = om.MVector(C3[0],C3[1],C3[2])

		#get mid between 1rsft vertices
		mid = ((V2 - V1) *.5 ) + V1
		Fmid = (((V3 - mid) * .333) + mid)

		cmds.select(verts)
		self.softEdgeConnect()
		lastE = shp+'.e['+ str(cmds.polyEvaluate(e=1)) + ']'
		cmds.select(lastE)
		cmds.polySubdivideEdge(dv=1,ch=0)
		lastV = shp+'.vtx['+ str(cmds.polyEvaluate(v=1)) + ']'
		cmds.move(Fmid.x,Fmid.y,Fmid.z,lastV)
		cmds.select(list([lastV]+topVert))
		self.softEdgeConnect()

	def cornerConnect(self):
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		chkVertex = cmds.filterExpand(sm = 31, ex = True)
		if chkEdge != None:
			
			if len(chkEdge) <2:return
			shp = self.getSandT()
			firstIndex = str(cmds.polyEvaluate(v=1))
			crnrEdges = self.getCornerEdge(self.softEdgeConnect())
			
			if crnrEdges:
				cmds.select(crnrEdges)
				preSel = cmds.ls(cmds.polyListComponentConversion(crnrEdges,tv = 1),fl=1)
				cmds.polySubdivideEdge(ch = 0)
				newVerts = cmds.ls(cmds.polyListComponentConversion(crnrEdges,tv = 1),fl=1)
				cmds.select(list(set(newVerts)- set(preSel)))
				crnrVerts = self.getAllSel()

				cmds.progressWindow(title='Corner Connect', progress=0,max=len(crnrVerts), status='Connecting Edges...', isInterruptable=True)
				for i,crn in enumerate(crnrVerts):
					cmds.progressWindow(e=1, progress=i, status='Building Corners...')
					self.buildAngle(crn)
				
			cmds.select(shp+'.vtx[0]')
			lastV = shp+'.vtx['+ firstIndex+":"+ str(cmds.polyEvaluate(v=1)) + ']'
			lastEdge = cmds.ls(cmds.polyListComponentConversion(lastV,te = 1,internal=1),fl=1)
			cmds.select(lastEdge)
			cmds.progressWindow(endProgress=1)
			
		elif chkVertex != None:
			if len(chkVertex) <2:return
			
			if len(chkVertex) == 2:
				self.connectCorner()
			else:
				self.softEdgeConnect()
#<<<<<<<<<<<<<< CORNER CONNECT [END] <<<<<<<<<<<<<<<<<

	def loadEdgeLoop(self):
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return self.inLineMessage("Only Edges/Edge Loops Supported")
		self.HighEdges = self.getAllSel()
		
		disString = str(len(self.HighEdges)) + " - Edges"
		cmds.textField(self.EdgeLoopNumber,text=disString,e=1,bgc=(89/255.0, 118/250.0, 106/255.0))
		
	def cutAndStitch(self):
		mayaUnit = pm.currentUnit(q=1, l=1)
		
		# Error Checking
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return self.inLineMessage("Only Edges/Edge Loops Supported")
		txtBox = cmds.textField(self.EdgeLoopNumber,text=1,q=1)
		if txtBox  == "No EdgeLoop":return self.inLineMessage("Load Edge Loop in the slot.")
		Low = self.getAllSel()
		if len(self.HighEdges) < len(Low) : return self.inLineMessage("More than source Edges")
		weld = True	
		if self.HighEdges[0].split(".")[0] != Low[0].split(".")[0]:
			weld = False
		
		
		totalVerts = str(pm.polyEvaluate(v=1))
		Threshold = cmds.floatSliderGrp(self.StitchThreshold,v=1,q=1) * 100.0
		pm.select(self.HighEdges)
		VertSelection = self.getOrderedSelection()[1]
		pm.currentUnit(linear="cm")
		for Edge in Low:
			pm.select(Edge)
			
			try:
				pm.scale(1.01,1.01,1.01,cs=1)
			except:
				pass
			
			EdgeNumber = int(Edge.split("[")[-1].split("]")[0])
			EdgeOrder = self.GetEdgeDirection(Edge)
			
			FP = pm.PyNode(EdgeOrder[0]).getPosition(space="world")
			LP = pm.PyNode(EdgeOrder[1]).getPosition(space="world")
			distance = round(dt.length(LP-FP),10)
			
			# Finding the point on line
			ValidPoints = {}
			WeldPoints = {}
			ToPoints = {}
			OrderCheck = []
			
			i = 0
			for sl in list(VertSelection):
				# calculating the point on line
				pysl = pm.PyNode(sl)
				CP = pysl.getPosition(space = 'world')
				
				Ln1 = dt.normal(LP - FP)
				Ln2 = CP - LP
				Dot = dt.dot(Ln2,Ln1)
				
				Pos = LP + Dot * Ln1
				
				
				tDist = dt.length(CP-Pos)
				if tDist > Threshold: continue

				# isolating the position possibe only on the line segment
				InLineAdd = round(dt.length(Pos-FP) + dt.length(Pos-LP),10)
				
				if str(distance) == str(InLineAdd):
					WeldPoints[i] = pysl
					ValidPoints[i] = Pos
					ToPoints[i] = CP
					OrderCheck.append(dt.length(FP - Pos))
					i+=1
			
			VPLength = len(ValidPoints)
			
			if not OrderCheck:
				continue
			
			#Finding the Vertex Order
			vOrder = ""
			if OrderCheck[0] < OrderCheck[-1]:
				vOrder = "Reverse"

			# Final points Generation
			for k,v in ValidPoints.items():
				#Calculating the Cut Position
				t = dt.length(v-FP) / distance
				o = k
				if vOrder == "Reverse":
					t = 1 - dt.length(v-FP) / distance
					o = (len(ValidPoints)-1)-k
				#Moving the vertices
				if k == 0:
					Spos = pm.PyNode(EdgeOrder[1]).getPosition(space="world")
					pm.move(EdgeOrder[1],ToPoints[o])
				elif k == VPLength-1:
					Epos = pm.PyNode(EdgeOrder[0]).getPosition(space="world")
					pm.move(EdgeOrder[0],ToPoints[o])
				else:
					cmds.polySplit( ip=[(EdgeNumber, t)])
					lastVert =	str(Edge.split(".")[0])+'.vtx['+ str(cmds.polyEvaluate(v=1)) + ']'
					
					pm.move(lastVert,ToPoints[o])

		if weld:
			highVerts = cmds.ls(pm.polyListComponentConversion(self.HighEdges, tv=True),fl=1)	
			lowVerts = cmds.ls(pm.polyListComponentConversion(Low, tv=True),fl=1)
			newVerts = cmds.ls(str(Low[0].split(".")[0])+'.vtx['+ str(totalVerts) + ":" + str(pm.polyEvaluate(v=1)) + ']',fl=1)
			
			weldVerts = highVerts + lowVerts + newVerts
			cmds.polyMergeVertex(weldVerts, d=0.1 )
			pm.select(cl=1)
			
		pm.currentUnit(linear=mayaUnit)


	def endConnect(self):
		# Usual Edge Check
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		
		if chkEdge != None:
			if len(chkEdge) !=1:return
			#ResetsomeVariables
			oppositeEdge="";V1="";E1="";V2="";innerFace=[]
			
			#Selections and findinf the overlapping Faces
			sel = self.getAllSel()
			V1 = cmds.ls(cmds.polyListComponentConversion(sel,tv=1),fl=1)
			E1 = cmds.ls(cmds.polyListComponentConversion(V1,te=1),fl=1)
			V2 = cmds.ls(cmds.polyListComponentConversion(E1,tv=1),fl=1)
			facelist = cmds.ls(cmds.polyListComponentConversion(sel,tf=1),fl=1)
			
			# Count the face vertex number is Exactly 6
			for f in facelist:
				toVert = cmds.ls(cmds.polyListComponentConversion(f,tv=1),fl=1)
				if len(toVert) == 6:
					innerFace.append(f)
					
			if len(innerFace) != 1:return
			F1 = cmds.ls(cmds.polyListComponentConversion(innerFace[0],tv=1),fl=1)
			finalVert = list(set(F1) - set(V2))
			oppositeEdge = cmds.ls(cmds.polyListComponentConversion(finalVert,te=1,internal=1),fl=1)
			if len(oppositeEdge) == 1:
				cmds.select(oppositeEdge[0],add=1)
				self.softEdgeConnect()
				crnrEdges = cmds.ls(sl=1)
				cmds.select(crnrEdges)
				preSel = cmds.ls(cmds.polyListComponentConversion(crnrEdges,tv = 1),fl=1)
				cmds.polySubdivideEdge(ch = 0)
				newVerts = cmds.ls(cmds.polyListComponentConversion(crnrEdges,tv = 1),fl=1)
				cmds.select(list(set(newVerts)- set(preSel)))
				lastVert = cmds.ls(sl=1)

		crnVert = []
		for oldVert in V1:
			vgroup = list(lastVert+[oldVert])
			cmds.select(vgroup)
			self.cornerConnect()
			tvert = cmds.ls(cmds.polyListComponentConversion(tv = 1),fl=1)
			tEdge = cmds.ls(cmds.polyListComponentConversion(tvert,te = 1),fl=1)
			crnVert.extend(tEdge)

		lastEdge = cmds.ls(cmds.polyListComponentConversion(lastVert,te = 1),fl=1)
		DelEdge= list(set(lastEdge) -	set(crnVert))
		cmds.polyDelEdge( DelEdge,ch=0,cv=True)

	def distConnect(self):
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return
		
		sel = self.getAllSel()
		if len(sel)!=2: return

		totalv = str(pm.polyEvaluate(v=1))
		
		faceIt = cmds.polyListComponentConversion(sel[0],tf = 1)
		pm.select(cmds.polyListComponentConversion(faceIt,te = 1))
		edgeIt = self.getAllSel()
		pm.select(sel[1])
		sedge = self.getAllSel()
		finalEdge = list(set(edgeIt) & set(sedge))
		if len(finalEdge) == 0:
			mel.eval('polySelectSp -ring '+sel[0] +';')
			ringEdges = self.getAllSel()
			pm.select(sel[1])
			secdge = self.getAllSel()
			sameRingCheck = list(set(ringEdges) & set(secdge))
			if len(sameRingCheck) == 1:
				mel.eval('polySelectSp -ring '+sel[0] +' '+sel[1]  +';')
				sel = self.getAllSel()
				pm.polyConnectComponents(sel,ch=0)
		else:
			pm.polyConnectComponents(sel,ch=0)
		
		sv = (str(sel[0].split(".")[0])+'.vtx['+ totalv + ":" + str(pm.polyEvaluate(v=1)) + ']')
		sedge = pm.polyListComponentConversion(sv,te = 1,internal=1)
		cmds.polySoftEdge(sedge,a=180,ch=0)
		pm.select(sedge)


	def flowConnect(self):
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return
		sel = self.getAllSel()
		if len(sel) < 2: return
		
		
		totalv = str(pm.polyEvaluate(v=1))
		pm.polyConnectComponents(sel,insertWithEdgeFlow=1,ch=0)
		
		sv = (str(sel[0].split(".")[0])+'.vtx['+ totalv + ":" + str(pm.polyEvaluate(v=1)) + ']')
		sedge = pm.polyListComponentConversion(sv,te = 1,internal=1)
		cmds.polySoftEdge(sedge,a=180,ch=0)
		pm.select(sedge)		
		

	def vertexToEdge(self):		
		sel = self.getAllSel()
		if len(sel) != 2: return
		
		Vert = sel[0]
		Edge = sel[1]
		
		if ".vtx[" not in Vert:
			Vert = sel[1]
			Edge = sel[0]
			
		if ".vtx[" not in Vert or ".e[" not in Edge:return self.inLineMessage("Select one Vertex and one Edge. \n\n <i style=\"color:#00FF00;\">Use Multi selection mode</i>.")
		
		EdgeNumber = int(Edge.split("[")[-1].split("]")[0])
		
		verts = self.GetEdgeDirection(Edge)
		FP = pm.PyNode(verts[0]).getPosition(space = 'world')
		LP = pm.PyNode(verts[1]).getPosition(space = 'world')
		distance = round(dt.length(LP-FP),10)

		CP = pm.PyNode(Vert).getPosition(space = 'world')
		
		# Calculating the position
		Ln1 = dt.normal(LP - FP)
		Ln2 = CP - LP
		Dot = dt.dot(Ln2,Ln1)
		
		Pos = LP + Dot * Ln1
		
		# isolating the position possibe only on the line segment
		InLineAdd = round(dt.length(Pos-FP) + dt.length(Pos-LP),10)
		if str(distance) == str(InLineAdd):
			t = dt.length(Pos-FP) / distance
			pm.polySplit( ip=[(EdgeNumber, t)],ch=0)
			lastVert = str(Vert.split(".")[0])+'.vtx['+ str(cmds.polyEvaluate(v=1)) + ']'
			pm.polyConnectComponents(Vert,lastVert,ch=0)
			pm.select(lastVert)
		
	def loadVertex(self):
		chkVtx = cmds.filterExpand(sm = 31, ex = True)
		if chkVtx is None or len(chkVtx)!=1:return self.inLineMessage("Load Single Vertex in the slot.")
		vert = str(chkVtx).split("'")[-2]

		cmds.textField(self.vertexNumber,text=vert,e=1,bgc=(89/255.0, 118/250.0, 106/255.0))
	
	def connectToVertex(self):
		txt = cmds.textField(self.vertexNumber,text=1,q=1)
		if txt == "No Vertex Loaded" : return self.inLineMessage("Load Vertex in the slot.")
		
		# Getting all the points
		oPoints = self.getAllSel()
		totalEdge = str(pm.polyEvaluate(e=1))
		
		# Loop Through all points and connect
		for point in oPoints:
			pm.select(txt,point)
			pm.polyConnectComponents(ch=0)
			
		# Select the final connected Edges
		sedge = (str(txt.split(".")[0])+'.e['+ totalEdge + ":" + str(pm.polyEvaluate(e=1)) + ']')
		cmds.polySoftEdge(sedge,a=180,ch=0)
					
		pm.select(sedge)

	def spaceloop(self):
		mayaUnit = pm.currentUnit(q=1, l=1)
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None or len(chkEdge) <3:return
		pm.currentUnit(linear="cm")
		origsel = self.getAllSel()
		edgeGroup = self.getEdgeGroup()
		for single in edgeGroup:
			sel = single
			if len(sel) <3: return
			shp = sel[0].split(".")[0]
			#Storing both verts and edges
			
			verts = cmds.ls(cmds.polyListComponentConversion(sel,fe=1,tv=1),fl=1)
			edges = cmds.polyListComponentConversion(verts,fv=1,te=1, internal=1)

			# iterating for getting vertnumber and vposition
			vertData = {}
			for index, vert in enumerate(verts):
				vertData[index] = {'vertex':vert,'vertexPos':cmds.xform(vert, q=1, ws=1, t=1),'cv':None,'cvPos':None}

			#create Curve
			cmds.select(edges, r=1)
			curve = cmds.polyToCurve(form=2, degree=1)[0]

			#find the matching cv
			cvs = cmds.getAttr('{}.cv[*]'.format(curve))
			for i in range(len(cvs)):
				curveCV = '{}.cv[{}]'.format(curve,i)
				cvPos = cmds.xform(curveCV, q=1, ws=1, t=1)
				
				for vert, data in vertData.items():
					vertex = vertData[vert]['vertex']
					pos = cmds.xform(vertex, q=1, ws=1, t=1)
					roundCvPos = [round(x, 3) for x in cvPos]
					roundPos = [round(x, 3) for x in pos]
					if roundCvPos == roundPos:
						vertData[vert]['cv'] = curveCV
						continue

			#Building the curve
			cmds.rebuildCurve(curve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=0, d=1, tol=0)

			#set New vertex postion
			for vert, data in vertData.items():
				vertex = vertData[vert]['vertex']
				curveCV = vertData[vert]['cv']
				cvPos = cmds.xform(curveCV, q=True, ws=True, t=True,a=1)
				vertData[vert]['cvPos'] = cvPos
				cmds.xform(vertex, ws=True, t=cvPos,a=1)
				
			cmds.delete(curve)
			
		cmds.hilite(shp)
		cmds.select(origsel, r=True)
		self.edgeMode()
		pm.currentUnit(linear=mayaUnit)
		
	def straightloop(self):
		mayaUnit = pm.currentUnit(q=1, l=1)
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return
		if len(chkEdge) <2: return
		
		origsel = self.getAllSel()
		edgeGroup = self.getEdgeGroup()
		pm.currentUnit(linear="cm")
		for single in edgeGroup:
			cmds.select(single)
			sel = self.getOrderedSelection()[1]
			otherPoint = list(sel)[1:-1]
			
			FP = pm.PyNode(sel[-1]).getPosition(space="world")
			LP = pm.PyNode(sel[0]).getPosition(space="world")
						
			for point in otherPoint:
				MP = pm.PyNode(point).getPosition(space="world")
				doot = dt.dot(dt.normal(LP-FP),dt.normal(MP-FP))
				pos = FP + dt.normal(LP-FP) * (dt.length(MP-FP) * doot)
				cmds.move(pos.x,pos.y,pos.z,point,ws=1,wd=1)
				
		cmds.select(origsel, r=True)
		self.edgeMode()
		pm.currentUnit(linear=mayaUnit)

	def circle(self):
		mayaUnit = pm.currentUnit(q=1, l=1)
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return
		if len(chkEdge) <4: return
		
		origsel = self.getAllSel()
		edgeGroup = self.getEdgeGroup()
		pm.currentUnit(linear="cm")
		
		for single in edgeGroup:
			cmds.select(single)
			fset = self.getAllSel()
			back2Vert = cmds.ls(pm.polyListComponentConversion(fset, fe=True, tv=True), fl=1 )
			pm.select(back2Vert)
		
			s = [pm.PyNode(i) for i in self.getAllSel()]
			lens = len(s)
			
			#Cacluating the center
			position = [i.getPosition(space='world') for i in s]
			cs = dt.Point(sum(position) / len(s))

			vts = []
			dist = []
			for i in range(lens):
				p = s[i].getPosition(space='world')
				l = dt.length(p - cs)
				vts.append(p)
				dist.append(l)
				

			averageDist = sum(dist)/lens
			for i in range(lens):			
				pos = cs + averageDist / dist[i] *  (vts[i] - cs)
				s[i].setPosition(pos, space='world')
				
			cmds.select(fset)
			self.spaceloop()
			
		self.edgeMode()
		cmds.select(origsel)
		pm.currentUnit(linear=mayaUnit)
		
	def geoPoly(self):
		mayaUnit = pm.currentUnit(q=1, l=1)
		chkFace = cmds.filterExpand(sm = 34, ex = True)
		if chkFace is None:return
		pm.currentUnit(linear="cm")
		orgSel = self.getAllSel()
		edges = cmds.ls(pm.polyListComponentConversion(orgSel, ff=True, te=True), fl=1)
		verts = cmds.ls(pm.polyListComponentConversion(orgSel, tv=True), fl=1)
		
		brdrList =[]
		for brd in edges:
			border = cmds.ls(pm.polyListComponentConversion(brd, fe=True, tf=True), fl=1 )
			if len(border) == 1:
				brdrList.append(brd)
		# Circling
		cmds.ConvertSelectionToEdgePerimeter()
		tsel = self.getAllSel()
		fset = list(tsel + brdrList)
		pm.select(fset)
		self.circle()

		# isolating the iiner and outer Verts
		outerVerts = cmds.ls(pm.polyListComponentConversion(self.getAllSel(), tv=True), fl=1)
		innerVerts = list(set(verts) - set(outerVerts))

		if innerVerts:
			pm.select(innerVerts)	
			cmds.polyAverageVertex(ch=0,i=5)
		
		self.faceMode()
		cmds.select(orgSel)
		pm.currentUnit(linear=mayaUnit)
		
	def viewPlanar(self):
		mayaUnit = pm.currentUnit(q=1, l=1)
		origsel = self.getAllSel()
		if len(origsel) < 2: return
		pm.currentUnit(linear="cm")
		
		pm.select(pm.polyListComponentConversion(origsel, tv=True))
		s = [pm.PyNode(i) for i in self.getAllSel()]
		lens = len(s)
		
		position = [i.getPosition(space='world') for i in s]
		cp = dt.Point(sum(position) / len(s))

		view = omu.M3dView.active3dView()
		dag = om.MDagPath()
		view.getCamera(dag)
		cname = str(om.MFnDagNode(dag.transform()).name())
		cz = cmds.xform(cname, q=1, m=1, ws=1)[8:11]
		up = cmds.camera(cname, q=1, worldUp=1)
		left = dt.cross(cz,up)
		cn = dt.cross(left,up)
		
		for i in range(lens):
			v = position[i] - cp
			dist = dt.dot(cn,v)
			pos = position[i] - dist * cn
			pm.move(s[i],pos)

		pm.select(origsel)
		pm.currentUnit(linear=mayaUnit)
		
	def makePlanar(self):
		mayaUnit = pm.currentUnit(q=1, l=1)
		origsel = self.getAllSel()
		if len(origsel) < 2: return
		pm.currentUnit(linear="cm")
		
		pm.select(pm.polyListComponentConversion(origsel, tv=True))
		s = [pm.PyNode(i) for i in self.getAllSel()]
		lens = len(s)
		
		position = [i.getPosition(space='world') for i in s]
		cp = dt.Point(sum(position) / len(s))
		
		fc = [pm.PyNode(i) for i in origsel]
		normal = [i.getNormal(space="world") for i in fc]
		cn = dt.normal(dt.Point(sum(normal) / len(fc)))

		for i in range(lens):
			v = position[i] - cp
			dist = dt.dot(cn,v)
			pos = position[i] - dist * cn
			pm.move(s[i],pos)

		pm.select(origsel)
		pm.currentUnit(linear=mayaUnit)

	def centerloop(self):
		chkEdge = cmds.filterExpand(sm = 32, ex = True)
		if chkEdge is None:return
		mel.eval("polyEditEdgeFlow -adjustEdgeFlow 1;")
		
	def relaxLoop(self):
		compSel = self.getAllSel()
		if compSel:
			cmds.polyAverageVertex(compSel,ch=0,i=1)
			cmds.select(compSel)	
		
	def abt(self):
		os.startfile('https://srivignesh35.github.io/nitropoly/')


def main():
	NP().UI()
	for f in NP().hotkeysList:
		NP().hotkeyMaker(f)


