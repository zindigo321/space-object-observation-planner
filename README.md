# bd-fmb 观测任务规划产品版

本地发行包含 S02 的 1,800 个冻结空间目标、10 个观测站及 2026-07-31 UTC 全日原料，同时提供 H180 和 synthetic 接口。运行环境为 Windows x64 与 64 位 CPython 3.11。根目录 SOURCE_IDENTITY.json 给出实际提交、源码、DLL 及白名单。实际成绩、计时和本次 ZIP 哈希见包外 FINAL_ACCEPTANCE.json。

## 从解压包运行

在解压包根用 PowerShell 执行。python 须为 64 位 CPython 3.11，Git 命令行用于项目中的临时仓库回归用例。每次使用新的包外输出目录。

```powershell
python -m venv "../S02 环境"
$py = (Resolve-Path "../S02 环境/Scripts/python.exe").Path
& $py -m pip install --isolated --no-index --find-links wheelhouse -r famou/requirements-test-lock.txt
if ($LASTEXITCODE) { throw "安装失败" }
$cli = "scripts/famou_run.py"
$r = "../S02 运行"
& $py -B -X utf8 $cli --case S02 --action cold --out "$r/cold"
if ($LASTEXITCODE) { throw "冷生产失败" }
foreach ($method in "baseline","improved") {
    & $py -B -X utf8 $cli --case S02 --action initial --input "$r/cold/input" --method $method --out "$r/init_$method"
    if ($LASTEXITCODE) { throw "初始规划失败" }
}
foreach ($origin in "baseline","improved") {
    foreach ($method in "baseline","improved") {
        & $py -B -X utf8 $cli --case S02 --action replan --input "$r/cold/input" --initial "$r/init_$origin/evaluation/selected.json" --method $method --out "$r/from_${origin}_$method"
        if ($LASTEXITCODE) { throw "重排失败" }
    }
}
foreach ($name in "init_baseline","init_improved","from_baseline_baseline","from_baseline_improved","from_improved_baseline","from_improved_improved") {
    foreach ($action in "evaluate","recheck") {
        & $py -B -X utf8 $cli --case S02 --action $action --input "$r/cold/input" --run "$r/$name" --out "$r/${action}_$name"
        if ($LASTEXITCODE) { throw "独立评价或只读复查失败" }
    }
}
& $py -B -X utf8 -m pytest -q tests --basetemp="../S02 回归临时目录"
```

## S02 输入、时限与评价

冷生产从两份原始压缩档及五份原始文本核验并解析 TLE、优先级和站址，再按冻结实例中的顺序处理每个目标的完整 86,400 秒。使用整数秒时间轴复用几何变换，窗口粗网格 30 秒、细化 1 秒，仰角 10–85 度。120/240 秒时长以 30 秒候选起点网格及末端补点生成，每个窗口每种时长最多保留 12 个均匀位置。目标按实例顺序处理，窗口和候选跨目标连续编号。冻结对照为 68,069 个窗口、6,937,709 条原始网格候选、1,177,265 条保留候选。

cold/input/ 使用与研究记录相同的有序 gzip NDJSON 任务模式。程序校验完整窗口、候选、裁剪与传播错误流的 SHA256、目标逐项计数、TLE、站址、优先级、规则及顺序。支持本发行冷生产的目录和与之完整匹配的冻结 S02 研究输入。每次冷生产写入实际时间、实际归档和 INPUT_MANIFEST.json，运行绑定到本次 manifest 的 SHA256。原始输入身份和语义流的校验值在 configs/s02_contract.json。

初始规划使用空历史。无故障重排从指定初始方案建立历史，决策时刻为第 3,600 秒，已完成和跨越此时刻的任务固定。未来任务必须属于原始候选池，每个目标最多成功一次，同站切换间隔至少 30 秒。高、中、低优先级权重为 5、3、2，120/240 秒分别乘 3/5 取得整数分。J 按整数分、覆盖目标数的字典序比较。严格改善才接受 raw，平局及退化均保留按决策时刻更新状态的原行、字段和顺序。evaluation/ 含 retained、raw、selected 的评分与逐秒几何明细、分支和选用计划。评价器从原始 TLE 重新传播，覆盖任务两端及所有内部整数秒。

冷生产预算 1,800 秒。S02 每个规划、独立评价或复查命令各自预算 600 秒，可用 --budget-seconds 收紧。可信父进程在启动子解释器前开始 30 秒求解计时，将挂起的进程加入 Windows Job 后才放行。导入、DLL 装载、读取解码、历史/索引、搜索、JSON 和 CSV 写出都在该 Job 内。退出后等待该 Job 活跃进程数归零。超时返回码 3，读取 workflow.json、case.json、solve.log 和 solve/native.json 核对原始退出码、自然退出与父级清理。只有完成的受控规划可进入独立评价与只读复查。复查重新打开独立原料和共同起点，并逐文件比较重算产物及源运行哈希。

## H180 和合成接口

```powershell
& $py scripts/famou_run.py --case synthetic --out "../旧入口/synthetic"
& $py scripts/famou_run.py --case H180_BASE --method baseline --out "../旧入口/H180_BASE"
& $py scripts/famou_run.py --case H180_IMP --method improved --out "../旧入口/H180_IMP"
& $py scripts/famou_evaluator.py --case H180_IMP --tasks "../旧入口/H180_IMP/run/selected.csv" --out "../旧入口/evaluate"
& $py scripts/team3_run.py recheck --source "../旧入口/H180_IMP/run" --source-sha256 b9567a450adf332fe587e9e325af0d61654e0268e1a889868e9d396d33e1dfac --out "../旧入口/recheck"
```

H180 的总预算上限为 180 秒。历史 H180 问题与外部候选脚本契约见 famou/problem.md。上传恢复、Windows 运行库和百度端待验收说明见 famou/PLATFORM_GUIDE.md，编译器及 ABI 见 famou/native/BUILD.md。
