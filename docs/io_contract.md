# Scheduling and Evaluation Interface v1

This is the handoff contract for the 60-target smoke test. Formal competition rules require separate confirmation. Team 1 data delivery and Team 3 integration still await confirmation from both sides. Use UTF-8 for CSV and JSON. CSV files may include a BOM. `examples/synthetic` contains artificial data and serves as a test fixture.

## Directory Provided by Team 1

| File | Required fields | Types and constraints |
| --- | --- | --- |
| `targets.csv` | `target_id, priority, full_score` | Unique positive decimal IDs. Priority is `high`, `medium`, or `low`, with maximum scores of 5, 3, or 2. |
| `stations.csv` | `station_id` | Unique positive integer. This is the only field required for window scheduling. Apply equipment constraints when producing the windows. |
| `windows.csv` | `window_id, target_id, station_id, start_utc, end_utc` | Nonempty unique `window_id`, references to existing targets and stations, and a start before the end. |
| `metadata.json` | `schema_version, data_version, time_precision_s, horizon_start_utc, horizon_end_utc, filters_applied` | `schema_version=1`, `time_precision_s=1`, a nonempty version string, and a list of strings naming the filters actually applied. |

Use `YYYY-MM-DDTHH:MM:SSZ` and integer-second precision for UTC. The parser rejects local times, unspecified time zones, offsets, and fractional seconds. Durations are in seconds and maximum scores are in task points. The compatibility adapter converts Alpha-5 TLE numbers to decimal IDs. `window_id` should be stable under reordering.

Geometric windows include both endpoints. A task must fit entirely within one window, and resource occupancy uses the half-open interval `[start,end)`. Legal windows shorter than 120 seconds remain in the input and are recorded without producing candidates. Windows may overlap even when the station has capacity for only one task at a time.

The parser rejects unknown or duplicate IDs, missing fields, invalid times, incorrect priorities or maximum scores, and windows outside the metadata horizon. Station subsets and planning sub-horizons are configurable. Legal windows are clipped to the sub-horizon. Standard window mode uses all targets in the table. The seed and sample counts apply only to the TLE sampling path.

`filters_applied` should list applied filters such as elevation, nighttime, Earth shadow or target illumination, Sun and Moon avoidance, weather, and field of view. An empty list declares no filters. Provider declarations require separate physical verification. The TLE adapter computes geometric elevations from 10° to 85°. Full optical observability remains unverified.

## Configuration and Scheduling Function

Copy the complete configurations from `configs/smoke.yaml`, `configs/seed17.yaml`, `configs/seed23.yaml`, or `configs/synthetic.yaml`.

- Experiment parameters include `seed`, `sample_counts: {high, medium, low}`, `station_ids`, `start_utc`, `horizon_seconds` (or `start_utc` plus `end_utc`), `input_dir`, `input_mode`, `method`, the candidate grid, and the pruning limit.
- The assumptions for this round are durations of `[120,240]` seconds, earning 60% or 100% of maximum points, a 30-second changeover, and elevation of `[10,85]` degrees. The parser rejects configurations that deviate from these values. The contract defines no scoring for intermediate durations.
- `frozen_sample` can specify an existing frozen TLE sample. The seed, counts by priority, and raw input hashes must match. If omitted, freeze the sample in the new output directory before computing. Select the sample before seeing the results.
- `method` can be `baseline`, `improved`, or `both` for regression. `baseline` retains the original start-time-ordered greedy method. `improved` constructs a plan using priority, scarcity, and conflict loss, and falls back after lexicographic comparison of integer points and coverage with the baseline.
- The callable is `planner.scheduler.schedule(candidates, method='baseline', *, fixed=(), interrupted=(), clock)`. It takes internal integer-second candidate dictionaries and returns a new task list without mutating the input. `clock.check()` enforces the budget. Prefer the common command for CSV integration so callers can use the documented interface fields.

## Tasks and Independent Evaluation

