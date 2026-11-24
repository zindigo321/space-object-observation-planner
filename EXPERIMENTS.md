# Experiment records

## Summary as of 2026-11-02

R33-C and R34 passed acceptance for one baseline group and one improved group, respectively, at `t=3600` from the H180_BASE starting plan. Selected `J` values from the common starting plan were (2758,180) and (2806,180), a gain of 48 integer points or 9.6 task points under the current scale. Both covered 180 targets. Improved made 49 net adjustments, with eight duration upgrades accounting for the entire gain. It reached the relaxed conditional primary-score upper bound of 2806 for the fixed history and discrete candidate pool. The result establishes optimality only for that primary score in this fixed case. See the [pair summary](docs/R33_R34_H180_BASE_PAIR.md) and the final section of this record.

R20 passed delivery of the common input. The original R21 remains PARTIAL with native 0/4. Additional native acceptance across rounds is now 2/4, with both H180_IMP starting-plan groups pending. R27 passed qualification. The technical sealing chain succeeded in R28, which remains PARTIAL due to a timing gap before registration. Later launch failures and qualification have separate records that preserve the original statuses. R33-C and R34 performed zero seal, post, or accept operations, and final evidence delivery is pending. That submission updated five documents. The corresponding PR records the actual tests, synthetic workflow, and CI results. Historical regression totals apply to their original runs.

The 2026-10-23 sections retain the context of those experiments. Items deferred to October 24 or listed as pending external confirmation describe the status at that time. The user later took over the original roles 1, 3, and 4 on the same machine. Acceptance by other team members, machines, or on-site equipment remains outside that evidence. Original statuses and failure evidence are preserved.

## Historical record for 2026-10-23

This record was compiled from local run artifacts. The new program generated the results without embedding the old control values. Raw files, sample IDs, per-task evidence, and detailed timing remain in local `outputs`, outside the repository.

## E0 and E2 fixed-sample results

All runs used official raw input, 20 targets in each of the high, medium, and low priority levels, and stations 1, 2, and 3. The horizon runs from 2026-08-03T00:00:00Z to midnight UTC the next day. Seed 42 used the original frozen sample. Samples for seeds 17 and 23 were frozen before calculating windows and were independent of the resulting scores.

| Seed | Windows | Grid candidates before pruning | Candidates after pruning | Baseline score | Fault replan score | Coverage / all targets | Coverage / executable targets | High / medium / low coverage | Violations | Cold run (s) | Cached run (s) |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: |
| 42 | 563 | 54699 | 10060 | 173.2 | 172.4 | 56/60 (93.33%) | 56/56 (100%) | 18/18/20 | 0/0 | 28.797 | 2.375 |
| 17 | 533 | 56685 | 9536 | 180.0 | 182.0 | 57/60 (95.00%) | 57/57 (100%) | 19/19/19 | 0/0 | 27.843 | 1.469 |
| 23 | 538 | 100072 | 9158 | 178.2 | 176.2 | 57/60 (95.00%) | 57/57 (100%) | 19/18/20 | 0/0 | 42.766 | 1.484 |

The improved initial and replanned schedules for seed 42 each scored 184.0, covering 56 targets with zero violations. The four legacy E0 task tables and `candidates.csv` matched the original package by SHA256, and the parsed fault event matched as well. Evidence is in `outputs/E0_security_verification/verification.json` and `outputs/E0_comparison.json`. The final cached run generated the same four task tables again.

After the seeded fault, the score for seed 17 rose because the original baseline used a chronological greedy strategy and selecting future candidates again can choose longer tasks. This result gives no guarantee of optimality or of a benefit from the fault. Seeds 17 and 23 ran only baseline in this round. The multi-seed comparison of the improved method was deferred to October 24. The original event-generation rule was applied to each sample's selected schedule, as recorded in its `fault_event.json`.

The executable denominator counts all targets with at least one valid 120-second candidate in the full planning horizon. It uses the original candidate pool and applies the 120-second threshold to geometric windows. The replanning coverage and coverage by priority in the table match each corresponding initial baseline.

## Data versions, configurations, and timing evidence

The adapter read 10,000 TLEs, including 108 Alpha-5 entries, with priority counts of 2024/3990/3986 and 10 stations. The latest problem 4 data ZIP, priority ZIP, main instructions, and supporting documentation were byte-identical to those in the reference project. The newly added v6 template was read for reference. See `outputs/prior_audit/current_official_comparison.json`.

| Seed | Raw hash manifest SHA256 | Actual frozen sample file SHA256 | Configuration | Results directory |
| --- | --- | --- | --- | --- |
| 42 | `e5786c6cd9c298319fca8eeb1fa1fc21da408549a707cda800550f90dce3fc24` | `5ec2c50132b3611a4857e159bfd35c65915dd2a59ec296df873aea8e1dbd038f` | configs/smoke.yaml | outputs/E0_seed42 |
| 17 | `e5786c6cd9c298319fca8eeb1fa1fc21da408549a707cda800550f90dce3fc24` | `d8cd3eff08992f1daab7443cabb24b0debd970ff3b1af9433ea28ce2bd2b4fcc` | configs/seed17.yaml | outputs/E2_seed17 |
| 23 | `e5786c6cd9c298319fca8eeb1fa1fc21da408549a707cda800550f90dce3fc24` | `24fc7d90d9c8b46952b67e05bd3102f984bc09526399f01f8dfd41a715d74cbd` | configs/seed23.yaml | outputs/E2_seed23 |

Each output directory contains `input_hashes.json` for raw file SHA256s, `frozen_sample.json` for the selected IDs, and `effective_config.json` for the executed configuration. The window cache also binds station parameters, the horizon, filters, sampling, dependencies, and the adapter SHA256. The code verifies cached content hashes. Final run directories were `outputs/E0_final_cached`, `outputs/E2_final_seed17_cached`, and `outputs/E2_final_seed23_cached`, respectively.

Cold-run stage times are reported in seconds below. The early Windows monotonic clock had a resolution of about 16 ms, so 0.000 denotes an elapsed time below its measurement resolution.

