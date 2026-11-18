"""Historical-only calibration, serialized-target equivalence and native selector comparison."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from expansion_worker import read,write,append,rows,manifest,Clock,ident

def historical(a):
    from planner.no_fault_source import load_source
    source=Path(a.source);out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    loaded=load_source(source/'H180_BASE',ident(source/'H180_BASE/source_manifest.json')['sha256'])
    geo=read(source/'geometry/model.json'); records=geo['records']; stations=geo['stations']
    spec=dict(unit_id='H180_DEV',selected={p:[r['satnum'] for r in records if r['priority']==p] for p in ('high','medium','low')},
        target_count=180,station_ids=list(range(1,11)),start_utc='2026-08-05T00:00:00Z',horizon_seconds=86400)
    config=dict(horizon_seconds=86400,station_ids=list(range(1,11)),coarse_step_seconds=30,fine_step_seconds=1,
        candidate_start_step_seconds=30,max_starts_per_window_duration=12,durations_seconds=[120,240],switch_seconds=30,elevation_degrees=[10,85])
    write(out/'meta.json',dict(schema='EXPANSION_SHARED_INPUT_V1',spec=spec,records=records,stations=stations,config=config,
        cold_production=False,origin='accepted historical H180 frozen pool',origin_manifest=ident(source/'H180_BASE/source_manifest.json')))
    append(out/'windows.jsonl.gz',loaded['context']['windows'].values());append(out/'candidates.jsonl.gz',loaded['candidates'])
    write(out/'progress.json',dict(status='PASS',targets_completed=180,targets_planned=180,windows=len(loaded['context']['windows']),
        candidates=len(loaded['candidates']),cold_production=False))
    write(out/'INPUT_MANIFEST.json',dict(status='COMPLETE',files=manifest(out)))
    records_dev=[records[0],next(r for r in records if float(r['line2'][52:63])<2),records[-1]]
    devspec=dict(unit_id='H180_3TARGET_6DAY_DEV',selected={p:[r['satnum'] for r in records_dev if r['priority']==p] for p in ('high','medium','low')},
        target_count=3,station_ids=list(range(1,11)),start_utc='2026-07-31T00:00:00Z',horizon_seconds=518400)
    write(Path(a.spec),devspec);print(json.dumps(dict(status='PASS',historical_targets=180,development_ids=[r['satnum'] for r in records_dev])),flush=True)

def equivalence(a):
    from datetime import datetime
    from planner.tle_adapter import Geometry,build_windows
    from planner.scheduler import make_candidates
    inp=Path(a.source);out=Path(a.out);out.mkdir(parents=True,exist_ok=False);meta=read(inp/'meta.json')
    day=datetime.fromisoformat(meta['spec']['start_utc'].replace('Z','+00:00'));clock=Clock(240)
    t=time.perf_counter();geometry=Geometry(meta['records'],meta['stations'],day,clock)
    windows=build_windows(geometry,meta['records'],meta['stations'],meta['config'],out,clock)
    candidates=make_candidates(windows,meta['records'],meta['config'],day,out,clock)
    streamed_windows=rows(inp/'windows.jsonl.gz');streamed_candidates=rows(inp/'candidates.jsonl.gz')
    result=dict(windows_exact=windows==streamed_windows,candidates_exact=candidates==streamed_candidates,
        windows=len(windows),candidates=len(candidates),whole_horizon_seconds=meta['config']['horizon_seconds'],stations=10,
        targets=len(meta['records']),stream_chunk='one target, whole 6 days; no time boundary split',
        temporal_chunking_used=False,seconds=time.perf_counter()-t)
    result['status']='PASS' if result['windows_exact'] and result['candidates_exact'] else 'FAIL'
    write(out/'EQUIVALENCE.json',result);print(json.dumps(result),flush=True)
    assert result['status']=='PASS'

def native_compare(a):
    from planner.no_fault import choose_from_files
    source=Path(a.source);cal=Path(a.calibration);out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    comparisons=[]
    for origin,label in [('baseline','H180_BASE'),('improved','H180_IMP')]:
        initial=read(cal/f'H180_DEV_INIT_{origin}_a01/evaluate/selected.json')
        from planner.no_fault_source import load_source
        rawsource=load_source(source/label,ident(source/label/'source_manifest.json')['sha256'])
        initial_equal=initial==rawsource['initial']
        for method in ('baseline','improved'):
            case=cal/f'H180_DEV_{origin}_C_{method}_a01'
            proposal=read(case/'solve/raw.json')
            selected,receipt=choose_from_files(source/label,ident(source/label/'source_manifest.json')['sha256'],3600,proposal)
            adapter=read(case/'evaluate/branch.json')
            comparisons.append(dict(origin=origin,method=method,initial_equal=initial_equal,
                selected_equal=selected==read(case/'evaluate/selected.json'),branch_equal=receipt['branch']==adapter['branch'],
                J_selected_equal=receipt['J_selected']==adapter['J_selected']))
    result=dict(status='PASS' if all(all(v for k,v in r.items() if k.endswith('equal')) for r in comparisons) else 'FAIL',comparisons=comparisons)
    write(out/'NATIVE_EQUIVALENCE.json',result);print(json.dumps(result),flush=True);assert result['status']=='PASS'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['historical','equivalence','native_compare'])
    for name in ('source','out','spec','calibration'):p.add_argument('--'+name)
    a=p.parse_args();globals()[a.mode](a)
