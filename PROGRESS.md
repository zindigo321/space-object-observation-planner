# Development Progress

## 2026-11-18 Formal Local S02 Acceptance

The production source commit is `6aacb4a64d5b32d388c7ecbcad7ae361bb31b29d`. After extracting the final product ZIP and installing dependencies offline, cold generation for the frozen 24-hour instance with 1800 targets and 10 stations took 204.52 seconds. Independent evaluation and read-only rechecks passed for 2/2 initial planning cases and 4/4 fault-free replanning cases. All six loaded the packaged native DLL. Checks of the 30-second hard solve limit and process cleanup passed.

All 302 tests passed in each of two environments, one extracted from the final ZIP and one restored from uploads. The actual platform was Windows 11 x64 with 64-bit CPython 3.11.17. Baidu FAMOU acceptance remains pending. The corresponding PR's Actions results report the GitHub source checks. See [current status](docs/CURRENT_STATUS.md) and the [entry points](README.md).

## 2026-11-17 Formal H180 Acceptance

All four formal matrix cases passed seal, readback from a new path, and accept. This historical version came from `96064be8e26b65d9c05e687cb44d89a8ccc65670`. See the [H180 delivery record](docs/FAMOU_DELIVERY_STATUS.md). During S02 production regression, all 12 task tables across the four H180 cases matched this version byte for byte.

## Historical Progress Through November 2, 2026

The latest result was R34_H180_BASE_IMPROVED_PASS. Together with R33-C H180_BASE/baseline, it formed a pair from the same starting point at t3600. Selected J rose from (2758,180) to (2806,180), or 48 integer points and 9.6 points on the current task scale. Both covered 180 targets. Baseline retained on a tie with zero net adjustments. Improved accepted a strict gain with 49 net adjustments. Eight duration upgrades accounted for the entire gain, and the other 41 changes had no scoring effect. The comparison did not establish reduced disruption. The improved case reached the loose conditional upper bound of 2806 for the primary score under its fixed history and discrete candidate pool. The bound is specific to those conditions.

R20 shared input delivery remains INPUT_DELIVERY_PASS. The original R21 round remains PARTIAL, with two initial passes and native acceptance at 0/4. R33-C and R34 added acceptance for the two BASE-starting cases in later rounds, bringing cross-round native acceptance to 2/4. The two H180_IMP-starting cases remained incomplete. The R21–R23 PARTIAL and R24–R26-A/B BLOCKED statuses remain recorded.

Earlier R19 evidence recovery was read-only. Recovery review, formal sealing, recovery of the execution version, and independent migration to a second new path all returned PASS. New schedule runs, native backend calls, and TLE propagations each totaled zero. The original R18 remains data PASS, seal FAIL, and overall PARTIAL. The user performed takeover verification on the same machine. Verification on another machine or on site falls outside that result.

- R9–R13 covered the native fault-free guard, interface and budgets, related scales, and cross-day checks. Historical versions and failures remain documented. Native functionality was merged into main.
- R14 compared three and ten stations using shared initial plans, 60 targets, and the same day. The ten-station selection gained 21 to 85 integer points and covered four additional targets. The original seal terminal and wall-time disclosure limitations still apply.
- R15 completed four successful native t2 runs that the verifier rejected incorrectly, with 0/8 complete and overall PARTIAL. R16 exceeded the preflight limit with zero real calls and remained BLOCKED. No replacement rerun was credited.
- R17 completed 8/8 continuous-chain nodes, 8 schedule runs, 24 backend calls, 28 external checks, and 8 new geometry checks. All eight nodes retained on ties. Data, sealing, and execution version passed.
- R18 performed 2 initial and 4 native runs, with 6 schedule runs, 12 primary external checks, and 6 new geometry checks. Data passed. The seal program failed due to a missing directory, leaving the round PARTIAL.
- R19 imported and reviewed evidence of 6 historical schedule runs, 12 backend calls, and 82080 geometry samples. One recovery package succeeded, with zero formal failures. One evidence collection preparation failure was retained. Independent accounting was 169.646280 / 600 seconds. The original R18 accounting remains 208.426582 / 600 seconds.

