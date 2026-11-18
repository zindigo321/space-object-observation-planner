Expansion batch 20261117T125000Z_7f31

This directory contains read-only raw inventory and expired-batch archival tools.
It DOES NOT contain an implemented scientific matrix runner.
The first batch expired during a conversation interruption before calibration,
preregistration freeze, geometry production or scheduling. All scientific cases
are NOT_RUN. The old H180 acceptance is not a result from this expansion.

Dependencies: Python 3.11, requirements-inventory.txt. The inventory execution
used the existing accepted environment with numpy 2.4.6, skyfield 1.55,
sgp4 2.27 and PyYAML 6.0.3. The archive tool additionally requires psutil.

Run inventory with a NEW output path:
python -B research/expansion_inventory.py --raw RAW_DIRECTORY --out NEW_INVENTORY_DIRECTORY --history-root PROJECT_ROOT

No scheduler is imported or called by these tools. The inherited parser checks
individual TLE epochs; these are data checks, not cold experiment geometry.
Outputs explicitly distinguish prospective IDs from a frozen protocol.

To continue the research, use RESUME_PROMPT.txt / RESUME_QUEUE.json in the audit
delivery. A new batch budget, resource-guarded matrix driver, H180 development
calibration, chunk equivalence and protocol freeze are still required.
