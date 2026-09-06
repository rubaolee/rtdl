# 严格审查：主 AI 的 post-Goal5851 最终整改行动计划

日期：2026-09-06。审查对象为计划，不是整改完成报告。

**结论：有条件接受核心路线；发现 P0=0、P1=0、P2=4、P3=0。四处问题需要明确修正后再将其定为唯一执行合同。R0 的只读盘点和 R1 的范围裁决可以推进，无须等待新实验，也不需要重新争论已经澄清的科学问题。** 本审查不关闭任何实际改稿、artifact 或投稿门。

这里的“严厉”体现为要求可验证的执行和准确的事实，不把摘要未重复的继承要求、尚未执行的计划任务，虚报成新的严重缺陷。

## 1. 审查快照与方法

全文阅读 [主 AI 行动计划][action]，773 行、40,074 bytes，SHA-256：

`6c3b1722b07a6e13d664a3f448f5d70ab1ac80fbe8bd413f94ff4b1d05a25136`。

当前 HEAD 为 `04bd1d54f4641f12b6cf8e19a9e9eef5767a2021`，tree 为 `06966bf16ea8ab1a2e8027543d8c00985c7389a6`。行动计划引用的三份主要输入 hash 均与当前文件一致：

| 输入 | SHA-256 |
| --- | --- |
| Codex 独立审查 | `83ed4c27b95fffdbcddce1fcd8193dcfd594ef3647cd895feb036f2de2094fed` |
| Claude 审查 | `f27bd7422a21015c3387c154de1d44507fb02c0a244b67d55a7a462fc5b3bdc9` |
| 先前整改执行计划 | `1be752a1026b5a499bd666f06e368977155dd2a065d8c316b153a1614cec6fdd` |

对照范围包括 [先前整改计划][previous]、[意见吸收记录][absorption]、[Goal5852–5856 控制流程][sprint]、原 Goal5848 receipt 合同和此前已核实的 runtime/worker 边界，以及 Goal5838 的实际选中 authority。并行只读复核分别覆盖科学语义、artifact 执行和架构主张。

本次没有重新运行 GPU、完整归档重算或测试。数字判断引用此前完成的 raw 复核并逐表对照，没有把本次读报告说成一次新实验。当前三份 memory 修改和其他未跟踪审查文件均在本次开始前存在；本次只新增本审查报告。

## 2. 四个必须修正的问题

### P2-1：最终 F 与实际成功演练之间，缺少直接的字节绑定验收

**位置：**[R5 第 548 行][f-test] 要求在记录 F 前运行检查；第 535 行记录 clean/dirty classification；[R2 第 405–414 行][rehearsal] 要求成功演练，但没有在本地操作条款中明确这次演练必须从已提交 F 的干净 checkout 启动。

**风险：**执行者可以在含未提交依赖的当前工作区完成测试和封包，再提交 F，只分别勾选“演练通过”和“F 已提交”。公开 verifier 即便能单独运行，也不证明 exporter、封包依赖和生成模板能够从 F 重建。这样冻结的对象与实际验证的对象可能不同。

第 710–713 行确实继承了 [原计划的 fresh-F 要求][fresh-f]，所以这不是证据表明作者已经撤销该要求，也不是一个已经发生的源码错配。本问题是最终操作 gate 未把继承要求落实为不能拆开的验收步骤。

**最小修正：**在 R5 acceptance 增加：

> 提交候选 F 后，从其全新干净 checkout，使用仓库外新输出目录，完整执行 R2 的匿名导出、两次确定性封包和陌生目录离线验证。记录 F commit/tree、exporter/verifier/template hashes、实际命令及 checkout 前后状态。随后任何工具字节变化均产生 F2，并使相关演练失效，必须重做受影响检查。

第 580 行允许不能 push 时记录原因和 recovery bundle，也应在此说明：原因记录本身不能代替可恢复性；若采用 bundle，须实际核对 bundle hash、Git 对象完整性，并从该 bundle 恢复同一个 F 完成演练。该替代路径应明确列为处置决定，而不是一句理由自动满足 push gate。

**完成标准：**freeze 记录中的 F、实际生成包的工具、包内 verifier 三者 hash 可对应；复核者能从记录的 F 或已验证 recovery bundle 重建结果。原多 AI 工作区的 scratch 可以保留，无须删除它们来制造 clean。

### P2-2：冻结模板目录与生成输出目录混用，和拒绝覆盖要求发生歧义

**位置：**[R2 第 346–352 行][output-contract] 将 `paper/cgo2027/artifact_post_goal5851/verify.py` 列为需提交的工具，并要求拒绝覆盖；[R6 第 588–589 行][staging] 又把同一目录称为新的 staging root。

**风险：**R2 完成后这个目录已经存在且含冻结源码。若 exporter 拒绝已有输出根，R6 按字面调用会失败；若为了让 R6 成功而放宽覆盖，就可能修改冻结模板、污染 F 或覆盖先前输出。

