"""Windows x64 binding for the frozen greedy and conflict-loss constructors."""
import ctypes
import time
from pathlib import Path

import numpy as np

from .s02_input import ROOT, identity, platform_check, read, write

ROW = np.dtype([('target','<i4'),('site','<i4'),('start','<i4'),('end','<i4'),
                ('points','<i4'),('window','<i4'),('id','S16')])
SLOT = np.dtype([('target','<i4'),('site','<i4'),('start','<i4'),('end','<i4')])
CHECK = ctypes.CFUNCTYPE(ctypes.c_int)


def slots(items):
    return np.fromiter(((r['satnum'],r['station_id'],r['start_s'],r['end_s']) for r in items),
                       dtype=SLOT, count=len(items))


class NativeConstructors:
    def __init__(self, receipt):
        platform_check()
        self.receipt = receipt
        self.source = self.packed = None
        native_dir = ROOT/'famou/native'
        path = native_dir/'frozen_native.dll'
        abi = read(native_dir/'ABI.json')
        expected = read(ROOT/'configs/s02_contract.json')['native']
        self.report = dict(backend='windows_x64_native',dll_path=str(path),expected=expected,calls=[],status='LOADING')
        write(receipt,self.report)
        if not path.is_file():
            raise ValueError('S02 native DLL missing: '+str(path))
        actual = identity(path)
        self.report['actual'] = actual
        write(receipt,self.report)
        if actual != expected:
            raise ValueError('S02 native DLL SHA256/size mismatch')
        if (ROW.itemsize != abi['row_bytes'] or SLOT.itemsize != abi['slot_bytes']
                or [ROW.fields[k][1] for k in ROW.names] != abi['row_offsets']
                or [SLOT.fields[k][1] for k in SLOT.names] != abi['slot_offsets']):
            raise ValueError('S02 native ABI record layout mismatch')
        try:
            self.library = ctypes.CDLL(str(path))
            self.kernel = self.library.select_rows
        except (OSError, AttributeError) as e:
            raise ValueError('S02 native DLL load or select_rows ABI export failed: '+str(e)) from e
        get_path = ctypes.WinDLL('kernel32',use_last_error=True).GetModuleFileNameW
        get_path.argtypes = [ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_uint]
        buf = ctypes.create_unicode_buffer(32768)
        if not get_path(self.library._handle,buf,len(buf)) or not Path(buf.value).samefile(path):
            raise ValueError('S02 loaded DLL path mismatch')
        self.kernel.argtypes = [ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,
                                ctypes.c_int,ctypes.c_void_p,CHECK]
        self.kernel.restype = ctypes.c_int
        probe = np.array([(1,1,0,120,15,0,b'C1')],dtype=ROW)
        answer = np.full(1,-1,dtype='<i4')
        rc = self.kernel(probe.ctypes.data,1,None,0,None,0,0,answer.ctypes.data,CHECK(lambda:0))
        if rc != 1 or answer.tolist() != [0]:
            raise ValueError('S02 native ABI call probe failed')
        self.report.update(loaded_path=buf.value,abi_probe=dict(returned=rc,indices=answer.tolist()),
                           row_bytes=ROW.itemsize,slot_bytes=SLOT.itemsize,status='LOADED')
        write(receipt,self.report)

    def select(self, candidates, fixed, interrupted, clock, method):
        started = time.perf_counter()
        reused = self.source is candidates
        if not reused:
            wins = {}
            def records():
                for r in candidates:
                    cid = r['candidate_id']
                    if not (0 < len(cid) < 16 and cid.isascii() and '\0' not in cid):
                        raise ValueError('S02 native candidate identifier is outside ABI')
                    yield (r['satnum'],r['station_id'],r['start_s'],r['end_s'],r['points_int'],
                           wins.setdefault(r['window_id'],len(wins)),cid)
            self.packed = np.fromiter(records(), dtype=ROW, count=len(candidates))
            self.source = candidates
        frozen, fragments = slots(fixed), slots(interrupted)
        selected = np.empty(len(candidates),dtype='<i4')
        errors = []
        @CHECK
        def check():
            try:
                clock.check()
                return 0
            except TimeoutError as e:
                errors.append(e)
                return 1
        clock.check()
        native_start = time.perf_counter()
        call = dict(method=('baseline','improved')[method],candidate_rows=len(candidates),
                    fixed_rows=len(fixed),reused_packed_rows=reused,packing_s=native_start-started,status='CALLING')
        self.report['calls'].append(call)
        write(self.receipt,self.report)
        n = self.kernel(self.packed.ctypes.data,len(candidates),frozen.ctypes.data,len(frozen),
                        fragments.ctypes.data,len(fragments),method,selected.ctypes.data,check)
        call.update(return_code=n,kernel_s=time.perf_counter()-native_start,status='RETURNED')
        write(self.receipt,self.report)
        if errors:
            raise errors[0]
        if not 0 <= n <= len(candidates):
            raise ValueError(f'S02 native constructor failed with return {n}')
        result = [dict(r) for r in fixed] + [dict(candidates[i]) for i in selected[:n]]
        clock.check()
        return sorted(result,key=lambda r:(r['start_s'],r['station_id'],r['satnum']))

    def greedy(self,candidates,fixed,interrupted,clock):
        return self.select(candidates,fixed,interrupted,clock,0)

    def improved_construct(self,candidates,fixed,interrupted,clock):
        return self.select(candidates,fixed,interrupted,clock,1)
