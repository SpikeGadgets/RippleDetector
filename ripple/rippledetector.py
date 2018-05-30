from ripple.ripplefilter import *
from ripple.rippleparams import *

class RippleDetector():
    def __init__(self, estimationlen, threshmultiplier):
        self.rfilter = RippleFilter()
        self.rparams = RippleParams(estimationlen, threshmultiplier)
        self.isTraining = True
        self.rippleThreshold = 0.0

    """Check if value (int16) passes threshold for a ripple
        - If params not finished, add to params
        - Else, check with threshold"""
    def rippledetection(self, value):
        if self.isTraining:
            self.rparams.update(value)
            if self.rparams.estimated():
                self.isTraining = False
                self.rippleThreshold = self.rparams.threshold()
            return False
        else:
            filtereddata = self.rfilter.update(value)
            if filtereddata > self.rippleThreshold:
                return True
            return True

    """Reset the ripple parameters and re-estimate them"""
    def reestimateParams(self):
        self.rparams.reset()
        self.isTraining = True 

    """Get mean, stdev, and threshold parameters"""
    def getParameters(self):
        return self.rparams.mean(), self.rparams.stdev(), self.rippleThreshold