- R20 generated all 1800 target-station pairs from scratch, reused zero, and replayed all candidates byte for byte. All 20127 geometry samples passed. Formal production and sealing each ran once, taking 530.423 / 600 seconds. The same-machine new-path and missing-file tests passed.

- In R21, five of six cases started and two passed completely. The initial J values were (2758,180) and (3000,180). Native acceptance was 0/4. Backend starts remained five confirmed and two unknown, for a range of [5,7].
- R22 and R23 revised recovery and readback paths and remain PARTIAL. Formal acceptance remained open after partial qualification or sealing.
- R24, R25, R26-A, and R26-B remain BLOCKED. Read identity, supervision, timing, and full-chain qualification were incomplete. Original failures and incomplete protection are preserved.
- R27 passed full executor qualification. Formal sealing and migration had yet to run. The scope was same-machine dependencies. Cross-machine and machine-level isolation certification fall outside that scope.
- R28 ran seal, post, and accept once each with exit code 0. All 18 negative cases, two audit layers, and protection checks passed. The overall result was PARTIAL because complete pre-registration timing evidence was missing.
- R29 and R30 were BLOCKED by the startup gate after materials were read before registration. Record the original registration and timing evidence as observed.
- R31 passed all 30 startup timing qualification checks. Two short commands exited with codes 0 and 7. There were zero new production operations. The result covers qualification.
- R32 preparation took 151.434 seconds, above the 80-second gate. The intended native case never started. Wrap-up also failed, and the minimum recorded failure duration of 702.082 seconds does not establish compliance with the budget. The result was BLOCKED.
- R33-A was blocked by the absence of a reusable startup state. R33-B registered and validated its entry point but failed to write during launch and capture, with a separate read-before-registration deviation. Both were BLOCKED. B lacks evidence for an exact production-call count.
- R33-C passed the single H180_BASE/baseline case, selected (2758,180), and retained on a tie. The run recorded one native call, one solve, exactly three backend starts and completions, 360 propagation calls, 39060 plan samples, and 78120 two-path propagation samples.
- R34 passed the single H180_BASE/improved case, selected (2806,180), and accepted a strict improvement. The run recorded one native call, one solve, exactly three backend starts and completions, 360 propagation calls, 40020 plan samples, and 80040 two-path propagation samples.

R20 is bound to the 99-file product tree at `b0e646159a36a4d4375afc083f3b8db793bc131b`. R21, R27, R33-C, and R34 used the public 100-file source tree at `1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5`. Production code matches earlier commit `83d3014`. These commits identify the actual execution versions. The original documentation update covered existing product and recovery behavior. The strict J guard applies to the native fault-free path. Fault and legacy paths use their own rules. Each round has its own ledger, and real data and full recovery packages stay local.

R33-C and R34 each passed the saved protection checks for 22624 historical files, 3 trees, and 3950 consumed originals. The independent audit reviewed saved records and experiment copies. It did not rescan every historical original or rerun the solves or TLE propagation. R34's saved accounting of 235.8957645 seconds is reproducible. Its terminal sample of 235.9102733 seconds and actual return coverage of 238.9717645 seconds came from the external terminal handoff. The saved parent JSON does not contain those fields. Both rounds recorded zero seal/post/accept runs, so final delivery remained open.

See the [same-start pair](docs/R33_R34_H180_BASE_PAIR.md), [current status](docs/CURRENT_STATUS.md), and [experiment record](EXPERIMENTS.md). The two IMP-starting cases, formal evidence delivery, and team receipt were next. Complete six-day runs, 10000 targets, dynamically arriving tasks or changing resources, full optical conditions, and official scoring remained unverified. The Demo and Word/PDF remain the versions from their existing batches.

## Historical Progress Snapshot for October 23, 2026

