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
        self.attocube = AttocubeANC300(commandline=False, constant_mode=True)
        self._x = self.attocube.x  # type: ignore
        self._y = self.attocube.y  # type: ignore
        self._z = self.attocube.z  # type: ignore
        self._last_x = self._x
        self._last_y = self._y
        self._last_z = self._z

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
        # # set global font
        # font = self.font()
        # font.setPointSize(12)
        # font.setFamily("Arial")
        # self.setFont(font)

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
        self.setGeometry(100, 100, 700, 650)

        def addTitle(text: str):
            label = QLabel(text)
            font = label.font()
            # font.setFamily("Consolas")
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
        addTitle("Movement controls")
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
        # network port number
        self.labelIP = QLabel("IP address:")
        self.inputIP = QLineEdit(self)
        self.inputIP.setText(str(self.attocube.address))  # type: ignore
        self.inputIP.editingFinished.connect(self.updateAddress)
        gridLayout.addWidget(self.labelIP, 0, 0)
        gridLayout.addWidget(self.inputIP, 1, 0)

        # Example for X axis
        self.labelFreqX = QLabel("X-axis Freq (Hz):")
        self.inputFreqX = QLineEdit(self)
        self.inputFreqX.setText(str(self.attocube.freq_x))
        self.inputFreqX.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelFreqX, 0, 1)
        gridLayout.addWidget(self.inputFreqX, 0, 2)

        # Y
        self.labelFreqY = QLabel("Y-axis Freq (Hz):")
        self.inputFreqY = QLineEdit(self)
        self.inputFreqY.setText(str(self.attocube.freq_y))
        self.inputFreqY.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelFreqY, 0, 3)
        gridLayout.addWidget(self.inputFreqY, 0, 4)

        # Z
        self.labelFreqZ = QLabel("Z-axis Freq (Hz):")
        self.inputFreqZ = QLineEdit(self)
        self.inputFreqZ.setText(str(self.attocube.freq_z))
        self.inputFreqZ.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelFreqZ, 0, 5)
        gridLayout.addWidget(self.inputFreqZ, 0, 6)

        # Add similar widgets for voltage
        # X
        self.labelVoltageX = QLabel("X-axis Volt (V):")
        self.inputVoltageX = QLineEdit(self)
        self.inputVoltageX.setText(str(self.attocube.volt_x))
        self.inputVoltageX.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelVoltageX, 1, 1)
        gridLayout.addWidget(self.inputVoltageX, 1, 2)

        # Y
        self.labelVoltageY = QLabel("Y-axis Volt (V):")
        self.inputVoltageY = QLineEdit(self)
        self.inputVoltageY.setText(str(self.attocube.volt_y))
        self.inputVoltageY.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelVoltageY, 1, 3)
        gridLayout.addWidget(self.inputVoltageY, 1, 4)

        # Z
        self.labelVoltageZ = QLabel("Z-axis Volt (V):")
        self.inputVoltageZ = QLineEdit(self)
        self.inputVoltageZ.setText(str(self.attocube.volt_z))
        self.inputVoltageZ.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelVoltageZ, 1, 5)
        gridLayout.addWidget(self.inputVoltageZ, 1, 6)

        # Set the layout for the frequency and voltage controls
        gridLayout.setColumnStretch(0, 3)
        gridLayout.setColumnStretch(1, 1)
        gridLayout.setColumnStretch(2, 1)
        gridLayout.setColumnStretch(3, 1)
        gridLayout.setColumnStretch(4, 1)
        gridLayout.setColumnStretch(5, 1)
        gridLayout.setColumnStretch(6, 1)
        self.freq_voltage_layout.addLayout(gridLayout)

    def updateAddress(self):
        new_address = str(self.inputIP.text())
        self.attocube.address = new_address
        self.inputIP.setText(str(self.attocube.address))

    def updateFreqVoltageControls(self):
        # X
        new_freq_x = int(self.inputFreqX.text())
        self.attocube.freq_x = new_freq_x
        self.inputFreqX.setText(str(self.attocube.freq_x))
        # Y
        new_freq_y = int(self.inputFreqY.text())
        self.attocube.freq_y = new_freq_y
        self.inputFreqY.setText(str(self.attocube.freq_y))
        # Z
        new_freq_z = int(self.inputFreqZ.text())
        self.attocube.freq_z = new_freq_z
        self.inputFreqZ.setText(str(self.attocube.freq_z))
        # X
        new_volt_x = float(self.inputVoltageX.text())
        self.attocube.volt_x = new_volt_x
        self.inputVoltageX.setText(str(self.attocube.volt_x))
        # Y
        new_volt_y = float(self.inputVoltageY.text())
        self.attocube.volt_y = new_volt_y
        self.inputVoltageY.setText(str(self.attocube.volt_y))
        # Z
        new_volt_z = float(self.inputVoltageZ.text())
        self.attocube.volt_z = new_volt_z
        self.inputVoltageZ.setText(str(self.attocube.volt_z))

    def initMovementControls(self):
        controlLayout = QHBoxLayout()
        # self.centralWidget = QWidget()
        # self.setCentralWidget(self.centralWidget)

        # Add a lock status button, if pressed the movement is locked
        lockWidget = QWidget()
        lockLayout = QVBoxLayout(lockWidget)
        lockLabel = QLabel("Movement Lock")
        self.lockButton = QPushButton("Lock")
        self.lockButton.setCheckable(True)
        self.lockButton.clicked.connect(self.lockMovement)
        lockLayout.addWidget(lockLabel)
        lockLayout.addWidget(self.lockButton)
        # vertical alignment
        lockLayout.setAlignment(Qt.AlignCenter)  # type: ignore
        controlLayout.addWidget(lockWidget)

        # Z axis buttons
        ZcontrolWidget = QWidget()
        ZcontrolLayout = QVBoxLayout(ZcontrolWidget)
        self.moveLeftZ = QPushButton("Z-- (d)")
        self.moveRightZ = QPushButton("Z++ (u)")
        ZcontrolLayout.addWidget(self.moveRightZ)
        ZcontrolLayout.addWidget(self.moveLeftZ)
        controlLayout.addWidget(ZcontrolWidget)
        # the keyboard u is for Z++
        # the keyboard d is for Z--
        self.moveLeftZ.setShortcut(Qt.Key_D)  # type: ignore
        self.moveRightZ.setShortcut(Qt.Key_U)  # type: ignore

        # Ring layout for X and Y axis control
        ringWidget = QWidget()
        ringLayout = QGridLayout(ringWidget)
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

        # Add X and Y axis buttons to the ring layout
        ringLayout.addWidget(self.moveLeftX, 1, 0)
        ringLayout.addWidget(self.moveRightX, 1, 2)
        ringLayout.addWidget(self.moveLeftY, 2, 1)
        ringLayout.addWidget(self.moveRightY, 0, 1)

        # Current X, Y, Z values display
        # self.currentXYZDisplay = QLabel("X: 0, Y: 0, Z: 0")
        # self.currentXYZDisplay.setAlignment(Qt.AlignCenter)  # type: ignore
        positionWidget = QWidget()
        positionLayout = QGridLayout(positionWidget)
        self.labelCurrentX = QLabel("X:")
        self.inputCurrentX = QLineEdit(self)
        self.inputCurrentX.setText(str(self.attocube.x))
        self.inputCurrentX.editingFinished.connect(self.updateFromText)
        self.labelCurrentY = QLabel("Y:")
        self.inputCurrentY = QLineEdit(self)
        self.inputCurrentY.setText(str(self.attocube.y))
        self.inputCurrentY.editingFinished.connect(self.updateFromText)
        self.labelCurrentZ = QLabel("Z:")
        self.inputCurrentZ = QLineEdit(self)
        self.inputCurrentZ.setText(str(self.attocube.z))
        self.inputCurrentZ.editingFinished.connect(self.updateFromText)
        positionLayout.addWidget(self.labelCurrentX, 0, 0)
        positionLayout.addWidget(self.inputCurrentX, 0, 1)
        positionLayout.addWidget(self.labelCurrentY, 1, 0)
        positionLayout.addWidget(self.inputCurrentY, 1, 1)
        positionLayout.addWidget(self.labelCurrentZ, 2, 0)
        positionLayout.addWidget(self.inputCurrentZ, 2, 1)
        ringLayout.addWidget(positionWidget, 1, 1)
        ringLayout.setColumnStretch(1, 1)
        ringLayout.setColumnStretch(0, 1)
        ringLayout.setColumnStretch(2, 1)

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
        statusLayout.addWidget(self.statusLabel)
        statusLayout.addWidget(self.statusText)
        statusLayout.addWidget(self.movestatusLabel)
        statusLayout.addWidget(self.movestatusText)

        # Add the ring widget and zeroLayout to the main layout
        controlLayout.addWidget(ZcontrolWidget)
        controlLayout.addWidget(ringWidget)
        controlLayout.addWidget(zeroWidget)
        controlLayout.addWidget(statusWidget)

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
        FIG_SIZE = 1000
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
