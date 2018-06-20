from spikegadgets import trodesnetwork as tnp
from ripple import RippleManager
import numpy as np
class RippleClient(tnp.AbstractModuleClient):
    def setTerminateCallback(self, callback):
        self.terminateCallback = callback

    def recv_quit(self):
        self.terminateCallback()

    def recv_acquisition(self, command, timestamp):
        if command == tnp.acq_PAUSE:
            self.terminateCallback()

class RippleModule():
    def __init__(self,ntrodes, minimumdetected=1, within=15, traininglength=20*60*1000, lockoutlength=200, threshmultiplier =4, positiontracking=False, velocitythresh = 200, videoframerate = 30, timestampconverter = 30000):
        self.samplingrate = 3000
        self.ntrodes = ntrodes
        self.numntrodes = len(ntrodes)
        self.minimumdetected = minimumdetected
        self.withinsamples = int(within*self.samplingrate/1000)
        self.threshmultiplier = threshmultiplier

        #time to train params, default 20min*60sec*1000ms
        self.trainingsamples = int(traininglength*self.samplingrate/1000)
        print("Training samples: {}".format(self.trainingsamples))

        #lockout period, default 200ms
        self.lockoutlength = self.samplingrate*lockoutlength/1000
        self.stimLockedOut = False
        self.lockoutTime = 0

        self.manager = RippleManager(self.numntrodes, self.minimumdetected, self.trainingsamples, self.threshmultiplier, self.withinsamples)

        #is position tracking on, default False
        self.positiontracking = positiontracking
        self.framerate = videoframerate
        self.velocitythresh = velocitythresh
        
        self.timestampconversion = timestampconverter
        self.terminate = False
        self.historylength = int(within*self.samplingrate/1000)


    """Initialize data streams from Trodes and possibly cameramodule"""
    def initstreams(self, network):
        self.lfpstream = network.subscribeLFPData(30, [str(n) for n in self.ntrodes])
        self.lfpstream.initialize()
        self.buf = self.lfpstream.create_numpy_array()
        if self.positiontracking:
            #Position stream
            self.positionstream = network.subscribeHighFreqData('PositionData', 'CameraModule', 2)
            self.positionstream.initialize()
            ndtype = self.positionstream.getDataType().dataFormat
            nbytesize = self.positionstream.getDataType().byteSize
            buf = memoryview(bytes(nbytesize))
            self.posbuf = np.frombuffer(buf, dtype=np.dtype(ndtype))
            #enable position data in manager
            self.manager.useposition(True, self.velocitythresh)

    def terminatecb(self):
        if not self.terminate:
            print("TERMINATE CALLBACK")
            self.terminate = True

    def resetparams(self):
        self.manager.reset()
        self.terminate = False
        self.lockoutTime = 0
        self.stimLockedOut = False

    def main_loop(self):
        timestamp = []

        while not self.terminate:
            # First update the velocity if any position data came in
            if self.positiontracking:
                n = self.positionstream.available(0)
                for i in range(n):
                    byteswritten = self.positionstream.readData(self.posbuf)
                    self.manager.position(self.posbuf[0][3], self.posbuf[0][4])

            n = self.lfpstream.available(1)
            # Get new lfp data
            for i in range(n):
                timestamp = self.lfpstream.getData()

                # Update filters and check detection for each ntrode
                self.manager.lfpdata(self.buf)

                # Reset lockout if enough time has passed
                if self.lockoutTime + self.lockoutlength < timestamp.trodes_timestamp:
                    self.stimLockedOut = False

                # Check if ripple detected, print out, and set lockout
                if self.manager.checkripples():
                    # print(timestamp.trodes_timestamp, "RIPPLE DETECTED. Latency:", tnp.systemTimeMSecs()-timestamp.system_timestamp)
                    print(timestamp.trodes_timestamp)
                    self.stimLockedOut = True
                    self.lockoutTime = timestamp.trodes_timestamp

if __name__ == "__main__":
    import time
    net = RippleClient("Rippleclient", "tcp://127.0.0.1", 49152)
    net.initialize()

    rm = RippleModule(ntrodes=[1,8,10,11,12,13,14], minimumdetected=2, traininglength=20*1000, threshmultiplier=5)
    rm.initstreams(net)
    net.setTerminateCallback(rm.terminatecb)

    rm.main_loop()

    del net