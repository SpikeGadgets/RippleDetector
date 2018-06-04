# Sharp-Wave Ripple Detector

Python and C code that is used to detect ripples. Ripple filter and detection implementation is from the Kemere Lab at Rice University [1]

## Installing

Make sure you have installed the new Trodes networking API before using:

[https://github.com/SpikeGadgets/TrodesNetwork](https://github.com/SpikeGadgets/TrodesNetwork)

To install the package:

```bash
pip3 install .
```

or

```bash
python3 setup.py install
```

(May need root privileges if you are using the system-installed python)

### Testing and development

Developed and tested on Ubuntu 16.04 using the system-included Python3.

- Jun 04, 2018: Finished and seems like it works, but actual accuracy hasn't been verified yet

## C filter

Filter and parameter estimation is implemented in C for speed and then used in Python via CFFI package.

[1] [Analysis of an open source, closed-loop, realtime system for hippocampal sharp-wave ripple disruption](https://www.biorxiv.org/content/biorxiv/early/2018/04/11/298661.full.pdf)