| Seed | Read and freeze | Windows | Candidates | Initial scheduling | Replanning | Validation and negative cases |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 0.390 | 26.250 | 0.063 | 0.125 | 0.109 | 1.328 |
| 17 | 0.281 | 26.297 | 0.063 | 0.015 | 0.000 | 0.656 |
| 23 | 0.266 | 41.062 | 0.125 | 0.016 | 0.016 | 0.765 |

Scheduling and replanning times for seed 42 sum baseline and improved. Seeds 17 and 23 report baseline only. The final version measures stages with `perf_counter` and stores the new measurements separately in `timing.json` in the `final_cached` directories listed above. The original timings remain in their own records. Parent process `execution.json` records elapsed time including child startup. Every run took less than 300 seconds.

## E1 interface and safety regression

- **All 43 pytest cases passed** in 8.97 seconds on the final run. See `outputs/pytest_delivery.xml`. Coverage includes valid data, missing fields, duplicate headers or IDs, invalid times, unknown targets or stations, reversed window endpoints, conflicting full scores, invalid metadata, invalid faults and YAML, and 119-second windows producing zero candidates. The unit-test fixtures are synthetic.
- History provenance checks rejected forged completed, locked, success, and new_success states. They also rejected removal of real completed or locked tasks and interruption segments, extra interruption segments, edits to historical times, states, windows, or original planned ends, and duplicated history. The tests cover faults starting or ending at exact task boundaries under the contract.
- For a negative case using real data, the test took a valid early candidate for a target from the original audit, independently confirmed its geometric and resource feasibility, and then forged history preceding the 01:00 fault. All four states returned FAIL with two history violations each. Replanning with genuine nonempty history still returned PASS. The detailed reports are in `outputs/E0_security_verification/` only.
- For the read-only check, `outputs/E0_recheck_final/recheck.json` returned PASS. All 56 source-directory files kept their SHA256s, and the report and new timings were written only to a fresh directory. Further tests verified rejection of overlapping or nested source and output directories, reuse of an old directory, and altered source evidence. The fresh-directory requirement also applies when the internal worker flag is set. The final code's read-only recheck of `E0_final_cached` is in `outputs/E0_delivery_recheck`.
- For the standard-table interface, baseline and improved both passed the synthetic case with stations [7,9], a 06:00 start, and a one-hour horizon. The official E0 exported window input yielded baseline 173.2 and replan 172.4 again in `outputs/E1_official_windows` by reusing the supplied windows.
- For external task scoring, `outputs/E1_external_fault_evaluation/evaluation.json` returned PASS for the real baseline replan. A unit test confirmed that the evaluator establishes scores independently of the tasks' self-reported `score` values.
- The parameterized run in `outputs/E1_parameters` used seed 17, priority counts 2/3/1, stations [4,7], a 06:00 start, and 5401 seconds. It produced 3 windows and 37 candidates. Baseline scored 9.8 with coverage 3/6, and the replan scored 5.0 with coverage 1/6. Both had zero violations. The run used the explicit settings in `outputs/E1_parameter_config.yaml`.
- The cache hit on real seed 42. Each of the three final seeds used its own cache and reran validation. Changing raw hashes, selected sample, stations, start time, duration, filters, or sampling produced a different key. Modified cache content was rejected.
- The targeted 1.2-second timeout test launched descendant processes and terminated the whole process tree. The 0.05-second CLI test returned BLOCKED/3 and retained `console.log`, `execution.json`, `failure.json`, and the manifest. The tests used those short timeouts and performed zero automatic retries.
- Reference integrity is recorded in `outputs/reference_integrity.json`. All 114 files from the original project matched the original inner ZIP, which retained its original bytes.

## Self-checks, budget, and retained failures

Compilation and static checks covered input handling, independent validation, resource cleanup, parameter paths, and Git data boundaries. The round reused Python 3.11.17, NumPy 2.4.6, Skyfield 1.55, sgp4 2.27, and PyYAML 6.0.3. The first synthetic run showed that the shared scheduler's default tuple could not be concatenated with a legacy list. The fix passed on rerun, and the original failing artifacts remain in `outputs/E1_synthetic`.

The optional legacy re-evaluator returned BLOCKED/3 when called through the new isolated entry point. See `outputs/optional_evaluator_check/optional_evaluator.json`. Its contract SHA256 and event rules still require reconciliation before acceptance.

Computation and tests finished within the 15-minute target. Detailed timings are in `execution.json` and the pytest XML. The measure covers computation and tests only. Real-case timeouts, cloud evolution runs, and credits consumed all totaled zero.

## Pending confirmations, unrun work, and limits

A clearly labeled delivery from Team Member 1 had yet to arrive, and external confirmation with Team Member 3 was pending. The interface and a review checklist were prepared, with messages still unsent. The planned October 24 work was to compare the existing improved method across the frozen seeds and make a before-and-after fault demonstration. Scaling to 180 or 300 targets, creating a web app, and repeating the extra re-evaluation were outside this round.

Assumptions included one successful task per target, zero points for an interrupted task, and elevation treated as approximate ellipsoidal height. Nighttime conditions, target illumination, Sun and Moon exclusion, weather, tracking, field of view, terrain, and state estimation remain unverified. The coarse-to-fine window search and one-second checks validate the sampled grid and support no claim of continuous-time feasibility or completeness. Standard-window mode validates scheduling within supplied windows. Task points use the experiment's own scale, and the two original scoring conventions remain to be confirmed for official reporting.

## 2026-10-23 E3 and E4 with the demo

The `work/improvement-demo` branch started at `9765eb8` and inherited both methods, including the existing scheduler and tuning. The following results were generated in this round. See [IMPROVEMENT_DEMO_HANDOFF.md](docs/IMPROVEMENT_DEMO_HANDOFF.md) for the full fields, evidence, and commands.

The run root was `outputs/improvement_demo_20261023_150452`. E3 froze and reused samples, windows, candidates, and the physical fault events from three original source directories. Candidate bytes matched individually, source and raw-input hashes matched before and after, and both methods derived their own impact lists.

| Seed | Baseline initial / after fault | Improved initial / after fault | Initial / after-fault gain | Coverage for both methods (all / executable) | Violations | Initial candidate bound |
| --- | --- | --- | --- | --- | ---: | ---: |
| 42 | 173.2/172.4 | 184.0/184.0 | +10.8/+11.6 | 56/60 · 56/56 | 0 | 184.0 |
| 17 | 180.0/182.0 | 190.0/190.0 | +10.0/+8.0 | 57/60 · 57/57 | 0 | 190.0 |
| 23 | 178.2/176.2 | 189.0/189.0 | +10.8/+12.8 | 57/60 · 57/57 | 0 | 189.0 |

