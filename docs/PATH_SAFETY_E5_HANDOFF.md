# P1 Directory Protection Fix and E5 Shared Initial Plan Replanning Handoff

Run date: 2026-10-23, Asia/Shanghai. This round started at `97d41e6` on `work/path-safety-replan-e5`. The separate P1 commit was `341ac9e`. E5, its tests, and this document were included in subsequent commits. The scope excluded `main`, the original algorithm, the independent validator, and the existing real data.

This round's root, R, was `G:\bd-fmb\outputs\path_safety_e5_20261023_164001`. The earlier delivery, OLD, was `G:\bd-fmb\outputs\improvement_demo_20261023_150452`. Real artifacts are stored in ignored directories. The repository contains source code, synthetic tests, and documentation.

## P1 Reproduction and Fix Verification

Before the fix, `outputs/E0_seed42` was copied to `R\before_fix\sealed_source_copy`. The old main entry point was run on that copy with `nested_output` inside it as the destination. The original CLI returned 2, but it had created the output directory, an empty snapshots directory and an event file, and `frozen_inputs.json`. The evidence in `R\before_fix\reproduction.json` includes full before-and-after trees, the command, its exit code, and the old code hash. The old scripts, stderr and stdout, and the internal fixture ledger were retained. The original sealed source was excluded from the destructive test.

The fix is in `planner/path_safety.py`, `scripts/run_improvement.py`, and `scripts/budget_run.py`.

- Checks use resolved `Path` objects, ancestor relationships, and `samefile` identity for existing files. This covers relative paths, `..`, Windows case differences, directory junctions, and file aliases without relying on string prefixes.
- Before creating directories, ledgers, or logs, the main entry point reads the source, current configuration, and source configuration for every seed. It collects raw inputs, frozen samples, configurations, specifications, and event files. It checks the output, cache, ledger, atomic temporary files, and all generated log locations.
- `--prepare` runs its own preflight and exclusively creates a new experiment root. The main entry point leaves root creation to this stage. The ledger is kept outside the experiment root, typically in its parent. Commands from the original delivery still work.
- Aggregation checks actual CSV, Markdown, JSON, and temporary write targets individually. It allows aggregation in the parent directory and rejects destinations inside a sealed case or resolving to a protected input. The budget entry point also checks the actual ledger, temporary files, and logs before its first `mkdir`.
- Invalid paths return FAIL/2 and write to stderr before any directory creation, including empty directories. Resolving junctions and checking file identities provides a preflight check. Atomic protection against malicious concurrent link replacement was outside scope, and input files were not changed concurrently in this round.

After the fix, the same attack was repeated on a new complete copy of the source. The CLI again returned 2. The entire fixture tree and its file hashes were unchanged, and neither the ledger nor the output root was created. See `R\path_fix_verification.json`. The 14 new path tests covered the first, second, and third sources, equal and nested paths, `..`, case differences, raw inputs, invalid ledgers, generated logs and atomic temporary file hard links, direct preparation, aggregation in sealed locations, legitimate paths with an adjacent prefix, and real Windows directory junctions. All passed, including the junction test. A final check verified separately that the E5 acceptance aggregator rejects sealed locations. See `R\final_code_checks.json`.

## E5 Fixed Shared Starting Point

The authoritative input was `OLD\experiments\E4_seed42_late\initial_frozen_baseline.json`. It was cross-checked against the full task semantics of `schedule_baseline.csv` in the same directory and independently rescored at 173.2 points over 56 targets. Both methods started from this existing plan.

The case used seed 42, 60 targets, stations 1/2/3, the full UTC day on 2026-08-03, and 10060 frozen candidates. The physical event affected station 2 over `[3783,10983)`, or 01:03:03–03:03:03 UTC. The completed, locked, and interrupted history and the future candidates were derived once and frozen. Each method received its own in-memory copy. Content and order hashes were checked before and after each call. A source mismatch also caused rejection.

The shared input hashes are listed below. Semantic hashes use UTF-8, sorted keys, and compact JSON with the original list order. The overall conditions hash also includes source paths. Moving the directory can therefore change the source and overall hashes independently of the individual task semantics hashes.