`tasks_<method>.csv` is the handoff file. It contains at least `task_id,target_id,station_id,start_utc,end_utc,duration_s,status`. `schedule_*.csv` keeps the legacy format for byte-for-byte comparison with E0 and uses `satnum` as the target field. Additional fields `candidate_id,window_id,priority,start_s,end_s,points_int,score` support tracing and checks. Independent evaluation recomputes the score from original target priorities and actual UTC task durations. Unified output also cross-checks self-reported scores and source fields.

A target can succeed at most once across all stations. Tasks cannot overlap at the same station, and different targets require at least 30 seconds between tasks. The evaluator checks resource conflicts for interrupted occupancy. An interrupted task scores zero and its target may be observed again. Convert task points to integer points with `points_int = task_score * 5`.

Fault replanning also requires an independently retained initial task table, an event JSON file, and an interruption table.

- The event requires `station_id,start_s,end_s`. Seconds are relative to the configuration's start time. The fault occupies `[start_s,end_s)`. Produced event records also include UTC and an explanation of event selection.
- Keep an initial task as `completed` when `end_s <= fault start`.
- When `start_s < fault start < end_s`, a healthy station's task is `locked`. At the failed station, truncate it to `interrupted` and retain `planned_end_s,planned_duration_s,planned_end_utc`.
- A task is unexecuted when the fault occurs exactly at its start. Such a task is neither locked nor a zero-length interruption, and a healthy station can reschedule from that instant. A task that ends exactly at the fault is completed.
- Beyond these retained successes, successful tasks must have `status=new_success` and start at or after the fault. The history and interruption sets must match the independently derived results exactly. Status edits cannot add or remove history.
- The evaluator should retain the initial plan, windows, and original targets. The local manifest detects accidents and single-file tampering. It provides no digital signature to detect coordinated changes to all inputs and the manifest.

`--evaluate` independently evaluates a standard task table and checks the initial table first. Initial tasks with only required columns can be evaluated. For dynamic evaluation, preserve the full source columns to match history identity field by field. If `window_id` is absent, the evaluator identifies the matching window.

## Outputs and Exit Codes

Use a new directory for every `--out`. Source inputs, source results, cache directories, and outputs must not be nested. `--check-only --source ... --out ...` reads source evidence and writes reports, logs, and timings to a new directory. It saves before-and-after SHA-256 inventories of all files under the source.

| Status and exit code | Meaning |
| --- | --- |
| PASS / 0 | The requested core workflow finished and independent constraint checks passed. Optimality, official scoring, and teammate confirmation require separate evidence. |
| FAIL / 2 | Data error, changed evidence, or a constraint violation. See `failure.json` or the check reports. |
| BLOCKED / 3 | Missing required input, expired budget, failed runtime isolation, or an unresolved optional evaluator contract. |

An empty task table satisfies resource constraints and yields zero coverage and score. Without a valid fault demonstration, `fault_demo_status=BLOCKED`. The core run and optional secondary evaluation report separate statuses.

Main artifacts include `metrics.json` with actual task scores, overall coverage, coverage by priority, the executable denominator, window and candidate counts, violations, and stage times. `checks/*.json` contains detailed independent evidence. Other outputs include `effective_config.json`, `frozen_sample.json`, `input_hashes.json`, `standard_input/`, `cache.json`, `timing.json`, `execution.json`, and `evidence_manifest.json`.

Coverage rates use two denominators. Divide covered targets by all input targets for total coverage, and by targets with at least one legal 120-second candidate for executable coverage. A zero denominator yields `rate=null`. Fault results retain the full-horizon candidate denominator for comparison with the initial plan. TLE mode also checks elevation at each integer second in the scheduled interval. Window mode verifies the supplied windows. Their physical filters require separate verification.

The cache binds raw input hashes, sampled IDs, station parameters, the UTC start and duration, filters, coarse and fine sampling parameters, runtime dependency versions, and the adapter source hash. It also verifies the cache contents by hash. A single run has a total budget of at most 300 seconds. The parent guards the full process tree with a Windows Job Object or POSIX process group. After a timeout, it preserves available evidence and stops.
