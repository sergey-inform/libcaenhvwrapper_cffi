#!/usr/bin/env python3

import sys, os
import time
import socket
import signal

from cffi_test import ffi, lib

''' A plain script to periodically read IMon and VMon of selected channels. '''

CAEN_ADDR = '172.22.4.1'
CAEN_LOGIN, CAEN_PASSW = b'admin', b'admin'

CH_BRD = 3
CH_LIST = 4,5,6 
# --------------------------------------------
def _ascii(arg):
    ''' Convert arg to bytes if possible. '''
    if isinstance(arg, bytes):
        return arg
    elif isinstance(arg, str):
        return arg.encode('ascii')

def signal_handler(sig, frame):
    print('Interrupted by user.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


caenhv_ip = _ascii(socket.gethostbyname(CAEN_ADDR))
caenhv_login = _ascii(os.environ.get('CAEN_LOGIN')) or CAEN_LOGIN
caenhv_passw = _ascii(os.environ.get('CAEN_PASSW')) or CAEN_PASSW

handle = ffi.new("int *", -1)

ret = lib.CAENHV_InitSystem(lib.SY1527, lib.LINKTYPE_TCPIP, 
                                caenhv_ip,
                                caenhv_login,
                                caenhv_passw,
                                handle)
if ret != 0:
    sys.stderr.write("Connection error.\n")
    sys.exit(1)

brd = int(CH_BRD)
n = len(CH_LIST)
buf = ffi.new('float[]', n)
chans = ffi.new('const unsigned short[]', list(CH_LIST)) 

prev = None

logfile = open("hv.log", 'a')

def log_hdr(logfile, chanlist):
    channames = ["={}=".format(str(x), ) for x in chanlist]
    logfile.write("# ts\t{}\n".format("\t".join(channames)))

def log_vals(logfile, ts, vals):
    vals_format = "{:5.1f} {:3.1f}" # V, I
    str_vals = "\t".join((vals_format.format(a,b) for a,b in zip(*vals)))
    logfile.write("{:<#10.2f}\t{}\n".format(ts, str_vals))
    pass

print_format = "{:<12}  {} "

def print_hdr(chanlist):
    channames = ["{:^15}".format(str(x), ) for x in chanlist]
    print(print_format.format("# ts", "  ".join(channames)))

def print_vals(timestr, vals, prev):
    vals_format = "{: >#5.1f}  {: >#3.1f} uA "
    str_vals = "  ".join((vals_format.format(a,b) for a,b in zip(*vals)))
    print(print_format.format(timestr, str_vals),
            end = ' \n' if vals != prev else ' \r',
            flush = True,
            )

if logfile:
    log_hdr(logfile, CH_LIST)

print_hdr(CH_LIST)

while(True):
    ts = time.time() 
    # Request IMon
    ret = lib.CAENHV_GetChParam(handle[0], brd, b'IMon', n, chans, buf)
    vals_IMon = tuple(buf) if ret == 0 else [None] * n
    # Reauest VMon
    ret = lib.CAENHV_GetChParam(handle[0], brd, b'VMon', n, chans, buf)
    vals_VMon = tuple(buf) if ret == 0 else [None] * n

    vals = (vals_VMon, vals_IMon)

    if logfile:
        log_vals(logfile, ts, vals)

    #str_time = time.strftime("%H:%M:%S") + "{:#.2f}".format(ts%1).lstrip("01")  # time + msec
    str_time = time.strftime("%H:%M:%S") 
    print_vals(str_time, vals, prev)

    if prev == vals:
        time.sleep(1.0)
        logfile.flush()
    else:
        time.sleep(0.05)

    prev = vals
