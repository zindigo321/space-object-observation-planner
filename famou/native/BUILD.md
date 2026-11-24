# Windows x64 Native Build

`frozen_native.cpp` is byte-for-byte identical to the source file at research commit `c118d8e`. Build it with MSYS2 UCRT64 GCC 13.2.0 Rev3. `ABI.json` records the compiler, source, and artifact SHA-256 hashes, compiler arguments, PE imports, and struct field offsets. The C interface is the cdecl function `select_rows`. Candidate rows occupy 40 bytes and occupancy records occupy 16 bytes. Integers are little-endian `int32` values, and IDs are fixed-width 16-byte character arrays. The caller supplies the output index buffer and the budget-check callback.

Copy `frozen_native.cpp` and `build_native.py` to a new empty directory, then run the compiler specified in `ABI.json`.

```powershell
$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
python build_native.py --compiler C:\msys64\ucrt64\bin\g++.exe --receipt DLL_BUILD.json
Get-FileHash frozen_native.dll -Algorithm SHA256
```

The release DLL is 587313 bytes and its SHA-256 is `95f539caea5dbf4cd46b0b34e678123089316fd6559c30376d40a246e5b94251`. Deploy it to `famou/native/` under the package root. The runtime host loads it through the Windows-provided Kernel32 and UCRT. A rebuild must match the frozen DLL byte for byte.
