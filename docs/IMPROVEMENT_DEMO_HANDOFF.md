# E3 / E4 and Offline Demo Handoff

Run date: 2026-10-23, Asia/Shanghai. The branch was `work/improvement-demo`, starting at `9765eb8`. This round inherited the existing greedy and improved construction methods and added frozen input reuse, a fixed physical fault entry point, validation, and a demo. It used the existing `planner/scheduler.py` and algorithm settings. Adding or tuning optimization algorithms was outside scope. `main` was unchanged.

## Delivery Artifacts

The root for this round was `G:\bd-fmb\outputs\improvement_demo_20261023_150452`, abbreviated as R below. Real data, target IDs, windows, HTML, and screenshots are stored only in ignored local directories.

- Open `R\demo_delivery\index.html` directly. It runs offline and requires no HTTP server or rerun of the solver.
- Three actual screenshots are `R\browser_delivery\01_seed17_improved_overview.png`, `02_late_fault_history.png`, and `03_late_replanned.png`.
- Comparison artifacts are `R\experiments\comparison.csv`, `comparison.md`, and `summary.json`.
- Final per-item acceptance is in `R\acceptance.json`. `experiments\summary.json` is the experiment snapshot from before the demo was built. Its demo status of NOT_RUN is supplemented by the final acceptance file, with the historical snapshot preserved.
- `R\run_ledger.json` records the commands, start and end times, exit codes, logs, and budget.
- Complete per-case evidence is in `R\experiments\E3_seed42`, `E3_seed17`, `E3_seed23`, and `E4_seed42_late`.
- The 60–90 second script is in [DEMO_SCRIPT.md](DEMO_SCRIPT.md). A video was outside the required delivery scope.

## Measured Comparison

All tasks used the full UTC day on 2026-08-03, three stations, and 20 targets in each priority tier. Each seed's sample, windows, candidates, and original physical event were frozen before both methods ran. The two methods consumed the same complete candidate table. Candidate bytes matched the original reference, and frozen sources and raw inputs retained their hashes. Machine-checkable evidence is available in `frozen_inputs.json`, each case's `input_reuse.json` and `event_provenance.json`, and `summary.json.fairness`.

For the same E3 seed, the physical fault affected station 1 from 00:02 to 02:02 UTC. Task IDs and impacts from the source plan are retained as provenance notes. The impacts were recalculated for each method. All four plans passed independent checks against the original TLE at both endpoints and each internal integer second, with zero violations.

| Seed | Method | Initial task score | Post-fault task score | Initial gain | Post-fault gain | Coverage / all | Coverage / feasible | Initial / post-fault violations | Initial upper bound | Gap to bound (initial / post-fault) |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- |
| 42 | Baseline | 173.2 | 172.4 | 0 | 0 | 56/60, 93.33% | 56/56, 100% | 0/0 | 184.0 | 10.8/11.6 |
| 42 | Improved | 184.0 | 184.0 | +10.8 | +11.6 | 56/60, 93.33% | 56/56, 100% | 0/0 | 184.0 | 0/0 |
| 17 | Baseline | 180.0 | 182.0 | 0 | 0 | 57/60, 95% | 57/57, 100% | 0/0 | 190.0 | 10.0/8.0 |
| 17 | Improved | 190.0 | 190.0 | +10.0 | +8.0 | 57/60, 95% | 57/57, 100% | 0/0 | 190.0 | 0/0 |
| 23 | Baseline | 178.2 | 176.2 | 0 | 0 | 57/60, 95% | 57/57, 100% | 0/0 | 189.0 | 10.8/12.8 |
| 23 | Improved | 189.0 | 189.0 | +10.8 | +12.8 | 57/60, 95% | 57/57, 100% | 0/0 | 189.0 | 0/0 |

For each case, coverage rates and counts by priority tier were identical across methods and between the initial and replanned results. The tables list the shared tier counts once. The feasible denominator is the number of targets with a valid 120-second candidate in the full planning horizon and is held constant after the fault.

| Seed | Targets / stations | Windows | Candidates before pruning / used | High / medium / low coverage | Data and window preparation (s) | Candidate generation (s) | Total independent validation across both stages (s) | Case process (s) |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| 42 | 60/3 | 563 | 54699/10060 | 18/18/20 | 0.104207 | 0.148827 | 1.097638 | 2.230404 |
| 17 | 60/3 | 533 | 56685/9536 | 19/19/19 | 0.091672 | 0.146627 | 1.175994 | 2.243093 |
| 23 | 60/3 | 538 | 100072/9158 | 19/18/20 | 0.100722 | 0.163738 | 1.149018 | 2.264886 |

