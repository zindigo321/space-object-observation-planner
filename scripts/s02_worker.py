"""Internal S02 worker. Successful admission belongs to the guarded public CLI."""
import argparse
import os
from pathlib import Path
import sys
import traceback
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from planner.s02_input import identity, now, produce, write


def origins(out, phase, filename="origins.json"):
    files = {}
    for name, module in tuple(sys.modules.items()):
        if not (name.startswith('planner.') or name in ('s02_cli','__main__','numpy','sgp4','skyfield','yaml','jplephem','certifi')):
            continue
        file = getattr(module,'__file__',None)
        if file:
            path = Path(file).resolve()
            if (name.startswith('planner.') or name in ('s02_cli','__main__')) and not path.is_relative_to(ROOT):
                raise ValueError('S02 module outside product: '+str(path))
            files[name] = dict(path=str(path),**identity(path))
    write(out/filename,dict(phase=phase,utc=now(),interpreter=sys.executable,base=sys.base_prefix,
          prefix=sys.prefix,version=sys.version,package_root=str(ROOT),modules=files))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase',choices=['cold','initial','replan','solve','score','evaluate','recheck'])
    for key in ('input','initial','run','out'):
        p.add_argument('--'+key,type=Path,required=key=='out')
    p.add_argument('--method',choices=['baseline','improved'],required=True)
    p.add_argument('--seconds',type=float,required=True)
    p.add_argument('--deadline',type=float)
    a = p.parse_args()
    try:
        if a.phase == 'cold':
            produce(a.out/'input',a.seconds)
        elif a.phase in ('initial','replan'):
            from s02_cli import calculate_case
            code = calculate_case(a.phase,a.method,a.input,a.initial,a.out,a.deadline)
            if code:
                return code
        elif a.phase in ('solve','score'):
            from planner.s02_plan import solve, evaluate
            if a.phase == 'solve':
                solve(a.input,a.initial,a.method,a.out)
            else:
                evaluate(a.input,a.initial,a.run/'solve/raw.json',a.out)
        else:
            from s02_cli import replay
            replay(a.phase,a.input,a.run,a.out)
        # Execution provenance belongs beside evaluation files so replay can compare science independently.
        location = a.out.parent if a.phase == 'score' else a.out
        if a.phase == 'score':
            origins(location,'score','evaluation_origins.json')
        else:
            origins(location,a.phase)
        return 0
    except Exception as e:
        traceback.print_exc()
        a.out.mkdir(parents=True,exist_ok=True)
        write(a.out/'failure.json',dict(phase=a.phase,kind=type(e).__name__,reason=str(e),utc=now()))
        return 3 if isinstance(e,TimeoutError) else 2


if __name__=='__main__':
    raise SystemExit(main())
