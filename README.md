# bd-fmb-observation-planner

自主观测任务规划。项目提供贪心基线、改进算法、站点故障后的重规划、原生无故障重排保护、独立校验及离线 Demo 生成工具。

Git 仓库包含源码、测试、合成示例和接入文档；真实比赛数据与完整运行产物保存在本地。无真实数据时也可以运行下面的合成流程。

## 快速开始（Windows / Python 3.11）

在 PowerShell 执行：

```powershell
git clone https://github.com/zindigo321/wznb.git
Set-Location wznb

conda create -n bd-fmb python=3.11 -y
conda activate bd-fmb
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw '依赖安装失败' }

python -X utf8 scripts/team3_run.py synthetic --out outputs/synthetic_01
if ($LASTEXITCODE -ne 0) { throw '查看控制台和 workflow.json' }
```

已有 `bd-fmb` 环境时，从激活环境开始。源码包解压后同样可从包根运行，不需要 `.git`。每次必须使用新的输出目录，例如下次改成 `outputs/synthetic_02`。

该命令依次运行基线规划、初始/故障独立评价和只读复查。合成例预期初始10分、故障后3分，两者均零违例；它验证接口和故障处理，不代表真实算法收益。结果位于 `outputs/synthetic_01`，总回执为 `workflow.json`。

## 运行测试与协作

```powershell
python -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw '开发依赖安装失败' }
New-Item -ItemType Directory -Path outputs -Force | Out-Null
python -X utf8 -m pytest tests -q --basetemp=outputs/pytest_01
```

