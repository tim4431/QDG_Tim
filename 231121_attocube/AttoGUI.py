from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QDialog,
    QSpinBox,
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from AttocubeANC300 import AttocubeANC300
from PyQt5.QtWidgets import QGridLayout
import time
from PyQt5.QtCore import QTimer
import numpy as np


class AttocubeControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize your AttocubeANC300 class here
        self.attocube = AttocubeANC300(commandline=False, constant_mode=False)
        self._x = self.attocube.x  # type: ignore
        self._y = self.attocube.y  # type: ignore
        self._z = self.attocube.z  # type: ignore
        self._last_x = self._x
        self._last_y = self._y
        self._last_z = self._z
        #
        self.BOUND_SIZE = 1000
        self.BOUND_STEP_SIZE = 10

        self.movementTimer = QTimer(self)
        self.movementTimer.setInterval(100)
        self.movementTimer.timeout.connect(self.step_move)

        self.moveAxis = None
        self.moveDirection = None
        self.START_STEP_SIZE = 1
        self.stepSize = self.START_STEP_SIZE
        self.STEP_INCREASE_RATE = 2
        self.MAX_STEP_SIZE = 50
        self._locked_movement = False

        self.stepsizeTimer = QTimer(self)
        self.stepsizeTimer.setInterval(200)
        self.stepsizeTimer.timeout.connect(self.increaseStepSize)

        self.historyPosition = []
        self.updatePlotNumber = 0

        self.initUI()
        # set global font
        font = self.font()
        font.setPointSize(10)
        font.setFamily("Open Sans")
        self.setFont(font)

    @property
    def position(self):
        return self._x, self._y, self._z

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value: int):
        self._last_x = self._x
        if not self._locked_movement:
            self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value: int):
        self._last_y = self._y
        if not self._locked_movement:
            self._y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value: int):
        self._last_z = self._z
        if not self._locked_movement:
            self._z = value

    def retrive_last_x(self):
        self._x = self._last_x

    def retrive_last_y(self):
        self._y = self._last_y

    def retrive_last_z(self):
        self._z = self._last_z

    def retrive_last_position(self):
        self._x = self._last_x
        self._y = self._last_y
        self._z = self._last_z

    def initUI(self):
        self.setWindowTitle("Attocube ANC300 Controller")
        self.setGeometry(50, 50, 700, 800)

        def addTitle(text: str):
            label = QLabel(text)
            font = label.font()
            # font.setFamily("Arial")
            font.setPointSize(12)
            font.setBold(True)
            label.setFont(font)
            layout.addWidget(label)

        # Main layout
        layout = QVBoxLayout()

        # Frequency and voltage controls
        addTitle("ANC300 Static Settings")
        self.freq_voltage_layout = QHBoxLayout()
        self.initFreqVoltageControls()
        layout.addLayout(self.freq_voltage_layout)

        # Movement control buttons
        addTitle("Movement controls (in steps)")
        self.movement_control_layout = QHBoxLayout()
        self.initMovementControls()
        layout.addLayout(self.movement_control_layout)

        # Plot for current position
        addTitle("Current position")
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Set main widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Update plot
        self.updatePlot()

    def closeApplication(self):
        # Stop the thread here
        self.attocube.stop_constant_move()
        # Exit the application
        QApplication.quit()

    def closeEvent(self, event):
        # Call the close application method
        self.closeApplication()
        event.accept()

    def initFreqVoltageControls(self):
        # Create a grid layout
        gridLayout = QGridLayout()
        labelIP = QLabel("IP Address:")
        self.inputIP = QLineEdit(self)
        self.inputIP.setText(str(self.attocube.address))
        self.inputIP.editingFinished.connect(self.updateAddress)
        #
        self.button_s200a = QPushButton("s200a")
        self.button_s200a.clicked.connect(self.address_s200a)
        self.button_s200b = QPushButton("s200b")
        self.button_s200b.clicked.connect(self.address_s200b)

        gridLayout.addWidget(labelIP, 0, 0)
        gridLayout.addWidget(self.inputIP, 0, 1)
        gridLayout.addWidget(self.button_s200a, 1, 0)
        gridLayout.addWidget(self.button_s200b, 1, 1)

        # connect button & status Label
        self.connectButton = QPushButton("Connect")
        self.connectButton.clicked.connect(self.connectAttocube)
        self.connectedLabel = QLabel("Disconnected")
        self.connectedLabel.setAlignment(Qt.AlignCenter)  # type: ignore
        self.connectedLabel.setStyleSheet("color: red")
        gridLayout.addWidget(self.connectButton, 0, 2)
        gridLayout.addWidget(self.connectedLabel, 1, 2)

        # Example for X axis
        self.labelFreqX = QLabel("X Freq (Hz):")
        self.inputFreqX = QLineEdit(self)
        self.inputFreqX.setText(str(self.attocube.freq_x))
        self.inputFreqX.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelFreqX, 0, 3)
        gridLayout.addWidget(self.inputFreqX, 0, 4)

        # Y
        self.labelFreqY = QLabel("Y Freq (Hz):")
        self.inputFreqY = QLineEdit(self)
        self.inputFreqY.setText(str(self.attocube.freq_y))
        self.inputFreqY.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelFreqY, 0, 5)
        gridLayout.addWidget(self.inputFreqY, 0, 6)

        # Z
        self.labelFreqZ = QLabel("Z Freq (Hz):")
        self.inputFreqZ = QLineEdit(self)
        self.inputFreqZ.setText(str(self.attocube.freq_z))
        self.inputFreqZ.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelFreqZ, 0, 7)
        gridLayout.addWidget(self.inputFreqZ, 0, 8)

        # Add similar widgets for voltage
        # X
        self.labelVoltageX = QLabel("X Volt (V):")
        self.inputVoltageX = QLineEdit(self)
        self.inputVoltageX.setText(str(self.attocube.volt_x))
        self.inputVoltageX.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelVoltageX, 1, 3)
        gridLayout.addWidget(self.inputVoltageX, 1, 4)

        # Y
        self.labelVoltageY = QLabel("Y Volt (V):")
        self.inputVoltageY = QLineEdit(self)
        self.inputVoltageY.setText(str(self.attocube.volt_y))
        self.inputVoltageY.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelVoltageY, 1, 5)
        gridLayout.addWidget(self.inputVoltageY, 1, 6)

        # Z
        self.labelVoltageZ = QLabel("Z Volt (V):")
        self.inputVoltageZ = QLineEdit(self)
        self.inputVoltageZ.setText(str(self.attocube.volt_z))
        self.inputVoltageZ.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelVoltageZ, 1, 7)
        gridLayout.addWidget(self.inputVoltageZ, 1, 8)

        # Set the layout for the frequency and voltage controls
        gridLayout.setColumnStretch(0, 2)
        gridLayout.setColumnStretch(1, 2)
        gridLayout.setColumnStretch(2, 1)
        gridLayout.setColumnStretch(3, 1)
        gridLayout.setColumnStretch(4, 1)
        gridLayout.setColumnStretch(5, 1)
        gridLayout.setColumnStretch(6, 1)
        gridLayout.setColumnStretch(7, 1)
        gridLayout.setColumnStretch(8, 1)
        self.freq_voltage_layout.addLayout(gridLayout)

    def address_s200a(self):
        self.attocube.address = "192.168.0.101"
        self.inputIP.setText(str(self.attocube.address))

    def address_s200b(self):
        self.attocube.address = "192.168.0.91"
        self.inputIP.setText(str(self.attocube.address))

    def connectAttocube(self):
        self.connectedLabel.setText("Connecting...")
        self.connectedLabel.setStyleSheet("color: blue")
        QApplication.processEvents()
        #
        self.attocube.init_Controller()
        #
        if self.attocube.connected:
            self.connectedLabel.setText("Connected")
            self.connectedLabel.setStyleSheet("color: green")
            self.displayFreqVoltageControls()
        else:
            self.connectedLabel.setText("Disconnected")
            self.connectedLabel.setStyleSheet("color: red")
        #
        QApplication.processEvents()

    def updateAddress(self):
        new_address = str(self.inputIP.text())
        self.attocube.address = new_address
        self.inputIP.setText(str(self.attocube.address))

    def updateFreqVoltageControls(self):
        # X
        new_freq_x = int(self.inputFreqX.text())
        self.attocube.freq_x = new_freq_x
        # Y
        new_freq_y = int(self.inputFreqY.text())
        self.attocube.freq_y = new_freq_y
        # Z
        new_freq_z = int(self.inputFreqZ.text())
        self.attocube.freq_z = new_freq_z
        # X
        new_volt_x = float(self.inputVoltageX.text())
        self.attocube.volt_x = new_volt_x
        # Y
        new_volt_y = float(self.inputVoltageY.text())
        self.attocube.volt_y = new_volt_y
        # Z
        new_volt_z = float(self.inputVoltageZ.text())
        self.attocube.volt_z = new_volt_z

    def displayFreqVoltageControls(self):
        self.inputFreqX.setText(str(self.attocube.freq_x))
        self.inputFreqY.setText(str(self.attocube.freq_y))
        self.inputFreqZ.setText(str(self.attocube.freq_z))
        self.inputVoltageX.setText(str(self.attocube.volt_x))
        self.inputVoltageY.setText(str(self.attocube.volt_y))
        self.inputVoltageZ.setText(str(self.attocube.volt_z))

    def initMovementControls(self):
        controlLayout = QHBoxLayout()
        # self.centralWidget = QWidget()
        # self.setCentralWidget(self.centralWidget)

        # Z axis buttons
        ZcontrolWidget = QWidget()
        ZcontrolLayout = QGridLayout(ZcontrolWidget)
        self.moveLeftZ = QPushButton("Z-- (d)")
        self.moveRightZ = QPushButton("Z++ (u)")
        labelCurrentZ = QLabel("Z:")
        self.inputCurrentZ = QLineEdit(self)
        self.inputCurrentZ.setText(str(self.attocube.z))
        self.inputCurrentZ.editingFinished.connect(self.updateFromText)
        labelBoundZmin = QLabel("Z min:")
        self.inputBoundZmin = QSpinBox(self)
        self.inputBoundZmin.setRange(-self.BOUND_SIZE, self.BOUND_SIZE)
        self.inputBoundZmin.setSingleStep(self.BOUND_STEP_SIZE)
        self.inputBoundZmin.setValue(self.attocube.zmin)
        self.inputBoundZmin.editingFinished.connect(self.updateBound)
        labelBoundZmax = QLabel("Z max:")
        self.inputBoundZmax = QSpinBox(self)
        self.inputBoundZmax.setRange(-self.BOUND_SIZE, self.BOUND_SIZE)
        self.inputBoundZmax.setSingleStep(self.BOUND_STEP_SIZE)
        self.inputBoundZmax.setValue(self.attocube.zmax)
        self.inputBoundZmax.editingFinished.connect(self.updateBound)
        #
        ZcontrolLayout.addWidget(self.moveRightZ, 0, 0, 1, 2)
        ZcontrolLayout.addWidget(labelBoundZmax, 1, 0)
        ZcontrolLayout.addWidget(self.inputBoundZmax, 1, 1)
        ZcontrolLayout.addWidget(labelCurrentZ, 2, 0)
        ZcontrolLayout.addWidget(self.inputCurrentZ, 2, 1)
        ZcontrolLayout.addWidget(labelBoundZmin, 3, 0)
        ZcontrolLayout.addWidget(self.inputBoundZmin, 3, 1)
        ZcontrolLayout.addWidget(self.moveLeftZ, 4, 0, 1, 2)
        # the keyboard u is for Z++
        # the keyboard d is for Z--
        self.moveLeftZ.setShortcut(Qt.Key_D)  # type: ignore
        self.moveRightZ.setShortcut(Qt.Key_U)  # type: ignore

        # X and Y axis buttons
        self.moveLeftX = QPushButton("X-- (<)")
        self.moveRightX = QPushButton("X++ (>)")
        self.moveLeftY = QPushButton("Y-- (v)")
        self.moveRightY = QPushButton("Y++ (^)")
        # the keyboard -> is for X++
        # the keyboard <- is for X--
        # the keyboard up arrow is for Y++
        # the keyboard down arrow is for Y--
        self.moveLeftX.setShortcut(Qt.Key_Left)  # type: ignore
        self.moveRightX.setShortcut(Qt.Key_Right)  # type: ignore
        self.moveLeftY.setShortcut(Qt.Key_Down)  # type: ignore
        self.moveRightY.setShortcut(Qt.Key_Up)  # type: ignore

        # Current X, Y, Z values display
        # self.currentXYZDisplay = QLabel("X: 0, Y: 0, Z: 0")
        # self.currentXYZDisplay.setAlignment(Qt.AlignCenter)  # type: ignore
        labelCurrentX = QLabel("X:")
        self.inputCurrentX = QLineEdit(self)
        self.inputCurrentX.setText(str(self.attocube.x))
        self.inputCurrentX.editingFinished.connect(self.updateFromText)
        labelBoundXmax = QLabel("X max:")
        self.inputBoundXmax = QSpinBox(self)
        self.inputBoundXmax.setRange(-self.BOUND_SIZE, self.BOUND_SIZE)
        self.inputBoundXmax.setSingleStep(self.BOUND_STEP_SIZE)
        self.inputBoundXmax.setValue(self.attocube.xmax)
        self.inputBoundXmax.editingFinished.connect(self.updateBound)
        labelBoundXmin = QLabel("X min:")
        self.inputBoundXmin = QSpinBox(self)
        self.inputBoundXmin.setRange(-self.BOUND_SIZE, self.BOUND_SIZE)
        self.inputBoundXmin.setSingleStep(self.BOUND_STEP_SIZE)
        self.inputBoundXmin.setValue(self.attocube.xmin)
        self.inputBoundXmin.editingFinished.connect(self.updateBound)
        #
        labelCurrentY = QLabel("Y:")
        self.inputCurrentY = QLineEdit(self)
        self.inputCurrentY.setText(str(self.attocube.y))
        self.inputCurrentY.editingFinished.connect(self.updateFromText)
        labelBoundYmax = QLabel("Y max:")
        self.inputBoundYmax = QSpinBox(self)
        self.inputBoundYmax.setRange(-self.BOUND_SIZE, self.BOUND_SIZE)
        self.inputBoundYmax.setSingleStep(self.BOUND_STEP_SIZE)
        self.inputBoundYmax.setValue(self.attocube.ymax)
        self.inputBoundYmax.editingFinished.connect(self.updateBound)
        labelBoundYmin = QLabel("Y min:")
        self.inputBoundYmin = QSpinBox(self)
        self.inputBoundYmin.setRange(-self.BOUND_SIZE, self.BOUND_SIZE)
        self.inputBoundYmin.setSingleStep(self.BOUND_STEP_SIZE)
        self.inputBoundYmin.setValue(self.attocube.ymin)
        self.inputBoundYmin.editingFinished.connect(self.updateBound)
        #
        positionWidget = QWidget()
        positionLayout = QGridLayout(positionWidget)
        positionLayout.setSpacing(2)  # Set the spacing between widgets to 2 pixels
        positionLayout.addWidget(labelCurrentX, 0, 0)
        positionLayout.addWidget(self.inputCurrentX, 0, 1)
        positionLayout.addWidget(labelCurrentY, 1, 0)
        positionLayout.addWidget(self.inputCurrentY, 1, 1)
        #
        XLeftWidget = QWidget()
        XLeftLayout = QGridLayout(XLeftWidget)
        XLeftLayout.setSpacing(2)  # Set the spacing between widgets to 2 pixels
        XLeftLayout.addWidget(self.moveLeftX, 0, 0, 1, 2)
        XLeftLayout.addWidget(labelBoundXmin, 1, 0)
        XLeftLayout.addWidget(self.inputBoundXmin, 1, 1)
        #
        XRightWidget = QWidget()
        XRightLayout = QGridLayout(XRightWidget)
        XRightLayout.setSpacing(2)  # Set the spacing between widgets to 2 pixels
        XRightLayout.addWidget(self.moveRightX, 0, 0, 1, 2)
        XRightLayout.addWidget(labelBoundXmax, 1, 0)
        XRightLayout.addWidget(self.inputBoundXmax, 1, 1)
        #
        YLeftWidget = QWidget()
        YLeftLayout = QGridLayout(YLeftWidget)
        YLeftLayout.setSpacing(2)  # Set the spacing between widgets to 2 pixels
        YLeftLayout.addWidget(self.moveLeftY, 0, 0, 1, 2)
        YLeftLayout.addWidget(labelBoundYmin, 1, 0)
        YLeftLayout.addWidget(self.inputBoundYmin, 1, 1)
        #
        YRightWidget = QWidget()
        YRightLayout = QGridLayout(YRightWidget)
        YRightLayout.setSpacing(2)  # Set the spacing between widgets to 2 pixels
        YRightLayout.addWidget(self.moveRightY, 0, 0, 1, 2)
        YRightLayout.addWidget(labelBoundYmax, 1, 0)
        YRightLayout.addWidget(self.inputBoundYmax, 1, 1)
        #
        ringWidget = QWidget()
        ringLayout = QGridLayout(ringWidget)
        ringLayout.addWidget(XLeftWidget, 1, 0)
        ringLayout.addWidget(XRightWidget, 1, 2)
        ringLayout.addWidget(positionWidget, 1, 1)
        ringLayout.addWidget(YRightWidget, 0, 1)
        ringLayout.addWidget(YLeftWidget, 2, 1)
        #
        # ringLayout.setColumnStretch(1, 1)
        # ringLayout.setColumnStretch(0, 1)
        # ringLayout.setColumnStretch(2, 1)

        # goto to zero buttons
        self.gotozeroX = QPushButton("X = 0")
        self.gotoZeroY = QPushButton("Y = 0")
        self.gotoZeroZ = QPushButton("Z = 0")
        self.gotoOrigin = QPushButton("X,Y,Z = 0")
        self.setOrigin = QPushButton("Set Origin")
        zeroWidget = QWidget()
        zeroLayout = QVBoxLayout(zeroWidget)
        zeroLayout.addWidget(self.gotozeroX)
        zeroLayout.addWidget(self.gotoZeroY)
        zeroLayout.addWidget(self.gotoZeroZ)
        zeroLayout.addWidget(self.gotoOrigin)
        zeroLayout.addWidget(self.setOrigin)

        # Status label
        lockLabel = QLabel("Movement Lock")
        self.lockButton = QPushButton("Lock")
        self.lockButton.setCheckable(True)
        self.lockButton.clicked.connect(self.lockMovement)
        self.statusLabel = QLabel("Status:")
        self.statusLabel.setAlignment(Qt.AlignCenter)  # type: ignore
        self.statusText = QLabel("Idle")
        self.statusText.setAlignment(Qt.AlignCenter)  # type: ignore
        self.statusText.setStyleSheet("color: green")
        self.movestatusLabel = QLabel("Next move")
        self.movestatusLabel.setAlignment(Qt.AlignCenter)  # type: ignore
        self.movestatusText = QLabel("OK")
        self.movestatusText.setAlignment(Qt.AlignCenter)  # type: ignore
        self.movestatusText.setStyleSheet("color: green")

        statusWidget = QWidget()
        statusLayout = QVBoxLayout(statusWidget)
        statusLayout.addWidget(lockLabel)
        statusLayout.addWidget(self.lockButton)
        statusLayout.addWidget(self.statusLabel)
        statusLayout.addWidget(self.statusText)
        statusLayout.addWidget(self.movestatusLabel)
        statusLayout.addWidget(self.movestatusText)
        statusLayout.setAlignment(Qt.AlignCenter)  # type: ignore

        # Add the ring widget and zeroLayout to the main layout
        controlLayout.addWidget(statusWidget)
        controlLayout.addWidget(ZcontrolWidget)
        controlLayout.addWidget(ringWidget)
        controlLayout.addWidget(zeroWidget)

        # Applying the layout to the main widget
        # self.centralWidget.setLayout(controlLayout)
        self.movement_control_layout.addLayout(controlLayout)

        # Connect your buttons to the respective functions
        self.moveLeftX.clicked.connect(lambda: self.stepMove("X", -1))
        self.moveLeftX.pressed.connect(lambda: self.startContinuousMove("X", -1))
        self.moveLeftX.released.connect(self.stopContinuousMove)

        self.moveRightX.clicked.connect(lambda: self.stepMove("X", 1))
        self.moveRightX.pressed.connect(lambda: self.startContinuousMove("X", 1))
        self.moveRightX.released.connect(self.stopContinuousMove)

        self.moveLeftY.clicked.connect(lambda: self.stepMove("Y", -1))
        self.moveLeftY.pressed.connect(lambda: self.startContinuousMove("Y", -1))
        self.moveLeftY.released.connect(self.stopContinuousMove)

        self.moveRightY.clicked.connect(lambda: self.stepMove("Y", 1))
        self.moveRightY.pressed.connect(lambda: self.startContinuousMove("Y", 1))
        self.moveRightY.released.connect(self.stopContinuousMove)

        self.moveLeftZ.clicked.connect(lambda: self.stepMove("Z", -1))
        self.moveLeftZ.pressed.connect(lambda: self.startContinuousMove("Z", -1))
        self.moveLeftZ.released.connect(self.stopContinuousMove)

        self.moveRightZ.clicked.connect(lambda: self.stepMove("Z", 1))
        self.moveRightZ.pressed.connect(lambda: self.startContinuousMove("Z", 1))
        self.moveRightZ.released.connect(self.stopContinuousMove)

        self.gotozeroX.clicked.connect(lambda: self.goto_zero("X"))
        self.gotoZeroY.clicked.connect(lambda: self.goto_zero("Y"))
        self.gotoZeroZ.clicked.connect(lambda: self.goto_zero("Z"))
        self.gotoOrigin.clicked.connect(self.goto_origin)
        self.setOrigin.clicked.connect(self.set_origin)

    def updateBound(self):
        self.attocube.xmin = min(int(self.inputBoundXmin.value()), self.attocube.xmax)
        self.inputBoundXmin.setValue(self.attocube.xmin)
        self.attocube.xmax = max(int(self.inputBoundXmax.value()), self.attocube.xmin)
        self.inputBoundXmax.setValue(self.attocube.xmax)
        self.attocube.ymin = min(int(self.inputBoundYmin.value()), self.attocube.ymax)
        self.inputBoundYmin.setValue(self.attocube.ymin)
        self.attocube.ymax = max(int(self.inputBoundYmax.value()), self.attocube.ymin)
        self.inputBoundYmax.setValue(self.attocube.ymax)
        self.attocube.zmin = min(int(self.inputBoundZmin.value()), self.attocube.zmax)
        self.inputBoundZmin.setValue(self.attocube.zmin)
        self.attocube.zmax = max(int(self.inputBoundZmax.value()), self.attocube.zmin)
        self.inputBoundZmax.setValue(self.attocube.zmax)
        self.updatePlot()

    def lockMovement(self):
        self._locked_movement = self.lockButton.isChecked()
        if self._locked_movement:
            self.lockButton.setText("Unlock")
            self.statusText.setText("Locked")
            self.statusText.setStyleSheet("color: red")
        else:
            self.lockButton.setText("Lock")
            self.statusText.setText("Idle")
            self.statusText.setStyleSheet("color: green")

    def step_move(self):
        if self.moveAxis == "X":
            self.x += int(self.moveDirection * self.stepSize)  # type: ignore
        elif self.moveAxis == "Y":
            self.y += int(self.moveDirection * self.stepSize)  # type: ignore
        elif self.moveAxis == "Z":
            self.z += int(self.moveDirection * self.stepSize)  # type: ignore
        self.updatePosition()

    def goto_zero(self, axis: str):
        if axis == "X":
            self.x = 0  # type: ignore
        elif axis == "Y":
            self.y = 0  # type: ignore
        elif axis == "Z":
            self.z = 0  # type: ignore
        self.updatePosition()

    def goto_origin(self):
        self.x = 0  # type: ignore
        self.y = 0  # type: ignore
        self.z = 0  # type: ignore
        self.updatePosition()

    def set_origin(self):
        # change the history Accordingly
        _x, _y, _z = self.position
        for i in range(len(self.historyPosition)):
            self.historyPosition[i] = (
                self.historyPosition[i][0] - _x,
                self.historyPosition[i][1] - _y,
                self.historyPosition[i][2] - _z,
            )
        self.attocube.set_to_origin()
        self.goto_origin()

    def stepMove(self, axis: str, direction: int):
        self.moveAxis = axis
        self.moveDirection = direction
        self.stepSize = self.START_STEP_SIZE
        self.step_move()

    def startContinuousMove(self, axis: str, direction: int):
        self.moveAxis = axis
        self.moveDirection = direction
        self.movementTimer.start()
        self.stepsizeTimer.start()

    def increaseStepSize(self):
        if self.stepSize < self.MAX_STEP_SIZE:
            self.stepSize += self.STEP_INCREASE_RATE

    def stopContinuousMove(self):
        self.movementTimer.stop()
        self.stepsizeTimer.stop()
        self.stepSize = self.START_STEP_SIZE  # Reset step size to 1 when movement stops

    def updateFromText(self):
        self.x = int(self.inputCurrentX.text())  # type: ignore
        self.y = int(self.inputCurrentY.text())  # type: ignore
        self.z = int(self.inputCurrentZ.text())  # type: ignore
        self.updatePosition()

    def updatePosition(self):
        # statusText changes to "Moving", and change colar to red
        if not self._locked_movement and self.statusText.text() != "Moving":
            self.statusText.setText("Moving")
            self.statusText.setStyleSheet("color: blue")
            QApplication.processEvents()  # Force the GUI to update
        #
        success = self.attocube_move(force_move=False)
        if not success:
            self.retrive_last_position()
            self.movestatusText.setText("Fail")
            self.movestatusText.setStyleSheet("color: red")
            QApplication.processEvents()
        else:  # success
            if self.movestatusText.text() != "OK":
                self.movestatusText.setText("OK")
                self.movestatusText.setStyleSheet("color: green")
                QApplication.processEvents()
        #
        # statusText changes to "Idle", and change colar to green
        if (not self._locked_movement) and (not (self.movementTimer.isActive())):
            self.statusText.setText("Idle")
            self.statusText.setStyleSheet("color: green")
        #
        self.updatePlot()

    def attocube_move(self, force_move=False):
        success = self.attocube.move_to(self.x, self.y, self.z, force_move=force_move)  # type: ignore
        # success = self.attocube.set_target(self.x, self.y, self.z, force_move=force_move)  # type: ignore
        self.inputCurrentX.setText(str(int(self.attocube.x)))
        self.inputCurrentY.setText(str(int(self.attocube.y)))
        self.inputCurrentZ.setText(str(int(self.attocube.z)))
        return success

    def updatePlot(self):
        FIG_SIZE = 1200
        # Fetch current position from your AttocubeANC300 class and add it to history
        self.updatePlotNumber += 1  # type: ignore
        current_position = self.attocube.position
        MAX_HISTORY = 6
        while len(self.historyPosition) > MAX_HISTORY:
            self.historyPosition.pop(0)

        # Clear the current figure
        self.figure.clear()

        # Create yOz cross-section subplot
        ax1 = self.figure.add_subplot(121)
        # set wspace
        self.figure.subplots_adjust(wspace=0.5)

        ax1.set_xlabel("Y")
        ax1.set_ylabel("Z")
        if len(self.historyPosition) > 0:
            # Draw line from last point to current point
            ax1.plot(
                [self.historyPosition[-1][1], current_position[1]],
                [self.historyPosition[-1][2], current_position[2]],
                color="blue",
            )
            ax1.scatter(
                [history[1] for history in self.historyPosition],
                [history[2] for history in self.historyPosition],
                alpha=np.linspace(0.2, 0.8, len(self.historyPosition)),  # type: ignore
            )
        ax1.scatter(current_position[1], current_position[2], color="black", marker="x")  # type: ignore
        ax1.axhline(y=self.attocube.zmin, color="red", linestyle="--")  # type: ignore
        ax1.axhline(y=self.attocube.zmax, color="red", linestyle="--")
        ax1.axvline(x=self.attocube.ymin, color="red", linestyle="--")
        ax1.axvline(x=self.attocube.ymax, color="red", linestyle="--")
        ax1.set_xlim(-FIG_SIZE / 2, FIG_SIZE / 2)
        ax1.set_ylim(-FIG_SIZE / 2, FIG_SIZE / 2)

        # Create xOy cross-section subplot
        ax2 = self.figure.add_subplot(122)
        ax2.set_xlabel("X")
        ax2.set_ylabel("Y")
        if len(self.historyPosition) > 0:
            # Draw line from last point to current point
            ax2.plot(
                [self.historyPosition[-1][0], current_position[0]],
                [self.historyPosition[-1][1], current_position[1]],
                color="blue",
            )
            ax2.scatter(
                [history[0] for history in self.historyPosition],
                [history[1] for history in self.historyPosition],
                alpha=np.linspace(0.2, 0.8, len(self.historyPosition)),  # type: ignore
            )
        ax2.scatter(current_position[0], current_position[1], color="black", marker="x")  # type: ignore
        ax2.axhline(y=self.attocube.ymin, color="red", linestyle="--")
        ax2.axhline(y=self.attocube.ymax, color="red", linestyle="--")
        ax2.axvline(x=self.attocube.xmin, color="red", linestyle="--")
        ax2.axvline(x=self.attocube.xmax, color="red", linestyle="--")
        ax2.set_xlim(-FIG_SIZE / 2, FIG_SIZE / 2)
        ax2.set_ylim(-FIG_SIZE / 2, FIG_SIZE / 2)

        # Redraw the canvas
        self.canvas.draw()
        # every 5 times, add current position to history
        if self.updatePlotNumber % 5 == 0:
            self.historyPosition.append(current_position)


# Main application
def main():
    app = QApplication(sys.argv)
    ex = AttocubeControlGUI()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
