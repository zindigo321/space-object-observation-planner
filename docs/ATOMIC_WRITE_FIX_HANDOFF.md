# Temporary File Hard-Link Fix Handoff (2026-10-23)

This round created `work/atomic-write-hardening` from `b504f93` on `work/path-safety-replan-e5` to fix truncation caused by preplanted hard links during atomic writes. The scheduler, candidate generation, independent validator, algorithm parameters, and demo interface were outside the scope of the fix. The original branch and `main` were retained. See the local `delivery_git.json` and the handoff reply for the final commit and push receipt.

The sole output root for this round was `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047`, abbreviated as R below. The actual control ledger was `R\control\run_ledger.json`, separate from all attack fixtures. The designated location for future handoff prompts is `G:\bd-fmb_local\handoff`, outside the project. This round added no prompts to the former `_local/handoff` directory. Project code and handoff documents live in the project.

## Evidence Before and After the Fix

The original `guard_writes([ledger.tmp], [raw_directory])` compared directory paths and checked the two endpoints with `samefile`. This missed a hard link outside the directory pointing to a file inside it. The budget save then truncated the fixed `ledger.tmp` path, corrupting the input even when the CLI later returned 2. Tests that protected a file directly did not cover this directory-level case.

This round created hard links only for synthetic `raw/input.txt` files. Real inputs, configurations, and historical artifacts were excluded. The two fixture locations were `R\before_fix\budget_execute\{raw\input.txt,ledger.tmp}` and `R\before_fix\full_experiment_cli\{raw\input.txt,ledger.tmp}`. After the fix, equivalent fixtures were recreated under a separate `after_fix` directory.

| Actual invocation | Before the fix | After the fix |
| --- | --- | --- |
| Budget `execute` with the raw directory protected | `samefile=true`. The guard returned ALLOWED. The intentionally failing command returned 2. The original text became ledger JSON and the old alias was removed. | `samefile=true`. The guard returned ALLOWED. The atomic save succeeded and the intentionally failing command still returned 2. The full raw directory tree and the old alias were preserved. |
| Full `run_improvement.py` entry point with the raw directory protected | Preparation succeeded and the intentionally incomplete configuration later produced exit code 2. The original text had already become ledger JSON. | Preparation succeeded, followed by the same exit code 2. The full raw tree, its hashes, and the old alias were preserved, and the three sealed synthetic sources were unchanged. |

The original synthetic text had SHA256 `dc7299a5dd1289ef57bac22a5c720a2089af8cbcf437bb7a5b8f9751af02a19d`. Before the fix, it became `8eb610ad03bf692726835778adccafee04aac97f6867fe837f08235d9599c6b4` in the budget case and `2e5dcd4c7254201b1efc82205e25b11bd84d047117412cdc92c5528119789f74` in the full entry-point case. Both post-fix cases preserved the original hash before and after the run, and the old aliases still returned `samefile=true`. See `before_fix/reproduction.json` and `after_fix/reproduction.json` for the full commands, actual paths, exit codes, content excerpts, and before-and-after trees including empty directories. The pre-fix source copies are `budget_run_before.py` and `common_before.py`.

The post-fix result verifies that the atomic save completed safely. The synthetic experiment was designed to fail. Preflight checks can still reject known file aliases or sealed directory targets. All 14 existing P1 path tests were retained as written.

## Implementation and Write Sites

The new `planner/atomic_io.py` uses `tempfile.mkstemp` to exclusively create a temporary file in the target directory. It writes through the returned file descriptor via `os.fdopen`, closes the handle, and calls `os.replace`. It avoids opening old fixed temporary paths or deleting unknown files in advance. If `fdopen` fails, it closes the original file descriptor. Serialization, partial write, close, and replace failures leave incomplete content unpublished and clean up only the temporary path created by that invocation. Cleanup failures are added as notes to the original exception, which is reraised.

The JSON and CSV writers in `planner/common.py` and all save branches in `scripts/budget_run.py` use this implementation. `scripts/run_improvement.py` also uses a safe replacement for the regenerated `comparison.md`. Conservative preflight checks still include older temporary names. The actual writers use exclusively created paths. Existing safeguards for direct file hard links, directory junctions, seals, logs, budgets, and process trees were retained.

JSON retains UTF-8 encoding, two-space indentation, insertion order, the original newline behavior, and the public API's `allow_nan=False` setting. The ledger uses its existing serialization parameters. CSV retains the field order, `extrasaction=ignore`, `newline=''`, and byte representation. Tests passed for creating new targets and updating valid targets. When an existing target name was itself a hard link to a synthetic input, replacement detached only that target name and left the input unchanged.

