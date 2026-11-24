# 正式产品运行手册

本手册适用于 `FAMOU_TEST_PACKAGE.zip`。包内包含 S02 的 1,800 个冻结空间目标、10 个观测站、2026-07-31 UTC 全日原料和离线依赖，还有 H180 与合成用例。每次在新的包外目录保存运行结果。

## 离线安装

在解压根目录打开 PowerShell，使用 Windows x64 和 64 位 CPython 3.11。完整回归还需要 Git 和系统 Windows PowerShell，分别用于临时 Git 仓库和目录联接测试。

```powershell
python -m venv '../bd-fmb-venv'
if ($LASTEXITCODE -ne 0) { throw '虚拟环境创建失败' }

$py = (Resolve-Path '../bd-fmb-venv/Scripts/python.exe').Path
& $py -m pip install --isolated --no-index --find-links wheelhouse -r famou/requirements-test-lock.txt
if ($LASTEXITCODE -ne 0) { throw '离线依赖安装失败' }

$cli = 'scripts/famou_run.py'
$r = '../bd-fmb-run_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
New-Item -ItemType Directory -Path $r -ErrorAction Stop | Out-Null
```

## S02 运行步骤

按顺序运行冷生产、两份初始规划、四组无故障重排、独立评价及复查。两种重排方法分别使用两份初始规划的 `evaluation/selected.json` 作为共同起点。

```powershell
& $py -B -X utf8 $cli --case S02 --action cold --out "$r/cold"
if ($LASTEXITCODE -ne 0) { throw '冷生产失败' }

foreach ($method in 'baseline', 'improved') {
    & $py -B -X utf8 $cli --case S02 --action initial --input "$r/cold/input" --method $method --out "$r/init_$method"
    if ($LASTEXITCODE -ne 0) { throw "初始规划失败：$method" }
}

foreach ($origin in 'baseline', 'improved') {
    foreach ($method in 'baseline', 'improved') {
        & $py -B -X utf8 $cli --case S02 --action replan --input "$r/cold/input" --initial "$r/init_$origin/evaluation/selected.json" --method $method --out "$r/from_${origin}_$method"
        if ($LASTEXITCODE -ne 0) { throw "重排失败：$origin / $method" }
    }
}

foreach ($name in 'init_baseline', 'init_improved', 'from_baseline_baseline', 'from_baseline_improved', 'from_improved_baseline', 'from_improved_improved') {
    foreach ($action in 'evaluate', 'recheck') {
        & $py -B -X utf8 $cli --case S02 --action $action --input "$r/cold/input" --run "$r/$name" --out "$r/${action}_$name"
        if ($LASTEXITCODE -ne 0) { throw "独立评价或只读复查失败：$name / $action" }
    }
}
```

### 冷生产和输入绑定

冷生产核验两份原始压缩档及五份原始文本，解析 TLE、优先级和站址，按冻结实例顺序处理每个目标的完整 86,400 秒。窗口粗网格 30 秒、细化 1 秒，仰角 10–85 度。120 秒和 240 秒任务按 30 秒起点网格和末端补点生成，每个窗口每种时长最多保留 12 个均匀位置。窗口和候选跨目标连续编号。冻结对照为 68,069 个窗口、6,937,709 条原始网格候选、1,177,265 条保留候选。

`cold/input/` 使用与研究记录相同的有序 gzip NDJSON 任务模式。程序校验完整窗口、候选、裁剪与传播错误流的 SHA256，以及目标逐项计数、TLE、站址、优先级、规则和顺序。它接受本发行冷生产的目录和与之完整匹配的冻结 S02 研究输入。每次冷生产写入实际时间、实际归档和 `INPUT_MANIFEST.json`，运行绑定本次 manifest 的 SHA256。原始输入身份和语义流校验值见 [S02 输入契约](../configs/s02_contract.json)。

### 规划与评价

初始规划使用空历史。无故障重排从指定初始方案建立历史，决策时刻为第 3,600 秒，已完成和跨越此时刻的任务固定。未来任务必须属于原始候选池，每个目标最多成功一次，同站切换间隔至少 30 秒。

高、中、低优先级权重为 5、3、2，120 秒和 240 秒分别乘 3 和 5 取得整数分。目标函数 `J` 按整数分、覆盖目标数的字典序比较。严格改善才选用 `raw`。平局或退化时保留按决策时刻更新状态的原行、字段和顺序。`evaluation/` 含 `retained`、`raw`、`selected` 的评分与逐秒几何明细、分支和选用计划。评价器从原始 TLE 重新传播，覆盖任务两端及所有内部整数秒。

### 时限和复查

冷生产预算 1,800 秒。S02 的每个规划、独立评价或复查命令各有 600 秒预算，可用 `--budget-seconds` 收紧。可信父进程在启动子解释器前开始 30 秒求解计时，将挂起的进程加入 Windows Job 后才放行。导入、DLL 装载、读取解码、历史与索引、搜索、JSON 和 CSV 写出都在该 Job 内。父进程使用回执中的高精度执行秒数检查 30 秒门槛，退出后等待 Job 活跃进程数归零，并单列操作系统终止与清理耗时。

超时返回码为 3。查看 `workflow.json`、`case.json`、`solve.log` 和 `solve/native.json` 核对原始退出码、自然退出及父级清理。完成受控规划后才可进行独立评价和只读复查。复查重新读取独立原料和共同起点，并逐文件比较重算产物及源运行哈希。

## H180 和合成接口

```powershell
& $py -B -X utf8 $cli --case synthetic --out "$r/legacy_synthetic"
if ($LASTEXITCODE -ne 0) { throw '合成接口失败' }

& $py -B -X utf8 $cli --case H180_BASE --method baseline --out "$r/H180_BASE"
if ($LASTEXITCODE -ne 0) { throw 'H180_BASE 失败' }

& $py -B -X utf8 $cli --case H180_IMP --method improved --out "$r/H180_IMP"
if ($LASTEXITCODE -ne 0) { throw 'H180_IMP 失败' }

& $py -B -X utf8 scripts/famou_evaluator.py --case H180_IMP --tasks "$r/H180_IMP/run/selected.csv" --out "$r/evaluate_H180_IMP"
if ($LASTEXITCODE -ne 0) { throw 'H180_IMP 独立评价失败' }

& $py -B -X utf8 scripts/team3_run.py recheck --source "$r/H180_IMP/run" --source-sha256 b9567a450adf332fe587e9e325af0d61654e0268e1a889868e9d396d33e1dfac --out "$r/recheck_H180_IMP"
if ($LASTEXITCODE -ne 0) { throw 'H180_IMP 只读复查失败' }
```

H180 总预算上限为 180 秒。[H180 问题与外部候选脚本契约](problem.md)说明旧问题和接口。

## 自动回归

```powershell
& $py -B -X utf8 -m pytest -q tests --basetemp "$r/pytest"
if ($LASTEXITCODE -ne 0) { throw '回归测试失败' }
```

查看[平台指南](PLATFORM_GUIDE.md)了解上传恢复、Windows 运行库和百度伐谋验收状态。编译器及 ABI 见[原生组件构建说明](native/BUILD.md)。
