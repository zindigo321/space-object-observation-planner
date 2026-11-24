# Delivery Self-Review (2026-10-23)

This self-review used the code-review skill for static inspection and runtime verification. The scope was internal review.

## Static Inspection

| Dimension | Findings and evidence |
| --- | --- |
| Inputs and security | The original ZIP was safely extracted. No path escapes or links were found. CSV, JSON, UTC, and IDs were strictly validated. Input was never executed as code, and no credentials or real data were staged. |
| Compatibility | Original candidates, schedules, and legacy task CSVs were preserved. E0's four task tables and candidate table were byte-identical. New standardized task tables are written separately. |
| Error handling | FAIL/2 and BLOCKED/3 have defined outcomes. Existing output directories are rejected. Tests cover invalid YAML, missing inputs, fault fields, and corrupt caches. |
| Resource cleanup | The Windows Job Object receives the child process before execution resumes. A `finally` block closes the job. A short test showed that descendant processes were terminated. |
| Independent evaluation | The validator has no scheduler dependency. It rescores from original priorities and durations, independently derives the fault history sets, and compares them exactly. |
| Change scope | The original parsing, geometry, candidates, and scheduling were retained. Changes were limited to handoff, parameters, caching, evidence isolation, and tests. Cloud execution and complex models were outside scope. |
| Types and boundaries | Checks cover integer seconds, positive IDs, non-boolean precision, and start, end, and boundary values. An actual run with non-default stations and horizon and unequal sample counts passed. |

The review found that internal worker arguments might bypass the existing output directory check. The fix verified the parent process and the new directory's state, then passed regression tests. All identified blockers were resolved.

## Runtime Verification

- All 43 pytest tests passed. The final JUnit report is `outputs/pytest_delivery.xml`. `compileall` passed.
- E0/E2 real runs, standard window adaptation, external replanning evaluation, non-default parameters, and cache reuse were exercised. See `EXPERIMENTS.md` for results.
- The real historical backdating counterexamples supplied by the review failed in all four statuses. The original valid control was unchanged.
- All source evidence retained its hashes. The original reference project's 114 files matched the inner ZIP.
- The earlier optional reevaluation remained BLOCKED.

## Nonblocking Maintenance and Verification Scope

To minimize changes to inherited code, some extracted modules still use compact expressions and wildcard imports from `common`. Maintenance can narrow those incrementally. The Windows branch was exercised. The POSIX process-group implementation was outside the OS tested in this round, so verification applies to Windows. The tests used the existing bd-fmb dependency environment. A fresh install, optimality, and full optical validation were outside scope.

## Additional Self-Review for E3/E4 and the Demo

This round also used the code-review skill. The original 43 tests were retained, and 65 passed after adding 22. Fixed event parameters and external evaluation parameters have separate roles. The checks verify frozen source seals, raw inputs, and the complete candidate set. The source event's impact list serves as provenance, and each method's statistics use its own impacts. The existing scheduler, validator, and TLE adapter were retained. The initial plan is frozen separately, and the independent validator still rejects history counterexamples. The five default entry-point tables were byte-identical to the baseline. Reproduction in a new directory matched the same outputs.

The demo uses a local template and sealed artifacts. It escapes HTML delimiters in embedded JSON and renders task details with `textContent`. It uses no external scripts, dynamic execution, or credentials. A mismatch in scores, coverage denominators, or validation reports produces FAIL, and missing evidence produces BLOCKED. Interaction verification requires running the browser checks. Chrome passed all 33 offline interaction checks against the local file, and three screenshots were reviewed. The browser's test-only no-sandbox mode loads only the locally generated page under a Windows process-tree budget.

The ledger is serial. The per-command cap is the minimum of 300 seconds, the requested cap, and the remaining budget. It records failures, timeouts, and incomplete runs distinctly. Actual compute time was 147.226 seconds of 600 seconds. The six failed runs and verification after their fixes were retained. The read-only recheck preserved the hashes of all 56 files. Raw inputs and the three old source directories were unchanged. The new-directory reproduction used the existing environment. External confirmation from members 1 and 3 remained PENDING_EXTERNAL, and the earlier optional reevaluation remained BLOCKED. See the [handoff document](IMPROVEMENT_DEMO_HANDOFF.md) for detailed causes, evidence, and scope.

## Additional Self-Review for P1/E5 (2026-10-23)

The code-review skill was used to inspect security, compatibility, error handling, resources, change scope, and boundaries, followed by runtime verification. P1 checks resolved paths before the first write at the main entry point, direct preparation, aggregation, and budget writes. Full tree snapshots include empty directories and link identity. Windows junctions, hard links, and paths sharing a neighboring prefix were tested, with real sources protected during counterexample tests. The scheduler stayed outside the fix, and the path changes used the existing project structure.

E5 uses one shared initial plan for both methods. The original JSON was cross-checked against the CSV. Ordered semantic hashes bind the source, event, candidates, and history. Each method uses an independent copy checked before and after the call. The independent validator derives history from the separately saved original plan and reads the original TLE, priorities, and station locations. Method timing measures `schedule` and includes the improved method's internal fallback. The conditional upper bound counts fixed targets once. Interrupted targets can still enter the future candidate set. The dedicated recheck accounts for the difference between E5 and the original four-plan format.