The full production call inventory is in `R\write_inventory.md`. Most direct writes outside the change create launch, exception, log, HTML, or screenshot files in controlled new result directories. A general framework for all new-file writes was outside the scope. This round validated serial execution scenarios. Protection against malicious concurrent directory replacement, durability across power loss, and cross-platform certification were outside the verification scope. The implementation uses the existing dependencies.

## Results from This Round

| Acceptance item | Observed result and evidence |
| --- | --- |
| Automated tests | 117 passed, 0 failed, 0 errors, and 0 skipped. The suite comprised 94 existing tests and 23 new tests. Pytest reported 28.86 seconds and the outer command measured 29.326782 seconds. See `pytest.xml` and `control/command_03.log`. |
| Actual Windows links | Hard links were created using `os.link` on drive G. The Windows directory junction tests ran without skips. |
| Exceptions and budget | Coverage included nonfinite and nonserializable JSON, failed CSV streaming, `fdopen`/partial-write/replace failures, preservation of useful exceptions on cleanup failure, and preservation of the original target and input. Budget cases covered start and completion, command FAIL, timeout BLOCKED, process launch exceptions, and save failures that leave the state RUNNING and block a resume. |
| Shared E5 conditions | 14 completed, 1 locked, 1 interrupted, and 2 affected future tasks. Both methods used the same 6839 future candidates. The shared conditions and inputs were preserved before and after both runs. |
| E5 byte compatibility | Both schedule CSVs were byte-identical to `PREV/E5_common_baseline`. See `csv_regression.json`. |
| Independent E5 recheck | The dedicated check-only command reran the checks. The complete tree of 33 files and 3 directories and its SHA256 hashes were preserved. See `E5_recheck/recheck.json`. |
| Real E3/E4 regression | All 16 plans across 4 cases passed checks against the original TLE at both endpoints and every integer second, with zero violations. The 16 task CSVs and 4 candidate CSVs were byte-identical to OLD. |
| Demo | Built from the new E3/E4 results. The data check passed. Chrome passed all 33 offline interaction checks with no runtime exceptions, and the three screenshots were reviewed individually. This round produced no new E5 interface. |
| Historical artifact protection | The original raw data, three older sealed sources, complete OLD and PREV trees, `requirements-lock.txt`, and `.gitignore` were unchanged, including empty directories. See `protected_before.json` and `protected_after.json`. |
| Seals and compilation | All six new sealed result directories had valid manifests with no temporary file from this round. The changed Python files compiled. Hashes are in `acceptance.json`. |

E5 results for this round follow.

| Method | Final score | Fixed history / new tasks | Coverage (all / feasible) | Violations | Net adjustments | Replanning (s) | Independent validation (s) | Conditional upper bound |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 172.4 | 51.0/121.4 | 56/60 · 56/56 | 0 | 5 | 0.003321 | 0.330995 | 182.0 |
| improved | 182.0 | 51.0/131.0 | 56/60 · 56/56 | 0 | 23 | 0.070897 | 0.326955 | 182.0 |

The 9.6-point gain comes from the existing algorithm. The I/O fix had no effect on the score. The shared initial file SHA256 was `1b37fab094cb6b2a9f0d99aa92d0c018d8ad02a4de14e42f1aba831b1963ec8c`, and the shared conditions SHA256 was `585404b8222cdcacc53127826603515a5a11be1ca2efc446cc975ff994db8d67`. A single run took 2.326887 seconds internally and 3.156530 seconds in the outer command. The conditional upper bound ignores resource conflicts. The demo presents the complete E3/E4 workflow, where the earlier E4 comparison used different initial plans and showed a gain of 11.6 points. E5 uses its own comparison above.

The E3 post-fault baseline and improved scores were again 172.4 and 184.0 for seed 42, 182.0 and 190.0 for seed 17, and 176.2 and 189.0 for seed 23. E4's later fault again yielded 172.4 and 184.0. Real inputs, IDs, TLE data, station locations, windows, HTML, screenshots, ledgers, and attack fixtures are stored only in ignored local directories.

## Budget, Failures, and Scope

The single 600-second ledger for this round recorded 15 serial controlled commands totaling **81.018276 seconds**, leaving **518.981724 seconds**. All 15 outer commands passed as expected, with no unexpected outer failures or timeouts. The two actual pre-fix exit codes of 2 and the input corruption were recorded. The post-fix exit codes of 2 from synthetic configurations and commands, along with intentional FAIL, BLOCKED, and save-error tests, were verification cases. Internal fixture ledgers were test data, and their timing was included in the outer commands. Each command was capped at 300 seconds and the remaining balance. Reading, editing, documentation, and permission waits were outside the compute budget.

