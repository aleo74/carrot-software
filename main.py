from PyQt5 import QtGui, QtWidgets, uic, QtSerialPort
from PyQt5.QtCore import QTimer

from pyqtgraph.opengl import GLMeshItem, GLLinePlotItem, MeshData
from pyqtgraph import Transform3D
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

import numpy as np
from filterpy.kalman import KalmanFilter
from stl import mesh

class MainWindow(QtWidgets.QMainWindow):
    connected = False
    ser = serial.Serial()
    serialPort = False
    serialBaud = False
    dummyPlug = False
    saving = False
    fileName = 'save_'+str(time.time())+'.txt'
    file_handle = None
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

        #3d vizuaalizer
        stl_mesh = mesh.Mesh.from_file('rocket2.stl')
        points = stl_mesh.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)

        mesh_data = MeshData(vertexes=points, faces=faces)

        self.cube = GLMeshItem(meshdata=mesh_data, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))

        axis_length = 2.0
        self.axis_x = GLLinePlotItem(pos=np.array([[0, 0, 0], [axis_length, 0, 0]]), color=(1, 0, 0, 1))
        self.axis_y = GLLinePlotItem(pos=np.array([[0, 0, 0], [0, axis_length, 0]]), color=(0, 1, 0, 1))
        self.axis_z = GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, axis_length]]), color=(0, 0, 1, 1))
        self.visualizer.addItem(self.axis_x)
        self.visualizer.addItem(self.axis_y)
        self.visualizer.addItem(self.axis_z)
        self.visualizer.addItem(self.cube)

        camera_position = self.visualizer.cameraPosition()
        print(camera_position)
        camera_position[2] = 150  # Mettez à jour la distance de la caméra
        camera_position[1] = 100  # Mettez à jour la distance de la caméra
        camera_position[0] = 100  # Mettez à jour la distance de la caméra
        print(camera_position)
        self.visualizer.setCameraPosition(pos=camera_position)

        self.kalman_filter = KalmanFilter(dim_x=3, dim_z=3)
        self.kalman_filter.F = np.eye(3)  # Matrice de transition d'état
        self.kalman_filter.H = np.eye(3)  # Matrice d'observation
        self.kalman_filter.P *= 1e3  # Matrice de covariance d'état initiale
        self.kalman_filter.R *= 0.01  # Matrice de covariance d'observation
        self.kalman_filter.Q *= 0.1  # Matrice de covariance du bruit du processus

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

                        self.update_cube_rotation(data['quat']['quat_w'], data['quat']['quat_x'], data['quat']['quat_y'], data['quat']['quat_z'])

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
                        if self.saving and self.file_handle:
                            self.file_handle.write(value + '\n')

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

        if self.saving:
            # nouveau fichier
            self.fileName = f"save_{int(time.time())}.txt"
            self.file_handle = open(self.fileName, "a", buffering=1)  # ligne-buffering
            self.label_saving_state.setText("Recording data…")
        else:
            if self.file_handle:
                self.file_handle.close()
                self.file_handle = None
            self.label_saving_state.setText("Not recording")

        self.pushButton_start_save.setEnabled(not self.saving)
        self.pushButton_stop_save.setEnabled(self.saving)

    def getData(self):
        data = ''
        value_chain = ''
        if self.dummyPlug == False:
            data = self.ser.read(1)
            data += self.ser.read(self.ser.inWaiting())
            if data:
                value_chain = data.decode("utf-8").splitlines()
        return value_chain

    def update_cube_rotation(self, w, x, y, z):
        q = np.array([w, x, y, z], dtype=float)
        q /= np.linalg.norm(q)

        # Qt veut (x,y,z,w)
        qt = QtGui.QQuaternion(q[1], q[2], q[3], q[0])
        m4 = QtGui.QMatrix4x4();
        m4.rotate(qt)
        t = Transform3D(m4)

        for item in (self.cube, self.axis_x, self.axis_y, self.axis_z):
            item.setTransform(t)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()