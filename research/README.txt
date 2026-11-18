Expansion batch 20261117T125000Z_7f31

This directory contains the raw inventory, expired-batch archival tools and the
explicitly authorized continuation's serial scientific matrix controller.
The first G-drive batch expired during a conversation interruption before
calibration or scientific execution; its audit archive remains unchanged.
The continuation uses F because G had zero free bytes, with user approval.
Its separate 8-hour wall clock starts 2026-11-18T03:35:55Z. The old H180
acceptance is not a scientific result from this expansion.

Dependencies: Python 3.11, requirements-inventory.txt. The inventory execution
used the existing accepted environment with numpy 2.4.6, skyfield 1.55,
sgp4 2.27 and PyYAML 6.0.3. The archive tool additionally requires psutil.

Run inventory with a NEW output path:
python -B research/expansion_inventory.py --raw RAW_DIRECTORY --out NEW_INVENTORY_DIRECTORY --history-root PROJECT_ROOT

expansion_inventory.py and close_expired_batch.py never call the scheduler.
expansion_worker.py uses inherited whole-horizon geometry, candidate generation,
schedule, native no-fault selection and actual fault replay/history validation.
expansion_run.py supervises every stage in an owned Windows Job, measures RSS,
CPU and disk, preserves failures and blocks upstream-dependent cases.

Controller entry (requires BATCH.json with a hash-bound FROZEN protocol):
python -B -X utf8 research/expansion_run.py --batch ../work/BATCH.json

The controller interpreter requires psutil; worker_python in BATCH.json points
to the accepted Python 3.11 dependency environment. The controller and worker
may also use the same Python 3.11 environment after installing psutil.
All new-score production must follow calibration and freeze_expansion.py.
Calibration uses historical H180 only, and is not counted in the 36+120 matrix.
Target partitioning keeps each target's full horizon intact. No daily plan merge.
C has strict retained selection. F retains legacy selected=raw behavior, and
its fault-legal retained reference is not silently turned into a new guard.

Never restart a RUNNING attempt, extend a failed budget, or replay old formal
H180 requests. Use the delivery's RESUME_QUEUE.json / RESUME_PROMPT.txt, preserve
completed and failed attempts, and assign a new attempt ID for repairs.