**这项歧义也存在于我先前计划的目录安排中。** 它是本次对共同执行方案的补充纠正，不能把全部责任归给主 AI，也不能借此宣称主 AI 没有采纳先前方案。

**最小修正：**明确两个不同职责：

- 仓库中的 `/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/artifact_post_goal5851/` 是冻结模板／工具源码根，只读。
- 每次导出使用一个显式、尚不存在的仓库外输出根；exporter 创建该根后复制冻结 verifier，生成 data、文档和 manifest。两次确定性构建使用两个不同的新根。

可以先创建一个临时父目录，然后把尚不存在的 `package-a`／`package-b` 子目录作为输出；不要把已经创建的父目录本身传给“拒绝已有输出根”的接口。实际 CLI 由 R2 明确定义并记录，不在本审查中假设尚未实现的参数已经可用。

**完成标准：**两个新输出根构建成功且归档相同；再次使用已有输出根被拒绝；模板和原 raw 的 hashes 前后不变；fresh F checkout 构建前后保持 clean。

### P2-3：生命周期 fallback 可能把必须留在主文的不利证据全部移走

**位置：**[风险表第 723 行][fallback] 允许移除 main evaluation 中的 first-result numbers，仅在获准后放入 supplement。它与 [R4 第 489–490、519 行][main-adverse] 的正文可见要求，以及明确继承的 [原计划第 164 行][adverse-floor] 不一致。

**风险：**最终压页或回复审查时，执行者可以留下 prepared 主表，将全部首结果数字和不利方向转移到不要求 reviewer 阅读的 supplement。这样虽然没有删除 raw，却削弱了当前方案已承诺的主文披露。`if approved` 没说明谁能撤销哪些最低披露要求。

**最小修正：**第 723 行应明确：可以移动完整表格、数组和详细分解，主文至少保留以下事实：

- post-import 方向不利，最大正式 diagnostic block ratio 为 **2.377129x**；
- 相对 E，四组中位数的首结果回退：entry 约 **8%–22%**，post-import 约 **16%–31%**；这些是派生非 gating 观察；
- 主端点在观察旧失败后更换，两个端点均受生命周期／依赖初始化影响，不能解释为内在语言成本。

这不强迫正文保留大表。若决定进一步删除整个生命周期讨论，应形成明确的主张删除及 reviewer disposition，而不是让表中的 fallback 默默覆盖正文最低披露要求。

**完成标准：**最终 PDF 的主文可直接找到上述最小披露；完整数组仍在 supplement/artifact；摘要和结论不能借删表恢复启动 parity、速度优势或无回归的暗示。

### P2-4：把 eligible candidate 误写成实际 selected topology

**位置：**[R3 第 455–456 行][wrong-selection] 为解释十行分母，写了 `the selected any-hit terminate route`。

**源码／authority 事实：**[Goal5838 FINAL_AUTHORITY.json 第 101 行][selected] 的实际选中项为：

`builtin_sphere::any_hit_count_continue_u64_per_query`。

用于反驳九行分母的是**候选** `builtin_round_linear_curve::any_hit_terminate_bool_per_query`；[前次 exact-source 仲裁][denominator] 比较旧 curve closest-hit 与这个 eligible candidate 的 any-hit+terminate。该候选不是实际被选中的 sphere count-continue。

**最小修正：**把 selected 改为 `eligible candidate curve any-hit-terminate`；另加一句实际 selected topology 的完整 ID。十行分母结论保留。

**完成标准：**正文、勘误和 ledger 都明确区分 candidate-domain exclusion 与实际 selection；不会把 curve terminate 写成那次 prospective GPU 成功的拓扑。

## 3. 对报告末尾六个问题的直接答复

| 问题 | 本次裁决 |
| --- | --- |
| Q1：两部分 receipt 判决是否准确，能否保留有限 prepared 观察？ | **可以，有条件。** 保留“未观察到正式错误 GPU 输出”和“原逐执行 receipt 要求未履行”两个不同判断；性能只能按已披露实际检查范围解释。新的范围裁决不能修改旧 authority 或补造 receipts。 |
| Q2：A/D 与生命周期表分开是否合适？ | **合适。** 不是唯一合法版式，但更保守且没有改动数据／gate。可以移走大表，须按 P2-3 保留主文最低不利披露。 |
| Q3：double-fault／native-fork 可否通过缩范围处理？ | **可以用于本次有限投稿范围。** 缺陷仍未修复；不能写成全生命周期 fail-closed、全部清理保留根因或所有 native fork 均拒绝。没有理由因此修改 d653 后沿用旧 timing。 |
| Q4：最小离线 exporter/verifier 是否适当？ | **适当。** 复用现有 formal validators 与 deterministic packaging；补最小投影和独立数值 replay。P2-1/2 必须在 R2/R5 前解决；不开发通用 full-authority 路径恢复系统。 |
| Q5：D1–D5 是否存在未获解释的科学冲突？ | **未发现。** D1/D5 是明确声明的更保守论文范围；D2 是观测与合规性分离；D3/D4 主要是展开既有要求，不能包装成新科学证据。无需强迫恢复正向 entry claim。 |
| Q6：是否仍包含广泛 lowering／人类／普遍正确性等过述？ | **未发现计划中央叙述存在这些新过述。** R3 的 selected/candidate 事实错误必须修正；最终正文仍要按继承的完整 ledger 验收，不能把计划措辞正确等同于现稿已经正确。 |

