# 百度伐谋公有云上传及运行

本次准备模式：用户在 https://www.famou.com/ 创建公有云测试任务、上传代码与数据、粘贴开场 Prompt。尚未登录百度、创建付费任务或取得百度实测回执。状态：待用户在百度伐谋测试。

2026-11-17 读取官方文档 https://cloud.baidu.com/doc/FAMOU/index.html 及 https://bce.bdstatic.com/p3m/pdf/bce-doc/online/FAMOU/FAMOU.pdf。PDF 的“常见问题 / 4.1”列出 .py、.csv、.json、.md、.txt 等，未列 ZIP；每次发送最多 30 文件。具体大小受套餐和页面规则约束。未验证用户账号的上传页面及配额；应以实际页面为准。

ZIP 是本地交付载体，请先在本机解压；只上传 upload/ 中 UPLOAD_MANIFEST.json 列出的文件以及清单指定的引导文件。UPLOAD_LIST.csv 逐项给出批次、用途、大小、哈希及恢复路径；UPLOAD_BATCHES.md 给出每批完整文件名。所有批次完成后再开始恢复。不要上传 AUDIT_PACKAGE.zip 或审计目录。

平铺上传文件保留可接受扩展名，原 yaml/mjs/无扩展名内容使用 .txt 传输；恢复程序按清单原样还原路径和字节，不能手工重写内容。首次恢复命令在 FAMOU_START_PROMPT.txt 中。程序会拒绝缺文件、哈希变化、重复或越界路径以及覆盖现有目录。若界面更改文件名，先据清单重命名，再执行。

推荐 Python 3.11；本机实测版本见验收报告。公有云安装：

`python -m pip install -r famou/requirements-lock.txt`

完整本地 ZIP 另带 Windows CPython 3.11 wheelhouse 时，可离线安装：

`python -m pip install --no-index --find-links wheelhouse -r famou/requirements-lock.txt`

wheelhouse 不在上传清单；Linux/macOS/其他 Python 需使用对应平台依赖，尚未实测，不宣称通过。

包内配置均按包根相对路径解析。输出必须使用新建目录，并放在包目录之外，例如 ../runs/H180_IMP_baseline。H180 包含真实冻结源的八个文件、初始计划、候选、模型和外部期望源哈希；geometry/ 附冻结几何参考。无原机 G:/D: 路径或本机受保护密钥运行依赖。原仓库历史文档中的路径仅供历史背景，使用本指南入口。

生产、独立评价、只读复查：

`python scripts/famou_run.py --case H180_IMP --method improved --out ../runs/H180_IMP_improved`

`python scripts/famou_evaluator.py --case H180_IMP --tasks ../runs/H180_IMP_improved/run/selected.csv --out ../runs/evaluate_imp`

`python scripts/team3_run.py recheck --source ../runs/H180_IMP_improved/run --source-sha256 b9567a450adf332fe587e9e325af0d61654e0268e1a889868e9d396d33e1dfac --out ../runs/recheck_imp`

原始 CSV 提案评价并选择：

`python scripts/famou_evaluator.py --case H180_BASE --tasks proposal.csv --proposal --out ../runs/proposal_check`

生产预期输出为 workflow.json、run/retained.csv、raw_proposal.csv、selected.csv、branch_receipt.json、solver_execution.json、evaluation/evaluation.json、recheck/recheck.json 及日志。适配器退出 0=通过，2=非法/失败，3=缺资源或超时（具体原因看日志）。可运行性复测单独记账，不是新的正式科学重复。

混合云区别：官方企业级 Skills 流程将问题定义与初始代码、演化提示、配置关联，并让评价器和原始数据留在本地、由本地 evaluator 上报指标。公开手册未给出可据此统一实现的 Python evaluate 函数签名，因此本包不伪造混合云 callback 或提交 API。需要混合云时须另按实际安装的企业工具契约适配；本次 problem.md 和评价 CLI 是本项目契约。

可优化范围与输入保护见 problem.md。合成结果不代表真实 H180；模型内几何验证不代表现场观测或真实轨道精度；完整六天、10000目标、官方评分和现场验收仍属扩展验证。