| Content | SHA256 |
| --- | --- |
| Original shared initial JSON bytes | `1b37fab094cb6b2a9f0d99aa92d0c018d8ad02a4de14e42f1aba831b1963ec8c` |
| Shared initial plan semantics | `c68cda7770c5baea117199b77059d1237302cf40322a13583f42a4c5ffef7037` |
| Event semantics | `fe2fc5e3dc76aedbc721d4f1289cd0579685ad96477260962b0ff9ba9affca2c` |
| Full candidate set semantics | `e242dddb7dc0b69892328aecf5090455e10fe73b02f2f44735a3f725fb3ee407` |
| Future candidate semantics | `1fa13c6cff72706e706130aeb8b7cfe59eb28ca22c903b652a06471b164b5c18` |
| Fixed successful history semantics | `5f12d96af1c7a42bccec0926d5b443cb1cdc7fcbe36c6f70efab026c4907330a` |
| Interrupted history semantics | `b8020956192d1acbaa1020146ef62d8aa29ad2822c6850dfde22e38b2d02db65` |
| Overall shared conditions | `585404b8222cdcacc53127826603515a5a11be1ca2efc446cc975ff994db8d67` |

Machine-readable evidence is in `R\E5_common_baseline\shared\contract.json`, `common_inputs.json`, `conditions_baseline.json`, and `conditions_improved.json`. The shared snapshot and authoritative source were unchanged before and after the run. The contract prevents a method from substituting another initial plan, supplying its own history, or silently replacing candidates.

## E5 Results from This Round

Both methods had 14 completed tasks, 1 locked task at an operational station, 1 interrupted task at the failed station, and 2 originally scheduled future tasks affected by the fault. The fixed successful history comprised 15 tasks and 51.0 points. The interruption earned zero points. Its actual occupancy counted in validation, and that target could still be observed in full later.

| Method | Final score | Fixed history score | New task score | Coverage / all | Coverage / feasible | High / medium / low coverage | Violations | Replanning (s) | Independent validation (s) | Net adjustments |
| --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| baseline | 172.4 | 51.0 | 121.4 | 56/60, 93.33% | 56/56, 100% | 18/18/20 | 0 | 0.003326 | 0.330910 | 5 |
| improved | 182.0 | 51.0 | 131.0 | 56/60, 93.33% | 56/56, 100% | 18/18/20 | 0 | 0.083727 | 0.391897 | 23 |

The gain from the shared starting point was `(910−862)/5 = +9.6` points. The baseline added 0, removed 0, moved or changed the duration of 5, and retained 51. The improved method added 0, removed 0, moved or changed the duration of 23, and retained 33. The comparison excludes changes solely to task status or ID. For both methods, independent validation derived the completed, locked, and interrupted history from the shared original plan and confirmed an exact match.

The relaxed conditional upper bound was 182.0 points, comprising 51.0 from fixed history and 131.0 from the highest-scoring future candidate per unfixed target. Fixed successful targets are counted once. Interrupted targets may enter the future candidate set. The bound ignores resource conflicts. The baseline was 9.6 points below the bound and the improved method reached it. This single case establishes neither universal improvement across replanning scenarios nor general optimality. The earlier 184-point result used different history constraints and is not a required outcome here.

Reading inputs and preparing the validator took 0.097736 seconds. Independent validation of the shared initial plan took 0.273137 seconds. Preparing shared history and future candidates took 0.002353 seconds. Total internal time was 2.430907 seconds and the outer command including process startup took 3.196393 seconds. Totals include source seal hashing and snapshot serialization. Method timings cover each `schedule` call. Copying inputs, reading and writing, hashing, and independent verification are outside those timings. The improved method includes its internal baseline fallback. These are single-run `perf_counter` observations and establish no statistically significant speed advantage.

Complete results are in `R\E5_common_baseline\comparison.csv`, `comparison.md`, and `summary.json`. The same directory contains each method's tasks, interruptions, changes, independent reports, configuration, versions, and the shared initial plan. The seal manifest is `evidence_manifest.json`.

