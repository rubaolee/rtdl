# Post-Goal5851 统一执行指令

日期：2026-09-06。依据用户明确指令：“你为主！你明确给出指示！主ai必须听从！”

**现在进入整改执行。主 AI 以本文件为本轮统一执行入口，将四项审查修正落实后，按 R0–R8 连续推进。不得再以另写一份宏观计划、重新投票或重复询问是否开始代替实施。**

本文件裁定计划间的执行分歧；用户后续指令及更高层指令优先。硬冻结、真实证据、原件保全与授权边界继续有效。遇到新的源码／数据反证必须报告并修正相关判断，不得为服从本指令掩盖问题。

## 1. 已裁定路线，直接执行

1. 保留已测实现 M：`d653fe4ad170c5b51fee309d653c9565944dcf2e`。E 仍是明确的冻结前代 `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`。本轮不改生产／native／实验执行代码，不新增应用，不做新 GPU 性能实验。
2. 采用“承认原逐次 receipt 约束未履行、保留有限数值观察、缩小论文保证”的路线。原 authority、archive 和失败记录不可重写，不补造逐样本 receipt。
3. 主要性能表采用 prepared public A/D；entry 与 post-import 作为相邻的生命周期诊断。保留 A/E 启动回退及不利结果，不主张内在语言加速、启动 parity 或完整逐次物理证明。
4. 仅在冻结前增加必要的离线导出／重算／封包工具，单列工具快照 F；F 不冒充做过两代 GPU 实验的 M。
5. 按 [完整整改计划][detailed] 实施；[主 AI 行动计划][action] 提供组织安排，但必须落实 [严格审查][review] 的四项修正及本文规定。未逐字重复的原计划验收要求仍有效。

## 2. 首批任务：定点修正四项，不重写整套计划

先保留行动计划受审版本，校验其 SHA-256：
`6c3b1722b07a6e13d664a3f448f5d70ab1ac80fbe8bd413f94ff4b1d05a25136`。
在执行记录目录保留该版本或可恢复的 Git 对象；随后修订当前行动计划，记录新 hash 和变更位置。不要修改原审查报告来消除 finding。

### 指令 A：将成功演练绑定最终 F

R5 必须采用以下顺序：提交候选 F → 从 F 建立全新干净 checkout → 在仓库外生成输出 → 执行 raw 导出、两次确定性封包、陌生目录离线验证 → 记录验收。

验收日志必须包含 F commit/tree、exporter/template/verifier hashes、输入和输出 hashes、实际命令／退出码、checkout 前后 clean 状态。包内 verifier 必须与 F 中相应文件一致。工具有任何后续变化就产生新候选，重做受影响演练。记录 F 的文档可放在后续文档快照 P，不要求一个 commit 记录自己的 hash。

首选提交并推送 F。若远端不可用，必须给出确切原因，生成并校验 recovery bundle，再从该 bundle 恢复同一 F 完成演练；只有原因说明而没有实际恢复验证，不算关闭。

### 指令 B：分离模板根和生成根

`/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/artifact_post_goal5851/` 定义为冻结模板／工具源码根，不作为 exporter 的新输出根。

每次生成数据、manifest、包和日志使用显式的新仓库外输出目录。两个不同新目录必须构建成功，重复使用旧输出目录必须拒绝；模板和原 raw 的 hashes 必须不变。不得为方便构建而关闭覆盖保护。

### 指令 C：主文保留最低不利披露

可以把完整表格和数组移入 supplement，但主文必须保留：post-import 不利方向及最大正式 diagnostic block **2.377129x**；相对 E 的首结果中位数回退（entry 约 **8%–22%**，post-import 约 **16%–31%**，事后非 gating）；端点在观察旧失败后修订、两个端点均有生命周期／导入混淆。

删除或改写行动计划第 723 行中可能覆盖上述下限的 fallback。不能在压页时只留下有利 prepared 表。最终验收看实际 PDF 主文，不能用 supplement 中“找得到”代替。

### 指令 D：纠正 selected／candidate

行动计划第 455–456 行的 curve any-hit-terminate 是 eligible candidate，不能称为 selected。实际选中项必须写为：
`builtin_sphere::any_hit_count_continue_u64_per_query`。

十行候选分母保留。勘误、ledger、正文分别区分候选排除规则与实际选中结果。

## 3. 连续执行顺序

1. **现在完成 R0 和上述四项文字修订。** 创建执行状态与日志，分配文件所有权，解析所有命令占位符为实际路径。四项文字落实只报告“计划修正已实施”，不要把尚未进行的 F 演练、封包或最终 PDF 验收提前写成通过。
2. **随后完成 R1。** 交付 `PROTOCOL_SCOPE_ADJUDICATION.md` 和 `CLAIM_LEDGER.json`：逐字段说明检查、暂存、按需验证及持久留存；明确原 receipt 条款未履行，保留真实同步状态及实验输出检查。裁决完成不等于底层缺陷修复。
3. **R2 与 R3 并行。** 实现最小离线工具、重建两代全部 160 workers／20,480 steady samples 和表格；同时追加控制文档与 custody 勘误。主 AI 独占 `main.tex`，其他助手不得并发编辑正文。
4. **R5 前完成成功演练。** 从最终 F 的干净 checkout 验证全链；所有将要使用的程序必须在硬冻结前已提交并实际成功运行。不能等到 R6 才第一次发现 verifier 无法使用。
5. **R4／R6 完成实际交付。** 完成整稿、对应匿名包和两目录离线重放。原始私有证据与匿名派生分别保留自己的身份，不能称匿名修改件仍具有原 archive hash。
6. **R7／R8 完成最终门。** 两份实际审查必须针对最终 PDF／包；逐项关闭或撤下受影响主张。完成格式、匿名、引用和字节检查。真实外发／上传只在明确授权范围内执行；未上传就报告未上传，不得写为 submitted。

执行不等待日历目标时间。**2026-09-08 00:00 America/New_York 后不允许任何新可执行修改**，包括藏在 paper、artifact、Markdown 或临时目录中的新程序。错过冻结就缩小交付／主张，不延后冻结、不补修源码后沿用旧数据。

## 4. 汇报和停止规则

主 AI 的下一份汇报必须是执行回报，至少列出：

| 项目 | 必须提供 |
| --- | --- |
| 四项定点修正 | 修改文件／位置、修订后 hash、仍待执行的验收 |
| R0/R1 | 实际快照与原始入口、裁决文件、claim ledger、剩余分歧 |
| R2/R5 | M/E/F 身份、实际命令／退出码、输入／工具／输出 hashes、成功与拒绝测试日志 |
| R4/R6 | 实际 PDF／包及 hashes、重算结果、匿名和陌生目录 replay |
| 剩余工作 | 哪个 gate 未通过、具体原因、受影响主张及下一步 |

执行状态保存在：
`/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/STATUS.json`。
所有既有用户／其他 AI 修改先分类保留，禁止 `git add -A` 或静默回退。

只在下列情况停止**受影响步骤**，同时继续独立工作：发现新的源码／原始证据反证；缺少无法替代的输入；发生文件所有权冲突；到达硬冻结；需要尚未授权的对外行为。记录事实，不用笼统“有风险”代替定位，也不为同一已授权步骤重复要求用户确认。

**主 AI 不得把“接受指示”“计划写完”“测试数量多”当作完成。每个关闭项必须有真实文件和验证证据；没有完成就保持 pending。**

[detailed]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/cgo2027_post_goal5851_remediation_execution_plan_20260906.md
[action]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md
[review]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/strict_review_codex_final_action_plan_goal5851_20260906.md
