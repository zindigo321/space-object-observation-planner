# R19 Recovery Delivery Status

Updated 2026-10-29.

R19 completed read-only recovery of existing R18 evidence, sealing of the recovered package, and independent acceptance from a new path. All four checks returned PASS. **The original R18 results remain data PASS, sealing FAIL, sealed execution-version acceptance BLOCKED, and round status PARTIAL.** The recovery package applies to the evidence collected in R19.

## Recovery Scope and Counts

| Item | R19 result |
| --- | --- |
| Evidence recovery / new package sealing / recovered execution version / independent migration | All PASS |
| New schedule / native backend / TLE propagation | 0 / 0 / 0 |
| Historical initial / native runs reviewed | 2 / 4 |
| Historical schedule / backend evidence | 6 / 12 |
| Primary external checks / geometry reports / whole-second samples | 12 / 6 / 82080 |
| Initial byte proofs / history contexts / historical geometry bindings / negative cases | 2 / 6 / 6 / 2 |
| Successful formal recovery packages / formal failures | 1 / 0 |

Historical files were taken into custody as a newly observed snapshot, with their original bytes preserved. The snapshot represents the evidence available during R19 recovery. One evidence-collection preparation failure and the expected failures in the qualification fixtures were recorded separately from the formal success count. Formal qualification, sealing, and migration used the same 10 frozen recovery tools. Some development revisions were not individually archived.

## Interpreting the Data Results

The two R18 ten-station initial plans with empty histories yielded integer objectives J of (914,60) and (1000,60). At t=3600, their cumulative completions were 53 tasks for 794 integer points and 21 tasks for 250 integer points, respectively. Three of the four native replans retained the original on a tie. The fourth retained 1000 over a lower candidate of 964.

Compared with the previous three-station plans, the two initial plans gained 41 and 75 integer points respectively and covered four additional targets each. The subsequent BASE selections scored 44 and 60 integer points below the old initialization path, so the results describe these specific paths. J includes future tasks. The completed count accumulates under the model's assumption of fault-free execution. Comparisons across different initial histories measure differences between paths.

## Delivery Evidence and Budget

The content manifest binds deduplicated blobs to logical paths. The terminal receipt was produced after the actual seal exited with code 0. The second new path was rebuilt solely from package contents and accepted in isolated Python mode with file-access auditing. The old-root read probe was denied and the missing-file negative case failed as expected. Verification covered a new path on the same machine.

The rounds were accounted for separately. R18 used 208.426582 / 600 seconds. R19 used 169.646280 / 600 seconds, including failed attempts, 60 seconds for formal sealing, and a conservative allowance for wrap-up. These are accounting totals for the individual rounds. End-to-end wall time was outside that measure.

This update covers documentation. The product uses the API and algorithm from the 98-file version associated with `83d3014`. Recovery tooling is outside CI. The historical test results apply to their original runs.

All real data, CSVs, ZIPs, machine logs, environment paths, and local prompts are kept locally under the [contribution guidelines](../CONTRIBUTING.md). The logical entry point to the recovery package is `RELEASE.json`. Its content package SHA256 is `03060189ebf342eb7626a6690875f01270609ca53d5f4c14b28d2b8f38a05378` for local verification.

Six-day runs, 10000 targets, complete optical equipment, and official scoring remain unverified. The limitations of the R14 sealing evidence and the R15 PARTIAL and R16 BLOCKED statuses still apply.
