# 部署、上传与恢复

本地发行适用于 Windows x64、64 位 CPython 3.11 和 Windows Universal C Runtime。解压完整测试包，按包根 README 建立干净环境，从 wheelhouse 安装锁定依赖。父进程需能创建嵌套 Windows Job Object。运行完整 pytest 还需可调用 git。

S02 从包根 famou/native/frozen_native.dll 的绝对解析路径装载 AMD64 PE32+。GCC 的 C++ 运行库静态链接，系统依赖为 KERNEL32 和 Windows UCRT API 集。系统 UCRT 随支持的现代 Windows 提供。每个求解进程核验 SHA256、ABI 布局、导出符号、实际模块路径及哨兵调用，再记录本次算法调用和返回。缺少 DLL、哈希或 ABI 不符、架构不符都会使 S02 原生求解失败，详情见 workflow.log、solve.log、failure.json 和 native.json。构建说明见 native/BUILD.md。

## 百度伐谋

**百度端待验收。** 当前官方文档的直接上传方式支持所有文件类型，每次发送最多 30 个文件，单文件大小受会员权益约束。按 UPLOAD_LIST.csv 和 UPLOAD_BATCHES.md 上传 upload/ 下的实际文件，保留 DLL、ZIP 原料和 wheel 的扩展名。运行机能否加载 Windows DLL 需单独核实。[百度伐谋官方文档](https://bce.bdstatic.com/p3m/pdf/bce-doc/online/FAMOU/FAMOU.pdf)

在平铺目录执行：

```powershell
python restore_upload.py --uploads . --out "../恢复 项目"
Set-Location "../恢复 项目"
python -m venv "../恢复 环境"
$py = (Resolve-Path "../恢复 环境/Scripts/python.exe").Path
& $py -m pip install --isolated --no-index --find-links wheelhouse -r famou/requirements-test-lock.txt
& $py scripts/famou_run.py --case synthetic --out "../恢复运行/synthetic"
```

恢复器按 UPLOAD_MANIFEST.json 验证长度、SHA256 和相对路径，再写入新目录。恢复后的 README 提供 S02、H180 和 pytest 命令。云端运行条件不足时，记录操作系统、架构、解释器及错误，保持 S02 云端待验收。Linux、macOS 和 ARM 原生求解需要另行移植和验收。完整本地测试包及审计包保存在交付目录。
