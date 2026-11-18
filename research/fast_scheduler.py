"""Local research adapter. All packing, indexing, search and selection run inside solve."""
import ctypes
from pathlib import Path
import numpy as np

ROW = np.dtype([('target','<i4'),('site','<i4'),('start','<i4'),('end','<i4'),
                ('points','<i4'),('window','<i4'),('id','S16')])
SLOT = np.dtype([('target','<i4'),('site','<i4'),('start','<i4'),('end','<i4')])
CHECK = ctypes.CFUNCTYPE(ctypes.c_int)
def slots(items):
    return np.fromiter(((r['satnum'],r['station_id'],r['start_s'],r['end_s']) for r in items),
                       dtype=SLOT, count=len(items))

def install(scheduler):
    library=ctypes.CDLL(str(Path(__file__).with_name('frozen_native.dll')))
    kernel=library.select_rows
    kernel.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,
                     ctypes.c_int,ctypes.c_void_p,CHECK]
    kernel.restype=ctypes.c_int
    legacy=[scheduler.greedy,scheduler.improved_construct]
    cached_source=packed=None
    def select(candidates, fixed, interrupted, clock, method):
        nonlocal cached_source,packed
        if cached_source is not candidates:
            wins={}
            def records():
                for r in candidates:
                    cid=r['candidate_id']
                    if not (0<len(cid)<16 and cid.isascii() and '\0' not in cid):
                        raise ValueError('unsupported native candidate identifier')
                    wid=r['window_id']
                    yield (r['satnum'],r['station_id'],r['start_s'],r['end_s'],r['points_int'],
                           wins.setdefault(wid,len(wins)),cid)
            try: packed=np.fromiter(records(),dtype=ROW,count=len(candidates))
            except (ValueError,OverflowError): packed=None
            cached_source=candidates
        if packed is None: return legacy[method](candidates,fixed,interrupted,clock)
        frozen,fragments=slots(fixed),slots(interrupted)
        selected=np.empty(len(candidates),dtype='<i4')
        errors=[]
        @CHECK
        def check():
            try: clock.check();return 0
            except Exception as e: errors.append(e);return 1
        clock.check()
        n=kernel(packed.ctypes.data,len(packed),frozen.ctypes.data,len(frozen),fragments.ctypes.data,len(fragments),
                 method,selected.ctypes.data,check)
        if errors: raise errors[0]
        if n==-2: return legacy[method](candidates,fixed,interrupted,clock)
        if n<0: raise RuntimeError(f'frozen native constructor returned {n}')
        result=[dict(r) for r in fixed]+[dict(candidates[i]) for i in selected[:n]]
        clock.check()
        return sorted(result,key=lambda r:(r['start_s'],r['station_id'],r['satnum']))
    def greedy(candidates,fixed,interrupted,clock):
        return select(candidates,fixed,interrupted,clock,0)
    def improved_construct(candidates,fixed,interrupted,clock):
        return select(candidates,fixed,interrupted,clock,1)
    scheduler.greedy=greedy
    scheduler.improved_construct=improved_construct