| Seed | Method | Initial scheduling (s) | Replanning (s) | Completed / locked / interrupted / affected future | Targets with net adjustments |
| --- | --- | ---: | ---: | --- | ---: |
| 42 | Baseline | 0.004036 | 0.012719 | 0/2/1/7 | 13 |
| 42 | Improved | 0.141064 | 0.101614 | 0/2/1/5 | 7 |
| 17 | Baseline | 0.005196 | 0.009572 | 0/1/1/9 | 11 |
| 17 | Improved | 0.095264 | 0.095637 | 0/1/1/5 | 7 |
| 23 | Baseline | 0.003513 | 0.011759 | 0/2/1/9 | 11 |
| 23 | Improved | 0.093631 | 0.097046 | 0/1/1/7 | 11 |

Timing uses `perf_counter()`. E3/E4 data preparation reused sealed windows (`sealed_source_reuse`), so it excludes cold-start propagation for window generation. Independent task validation still propagated the original TLE. Each improved-method timing includes the cost of its internal greedy fallback. The validation total covers both methods. Case process time includes startup, counterexamples, and evidence writes. See `timing.json` and `execution.json` in each case. The outer ledger records the full command time separately, without adding the phases again.

The upper bound was recomputed from this round's candidates by summing the maximum integer candidate points per target and ignoring station resource conflicts. The table shows the initial candidate bound and gaps to it. It provides no exact post-fault bound or proof of general optimality. E3 compares the full initial scheduling and replanning workflow using different initial plans. The gain cannot be attributed to the replanner alone. The three seeds provide a descriptive comparison. The seed 17 baseline's higher post-fault score came from changes such as selecting different task durations and establishes no benefit from the fault.

## Later Fault E4

Seed 42 used a fault at station 2 over relative seconds 3783–10983, or 01:03:03–03:03:03 UTC. The event is in `configs/late_fault.json` and was used for E4 alongside the existing E3 cases.

| Method | Completed | Locked at operational station | Interrupted at failed station | Affected future | Initial / post-fault score | Post-fault gain over baseline | Initial / replanning (s) | Net adjustments |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- | ---: |
| Baseline | 14 | 1 | 1 | 2 | 173.2/172.4 | 0 | 0.004244/0.008077 | 5 |
| Improved | 10 | 1 | 1 | 4 | 184.0/184.0 | +11.6 | 0.111321/0.150969 | 18 |

Both methods covered 56/60 and 56/56 targets, with 18/18/20 in the high, medium, and low tiers. Initial and replanned results had zero violations. E4 used window reuse and took 0.116349 seconds for preparation, 0.228923 seconds for candidate generation, 1.164077 seconds for independent validation, and 2.439516 seconds for the case process. The baseline moved or changed the duration of 5 tasks and retained 51. The improved method moved or changed the duration of 18 and retained 38. Both added and removed 0. Changes are compared by target, station, UTC start and end, and duration. Status and task ID differences are ignored. The count of tasks canceled and then replanned is separate from net adjustments.

`initial_frozen_<method>.json` is saved separately after initial scheduling. The independent validator derives the completed, locked, and zero-point interrupted sets to preserve from that original plan. It operates independently of the planner's reported history and scheduling conflict function. An interrupted segment retains its originally planned end time and duration, and its actual occupancy is checked for resource conflicts.

The real-case attack validation is in `R\history_security_v2`. Each method had one valid control and seven attacks, and all 16 behaved as expected. Removing completed or locked tasks, removing or forging interruptions, and backdating `success`, `completed`, or `locked` before the fault were all rejected with a required history provenance violation. For the baseline, no backdated candidate was found that was resource-compatible with every replanned task. The case used a candidate from an original valid window and retained the additional resource violation. See `backfill_resource_isolated` and the per-case reports for the recorded scope. The existing synthetic counterexamples that isolate history violations continued to pass.

## Acceptance, Environment, and Budget

