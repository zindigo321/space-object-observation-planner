"""Time-bounded candidate run followed by fixed evaluator in a separate process."""
import argparse,hashlib,json,os,shutil,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from famou_common import ROOT,case_config,verify_fixed,write,identity
sys.path.insert(0,str(ROOT))
from planner.process_guard import run_guarded
from planner.no_fault import checked_output
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',choices=['synthetic','H180_BASE','H180_IMP'],required=True)
    p.add_argument('--script',required=True);p.add_argument('--out',required=True)
    p.add_argument('--timeout',type=float,default=180)
    a=p.parse_args()
    if not 0<a.timeout<=180:raise ValueError('candidate timeout must be in (0,180]')
    seal=verify_fixed();script=Path(a.script).resolve();source,sha,t=case_config(a.case)
    out=checked_output(a.out,[ROOT,script]);out.mkdir(parents=True)
    work=out/'candidate_workspace';work.mkdir()
    shutil.copyfile(script,work/'candidate.py')
    result_file=work/'proposal.csv'
    cmd=[sys.executable,'-I','-B','-X','utf8',str(work/'candidate.py'),'--package-root',str(ROOT),
         '--source',str(source),'--source-sha256',sha,'--decision-s',str(t),'--out',str(result_file)]
    result=run_guarded(cmd,timeout=a.timeout,log_path=out/'candidate.log',cwd=work)
    result.update(command=cmd,candidate=identity(script),case=a.case,formal_business_experiment=False)
    write(out/'candidate_execution.json',result)
    if verify_fixed()!=seal:raise ValueError('candidate changed fixed manifest')
    if result['timed_out'] or result['exit_code']!=0:return 3 if result['timed_out'] else 2
    if not result_file.is_file() or result_file.is_symlink():raise ValueError('candidate did not produce a regular CSV')
    evaluate=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'scripts/famou_evaluator.py'),'--case',a.case,
              '--tasks',str(result_file),'--proposal','--out',str(out/'evaluation')]
    evaluation=run_guarded(evaluate,timeout=180,log_path=out/'evaluator.log',cwd=ROOT)
    evaluation.update(command=evaluate);write(out/'evaluator_execution.json',evaluation)
    if verify_fixed()!=seal:raise ValueError('fixed manifest changed')
    return 3 if evaluation['timed_out'] else 0 if evaluation['exit_code']==0 else 2
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,KeyError) as e:
        print(json.dumps({'status':'FAIL','reason':str(e)}),file=sys.stderr);raise SystemExit(2)
