# R27 Executor Qualification Status

Updated 2026-11-01.

R27 reached **R27_EXECUTOR_QUALIFICATION_PASS**. On the same machine, the recovered candidate ran through the parent Job, copied post, FileAudit, unified launcher, and original v2 accept in that order. The qualification post and original accept each ran once, and both returned raw exit code 0.

**Formal seal and formal post each had a count of 0 and exit code null.** Formal sealing and migration still require independent execution and acceptance. This public update reports the aggregate evidence. The research executor and its product API integration are outside this update.

## Qualification and Protection Evidence

| Item | R27 measured result and scope |
| --- | --- |
| Qualification post / original accept | One run each, raw exit code 0 |
| Negative cases using built-in copies | 18/18 passed |
| Old-root read probe | Denied as expected, 0 bytes read |
| Two layers of application auditing | Inner recorded one expected read denial. Outer recorded zero unexpected denials |
| Core original bytes / candidate ZIP | 37 regular members, 38 ZIP entries with the root manifest |
| Execution-file freeze | 11 matching identities |
| Historical originals / trees / consumed originals | 22624 / 3 / 41, all passed |
| Parent supervision | Raw exit code 0, zero active Job members, and closed output and process/Job handles |
| Formal seal / formal post | 0 / 0, never started |
| New solves / production schedule or backend calls / propagation | All 0 |

The final receipt directly binds 29 key files. The parent observation adds 16 late evidence items and six entry-point identities. Repeated payloads are covered through their exact manifests. Certification is limited to that scope. The original RESULT retained its pending final-readback state. The final PASS is supported jointly by the outer readback, the actual parent exit, and the last parent observation.

## Historical Statuses

| Round | Status and explanation |
| --- | --- |
| R21 | PARTIAL. Five of six cases started and two passed. Native runs were 0/4, so the matrix remained incomplete |
| R22, R23 | PARTIAL. The recovery and readback revisions did not reach complete acceptance in those rounds |
| R24, R25 | BLOCKED. Only partial supervision or read checks were completed |
| R26-A | BLOCKED. Reading preceded registration, leaving the starting state unresolved |
| R26-B | BLOCKED. All 12 partial Job checks passed. Full qualification remained unstarted and protection was incomplete at expiry |
| R27 | Full executor qualification PASS for R27 |

The two R21 initial objectives J were (2758,180) and (3000,180). They remain R21 results. The R21 backend start counts remain five confirmed and two unknown, for a range of [5,7]. Four completion receipts establish four completions. R18 remains PARTIAL, and the previously reported R19 recovery and R20 input delivery statuses still apply.

## Timing Scope

Preparation completed at 100.925 seconds, qualification at 176.992 seconds, the parent protection report at 232.279 seconds, and the parent finalization report at 253.919 seconds. The last saved parent sample was 423.5412529 seconds, reproducible from the same run's QPC data. The stage thresholds passed.

The execution handoff also reported a final sample of 423.59 seconds and conservative coverage of 428.72 seconds including the final tool return, below 600 seconds. The delivery directory lacks the independent final tool-return receipts for those exact values, so they are attributed to the execution handoff. The charge covers the declared tooling and executor interval. End-to-end chat time and cumulative development costs fall outside that measure.

## Reuse and Publication Scope

A later round can reuse the qualified post, accept, and Job bytes and perform formal sealing and migration to a new path separately. New late evidence belongs in a declared outer package or sidecar with its own binding. The original manifest applies to its exact 37-member tree.

The runtime environment was bound on the same machine and kept outside the package. Read checks for 3935 declared runtime paths cover those paths. Full environment equivalence and generic security isolation are outside that scope. R27 generated zero additional algorithm scores, completed tasks, or method gains. It established no new orbital or geometric ground truth.

The public repository carries this page and other aggregate documentation. Real targets, task tables, TLEs, full manifests, ZIPs, audit logs, research tools, machine paths, and local prompts stay local. The SHA256 digest of the audited local parent-observation entry point is

`de09d4263a1b4d3e53c1fdade3fb31e303074bcd504108158d82304e1ec264a7`

Use this digest to verify the identity of the local evidence. Publication scope follows the [contribution guidelines](../CONTRIBUTING.md).
