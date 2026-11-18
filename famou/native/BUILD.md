# Windows x64 原生构建

frozen_native.cpp 与研究提交 c118d8e 的源文件逐字节相同。使用 MSYS2 UCRT64 GCC 13.2.0 Rev3。ABI.json 记录编译器 SHA256、源及产物 SHA256、参数、PE 导入库和结构体字段偏移。C 接口为 cdecl select_rows，候选行 40 字节，占用记录 16 字节，整数为小端 int32，ID 为 16 字节定长字符数组。调用者提供输出索引缓冲区及预算检查回调。

将 frozen_native.cpp 和 build_native.py 复制到新的空目录，使用 ABI.json 指定的编译器运行：

```powershell
$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
python build_native.py --compiler C:\msys64\ucrt64\bin\g++.exe --receipt DLL_BUILD.json
Get-FileHash frozen_native.dll -Algorithm SHA256
```

发行 DLL 为 587313 字节，SHA256 为 95f539caea5dbf4cd46b0b34e678123089316fd6559c30376d40a246e5b94251。部署在包根 famou/native/。运行机通过 Windows 自带的 Kernel32 和 UCRT 加载。重建结果须与冻结 DLL 逐字节匹配。