The following sections record the completed, pending, and verified work at the time. Use the beginning of this page and the current-status page for the latest state. Pending items and smaller test counts in these sections belong to their historical machine receipts.

## Work Completed

* \[x] Created work/baseline-handoff from main/e5c7935 and kept the original requirements-lock.txt.
* \[x] Safely extracted the inner project and confirmed that all 114 prototype\_v1 reference files still match the original ZIP.
* \[x] Confirmed that the latest problem 4 data and main instructions matched the earlier versions. Reviewed template v6 within the existing implementation scope.
* \[x] Kept the original candidate and scheduling implementation and split out an independent verifier and unified entry point.
* \[x] Fixed forged-history acceptance. Tested exactly-at-start and exactly-at-end faults and missing, altered, and extra history.
* \[x] Verified that all source files had identical hashes before and after read-only recheck.
* \[x] Routed parameters through actual execution. Cases with nondefault stations, start times, durations, and per-tier counts passed.
* \[x] Passed the standard-window contract, official-input adapter, and synthetic examples.
* \[x] Matched all four E0 plans and the candidate tables byte for byte. Baselines had zero violations for three fixed seeds.
* \[x] Verified cache identity and contents, subprocess-tree timeouts, and safeguards against overwriting prior outputs.
* \[x] Prepared the runnable October 23 baseline and handoff documentation in BASELINE\_HANDOFF.md and EXPERIMENTS.md.

## Pending External Confirmation

* \[ ] Read-check the member 1 data delivery from the October 22 milestone. Official input and teammate-delivered input need separate verification.
* \[ ] Confirm startup, inputs and outputs, and evaluation with member 3. Teammate outreach and confirmation were pending in this round.
* \[ ] Confirm the official per-target limit, handling of interruptions, multi-station requirements, window filtering, and the two scoring conventions.

## Work Not Yet Run

* \[ ] October 24. Validate an improvement across seeds and create a before-and-after fault Demo. Keep existing improvements and the fixed evaluation samples.
* \[ ] October 25. Formally hand off the stable program, comparison tables, and presentation materials to the team lead and member 4.
* \[ ] Unify the legacy extra-evaluation contract, currently isolated and explicitly BLOCKED.
* \[ ] Larger scales of 180 or 300 targets, a complex web interface, integer programming or genetic algorithms, and cloud evolution were outside this round's execution.

## Known Limitations

Window search and per-second elevation checks cover sampled time. Continuous-time validity, full optical conditions, weather, terrain, tracking, field of view, and state estimation remain unverified. Standard-window mode verifies scheduling only inside supplied windows. Grid pruning can discard optimal solutions. Task scores are separate from the official 100-point scale. Real inputs and all outputs are kept in locally ignored directories.

## 2026-10-23 Addition for E3/E4 and Demo Delivery

The preceding snapshot records baseline delivery. The actual outcomes below update the October 24 cross-seed and Demo item with their observed timing.

* \[x] Created work/improvement-demo from 9765eb8. The work was isolated from main and used the existing algorithm and parameters.
* \[x] Ran initial planning and fault replanning for both methods across three frozen E3 seeds. Candidates and events matched, and all independent per-second checks reported zero violations.
* \[x] E4 counts for completed, locked, interrupted, and future-affected tasks agreed with expectations for the later fault. All 16 independent history counterexamples behaved as expected.
* \[x] Matched the four default-seed-42 task tables and candidate tables to the baseline byte for byte, including a rerun in a new directory.
* \[x] Passed 65 pytest tests. The SHA256 values of 56 files matched before and after the later-fault read-only recheck.
* \[x] Passed offline HTML generation, data checks, and 33 actual browser interaction checks. Prepared three screenshots and an approximately 80-second script.
* \[x] Pinned the minimal development dependency to pytest 9.1.1. The existing environment was reused without installing or upgrading packages. The original requirements-lock.txt stayed unmodified and untracked.
* \[x] Completed CSV and Markdown comparisons, per-case evidence, and itemized acceptance. The 27 computation and test commands took 147.226 seconds, including six preserved failed commands, within the 600-second budget.
* \[x] Provided review materials for members 3 and 4 and the team lead in the [handoff guide](docs/IMPROVEMENT_DEMO_HANDOFF.md). Demo assets are in ignored local directories.
* \[ ] Actual receipt from member 1, external confirmation with member 3, and formal handoff to the lead and member 4 remained with the user and team. No messages were sent in this round.
* \[ ] Legacy extra evaluation remained BLOCKED. Video and clean-environment installation were pending. Work on 180 or 300 targets, stress sweeps, and new algorithms fell outside this round.