All 94 tests passed. This round records evidence for E3/E4 byte regressions, real-case E5 history attacks, read-only rechecks of complete trees, and browser validation of the new demo. Directory checks were scoped to serial execution, with malicious concurrent link replacement outside verification. Timings came from single runs, with no statistical conclusions. Verification covered native Windows and the existing environment. The commit excluded real artifacts, the original environment snapshot, and credentials, and existing ignore rules were used. See `PATH_SAFETY_E5_HANDOFF.md` for per-item acceptance and external follow-up.

## Additional Self-Review for the Atomic Write Fix (2026-10-23)

This round used the code-review skill for file-by-file static inspection and runtime verification. Production changes were limited to `planner/atomic_io.py`, `planner/common.py`, `scripts/budget_run.py`, and `scripts/run_improvement.py`. The round added `tests/test_atomic_io.py` and handoff documentation. Scheduling, candidates, independent validation, path preflight, process-tree protection, and the interface were outside scope.

| Dimension | Review and evidence for this round |
| --- | --- |
| Security | `mkstemp` exclusively creates the file and writes use its returned file descriptor. The old fixed `.tmp` path is never opened. Cleanup only touches the temporary path owned by the invocation. Directory-level hard-link cases were run through the actual budget and full CLI entry points before and after the fix, verifying preservation of the old alias and input after the fix. |
| Compatibility | JSON UTF-8 encoding, indentation, key order, and nonfinite value handling and CSV column order and newlines were preserved. New targets and valid updates passed. The two real E5 CSVs and twenty E3/E4 CSVs were byte-identical. |
| Error handling | Serialization, `fdopen`, partial write, and `replace` failures preserve the target. Cleanup failures are noted on the original exception, which is reraised. A failure to save final budget state leaves RUNNING and prevents continued execution. |
| Resource management | The file descriptor is closed before replacement on Windows. After failures, `fstat` confirmed it was closed and the invocation's temporary file was gone. Both existing real process-tree timeout tests and new budget timeout tests ran. |
| Scope and conventions | The helper is small and uses the standard library, with no new dependencies or generalized security framework. Normal new-file writes in new directories were retained. See this round's `write_inventory.md` for the full list. |
| Types and boundaries | `Path` objects and existing API signatures were retained. Tests cover CSV streaming failure, JSON nan, inf, and nonserializable values, ordinary old temporary files, and existing target links. |

117 tests passed, comprising 94 existing and 23 new tests, with 0 failures, 0 errors, and 0 skips, including actual Windows junction tests. E5's shared conditions of 14/1/1/2, 6839 future candidates, and 172.4/182.0 points matched the historical results, with zero original-TLE violations. The dedicated read-only recheck preserved all 33 files and 3 directories, and all older protected trees and their hashes matched. The new demo passed 33 browser checks, and three screenshots were reviewed. Seal manifests contained no temporary files from this round, and the source compiled. See `outputs/atomic_write_fix_20261023_182047/acceptance.json` for per-item evidence.

The single budget recorded 15 commands totaling 81.018276 seconds. Outer commands passed as expected. Counterexample exit code 2 and intentional test failures were retained. No unresolved blockers were identified in this round. The existing compact-code maintenance item remains. Verification covered serial Windows project scenarios. Malicious concurrent directory replacement, durability across power loss, and POSIX execution were outside scope. The existing E5 gain comes from the algorithm. Environment reinstallation, full optical validation, formal scoring, and teammate confirmation were outside scope. The earlier optional reevaluation remains BLOCKED.

## Stable Handoff and Read-Only Intake Review Before Commit (2026-10-23)

This round continued to use the code-review skill. It added three lightweight scripts and synthetic boundary tests. The planner, `smoke_test.py`, the original 117 tests, dependencies, and ignore rules were outside the change. Path preflight precedes `mkdir`. Subprocesses use the existing `process_guard` and propagate exit codes 0, 2, and 3. Unknown input is read as supplied. Read-only intake reuses `load_tables` and `normalize`, then explicitly selects a slice after reading the full tables. Failure reports identify the first error and the unfinished scope. A failed planning workflow stops before evaluation or recheck, with parent and child outputs in separate locations.

The source kit reads Git objects from the specified commit and rejects files outside the controlled allowlist. ZIP contents are checked against the manifest and their hashes. Duplicate members, out-of-bounds names, and symbolic links are rejected, and extraction uses a new directory. Real reference data is restricted to a separate local kit. Git staging contains only source, tests, documentation, and synthetic templates. Dependency versions come from the existing environment. The manifest excludes itself, and the external archive SHA avoids a circular hash.

Local synthetic planning, initial and fault evaluation, rechecks, and read-only intake of the synthetic and official reference inputs were run and passed as expected. Final source-commit archive export, import provenance from extraction, the real-window workflow, full pytest, and the real demo browser results require the external `acceptance.json`, `portable_validation.json`, `pytest.xml`, and `browser_from_kit` reports. Certification requires the corresponding checks to run. Historical TLE evidence, this round's window integration, and pending external confirmation each have their own verification scope.
