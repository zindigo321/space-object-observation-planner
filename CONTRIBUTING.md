# Contributing

## Start a Change

Organize any local changes, then create a working branch from the latest `main`.

```powershell
git switch main
git pull --ff-only origin main
git switch -c work/your-task-name
```

Merge changes into `main` through a pull request. Use a commit message that describes the actual change, such as "Fix preservation of tasks completed before a fault."

## Local Verification

Follow the [quick start](README.md#quick-start) to set up Windows x64, 64-bit CPython 3.11, and development dependencies. Run the following commands from the repository root. To use an existing environment, set `$py` to its interpreter.

```powershell
$py = (Resolve-Path '.venv/Scripts/python.exe').Path
$run = 'outputs/local_check_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
New-Item -ItemType Directory -Path $run -ErrorAction Stop | Out-Null

& $py -X utf8 -m pytest tests -q --basetemp "$run/pytest" --junitxml "$run/pytest.xml"
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }

& $py -X utf8 scripts/team3_run.py synthetic --out "$run/synthetic"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic integration failed' }
```

Use a fresh output directory for each run. Run directory junction, case-alias, and similar tests on Windows. Report which tests ran and why any were skipped.

## Inspect the Staged Changes

Stage the files you intend to deliver, then inspect the file list and diff before committing.

```powershell
git add -- path/to/changed-file
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m 'Describe the change'
git push -u origin HEAD
```

Remove real source data, real target, window, or task tables, run outputs, caches, screenshots, archives, passwords, tokens, machine-specific environment snapshots, and local prompts from the staging area. Label new examples as synthetic.

## Issues, Pull Requests, and CI

Use [GitHub Issues](https://github.com/zindigo321/space-object-observation-planner/issues) to report problems or suggest improvements. Prefer synthetic examples for reproductions and remove real data and credentials from log excerpts.

Use the [pull request template](.github/pull_request_template.md) to describe the change, the checks actually run, and any impact on interfaces or data. Confirm that the `Windows Python 3.11` check passes before merging into `main`.

The [CI workflow](.github/workflows/ci.yml) runs for pull requests targeting `main`, pushes to `main`, and manual dispatches. It checks dependencies, runs the regression suite and synthetic integration, and checks the synthetic workflow receipt. Pull requests and pushes also check whitespace on changed lines in Markdown, YAML, JSON, EditorConfig, and Git configuration. See the [release runbook](famou/RUNBOOK.md) for formal data workflows.

## Formatting and Existing Evidence

- Follow [EditorConfig](.editorconfig) and the [Git attributes](.gitattributes) when adding or editing source and documentation. Use UTF-8, LF line endings, and a final newline in documentation. Label code blocks with their language, such as `powershell`, and use inline code for paths.
- Indent Python with four spaces. Indent YAML, JSON, HTML, and JavaScript with two spaces. Limit formatting changes to the content you are editing.
- Preserve the original bytes of sealed experiments, fixed inputs, and release manifests. CSV files follow the existing Git text handling rules.

The project has yet to select an open-source license. The project team will decide the applicable terms.
