from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QHBoxLayout,
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
        self.attocube = AttocubeANC300()
        self.x = self.attocube.x  # type: ignore
        self.y = self.attocube.y  # type: ignore
        self.z = self.attocube.z  # type: ignore

        self.movementTimer = QTimer(self)
        self.movementTimer.setInterval(100)
        self.movementTimer.timeout.connect(self.perform_step_move)

        self.moveAxis = None
        self.moveDirection = None
        self.START_STEP_SIZE = 1
        self.stepSize = self.START_STEP_SIZE
        self.STEP_INCREASE_RATE = 0.2
        self.MAX_STEP_SIZE = 10

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
        addTitle("Frequency and voltage controls")
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

    def initFreqVoltageControls(self):
        # Create a grid layout
        gridLayout = QGridLayout()

        # Example for X axis
        self.labelFreqX = QLabel("X-axis Frequency (Hz):")
        self.inputFreqX = QLineEdit(self)
        self.inputFreqX.setText(str(self.attocube.freq_x))
        self.inputFreqX.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelFreqX, 0, 0)
        gridLayout.addWidget(self.inputFreqX, 0, 1)

        # Y
        self.labelFreqY = QLabel("Y-axis Frequency (Hz):")
        self.inputFreqY = QLineEdit(self)
        self.inputFreqY.setText(str(self.attocube.freq_y))
        self.inputFreqY.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelFreqY, 0, 2)
        gridLayout.addWidget(self.inputFreqY, 0, 3)

        # Z
        self.labelFreqZ = QLabel("Z-axis Frequency (Hz):")
        self.inputFreqZ = QLineEdit(self)
        self.inputFreqZ.setText(str(self.attocube.freq_z))
        self.inputFreqZ.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelFreqZ, 0, 4)
        gridLayout.addWidget(self.inputFreqZ, 0, 5)

        # Add similar widgets for voltage
        # X
        self.labelVoltageX = QLabel("X-axis Voltage (V):")
        self.inputVoltageX = QLineEdit(self)
        self.inputVoltageX.setText(str(self.attocube.volt_x))
        self.inputVoltageX.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelVoltageX, 1, 0)
        gridLayout.addWidget(self.inputVoltageX, 1, 1)

        # Y
        self.labelVoltageY = QLabel("Y-axis Voltage (V):")
        self.inputVoltageY = QLineEdit(self)
        self.inputVoltageY.setText(str(self.attocube.volt_y))
        self.inputVoltageY.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelVoltageY, 1, 2)
        gridLayout.addWidget(self.inputVoltageY, 1, 3)

        # Z
        self.labelVoltageZ = QLabel("Z-axis Voltage (V):")
        self.inputVoltageZ = QLineEdit(self)
        self.inputVoltageZ.setText(str(self.attocube.volt_z))
        self.inputVoltageZ.editingFinished.connect(self.updateFreqVoltageControls)
        gridLayout.addWidget(self.labelVoltageZ, 1, 4)
        gridLayout.addWidget(self.inputVoltageZ, 1, 5)

        # Set the layout for the frequency and voltage controls
        self.freq_voltage_layout.addLayout(gridLayout)

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
        gridLayout = QGridLayout()
        # ----------X axis control----------
        gridXLayout = QHBoxLayout()
        self.labelCurrentX = QLabel("Current X: ")
        self.inputCurentX = QLineEdit(self)
        self.inputCurentX.setText(str(self.attocube.x))
        self.inputCurentX.editingFinished.connect(self.updateFromText)
        # set to zero button
        self.setzeroX = QPushButton("X = 0")
        self.setzeroX.clicked.connect(lambda: self.set_zero("X"))
        gridXLayout.addWidget(self.labelCurrentX)
        gridXLayout.addWidget(self.setzeroX)
        #
        gridLayout.addLayout(gridXLayout, 0, 0)
        gridLayout.addWidget(self.inputCurentX, 1, 0)
        # X axis button
        self.moveLeftX = QPushButton("<- X")
        self.moveRightX = QPushButton("X ->")
        gridLayout.addWidget(self.moveLeftX, 0, 1)
        gridLayout.addWidget(self.moveRightX, 1, 1)
        # Connect these buttons to your movement control functions
        # if holding down the button, move continuously
        # if clicked, move by 1 step
        self.moveLeftX.clicked.connect(lambda: self.stepMove("X", -1))
        self.moveLeftX.pressed.connect(lambda: self.startContinuousMove("X", -1))
        self.moveLeftX.released.connect(self.stopContinuousMove)
        self.moveRightX.clicked.connect(lambda: self.stepMove("X", 1))
        self.moveRightX.pressed.connect(lambda: self.startContinuousMove("X", 1))
        self.moveRightX.released.connect(self.stopContinuousMove)
        #
        # ----------Y axis control----------
        gridYLayout = QHBoxLayout()
        self.labelCurrentY = QLabel("Current Y: ")
        self.inputCurentY = QLineEdit(self)
        self.inputCurentY.setText(str(self.attocube.y))
        self.inputCurentY.editingFinished.connect(self.updateFromText)
        # set to zero button
        self.setzeroY = QPushButton("Y = 0")
        self.setzeroY.clicked.connect(lambda: self.set_zero("Y"))
        gridYLayout.addWidget(self.labelCurrentY)
        gridYLayout.addWidget(self.setzeroY)
        #
        gridLayout.addLayout(gridYLayout, 0, 3)
        gridLayout.addWidget(self.inputCurentY, 1, 3)
        # Y axis button
        self.moveLeftY = QPushButton("vv Y")
        self.moveRightY = QPushButton("Y ^^")
        gridLayout.addWidget(self.moveLeftY, 0, 4)
        gridLayout.addWidget(self.moveRightY, 1, 4)
        # Connect these buttons to your movement control functions
        # if holding down the button, move continuously
        # if clicked, move by 1 step
        self.moveLeftY.clicked.connect(lambda: self.stepMove("Y", -1))
        self.moveLeftY.pressed.connect(lambda: self.startContinuousMove("Y", -1))
        self.moveLeftY.released.connect(self.stopContinuousMove)
        self.moveRightY.clicked.connect(lambda: self.stepMove("Y", 1))
        self.moveRightY.pressed.connect(lambda: self.startContinuousMove("Y", 1))
        self.moveRightY.released.connect(self.stopContinuousMove)

        # ----------Z axis control----------
        gridZLayout = QHBoxLayout()
        self.labelCurrentZ = QLabel("Current Z: ")
        self.inputCurentZ = QLineEdit(self)
        self.inputCurentZ.setText(str(self.attocube.z))
        self.inputCurentZ.editingFinished.connect(self.updateFromText)
        # set to zero button
        self.setzeroZ = QPushButton("Z = 0")
        self.setzeroZ.clicked.connect(lambda: self.set_zero("Z"))
        gridZLayout.addWidget(self.labelCurrentZ)
        gridZLayout.addWidget(self.setzeroZ)
        #
        gridLayout.addLayout(gridZLayout, 0, 5)
        gridLayout.addWidget(self.inputCurentZ, 1, 5)
        # Z axis button
        self.moveLeftZ = QPushButton("vv Z")
        self.moveRightZ = QPushButton("Z ^^")
        gridLayout.addWidget(self.moveLeftZ, 0, 6)
        gridLayout.addWidget(self.moveRightZ, 1, 6)
        # Connect these buttons to your movement control functions
        # if holding down the button, move continuously
        # if clicked, move by 1 step
        self.moveLeftZ.clicked.connect(lambda: self.stepMove("Z", -1))
        self.moveLeftZ.pressed.connect(lambda: self.startContinuousMove("Z", -1))
        self.moveLeftZ.released.connect(self.stopContinuousMove)
        self.moveRightZ.clicked.connect(lambda: self.stepMove("Z", 1))
        self.moveRightZ.pressed.connect(lambda: self.startContinuousMove("Z", 1))
        self.moveRightZ.released.connect(self.stopContinuousMove)
        #
        # Finnaly, add a status light to indicate if the movement is in progress
        self.statusLabel = QLabel("Status: ")
        self.statusText = QLabel("Idle")
        self.statusText.setAlignment(Qt.AlignCenter)  # type: ignore
        self.statusText.setStyleSheet("color: green")

        gridLayout.addWidget(self.statusLabel, 0, 7)
        gridLayout.addWidget(self.statusText, 1, 7)
        # Set the column stretch for the button column
        # gridLayout.setColumnStretch(1, 2)
        # gridLayout.setColumnStretch(4, 2)
        # gridLayout.setColumnStretch(6, 2)

        self.movement_control_layout.addLayout(gridLayout)

    def perform_step_move(self):
        if self.moveAxis == "X":
            self.x += int(self.moveDirection * self.stepSize)  # type: ignore
        elif self.moveAxis == "Y":
            self.y += int(self.moveDirection * self.stepSize)  # type: ignore
        elif self.moveAxis == "Z":
            self.z += int(self.moveDirection * self.stepSize)  # type: ignore
        self.updatePosition()

    def set_zero(self, axis: str):
        if axis == "X":
            self.x = 0  # type: ignore
        elif axis == "Y":
            self.y = 0  # type: ignore
        elif axis == "Z":
            self.z = 0  # type: ignore
        self.updatePosition()

    def stepMove(self, axis: str, direction: int):
        self.moveAxis = axis
        self.moveDirection = direction
        self.stepSize = self.START_STEP_SIZE
        self.perform_step_move()

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
        self.x = int(self.inputCurentX.text())  # type: ignore
        self.y = int(self.inputCurentY.text())  # type: ignore
        self.z = int(self.inputCurentZ.text())  # type: ignore
        self.updatePosition()

    def updatePosition(self):
        # statusText changes to "Moving", and change colar to red
        if self.statusText.text() != "Moving":
            self.statusText.setText("Moving")
            self.statusText.setStyleSheet("color: red")
            QApplication.processEvents()  # Force the GUI to update
        #
        self.attocube.move_to(self.x, self.y, self.z)  # type: ignore
        self.inputCurentX.setText(str(int(self.attocube.x)))
        self.inputCurentY.setText(str(int(self.attocube.y)))
        self.inputCurentZ.setText(str(int(self.attocube.z)))
        #
        # statusText changes to "Idle", and change colar to green
        if not (self.movementTimer.isActive()):
            self.statusText.setText("Idle")
            self.statusText.setStyleSheet("color: green")
        #
        self.updatePlot()

    def updatePlot(self):
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
        ax1.scatter(current_position[1], current_position[2], color="black", marker="x")  # type: ignore
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
                alpha=np.linspace(0.2, 1, len(self.historyPosition)),  # type: ignore
            )
        ax1.set_xlim(-100, 100)
        ax1.set_ylim(-100, 100)

        # Create xOy cross-section subplot
        ax2 = self.figure.add_subplot(122)
        ax2.set_xlabel("X")
        ax2.set_ylabel("Y")
        ax2.scatter(current_position[0], current_position[1], color="black", marker="x")  # type: ignore
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
                alpha=np.linspace(0.2, 1, len(self.historyPosition)),  # type: ignore
            )
        ax2.set_xlim(-100, 100)
        ax2.set_ylim(-100, 100)

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