The upper bound sums the highest integer points per target from this round's candidates while relaxing resource constraints. The comparison measures each method's full initial scheduling and replanning workflow. It cannot isolate the replanner's contribution or establish statistical significance or general optimality. The four task tables for each case underwent independent one-second checks against the original TLEs. Input preparation reused sealed windows. See the handoff and `experiments/comparison.csv` for `perf_counter` stage timing and coverage by priority.

E4 used seed 42 with station 2 out from 01:03:03 to 03:03:03 UTC. Actual completed, locked, interrupted, and affected future counts were 14/1/1/2 for baseline and 10/1/1/4 for improved. Post-fault scores were 172.4 and 184.0, a gain of 11.6, with zero violations in both. Net adjustments were 5 and 18, with zero additions and deletions. Sixteen independent history attack and valid-control checks on real data met expectations, including two valid controls. The backfilled baseline negative case specifically required rejection on history provenance grounds. Resource isolation was outside the claim for that case.

All 65 pytest cases passed in 19.03 seconds, including 43 existing and 22 new cases. For the default seed 42, the four legacy task CSVs and the candidate CSV matched the original baseline byte for byte. That cold run measured 25.623 seconds for window calculation and 29.084 seconds for the full command. A fresh output directory reproduced all five tables from prepared artifacts and ran independent validation again. Testing reused the existing environment. The complete later-fault directory retained the SHA256s of all 56 files during the read-only recheck.

The deliverable `demo_delivery/index.html` is an offline replay of real results. Scores, coverage, and priority coverage match the independent reports. Errors and missing files yield a status other than success. The `browser_delivery/browser_checks.json` file records 33 browser checks covering all cases, methods, and views, play and pause, stepping, task details, zoom, and narrow screens. Three actual PNG screenshots were inspected. The original Chinese narration script is documented in `docs/DEMO_SCRIPT.md`. The synthetic run `outputs/demo_synthetic_run` and demo `outputs/demo_synthetic_html` were also generated, with the page explicitly identifying the synthetic inputs and supplied-window scope.

The 27 serial compute and test commands used 147.226 seconds of the 600-second budget, leaving 452.774, with 21 PASS and 6 FAIL. See `run_ledger.json`. Failed attempts 8, 10, 12, 13, 16, and 17 are preserved. The handoff describes the issues and fixes. The record preserves failed attempts and bounded retries. The compute budget excludes reading, editing, writing, and time from the legacy re-evaluator. Final per-item acceptance is in `acceptance.json`. The algorithm, independent legality, history, demo data, browser, read-only check, and reproduction in both the default and a fresh directory all passed. Team Member 1 delivery and Team Member 3 confirmation remained PENDING_EXTERNAL, the legacy re-evaluation remained BLOCKED, and video and clean installation were NOT_RUN.

## 2026-10-23 P1 directory safeguards and E5 controlled comparison

This round began at `97d41e6` on `work/path-safety-replan-e5`, with P1 commit `341ac9e`. The earlier rounds keep their original records. The results below were run in `outputs/path_safety_e5_20261023_164001`.

Running the original entry point against a complete source copy reproduced source contamination. It returned 2 and added `nested_output`, `snapshots`, and `frozen_inputs.json`. The fix moved checks on all sources, raw inputs, configurations, events, outputs, caches, ledgers, logs, and temporary files ahead of the first write. It also covered direct preparation and summary calls. The same test returned 2 after the fix, with the complete fixture tree and all hashes preserved, including empty directories. All 14 new path tests passed, including actual Windows junction coverage. See `before_fix/reproduction.json` and `path_fix_verification.json` for before-and-after evidence.

The E5 common starting plan was the OLD/E4 `initial_frozen_baseline.json`, with 173.2 points and 56 targets. Its SHA256 was `1b37fab094cb6b2a9f0d99aa92d0c018d8ad02a4de14e42f1aba831b1963ec8c`. Both methods used 14 completed, 1 locked, 1 interrupted, and 2 affected future tasks derived once from the same original plan. They also shared ordered candidates and the event. Inputs were byte-identical before and after each method.

| Method | Final score | Fixed history / new task score | Coverage (all / executable) | High / medium / low | Violations | Replanning (s) | Independent validation (s) | Added / removed / moved / retained | Net adjustments |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | --- | ---: |
| baseline | 172.4 | 51.0/121.4 | 56/60 · 56/56 | 18/18/20 | 0 | 0.003326 | 0.330910 | 0/0/5/51 | 5 |
| improved | 182.0 | 51.0/131.0 | 56/60 · 56/56 | 18/18/20 | 0 | 0.083727 | 0.391897 | 0/0/23/33 | 23 |

The gain from the common start was 9.6 points. The conditional relaxed bound of 182.0 sums points fixed by successful history and the best post-fault valid future candidate for each unfixed target, relaxing resource conflicts. The old E4 gain of 11.6 used different initial plans, and the old score of 184 does not establish an attainable target under this common history. Input and validator preparation took 0.097736 seconds, independent validation of the common initial plan 0.273137 seconds, and history and future candidate preparation 0.002353 seconds. Total internal time was 2.430907 seconds, and the outer command took 3.196393 seconds. Method timings include internal fallback and exclude reading, copying, hashing, and independent validation. Each was observed once.

All 94 tests passed in 25.92 seconds, including 65 existing tests, 14 path tests, and 15 E5 fairness and history tests. Sixteen real E5 valid and attack controls met expectations. Tests exercised malformed data only in full or in-memory copies, and each invalid history had to trigger an independent history provenance violation. The dedicated E5 read-only verification propagated the TLEs again and preserved the full tree and hashes of 33 files and 3 directories. The E3/E4 rerun in a fresh directory produced four cases and 16 schedules. All 16 task CSVs and four candidate CSVs were byte-identical to the original delivery. The demo was regenerated from the new results and passed all 33 browser checks. The original demo, the full OLD directory, the three original sources, raw inputs, environment inventory, and ignore rules were unchanged by the checks.

