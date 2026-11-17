# 2026-11-17 FAMOU 交付状态

本地正式实验矩阵 3/4；剩余组受原生宿主资格检查阻塞，未提交或消耗新正式请求。 百度端：待用户在百度伐谋测试。

本轮源码从实际H180产品对象 `1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5` 建立隔离分支。最终对象记录在包内 SOURCE_IDENTITY.json；planner/ 科学核心未改变。新增相对路径入口、独立评价、候选限时运行、固定资产核验、平铺上传恢复和白名单打包。没有用旧main的源码冒充H180实跑对象。

| 实验组 | 正式状态 | retained / raw / selected J |
| --- | --- | --- |
| H180_BASE_baseline | PASS | [2758, 180] / [2758, 180] / [2758, 180] |
| H180_BASE_improved | PASS | [2758, 180] / [2806, 180] / [2806, 180] |
| H180_IMP_baseline | PASS | [3000, 180] / [2814, 180] / [3000, 180] |
| H180_IMP/improved | BLOCKED，尚未正式提交 | 无正式结果 |

BASE配对使用完全相同起点，selected主分增加48，覆盖仍180。IMP已证实的baseline从retained3000、raw2814选择保留3000。只有正式证据完整时才补齐剩余格；ZIP可运行性复测不计为正式科学重复。

历史100个产品文件中92个与原Git blob逐字节相同，8个examples/synthetic CSV仅部署时CRLF转LF；科学Python及H180源完全一致。最终源码从最终Git对象原始blob导出。旧R35宿主实际V1/后写V2来源差异保存在审计包历史说明中。

完整回归290项通过。最终ZIP的实际依赖安装、合成流程、H180生产/独立评价/只读复查、上传还原、合法不同分数、非法输出、历史篡改、超时和固定资产篡改结果，见包外LOCAL_ACCEPTANCE.json及审计包validation/；验收绑定最终ZIP字节和SHA256，不从本说明推断未执行测试。

本地包使用Windows CPython3.11；随包离线wheel适用于该平台。百度端、Linux/macOS及其他Python未实测。公有云每次最多30文件，ZIP不在当前官方格式表；逐文件用途和恢复路径见UPLOAD_LIST.csv，步骤见famou/PLATFORM_GUIDE.md，全部上传后粘贴FAMOU_START_PROMPT.txt。

包内H180为真实冻结输入，180目标、10站、24小时时域；完整六天、10000目标、官方评分、现场验收不属于本轮默认范围。原机受保护Windows宿主只作审计，不是上传算法的依赖。

逐次失败、原始退出、资格判定、复现和最小剩余动作均在AUDIT_PACKAGE.zip。不能把程序seal/post/accept冒充本人签收；不完整矩阵不得标为四组通过。
