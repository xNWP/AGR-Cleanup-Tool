"""
	file: agrcleanuptool.pyp
	author: Brett "xNWP" Anthony

"""

""" 		ID LAYOUT

0 - Primary UI
	100 - Group (Program Information)
	200 - Group (Tools)
		201 - Delete Hitboxes/Physics Objects
		202 - Fix Ball Joint Rotations
		
500 - BallJoint UI
	551 - Iterator
	552 - View 1
	553 - View 2
	554 - View 3
	555 - H + 45
	556 - H - 45
	557 - P + 45
	558 - P - 45
	559 - B + 45
	560 - B - 45	
	565 - H
	566 - P
	567 - B
	575 - Prev
	576 - Next
	580 - Tau
	581 - Height
	582 - Frame
	583 - FrameEdit

"""

# Imports
import c4d
from c4d import plugins
from c4d import documents
from c4d import gui

import math # Algebraic!
import urllib2 # For Update Checking
import webbrowser # ^^

# Global Vars
PLUGIN_VERSION = "v0.5 [ALPHA]"
PLUGIN_VERSION_INT = 0 # 0 for alpha release, even though it will be displayed as 0.5
PLUGIN_NAME = "AGR Cleanup Tool " + PLUGIN_VERSION
PLUGIN_DESCRIPTION = "Aids in cleaning up Advanced Effects Game Recording (AGR) Files."
PLUGIN_ID = 1040374 # Registered ID
PLUGIN_WEBPAGE = "https://github.com/xNWP"
PLUGIN_UPDATE_LINK = "http://code.thatnwp.com/version/AGRCleanupTool"
MAINUI_WIDTH = 420
MAINUI_HEIGHT = 250

def CheckUpdateAvailable(CheckURL):
	# if update available, returns download url, otherwise None
	UpdateFile = urllib2.urlopen(CheckURL).read(2000)
	UpdateFile = UpdateFile.split('\0')
	
	for it in range(len(UpdateFile)):
		if (UpdateFile[it] == "version"):
			LatestVersion = UpdateFile[it + 1]
		if (UpdateFile[it] == "download"):
			DownloadLink = UpdateFile[it + 1]
			
	if (int(LatestVersion) > PLUGIN_VERSION_INT):
		return DownloadLink
	else:
		return None
	

# Helper Function To Find all Objects in Document containing String
def FindAll(Document, String):
	OBJS_MATCHING = []
	OBJS = Document.GetObjects()
	
	def IterateChildren(Objects):
		for OBJ in Objects:
			if String in OBJ.GetName():
				OBJS_MATCHING.append(OBJ)
			elif (OBJ.GetChildren() != None):
				IterateChildren(OBJ.GetChildren())
	
	IterateChildren(OBJS)
	
	return OBJS_MATCHING
	
	# Helper Function To Find all Objects in Document containing String and excluding NString && NString2
def FindAllBut2(Document, String, NString, NString2):
	OBJS_MATCHING = []
	OBJS = Document.GetObjects()
	
	def IterateChildren(Objects):
		for OBJ in Objects:
			if NString in OBJ.GetName() or NString2 in OBJ.GetName():
				continue
			elif String in OBJ.GetName():
				OBJS_MATCHING.append(OBJ)
			elif (OBJ.GetChildren() != None):
				IterateChildren(OBJ.GetChildren())
	
	IterateChildren(OBJS)
	
	return OBJS_MATCHING
		