## 2026-10-23 Addition for the P1 Fix and E5 Shared Initial Plan Comparison

This section records the new run, following the historical snapshot above.

* \[x] Created work/path-safety-replan-e5 from 97d41e6. The standalone P1 commit is 341ac9e.
* \[x] Reproduced P1 in a source copy, where return code 2 still left directory changes. After the fix, rejection occurred before the first write and the complete tree, including empty directories, matched.
* \[x] Passed 14 path regression tests, including real Windows junctions. Byte-matched all 16 plans and four candidate tables from the E3/E4 rerun to the earlier delivery.
* \[x] Froze the shared E5 baseline initial plan, event, history, and future candidates. Hash, provenance, and pre/post method checks passed.
* \[x] Recorded 172.4 and 182.0 points for the two E5 methods, a gain of 9.6. Both covered 56/60 overall and 56/56 executable targets with zero violations. Net adjustments were 5 and 23, and the conditional upper bound was 182.
* \[x] Passed all 94 tests and met expectations for 16 actual valid-history and tampering checks.
* \[x] The E5 read-only review preserved all 33 files and 3 directories. The old input, complete OLD directory, and original HTML tree and hashes matched their pre-run state.
* \[x] Regenerated the Demo from new E3/E4 results. All 33 actual browser checks passed. Delivered the E5 tables separately, with each score gain attributed to its own experiment.
* \[x] The 20 computation and test commands totaled 152.042 seconds, within the round's independent 600-second budget.
* \[x] Prepared the startup, I/O, 0-2-3 exit code, and independent evaluation materials for member 3, plus tables and precise conclusions for member 4. See docs/PATH\_SAFETY\_E5\_HANDOFF.md.
* \[ ] Actual member 1 delivery, member 3 interface confirmation, and formal team handoff remained with the user and team. No messages were sent.
* \[ ] Legacy extra evaluation remained BLOCKED. The optional second shared starting point, clean installation, full optical checks, and official scoring remained unrun or unverified.

## 2026-10-23 Addition for the Atomic Temporary File Hard-Link Fix

* \[x] Created work/atomic-write-hardening from b504f93, preserving the original branches, main, and ignore rules.
* \[x] Reproduced the directory-level hard-link issue in synthetic fixtures only. Preserved complete before-and-after evidence for the budget-save and full-entry-point cases where return code 2 still damaged input.
* \[x] The ledger, JSON and CSV output, and repeated rollups use exclusive temporary files in the destination directory and replace atomically after closing them. Cleanup covers only files created by that run and reports failures.
* \[x] Passed 117 tests, including 94 existing and 23 new tests, with zero failures, errors, or skips. Ran actual Windows junction and hard-link tests. The budget state machine and failure and timeout semantics stayed consistent.
* \[x] The actual E5 rerun scored 172.4 and 182.0, with 51 fixed points, 121.4 and 131 new-task points, a gain of 9.6, 6839 future candidates, and zero violations. Both task CSVs matched the prior round byte for byte.
* \[x] The E5 read-only review preserved 33 files and 3 directories. A new-directory E3/E4 run byte-matched 16 task CSVs and 4 candidate CSVs.
* \[x] The new Demo passed 33 actual browser checks, and all three screenshots were reviewed. The complete old raw, source, OLD, and PREV trees, including empty directories, matched their originals, as did the environment manifest and ignore rules.
* \[x] The 15 serial commands took 81.018276 seconds on one 600-second ledger. Handoff, the inventory of write locations, and itemized acceptance were completed. See docs/ATOMIC\_WRITE\_FIX\_HANDOFF.md.
* \[ ] Member 1 delivery and member 3 integration confirmation remained external. Legacy extra evaluation was BLOCKED. New algorithms, clean installation, full optical checks, and official scoring were unrun.

