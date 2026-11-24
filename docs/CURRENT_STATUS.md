# Current Project Status

## 2026-11-18 S02 Product Acceptance

The accepted production commit is `6aacb4a64d5b32d388c7ecbcad7ae361bb31b29d`. The frozen instance covers 1800 targets, 10 observation stations, and 24 hours. After extracting the final product ZIP and installing its dependencies offline, cold generation completed for 1800/1800 targets and produced 68,069 windows and 1,177,265 retained candidates. Independent evaluation and read-only rechecks passed for 2/2 initial planning cases and 4/4 fault-free replanning cases.

All six cases loaded the packaged DLL. Normal solves took 7.04–8.91 seconds. Verification covered the 30-second hard solve limit, descendant cleanup after timeout, and rejection of leftover proposals. All 302 regression tests passed in each of the two environments, one extracted from the final ZIP and one restored from uploads. The 12 task tables for the four H180 cases matched the original acceptance byte for byte.

Acceptance ran on Windows 11 x64 with 64-bit CPython 3.11.17. **Baidu FAMOU acceptance remains pending.** S02 fault replanning, 10000 targets over six continuous days, and broad algorithmic advantages across data sources remain unverified. See the [synthetic example](../README.md#quick-start) and the [release runbook](../famou/RUNBOOK.md) for the entry points.

## 2026-11-17 Formal H180 Acceptance

All four cases in the formal experiment matrix passed sealing, post and readback from a new path, and programmatic accept. See the [H180 delivery record](FAMOU_DELIVERY_STATUS.md).

## R35 Preliminary Review and Earlier Status

As of the R35 preliminary review, H180 native acceptance across rounds remained at 2/4. The H180_IMP baseline and improved cases were still pending. R35-A and R35-B were BLOCKED. R35-C had yet to start while the execution environment's permitted scope was being confirmed. R28 remained PARTIAL, with formal evidence delivery and receipt still open.

Updated 2026-11-02. The latest result at that point was R34_H180_BASE_IMPROVED_PASS for the single H180_BASE/improved case at t3600. The accepted R33-C baseline case used the same starting point. Selected J increased from (2758,180) to (2806,180), gaining 48 integer points, or 9.6 points on the current task scale. Both covered 180 targets. The improved method reached the loose conditional upper bound of 2806 for the primary score under this fixed history and discrete candidate pool. General optimality, fault-specific gains, and official scoring are outside the scope of this result. See the [H180 same-start pair](R33_R34_H180_BASE_PAIR.md).

R20 shared input delivery retains INPUT_DELIVERY_PASS. The original R21 round remains PARTIAL with native acceptance at 0/4. Subsequent rounds brought cross-round native acceptance to 2/4, with both IMP-starting cases still open. R22 and R23 remain PARTIAL, and R24 through R26-A/B remain BLOCKED. R27 passed qualification. R28 passed the technical seal/post/accept chain and remained PARTIAL overall. R29, R30, R32, R33-A, and R33-B remain BLOCKED. R31 passed startup timing qualification only. Original failures remain attributed to their rounds. R33-C and R34 recorded zero seal/post/accept runs.

In R19, evidence recovery review, formal sealing, recovery of the execution version, and independent acceptance from a second new path all returned PASS. New schedule runs, native backend calls, and TLE propagations each totaled zero. The original R18 remains data PASS, sealing FAIL, sealed execution-version acceptance BLOCKED, and overall PARTIAL. The R15 PARTIAL and R16 BLOCKED statuses and original failure records also remain.

The actual calculations in R14 through R18 used the 98-file source at published commit `83d3014c7d030b314320b36682f27e9cc1d0d6a6`. The earlier 97-file development tree and the pre-commit parent wrap-up revision in R11 through R13 are distinct versions. R20 is bound to the complete 99-file tree at `b0e6461`, with production modules matching the prior version. This document reports public aggregate facts. See the [R19 recovery record](R19_RECOVERY_STATUS.md) and [R20 input delivery](R20_INPUT_DELIVERY.md) for their scopes. Real inputs and the full recovery package are kept locally.

## Software and Local Acceptance

Source delivery allowlisting and compatibility with historical fault paths during read-only evaluation and recheck were fixed. Scheduling and scoring use the frozen algorithms. The historical source and extracted-package regression passed 149 tests, with zero failures and zero skips. Use the relevant run and PR checks for regression and GitHub Actions results following this documentation update.

The user assumed the former roles of team members 1, 3, and 4 on the same machine, with AI-assisted execution and independent audit. Each of the two H180_BASE methods adds one accepted case on that machine. Acceptance by other members, on another machine, or at the equipment site falls outside this scope. Existing workflow fields such as PENDING_EXTERNAL retain their original values. The original update covered five public documents, while actual runs remained bound to the 100-file product tree at `1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5`.

| Round | Work completed | Status and scope |
| --- | --- | --- |
| 1 | Cold generation for 60 targets, 3 stations, 24 hours, and 563 windows, with provenance for four tables | Original overall BLOCKED / strict FAIL. A specific version later received read-only consumption approval |
| 2 | Integration at a fixed version and comparison of the full initial planning and fault workflows | PASS within supplied windows. The initial plans differed |
| 3 | Offline playback, a five-page Word/PDF report, and portable materials | Local acceptance passed for that batch |
| 4 | Same-start comparisons from the two frozen A/B initial plans | Independent audit passed. The method gaps were 9.6 points each, within supplied windows |
| 5 | Local report revision and four draft documents | Zero new scheduling experiments. The drafts represent this round |
| 6 | 12 comparisons and 24 plans across six faults and two starting points | Independent audit passed within supplied windows |
| 7 | 8 real fault-free controls and 12 matched comparisons | Independent audit passed. Trials with shared controls are dependent |
| 8 | Two new disjoint 60-target samples, 20 plans, and three verification layers | Independent audit passed. Successful tasks received new per-second geometry checks against the original TLEs |
| 9 | Isolated fault-free selection guard and known regression/tie cases | Known cases passed. Formal integration was pending |
| 10 | no-fault, evaluate-no-fault, and native recheck | 16 native keys passed. 252 historical regression tests |
| 11 | Final solve admission, absolute parent-child deadlines, call counts, and two patches | Rerun passed. 280 historical regression tests. The original failure is recorded separately |
| 12 | Related scales using 180 new targets and a nested set of 60 | 8 keys / 12 solves / 24 external checks / 12 geometry checks. Actual migration to a new path |
| 13 | Two new model days and element-age sensitivity for 60 fixed targets | 8 keys / 12 solves / 24 external checks / 12 geometry checks. Two cross-day mismatch negative cases |
| 14 | Same-day 60-target comparison across three and ten stations with shared initial plans | Matrix passed. 8 keys, 10 schedule runs, 22 + 2 external checks, and 10 geometry checks. Historical sealing terminal and partial wall-time disclosure limitations apply |
| 15 | First attempt at a ten-station continuous chain | PARTIAL. Four native t2 runs succeeded and were wrongly rejected by the verifier. Complete nodes 0/8, with t3 blocked |
| 16 | Verifier repair and preflight | BLOCKED. Preparation exceeded the limit, with zero actual calls. Run-script provenance limitations apply |
| 17 | Complete continuous state chain following control-layer revision | Data, sealing, and execution version PASS. 8 nodes, 8 schedule runs, 28 external checks, and 8 new geometry checks |
| 18 | Ten-station initial plans with empty histories and replanning at t3600 | Data PASS. 2 initial and 4 native runs, sealing FAIL, overall PARTIAL |
| 19 | Read-only recovery of R18 evidence, new-package sealing, and independent migration | All four recovery checks PASS. Zero new solves. Original R18 status remains |
| 20 | Production and delivery of shared Aug05 input for H180 across ten stations | INPUT_DELIVERY_PASS. 6709 windows, 116223 candidates, and zero scheduling runs. Acceptance covers input delivery |
| 21 | H180 initial and native attempts | PARTIAL. 2/6 passed, native 0/4. The original backend start range remains [5,7] |
| 22, 23 | Recovery evidence, readback paths, and supervision revisions | Both PARTIAL. Qualification passed only in part, and formal post acceptance was outstanding |
| 24, 25 | Read identity, Job supervision, and preparation for the full chain | Both BLOCKED. Full qualification was not run |
| 26-A/B | Another attempt to finalize startup and prepare qualification | Both BLOCKED. B passed 12 partial Job checks. Full qualification did not run, and protection was unfinished at the deadline |
| 27 | Full qualification with actual post, FileAudit, and original accept | EXECUTOR_QUALIFICATION_PASS. Zero formal seal/post runs and zero new solves or propagation calls |
| 28 | Technical chain for formal seal/post/accept | One run each, exit code 0. All 18 negative cases, two audit layers, and protection checks passed. Overall PARTIAL because complete pre-registration timing evidence was missing |
| 29, 30 | Startup sequence gate | Both BLOCKED. Reads preceded registration, so the starting points were ineligible |
| 31 | Startup timing qualification with first-tool registration | 30 checks passed. Two short commands exited 0/7. Zero production operations, with qualification the scope of the round |
| 32 | Native run preparation | BLOCKED. The case did not start. Preparation took 151.434 seconds and exceeded the 80-second gate. Wrap-up failed, with a minimum recorded total of 702.082 seconds |
| 33-A/B | Startup state and permissions attempts | Both BLOCKED. B lacked production call counts and complete protection evidence |
| 33-C | H180_BASE/baseline at t3600 | Single-case PASS, selected (2758,180), KEEP_RETAINED_TIE, 0 net adjustments |
| 34 | H180_BASE/improved at t3600 | Single-case PASS, selected (2806,180), ACCEPT_CANDIDATE_STRICTLY_BETTER, 49 net adjustments |

The first round's protection check failed because another task added a subtree to the shared history container. Existing files matched their original bytes. The original failure, subsequent approval for read-only use of the specific version, and other rounds' PASS results are recorded separately. Real data and complete machine evidence are kept locally.

## Fault Gaps and Fault-Free Controls

In round 2, baseline scored 173.2 initially and 172.4 after the fault. Improved scored 184.0 initially and 184.0 after the fault. The initial plans differed, so the post-fault gap of 11.6 points compares full workflows. In round 4, the two methods shared an initial plan, event, and opportunity set within each of A and B. Each pair had a method gap of 9.6 points. From baseline to improved, adjustment counts rose from 5 to 23 for A and fell from 33 to 18 for B. The direction depended on the starting point.

Round 6 fault method gaps ranged from 4.0 to 10.8 points. Means on the fixed grid were 7.4 for A and about 8.2667 for B. In round 7, the fault-free control gaps were 8.8 and 6.8 for A and 10.0 and 7.6 for B at 00:30 and 02:00, respectively. Across 12 matched cases, F−C was 0 for every improved case and ranged from −1.2 to +2.8 for baseline. The interaction ranged from −2.8 to +1.2, with 3 positive, 3 zero, and 6 negative values. Method gaps were already present in proactive fault-free replanning, so the full gap in a fault scenario cannot be attributed to a fault-specific benefit.

## Round 8 New Target Samples

All dates and times in this section use UTC.

The historical exclusion set contained 181 targets. H1 and H2 each had 60 targets, with 20 per tier. Both were disjoint from the sealed exclusion list and from each other. The SHA256-based stratified ordering was fixed in advance, independent of visibility and scores. Both used the same source data, all of August 3, 2026, and three stations. H1 contained 544 windows and 9192 candidates, and H2 contained 564 windows and 10101 candidates. Each had 58 executable targets. Both samples cover a single date and epoch.

For each sample, initial baseline and improved plans were frozen as A and B. At 02:00 each starting point used proactive fault-free replanning for C and a station 1 outage from 02:00 to 04:00 for F. The methods shared all conditions within each sample, starting point, and arm.

| Sample / starting point | Frozen initial score | C baseline | C improved | F baseline | F improved | Interaction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| H1 / A | 183.6 | 183.6 | 189.2 | 183.6 | 189.2 | 0.0 |
| H1 / B | 196.0 | 189.2 | 196.0 | 189.2 | 196.0 | 0.0 |
| H2 / A | 175.2 | 175.2 | 183.6 | 175.2 | 183.6 | 0.0 |
| H2 / B | 192.0 | 180.8 | 192.0 | 179.6 | 192.0 | +1.2 |

The fault gaps were 5.6, 6.8, 8.4, and 12.4 points. The fault-free gaps were 5.6, 6.8, 8.4, and 11.2 points. Each gap G is improved minus baseline. Interaction is the fault gap minus the fault-free gap. Signed differences were calculated first in integer points and then divided by 5. Shared C/F conditions and A/B starting points make these dependent comparisons. The report is limited to descriptive results for these cases. Statistical significance, general causal effects, and attributable fractions are outside its scope.

All 20 plans covered 58/60 targets overall and 58/58 executable targets and had zero violations. All 20 independent rule and history checks, 20 original CLI evaluations, and 20 per-second geometry reports using the original TLEs passed. The two negative cases, independent recomputation, protection checks, and manifest checks also passed. For C, the CLI and geometry checks consumed a projection with status set to success. An independent external verifier accepted the actual history separately. F used the actual events, frozen initial plans, and interruption evidence.

At the fault time, none of the four frozen initial plans had a station 1 task in progress, so this round included zero nonempty interrupted segments. The 20 new geometry reports covered successful tasks. Per-second checks include whole-second endpoints. Continuous-time and full optical equipment certification remain outside that scope.

## Native Fault-Free Guard and Historical Regressions

In round 8, baseline fault-free replanning for H1/B and H2/B lost 6.8 and 11.2 points, respectively, against the frozen initial plans. R9 through R11 introduced the native guard. It checks the original candidate pool and full initial history independently, accepting a candidate only when integer J improves strictly in lexicographic order. Lower values and ties retain the original. Illegal candidates return failure. The added entry point protects the primary score. Coverage may decrease, and legacy and fault paths use their own rules.

The native source uses an externally held manifest SHA. Evaluation directly checks real completed, locked, and new_success states. Recheck runs without solving or relying on old absolute paths. After resources are prepared, solve admission checks for 32 seconds. The 30 seconds inside the solve block include a 1-second save allowance, with 2 seconds of margin outside the block. Parent and child use the same host monotonic deadline. A timed-out solve remains failed. See the [native workflow guide](NO_FAULT_NATIVE.md).

The 280 R11 tests and the actual R12/R13 matrices are measured results of their historical snapshots. Before native functionality was merged, the parent snapshot and finalization checks after child-command completion were corrected to prevent a workflow PASS after crossing the parent deadline. The original PR contains the same-source historical regressions and synthetic workflow results. The current documentation PR's Actions run provides its own verification results.

## Aggregated Results and Scope for Rounds 12 and 13

R12 used 180 new targets disjoint from the historical set of 301, with a nested subset of 60. The two scales and A/B starting points shared data. Selected method gaps were 3.2 points for H60/A, 0 for H60/B, 35.2 for H180/A, and 0 for H180/B. The branches were 2 accepted, 2 retained for a lower value, and 4 retained on a tie. The budget use was 253.184 seconds.

R13 reused 60 targets and the same TLEs. The model days were 2026-08-05 and 2026-08-06 at t3600. Starting element ages were 0.56084577–2.19982376 days and 1.56084577–3.19982376 days, respectively. All were nonnegative. Historical publication, availability, and orbital ground-truth accuracy remain unverified. Selected method gaps were 5.2 points for D1/A, 0 for D1/B, 7.2 for D2/A, and 0 for D2/B. Branch counts were again 2/2/4. The budget use was 262.701 seconds. Date and element age changed together.

Each round's normal path included 8 native evaluations, 8 rechecks, and 0 solves. R12 migrated the actual package to a new path. R13 reused the frozen code. The original cross-day task negative case first triggered a frozen-history mismatch, confirming rejection of the combined mismatch. A later independent audit verified time binding with positive and negative controls that shifted only UTC. The original rejection reason stands.

The previous R11 failure took 8387.504 seconds and is recorded separately from the explicitly rerun 368.955 seconds. The R12 negative-case adapter failure took 0.782 seconds. R13 bootstrap and smoke took 0.578 and 3.625 seconds. Each is included in its own ledger. The 600-second limit applies to each round's controlled ledger separately.

## Summary of Rounds 14 Through 19

R14 changed only the future set of available stations. Both initial plans came from the three-station configuration and were shared byte for byte. Selected scores with ten stations increased by 21 to 85 integer points and covered four more targets. This measures resource sensitivity for the instance with shared starting plans. Ten-station initialization from scratch and general heuristic monotonicity are outside the test scope. The present file-closure review passed. The package lacks the original seal terminal record with exit code 0, and the last approximately 339.684 seconds of between-case wall time were previously omitted.

The R15 verifier compared the product enum retained_original with the CSV identifier retained, so four successful native t2 runs did not count as fully accepted nodes. R16 replayed the verifier but exceeded the preparation limit. Its limitations include overlapping accounting, repeated freeze execution, and editing the seal script while work was in progress. After control-layer revision, R17 completed eight nodes, all retaining on ties. The A/B strategy path differences remained 16 and 54 integer points. Per-stage completed growth was measured against the immediate parent, and cumulative growth against t1. The t3 primary scores for all four chains reached their respective loose upper bounds with fixed history.

R18 created two initial plans from empty histories using the same complete ten-station candidate pool. J was (914,60) and (1000,60). At t3600, completed task counts were 53 and 21. Of the four native runs, three retained on ties and one retained a higher original score, producing selected 1000 over raw 964. BASE initialization improved by 41 integer points over the old initial plan. Its subsequent path scored 44 or 60 integer points below its old reference. The direction depended on the stage. Six geometry reports covered 82080 whole-second samples, supporting agreement with the current TLE model.

The R18 frozen finalizer failed to create the parent directory for its control-code archive and exited with code 1, leaving sealing unstarted. R19 took the current unsealed evidence snapshot into read-only custody, reviewed it, packaged it, and completed actual sealing and independent reconstruction acceptance. New schedule runs, backend calls, and propagations totaled zero. R18 and R19 used 208.426582 and 169.646280 seconds, respectively, against separate 600-second limits. R19 certifies its new recovery package. R18's seal failure remains, and some evidence-collection development revisions lack individual archives.

## Round 20 Shared Input

R20 used 180 targets, 60 per tier, with H60 strictly nested. All nine raw file identities matched the earlier research. The model used all of 2026-08-05, ten stations, and the original geometry and candidate parameters. The historical H60 data lacked complete historical byte identities for dependencies and embedded time auxiliary data. All 1800 target-station pairs were generated from scratch, reusing zero windows. The R12 Aug03 windows were excluded. The H60 subset had 2173 windows and 39720 candidates. The other 120 targets had 4536 windows and 76503 candidates. All candidates passed deterministic byte-for-byte replay.

Both window endpoints are valid whole seconds and `end_s` is inclusive. All 20127 direct geometry samples passed. The 153 empty target-station pairs establish absence on the frozen grid and in the ranges actually refined. Summing each target's highest candidate score gives 3000 integer points. Joint feasibility and attainment of that total are unverified. The accounting total was 530.423 / 600 seconds. Preparation used 442.438, sealing 60, independent acceptance 7.985, and wrap-up 20. Parts of the 45-second preflight lacked a UTC position. The ledger measures scoped work. Formal production and sealing each ran once with raw exit code 0. Acceptance from a new path used an external bound Python environment on the same machine.

## Status of Rounds 21 Through 27

In R21, five of six cases started and only the two initial cases passed completely. Their J values were (2758,180) and (3000,180). Three native workflows timed out at later stages, and the fourth was budget-blocked, leaving native acceptance at 0/4. The recorded timeouts apply to workflows, and leftover unaccepted candidates were excluded from method-gain reporting. The backend evidence retains four completion receipts, five confirmed starts, two unknowns, and a start range of [5,7].

R22 and R23 both remain PARTIAL. R24, R25, R26-A, and R26-B remain BLOCKED. Their original failures, missing starting states, and incomplete protection are recorded separately. R27 first completed actual post and original accept from a new candidate path on the same machine, along with 18 negative cases and two audit layers. The original core bytes and full freeze matched. R27 performed zero additional solves, propagation, or formal seal/post operations. See [R27 executor qualification](R27_EXECUTOR_QUALIFICATION.md) for budget and evidence scope.

## Rounds 28 Through 34 Timing Fixes and the BASE Same-Start Pair

In R28, actual seal, post, and accept each ran once and returned code 0. Execution files were read before registration, leaving the overall round budget unverified and the status PARTIAL. R29 and R30 were again blocked by pre-registration reads. R31 completed the 30 qualification items for first-tool registration, two short commands, and waiting for cleanup. Actual exit codes were 0 and 7, with zero production operations. R32 preparation took 151.434 seconds, above an 80-second hard limit, and the native case never started. Wrap-up failed and the 702.082-second minimum record did not close the budget. R33-A was blocked by missing startup code or state. R33-B passed registration and entry-point SHA checks. The launcher and capture exited 1 due to write permissions, with a separate pre-registration read deviation. Verifiable production call counts are unavailable.

R33-C and R34 successfully ran baseline and improved, respectively, from H180_BASE. Each had one native run, one solve, exactly three backend starts and three completions, and zero exit codes for produce, evaluate, and recheck. The two rounds shared 8 source files, 100 product files, 279 frozen dependencies, and declared runtime identities. They used budgets of 30 seconds for the solver, 180 for the workflow, and 230 for the group, with decision time t3600 and the same retained plan. J increased from (2758,180) to (2806,180). Of 49 adjustments, eight extending tasks from 120 to 240 seconds contributed all 48 extra integer points. The other 41 contributed zero points. The case compares the methods on a single fixed instance. It does not establish a reduction in adjustments.

Each round made 360 propagation calls. Baseline had 39060 plan samples and 78120 two-path propagation samples. Improved had 40020 and 80040, respectively. The 960 extra plan samples equal eight extensions of 120 seconds. Protection records passed for 22624 files, 3 trees, and 3950 consumed originals in each round. The independent audit reviewed saved records and experiment copies. It did not rescan all historical originals or rerun solves or propagation.

The last saved sample was 173.1593674 seconds for R33-C and 235.8957645 for R34. External terminal handoff separately reported return coverage of 177.011 and 238.9717645 seconds, respectively, and a terminal sample of 235.9102733 seconds for R34. Those external values are absent from saved parent JSON fields. The last saved sample alone cannot establish final tool coverage. Each round's saved sample and reported external coverage stayed below its separate 600-second limit. These figures measure the individual recorded intervals, with method speed and end-to-end chat time outside that scope.

## Next Steps and Unverified Items

Cross-round H180 native acceptance stood at 2/4, with the two IMP-starting cases awaiting independent acceptance. The original R21 native status remains 0/4, with two unknown starts. R33-C and R34 had zero repeat seal/post/accept runs. Full evidence delivery and receipt and updates to the historical Demo and Word/PDF materials were still open. The original public update covered aggregate documentation. The research executor and new product APIs were outside its scope.

Algorithm verification to that point covered 60 targets from a single source, ten real stations, 24 hours and a bounded continuous state chain, and a single H180_BASE instance with two methods. The full H180 matrix, six days, and 10000 targets were not yet complete in this historical snapshot. New task arrivals, withdrawal or failure of resources, independent sources, and larger scales require separately frozen problems and budgets. Static-chain stability covers a different condition from dynamic adaptation. Full optical equipment, window search completeness, continuous-time feasibility, historical publication availability, different-machine or on-site receipt, and final official scoring remain unverified. The legacy extra evaluator remains [BLOCKED](optional_evaluator.md). Existing Demo and Word/PDF materials belong to their historical batches.

The repository publishes source, synthetic inputs, and aggregate facts. Real target identifiers, task tables, TLEs, full manifests and recovery packages, machine logs, and local prompts are kept locally. Reproducing the real-data experiments requires those local materials. See the [R19 recovery record](R19_RECOVERY_STATUS.md), [R20 input delivery](R20_INPUT_DELIVERY.md), [R27 executor qualification](R27_EXECUTOR_QUALIFICATION.md), and latest method pair [R33-C/R34](R33_R34_H180_BASE_PAIR.md).
