import pyqtgraph as pg
import numpy as np
import math


class graph_speed(pg.PlotWidget):

    def __init__(self, object, parent=None, title='Speed (m/s)', **kargs):
        super().__init__(parent=None, background='default', plotItem=None, **kargs)

        self.object = object

        self.vel_plot = self.object.plot(pen=(29, 185, 84))
        self.object.setTitle(title)
        self.vel_data = np.linspace(0, 0, 30)
        self.ptr = 0
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.vel = 0


    def update(self, vx, vy, vz):
        i = 0
        if(i == 0):
            vzo = float(vz)
            i += 1

        self.vx += (float(vx)) * 500
        self.vy += (float(vy)) * 500
        self.vz += (float(vz) - vzo) * 500
        self.sum = math.pow(self.vx, 2) + math.pow(self.vy, 2) + math.pow(self.vz, 2)
        self.vel = math.sqrt(self.sum)
        self.vel_data[:-1] = self.vel_data[1:]
        self.vel_data[-1] = self.vel
        self.ptr += 1
        self.vel_plot.setData(self.vel_data)
        self.vel_plot.setPos(self.ptr, 0)