# RTDL CGO 2027：审查邀请、Claude 意见与 Codex 仲裁的独立复核

日期：2026-09-06，America/New_York。审查者：Codex；另有三个并行只读子审查，属于本次内部交叉检查，不计作外部人类评审或 Claude 同意。

范围：完整阅读用户指定的三份文件，按审查邀请第 14 节组织本报告，并以实际源码、Git 对象和留存证据裁决。原 Claude 文件本身是被审对象，因此没有按邀请中的旧输出路径覆盖它；本报告单独保存。没有修改源码、实验、测试、历史证据、原审查、仲裁或论文，也没有启动 GPU、联系 Claude、创建新实验或执行修复。只读验证在内存中重算，不落盘更新 authority。

## 1. Cold-start understanding：冷启动理解与审查身份

问题不是“能否用 Python 发起光线追踪”，而是一个计算结果依赖多个回调、槽位含义、几何和 SBT 绑定、容量与状态处理，以及最终加载的程序是否一致。各局部片段能通过编译，并不保证整个协议能正确交付结果。RTDL 的可辩护贡献是把这组跨边界约束纳入同一个受限编译和运行协议：受限 Python 叶函数确实经过 IR 与代码生成；支持的拓扑则由特定的可信 lowerer 实现；公开运行路径继续执行状态和身份检查。

它没有自动选择 RT 算法，没有通用拓扑代码生成，没有证明应用正确性，也没有人类易用性证据。最强架构证据是一次预先限定域内的冻结框架扩展和一套独立实现的有限结构检查，而不是“任意回调都能编译”。最强当前性能证据是一代 GPU 上的修正生命周期实验；它不代表原 post-import 门槛已经通过。

最大威胁是把不同证据层级合并：把框架扩展写成通用 lowering，把字符串/AST 结构检查写成语义证明，把稳态门槛写进首次结果承诺，以及把一代结果写成两代完成。项目仍有可投稿的受限编译器贡献，但现有稿件和两份评审都不能直接当最终事实表。

### 1.1 精确审查快照

| 项目 | 本次观察 |
|---|---|
| 工作目录 | /Users/rl2025/rtdl_v4_restricted_python_design |
| 分支 | codex/cgo-goal5836-handoff |
| 审查开始 HEAD | 65bf05c007af426ff4d34b52552c4a21a1db074d |
| HEAD tree | 13fa25e3a2188d8d1d38e4b9da5185f17b74bed0 |
| 审查开始 git status --short | 空，干净 |
| git diff HEAD --binary 的 SHA-256 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855（空 diff） |
| 当前实验源 | c4351f6120d1d73d7c2b72ff4d61ad747061f836 |
| 实验源 tree | 1faf8ca2a99e4c1011443942479e2edf7b297edb |
| 验证 Python | /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python，3.12.14 |

HEAD 相对实验源只更改六个文档/记忆文件，没有实现差异。邀请和 Claude 的历史快照则是 5de0e7ec… 加未提交 Goal5848 内容；其“0/2、dirty WIP”在当时成立，不能用作今天的状态。原 tracked diff 的哈希也没有覆盖当时未跟踪的 cleanup test，因此不能把它称作完整 WIP 内容身份。

| 本次完整阅读的输入 | SHA-256 |
|---|---|
| [审查邀请][cfr] | 127e1c69d43263d7c89f8f39e4da203aec1f94d734d7486fa369070e1f480912 |
| [Claude 审查][claude] | 9155d8c472325bc62ef298c978294509a86e1ededa9de46a23b1254946ffbf34 |
| [Codex 仲裁][adjudication] | b36899d5ad6a9cf9766fce1eb262c8af603463171855cf49f7dd27446cb3daa3 |

另外阅读了 Mac 交接、AGENTS 当前约束、最终冲刺计划、相关先前意见、源码和证据。旧工作指南中已被完成状态覆盖的动作没有重新执行。

### 1.2 期限

