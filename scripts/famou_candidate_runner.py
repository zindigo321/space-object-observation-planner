"""Trusted supervisor: prepare40 / solve30 / write20 / evaluate80, total180."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from famou_common import ROOT,case_config,verify_fixed,write,identity
sys.path.insert(0,str(ROOT))
from planner.process_guard import run_guarded
from planner.no_fault import checked_output

BUDGETS={'prepare':40,'solve':30,'write':20,'evaluate':80}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',choices=['synthetic','H180_BASE','H180_IMP'],required=True)
    p.add_argument('--script',required=True);p.add_argument('--out',required=True)
    p.add_argument('--timeout',type=float,default=180,help='total cap; never increases solve30')
    a=p.parse_args()
    if not 0<a.timeout<=180:raise ValueError('workflow timeout must be in (0,180]')
    started=time.monotonic();deadline=started+a.timeout
    script=Path(a.script).resolve();out=checked_output(a.out,[ROOT,script]);out.mkdir(parents=True)
    work=out/'candidate_workspace';work.mkdir()
    receipt={'schema':'FAMOU_CANDIDATE_EXECUTION_V2','case':a.case,'formal_business_experiment':False,
             'budgets_seconds':BUDGETS,'total_budget_seconds':a.timeout,'phases':[],
             'timed_out':False,'exit_code':2,'status':'RUNNING'}
    def save():
        receipt['total_seconds']=time.monotonic()-started
        write(out/'candidate_execution.json',receipt)
    def phase(name,args):
        if time.monotonic()>=deadline:
            receipt.update(timed_out=True,status='TIMEOUT',failed_phase=name,exit_code=3);save();return False
        cmd=[sys.executable,'-I','-B','-X','utf8',*map(str,args)]
        row=run_guarded(cmd,timeout=BUDGETS[name],deadline_monotonic=deadline,
                        log_path=out/(name+'.log'),cwd=work)
        row.update(phase=name,command=cmd,budget_seconds=BUDGETS[name]);receipt['phases'].append(row)
        if name=='solve':receipt.update(command=cmd,solve=row)
        if name=='evaluate':write(out/'evaluator_execution.json',row)
        if row['timed_out'] or row['exit_code']!=0 or not row['cleanup']['confirmed']:
            receipt.update(timed_out=row['timed_out'],status='TIMEOUT' if row['timed_out'] else 'FAIL',
                           failed_phase=name,exit_code=3 if row['timed_out'] else 2);save();return False
        save();return True
    def maybe_identity(path):
        try:return identity(path)
        except OSError:return None
    try:
        seal=verify_fixed();source,sha,t=case_config(a.case)
        # Read once and bind exact copied bytes before any candidate code runs.
        candidate=work/'candidate.py';candidate.write_bytes(script.read_bytes())
        receipt.update(candidate=identity(candidate),executed_copy_path=str(candidate),
                       original_path=str(script),original_at_snapshot=identity(candidate))
        save()
        worker=ROOT/'scripts/famou_candidate_worker.py'
        prepared=work/'prepared.json';proposal=work/'proposal.json';fixed_csv=out/'proposal.csv'
        if not phase('prepare',[worker,'prepare','--source',source,'--source-sha256',sha,
                                '--decision-s',t,'--out',prepared]):return receipt['exit_code']
        receipt['prepared_identity']=identity(prepared)
        # Persist actual solve argv and copied identity before launch, even on crash.
        receipt['command']=[sys.executable,'-I','-B','-X','utf8',str(worker),'solve',
                            '--candidate',str(candidate),'--input',str(prepared),
                            '--package-root',str(ROOT),'--out',str(proposal)]
        receipt['executed_copy_before']=identity(candidate)
        if receipt['executed_copy_before']!=receipt['candidate']:
            raise ValueError('candidate copy changed before launch')
        save()
        solve_ok=phase('solve',receipt['command'][5:])
        receipt['executed_copy_after']=maybe_identity(candidate)
        receipt['executed_copy_unchanged']=receipt['candidate']==receipt['executed_copy_after']
        receipt['original_after']=maybe_identity(script)
        receipt['original_changed_during_run']=receipt['original_after']!=receipt['original_at_snapshot']
        save()
        if verify_fixed()!=seal:raise ValueError('candidate changed fixed manifest')
        if not receipt['executed_copy_unchanged']:raise ValueError('executed candidate copy changed')
        if not solve_ok:return receipt['exit_code']
        if identity(prepared)!=receipt['prepared_identity']:raise ValueError('prepared input changed')
        # Owned descendants are terminal before the trusted writer freezes the CSV.
        if not phase('write',[worker,'write','--input',proposal,'--prepared',prepared,'--out',fixed_csv]):return receipt['exit_code']
        receipt['proposal_identity']=identity(fixed_csv)
        if not phase('evaluate',[ROOT/'scripts/famou_evaluator.py','--case',a.case,
                                '--tasks',fixed_csv,'--proposal','--out',out/'evaluation']):return receipt['exit_code']
        if verify_fixed()!=seal or identity(fixed_csv)!=receipt['proposal_identity']:
            raise ValueError('fixed inputs or proposal changed during evaluation')
        if time.monotonic()>deadline:
            receipt.update(status='TIMEOUT',timed_out=True,exit_code=3,failed_phase='total');return 3
        receipt.update(status='PASS',exit_code=0);return 0
    except (ValueError,OSError,KeyError,RuntimeError) as e:
        receipt.update(status='FAIL',exit_code=2,reason=str(e))
        print(json.dumps({'status':'FAIL','reason':str(e)}),file=sys.stderr);return 2
    finally:save()

if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,KeyError,RuntimeError) as error:
        print(json.dumps({'status':'FAIL','reason':str(error)}),file=sys.stderr)
        raise SystemExit(2)
