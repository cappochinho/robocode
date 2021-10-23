import collections
import json
import sys
import time

import pyqtgraph as pg
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QApplication, QComboBox, QErrorMessage,
                             QHBoxLayout, QLabel, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)
from serial.serialutil import SerialException

app = QApplication(sys.argv)


class App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.acc_x = collections.deque(maxlen=1000)
        self.acc_y = collections.deque(maxlen=1000)
        self.acc_z = collections.deque(maxlen=1000)
        self.gyr_x = collections.deque(maxlen=1000)
        self.gyr_y = collections.deque(maxlen=1000)
        self.gyr_z = collections.deque(maxlen=1000)
        self.time = collections.deque(maxlen=1000)

        hboxlayout = QHBoxLayout()
        vboxlayout = QVBoxLayout()
        hboxlayout.addLayout(vboxlayout)

        vboxlayout.addWidget(QLabel("Select COM port"))
        self.comport_combobox = QComboBox(self)
        self.comport_combobox.setFixedSize(200, 20)
        self.comport_combobox.currentTextChanged.connect(self.comport_changed)
        self.list_comports()
        vboxlayout.addWidget(self.comport_combobox)

        vboxlayout.addWidget(QLabel("Select data to plot"))

        self.plotWidget = pg.PlotWidget()
        self.plotWidget.getPlotItem().setLabel("bottom", "Time", units="s")
        self.plotWidget.getPlotItem().setLabel("left", "Acceleration", units="m/s²")
        self.plotWidget.getPlotItem().setTitle(title="Realtime IMU plot from Arduino")
        self.x_curve = self.plotWidget.getPlotItem().plot(title="Just a plot")
        self.y_curve = self.plotWidget.getPlotItem().plot()
        self.z_curve = self.plotWidget.getPlotItem().plot()
        hboxlayout.addWidget(self.plotWidget)

        self.plot_data = QComboBox(self)
        self.plot_data.addItem("Acceleration")
        self.plot_data.addItem("Angular Rates")
        self.plot_data.currentTextChanged.connect(self.plot_data_changed)
        vboxlayout.addWidget(self.plot_data)
        self.plot_var = "acc"

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
            self.x_curve.clear()
            self.y_curve.clear()
            self.z_curve.clear()
            self.acc_x.clear()
            self.acc_y.clear()
            self.acc_z.clear()
            self.gyr_x.clear()
            self.gyr_y.clear()
            self.gyr_z.clear()
            self.time.clear()

            self.plot_button.setDisabled(True)
            self.stop_button.setDisabled(False)
            self.arduino_serial = serial.Serial()
            self.arduino_serial.baudrate = 9600
            self.arduino_serial.port = self.port.device
            self.start_time = time.time()

            try:
                self.arduino_serial.open()
                self.arduino_serial.flushOutput()
                time.sleep(1)
                self.arduino_serial.write(b'Y')
                self.timer.start(1)
                self.is_plotting = True
            except SerialException as e:
                self.plot_button.setDisabled(False)
                self.stop_button.setDisabled(True)
                self.launch_error(title="Port error",
                                  msg="Serial Port is already open")

    def stop(self):
        self.timer.stop()
        self.arduino_serial.write(b'N')
        self.arduino_serial.close()
        self.is_plotting = False
        self.plot_button.setDisabled(False)
        self.stop_button.setDisabled(True)

    def update(self):
        if self.arduino_serial.in_waiting:
            data = self.getdata()
            if "err" in data:
                # Launch error message box with error message
                self.launch_error(title="Error reading data", msg=data["err"])
                self.stop()
            else:
                self.time.append(time.time() - self.start_time)
                x_pen = pg.mkPen({'color': "#F00"})
                y_pen = pg.mkPen({'color': "#0F0"})
                z_pen = pg.mkPen({'color': "#00F"})

                if self.plot_var == "acc":
                    self.acc_x.append(data["acc_x"])
                    self.acc_y.append(data["acc_y"])
                    self.acc_z.append(data["acc_z"])

                    self.x_curve.setData(
                        self.time, self.acc_x, name="Acceleration X", pen=x_pen)
                    self.y_curve.setData(
                        self.time, self.acc_y, name="Acceleration Y", pen=y_pen)
                    self.z_curve.setData(
                        self.time, self.acc_z, name="Acceleration Z", pen=z_pen)
                elif self.plot_var == "ang":
                    self.gyr_x.append(data["gyr_x"])
                    self.gyr_y.append(data["gyr_y"])
                    self.gyr_z.append(data["gyr_z"])
                    self.x_curve.setData(
                        self.time, self.gyr_x, name="Angular Rate X", pen=x_pen)
                    self.y_curve.setData(
                        self.time, self.gyr_y, name="Angular Rate Y", pen=y_pen)
                    self.z_curve.setData(
                        self.time, self.gyr_z, name="Angular Rate Z", pen=z_pen)
        app.processEvents()

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
