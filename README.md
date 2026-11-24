# Space Object Observation Planner

The planner builds and revises observation schedules from ground stations, space objects, and visibility windows. Synthetic inputs let you run scheduling, independent evaluation, and read-only checks locally.

## Quick Start

Use Windows x64, 64-bit CPython 3.11, Git, and PowerShell. Run `python --version` to confirm the active interpreter.

```powershell
git clone https://github.com/zindigo321/space-object-observation-planner.git
if ($LASTEXITCODE -ne 0) { throw 'Repository clone failed' }
Set-Location space-object-observation-planner -ErrorAction Stop
python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed' }

$py = (Resolve-Path '.venv/Scripts/python.exe').Path
& $py -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw 'Development dependency installation failed' }

$out = 'outputs/synthetic_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
& $py -X utf8 scripts/team3_run.py synthetic --out $out
if ($LASTEXITCODE -ne 0) { throw 'Synthetic workflow failed. Check the console and output directory.' }
```

On success, `$out/workflow.json` reports `status: PASS` and `exit_code: 0`. The same output directory contains the schedule, evaluation, and recheck results. Use a fresh directory for each run. See the [contributing guide](CONTRIBUTING.md#local-verification) for the full test commands.

## Release Package and Acceptance

The project team distributes the frozen S02 and H180 cases in `FAMOU_TEST_PACKAGE.zip`. From the extracted directory for the corresponding release, follow the [release runbook](famou/RUNBOOK.md) to install dependencies offline and run planning, evaluation, and rechecks.

S02 completed formal local acceptance on Windows x64 at commit `6aacb4a64d5b32d388c7ecbcad7ae361bb31b29d`. Acceptance on Baidu FAMOU is pending. The package contains `SOURCE_IDENTITY.json`, and the accompanying `FINAL_ACCEPTANCE.json` records scores, timing, and the ZIP hash.

## Repository Layout

| Path | Contents |
| --- | --- |
| `planner/` | Scheduling, replanning, input validation, and independent evaluation |
| `scripts/` | Workflow, input inspection, packaging, and acceptance entry points |
| `configs/`, `examples/synthetic/` | Configuration and public synthetic examples |
| `tests/` | Automated regression tests |
| `famou/` | Release runbook, platform guide, locked dependencies, and native components |
| `demo/` | [Offline demo](demo/README.md) template and synthetic example instructions |
| `docs/`, `research/` | Interface documentation, acceptance records, and research tools |

Find the current status, integration contracts, and experiment history in the [documentation index](https://github.com/zindigo321/space-object-observation-planner/tree/main/docs#readme). Read the [contributing guide](CONTRIBUTING.md) before submitting changes.
