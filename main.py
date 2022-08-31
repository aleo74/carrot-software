from PyQt5 import QtCore, QtGui, QtWidgets, uic, QtSerialPort
from PyQt5.QtCore import QIODevice, QTimer, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
from random import randint

from graphs.graph_temperature import graph_temperature
from graphs.graph_gyro import graph_gyro
from graphs.graph_acceleration import graph_acceleration
from graphs.graph_speed import graph_speed
from graphs.graph_altitude import graph_altitude
from map.map import Map
import serial
import json
import time

class MainWindow(QtWidgets.QMainWindow):
    connected = False
    ser = serial.Serial()
    serialPort = False
    serialBaud = False
    dummyPlug = False
    saving = False
    _now = 0
    _sleep_time = 0

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('mainwindow.ui', self)

        # Serial
        for info in QtSerialPort.QSerialPortInfo.availablePorts():
            self.comboBox_serialPort.addItem(info.portName())

        for baudrate in QtSerialPort.QSerialPortInfo.standardBaudRates():
            self.comboBox_baudRate.addItem(str(baudrate), baudrate)

        self.pushButton_stop_save.setEnabled(False)
        self.label_saving_state.setText("Not recording")

        # instance
        self.pushButton_connect.clicked.connect(self.button_connect_serial)
        self.pushButton_start_save.clicked.connect(self.saving_data)
        self.pushButton_stop_save.clicked.connect(self.saving_data)
        self.temperature = graph_temperature(self.graphWidget_temp)
        self.gyro = graph_gyro(self.graphWidget_gyro)
        self.acc = graph_acceleration(self.graphWidget_acc)
        self.speed = graph_speed(self.graphWidget_speed)
        self.alt = graph_altitude(self.graphWidget_alt)
        self.map = Map(self.widget_map)
        self.map.coordinate_changed.connect(self.map.add_marker)

        # Timer
        self.populateTimer = QTimer(self)
        self.populateTimer.setInterval(100)
        self.populateTimer.setSingleShot(False)
        self.populateTimer.timeout.connect(self.update)
        self.populateTimer.start()

    def update(self):
        if self.dummyPlug:
            self.temperature.update(randint(0, 10))
            self.gyro.update(randint(0, 10), randint(0, 10), randint(0, 10))
            self.acc.update(randint(0, 10), randint(0, 10), randint(0, 10))
            self.speed.update(randint(0, 10), randint(0, 10), randint(0, 10))
            self.alt.update(randint(0, 10))
            self.map.coordinate_changed.emit(43.0252, 1.61253)
        elif self.connected:
            try:
                value_chain = self.getData()
                self._now = time.monotonic()
                try:
                    for value in value_chain:
                        data = json.loads(value)

                        self.speed.update(data['mpu']['acc_x'], data['mpu']['acc_y'],
                                     data['mpu']['acc_z'])
                        self.acc.update(data['mpu']['acc_x'], data['mpu']['acc_y'],
                                            data['mpu']['acc_z'])
                        self.gyro.update(data['mpu']['gyro_x'], data['mpu']['gyro_y'],
                                    data['mpu']['gyro_z'])

                        self.temperature.update(round(data['mpu']['temp'], 1))
                        if 'gps' in data:
                            self.alt.update(data['GPS']['altitude_m'])
                            self.label_latitude.setText(str(data['GPS']['latitude']))
                            self.label_longitude.setText(str(data['GPS']['longitude']))
                            # add gps point every 2 sec
                            if self._now >= self._sleep_time + 2:
                                self.map.coordinate_changed.emit(data['GPS']['latitude'],
                                                                 data['GPS']['longitude'])
                                self._sleep_time = self._now
                            self.label_gps_fix.setText(str(data['GPS']['sat_fix']))
                            self.label_2d_fix.setText(str(data['GPS']['2D_fix']))
                            self.label_3d_fix.setText(str(data['GPS']['3D_fix']))
                            self.label_vdop.setText(str(data['GPS']['VDOP']))
                            self.label_pdop.setText(str(data['GPS']['PDOP']))
                            self.label_hdop.setText(str(data['GPS']['HDOP']))
                        # data_base.guardar(data)
                except ValueError as e:
                    print(value_chain)
                    print('json errone')
                    print(e)
                    pass

            except IndexError:
                print('starting, please wait a moment')


    def button_connect_serial(self):
        self.serialPort = self.comboBox_serialPort.currentText()
        self.serialBaud = self.comboBox_baudRate.currentText()

        self.label_status.setText("openning")

        # Only for debug
        # self.serialBaud = 9600
        # self.serialPort = 'COM4'
        try:
            print('Try OPEN')
            self.ser = serial.Serial(self.serialPort, self.serialBaud)
        except serial.serialutil.SerialException:
            print("Can't open : ", self.serialPort)
            self.dummyPlug = True
        self.label_status.setText("connected")
        self.connected = True


        if self.connected:
            self.comboBox_serialPort.setEnabled(False)
            self.comboBox_baudRate.setEnabled(False)
            self.pushButton_connect.setEnabled(False)

    def saving_data(self):
        self.saving = not self.saving
        self.pushButton_start_save.setEnabled(not self.saving)
        self.pushButton_stop_save.setEnabled(self.saving)
        if self.saving:
            self.label_saving_state.setText("Recording data...")
        else:
            self.label_saving_state.setText("Not recording")

    def getData(self):
        data = ''
        value_chain = ''
        if self.dummyPlug == False:
            data = self.ser.read(1)
            data += self.ser.read(self.ser.inWaiting())
            if data:
                value_chain = data.decode("utf-8").splitlines()
        return value_chain


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()