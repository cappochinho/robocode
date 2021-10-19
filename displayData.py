
import collections
import math
import random
import time

import numpy as np
import pyqtgraph as pg
import serial.tools.list_ports
from pyqtgraph.Qt import QtCore, QtGui


class DynamicPlotter():

    def __init__(self, sampleinterval=0.001, timewindow=10., size=(600, 350)):
        # Data stuff
        # self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'Acceleration', 'm/s^2')
        self.plt.setLabel('bottom', 'time', 's')
        self.curve = self.plt.plot(self.x, self.y, pen=(255, 0, 0))
        self.setupCom()
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(1)

    def setupCom(self):
        ports = serial.tools.list_ports.comports()
        self.serialInst = serial.Serial()

        portlist = []

        for onePort in ports:
            portlist.append(str(onePort))
            print(str(onePort))

        val = input("Select port: COM")

        self.serialInst.baudrate = 9600
        self.serialInst.port = "COM" + str(val)
        self.serialInst.open()

        # while True:
        #     if self.serialInst.in_waiting:
        #         packet = self.serialInst.readline()
        #         print(packet.decode('utf'))

    def getdata(self):
        if self.serialInst.in_waiting:
            packet = self.serialInst.readline()
            val = packet.decode('utf-8')
            print(val)
            return float(val.split(',')[2])

    def updateplot(self):
        self.databuffer.append(self.getdata())
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)
        self.app.processEvents()

    def run(self):
        self.app.exec_()


if __name__ == '__main__':

    m = DynamicPlotter(sampleinterval=0.05, timewindow=10.)
    m.run()