The 20 serial outer commands took 152.042 of 600 seconds, leaving 447.958, as measured solely by `run_ledger.json`. The outer wall clock already covers the old ledger in the copied fixture. The pre-fix CLI exit code of 2 and source contamination are preserved. The negative-case wrapper passed because it reproduced the expected defect. See `acceptance.json` for acceptance by component and `final_code_checks.json` for the final supplemental code check. External confirmation from Team Members 1 and 3 remained pending, and the optional legacy re-evaluation remained BLOCKED. The optional second common start, environment reinstallation, full optical checks, and official scoring were outside this round. See the [P1/E5 handoff](docs/PATH_SAFETY_E5_HANDOFF.md) for hashes, data, limits, and commands.

## 2026-10-23 temporary-file hard-link fix

The `work/atomic-write-hardening` branch started from `b504f93`, focusing on I/O safety with the existing algorithm. The output root was `outputs/atomic_write_fix_20261023_182047`. See the [complete handoff](docs/ATOMIC_WRITE_FIX_HANDOFF.md). Earlier results remain under their historical sections.

Before the fix, a fresh synthetic fixture protected its `raw` directory. The paths `ledger.tmp` and `raw/input.txt` resolved to the same file (`samefile=true`), so the preflight allowed them. Both the budget `execute` and the complete `run_improvement` entry points returned 2, but the input was replaced by ledger JSON. The test commands, before-and-after SHA values, and full tree are in `before_fix/reproduction.json`. The fix exclusively creates a temporary file in the same directory with `mkstemp`, closes it, and then replaces the destination atomically. The same test safely saved the ledger. A deliberate later error still returned 2 and preserved the raw input, empty directories, and the old alias. JSON and CSV output and repeated summary writes use the same safe approach and leave pre-existing regular files and links in place.

All 117 tests passed with zero failures, errors, or skips, including 94 existing and 23 new tests with actual Windows junctions and hard links. Fault injection covered serialization, partial writes, `fdopen`, replacement, and cleanup failures. It confirmed that destinations and inputs held their original content, and that budget states RUNNING, PASS, FAIL, and BLOCKED and rejection of incomplete work held. Pytest took 28.86 seconds and the outer command took 29.326782 seconds. JSON and CSV formats remained compatible, and the six newly sealed directories contained zero temporary files from this run.

This round's E5 run again produced baseline 172.4 and improved 182.0, with 51.0 fixed points, 121.4/131.0 new-task points, a gain of 9.6, coverage 56/60 and 56/56, net adjustments 5/23, and a conditional bound of 182. The common history was 14 completed, 1 locked, 1 interrupted, and 2 affected future tasks, with 6839 future candidates. Original TLE checks each second and at both task endpoints found zero violations. Both task CSVs matched PREV byte for byte, and the read-only recheck preserved 33 files and 3 directories. E3/E4 reran four cases and 16 plans with all 16 task CSVs and four candidate CSVs byte-identical to OLD. The new demo passed all 33 actual browser checks, and three screenshots were inspected.

The run preserved the raw inputs, three old sealed sources, the complete OLD and PREV trees including empty directories, `requirements-lock.txt`, and `.gitignore`. The sole ledger `control/run_ledger.json` records 15 outer commands totaling 81.018276 of 600 seconds, leaving 518.981724 seconds. All outer commands passed as expected, including those designed to observe a negative case or injected failure. Internal code 2 or BLOCKED results are reported as such. New algorithm experiments, environment installation, full optical checks, and official scoring were outside this round. External confirmation from Team Members 1 and 3 remained pending, and the extra legacy re-evaluation remained BLOCKED.

## 2026-10-23 stable handoff and standard-window intake

The `work/stable-handoff-intake` branch was created from algorithm candidate `b0eb3b5`. It added portable `team3_run`, read-only `inspect_team1_input`, and `build_handoff` with a Git commit export allowlist. The existing planner core, scheduling, scoring, independent validation, safe writes, and default algorithm were used. The output root was `outputs/stable_handoff_20261023_190522`. The sole new 600-second ledger was `control/run_ledger.json`, with its own independent budget.

Before commit, the local workflow ran the synthetic baseline, evaluated the initial and fault task sets, and performed the read-only recheck. Initial score was 10.0 with coverage 3/3, and post-fault score was 3.0 with coverage 1/3. Both had zero violations and preserved the complete input and result trees. The intake entry point read all four synthetic files and all four official frozen reference files, which included 60 targets, three stations, and 563 windows. Of those, nine were shorter than 120 seconds, 554 could fit 120 seconds, and 502 could fit 240 seconds. This validation used supplied windows. Physical certification and new orbit propagation are outside its scope. The source BASE sealing manifest, historical tasks and metrics, and demo hashes were verified first.

The final source package was to be built from the Git objects of the code commit, then extracted and run from a fresh directory with Chinese characters and spaces in its path. The final package version, size, and SHA256 were to appear in `packages/packages.json` and the packaged manifest. The root's `portable_validation.json`, `pytest.xml`, `acceptance.json`, and ledger were to record relocation and reference-input intake, browser checks, the original 117 tests and new tests, full protection snapshots, and actual budget. These release checks were scheduled for after commit, with actual statuses and failures to be reported in the delivery response.

The limited search of `data/raw`, `data/processed`, and specified handoff material found no definite Team Member 1 delivery. Direct trial intake was PENDING_INPUT/NOT_RUN, and confirmation by Team Member 3 was PENDING_EXTERNAL. The intake checklist, receipt, metadata template, and draft notes for Team Members 1, 3, and 4 were prepared, with zero messages sent. E3/E4, the demo, and E5 were complete, and outdated follow-up plans were updated. A clean install, full TLE relocation, full optical checks, and official scoring remained unverified. The extra legacy re-evaluation remained BLOCKED. See `docs/STABLE_HANDOFF.md`, `TEAM3_INTEGRATION.md`, and `TEAM1_DATA_INTAKE.md`.

## 2026-10-26 control studies in rounds 4 through 7

Experiment dates and times such as 00:30 and 02:00 are UTC.