# Delete Hitboxes/Physics Objects
def DeletePhysicsObjs():
	print "--- Deleting Hitboxes/Physics Objects"
	c4d.StatusSetSpin()
	c4d.StopAllThreads()
	
	ACTIVE_DOC = documents.GetActiveDocument()
	PhysicsObjects = FindAll(ACTIVE_DOC, "physics")
		
	if len(PhysicsObjects) == 0:
		gui.MessageDialog("No Hitboxes/Physics Objects Found.")
		print "--- No Hitboxes/Physics Objects Found."
		c4d.StatusClear()
		return True
	
	ACTIVE_DOC.StartUndo()
	
	for OBJ in PhysicsObjects:
		print "--- Found physics object %s" % (OBJ)
		ACTIVE_DOC.AddUndo(c4d.UNDOTYPE_DELETE, OBJ)
		OBJ.Remove()
	
	c4d.StatusClear()
	ACTIVE_DOC.EndUndo()
	c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
	
	gui.MessageDialog("Successfully deleted %s Hitboxes/Physics Objects." % len(PhysicsObjects))
	
	return True

def FixBallJointRotations():
	print "--- Fixing Ball Joint Rotations"
	c4d.StatusSetSpin()
	c4d.StatusSetText("Setting Ball Joint Rotations.")
	
	ACTIVE_DOC = documents.GetActiveDocument()
	StartTime = ACTIVE_DOC.GetMinTime()
	EndTime = ACTIVE_DOC.GetMaxTime()
	CurrentTime = ACTIVE_DOC.GetTime()
	
	
	BallJoints = FindAllBut2(ACTIVE_DOC, "ball_L", "w_", "v_")
	BallJoints += FindAllBut2(ACTIVE_DOC, "ball_R", "w_", "v_")
	
	if len(BallJoints) is 0:
		gui.MessageDialog("No Ball Joints Found.")
		print "--- No Ball Joints Found."
		c4d.StatusClear()
		UI = PrimaryUI()
		UI.Open(c4d.DLG_TYPE_MODAL, PLUGIN_ID, -1, -1, 420, 360, 0) # open ui
		return False
		
	for Joint in BallJoints:
		print "--- Found Ball Joint %s" % (Joint)
		Tracks = Joint.GetCTracks()
		
		# Remove all animation from the ball joints
		for track in Tracks:
			track.Remove()
	
	TmpCamera = c4d.BaseObject(c4d.Ocamera)
	TmpCamera.SetName("__AGR-CLEANUP-TOOL-TMPCAMERA")
	TmpUpVec = c4d.BaseObject(c4d.Onull)
	TmpUpVec.SetName("__AGR-CLEANUP-TOOL-TMPUPVECTOR")
	ACTIVE_DOC.InsertObject(TmpCamera)
	ACTIVE_DOC.InsertObject(TmpUpVec)
	
	TargetTag = c4d.BaseTag(c4d.Ttargetexpression)
	TmpCamera.InsertTag(TargetTag)
	
	bd = ACTIVE_DOC.GetActiveBaseDraw()
	
	bd.SetSceneCamera(TmpCamera)
	
	ACTIVE_DOC.SetAction(c4d.ID_MODELING_ROTATE)

	def SetCamera(Joint, Tau, Height):
		ACTIVE_DOC.SetActiveObject(Joint)
		
		CameraLoc = Joint.GetMg()
		TmpUpVecLoc = Joint.GetMg()
		Angle = Tau * math.pi
		cX = CameraLoc.off.x + (math.cos(Angle)*35)
		cY = CameraLoc.off.y + Height
		cZ = CameraLoc.off.z + (math.sin(Angle)*35)
		CameraLoc.off = c4d.Vector(cX, cY, cZ)
		TmpUpVecLoc.off = c4d.Vector(cX, cY + 500, cZ)
		TmpCamera.SetMg(CameraLoc)
		TmpUpVec.SetMg(TmpUpVecLoc)
		
		TargetTag[c4d.TARGETEXPRESSIONTAG_LINK] = Joint
		TargetTag[c4d.TARGETEXPRESSIONTAG_UP_LINK] = TmpUpVec
		c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
	
	# BallJoint UI
	class BJUI(gui.GeDialog):
		global it
		it = 0
		
		def __init__(self):
			SetCamera(BallJoints[it], 0, 15)

		def CreateLayout(self):
			self.SetTitle(PLUGIN_NAME + " -- Ball Joint Rotation Fixer")
			
			self.GroupBegin(0, c4d.BFH_SCALE|c4d.BFV_SCALE, cols=1, rows=3)
			self.GroupBorderSpace(2,2,2,2)
			self.GroupSpace(0, 12)
			
			self.GroupBegin(0, c4d.BFH_SCALE, cols=1, rows=5)
			self.AddStaticText(551, c4d.BFH_CENTER|c4d.BFH_SCALE, 160, 20, "Ball Joint %s of %s." % (it + 1, len(BallJoints)))
			self.GroupBegin(0, c4d.BFH_CENTER, cols=2, rows=1)
			self.AddEditNumberArrows(583, c4d.BFH_RIGHT)
			self.AddSlider(582, c4d.BFH_LEFT, initw=360)
			self.GroupEnd()
			self.SetTime(582, ACTIVE_DOC, value=CurrentTime, min=StartTime, max=EndTime, stepframes=1)
			self.SetTime(583, ACTIVE_DOC, value=CurrentTime, min=StartTime, max=EndTime, stepframes=1)
			self.GroupEnd()
			self.GroupBegin(0, c4d.BFH_SCALE, cols=3, rows=1)
			self.AddButton(552, c4d.BFH_RIGHT|c4d.BFH_SCALE, 100, 0, "View 1")
			self.AddButton(553, c4d.BFH_CENTER|c4d.BFH_SCALE, 100, 0, "View 2")
			self.AddButton(554, c4d.BFH_LEFT|c4d.BFH_SCALE, 100, 0, "View 3")
			self.GroupEnd()
			
			self.GroupBegin(0, c4d.BFH_SCALE, cols=1, rows=2)
			self.GroupSpace(0, 0)
			self.GroupBegin(0, c4d.BFH_SCALE|c4d.BFH_CENTER, cols=2, rows=1)
			self.GroupSpace(5, 0)
			self.AddStaticText(0, c4d.BFH_RIGHT, 12, 0, "τ")
			self.AddSlider(580, c4d.BFH_LEFT, initw=360)
			self.SetFloat(580, value=0, min=-2, max=2, step=0.05)
			self.GroupEnd()
			self.GroupBegin(0, c4d.BFH_SCALE|c4d.BFH_CENTER, cols=2, rows=1)
			self.GroupSpace(5, 0)
			self.AddStaticText(0, c4d.BFH_RIGHT, 12, 0, "h")
			self.AddSlider(581, c4d.BFH_LEFT, initw=180)
			self.SetFloat(581, value=15, min=-50, max=50, step=1)
			self.GroupEnd()
			self.GroupEnd()
			
			self.AddSeparatorH(300, c4d.BFH_CENTER)
			
			self.GroupBegin(0, c4d.BFH_SCALE, cols=2, rows=1)
			self.GroupSpace(20, 0)
			
			self.GroupBegin(0, c4d.BFH_SCALE|c4d.BFH_RIGHT, cols=2, rows=3)
			self.AddButton(555, c4d.BFH_SCALE|c4d.BFH_CENTER, 85, 0, "∠H + 45°")
			self.AddButton(556, c4d.BFH_SCALE|c4d.BFH_CENTER, 85, 0, "∠H - 45°")
			self.AddButton(557, c4d.BFH_SCALE|c4d.BFH_CENTER, 85, 0, "∠P + 45°")
			self.AddButton(558, c4d.BFH_SCALE|c4d.BFH_CENTER, 85, 0, "∠P - 45°")
			self.AddButton(559, c4d.BFH_SCALE|c4d.BFH_CENTER, 85, 0, "∠B + 45°")
			self.AddButton(560, c4d.BFH_SCALE|c4d.BFH_CENTER, 85, 0, "∠B - 45°")
			self.GroupEnd()
			
			self.GroupBegin(0, c4d.BFH_SCALE|c4d.BFH_LEFT, cols=1, rows=3)
			self.GroupBegin(0, c4d.BFH_SCALEFIT, cols=2, rows=1)
			self.AddStaticText(0, c4d.BFH_RIGHT, 16, 0, "H")
			self.AddEditNumberArrows(565, c4d.BFH_CENTER, initw=100)
			self.SetFloat(565, BallJoints[it].GetRelRot().x, step=math.radians(1), format=c4d.FORMAT_DEGREE)
			self.GroupEnd()
			
			self.GroupBegin(0, c4d.BFH_SCALE, cols=2, rows=1)
			self.AddStaticText(0, c4d.BFH_RIGHT, 16, 0, "P")
			self.AddEditNumberArrows(566, c4d.BFH_CENTER, initw=100)
			self.SetFloat(566, BallJoints[it].GetRelRot().y, step=math.radians(1), format=c4d.FORMAT_DEGREE)
			self.GroupEnd()
			
			self.GroupBegin(0, c4d.BFH_SCALE, cols=2, rows=1)
			self.AddStaticText(0, c4d.BFH_RIGHT, 16, 0, "B")
			self.AddEditNumberArrows(567, c4d.BFH_CENTER, initw=100)
			self.SetFloat(567, BallJoints[it].GetRelRot().z, step=math.radians(1), format=c4d.FORMAT_DEGREE)
			self.GroupEnd()
			
			
			self.GroupEnd()
			self.GroupEnd()
			
			self.GroupBegin(0, c4d.BFH_SCALE, cols=2, rows=1)
			self.GroupSpace(10,0)
			self.AddButton(575, c4d.BFH_SCALE|c4d.BFH_RIGHT, 60, 12, "Prev")
			self.Enable(575, False)
			self.AddButton(576, c4d.BFH_SCALE|c4d.BFH_LEFT, 60, 12, "Next")
			if(len(BallJoints) == 1):
				self.Enable(576, False)
			self.GroupEnd()
			
			self.GroupEnd()

			return True

		def Command(self, id, msg):
			global it
			
			def UpdateHPB():
				self.SetFloat(565, BallJoints[it].GetRelRot().x, step=math.radians(1), format=c4d.FORMAT_DEGREE)
				self.SetFloat(566, BallJoints[it].GetRelRot().y, step=math.radians(1), format=c4d.FORMAT_DEGREE)
				self.SetFloat(567, BallJoints[it].GetRelRot().z, step=math.radians(1), format=c4d.FORMAT_DEGREE)
			
			# NEXT
			if(id == 576):
				it += 1
				if(it == len(BallJoints) - 1):
					self.Enable(576, False)
				if(it > 0):
					self.Enable(575, True)
				
				SetCamera(BallJoints[it], self.GetFloat(580), self.GetFloat(581))
				self.SetString(551, "Ball Joint " + str(it + 1) + " of " + str(len(BallJoints)) + ".")
				UpdateHPB()
				return True
			
			# PREV
			if(id == 575):
				it -= 1
				if(it == 0):
					self.Enable(575, False)
				if(it < len(BallJoints) - 1):
					self.Enable(576, True)
					
				SetCamera(BallJoints[it], self.GetFloat(580), self.GetFloat(581))
				self.SetString(551, "Ball Joint " + str(it + 1) + " of " + str(len(BallJoints)) + ".")
				UpdateHPB()
				return True
					
			
			# VIEWS
			if(id == 552):
				SetCamera(BallJoints[it], -0.5, 15)
				self.SetFloat(580, value=-0.5, min=-2, max=2, step=0.05)
				self.SetFloat(581, value=15, min=-50, max=50, step=1)
				return True
			if(id == 553):
				SetCamera(BallJoints[it], 0, 15)
				self.SetFloat(580, value=0, min=-2, max=2, step=0.05)
				self.SetFloat(581, value=15, min=-50, max=50, step=1)
				return True
			if(id == 554):
				SetCamera(BallJoints[it], 0.5, 15)
				self.SetFloat(580, value=0.5, min=-2, max=2, step=0.05)
				self.SetFloat(581, value=15, min=-50, max=50, step=1)
				return True
				
			# PRECISION VIEW
			if(id == 580 or id == 581):
				SetCamera(BallJoints[it], self.GetFloat(580), self.GetFloat(581))
				return True
			
			# Quick Adjust
			# H +/- 45
			if(id == 555):
				LocalMatrix = BallJoints[it].GetMl()
				TMatrix = c4d.utils.HPBToMatrix(c4d.Vector(math.radians(45), 0, 0))
				BallJoints[it].SetMl(LocalMatrix * TMatrix)
				UpdateHPB()
				c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
				return True
			if(id == 556):
				LocalMatrix = BallJoints[it].GetMl()
				TMatrix = c4d.utils.HPBToMatrix(c4d.Vector(math.radians(-45), 0, 0))
				BallJoints[it].SetMl(LocalMatrix * TMatrix)
				UpdateHPB()
				c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
				return True
			# P +/- 45
			if(id == 557):
				LocalMatrix = BallJoints[it].GetMl()
				TMatrix = c4d.utils.HPBToMatrix(c4d.Vector(0, math.radians(45), 0))
				BallJoints[it].SetMl(LocalMatrix * TMatrix)
				UpdateHPB()
				c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
				return True
			if(id == 558):
				LocalMatrix = BallJoints[it].GetMl()
				TMatrix = c4d.utils.HPBToMatrix(c4d.Vector(0, math.radians(-45), 0))
				BallJoints[it].SetMl(LocalMatrix * TMatrix)
				UpdateHPB()
				c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
				return True
			# B +/- 45
			if(id == 559):
				LocalMatrix = BallJoints[it].GetMl()
				TMatrix = c4d.utils.HPBToMatrix(c4d.Vector(0, 0, math.radians(45)))
				BallJoints[it].SetMl(LocalMatrix * TMatrix)
				UpdateHPB()
				c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
				return True
			if(id == 560):
				LocalMatrix = BallJoints[it].GetMl()
				TMatrix = c4d.utils.HPBToMatrix(c4d.Vector(0, 0, math.radians(-45)))
				BallJoints[it].SetMl(LocalMatrix * TMatrix)
				UpdateHPB()
				c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
				return True
			
			# Precision Adjust
			if(id == 565 or id == 566 or id == 567):
				LocalMatrix = BallJoints[it].GetMl()
				if(id == 565):
					Th = self.GetFloat(565) - BallJoints[it].GetRelRot().x
					TMatrix = c4d.utils.HPBToMatrix(c4d.Vector(Th, 0, 0))
				elif(id == 566):
					Tp = self.GetFloat(566) - BallJoints[it].GetRelRot().y
					TMatrix = c4d.utils.HPBToMatrix(c4d.Vector(0, Tp, 0))
				elif(id == 567):
					Tb = self.GetFloat(567) - BallJoints[it].GetRelRot().z
					TMatrix = c4d.utils.HPBToMatrix(c4d.Vector(0, 0, Tb))

				BallJoints[it].SetMl(LocalMatrix * TMatrix)
				UpdateHPB()
				c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
				return True
			
			# FrameChange
			if(id == 582 or id == 583):
				if(id == 582):
					ACTIVE_DOC.SetTime(self.GetTime(582, ACTIVE_DOC))
					self.SetTime(583, ACTIVE_DOC, self.GetTime(582, ACTIVE_DOC), StartTime, EndTime)
				else:
					ACTIVE_DOC.SetTime(self.GetTime(583, ACTIVE_DOC))
					self.SetTime(582, ACTIVE_DOC, self.GetTime(582, ACTIVE_DOC), StartTime, EndTime)
					
				SetCamera(BallJoints[it], self.GetFloat(580), self.GetFloat(581))
				return True
			
			return False
	
	aBJUI = BJUI()
	aBJUI.Open(c4d.DLG_TYPE_MODAL, PLUGIN_ID, -1, -1, 360, 280, 500)
	
	c4d.StatusClear()
	TmpCamera.Remove()
	TmpUpVec.Remove()
	c4d.DrawViews(c4d.DRAWFLAGS_FORCEFULLREDRAW)
	UI = PrimaryUI()
	UI.Open(c4d.DLG_TYPE_MODAL, PLUGIN_ID, -1, -1, MAINUI_WIDTH, MAINUI_HEIGHT, 0) # open ui
	
