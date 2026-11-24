# Team 1 Standard Window Intake and Read-Only Inspection

No Team 1 data with a clear delivery note or provenance record has been found. Inspection of actual Team 1 data is **PENDING_INPUT / NOT_RUN**. The synthetic examples and official frozen reference windows validate the tools. Team 1 delivery requires its own provenance and confirmation. A directory name, official ZIP, or source label alone cannot establish delivery.

## What to Deliver

Provide four UTF-8 files in one directory. CSV files may have a UTF-8 BOM. JSON is read as UTF-8. Complete the [intake checklist](templates/TEAM1_DELIVERY.md) with the sender, time, version, source, filters, and any differences in rules. The [metadata template](templates/team1_metadata.template.json) shows the fields. Replace the placeholders with actual metadata.

| File | Required fields and constraints |
| --- | --- |
| `targets.csv` | `target_id` is unique and a positive decimal integer. `priority` is `high`, `medium`, or `low`, corresponding to `full_score` values 5, 3, and 2. |
| `stations.csv` | `station_id` is unique and a positive decimal integer. The configured stations must exist. |
| `windows.csv` | `window_id` is unique. `target_id` and `station_id` reference existing rows. `start_utc` and `end_utc` are integer-second UTC timestamps within the metadata range. The start precedes the end. |
| `metadata.json` | `schema_version=1`, `time_precision_s=1`, a nonempty `data_version`, `horizon_start_utc`, `horizon_end_utc`, and a `filters_applied` list of strings. |

UTC uses `YYYY-MM-DDTHH:MM:SSZ`. The tool rejects local time, offsets, and fractional seconds instead of converting them silently. Report any adaptation needed for Alpha-5, other ID mappings, or differences in table structure, precision, or priorities. The [I/O contract](io_contract.md) gives the full specification.

## Inspect Received Data

Run from the root of the source package with your active Python 3.11 interpreter. The tool reads the data and writes reports to a new, separate directory. The default budget is 30 seconds and the maximum is 300 seconds. It guards the full child process tree. Inspection stops before scheduling, plotting, or orbit propagation.

```powershell
$py='python'
& $py -X utf8 scripts/inspect_team1_input.py --input-dir '../Received Windows' --source-label 'Replace with actual sender, time, and version' --out 'outputs/intake 01'
if ($LASTEXITCODE -ne 0) { throw 'Resolve the intake report errors before planning' }
```

On success, read `inspection.json` and `prepared_windows.yaml`. The report lists file SHA-256 hashes and byte counts, decoding results, target, station, and window counts, counts by priority, the UTC range, minimum, median, and maximum durations, counts below 120 seconds and long enough for 120 or 240 seconds, declared filters, and the full directory trees before and after inspection for the input integrity check. Validation uses the original `load_tables` and integer and UTC parsers. For valid data, it checks every row of all four files. An error report records the first failure and any uncompleted scope. A timeout reports `BLOCKED/NOT_COMPLETED` and leaves full validation incomplete.

The configuration defaults to the full metadata horizon and all stations in the table. `input_dir` points to the actual input for this run, and the cache is separate. To plan a specific subset, set the stations and time range explicitly.

```powershell
# Stations 7/9 and 06:10–06:30 apply only to the repository's synthetic example.
# Set these values to match your actual data.
& $py -X utf8 scripts/inspect_team1_input.py --input-dir 'examples/synthetic' --source-label 'Synthetic subset validation' --station-ids 9 --start-utc '2026-08-03T06:10:00Z' --end-utc '2026-08-03T06:30:00Z' --out 'outputs/subset intake 01'
```

Even with an explicit subset, the tool first validates all four original files. The report distinguishes full-data statistics from `planning_selection`. It clips windows only for an explicitly selected planning slice and preserves the original files. After a manual review of the prepared configuration, run the [Team 3 window workflow](TEAM3_INTEGRATION.md). If the data moves, inspect it again or pass the new `--input-dir`. Window mode does not resample targets by seed.

## Results and Scope

Exit 0 means the input contract and selected configuration passed. Exit 2 means invalid data or paths. Exit 3 means missing files or a budget or runtime blocker. Nested output under input, an existing output, or writes into a sealed directory are rejected before creating an empty output directory. Use a fresh report directory each time.

A valid window shorter than 120 seconds is retained. A window long enough for a task only establishes that the geometric interval fits the duration. Resource conflicts can still prevent scheduling, and overlapping windows do not give a station parallel capacity. Successful intake confirms the data contract. The report records `filters_applied` as the provider's declaration and states that the physical conditions were not independently verified.

The current smoke-test assumptions await confirmation. Each target can succeed at most once across all stations. A 120- or 240-second task earns 60% or 100%, respectively. The maximum scores for high, medium, and low priority are 5, 3, and 2. Changeovers between targets require 30 seconds. An interruption earns zero points and can be followed by another attempt. Geometric windows include endpoints, and resource occupancy is half-open. The two formal scoring systems have yet to be reconciled.

Confirm individually whether the windows include elevation, nighttime, target illumination, Sun and Moon avoidance, weather, field of view, tracking speed, terrain, and station availability. Identify the fields, units, and owners for excluded conditions. Team 2 needs those explicit declarations.

This inspection covered the project's `data/raw`, `data/processed`, the designated handoff directories, and known project material. Source files and prior outputs were treated as read-only. The missing Team 1 data blocks actual intake inspection. The tool, templates, and reference verification remain deliverable.