These rounds used the same frozen date, 60 targets, three stations, 24 hours, and 563 supplied windows. Round 4 paired the fault replans within each existing starting plan A and B. The methods differed by 9.6 points at each start. From baseline to improved, the adjustment counts went from 5 to 23 and from 33 to 18, respectively. These counts vary with the starting plan. The same seven target duration upgrades produced the gain for both starts, so the results are related.

Round 5 finished the local report revisions and a four-document candidate, with zero new scheduling experiments. That candidate covers results through round 4. Rounds 6 through 8 are covered by this record. The older Word and PDF documents and Demo retain their original scope.

Round 6 preset six outage events across two starts, giving 12 pairs and 24 faulted schedules. The method difference ranged from 4.0 to 10.8 points. The fixed-grid averages for A and B were 7.4 and about 8.2667 points respectively. They describe these related settings only. The study does not establish independent random repetitions, a population win rate, or statistical significance. All plans covered 56/60 and 56/56 targets, with zero violations within the supplied windows.

Round 7 generated eight genuine active no-fault replanning controls at the same times and matched them to the round 6 faulted schedules.

| Starting plan / time | baseline C | improved C | Method score difference |
| --- | ---: | ---: | ---: |
| A / 00:30 | 173.2 | 182.0 | 8.8 |
| A / 02:00 | 173.2 | 180.0 | 6.8 |
| B / 00:30 | 174.0 | 184.0 | 10.0 |
| B / 02:00 | 176.4 | 184.0 | 7.6 |

D is the fault score F minus the no-fault score C for the same method. The method gap G is improved minus baseline. The interaction is the fault G minus the no-fault G. Across 12 matched groups, F−C was 0 for improved and ranged from −1.2 to +2.8 for baseline. Interactions ranged from −2.8 to +1.2, with three positive, three zero, and six negative. The eight controls were shared by fault station across the 12 groups. Active no-fault replanning and leaving the frozen original plan in place are distinct reference modes. Equal scores can come from different schedules and adjustment counts.

The method differences observed in fault scenarios were already present during active no-fault replanning. The full gap therefore cannot be attributed specifically to the fault. Rounds 4, 6, and 7 validated scheduling within supplied windows. Earlier per-second raw TLE checks cover their original cases.

## 2026-10-26 new-target validation in round 8

Experiment dates and times in this section are UTC.

The algorithm was frozen before stratified sampling from the eligible raw population using a pre-sealed SHA256 ordering. The historical exclusion set held 181 targets. Samples H1 and H2 each had 60 targets, 20 at each priority. They were disjoint from the exclusion set and from each other. Sampling preceded window calculation and scheduling, with selection independent of visibility and score. Both samples used the same orbital elements, the full day of August 3, 2026, stations 1, 2, and 3, and the original geometry and candidate rules. This validates new targets within that common setting. Different dates, epochs, and independent external data remain outside its scope.

| Sample | Windows | Candidates | All targets | Originally executable targets |
| --- | ---: | ---: | ---: | ---: |
| H1 | 544 | 9192 | 60 | 58 |
| H2 | 564 | 10101 | 60 | 58 |

Each sample had one cold production run with zero propagation errors. Its initial baseline and improved plans were frozen as A and B. At 02:00, each starting plan yielded a no-fault C and a fault F for both methods, with station 1 out from 02:00 to 04:00 in F. The initial and replanned schedules totaled 20. The event timing was fixed independently of plan impact. C and F each derived the appropriate history.

| Sample / starting plan | Frozen initial score | C baseline | C improved | F baseline | F improved | Interaction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| H1 / A | 183.6 | 183.6 | 189.2 | 183.6 | 189.2 | 0.0 |
| H1 / B | 196.0 | 189.2 | 196.0 | 189.2 | 196.0 | 0.0 |
| H2 / A | 175.2 | 175.2 | 183.6 | 175.2 | 183.6 | 0.0 |
| H2 / B | 192.0 | 180.8 | 192.0 | 179.6 | 192.0 | +1.2 |

The fault G values were 5.6, 6.8, 8.4, and 12.4 points, and the no-fault G values were 5.6, 6.8, 8.4, and 11.2. Improved F−C was 0 throughout. Baseline F−C was −1.2 for H2/B and 0 elsewhere. Initial method gaps were 12.4 for H1 and 16.8 for H2. They refer to initialization, with the common-start replanning comparisons above. The calculations first subtract integer points and then divide by 5, preserving negative values.

All 20 plans covered 58/60 and 58/58 with zero violations. All 20 independent rule and history checks, 20 original CLI invocations, and 20 TLE geometry reports with one-second sampling passed. Both real negative cases returned nonzero exit codes. Independent recalculation, protection, and manifest checks also passed. For C, the original CLI and TLE checks used a projection that changed only `status` to `success`. The independent external checker accepted the actual history. F used the original event, frozen initial plan, and interruption evidence. All four frozen initial plans had zero active station 1 tasks at the event time. The round therefore had zero nonempty interruption segments, and the 20 reports provide new one-second geometry evidence for successful tasks only.

Controlled top-level commands consumed 184.991159200 of 600 seconds, including production, both methods, checks, protection, and final machine verification. Nested durations count once. Time for reading, editing, and assembling report text was accounted for separately. The measure applies to the controlled commands and does not support a concurrent repeat performance study with earlier rounds. Peak memory was unmeasured. The interface did not expose which fallback branch ran, leaving fallback activation unknown.

### Regression under active no-fault replanning

Baseline C lost 6.8 points from the frozen H1/B initial plan and 11.2 from H2/B. Baseline held its score from both A starts. Improved gained 5.6 and 8.4 points from A and held its score from both B starts. The existing improved method falls back only against its internally rerun baseline. The experimental validity PASS covers those results. A safeguard against degradation relative to the frozen original plan still required implementation and verification, followed by separate checks for scale, different dates, and receiving environments. The round preserved the original algorithm and samples when reporting negative differences.

The independent round audit passed. The four starts and shared C/F inputs yield related comparisons. General causal conclusions, statistical significance, and the attributable share of fault-specific gain remain outside the evidence. Elevation checks at one-second intervals support geometry checks within the model. Continuous-time feasibility, completeness of the window search, full optical equipment, and official scoring remain unverified. Full data and per-task evidence are held locally. The repository provides aggregate summaries of these real-data experiments.

## 2026-10-27 native safeguards, scale, and date changes

