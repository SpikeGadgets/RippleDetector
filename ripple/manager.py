from spikegadgets import trodesnetwork as tnp
from ripple import RippleDetector
import numpy as np
class RippleClient(tnp.AbstractModuleClient):
    def setTerminateCallback(self, callback):
        print("terminate callback set to ", callback)
        self.terminateCallback = callback

    def recv_quit(self):
        self.terminateCallback()

    def recv_acquisition(self, command, timestamp):
        if command == tnp.acq_PAUSE:
            self.terminateCallback()


class RippleManager():
    """Module that handles ripple detection of multiple ntrodes
    - Manages network object
    - Tracks the time across detected ripples, lockout period
    - Does timestamp conversions based on trodes timestamps
    - If true, does position/velocity tracking
    """
    def __init__(self,ntrodes, minimumdetected=1, within=15, samplingrate=3000, traininglength=20*60*1000, lockoutlength=200, positiontracking=False, timestampconverter = 30000):
        # self.network = network
        # network.setTerminateCallback(self.terminatecb)
        self.ntrodes = ntrodes
        self.numntrodes = len(ntrodes)
        self.minimumdetected = minimumdetected
        self.within = within

        #time to train params, default 20min*60sec*1000ms
        self.traininglength = traininglength
        self.trainingsamples = int(traininglength*samplingrate/1000)
        
        #lockout period, default 200ms
        self.lockoutlength = samplingrate*lockoutlength/1000
        self.lockedOut = False
        self.lockoutTime = 0

        #is position tracking on, default False
        self.positiontracking = positiontracking

        #
        self.timestampconversion = timestampconverter
        self.terminate = False
        self.historylength = int(within*samplingrate/1000)

        # one detector per ntrode
        self.detectors = []
        for i in ntrodes:
            self.detectors.append(RippleDetector(self.trainingsamples))
        
        # (ntrodes x historylength) ringbuffer
        self.detecthistory = np.zeros((self.numntrodes, self.historylength), dtype=np.bool)
        self.histIndex = 0 #use as ringbuffer

    """Initialize data streams from Trodes and possibly cameramodule"""
    def initstreams(self, network):
        self.lfpstream = network.subscribeLFPData(10, [str(n) for n in self.ntrodes])
        self.lfpstream.initialize()
        self.buf = self.lfpstream.create_numpy_array()
        #if positiontracking:
            #... ... 

    def terminatecb(self):
        if not self.terminate:
            print("TERMINATE CALLBACK")
            self.terminate = True

    def rippleDetected(self):
        # print("Checking for ripples")
        if not self.lockedOut:
            #for each n ntrode, check if True exists in the history
            trues = [True in n for n in self.detecthistory]
            histcount = trues.count(True)
            if histcount >= self.minimumdetected:
                print(trues)
                return True

        return False

    def resetparams(self):
        for det in self.detectors:
            det.reestimateParams()
        self.detecthistory = np.zeros((self.numntrodes, self.historylength), dtype=np.bool)
        self.histIndex = 0 #use as ringbuffer
        self.terminate = False

    def main_loop(self):
        timestamp = []

        while not self.terminate:
            n = self.lfpstream.available(1)
            for i in range(n):
                timestamp = self.lfpstream.getData()

                for i in range(self.numntrodes):
                    r = self.detectors[i].rippledetection(self.buf[i])
                    self.detecthistory[i][self.histIndex] = r
                    # print(self.detecthistory[i][self.histIndex])
                    # print(self.buf[i])
                    # if r:
                        # print("Ripple in ntrode ", self.ntrodes[i])
                    self.histIndex = (self.histIndex+1)%self.historylength

                if self.lockoutTime + self.lockoutlength < timestamp.trodes_timestamp:
                    self.lockedOut = False
                    # print("LOCKOUT ENDED")
                # #if detection for at least `minimumdetected` ntrodes occured in the recorded history
                if self.rippleDetected():
                    print(timestamp.trodes_timestamp, "RIPPLE DETECTED")
                    self.lockedOut = True
                    self.lockoutTime = timestamp.trodes_timestamp

if __name__ == "__main__":
    net = RippleClient("Rippleclient", "tcp://127.0.0.1", 49152)
    net.initialize()

    rm = RippleManager(ntrodes=[5,6,7,8], minimumdetected=2, traininglength=3*60*1000) # 3 minutes * 60s * 1000ms
    rm.initstreams(net)
    net.setTerminateCallback(rm.terminatecb)
    
    rm.main_loop()

    del net