# 协作指南

## 开始修改

整理好本地改动后，从最新的 `main` 创建工作分支。

```powershell
git switch main
git pull --ff-only origin main
git switch -c work/你的任务名称
```

通过 Pull Request 合入 `main`。提交说明写清实际变化，例如“修复故障前完成任务保留”。

## 本地验证

按[快速上手](README.md#快速上手)准备 Windows x64、64 位 CPython 3.11 和开发依赖。在仓库根目录执行以下命令。使用已有环境时，将 `$py` 设为对应的解释器。

```powershell
$py = (Resolve-Path '.venv/Scripts/python.exe').Path
$run = 'outputs/local_check_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
New-Item -ItemType Directory -Path $run -ErrorAction Stop | Out-Null

& $py -X utf8 -m pytest tests -q --basetemp "$run/pytest" --junitxml "$run/pytest.xml"
if ($LASTEXITCODE -ne 0) { throw '测试未通过' }

& $py -X utf8 scripts/team3_run.py synthetic --out "$run/synthetic"
if ($LASTEXITCODE -ne 0) { throw '合成接入未通过' }
```

每次使用新输出目录。目录联接和大小写别名等用例在 Windows 上执行。报告中注明实际运行的测试和跳过原因。

## 检查提交内容

只暂存本次要交付的文件，在提交前查看列表与差异：

```powershell
git add -- 你修改的文件
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m '说明本次实际改动'
git push -u origin HEAD
```

检查暂存区，移除真实原始数据、真实目标/窗口/任务表、运行输出、缓存、截图、压缩包、密码、Token、机器专属环境快照及本地提示词。新增示例应明确标注为合成数据。

## Issue、Pull Request 与 CI

在 [GitHub Issues](https://github.com/zindigo321/wznb/issues)报告问题或提交改进建议。复现问题时优先使用合成示例，日志摘录应去除真实数据和凭据。

按 [PR 模板](.github/pull_request_template.md)说明改动、实际验证和接口或数据影响。合入 `main` 前确认 `Windows Python 3.11` 检查通过。

[CI 工作流](.github/workflows/ci.yml)在指向 `main` 的 PR、`main` 的推送和手动触发时运行。它检查依赖、执行回归和合成接入，并校验合成回执。PR 和推送还会检查 Markdown、YAML、JSON、EditorConfig 和 Git 配置中改动行的空白格式。正式数据的运行步骤见[正式产品运行手册](famou/RUNBOOK.md)。

## 格式与现有证据

- 新增或编辑的源码和文档遵循 [EditorConfig](.editorconfig) 和 [Git 属性](.gitattributes)。文档使用 UTF-8、LF 及文件末尾换行。命令示例标注语言，例如 `powershell`，文件路径用行内代码。
- Python 使用 4 空格缩进。YAML、JSON、HTML 和 JavaScript 使用 2 空格缩进。格式调整限于本次编辑的内容。
- 保留封存实验、固定输入和发布清单的原始字节。CSV 沿用现有 Git 文本处理规则。

项目尚未确定开源许可证，由项目组决定适用条款。
