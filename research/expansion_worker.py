"""Fixed expansion stages. Scheduling/geometry/rules remain inherited product code."""
import argparse, csv, gzip, hashlib, json, os, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from expansion_inventory import ident

def write(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');os.replace(tmp,p)

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def utc(): return datetime.now(timezone.utc).isoformat()
def rows(p):
    with gzip.open(p,'rt',encoding='utf-8') as f: return [json.loads(line) for line in f if line.strip()]
def append(p,values):
    data=''.join(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n' for v in values).encode()
    with Path(p).open('ab') as f: f.write(gzip.compress(data,compresslevel=3,mtime=0))
def manifest(root): return {p.name:ident(p) for p in sorted(root.iterdir()) if p.is_file() and p.name!='INPUT_MANIFEST.json'}
def check_input(root):
    m=read(root/'INPUT_MANIFEST.json')
    for name,value in m['files'].items():
        if ident(root/name)!=value: raise ValueError('frozen input hash mismatch: '+name)
    return m

class Clock:
    def __init__(self,seconds=1800): self.deadline=time.monotonic()+seconds
    def check(self,*a):
        from planner.common import BudgetExpired
        if time.monotonic()>self.deadline: raise BudgetExpired('research stage cooperative deadline')
    def log(self,message): pass

def produce(a):
    from planner.tle_adapter import build_windows
    from axis_cache import CachedGeometry
    from planner.scheduler import make_candidates
    spec=read(a.spec); inventory=Path(a.inventory); out=Path(a.out); out.mkdir(parents=True,exist_ok=False)
    all_records=read(inventory/'parsed/selected_tle.json'); numbers=[n for group in spec['selected'].values() for n in group]
    byid={r['satnum']:r for r in all_records}; records=[byid[n] for n in numbers]
    with (inventory/'parsed/stations.csv').open(encoding='utf-8-sig',newline='') as f: stations=list(csv.DictReader(f))
    for s in stations:
        s['station_id']=int(s['station_id'])
        for k in ('longitude_original','longitude','latitude','height_m'): s[k]=float(s[k])
    config=dict(horizon_seconds=spec['horizon_seconds'],station_ids=spec['station_ids'],coarse_step_seconds=30,
        fine_step_seconds=1,candidate_start_step_seconds=30,max_starts_per_window_duration=12,
        durations_seconds=[120,240],switch_seconds=30,elevation_degrees=[10,85])
    day=datetime.fromisoformat(spec['start_utc'].replace('Z','+00:00'))
    meta=dict(schema='EXPANSION_SHARED_INPUT_V1',spec=spec,records=records,stations=stations,config=config,
        raw_files_sha256=ident(inventory/'RAW_FILES.csv')['sha256'],source_files={str(p.relative_to(ROOT)):ident(p) for p in
        [ROOT/'planner/tle_adapter.py',ROOT/'planner/scheduler.py',Path(__file__)]},cold_production=True,
        chunking='one target, all 10 stations, entire horizon; no temporal chunk and no per-day solve',
        candidate_rule='inherited make_candidates, global sequential IDs restored after target partition',started_utc=utc())
    write(out/'meta.json',meta); tmp=out/'scratch';tmp.mkdir(); clock=Clock(a.seconds-2)
    geo=CachedGeometry(records,stations,day,clock,config['horizon_seconds'],config['coarse_step_seconds'])
    wc=cc=rawc=errors=0; executable=set(); start=time.perf_counter(); geometry_s=candidate_s=0
    for index,r in enumerate(records):
        t=time.perf_counter(); batch=build_windows(geo,[r],stations,config,tmp,clock); geometry_s+=time.perf_counter()-t
        for i,w in enumerate(batch): w['window_id']=f'W{wc+i+1:05d}'
        t=time.perf_counter(); cand=make_candidates(batch,[r],config,day,tmp,clock); candidate_s+=time.perf_counter()-t
        for i,c in enumerate(cand): c['task_id']=c['candidate_id']=f'C{cc+i+1:06d}'
        pruning=read(tmp/'candidate_pruning.json'); rawc+=pruning['raw_grid_candidates']; wc+=len(batch);cc+=len(cand)
        executable.update(c['satnum'] for c in cand); errors+=len(geo.errors)
        append(out/'windows.jsonl.gz',batch);append(out/'candidates.jsonl.gz',cand)
        append(out/'pruning.jsonl.gz',pruning['per_window_duration']);append(out/'propagation_errors.jsonl.gz',geo.errors)
        append(out/'target_progress.jsonl.gz',[dict(satnum=r['satnum'],target_index=index+1,windows=len(batch),
            candidates=len(cand),propagation_errors=len(geo.errors),elapsed_s=time.perf_counter()-start)])
        geo.errors.clear()
        write(out/'progress.json',dict(targets_completed=index+1,targets_planned=len(records),windows=wc,candidates=cc,
            raw_grid_candidates=rawc,pruned=rawc-cc,executable_targets=len(executable),propagation_errors=errors,
            geometry_s=geometry_s,candidate_generation_s=candidate_s,wall_s=time.perf_counter()-start,status='BUILDING'))
        if (index+1)%10==0: print(json.dumps(read(out/'progress.json')),flush=True)
    # Scratch contains only the last target's redundant serialization, not scientific evidence.
    import shutil
    assert tmp.resolve().parent==out.resolve() and tmp.name=='scratch'
    shutil.rmtree(tmp)
    summary=read(out/'progress.json');summary.update(status='PASS',all_target_ids=numbers,executable_ids=sorted(executable),
        finished_utc=utc(),total_wall_s=time.perf_counter()-start)
    write(out/'progress.json',summary)
    write(out/'INPUT_MANIFEST.json',dict(status='COMPLETE',files=manifest(out)))
    print(json.dumps(summary|{'all_target_ids':'stored_in_progress','executable_ids':'stored_in_progress'}),flush=True)

def load(a):
    from candidate_io import read_candidates
    root=Path(a.input);check_input(root);meta=read(root/'meta.json')
    windows=rows(root/'windows.jsonl.gz');candidates=read_candidates(root/'candidates.jsonl.gz')
    day=datetime.fromisoformat(meta['spec']['start_utc'].replace('Z','+00:00'))
    context=dict(day=day,horizon=meta['config']['horizon_seconds'],priorities={r['satnum']:r['priority'] for r in meta['records']},
        stations=set(meta['config']['station_ids']),windows={w['window_id']:w for w in windows})
    initial=read(a.initial) if a.initial else []
    return meta,windows,candidates,day,context,initial

def history(initial,candidates,day,scene):
    from planner.no_fault_rules import status_at
    from planner.scheduler import replay_state,future_candidates
    if scene=='I': return [],[],[],candidates,None,{}
    if scene=='C':
        retained=[dict(r,status=status_at(r,3600)) for r in initial]
        fixed=[r for r in retained if r['status']=='completed']+[r for r in retained if r['status']=='locked']
        ids={r['satnum'] for r in fixed}
        future=[dict(r,status='new_success') for r in candidates if r['start_s']>=3600 and r['satnum'] not in ids]
        return retained,fixed,[],future,None,{}
    event=dict(station_id=1,start_s=3600,end_s=10800)
    completed,locked,interrupted,cancelled=replay_state(initial,event,day)
    fixed=completed+locked;future=future_candidates(candidates,fixed,event)
    retained=fixed+future_candidates(initial,fixed,event)
    return retained,fixed,interrupted,future,event,dict(completed=completed,locked=locked,interrupted=interrupted,cancelled_future=cancelled)

def validator(meta,windows,day,inventory,clock):
    from planner.validator import IndependentValidator
    sample=dict(selected={p:[r['satnum'] for r in meta['records'] if r['priority']==p] for p in ('high','medium','low')})
    return IndependentValidator(dict(meta['config'],input_dir=str(Path(inventory)/'raw')),day,sample,windows,clock)

def evaluate_rows(v,rows_,scene,interrupted,event,initial,label):
    if scene=='F': return v.check(rows_,interrupted,event,original_plan=initial,label=label)
    return v.check([dict(r,status='success') for r in rows_],label=label)

def prepare(a):
    from planner.no_fault_rules import validate_source
    out=Path(a.out);out.mkdir(parents=True,exist_ok=False);t0=time.perf_counter()
    meta,windows,candidates,day,context,initial=load(a)
    validate_source(context,initial,candidates)
    retained,fixed,interrupted,future,event,h=history(initial,candidates,day,a.scene)
    clock=Clock(a.seconds-2); v=validator(meta,windows,day,a.inventory,clock)
    t1=time.perf_counter(); initial_check=v.check(initial,label='initial_authority') if initial else None
    retained_check=evaluate_rows(v,retained,a.scene,interrupted,event,initial,'retained')
    if initial_check and initial_check['status']!='PASS': raise ValueError('initial plan independent validation failed')
    if retained_check['status']!='PASS': raise ValueError('retained independent validation failed')
    write(out/'history.json',dict(retained=retained,fixed=fixed,interrupted=interrupted,event=event,fault_history=h,
        future_count=len(future),scene=a.scene,initial_file_sha256=ident(a.initial)['sha256'] if a.initial else None))
    write(out/'initial_check.json',initial_check);write(out/'retained_check.json',retained_check)
    write(out/'preparation.json',dict(status='PASS',all_denominator=len(meta['records']),executable_denominator=len({r['satnum'] for r in candidates}),
        windows=len(windows),candidates=len(candidates),future_count=len(future),load_and_rule_validation_s=t1-t0,
        independent_geometry_s=time.perf_counter()-t1,total_s=time.perf_counter()-t0,
        input_manifest_sha256=ident(Path(a.input)/'INPUT_MANIFEST.json')['sha256']))

def configure_scheduler():
    from planner import scheduler
    if not getattr(scheduler,'_research_native',False):
        from fast_scheduler import install
        install(scheduler)
        scheduler._research_native=True

def solve(a):
    # Entire interpreter, imports, input load, candidate code and output are inside parent solve30.
    from planner import scheduler
    from planner.common import TASK_FIELDS,csv_write
    configure_scheduler()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    t0=time.perf_counter();meta,windows,candidates,day,context,initial=load(a)
    retained,fixed,interrupted,future,event,h=history(initial,candidates,day,a.scene)
    instrument=out/'calls.jsonl';calls=[];baseline_rows=None;alternative_rows=None
    def emit(value):
        calls.append(value)
        with instrument.open('a',encoding='utf-8') as f:f.write(json.dumps(value)+'\n');f.flush()
    def wrap(name,fn):
        def run(*args,**kwargs):
            nonlocal baseline_rows,alternative_rows
            emit(dict(function=name,event='start',elapsed_s=time.perf_counter()-t0));t=time.perf_counter()
            result=fn(*args,**kwargs)
            if name=='greedy':baseline_rows=result
            if name=='improved_construct':alternative_rows=result
            emit(dict(function=name,event='return',elapsed_s=time.perf_counter()-t0,seconds=time.perf_counter()-t))
            return result
        return run
    scheduler.greedy=wrap('greedy',scheduler.greedy);scheduler.improved_construct=wrap('improved_construct',scheduler.improved_construct)
    clock=Clock(29);emit(dict(function='schedule',event='start',elapsed_s=time.perf_counter()-t0));ts=time.perf_counter()
    proposal=scheduler.schedule(future,a.method,fixed=fixed,interrupted=interrupted,clock=clock)
    emit(dict(function='schedule',event='return',elapsed_s=time.perf_counter()-t0,seconds=time.perf_counter()-ts))
    write(out/'raw.json',proposal);csv_write(out/'raw.csv',proposal,TASK_FIELDS)
    write(out/'solve.json',dict(status='RETURNED',method=a.method,load_and_history_s=ts-t0,schedule_s=time.perf_counter()-ts,
        calls=calls,top_level_schedule_calls=1,internal_baseline_calls=1,improved_construct_calls=int(a.method=='improved'),
        improved_returned_internal_baseline=(a.method=='improved' and proposal==baseline_rows and proposal!=alternative_rows),
        total_worker_s=time.perf_counter()-t0))

def evaluate(a):
    from planner.no_fault_rules import native_report,validate_source,member
    from planner import no_fault
    from planner.common import TASK_FIELDS,csv_write
    out=Path(a.out);out.mkdir(parents=True,exist_ok=False);t0=time.perf_counter()
    meta,windows,candidates,day,context,initial=load(a);proposal=read(a.proposal)
    retained,fixed,interrupted,future,event,h=history(initial,candidates,day,a.scene)
    pool=validate_source(context,initial,candidates)
    # Independent membership always refers to the original frozen pool, not filtered worker state.
    if any(not member(r,pool) for r in proposal):raise ValueError('proposal is not in frozen original candidate pool')
    v=validator(meta,windows,day,a.inventory,Clock(a.seconds-2));tg=time.perf_counter()
    raw_report=evaluate_rows(v,proposal,a.scene,interrupted,event,initial,'raw')
    write(out/'raw_evaluation.json',raw_report)
    if raw_report['status']!='PASS':raise ValueError('ILLEGAL_OUTPUT: raw independent evaluation failed')
    retained_report=evaluate_rows(v,retained,a.scene,interrupted,event,initial,'retained')
    write(out/'retained_evaluation.json',retained_report)
    if retained_report['status']!='PASS':raise ValueError('retained independent evaluation failed')
    if a.scene=='C':
        source=dict(context=context,initial=initial,candidates=candidates)
        original_loader=no_fault.load_source
        expected=ident(Path(a.input)/'INPUT_MANIFEST.json')['sha256']
        def sealed_adapter(directory,hash_):
            if Path(directory)!=Path(a.input) or hash_!=expected:raise ValueError('compressed source adapter identity mismatch')
            check_input(Path(directory));return source
        no_fault.load_source=sealed_adapter
        try:selected,branch=no_fault.choose_from_files(a.input,expected,3600,proposal)
        finally:no_fault.load_source=original_loader
        native=native_report(context,initial,candidates,3600,selected,True)
        write(out/'native_selected_check.json',native)
    else:
        selected=proposal
        branch=dict(branch='LEGACY_FAULT_RAW_NO_NATIVE_GUARD' if a.scene=='F' else 'INITIAL_RAW',
            selected_source='raw_proposal',physical_changes=no_fault.changes(initial,selected))
    selected_report=evaluate_rows(v,selected,a.scene,interrupted,event,initial,'selected') if selected!=proposal else dict(raw_report,label='selected')
    if selected_report['status']!='PASS':raise ValueError('selected independent validation failed')
    write(out/'selected_evaluation.json',selected_report);write(out/'selected.json',selected);csv_write(out/'selected.csv',selected,TASK_FIELDS)
    write(out/'interrupted.json',interrupted);write(out/'branch.json',branch)
    def J(r):return [r['points_int'],r['coverage']]
    summary=dict(status='PASS',scene=a.scene,method=a.method,all_denominator=len(meta['records']),
        executable_denominator=len({c['satnum'] for c in candidates}),J_raw=J(raw_report),J_retained=J(retained_report),J_selected=J(selected_report),
        raw_minus_retained_points=raw_report['points_int']-retained_report['points_int'],branch=branch['branch'],
        physical_changes=branch.get('physical_changes'),coverage_by_priority=selected_report['by_priority_coverage'],
        priority_points={p:sum({'high':5,'medium':3,'low':2}[p]*(3 if r['duration_s']==120 else 5) for r in selected if r['priority']==p) for p in ('high','medium','low')},
        legality='PASS',geometry='raw_TLE_per_second_PASS',interrupted_count=len(interrupted),
        independent_geometry_and_selection_s=time.perf_counter()-tg,total_evaluation_s=time.perf_counter()-t0,
        C_selection_adapter='original choose_from_files with independently hash-checked compressed source loader' if a.scene=='C' else None,
        F_selection_semantics='inherited legacy raw output; legal retained is a comparison, not a guard' if a.scene=='F' else None)
    write(out/'evaluation.json',summary);print(json.dumps(summary),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=['produce','prepare','solve','evaluate'])
    for key in ('spec','inventory','input','initial','proposal','out'):p.add_argument('--'+key)
    p.add_argument('--scene',choices=['I','C','F'],default='I');p.add_argument('--method',choices=['baseline','improved'],default='baseline')
    p.add_argument('--seconds',type=float,default=1800);a=p.parse_args()
    try:globals()[a.phase](a);return 0
    except Exception as e:
        traceback.print_exc()
        if a.out and Path(a.out).exists():write(Path(a.out)/'worker_failure.json',dict(type=type(e).__name__,message=str(e),phase=a.phase,time_utc=utc()))
        return 3 if type(e).__name__ in ('BudgetExpired','TimeoutError') else 1
if __name__=='__main__':raise SystemExit(main())