# UI Definition
class PrimaryUI(gui.GeDialog):

	def CreateLayout(self):
		# Creates our layout.
		self.SetTitle(PLUGIN_NAME)
		
		# PROGRAM INFO
		self.GroupBegin(100, c4d.BFH_SCALE, 1, 6)
		
		self.GroupSpace(0, 0)
		
		self.AddStaticText(101, c4d.BFH_RIGHT, 0, 0, PLUGIN_VERSION)
		self.AddStaticText(0, c4d.BFH_CENTER, 0, 6) # spacer
		self.AddStaticText(102, c4d.BFH_CENTER, 0, 0, PLUGIN_DESCRIPTION)
		self.AddStaticText(0, c4d.BFH_CENTER, 0, 6) # spacer
		self.AddStaticText(103, c4d.BFH_CENTER, 0, 0, "Plugin by xNWP")
		self.AddStaticText(104, c4d.BFH_CENTER, 0, 0, PLUGIN_WEBPAGE)
		
		self.GroupEnd()
		
		self.AddStaticText(0, c4d.BFH_CENTER, 0, 3) # spacer
		self.AddSeparatorH(300, c4d.BFH_CENTER)
 		self.AddStaticText(0, c4d.BFH_CENTER, 0, 3) # spacer
		
		# Tools
		self.GroupBegin(200, c4d.BFH_SCALE, 1, 3, initw=420, inith=100) 
		
		self.GroupBorderNoTitle(c4d.BORDER_THIN_IN)
		
		self.AddStaticText(0, c4d.BFH_CENTER, 0, 3) # spacer
		self.AddButton(201, c4d.BFH_SCALE, 300, 0, "Delete Hitboxes/Physics Objects")
		self.AddButton(202, c4d.BFH_SCALE, 300, 0, "Fix Ball Joint Rotations")
		
		self.GroupEnd()
		
		return True
		
	def Command(self, id, msg):
		if(id == 201):
			DeletePhysicsObjs()
			return True
		if(id == 202):
			self.Close()
			FixBallJointRotations()
			return True
		
		return False

# Plugin Definition
class AGRCleanupTool(plugins.CommandData):

	def Execute(self, BaseDocument):
	# defines what happens when the user clicks the plugin in the menu
		
		# check for update
		try:
			UpdateURL = CheckUpdateAvailable(PLUGIN_UPDATE_LINK)
			if (UpdateURL != None):
				rvalue = gui.QuestionDialog("An update for " + PLUGIN_NAME + " is available, would you like to download it now?")
				if(rvalue == True):
					webbrowser.open(UpdateURL)
					return True
		except BaseException, e:
			print "-- Error checking for update to %s" % (PLUGIN_NAME)
			print str(e)
		
		UI = PrimaryUI()
		UI.Open(c4d.DLG_TYPE_MODAL, PLUGIN_ID, -1, -1, MAINUI_WIDTH, MAINUI_HEIGHT, 0) # open ui
		return True
		
# Main Definition
def main():	
	# Register the plugin
	plugins.RegisterCommandPlugin(PLUGIN_ID, PLUGIN_NAME, 0, None, PLUGIN_DESCRIPTION, AGRCleanupTool())
	
	# Console confirmation
	print "Loaded %s" % (PLUGIN_NAME)

# Main Execution
main()