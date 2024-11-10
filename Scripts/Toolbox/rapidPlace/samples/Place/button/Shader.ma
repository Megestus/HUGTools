//Maya ASCII 2020 scene
//Name: Shader.ma
//Last modified: Mon, Oct 11, 2021 11:49:55 AM
//Codeset: 950
requires maya "2020";
requires "mtoa" "4.0.3";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2020";
fileInfo "version" "2020";
fileInfo "cutIdentifier" "202004291615-7bd99f0972";
fileInfo "osv" "Microsoft Windows 10 Technical Preview  (Build 19043)\n";
fileInfo "UUID" "193AF978-4552-8761-C2DA-4992939AF904";
createNode blinn -n "button_SHD";
	rename -uid "AA032F19-4E00-D49A-1F98-389773F66DFA";
	setAttr ".sc" -type "float3" 0.37062937 0.37062937 0.37062937 ;
	setAttr -av ".rfl" 0.32867133617401123;
	setAttr -av ".ec" 0.39156922698020935;
	setAttr ".sro" 1;
createNode ramp -n "ramp1";
	rename -uid "0783E627-4B40-CA0C-6F9F-86A3AA0F7B0C";
	setAttr -s 5 ".cel";
	setAttr ".cel[0].ep" 0.34674921631813049;
	setAttr ".cel[0].ec" -type "float3" 0 0 0 ;
	setAttr ".cel[1].ep" 0.3622291088104248;
	setAttr ".cel[1].ec" -type "float3" 1 1 1 ;
	setAttr ".cel[2].ep" 0.70588237047195435;
	setAttr ".cel[2].ec" -type "float3" 1 0 0 ;
	setAttr ".cel[3].ep" 0.61300307512283325;
	setAttr ".cel[3].ec" -type "float3" 0 0 0 ;
	setAttr ".cel[4].ep" 0.56965947151184082;
	setAttr ".cel[4].ec" -type "float3" 1 1 1 ;
createNode samplerInfo -n "samplerInfo1";
	rename -uid "28ED42FC-4FA2-8B01-F803-FD91A023C6CC";
createNode place2dTexture -n "place2dTexture1";
	rename -uid "733CDC15-413C-AE7D-11DE-E999C9844443";
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 5 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 8 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -s 10 ".u";
select -ne :defaultRenderingList1;
select -ne :defaultTextureList1;
	setAttr -s 6 ".tx";
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr ".ren" -type "string" "arnold";
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "ramp1.oc" "button_SHD.c";
connectAttr "samplerInfo1.uv" "ramp1.uv";
connectAttr "place2dTexture1.ofs" "ramp1.fs";
connectAttr "button_SHD.msg" ":defaultShaderList1.s" -na;
connectAttr "samplerInfo1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "place2dTexture1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "ramp1.msg" ":defaultTextureList1.tx" -na;
// End of Shader.ma
