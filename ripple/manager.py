from spikegadgets import trodesnetwork as tnp
from ripple import RippleDetector
import numpy as np
class RippleClient(tnp.AbstractModuleClient):
    def setTerminateCallback(self, callback):
        self.terminateCallback = callback

    def recv_quit(self):
        self.terminateCallback()

    def recv_acquisition(self, command, timestamp):
        if command == tnp.acq_PAUSE:
            self.terminateCallback()

class VelocityCalculator():
    def __init__(self, framerate):
        self.lastx = 0.0
        self.lasty = 0.0
        self.velocity = 0.0
        self.lastvel = 0.0
        self.framerate = framerate
        self.perframe = 1/framerate
    def calculateVelocity(self, x, y):
        # Current velocity is basically by pixels
        # TODO Add pixels to real distance conversion
        dist = np.sqrt((self.lastx-x)**2 + (self.lasty-y)**2)
        vel = dist/self.perframe
        self.lastx = x
        self.lasty = y
        self.velocity = (vel+self.lastvel)/2
        self.lastvel = vel

class RippleManager():
    """Module that handles ripple detection of multiple ntrodes
    - Manages network object
    - Tracks the time across detected ripples, lockout period
    - Does timestamp conversions based on trodes timestamps
    - If true, does position/velocity tracking
    """
    def __init__(self,ntrodes, minimumdetected=1, within=15, traininglength=20*60*1000, lockoutlength=200, threshmultiplier =4, positiontracking=False, velocitythresh = 200, videoframerate = 30, timestampconverter = 30000):
        self.samplingrate = 3000
        self.ntrodes = ntrodes
        self.numntrodes = len(ntrodes)
        self.minimumdetected = minimumdetected
        self.within = within

        #time to train params, default 20min*60sec*1000ms
        self.traininglength = traininglength
        self.trainingsamples = int(traininglength*self.samplingrate/1000)
        
        #lockout period, default 200ms
        self.lockoutlength = self.samplingrate*lockoutlength/1000
        self.lockedOut = False
        self.lockoutTime = 0

        print("Training samples: {}, lockout length: {}".format(self.trainingsamples, self.lockoutlength))

        #is position tracking on, default False
        self.positiontracking = positiontracking
        self.framerate = videoframerate
        self.velocitythresh = velocitythresh
        #
        self.timestampconversion = timestampconverter
        self.terminate = False
        self.historylength = int(within*self.samplingrate/1000)

        # one detector per ntrode
        self.detectors = []
        for i in ntrodes:
            self.detectors.append(RippleDetector(self.trainingsamples, threshmultiplier))
        
        # (ntrodes x historylength) ringbuffer
        self.detecthistory = np.zeros((self.numntrodes, self.historylength), dtype=np.bool)
        self.histIndex = 0 #use as ringbuffer

    """Initialize data streams from Trodes and possibly cameramodule"""
    def initstreams(self, network):
        self.lfpstream = network.subscribeLFPData(30, [str(n) for n in self.ntrodes])
        self.lfpstream.initialize()
        self.buf = self.lfpstream.create_numpy_array()
        if self.positiontracking:
            self.velcalc = VelocityCalculator(self.framerate)
            #Position stream
            self.positionstream = network.subscribeHighFreqData('PositionData', 'CameraModule', 2)
            self.positionstream.initialize()
            ndtype = self.positionstream.getDataType().dataFormat
            nbytesize = self.positionstream.getDataType().byteSize
            buf = memoryview(bytes(nbytesize))
            self.posbuf = np.frombuffer(buf, dtype=np.dtype(ndtype))

    def terminatecb(self):
        if not self.terminate:
            print("TERMINATE CALLBACK")
            self.terminate = True

    def isrippleDetected(self):
        if not self.lockedOut:
            # if moving fast enough, don't bother calculating
            if self.positiontracking and self.velcalc.velocity > self.velocitythresh:
                return False

            #for each n ntrode, check if True exists in the history
            trues = [True in n for n in self.detecthistory]
            histcount = trues.count(True)

            #if got enough ntrodes to detect a ripple, then success
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
        self.lockoutTime = 0
        self.lockedOut = False

    def main_loop(self):
        timestamp = []

        while not self.terminate:
            # First update the velocity if any position data came in
            if self.positiontracking:
                n = self.positionstream.available(0)
                for i in range(n):
                    byteswritten = self.positionstream.readData(self.posbuf)
                    self.velcalc.calculateVelocity(self.posbuf[0][3], self.posbuf[0][4])
                    # self.vels.append(self.velcalc.velocity)

            n = self.lfpstream.available(1)
            # Get new lfp data
            for i in range(n):
                timestamp = self.lfpstream.getData()

                # Update filters and check detection for each ntrode
                for i in range(self.numntrodes):
                    r = self.detectors[i].rippledetection(self.buf[i])
                    self.detecthistory[i][self.histIndex] = r
                    self.histIndex = (self.histIndex+1)%self.historylength

                # Reset lockout if enough time has passed
                if self.lockoutTime + self.lockoutlength < timestamp.trodes_timestamp:
                    self.lockedOut = False

                # Check if ripple detected, print out, and set lockout
                if self.isrippleDetected():
                    print(timestamp.trodes_timestamp, "RIPPLE DETECTED. Latency:", tnp.systemTimeMSecs()-timestamp.system_timestamp)
                    self.lockedOut = True
                    self.lockoutTime = timestamp.trodes_timestamp

if __name__ == "__main__":
    import time
    net = RippleClient("Rippleclient", "tcp://127.0.0.1", 49152)
    net.initialize()

    rm = RippleManager(ntrodes=[4,9,10,11], minimumdetected=2, traininglength=1*60*1000, threshmultiplier=3, positiontracking=True) # minutes * 60s * 1000ms
    rm.initstreams(net)
    net.setTerminateCallback(rm.terminatecb)

    rm.main_loop()

    del net