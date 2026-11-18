"""Close an expired, unexecuted expansion batch without inventing experiment results."""
from __future__ import annotations
import argparse, csv, hashlib, json, os, platform, re, shutil, subprocess, sys, time, zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from expansion_inventory import ident,write,csvout

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def stamp(): return datetime.now(timezone.utc).isoformat()
def sha(data): return hashlib.sha256(data).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=HERE)

def build(args):
    started=time.perf_counter(); work=Path(args.work); inventory=work/'closure/inventory'
    dest=Path(args.out); dest.mkdir(parents=True,exist_ok=False)
    payload=dest/'audit'; payload.mkdir()
    shutil.copytree(inventory,payload/'inputs')
    original=Path(args.original)
    prior=payload/'prior_acceptance'; prior.mkdir()
    for name in ('FINAL_ACCEPTANCE.json','DELIVERY_RECEIPT.json'):
        shutil.copyfile(original/name,prior/name)
    request=Path(args.request); shutil.copyfile(request,payload/'USER_REQUEST.txt')
    acceptance=read(original/'FINAL_ACCEPTANCE.json'); receipt=read(original/'DELIVERY_RECEIPT.json')
    prior_zip=ident(original/'FAMOU_TEST_PACKAGE.zip')
    assert prior_zip=={k:receipt['FAMOU_TEST_PACKAGE.zip'][k] for k in ('bytes','sha256')}
    base='96064be8e26b65d9c05e687cb44d89a8ccc65670'
    assert acceptance['source_commit']==base
    commit=git('rev-parse','HEAD').decode().strip()
    assert git('status','--porcelain').decode().strip()==''
    source=payload/'source'; source.mkdir()
    tracked=git('ls-files','-z').decode().split('\0')
    for name in filter(None,tracked):
        p=source/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(git('show',f'{commit}:{name}'))
    diff=git('diff','--binary',base,commit); (payload/'SOURCE_DIFF.patch').write_bytes(diff)
    binding=dict(base_commit=base,research_commit=commit,branch=git('branch','--show-current').decode().strip(),
        worktree=str(HERE),accepted_product_code_unchanged=not bool(git('diff','--name-only',base,commit,'--','planner','scripts','famou')),
        added_research_files=git('diff','--name-only',base,commit).decode().splitlines(),
        prior_test_zip_verified=prior_zip,old_acceptance_status=acceptance['status'],old_evidence_replayed=False,
        source_files={name:ident(source/name) for name in filter(None,tracked)})
    assert binding['accepted_product_code_unchanged']
    write(payload/'SOURCE_BINDING.json',binding)
    registry=read(inventory/'PROSPECTIVE_INSTANCES.json'); units=registry['units']
    history=read(inventory/'HISTORY_EXPOSURE.json'); raw=read(inventory/'RAW_INVENTORY.json')
    stop_reason='BATCH_WALL_DEADLINE_EXPIRED_DURING_CONVERSATION_INTERRUPTION_BEFORE_CALIBRATION'
    group_ids=[f"{u['unit_id']}_{origin}_{scene}" for u in units for origin in ('baseline','improved')
               for scene in (('C',) if u['line']=='A' else ('C','F'))]
    ranked=sorted(group_ids,key=lambda s:sha(('method-order-v1|'+s).encode()))
    first={s:('baseline' if i%2==0 else 'improved') for i,s in enumerate(ranked)}
    initial_rank=sorted([u['unit_id'] for u in units],key=lambda s:sha(('initial-order-v1|'+s).encode()))
    initial_first={s:('baseline' if i%2==0 else 'improved') for i,s in enumerate(initial_rank)}
    queue=[]
    def add(row):
        queue.append(dict(sequence=len(queue)+1,status='NOT_RUN',reason=stop_reason,attempt_id=None,
            result=None,source_commit=commit,**row))
    for u in units:
        unit=u['unit_id']; order=[initial_first[unit], 'improved' if initial_first[unit]=='baseline' else 'baseline']
        add(dict(case_id=unit+'_INPUT',kind='cold_input',unit_id=unit,line=u['line'],dependencies=[],parent_budget_s=1800,
            instance_sha256=u['instance_sha256'],target_count=u['target_count'],horizon_seconds=u['horizon_seconds']))
        for method in order:
            add(dict(case_id=f'{unit}_INIT_{method}',kind='initial',unit_id=unit,line=u['line'],method=method,
                dependencies=[unit+'_INPUT'],parent_budget_s=600,solve_hard_cap_s=30,instance_sha256=u['instance_sha256']))
        for origin in ('baseline','improved'):
            for scene in (('C',) if u['line']=='A' else ('C','F')):
                group=f'{unit}_{origin}_{scene}'; method0=first[group]
                for method in (method0,'improved' if method0=='baseline' else 'baseline'):
                    add(dict(case_id=f'{group}_{method}',kind='replan',unit_id=unit,line=u['line'],origin=origin,
                        scenario=scene,method=method,pair_id=group,decision_s=3600,
                        event=None if scene=='C' else dict(station_id=1,start_s=3600,end_s=10800),
                        dependencies=[unit+'_INPUT',f'{unit}_INIT_{origin}'],parent_budget_s=600,solve_hard_cap_s=30,
                        instance_sha256=u['instance_sha256']))
    # The file is a prospective protocol, explicitly not a completed preregistration.
    protocol=dict(schema='BD_FMB_EXPANSION_PROTOCOL_V1',status='DRAFT_NOT_FROZEN',created_utc=stamp(),
        experiment_kind='first_expansion_not_H180_reacceptance',base_commit=base,source_commit=commit,
        reason_not_frozen='H180 calibration and research execution/resource driver were not completed before interruption and batch expiry.',
        batch=dict(id=work.name,status='EXPIRED_BEFORE_SCIENTIFIC_RUN',start_reference_utc='2026-11-17T12:47:00Z',
            start_reference_precision='approximate from turn; earliest recorded clock 2026-11-17T12:48:53Z; budget definitely expired by 2026-11-17T20:48:53Z',
            conservative_stop_new_cases_utc='2026-11-17T20:27:00Z',conservative_wall_deadline_utc='2026-11-17T20:47:00Z',
            interruption_interval_exact='unknown; no background scientific runner was launched',
            resumed_clock_utc='2026-11-18T03:27:49Z',closure_only=True,budget_reset_authorized=False,
            wall_cap_s=28800,archive_reserve_s=1200),
        model=dict(window_label='PROJECT_EXPERIMENT_WINDOW',start_utc='2026-07-31T00:00:00Z',
            end_utc_exclusive='2026-08-06T00:00:00Z',horizon_s=518400,weights=dict(high=5,medium=3,low=2),
            durations_s=[120,240],fraction_by_duration={'120':0.6,'240':1.0},points_integer_scale=5,
            J_order=['authoritative_integer_points','unique_successful_targets'],switch_s=30,
            max_success_per_target_entire_horizon=1,station_parallel_tasks=1,elevation_bounds_deg=[10,85],
            station_ids=list(range(1,11)),coarse_sampling_s=30,fine_sampling_s=1,
            longitude_rule='((longitude+180)%360)-180',alpha5_rule='sgp4.alpha5.from_alpha5 checked against Satrec.satnum',
            official_six_day_dates=False,optical_certification=False,online_multi_event_state_chain=False),
        candidates=dict(start_grid_s=30,maximum_starts_per_window_per_duration=12,
            algorithm='inherited make_candidates: start at window start, append last endpoint, evenly spaced rounded linspace indices if over cap',
            rules_unchanged=True,full_population_required=True,no_window_targets_retained=True,
            continuous_time_exhaustiveness=False,merge_time_chunk_boundary_windows_before_cap=True,
            shared_readonly_complete_input=True,cold_and_cache_accounting_separate=True),
        design=dict(A_units=6,A_initial=12,A_replans=24,B_blocks=12,B_initial=24,B_replans=96,
            total_initial=36,total_replans=120,total_cold_input_units=18,
            order=[u['unit_id'] for u in units],B_start_utc='2026-08-05T00:00:00Z',B_horizon_s=86400,
            B_priority_counts=dict(high=60,medium=60,low=60),B_pair_scenarios=['C','F'],decision_s=3600,
            fault=dict(station_id=1,start_s=3600,end_s=10800),method_order_rule='SHA256-ranked pair IDs, alternating first method; 30 pairs per first method',
            initial_order_rule='SHA256-ranked unit IDs, alternating; 9 units per first method',
            method_order_status='prospective until calibration and protocol seal',
            independent_sample_definition='target block; origin, scenario, seed, day, station and per-second samples are not independent repeats',
            selection_seed=registry['selection_seed'],B_capacity_blocks=registry['B_capacity_blocks'],
            history_exclusion_count=history['unique_excluded_count'],historical_exposure_completeness='NOT_PROVEN'),
        budgets=dict(cold_input_s=1800,initial_parent_s=600,replan_parent_s=600,solve_all_editable_code_and_descendants_s=30,
            CLI_bound_separate=True,product_no_fault_CLI_max_s=300,research_prepare_configuration='NOT_CALIBRATED_NOT_FROZEN',
            startup_available_memory_bytes=4767776*1024,aggregate_RSS_cap_bytes=4767776*1024//2,
            startup_G_free_bytes=1216983040,new_disk_cap_bytes=1216983040//4,
            observed_resource_monitor_implementation='NOT_IMPLEMENTED',resource_gate_required_before_new_scientific_run=True),
        methods=dict(baseline='planner.scheduler.schedule(method=baseline)',
            improved='planner.scheduler.schedule(method=improved); includes internal greedy baseline and comparison fallback',
            C='native no_fault retained guard; strict J improvement; ties preserve retained bytes',
            F='actual replay_state and future_candidates fault interface plus independent interrupted-history check; legacy fault path has no native C guard',
            F_retained='only fixed history and original future tasks legal under the predeclared fault; selection semantics must be documented, not silently changed',
            algorithm_changes=[]),
        metrics=dict(required=['input/source hashes','all/executable target denominators','windows/candidates/raw grid/retained/pruned',
            'initial/retained/raw/selected J','selection branch','changes','coverage and priority score',
            'raw exits','actual solve calls including internal baseline','cold/prepare/solve/evaluate/geometry/archive/total wall time',
            'CPU/peak aggregate RSS/disk','failures/timeouts/cleanup','independent evaluation','input protection'],
            B_primary='Within each block, mean of C selected main-score improved-minus-baseline across the two common origins; report blocks, mean, median, quantiles and win/tie/loss.',
            B_secondary='F and raw; matched fault-specific effect Delta_F-Delta_C.',
            failure_policy='No fabricated zero score. Full planned denominators retained. Successful-pair subset explicitly labeled.',
            significance_claim=False,generalization='conditional on current TLE source and frozen engineering model; no universal superiority'),
        bindings=dict(raw_inventory_sha256=ident(inventory/'RAW_INVENTORY.json')['sha256'],
            raw_files_sha256=ident(inventory/'RAW_FILES.csv')['sha256'],prospective_instances_sha256=ident(inventory/'PROSPECTIVE_INSTANCES.json')['sha256'],
            source_binding_sha256=ident(payload/'SOURCE_BINDING.json')['sha256'],
            request_sha256=ident(payload/'USER_REQUEST.txt')['sha256']))
    write(payload/'RESEARCH_PROTOCOL.json',protocol)
    (payload/'RESEARCH_PROTOCOL.txt').write_text('状态：DRAFT_NOT_FROZEN（草案，未完成预注册冻结）。\n原8小时批次已到期；未做H180校准，未启动扩展科学案例。\n完整机器可读协议、模型、矩阵、资源上限及未满足门槛见RESEARCH_PROTOCOL.json。\n本文件封存时间不等于算法预注册冻结时间。\n',encoding='utf-8')
    write(payload/'PLANNED_QUEUE.json',dict(status='DRAFT_NOT_FROZEN',queue=queue))
    coverage=[dict(item='accepted_source_and_receipt',status='VERIFIED',evidence='SOURCE_BINDING.json'),
        dict(item='nine_raw_files_and_zip_docx_parse',status='VERIFIED',evidence='inputs/RAW_INVENTORY.json'),
        dict(item='population_10000_and_priorities',status='VERIFIED',evidence='inputs/POPULATION.csv'),
        dict(item='historical_exclusion',status='PARTIAL_NOT_PROVEN_COMPLETE',evidence='inputs/HISTORY_EXPOSURE.json'),
        dict(item='external_TLE_source',status='NOT_ESTABLISHED',evidence='inputs/TLE_SNAPSHOT_CATALOG.json'),
        dict(item='H180_driver_calibration',status='NOT_RUN',evidence='BATCH_EVENTS.json'),
        dict(item='resource_guard_and_chunk_equivalence',status='NOT_IMPLEMENTED_NOT_RUN',evidence='RESEARCH_PROTOCOL.json'),
        dict(item='preregistration_freeze',status='NOT_FROZEN',evidence='RESEARCH_PROTOCOL.json')]
    coverage += [dict(item=q['case_id'],status='NOT_RUN',evidence='PLANNED_QUEUE.json') for q in queue]
    csvout(payload/'RUN_COVERAGE.csv',coverage,['item','status','evidence'])
    fields=['sequence','case_id','unit_id','line','origin','scenario','method','pair_id','status','reason',
        'attempt_id','source_commit','instance_sha256','J_initial','J_retained','J_raw','J_selected','branch','solve_calls',
        'wall_seconds','peak_aggregate_RSS_bytes','independent_legality','geometry_status','input_protection']
    csvout(payload/'PAIRED_RESULTS.csv',[q for q in queue if q['kind']=='replan'],fields)
    csvout(payload/'INITIAL_RESULTS.csv',[q for q in queue if q['kind']=='initial'],fields)
    csvout(payload/'INPUT_RESULTS.csv',[q for q in queue if q['kind']=='cold_input'],
        ['sequence','case_id','unit_id','line','target_count','horizon_seconds','status','reason','parent_budget_s','source_commit','instance_sha256'])
    scale=[]
    for u in units:
        if u['line']=='A': scale.append(dict(unit_id=u['unit_id'],targets=u['target_count'],stations=10,hours=u['horizon_seconds']//3600,
            input_status='NOT_RUN',initial_completed=0,initial_planned=2,replan_completed=0,replan_planned=4,
            full_pipeline_status='NOT_RUN',reason=stop_reason))
    csvout(payload/'SCALE_RESULTS.csv',scale,list(scale[0]))
    csvout(payload/'FAILURES_NOT_RUN.csv',queue,['sequence','case_id','kind','status','reason','attempt_id'])
    write(payload/'BATCH_EVENTS.json',dict(events=[
        dict(time='2026-11-17T12:48:53Z',event='earliest_exact_tool_clock; source/acceptance inspection in progress'),
        dict(time='2026-11-17T12:49:31Z',event='isolated worktree created; directory LastWriteTime evidence'),
        dict(time=None,event='conversation interrupted before driver/calibration/freeze; no background scientific process launched'),
        dict(time='2026-11-18T03:27:49Z',event='resumed clock; original budget expired; process inspection found no scientific runner'),
        dict(time=stamp(),event='closure raw inventory and queue archival only; no new scientific cases')],
        scientific_case_attempts=0,scientific_solver_calls=0,case_timeouts=0,case_illegal_outputs=0,
        initial_NOT_RUN=36,replan_NOT_RUN=120,input_NOT_RUN=18,completed_B_blocks=0,
        cleanup=dict(owned_scientific_processes=0,termination_required=False,unrelated_processes_terminated=0),
        limitation='Time of interruption is not available; no fabricated elapsed breakdown or process monitoring history.'))
    import psutil
    current_memory=psutil.virtual_memory(); disk=shutil.disk_usage(dest.anchor)
    resources=dict(initial_snapshot=dict(observed_during_preparation=True,exact_timestamp=None,
        CPU='Intel Core i9-14900HX',physical_cores=24,logical_processors=32,total_memory_bytes=33271672*1024,
        available_memory_bytes=4767776*1024,G_free_bytes=1216983040),
        limits=dict(aggregate_RSS_bytes=4767776*1024//2,new_disk_bytes=1216983040//4),
        closure_snapshot=dict(time_utc=stamp(),available_memory_bytes=current_memory.available,G_free_bytes=disk.free,
            Python=platform.python_version(),CPU_load_percent=psutil.cpu_percent(interval=0.2)),
        scientific_run_peak_RSS_bytes=None,scientific_run_CPU_seconds=None,scientific_run_disk_bytes=None,
        initial_preparation_peak_RSS_bytes=None,initial_preparation_CPU_seconds=None,
        status='NO_SCIENTIFIC_RUN; PREPARATION_CONTINUOUS_MONITORING_NOT_AVAILABLE',
        memory_and_disk_forecasts_are_not_measurements=True)
    write(payload/'RESOURCE_RECORDS.json',resources)
    (payload/'RULE_BOUNDARIES.txt').write_text(
        '工程模型与规则边界\n'
        '原始9文件已复制原字节并哈希；两份DOCX均解析，原文见inputs/parsed/official_document_text.json。\n'
        '说明.docx规定10000目标、10站、前后共6天，未指定共同UTC起止；本轮日期为项目实验约定。\n'
        '说明.docx为计算40%/体验30%/效率30%及额外加分；另一份DOCX为25/25/25/15/10。不能合成官方百分制成绩。\n'
        '5/3/2、120秒60%、240秒100%、切换30秒沿用；仅120/240离散、整个时域每目标至多一次成功是工程假设。\n'
        '几何10–85度仅对应给定TLE/仰角模型，不能认证完整光学、天气、跟踪速度、受光或日月规避。\n'
        '继承候选30秒起点网格+终点补入，每窗每时长最多12个；全目标覆盖不等于连续时间穷举。\n'
        '跨日连续窗口必须先合并再cap；不能按天独立求解后拼接。多次在线事件状态链未预注册。\n'
        '当前仅做逐目标TLE历元解析器自检；未在实验时域生成任何窗口或候选。\n'
        '未建立可用的独立外部TLE验证集；历史ID排除集只覆盖扫描到的可识别文件，不证明完全无暴露。\n',encoding='utf-8')
    report=(
        'bd-fmb 第一轮扩展运行测试：中断后到期批次审计\n'
        '状态：EXPIRED_BEFORE_SCIENTIFIC_RUN。不是扩展实验完成，不是旧H180重新验收。\n\n'
        '实际执行：0/18输入冷生产单元、0/36初始计划、0/120重排案例，完整B块0/12。\n'
        '全部18+36+120项均为NOT_RUN；案例失败、超时、非法输出均0，因为没有案例尝试。\n'
        '本批未产生窗口、候选、调度或重排成绩。所有J、耗时与峰值内存结果保留缺失值，不填0分或PASS。\n'
        '原因：会话在源码/环境检查阶段被中断。恢复时为2026-11-18 11:27:49北京时间，原8小时墙钟上限早已到达。\n'
        '原批起点约2026-11-17 20:47北京时间；最早精确工具时间20:48:53，故截止至迟为2026-11-18 04:48:53。\n'
        '没有自动重置预算，也没有在截止后启动科学案例。恢复后的动作仅为盘点和收尾归档，已超原归档截止。\n\n'
        '1. 规模能力\n'
        '本轮实测最大完成规模：无。10000×10×144h没有完成，也没有开始。\n'
        '不能由本批判断算法规模上限、求解耗时、合法性或质量。既有H180验收不计为本轮新证据。\n'
        '启动检查时可用内存4,767,776 KiB，任务RSS上限2,441,101,312字节；G盘可用1,216,983,040字节，新增落盘上限304,245,760字节。\n'
        '资源紧张是已观察的环境约束；没有运行失败证据证明它是实际计算瓶颈。3874万候选只是此前估计，本批未验证。\n\n'
        '2. 方法效果\n'
        '无新测试成绩，不能判定improved优于、持平或退化于baseline。raw、selected、胜平负、退化率和成功子集比较均未测。\n'
        'H180驱动校准未执行，协议为DRAFT_NOT_FROZEN。待运行ID及方法顺序已列出，但不冒充已完成的预注册。\n'
        f"原始数据复核：{raw['tle_count']}个唯一TLE目标、{raw['alpha5_count']}个Alpha-5；高/中/低2024/3990/3986，10站；原始文件保护核验通过。\n"
        f"历史扫描识别并保守排除{history['unique_excluded_count']}个目标；可选每档60目标的B块容量{registry['B_capacity_blocks']}。历史暴露完整性未证明。\n"
        '即使未来完成12块，也只支持本来源和固定工程模型下的条件评价，不证明普遍优势或外部泛化。\n\n'
        '3. 故障专属效果\n'
        'C/F均未运行，Delta_F-Delta_C无值，不能用既有方法差推断故障收益。\n'
        'F计划固定站点1在[3600,10800)停机，必须走真实replay_state/中断接口，保留合法retained；不能仅删窗口模拟。\n\n'
        '完成的准备工作：核验验收提交及原测试ZIP哈希；新建隔离分支；复核9份原料、两ZIP与两DOCX；建立全10000分母和龄期表；\n'
        '扫描历史排除集及TLE快照；封存完整待运行清单、协议草案、源码与差异。\n'
        '未完成的必要工作：资源监控驱动、H180校准、分块等价性、协议正式冻结、全部扩展执行。没有可直接启动完整科学矩阵的研究执行器。\n'
        '下一批精确恢复入口为RESUME_PROMPT.txt与RESUME_QUEUE.json；首先需要新的明确墙钟预算，再完成缺失驱动/校准/冻结，首个科学单元S01。\n'
        '原36+120案例无已完成项可重用；已验证原料与源代码可按哈希只读复用。不要重放旧H180正式请求。\n')
    (payload/'EXPANSION_REPORT.txt').write_text(report,encoding='utf-8')
    resume=dict(schema='BD_FMB_EXPANSION_RESUME_V1',previous_batch=work.name,previous_status='EXPIRED_BEFORE_SCIENTIFIC_RUN',
        budget_authorization='NEW_BATCH_WALL_BUDGET_REQUIRED',source_commit=commit,base_commit=base,
        worktree=str(HERE),protocol_status='DRAFT_NOT_FROZEN',protocol_sha256=ident(payload/'RESEARCH_PROTOCOL.json')['sha256'],
        input_registry_sha256=ident(payload/'inputs/PROSPECTIVE_INSTANCES.json')['sha256'],
        raw_files_sha256=ident(payload/'inputs/RAW_FILES.csv')['sha256'],
        plan_queue_sha256=ident(payload/'PLANNED_QUEUE.json')['sha256'],completed_case_ids=[],attempted_case_ids=[],
        consumed_old_formal_requests_replay=False,all_new_attempt_ids_must_be_unique=True,
        remaining=[dict(action='authorize_new_batch_and_record_start_and_deadline'),
            dict(action='verify_bound_source_inputs_and_original_accepted_package'),
            dict(action='implement_dedicated_guarded_research_driver_without_changing_algorithms'),
            dict(action='calibrate_on_historical_H180_and_verify_chunk_equivalence',development_only=True),
            dict(action='freeze_execution_budgets_source_protocol_ID_lists_orders_events_metrics_before_any_new_test_scores'),
            dict(action='execute_planned_queue',first_unit='S01',next_unit='B001',queue_file='PLANNED_QUEUE.json')],
        remaining_counts=dict(cold_inputs=18,initial=36,replan=120),
        budget_plan=dict(proposed_new_wall_s=28800,archive_reserve_s=1200,cold_input_s=1800,initial_parent_s=600,
            replan_parent_s=600,solve_hard_s=30,new_resource_limits='recompute from new-batch available memory/disk and freeze before tests'),
        runnable_matrix_driver_available=False,inventory_driver='source/research/expansion_inventory.py')
    write(payload/'RESUME_QUEUE.json',resume)
    prompt=(f'继续bd-fmb第一轮扩展测试。先取得明确的新批墙钟预算，不能重置或延长已过期原批。\n'
        f'原批审计目录：{dest}\n隔离源码：{HERE}\n绑定提交：{commit}\n基线：{base}\n'
        f"协议草案SHA256：{resume['protocol_sha256']}\n实例注册表SHA256：{resume['input_registry_sha256']}\n"
        f"原料哈希表SHA256：{resume['raw_files_sha256']}\n计划队列SHA256：{resume['plan_queue_sha256']}\n"
        '先重新打开AUDIT_PACKAGE.zip，验证FILE_MANIFEST.json与包外回执；保持旧FINAL_ACCEPTED交付只读。\n'
        '准确断点：还没有研究执行驱动、H180校准或正式协议冻结；科学案例0/174，全部NOT_RUN。\n'
        '先实现Windows Job Object受控研究驱动与聚合RSS/磁盘监控，记录30秒全部候选代码及后代硬限、600秒父级、1800秒输入冷生产。\n'
        '高负载串行；开发仅用既有H180。分块时先合并完整跨日窗口再cap，验证与原单体等价。\n'
        '继承调度评分候选策略。F用真实replay_state和future_candidates及独立中断历史校验；披露C/F选择差异。\n'
        '检视历史排除扫描未覆盖项；如修订ID/样本设计，必须在任何新成绩前记录原因。\n'
        '完成校准后，提交源代码并正式封存协议、全部ID/哈希/方法顺序/事件/预算/指标，再启动S01→完整B001→S02至S06→B002至B012。\n'
        '本批无已完成科学案例需跳过；以后完成项按哈希只读复用，每次新尝试唯一attempt_id，保留失败；不重放旧已消费正式请求。\n'
        '原料原字节和完整已验收源码已在审计ZIP内。inventory脚本可运行但不是科学矩阵执行器。\n'
        '收尾仍必须交付真实CSV/报告/审计ZIP及续跑队列；资源或预算失败不能当算法质量0分或PASS。\n')
    (payload/'RESUME_PROMPT.txt').write_text(prompt,encoding='utf-8')
    (payload/'INDEX.txt').write_text('本包状态：首批中断后预算到期，科学案例0；不得当作扩展测试完成。\n'
        'EXPANSION_REPORT.txt：三条结论与未完成事项。\nRESEARCH_PROTOCOL.json/txt：尚未冻结的协议草案。\n'
        'PLANNED_QUEUE.json、RUN_COVERAGE.csv：完整18+36+120队列及状态。\n'
        'SCALE_RESULTS.csv、PAIRED_RESULTS.csv、INITIAL_RESULTS.csv、INPUT_RESULTS.csv：所有结果缺失，状态NOT_RUN。\n'
        'inputs/：9原始文件字节、解析、10000目标分母、龄期、历史排除集和待运行ID。共享原料只存一次。\n'
        'source/：验收基线及本批新增盘点/收尾脚本；SOURCE_DIFF.patch为差异；不包含尚未实现的科学矩阵执行器。\n'
        'SOURCE_BINDING.json、prior_acceptance/：源代码与旧回执身份，原测试ZIP只校验哈希不重复打包。\n'
        'RESOURCE_RECORDS.json、BATCH_EVENTS.json：环境快照、中断和清理事实；缺少连续测量明确标注。\n'
        'RESUME_QUEUE.json、RESUME_PROMPT.txt：新批预算和准确断点。\n'
        'FILE_MANIFEST.json：除自身外每文件字节数与SHA256；自身身份由包外回执绑定。\n',encoding='utf-8')
    # Export review files beside the ZIP, with one authoritative copy inside payload.
    export=['EXPANSION_REPORT.txt','RESEARCH_PROTOCOL.json','RESEARCH_PROTOCOL.txt','SCALE_RESULTS.csv','PAIRED_RESULTS.csv',
            'INITIAL_RESULTS.csv','INPUT_RESULTS.csv','FAILURES_NOT_RUN.csv','RUN_COVERAGE.csv','RESUME_QUEUE.json','RESUME_PROMPT.txt','RESOURCE_RECORDS.json']
    for name in export: shutil.copyfile(payload/name,dest/name)
    # Scan for actual credential forms, never print matching secret text.
    patterns={
        'private_key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
        'github_token':re.compile(rb'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{30,}\b'),
        'openai_token':re.compile(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}\b'),
        'aws_access_key':re.compile(rb'\bAKIA[0-9A-Z]{16}\b')}
    findings=[]; scanned=0
    for p in payload.rglob('*'):
        if p.is_file():
            scanned+=1; data=p.read_bytes()
            for kind,pattern in patterns.items():
                if pattern.search(data): findings.append(dict(path=p.relative_to(payload).as_posix(),kind=kind))
    scan=dict(files_scanned=scanned,findings=findings,scope='known private-key/token patterns; no environment dumps or git metadata included',
        exhaustive_secret_detection_claim=False)
    write(payload/'CREDENTIAL_SCAN.json',scan)
    if findings: raise RuntimeError('credential-form review required; see paths in CREDENTIAL_SCAN.json')
    manifest={p.relative_to(payload).as_posix():ident(p) for p in sorted(payload.rglob('*')) if p.is_file()}
    write(payload/'FILE_MANIFEST.json',dict(schema='SHA256_MANIFEST_V1',self_excluded=True,files=manifest))
    archive=dest/'AUDIT_PACKAGE.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in sorted(payload.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(payload).as_posix())
    members_expected=set(manifest)|{'FILE_MANIFEST.json'}
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist(); names=[i.filename for i in infos]
        assert len(names)==len(set(names)) and set(names)==members_expected
        for info in infos:
            p=PurePosixPath(info.filename)
            assert not p.is_absolute() and '\\' not in info.filename and all(x not in ('.','..') and ':' not in x for x in p.parts)
            assert not ((info.external_attr>>16)&0o170000)==0o120000
        assert z.testzip() is None
        for name,entry in manifest.items():
            data=z.read(name); assert dict(bytes=len(data),sha256=sha(data))==entry
        assert z.read('FILE_MANIFEST.json')==(payload/'FILE_MANIFEST.json').read_bytes()
    protection={name:ident(original/name)==ident(prior/name) for name in ('FINAL_ACCEPTANCE.json','DELIVERY_RECEIPT.json')}
    assert all(protection.values())
    assert ident(original/'FAMOU_TEST_PACKAGE.zip')==prior_zip
    # Only task-owned files contribute to this task's observed final footprint.
    task_bytes=sum(p.stat().st_size for root in (work,dest) for p in root.rglob('*') if p.is_file())
    assert task_bytes<1216983040//4, 'task disk footprint exceeds original cap'
    verification=dict(verified_utc=stamp(),members=len(names),member_set=True,duplicate_names=False,CRC=True,path_safety=True,
        every_member_sha256=True,manifest_identity=ident(payload/'FILE_MANIFEST.json'),credential_scan=scan,
        old_accepted_files_unchanged=protection,old_test_zip_unchanged=True,
        measured_task_final_disk_bytes=task_bytes,original_task_disk_cap_bytes=1216983040//4,
        archive_build_and_verify_seconds=time.perf_counter()-started)
    write(dest/'ZIP_VERIFICATION.json',verification)
    delivery=dict(schema='BD_FMB_EXPANSION_DELIVERY_RECEIPT_V1',status='EXPIRED_BEFORE_SCIENTIFIC_RUN',generated_utc=stamp(),
        base_commit=base,source_commit=commit,protocol_status='DRAFT_NOT_FROZEN',
        scientific_results=dict(inputs_completed=0,inputs_planned=18,initial_completed=0,initial_planned=36,
            replans_completed=0,replans_planned=120,B_blocks_completed=0,B_blocks_planned=12,
            full_10000x10x144h=False,attempted_case_failures=0,all_cases_NOT_RUN=True),
        package=dict(path=str(archive),**ident(archive)),manifest=ident(payload/'FILE_MANIFEST.json'),
        verification=ident(dest/'ZIP_VERIFICATION.json'),review_files={name:ident(dest/name) for name in export},
        execution_claim='Only source/environment inspection and raw data inventory. No expanded solve, cold geometry or new quality evidence.',
        new_batch_budget_required=True,old_FINAL_ACCEPTED_not_replaced=True)
    write(dest/'DELIVERY_RECEIPT.json',delivery)
    assert read(dest/'DELIVERY_RECEIPT.json')['package']['sha256']==ident(archive)['sha256']
    print(json.dumps(dict(out=str(dest),archive=delivery['package'],source_commit=commit,members=len(names),task_bytes=task_bytes),ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('work','out','original','request'): p.add_argument('--'+name,required=True)
    build(p.parse_args())
