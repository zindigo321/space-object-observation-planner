# Team 3 Integration from the Extracted Source Package

Deliver baseline first. The source package contains small synthetic examples and requires no `.git` directory. Real data is distributed separately. The archive has an adjacent `.sha256` file. Its `MANIFEST.json` records the exact source commit, algorithm candidate `b0eb3b5`, file hashes, and packaging environment versions.

## 1. Environment and Quick Workflow

Use the **extracted source_kit directory** as your working directory. Its path may contain spaces or Chinese characters. Replace `python` below with the full path to your Python 3.11 interpreter if needed. The local trial reused the existing interpreter without reinstalling the environment.

```powershell
Set-Location 'path/to/extracted/source_kit'
$py = 'python'  # Use an active environment or the path to your python.exe.
# Install only in a new environment. This round did not perform a clean install.
& $py -m pip install -r requirements.txt
# Use a fresh output directory for each run.
& $py -X utf8 scripts/team3_run.py --python $py synthetic --out 'outputs/integration 01'
if ($LASTEXITCODE -ne 0) { throw 'Check workflow.json or the console before proceeding' }
```

If dependencies are already installed, run the last two lines. The script locates its code relative to its own path. Relative input and output arguments resolve from the current working directory, while internal commands run in the package root. `--python` selects the child interpreter and defaults to the interpreter running this script. The method defaults to baseline. Add `--method both` for comparison with the existing improved method. The run stages share a default 120-second budget. Set `--budget-seconds` before the subcommand to allow up to 300 seconds. The existing Windows Job Object or process group enforces child process time limits, and the workflow does not retry automatically. A nonzero exit stops dependent steps.

The workflow runs planning, independent evaluation of the initial tasks, independent evaluation of a valid fault, and a read-only recheck in order. In the new directory, `config.yaml` is the actual configuration and `run/` contains the plan. `evaluate_baseline/`, `evaluate_fault_baseline/`, and `recheck/` contain evaluations and the recheck. `cache/` is separate. `workflow.json` records the code import path, interpreter, versions, actual commands, exit codes, elapsed time, and whether the complete input and result trees stayed unchanged.

The local synthetic baseline trial scored 10.0 points and covered 3/3 targets initially. After the fault, it scored 3.0 points and covered 1/3. Both had zero violations. The small example validates the interface and uses a long simulated fault. Real algorithm gains require separate evidence. See the acceptance report adjacent to the released package for verification of the extracted package. Your integration confirmation is a separate step.

## 2. Standard Window Integration

Treat the received data as read-only. The four files must satisfy the [contract](io_contract.md). Inspect unfamiliar data first, then review the report and prepared configuration.

```powershell
& $py -X utf8 scripts/inspect_team1_input.py --input-dir '../local_demo_reference_kit/reference_windows' --source-label 'Official frozen reference, separate from Team 1 delivery' --out 'outputs/reference intake 01'
if ($LASTEXITCODE -ne 0) { throw 'Intake inspection failed' }
& $py -X utf8 scripts/team3_run.py --python $py windows --input-dir '../local_demo_reference_kit/reference_windows' --config 'outputs/reference intake 01/prepared_windows.yaml' --out 'outputs/reference integration 01'
if ($LASTEXITCODE -ne 0) { throw 'Integration failed' }
```

You can extract the two packages into adjacent directories. Set paths for the actual locations. For the formal Team 1 delivery, replace the input directory and provenance label. The prepared configuration reads the UTC horizon from the metadata and defaults to all stations in the table. See the [Team 1 intake guide](TEAM1_DATA_INTAKE.md) for selecting stations or a sub-horizon explicitly. After moving data, inspect it again or pass the new `--input-dir`. The wrapper resets the input and cache locations from the current input and new output. Old sealed JSON can stay as recorded.

Standard window mode uses all supplied targets, without seed resampling. It checks scheduling constraints within the supplied windows. Orbit propagation and independent physical verification of provider declarations about nighttime, illumination, weather, and other filters are outside this mode's scope. The reference package's historical per-second TLE evidence applies to its original source.

## 3. Read the Results

