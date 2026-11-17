"""Fixed independent CSV evaluator and strict retained-versus-candidate selection."""
import argparse,json,sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from famou_common import ROOT,case_config,verify_fixed,write,identity
sys.path.insert(0,str(ROOT))
from planner.io_contract import read_complete_tasks
from planner.no_fault import choose_from_files,evaluate,checked_output,write_tasks
from planner.no_fault_source import load_source
from planner.no_fault_rules import status_at
from planner.common import csv_write
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',choices=['synthetic','H180_BASE','H180_IMP'],required=True)
    p.add_argument('--tasks',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--proposal',action='store_true',help='Validate raw proposal, apply unchanged strict selection, then evaluate selected')
    a=p.parse_args();seal=verify_fixed();source,sha,t=case_config(a.case)
    tasks=Path(a.tasks).resolve();out=checked_output(a.out,[ROOT,tasks])
    if not a.proposal:
        code=evaluate(source,sha,t,tasks,out)
    else:
        s=load_source(source,sha);_,_,rows=read_complete_tasks(tasks)
        selected,receipt=choose_from_files(source,sha,t,rows)
        out.mkdir(parents=True)
        if receipt['selected_source']=='raw_proposal':
            shutil.copyfile(tasks,out/'selected.csv')
        else:
            retained=[dict(r,status=status_at({'start_s':int(r['start_s']),'end_s':int(r['end_s'])},t)) for r in s['initial_raw']]
            csv_write(out/'selected.csv',retained,s['initial_fields'])
        code=evaluate(source,sha,t,out/'selected.csv',out/'independent')
        report=json.loads((out/'independent/evaluation.json').read_text(encoding='utf-8'))
        write(out/'candidate_evaluation.json',dict(status='PASS',case=a.case,source_sha256=sha,
            proposal_identity=identity(tasks),selection=receipt,independent=report,
            authoritative_score=report['points_int'],coverage=report['coverage'],
            score_order='lexicographic (integer points, coverage); exact ties retain original',
            platform_callback=False))
    if verify_fixed()!=seal:raise ValueError('fixed manifest changed')
    print(json.dumps({'status':'PASS','evaluation':str(out)}))
    return code
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,KeyError) as e:
        print(json.dumps({'status':'FAIL','validity':0,'reason':str(e)}),file=sys.stderr);raise SystemExit(2)
