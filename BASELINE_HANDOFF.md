# Baseline Handoff for Team Members 1 and 3

This document preserves the original baseline handoff and its context. At the time of this update, the local experiments and independent audits had reached round 13. See the [current status](docs/CURRENT_STATUS.md) and [experiment log](EXPERIMENTS.md) for newer information. The user took over the roles of team members 1, 3, and 4 on the same machine. The earlier notes about missing Team 1 data and pending confirmation from Team 3 describe the period before that takeover. They do not affect the current workflow or establish acceptance by another person or machine. See the [team checklist](docs/team_questions.md) for formal rules and receiving environments. Real data stays local. The repository contains source code, configuration, documentation, and explicitly labeled synthetic examples. The [separate native no-fault contract](docs/NO_FAULT_NATIVE.md) documents the newer entry point. The baseline and fault commands below retain their original purpose.

## Environment and Startup

Use the existing environment directly. Run these commands in PowerShell.

```powershell
# Run from the local project root with the existing environment active.
$py = 'python'
& $py -X utf8 smoke_test.py --config configs/smoke.yaml --method baseline --out outputs/baseline_delivery_01
```

This defaults to local inputs under `prototype_v1/data_raw` and the original frozen seed42 sample. Use a path available on the target machine when moving the project. For a new Python 3.11 environment, run `python -m pip install -r requirements.txt`. Tests also require pytest. The original `requirements-lock.txt` is a complete local environment inventory preserved byte for byte in this round. Use `requirements.txt` for the minimal runtime dependencies.

Run the synthetic example when real data is unavailable.

```powershell
& $py -X utf8 smoke_test.py --config configs/synthetic.yaml --method baseline --out outputs/synthetic_delivery_01
```

`--out` must be a new directory. Change the final number on subsequent runs. Each case runs in a guarded child process with a total budget of at most 300 seconds. A timeout returns 3, preserves partial files, and terminates the process tree. The workflow only runs once per invocation.

## Team 1 Standard Window Integration

Supply `targets.csv`, `stations.csv`, `windows.csv`, and `metadata.json` as specified in the [I/O contract](docs/io_contract.md). Copy `configs/synthetic.yaml` and set `input_dir`, `station_ids`, the UTC start, and the horizon length to match the delivered data. Keep `input_mode: windows`. This path schedules all supplied targets directly from their windows and requires no TLEs or orbit propagation.

On the original machine, you can reuse the standard table export from the completed E0 run to verify the real-data window interface.

```powershell
& $py -X utf8 smoke_test.py --config configs/smoke.yaml --input-mode windows --input-dir outputs/E0_seed42/standard_input --method baseline --out outputs/window_delivery_01
```

The TLE compatibility path parses Alpha-5 identifiers, validates priorities and station locations, freezes the sample, and generates and caches geometric windows. When changing the seed, use `configs/seed17.yaml` or `configs/seed23.yaml`, or remove the old `frozen_sample` from the copied configuration before setting a new seed. The frozen seed42 sample belongs to seed42. `sample_counts` controls the count for each priority tier.

## Team 3 Consumption and Evaluation

Read `tasks_baseline.csv`. A task includes at least `target_id`, `station_id`, UTC start and end, `duration_s`, `status`, and `task_id`. `metrics.json` provides task scores, coverage denominators for all and executable targets, coverage by priority, and violations. `checks/` contains the independent validation evidence. Replanned tasks appear in `tasks_baseline_replanned.csv`, with the corresponding `fault_event.json`, `history_baseline.json`, and `interrupted_baseline.csv`.

Run a read-only recheck of a completed run.

```powershell
& $py -X utf8 smoke_test.py --check-only --source outputs/E0_seed42 --out outputs/recheck_delivery_01
```

The new directory contains `recheck.json` and the before-and-after source hashes in `source_hashes_before.json` and `source_hashes_after.json`. Use the current recheck command instead of the legacy one under `prototype_v1`.

Evaluate an external task table using the authoritative E0 targets and windows in this example.

```powershell
& $py -X utf8 smoke_test.py --config configs/smoke.yaml --input-mode windows --input-dir outputs/E0_seed42/standard_input --evaluate outputs/E0_seed42/tasks_baseline.csv --out outputs/evaluate_delivery_01
```

Evaluate external fault replanning.

```powershell
& $py -X utf8 smoke_test.py --config configs/smoke.yaml --input-mode windows --input-dir outputs/E0_seed42/standard_input --evaluate outputs/E0_seed42/tasks_baseline_replanned.csv --initial-plan outputs/E0_seed42/tasks_baseline.csv --event outputs/E0_seed42/fault_event.json --interrupted outputs/E0_seed42/interrupted_baseline.csv --out outputs/evaluate_fault_delivery_01
```

The evaluator must retain an independent copy of the initial plan so that the planner being evaluated cannot replace its history source. Evaluation recomputes scores from actual durations and original priorities. It ignores task-reported `score` values when computing those scores. Standard window mode verifies window constraints. TLE mode additionally checks actual elevation at each integer second. Full optical observability remains unverified.

Exit code 0 indicates `PASS` for the core workflow, 2 indicates `FAIL` due to invalid input or a constraint violation, and 3 indicates `BLOCKED` due to budget, missing input, or execution conditions. The [optional legacy evaluator](docs/optional_evaluator.md) remains `BLOCKED`. The main validator completes its own evaluation independently and reports its status separately.

## Regression Checks and Follow-Up

```powershell
& $py -X utf8 -m pytest tests -q
& $py -X utf8 smoke_test.py --config configs/seed17.yaml --out outputs/seed17_delivery_01
& $py -X utf8 smoke_test.py --config configs/seed23.yaml --out outputs/seed23_delivery_01
```

See the [experiment log](EXPERIMENTS.md) for actual runs. This section describes the original baseline delivery context. E3/E4, the demo, and E5 have since been completed and their historical records are available. See the [stable handoff](docs/STABLE_HANDOFF.md) and [Team 3 integration guide](docs/TEAM3_INTEGRATION.md) for the stable integration workflow.
