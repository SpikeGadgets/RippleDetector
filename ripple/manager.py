from _ripplefilter import ffi, lib

class RippleManager():
    """
    Manages ripple detectors and position data to calculate if a valid ripple occured
    """
    def __init__(self, numntrodes, mindetected, trainingsamples, sdthreshold, samplehistory):
        p = lib.rmanager_new(numntrodes, mindetected, trainingsamples, sdthreshold, samplehistory)
        self._p = ffi.gc(p, lib.rmanager_destroy)

    def useposition(self, enable, velocitythresh):
        lib.rmanager_useposition(self._p, enable, velocitythresh)

    def position(self, x, y):
        lib.rmanager_position(self._p, x, y)

    def lfpdata(self, data):
        lib.rmanager_lfpdata(self._p, ffi.cast("int16_t *", ffi.from_buffer(data)))

    def checkripples(self):
        return lib.rmanager_checkripples(self._p)

    def reset(self):
        lib.rmanager_reset(self._p)