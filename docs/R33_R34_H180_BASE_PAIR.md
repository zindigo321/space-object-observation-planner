# R33-C and R34 H180_BASE native comparison from a common starting plan

Updated 2026-11-02.

R33-C's `R33_H180_BASE_BASELINE_PASS` and R34's `R34_H180_BASE_IMPROVED_PASS` support a specific result. With the same H180_BASE starting plan, `t=3600`, and frozen candidate pool, baseline selected `J=(2758,180)` and improved selected `J=(2806,180)`. The integer primary score rose by 48, or 9.6 task points under this task's one-fifth conversion. Both plans covered 180 targets.

The read-only review passed all 354 paired-audit checks under the preregistered protocol and all 499 R34 result-audit checks. The review used saved evidence and performed zero native runs, solver runs, or new orbit propagation. The two execution passes cover a subset of the native matrix. Formal sealing and acceptance remain pending.

## Pairing identity and execution scope

Both runs executed product version `1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5`, corresponding to the full, file-by-file verified 100-file product tree. This page was added on top of remote documentation baseline `ab5fdd73315242353beb0bc31290379208fe5a8a`. The product commit identifies the executed version.

| Pairing condition | Verification result |
| --- | --- |
| Source data | Same H180_BASE and byte-identical eight-file source. 180 targets, 10 stations, 6,709 windows, and 116,223 candidates. |
| Starting plan and decision time | Same initial plan, shared retained plan, and `t=3600`. Both runs reused the starting plan, windows, and candidates. |
| Product and control baseline | Same 100-file product tree, frozen set of 279 original control files, and shared execution components. |
| Runtime identity | Same interpreter and declared runtime mapping of 3,935 files. This establishes the environment identity for the paired runs only. |
| Budget configuration | Each group had 30 seconds for the solver, 180 seconds for the workflow, and 230 seconds for the group. Each round had a separate 600-second accounting limit. |
| Method | The planned method parameter differed between baseline and improved. Each round recorded its own identifiers, output labels, and capture format. |

The pair compares one fixed instance across two rounds. Round identifiers and the outer recording format differ, so the byte-identity finding applies to the shared inputs and product tree.

Each round had one confirmed native launch and one solver entry. The produce, evaluate, and recheck backend stages each completed once, with exit code 0 for all three. Data, selection branch, and execution-time geometry checks passed. The saved records support successful parent process exit and Job cleanup.

## Objective and breakdown of adjustments

Here `J=(integer primary score, covered target count)`. Task points equal the integer primary score divided by 5.

| Method | retained J | raw J | selected J | Branch | Targets with net adjustments |
| --- | --- | --- | --- | --- | ---: |
| R33-C baseline | (2758,180) | (2758,180) | (2758,180) | KEEP_RETAINED_TIE | 0 |
| R34 improved | (2758,180) | (2806,180) | (2806,180) | ACCEPT_CANDIDATE_STRICTLY_BETTER | 49 |

The independent calculation rebuilt scores from source priorities and task durations. It confirmed a selected-plan gain of `+48` integer primary points, or `+9.6` task points under the current scale, with zero change in coverage. The baseline selected plan is byte-identical to retained. The improved selected plan is byte-identical to raw.

Of the 49 net target adjustments in improved, eight upgraded tasks from 120 to 240 seconds and contributed the full score gain. The other 41 kept the same score. Both duration decreases and score decreases totaled zero.

| Priority | Targets upgraded in duration | Integer primary score gain |
| --- | ---: | ---: |
| High | 1 | +10 |
| Medium | 5 | +30 |
| Low | 2 | +8 |
| Total | 8 | +48 |

The following mutually exclusive groups break down the 49 adjusted targets by physical field changes. Another 131 targets kept all these fields.

| Changed fields | Targets |
| --- | ---: |
| Station, start, end, duration | 6 |
| Station, start, end | 26 |
| Start, end | 13 |
| Start, end, duration | 2 |
| Station only | 2 |
| Total | 49 |

In total, 34 targets changed station, 47 changed start time, 47 changed end time, and eight each changed duration and score. These field counts overlap. Eight of the 49 adjusted targets gained points, and baseline made zero adjustments.

## Conditional upper bound and geometry

At the decision time, 114 targets were complete and four were locked. Both runs kept them, contributing `1666+70=1736` fixed integer points. For the remaining 62 targets, taking the highest available score per target in the frozen discrete candidate pool gives a relaxed total of 1070. Relaxing mutual-exclusion constraints between these targets gives the conditional upper bound `1736+1070=2806` for the integer primary score. The feasible improved plan attained it.

