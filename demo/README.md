# 离线实验回放

`template.html` 是生成器模板，页面数据由任务 CSV、独立校验报告及指标生成。将真实生成物留在 Git 忽略的 `outputs/`，包括 HTML、截图、目标和窗口 JSON。

历史 E3/E4 结果的演示与截图命令见[源码仓库交接说明](https://github.com/zindigo321/wznb/blob/main/docs/IMPROVEMENT_DEMO_HANDOFF.md)。生成的 HTML 可直接在浏览器中离线打开。

## 生成合成演示

按[快速上手](../README.md#快速上手)安装依赖后，从仓库根目录执行。示例使用 06:00 UTC 开始的 1 小时合成窗口，包含站点 7 和 9。

```powershell
$py = (Resolve-Path '.venv/Scripts/python.exe').Path
$out = 'outputs/demo_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
& $py -X utf8 smoke_test.py --config configs/synthetic.yaml --out "$out/run"
if ($LASTEXITCODE -ne 0) { throw '合成规划失败' }

$summary = Get-Content 'configs/demo_synthetic.json' -Raw | ConvertFrom-Json
$summary.cases[0].directory = "$out/run"
$summaryPath = Join-Path (Get-Location) "$out/summary.json"
[System.IO.File]::WriteAllText($summaryPath, ($summary | ConvertTo-Json -Depth 5))

& $py -X utf8 scripts/build_demo.py --summary $summaryPath --out "$out/html"
if ($LASTEXITCODE -ne 0) { throw '演示生成失败' }
Start-Process (Resolve-Path "$out/html/index.html").Path
```

每次运行生成新的输出目录，并在其中保存指向本次运行的摘要。

## 排查生成失败

错误证据会生成可解释的 FAIL/BLOCKED 页面，并隐藏正常指标区域。生成器返回码：成功 0、无完整证据 3、证据内容不一致 2；已存在目录和源目录嵌套直接拒绝，不覆盖源证据。

可选自动浏览器测试使用本机 Node 24 与 Chrome/Edge，无 npm 依赖。它针对完整 E3/E4 页面；合成示例由 pytest 验证数据和状态。测试器通过本机 DevTools 接口加载 `file://` 页面，并启用离线网络条件；只为受控本地页面使用 `--no-sandbox --disable-gpu`，外层预算入口负责终止浏览器进程树。用户正常打开 HTML 无需这些启动参数。
