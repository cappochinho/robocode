import sys

from PyQt5.QtCore import QRect, QSize
# from PyQt5
from PyQt5.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget)
import pyqtgraph as pg
import serial.tools.list_ports


class App(QWidget):
    def __init__(self) -> None:
        super().__init__()
        hboxlayout = QHBoxLayout()
        vboxlayout = QVBoxLayout()
        hboxlayout.addLayout(vboxlayout)

        vboxlayout.addWidget(QLabel("Select COM port"))
        self.comport_combobox = QComboBox(self)
        self.comport_combobox.setFixedSize(200, 20)
        self.comport_combobox.currentTextChanged.connect(self.comport_changed)
        vboxlayout.addWidget(self.comport_combobox)

        vboxlayout.addWidget(QLabel("Select data to plot"))

        self.graphwidget = pg.PlotWidget()
        hboxlayout.addWidget(self.graphwidget)

        self.plot_data = QComboBox(self)
        self.plot_data.addItem("Accelerometer X")
        self.plot_data.addItem("Accelerometer Y")
        self.plot_data.addItem("Accelerometer Z")
        self.plot_data.addItem("Gyroscope X")
        self.plot_data.addItem("Gyroscope Y")
        self.plot_data.addItem("Gyroscope Z")
        self.plot_data.currentTextChanged.connect(self.plot_data_changed)
        vboxlayout.addWidget(self.plot_data)

        self.connect_button = QPushButton("Plot")
        self.connect_button.clicked.connect(self.button_clicked)
        vboxlayout.addWidget(self.connect_button)

        vboxlayout.addStretch(1)
        self.setLayout(hboxlayout)
        self.list_comports()

    def list_comports(self):
        self.ports = serial.tools.list_ports.comports()
        for port in self.ports:
            self.comport_combobox.addItem(port.description)
    
    def plot_data_changed(self):
        print(self.plot_data.currentText())

    def comport_changed(self):
        ports = list(filter(lambda port: port.description == self.comport_combobox.currentText(), self.ports))
        print(ports[0].name)

    def button_clicked(self):
        print("Button clicked")

    def update(self):
        ...


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