| File or field | Meaning |
| --- | --- |
| `run/tasks_baseline.csv` | Initial plan. The improved file is `tasks_improved.csv`. |
| `task_id,target_id,station_id` | Task, target, and station identifiers. Target and station IDs are positive decimal integers. |
| `start_utc,end_utc,duration_s` | Integer-second UTC start and end and duration in seconds. UTC format is `YYYY-MM-DDTHH:MM:SSZ`. |
| `status` | `success` for initial success, `completed` for completion before the fault, `locked` for preserved active work on a healthy station, `new_success` for new post-fault assignments, and `interrupted` for a separate zero-point segment. |
| `tasks_baseline_replanned.csv` | Baseline replan. The improved file is `tasks_replanned.csv`. |
| `fault_event.json,interrupted_baseline.csv` | Fault station and relative second interval, actual interrupted occupancy, and the original planned end. |
| `metrics.json → plans` | `task_score`, target `coverage`, counts by priority in `by_priority_coverage`, and `violation_count`. |
| `coverage_all` | Covered targets divided by all input targets. |
| `coverage_executable` | Covered targets divided by targets with a legal 120-second candidate in the full horizon. The denominator stays fixed after the fault. A zero denominator gives `rate=null`. |
| `checks/*.json` | Independent validation details. Evaluation recomputes score from original priorities and actual durations. |
| `timing.json,metrics.runtime` | Stage timings and total time within the child. Avoid adding totals from different layers. |
| `execution.json,workflow.json` | Process exits, timeouts, and outer wall time. Improved-method time includes internal baseline fallback. |

## 4. Run Evaluation Separately

The evaluator keeps the authoritative targets, windows, and initial plan under independent custody. The planner under evaluation should submit its task table without replacing those inputs.

```powershell
& $py -X utf8 scripts/team3_run.py evaluate --input-dir 'examples/synthetic' --config 'configs/synthetic.yaml' --tasks 'outputs/integration 01/run/tasks_baseline.csv' --out 'outputs/standalone evaluation 01'
if ($LASTEXITCODE -ne 0) { throw 'Evaluation failed' }
& $py -X utf8 scripts/team3_run.py evaluate --input-dir 'examples/synthetic' --config 'configs/synthetic.yaml' --tasks 'outputs/integration 01/run/tasks_baseline_replanned.csv' --initial-plan 'outputs/integration 01/run/tasks_baseline.csv' --event 'outputs/integration 01/run/fault_event.json' --interrupted 'outputs/integration 01/run/interrupted_baseline.csv' --out 'outputs/fault evaluation 01'
if ($LASTEXITCODE -ne 0) { throw 'Fault evaluation failed' }
& $py -X utf8 scripts/team3_run.py recheck --source 'outputs/integration 01/run' --out 'outputs/recheck 01'
```

Fault evaluation requires the initial plan, event, and interruption table together. Independent validation derives completed, locked, and interrupted sets from the initial plan before checking the submitted table. A task that ends exactly when the fault starts counts as completed. A task that starts exactly then does not count as locked. An interruption scores zero and still occupies the station for its actual duration. The target can be retried afterward.

For regular planning, inject a fixed fault with `synthetic/windows --fault-event FILE`. For external fault evaluation, use `evaluate --event FILE`. Event seconds are relative to the UTC start in the configuration. See the contract for fields. The wrapper uses the scoring and validation algorithms in `smoke_test.py`.

`evaluate --config` also accepts `run/effective_config.json` from a successful run. `recheck` loads that file automatically. Both read-only modes remove the historical planning field `fault_event_path` only from the in-memory configuration. They preserve source files and skip fault reinjection. Fault evaluation still requires the initial plan, event, and interruptions explicitly, and recheck still verifies the source results' sealed evidence. All standard window modes reject `reuse_source` and `frozen_sample`. Planning still requires `--fault-event` for explicit injection.

## 5. Handle Failures

| Exit code | Meaning and response |
| --- | --- |
| 0 | The requested workflow passed. Check the report and scope. Official scoring and physical certification require separate evidence. |
| 2 | Invalid input, a constraint violation, existing or nested output, or a contract mismatch. See `inspection.json`, `workflow.json`, console logs, and the checks. Fix a copy of the input and use a new output directory. |
| 3 | A required file is missing, the budget was insufficient or expired, or runtime conditions blocked execution. Supply the input or increase the budget up to 300 seconds where appropriate, then use a fresh directory. Partial output is insufficient for a pass. |

Path checks run before output creation, so the reason may appear only on the console. Invalid intake data generally leaves its first error in the new report directory. Later errors may not yet be listed. To retry, preserve prior outputs, original inputs, and protections.

## 6. Demo and Receipt

Open `demo/index.html` in the separate local package for offline, precomputed replay without Python or Node.js. The old E4 gain of 11.6 points on the E3/E4 page compares whole workflows with different initial plans. The E5 gain of 9.6 points belongs to its separate comparison table.

Complete the [integration receipt template](templates/TEAM3_RECEIPT.md). Team 3 confirmation is `PENDING_EXTERNAL`. This round covered local and fresh extraction directory verification. No message was sent or pass recorded on behalf of Team 3. Clean installation, full TLE reproduction on another machine, full optical verification, and official scoring remain unverified. The legacy optional evaluator remains `BLOCKED`.
