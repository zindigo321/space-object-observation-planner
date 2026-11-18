"""Read-only source inventory and prospective instance registry; never solve a case."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, os, shutil, statistics, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

def ident(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return {'bytes': Path(path).stat().st_size, 'sha256': h.hexdigest()}

def csvout(path, rows, fields):
    with Path(path).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)

class InventoryClock:
    def __init__(self, seconds=120): self.deadline = time.monotonic() + seconds
    def check(self, *args):
        if time.monotonic() > self.deadline: raise TimeoutError('inventory deadline')
    def log(self, message): pass

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw', required=True); p.add_argument('--out', required=True)
    p.add_argument('--history-root', action='append', default=[])
    a = p.parse_args(); raw = Path(a.raw); out = Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    protected_before = {q.name: ident(q) for q in raw.iterdir() if q.is_file()}
    copied = out / 'raw'; copied.mkdir()
    for q in raw.iterdir():
        if q.is_file(): shutil.copyfile(q, copied / q.name)
    audit = out / 'parsed'; audit.mkdir()
    config = dict(input_dir=str(copied.resolve()), frozen_sample=str((out/'population_parse_order.json').resolve()),
        seed=42, sample_counts=dict(high=2024, medium=3990, low=3986), station_ids=list(range(1,11)),
        start_utc='2026-07-31T00:00:00Z', horizon_seconds=518400)
    from planner.tle_adapter import read_and_audit
    records, stations, day, sample, checked = read_and_audit(config, audit, InventoryClock())
    records.sort(key=lambda r:r['satnum'])
    epochs = [r['epoch_timestamp'] for r in records]
    summary = dict(checked, inventory_only=True, scientific_cases_executed=0,
        epoch_min_utc=datetime.fromtimestamp(min(epochs),timezone.utc).isoformat(),
        epoch_max_utc=datetime.fromtimestamp(max(epochs),timezone.utc).isoformat(),
        epoch_median_utc=datetime.fromtimestamp(statistics.median(epochs),timezone.utc).isoformat(),
        epoch_check_scope='inherited parser SGP4 at individual TLE epoch; no observation-window production',
        geometry_at_experiment_times='NOT_RUN', raw_input_protection=protected_before == {q.name:ident(q) for q in raw.iterdir() if q.is_file()})
    write(out/'RAW_INVENTORY.json', summary)
    write(out/'RAW_PARSE_ERRORS.json', {'parser_errors':[], 'epoch_propagation_errors':checked['epoch_propagation_errors']})
    csvout(out/'RAW_FILES.csv', [dict(name=k,**v) for k,v in protected_before.items()], ['name','bytes','sha256'])
    # All population IDs remain denominators, including any future no-window targets.
    start=day.timestamp(); end=start+518400
    csvout(out/'POPULATION.csv', [dict(satnum=r['satnum'], priority=r['priority'], full_score=r['full_score'],
        epoch_utc=r['epoch_utc'], age_days_at_start=(start-r['epoch_timestamp'])/86400,
        age_days_at_end=(end-r['epoch_timestamp'])/86400, experiment_propagation_status='NOT_RUN') for r in records],
        ['satnum','priority','full_score','epoch_utc','age_days_at_start','age_days_at_end','experiment_propagation_status'])
    # Discover actual selected-ID artifacts. Duplicate bytes are parsed only once.
    # Never claim the absence of files proves the absence of previous exposure.
    names={'frozen_sample.json','selected_tle.json','sample.csv','targets.csv'}
    skip={'.git','node_modules','site-packages','__pycache__','.venv','venv','.conda','Lib','Scripts','wheelhouse','test_wheelhouse'}
    population={r['satnum'] for r in records}; seen={}; excluded=set(); sources=[]; errors=[]; snapshots=[]
    deadline=time.monotonic()+120; truncated=False; visited=0
    raw_tle=ident(copied/'轨道.txt')
    for scanroot in a.history_root:
        for base, dirs, files in os.walk(scanroot, followlinks=False):
            visited+=1
            dirs[:]=[d for d in dirs if d not in skip and not d.startswith('expansion_') and not d.startswith('bd-fmb_expansion_')
                     and not (Path(base)/d).is_symlink()]
            if time.monotonic()>deadline:
                truncated=True; break
            for name in files:
                path=Path(base)/name
                try:
                    if name=='轨道.txt' or path.suffix.lower() in {'.tle','.tles'}:
                        identity=ident(path)
                        snapshots.append(dict(path=str(path),**identity,relation_to_supplied_raw='identical_bytes' if identity==raw_tle else 'unclassified_requires_source_review'))
                    if name not in names: continue
                    size=path.stat().st_size
                    if size>32*1024*1024:
                        errors.append(dict(path=str(path),error='selected-ID artifact over 32MiB; not read')); continue
                    identity=ident(path); digest=identity['sha256']
                    if digest in seen:
                        ids=seen[digest]
                    else:
                        if path.suffix=='.csv':
                            with path.open(encoding='utf-8-sig',newline='') as f:
                                rows=list(csv.DictReader(f))
                            ids={int(r.get('satnum',r.get('target_id',r.get('id','-1')))) for r in rows}
                        else:
                            data=json.loads(path.read_text(encoding='utf-8-sig'))
                            if isinstance(data,dict) and isinstance(data.get('selected'),dict):
                                ids={int(n) for group in data['selected'].values() for n in group}
                            elif isinstance(data,list):
                                ids={int(r.get('satnum',r.get('target_id',-1))) for r in data if isinstance(r,dict)}
                            else:
                                raise ValueError('unrecognized selected-ID schema')
                        ids=sorted(ids & population); seen[digest]=ids
                    excluded.update(ids)
                    sources.append(dict(path=str(path),**identity,matched_population_ids=len(ids)))
                except Exception as e: errors.append(dict(path=str(path),error=type(e).__name__+': '+str(e)))
        if truncated: break
    write(out/'HISTORY_EXPOSURE.json', dict(scope_roots=a.history_root,visited_directories=visited,
        scan_time_cap_seconds=120,scan_truncated=truncated,excluded_ids=sorted(excluded),unique_excluded_count=len(excluded),
        sources=sources,unique_content_ids=seen,errors=errors,history_completeness='NOT_PROVEN',
        limitations=['Only recognized selected-ID artifacts were parsed.','Archives not extracted; deleted, inaccessible and unrecognized historical artifacts may be missing.',
                    'Membership in source inputs is conservatively treated as historical exposure, even if no solve is proved.']))
    write(out/'TLE_SNAPSHOT_CATALOG.json',dict(snapshots=snapshots,
        independent_external_validation_set='NOT_ESTABLISHED',
        conclusion='Identical bytes and changed observation dates do not establish an independent TLE source. Different bytes require provenance review.'))
    seed='bd-fmb-expansion-round1-20261117-v1'
    def order(ids,tag): return sorted(ids,key=lambda n:(hashlib.sha256(f'{seed}|{tag}|{n}'.encode()).hexdigest(),n))
    bypriority={p:[r['satnum'] for r in records if r['priority']==p] for p in ('high','medium','low')}
    ordered={p:order(v,'A|'+p) for p,v in bypriority.items()}
    units=[]
    for label,quota,hours in [('S01',(122,239,239),24),('S02',(364,718,718),24),('S03',(1012,1995,1993),24),
                              ('S04',(2024,3990,3986),24),('S05',(2024,3990,3986),72),('S06',(2024,3990,3986),144)]:
        ids={p:ordered[p][:q] for p,q in zip(bypriority,quota)}
        units.append(dict(unit_id=label,line='A',selected=ids,target_count=sum(quota),station_ids=list(range(1,11)),
            start_utc='2026-07-31T00:00:00Z',horizon_seconds=hours*3600))
    remaining={p:order(set(v)-excluded,'B|'+p) for p,v in bypriority.items()}
    capacity=min(len(v)//60 for v in remaining.values())
    for block in range(12):
        ids={p:v[block*60:(block+1)*60] for p,v in remaining.items()}
        units.append(dict(unit_id=f'B{block+1:03d}',line='B',selected=ids,target_count=sum(map(len,ids.values())),
            requested_target_count=180,selection_status='PROSPECTIVE' if all(len(v)==60 for v in ids.values()) else 'INSUFFICIENT_POOL_REQUIRES_DESIGN_REVISION',
            station_ids=list(range(1,11)),start_utc='2026-08-05T00:00:00Z',horizon_seconds=86400))
    sequence=['S01','B001','S02','S03','S04','S05','S06']+[f'B{n:03d}' for n in range(2,13)]
    units.sort(key=lambda u:sequence.index(u['unit_id']))
    for unit in units:
        unit['instance_sha256']=hashlib.sha256(json.dumps(unit,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    write(out/'PROSPECTIVE_INSTANCES.json',dict(status='DRAFT_NOT_FROZEN',selection_seed=seed,
        historical_exclusion_sha256=ident(out/'HISTORY_EXPOSURE.json')['sha256'],B_capacity_blocks=capacity,
        history_completeness='NOT_PROVEN',units=units))
    print(json.dumps(dict(tle_count=len(records),excluded=len(excluded),B_capacity_blocks=capacity,history_sources=len(sources),
        history_scan_truncated=truncated,raw_protected=summary['raw_input_protection']),ensure_ascii=False))
    return 0

if __name__=='__main__': raise SystemExit(main())
