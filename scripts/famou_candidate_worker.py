"""Fixed stage worker; candidate import and all editable code execute only in solve."""
import argparse,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase',choices=['prepare','solve','write'])
    for name in ('source','source-sha256','candidate','input','prepared','package-root'):
        p.add_argument('--'+name)
    p.add_argument('--decision-s',type=int);p.add_argument('--out',required=True)
    a=p.parse_args()
    if a.phase=='prepare':
        from planner.no_fault_source import load_source
        from planner.no_fault_rules import decision,status_at
        from planner.no_fault import verify_tasks
        source=load_source(a.source,a.source_sha256)
        decision(a.decision_s,source['context']['horizon'])
        retained=[dict(row,status=status_at(row,a.decision_s)) for row in source['initial']]
        verify_tasks(source,a.decision_s,retained)
        fixed=[row for row in retained if row['status']=='completed']+[row for row in retained if row['status']=='locked']
        ids={row['satnum'] for row in fixed}
        future=[dict(row,status='new_success') for row in source['candidates']
                if row['start_s']>=a.decision_s and row['satnum'] not in ids]
        value={'schema':'FAMOU_SOLVE_INPUT_V1','future':future,'fixed':fixed,'retained':retained,
               'fields':source['initial_fields'],'decision_s':a.decision_s,'source_sha256':a.source_sha256}
        Path(a.out).write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
    elif a.phase=='solve':
        value=json.loads(Path(a.input).read_bytes())
        spec=importlib.util.spec_from_file_location('editable_candidate',a.candidate)
        module=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=module
        spec.loader.exec_module(module)
        rows=module.solve(value)
        if not isinstance(rows,list) or not all(isinstance(row,dict) for row in rows):
            raise ValueError('solve(problem) must return a list of complete task rows')
        Path(a.out).write_text(json.dumps(rows,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    else:
        from planner.no_fault import write_tasks
        path=Path(a.input)
        if path.is_symlink() or not path.is_file() or path.stat().st_size>64*1024*1024:
            raise ValueError('proposal must be a regular JSON file of at most 64 MiB')
        rows=json.loads(path.read_bytes());prepared=json.loads(Path(a.prepared).read_bytes())
        if not isinstance(rows,list) or not all(isinstance(row,dict) for row in rows):
            raise ValueError('proposal must contain task dictionaries')
        write_tasks(a.out,rows,prepared['fields'])
    return 0

if __name__=='__main__':raise SystemExit(main())
