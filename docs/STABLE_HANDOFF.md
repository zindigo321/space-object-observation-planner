# Stable Release Handoff

This round added integration and read-only intake tools on top of algorithm candidate `b0eb3b5`. The scheduling, scoring, candidate generation, independent validation, and safe-write core remained outside scope. The branch was `work/stable-handoff-intake`. The full source commit for the final source kit is recorded in `MANIFEST.json → source_commit` to avoid a circular reference to this document's own commit.

## Using the Two Kits

| Kit | Audience and purpose | Data boundary |
| --- | --- | --- |
| `source_kit.zip` | Member 3 integration and member 1 intake. Provides runtime code, tests, configuration, dependencies, a synthetic example, templates, and instructions. | Exported only from controlled, allowlisted files in the specified Git commit. Excludes `.git`, original real data, old outputs, real tasks and windows, real HTML and screenshots, the full environment snapshot, prompts, and untracked files. |
| `local_demo_reference_kit.zip` | Local handoff to members 3 and 4 by the user. Provides the offline demo, three screenshots, E3/E4 and E5 tables, a talk script, and official reference windows. | Contains real identifiers and lives only in a local ignored output directory. Excluded from Git, cloud uploads, and Releases. |

Each kit contains `MANIFEST.json` with file purposes, sources, byte counts, SHA256 hashes, creation time, the algorithm candidate and source commits, and dependency versions. The manifest explicitly excludes its own hash. A separate `.zip.sha256` alongside each ZIP verifies the archive itself. Source files are read from Git objects, file by file, so the export corresponds exactly to the commit. Dates of older experiments referenced by the local kit remain their actual dates.

The source allowlist explicitly includes `.github/pull_request_template.md` and `.github/workflows/ci.yml`. An unknown tracked file still causes packaging to fail. Packaging regression tests create a temporary Git repository and a synthetic historical source. Tests run from the extracted kit without a bundled `.git` directory or real historical data, using the Git command installed on the local machine. The new kit after the fix still needs to be exported from the final local commit and its results recorded in the separate acceptance receipts. The older paths and observations below refer to the historical handoff.

```powershell
# Verify the downloaded or transferred archive in PowerShell.
Get-FileHash -Algorithm SHA256 .\source_kit.zip
Get-Content .\source_kit.zip.sha256
Expand-Archive -LiteralPath .\source_kit.zip -DestinationPath '.\source kit intake'
Expand-Archive -LiteralPath .\local_demo_reference_kit.zip -DestinationPath '.\local_demo_reference_kit'
```

The final kits and acceptance artifacts are on the local machine at `G:\bd-fmb\outputs\stable_handoff_20261023_190522`. `packages/packages.json` gives the archive paths, sizes, external hashes, and exact versions. `acceptance.json`, `portable_validation.json`, `pytest.xml`, and `browser_from_kit/browser_checks.json` are post-commit acceptance evidence for the final kits. Review the external receipts along with the kits when releasing them. The receipts establish whether the ZIPs passed.

## Getting Started

Member 3 should run the one-command synthetic workflow in the [integration instructions](TEAM3_INTEGRATION.md) and then try the real-window interface with `reference_windows` from the local reference kit. Member 1 should use the [intake instructions](TEAM1_DATA_INTAKE.md) to prepare the four files and a provenance list. Member 3 should fill in the [integration receipt](templates/TEAM3_RECEIPT.md) after running the workflow personally. Messages for members 1, 3, and 4 are in the [forwarding drafts](FORWARD_DRAFTS.md). No messages were sent during this round.

The local synthetic baseline was run in this round. It scored 10.0 initially with 3/3 coverage and 3.0 after the fault with 1/3 coverage. Independent initial and fault evaluations and the read-only recheck all found zero violations, and the complete result tree was preserved. The read-only tool loaded both the four synthetic files and the four official frozen reference files. The official reference contained 60 targets, 3 stations, and 563 windows. Of those windows, 9 were shorter than 120 seconds, 554 could fit 120 seconds, and 502 could fit 240 seconds. This checks the supplied window constraints. Physical certification of the declared filters is a separate matter.

The final results for source kit relocation, real reference-window integration, full test counts, browser checks of the extracted demo, protection snapshots, and the single budget come from this round's machine-generated receipts outside the kits. These receipts are generated after the source commit, so pending results do not appear in that commit. The delivery reply lists the actual results and failures. Any subsequent fix that produces a new source commit requires a matching export of the final kits.

## Historical Result Sources

The main source was `outputs/atomic_write_fix_20261023_182047`. This round first verified its seal manifest, agreement between scores and reports, demo hash, and browser records. See `source_verification.json`. The authoritative initial plan for E5 remains `outputs/improvement_demo_20261023_150452/experiments/E4_seed42_late`. The sealed JSON and original machine paths were used as recorded.

Historical E5 used a shared initial plan and reported 14 completed, 1 locked, 1 interrupted, and 2 affected future tasks, with 6839 future candidates. Scores were 172.4/182.0, a gain of 9.6 points. Fixed history contributed 51, and new tasks contributed 121.4/131. Coverage was 56/60 and 56/56. Net adjustments were 5/23. The relaxed upper bound was 182, and per-second checks against the original TLE found zero violations. The historical E3/E4 demo compares the complete workflow. Earlier E4 scored 172.4/184.0, a gain of 11.6 points, using different initial plans. These measurements refer to distinct experiments. This round used the recorded results and sample sizes, with separate verification scopes for historical TLE checks and current window integration.

Sealed configurations from older TLE work may still depend on local raw orbit and station data, absolute paths, and the original directory structure. The source kit excludes those data. Full relocation and reproduction of older TLE runs was outside scope. The standard window and synthetic workflows locate code relative to the kit root and support paths with Chinese characters and spaces. Final verification should confirm that `planner_import` points inside the extracted kit and that the kit has no `.git` directory.

## Status and Limitations

- Member 1's actual data: PENDING_INPUT / NOT_RUN. A limited check found no delivery with clear provenance. The official reference has its own provenance.
- Member 3's actual integration confirmation: PENDING_EXTERNAL. Member 2's local and extracted-directory verification covers member 2's runs. Member 3 must confirm their own run.
- Clean environment installation: NOT_RUN. Installation commands are provided. This round used the existing bd-fmb interpreter and dependencies and left `requirements-lock.txt` as it was.
- Full TLE reproduction on another machine, full optical validation, and formal scoring: unverified.
- Earlier optional reevaluation: BLOCKED under the existing contract.
- Source kit integrity, relocated integration, window evaluation and rechecks, the intake tool, and the demo kit each use the corresponding acceptance evidence. Items waiting for external confirmation retain that status.

See the [interface contract](io_contract.md) for windows, UTC, fault history, and scoring. Rule extensions require explicit team agreement before changing IDs, precision, time zones, priorities, stations, or sample definitions. Complete earlier records are in EXPERIMENTS and PROGRESS. E3/E4 and the demo are complete.