| Stage | Observed result | Evidence relative to R |
| --- | --- | --- |
| Algorithm execution and candidate/event fairness | PASS, 4 cases × 4 plans | `experiments/summary.json` and manifests in each directory |
| Independent real orbit validity | PASS, all integer-second checks with zero violations | Each case's `checks/` |
| History protection | PASS, 16 real-case valid controls and attacks | `history_security_v2/history_security.json` |
| Default entry-point compatibility | PASS, four old-format task CSVs and the candidate CSV were byte-identical | `delivery_verification/verification.json` |
| Read-only recheck | PASS, SHA256 identical for all 56 files before and after | `recheck_late/recheck.json` and before-and-after hash files |
| Reproduction in a new directory | PASS, all four task tables and candidates matched and per-second validation was rerun | `delivery_verification/workspace` and `result` |
| Automated tests | 65 passed, comprising 43 existing and 22 new tests, in 19.03 seconds | `pytest_pass.xml` and `command_18.log` |
| Demo data | PASS, task scores, integer points, coverage denominators and tiers, and validation reports matched | `demo_delivery/demo_data_check.json` |
| Actual demo browser interactions | PASS, 33 checks, 3 screenshots, and no runtime exceptions | `browser_delivery/browser_checks.json` |
| Raw data and three older source directories | PASS, identical hashes before and after | `acceptance.json` and each `input_reuse.json` |
| Member 1's data delivery and member 3's confirmation | PENDING_EXTERNAL | No delivery or confirmation received and no messages sent |
| Earlier optional reevaluation | BLOCKED | Original SHA256 and event contract issues remain isolated |
| Clean installation and video | NOT_RUN | Outside the completed verification |

The checks used local Chrome through DevTools to exercise all 4 cases × 2 methods × 3 views. They also checked the later-fault seed restriction, zoom, task clicks, stepping, play, pause, and the absence of page-level overflow at a narrow width. The browser opened the local file under offline network conditions. Normal use requires no Node installation. Screenshots were reviewed manually and showed distinguishable initial, locked and interrupted, and replanned views.

This round's 27 serial compute and test commands took 147.226 seconds, leaving 452.774 seconds of its 600-second budget. There were 21 PASS and 6 FAIL results, with logs retained for each and no budget timeouts. The budget was authorized for this round. The earlier optional reevaluation kept its original deadline. Each command had its process tree constrained by a Windows Job Object, with a per-command limit capped at 300 seconds and the remaining budget at that point.

Retained failures include command 8, where the history script found no resource-isolated candidate. Commands 10, 12, and 13 encountered browser connectivity, Chrome sandbox compatibility, and SVG click invocation issues. Command 16 hit permissions on the system temporary directory used by pytest. Command 17 encountered missing cache guidance for the synthetic windows run. Verification passed after adjusting fixture assertions, browser connections and input handling, switching to a project temporary directory, and completing the window-mode cache instructions. Ordinary errors retained FAIL status, and failed result directories were preserved.

The default entry-point regression encountered a real cache miss. Window propagation took 25.623 seconds and the outer command took 29.084 seconds. Cache identity was left as generated. Reproduction in a new directory used the same installed environment and prepared read-only artifacts. `requirements-dev.txt` pins the tested pytest 9.1.1 release. No packages were installed or upgraded during the round. The original `requirements-lock.txt` remained untracked with its original bytes.

## Copyable Commands

Run directly in the existing environment. A new environment can use the minimum dependency installation below. Installation was outside the executed checks for this round.

```powershell
Set-Location G:\bd-fmb
$py = 'D:\conda_envs\bd-fmb\python.exe'
# Install only for a new environment. Runtime uses requirements.txt, while tests use requirements-dev.txt.
& $py -X utf8 -m pip install -r requirements-dev.txt
```

Reproduction requires the local raw inputs and the three older sealed results referenced by `configs/improvement_demo.json`. It requires the sample and windows for each seed. For a fresh clone, start with the [synthetic example](../demo/README.md). These commands create a new 600-second ledger in a new directory.