## 2026-10-23 Addition for Stable Handoff and Member 1 Read-Check Preparation

* \[x] Created work/stable-handoff-intake from b0eb3b5, preserving the algorithms and safe-write core.
* \[x] Reused the unified CLI for the portable entry point. It supports synthetic and standard-window inputs, task and fault evaluation, and read-only rechecks. It accepts an explicit interpreter and paths with Chinese characters and spaces. Drive letters come from the user's environment.
* \[x] The local synthetic run scored 10 points initially and 3 after the fault. Evaluation and recheck passed, with the input and output trees preserved.
* \[x] The read-only input check reused the original contract. Synthetic and official reference windows passed. It generated metadata and station-driven configuration without scheduling or orbital propagation.
* \[x] Prepared member 3 integration instructions, a member 1 intake checklist and metadata template, an unconfirmed receipt, and drafts for members 1, 3, and 4. No messages were sent.
* \[x] Prepared allowlist build and SHA256 manifest tools for separate source and local real-data packages. The final package must use Git objects exported after commit.
* \[ ] Post-commit release acceptance was to be recorded in outputs/stable\_handoff\_20261023\_190522/acceptance.json for the final package, actual run from a moved directory, browser checks, all tests, and the protection snapshot. Results needed to be measured after commit.
* \[ ] Actual member 1 delivery remained PENDING\_INPUT/NOT\_RUN, member 3 confirmation PENDING\_EXTERNAL, and legacy extra evaluation BLOCKED.
* \[ ] Clean installation, a full old-TLE migration to another machine, full optics, and official scoring remained unverified. The algorithm work remained scoped to this round.



## 2026-10-24 Addition for Local Takeover and Three Rounds of Acceptance



The user took over the former roles of members 1, 3, and 4 on the same machine. AI-assisted work completed cold generation for fixed subsets, integration with independent evaluation, and delivery of the Demo report. The source fix baseline was `0d6db405`. The [current status](docs/CURRENT_STATUS.md) now consolidates the contemporary summary.



Results and verification scopes from the first three rounds are recorded in this historical section. Use the beginning of this page and the current-status page for the latest results. External handoff items above describe that snapshot. Confirmation by another member or on another machine was outside the scope. The first round's original `BLOCKED / strict FAIL` and the read-only consumption approval for a specific version are recorded separately. Required items passed in the second and third rounds. Real data and complete run, Demo, and report artifacts stay local.


## 2026-10-26 Addition for Rounds 4 Through 8

- [x] Round 4. Both fixed A/B starting points yielded a fault-method gap of 9.6 points. The related starting points are dependent comparisons. Adjustment costs are reported by starting point.
- [x] Round 5. Revised the local report and prepared four draft documents. Those drafts record the historical round. Rounds 6 through 8 have their own records.
- [x] Round 6. Compared 12 cases across six faults and two starting points. Fault-method gaps were 4.0 to 10.8 points, with zero violations within the supplied windows.
- [x] Round 7. Ran eight actual fault-free controls. Twelve matched interaction differences were 3 positive, 3 zero, and 6 negative. Shared controls make these dependent trials.
- [x] Round 8. Used two disjoint new 60-target samples that do not overlap the sealed historical exclusion set of 181 targets. All 20 plans, all three verification layers, and independent audit passed.
- [ ] Define and verify a non-regression policy for proactive fault-free replanning against frozen originals. The round's PASS covers the reported experiment.
- [ ] Verify additional dates, larger scales, full optical equipment, official scoring, and receiving environments separately. Update the formal report, Demo, and release package together.
