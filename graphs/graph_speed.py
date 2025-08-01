import time, numpy as np, math, pyqtgraph as pg

class graph_speed(pg.PlotWidget):

    def __init__(self, obj, parent=None, title="Speed (m/s)", **k):
        super().__init__(parent=None, background="default", plotItem=None, **k)
        self.obj = obj
        self.curve = self.obj.plot(pen=(29,185,84))
        self.obj.setTitle(title)

        self.buf = np.zeros(50)          # 50 pts historiques
        self.ptr = 0
        self.vx = self.vy = self.vz = 0.0
        self.t_prev = None               # timestamp précédent

    # ------------------------------------------------------------------
    def update(self, ax, ay, az):
        t_now = time.monotonic()
        if self.t_prev is None:          # première passe
            self.t_prev = t_now
            return

        dt = t_now - self.t_prev
        self.t_prev = t_now
        if dt <= 0 or dt > 1:            # saut d’horloge ? on ignore
            return

        # --------- enlever la gravité sur Z ---------
        az -= 9.80665                    # m/s²

        # --------- petit seuil pour le bruit --------
        TH = 0.15                        # m/s²
        ax = 0 if abs(ax) < TH else ax
        ay = 0 if abs(ay) < TH else ay
        az = 0 if abs(az) < TH else az

        # --------- intégration simple (Euler) -------
        self.vx += ax * dt
        self.vy += ay * dt
        self.vz += az * dt

        speed = math.sqrt(self.vx**2 + self.vy**2 + self.vz**2)

        # --------- mise en tampon pour le graphe ----
        self.buf[:-1] = self.buf[1:]
        self.buf[-1] = speed
        self.ptr += 1
        self.curve.setData(self.buf)
        self.curve.setPos(self.ptr, 0)
