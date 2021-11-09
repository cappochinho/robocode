import collections
import json
import sys
import time
from numpy.lib.type_check import real

import serial
import serial.tools.list_ports
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (QApplication, QComboBox, QErrorMessage,
                             QHBoxLayout, QLabel, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)
from serial.serialutil import SerialException
import pyqtgraph as pg
import numpy as np

app = QApplication(sys.argv)


class App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.data = collections.deque(maxlen=100000)

        hboxlayout = QHBoxLayout()
        vboxlayout = QVBoxLayout()
        hboxlayout.addLayout(vboxlayout)

        vboxlayout.addWidget(QLabel("Select COM port"))
        self.comport_combobox = QComboBox(self)
        self.comport_combobox.setFixedSize(200, 20)
        self.comport_combobox.currentTextChanged.connect(self.comport_changed)
        self.port = None
        self.list_comports()
        vboxlayout.addWidget(self.comport_combobox)

        vboxlayout.addWidget(QLabel("Select data to plot"))

        self.plotWidget = pg.PlotWidget()
        self.plotWidget.getPlotItem().setLabel("bottom", "Time", units="s")
        self.plotWidget.getPlotItem().setLabel("left", "Acceleration", units="m/s²")
        self.plotWidget.getPlotItem().setTitle(title="Realtime IMU plot from Arduino")
        self.curve = self.plotWidget.getPlotItem().plot(title="Just a plot", stepMode=True)
        self.real_curve = self.plotWidget.getPlotItem().plot(title="Just a plot")
        hboxlayout.addWidget(self.plotWidget)

        self.plot_data = QComboBox(self)
        self.plot_data.addItem("Acceleration")
        self.plot_data.addItem("Angular Rates")
        self.plot_data.currentTextChanged.connect(self.plot_data_changed)
        vboxlayout.addWidget(self.plot_data)
        self.plot_var = "acc"

        vboxlayout.addWidget(QLabel("Axis to plot"))
        self.graph_to_plot = QComboBox(self)  # type of graph to be plotted
        self.graph_to_plot.setFixedSize(200, 20)
        self.graph_to_plot.addItem("X")
        self.graph_to_plot.addItem("Y")
        self.graph_to_plot.addItem("Z")
        vboxlayout.addWidget(self.graph_to_plot)

        self.plot_button = QPushButton("Start Plot")
        self.plot_button.clicked.connect(self.plot_clicked)
        vboxlayout.addWidget(self.plot_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setDisabled(True)
        vboxlayout.addWidget(self.stop_button)

        vboxlayout.addStretch(1)
        self.setWindowTitle("Arduino Realtime Plotter")

        # QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.is_plotting = False
        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(hboxlayout)

    def list_comports(self):
        self.ports = serial.tools.list_ports.comports()
        for port in self.ports:
            self.comport_combobox.addItem(port.description)

    def plot_data_changed(self):
        currentText = self.plot_data.currentText()
        if not self.is_plotting:
            if currentText.lower() == "Angular Rates".lower():
                self.plotWidget.getPlotItem().setLabel("left", "Angular Rates", units="rad/s")
                self.plot_var = "ang"
            elif currentText.lower() == "acceleration".lower():
                self.plotWidget.getPlotItem().setLabel("left", "Acceleration", units="m/s²")
                self.plot_var = "acc"

    def comport_changed(self):
        ports = list(filter(lambda port: port.description ==
                            self.comport_combobox.currentText(), self.ports))
        if len(ports) == 0:
            self.port = None
        else:
            self.port = ports[0]

    def plot_clicked(self):
        if self.port != None:
            self.line_plot()

    def line_plot(self):
        self.curve.clear()

        self.plot_button.setDisabled(True)
        self.stop_button.setDisabled(False)
        # self.arduino_serial = serial.Serial()
        # self.arduino_serial.baudrate = 9600
        # self.arduino_serial.port = self.port.device
        self.start_time = time.time()

        try:
            # self.arduino_serial.open()
            # self.arduino_serial.flushOutput()
            # time.sleep(1)
            # self.arduino_serial.write(b'Y')
            self.timer.start(1)
            self.is_plotting = True
        except SerialException as e:
            self.plot_button.setDisabled(False)
            self.stop_button.setDisabled(True)
            self.launch_error(title="Port error",
                              msg="Serial Port is already open")

    def stop(self):
        self.timer.stop()
        # self.arduino_serial.write(b'N')
        # self.arduino_serial.close()
        self.is_plotting = False
        self.plot_button.setDisabled(False)
        self.stop_button.setDisabled(True)

    def update(self):
        # if self.arduino_serial.in_waiting:
        # data = self.getdata()
        data = {"acc_x": np.random.normal(0, 10)}
        if "err" in data:
            # Launch error message box with error message
            self.launch_error(title="Error reading data", msg=data["err"])
            self.stop()
        else:
            x_pen = pg.mkPen({'color': "#F00"})
            y_pen = pg.mkPen({'color': "#0F0"})
            
            if self.plot_var == "acc":
                axis = self.graph_to_plot.currentText()
                if axis == "X":
                    self.data.append(data["acc_x"])
                if axis == "Y":
                    self.data.append(data["acc_y"])
                if axis == "Z":
                    self.data.append(data["acc_z"])
                
                y, x = np.histogram(self.data, bins=100)
                mu = np.average(self.data)
                sigma_square = np.var(self.data)
                real_x = np.arange(min(x), max(x), 0.01)
                max_y = max(y)
                real_y = [self.gaussian(i, mu, sigma_square) for i in real_x]
                real_y = np.array(real_y)*max_y/max(real_y)
                print(f"Mean: {mu}")
                print(f"Variance: {sigma_square}")
                print(len(self.data))
                self.curve.setData(
                    x, y, name="Acceleration X", pen=x_pen)
                self.real_curve.setData(
                    real_x, real_y, name="Acceleration X", pen=y_pen)
            elif self.plot_var == "ang":
                axis = self.graph_to_plot.currentText()
                if axis == "X":
                    self.data.append(data["gyr_x"])
                if axis == "Y":
                    self.data.append(data["gyr_y"])
                if axis == "Z":
                    self.data.append(data["gyr_z"])
                
                y, x = np.histogram(self.data, bins=10)
                self.curve.setData(
                    x, y, name="Angular Rate X", pen=x_pen)
        app.processEvents()

    def gaussian(self, x, mu, sigma_square):
        return (1/np.sqrt(2*np.pi*sigma_square))*np.exp(-(x-mu)**2/(2*sigma_square))

    def getdata(self):
        packet = self.arduino_serial.readline()
        val = packet.decode('utf-8')
        try:
            val: 'dict[str, float] | dict[str, str]' = json.loads(
                val[:val.find("}")+1])
            return val
        except json.JSONDecodeError as e:
            return {"err": "Could not decode the JSON message"}

    def launch_error(self, title: str, msg: str):
        error_message = QErrorMessage()
        error_message.setWindowTitle(title)
        error_message.showMessage(msg)
        error_message.exec_()


if __name__ == "__main__":
    window = App()
    window.show()
    sys.exit(app.exec())
