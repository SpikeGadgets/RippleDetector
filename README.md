# Sharp-Wave Ripple Detector

Python and C code that is used to detect ripples. Ripple filter and detection implementation is from the Kemere Lab at Rice University [[1]](#References)

- Jun 19, 2018: Compared to Frank lab implementation and works well. all major ripples are detected by both. False positives haven't been tested yet, since they must be done manually
- Jun 04, 2018: Finished and seems like it works, but actual accuracy hasn't been verified yet

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

To test, open Trodes, version 2.0-alpha, open a .rec file, and then run your python code. For a very simple example, refer to the code at the bottom of `manager.py`.

## C filter

Filter and parameter estimation is implemented in C for speed and then used in Python via CFFI package. We also have an option for an integer filter, in cases where floating math is not supported like microcontrollers or FPGAs.[[2]](#References)

## References

[[1] Analysis of an open source, closed-loop, realtime system for hippocampal sharp-wave ripple disruption](https://www.biorxiv.org/content/biorxiv/early/2018/04/11/298661.full.pdf)

[[2] Implementation of FIR Filtering in C (Part 2)](https://sestevenson.wordpress.com/2009/10/08/implementation-of-fir-filtering-in-c-part-2/)
