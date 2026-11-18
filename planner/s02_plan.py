"""S02 planning and independent raw-TLE evaluation in separate worker processes."""
from .common import TASK_FIELDS, csv_write
from .no_fault_rules import member, plan, status_at, validate_source, _report_with_pool
from .s02_input import RAW, StageClock, load, read, write

DECISION = 3600


def retained_rows(initial):
    return [dict(r,status=status_at(r,DECISION)) for r in initial]


def solve(input_dir, initial_path, method, out):
    from . import scheduler
    from .s02_native import NativeConstructors
    out.mkdir()
    clock = StageClock(30)
    native = NativeConstructors(out/'native.json')
    _, _, candidates, _ = load(input_dir)
    fixed = []
    future = candidates
    if initial_path:
        retained = retained_rows(read(initial_path))
        fixed = [r for state in ('completed','locked') for r in retained if r['status']==state]
        occupied = {r['satnum'] for r in fixed}
        future = [dict(r,status='new_success') for r in candidates if r['start_s'] >= DECISION and r['satnum'] not in occupied]
    # This process runs exactly one schedule. The legacy entry points retain their own constructors.
    scheduler.greedy = native.greedy
    scheduler.improved_construct = native.improved_construct
    proposal = scheduler.schedule(future,method,fixed=fixed,interrupted=[],clock=clock)
    write(out/'raw.json',proposal)
    csv_write(out/'raw.csv',proposal,TASK_FIELDS)
    native.report.update(status='PASS',method=method,proposed=len(proposal))
    write(native.receipt,native.report)


def evaluate(input_dir, initial_path, proposal_path, out):
    from .no_fault import _select_by_j
    from .validator import IndependentValidator
    out.mkdir()
    meta, windows, candidates, context = load(input_dir)
    initial = read(initial_path) if initial_path else []
    raw = read(proposal_path)
    pool = validate_source(context, initial, candidates)
    if any(not member(r,pool) or r['task_id'] != r['candidate_id'] for r in raw):
        raise ValueError('S02 proposal fields do not match original frozen candidates')
    retained = retained_rows(initial)
    if initial_path:
        raw_rules = _report_with_pool(context,initial,pool,DECISION,raw,False)
        jr, jp = raw_rules['J_retained'], raw_rules['J']
        selected, branch = _select_by_j(initial,retained,raw,jr,jp)
        selected_rules = _report_with_pool(context,initial,pool,DECISION,selected,True)
        write(out/'history_check.json',selected_rules)
    else:
        jp = list(plan(context,raw))
        if any(r['status'] != 'success' for r in raw):
            raise ValueError('S02 initial proposal status must be success')
        jr = [0,0]
        selected = raw
        branch = dict(branch='INITIAL_RAW',selected_source='raw_proposal',J_retained=jr,J_proposal=jp,J_selected=jp)
    v = IndependentValidator(dict(meta['config'],input_dir=str(RAW)),context['day'],meta['spec'],windows,StageClock(600))
    def geometry(rows,label,expected):
        report = v.check([dict(r,status='success') for r in rows],label=label)
        write(out/(label+'_evaluation.json'),report)
        if (report['status'] != 'PASS' or report['evaluation_scope'] != 'raw_TLE_per_second'
                or [report['points_int'],report['coverage']] != expected):
            raise ValueError('S02 independent TLE or score validation failed: '+label)
        return report
    rr = geometry(retained,'retained',jr)
    rp = geometry(raw,'raw',jp)
    # Selection is an exact row sequence from one of these two independently propagated plans.
    origin = 'raw' if branch['selected_source']=='raw_proposal' else 'retained'
    reference, report = (raw,rp) if origin=='raw' else (retained,rr)
    if selected != reference:
        raise ValueError('S02 selected row sequence differs from the independently evaluated plan')
    write(out/'selected_evaluation.json',dict(report,label='selected',evaluated_rows_from=origin))
    write(out/'selected.json',selected)
    csv_write(out/'selected.csv',selected,TASK_FIELDS)
    write(out/'branch.json',branch)
    write(out/'evaluation.json',dict(status='PASS',scene='C' if initial_path else 'I',
          decision_s=DECISION if initial_path else 0,targets=len(meta['records']),executable=1800,
          windows=len(windows),candidates=len(candidates),J_retained=jr,J_raw=jp,J_selected=branch['J_selected'],
          branch=branch['branch'],coverage_by_priority=report['by_priority_coverage'],violations=report['violation_count'],
          geometry='raw_TLE_per_second',selected_geometry_origin=origin,solver_calls=0))