The earlier optional reevaluation remains BLOCKED. This round left that contract in place and did not run the reevaluation. Member 1's actual delivery and member 3's confirmation remain PENDING_EXTERNAL. No messages were sent. Clean installation, full optical validation, formal scoring, new algorithms, parameter sweeps, and a second E5 starting point were outside scope. The 16 independent historical attack cases belong to an earlier round. The 117 tests run in this round included the existing E5 history and fairness regressions.

The environment snapshot was still untracked and ignored. Its SHA256 was `03471313d71afce5590dc529b8adf38f2f6c8a94704a95e01ad8823feba0856c`. The original `.gitignore` rules remained in effect. See `R\acceptance.json` for individual statuses and source hashes.

## Copyable PowerShell Commands

These commands are for a later manual recheck in a new directory with an independent 600-second ledger. This round did not rerun them. Stop and investigate if any block fails. The existing real raw data and the OLD sealed artifacts are required inputs and are absent from a fresh clone.

```powershell
Set-Location 'G:\bd-fmb'
$py = 'D:\conda_envs\bd-fmb\python.exe'
$r = 'G:\bd-fmb\outputs\atomic_write_fix_20261023_182047'
$v = Join-Path 'G:\bd-fmb\outputs' ('atomic_manual_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
$ledger = Join-Path $v 'control\run_ledger.json'

# Use a new basetemp and the single ledger for this manual recheck.
& $py -X utf8 scripts/budget_run.py --ledger $ledger --timeout 120 -- $py -X utf8 -m pytest tests -q --basetemp "$v\pytest_tmp" --junitxml "$v\pytest.xml"
if ($LASTEXITCODE -ne 0) { throw 'pytest failed' }

# Recheck the directory-level hard-link fix using only new synthetic fixtures.
& $py -X utf8 scripts/budget_run.py --ledger $ledger --timeout 60 -- $py -X utf8 "$r\reproduce_atomic.py" --out "$v\hardlink_probe" --expect safe
if ($LASTEXITCODE -ne 0) { throw 'hardlink probe failed' }

# Reproduce E5 with the actual inputs. Its entry point already uses the shared ledger.
& $py -X utf8 scripts/run_replan_e5.py --source outputs/improvement_demo_20261023_150452/experiments/E4_seed42_late --initial-plan outputs/improvement_demo_20261023_150452/experiments/E4_seed42_late/initial_frozen_baseline.json --event configs/late_fault.json --out "$v\E5" --ledger $ledger --budget-seconds 120
if ($LASTEXITCODE -ne 0) { throw 'E5 failed' }
& $py -X utf8 scripts/run_replan_e5.py --check-only --source "$v\E5" --out "$v\E5_recheck" --ledger $ledger --budget-seconds 120
if ($LASTEXITCODE -ne 0) { throw 'E5 recheck failed' }

# Reproduce E3/E4 and the demo. Use a new directory for each output.
& $py -X utf8 scripts/run_improvement.py --spec configs/improvement_demo.json --out "$v\experiments" --ledger $ledger
if ($LASTEXITCODE -ne 0) { throw 'E3/E4 failed' }
& $py -X utf8 scripts/budget_run.py --ledger $ledger --timeout 60 -- $py -X utf8 scripts/build_demo.py --summary "$v\experiments\summary.json" --out "$v\demo"
if ($LASTEXITCODE -ne 0) { throw 'Demo build failed' }
& $py -X utf8 scripts/budget_run.py --ledger $ledger --timeout 60 -- node scripts/browser_demo_test.mjs "$v\demo\index.html" "$v\browser"
if ($LASTEXITCODE -ne 0) { throw 'browser checks failed' }

# Open the delivered demo. Substitute $v for $r to open the manual recheck build.
Start-Process "$r\demo\index.html"
```

## Full Paths to Key Artifacts

- Individual acceptance results at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\acceptance.json`
- Write-site inventory at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\write_inventory.md`
- Before-and-after reproduction reports at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\before_fix\reproduction.json` and `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\after_fix\reproduction.json`
- Test report at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\pytest.xml`
- E5 comparison table at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\E5_common_baseline\comparison.csv`
- Read-only recheck at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\E5_recheck\recheck.json`
- Byte regression report at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\csv_regression.json`
- E3/E4 comparison table at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\experiments\comparison.csv`
- Demo at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\demo\index.html`
- Browser report at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\browser\browser_checks.json`, with `01_seed17_improved_overview.png`, `02_late_fault_history.png`, and `03_late_replanned.png` in the same directory
- Complete before-and-after trees at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\protected_before.json` and `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\protected_after.json`
- Single ledger at `G:\bd-fmb\outputs\atomic_write_fix_20261023_182047\control\run_ledger.json`
