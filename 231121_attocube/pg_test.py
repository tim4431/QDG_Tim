import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PyQtGraph Example")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout
        layout = QVBoxLayout(self.central_widget)

        # Create a plot widget and add it to the layout
        self.plot_widget = pg.PlotWidget(self)
        layout.addWidget(self.plot_widget)

        # Example data
        self.x = np.arange(100)
        self.y = np.random.normal(size=100)

        # Plot the data
        self.plot_widget.plot(self.x, self.y)

    def updatePlot(self, new_data):
        # Update the plot with new data
        self.plot_widget.clear()  # Clear the old plot
        self.plot_widget.plot(new_data)  # Plot the new data


# Running the application
def main():
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
