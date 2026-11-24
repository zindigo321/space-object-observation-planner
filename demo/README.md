# Offline Experiment Replay

`template.html` is the generator template. The generator builds the page data from task CSV files, independent validation reports, and metrics. Keep real generated artifacts in the Git-ignored `outputs/` directory, including HTML, screenshots, and JSON files containing targets or windows.

The [source repository handoff](https://github.com/zindigo321/space-object-observation-planner/blob/main/docs/IMPROVEMENT_DEMO_HANDOFF.md) contains demo and screenshot commands for the historical E3/E4 results. The generated HTML opens directly in a browser offline.

## Generate the Synthetic Demo

Install the dependencies from the [quick start](../README.md#quick-start), then run the commands from the repository root. The example uses a one-hour synthetic time window starting at 06:00 UTC and includes stations 7 and 9.

```powershell
$py = (Resolve-Path '.venv/Scripts/python.exe').Path
$out = 'outputs/demo_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
& $py -X utf8 smoke_test.py --config configs/synthetic.yaml --out "$out/run"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic planning failed' }

$summary = Get-Content 'configs/demo_synthetic.json' -Raw | ConvertFrom-Json
$summary.cases[0].directory = "$out/run"
$summaryPath = Join-Path (Get-Location) "$out/summary.json"
[System.IO.File]::WriteAllText($summaryPath, ($summary | ConvertTo-Json -Depth 5))

& $py -X utf8 scripts/build_demo.py --summary $summaryPath --out "$out/html"
if ($LASTEXITCODE -ne 0) { throw 'Demo generation failed' }
Start-Process (Resolve-Path "$out/html/index.html").Path
```

Each run creates a fresh output directory and saves a summary that points to that run.

## Troubleshoot Generation Failures

Invalid evidence produces a `FAIL` or `BLOCKED` page with a reason and hides the normal metrics. The generator exits with 0 on success, 3 when complete evidence is missing, or 2 when the evidence is inconsistent. It rejects existing output directories and paths nested under the source directory to protect the source evidence.

The optional automated browser test uses local Node.js 24 and Chrome or Edge without npm dependencies. It targets the complete E3/E4 page. Pytest checks the synthetic example's data and status. The browser test loads the `file://` page through a local DevTools interface and applies offline network conditions. It uses `--no-sandbox --disable-gpu` only for the controlled local page. The outer budget wrapper terminates the browser process tree. Open the generated HTML normally for manual viewing.
