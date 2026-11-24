# Space Object Observation Planner

The planner builds and revises observation schedules from ground stations, space objects, and visibility windows. Synthetic inputs let you run scheduling, independent evaluation, and read-only checks locally.

## 快速上手

使用 Windows x64、64 位 CPython 3.11、Git 和 PowerShell。先用 `python --version` 确认当前解释器版本。

```powershell
git clone https://github.com/zindigo321/space-object-observation-planner.git
if ($LASTEXITCODE -ne 0) { throw '仓库克隆失败' }
Set-Location space-object-observation-planner -ErrorAction Stop
python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw '虚拟环境创建失败' }

$py = (Resolve-Path '.venv/Scripts/python.exe').Path
& $py -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw '开发依赖安装失败' }

$out = 'outputs/synthetic_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
& $py -X utf8 scripts/team3_run.py synthetic --out $out
if ($LASTEXITCODE -ne 0) { throw '合成流程失败，请查看控制台和输出目录' }
```

成功后查看 `$out/workflow.json`，其中 `status` 为 `PASS`，`exit_code` 为 `0`。规划、评价和复查结果保存在同一输出目录。每次运行使用新目录。完整测试命令见[协作指南](CONTRIBUTING.md#本地验证)。

## 正式交付与验收

S02 和 H180 的冻结用例随项目组交付的 `FAMOU_TEST_PACKAGE.zip` 提供。拿到对应版本后，从解压目录按[正式产品运行手册](famou/RUNBOOK.md)离线安装，并执行规划、评价和复查。

S02 已在 Windows x64 上完成本地正式验收，验收版本绑定提交 `6aacb4a64d5b32d388c7ecbcad7ae361bb31b29d`。百度伐谋端待验收。交付包的源码身份见包内 `SOURCE_IDENTITY.json`，成绩、计时和 ZIP 哈希见随包的 `FINAL_ACCEPTANCE.json`。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `planner/` | 调度、重规划、输入校验及独立评价 |
| `scripts/` | 运行、试读、打包及验收入口 |
| `configs/`、`examples/synthetic/` | 配置及公开合成示例 |
| `tests/` | 自动回归测试 |
| `famou/` | 正式运行手册、平台说明、锁定依赖及原生组件 |
| `demo/` | [离线演示](demo/README.md)模板和合成示例用法 |
| `docs/`、`research/` | 源码仓库的接口文档、验收记录和研究工具 |

通过[源码文档索引](https://github.com/zindigo321/space-object-observation-planner/tree/main/docs#readme)查找当前状态、数据接入契约与历史实验记录。提交修改前请阅读[协作指南](CONTRIBUTING.md)。
