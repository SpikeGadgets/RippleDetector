from _ripplefilter import ffi, lib

class RippleFilter():
    """Ripple filter for spikegadgets ripple package. Written in C, compiled with cffi 
    Passes values through a bandpass filter followed by lowpass filter. Uses floating point math""" 
    def __init__(self):
        p = lib.rfilter_new()
        self._p = ffi.gc(p, lib.rfilter_destroy)
        
    """Adds a value (cast to int16) to the filter
    Returns the calculated value (double)"""
    def update(self, value):
        return lib.rfilter_update(self._p, value)


class RippleIntFilter():
    """Ripple filter for spikegadgets ripple package. 
    
    *** Uses 16 bit integer math***

     Written in C, compiled with cffi 
    Passes values through a bandpass filter followed by lowpass filter.""" 
    def __init__(self):
        p = lib.rintfilter_new()
        self._p = ffi.gc(p, lib.rintfilter_destroy)

    def update(self, value):
        return lib.rintfilter_update(self._p, value)