测试目录也应每次使用新名称。GitHub 工作流提供 `Windows Python 3.11` 检查，首次云端运行状态以 [Actions 页面](https://github.com/zindigo321/wznb/actions)为准。协作、PR 和格式约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。干净环境安装是否已通过，应以云端安装步骤或单独安装回执为证，不能由现有环境运行结果推断。

## 项目结构

| 目录/入口 | 用途 |
| --- | --- |
| `planner/` | 调度、重规划、独立校验、窗口适配及安全读写 |
| `scripts/` | 团队接入、数据试读、受控实验和 Demo 生成 |
| `smoke_test.py` | 规划、独立评价及只读复查统一入口 |
| `configs/` | 合成及固定种子实验配置 |
| `examples/synthetic/` | 可公开运行的合成输入 |
| `tests/` | 接口、故障历史、路径和写入安全回归 |
| `demo/` | 离线演示模板和说明 |
| `docs/` | 接入契约、交接与实验说明 |

## 队友接入与实验结果

- [3号接入说明](docs/TEAM3_INTEGRATION.md)：从解压、运行到独立评价。
- [1号数据试读](docs/TEAM1_DATA_INTAKE.md)：标准窗口四文件及来源检查。
- [输入输出契约](docs/io_contract.md)：UTC、字段、故障边界和返回码。
- [原生无故障流程](docs/NO_FAULT_NATIVE.md)：冻结 source 包、严格选择、真实历史评价与零求解重查。
- [稳定交接](docs/STABLE_HANDOFF.md)：源码包与仅本地转交的参考包。
- [离线 Demo](demo/README.md)与[演示讲稿](docs/DEMO_SCRIPT.md)。
- [E5受控对照](docs/PATH_SAFETY_E5_HANDOFF.md)、[多种子与较晚故障实验](docs/IMPROVEMENT_DEMO_HANDOFF.md)、[原子写入修复](docs/ATOMIC_WRITE_FIX_HANDOFF.md)。
- [基线交接](BASELINE_HANDOFF.md)、[实验记录](EXPERIMENTS.md)、[进度记录](PROGRESS.md)、[团队待确认项](docs/team_questions.md)。

截至2026年11月2日，R33-C与R34分别通过H180_BASE起点的baseline、improved单组验收，决策时刻均为t=3600。相同冻结初始、候选、历史、规则和预算下，selected J分别为(2758,180)、(2806,180)：增加48整数分，即当前任务分口径9.6分，覆盖均为180。baseline平局保留；improved严格改善接纳，净调整49个目标，其中8个120→240秒升级贡献全部增分，其余41个调整不改变分数。详见[H180同起点配对](docs/R33_R34_H180_BASE_PAIR.md)。

R34达到本例固定completed/locked历史与冻结离散候选池下的2806条件主分松上界；这不是算法普遍最优或官方评分结论，也不支持降低扰动。R20共同输入保持INPUT_DELIVERY_PASS；R21原轮仍PARTIAL、native0/4，跨轮新增验收现为native2/4，H180_IMP起点两组尚未完成。不能报告完整H180方法矩阵或独立随机重复。

交付链状态另列：R27执行器资格通过；R28的seal/post/accept技术链退出均0，但缺少登记前完整计时证据，整体保持PARTIAL。R29/R30、R32和R33-A/B保持BLOCKED，R31仅启动计时资格通过。R33-C/R34未执行seal/post/accept，不表示最终交付闭合。旧轮状态不因后续成功升级，详见[当前状态](docs/CURRENT_STATUS.md)与[R27历史资格](docs/R27_EXECUTOR_QUALIFICATION.md)。

此前本机验证已包含第十四轮三站／十站共享初始对照、第十七轮连续状态链，以及第十八轮十站空历史初始化。第十八轮数据通过、封存失败，整体保持PARTIAL；第十九轮以零新增求解完成其证据恢复、正式封存、执行版本验收和独立新路径迁移，恢复交付通过。R19不把R18改记为完整PASS。

R20绑定已合入main的 `b0e646159a36a4d4375afc083f3b8db793bc131b` 完整99文件树；R33-C/R34实际执行绑定 `1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5` 的100文件产品树，不以本次文档提交替代执行版本。生产代码与此前 `83d3014` 绑定版本一致，差异为公开文档。原生 `no-fault` 使用 `J=(权威整数分,唯一覆盖)` 严格字典序选择，合法候选严格改善才接纳；低值／平局原字节保留retained。主分提高时覆盖仍可能下降，该保护不自动改变历史fault／legacy入口。本次更新仅同步文档，不新增产品算法、恢复API或测试通过数量。

R17完成8节点、8次schedule、28份外检及8份新几何，八节点均平局保留；R18完成2次initial和4次native，新initial为(914,60)、(1000,60)，但初始化分数提高不保证后续路径分数提高。R19新增schedule／原生backend／TLE传播均为0，只复核已有历史结果。历史失败、各轮独立预算和比较边界见[当前状态](docs/CURRENT_STATUS.md)、[R19恢复记录](docs/R19_RECOVERY_STATUS.md)及[实验记录](EXPERIMENTS.md)。

真实数据、任务表、完整恢复包、机器回执和本机提示词保留本地；仓库提供源码、合成输入和聚合事实。本机新路径独立验收不等于异机或现场设备验收。

## 本机真实 TLE 实验

以下命令仅适用于已有忽略目录 `prototype_v1/data_raw` 与原冻结样本的本机工程。新克隆应先运行合成示例；旧 TLE 全量移机未验证。

```powershell
# 在本机项目根、已激活的既有环境中执行。
$py = 'python'
& $py -X utf8 smoke_test.py --config configs/smoke.yaml --method baseline --out outputs/baseline_01
if ($LASTEXITCODE -ne 0) { throw '规划未通过' }
& $py -X utf8 smoke_test.py --check-only --source outputs/baseline_01 --out outputs/recheck_01
if ($LASTEXITCODE -ne 0) { throw '复查未通过' }
```

不修改原始数据和封存结果。E5复核须使用其专用 `scripts/run_replan_e5.py --check-only`，见对应交接说明。`requirements-lock.txt` 为本机原有完整环境快照，保持忽略，不作为公共依赖文件。

## 验证范围

每目标一次成功、中断零分、120/240秒离散得分、海拔近似椭球高是当前测试口径。几何仰角不代表完整光学可观测；标准窗口接入只检查供应窗口内的调度约束，不认证夜间、受光、天气等声明。R12增加同源同日的60/180相关规模，R13增加同一60目标的跨日/龄期敏感性；R14、R17和R18进一步验证同源60目标、十站、24小时模型；R20交付180目标共同输入，R33-C/R34补齐BASE起点的两方法单实例配对，完整H180矩阵仍未完成。十站完整六天、全10000目标、独立新来源、完整光学设备、正式评分和异机接收发布未验证。真实运行包仅在本机新路径完成迁移及零求解重查，不等于异机/设备现场验收。正式规则和两套评分差异待明确。
