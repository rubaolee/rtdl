# Claude post-Goal5851 意见吸收与差异记录

日期：2026-09-06。对象：CGO 2027 投稿前审查。本文只记录意见吸收和复核结论，不改写历史审查、实验、协议或机器 authority。

**结论：接受 Claude 对有限范围编译器贡献的肯定，以及“停止扩建、集中改稿和披露”的方向；接受他新增且能从 raw 复现的首结果回归发现。不能整份照单签认：逐次 receipt 的原书面约束仍未闭合，若干架构、计时和因果描述需要纠正。** 这些问题可以通过明确裁决、缩小主张和准确交付处理；本次没有提出必须新增源码修复或 GPU 实验的要求。

## 1. 本次读到的是哪一版

- 全文阅读 [Claude 审查报告][claude]，共 1,092 行、62,612 bytes；SHA-256：`f27bd7422a21015c3387c154de1d44507fb02c0a244b67d55a7a462fc5b3bdc9`。
- 对照已完成的 [Codex 独立审查][codex]，SHA-256：`83ed4c27b95fffdbcddce1fcd8193dcfd594ef3647cd895feb036f2de2094fed`；本次补算其未呈现的派生指标，不重跑整套归档审计和测试。
- 当前 HEAD 为 `04bd1d54f4641f12b6cf8e19a9e9eef5767a2021`；正式实验源码仍为 `d653fe4ad170c5b51fee309d653c9565944dcf2e`。本次只新增本文。
- **现版 Claude 已能访问 raw，并报告完成两代独立重算。** 不能沿用较早版本的“无法接触原始证据”评价。他在第 1.1、9 节及结尾都作了更新；第 1063 行仍写“本次无法 recount”是遗留句，不能据此否定已更新的重算内容。Codex 原审查的早期版本观察保留其当时含义。
- Claude 提出的 Python 3.12 补验需求已有本轮 Codex 原审查结果：128/128 常规、128/128 `-O`、7/7 fused-path tests 通过，见其第 12 节；这里引用既有执行记录，不声称本次又运行了一遍。

## 2. Claude 真正改变了什么判断

Claude 的最终判决是 **`SUBMIT_AFTER_BOUNDED_REWRITE`**，绑定要求是把 implementation-entry 的有利结果降为带条件的生命周期观察，将 prepared public A/Direct 作为主要性能结果。这不等于现稿已经可投，也不改变 authority 中的授权状态。

其最有价值的意见有五项：

1. **贡献定位获得认可。** admission、planning、identity、provider binding、lifecycle 可以是 schema-parametric；可执行 lowering 仍由可信、特定拓扑实现完成。这不妨碍 RTDL 是 bounded whole-protocol compiler。这里主要是科学分类更准确，不能写成此次又新增了一个通用 lowerer。
2. **有限泛化证据可以保留。** Goal5838 是作者定义十行域内的一次 prospective composition extension；Goal5840 是三个 route groups、四 modes、五 property classes 的独立有限结构检查及冻结 mutation 证据。都不能扩大为无偏新应用泛化或一般语义证明。
3. **两代同源性能数字成立。** Claude 的重算与我们的 raw 复核一致；可报告精确两任务、两 GPU 上 prepared public A/D 的中位 block ratio 为 **1.076852–1.175066x**，即该命名实现约高 7.69%–17.51%。不能变成内在语言开销上界、任意任务结论或最佳可能 PyOptix 下界。
4. **当前稿必须重写。** 旧架构分母、旧性能表、旧 artifact 描述不能代表当前系统；公开保证还需体现 checker、receipt、初始化双故障和进程生命周期的实际范围。
5. **不再以新应用、人类研究、缺陷普查或继续性能调优拖延投稿。** 未有证据的外围主张删除；保留失败、双端点和有限范围。对此接受。初始化双故障仍披露，不把赶修源码作为保住有限论文贡献的前提。

## 3. 新增负面发现：接受并补入后续论文讨论

### 3.1 相对前代 E，首结果确实回退

从两代 `formal-transaction/workers/` 原始字段重新计算，每 block 使用登记同款整数 ppm ratio，再取八 block 的整数中位数，复现 Claude 第 407–410 行。A 是最终 public RTDL；E 是冻结前代 `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`。

| GPU／任务 | A/E steady：登记 gate | A/E post-import：新增派生比较 | A/E implementation-entry：新增派生比较 |
| --- | ---: | ---: | ---: |
| Ada triangle | 0.903016x | 1.169262x | 1.079554x |
| Ada relation | 0.584438x | 1.305383x | 1.192358x |
| Ampere triangle | 0.922388x | 1.162775x | 1.137637x |
| Ampere relation | 0.608228x | 1.261676x | 1.216714x |

