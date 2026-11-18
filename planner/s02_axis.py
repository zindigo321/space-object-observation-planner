"""Reuse Skyfield time-only quantities on the exact integer-second sample axis."""
import numpy as np
from planner.tle_adapter import Geometry

class _Orbit:
    def __init__(self, owner, satellite):
        self.owner = owner
        self.satellite = satellite

    def at(self, t):
        owner = self.owner
        if t is not owner.coarse_time:
            return self.satellite.at(t)
        if owner.last_satellite is not self:
            owner.coarse_position = self.satellite.at(t)
            owner.last_satellite = self
        return owner.coarse_position

class CachedGeometry(Geometry):
    def __init__(self, records, stations, day, clock, horizon, step):
        super().__init__(records, stations, day, clock)
        self.horizon = horizon
        self.coarse_seconds = np.unique(np.append(np.arange(0, horizon + 1, step), horizon))
        self.coarse_time = None
        self.last_satellite = self.coarse_position = None
        self.satellites = {n: _Orbit(self, sat) for n, sat in self.satellites.items()}
        self.axis = None

    def prepare_axis(self):
        seconds = np.arange(self.horizon + 1, dtype=np.int64)
        axis = super().times(seconds)
        rotation = np.empty((3, 3, len(seconds)))
        gast = np.empty(len(seconds))
        ut1 = np.empty(len(seconds))
        for first in range(0, len(seconds), 512):
            self.clock.check()
            block = slice(first, first + 512)
            part = axis[block]
            rotation[..., block] = part.M
            gast[block] = part.gast
            ut1[block] = part.ut1_fraction
        axis.M, axis.gast, axis.ut1_fraction = rotation, gast, ut1
        self.axis = axis

    def times(self, seconds):
        if self.axis is None:
            self.prepare_axis()
        s = np.asarray(seconds, dtype=np.int64)
        coarse = s.shape == self.coarse_seconds.shape and np.array_equal(s, self.coarse_seconds)
        if coarse and self.coarse_time is not None:
            return self.coarse_time
        contiguous = len(s) and s[-1] - s[0] + 1 == len(s) and np.all(np.diff(s) == 1)
        index = slice(int(s[0]), int(s[-1]) + 1) if contiguous else s
        t = self.axis[index]
        t.M, t.gast = self.axis.M[..., index], self.axis.gast[index]
        if coarse:
            self.coarse_time = t
        return t

