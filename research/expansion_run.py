"""Serial research controller with owned Windows jobs, per-stage limits and resumable receipts."""
import argparse, ctypes, hashlib, json, os, shutil, subprocess, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
import psutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(Path(__file__).resolve().parent))
from planner.process_guard import WindowsJob
from expansion_inventory import ident

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');os.replace(tmp,p)
def utc():return datetime.now(timezone.utc).isoformat()
def disk_bytes(root):return sum(p.stat().st_size for p in Path(root).rglob('*') if p.is_file())
def configure_job_memory(job,cap):
    from ctypes import wintypes as w
    class Basic(ctypes.Structure):
        _fields_=[('process_time',ctypes.c_int64),('job_time',ctypes.c_int64),('flags',w.DWORD),('min_ws',ctypes.c_size_t),('max_ws',ctypes.c_size_t),('active',w.DWORD),('affinity',ctypes.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
    class IO(ctypes.Structure):_fields_=[(k,ctypes.c_uint64) for k in ('r','w','o','rb','wb','ob')]
    class Extended(ctypes.Structure):
        _fields_=[('basic',Basic),('io',IO),('process_memory',ctypes.c_size_t),('job_memory',ctypes.c_size_t),('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]
    info=Extended();info.basic.flags=0x2000|0x200;info.job_memory=max(32*1024**2,cap-psutil.Process().memory_info().rss)
    if not job.api.SetInformationJobObject(job.handle,9,ctypes.byref(info),ctypes.sizeof(info)):raise ctypes.WinError(ctypes.get_last_error())

def monitor(argv,timeout,log,resource_root,config,deadline=None,rss_cap=None):
    start=time.monotonic();limit=min(start+timeout,deadline) if deadline else start+timeout
    cap=rss_cap or config['RSS_cap_bytes'];job=WindowsJob();configure_job_memory(job,cap)
    process=None;done=False;peak=0;cpus={};samples=[];next_disk=0;size=0;reason=None
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    try:
        Path(log).parent.mkdir(parents=True,exist_ok=True)
        with Path(log).open('wb') as stream:
            process=subprocess.Popen(list(map(str,argv)),cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,env=env,
                creationflags=0x4|subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            job.attach_and_resume(process)
            while process.poll() is None:
                now=time.monotonic();aggregate=psutil.Process().memory_info().rss
                try:
                    leader=psutil.Process(process.pid);owned=[leader]+leader.children(recursive=True)
                    for p in owned:
                        try:
                            aggregate+=p.memory_info().rss;t=p.cpu_times();cpus[str(p.pid)]=max(cpus.get(str(p.pid),0),t.user+t.system)
                        except psutil.NoSuchProcess:pass
                except psutil.NoSuchProcess:pass
                peak=max(peak,aggregate)
                if now>=next_disk:
                    size=disk_bytes(resource_root);next_disk=now+5
                    samples.append(dict(elapsed_s=now-start,aggregate_RSS=aggregate,task_disk_bytes=size,
                        available_memory=psutil.virtual_memory().available,system_CPU_percent=psutil.cpu_percent(interval=None)))
                if aggregate>cap:reason='RESOURCE_BLOCKED_RSS';break
                if size>config['working_disk_cap_bytes']:reason='RESOURCE_BLOCKED_DISK_ARCHIVE_RESERVE';break
                if now>=limit:reason='TIMEOUT';break
                time.sleep(min(.05,max(0,limit-now)))
            natural_code=process.poll();execution_s=time.monotonic()-start;tc=time.monotonic()
            cleanup=job.terminate_and_wait();done=True;process.wait(timeout=10);cleanup['seconds']=time.monotonic()-tc
        raw_code=process.returncode
        if reason is None:
            reason='PASS' if natural_code==0 else 'WORKER_FAILED'
            if time.monotonic()>limit:reason='TIMEOUT'
        result=dict(status=reason,raw_exit_code=raw_code,natural_exit_code=natural_code,execution_s=execution_s,
            wall_s=time.monotonic()-start,peak_sampled_aggregate_RSS_bytes=peak,CPU_seconds_sampled=sum(cpus.values()),
            CPU_seconds_by_pid_sampled=cpus,resource_samples=samples,task_disk_bytes_last_sample=size,
            timeout_budget_s=timeout,cleanup=cleanup,argv=list(map(str,argv)),thread_environment={k:env[k] for k in
            ('PYTHONDONTWRITEBYTECODE','PYTHONUTF8','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')},
            RSS_cap_bytes=cap,sampling_s=.05,disk_sampling_s=5,
            monitoring_limit='RSS/CPU sampling can miss sub-50ms peaks; disk writes can overshoot between 5s samples. Additional Job private-commit cap at RSS budget less controller RSS.',
            job_memory_limit=True,priority='BELOW_NORMAL',finished_utc=utc())
        write(Path(log).with_suffix('.resource.json'),result);return result
    finally:
        if process is not None and not done:
            try:job.terminate_and_wait()
            finally:
                if process.poll() is None:process.kill()
                process.wait(timeout=10)
        job.close()

def worker_argv(batch,phase,**kw):
    args=[batch['worker_python'],'-B','-X','utf8',str(ROOT/'research/expansion_worker.py'),phase]
    for k,v in kw.items():
        if v is not None:args+=['--'+k.replace('_','-'),str(v)]
    return args

def execute_case(batch,unit,case,out,input_dir,initial=None,global_deadline=None):
    out.mkdir(parents=True,exist_ok=False);started=time.monotonic();deadline=min(started+600,global_deadline) if global_deadline else started+600
    result=dict(case=case,attempt_id=out.name,started_utc=utc(),status='RUNNING',phases=[],input_manifest=ident(input_dir/'INPUT_MANIFEST.json'),
        initial_identity=ident(initial) if initial else None,source_commit=batch.get('source_commit'),protocol_sha256=batch.get('protocol_sha256'))
    write(out/'case.json',result)
    scene=case.get('scenario','I')
    try:
        for phase,cap in [('prepare',240),('solve',30),('evaluate',300)]:
            if time.monotonic()+1>=deadline:result['status']='PARENT_TIMEOUT';break
            if phase=='solve' and deadline-time.monotonic()<32:result['status']='PARENT_TIMEOUT_BEFORE_SOLVE30';break
            kwargs=dict(input=input_dir,initial=initial,inventory=batch['inventory'],scene=scene,method=case['method'],out=out/phase,
                seconds=cap,proposal=out/'solve/raw.json' if phase=='evaluate' else None)
            phase_result=monitor(worker_argv(batch,phase,**kwargs),cap,out/(phase+'.log'),batch['root'],batch,deadline)
            result['phases'].append(dict(phase=phase,**phase_result));write(out/'case.json',result)
            if phase_result['status']!='PASS':
                result['status']=phase_result['status'];result['failure_phase']=phase
                failure=out/phase/'worker_failure.json'
                if failure.exists():
                    result['worker_failure']=read(failure)
                    if result['worker_failure']['type']=='MemoryError':result['status']='OOM'
                    elif 'ILLEGAL_OUTPUT' in result['worker_failure']['message']:result['status']='ILLEGAL_OUTPUT'
                    elif result['worker_failure']['type']=='BudgetExpired':result['status']='TIMEOUT'
                break
        else:
            result.update(read(out/'evaluate/evaluation.json'));result['status']='PASS'
            initcheck=read(out/'prepare/initial_check.json')
            result['J_initial']=[initcheck['points_int'],initcheck['coverage']] if initcheck else None
        # Independently reopen shared bytes after all editable code has been terminated.
        t=time.monotonic();m=read(input_dir/'INPUT_MANIFEST.json')
        protection={name:ident(input_dir/name)==value for name,value in m['files'].items()}
        result['input_protection']=all(protection.values()) and ident(input_dir/'INPUT_MANIFEST.json')==result['input_manifest']
        result['initial_protection']=ident(initial)==result['initial_identity'] if initial else True
        result['protection_seconds']=time.monotonic()-t
        if not result['input_protection'] or not result['initial_protection']:result['status']='INPUT_MUTATION'
        if time.monotonic()>deadline and result['status']=='PASS':result['status']='PARENT_TIMEOUT'
    except Exception as e:
        result.update(status='CONTROLLER_FAILED',error=type(e).__name__+': '+str(e));traceback.print_exc()
    finally:
        result.update(wall_s=time.monotonic()-started,finished_utc=utc(),parent_budget_s=600,
            peak_sampled_aggregate_RSS_bytes=max([p['peak_sampled_aggregate_RSS_bytes'] for p in result['phases']],default=0),
            CPU_seconds_sampled=sum(p['CPU_seconds_sampled'] for p in result['phases']),
            all_owned_jobs_cleaned=all(p['cleanup']['confirmed'] for p in result['phases']))
        callfile=out/'solve/calls.jsonl'
        result['observed_solver_calls']=[json.loads(x) for x in callfile.read_text().splitlines()] if callfile.exists() else []
        write(out/'case.json',result)
    return result

def verify_source(batch):
    for name,identity in batch['source_files'].items():
        if ident(ROOT/name)!=identity:raise RuntimeError('frozen source changed: '+name)

def run(batch):
    root=Path(batch['root']);work=root/'work';queue=read(work/'PLAN.json')['queue'];results={}
    deadline_epoch=datetime.fromisoformat(batch['stop_new_cases_utc']).timestamp()
    for row in queue:
        cid=row['case_id'];caseout=work/'attempts'/(cid+'_a01')
        if caseout.exists() and (caseout/'case.json').exists():
            previous=read(caseout/'case.json')
            if previous['status']=='RUNNING':raise RuntimeError('unfinished attempt requires explicit recovery, never replay')
            results[cid]=previous;continue
        if time.time()>=deadline_epoch:
            results[cid]=dict(case=row,status='NOT_RUN',reason='BATCH_STOP_NEW_CASES_DEADLINE');continue
        blocked=[d for d in row.get('dependencies',[]) if results.get(d,{}).get('status')!='PASS']
        if blocked:
            results[cid]=dict(case=row,status='BLOCKED',reason='upstream_not_pass',dependencies=blocked)
            write(work/'RESULTS.json',results);continue
        verify_source(batch); print(json.dumps(dict(event='START',case_id=cid,time_utc=utc())),flush=True)
        global_deadline=time.monotonic()+max(0,deadline_epoch-time.time())
        input_dir=work/'inputs'/row['unit_id']
        if row['kind']=='cold_input':
            caseout.mkdir(parents=True,exist_ok=False)
            state=monitor(worker_argv(batch,'produce',spec=work/'specs'/(row['unit_id']+'.json'),inventory=batch['inventory'],
                out=input_dir,seconds=1800),1800,caseout/'produce.log',root,batch,global_deadline)
            state.update(case=row,attempt_id=caseout.name,source_commit=batch['source_commit'],protocol_sha256=batch['protocol_sha256'])
            if state['status']=='PASS' and not (input_dir/'INPUT_MANIFEST.json').exists():state['status']='PRODUCTION_INCOMPLETE'
            if (input_dir/'worker_failure.json').exists():
                state['worker_failure']=read(input_dir/'worker_failure.json')
                if state['worker_failure']['type']=='MemoryError':state['status']='OOM'
                elif state['worker_failure']['type']=='BudgetExpired':state['status']='TIMEOUT'
            if (input_dir/'progress.json').exists():
                try:state['progress']=read(input_dir/'progress.json')
                except Exception:state['progress_parse_error']=True
            write(caseout/'case.json',state)
        else:
            initial=work/'attempts'/(f"{row['unit_id']}_INIT_{row['origin']}_a01")/'evaluate/selected.json' if row['kind']=='replan' else None
            state=execute_case(batch,None,row,caseout,input_dir,initial,global_deadline)
        results[cid]=state;write(work/'RESULTS.json',results)
        counts={s:sum(r['status']==s for r in results.values()) for s in sorted({r['status'] for r in results.values()})}
        write(work/'LIVE_STATUS.json',dict(last_case=cid,last_status=state['status'],counts=counts,processed=len(results),planned=len(queue),updated_utc=utc()))
        print(json.dumps(dict(event='DONE',case_id=cid,status=state['status'],wall_s=state.get('wall_s'),counts=counts)),flush=True)
    write(work/'RESULTS.json',results);write(work/'RUN_FINISHED.json',dict(time_utc=utc(),processed=len(results),planned=len(queue)))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);a=p.parse_args();batch=read(a.batch)
    if batch.get('protocol_status')!='FROZEN':raise ValueError('scientific run requires frozen protocol')
    if ident(Path(batch['root'])/'work/RESEARCH_PROTOCOL.json')['sha256']!=batch['protocol_sha256']:raise ValueError('protocol binding changed')
    run(batch)
if __name__=='__main__':main()
