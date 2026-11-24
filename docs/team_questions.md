# Open Questions for Team Members 1 and 3

As of 2026-10-27, the user took over the roles of team members 1, 3, and 4 on the same machine. AI assisted with local experiments and independent audits through round 13. The user coordinates follow-up materials, rules, and receiving environments. The evidence covers this machine and does not establish acceptance by another team member, machine, or onsite device. See the [current status](CURRENT_STATUS.md) for the latest summary.

The historical snapshot before the takeover recorded Team 1 delivery as **PENDING_INPUT/NOT_RUN** and Team 3 confirmation as **PENDING_EXTERNAL**. At that time, `data/raw` and `data/processed` were empty, and the designated handoff locations contained no Team 1 data with recorded provenance. Those statuses describe the earlier assignment, and the old workflow fields preserve that snapshot. Official reference data and synthetic fixtures have their own provenance.

## Completed Work and Tools

The E3 multi-seed runs, E4 late fault, offline demo, E5 comparison with a common initial plan, and atomic write fix were completed. See `EXPERIMENTS.md`, `PROGRESS.md`, and the corresponding handoff documents. These results supersede the old plan to do E3/E4 and the demo in a later round. Historical integration tools include the [stable kit](STABLE_HANDOFF.md), [Team 3 integration](TEAM3_INTEGRATION.md), and [Team 1 read-only intake](TEAM1_DATA_INTAKE.md). Rounds 4–13 were completed separately. Local evidence covers native no-fault regression protection, limited scaling from a common source, and sensitivity across days. The next ten-station comparison remained planned. Receiving environments and formal materials still required separate acceptance. See the current status and the [native interface](NO_FAULT_NATIVE.md). The following legacy and fault integration questions remain open.

## Data Production (Formerly Team Member 1)

1. Provide the sender, timestamp, directory, version, and provenance record in the [intake checklist](templates/TEAM1_DELIVERY.md). Will the delivery use the existing three CSV files and metadata JSON?
2. Are IDs positive decimal integers, and is Alpha-5 or another mapping required? Confirm any differences in UTC precision, horizon, stations, or priorities. Agree on adapters for different precision or time zones before converting anything.
3. For elevation, nighttime, target illumination, Sun and Moon avoidance, weather, field of view, tracking speed, terrain, and station availability, specify whether the windows include each condition. For any excluded condition, identify who provides it and document its fields and units.
4. Confirm that geometric windows include their endpoints, resource occupancy uses half-open intervals, and windows shorter than 120 seconds are retained without producing candidates. Confirm that overlapping windows do not imply parallel station capacity.

## Integration and Evaluation (Formerly Team Member 3)

1. Run the synthetic and standard window flows from the source package. Confirm Python 3.11, the standard task CSV, independent evaluation and recheck, exit codes 0, 2, and 3, and upstream integration. Record the machine, version, inputs, commands, and artifacts in the [receipt template](templates/TEAM3_RECEIPT.md).
2. Does the evaluator independently retain the authoritative targets, windows, and original initial plan? The evaluator must derive completed, locked, and interrupted cases from the fault and initial plan.
3. Use baseline first for formal integration. The existing improved method is available through `both`. Use the actual receipt to identify any need for a different data transport or field interface.

## Team Rules Pending Confirmation

Each target may succeed once across all stations. The 120- and 240-second durations earn 60% and 100%, and high, medium, and low priority maximum scores are 5, 3, and 2. Switching targets takes 30 seconds. Interrupted tasks score zero and may be retried. Geometric windows are closed and resource occupancy is half-open. These are smoke-test assumptions pending formal confirmation. The two official scoring definitions have yet to be reconciled. The legacy optional evaluator remains `BLOCKED`. Existing evidence covers 60- and 180-target samples from the same source and cross-day sensitivity on the same 60 targets. The full ten-station, six-day, 10,000-target scenario, independent sources, full optical equipment, real-data transfer and operation on another machine, and official scoring remain unverified. Local runs in the existing environment and acceptance in a new receiving environment are separate. See the corresponding Actions run for cloud installation of the synthetic example.
