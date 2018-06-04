from ripple.filter import *
from ripple.params import *

class RippleDetector():
    def __init__(self, estimationlen, threshmultiplier=4):
        self.rfilter = RippleFilter()
        self.rparams = RippleParams(estimationlen, threshmultiplier)
        self.isTraining = True
        self.rippleThreshold = 0.0

    """Check if value (int16) passes threshold for a ripple
        - If params not finished, add to params
        - Else, check with threshold"""
    def rippledetection(self, value):
        filtereddata = self.rfilter.update(value)
        if self.isTraining:
            self.rparams.update(filtereddata)
            if self.rparams.estimated():
                self.isTraining = False
                self.rippleThreshold = self.rparams.threshold()
                # print("Threshold set at ", self.rippleThreshold, " Mean: ", self.rparams.mean(), " Stdev: ", self.rparams.stdev())
            return False
        elif filtereddata > self.rippleThreshold:
            return True
        return False

    """Reset the ripple parameters and re-estimate them"""
    def reestimateParams(self):
        self.rparams.reset()
        self.isTraining = True 

    """Get mean, stdev, and threshold parameters"""
    def getParameters(self):
        return self.rparams.mean(), self.rparams.stdev(), self.rippleThreshold

