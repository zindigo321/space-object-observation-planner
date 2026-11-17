"""Public-cloud file/CLI adapter; this is not a claimed Baidu SDK callback."""
import argparse,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from famou_common import ROOT,case_config,verify_fixed
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',choices=['synthetic','H180_BASE','H180_IMP'],required=True)
    p.add_argument('--method',choices=['baseline','improved'],default='baseline')
    p.add_argument('--out',required=True)
    p.add_argument('--budget-seconds',type=float,default=180)
    a=p.parse_args();seal=verify_fixed();source,sha,t=case_config(a.case)
    cmd=[sys.executable,'-B','-X','utf8',str(ROOT/'scripts/team3_run.py'),'--budget-seconds',str(a.budget_seconds),
         'no-fault','--source',str(source),'--source-sha256',sha,'--decision-s',str(t),'--method',a.method,'--out',a.out]
    result=subprocess.run(cmd,cwd=ROOT)
    if verify_fixed()!=seal:raise ValueError('fixed manifest changed')
    return result.returncode
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,KeyError) as e:
        print(json.dumps({'status':'FAIL','reason':str(e)}),file=sys.stderr);raise SystemExit(2)