官方 R2 截止为 2026-09-10，页面标示 AoE；正文上限 11 页、参考文献除外，采用匿名审稿。按本仓库更早的内部规定，2026-09-08 00:00 ET 后不得再修改实现、实验、计时器、估计量或测试，只能使用已提交工具、限缩主张和完成文稿/工件工作。本报告不把官方截止视为放宽内部冻结的理由。[官方 CFP](https://2027.cgo.org/track/cgo-2027-papers)、[内部冻结约束][freeze]。

## 2. Prior-finding closure table：前次问题关闭表

| Prior attack | Current disposition | Evidence that closes or fails to close it | Remaining blocker | Severity |
|---|---|---|---|---|
| Only two closed protocol families; generality zero | 部分关闭 | 真实 frontend/IR/lowering；Goal5838 扩展了冻结 admission/identity/lifecycle，但新增特定拓扑实现 | 明确框架参数化与拓扑特定 lowering | P1 文稿 |
| No prospective frozen-core exam | 按预注册窄范围关闭 | Goal5838 历史 authority 验证通过，十行作者定义域中抽取一次 | 不能升级成无偏新应用或通用 lowering | P1 计数/措辞 |
| No real-world protocol-defect prevalence evidence | 未关闭 | Goal5839 零分类；Goal5820 的 NOT_FOUND/UNCERTAIN 不是 bug | 删除 prevalence 主张；不临时扩展 census | P1，删主张可解决 |
| No external human author | 未关闭 | 人类外部作者、usability study 均为零 | 删除易用性/生产力比较 | P1，删主张可解决 |
| Native OptiX/OWL/PyOptix boundary unclear | 大部分关闭 | 稿件已有 typed payload 与 OWL residual 分析；baseline B/C/D/E 分工明确 | 不能照抄 Claude 的“没有任何现有工具检查”绝对断言 | P2 措辞 |
| No causal admission-cost analysis | 历史范围关闭 | Goal5842 双代 authority 本次验证通过 | 不把旧版本因果分解迁移为新版本份额 | 无新增阻断 |
| Weak/asymmetric performance baseline | 修复中 | 强 Arm C 与 Direct；Goal5850 一代成功、原 post-import 仍 adverse | 第二代同源复现；严格分开 endpoint 与 gate | P1 性能主张 |
| Application-specific logic may leak into engine | 所审 V4 路径未发现 | owner-indexed Boolean 运算与应用几何/意义分离 | fixture 边界与 legacy 包分区须清楚 | P2 |
| No independent lowering/refinement evidence | 有限结构范围关闭 | Goal5840 authority 验证通过，独立源码、15 个冻结 mutation | 删去独立语义求值/控制流证明含义 | P2 |
| Adverse results could be hidden by successor optimization | 留存机制与所核证据通过 | 历史性能 authority、三次失败与第四次成功分离 | 不把留存完整误当统计无偏或最优 baseline 证明 | 无新增阻断 |

## 3. Executive verdict：执行结论（九句）

1. 项目仍具备可辩护的受限 whole-protocol 编译器贡献，不应因为 lowerer 是模板实现就否定整个编译器。
2. Claude 对冻结边界和 baseline 弱点的源码观察有价值，但三个 P0 的外推过强，仲裁对这三项的主要更正成立。
3. Goal5838 通过了它实际预注册的框架扩展目标；它没有通过未曾测试的通用 lowering 或无偏新应用目标。
4. Goal5840 的独立实现成立，但两份评审高估了其语义分析深度。
5. 应用/引擎分工基本清楚，Boolean 曲线域问题当前是以明确限缩范围处理，而不是增加了运行时几何保护。
6. Claude 建议的性能句子存在独立于版本变化的 endpoint 混用，不能进入论文。
7. Goal5850 当前只完成一代，旧 post-import 仍约 2x adverse，任何两代性能关闭或 post-import parity 结论都不成立。
8. 当前 manuscript 不可直接投稿，回放说明也尚未穷尽已知历史漂移。
9. 建议按下面最多五项行动完成投稿准备；不能完成的正面主张应删除，不能改写历史或越过冻结。

## 4. P0/P1/P2/P3 findings：精确问题与处置

分级指对当前拟投稿内容的影响；P0 不表示已发现生产代码使所有结果无效。开放项计数为 P0=1、P1=3、P2=4、P3=1；已修历史问题在后文另列，不重复计数。

### P0-1：现稿尚不能代表拟提交的证据和研究范围

位置：[main.tex:650][paper-scope]、[main.tex:934][paper-table]、[main.tex:1117][paper-perf]。现稿仍列两种叶类别、零冻结新形状测试，并以旧测量为当前评估。旧数字可以在注明版本/实验后保留，不能仅因有新版本就说它们“已无 authority”；但它们也不能证明 c4351f612 的当前表现。

**影响：** 如果直接提交，读者无法从同一稿件确定系统支持面、性能版本和泛化单位。最小修复是文稿与 claim ledger 重写；不需要实现新 lowerer。应保留依然正确的“无偏新应用测试、人类外部作者和 usability study 为零”。

### P1-1：Claude 的可发表性能句把三个不同估计对象合成一个承诺

位置：[Claude:1046][claude-performance-sentence]；实际门槛在 [contracts.py:1255][gate-steady] 和 [contracts.py:1287][gate-lifecycle]。该句从 post-import 首次正确结果讲起，随后把 C/B ≤1.05、A/D ≤1.20 和 no block >1.35 连在一起。代码中 C/B、A/D、successor/predecessor 都是 **prepared steady 的块内比值中位数**；1.35 worst-block 只约束 A/C 的主首次结果 endpoint。Direct 没有该逐块门槛。

当前后继又把主首次结果 endpoint 改为 implementation-entry，旧句因此同时在时间起点上过时。即使没有这一改动，原句也已经过度承诺。仲裁没有明确纠正这个漏洞。

**最小修复：** 分开写生命周期 A/C、稳态 A/D、baseline competence 三句，并逐句注明估计量和硬件。不得称为 Direct 首次结果 parity，不得给 Direct 附加“每块 ≤1.35”的通过结论。当前仅一代，不发布两代结果。

### P1-2：Claude 要求的两个计数修改会把正确事实改错，仲裁未充分筛除

位置：[Claude:1172][claude-counts]、[main.tex:70][paper-zero-app]、[main.tex:1115][paper-zero-app-long]。Goal5838 增加的是作者定义域内的一次 prospective topology composition；不是 prospective unbiased new-application exam。因此后两处“零”不应直接改成“一”。应另增拓扑测试计数，更新真正过时的 frozen-core new-shape transfer 行。

同一建议称 build-input kinds 仍为 2/6，也是错误的当前全 V4 分母。原生实现明确分别设置 TRIANGLES、CUSTOM_PRIMITIVES、SPHERES、CURVES，见 [native:1905][native-triangle]、[native:6016][native-custom]、[native:2476][native-sphere]、[native:3115][native-curve]。按同一 pinned 六枚举口径，全 V4 有四种 build-input enum 的受限实例；只有限定到旧 stable-v4 两固定构造器时才可说两种。四类 leaf 的存在也不意味着所有 curve 变体、配置或层次都支持。

**最小修复：** 用五个独立量：全 V4 受限 build-input presence 4/6；leaf-kind presence 4/4；stable fixed constructors 2；prospective bounded topology exam 1；unbiased new-application exam 0。不相加、不换单位。

### P1-3：历史回放指南尚未关闭 current-tree 验证问题

位置：[KNOWN_STALE_CUSTODY_CHECKS.md:113][custody-guide]；[Goal5837 verifier][g5837-verifier]；[Goal5843 contracts:559][g5843-prereg-compare]。本次实际执行又发现两条指南未列出的失败：

| 当前命令 | 本次结果 | 已核实原因与边界 |
|---|---|---|
| scripts/goal5837_freeze_owner_grouped_classification.py --verify-stored | AUTHORITY_CURRENT_INPUT_MISMATCH | historical_validator_context.current_root_identity 绑定的 __init__.py 从 319,859 字节变为 320,213；旧 hash 在 2caa73b5… 和 0f5c9d42… Git 对象可找到 |
| scripts/goal5843_build_final_authority.py --verify-stored | preregistration differs from canonical builder | builder 读取当前源；45 个冻结 source pin 对正式 c2662603… Git blob 全部匹配，当前九个文件已变；authority/preregistration/recount seal 仍匹配，pod/local recount 字节一致 |

**影响：** 按 AGENTS 的当前命令会失败，仲裁“replay guide 已修”的表述不完整。证据不支持把这称为历史科学结果失败。最小修复是补充历史 commit、当前预期失败和源重建/原字节重放的不同保证；不重封旧 authority。

Goal5850 也必须另列：本地有完整 raw archive，但完整 authority builder 绑定 /workspace 绝对路径，Mac 的 worker/gate recount 不等于完整迁址 custody replay。[当前报告:218][g5850-portability] 已披露该限制；后续 artifact 说明必须保留。

### P2-1：Goal5840 被描述成独立 partial evaluation，超过代码实际能力

位置：[Claude:885][claude-checker]、[仲裁:281][adjudication-checker]；实现：[checker:568][checker-anchors]。所谓 _bounded_partial_evaluation_effects 是从固定函数窗口检查字符串、次数和相对位置，然后返回预定 effect 映射；linked 路径又令 executable_target = generated_target（[checker:820][checker-linked]）。它不执行一般 C++ 控制流/数值语义。

本次只读内存探针在留存 bounded-relation wrapper 的 any-hit 函数开头插入无条件 return；effect 提取仍返回 accept_continue，wrapper status-flow 检查仍通过。这只证明两个结构谓词没有可达性/支配性检查；**没有构造完整重封 authority 绕过，没有运行修改后的 GPU 程序，也没有推翻已冻结的 15 个 mutation 结果**。

**最小修复：** 写“对编译器已特化/部分求值输出的独立有限结构检查”，明确不覆盖控制流可达性、完整数值语义或 binary correctness。官方 bounded structural claim 可保留；无需在冲刺期扩建 checker。

### P2-2：仲裁的 collision “locally repaired”只能指主张限缩

位置：[仲裁:112][adjudication-domain]、[Boolean admission:917][boolean-guard]、[case-study README:70][collision-readme]。Boolean/owner-grouped 入口仍只验证形状、f32 可表示性和非零方向；它并未增加 pairwise near-parallel 或 closed-capsule 等价性保护。README 已明确 frozen fixtures 通过构造避开边界，因此文档修复成立。

**最小修复：** 把“domain enforcement gap 已修复”写成“以 fixture-only correctness claim 限缩处理”。通用引擎计算 provider 接受事件的 BOOL_OR，不承担任意闭胶囊几何语义；不能用 30/30 fixture match 外推一般碰撞正确性。

### P2-3：最新报告少算了 Direct adverse blocks

位置：[Goal5850 报告:179][g5850-direct-blocks]。列出的 triangle A/D ratios 中 1.452162、1.394327、1.401147 共 **三块**超过 1.35，正文却写 two。Direct gate 是 median-only，因此这不改变该 gate PASS；它影响对离散程度的描述，也再次说明不能将 A/C 的 worst-block gate 借给 Direct。

**最小修复：** 后续勘误/claim ledger 标为 3/8；不改 raw ratios，不修改原门槛。

### P3-1：当前状态入口仍有旧标题

位置：[最终冲刺计划:9][sprint-header] 写 GOAL5849_COMPLETE__GOAL5850_NEXT，后文和最新 AGENTS 已正确写 Goal5850 完成、Goal5851 下一步。这是导航歧义，优先级低于论文和证据。最小修复是在允许的文档整理中同步状态标题；无需重开任何完成目标。

### P2-4：provider bind 的清理失败仍会覆盖原始错误

位置：[v4_rtdlexe.py:3076][bind-cleanup]、[v4_rtdlexe.py:3094][initializing-close]。bind 的 except 分支调用 release/close，没有捕获 secondary cleanup exception；若 release 抛错，后续清空状态的代码不会执行，重新抛出的变成 cleanup 错误。随后 close 又先将对象标为 CLOSED 并清空引用，再调用可能失败的 release。

使用现有 Goal5847 fixture 的临时资源进行 fault injection：descriptor validation 抛 ORIGINAL_DESCRIPTOR_FAILURE，release 抛 SECONDARY_RELEASE_FAILURE；实际暴露后者，bind 后状态仍为 BINDING。此反例说明 Claude “所有审查路径 cleanup 都保留原错、资源所有权已全部关闭”的保证过强，外层 worker 的 add_note 并没有修复内层先覆盖原错的问题。

更具体地，注入点为真实 release 流程内部的 _remove_native_cache_lease：第一次失败后 lease 处于 PROVENANCE_UNREGISTERED；第二次 close 失败后 active_lease_ids 仍含该 lease，但 initializer 已清引用且 CLOSED；第三次 close 是 no-op。这证明不只是异常消息改变，还可能丢失资源重试所有权。

这是组合故障路径缺陷，不是已成功正式样本的错误输出证据，也不支持推翻保留的性能数据。不能只修改第二代源码来修它，否则两代不再同源。本次不做修复；在当前提交中明确披露并取消“全面失败清理正确”的保证，修复另行安排。若 owner 决定在冻结前纳入实现修复，则必须重新处理两代同源实验要求，不能沿用一代旧结果作为相同实现。

## 5. Architecture/generalization verdict：架构与泛化

对应邀请第 6 节逐项回答：

| 问题 | 裁决 |
|---|---|
| 6.1 协议形状代数是编译抽象还是描述 schema？ | 有意义的 admission/identity 抽象，能区分 family、instance、deployment；目前不驱动拓扑通用可执行 lowering。canonical plan 的 executable=false 是边界说明，不足以否定整个编译器。 |
| 6.2 冻结核心是否包含重要通用机制？ | 包含重要的 admission、计划、身份、provider binding 和 lifecycle；不包含通用 codegen。按已注册问题足够，按任意拓扑编译器问题不够。 |
| 6.3 selected extension 是实例化还是新特例？ | 对通用 SPI 是真实实例化；对 wrapper/native realization 是新增特定拓扑实现，二者同时成立。 |
| 6.4 NIST 能否防 cherry-picking？ | 防止表冻结后便利选行；不能消除作者定义候选域、先验知识和较窄 topology 选择。 |
| 6.5 package-external 是否实质边界？ | 是模块/SPI 边界，不是自动生成 GPU provider，也不是用户与可信 runtime 之间的安全隔离。外部 fixture 自行产生 CPU 输出，不算外部 GPU 作者实验。 |
| 6.6 最强 generality 句？ | 见第 7 节，必须同时写候选域、冻结边界和新增 lowerer 成本。 |
| 6.7 checker 是否循环？ | 没有共享 rtdsl 实现导入，拒绝 compiler_projection，是独立实现；但同一团队、原始编译器产物和 TCB 假设不因此独立。 |
| 6.8 五个属性是否足够？ | 对冻结的结构/变异分母足够；不是可达性、数值、SBT 动态执行、跨 launch 语义或完整 soundness 的充分条件。 |
| 6.9 compiler 还是 checker+templates？ | 包含真实 frontend、IR 与叶函数代码生成的 bounded compiler，加 schema-parametric admission 和模板 lowerers。避免二选一的标签争论，准确列出哪层由 schema 驱动。 |
| 6.10 零外部人类作者是否致命？ | 不自行否定编译机制贡献；删除 ease/productivity/learnability 优越性，保留限制。 |

源码依据：[canonical plan][canonical-plan]、[selected leaf codegen][sphere-numba]、[selected OptiX compiler][sphere-compiler]、[wrapper 固定 skeleton][sphere-wrapper]、[package-external fixture][external-fixture]。

与已有工具的差异要保留“精确 residual”。OptiX 已有按 shader 类型规定 payload word 读写的机制；OWL 已提供 SBT、buffer、pipeline 和 acceleration structure 的组织。因此 Claude 开头“没有任何现有工具检查 assembled protocol”的绝对论断不能作为 novelty 证据。本项目应声称并展示的是在所检查版本/路径中仍由应用负责的名义槽位含义、跨角色义务、状态发布和 executable binding，而不是所有既有工具均无检查。[NVIDIA payload 文档](https://raytracing-docs.nvidia.com/optix8/api/group__optix__types.html)、[OWL 官方仓库](https://github.com/owl-project/owl)。当前稿件保留的三项 full residual、一项 partial、一项 binding-support 分类也不能重新合成“五项完整错误输出证明”。

## 6. Sphere/curve/collision verdict：几何和应用边界

| 邀请问题 | 裁决 |
|---|---|
| 7.1 built-in geometry 真伪 | sphere/curve 使用真实相应 OptiX build-input 和 built-in IS；core 显式拒绝同时提供 user IS，entryFunctionNameIS=nullptr。[native built-in IS][builtin-is] |
| 7.2 应用语义是否进入引擎 | 所审 V4 新路径未发现 robot/trajectory/RT-CCD 特定调度或应用公式。legacy metadata 有应用名，需分区说明；关键词检查不能替代结构审查。 |
| 7.3 near-parallel exclusion | First Contact 有执行前保护；Boolean 与 owner-grouped 没有同等保护。当前通过 fixture-only 范围披露，不能说所有 public entry points 都强制排除。 |
| 7.4 OWNER_GROUPED_ANY_HIT / BOOL_OR | 是通用 accepted-event 到 owner-indexed bit 的归约；owner 含义不进入引擎。[wrapper:228][owner-wrapper] |
| 7.5 应用 ownership | swept geometry、edge policy、collision interpretation 和独立 oracle 在 case_studies 中。[应用源码][collision-app] |
| 7.6 Goal5835 是否 case study | 只能说 bounded semantic projection with inherited true-OptiX evidence；没有执行其 app front door、没有新 GPU launches，不可简称执行过的 case study。[当前状态][g5835-status] |
| 7.7 Goal5836 terminal 是否合理 | 合理；方向/连通性及 inside-start 谓词不同，同一事务不能继续假定同函数比较或晋升 Paper App。不是证明 RTDL 永远无法表达该应用。 |
| 7.8 仍可能误读之处 | 将 Goal5835 与 Goal5837 统称一次完整 RT-CCD 实验会误导。目录名或引用 Sui 本身不是错误；邻接说明 mapping idea、terminal mismatch 和限制即可，不改历史路径。 |
| 7.9 投稿前还需新增什么 | 不要求 full RT-CCD、TOI 或新 app；精确披露 fixture 域、两项案例的不同证据层级即可。 |

只读反例也验证了边界：胶囊轴 (0,0,0)→(2,0,0)、半径 0.25，与共线 query (-2,0,0)→(4,0,0)，Boolean/app length admission 接受，而 First Contact 拒绝 near_parallel_curve_query；closed-capsule oracle 为 hit。本机没有对此运行 GPU，不能报告新 OptiX 错误输出。

## 7. Goal5838 prospective-exam verdict：冻结框架考试

**接受预注册窄范围成功，不接受通用 lowering 推论。** [预注册:9][g5838-prereg] 定义了真正的问题，[预注册:50][g5838-extension] 明确允许 provider-specific implementation 等冻结外工作。新增约 2,635 行是重要 TCB 和工程成本，不是事后违反冻结。

Claude 的“curve Boolean 可能已实现，所以分母是九”被源码反驳：基线旧 Boolean 使用 closest_hit，候选是 any_hit + terminate。十行分母成立。Claude 的推荐句还错误地称所有候选共享同一四角色、没有 user intersection；custom candidates 实际增加 bounds/intersection 角色，见 [CHALLENGE_TABLE:405][challenge-custom]。仲裁对这两点的纠正应保留。

可用的最强表述为：

> 在 7da68056550818d8e2f6cdb4d7aa3e9029cc4524，项目从预先冻结的十行作者定义候选表中，按预定 NIST beacon 规则选出此前未实现的 sphere/count/continue 组合。该表交叉已有四类 primitive 和三种有限 any-hit continuation/result 变体，并按已实现的精确拓扑排除两行；custom 候选另有 bounds/intersection 角色。实现所选组合新增约 2,635 行特定拓扑代码，但三份已封存的 admission/identity/lifecycle 文件没有改变。该路径在 RTX 2000 Ada / OptiX 9 的两次实际执行中匹配 12 行独立 oracle。这证明一次受限框架扩展，不证明无偏新应用泛化或拓扑通用代码生成。

本次 authority verifier PASS；当前树后来改变 seal 文件不推翻过去时结论。不得再用当前文件的 seal test 失败推导历史作弊，也不得反过来用历史 PASS 声称当前 core 仍完全相同。

## 8. Goal5840 refinement-evidence verdict：独立结构检查

**接受三个 route groups、四 modes、五 property classes 的已冻结结构证据。** 20/20 property applications 和 15 个独特 mutation / 20 次应用的分母可保留；不能写成 20 个独立语义属性或穷尽变异。

独立性成立在实现层：stdlib-only checker、拒绝 compiler_projection，重新检查原始 source/ABI/PTX 和 host ordering。它不构成独立硬件 attestation，不验证所有机器指令含义，不覆盖任意 numeric refinement。对具体模板的 source anchors 和固定 route 分支仍属方法的限制。

P2-1 的 early-return 探针不在冻结 mutation 中，因此不把原实验判 FAIL；但它足以否定“rather than pattern-matching”的强化叙述。论文应明确：文本先后关系并不自动证明控制流支配或可达性。也不能仅因 checker 没有 import rtdsl 就声称消除了所有共同假设。[原报告自身的限制][g5840-limits] 比两份评审的表述更准确。

## 9. Performance and baseline-fairness verdict：性能与公平性

### 9.1 历史链与当前结果

Goal5842 的因果测量与 Goal5843 adverse baseline，随后 envelope、compaction、cache、AOT 和同源执行 ABI 修复，构成可理解的工程链。查到的修复表达在通用受限路径上，没有发现仅按本次 benchmark 名称选择的 native kernel。保留失败是必要条件，不能单凭这一点排除所有 baseline weakness 或调参选择效应。

Goal5845 的机制应准确分三步：device deduplication、传回 deduplicated packed rows、native-host sort/unique。弱 PyOptix 则复制 raw duplicate rows 并进行 NumPy/Python 对象化和 sorted(set(...))。Claude 由“约两倍行数”推断不可能解释 9.53x，没有因果测量支撑；仲裁驳回这个推断正确。反过来，仲裁也不能声称已经证明 Python 对象化占多少比例。保留精确内部 measurement，paper 主比较应使用强 C；不展示 intrinsic 9.53x speedup。[追加式机制勘误][g5845-correction] 已正确避免重写旧报告。

当前 Goal5850 transaction 4 的内部结果如下。它只表示一代实验，不授权 manuscript 正面 performance claim：

| 任务 | A/C implementation-entry median / worst block | 旧 post-import median | A/D prepared steady median | C/B prepared steady median | A/E prepared steady median |
|---|---:|---:|---:|---:|---:|
| 16,384-query checked-U64 triangle | 0.327669 / 0.414433 | 1.997967，adverse | 1.171933 | 0.658855 | 0.684053 |
| 4,096×4,096 canonical relation，4,096 rows | 0.389597 / 0.423498 | 2.111030，adverse | 1.075168 | 0.231363 | 0.643587 |

比值均为同机规定估计量，不是跨机器原始时间之比。首次结果 A/C 很受 dependency import 影响，不能改写成语言速度提升；A/D 只通过中位数 gate，triangle 有 3/8 块超过 1.35。

### 9.2 对邀请第 8 节的完整回答

| 问题 | 裁决 |
|---|---|
| 8.1 修复是否对应测得成本 | 所查 causal chain 合理，未发现 app-specific native dispatch；每个新版本仍需自己的测量。 |
| 8.2 Goal5844 immutable cache | 冻结身份对象上的纯 digest memoization 不等于缓存 mutable proof；逐执行状态/stamp 仍检查。进程级缓存的持有期是资源限制，不是已证 stale output。 |
| 8.3 Goal5845 compaction | 是 bounded relation 的去重/精确输出机制；final ordering 仍在 native host，不是全部 canonicalization 都在 device。 |
| 8.4 1.046x 是否有价值 | 有，作为同设备程序字节下的公开 envelope 比较；只限该任务/硬件/稳态，最差块 1.1543x，不是语言零开销。 |
| 8.5 弱 baseline 9.53x | 是特定实现 comparison 的内部事实，不是 PyOptix 上界或 intrinsic speedup；主文应删该 headline，用强 C。 |
| 8.6 Goal5846 warm-cache | 只能按其 source-compiling comparator 的实际部署合同讲工程里程碑，同时保留 precompiled sensitivity；不能说对称 AOT parity。 |
| 8.7 Goal5847 complete-process | 可说明打包/生命周期负担，不用作语言快慢；原 post-import 仍保留，但后来已知它不是等 lifecycle state 比较。 |
| 8.8 后继优化是否违规 | 泛化到路径的优化且旧样本不池化，可以作为新实验；不是因为修复只发生在 RTDL 就自动无效。最后三次失败与第4次应明示适应性工程过程。 |
| 8.9 B/C 区别及公平性 | B 为 pinned idiomatic route；C 有等价 device continuation，并经过 competence gate。C 胜 B 不证明全世界最优 PyOptix，仅支持已审强实现。 |
| 8.10 Direct D | 对匹配的具体输出是有用低开销参考；不是等价公共 DSL API。必须披露 launch、D2H、oracle validation 及 prepared regime，不能借它推出首次结果 gate。 |
| 8.11 predecessor E | 支持该两任务同机稳态回归控制，不证明全部 API、setup 或所有输入都无回归。 |
| 8.12 门槛 | 1.20/1.35/1.05 是项目预定操作目标，不是统计显著性或普遍可接受性定理；发生失败不能改阈值。 |
| 8.13 cache disabling | CUDA/OptiX disk cache 的受控关闭与 executable AOT hit cache 是不同层；前者限定实验环境，后者仍使用。不能称为 first-ever build 或全面 cache-free deployment。 |
| 8.14 八块与128样本 | 对预注册描述统计和硬门槛足够；稳态重复在 worker 内，不能当 10,240 独立冷启动。最大块值不是总体尾部上界或 CI。无需为通过门槛临时扩样。 |
| 8.15 两代意义 | 目前1/2。未来同源两代通过只证明这些 task/stack 上重复成立，不是 vendor/OptiX 通用 portability。 |
| 8.16 可用性能句 | 必须等待第二代、recount和claim review；分别写 A/C implementation-entry 与 A/D prepared median，说明 import confound、cache policy 与 exact tasks。不能复制 Claude 的混合句。 |

## 10. Goal5848 design-readiness verdict：设计、实现与证据成熟度

这是设计/实现就绪度审查，不是 Goal5848 完成判决。历史 Claude 所审 WIP 没有 formal result；当前 c4351f612 有一代完整事务。两者必须分开。

### 10.1 endpoint 修正的可接受范围

原 post-import 源码只显示 import 已结束，并不能证明 CUDA 初始化状态相同。留存 transaction4 的 pyoptix-source.tar.gz 中，src/optix/__init__.py:25 导入 _optix，src/main.cpp:2331 在模块初始化执行 cudaFree(0)；因此所 pin 的 import 有 CUDA 启动副作用，修正为 implementation-entry 有技术依据。正式 worker 同时记录 import、gap、post-import，验证三项精确相加，且仍输出旧 adverse diagnostic。

这是一项在看到失败后定义、再提交并重新注册的后继 endpoint，不能称为原 post-import 目标通过。所报八次 context probes 的原始输出未在本次检索的本地证据目录中找到，所以本次独立确认的是 pinned 源码副作用和正式时间分解，**没有独立核实 485.4ms probe median**。不要让这个探针统计成为论文的唯一因果支柱。

### 10.2 邀请第 9 节的证据/安全检查

| 检查 | 本次结果与限制 |
|---|---|
| 9.1 source/toolchain/task/GPU 绑定 | 已核 current Git、主要历史 authorities 和成功 archive 的 file commitments。没有对整个项目所有旧 DSO 做本机 byte replay。 |
| 9.2 failed/superseded retention | transaction1/2/3 分别保留，transaction4 独立；所查历史 authority 和报告仍披露 adverse。无复用旧 samples 的证据。 |
| 9.3 independent verifier imports | Goal5838/5840 和强 baseline recount 的独立性按其实际 imports 判断；source-reading 不等于 import implementation，也不等于独立硬件见证。 |
| 9.4 hostile mutation 面 | 检查了现有 preregistration/command/strict JSON/artifact/output/timer mutation 路径；不能从有限 mutation suite 推出所有 coherent resealing 都封闭。 |
| 9.5 seal 时点 | Goal5838 seal/selection 与 exact evidence commit 有效；Goal5840 限定 checker/route/mutation 与历史绑定有效。 |
| 9.6 AOT binding | exact payload/provider/family/target/toolchain 身份链不依赖友好文件名；不得把摘要绑定或 load-time image 身份宣称为独立硬件认证。 |
| 9.7 production cache policy | 实验显式关闭 driver/OptiX cache；不是默认 production 禁用。AOT executable cache 仍命中，两个概念不混写。 |
| 9.8 从 raw 重算 | 成功 archive 全 manifest 验证、正式80 receipts及ratio/gates重算支持一代结果；controller/recount字节一致。 |
| 9.9 exact commands 与 git trees | 现有 builder 重建 preregistration、期望 command 和 execution context；只能建立其声明 trust model 内的一致性，不能抵御控制整个 producing host 的伪造。 |
| 9.10 failure-path ownership | worker 层 add_note/cleanup 的主要修复保留；P2-4 证明内层 bind 双故障仍能覆盖原错，不能宣布全面关闭。 |
| 9.11 stale tests | 5832/5838 已披露；本次补发现 5837/5843。不要 broad discovery 全绿包装，也不要修历史 manifest。 |
| 9.12 checkout 内 evidence | current formal output 实际在 repository 外，避免 worker source identity 被输出污染；Git 中历史证据用于后续审计，不因此自动污染它原先绑定的 snapshot。 |

### 10.3 实际执行的验证与未执行项

所有 Python 验证使用上述 3.12.14 环境和 PYTHONDONTWRITEBYTECODE=1、PYTHONPATH=src:.。未运行全历史测试。

| 已存在命令或只读检查 | 结果 |
|---|---|
| audit_goal5835_goal5836.py --verify-stored | PASS |
| goal5836_a1_build_source_fidelity.py --verify-stored | PASS |
| goal5838_build_final_authority.py --verify-stored | PASS，seal c0578a22…，两次 launch / 12 oracle rows |
| goal5840_build_final_authority.py --verify-stored | PASS，seal 3857a8c1…，4 modes / 20 property applications |
| goal5842_build_final_authority.py --verify-stored | PASS，seal 5c8044d9… |
| goal5844_build_public_parity_authority.py --verify-stored | PASS，seal 3c44e950… |
| goal5845_build_relation_public_parity_authority.py --verify-stored | PASS，seal 49827211… |
| goal5846_build_relation_startup_authority.py --verify-stored | PASS，seal 7ccf6b63… |
| goal5847_build_aot_startup_authority.py --verify-stored | PASS，seal 3501c83a… |
| Goal5837/5843 current-tree verify-stored | FAIL，原因和历史边界见 P1-3，未隐藏 |
| Goal5843 frozen source / seals | 45/45 Git source hashes 匹配；三个 seal 匹配；pod/local recount 字节一致 |
| Goal5850 archive | 37,255,534 bytes；SHA-256 f487f42580ac8cb81c202fe867b976ba7a267b9ca7ccffb980c626d775b112c8 |
| Goal5850 manifest | 2,405 payloads / 125,733,693 bytes，全部大小/hash匹配；无缺失/额外payload，manifest自身按合同排除 |
| Goal5850 tar safety | 2,446 members，无 symlink/hardlink/absolute/parent traversal 成员 |
| Goal5850 authority pair | byte-identical；file SHA-256 82bda443b3a21f5970e6f8e81fec34d57471c88e82a237ade8034bf93d4d1aed |
| Goal5850 raw workers | 全部80份经现有 evaluate_complete_transaction 重算，与 stored recount 相等；另以 stdlib 检查时间分解及每 task/arm 八 worker，无不一致。共10,240 steady samples |
| 定向 unittest | goal5848_transaction_authority_test、goal5848_worker_failure_cleanup_test、goal5845_relation_compact_execution_test：45/45 PASS；不覆盖本次 initializer 双故障 |
| 内存探针 | checker early-return盲点、curve domain接受边界、provider双故障覆盖原错均已复现；不写仓库、不运行GPU |

验证 stored authority 只代表其当前 verifier 能重算声明范围，不能冒充本次独立 GPU 执行。对原始 GPU 与 hostile producing-host 的真实性仍遵守原证据 trust model；本次也没有完成匿名 artifact 的干净安装、PDF渲染或投稿系统检查。

使用同一个 contracts 模块重算，不等于独立实现了第二套统计算法；本报告把其与额外 stdlib 时间分解/计数检查分开记录。

交付前检查：第1至15节齐全、18项claim齐全、所有文件引用存在且行号有效；第10.4节两个命令由主审从报告文本重新执行，均重现所述结果。原三份输入的SHA-256保持不变，tracked git diff为空，唯一新增文件是本报告。架构与性能子审查分别复核了最终相关段落，未提出必须再修正的事实项；这不计作外部共识。

### 10.4 两个关键反例的最短重放

以下命令只在内存/系统临时目录构造输入，不编辑仓库文件，不产生新 GPU 证据。运行目录为本报告第1节工作目录。

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python - <<'PY'
import base64, json
from pathlib import Path
from scripts import goal5840_independent_target_checker as c
p = Path('history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_GPU_EVIDENCE/mode_01_capacity_fail_closed_collection_bundle.json')
b = json.loads(p.read_text())
s = base64.b64decode(b['generated_target_artifacts']['wrapper']['source']['base64']).decode()
anchor = 'extern "C" __global__ void __anyhit__rtdl_v4_bounded_relation() {'
assert s.count(anchor) == 1
mutated = s.replace(anchor, anchor + '\n    return;\n', 1)
for label, source in [('original', s), ('early_return', mutated)]:
    print(label, c._bounded_partial_evaluation_effects(source))
    print(label, c._check_wrapper_status_flow(b['route_id'], source))
print('Helper-level probe only; no full bundle/authority bypass claimed.')
PY
~~~

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python - <<'PY'
import contextlib
from unittest.mock import patch
from tests.goal5847_aot_provider_initialization_test import Goal5847AotProviderInitializationTest
import rtdsl.v4_rtdlexe as r
case = Goal5847AotProviderInitializationTest()
case.setUp()
try:
    source, digest, entry, lease, readiness = case._resources()
    deployment, loaded, descriptor = case._deployment_and_loaded(digest)
    with contextlib.ExitStack() as stack:
        for p in case._patches(lease, readiness, descriptor):
            stack.enter_context(p)
        initial = deployment.begin_provider_initialization(source)
        initial._thread.join()
        original = ValueError('ORIGINAL_DESCRIPTOR_FAILURE')
        stack.enter_context(patch.object(r.LoadedRTDLExecutable,
            '_validate_native_provider_descriptor', side_effect=original))
        fail = stack.enter_context(patch.object(r, '_remove_native_cache_lease',
            side_effect=RuntimeError('SECONDARY_RELEASE_FAILURE')))
        try:
            initial.bind(loaded)
        except BaseException as e:
            print('bind', repr(e), 'is_original', e is original,
                  'state', initial.state, 'release_calls', fail.call_count)
        try:
            initial.close()
        except BaseException as e:
            print('close', repr(e), 'state', initial.state,
                  'refs_cleared', initial._library is None and initial._readiness is None,
                  'active_lease_retained', lease._rtdl_native_cache_lease_id in entry.active_lease_ids,
                  'phase', lease._rtdl_native_image_release_phase)
        initial.close()
        print('third close no-op; release_calls', fail.call_count)
finally:
    case.tearDown()
PY
~~~

## 11. Claim-by-claim classification：全部18项主张

SUPPORTED 指事实在注明范围内有证据；不是本次替 owner 授权发布历史仍受限制的性能结果。

| # | 邀请中的 statement | Classification | 必要边界或改写 |
|---:|---|---|---|
| 1 | RTDL makes the complete callback protocol the compilation unit. | SUPPORTED_WITH_REWRITE | 限 supported bounded protocols；说明 frontend/IR、admission 与 trusted template lowerer 的分工。 |
| 2 | RTDL enforces cross-role callback invariants before GPU execution. | SUPPORTED_WITH_REWRITE | 静态可判的义务在 launch 前检查；设备状态、完成性与精确输出还有运行时 publication gate，不能说五项动态事实全在执行前已证明。 |
| 3 | RTDL is a generic callback-protocol compiler. | NOT_YET_SUPPORTED | 若 generic 指拓扑通用 lowering 不成立；可改为 bounded compiler with schema-parametric admission/identity/lifecycle。 |
| 4 | RTDL executes arbitrary restricted-Python callbacks on RT cores. | FORBIDDEN | arbitrary 无实现和证据。 |
| 5 | A schema-driven frozen core admitted one independently selected unseen topology without modification. | SUPPORTED_WITH_REWRITE | 指7da6805时一次作者定义十行域中的未实现组合；冻结范围不含特定 lowerer，披露2,635行成本。 |
| 6 | RTDL supports all OptiX primitive types. | FORBIDDEN | bounded presence 不是配置、类别、所有变体或层次全覆盖。 |
| 7 | RTDL instantiates all four pinned OptiX leaf-primitive kinds in bounded public routes. | SUPPORTED_WITH_REWRITE | custom、triangle、sphere、round-linear curve 的有限实例；独立于 build-input 和 stable constructor 分母。 |
| 8 | RTDL reproduces Sui et al. RT-CCD. | FORBIDDEN | Goal5836 terminal fidelity mismatch，Goal5835不是Paper App。 |
| 9 | A bounded collision-detection case study consumes an app-neutral owner-grouped any-hit Boolean primitive. | SUPPORTED_WITH_REWRITE | 指后继owner-grouped案例、注册fixture域；不能把Goal5835投影说成执行了相同app front door。 |
| 10 | Independent developers can use RTDL more easily than PyOptix. | FORBIDDEN | 无外部人类作者或比较研究。 |
| 11 | RTDL has negligible runtime overhead. | FORBIDDEN | 无普遍结论；Direct median-only、adverse blocks与启动成本均须呈现。 |
| 12 | RTDL is 9.53x faster than PyOptix. | FORBIDDEN | comparator仅特定弱实现，非intrinsic或一般PyOptix速度。 |
| 13 | On one exact scalar route, the repaired public envelope was within the preregistered parity bound of pinned PyOptix. | SUPPORTED_WITH_REWRITE | 历史Goal5844 exact task/Ada/steady/identical device bytes，median1.0457与worst1.1543；不扩为当前全路径。 |
| 14 | On one exact row-returning route, generic RTDL device compaction was much faster than a pinned host-continuation PyOptix implementation. | SUPPORTED_WITH_REWRITE | 精确弱arm endpoint measurement有效；写device dedup + native-host ordering，不能因果归于单一阶段，建议主文不用该headline。 |
| 15 | Goal5848 closes strong-baseline and post-import performance. | NOT_YET_SUPPORTED | 当前1/2；而且修正协议也不再承诺旧post-import通过。未来若两代通过，仍必须重写这句话。 |
| 16 | The real-artifact census shows protocol bugs are prevalent. | FORBIDDEN | 零分类不支持prevalence；NOT_FOUND/UNCERTAIN不是bug。 |
| 17 | RTDL's target lowering is formally proven sound. | FORBIDDEN | 无soundness theorem；有限结构mutation不等价。 |
| 18 | A separately implemented checker found bounded structural refinement for three route groups, four modes, and five properties. | SUPPORTED_WITH_REWRITE | 限exact structural properties/mutations；明确anchors与控制流/数值边界，不能加独立语义partial evaluator。 |

## 12. Required manuscript edits and evidence cuts：文稿修改与两份意见清审

### 12.1 Claude 意见的逐项处置

| 原意见 | 本次裁决 |
|---|---|
| P0-1 sealed core没有通用lowering | 接受源码观察；拒绝“所以整个RTDL不是compiler”。按预注册framework extension接受，按通用lowering拒绝。 |
| P0-2 domain作者预选、狭窄 | 接受限制；拒绝因此否定预注册实验、九行分母疑虑，以及所有candidate只有四角色的推荐句。 |
| P0-3 host canonicalization存在 | 接受；追加式机制勘误已处理。拒绝仅由2x rows推导9.53x“无法解释”，拒绝改写历史sealed报告。 |
| P1-1 stale seal tests | 接受历史/当前要分开；guide已改善但本次发现5837/5843缺项。 |
| P1-2 Boolean near-parallel gap | 源码事实成立；fixture-only披露已落实，不代表runtime enforcement已修。 |
| P1-3 binaries/raw capsule不在Git | 仓库自足性问题成立；不必强制commit/LFS，独立artifact提供exact bytes或注明不可byte replay也可。 |
| P1-4 manuscript stale | 接受，但拒绝把unbiased new-app zero改成一，拒绝称旧有效authority因新版本而不存在。 |
| P2-1 load-time identity/cache retention | 接受精确身份与持有期限制；不等于cached digest可随mutable对象失效，更不自动等于runtime篡改漏洞。 |
| P2-2 vocabulary blacklist | 降为hygiene；不建议为扩充字符串blacklist改compiler，不能拿它证明app-neutrality。 |
| P2-3 legacy app metadata | 分区说明足够；不将legacy文本命中判为V4应用调度泄漏。 |
| P2-4 README dead links | 当前已修，不再列未修blocker；pyproject存在，CFR无packaging metadata的断言错误。 |
| P3-1 instrumentation asymmetry | 当时真实、正式计时前应修；当前flag对称已落实，不沿用旧WIP判定。 |
| P3-2 pod endpoints | 仅在derived anonymous artifact处理，不改sealed authorities；不是见IP就能认定作者身份泄露。 |
| Goal5840强于structural | 拒绝其语义partial-evaluation扩张，保留bounded structural事实。 |
| Goal5848资源清理已全面关闭 | 拒绝全面保证；P2-4有具体未覆盖双故障。 |
| Goal5848可发表性能句 | 拒绝，endpoint/gate混用；拆句且遵守当前1/2边界。 |

### 12.2 仲裁文档的裁决

仲裁作为“内部处理意见”总体比原 Claude 的三个 P0 更准确，尤其是预注册成功与泛化程度分离、closest-hit/any-hit拓扑区分、Goal5845因果不确定性、immutable history与当前树分离、明确不自行宣布外部共识。这些判断应保留。

但不能接受为最终无遗漏仲裁：它仍沿用过强的Goal5840 partial-evaluation措辞，没有明确处理Claude性能句的regime混合，没有纠正所有分母/zero-count修改建议，将case-study disclosure称作locally repaired时不够精确，也漏了P2-4清理失败。其0/2和未提交状态是历史，不应刷新原文伪装当时已知当前成功；用本报告/新状态页追加更新。

### 12.3 必须落实到论文的编辑

1. Abstract/design明确bounded whole-protocol compilation、schema-parametric framework、topology-specific trusted lowerers。贡献不以“generic”形容词、goal/test数量或留存文件体量成立。
2. 分别列4/6 build-input presence、4/4 leaf-kind presence、2 stable constructors、一个closed successor、一次bounded prospective topology exam；保留unbiased new-app/human作者/usability三项零。
3. Goal5840写独立结构检查，列真实TCB和未覆盖控制流/数值问题；不要把不同证据包装成formal proof。
4. Goal5835写语义投影；Goal5837写独立后继fixture执行；Goal5836负结果只用足够解释fidelity边界的篇幅。无需把全部goal历史塞入主文。
5. 性能只按已准许证据分支写：输入/输出、source、hardware、timer、cache、estimator逐项清楚；precompiled部署首次结果不包括首次AOT构建费用，不能称first-ever startup。
6. 删除intrinsic9.53x、普遍negligible overhead、任意Callback IR、prevalence和人类生产力结论。strong C也不等于最佳可能PyOptix实现；说明两边对象物化/packed output reuse的实际差异。
7. 使用已有OptiX payload/OWL residual分析，保留原生工具的能力；对现稿仍准确的限制不做“为了显得进步”式改写。
8. Artifact说明补历史replay命令、缺失raw bytes、绝对路径限制和组合cleanup故障；最终匿名产物与sealed原件分开，原件保持原hash。

## 13. Smallest credible repair plan：最小可信修复计划

按投稿价值排序，仅五项，与下一节一一对应：

1. **先形成可执行的claim ledger并重写论文主张。** 纠正checker能力、拓扑/应用计数、全V4分母和性能regime，保留正确的零计数。证据缺口通过删/限claim解决。
2. **按既定Goal5851收尾性能分支。** 第二代必须同c4351f612；若到既定窗口未满足两代/交叉authority，不使用Goal5848正面论文性能结论。P2-4不准偷修进第二代实现；取消全面cleanup保证，不改变正式数据。
3. **完成选定分支的evaluation。** 分离first-result与steady，保留旧post-import与三次失败，修正3/8 Direct adverse blocks。生命周期探针若无原始凭据，不把485.4ms作为已独立核实的因果数据。
4. **补完整artifact replay地图并做匿名clean-checkout验证。** 明确哪些是历史commit验证、哪些是原二进制byte replay、哪些只是源重建；补5837/5843而不重封任何历史。
5. **冻结后只做最终稿件/工件审查和投稿检查。** 检查PDF、引用、页数、匿名性、claim ledger和上传字节；评审分歧逐项处理，不把本次子审查称外部共识。

无需在截止前完成：通用topology lowering、外部人类研究、全量prevalence census、完整RT-CCD、更多应用、blacklist扩展、超出本次主张的checker完备性。论文可在明确删除对应主张后继续。P2-4修复可作为后继工程；它不能被写成现有清理正确性已闭合。

## 14. Deadline-aware action matrix：五项限额

工时是集中工作的规划估计，不是完成承诺；GPU等待另计。所有实现/实验变更服从9月8日00:00 ET硬冻结，不能用估计工时延后它。

| Finding | Fatal if unfixed? | Repair or descope | Estimated focused hours | Exact files/evidence | Must finish before 2026-09-10? |
|---|---|---|---:|---|---|
| 论文范围/计数/检查器能力混淆，P0-1/P1-2/P2-1 | 是，若保留错误claim | 重写thesis与claim ledger；拆分不同计数；不新增功能 | 5–8 | [main.tex][paper-table]；Goal5838/5840 authorities；本报告§11 | 是，主体应在9月8日完成 |
| 两代性能尚未完成，P1-1/P2-4 | 对Goal5848正面性能claim是；对删该claim后的论文否 | 同c4351f612执行Goal5851；未完成走预定删claim分支；披露cleanup限制 | 2–4操作 + GPU运行/等待 | [冲刺计划][sprint-plan]；transaction4归档；第二代authority | 分支决定须9月7日20:00 ET；冻结不延期 |
| evaluation与endpoint/离散度，P1-1/P2-3 | 是，若保留混合或失实数字 | 分first-result/steady；明确imports；3/8 Direct adverse；历史失败留存 | 4–6 | [contracts.py][gate-steady]；[结果报告][g5850-report]；main.tex evaluation | 是，9月8日前后按冻结分支写作 |
| artifact replay不自足/指南缺项，P1-3 | 对承诺完整byte replay的artifact是 | exact snapshot地图、missing-byte清单、明确relocation边界、干净重放与匿名派生包 | 3–5 | [custody guide][custody-guide]；5837/5843 authorities；off-repo archives | 是，目标9月9日上午 |
| 最终一致性与提交门禁 | 是 | 冻结后第二轮review、PDF/引用/页数/匿名scan、上传hash验证；不修代码 | 3–5 | main.tex/PDF、最终claim ledger、匿名artifact | 是，9月9日审查，9月10日提前上传 |

Goal5848失败或未完成不会被本报告自动改判为整篇不能投；应把“无不可接受性能税”从已证主张中拿掉，保留诚实的测量和受限机制贡献。能否录用仍取决于同行对该较窄贡献的评价，不从内部gate或本报告推算接受概率。

## 15. Final verdicts：最终判决

| Area | Exact verdict | 范围 |
|---|---|---|
| A. Architecture and bounded generalization | ACCEPT_POST_REVIEW_PROGRESS_WITH_SCOPED_CLAIMS | 受限compiler +参数化admission/identity/lifecycle；不含通用topology lowering |
| B. Sphere/curve/collision architecture boundary | ACCEPT_POST_REVIEW_PROGRESS_WITH_SCOPED_CLAIMS | built-in路径和应用ownership成立；fixture-only边界；Goal5835仅投影 |
| C. Independent lowering/refinement evidence | ACCEPT_POST_REVIEW_PROGRESS_WITH_SCOPED_CLAIMS | exact bounded structural与冻结mutation分母；不接受语义partial-evaluator扩张 |
| D. Committed performance evidence through Goal5847 | ACCEPT_POST_REVIEW_PROGRESS_WITH_SCOPED_CLAIMS | 各自精确历史版本/arm/regime的事实；不作intrinsic或最强baseline结论 |
| E. Goal5848 experiment design and implementation readiness | ACCEPT_WITH_BLOCKING_FIXES | 设计和一代raw结果可接受；不能使用混合endpoint性能句或全面failure-cleanup保证。通过主张更正/披露可处置P2-4，不能因此宣布两代完成 |
| F. Current CGO submission readiness | ACCEPT_WITH_BLOCKING_FIXES | 文稿、claim ledger、两代证据分支、artifact和最终提交检查尚未完成 |

可继续准备并提交精确限缩后的CGO论文。Claude意见应逐条吸收，仲裁的三项主要反驳应保留；两者均不能未经本次更正直接作为最终论文事实。没有授权原post-import parity、Goal5848两代完成、最终外部共识或直接上传现稿。

**Overall recommendation: PROCEED_ONLY_AFTER_LISTED_BLOCKERS_ARE_FIXED**

[cfr]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/call_for_review_since_last_claude_goal5830_goal5848_20260905.md:1
[claude]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md:1
[adjudication]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_claude_cgo_adjudication_20260905.md:1
[freeze]: /Users/rl2025/rtdl_v4_restricted_python_design/AGENTS.md:3
[sprint-plan]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/cgo2027_final_sprint_goals_20260905.md:103
[sprint-header]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/cgo2027_final_sprint_goals_20260905.md:9
[paper-scope]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:650
[paper-table]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:934
[paper-perf]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:1117
[paper-zero-app]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:70
[paper-zero-app-long]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:1115
[claude-counts]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md:1172
[claude-performance-sentence]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md:1046
[claude-checker]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md:885
[adjudication-checker]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_claude_cgo_adjudication_20260905.md:281
[adjudication-domain]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_claude_cgo_adjudication_20260905.md:112
[gate-steady]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/contracts.py:1255
[gate-lifecycle]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/contracts.py:1287
[native-triangle]: /Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:1905
[native-custom]: /Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:6016
[native-sphere]: /Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:2476
[native-curve]: /Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:3115
[builtin-is]: /Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_core.cpp:1973
[custody-guide]: /Users/rl2025/rtdl_v4_restricted_python_design/KNOWN_STALE_CUSTODY_CHECKS.md:113
[g5837-verifier]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5837_freeze_owner_grouped_classification.py:1023
[g5843-prereg-compare]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5843_post_r1_baseline/contracts.py:559
[g5850-portability]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5850_generation_a_final_report_20260906.md:218
[g5850-report]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5850_generation_a_final_report_20260906.md:1
[g5850-direct-blocks]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5850_generation_a_final_report_20260906.md:179
[checker-anchors]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5840_independent_target_checker.py:568
[checker-linked]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5840_independent_target_checker.py:820
[boolean-guard]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_curve_physical_schema.py:917
[collision-readme]: /Users/rl2025/rtdl_v4_restricted_python_design/case_studies/linear_rtccd_owner_grouped/README.md:70
[bind-cleanup]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:3076
[initializing-close]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:3094
[canonical-plan]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_family_schema.py:1427
[sphere-numba]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_sphere_any_hit_count_numba_codegen.py:67
[sphere-compiler]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_sphere_any_hit_count_optix_compiler.py:123
[sphere-wrapper]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_sphere_any_hit_count_wrapper_codegen.py:287
[external-fixture]: /Users/rl2025/rtdl_v4_restricted_python_design/tests/fixtures/goal5838_external_provider.py:9
[owner-wrapper]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_curve_owner_grouped_any_hit_optix_wrapper_codegen.py:228
[collision-app]: /Users/rl2025/rtdl_v4_restricted_python_design/case_studies/linear_rtccd_owner_grouped/linear_rtccd_owner_grouped.py:150
[g5835-status]: /Users/rl2025/rtdl_v4_restricted_python_design/case_studies/sui_derived_edge_crossing_core/CURRENT_STATUS_AFTER_GOAL5836.md:24
[g5838-prereg]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5838_generic_core_exam_20260902/PREREGISTRATION.md:9
[g5838-extension]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5838_generic_core_exam_20260902/PREREGISTRATION.md:50
[challenge-custom]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5838_generic_core_exam_20260902/CHALLENGE_TABLE.json:405
[g5840-limits]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_TECHNICAL_REPORT.md:180
[g5845-correction]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5845_relation_public_parity_20260904/CAUSAL_WORDING_CORRECTION_20260905.md:1
