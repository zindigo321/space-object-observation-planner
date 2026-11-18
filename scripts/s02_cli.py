"""Parent-owned S02 workflow, deadlines and sealed read-only replay."""
import json
import math
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from planner.no_fault_source import reject_links
from planner.path_safety import guard_writes
from planner.process_guard import run_guarded
from planner.s02_input import check_input, identity, now, platform_check, read, write

WORKER = ROOT/'scripts/s02_worker.py'
BUDGET = {'cold':1800,'initial':600,'replan':600,'evaluate':600,'recheck':600}
SEAL = 'evidence_manifest.json'


def worker_cmd(phase, out, *, input_dir=None, initial=None, run=None, method='baseline', seconds=600, deadline=None):
    argv = [sys.executable,'-B','-X','utf8',str(WORKER),phase,'--out',str(out),'--seconds',str(seconds),'--method',method]
    if deadline is not None:
        argv += ['--deadline',str(deadline)]
    for name, path in [('input',input_dir),('initial',initial),('run',run)]:
        if path is not None:
            argv.extend(['--'+name,str(path)])
    return argv


def snapshot(root):
    paths = [reject_links(p) for p in sorted(root.rglob('*'))]
    return {p.relative_to(root).as_posix():identity(p) for p in paths if p.is_file() and p != root/SEAL}


def verify_planning_run(run, input_dir):
    workflow = read(reject_links(run/'workflow.json'))
    if workflow['status'] != 'PASS' or workflow['action'] not in ('initial','replan'):
        raise ValueError('only completed successful S02 planning runs can enter evaluation')
    entries = read(reject_links(run/SEAL))['files']
    if snapshot(run) != entries:
        raise ValueError('S02 sealed run hash/member mismatch')
    case = read(run/'case.json')
    solve = case['solve']
    if (case['status'] != 'PASS' or solve['timed_out'] or solve['raw_exit_code'] != 0 or solve['exit_code'] != 0
            or solve['budget_seconds'] != 30 or solve['execution_seconds'] > 30
            or not solve['cleanup']['confirmed'] or solve['cleanup']['active_processes'] != 0
            or case['input_manifest'] != identity(input_dir/'INPUT_MANIFEST.json')):
        raise ValueError('S02 run is missing a clean admitted solve or its exact input')
    return entries


def calculate_case(action, method, input_dir, initial, out, deadline):
    from planner.no_fault_rules import validate_source
    from planner.s02_input import load
    case = dict(action=action,method=method,status='PREPARING',started_utc=now())
    start = time.monotonic()
    write(out/'case.json',case)
    # Protect the actual original bytes throughout the full case, including their history.
    if initial is not None:
        before = identity(initial)
        shutil.copyfile(initial,out/'initial.json')
        if identity(out/'initial.json') != before or identity(initial) != before:
            raise ValueError('S02 common initial changed while being copied')
        case['initial'] = before
        initial = out/'initial.json'
        _, _, candidates, context = load(input_dir)
        pool = validate_source(context,read(initial),candidates)
        del pool, candidates, context
    else:
        check_input(input_dir)
    case['input_manifest'] = identity(input_dir/'INPUT_MANIFEST.json')
    case['prepare_seconds'] = time.monotonic()-start
    if deadline-time.monotonic() < 31:
        case.update(status='TIMEOUT',reason='insufficient case budget for a full 30-second solver and cleanup')
        write(out/'case.json',case)
        return 3
    case['status'] = 'SOLVING'
    write(out/'case.json',case)
    solve = run_guarded(worker_cmd('solve',out/'solve',input_dir=input_dir,initial=initial,method=method,seconds=30),
                        timeout=30,log_path=out/'solve.log',cwd=ROOT)
    case['solve'] = dict(solve,budget_seconds=30)
    case['status'] = 'TIMEOUT' if solve['timed_out'] or solve['exit_code']==3 else 'FAIL'
    if solve['execution_seconds'] > 30 or solve['timed_out']:
        case['status'] = 'TIMEOUT'
        write(out/'case.json',case)
        return 3
    if solve['exit_code'] or not solve['cleanup']['confirmed'] or solve['cleanup']['active_processes']:
        write(out/'case.json',case)
        return solve['exit_code'] or 2
    native = read(out/'solve/native.json')
    expected = ['baseline'] if method=='baseline' else ['baseline','improved']
    if (native['status'] != 'PASS' or native['actual'] != native['expected']
            or [r['method'] for r in native['calls']] != expected
            or any(r['status'] != 'RETURNED' or r['return_code'] < 0 for r in native['calls'])):
        raise ValueError('S02 native calls did not complete')
    case['status'] = 'EVALUATING'
    write(out/'case.json',case)
    # Score in a fresh interpreter that opens the original raw TLE, never in the solver.
    ev = run_guarded(worker_cmd('score',out/'evaluation',input_dir=input_dir,initial=initial,run=out),
                     timeout=600,deadline_monotonic=deadline-0.5,log_path=out/'evaluate.log',cwd=ROOT)
    case['evaluation'] = ev
    if ev['exit_code'] or ev['timed_out'] or not ev['cleanup']['confirmed'] or ev['cleanup']['active_processes']:
        case['status'] = 'TIMEOUT' if ev['timed_out'] or ev['exit_code']==3 else 'FAIL'
        write(out/'case.json',case)
        return ev['exit_code'] or 2
    case.update(status='PASS',finished_utc=now(),evaluation_result=read(out/'evaluation/evaluation.json'),
                native=dict(backend=native['backend'],dll=native['actual'],calls=native['calls']))
    write(out/'case.json',case)
    return 0


