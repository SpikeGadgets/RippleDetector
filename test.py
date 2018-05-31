from ripple import RippleIntFilter, RippleFilter
import numpy as np
import random 
import time
#calculate mse of int vs floating point filters
ri = RippleIntFilter()
rp = RippleFilter()
invals = [i for i in range(-2**15,2**15)]
random.shuffle(invals)

riout = np.array([ri.update(i) for i in invals])
rpout = np.array([rp.update(i) for i in invals])

mse = ((rpout-riout)**2).mean()
print("mse: ", mse)

start = time.monotonic()
for i in range(30000):
    ri.update(invals[i])
end = time.monotonic()
print("Integer 30000 updates: ", (end-start)*1000, " msecs")

start = time.monotonic()
for i in range(30000):
    rp.update(invals[i])
end = time.monotonic()
print("Floats 30000 updates: ", (end-start)*1000, " msecs")