## 4. 明确接受的部分，不应重复列为缺陷

1. **Receipt 缺口被真正接受。** 第 122–124、323–327 行明确原要求 false；没有把另一轮 diagnostic 当逐样本证明，也没有把 mock 变成实际 GPU 错误。
2. **数值与分母正确。** 四组 A/D、A/C、A/E 表与已审 raw 一致；160 workers、20,480 steady samples、32 个 A/D blocks 没有混淆。此处不是本次又重跑了 raw。
3. **整数 estimator 和原 gate 没被删除。** 第 710–713 行明确继承旧计划；整数 median、ppm 舍入、A/D 无 worst gate、A/E 仅 steady gate 等约束仍有效。不能因为本文件没再完整抄一遍公式而判其改了统计方法。
4. **冻结前成功 E2E 已存在。** 第 405–418 行明确要求 raw→匿名→封包→陌生目录验证。P2-1 要求将它绑定最终 F，不是指责它根本没安排成功路径。
5. **M/F 与原件／派生件分开。** 没有要求更改测量实现、重封旧 authority、再租 GPU 或开发完整 relocation。原始证据仍保留，匿名包有新身份。
6. **实际完成状态没有虚报。** 报告开头明示 `PLAN_FOR_REVIEW__REMEDIATION_NOT_YET_EXECUTED`；不能把“论文还没改、包还没生成”本身列为这份计划造假的证据。
7. **最终字节审查和匿名检查仍是 gate。** R7/第 745–746 行要求两份实际最终审查；R8 区分 package-ready 与 submitted。review 不可用时，pending 或作者承担风险的决定不等于门槛已通过。

## 5. 执行前应写清的两项解释，不另计 finding

**授权解释。** 第 772 行的 `Review acceptance ... authorizes execution` 应理解为：在用户既有授权范围内接受执行方案。审查者的技术接受不自行授权对外发信、上传或修改旧 claim flags。原计划相关限制已被继承，不需要由此额外创建重复审批门。

**范围量词。** 第 80 行的 `task-tuned workloads` 建议改成“implementation tuned on two frozen workloads”；调优的是实现，工作负载未改。`1.076852–1.175066x` 是四个 task×GPU 中位数的总范围，应避免读成每台 GPU 都出现两个端点。第 732 行也应按 R2 的明确 M/E 分工解释，不能把 predecessor E 或历史失败都写成运行于 M。

## 6. 最小返修清单及最终判决

主 AI 不需要重写整份行动计划，修改以下四处即可：

| 修改 | 验收位置 | 通过标准 |
| --- | --- | --- |
| F 后 clean-checkout 演练与 hash 绑定 | R2/R5 | exporter、模板、包内 verifier 与最终 F 同字节；变化后相关演练失效 |
| 模板根／生成根分离 | R2/R6 | 新输出可构建，旧输出拒绝，模板不变 |
| fallback 的主文披露下限 | R4／风险表／R8 | 最终 PDF 主文保留不利方向、最大 block、A/E 回退及端点限制 |
| selected 改为 candidate | R3／Goal5838 ledger | sphere count-continue 是 selected；curve terminate 只是 eligible candidate |

**最终判决：核心方案通过审查，四个 P2 修正后定版。允许在既有任务授权范围内推进 R0/R1；R2/R5/R6 和最终主文验收必须采用上述修正，不能照模糊条款分别打勾。** 不发现需要增加生产代码修复、新应用或新 GPU 实验才能让这份方案成立的 P0/P1。

本次只审查方案；原始实现、历史证据、主 AI 报告和先前计划均未修改，也没有宣布整改或投稿已完成。

[action]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md
[previous]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/cgo2027_post_goal5851_remediation_execution_plan_20260906.md
[absorption]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_claude_post_goal5851_review_absorption_20260906.md
[sprint]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/cgo2027_final_sprint_goals_20260905.md:117
[f-test]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md:548
[rehearsal]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md:405
[fresh-f]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/cgo2027_post_goal5851_remediation_execution_plan_20260906.md:284
[output-contract]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md:346
[staging]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md:588
[fallback]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md:723
[main-adverse]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md:489
[adverse-floor]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/cgo2027_post_goal5851_remediation_execution_plan_20260906.md:164
[wrong-selection]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md:455
[selected]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5838_generic_core_exam_20260902/FINAL_AUTHORITY.json:101
[denominator]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_claude_cgo_adjudication_20260905.md:175