def replay(action, input_dir, run, out):
    from planner.s02_plan import evaluate
    before = verify_planning_run(run,input_dir)
    initial = run/'initial.json' if (run/'initial.json').is_file() else None
    evaluate(input_dir,initial,run/'solve/raw.json',out/'evaluation')
    current = read(out/'evaluation/evaluation.json')
    original = run/'evaluation'
    if snapshot(out/'evaluation') != snapshot(original):
        raise ValueError('S02 fresh evaluation or exact selected output differs from the sealed run')
    if snapshot(run) != before:
        raise ValueError('S02 sealed source changed during read-only replay')
    write(out/'replay.json',dict(status='PASS',action=action,solver_calls=0,source_unchanged=True,
          checked_evaluation_files=len(snapshot(original)),source_manifest=identity(run/SEAL),result=current))


def dispatch(a):
    start = time.monotonic()
    platform_check()
    if a.action not in BUDGET:
        raise ValueError('S02 requires --action cold, initial, replan, evaluate or recheck')
    action = a.action
    limit = BUDGET[action] if a.budget_seconds is None else a.budget_seconds
    if not math.isfinite(limit) or not 0 < limit <= BUDGET[action]:
        raise ValueError(f'S02 {action} budget must be in (0,{BUDGET[action]}] seconds')
    supplied = {key for key in ('input','initial','run') if getattr(a,key)}
    required = {'cold':set(),'initial':{'input'},'replan':{'input','initial'},
                'evaluate':{'input','run'},'recheck':{'input','run'}}[action]
    if required != supplied:
        raise ValueError(f'S02 {action} requires exactly these input options: {sorted(required)}')
    args = {k:reject_links(getattr(a,k)).resolve() if k in supplied else None for k in ('input','initial','run')}
    out = reject_links(a.out).resolve()
    guard_writes([out],[ROOT,*(p for p in args.values() if p)])
    out.mkdir(parents=True,exist_ok=False)
    started = now()
    argv = worker_cmd(action,out,input_dir=args['input'],initial=args['initial'],run=args['run'],method=a.method,seconds=limit,deadline=start+limit)
    receipt = run_guarded(argv,timeout=limit,deadline_monotonic=start+limit,log_path=out/'workflow.log',cwd=ROOT)
    code = receipt['exit_code']
    status = 'TIMEOUT' if receipt['timed_out'] or code==3 else ('FAIL' if code else 'PASS')
    origin = read(ROOT/'SOURCE_IDENTITY.json')
    workflow = dict(status=status,case='S02',action=action,method=a.method,source_commit=origin['source_commit'],
                    started_utc=started,finished_utc=now(),wall_seconds=time.monotonic()-start,budget_seconds=limit,
                    guard=receipt,command=sys.argv,package_root=str(ROOT))
    write(out/'workflow.json',workflow)
    if status == 'PASS':
        write(out/SEAL,dict(schema='FAMOU_S02_RUN_V1',files=snapshot(out)))
    print(json.dumps(dict(status=status,action=action,receipt=str(out/'workflow.json')),ensure_ascii=False))
    return code
