#!/usr/bin/env python3

import sys

from cffi_test import ffi, lib                                                                                                                     

handle = ffi.new("int *", -1)                                                                                                                           
ret = lib.CAENHV_InitSystem(0, 0, b"172.22.4.1", b"admin", b"admin" , handle)

if ret != 0:
    print("connection failed")
    sys.exit(1)

nrSlots = ffi.new("unsigned short *")
nrChList = ffi.new("unsigned short **")
chModelList = ffi.new("char *[100]")
chDescList = ffi.new("char **")
sernumList = ffi.new("unsigned short *")
sernumList = ffi.new("unsigned short **")
fwRelMinList = ffi.new("unsigned char **")
fwRelMaxList = ffi.new("unsigned char **")

ret = lib.CAENHV_GetCrateMap(0, nrSlots, nrChList, chModelList, chDescList, sernumList, fwRelMinList, fwRelMaxList)
print( hex(ret))

n = nrSlots[0]
print("N:", n)

for a in range(n):
    print( nrChList[0][a])


