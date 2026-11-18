import hashlib

import pytest

from planner import s02_input
from planner.no_fault import _select_by_j
from scripts.s02_cli import verify_planning_run


def test_equal_j_keeps_original_row_order():
    initial = [dict(satnum=n,station_id=1,start_utc='a',end_utc='b',duration_s=120) for n in (7,3)]
    retained = [dict(r,status='new_success') for r in initial]
    selected, result = _select_by_j(initial,retained,retained[::-1],[30,2],[30,2])
    assert selected == retained and selected is not retained
    assert result['branch'] == 'KEEP_RETAINED_TIE'


def test_timeout_run_cannot_enter_independent_evaluation(tmp_path):
    s02_input.write(tmp_path/'workflow.json',dict(status='TIMEOUT',action='initial'))
    with pytest.raises(ValueError,match='successful S02 planning'):
        verify_planning_run(tmp_path,tmp_path)


def test_resealing_a_changed_ordered_stream_does_not_change_authority(tmp_path,monkeypatch):
    import gzip
    ref = {}
    for name in s02_input.MEMBERS:
        file = tmp_path/name
        file.write_bytes(gzip.compress(b'original\n') if name.endswith('.gz') else b'{}')
        ref[name] = s02_input.identity(file)
    (tmp_path/'candidates.jsonl.gz').write_bytes(gzip.compress(b'changed\n'))
    s02_input.write(tmp_path/'INPUT_MANIFEST.json',dict(status='COMPLETE',files={n:s02_input.identity(tmp_path/n) for n in ref}))
    contract = dict(reference_files=ref,ordered_ndjson_sha256={'candidates':hashlib.sha256(b'original\n').hexdigest()})
    monkeypatch.setattr(s02_input,'authority',lambda:(contract,{}))
    with pytest.raises(ValueError,match='frozen ordered stream mismatch: candidates'):
        s02_input.check_input(tmp_path)

def test_successful_exit_observed_after_30_seconds_is_not_admitted(tmp_path,monkeypatch):
    import time
    from scripts import s02_cli
    cold = tmp_path/'input'
    cold.mkdir()
    (cold/'INPUT_MANIFEST.json').write_text('{}')
    out = tmp_path/'run'
    out.mkdir()
    monkeypatch.setattr(s02_cli,'check_input',lambda path: None)
    delayed = dict(exit_code=0,raw_exit_code=0,timed_out=False,execution_seconds=30.0001,
                   cleanup=dict(confirmed=True,active_processes=0))
    monkeypatch.setattr(s02_cli,'run_guarded',lambda *args,**kw: delayed)
    assert s02_cli.calculate_case('initial','baseline',cold,None,out,time.monotonic()+600) == 3
    assert s02_input.read(out/'case.json')['status'] == 'TIMEOUT'
    assert not (out/'evaluation').exists()

def test_unsupported_machine_fails_before_dll_loading(monkeypatch):
    monkeypatch.setattr(s02_input.platform,'machine',lambda:'ARM64')
    with pytest.raises(ValueError,match='Windows x64'):
        s02_input.platform_check()
