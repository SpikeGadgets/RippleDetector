from _ripplefilter import ffi, lib

class RippleFilter():
    """Ripple filter for spikegadgets ripple package. Written in C, compiled with cffi 
    Passes values through a bandpass filter followed by lowpass filter. """ 
    def __init__(self):
        p = lib.rfilter_new()
        self._p = ffi.gc(p, lib.rfilter_destroy)
    def update(self, value):
        return lib.rfilter_update(self._p, value)


