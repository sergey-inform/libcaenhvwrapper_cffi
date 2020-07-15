#!/usr/bin/env python3

import sys
import time
import numpy as np
from itertools import chain, cycle
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
import datetime

fp = open('hv.log', 'r')

while True:
    line = fp.readline()
    if line[0] != '#':  # skip comments
        break 

vals = line.split() #split on whitespace

# expecting floats: <ts> <1:VMon> <1:IMon> <2:VMon> <2:IMon> ... 
ncols = len(vals)
if len(vals) < 3 or len(vals[1:]) % 2 == 1: # odd number of value columns
    sys.stderr.write("Unexpected file format: {}\n".format(vals))
    exit(1)
else:
    try:
        ts_start = float(vals[0])
        v_start = tuple(map(float,vals[1::2])) 
        i_start = tuple(map(float,vals[2::2]))
    except ValueError as e:
        sys.stderr.write(e)
        exit(1)

nchans = ncols // 2  # number of pairs VMon IMon

log_since_date = time.strftime("%D %H:%M", time.localtime(int(ts_start)))
print("Import log since: {} ...".format(log_since_date))

fields_vmon =["{}_VMon".format(x) for x in range(nchans)]
fields_imon =["{}_IMon".format(x) for x in range(nchans)]
fieldnames = ['ts'] + list(chain(*zip(fields_vmon, fields_imon))) # V and I interleaved

print(fieldnames)

arr = np.genfromtxt(fp, names= fieldnames)
fp.close()

#print(arr)

# Plot
markers =( 'v', '^', '<', '>', 'x', '+')

# Convert timestamps to dates
import datetime as dt
dateconv = np.vectorize(dt.datetime.fromtimestamp)
dates = dateconv(arr['ts'])

lastHour = datetime.datetime.now() - datetime.timedelta(minutes = 80)
lastHour_idx = np.argmax(dates> lastHour)  # since lastHour

arr = arr[lastHour_idx:]
dates = dates[lastHour_idx:]


ax=plt.gca()
ax1 = plt.subplot(211)
ax1.set_ylabel('Volts')
marker = cycle(markers)
for name in fields_vmon:
    plt.plot(dates,arr[name], label=name, marker = next(marker))
plt.setp(ax1.get_xticklabels(), visible=False) #hide dates
plt.legend()

ax2 = plt.subplot(212, sharex=ax1)
ax2.set_ylabel('uA')
marker = cycle(markers)
for name in fields_imon:
    plt.plot(dates, arr[name], label=name, marker = next(marker))
plt.legend()

locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
formatter = mdates.ConciseDateFormatter(locator)
ax2.xaxis.set_major_locator(locator)
ax2.xaxis.set_major_formatter(formatter)

plt.xticks( rotation=25 )
#plt.show()
plt.savefig('hv.png')

