"""Seal the prospective matrix only after historical calibration, before test outcomes."""
import hashlib,json,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import psutil
sys.path.insert(0,str(Path(__file__).resolve().parent))
from expansion_run import read,write,ROOT
from expansion_inventory import ident

def main():
    work=ROOT.parent/'work';batch=read(work/'BATCH.json');cal=work/'calibration'
    assert not (work/'RESEARCH_PROTOCOL.json').exists(),'protocol already sealed'
    assert not (work/'RESULTS.json').exists(),'new test outcomes already exist'
    summary=read(cal/'CALIBRATION_FINISHED.json');assert summary['all_cases_pass'] and summary['case_count']==10
    assert read(cal/'monolithic3/EQUIVALENCE.json')['status']=='PASS'
    assert read(cal/'native_compare/NATIVE_EQUIVALENCE.json')['status']=='PASS'
    hard=read(cal/'hard30_RECEIPT.json');assert hard['status']=='TIMEOUT' and hard['cleanup']['active_processes']==0
    mem=read(cal/'memory_guard_RECEIPT.json');assert mem['status']!='PASS' and mem['cleanup']['active_processes']==0
    state=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).decode();assert not state.strip(),'commit source before freezing'
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    source_files={n:ident(ROOT/n) for n in filter(None,files)}
    assert not subprocess.check_output(['git','diff','--name-only',batch['base_commit'],commit,'--','planner','scripts','famou'],cwd=ROOT).strip()
    old=Path('G:/gpt-file/Codex/2026-11-17/qing/outputs/bd-fmb_expansion_20261117T125000Z_7f31/audit')
    registry=read(work/'inventory/PROSPECTIVE_INSTANCES.json');registry.update(status='FROZEN',source_commit=commit)
    write(work/'INSTANCE_REGISTRY.json',registry)
    plan=read(old/'PLANNED_QUEUE.json')
    for row in plan['queue']:
        row.update(source_commit=commit,reason=None)
    plan.update(status='FROZEN',source_commit=commit)
    write(work/'PLAN.json',plan)
    for u in registry['units']:write(work/'specs'/(u['unit_id']+'.json'),u)
    p=read(old/'RESEARCH_PROTOCOL.json')
    p.update(status='FROZEN',frozen_utc=datetime.now(timezone.utc).isoformat(),source_commit=commit,
        reason_not_frozen=None,batch=batch.copy(),calibration=summary,
        actual_historical_calibration_metrics=[dict(case=r['case']['case_id'],wall_s=r['wall_s'],peak_RSS=r['peak_sampled_aggregate_RSS_bytes'],
            J_selected=r.get('J_selected'),status=r['status']) for r in read(cal/'CASE_SUMMARY.json')],
        source_files=source_files,algorithm_changes=[],engineering_changes=[
            'Serial research controller with independent preparation/solve/evaluation processes and Windows Job cleanup.',
            'Target partition only; each target uses original whole-horizon build_windows and make_candidates; exact 3-target/10-station/6-day comparison passed.',
            'Compressed shared complete inputs; global original sequential window/candidate IDs preserved.',
            'Original native C selector with hash-checked compressed loader; four historical native selector equivalence comparisons passed.',
            'F invokes original replay_state/future_candidates and independent interrupted-history validator; selected=raw to retain legacy semantics.',
            'Non-mutating counters wrap schedule internal greedy/improved_construct calls; actual starts/returns recorded.'])
    p['batch'].update(protocol_status='FROZEN',source_commit=commit)
    p['design']['method_order_status']='FROZEN'
    p['budgets'].update(research_prepare_configuration=dict(prepare_s=240,solve_s=30,evaluate_s=300,parent_s=600,
        other_work='input protection, output and cleanup are charged to the same 600s parent; no stage receives unused-time extensions'),
        startup_available_memory_bytes=batch['available_memory_at_start_bytes'],aggregate_RSS_cap_bytes=batch['RSS_cap_bytes'],
        startup_G_free_bytes=0,new_disk_cap_bytes=batch['disk_cap_bytes'],working_disk_cap_bytes=batch['working_disk_cap_bytes'],
        storage_volume='F',storage_change_explicitly_authorized=True,observed_resource_monitor_implementation='expansion_run.monitor',
        RSS_sample_interval_s=.05,disk_sample_interval_s=5,additional_private_commit_job_cap=True,
        resource_gate_required_before_new_scientific_run=False,monitor_limit=hard['monitoring_limit'])
    p['methods']['C']='Original no_fault.choose_from_files selection with independently hash-checked compressed shared-source loader; native_report for history/membership plus fresh per-second raw TLE geometry.'
    p['methods']['F']='Original replay_state/future_candidates and IndependentValidator.check(original_plan,fault,interrupted); selected equals raw, no newly added retained guard.'
    p['methods']['F_retained']='Fixed completed/locked history plus original future tasks legal under the fixed fault; reference score only, not a new fallback.'
    p['bindings']=dict(instance_registry_sha256=ident(work/'INSTANCE_REGISTRY.json')['sha256'],plan_sha256=ident(work/'PLAN.json')['sha256'],
        raw_files_sha256=ident(work/'inventory/RAW_FILES.csv')['sha256'],history_sha256=ident(work/'inventory/HISTORY_EXPOSURE.json')['sha256'],
        calibration_files={str(f.relative_to(cal)):ident(f) for f in cal.rglob('*.json') if f.is_file()},
        request_sha256=ident(old/'USER_REQUEST.txt')['sha256'])
    p['environment']=dict(CPU='Intel Core i9-14900HX',logical_cpus=psutil.cpu_count(),physical_cpus=psutil.cpu_count(logical=False),
        controller_python=platform.python_version(),worker_python='3.11.17',worker_dependencies={'numpy':'2.4.6','skyfield':'1.55','sgp4':'2.27','PyYAML':'6.0.3'},
        threads={'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1'},priority='BELOW_NORMAL')
    write(work/'RESEARCH_PROTOCOL.json',p)
    (work/'RESEARCH_PROTOCOL.txt').write_text('状态：FROZEN。正式新测试成绩产生前已冻结；不是旧H180再次验收。\n'
        '连续窗口为项目实验日期[2026-07-31T00:00:00Z,2026-08-06T00:00:00Z)。\n'
        '保留全部10000目标分母；十站；每目标全时域最多一次成功；30秒候选网格，每窗每时长cap12。\n'
        '输入按目标分块而不按天拆解；三目标、十站、六天与单体逐窗逐候选精确相等。\n'
        'S01→B001→S02–S06→B002–B012；18冷生产、36初始、120重排；失败依赖BLOCKED，未启动NOT_RUN。\n'
        'C严格J保底；F保持原故障路径selected=raw，无额外保底；retained仅包含故障合法原状态。\n'
        '新批2026-11-18 11:35:55北京时间开始，19:15:55停止新案例，19:35:55墙钟截止。\n'
        'G盘为0字节，用户已明确授权改F盘，落盘最多20GiB；工作证据9GiB上限为审计ZIP留空间。\n'
        'RSS上限2165493760字节；输入1800秒、每份初始/每重排600秒、prepare240/solve30/evaluate300。\n'
        '新研究prepare240秒与旧H180验收不同；两方法相同；旧验收80/600未修改。\n'
        '详见JSON、哈希实例清单、计划队列与校准证据。\n',encoding='utf-8')
    batch.update(protocol_status='FROZEN',source_commit=commit,source_files=source_files,protocol_sha256=ident(work/'RESEARCH_PROTOCOL.json')['sha256'])
    write(work/'BATCH.json',batch)
    write(work/'FREEZE_RECEIPT.json',dict(time_utc=p['frozen_utc'],source_commit=commit,protocol_sha256=batch['protocol_sha256'],
        instances=ident(work/'INSTANCE_REGISTRY.json'),plan=ident(work/'PLAN.json'),new_test_outcomes_seen=0,old_product_code_unchanged=True,
        calibration_only=True,history_completeness='NOT_PROVEN',independent_external_TLE_source='NOT_ESTABLISHED'))
    print(json.dumps(dict(source_commit=commit,protocol_sha256=batch['protocol_sha256'],planned_cases=len(plan['queue']))))
if __name__=='__main__':main()
