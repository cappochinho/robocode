import collections
import sys

import pyqtgraph as pg
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer
# from PyQt5
from PyQt5.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QPushButton, QVBoxLayout, QWidget)

app = QApplication(sys.argv)


class App(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.acc_x = collections.deque(maxlen=10000)
        self.acc_y = collections.deque(maxlen=10000)
        self.acc_z = collections.deque(maxlen=10000)
        self.gyr_x = collections.deque(maxlen=10000)
        self.gyr_y = collections.deque(maxlen=10000)
        self.gyr_z = collections.deque(maxlen=10000)
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

        self.graphwidget = pg.PlotWidget()
        self.graphwidget.getPlotItem().setLabel("bottom", "Time", units="s")
        self.graphwidget.getPlotItem().setLabel("left", "Acceleration", units="m/s²")
        hboxlayout.addWidget(self.graphwidget)

        self.plot_data = QComboBox(self)
        self.plot_data.addItem("Acceleration")
        self.plot_data.addItem("Angular Rates")
        self.plot_data.currentTextChanged.connect(self.plot_data_changed)
        vboxlayout.addWidget(self.plot_data)

        self.plot_button = QPushButton("Start Plot")
        self.plot_button.clicked.connect(self.plot_clicked)
        vboxlayout.addWidget(self.plot_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        vboxlayout.addWidget(self.stop_button)

        vboxlayout.addStretch(1)
        self.setLayout(hboxlayout)
        self.setWindowTitle("Arduino Realtime Plotter")

        # QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        # self.timer.start(1)

    def list_comports(self):
        self.ports = serial.tools.list_ports.comports()
        for port in self.ports:
            self.comport_combobox.addItem(port.description)

    def plot_data_changed(self):
        currentText = self.plot_data.currentText()
        if currentText.lower() == "Angular Rates".lower():
            self.graphwidget.getPlotItem().setLabel("left", "Angular Rates", units="rad/s")
        elif currentText.lower() == "acceleration".lower():
            # self.graphwidget.setLabel("bottom", "Time", units="s")
            self.graphwidget.getPlotItem().setLabel("left", "Acceleration", units="m/s²")

    def comport_changed(self):
        ports = list(filter(lambda port: port.description ==
                            self.comport_combobox.currentText(), self.ports))
        if len(ports) == 0:
            self.port = None
        else:
            self.port = ports[0]

    def plot_clicked(self):
        if self.port != None:
            self.arduino_serial = serial.Serial()
            self.arduino_serial.baudrate = 9600
            self.arduino_serial.port = self.port.device
            self.arduino_serial.open()
            self.timer.start()

    def stop(self):
        self.timer.stop()

    def update(self):
        if self.arduino_serial.in_waiting:
            
            acc, gyr = self.getdata()
            self.acc_x.append(acc[0])
            self.acc_y.append(acc[1])
            self.acc_z.append(acc[2])
            self.gyr_x.append(gyr[0])
            self.gyr_y.append(gyr[1])
            self.gyr_z.append(acc[2])

            # self.y[:] = self.acc_x
            self.graphwidget.getPlotItem.setData(self.x, [self.acc_x])
            self.app.processEvents()

    def getdata(self):
        packet = self.arduino_serial.readline()
        val = packet.decode('utf-8')
        val = val.split(',')
        val = [float(val.strip()) for val in val]
        acc = val[0:3]
        gyr = val[3:]
        return acc, gyr


if __name__ == "__main__":
    window = App()
    window.show()
    sys.exit(app.exec())