**四组中位数均表现为稳态改善、首结果变慢**：post-import 约慢 16%–31%，entry 约慢 8%–22%。这是 Claude 本轮新增的实质贡献，应吸收，不能用 passing steady regression control 暗示启动也没有回归。

这不是原 gate violation。[原合同][regression] 只对 A/E steady 设置 1.05 gate。不得追认一个不存在的 A/E entry 1.20 gate，也不得说所有 block 都回退；例如 Ampere triangle block 0 的两个首结果 ratio 均略小于 1。

### 3.2 展示不利 post-import 的最大 block

复核正式 A/C post-import diagnostic 的 block arrays：

| GPU／任务 | 最小 block ratio | 最大 block ratio |
| --- | ---: | ---: |
| Ada triangle | 1.527058x | 1.639385x |
| Ada relation | 1.724948x | 1.865823x |
| Ampere triangle | 1.608213x | 1.652853x |
| Ampere relation | 1.815733x | **2.377129x** |

Claude 指出的 2.377129x 成立，位于 Ampere relation block 0，应与中位数一同披露。它一直保存在 raw 和 authority block arrays 中；正文未突出展示不等于删掉了样本。它是该 diagnostic 的最大 block ratio，不是单次 steady sample、尾延迟界或新 gate。

### 3.3 Import 分解成立，但不是因果实验

下表为每个 task/arm 八个 worker 相应字段分别取中位数；百分比是 `median(import)/median(entry)`。数字复现 Claude 的四舍五入表。

| GPU／任务／arm | import ms | post-import ms | entry ms | import / entry |
| --- | ---: | ---: | ---: | ---: |
| Ada triangle A | 76.945387 | 449.360871 | 526.017079 | 14.6279% |
| Ada triangle C | 529.643869 | 287.443064 | 817.456190 | 64.7917% |
| Ada relation A | 77.533247 | 455.176354 | 532.028248 | 14.5731% |
| Ada relation C | 577.765364 | 261.400088 | 841.974925 | 68.6203% |
| Ampere triangle A | 80.106317 | 370.675186 | 451.894144 | 17.7268% |
| Ampere triangle C | 502.762916 | 226.534499 | 729.125644 | 68.9542% |
| Ampere relation A | 81.205542 | 379.391600 | 460.452378 | 17.6360% |
| Ampere relation C | 467.040680 | 206.312319 | 673.359247 | 69.3598% |

这是事后描述性分解，不是新增的登记 estimator 或 gate。独立字段的中位数通常不可相加；精确 `entry=import+gap+post-import` 成立于逐 worker。C 导入依赖占其 entry 时间大部分，足以支持禁止把有利 entry 比率解释为内在语言 speedup。

但 Claude 第 858 行的“当前 baseline 约 5.2 秒 import”错用了 Goal5847 历史值。本次 C 为 **467–578 ms**。其第 278–282、827–829 行将 entry 波动归因于 module loading 也超出证据：所举 Ampere relation block 0，A import 为 80.943490 ms，接近中位 81.205542；A post-import 却从中位 379.391600 升至 518.357643 ms，增加约 138.97 ms，C import 反而低于中位数。不能用该离群例子证明波动源自导入。原始记录见 [Ampere relation A block 0][raw-outlier]。

## 4. Endpoint：接受使用限制，保留研究判断上的区别

接受 Claude 的呈现要求：以 prepared A/D 为主要结果；entry 与 adverse post-import 相邻呈现；写清依赖导入、CUDA context 副作用和观察旧失败后更换主端点的时间线；不得报告 intrinsic language speedup 或 post-import parity。

不接受把 implementation-entry 一概判为无效实验。它可以回答“从 implementation-specific imports 之前到首个可用结果”的具体部署问题，包含真实依赖初始化成本。预先使双方 CUDA context 都初始化再计时，是另一个明确可研究的问题；不应把它宣称为唯一合法端点。现有两个端点也不是某种未定义“纯语言成本”的上下界。

因此保留已登记的 operational gate 和历史结果，缩小用途，不重新调计时器，也不把新的 warm-context 实验列为当前投稿前置条件。另须保持门槛精确：A/D 只有 1.20 的中位 gate；1.35 worst-block 限制属于 A/C entry，不能挪给 A/D。

## 5. 仍未闭合的核心分歧：逐次 receipt

