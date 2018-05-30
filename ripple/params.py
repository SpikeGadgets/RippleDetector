from _ripplefilter import ffi, lib

class RippleParams():
    """Ripple filter for spikegadgets ripple package. Written in C, compiled with cffi 
    Takes in values from filter to create parameters for  """ 
    def __init__(self, datalen, threshcontrol):
        p = lib.rparams_new(datalen, threshcontrol)
        self._p = ffi.gc(p, lib.rparams_destroy)

    """Add value to parameter estimator. 
        - Parameters will be automatically calculated once number of data reaches `datalen`
        - If array has been filled and parameters calculated, any further calls will be ignored unless reset is called."""
    def update(self, value):
        return lib.rparams_update(self._p, value)

    """Resets all the parameters so it can be run again"""
    def reset(self):
        return lib.rparams_reset(self._p)

    """Returns if the parameters have finished estimated or not"""
    def estimated(self):
        return lib.rparams_estimated(self._p)

    """Returns the mean"""
    def mean(self):
        return lib.rparams_mean(self._p)
        
    """Returns the standard deviation"""
    def stdev(self):
        return lib.rparams_stdev(self._p)

    """Returns ripple threshold"""
    def threshold(self):
        return lib.rparams_threshold(self._p)