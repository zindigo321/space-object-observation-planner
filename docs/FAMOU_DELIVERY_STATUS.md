# 2026-11-17 最终 FAMOU 交付状态

本地正式实验矩阵 4/4；四组 seal、全新路径 post/读回及程序 accept 已通过。 百度端：待用户在百度伐谋测试。

本轮从实际前次交付提交 `690eb12c66e2906d7596435e8a70823805f789f3` 建立隔离分支，科学基线为 `1e35f9575ba79bd0d25fdfe96f624dce2a4ff5a5`。最终提交写入包内 SOURCE_IDENTITY.json，原始 Git blob 白名单导出。没有用旧 main 的 09c12b9 替代。

planner/ 中只有运行保护 process_guard.py 改变；其余调度、候选生成、计分、历史和选择规则与科学基线逐字节相同。Windows 在成功、失败、超时三种终态都终止 Job 并确认 ActiveProcesses=0。POSIX 在清理前用 waitid/WNOWAIT 保留父进程 PID，再终止受控进程组；该系统路径未实测，不把模拟当作 Linux 验收。

候选改为 solve(problem) 返回任务行。可信父进程控制准备40/求解30/写出20/评价80秒，合计受180秒外层截止限制；候选导入、求解和返回序列化均在30秒受控子进程内。所有后代结束后才固定CSV、独立评价。回执在启动前绑定执行副本的大小、SHA256、argv，执行后复核副本，原稿并发变化单列。

Windows虚拟环境的嵌套入口使用底层解释器的实际argv，并保留虚拟环境身份和父进程校验。请求argv与实际argv分别记录；失败的前两版ZIP及回归证据保留，最终验收只绑定最终ZIP。

| 正式实验组 | 状态 | retained / raw / selected J |
| --- | --- | --- |
| H180_BASE_baseline | PASS | [2758, 180] / [2758, 180] / [2758, 180] |
| H180_BASE_improved | PASS | [2758, 180] / [2806, 180] / [2806, 180] |
| H180_IMP_baseline | PASS | [3000, 180] / [2814, 180] / [3000, 180] |
| H180_IMP_improved | PASS | [3000, 180] / [3000, 180] / [3000, 180] |

BASE 配对 selected 主分增加48，覆盖仍180。IMP/baseline 的 raw2814 被保护为 selected3000。配对使用相同冻结起点、产品、计分和选择规则；合法平局保留原方案。包内独立可运行性复测不计为正式科学重复。

末轮使用新绑定 58692dbe558b4ee98ebcb1810c99a07b，四次实时原生决策合计 27.472779 秒，低于原定80秒。词法声明复用与证明索引优化保留实时原生检查；宿主显式采用进程级HighQoS，同机另一任务继续保留。实际63分支、80/600秒预算和正式调用记录均在审计包。正式请求提交、消费、分发和回执确认各1次；终态后该绑定不可重放。

旧100个部署产品文件中92个与科学 Git blob 完全相同，8个 examples/synthetic CSV 仅CRLF转LF；科学Python与H180输入相同。宿主性能修复仅用于准入/执行控制，实际部署身份、原生权限检查、每次新epoch、56动作/63分支、四次决策和80/600秒预算的结果在审计包 attempts/ 与 FINAL_ACCEPTANCE.json 中；保留所有失败，不重放已消费请求。

最终ZIP另在全新中文/空格目录及干净Windows CPython3.11环境验证。验收覆盖离线依赖、上传还原、合成和H180生产→独立评价→recheck、非法自报分、历史篡改、固定资产保护及完整回归。实际测试数量、日志、退出、计时绑定该ZIP的字节/SHA256，见包外 FINAL_ACCEPTANCE.json 与审计包 validation/final/ACCEPTANCE.json；本说明不提前认证未运行检查。

upload/、UPLOAD_LIST.csv、UPLOAD_BATCHES.md、FAMOU_START_PROMPT.txt 供百度公有云测试。先按清单上传全部文件，再粘贴开场Prompt；ZIP为本地交付载体。平台规则以用户实际页面为准，详见 famou/PLATFORM_GUIDE.md。上传还原不依赖原机盘符、本地审计宿主或受保护密钥。

本轮实际系统范围为 Windows CPython3.11，离线wheel适用于该平台。POSIX、其他Python和百度端未实测；百度端状态固定为“待用户在百度伐谋测试”。H180为180目标、10站、24小时冻结实例；六天、10000目标、官方评分、现场验收不扩为本轮门槛。

AUDIT_PACKAGE.zip 保存历史包、新尝试、正式证据、性能计时、修复差异和最终包验证；包内manifest排除自身，ZIP哈希放包外回执。程序accept不代表用户本人签收。整体状态只能以真实门槛计算得到，缺项时仍交付审计ZIP并标明PARTIAL。