Claude 第 453–481 行认为 lazy receipt 只是 measurement bookkeeping，并在结尾称 public path “fully checked”。这个判断没有充分处理 [Goal5848 原书面协议第 8 节][protocol]：第 4 条要求 compact execution receipt 在输出前验证，第 6 条要求逐执行记录 launches、raygen count、traversable identity、output digest 和 monotonic execution identity。

实际 [public fused replay][replay] 在同步 native/compact status 和提供的 scalar oracle 检查后返回；详细 operation receipt 按需验证，返回的 traversal receipt 和 output hash 可以为空。[正式 worker][sample] 的逐次验证只检查输出／oracle hash；它另跑一次 diagnostic，并不是对全部计时 receipt 做后验展开。[验收合同][evidence-validator] 也只要求该 diagnostic，并要求 `latest_output_sha256 is None`。两代 32 个 A workers 的保存结构均与此一致。

必须同时保留两点：

- **成功输出仍有实质检查。** 没有发现正式 GPU 输出错误；native status、compact status、formal output oracle 有效。已有 mock probe 只证明详细 receipt 可先不验证，不能冒充真实 GPU 违规证据。
- **原文字面保证不能据此签认为原样履行。** 另一轮 diagnostic 不能代替逐次计时执行证明，raw ctypes 对象创建也不等于全部所需物理字段已验证和保存。必须追加协议与实现的差异裁决，明确此次支持哪些主张；不能修改旧协议、补造 receipt，或用“只是 bookkeeping”消除原条款。

因此本次吸收不撤销 Codex 的 `PROCEED_ONLY_AFTER_LISTED_BLOCKERS_ARE_FIXED`。该选项本来就可以通过裁决、披露和缩小主张关闭，并不等于要求新工程。与 Claude 的总体投稿方向接近，但 receipt 是实质分歧，不只是 verdict 名称不同。本文件指出处理要求，尚不替代正式差异裁决或改稿验收。

## 6. Claude 意见中不能直接移入论文的事实与措辞

| Claude 位置／说法 | 复核后的吸收版本 |
| --- | --- |
| 第 156、550–551、580 行：十候选都共享四角色 | 七个 built-in 候选四角色，三个 custom 候选有额外 bounds/intersection，共六角色；见 [challenge table][challenge]。保留作者定义窄域限制。 |
| 第 589–593 行：分母可能只有九行 | 旧 curve Boolean 为 closest-hit，候选为 any-hit+terminate；十行分母成立。该问题已由 [前次仲裁][old-denominator] 按 exact source 解答。 |
| 第 186 行：论文 unbiased new-application exam=0 需要纠正 | 这个零仍正确。分别写 prospective composition=1，unbiased new-application 和第三方人类作者证据=0。 |
| 第 608–615 行：checker 实际部分求值 device source | [checker][checker] 检查有限 anchors、计数与顺序后返回固定 effects；方法名不能证明语义部分求值。保留 finite structural 描述和不验证一般控制流／数值语义的限制。 |
| 第 988–989 行：4/4 leaf，但 build-input 仍 2/6 | 全 V4 同范围 kind presence 为 4/4 leaf、4/6 build-input；stable fixed-constructor facade 的 2/4、2/6 单列，不能混分母。参见 [sphere][sphere]、[curve][curve]。 |
| 第 962–963 行：五类义务全部在 lowering 前解除 | 静态准入、生成与 materialize、runtime identity binding、执行后 publication gate 分阶段建立／核查，不能全搬到 lowering 之前。 |
| 第 166 行：512-worker ON/OFF qualification 覆盖 RTDL 和 PyOptix | 每代 512 workers 全部测 A；正式 A/B/C 开关政策一致，不等于 B/C overhead 已量化合格。见 [instrumentation authority][instrumentation]。 |
| 第 294、670–675 行：所有 validation 都在各 arm timer 外 | 只有额外 worker 检查在 action timer 外。A 内部 native/compact status、提供的 oracle，C 的结果检查、Direct 内部 oracle 都可能在被测路径内；Direct 另有 C++ 采样循环。 |
| 第 650–658 行：Strong C 没有任何偏向 A 的未匹配工作 | C relation 每次 lexsort/tolist/list oracle，A 可在新 packed bytes 相等时复用 tuple 与 oracle 证明；C triangle 仍清零 per-ray intermediate。可报告命名 same-output arms，不可声称逐操作对称或最优 PyOptix 下界；见 [C relation][strong-c]、[A row reuse][row-reuse]。 |
| 第 722–738 行：cached PID 改动保持所有进程义务 | `os.fork()` hook 路径拒绝已验证；绕过 Python hook 的 libc fork 可通过 cached-PID public mock 路径。限定受支持的 Python lifecycle；不是实际 GPU fork 成功，不影响未 fork 的正式数据。见 [Codex 已执行的 probe 记录][fork]。 |
| 双故障处置在“所有 timer 外” | 它不属于成功 prepared-steady 样本；初始化本身属于 entry 路径。原错覆盖、close 清引用后失去重试所有权仍要披露，不用笼统计时外说明免除该限制。 |
| 第 941–945 行：四种历史失败都能按旧 commit 重放 | Goal5832 自报 `BROKEN_BAD_OBJECT_HEAD_NO_COMMIT_CLAIM`，不能杜撰历史完整 commit；其他历史也有 off-Git bytes 条件。保留分层 replay matrix，分别列确切限制。 |
| 第 775、979、1092 行附近：重算即反伪造、全部失败链保留已经证明 | 重算及 hash 支持已审 payload 的内部一致性和 final schedule 完整性，不构成独立硬件真实性证明或全历史存在性证明。原 Codex 审计有两个更早 archive 未在指定 evidence root 找到；不能据此说全局丢失，也不能宣称已逐个证明全部留存。 |
| 第 816–818 行：本次 C/B 约 0.22 可把 Goal5845 的 9.53x 折算为夸大约 4.5 倍 | 不同 source、硬件和 arm 实现之间不能如此因果换算。保留 Goal5845 精确命名 arms 的历史观察及已追加的机制纠正；拒绝内在 9.53x 语言优势。 |