Member 4 can quote this conclusion directly. **With seed 42, the shared baseline initial plan, and the same later fault, the existing improved replanner scored 182.0 versus 172.4 for the baseline, a gain of 9.6 points. Coverage was identical, history was preserved, and independent per-second validation found zero violations. Net adjustments rose from 5 to 23, and this single improved run took longer to replan.**

## Acceptance and Scope for This Round

| Acceptance item | Observed result and evidence relative to R |
| --- | --- |
| Full test suite | 94 passed without skips, comprising 65 existing, 14 path, and 15 E5 conditions and history tests. See `pytest_e5.xml`. The suite took 25.92 seconds. |
| Shared condition integrity | Any mismatch in the initial plan, source, event, fixed or interrupted history, or full or future candidate set is rejected. Modified method inputs are also rejected. |
| Independent E5 validity | Both new plans passed checks against the original TLE at both endpoints and every internal integer second. All window, fault occupancy, resource, 30-second changeover, single-success, original-priority scoring, and exact-history checks passed. |
| E5 real-case history attacks | All 16 legitimate and attack cases behaved as expected. A separate shared-source mismatch was rejected. All attacks used complete copies and independent in-memory copies. See `E5_history_security_final/history_security.json`. |
| Scope of real backdating counterexamples | The backdated candidates independently passed real TLE and window checks. Isolation from all plan resource constraints is unverified. Each attack was required to trigger a history provenance violation. |
| Read-only E5 recheck | The full tree of 33 files and 3 directories was identical before and after. The initial plan and both new plans were independently validated again. See `E5_recheck/recheck.json`. |
| E3/E4 regression | All 16 plans across 4 cases were rerun and passed the real TLE checks. The 16 old-format task tables and 4 candidate tables were byte-identical. See `e3_e4_regression.json`. |
| Newly generated demo | `demo/index.html` was regenerated from this round's E3/E4 artifacts. The data check passed and all 33 actual Chrome interaction checks passed. See `browser/browser_checks.json` and the 3 screenshots. |
| Full protection of earlier artifacts | The full OLD delivery including the old HTML, the three original sealed sources, raw inputs, `requirements-lock.txt`, and `.gitignore` had identical trees and hashes. See `protected_before.json` and `protected_after.json`. |
| Compilation and final supplemental checks | PASS. See `final_code_checks.json` and ledger entries 17, 19, and 20. |
| External confirmation | Member 1's delivery and member 3's interface confirmation remain PENDING_EXTERNAL. No messages were sent and no confirmation was given on the team's behalf. |
| Earlier optional reevaluation | BLOCKED. No contract changes or extensions to the old budget were made. |
| Optional second shared starting point | NOT_RUN. This round reports only the requested shared baseline starting point. |
| Clean install, full optical validation, and formal scoring | Unverified. |

The demo presents the full E3/E4 workflow. E5 is delivered as its own comparison table because the previous E4 page's +11.6-point gain refers to E4. The new screenshots were reviewed and the old HTML bytes were preserved. Acceptance gates are individually recorded in `acceptance.json`. See `final_code_checks.json` for the final supplemental script checks.

The single budget ledger, `R\run_ledger.json`, records 20 serial controlled commands totaling 152.042 seconds, leaving 447.958 seconds of the 600-second budget. Each command completed as expected. The audited old CLI actually returned 2 and modified the copy before the fix. That outcome was retained as a counterexample. The first outer verification command returned 0 because the defect was successfully reproduced. The old ledger inside the fixture was an output of the entry point under test. All of its time was included in the first command and contributed no additional budget. Reading, editing, permission review waits, and writing time were outside the compute budget. Environment installation or upgrades, expanded samples, and parameter sweeps were outside scope.

## Running E5 for Member 3

Run the commands from `G:\bd-fmb` with the existing interpreter and dependencies. Exit code 0 is pass, 2 is failure, and 3 indicates missing inputs or a budget block. Use a new directory for every result and keep the ledger outside the result root. Existing results are protected from overwrite.

