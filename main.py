from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

# from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
# import pandas as pd

import sys  # We need sys so that we can pass argv to QApplication
import random
# import os

NAMES = ["Velocity", "RPM", "Oil Temperature", "Battery Voltage",
         "Battery Temperature", "Mileage", "Something else"]
VALUES = {
    "Velocity": random.randint(0, 250),
    "RPM": random.randint(0, 8000),
    "Oil Temperature": random.randint(0, 120),
    "Battery Voltage": random.randint(10, 50),
    "Battery Temperature": random.randint(0, 80),
    "Mileage": random.randint(0, 5000),
    "Something else": random.randint(0, 12)
}
UNITS = {
    "Velocity": "km/h",
    "RPM": "rev/min",
    "Oil Temperature": "°C",
    "Battery Voltage": "V",
    "Battery Temperature": "°C",
    "Mileage": "km",
    "Something else": "lol/s"
}
# Some static data
hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]


# Main window af the application
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Main fields initialization
        self.grid = QGridLayout()
        self.gridOfLabels = QGridLayout()
        self.graphWidget = pg.PlotWidget()
        self.mainFrame = QFrame()
        self.labelFrame = QFrame()
        self.pen = pg.mkPen(color=(255, 255, 255))  # Plot color
        self.line = 0
        self.lastButtonClicked = 0
        self.valueLabelContainer = []
        self.valueButtonContainer = []
        # Run GUI
        self.initializeUI()

    def initializeUI(self):
        # MainWindow's Layout = grid
        self.setCentralWidget(self.mainFrame)
        self.mainFrame.setLayout(self.grid)
        # Call functions constructing corresponding parts of GUI
        self.makeLabels()
        self.makeGraphs()
        # Overall window settings and shenanigans
        self.setWindowState(Qt.WindowMaximized)  # start with the window maximized
        self.move(300, 150)  # spawn the window offset from the Display's top left corner
        self.setWindowIcon(QIcon("TelemetryIcon.png"))
        self.setWindowTitle("Telemetry")
        self.show()

    # Builds a label grid
    def makeLabels(self):
        # Add to mainWindow's grid
        self.grid.addWidget(self.labelFrame, 0, 0)
        self.labelFrame.setLayout(self.gridOfLabels)

        # First row is static - Annotates columns
        self.gridOfLabels.addWidget(QLabel(text="Name"), 0, 1)
        self.gridOfLabels.addWidget(QLabel(text="Value"), 0, 2)
        self.gridOfLabels.addWidget(QLabel(text="Unit"), 0, 3)
        # Create labels
        for i in range(6):
            for index, name in enumerate(NAMES):
                row = index + i * len(NAMES) + 1
                # PLOT BUTTONS
                plotButton = QPushButton(text=f"{row}")  # Create
                plotButton.setFixedWidth(20)  # Buttons smaller
                self.gridOfLabels.addWidget(plotButton, row, 0, alignment=Qt.AlignLeft)  # Locate in grid
                self.gridOfLabels.setSpacing(1)  # Makes button text readable
                # NAMES
                nameLabel = QtWidgets.QLabel(text=f"{name}")  # Create
                nameLabel.setFont(QFont("Segoe UI", 8))  # Change font size
                self.gridOfLabels.addWidget(nameLabel, row, 1)  # Locate in grid
                # VALUES
                valueLabel = QtWidgets.QLabel(text=str(VALUES[name]))
                valueLabel.setFont(QFont("Segoe UI", 9))
                self.gridOfLabels.addWidget(valueLabel, row, 2)
                # UNITS
                metricLabel = QtWidgets.QLabel(text=UNITS[name])
                metricLabel.setFont(QFont("Segoe UI", 8))
                self.gridOfLabels.addWidget(metricLabel, row, 3)
                # Store value labels for further text manipulation
                self.valueLabelContainer.append(valueLabel)
                # Store index buttons for further callback assignment
                self.valueButtonContainer.append(plotButton)
                self.valueButtonContainer[row - 1].clicked.connect(lambda state, x=row: self.changeColor(x))

    # Builds Plot
    def makeGraphs(self):
        # Add to mainWindow's grid
        self.grid.addWidget(self.graphWidget, 0, 1)
        # plot data: x, y values
        self.line = self.graphWidget.plot(hour, temperature)

    # Changes color of the clicked button as well as data and it's color on plot
    def changeColor(self, index):
        self.valueButtonContainer[self.lastButtonClicked].setStyleSheet("background-color: light gray")
        self.valueButtonContainer[index - 1].setStyleSheet("background-color: red")
        self.lastButtonClicked = index - 1
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.updateData()  # For now - TODO - Multiprocess it

    def updateData(self):
        gd = getData()
        self.line.setData([i for i in range(len(gd))], gd)  # line refresh with new data
        self.line.setPen(self.pen)  # line color


def getData():
    # d = {name: [VALUES[name], UNITS[name]] for name in NAMES}  # Cool but not needed
    d = [VALUES[name] for name in NAMES]
    d *= 6
    print(d)
    return d


def BuildUI():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


def main():
    getData()
    BuildUI()


if __name__ == '__main__':
    main()
