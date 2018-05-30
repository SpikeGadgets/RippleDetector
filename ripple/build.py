import cffi
import os
ffibuilder = cffi.FFI()
header = ""
src = ""

with open("ripple/ripplefilter.h") as f:
    header = f.read().split("///_PYTHONCFFI")[1]
    ffibuilder.cdef(header)

with open("ripple/ripplefilter.c") as f:
    src = f.read().split("///_PYTHONCFFI")[1]
    ffibuilder.set_source("_ripplefilter",header + src)


if __name__ == "__main__":
    ffibuilder.compile()