```powershell
Set-Location G:\bd-fmb
$py = 'D:\conda_envs\bd-fmb\python.exe'
$r = 'outputs/reproduce_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
& $py -X utf8 scripts/run_improvement.py --spec configs/improvement_demo.json --out "$r/experiments" --ledger "$r/run_ledger.json"
if ($LASTEXITCODE -ne 0) { throw 'Experiment failed. Check the ledger and logs first.' }
& $py -X utf8 scripts/budget_run.py --ledger "$r/run_ledger.json" --timeout 60 --output "$r/recheck" -- $py -X utf8 smoke_test.py --check-only --source "$r/experiments/E4_seed42_late" --out "$r/recheck"
if ($LASTEXITCODE -ne 0) { throw 'Read-only recheck failed' }
& $py -X utf8 scripts/budget_run.py --ledger "$r/run_ledger.json" --timeout 60 --output "$r/demo" -- $py -X utf8 scripts/build_demo.py --summary "$r/experiments/summary.json" --out "$r/demo"
if ($LASTEXITCODE -ne 0) { throw 'Demo evidence check failed' }
Start-Process (Resolve-Path "$r/demo/index.html").Path
```

Build a new demo from the delivered results without recomputing orbits.

```powershell
$py = 'D:\conda_envs\bd-fmb\python.exe'
$source = 'G:\bd-fmb\outputs\improvement_demo_20261023_150452\experiments\summary.json'
$htmlOut = 'G:\bd-fmb\outputs\demo_copy_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
& $py -X utf8 G:\bd-fmb\scripts\build_demo.py --summary $source --out $htmlOut
if ($LASTEXITCODE -eq 0) { Start-Process "$htmlOut/index.html" }
# Open the delivered HTML directly.
Start-Process 'G:\bd-fmb\outputs\improvement_demo_20261023_150452\demo_delivery\index.html'
```

These optional rechecks continue from the new `$r` above. Run commands one at a time and check each exit code. Use new output directories and a new pytest basetemp to avoid permission problems or cleanup of existing temporary directories.

```powershell
& $py -X utf8 scripts/budget_run.py --ledger "$r/run_ledger.json" --timeout 120 -- $py -X utf8 -m pytest tests -q --basetemp="$r/pytest_tmp" --junitxml="$r/pytest.xml"
& $py -X utf8 scripts/budget_run.py --ledger "$r/run_ledger.json" --timeout 60 --output "$r/history" -- $py -X utf8 scripts/verify_late_history.py --source "$r/experiments/E4_seed42_late" --out "$r/history"
& $py -X utf8 scripts/budget_run.py --ledger "$r/run_ledger.json" --timeout 60 --output "$r/browser" -- node scripts/browser_demo_test.mjs "$r/demo/index.html" "$r/browser"
```

Automated browser tests require Node 24 and local Chrome, which defaults to `C:/Program Files/Google/Chrome/Application/chrome.exe`. To use Edge, supply its executable path after the HTML and output-directory arguments. The test-only `--no-sandbox --disable-gpu` flags apply to controlled automation of locally generated pages, with the outer budget entry point terminating the entire process tree. Open the HTML normally without these flags.

`--reuse-source` and `--fault-event` apply only to normal runs. `--fault-event` strictly checks the integer station ID and relative seconds, station existence, a valid interval, and UTC consistency. `--event` is reserved for external task evaluation and returns FAIL if used in a normal run. The default entry point uses the existing behavior when these new options are omitted.

## Handoff to Members 3 and 4 and the Team Lead

Member 3 can use the unified `smoke_test.py` entry point or the existing `schedule()` interface. Read task CSVs, `fault_impacts.json`, `changes_<method>.json`, and each plan's `checks/*.json`. Use the exit code as the outcome: 0 for success, 2 for failure, and 3 for blocked. The files alone do not establish success. See [io_contract.md](io_contract.md) for the input and output contract. Member 1's data version, window filtering, success counting and interruption rules, and the actual integration commands still require external confirmation. The artifacts are ready for review, and confirmation is up to the relevant teammate.

Member 4 and the team lead can use the offline HTML, three screenshots, talk script, and comparison table on this page. Explain the frozen sample, task scoring conventions, and comparison of the full workflow. Real artifacts stay outside Git. The user handles any handoff via team channels. This round sent no messages or real data uploads.

This was a smoke demo of real orbital geometry. Full optical conditions were outside the validation scope, including night conditions, illumination, Sun and Moon avoidance, weather, tracking, field of view, terrain, and state estimation. The window grid and per-second checks establish neither continuous-time validity nor window completeness. Task scores use their own scale rather than the formal 100-point scoring scale. Larger target counts, stress sweeps, cloud-based evolution, and repairs to the earlier optional reevaluation were outside scope.
