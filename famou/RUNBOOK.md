# Release Runbook

This runbook applies to `FAMOU_TEST_PACKAGE.zip`. The package includes the frozen S02 instance with 1,800 space objects, 10 ground stations, a full day of raw inputs for 2026-07-31 UTC, and offline dependencies. It also contains H180 and synthetic cases. Save each run's results in a fresh directory outside the package.

## Offline Installation

Open PowerShell in the extracted package root. Use Windows x64 and 64-bit CPython 3.11. The full regression suite also needs Git for temporary repositories and Windows PowerShell for directory junction tests.

```powershell
python -m venv '../bd-fmb-venv'
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed' }

$py = (Resolve-Path '../bd-fmb-venv/Scripts/python.exe').Path
& $py -m pip install --isolated --no-index --find-links wheelhouse -r famou/requirements-test-lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Offline dependency installation failed' }

$cli = 'scripts/famou_run.py'
$r = '../bd-fmb-run_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
New-Item -ItemType Directory -Path $r -ErrorAction Stop | Out-Null
```

## Run S02

Generate the cold inputs first, then run two initial plans, four no-fault replans, independent evaluation, and read-only rechecks. Apply both replanning methods to each initial plan's `evaluation/selected.json` so that the pair shares a starting point.

```powershell
& $py -B -X utf8 $cli --case S02 --action cold --out "$r/cold"
if ($LASTEXITCODE -ne 0) { throw 'Cold input generation failed' }

foreach ($method in 'baseline', 'improved') {
    & $py -B -X utf8 $cli --case S02 --action initial --input "$r/cold/input" --method $method --out "$r/init_$method"
    if ($LASTEXITCODE -ne 0) { throw "Initial planning failed for $method" }
}

foreach ($origin in 'baseline', 'improved') {
    foreach ($method in 'baseline', 'improved') {
        & $py -B -X utf8 $cli --case S02 --action replan --input "$r/cold/input" --initial "$r/init_$origin/evaluation/selected.json" --method $method --out "$r/from_${origin}_$method"
        if ($LASTEXITCODE -ne 0) { throw "Replanning failed for $origin / $method" }
    }
}

foreach ($name in 'init_baseline', 'init_improved', 'from_baseline_baseline', 'from_baseline_improved', 'from_improved_baseline', 'from_improved_improved') {
    foreach ($action in 'evaluate', 'recheck') {
        & $py -B -X utf8 $cli --case S02 --action $action --input "$r/cold/input" --run "$r/$name" --out "$r/${action}_$name"
        if ($LASTEXITCODE -ne 0) { throw "Independent evaluation or read-only recheck failed for $name / $action" }
    }
}
```

### Cold Input Generation and Input Binding

Cold input generation verifies two original archives and five original text files, parses TLEs, priorities, and station locations, and processes all 86,400 seconds for each target in frozen instance order. Visibility windows use a coarse grid of 30 seconds, refined to 1 second, with elevation from 10 to 85 degrees. The generator creates 120- and 240-second tasks from a 30-second start grid plus the window's final feasible start. It retains at most 12 evenly spaced positions per duration per window. Window and candidate IDs are sequential across targets. The frozen reference contains 68,069 windows, 6,937,709 original grid candidates, and 1,177,265 retained candidates.

`cold/input/` uses the same ordered gzip NDJSON task schema as the research record. The program verifies the SHA-256 of the complete window, candidate, pruning, and propagation error streams, along with per-target counts, TLEs, stations, priorities, rules, and ordering. It accepts directories generated from scratch by this release and frozen S02 research inputs that match in full. Each cold generation records the actual time, archive, and `INPUT_MANIFEST.json`. Subsequent runs bind to the SHA-256 of that manifest. See the [S02 input contract](../configs/s02_contract.json) for raw input identities and semantic stream checksums.

### Planning and Evaluation

Initial planning starts with empty history. No-fault replanning derives history from the specified initial plan at decision second 3,600. Tasks completed before or at that time and tasks spanning it are fixed. Future tasks must come from the original candidate pool. Each target may succeed at most once, and switching between targets at the same station requires at least 30 seconds.

High, medium, and low priorities have weights of 5, 3, and 2. Multiply the weight by 3 for a 120-second task and by 5 for a 240-second task to obtain integer points. The objective `J` compares integer points first and then the number of covered targets. The evaluator selects `raw` only when it strictly improves the objective. On a tie or regression, it retains the original rows, fields, and ordering with statuses updated at the decision time. `evaluation/` contains scores and per-second geometry details for `retained`, `raw`, and `selected`, together with the decision branch and chosen plan. The evaluator propagates from the original TLEs, checking both endpoints of every task and each integer second between them.

### Time Limits and Rechecks

Cold input generation has a budget of 1,800 seconds. Every S02 planning, independent evaluation, or recheck command has a 600-second budget, which `--budget-seconds` can tighten. The trusted parent process starts the 30-second solve timer before launching the child interpreter. It adds the suspended child to a Windows Job before resuming it. Imports, DLL loading, reads and decoding, history and indexing, search, and JSON and CSV writes all run within that Job. The parent uses the high-resolution execution time in the receipt to check the 30-second limit. After the child exits, it waits for the Job's active process count to reach zero and records operating-system termination and cleanup time separately.

A timeout returns exit code 3. Check `workflow.json`, `case.json`, `solve.log`, and `solve/native.json` for the raw exit code, natural exit status, and parent cleanup. Independent evaluation and read-only recheck require a completed guarded plan. The recheck reads the independent raw inputs and common starting point again, then compares the recomputed artifacts and source-run hashes file by file.

## H180 and Synthetic Interfaces

```powershell
& $py -B -X utf8 $cli --case synthetic --out "$r/legacy_synthetic"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic interface failed' }

& $py -B -X utf8 $cli --case H180_BASE --method baseline --out "$r/H180_BASE"
if ($LASTEXITCODE -ne 0) { throw 'H180_BASE failed' }

& $py -B -X utf8 $cli --case H180_IMP --method improved --out "$r/H180_IMP"
if ($LASTEXITCODE -ne 0) { throw 'H180_IMP failed' }

& $py -B -X utf8 scripts/famou_evaluator.py --case H180_IMP --tasks "$r/H180_IMP/run/selected.csv" --out "$r/evaluate_H180_IMP"
if ($LASTEXITCODE -ne 0) { throw 'H180_IMP independent evaluation failed' }

& $py -B -X utf8 scripts/team3_run.py recheck --source "$r/H180_IMP/run" --source-sha256 b9567a450adf332fe587e9e325af0d61654e0268e1a889868e9d396d33e1dfac --out "$r/recheck_H180_IMP"
if ($LASTEXITCODE -ne 0) { throw 'H180_IMP read-only recheck failed' }
```

H180 has a 180-second total budget. The [H180 problem and external candidate script contract](problem.md) describes the legacy case and interface.

## Automated Regression Tests

```powershell
& $py -B -X utf8 -m pytest -q tests --basetemp "$r/pytest"
if ($LASTEXITCODE -ne 0) { throw 'Regression tests failed' }
```

See the [platform guide](PLATFORM_GUIDE.md) for upload restoration, Windows runtime requirements, and Baidu FAMOU acceptance status. The [native build guide](native/BUILD.md) documents the compiler and ABI.
