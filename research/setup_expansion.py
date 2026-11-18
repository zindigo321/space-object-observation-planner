"""Initialize the explicitly authorized F-drive continuation; no science execution."""
import json,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from expansion_run import write,ROOT
root=ROOT.parent;work=root/'work';inventory=work/'inventory'
worker=next(Path('G:/bd-fmb/work/final_20261117T094516Z_d806d799/validation_v4').glob('*/Scripts/python.exe'))
batch=dict(id=root.name,root=str(root),inventory=str(inventory),worker_python=str(worker),
    controller_python=sys.executable,base_commit='96064be8e26b65d9c05e687cb44d89a8ccc65670',
    started_utc='2026-11-18T03:35:55+00:00',stop_new_cases_utc='2026-11-18T11:15:55+00:00',wall_deadline_utc='2026-11-18T11:35:55+00:00',
    wall_cap_s=28800,archive_reserve_s=1200,RSS_cap_bytes=2165493760,
    available_memory_at_start_bytes=4229480*1024,G_free_at_start_bytes=0,
    storage_authorization='User explicitly approved F:/gpt-file/Codex/bd-fmb-expansion and maximum 20 GiB, retaining G archives.',
    disk_cap_bytes=20*1024**3,working_disk_cap_bytes=9*1024**3,
    disk_archive_reserve='Working evidence limited to 9 GiB so compressed audit and metadata fit under 20 GiB total.',
    historical_payload='G:/bd-fmb/work/famou_20261117T080601Z_f7d6e606/input_payload',protocol_status='DRAFT_NOT_FROZEN',
    previous_expired_audit=dict(path='G:/gpt-file/Codex/2026-11-17/qing/outputs/bd-fmb_expansion_20261117T125000Z_7f31/AUDIT_PACKAGE.zip',
        bytes=3831067,sha256='0d14f795b3ba5b7f53174d6c1d7091faf46426d48fca811dab1a4331633a1a19'))
write(work/'BATCH.json',batch)
write(work/'MEMORY_ONLY_CALIBRATION.json',dict(purpose='historical development only',attempt01=dict(status='LAUNCH_FAILED',error='WinError2 due PowerShell stdin Unicode path encoding'),
    attempt02=dict(baseline=dict(J=[2758,180],legal='PASS',violations=0,wall_s=6.786406199913472,peak_RSS_bytes=309243904,
        prepare_s=4.076945300097577,schedule_s=.08290819998364896,geometry_evaluation_s=.9316283999942243),
        improved=dict(J=[3000,180],legal='PASS',violations=0,wall_s=8.443935899995267,peak_RSS_bytes=310788096,
        prepare_s=4.164179800078273,schedule_s=2.866956299985759,geometry_evaluation_s=.8813509999308735)),
    solve_outer_cap_s=30,all_owned_jobs_active_after_cleanup=0,source_manifest_sha256='571bd32b2265aa46f7fa09cfbee9af4cf7be1d5cb57e63916d11e0d04cb12914',
    evidence_provenance='actual tool stdout captured before F storage authorization; no scientific case counted'))
print(json.dumps(batch,ensure_ascii=False))
