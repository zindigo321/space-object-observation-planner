"""Frozen S02 authority and lossless, ordered compressed product input."""
import ctypes
import gzip
import hashlib
import json
import platform
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from .no_fault_source import reject_links

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'S02'
RAW = DATA / 'raw'
STREAMS = ('windows', 'candidates', 'pruning', 'propagation_errors')
MEMBERS = {'meta.json', 'progress.json', 'target_progress.jsonl.gz', *(n+'.jsonl.gz' for n in STREAMS)}


def platform_check():
    if (sys.platform != 'win32' or platform.machine().upper() not in ('AMD64','X86_64')
            or ctypes.sizeof(ctypes.c_void_p) != 8 or sys.implementation.name != 'cpython'
            or sys.version_info[:2] != (3,11)):
        raise ValueError('S02 requires Windows x64 and 64-bit CPython 3.11')


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    from .common import json_write
    json_write(path, value)


def identity(path):
    path = reject_links(path)
    with path.open('rb') as f:
        return dict(bytes=path.stat().st_size, sha256=hashlib.file_digest(f, 'sha256').hexdigest())


def canonical(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


class StageClock:
    """Cooperative geometry/kernel checks supplement the outer process deadline."""
    def __init__(self, seconds):
        self.deadline = time.monotonic() + seconds

    def check(self, reserve=0):
        if time.monotonic() + reserve >= self.deadline:
            raise TimeoutError('S02 stage deadline')

    def log(self, message):
        pass


def authority():
    contract = read(ROOT/'configs/s02_contract.json')
    if identity(DATA/'spec.json') != contract['spec']:
        raise ValueError('S02 frozen instance file hash mismatch')
    spec = read(DATA/'spec.json')
    if canonical({k:v for k,v in spec.items() if k != 'instance_sha256'}) != contract['instance_sha256']:
        raise ValueError('S02 frozen instance digest mismatch')
    if {p.name for p in RAW.iterdir()} != set(contract['raw']):
        raise ValueError('S02 raw inventory member set differs')
    for name, expected in contract['raw'].items():
        if identity(RAW/name) != expected:
            raise ValueError('S02 raw input hash mismatch: '+name)
    return contract, spec


def append_stream(path, rows):
    data = ''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n' for r in rows)
    with path.open('ab') as f:
        f.write(gzip.compress(data.encode(), compresslevel=3, mtime=0))


def read_rows(path):
    with gzip.open(path, 'rb') as f:
        return [json.loads(line) for line in f if line.strip()]


def check_input(path):
    root = reject_links(path)
    contract, spec = authority()
    manifest = read(reject_links(root/'INPUT_MANIFEST.json'))
    if manifest['status'] != 'COMPLETE' or set(manifest['files']) != MEMBERS:
        raise ValueError('S02 incomplete or unknown input manifest')
    if {p.name for p in root.iterdir()} != MEMBERS | {'INPUT_MANIFEST.json'}:
        raise ValueError('S02 input directory member set differs')
    for name, expected in manifest['files'].items():
        if identity(root/name) != expected:
            raise ValueError('S02 input hash mismatch: '+name)
    # Gzip headers/compression may change across runs. The entire ordered row stream
    # (all fields, including window extrema) remains pinned independently of that manifest.
    for stream in STREAMS:
        name = stream+'.jsonl.gz'
        if manifest['files'][name] != contract['reference_files'][name]:
            with gzip.open(root/name, 'rb') as f:
                if hashlib.file_digest(f,'sha256').hexdigest() != contract['ordered_ndjson_sha256'][stream]:
                    raise ValueError('S02 frozen ordered stream mismatch: '+stream)
    meta = read(root/'meta.json')
    if meta['spec'] != spec or canonical({k:meta[k] for k in ('records','stations','spec','config')}) != contract['model_sha256']:
        raise ValueError('S02 frozen TLE, target order, station, or rule mismatch')
    progress = read(root/'progress.json')
    expected = contract['expected_counts']
    completed = [n for group in spec['selected'].values() for n in group]
    counts = dict(targets_completed=progress['targets_completed'],windows=progress['windows'],candidates=progress['candidates'],
                  raw_grid=progress['raw_grid_candidates'],pruned=progress['pruned'],executable=progress['executable_targets'],
                  propagation_errors=progress['propagation_errors'])
    if (progress['status'] != 'PASS' or counts != expected or progress['all_target_ids'] != completed
            or progress['targets_planned'] != len(completed) or progress['executable_ids'] != sorted(completed)):
        raise ValueError('S02 cold completion counts differ')
    target_rows = read_rows(root/'target_progress.jsonl.gz')
    summary = [[r[k] for k in ('target_index','satnum','windows','candidates','propagation_errors')] for r in target_rows]
    if canonical(summary) != contract['target_summary_sha256']:
        raise ValueError('S02 target-by-target counts/order differ')
    return meta


def produce(out, seconds):
    from . import scheduler, tle_adapter
    from .s02_axis import CachedGeometry
    contract, spec = authority()
    day = datetime.fromisoformat(spec['start_utc'])
    config = contract['configuration']
    clock = StageClock(seconds)
    out.mkdir()
    with tempfile.TemporaryDirectory(prefix='cold_', dir=out.parent) as temp:
        scratch = Path(temp)
        frozen = scratch/'sample.json'
        write(frozen, dict(seed=42, selected=spec['selected'], input_hashes=contract['raw']))
        parse_config = dict(config, input_dir=str(RAW), frozen_sample=str(frozen), seed=42, start_utc=spec['start_utc'],
                            sample_counts={p:len(group) for p,group in spec['selected'].items()})
        records, stations, day, _, audit = tle_adapter.read_and_audit(parse_config, scratch, clock)
        if audit['epoch_propagation_errors']:
            raise ValueError('S02 raw TLE epoch propagation failed')
        model = dict(spec=spec, records=records, stations=stations, config=config)
        if canonical(model) != contract['model_sha256']:
            raise ValueError('S02 raw-derived model differs from the frozen model')
        started = time.monotonic()
        write(out/'meta.json', dict(model, schema='FAMOU_S02_INPUT_V1', started_utc=now(),
              raw_files=contract['raw'], producer=identity(__file__), cold_production=True))
        geometry = CachedGeometry(records, stations, day, clock, config['horizon_seconds'], config['coarse_step_seconds'])
        windows = candidates = raw_count = error_count = 0
        executable = set()
        for index, record in enumerate(records, 1):
            batch = tle_adapter.build_windows(geometry, [record], stations, config, scratch, clock)
            for i, row in enumerate(batch, windows+1):
                row['window_id'] = f'W{i:05d}'
            options = scheduler.make_candidates(batch, [record], config, day, scratch, clock)
            for i, row in enumerate(options, candidates+1):
                row['candidate_id'] = row['task_id'] = f'C{i:06d}'
            pruning = read(scratch/'candidate_pruning.json')
            for name, rows in [('windows',batch),('candidates',options),('pruning',pruning['per_window_duration']),
                               ('propagation_errors',geometry.errors)]:
                append_stream(out/(name+'.jsonl.gz'), rows)
            append_stream(out/'target_progress.jsonl.gz', [dict(satnum=record['satnum'],target_index=index,
                windows=len(batch),candidates=len(options),propagation_errors=len(geometry.errors),elapsed_s=time.monotonic()-started)])
            windows += len(batch)
            candidates += len(options)
            raw_count += pruning['raw_grid_candidates']
            error_count += len(geometry.errors)
            geometry.errors.clear()
            if options:
                executable.add(record['satnum'])
            if index % 50 == 0:
                print(json.dumps(dict(target=index,windows=windows,candidates=candidates)), flush=True)
    write(out/'progress.json',dict(status='PASS',targets_completed=len(records),targets_planned=len(records),
        all_target_ids=[r['satnum'] for r in records],executable_ids=sorted(executable),executable_targets=len(executable),
        windows=windows,candidates=candidates,raw_grid_candidates=raw_count,pruned=raw_count-candidates,
        propagation_errors=error_count,finished_utc=now(),total_wall_s=time.monotonic()-started))
    write(out/'INPUT_MANIFEST.json',dict(status='COMPLETE',files={name:identity(out/name) for name in sorted(MEMBERS)}))
    check_input(out)


def load(path):
    from .s02_candidates import read_candidates
    meta = check_input(path)
    windows = read_rows(path/'windows.jsonl.gz')
    candidates = read_candidates(path/'candidates.jsonl.gz')
    context = dict(day=datetime.fromisoformat(meta['spec']['start_utc']),horizon=meta['config']['horizon_seconds'],
                   priorities={r['satnum']:r['priority'] for r in meta['records']},stations=set(meta['config']['station_ids']),
                   windows={r['window_id']:r for r in windows})
    return meta, windows, candidates, context
