"""Real subprocess regression tests for the public candidate trust boundary."""
import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
import pytest
from no_fault_fixtures import fixture
from planner.process_guard import run_guarded

ROOT=Path(__file__).resolve().parents[1]

def identity(path):
    raw=path.read_bytes();return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

@pytest.fixture
def package(tmp_path):
    root=tmp_path/'包 空格';root.mkdir()
    for name in ('planner','scripts'):
        shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('__pycache__'))
    source=root/'data/synthetic';sha=fixture(source)
    (root/'configs').mkdir()
    (root/'configs/famou_cases.json').write_text(json.dumps({'synthetic':{
        'source':'data/synthetic','source_sha256':sha,'decision_s':120}}),encoding='utf-8')
    fixed={p.relative_to(root).as_posix():identity(p) for p in root.rglob('*') if p.is_file()}
    (root/'FIXED_MANIFEST.json').write_text(json.dumps({'files':fixed}),encoding='utf-8')
    return root

def command(package,candidate,out):
    return [sys.executable,'-B','-X','utf8',str(package/'scripts/famou_candidate_runner.py'),
            '--case','synthetic','--script',str(candidate),'--out',str(out)]

def execute(package,tmp_path,code,expected):
    candidate=tmp_path/'editable.py';candidate.write_text(code,encoding='utf-8')
    out=tmp_path/'run'
    result=subprocess.run(command(package,candidate,out),capture_output=True,timeout=100)
    (tmp_path/'stdout.bin').write_bytes(result.stdout);(tmp_path/'stderr.bin').write_bytes(result.stderr)
    assert result.returncode==expected,result.stderr.decode(errors='replace')
    return out,json.loads((out/'candidate_execution.json').read_bytes())

def test_fast_candidate_and_exact_copy(package,tmp_path,record_property):
    code='from __future__ import annotations\nfrom dataclasses import dataclass\n@dataclass\nclass Result:\n    rows: list\ndef solve(problem):\n    return Result(problem["retained"]).rows\n'
    out,receipt=execute(package,tmp_path,code,0)
    assert receipt['status']=='PASS' and receipt['executed_copy_unchanged']
    assert receipt['candidate']==identity(out/'candidate_workspace/candidate.py')
    assert receipt['command']==receipt['solve']['command']
    assert receipt['solve']['budget_seconds']==30
    assert all(row['cleanup']['confirmed'] for row in receipt['phases'])
    assert (out/'evaluation/candidate_evaluation.json').is_file()
    record_property('execution',json.dumps(receipt))

def test_real_over30_never_evaluated(package,tmp_path,record_property):
    code='import time\ndef solve(problem):\n    time.sleep(31.25)\n    return problem["retained"]\n'
    out,receipt=execute(package,tmp_path,code,3)
    assert receipt['status']=='TIMEOUT' and receipt['failed_phase']=='solve'
    assert receipt['solve']['timed_out'] and 29.5<=receipt['solve']['execution_seconds']<31.25
    assert receipt['solve']['cleanup']['confirmed']
    assert not (out/'evaluation').exists() and not (out/'proposal.csv').exists()
    record_property('execution',json.dumps(receipt))

def test_original_change_keeps_executed_copy_binding(package,tmp_path,record_property):
    marker=tmp_path/'entered'
    candidate=tmp_path/'editable.py'
    candidate.write_text('import time\nfrom pathlib import Path\ndef solve(problem):\n'
        f'    Path({str(marker)!r}).write_text("entered")\n'
        '    time.sleep(1)\n    return problem["retained"]\n',encoding='utf-8')
    original=identity(candidate);out=tmp_path/'run'
    with (tmp_path/'stdout.bin').open('wb') as stdout,(tmp_path/'stderr.bin').open('wb') as stderr:
        process=subprocess.Popen(command(package,candidate,out),stdout=stdout,stderr=stderr)
        end=time.monotonic()+20
        while not marker.exists():
            assert process.poll() is None and time.monotonic()<end
            time.sleep(.02)
        candidate.write_text('raise RuntimeError("THIS VERSION WAS NEVER EXECUTED")\n',encoding='utf-8')
        assert process.wait(timeout=30)==0
    receipt=json.loads((out/'candidate_execution.json').read_bytes())
    assert receipt['candidate']==original==receipt['executed_copy_after']
    assert receipt['original_changed_during_run'] and receipt['original_after']==identity(candidate)
    assert receipt['candidate']!=receipt['original_after'] and receipt['status']=='PASS'
    record_property('execution',json.dumps(receipt))

@pytest.mark.parametrize('mode',['success','failure','timeout'])
def test_descendants_terminated_after_all_parent_outcomes(tmp_path,mode,record_property):
    heartbeat=tmp_path/'heartbeat';parent=tmp_path/'parent.py'
    worker_identity=tmp_path/'worker_identity.json'
    child='import sys,time;from pathlib import Path;p=Path(sys.argv[1])\nwhile True:p.write_text(str(time.monotonic()));time.sleep(.02)\n'
    parent.write_text('import subprocess,sys,time,os,json\nfrom pathlib import Path\n'
        f'Path({str(worker_identity)!r}).write_text(json.dumps(dict(ppid=os.getppid(),prefix=sys.prefix,executable=sys.executable)))\n'
        f'p=Path({str(heartbeat)!r})\n'
        f'subprocess.Popen([sys.executable,"-B","-c",{child!r},str(p)])\n'
        'while not p.exists():time.sleep(.01)\n'+
        ('time.sleep(20)\n' if mode=='timeout' else f'raise SystemExit({7 if mode=="failure" else 0})\n'),encoding='utf-8')
    result=run_guarded([sys.executable,'-B',str(parent)],timeout=.8 if mode=='timeout' else 8,
                       log_path=tmp_path/'guard.log',cwd=tmp_path)
    assert result['timed_out']==(mode=='timeout')
    assert result['exit_code']=={'success':0,'failure':7,'timeout':3}[mode]
    assert result['cleanup']['confirmed'] and result['cleanup']['active_processes']==0
    actual=json.loads(worker_identity.read_bytes())
    assert actual==dict(ppid=os.getpid(),prefix=sys.prefix,executable=sys.executable)
    before=heartbeat.read_bytes();time.sleep(.2);assert heartbeat.read_bytes()==before
    record_property('execution',json.dumps(result))

def test_candidate_self_modification_is_rejected(package,tmp_path):
    code='from pathlib import Path\ndef solve(problem):\n    Path(__file__).write_text("# changed")\n    return problem["retained"]\n'
    out,receipt=execute(package,tmp_path,code,2)
    assert not receipt['executed_copy_unchanged'] and not (out/'evaluation').exists()