R9 verified the strict J safeguard in isolation. R10 integrated `no-fault`, `evaluate-no-fault`, and native `recheck`. R11 added the final 32-second solver admission check, absolute parent and child deadlines, a single 30-second Clock, and unknown counts after a forced kill. The R11 snapshot passed a complete 280-test regression (149 + 103 + 28) with zero failures, errors, or skips. This count belongs to that historical run. Source provenance tree `54766909c8f539c8af3cfe733378da7e3aafc347206d904f7b5dbaed6f5a3354` identifies the source tree separately from the final Git commit.

| Round | Fixed conditions | Executed matrix | Improved minus baseline selected score | Selection branches |
| --- | --- | --- | --- | --- |
| R12 | Same raw inputs and date, new 180 targets plus a nested 60, A/B starts | 8 keys, 12 solves, 24 external checks, 12 geometry checks | H60 A/B=3.2/0, H180 A/B=35.2/0 | 2 accepted / 2 lower-score / 4 ties |
| R13 | Same 60 targets, Aug 5 and Aug 6, t3600 | 8 keys, 12 solves, 24 external checks, 12 geometry checks | D1 A/B=5.2/0, D2 A/B=7.2/0 | 2 accepted / 2 lower-score / 4 ties |

Each round's normal paths ran eight native evaluations, eight native rechecks, and zero new solver calls for those checks. Lower-score and tied results selected the originals with zero physical disruption. R12 passed an actual new-path relocation. R13 recorded its smaller smoke and cross-date mismatch case separately. Its relocation and full 280-test suite were not repeated. Date and TLE age varied together. The experiments share targets, starts, and/or model dates, so they support related comparisons within these cases only.

R11 retains the earlier failed 8387.504-second attempt and the subsequent 368.955-second rerun. R12's 253.184 seconds include 0.782 seconds spent on the failing negative-case adapter. R13's 262.701 seconds include 0.578 seconds for bootstrap and 3.625 seconds for the failing smoke. Rounds and reruns have separate budgets. Original evidence and detailed logs remain local.

An additional parent finalization timing gap was discovered and corrected before that submission. Even with a successful child command, a protection snapshot or finalization crossing the parent deadline must prevent PASS. This source change followed the real-data experiments above and kept the original scheduler and scoring. The PR should record validation of the change separately and assign PASS only to checks actually run.

This section is the historical snapshot at the end of R13, before R14 was run. Later results follow below. Full six-day, ten-station operation with 10,000 targets, full optical equipment, independent sources, availability of historical releases, orbit ground truth, acceptance on another machine or on site, and official scoring remain unverified. Real tables, TLEs, run packages, and local prompts are kept outside the repository.

## 2026-10-29 aggregate record of rounds 14 through 19

The following aggregate facts describe local real-data experiments and recovery delivery. Full real inputs, task tables, TLEs, manifests, and recovery bundles remain local. The product used the 98-file source tree from published commit `83d3014` with the original algorithm. This documentation records those experiments. Additional code regression testing and on-site acceptance are outside its scope.

| Round | Result | Completed scope and limits |
| --- | --- | --- |
| R14 | Matrix PASS | Same H60 and date. Three- and ten-station cases shared a three-station initial plan. Eight native keys, 10 schedules, 22 + 2 external checks, and 10 geometry checks. The original seal terminal record is missing, and part of the wall clock was omitted. |
| R15 | PARTIAL | Four native t2 runs succeeded and were wrongly rejected by the external checker. Fully accepted 0/8, with all four t3 runs blocked by dependencies. A rerun after the fix remained pending. |
| R16 | BLOCKED | The checker replay passed, the preparation budget was exceeded, and actual calls totaled zero. Control accounting and sealing version provenance have recorded limitations. |
| R17 | Data, seal, and version PASS | Eight nodes, 8 schedules, 24 backend runs, 28 external checks, 8 conversions, 8 new geometry checks, and 4 old bindings. All eight ties retained the original. |
| R18 | Data PASS, overall PARTIAL | Two initial and four native runs, 6 schedules, 12 backend runs, 12 main external checks, and 6 new geometry checks. A missing directory caused the finalizer to exit with code 1 before seal could start. |
| R19 | All four recovery checks PASS | Read-only verification, actual sealing of a new package, recovered execution version, and independent relocation. New schedules, backend calls, and TLE propagation each totaled zero. The original R18 result remains recorded separately. |

In R14, the ten-station selected plan gained 21 to 85 integer points and covered four more targets than the three-station plan. The figures show this instance's sensitivity to resources from a common three-station initial plan. Ten-station optimality from empty history and general monotonicity remain beyond the comparison. R17 validly retained the archived t3600 anchor into the chains to t4800 and t6000. A/B integer score gaps remained 16/54, and completed counts were correct both per stage and cumulatively. The four t3 primary scores reached their relaxed bounds for their respective fixed histories. Extending these static chains yielded zero new gains.

R18 specifically added ten-station initialization from empty history.

| Starting plan | Initial J | Change from old three-station initial plan | Completed tasks / integer points at t3600 |
| --- | --- | --- | --- |
| Baseline initialization | (914,60) | (+41,+4) | 53/794 |
| Improved initialization | (1000,60) | (+75,+4) | 21/250 |

J uses the authoritative integer points and unique coverage. Dividing integer points by 5 yields task points. Three of the four native runs tied, and one scored lower, so all retained the original plan. From the improved initial plan, baseline raw scored 964 and selected retained the byte-identical original at 1000, recovering 36 points under the safeguard. Both starts had a selected method gap of 0. The new baseline start later selected 914, below old paths 958 and 974 by 44 and 60 points. The initialization gain applies to the initial results only. Full J includes future tasks. The early completed count and the full-day score use separate measures.

R18 had complete data evidence, but the finalizer failed before creating the manifest, reproduction package, or terminal record because the `controller_sources` parent directory was missing. R19 read the then-unsealed 1272-file observation snapshot without modifying it. It reviewed the two historical initial plans, four native runs, six schedules, 12 backend results, 12 main external checks, six geometry reports with 82080 samples, two byte-identity proofs, six historical references, six old bindings, and two negative cases. It then produced a new recovery delivery. Its global manifest applies to this recovery observation.

