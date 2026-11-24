# Short Messages for the User to Forward (Unsent)

## To Team Member 1

The standard window intake tool is ready. Please deliver `targets.csv`, `stations.csv`, `windows.csv`, and `metadata.json` and record the source, version, and filtering checklist. The tool reads the data and generates configuration without changing the original files. Please specify which nighttime, target illumination, Sun and Moon avoidance, weather, field of view, tracking, terrain, and station-availability conditions the windows include, along with any differences in IDs, UTC precision, or scoring. The actual intake inspection is pending because a delivery with identified provenance has yet to arrive. See `docs/TEAM1_DATA_INTAKE.md`.

## To Team Member 3

The source integration package is based on stable algorithm candidate `b0eb3b5`. See the package manifest and the adjacent checksum for the exact source commit and SHA-256. After extracting it, run `python -X utf8 scripts/team3_run.py synthetic --out outputs/check_01` with your Python 3.11 interpreter. It runs planning, independent evaluation, and a read-only recheck in order. Use a new directory every time. Inspect real windows before running windows mode and prefer baseline for formal integration. In `docs/templates/TEAM3_RECEIPT.md`, record your command, exit code 0, 2, or 3, and results, then confirm the outcome yourself. Our local verification is separate from your confirmation.

## To Team Member 4

Open `demo/index.html` in the local demo package for offline playback. It includes three screenshots, the script, and separate E3/E4 and E5 tables. The old E4 page compares whole workflows with different initial plans and shows a gain of 11.6 points. E5 uses a common fixed initial plan and changes the score from 172.4 to 182.0, a gain of 9.6 points. Coverage is equal, all history is preserved, and the historical per-second TLE validation found zero violations. Net adjustments rose from 5 to 23. Please describe the score as a smoke-test task score for a fixed scenario. Official percentage scores and full optical validation are outside that scope. This round delivered stable integration and recorded no new algorithm gain.
