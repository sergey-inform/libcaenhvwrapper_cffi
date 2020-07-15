import cffi
ffi = cffi.FFI()
with open('wrapper.h') as file:
	ffi.cdef(file.read(), override=True);
ffi.set_source("cffi_test", '#include "wrapper.h"', library_dirs=["./libcaenhvwrapper/x64/"], extra_link_args=['-Wl,-rpath,./libcaenhvwrapper/x64/', '-l:libcaenhvwrapper.so.5.82', '-shared', '-I/usr/include/python3.8'])
ffi.compile()