R19 formally recovered one package with zero formal failures. One failure during forensic preparation remains recorded. The ten final recovery tools had matching identities across frozen qualification, preparation, formal sealing, and relocation. Some older development edits were not archived version by version, limiting traceability for that phase. R18 incurred 208.426582 seconds and R19 independently incurred 169.646280 seconds, each against its own 600-second limit. R18's 60-second advance for failing seal was charged. The reserve for the unstarted post was unspent. R19 succeeded in recovering a new package, with the original R18 overall status still PARTIAL.

Independent relocation reconstructed the deliverable at a second path on the same machine, using an isolated Python environment and read-only file-access auditing. The old-path probe was denied, and a copy with a missing file failed. This verifies the dependency boundary for this acceptance. General security sandboxing, operation on another machine, and on-site equipment certification are beyond the scope. Geometry verification reviewed existing reports and bindings with zero new TLE propagation.

Full optical equipment, six days with ten stations, 10,000 targets, window-search completeness, continuous time, independent orbital sources, availability of historical releases, and official scoring remain unverified. See the [R19 recovery record](docs/R19_RECOVERY_STATUS.md) for the public summary. The recovery tools remain isolated research material outside the product API.

## 2026-10-30 common input delivery in round 20

R20 reached INPUT_DELIVERY_PASS, with four PASS results for the input, seal, execution version, and readback from a new path on the same machine. It produced only the common research input for H180 and ten stations. Scheduling, native no-fault backend, initialization, and native runs each totaled zero, so this is an input delivery with no new algorithm PASS, J, completed count, or method gap. R18 remains PARTIAL. R19 and earlier failures remain in their original records.

| Aggregate item | Observed |
| --- | --- |
| Targets / executable targets / stations | 180/180/10 |
| High / medium / low priority | 60/60/60 |
| Windows / full candidates | 6709/116223 |
| Targets with zero candidates / target-station combinations with zero windows | 0/153 |
| Windows / candidates for the H60 subset | 2173/39720 |
| Windows / candidates for the remaining 120 targets | 4536/76503 |
| Windows reused | 0 |
| Independent direct geometry sample points | 20127 |

The model spans 86400 seconds from 2026-08-05T00:00:00Z, using the same ten stations and numerical parameters as R18. H60 is strictly nested in H180, and all nine raw-file identities match. R12's earlier H180 windows were for Aug 03 and remained outside this round. Historical H60 lacked full byte-level provenance for dependencies and built-in time-support data, so the run regenerated all 1800 combinations from cold inputs. Windows were consistently sorted, numbered, and mapped in sidecar data. The original `make_candidates` reproduced all candidate bytes. The candidate pool can contain mutually conflicting entries.

The scalar sgp4 check evaluated 10000 raw TLE epochs. The production vector backend made 14725 calls over 20952285 samples, with 13078 geometry `elevations` calls and another 1647 independent direct geometry calls. Propagation errors totaled zero. These counts cover production and geometry. The run made zero native no-fault backend or scheduling calls. The input verification's read-only phase logged `propagation_calls=0`, separately from production. Checks covered every window's start, last valid integer second, and midpoint, at a tolerance of 1e-7 degrees and a maximum direct/reference difference of 0 degrees. The `end_s` endpoint is inclusive. Negative evidence from empty combinations applies to this sample. It gives no guarantee of continuous-time search completeness or full optical observability.

Summing each target's maximum candidate score gives 3000 integer points, corresponding to score 600. This relaxed input bound omits resource conflicts. Joint feasibility, achieved optimality, and method gains remain outside that calculation. The aggregate comes from the actual H180 pool.

The full 99-file source tree was pinned to `b0e646159a36a4d4375afc083f3b8db793bc131b`. Production modules matched the version bound to R18/R19. Five control and protocol files were frozen before production. Formal production and seal each ran once, with zero formal failures. The qualification positive case completed the actual archive, seal, and terminal stages. Duplicate IDs, wrong dates, wrong bindings, missing files, byte modifications, nonzero exits, and short timeouts were rejected as expected. Preflight and final report command failures are recorded separately from the formal run count.

Independent accounting was 530.423 of 600 seconds. Preparation took 442.438 seconds, including 370.906 seconds for formal production. Seal accounted for 60 seconds, independent acceptance for 7.985 seconds, and the closing allowance for 20 seconds. Early tools without a full UTC reference were conservatively charged 45 seconds of preflight. The ledger measures this round's accounted work. The overall conversation and prior rounds have separate boundaries. The new path used only packaged research material and the bound Python runtime. A missing-file copy returned 1. The package records dependency identities, and the runtime was supplied separately on the same machine. This verifies that machine's acceptance access boundary.

Full data, research tools, ZIPs, machine receipts, and local paths remain local. The public update is documentation only, with the original API and scoring scope. R21 had yet to run when R20 was delivered. The next section records its later attempts separately. See [R20 input delivery](docs/R20_INPUT_DELIVERY.md).


## 2026-11-01 partial matrix and executor qualification in rounds 21 through 27

R21 consumed R20's common input for H180 and ten stations. Five of six groups started and two fully passed. The two initial J values were (2758,180) and (3000,180). Three native workflows timed out in later stages, and the last was blocked by budget. Native acceptance was 0/4 and the overall status PARTIAL. With no complete common-initial-method comparison, method gains omit residual candidates that failed acceptance. The backend counts remain recorded as four completion receipts, five confirmed starts, two unknowns, and a start interval of [5,7]. These timeouts apply to the workflows as a whole.

R22 and R23 remained PARTIAL during read-only recovery and readback revisions. R24, R25, R26-A, and R26-B were BLOCKED. R26-A ended due to a startup timing gap. R26-B completed 12 local Job checks, with full qualification unrun and historical protection unfinished at expiry. Later successes are recorded apart from these original failures.

R27 reached R27_EXECUTOR_QUALIFICATION_PASS. After recovering the candidate on the same machine, the actual post and original accept each ran once with original exit code 0. All 18 built-in negative cases, the old-root read denial probe (0 bytes), and two fresh audit layers passed. Identities matched for 37 regular core members, 38 candidate ZIP entries including the root manifest, and 11 freeze entries. Verification passed for 22624 historical files, 3 trees, 41 consumed originals, and parent Job cleanup. Formal seal and post counts were both zero. The pass covers executor qualification only.

