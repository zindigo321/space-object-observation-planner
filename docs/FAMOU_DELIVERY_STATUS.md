# 2026-11-17 Final FAMOU Delivery Status

The local formal experiment matrix passed 4/4. Sealing, post and readback from a new path, and programmatic accept passed for all four cases. User testing on Baidu FAMOU remains pending.

This round branched in isolation from the actual previous delivery commit `690eb12c66e2906d7596435e8a70823805f789f3`. The scientific baseline was `1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5`. The export used the original Git blob allowlist, and the final commit is recorded in the package's `SOURCE_IDENTITY.json`. The older `main` commit `09c12b9` was outside the selected baseline.

Within `planner/`, the sole change was the runtime guard `process_guard.py`. Scheduling, candidate generation, scoring, history, and selection rules match the scientific baseline byte for byte. On Windows, success, failure, and timeout all terminate the Job and verify `ActiveProcesses=0`. POSIX uses `waitid/WNOWAIT` to retain the parent PID before cleanup, then terminates the controlled process group. That path was simulated, and Linux acceptance remains pending.

The candidate interface now returns task rows from `solve(problem)`. The trusted parent controls 40 seconds for preparation, 30 for solving, 20 for writing, and 80 for evaluation, with an outer deadline of 180 seconds. Candidate import, solving, and return serialization run in a controlled 30-second subprocess. Once all descendants have exited, the parent fixes the CSV bytes and runs an independent evaluation. The receipt binds the execution copy's size, SHA256, and `argv` before launch. It rechecks the copy afterward and reports concurrent changes to the original separately.

Nested entry points in Windows virtual environments use the underlying interpreter's actual `argv` and preserve virtual environment identity and parent process verification. The requested and actual `argv` are recorded separately. The two failed predecessor ZIPs and their regression evidence were preserved. Final acceptance applies to the final ZIP.

| Formal experiment case | Status | retained / raw / selected J |
| --- | --- | --- |
| H180_BASE_baseline | PASS | [2758, 180] / [2758, 180] / [2758, 180] |
| H180_BASE_improved | PASS | [2758, 180] / [2806, 180] / [2806, 180] |
| H180_IMP_baseline | PASS | [3000, 180] / [2814, 180] / [3000, 180] |
| H180_IMP_improved | PASS | [3000, 180] / [3000, 180] / [3000, 180] |

The selected primary score for the BASE pair increased by 48, with coverage of 180 in both cases. For IMP/baseline, the selection guard retained 3000 over a raw score of 2814. Each pair used the same frozen starting point, product, scoring, and selection rules. A legal tie retains the original plan. Independent package retests verify that it runs and are accounted for separately from formal scientific repeats.

The final round used the new binding `58692dbe558b4ee98ebcb1810c99a07b`. Four live native decisions took 27.472779 seconds in total, below the original 80-second budget. Lexical declaration reuse and proof-index optimization preserved live native checks. The host explicitly used process-level HighQoS and kept the other task on the same machine. The audit package contains records for the actual 63 branches, the 80/600-second budgets, and formal calls. Submission, consumption, distribution, and receipt acknowledgment of the formal request each occurred once. The binding is single-use after a terminal state.

Of the previous 100 deployment product files, 92 match the scientific Git blobs exactly. Eight `examples/synthetic` CSVs differ only by CRLF-to-LF conversion. The scientific Python code and H180 input match. Host performance changes apply to admission and execution control. Actual deployment identities, native authorization checks, each new epoch, 56 actions and 63 branches, four decisions, and the 80/600-second budget results are recorded in the audit package's `attempts/` and `FINAL_ACCEPTANCE.json`. The archive retains all failures, and consumed requests are single-use.

The final ZIP was also verified from a new path containing Chinese characters and spaces in a clean Windows CPython 3.11 environment. Acceptance covered offline dependencies, upload restoration, synthetic and H180 production followed by independent evaluation and recheck, invalid self-reported scores, history tampering, fixed-asset protection, and full regression testing. Actual test counts, logs, exit codes, and timings are bound to the ZIP's bytes and SHA256. See the external `FINAL_ACCEPTANCE.json` and `validation/final/ACCEPTANCE.json` in the audit package for checks actually run.

`upload/`, `UPLOAD_LIST.csv`, `UPLOAD_BATCHES.md`, and `FAMOU_START_PROMPT.txt` support Baidu public cloud testing. Upload all listed files, then paste the opening prompt. Use the ZIP for local delivery. Follow the platform rules shown in the live interface. See `famou/PLATFORM_GUIDE.md` for details. Restoration works independently of the original drive letter, local audit host, and protected keys.

Actual system verification covered Windows with CPython 3.11, the target platform for offline wheels. POSIX, other Python versions, and Baidu FAMOU remain untested. The Baidu status is recorded as pending user testing on Baidu FAMOU. H180 uses a frozen 24-hour instance with 180 targets and 10 stations. Six-day runs, 10000 targets, official scoring, and on-site acceptance fall outside the gates for this round.

`AUDIT_PACKAGE.zip` preserves historical packages, new attempts, formal evidence, performance timings, repair diffs, and validation of the final package. The internal manifest excludes its own bytes, and the ZIP hash is in the external receipt. Programmatic accept and the user's receipt are separate verification steps. The overall status follows the actual gates. When any gate is incomplete, deliver the audit ZIP with a PARTIAL status.
