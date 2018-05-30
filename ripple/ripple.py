from _ripplefilter import ffi, lib

class RippleFilter():
    def __init__(self):
        p = lib.rfilter_new()
        self._p = ffi.gc(p, lib.rfilter_destroy)
    def update(self, value):
        return lib.rfilter_update(self._p, value)


