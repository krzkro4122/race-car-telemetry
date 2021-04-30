from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import (Qt, QTimer)

import pyqtgraph as pg
import pandas as pd
import sys  # We need sys so that we can pass argv to QApplication
import random

import tcp_sock
import threading

# Data Dict
# Format = {key: [values], ...}
DATA_NAMES = [line for line in open("Dane.txt")]
DATA = {line[0:len(line) - 1]: [-1 for i in range(100)] for line in DATA_NAMES}


# Main window af the application
class MainWindow(QtWidgets.QMainWindow):
    line: pg.plot

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Main fields initialization
        self.grid = QGridLayout()
        self.gridOfLabels = QGridLayout()
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.showGrid(x=True, y=True, alpha=0.4)
        self.mainFrame = QFrame()
        self.labelFrame = QFrame()
        self.labelScroll = QScrollArea()
        self.pen = pg.mkPen(color=(255, 255, 255))  # Plot color
        self.lastButtonClicked = 0  # Last clicked button's index (so it can be uncolored)
        self.currentDataKey = list(DATA.keys())[0]
        self.valueLabelContainer = []
        self.valueButtonContainer = []
        self.df = pd.DataFrame(data=DATA)
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
        # self.setWindowState(Qt.WindowMaximized)  # start with the window maximized
        self.move(300, 150)  # spawn the window offset from the Display's top left corner
        self.setWindowIcon(QIcon("TelemetryIcon.png"))
        self.setWindowTitle("Telemetry")
        self.show()

    # Builds a label grid
    def makeLabels(self):
        # Add to mainWindow's grid
        self.grid.addWidget(self.labelScroll, 0, 0)
        self.labelFrame.setLayout(self.gridOfLabels)
        # Scroll area's settings
        self.labelScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.labelScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.labelScroll.setWidgetResizable(True)
        self.labelScroll.setMaximumWidth(500)
        self.labelScroll.setMinimumWidth(500)
        self.labelScroll.setWidget(self.labelFrame)
        # First row is static - Annotates columns
        uselessButtons = QPushButton(text=f"#")
        uselessButtons.setFixedWidth(20)
        self.gridOfLabels.addWidget(uselessButtons, 0, 0)  # Create
        self.gridOfLabels.addWidget(QLabel(text="Name"), 0, 1)
        self.gridOfLabels.addWidget(QLabel(text="Value"), 0, 2, alignment=Qt.AlignCenter)
        self.gridOfLabels.addWidget(QLabel(text="Unit"), 0, 3, alignment=Qt.AlignCenter)
        # Create labels
        names = list(DATA.keys())
        for index, name in enumerate(names):
            row = index + 1
            # PLOT BUTTONS
            plotButton = QPushButton(text=f"{row}")  # Create
            plotButton.setFixedWidth(20)  # Buttons smaller
            self.gridOfLabels.addWidget(plotButton, row, 0, 1, 6, alignment=Qt.AlignLeft)  # Locate in grid
            self.gridOfLabels.setSpacing(1)  # Makes button text readable
            # NAMES
            nameLabel = QtWidgets.QLabel(text=f"{name}")  # Create
            nameLabel.setFont(QFont("Segoe UI", 8))  # Change font size
            self.gridOfLabels.addWidget(nameLabel, row, 1, alignment=Qt.AlignLeft)  # Locate in grid
            # VALUES
            valueLabel = QtWidgets.QLabel(text=str(list(DATA.values())[index][-1]))
            valueLabel.setFont(QFont("Segoe UI", 10))
            valueLabel.setStyleSheet("border: 1px solid black;")
            valueLabel.setFixedWidth(100)
            valueLabel.setAlignment(Qt.AlignRight)
            self.gridOfLabels.addWidget(valueLabel, row, 2)
            # UNITS
            metricLabel = QtWidgets.QLabel(text="meters idk")
            metricLabel.setFont(QFont("Segoe UI", 8))
            self.gridOfLabels.addWidget(metricLabel, row, 3, alignment=Qt.AlignCenter)
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
        df = self.df
        self.line = self.graphWidget.plot(df.index, df.get(self.currentDataKey))
        self.changeColor(12)  # start with button 12 active (Motor RPM)

    # Changes color of the clicked button as well as data and it's color on plot
    def changeColor(self, index):
        self.valueButtonContainer[self.lastButtonClicked].setStyleSheet("background-color: light gray")
        self.valueButtonContainer[index - 1].setStyleSheet("background-color: red")
        self.lastButtonClicked = index - 1
        self.currentDataKey = list(DATA.keys())[index - 1]
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.updateData()

    def updateData(self):
        df = self.df
        dataChannel = df.get(self.currentDataKey)
        self.line.setData(df.index, dataChannel)  # line refresh with new data
        for index, column in enumerate(df.columns):
            self.valueLabelContainer[index].setText(f"{list(df[column])[len(df.index) - 1]}")

    def getData(self):
        # Drop oldest data row
        self.df.drop(index=0, inplace=True)
        self.df.reset_index(drop=True)
        # Append a new, youngest row. We get data from DATA.py which is modified continuously by tcp_sock.reading()
        newRow = [(int(tcp_sock.CAN[tcp_sock.SketchyDNS[i]].get()[2:], 16)) for i in self.df.columns]
        a_series = pd.Series(newRow, index=self.df.columns)
        self.df = self.df.append(a_series, ignore_index=True)


def BuildUI():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()

    # Interval in ms
    refreshInterval = 0
    # "Thread" executing data cycling
    timerCycle = QTimer()
    timerCycle.timeout.connect(mainWindow.getData)
    timerCycle.start(refreshInterval)
    # "Thread" executing plot update
    timerPlot = QTimer()
    timerPlot.timeout.connect(mainWindow.updateData)
    timerPlot.start(refreshInterval)
    # "Thread" implementing a socket
    timerSocket = threading.Thread(target=tcp_sock.reading)
    timerSocket.daemon = True  # This makes the tcp_sock close upon app exit
    timerSocket.start()

    sys.exit(app.exec_())


def main():
    BuildUI()


if __name__ == '__main__':
    main()
