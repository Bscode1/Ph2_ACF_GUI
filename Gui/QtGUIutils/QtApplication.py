from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QPixmap, QPalette,  QImage
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
		QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
		QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
		QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit, QHBoxLayout,
		QVBoxLayout, QWidget, QMainWindow, QMessageBox)

#from guidarktheme.widget_template import DarkPalette

import sys
import os
import time

from Gui.GUIutils.DBConnection import *
from Gui.GUIutils.settings import *
from Gui.GUIutils.FirmwareUtil import *
from Gui.GUIutils.GPIBInterface import PowerSupply
from Gui.QtGUIutils.PeltierCoolingApp import *
from Gui.QtGUIutils.QtFwCheckWindow  import *
from Gui.QtGUIutils.QtFwStatusWindow import *
from Gui.QtGUIutils.QtSummaryWindow import *
from Gui.QtGUIutils.QtStartWindow import *
from Gui.QtGUIutils.QtProductionTestWindow import *
from Gui.QtGUIutils.QtModuleReviewWindow import *
from Gui.QtGUIutils.QtDBConsoleWindow import *
from Gui.QtGUIutils.QtuDTCDialog import *
from Gui.python.Firmware import *
from Gui.python.ArduinoWidget import *
from Gui.QtGUIutils.QtRunWindow import *
from Gui.python.SimplifiedMainWidget import *