The saved parent sample of 423.5412529 seconds can be recalculated. The execution handoff separately reported a final sample of 423.59 seconds and 428.72 seconds through the last tool return. The two handoff figures are sourced to the external handoff. The delivery directory has no separate final-return receipt from which to independently recalculate them. The saved stages and parent sample were below 600 seconds. Each round has its own budget, separate from cumulative development time.

R27 made zero new solver, production schedule or backend, TLE, or task geometry propagation calls. Semantic review of saved rules, bounds, and geometry reports is recorded separately. There were no new J scores, completed counts, or method gains. The runtime remained external to the package. The 3935 declared runtime read identities cover that mapping, with full-environment, cross-machine, and on-site equipment acceptance beyond this scope. Real data, research tools, complete manifests and ZIPs, machine receipts, and the local prompt remain local. See [R27 executor qualification](docs/R27_EXECUTOR_QUALIFICATION.md).

## 2026-11-02 technical delivery and startup timing in rounds 28 through 32

R28 ran seal, post, and accept once each, all exiting 0. Eighteen negative cases, two audit layers, and protection of 22624 files and 3 trees passed. The execution file was read before registration, and full timing evidence for the preceding stage was missing. The overall status remains PARTIAL, with whole-round budget closure unverified.

R29 and R30 remained BLOCKED due to reads before registration. Their original timing and status records are preserved. R31 passed 30 startup qualification checks by registering on the first tool call before reading. Two small commands actually exited 0 and 7, with waiting and cleanup passing. Application operations totaled zero. The saved sample was 334.303 seconds. External handoff evidence conservatively covered the final return at 337.406 seconds, separate from the parent JSON. This round validated startup qualification only.

R32 preparation took 151.434 seconds, exceeding the 80-second hard limit and failing budget admission. The specified native run never started. Protection verified 22624 files, three trees, and 18 consumed originals. Finalization also timed out, and the archival script exited 1. The minimum failure record was 702.082 seconds. A complete ledger was never produced, so the status is BLOCKED and budget closure remains unverified.

## 2026-11-02 H180_BASE common-start pairing in rounds 33 and 34

R33's early A attempt was blocked by missing reusable bootstrap code or state. B passed registration and entry point SHA checks. Its launcher record creation and short capture both exited 1 due to write permissions, and a deviation also occurred from reading before registration. A and B remain BLOCKED. For B, the application call count, protection, and cleanup are unverified.

R33-C reached R33_H180_BASE_BASELINE_PASS and R34 reached R34_H180_BASE_IMPROVED_PASS. Both consumed the same frozen H180_BASE initial plan for the full day of 2026-08-05, with 180 targets, ten stations, 6709 windows, 116223 candidates, and t3600. The product was bound to the complete 100-file tree at `1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5`. Both rounds used the same source, rules, retained plan, declared runtime, and budgets of 30 seconds for the solver, 180 for the workflow, and 230 for the group. The paired comparison varies the method under the executed product version above.

| Aggregate item | R33-C baseline | R34 improved |
| --- | ---: | ---: |
| retained J | (2758,180) | (2758,180) |
| raw J | (2758,180) | (2806,180) |
| selected J | (2758,180) | (2806,180) |
| Selection branch | KEEP_RETAINED_TIE | ACCEPT_CANDIDATE_STRICTLY_BETTER |
| Targets with net adjustments | 0 | 49 |
| Native / solver | 1/1 | 1/1 |
| Exact backend starts / completions | 3/3 | 3/3 |
| Propagation calls | 360 | 360 |
| Scheduled integer-second samples | 39060 | 40020 |
| Samples across both propagation paths | 78120 | 80040 |
| Last saved accounting sample (seconds) | 173.1593674 | 235.8957645 |

From the common start, the selected plan gained +48 integer points, or +9.6 task points on the current points/5 scale, with zero change in coverage. Eight of the 49 adjustments upgraded durations from 120 to 240 seconds and contributed the full difference. One high-priority target contributed +10, five medium-priority targets contributed +30 in total, and two low-priority targets contributed +8. The other 41 adjustments kept the same score. Stations changed for 34 targets, and start and end times changed for 47. These counts overlap duration upgrades. The pair provides no evidence of reduced disruption. The extra 960 seconds of task duration accounts for exactly 960 additional scheduled samples including endpoints and 1920 additional samples across both propagation paths.

Fixed completed and locked history contributed 1736 integer points. Taking the highest available score per remaining target in the frozen discrete pool adds 1070. Hence 2806 is the conditional relaxed primary-score bound when some resource couplings are relaxed. R34's valid selected plan attained that bound for this fixed history and pool. Continuous-time schedules, the initial full-day score of 3000, and general algorithm optimality remain outside this finding.

Produce, evaluate, and recheck all exited 0 in both rounds, and saved Job cleanup and data acceptance passed. The saved protection records passed for 22624 historical files, 3 trees, and 3950 consumed originals. This independent audit reviewed those records and experiment copies. A new full scan of historical or runtime originals, new application work, new solves, and new TLE propagation were outside the audit.

The R34 last saved accounting point of 235.8957645 seconds is independently reproducible from the start, QPC, and W. The external terminal handoff additionally reported a terminal reading of 235.9102733 seconds and actual final return coverage of 238.9717645 seconds. R33-C's external final return coverage was 177.011 seconds. The external handoff supplies the final return evidence. Saved parent JSON samples cover their own checkpoints. Each round is separately reported as within 600 seconds. The measurements do not establish a controlled comparison of method performance or measure the full conversation.

The original R21 retains initial 2/2, native 0/4, and backend start range [5,7]. R33-C and R34 brought additional native acceptance across rounds to 2/4 for the BASE start, with both IMP groups pending. The two runs performed zero seal, post, or accept operations, and complete evidence delivery is pending. The evidence covers a single fixed instance. Statistical significance, independent random replications, general improvement, fault-specific gains, full optical equipment, and cross-machine or on-site certification remain outside its scope. This documentation uses the existing Demo, Word, and PDF artifacts. Full data and research tools remain local. See the [pair summary](docs/R33_R34_H180_BASE_PAIR.md) for evidence entry point SHAs and details.
