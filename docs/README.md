# Documentation Index

Start with the synthetic example on the [project homepage](../README.md). This index covers runbooks, interface contracts, and historical records in the GitHub source repository.

## Running and Acceptance

| Document | Contents |
| --- | --- |
| [Release runbook](../famou/RUNBOOK.md) | S02 cold input generation, initial planning, no-fault replanning, independent evaluation, rechecks, and H180 entry points |
| [Deployment, upload, and restoration](../famou/PLATFORM_GUIDE.md) | Windows requirements and Baidu FAMOU upload and restoration |
| [Current status](CURRENT_STATUS.md) | Acceptance scope and pending checks for S02 and H180 |
| [H180 delivery record](FAMOU_DELIVERY_STATUS.md) | Formal H180 acceptance scope and delivery evidence |
| [S02 native component build](../famou/native/BUILD.md) | Compilation, ABI, and source identity verification |

## Interfaces and Contributing

- The [standard window interface v1](io_contract.md) describes fields and validation rules for windows, tasks, fault events, and evaluation results.
- The [data delivery and intake inspection guide](TEAM1_DATA_INTAKE.md) is for data providers. The [integration guide](TEAM3_INTEGRATION.md) is for data consumers. Use the [delivery checklist](templates/TEAM1_DELIVERY.md) and [integration receipt](templates/TEAM3_RECEIPT.md) as applicable.
- The [contributing guide](../CONTRIBUTING.md) covers local checks, what to commit, and the pull request process.

## Demos and Research Records

- The [offline demo](../demo/README.md) generates HTML from synthetic data. The [demo script](DEMO_SCRIPT.md) and [historical demo handoff](IMPROVEMENT_DEMO_HANDOFF.md) cover the E3/E4 demo.
- The [progress log](../PROGRESS.md) tracks delivery by phase. The [experiment log](../EXPERIMENTS.md) records the scope, comparison results, and limitations of each round.
- The [stable handoff](STABLE_HANDOFF.md), [R19 evidence recovery](R19_RECOVERY_STATUS.md), [R20 common input](R20_INPUT_DELIVERY.md), [R27 executor qualification](R27_EXECUTOR_QUALIFICATION.md), and [R33–R34 same-start comparison](R33_R34_H180_BASE_PAIR.md) record the corresponding versions.
- The [research tools](../research/README.txt) document inputs, environment, and entry points for the expansion batches.
