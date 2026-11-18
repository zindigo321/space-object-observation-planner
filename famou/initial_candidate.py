"""Editable solve(problem) template. Every line runs inside the parent's 30s cap."""
def solve(problem):
    from pathlib import Path
    from planner.no_fault_clock import NativeSolverClock
    from planner.scheduler import schedule
    # This cooperative clock never replaces the trusted parent's hard cutoff.
    solver_dir=Path('solver');solver_dir.mkdir()
    clock=NativeSolverClock(solver_dir)
    try:
        clock.activate()
        return schedule(problem['future'],'baseline',fixed=problem['fixed'],interrupted=[],clock=clock)
    finally:clock.logfile.close()