class QtApplication(QWidget):
	globalStop = pyqtSignal()
	def __init__(self, dimension):
		super(QtApplication,self).__init__()
		self.mainLayout = QGridLayout()
		self.setLayout(self.mainLayout)
		self.ProcessingTest = False
		self.expertMode = False
		self.FwUnderUsed = ''

		# self.FwUnderUsed = []

		self.FwDict = {}
		self.FwStatusVerboseDict = {}
		self.FPGAConfigDict = {}
		self.LogList = {}
		self.PYTHON_VERSION = str(sys.version).split(" ")[0]
		self.dimension = dimension
		self.HVpowersupply = PowerSupply(powertype = "HV",serverIndex = 1)
		self.LVpowersupply = PowerSupply(powertype = "LV",serverIndex = 2)
		self.PowerRemoteControl = {"HV":True, "LV": True}

		self.setLoginUI()
		self.initLog()
		self.createLogin()

	def setLoginUI(self):
		self.setGeometry(300, 300, 400, 500)  
		self.setWindowTitle('Phase2 Pixel Module Test GUI')

		if False and sys.platform.startswith("darwin"):
			QApplication.setStyle(QStyleFactory.create('macintosh'))
			QApplication.setPalette(QApplication.style().standardPalette())
	
		elif sys.platform.startswith("linux") or sys.platform.startswith("win") or sys.platform.startswith("darwin"):
			darkPalette = QPalette()
			darkPalette.setColor(QPalette.Window, QColor(53,53,53))
			darkPalette.setColor(QPalette.WindowText, Qt.white)
			darkPalette.setColor(QPalette.Base, QColor(25,25,25))
			darkPalette.setColor(QPalette.AlternateBase, QColor(53,53,53))
			darkPalette.setColor(QPalette.ToolTipBase, Qt.darkGray)
			darkPalette.setColor(QPalette.ToolTipText, Qt.white)
			darkPalette.setColor(QPalette.Text, Qt.white)
			darkPalette.setColor(QPalette.Button, QColor(53,53,53))
			darkPalette.setColor(QPalette.ButtonText, Qt.white)
			darkPalette.setColor(QPalette.BrightText, Qt.red)
			darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
			darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
			darkPalette.setColor(QPalette.HighlightedText, Qt.black)

			darkPalette.setColor(QPalette.Disabled, QPalette.Window, Qt.lightGray)
			darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.gray)
			darkPalette.setColor(QPalette.Disabled, QPalette.Base, Qt.darkGray)
			darkPalette.setColor(QPalette.Disabled, QPalette.ToolTipBase, Qt.darkGray)
			darkPalette.setColor(QPalette.Disabled, QPalette.ToolTipText, Qt.white)
			darkPalette.setColor(QPalette.Disabled, QPalette.Text, Qt.gray)
			darkPalette.setColor(QPalette.Disabled, QPalette.Button, QColor(73,73,73))
			darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.lightGray)
			darkPalette.setColor(QPalette.Disabled, QPalette.BrightText, Qt.lightGray)
			darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, Qt.lightGray)
			darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, Qt.gray)


			QApplication.setStyle(QStyleFactory.create('Fusion'))
			QApplication.setPalette(darkPalette)
		else:
			print("This GUI supports Win/Linux/MacOS only")
		self.show()

	def initLog(self):
		for index, (firmwareName, fwAddress) in enumerate(FirmwareList.items()):
			LogFileName = "{0}/Gui/.{1}.log".format(os.environ.get("GUI_dir"),firmwareName)
			try:
				logFile  = open(LogFileName, "w")
				self.LogList[index] = LogFileName
				logFile.close()
			except:
				QMessageBox(None,"Error","Can not create log files: {}".format(LogFileName))

	###############################################################
	##  Login page and related functions
	###############################################################
	def createLogin(self):
		self.LoginGroupBox = QGroupBox("")
		self.LoginGroupBox.setCheckable(False)

		TitleLabel = QLabel('<font size="12"> Phase2 Pixel Module Test </font>')
		TitleLabel.setFont(QFont("Courier"))
		TitleLabel.setMaximumHeight(30)

		UsernameLabel = QLabel("Username:")
		self.UsernameEdit = QLineEdit('')
		self.UsernameEdit.setEchoMode(QLineEdit.Normal)
		self.UsernameEdit.setPlaceholderText('Your username')
		self.UsernameEdit.setMinimumWidth(220)
		self.UsernameEdit.setMaximumWidth(260)
		self.UsernameEdit.setMaximumHeight(30)

		PasswordLabel = QLabel("Password:")
		self.PasswordEdit = QLineEdit('')
		self.PasswordEdit.setEchoMode(QLineEdit.Password)
		self.PasswordEdit.setPlaceholderText('Your password')
		self.PasswordEdit.setMinimumWidth(220)
		self.PasswordEdit.setMaximumWidth(260)
		self.PasswordEdit.setMaximumHeight(30)

		HostLabel = QLabel("HostName:")

		if self.expertMode == False:
			self.HostName = QComboBox()
			#self.HostName.addItems(DBServerIP.keys())
			self.HostName.addItems(dblist)
			self.HostName.currentIndexChanged.connect(self.changeDBList)
			HostLabel.setBuddy(self.HostName)
		else:
			HostLabel.setText("HostIPAddr")
			self.HostEdit = QLineEdit('128.146.38.1')
			self.HostEdit.setEchoMode(QLineEdit.Normal)
			self.HostEdit.setMinimumWidth(220)
			self.HostEdit.setMaximumWidth(260)
			self.HostEdit.setMaximumHeight(30)

		DatabaseLabel = QLabel("Database:")
		if self.expertMode == False:	
			self.DatabaseCombo = QComboBox()
			#self.DBNames = DBNames['All']
			self.DBNames = eval(self.HostName.currentText()+'.All_list')
			self.DatabaseCombo.addItems(self.DBNames)
			self.DatabaseCombo.setCurrentIndex(0)
		else:
			self.DatabaseEdit = QLineEdit('SampleDB')
			self.DatabaseEdit.setEchoMode(QLineEdit.Normal)
			self.DatabaseEdit.setMinimumWidth(220)
			self.DatabaseEdit.setMaximumWidth(260)			
			self.DatabaseEdit.setMaximumHeight(30)

		self.disableCheckBox = QCheckBox("&Do not connect to DB")
		self.disableCheckBox.setMaximumHeight(30)
		if self.expertMode:
			self.disableCheckBox.toggled.connect(self.HostEdit.setDisabled)
			self.disableCheckBox.toggled.connect(self.DatabaseEdit.setDisabled)
		else:
			self.disableCheckBox.toggled.connect(self.HostName.setDisabled)
			self.disableCheckBox.toggled.connect(self.DatabaseCombo.setDisabled)

		#self.expertCheckBox = QCheckBox("&Expert Mode")
		#self.expertCheckBox.setMaximumHeight(30)
		#self.expertCheckBox.setChecked(self.expertMode)
		#self.expertCheckBox.clicked.connect(self.switchMode)

		button_login = QPushButton("&Login")
		button_login.setDefault(True)
		button_login.clicked.connect(self.checkLogin)

		layout = QGridLayout()
		layout.setSpacing(20)
		layout.addWidget(TitleLabel,0,1,1,3,Qt.AlignCenter)
		layout.addWidget(UsernameLabel,1,1,1,1,Qt.AlignRight)
		layout.addWidget(self.UsernameEdit,1,2,1,2)
		layout.addWidget(PasswordLabel,2,1,1,1,Qt.AlignRight)
		layout.addWidget(self.PasswordEdit,2,2,1,2)
		#layout.addWidget(HostLabel,3,1,1,1,Qt.AlignRight)
		#if self.expertMode:
		#	layout.addWidget(self.HostEdit,3,2,1,2)
		#else:
		#	layout.addWidget(self.HostName,3,2,1,2)
		#layout.addWidget(DatabaseLabel,4,1,1,1,Qt.AlignRight)
		#if self.expertMode:
		#	layout.addWidget(self.DatabaseEdit,4,2,1,2)
		#else:
		#	layout.addWidget(self.DatabaseCombo,4,2,1,2)

		#######  uncomment for debugging (skips db connection) ####

		#layout.addWidget(self.disableCheckBox,5,2,1,1,Qt.AlignLeft)

		###########################################################
		#layout.addWidget(self.expertCheckBox,5,3,1,1,Qt.AlignRight)
		layout.addWidget(button_login,6,1,1,3)
		layout.setRowMinimumHeight(6, 50)

		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 1)
		layout.setColumnStretch(2, 2)
		layout.setColumnStretch(3, 1)
		self.LoginGroupBox.setLayout(layout)


		self.LogoGroupBox = QGroupBox("")
		self.LogoGroupBox.setCheckable(False)
		self.LogoGroupBox.setMaximumHeight(100)

		self.LogoLayout = QHBoxLayout()
		OSULogoLabel = QLabel()
		OSUimage = QImage("icons/osuicon.jpg").scaled(QSize(200,60), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		OSUpixmap = QPixmap.fromImage(OSUimage)
		OSULogoLabel.setPixmap(OSUpixmap)
		CMSLogoLabel = QLabel()
		CMSimage = QImage("icons/cmsicon.png").scaled(QSize(200,60), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		CMSpixmap = QPixmap.fromImage(CMSimage)
		CMSLogoLabel.setPixmap(CMSpixmap)
		self.LogoLayout.addWidget(OSULogoLabel)
		self.LogoLayout.addStretch(1)
		self.LogoLayout.addWidget(CMSLogoLabel)

		self.LogoGroupBox.setLayout(self.LogoLayout)

		self.mainLayout.addWidget(self.LoginGroupBox, 0, 0)
		self.mainLayout.addWidget(self.LogoGroupBox, 1, 0)

	def changeDBList(self):
		try:
			#self.DBNames = DBNames[str(self.HostName.currentText())]
			self.DBNames = eval(self.HostName.currentText()+'.DBName')
			self.DatabaseCombo.clear()
			self.DatabaseCombo.addItems(self.DBNames)
			self.DatabaseCombo.setCurrentIndex(0)
		except:
			print("Unable to change database")

	def switchMode(self):
		if self.expertMode:
			self.expertMode =  False
		else:
			self.expertMode = True
		self.destroyLogin()
		self.setLoginUI()
		self.createLogin()

	def destroyLogin(self):
		self.LoginGroupBox.deleteLater()
		self.LogoGroupBox.deleteLater()
		self.mainLayout.removeWidget(self.LoginGroupBox)
	
	def checkLogin(self):
		msg = QMessageBox()
		if self.UsernameEdit.text() in ExpertUserList:
			self.expertMode = True
		try:
			if self.expertMode == True:
				self.TryUsername = self.UsernameEdit.text()
				self.TryPassword = self.PasswordEdit.text()
				self.DisplayedPassword = self.PasswordEdit.displayText()
				#self.TryHostAddress = self.HostEdit.text()
				#self.TryDatabase = self.DatabaseEdit.text()
				#self.TryHostAddress = DBServerIP[str(self.HostName.currentText())]
				#self.TryDatabase = str(self.DatabaseCombo.currentText())
				self.TryHostAddress = defaultDBServerIP
				self.TryDatabase = str(defaultDBName)
			else:
				self.TryUsername = self.UsernameEdit.text()
				self.TryPassword = self.PasswordEdit.text()
				self.DisplayedPassword = self.PasswordEdit.displayText()
				#self.TryHostAddress = DBServerIP[str(self.HostName.currentText())]
				#self.TryDatabase = str(self.DatabaseCombo.currentText())
				self.TryHostAddress = defaultDBServerIP
				self.TryDatabase = str(defaultDBName)
		except:
			print("Unexpected content detected ")

		try:
			if self.TryUsername == '':
				msg.information(None,"Error","Please enter a valid username", QMessageBox.Ok)
				return
			if self.TryUsername not in ["local","localexpert"] and self.disableCheckBox.isChecked() == False:
				print("Connect to database...")
				self.connection = QtStartConnection(self.TryUsername, self.TryPassword, self.TryHostAddress, self.TryDatabase)

				if isActive(self.connection):
					self.destroyLogin()
					if self.expertMode:
						self.createMain()
					else:
						self.createSimplifiedMain()
					self.checkFirmware()
					
			else:
				self.connection = "Offline"
				self.destroyLogin()
				if self.expertMode:
					self.createMain()
					self.checkFirmware()
				else:
					self.createSimplifiedMain()
				#self.checkFirmware()

		except Exception as err:
			print("Failed to connect the database: {}".format(repr(err)))

	###############################################################
	##  Login page and related functions  (END)
	###############################################################


	###############################################################
	##  Main page for non-expert
	###############################################################
	def createSimplifiedMain(self):
		#self.welcomebox = QGroupBox("Hello,{}!".format(self.TryUsername))
		#self.FirmwareStatus.setDisabled(True)
		self.SimpleMain = SimplifiedMainWidget(self)
		self.mainLayout.addWidget(self.SimpleMain)
		'''
		##################################
		##  Testing some things out #######
		##################################
		self.simplifiedStatusBox = QGroupBox("Hello,{}!".format(self.TryUsername))
		

		statusString, colorString = checkDBConnection(self.connection)
		DBStatusLabel = QLabel()
		DBStatusLabel.setText("Database connection:")
		DBStatusValue = QLabel()
		DBStatusValue.setText(statusString)
		DBStatusValue.setStyleSheet(colorString)

		self.HVPowerStatusLabel = QLabel()
		self.HVPowerStatusValue = QLabel()
		self.LVPowerStatusLabel = QLabel()
		self.LVPowerStatusValue = QLabel()
		
		self.ModuleEntryBox = QGroupBox("Please scan module QR code")
		ModuleEntryLayout = QGridLayout()

		SerialLabel = QLabel("SerialNumber:")
		self.SerialEdit = QLineEdit()

		CableLabel = QLabel("CableNumber")
		self.CableEdit = QLineEdit()

		#Selecting default HV
		self.HVpowersupply.setPowerModel(defaultHVModel[0])
		self.HVpowersupply.setInstrument(defaultUSBPortHV[0])
		statusString = self.HVpowersupply.getInfo()
		self.HVPowerStatusLabel.setText("HV status")
		if statusString != "No valid device" and statusString != None:
			self.HVPowerStatusValue.setStyleSheet("color:green")
			self.HVPowerStatusValue.setText(statusString)
		else:
			self.HVPowerStatusValue.setStyleSheet("color:red")
			self.HVPowerStatusValue.setText("No valid device")
		time.sleep(0.5)
		#Selecting default LV
		self.LVpowersupply.setPowerModel(defaultLVModel[0])
		self.LVpowersupply.setInstrument(defaultUSBPortLV[0])
		statusString = self.LVpowersupply.getInfo()
		self.LVPowerStatusLabel.setText("LV status")
		if statusString != "No valid device" and statusString != None:
			self.LVPowerStatusValue.setStyleSheet("color:green")
			self.LVPowerStatusValue.setText(statusString)
		else:
			self.LVPowerStatusValue.setStyleSheet("color:red")
			self.LVPowerStatusValue.setText("No valid device")

		self.StatusList = []
		self.StatusList.append([DBStatusLabel, DBStatusValue])
		self.StatusList.append([self.HVPowerStatusLabel, self.HVPowerStatusValue])
		self.StatusList.append([self.LVPowerStatusLabel, self.LVPowerStatusValue])

		FC7NameLabel = QLabel()
		FC7NameLabel.setText(defaultFC7)
		FC7StatusValue = QLabel()

		firmwareName, fwAddress = defaultFC7, defaultFC7IP

		self.BeBoard = QtBeBoard()
		self.BeBoard.setBoardName(firmwareName)
		self.BeBoard.setIPAddress(FirmwareList[firmwareName])
		self.BeBoard.setFPGAConfig(FPGAConfigList[firmwareName])

		self.FwDict[firmwareName] = self.BeBoard
		self.BeBoardWidget = SimpleBeBoardBox(self.BeBoard)
	
		LogFileName = "{0}/Gui/.{1}.log".format(os.environ.get("GUI_dir"),firmwareName)
		try:
			logFile  = open(LogFileName, "w")
			logFile.close()
		except:
			QMessageBox(None,"Error","Can not create log files: {}".format(LogFileName))
		
		FwStatusComment, FwStatusColor, FwStatusVerbose = self.getFwComment(firmwareName,LogFileName)
		FC7StatusValue.setText(FwStatusComment)
		FC7StatusValue.setStyleSheet(FwStatusColor)
		self.FwModule = self.FwDict[firmwareName]
		
		self.StatusList.append([FC7NameLabel,FC7StatusValue])

		StatusLayout = QGridLayout()


		for index, items in enumerate(self.StatusList):
			StatusLayout.addWidget(items[0], index, 1,  1, 1)
			StatusLayout.addWidget(items[1], index, 2,  1, 2)


		ModuleEntryLayout.addWidget(self.BeBoardWidget)
		
		self.AppOption = QGroupBox()
		self.StartLayout = QHBoxLayout()
		self.ExitButton = QPushButton("&Exit")
		self.ExitButton.clicked.connect(self.close)
		self.RunButton = QPushButton("&Run Tests")
		self.RunButton.clicked.connect(self.runNewTest)
		self.StartLayout.addStretch(1)
		self.StartLayout.addWidget(self.ExitButton)
		self.StartLayout.addWidget(self.RunButton)
		self.AppOption.setLayout(self.StartLayout)

		
		self.simplifiedStatusBox.setLayout(StatusLayout)
		self.ModuleEntryBox.setLayout(ModuleEntryLayout)
		#self.mainLayout.addWidget(self.welcomebox)
		self.mainLayout.addWidget(self.simplifiedStatusBox)
		self.mainLayout.addWidget(self.ModuleEntryBox)
		self.mainLayout.addWidget(self.AppOption)

	def runNewTest(self):
		self.firmwareDescription = self.BeBoardWidget.getFirmwareDescription()
		self.info = [self.FwModule.getModuleByIndex(0).getOpticalGroupID(), "AllScan"]
		self.runFlag = True
		self.RunTest = QtRunWindow(self, self.info, self.firmwareDescription)
		self.LVpowersupply.setPoweringMode("Direct")
		self.LVpowersupply.setCompCurrent(compcurrent = 1.05) # Fixed for different chip
		self.LVpowersupply.TurnOn()
		######################################
		## Testin some things out (end) #######
		######################################
	'''
	###############################################################
	##  Main page and related functions
	###############################################################
	
	def createMain(self):
		statusString, colorString = checkDBConnection(self.connection)
		self.FirmwareStatus = QGroupBox("Hello,{}!".format(self.TryUsername))
		self.FirmwareStatus.setDisabled(True)
		
		DBStatusLabel = QLabel()
		DBStatusLabel.setText("Database connection:")
		DBStatusValue = QLabel()
		DBStatusValue.setText(statusString)
		DBStatusValue.setStyleSheet(colorString)


		self.StatusList = []
		self.StatusList.append([DBStatusLabel, DBStatusValue])
		

		try:
			for index, (firmwareName, fwAddress) in enumerate(FirmwareList.items()):
				FwNameLabel = QLabel()
				FwNameLabel.setText(firmwareName)
				FwStatusValue = QLabel()
				#FwStatusComment, FwStatusColor = self.getFwComment(firmwareName,fwAddress)
				#FwStatusValue.setText(FwStatusComment)
				#FwStatusValue.setStyleSheet(FwStatusColor)
				self.StatusList.append([FwNameLabel,FwStatusValue])
				self.FwStatusVerboseDict[str(firmwareName)] = {}
				BeBoard = QtBeBoard()
				BeBoard.setBoardName(firmwareName)
				BeBoard.setIPAddress(FirmwareList[firmwareName])
				BeBoard.setFPGAConfig(FPGAConfigList[firmwareName])
				self.FwDict[firmwareName] = BeBoard
		except Exception as err:
			print("Failed to list the firmware: {}".format(repr(err)))

		self.UseButtons = []

		StatusLayout = QGridLayout()

		for index, items in enumerate(self.StatusList):
			if index == 0:
				self.CheckButton = QPushButton("&Fw Check")
				self.CheckButton.clicked.connect(self.checkFirmware)
				StatusLayout.addWidget(self.CheckButton, index, 0, 1, 1)
				StatusLayout.addWidget(items[0], index, 1,  1, 1)
				StatusLayout.addWidget(items[1], index, 2,  1, 2)
			else:
				UseButton = QPushButton("&Use")
				UseButton.setDisabled(True)
				UseButton.toggle()
				UseButton.clicked.connect(lambda state, x="{0}".format(index-1) : self.switchFw(x))
				if self.PYTHON_VERSION.startswith(("3.6","3.7","3.9")):
					UseButton.clicked.connect(self.update)
				if self.PYTHON_VERSION.startswith(("3.8")):
					UseButton.clicked.connect(self.destroyMain)
					UseButton.clicked.connect(self.createMain)
					UseButton.clicked.connect(self.checkFirmware)
				UseButton.setCheckable(True)
				self.UseButtons.append(UseButton)
				StatusLayout.addWidget(UseButton, index, 0, 1, 1)
				StatusLayout.addWidget(items[0], index, 1,  1, 1)
				StatusLayout.addWidget(items[1], index, 2,  1, 2)
				FPGAConfigButton = QPushButton("&Change uDTC firmware")
				if self.expertMode is False:
					FPGAConfigButton.setDisabled(True)
					FPGAConfigButton.setToolTip('Enter expert mode to change uDTC firmware')

				FPGAConfigButton.clicked.connect(lambda state, x="{0}".format(index-1) : self.setuDTCFw(x))
				StatusLayout.addWidget(FPGAConfigButton, index, 4, 1, 1)
				SolutionButton = QPushButton("&Firmware Status")
				SolutionButton.clicked.connect(lambda state, x="{0}".format(index-1) : self.showCommentFw(x))
				StatusLayout.addWidget(SolutionButton, index, 5, 1, 1)
				LogButton = QPushButton("&Log")
				LogButton.clicked.connect(lambda state, x="{0}".format(index-1) : self.showLogFw(x))
				StatusLayout.addWidget(LogButton, index, 6, 1, 1)

		if self.FwUnderUsed != '':
			index = self.getIndex(self.FwUnderUsed,self.StatusList)
			self.occupyFw("{0}".format(index))

		#if self.FwUnderUsed != []:
		#	for fw in self.FwUnderUsed:
		#		index = self.getIndex(fw,self.StatusList)
		#		self.occupyFw("{0}".format(index))

		self.FirmwareStatus.setLayout(StatusLayout)
		self.FirmwareStatus.setDisabled(False)

		self.UseDefaultGroup = QGroupBox()
		self.DefaultLayout = QHBoxLayout()
		self.DefaultButton = QPushButton("&Connect all devices")
		self.DefaultButton.clicked.connect(self.useDefault)
		self.DefaultLabel = QLabel()
		self.DefaultLabel.setText("Connecting to all default devices...")
		self.DefaultLayout.addWidget(self.DefaultButton)
		self.DefaultLayout.addWidget(self.DefaultLabel)
		self.DefaultLayout.addStretch(1)
		self.UseDefaultGroup.setLayout(self.DefaultLayout)

		self.HVPowerRemoteControl = QCheckBox("Use HV power remote control")
		self.HVPowerRemoteControl.setChecked(True)
		self.HVPowerRemoteControl.toggled.connect(self.switchHVPowerPanel)

		self.HVPowerGroup = QGroupBox("HV Power")
		self.HVPowerLayout = QHBoxLayout()
		self.HVPowerStatusLabel = QLabel()
		self.HVPowerStatusLabel.setText("Choose HV Power:")
		self.HVPowerList = self.HVpowersupply.listResources()
		self.HVPowerCombo = QComboBox()
		self.HVPowerCombo.addItems(self.HVPowerList)
		self.HVPowerModelLabel = QLabel()
		self.HVPowerModelLabel.setText("HV Power Model:")
		self.HVPowerModelCombo = QComboBox()
		self.HVPowerModelCombo.addItems(HVPowerSupplyModel.keys())
		self.HVPowerStatusValue = QLabel()
		self.UseHVPowerSupply = QPushButton("&Use")
		self.UseHVPowerSupply.clicked.connect(self.frozeHVPowerPanel)
		self.ReleaseHVPowerSupply = QPushButton("&Release")
		self.ReleaseHVPowerSupply.clicked.connect(self.releaseHVPowerPanel)
		self.ReleaseHVPowerSupply.setDisabled(True)

		self.HVPowerLayout.addWidget(self.HVPowerStatusLabel)
		self.HVPowerLayout.addWidget(self.HVPowerCombo)
		self.HVPowerLayout.addWidget(self.HVPowerModelLabel)
		self.HVPowerLayout.addWidget(self.HVPowerModelCombo)
		self.HVPowerLayout.addWidget(self.HVPowerStatusValue)
		self.HVPowerLayout.addStretch(1)
		self.HVPowerLayout.addWidget(self.UseHVPowerSupply)
		self.HVPowerLayout.addWidget(self.ReleaseHVPowerSupply)

		self.HVPowerGroup.setLayout(self.HVPowerLayout)


		self.LVPowerRemoteControl = QCheckBox("Use LV power remote control")
		self.LVPowerRemoteControl.setChecked(True)
		self.LVPowerRemoteControl.toggled.connect(self.switchLVPowerPanel)

		self.LVPowerGroup = QGroupBox("LV Power")
		self.LVPowerLayout = QHBoxLayout()
		self.LVPowerStatusLabel = QLabel()
		self.LVPowerStatusLabel.setText("Choose LV Power:")
		self.LVPowerList = self.LVpowersupply.listResources()
		self.LVPowerCombo = QComboBox()
		self.LVPowerCombo.addItems(self.LVPowerList)
		self.LVPowerModelLabel = QLabel()
		self.LVPowerModelLabel.setText("LV Power Model:")
		self.LVPowerModelCombo = QComboBox()
		self.LVPowerModelCombo.addItems(LVPowerSupplyModel.keys())
		self.LVPowerStatusValue = QLabel()
		self.UseLVPowerSupply = QPushButton("&Use")
		self.UseLVPowerSupply.clicked.connect(self.frozeLVPowerPanel)
		self.ReleaseLVPowerSupply = QPushButton("&Release")
		self.ReleaseLVPowerSupply.clicked.connect(self.releaseLVPowerPanel)
		self.ReleaseLVPowerSupply.setDisabled(True)

		self.LVPowerLayout.addWidget(self.LVPowerStatusLabel)
		self.LVPowerLayout.addWidget(self.LVPowerCombo)
		self.LVPowerLayout.addWidget(self.LVPowerModelLabel)
		self.LVPowerLayout.addWidget(self.LVPowerModelCombo)
		self.LVPowerLayout.addWidget(self.LVPowerStatusValue)
		self.LVPowerLayout.addStretch(1)
		self.LVPowerLayout.addWidget(self.UseLVPowerSupply)
		self.LVPowerLayout.addWidget(self.ReleaseLVPowerSupply)

		self.LVPowerGroup.setLayout(self.LVPowerLayout)

		self.ArduinoGroup = ArduinoWidget()
		self.ArduinoGroup.stop.connect(self.GlobalStop)
		self.ArduinoControl = QCheckBox("Use arduino monitoring")
		self.ArduinoControl.setChecked(True)
		self.ArduinoControl.toggled.connect(self.switchArduinoPanel)

				
		self.MainOption = QGroupBox("Main")

		kMinimumWidth = 120
		kMaximumWidth = 150
		kMinimumHeight = 30
		kMaximumHeight = 100

		self.SummaryButton = QPushButton("&Status summary")
		if not self.expertMode:
			self.SummaryButton.setDisabled(True)
		self.SummaryButton.setMinimumWidth(kMinimumWidth)
		self.SummaryButton.setMaximumWidth(kMaximumWidth)
		self.SummaryButton.setMinimumHeight(kMinimumHeight)
		self.SummaryButton.setMaximumHeight(kMaximumHeight)
		self.SummaryButton.clicked.connect(self.openSummaryWindow)
		SummaryLabel = QLabel("Statistics of test status")

		self.NewTestButton = QPushButton("&New")
		self.NewTestButton.setDefault(True)
		self.NewTestButton.setMinimumWidth(kMinimumWidth)
		self.NewTestButton.setMaximumWidth(kMaximumWidth)
		self.NewTestButton.setMinimumHeight(kMinimumHeight)
		self.NewTestButton.setMaximumHeight(kMaximumHeight)
		self.NewTestButton.clicked.connect(self.openNewTest)
		self.NewTestButton.setDisabled(True)
		if self.FwUnderUsed != '':
			self.NewTestButton.setDisabled(False)
		# Vectorized fw
		#if self.FwUnderUsed != '':
		#	self.NewTestButton.setDisabled(False)
		if self.ProcessingTest == True:
			self.NewTestButton.setDisabled(True)
		NewTestLabel = QLabel("Open new test")

		self.NewProductionTestButton = QPushButton("&Production Test")
		self.NewProductionTestButton.setMinimumWidth(kMinimumWidth)
		self.NewProductionTestButton.setMaximumWidth(kMaximumWidth)
		self.NewProductionTestButton.setMinimumHeight(kMinimumHeight)
		self.NewProductionTestButton.setMaximumHeight(kMaximumHeight)
		self.NewProductionTestButton.clicked.connect(self.openNewProductionTest)
		NewProductionTestLabel = QLabel("Open production test")

		self.ReviewButton = QPushButton("&Review")
		self.ReviewButton.setMinimumWidth(kMinimumWidth)
		self.ReviewButton.setMaximumWidth(kMaximumWidth)
		self.ReviewButton.setMinimumHeight(kMinimumHeight)
		self.ReviewButton.setMaximumHeight(kMaximumHeight)
		self.ReviewButton.clicked.connect(self.openReviewWindow)
		ReviewLabel = QLabel("Review all results")

		self.ReviewModuleButton = QPushButton("&Show Module")
		self.ReviewModuleButton.setMinimumWidth(kMinimumWidth)
		self.ReviewModuleButton.setMaximumWidth(kMaximumWidth)
		self.ReviewModuleButton.setMinimumHeight(kMinimumHeight)
		self.ReviewModuleButton.setMaximumHeight(kMaximumHeight)
		self.ReviewModuleButton.clicked.connect(self.openModuleReviewWindow)
		self.ReviewModuleEdit = QLineEdit('')
		self.ReviewModuleEdit.setEchoMode(QLineEdit.Normal)
		self.ReviewModuleEdit.setPlaceholderText('Enter Module ID')

		self.PeltierCooling = Peltier(100)
		self.PeltierBox = QGroupBox("Peltier Controller",self)
		self.PeltierLayout = QGridLayout()
		self.PeltierLayout.addWidget(self.PeltierCooling)
		self.PeltierBox.setLayout(self.PeltierLayout)

		layout = QGridLayout()
		layout.addWidget(self.NewTestButton,0, 0, 1, 1)
		layout.addWidget(NewTestLabel, 0, 1, 1, 2)
		layout.addWidget(self.NewProductionTestButton,1, 0, 1, 1)
		layout.addWidget(NewProductionTestLabel, 1, 1, 1, 2)
		layout.addWidget(self.SummaryButton,2, 0, 1, 1)
		layout.addWidget(SummaryLabel, 2, 1, 1, 2)
		layout.addWidget(self.ReviewButton, 3, 0, 1, 1)
		layout.addWidget(ReviewLabel,  3, 1, 1, 2)
		layout.addWidget(self.ReviewModuleButton,4, 0, 1, 1)
		layout.addWidget(self.ReviewModuleEdit,  4, 1, 1, 2)

		####################################################
		# Functions for expert mode
		####################################################

		if self.expertMode:
			self.SummaryButton.setDisabled(False)
			self.DBConsoleButton = QPushButton("&DB Console")
			self.DBConsoleButton.setMinimumWidth(kMinimumWidth)
			self.DBConsoleButton.setMaximumWidth(kMaximumWidth)
			self.DBConsoleButton.setMinimumHeight(kMinimumHeight)
			self.DBConsoleButton.setMaximumHeight(kMaximumHeight)
			self.DBConsoleButton.clicked.connect(self.openDBConsole)
			DBConsoleLabel = QLabel("Console for database")
			layout.addWidget(self.DBConsoleButton, 5, 0, 1, 1)
			layout.addWidget(DBConsoleLabel, 5, 1, 1, 2)

		####################################################
		# Functions for expert mode  (END)
		####################################################

		self.MainOption.setLayout(layout)

		self.AppOption = QGroupBox()
		self.AppLayout = QHBoxLayout()

		if self.expertMode is False:
			self.ExpertButton = QPushButton("&Enter Expert Mode")
			self.ExpertButton.clicked.connect(self.goExpert)

		self.RefreshButton = QPushButton("&Refresh")
		if self.PYTHON_VERSION.startswith("3.8"):
			self.RefreshButton.clicked.connect(self.disableBoxs)
			self.RefreshButton.clicked.connect(self.destroyMain)
			self.RefreshButton.clicked.connect(self.createMain)
			self.RefreshButton.clicked.connect(self.checkFirmware)
			self.RefreshButton.clicked.connect(self.setDefault)
		elif self.PYTHON_VERSION.startswith(("3.7","3.9")):
			self.RefreshButton.clicked.connect(self.disableBoxs)
			self.RefreshButton.clicked.connect(self.destroyMain)
			self.RefreshButton.clicked.connect(self.reCreateMain)
			#self.RefreshButton.clicked.connect(self.checkFirmware)
			self.RefreshButton.clicked.connect(self.enableBoxs)
			self.RefreshButton.clicked.connect(self.update)
			self.RefreshButton.clicked.connect(self.setDefault)

		self.LogoutButton = QPushButton("&Logout")
		# Fixme: more conditions to be added
		if self.ProcessingTest:
			self.LogoutButton.setDisabled(True)
		self.LogoutButton.clicked.connect(self.destroyMain)
		self.LogoutButton.clicked.connect(self.setLoginUI)
		self.LogoutButton.clicked.connect(self.createLogin)

		self.ExitButton = QPushButton("&Exit")
		# Fixme: more conditions to be added
		if self.ProcessingTest:
			self.ExitButton.setDisabled(True)
		#self.ExitButton.clicked.connect(QApplication.quit)
		self.ExitButton.clicked.connect(self.close)
		if self.expertMode is False:
			self.AppLayout.addWidget(self.ExpertButton)
		self.AppLayout.addStretch(1)
		self.AppLayout.addWidget(self.RefreshButton)
		self.AppLayout.addWidget(self.LogoutButton)
		self.AppLayout.addWidget(self.ExitButton)
		self.AppOption.setLayout(self.AppLayout)

		self.mainLayout.addWidget(self.FirmwareStatus, 0,0,1,2)
		self.mainLayout.addWidget(self.UseDefaultGroup, 1,0,1,2)
		self.mainLayout.addWidget(self.HVPowerGroup, 2,0,1,2)
		self.mainLayout.addWidget(self.HVPowerRemoteControl, 3, 0,1,2)
		self.mainLayout.addWidget(self.LVPowerGroup, 4, 0,1,2)
		self.mainLayout.addWidget(self.LVPowerRemoteControl, 5, 0,1,2)
		self.mainLayout.addWidget(self.ArduinoGroup, 6, 0,1,2)
		self.mainLayout.addWidget(self.ArduinoControl, 7, 0,1,2)
		self.mainLayout.addWidget(self.MainOption,8, 0,1,1)
		self.mainLayout.addWidget(self.PeltierBox, 8,1,1,1)
		self.mainLayout.addWidget(self.AppOption, 9, 0,1,2)

		self.setDefault()
	
	def setDefault(self):
		if self.expertMode is False:
			self.HVPowerGroup.setDisabled(True)
			self.HVPowerRemoteControl.setDisabled(True)
			self.LVPowerGroup.setDisabled(True)
			self.LVPowerRemoteControl.setDisabled(True)
			self.ArduinoGroup.disable()
			self.ArduinoControl.setDisabled(True)

	def useDefault(self):
			#self.HVPowerCombo.clear()
			HVIndex = self.HVPowerCombo.findText(defaultUSBPortHV[0])
			if HVIndex != -1:
				self.HVPowerCombo.setCurrentIndex(HVIndex)
			#self.HVPowerCombo.addItems(defaultUSBPortHV)
			#elf.HVPowerModelCombo.clear()
			#self.HVPowerModelCombo.addItems(defaultHVModel)
			#self.LVPowerCombo.clear()
			LVIndex = self.LVPowerCombo.findText(defaultUSBPortLV[0])
			if LVIndex != -1:
				self.LVPowerCombo.setCurrentIndex(LVIndex)
			#self.LVPowerCombo.addItems(defaultUSBPortLV)
			#self.LVPowerModelCombo.clear()
			#self.LVPowerModelCombo.addItems(defaultLVModel)
			self.frozeHVPowerPanel()
			self.frozeLVPowerPanel()
			self.ArduinoGroup.setBaudRate(defaultSensorBaudRate)
			self.ArduinoGroup.frozeArduinoPanel()



	def reCreateMain(self):
		print("Refreshing the main page")
		self.createMain()
		self.checkFirmware()


	def disableBoxs(self):
		self.FirmwareStatus.setDisabled(True)
		self.MainOption.setDisabled(True)
	
	def enableBoxs(self):
		self.FirmwareStatus.setDisabled(False)
		self.MainOption.setDisabled(False)

	def destroyMain(self):
		self.expertMode = False
		self.FirmwareStatus.deleteLater()
		self.UseDefaultGroup.deleteLater()
		self.HVPowerGroup.deleteLater()
		self.HVPowerRemoteControl.deleteLater()
		self.LVPowerGroup.deleteLater()
		self.LVPowerRemoteControl.deleteLater()
		self.ArduinoGroup.deleteLater()
		self.ArduinoControl.deleteLater()
		self.MainOption.deleteLater()
		self.AppOption.deleteLater()
		self.mainLayout.removeWidget(self.FirmwareStatus)
		self.mainLayout.removeWidget(self.HVPowerGroup)
		self.mainLayout.removeWidget(self.UseDefaultGroup)
		self.mainLayout.removeWidget(self.HVPowerRemoteControl)
		self.mainLayout.removeWidget(self.LVPowerGroup)
		self.mainLayout.removeWidget(self.LVPowerRemoteControl)
		self.mainLayout.removeWidget(self.ArduinoGroup)
		self.mainLayout.removeWidget(self.ArduinoControl)
		self.mainLayout.removeWidget(self.MainOption)
		self.mainLayout.removeWidget(self.AppOption)

	def openNewProductionTest(self):
		self.ProdTestPage = QtProductionTestWindow(self, HV= self.HVpowersupply, LV = self.LVpowersupply)
		self.ProdTestPage.close.connect(self.releaseProdTestButton)
		self.NewProductionTestButton.setDisabled(True)
		self.LogoutButton.setDisabled(True)
		self.ExitButton.setDisabled(True)

	def openNewTest(self):
		FwModule = self.FwDict[self.FwUnderUsed]
		# Vectorized the firmware
		#FwModule = []
		#for fw in self.FwUnderUsed:
		#	FwModule.append(self.FwDict[fw])
		self.StartNewTest = QtStartWindow(self,FwModule)
		self.NewTestButton.setDisabled(True)
		self.LogoutButton.setDisabled(True)
		self.ExitButton.setDisabled(True)
		pass

	def openSummaryWindow(self):
		self.SummaryViewer = QtSummaryWindow(self)
		self.SummaryButton.setDisabled(True)

	def openReviewWindow(self):
		self.ReviewWindow =  QtModuleReviewWindow(self)

	def openModuleReviewWindow(self):
		Module_ID = self.ReviewModuleEdit.text()
		if Module_ID != "":
			self.ModuleReviewWindow =  QtModuleReviewWindow(self, Module_ID)
		else:
			QMessageBox.information(None, "Error", "Please enter a valid module ID", QMessageBox.Ok)

	def openDBConsole(self):
		self.StartDBConsole = QtDBConsoleWindow(self)

	def switchHVPowerPanel(self):
		if self.HVPowerRemoteControl.isChecked():
			self.HVPowerGroup.setDisabled(False)
			self.PowerRemoteControl["HV"] = True
		else:
			self.HVPowerGroup.setDisabled(True)
			self.PowerRemoteControl["HV"] = False
	
	def frozeHVPowerPanel(self):
		# Block for HVPowerSupply operation
		#self.HVpowersupply.setPowerModel(HVPowerSupplyModel[self.HVPowerModelCombo.currentText()])
		self.HVpowersupply.setPowerModel(self.HVPowerModelCombo.currentText())
		self.HVpowersupply.setInstrument(self.HVPowerCombo.currentText())
		#self.HVpowersupply.TurnOn()
		# Block for GUI front-end
		statusString = self.HVpowersupply.getInfo()
		if statusString != "No valid device" and statusString != None:
			self.HVPowerStatusValue.setStyleSheet("color:green")
			self.HVPowerCombo.setDisabled(True)
			self.HVPowerStatusValue.setText(statusString)
			self.UseHVPowerSupply.setDisabled(True)
			self.ReleaseHVPowerSupply.setDisabled(False)
		else:
			self.HVPowerStatusValue.setStyleSheet("color:red")
			self.HVPowerStatusValue.setText("No valid device")

	def releaseHVPowerPanel(self):
		self.HVpowersupply.TurnOff()
		try:
			self.HVPowerCombo.setDisabled(False)
			self.HVPowerStatusValue.setText("")
			self.UseHVPowerSupply.setDisabled(False)
			self.ReleaseHVPowerSupply.setDisabled(True)
			self.HVPowerList = self.HVpowersupply.listResources()
		#with Exception as err:
		except Exception as err:
			print("HV PowerPanel not released properly")

	def switchLVPowerPanel(self):
		if self.LVPowerRemoteControl.isChecked():
			self.LVPowerGroup.setDisabled(False)
			self.PowerRemoteControl["LV"] = True
		else:
			self.LVPowerGroup.setDisabled(True)
			self.PowerRemoteControl["LV"] = False
	
	def frozeLVPowerPanel(self):
		# Block for LVPowerSupply operation
		self.LVpowersupply.setPowerModel(self.LVPowerModelCombo.currentText())
		self.LVpowersupply.setInstrument(self.LVPowerCombo.currentText())
		#self.LVpowersupply.getInfo()
		#self.LVpowersupply.TurnOn()
		# Block for GUI front-end
		statusString = self.LVpowersupply.getInfo()
		if statusString != "No valid device":
			self.LVPowerStatusValue.setStyleSheet("color:green")
		else:
			self.LVPowerStatusValue.setStyleSheet("color:red")
		if statusString:
			self.LVPowerCombo.setDisabled(True)
			self.LVPowerStatusValue.setText(statusString)
			self.UseLVPowerSupply.setDisabled(True)
			self.ReleaseLVPowerSupply.setDisabled(False)
		else:
			self.LVPowerStatusValue.setStyleSheet("color:red")
			self.LVPowerStatusValue.setText("No valid device")

	def releaseLVPowerPanel(self):
		self.LVpowersupply.TurnOff()
		self.LVPowerCombo.setDisabled(False)
		self.LVPowerStatusValue.setText("")
		self.UseLVPowerSupply.setDisabled(False)
		self.ReleaseLVPowerSupply.setDisabled(True)
		self.LVPowerList = self.LVpowersupply.listResources()

	def switchArduinoPanel(self):
		if self.ArduinoControl.isChecked():
			self.ArduinoGroup.enable()
		else:
			self.ArduinoGroup.disable()

	def checkFirmware(self):
		for index, (firmwareName, fwAddress) in enumerate(FirmwareList.items()):
			fileName = self.LogList[index]
			if firmwareName != self.FwUnderUsed:
			#if firmwareName not in self.FwUnderUsed:
				FwStatusComment, FwStatusColor, FwStatusVerbose = self.getFwComment(firmwareName,fileName)
				self.StatusList[index+1][1].setText(FwStatusComment)
				self.StatusList[index+1][1].setStyleSheet(FwStatusColor)
				self.FwStatusVerboseDict[str(firmwareName)] = FwStatusVerbose
			#This if was added for a test.  
			if self.expertMode:
				self.UseButtons[index].setDisabled(False)
		if self.FwUnderUsed != '':
			index = self.getIndex(self.FwUnderUsed,self.StatusList)
			self.StatusList[index+1][1].setText("Connected")
			self.StatusList[index+1][1].setStyleSheet("color: green")
			self.occupyFw("{0}".format(index))
		#if self.FwUnderUsed != []:
		#	for fw in self.FwUnderUsed:
		#		index = self.getIndex(fw,self.StatusList)
		#		self.StatusList[index+1][1].setText("Connected")
		#		self.StatusList[index+1][1].setStyleSheet("color: green")
		#		self.occupyFw("{0}".format(index))
	
	def refreshFirmware(self):
		for index, (firmwareName, fwAddress) in enumerate(FirmwareList.items()):
			self.UseButtons[index].setDisabled(False)
		if self.FwUnderUsed != '':
			index = self.getIndex(self.FwUnderUsed,self.StatusList)
			self.occupyFw("{0}".format(index))

		#if self.FwUnderUsed != []:
		#	for fw in self.FwUnderUsed:
		#		index = self.getIndex(self.fw,self.StatusList)
		#		self.occupyFw("{0}".format(index))


	def getFwComment(self,firmwareName,fileName):
		comment,color, verboseInfo = fwStatusParser(self.FwDict[firmwareName],fileName)
		return comment,color, verboseInfo

	def getIndex(self, element, List2D):
		for index, item in enumerate(List2D):
			if item[0].text() == element:
				return index - 1
		return -1

	def switchFw(self, index):
		if self.UseButtons[int(index)].isChecked():
			self.occupyFw(index)
		else:
			self.releaseFw(index)
			self.checkFirmware

	def occupyFw(self, index):
		if self.StatusList[int(index)+1][1].text() == "Connected":
			self.NewTestButton.setDisabled(False)
		for i ,button in enumerate(self.UseButtons):
			if i == int(index):
				button.setChecked(True)
				button.setText("&In use")
				button.setDisabled(False)
				self.CheckButton.setDisabled(True)
				self.FwUnderUsed = self.StatusList[i+1][0].text()
				#self.FwUnderUsed.append(self.StatusList[i+1][0].text())
			else:
				button.setDisabled(True)

	def releaseFw(self, index):
		for i ,button in enumerate(self.UseButtons):
			if i == int(index):
				self.FwUnderUsed = ''
				# vectorzied fw
				#fwIndex = self.FwUnderUsed.index(self.StatusList[i+1][0].text())
				#self.FwUnderUsed.pop(fwIndex)
				button.setText("&Use")
				button.setDown(False)
				button.setDisabled(False)
				self.CheckButton.setDisabled(False)
				self.NewTestButton.setDisabled(True)
			else:
				button.setDisabled(False)

	def showCommentFw(self, index):
		fwName  = self.StatusList[int(index)+1][0].text()
		comment = self.StatusList[int(index)+1][1].text()
		solution = FwStatusCheck[comment]
		verboseInfo =  self.FwStatusVerboseDict[self.StatusList[int(index)+1][0].text()]
		#QMessageBox.information(None, "Info", "{}".format(solution), QMessageBox.Ok)
		self.FwStatusWindow = QtFwStatusWindow(self,fwName,verboseInfo,solution)


	def showLogFw(self, index):
		fileName = self.LogList[int(index)]
		self.FwLogWindow = QtFwCheckWindow(self,fileName)

	def setuDTCFw(self, index):
		fwName = self.StatusList[int(index)+1][0].text()
		firmware = self.FwDict[fwName]
		changeuDTCDialog = QtuDTCDialog(self,firmware)

		response = changeuDTCDialog.exec_()
		if response == QDialog.Accepted:
			firmware.setFPGAConfig(changeuDTCDialog.uDTCFile)
		
		self.checkFirmware()
	
	def releaseProdTestButton(self):
		self.NewProductionTestButton.setDisabled(False)
		self.LogoutButton.setDisabled(False)
		self.ExitButton.setDisabled(False)

	def goExpert(self):
		self.expertMode = True

		## Authority check for expert mode

		self.destroyMain()
		self.createMain()
		self.checkFirmware()

			
	###############################################################
	##  Global stop signal
	###############################################################
	@QtCore.pyqtSlot()
	def GlobalStop(self):
		print("Critical status detected: Emitting Global Stop signal")
		self.globalStop.emit()
		self.HVpowersupply.TurnOff()
		self.LVpowersupply.TurnOff()
		if self.expertMode == True:
			self.releaseHVPowerPanel()
			self.releaseLVPowerPanel()


	###############################################################
	##  Main page and related functions  (END)
	###############################################################

	def closeEvent(self, event):
		#Fixme: strict criterias for process checking  should be added here:
		#if self.ProcessingTest == True:
		#	QMessageBox.critical(self, 'Critical Message', 'There is running process, can not close!')
		#	event.ignore()

		reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to exit ?',
			QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			print('Application terminated')
			self.HVpowersupply.TurnOff()
			self.LVpowersupply.TurnOff()

			# If you didn't start the Peltier controller, tempPower won't be defined
			try:
				self.PeltierCooling.shutdown()
			except AttributeError:
				pass

			os.system("rm -r {}/Gui/.tmp/*".format(os.environ.get("GUI_dir")))
			event.accept()
		else:
			event.ignore()


		
