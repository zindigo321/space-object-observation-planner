"""Editable candidate template. Only this candidate file is an optimization surface."""
import argparse,sys,shutil
from pathlib import Path
def main():
    p=argparse.ArgumentParser()
    for n in ('package-root','source','source-sha256','out'):p.add_argument('--'+n,required=True)
    p.add_argument('--decision-s',type=int,required=True)
    a=p.parse_args();sys.path.insert(0,a.package_root)
    # Initial algorithm reuses the frozen baseline. Optimizers may replace this
    # candidate implementation, while retaining CLI and complete CSV contract.
    from planner.no_fault import produce
    import time
    started=time.monotonic();run=Path(a.out).parent/'baseline_internal'
    produce(a.source,a.source_sha256,a.decision_s,'baseline',run,lambda:150-(time.monotonic()-started))
    shutil.copyfile(run/'raw_proposal.csv',a.out)
if __name__=='__main__':main()
