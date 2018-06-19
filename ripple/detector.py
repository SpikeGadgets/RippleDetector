from _ripplefilter import ffi, lib

class RippleDetector():
    def __init__(self, estimationlen, threshmultiplier=4):
        p = lib.rdetector_new()
        self._p = ffi.gc(p, lib.rdetector_destroy)

    def detect(self, value):
        return bool(lib.rdetector_detect(self._p, value))
        
    def reset(self):
        lib.rdetector_reset(self._p)
        
# from ripple.filter import *
# from ripple.params import *
# import numpy as np
# class RippleDetector():
#     def __init__(self, estimationlen, threshmultiplier=4):
#         self.rfilter = RippleFilter()
#         self.rparams = RippleParams(estimationlen, threshmultiplier)
#         self.isTraining = True
#         self.rippleThreshold = 0.0
#         self.data = np.zeros(3000*20)
#         self.i = 0

#     def getdata(self):
#         return self.data[:self.i]

#     """Check if value (int16) passes threshold for a ripple
#         - If params not finished, add to params
#         - Else, check with threshold"""
#     def rippledetection(self, value):
#         filtereddata = self.rfilter.update(value)
#         if(self.i<3000*20):
#             self.data[self.i] = filtereddata
#             self.i += 1
#         if self.isTraining:
#             self.rparams.update(filtereddata)
#             if self.rparams.estimated():
#                 self.isTraining = False
#                 self.rippleThreshold = self.rparams.threshold()
#                 print("Threshold set at ", self.rippleThreshold, " Mean: ", self.rparams.mean(), " Stdev: ", self.rparams.stdev())
#             return False
#         elif filtereddata > self.rippleThreshold:
#             return True
#         return False

#     """Reset the ripple parameters and re-estimate them"""
#     def reestimateParams(self):
#         self.rparams.reset()
#         self.isTraining = True 

#     """Get mean, stdev, and threshold parameters"""
#     def getParameters(self):
#         return self.rparams.mean(), self.rparams.stdev(), self.rippleThreshold

