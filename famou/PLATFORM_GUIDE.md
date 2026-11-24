# Deployment, Upload, and Restoration

The local release targets Windows x64, 64-bit CPython 3.11, and the Windows Universal C Runtime. Extract the complete test package and follow the [release runbook](RUNBOOK.md) to create a clean environment and install locked dependencies from `wheelhouse/`. The parent process must be able to create nested Windows Job Objects. The full pytest suite also requires Git.

S02 loads an AMD64 PE32+ DLL from the resolved absolute path of `famou/native/frozen_native.dll` under the package root. The build statically links the GCC C++ runtime and uses KERNEL32 and Windows UCRT API sets as system dependencies. Supported modern Windows versions supply the UCRT. Each solve process verifies the SHA-256, ABI layout, exported symbols, actual module path, and sentinel call before recording the algorithm call and its return value. S02 native solving fails if the DLL is missing or its hash, ABI, or architecture does not match. See `workflow.log`, `solve.log`, `failure.json`, and `native.json` for details and [native/BUILD.md](native/BUILD.md) for build instructions.

## Baidu FAMOU

**Acceptance on Baidu FAMOU is pending.** The official documentation describes direct uploads of all file types, with a maximum of 30 files per message and per-file size limits based on membership. Follow `UPLOAD_LIST.csv` and `UPLOAD_BATCHES.md` to upload the files from `upload/`. Keep the original extensions on DLLs, raw input ZIPs, and wheels. Check separately whether the runtime host can load Windows DLLs. [Official Baidu FAMOU documentation](https://bce.bdstatic.com/p3m/pdf/bce-doc/online/FAMOU/FAMOU.pdf)

Run these commands from the directory containing the flattened upload files.

```powershell
python restore_upload.py --uploads . --out "../Restored Project"
Set-Location "../Restored Project"
python -m venv "../Restored Environment"
$py = (Resolve-Path "../Restored Environment/Scripts/python.exe").Path
& $py -m pip install --isolated --no-index --find-links wheelhouse -r famou/requirements-test-lock.txt
& $py scripts/famou_run.py --case synthetic --out "../Restored Runs/synthetic"
```

The restore tool verifies file lengths, SHA-256 values, and relative paths against `UPLOAD_MANIFEST.json`, then writes to a new directory. The restored `famou/RUNBOOK.md` provides S02, H180, and pytest commands. If the cloud runtime cannot meet the requirements, record the operating system, architecture, interpreter, and error, and leave S02 cloud acceptance pending. Native solving on Linux, macOS, and ARM requires separate porting and acceptance. The delivery directory contains the complete local test and audit packages.