This result applies to the fixed history, model, and frozen discrete candidate pool. The bound covers the paired replanning problem and its generated discrete candidates. The full-day initial problem, continuous time, candidates outside the pool, and general algorithm optimality fall outside that scope. The initial score of 3000 for the separate H180_IMP starting plan also falls outside this pair.

| Geometry check count | baseline | improved |
| --- | ---: | ---: |
| Propagation calls | 360 | 360 |
| Scheduled-time samples | 39,060 | 40,020 |
| Combined samples across both propagation paths | 78,120 | 80,040 |

The scheduled-time count includes both endpoints of each task's integer-second interval, giving `sum(duration+1)`. Adding 120 seconds to each of eight tasks raised total duration from 38,880 to 39,840 seconds, adding exactly 960 scheduled-time samples and 1,920 samples across the two propagation paths. The counts are per task and per propagation path, so they can include shared time points and do not represent independent random samples.

Execution-time checks established agreement across both paths under the orbit model used. The read-only review analyzed the saved results and performed zero new reference orbit propagation. Real-world orbital accuracy, refraction, full optical constraints, window completeness, continuous time, and on-site observation certification remain outside the validated scope.

## Time accounting, final return, and protection scope

| Accounted checkpoint (seconds) | R33-C | R34 |
| --- | ---: | ---: |
| Pre-registration time included in W | 8.576 | 13.817 |
| Saved LEDGER sample | 163.3274467 | 227.7067175 |
| Saved parent sample | 163.741209 | 228.5667594 |
| Saved tool sample | 173.1593674 | 235.8957645 |
| Coverage through the actual final tool return reported by the external handoff | 177.011 | 238.9717645 |

W includes initial module loading and synchronization waits. R33-C recorded 5.303 seconds for module loading. The saved continuous timing ledgers support recalculation through each saved sample. R34 separately has an external terminal sample of 235.9102733 seconds.

The final row comes from the execution terminal handoff. Both final captures exited with code 0. The evidence for final tool return comes from that external handoff, while the saved parent and tool JSON report their own samples. The limited passes depend on both the saved ledgers and final-return evidence. The 600-second limit applied to each round individually. The combined rounds, development time, and overall conversation wall time use different accounting boundaries.

Saved execution-time protection results were PASS in both rounds, with 22,624 historical files, three historical trees, and 3,950 consumed originals verified. This audit fully reviewed the saved protection records and their anchors and recalculated hashes for source data, product files, and frozen files in experimental copies. The read-only review used these records and copies. A new scan of all historical originals, consumed originals, 3,935 runtime library originals, and historical trees fell outside its scope.

## Coverage and public evidence

The additional H180 native matrix entries accounted for across rounds total **2/4**. Both H180_BASE methods passed. The two H180_IMP groups are still pending. The original R21 remains PARTIAL, and its historical count uncertainty still applies. The R33 A/B attempts remain BLOCKED.

R33-C and R34 performed zero seal, post, or accept operations. R28 remains PARTIAL. This page summarizes the completed pair. The full matrix, formal migration acceptance, and final delivery remain pending. The scope is one fixed case and supports conclusions about that pair only. Statistical significance, independent random repeats, general algorithm superiority, and fault recovery gains remain outside the evidence.

The following SHA-256 digests identify the private evidence entry points for the audited version. Public disclosure is limited to the digests and this summary. The original evidence, local paths, real target identifiers, orbital elements, full manifests, and raw logs are held privately.

| Evidence entry point | SHA-256 |
| --- | --- |
| Preregistered pairing protocol | `10adddc65d359517a80b89e06513e9d85d14d0a9d19daac4ad24eb9e59142549` |
| Product identity record shared by both groups | `a174f6dc48129440eb1c1f7fe0f9ab8a0481cd8b5f2b53ad73a78f54ad5e6978` |
| R33-C FINAL_TOOL_OBSERVATION | `909ca98544a09699c0ea7d2da081b708ce0b3fc712d388b577de98c2898916fc` |
| R34 FINAL_TOOL_OBSERVATION | `b99eaeaacd997e72ee53a731f4fe345adffbccec81c40f0a23a8769de3bb6bd4` |

For the original scope, see [no-fault native verification](NO_FAULT_NATIVE.md), [executor qualification](R27_EXECUTOR_QUALIFICATION.md), and [experiment records](../EXPERIMENTS.md). The [contribution guide](../CONTRIBUTING.md) covers publication and review.