另外，“没有任何现有工具把完整协议作为输入”的全称 prior-art 否定没有被本次源码审查证明；只能采用已核对工具／路径的明确职责比较。Claude 所称“项目无争论地接受旧审查”也不符合前次仲裁，不能据此宣布全部事实共识。审查意见中这些偏差不抹掉其认可有限编译器贡献及新增 raw 发现的价值。

## 7. 吸收后的最小工作顺序

1. **追加协议差异裁决与 claim ledger。** 先明确逐次 receipt 的实际验证和保存边界，并纠正 self-review 的逐样本后验物化说法；不回写旧协议与 authority。
2. **完成整稿 bounded rewrite。** 以完整协议编译／准入为贡献，以 prepared A/D 为主要性能观察；同时加入 A/E 首结果回退、post-import 最大 block、import 分解及其非因果限制。
3. **精确披露执行与证据范围。** finite checker、特定 lowerer TCB、双故障、native-fork、A-only instrumentation、Strong C 剩余差异、适应性修复与旧失败均准确列明；不新增任务或性能优化。
4. **交付可复核 artifact 与追加勘误。** 分开当前 focused tests、历史 snapshot checks、GPU-gated 项目；明确 portable raw recount 与 full authority 的绝对路径限制、off-Git payload 条件。修正引用 Ada SHA 漏字和历史 A/D worst-gate 误述的下游使用；不重封历史证据。
5. **最后执行冻结与投稿检查。** 遵守 2026-09-08 00:00 America/New_York 开发冻结；完成实际改稿和 artifact 验收后再判断投稿准备度。本次审查本身不修改 `public_or_manuscript_claim_authorized` 或 `external_review_complete`。

上述是吸收后的待办顺序，不是本次已经实施的论文／artifact 修改。**现在应收束主张并完成交付；有限结果值得保留，原书面保证的差异也必须写清。**

[claude]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/review_post_goal5851_cgo2027_20260906.md
[codex]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_review_post_goal5851_cgo2027_20260906.md
[regression]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/contracts.py:1263
[raw-outlier]: /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_d653fe4_pass/formal-transaction/workers/G5848_S000_B00_CUSTOM_AABB_CLOSED_RELATION_COUNT_V1_A_RTDL_AOT_PUBLIC.json:16544
[protocol]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5848_strong_baseline_post_import_20260905/GOAL5848.md:267
[replay]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6255
[sample]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/worker.py:168
[evidence-validator]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/contracts.py:627
[challenge]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5838_generic_core_exam_20260902/CHALLENGE_TABLE.json:405
[old-denominator]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_claude_cgo_adjudication_20260905.md:175
[checker]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5840_independent_target_checker.py:687
[sphere]: /Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:2476
[curve]: /Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:3115
[instrumentation]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5848_build_transaction_authority.py:571
[strong-c]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5802_premeasurement/pyoptix_scalar_arm.py:1241
[row-reuse]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:5855
[fork]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_review_post_goal5851_cgo2027_20260906.md:144