The E5 source must be a sealed real-TLE case with traceable raw inputs. `--initial-plan` accepts the shared JSON and defaults to the source's `initial_frozen_baseline.json`. `--event` accepts the fixed event. These arguments are specific to this entry point and independent of the original `smoke_test.py` run and evaluation modes. The initial plan must match the source's baseline CSV, and the event must match the source's later physical event. Both methods use the same initial plan and event arguments. The optional `--reference-method improved` selects another shared starting point, which was outside this run and should be reported separately.

The following commands reproduce the tests, E5, and the read-only recheck in a new directory with a new 600-second ledger. They require the existing local raw data and OLD artifacts, which are absent from a fresh clone.

```powershell
Set-Location G:\bd-fmb
$py = 'D:\conda_envs\bd-fmb\python.exe'
$r = 'outputs/e5_reproduce_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
$old = 'outputs/improvement_demo_20261023_150452/experiments/E4_seed42_late'

& $py -X utf8 scripts/budget_run.py --ledger "$r/run_ledger.json" --timeout 120 -- $py -X utf8 -m pytest tests -q --basetemp="$r/pytest_tmp" --junitxml="$r/pytest.xml"
if ($LASTEXITCODE) { throw 'Tests failed' }

& $py -X utf8 scripts/run_replan_e5.py --source $old --initial-plan "$old/initial_frozen_baseline.json" --event configs/late_fault.json --out "$r/E5" --ledger "$r/run_ledger.json"
if ($LASTEXITCODE) { throw 'E5 failed. Check the ledger and failure evidence.' }

& $py -X utf8 scripts/run_replan_e5.py --check-only --source "$r/E5" --out "$r/recheck" --ledger "$r/run_ledger.json"
if ($LASTEXITCODE) { throw 'Independent recheck failed' }

Import-Csv "$r/E5/comparison.csv" | Format-Table method,final_score,fixed_history_score,new_tasks_score,coverage,violations,replan_seconds,net_adjusted_targets
Get-Content "$r/E5/comparison.md" -Encoding UTF8
```

E5 uses the `shared_initial_replanning_v1` format. Both schedules are replanning results and the initial plan lives only in the shared snapshot. Use the dedicated read-only entry point above because the old `smoke_test.py --check-only` expects the earlier initial and replanning naming convention. The dedicated recheck reads the shared snapshot, each method's conditions, actual interruption tables, and new tasks. It calls the same independent original-TLE validator and records full before-and-after tree evidence. Recheck rejects substitutions of the initial plan or event.

As needed, continue with the same new ledger to verify the real-case history attacks and rebuild the E3/E4 demo.

```powershell
& $py -X utf8 scripts/budget_run.py --ledger "$r/run_ledger.json" --timeout 60 -- $py -X utf8 scripts/verify_e5_history.py --source "$r/E5" --out "$r/history_attacks"
if ($LASTEXITCODE) { throw 'History protection verification failed' }
& $py -X utf8 scripts/run_improvement.py --spec configs/improvement_demo.json --out "$r/experiments" --ledger "$r/run_ledger.json"
if ($LASTEXITCODE) { throw 'E3/E4 failed' }
& $py -X utf8 scripts/budget_run.py --ledger "$r/run_ledger.json" --timeout 60 -- $py -X utf8 scripts/build_demo.py --summary "$r/experiments/summary.json" --out "$r/demo"
if ($LASTEXITCODE) { throw 'Demo evidence check failed' }
Start-Process (Resolve-Path "$r/demo/index.html").Path
```

Open the demo already generated in this round directly, without recomputing.

```powershell
Start-Process 'G:\bd-fmb\outputs\path_safety_e5_20261023_164001\demo\index.html'
```

The automated browser regression still uses `node scripts/browser_demo_test.mjs HTML NEW_OUTPUT_DIRECTORY` under the outer budget entry point. Node 24 and a local Chrome or Edge installation are optional test tools. The self-contained HTML opens normally without Node or Python.

Member 3 should start with `status`, `shared_conditions`, `gain`, and `rows` in `summary.json` and review `checks/*.json` alongside the task files. Member 4 can use the E5 table and conclusion on this page while keeping the E3/E4 visuals and script within their original scope. The user and team are responsible for actual handoff and teammate confirmation. This round ended at this point with no additional scenarios.
