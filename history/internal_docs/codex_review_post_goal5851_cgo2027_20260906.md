# Codex 独立审查：RTDL post-Goal5851 CGO 2027 投稿门槛

日期：2026-09-06。审查者：Codex，联合三个独立分工的源码／证据审查子任务。本文是 AI 辅助独立复核，不冒充 Claude、人类外部作者或已经达成的外部共识。

**最终判决：`PROCEED_ONLY_AFTER_LISTED_BLOCKERS_ARE_FIXED`。**

两代同源的性能数字经原始字节和逐 worker 重算成立；bounded whole-protocol compiler 的研究定位也成立。但“机器验收通过”不能直接提升为“原 Goal5848 的全部书面安全不变量已经履行”：正式快路径没有在输出发布前验证详细 receipt，正式 worker 也没有逐样本补验或保存这些 receipt。这是本轮最重要的新增发现。可以保留精确源码下的有限性能观察，必须追加协议差异裁决、缩小保证并完成论文和 artifact 改写。未发现必须更换现有源码、增加应用或赶做人类研究才能保住这个有限论文贡献的理由。

## 1. 精确 custody 快照与审读文件

开始时间：2026-09-06 12:42:19 America/New_York（16:42:19 UTC）。

| 项目 | 本轮直接取得的值 |
| --- | --- |
| 工作目录 | `/Users/rl2025/rtdl_v4_restricted_python_design` |
| 分支 | `codex/cgo-goal5836-handoff` |
| HEAD | `04bd1d54f4641f12b6cf8e19a9e9eef5767a2021` |
| HEAD tree | `06966bf16ea8ab1a2e8027543d8c00985c7389a6` |
| 本地 origin tracking ref | 同 HEAD；本轮未联网 fetch 来声称远端实时状态 |
| 最终实验 commit | `d653fe4ad170c5b51fee309d653c9565944dcf2e` |
| 最终实验 tree | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| 实验前驱 | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` |
| 开始时 tracked/staged diff | 均为 0 bytes；SHA-256 均为 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| 开始时 untracked | 仅 `history/internal_docs/independent_reaudit_cfr_claude_adjudication_20260906.md`，保留且未用其结论代替重建 |

`git diff --name-only d653fe4..HEAD` 精确返回 11 个文件：AGENTS、此次 CFR、Goal5850 generation-A final report、Goal5851 cross-generation final report、两个 Goal5851 execution packets、triangle repair report、strict self-review，以及 memory 的 decisions/progress/todo。没有 source、native、experiment、workload、baseline、timer、estimator、threshold 或 test 变化。该 binary diff 为 100,748 bytes，SHA-256 `c3caf007a2443763c8099e740c9d27428a7a9a341511b753981ef65802790aee`。

关键输入的本轮 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| [本轮 CFR][cfr] | `45b56ccfd62703b713dab79caa0b0eabbef7143f3d1b00fc281cd146923f629b` |
| [strict self-review][self] | `82adfacb717082f776ad83b4cbaab04675a013e56f359e52d5be2c6732361732` |
| [2026-09-05 Claude review][claude] | `9155d8c472325bc62ef298c978294509a86e1ededa9de46a23b1254946ffbf34` |
| [2026-09-05 adjudication][adjudication] | `b36899d5ad6a9cf9766fce1eb262c8af603463171855cf49f7dd27446cb3daa3` |
| [cross-generation final report][final-report] | `4e5c54e315ef1cd56100ad511749f60427f83c5012f1a95697033a15cf842d79` |
| [manuscript][paper] | `d9cf2dc38f83e6545c4880efd6f101be27553c6729f41dcc7afe0e126c504716` |
| [paper README][paper-readme] | `71e5e7a510387d8229c9b543b6f6662b278597540cddca66f226b3f03fdde2d1` |
| [custody guide][custody] | `3402a6ddbdc0eade28b0c9c5002095fe6d1d8e02b5a11995c20d7bb7139578df` |
| AGENTS.md | `1365411c44180c0303db76b713603a54b82fac6499cb29b1ec5750dbdfbc04b0` |

CFR 全文、主审稿全文（1,579 行）、self-review、旧 Claude review/adjudication及其 material findings 已审读。源码审查沿相关调用链进行，不声称逐字阅读所有大型 native 文件。团队检查的实现包括 `v4_rtdlexe.py`、`v4_aot_cache.py`、family schema/lifecycle/SPI/route adapters、sphere leaf/compiler/wrapper、三个 OptiX native 文件；实验包括 Goal5848 contracts/controller/worker/strong_pyoptix/direct_bridge/workloads、transaction/cross-generation builders、pod runbook、相关测试及继承的 strong-PyOptix 实现。历史部分直接核验 Goal5838/5840 authorities、seal、challenge table、target checker 和内部 hostile review；证据部分读取两个最终原始目录及 cross-generation 目录。

审查中另有外部写入：12:52:19，目录新增 [署名 Claude 的同题报告][parallel-review]，56,623 bytes，首次观察 SHA-256 `10608221e7f9447bb706a2b30f1b7d17812f8147fb3aa17d9f834dcbeb294fa2`。本轮只读其头部以识别并避免覆盖，没有把它作为独立重算或科学结论的依据。因此本报告另取 `codex_review_...` 文件名。旧 scratch 的 SHA-256 为 `3c7946108fd72e17c2872fa0778d5073c248f5f1c39d2cc37b2948507f1a6b50`，同样保留。

本轮只创建本最终报告，不改源码、测试、实验、既有文档、memory、权威文件或原始证据，不启动 GPU/POD，不生成新的性能数据。

收尾快照（2026-09-06 13:06:40 America/New_York）：HEAD/tree 与开始时相同，tracked diff 仍为空；主稿、CFR、旧 scratch 和审查期间新增的 Claude 报告 hash 均与上述记录相同。工作区三项 untracked 分别是本报告、开始时的旧 scratch、审查期间外部新增的 Claude 报告；后两项均不是本次创建或修改。报告的 15 节顺序、五项行动上限、全部本地链接及行号已经检查。

## 2. 从零重述问题、贡献、非主张与截止日期

一个非渲染 RT 程序把计算分散在 host 输入／geometry／buffer／SBT、raygen、intersection、hit/miss、payload、continuation、状态和实际加载的 executable 中。各部分分别合法，不能保证它们对 item identity、结果完整性、状态消费和物理绑定具有一致理解。RTDL 的合理问题是：在应用已经选择 RT 映射后，把这些相互依赖的声明和产物组织成一个编译与准入单元，能否提前拒绝具体的全局不一致，并提供可检查的执行边界？

最强的一句话 thesis：**RTDL 对有限 OptiX 协议，将受限 Python callback、跨角色合同、物理绑定、状态发布与 executable identity 纳入同一编译／准入单元，通过共享的 schema-parametric 框架及可信特定拓扑 lowerer 实现和检查这些义务，并以有限扩展、结构检查和两项同合同任务量化其能力与执行成本。**

最多四项贡献：

1. 有类型、角色／effect／resource 边界的 Callback IR，以及明确分离静态准入、动态 native 状态和身份绑定的整体架构。
2. 一次预先封存三文件框架后，在作者定义十行域中选出的未实现组合扩展，公开特定 lowerer 的工作与 TCB 成本。
3. 与 production projector 分别实现的有限 target-structure 检查，以及其冻结 mutation liveness 结果。
4. 两个精确任务、两个 GPU 世代、同一源码的公开 prepared path 成本观察；明确其适应性工程过程、receipt 范围和不利生命周期诊断。

不支持任意 Python/CUDA、任意 Callback IR 的 GPU lowering、任意 topology、自动发现盈利 RT 映射、应用正确性、通用编译器 soundness、所有 failure path 完整清理、逐计时执行的独立物理证明、普遍低开销、内在语言速度优势、用户生产率或真实缺陷流行率。论文不需要靠新增应用、外部作者研究或缺陷 census 才能删除这些非必要主张。

内部不可逆代码冻结是 **2026-09-08 00:00 America/New_York**；目标投稿日期是 2026-09-10。冻结后只能执行已经提交的工具、保留／打包证据、缩小主张和编辑论文等。官方页面确认主文最多 11 页、参考文献不计，采用匿名评审；主文必须自包含。不能把本报告的关键限定全部埋入不保证被阅读的补充材料。[CGO 2027 投稿说明](https://2027.cgo.org/track/cgo-2027-papers)

## 3. 2026-09-05 Claude material findings 关闭表

“关闭”只表示相关事实／范围已经可裁决，不表示论文已经改好或自动获得发布授权。

| 旧意见 | 本轮裁决 | 当前剩余工作 |
| --- | --- | --- |
| P0-1：sealed core 不含 executable lowering | 接受观察，反对因此把整个 RTDL 判成非编译器 | 论文写清共享 admission/identity/lifecycle 与特定 lowerer；不能称 topology-generic lowering |
| P0-2：challenge domain 作者定义且窄 | 接受限制，不据此取消按该域预注册的检验 | 写明 4×3 组合、两个精确 exclusions、10 candidates、一次选行 |
| P0-2：旧 curve Boolean 可能令分母变成 9 | 事实反驳 | 旧项为 closest-hit，候选为 any-hit terminate；分母仍为 10 |
| P0-2／§6.6：全部候选四角色、没有 user intersection | 事实反驳 | 7 个 built-in 候选四角色；3 个 custom 候选有 bounds/intersection，共六角色 |
| 2,635 行 post-selection code 否定 prospective 性质 | 不接受该推论；接受实现成本及 TCB 限制 | 预注册允许 seal 外 provider/lowerer 实现，不能宣传自动生成未知 topology |
| P0-3：9.53x 被错误归因于全 device canonicalization | 机制措辞已由追加 correction 修正 | 保留历史精确 arms，排除内在 9.53x／最佳 PyOptix 主张；RTDL 仍有 native-host sort/unique |
| P0-3：仅 2x rows 不足解释 9.53x，所以结果／机制不可信 | 无这种因果上界；驳回 | native packed rows 与 Python 对象／set/sort 不同，缺 phase 因果分解，双方都不应猜分摊 |
| P1-1：当前 Goal5838/5832 custody 失败 | 已复现，历史范围可区分；文档部分关闭 | guide 仍遗漏 Goal5837/5843；不重封历史文件 |
| P1-2：Boolean collision route 没有 near-parallel admission guard | 源码缺口保留，fixture 范围可关闭论文风险 | [当前 case-study README][collision] 已明确靠构造避开；不得宣传通用 capsule／完整 RT-CCD |
| P1-3：native/raw bytes 在 Git 外 | 仍为交付问题；最终 Goal5848 的当前原始字节本轮可读 | 向 artifact reviewer 提供这些字节；旧 Goal5838/5840 缺失字节与重建不能混同 |
| P1-4：manuscript stale | 未关闭，仍是 P0 投稿阻断 | 更新全稿，不能只换一张性能表 |
| P2-1：provider identity 是 loaded-image identity | 接受范围限定 | 不声称每次执行重新读取磁盘 DSO/PTX；审查新增 lazy receipt 边界 |
| P2-2：app-vocabulary blacklist 很窄 | 接受，但它只是 hygiene | 主张 app-neutrality 应靠 ownership／call graph／source；不要求赶扩 blacklist |
| P2-3：package 保留旧 app vocabulary | 接受 artifact 分区问题 | V4 当前路线与 V1–V3 历史代码明确分层；不能由关键词直接推断新路线 app dispatch |
| P2-4：README dead links／packaging 说法 | dead links 已局部修复；pyproject 存在 | 离线依赖和当前 artifact 交付仍需说明；README 性能叙事仍旧 |
| P3-1：instrumentation policy 不对称 | formal A/B/C 开关政策已修复；实测覆盖不能夸大 | 512 个 ON/OFF qualification workers **仅测 A**，不是 A/B/C 都实测低于 5% |
| P3-2：sealed evidence 暴露 pod endpoints | 保留旧 seal；衍生匿名视图待交付 | 不修改 sealed authorities 去“匿名化” |
| Goal5848 尚为 0/2 formal generations | 两个同源数值实验已补齐 | 原书面 receipt 不变量与机器验收不一致，不能无条件称全部原约束已完成 |
| Goal5840 不是 pattern matching 而是一般 partial evaluator | 旧措辞过强；新 self-review 已正确缩为有限结构检查 | 论文吸收该边界，不能提升为 reachability／refinement theorem |
| 无 external human／无 prevalence | 限制仍为真 | 删除相应优势或流行率主张即可，不另开研究 |

## 4. 新增或重新确认的 P0/P1/P2/P3 findings

本轮计为 P0=1、P1=3、P2=5、P3=0 个独立条目。级别按投稿影响排列，不把条目数量当科学价值评分。

### P0-1：当前论文把过时的架构和性能实验写成当前系统

类型：**manuscript overclaim／事实失配**。阻断当前稿提交。

[main.tex:50][paper-abstract] 把整个 public surface 限于两种 geometry；[main.tex:651][paper-shape] 仍写 2/6、2/4 及零 frozen-core exam；[main.tex:1124][paper-perf] 到性能表仍是 324 workers、7,128 timings、单 RTX 4000 Ada、18 blocks 和旧 CI/gates；[main.tex:1564][paper-conclusion] 继续用旧结论。[paper README][paper-readme] 也宣称已有对应旧 anonymous artifact。§13 给出逐段 ledger。

需要精确改写：stable facade 的 **两个固定构造器仍正确**，不能机械改成三个；unbiased new-application exam=0 也仍正确。问题是把这些局部计数当成全 V4 能力边界，并漏报新证据。self-review 把“两固定构造器”孤立列为错误旧事实，同样需纠正。

### P1-1：receipt-before-publication 的书面不变量没有被当前正式快路径和验收实现

类型：**实现／书面合同不一致、evidence limitation、manuscript overclaim**。阻断“原全部 safety invariants 原样完成”的主张。

[GOAL5848.md:274][written-invariants] 明定输出发布前 dynamic native status 与 compact execution receipt 均须验证；同处 277–278 要求每次执行记录真实 launches、raygen count、traversable identity、output digest、monotonic execution identity。普通快路径的详细 operation receipt 在 [_DeferredFastOperationReceipt:5343][lazy-receipt] 才按需验证；[public replay:6274][replay] 先检查 compact 状态和可选 scalar oracle，随后已可返回输出，`traversal_receipt` 与 `output_sha256` 为 `None`。

[worker.py:168][sample] 逐次执行的验证只走 [output/oracle hash validator:268][output-validator]。正式样本后 [worker.py:482][diagnostic] 执行的是**另外一轮** diagnostics，再验证这份 traversal receipt。[contracts.py:627][rtdl-contract] 只要求这一份 diagnostic receipt，且明确接受／要求 `latest_output_sha256 is None`。全部 32 个最终 A workers 的 raw 文件均与此一致。

因此 [self-review:627][self-receipt] 所称 workers 在 timer 后物化并绑定“这些 receipt”不实。每次创建并暂存一个 raw ctypes object，不等于每次验证／持久保存完整物理证据；`_FastPathReceipt` 的结构也不包含完整的 per-execution traversable/output-digest/monotonic identity 集合。§11 给出本轮纯内存反例。

**必须追加协议偏离裁决，不能仅改一句 self-review 然后继续称原不变量全部通过。** 旧协议、authority、数据均保持原样。有限可用范围是现有机器合同通过、每次输出的 oracle 检查、同步 native/compact 状态及单独 diagnostic／timer-free witness。若坚持原逐执行证明主张，现有档案无法补出缺失证据，需要新实现和新取证；不能借当前 PASS 字符串代替。

这不是实际 GPU 返回错误值的证据，也不意味着 10,240 个 timing samples 被丢弃。它限制的是每次执行的证明与 publication 保证。

### P1-2：provider 初始化 bind/close 双故障仍会覆盖原错并丢失重试所有权

类型：**source/runtime defect**。阻断全面 failure-cleanup 保证，不直接否定成功 prepared samples。

[bind except:3078][bind-fault] 在重新抛原异常前做可能再次抛错的 release；二次错误会跳过后续状态清理。[close:3096][close-fault] 在实际 release 前先清空引用并标成 CLOSED，release 失败后第三次 close 直接返回。本轮注入原 descriptor failure 与真实内部 `_remove_native_cache_lease` failure，重现 `BINDING → CLOSED`、原错被覆盖、active lease 仍在、第三次 close 没有重试（§11）。

可删除／限定复合失败清理承诺并披露，不必为成功 public execution 成本这一有限主张修改已完成两代的源码。把“close destroys the owner”写成无条件全路径保证则不成立。

### P1-3：当前可复核证据不等于已交付、完全可迁移的投稿 artifact

类型：**evidence/custody limitation、artifact usability**。

最终 archive 本轮完整可读，但单代 full-authority builder 仍解析 pod 的绝对 artifact 路径（[builder:190][authority-path] 及同文件 `build_authority`）。把目录搬到 Mac 后，manifest 和 worker/gate recount 可执行，不等于原 full authority 已在任意新根路径重建。[custody guide][custody] 缺少当前 Goal5837/5843 的预期失败映射；旧 Goal5838/5840 的 Git-only 历史原始二进制可得性亦须单独说明。最早两份 `d29c0b79...`、`fde22b987...` 失败 archive 未在本轮指定证据根目录的 `.tar.gz` inventory 中找到；有报告引用，但本轮没有重哈希这些原始包，不能签认完整失败链均已核实。

最小关闭条件是交付精确字节及可运行、明确分层的核验入口；可以如实只承诺 portable manifest/worker recount，而不实现新的通用 path-rebasing 系统。不能把当前 Mac 成功 recount 宣传为新 GPU 重演或完全独立硬件 attestation。

### P2-1：适应性任务工程与残留 baseline 实现差异限制外推

类型：**experiment-design limitation**，通过明确范围即可关闭。

[repair report:327][repair-final] 明确记录看到 RTX 4090 分解结果后继续优化同一 triangle 任务。最终两个正式交易独立新取样且同源，并未因此成为对任务选择和实现选择 outcome-blind 的试验。C 也不是最佳可能 PyOptix 下界：relation 每次 `lexsort/tolist/list` oracle，而 A 可在新 packed bytes 相等时复用已验证 tuple；triangle C 保留／清零 per-ray device intermediate，A 的 scalar 路线不同。见 [PyOptix:1241][pyoptix-relation]、[runtime:5855][row-reuse]、[PyOptix:1504][pyoptix-triangle]。

同语义／同输出／同生命周期边界成立，不等于每一个 host/device 操作相同，更不能因果归因于 Python 语言、DSL 或检查本身。无需赶改 C 再重启整个实验；删去最优／通用／纯语言因果主张。

### P2-2：cached PID 不能拦截绕过 Python at-fork hook 的 native fork

类型：**source/runtime boundary defect**。

[PID hook:239][pid-hook] 更新 `_NATIVE_IMAGE_CACHE_PID`；[prepared check:6184][pid-check] 直接比较该缓存值。子进程由 Python `os.fork()` 创建时拒绝 RX038；由 `ctypes.CDLL(None).fork()` 创建、绕过 Python hooks 时，mock native 的同一 public execute 被接受。测试没有启动 GPU，证明的是 process gate 可被这种合法但不受支持的 lifecycle 绕过；不是已测 GPU fork 成功。

限制为受支持的 Python lifecycle，明确禁止 inherited GPU owner 在 native fork 后复用。不能继续声称任何跨进程使用都必在 native entry 前拒绝。正式 workers 未 fork，这一边界不取消其数据。

### P2-3：审查包 Ada hash 抄错，Direct worst-block 误述未在所有下游记录中消失

类型：**evidence/custody 文档缺陷**。

[CFR:228][bad-hash] 与 [self-review:308][self-hash] 的 Ada archive SHA 只有 63 个十六进制字符，漏掉 `...3262c0...` 中的一个 `2`。本轮实际归档 SHA 是 `c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced`；raw `.sha256`、AGENTS 与 final report 的 64 位值正确。没有发现归档损坏。

新 final report 已纠正 A/D 没有 1.35 worst-block gate；但 [triangle repair report:180][repair-errata] 和同文件 220–222 仍保留把 Direct worst block 与 1.35 比作 gate 的历史措辞。应追加明确 erratum 并禁止下游复用，不能偷偷改旧数字或旧 authority。Goal5850 的那三个超 1.35 block 也不能又写成两个。

### P2-4：Goal5840 有用的独立结构检查仍不是控制流／语义证明

类型：**design/evidence limitation**。

本轮把 frozen bounded-relation wrapper 的 any-hit 开头插入无条件 `return;`，[_bounded_partial_evaluation_effects][checker-effects] 和 [_check_wrapper_status_flow][checker-flow] 仍接受原 effect／status 结构。它检查有限 source anchors、数量和位置，未证明 reachability、dominance、一般数值语义或 binary correctness。新 self-review 已正确承认，旧 adjudication 的 partial-evaluation 描述不能直接进论文。无需升级为完整 C++ verifier；缩为 finite structural check。

### P2-5：instrumentation qualification 仅覆盖 RTDL，不能据此宣称所有 Python arms 均低于 5%

类型：**experiment-design／evidence coverage limitation**。

[contracts.py:218][instrumentation] 的 schedule 为 2 tasks × 8 blocks × 2 modes × 16 replicates=512；其 endpoint 明确是 RTDL implementation-entry。原始文件中的全部 instrumentation workers 都是 `A_RTDL_AOT_PUBLIC`；[authority builder:571][instrumentation-arm] 也要求 `worker.arm == RTDL_ARM`。

formal A/B/C 的 `phase_instrumentation:true` 表明开关政策一致，不证明 B/C 各自 ON/OFF overhead 通过。此差异不改变已经按同一 committed timer 得到的数值，但新 self-review 关闭表的“双边 policy 和 paired qualification”应拆开。A/C entry 比较应保留这一测量限制；不可把只对 A 的 512 次资格试验计为三 arms 全覆盖。

## 5. Architecture／generality 判决（Q1–4）

**bounded whole-protocol compiler 可成立；topology-generic executable lowerer 不成立。** schema 层按结构核对 instance/参数/角色合同，产生规范计划（[schema:1210][schema]）；generic lifecycle 从节点、角色、channel、operator contracts 抽取 provider requirements，并经 SPI 核验 descriptor/projection/plan/target 身份（[lifecycle:367][generic]、同文件 983）。

这条框架本身不合成任意拓扑程序。但完整系统确有 source→typed IR→ABI→Numba leaves→PTX composition→OptiX wrapper 的编译链，[sphere compiler:123][sphere-compiler] 是具体可执行例子。[sphere wrapper:287][sphere-wrapper] 固定 flags、payload/output 布局和 continuation，必须纳入 TCB。新增特定 topology 仍需大量 provider/lowerer/native 工作，不能把 SPI registration 说成自动 lowering。

贡献的判断依据是哪些分散片段之间的义务被显式表示、比较并约束 executable，不能由 JSON、代码行数、测试量或模板数量直接裁决。compiler label 也不自动证明 novelty：论文必须把具体残留问题与 typed OptiX、OWL 等已有 interface／construction 检查对照，避免把既有系统说成“完全不验证”。production projector 共源和离线 checker 分别实现是两个事实，不可互换。

当前论文的主要 architecture 错误是过时范围与遗漏，非新出现的大量正向 arbitrary 夸张。应保留 arbitrary IR 不支持、opaque proof truth 仍为假设、TCB 包含 compiler/native/driver/GPU/host 的限定；新增 §4 的动态 receipt、fork 和 cleanup 边界。

## 6. Goal5838 有限 prospective exam 判决（Q3–4）

本轮从 [CHALLENGE_TABLE][challenge] 重数 10 行；7 个 built-in 四角色、3 个 custom 六角色。旧 curve Boolean 在 baseline `0f5c9d4297f73e412732e5a8ab133423fe4cfd21` 的 `v4_builtin_curve_standard_library.py:96` 为 closest-hit，与 any-hit terminate 候选不同。NIST 选行限制冻结后的任意挑选，不消除作者对候选域的设计偏好。

本轮直接 `git show 7da68056550818d8e2f6cdb4d7aa3e9029cc4524:<path>` 核三份 frozen core 的长度和 hash，全部一致；[authority verifier][g5838-builder] 返回 `PASS__GOAL5838_COMPLETE_AT_PREREGISTERED_BOUNDED_SCOPE`，seal `c0578a22e006e2bee2dec39e6de98201ce547eca95dc20b6b7f4c1a891479a8e`。authority 支持 one selected sphere any-hit-count composition、12 oracle rows、2 true-OptiX launches。

该结果是**历史 exact commit 上，一次 narrow-domain prospective composition 成功**。[预注册:50][g5838-prereg] 允许 seal 外 provider-specific implementation，所以约 2,635 行扩展成本不违反注册；它也证明不了任意新 topology 无需编写 lowerer。当前三文件后来改变，与历史零字节变化并不矛盾。新论文应同时报告 narrow composition exam=1、unbiased new-application exam=0、external human author=0。

## 7. Goal5840 independent checker 判决（Q5–7）

本轮 [final authority verifier][g5840-builder] 通过，seal `3857a8c1f579808ea96a2f54c58e5698818deae7b879c849523ccf72a3f59a80`。范围为 3 route groups、4 modes、5 property classes、20 property applications、15 unique frozen mutations across 20 applications。

它不 import `rtdsl`，拒绝直接相信 compiler 提供的 projection，并从目标 source/ABI/PTX/host-order anchors 独立构造有限检查，减少了直接调用同一个 projector 的循环性。它仍共享作者、布局／wrapper 假设与 produced evidence 的可信环境，不是独立硬件鉴证。

本轮 early-return probe 只在内存修改 frozen mode-01 wrapper 字符串：在 `__anyhit__rtdl_v4_bounded_relation()` 起始插入 `return;`。effect helper 仍报告 `any_hit=('accept_continue',)`；status-flow helper 仍通过，只改变 offset。这是结构分析的反例，不是完整重封 bundle 的 authority bypass，不推翻原 15 mutations 的拒绝结果，也未证明历史 GPU 输出错误。

允许术语：**分别实现的、针对有限 specialized target 的结构一致性检查**。不允许：一般 partial evaluation、完整 compiler refinement、控制流支配／数值／binary 正确性或 arbitrary Callback-IR soundness。当前 [historical hostile review][g5840-hostile] 本来就承认这些边界，主文应直接吸收。

## 8. 每个 arm／task 的同合同与公平性判决（Q8–13）

名字含 `RELATION_COUNT` 不能把任务写成只返回 scalar count。[TASK_CONTRACTS:121][task-contracts] 指定 relation 输出 `canonical_u32_pair_rows.v1`，4,096 行、32,768 bytes；triangle 输出 checked-U64 scalar，8 bytes、冻结期望值 65,530。输入分别为 4,096×4,096 的构造 AABB workload 与 16,384 triangles／queries 的 weighted all-hit workload。两者都是刻意设计的有限数据，不代表一般 sparse/dense relation 或 arbitrary mesh 分布。

| Arm | Triangle 实际合同 | Relation 实际合同 | 比较角色与界限 |
| --- | --- | --- | --- |
| A public RTDL | checked-U64 reduction、8-byte scalar、1 OptiX launch 的路线 | canonical pairs、2 OptiX launches、device dedup＋native-host 最终排序／去重 | 被测 public prepared path；同步状态／oracle，详细 receipt lazy；不是全部书面 receipt 保证 |
| B idiomatic pinned PyOptix | 同一 exact scalar，采用 pinned 实现 | raw duplicate events 在 host canonicalize 后同一 rows | idiomatic competence reference；不单独用其弱 host continuation 推 intrinsic RTDL speedup |
| C strong PyOptix | device scalar continuation、无 per-ray D2H、同一 scalar | device compaction 后转同一 canonical rows；仍有 Python/NumPy host 操作 | 明确比 B competent；不是全局最佳 Python/OptiX 实现下界 |
| D Direct CUDA/OptiX | 同合同 scalar/status/同步边界 | 同合同 rows/status/同步边界 | prepared steady 低层 reference；无需承担 RTDL DSL admission，本来就用于衡量上层总差异 |
| E frozen predecessor | 相同 task/input/output | 相同 task/input/output | 同机器历史实现回归控制；不能作为另一 GPU 的替代样本 |

steady 样本排除离线 source build，以及已经完成的准备、首次动态上传／GAS 构建，测量复用已准备状态到公开结果的执行；没有用 native-kernel-only 时间假装 public RTDL 时间。部分动态上传／GAS 构建在第一次 execution 才发生，不能把所有这些工作统称为 prepare 函数内部。各任务／arm 的外部 correctness validation 也由 worker 执行，但实现内部验证／materialization 开销并非逐操作相同。A relation 的 byte equality reuse 仍读取新输出字节，不是直接缓存旧答案；C 可保持更高 Python object 成本。这些事实允许比较命名实现，禁止把差额全归语言或 semantic checks。

源检查未发现 final d653 修改 workload、native traversal 或加入 app-name dispatch。v9 API 验证 32-byte digest、count／mode／输出指针；native owner mutex 内核验缓存已提交及 exact digest；同一 immutable batch 才走 public replay，等值不同对象仍经 digest 路径。thread/reentry/closed-owner 与错误清空 replay eligibility 保留；process 保证有 §4 P2-2 限制。

A/D **只有中位数 ≤1.20** 的工程门槛，作为这两个任务可接受的 observed median tax 可以报告；它不是每个 block／每次调用的 latency ceiling，也不证明统计非劣或未来任务开销上界。A/C implementation-entry 才具有 median≤1.20、worst-block≤1.35 的组合门槛。不能借用该 1.35 为 Direct 构造不存在的成功条件。

## 9. Goal5848／Goal5851 原始证据重算与性能判决（Q18）

本节数字从 retained worker `samples_ns`、schedule、process/receipt、manifest/archive 字节重建，未用报告表替代。机器合同的 validators 作为另一路一致性检查；独立实现 estimator 的重算没有调用 controller 的汇总函数。

### 9.1 字节、源码、环境及分母

直接审计目录为 [Ada raw][ada-raw]、[Ampere raw][ampere-raw]、[cross-generation raw][cross-raw]。

| 项目 | Ada | Ampere |
| --- | --- | --- |
| GPU | GeForce RTX 4090，CC 8.9 | GeForce RTX 3090，CC 8.6 |
| UUID | `GPU-01a12a86-b470-30ee-c81c-272e3b8fb6d7` | `GPU-eda7acdc-0cc5-6c7f-689f-e8c6831f3b63` |
| driver | 580.159.04 | 580.159.03 |
| archive bytes | 37,253,048 | 37,236,329 |
| manifest-bound payloads | 2,405 | 2,405 |
| payload bytes | 125,718,265 | 125,646,793 |
| tar regular files（含 manifest） | 2,406 | 2,406 |
| 解包 payload／tar 内 payload 的长度或 hash 不匹配 | 0 | 0 |
| 正式 schedule cells／worker IDs／process records | 80／80／80 | 80／80／80 |
| 正式 steady samples | 10,240 | 10,240 |
| 正式 retry／discard | 0／0 | 0／0 |

10,240 是 **五 arms 合计**：2 tasks×5 arms×8 blocks×128 samples；每代 A 只有 2,048 个 steady samples，两代 A 合计 4,096，不能把全部 20,480 都称为 RTDL executions。每个 worker 有 16 warmups、128 measured samples；warmup 不混入 estimator。正式 process exit 全部为 0，stderr 为空，stdout 与对应 worker JSON 相同，相关 process/worker seals、stdout hashes 复算一致；没有缺失／重复 schedule cell。

每代 A/B/C/D 共 64 个 worker 的源码／tree 为 d653；E 的 16 个 worker 为前驱 `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`，tree `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6`。这是有意的 regression arm，不是混源错误。preregistration、manifest、transaction、authority 的内部 seals 也重新计算通过。

| 字节对象 | 本轮 SHA-256 |
| --- | --- |
| Ada archive | `c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced` |
| Ampere archive | `7bbabfc8d1d9dfd3cc9bd701bd7f40e9f50c8ccfcbbac9504db43e9e42b7c2a2` |
| Ada authority＝recount | `191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7` |
| Ampere authority＝recount | `35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3` |
| cross authority＝recount | `99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692` |

cross builder 在本机现有原始证据布局下**纯内存重新 build**，与存档完全相等，seal `0ec93d9e529a3ff3dc4a09a178b3c1c5eaf2aa930352777917c8753a7b748d9b`。保留 `cross_machine_raw_time_ratio_computed:false`、`external_review_complete:false`、`public_or_manuscript_claim_authorized:false`。两个单代 full-authority 原样搬迁重建则实际抛 `FileNotFoundError: '/workspace'`；cross 此次可重建不等于任意 relocation 都成立。

### 9.2 从所有原始 samples 重建 estimator 与 gates

先分别排序每个 worker 的 128 个 ns samples，以偶数中间两项整数均值取得 worker median；每 block ratio 使用 `(numerator * 1_000_000 + denominator // 2) // denominator` 四舍五入为 ppm；八个 block ratios 的中位数再取整数下整。不是 pooled arm medians 相除，也不是旧稿 18-block bootstrap CI。本轮全部 160 worker medians 与原收据相等；独立结果与机器 evaluator、两 transaction recount 和两 authorities 均一致。

| GPU／task | A/D steady median | A/D max，仅描述 | A/C entry median | A/C entry max | A/C old post-import median | C/B steady median | A/E steady median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ada triangle | 1.175066 | 1.211025 | 0.642180 | 0.650937 | 1.559788 | 0.602851 | 0.903016 |
| Ada relation | 1.076852 | 1.092253 | 0.653826 | 0.719416 | 1.749327 | 0.220775 | 0.584438 |
| Ampere triangle | 1.133636 | 1.142675 | 0.618362 | 0.681696 | 1.637468 | 0.654279 | 0.922388 |
| Ampere relation | 1.094795 | 1.118811 | 0.681393 | 0.911861 | 1.837415 | 0.226921 | 0.608228 |

全部 A/D blocks，按登记 block 0–7：

| block | Ada triangle | Ada relation | Ampere triangle | Ampere relation |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1.173303 | 1.092253 | 1.135639 | 1.094816 |
| 1 | 1.211025 | 1.081622 | 1.130437 | 1.094538 |
| 2 | 1.176830 | 1.071687 | 1.141042 | 1.094775 |
| 3 | 1.171694 | 1.066402 | 1.142675 | 1.101122 |
| 4 | 1.188183 | 1.081821 | 1.132267 | 1.091728 |
| 5 | 1.178393 | 1.079510 | 1.135005 | 1.118811 |
| 6 | 1.158989 | 1.074195 | 1.131221 | 1.100408 |
| 7 | 1.161689 | 1.067929 | 1.124331 | 1.087112 |

四个 A/D medians 均 ≤1.20；Ada triangle block 1 为 1.211025，仍保留。这不是违反登记门槛，因为 **A/D 没有 worst-block gate**。A/C entry median≤1.20、max≤1.35；C/B 与 A/E steady median≤1.05，均通过。旧 post-import diagnostic 四行均不利，不能声称 parity。所有 ratios 都在同一机器内计算。

### 9.3 Instrumentation、AOT、competence 与 build derivation

两代合计 1,024 个 instrumentation workers 的原 worker/process/stdout/stderr、seals、source/tree/hardware、ON/OFF schedule 与 endpoint 分解重新核对。每代 512 个均为 A；这不是另 512 个 B/C trials。按登记 paired estimator，`max(0, median(block median-on/median-off)-1)`：

| GPU／task | A instrumentation overhead ppm | AOT fresh-hit median ns | AOT hit/cold ppm |
| --- | ---: | ---: | ---: |
| Ada triangle | 2,349 | 76,826,501 | 20,166 |
| Ada relation | 2,781 | 78,176,935 | 11,171 |
| Ampere triangle | 0 | 58,513,283 | 19,626 |
| Ampere relation | 2,431 | 58,279,761 | 10,431 |

A instrumentation 均 ≤50,000 ppm。每代 AOT 10 个 fresh-hit workers（每 task 5，10 distinct PIDs）均 exact hit、producer 未调用、compiler modules/NVRTC mappings 前后皆空；identity 和 seals 正确。hit median 均 ≤1 s 且 ≤cold 的 100,000 ppm。这些资格时间没有进入 formal estimator，也不能当 first-ever compilation 成本。

每代另四个 nonformal competence workers 为 B/C×2 tasks：Ada triangle C/B=0.599132、relation=0.222572；Ampere triangle=0.655328、relation=0.223010。formal C/B 见上表，两组均说明 C 在此 workload 下 competent，非证明最优。

每代 current/predecessor native build 各 12 个 source inventory entries 与对应 Git blobs 的长度和 hash 全匹配，build 前后 commits 一致且 clean。DSO 本体与 manifest 一致：

| native DSO | SHA-256 |
| --- | --- |
| Ada current | `6081c3637548e6ab0d149fce15137cfe565a61d780c1dfdaf545d45ddaa889d2` |
| Ada predecessor | `8b4a52092b50c700b25a431ac7b70dcf47f64df5a135e714f138040c6661f79c` |
| Ampere current | `afc64283a83a96cb0ec34a92cfe0691a5de055987f735a83bac249bfdd57385a` |
| Ampere predecessor | `f2f482d12ed479d683f28fb9a8afecfbe7ef580bdcc488bf3c69dfa3e6a3789a` |

每代 device artifact receipt 的三个 sources 与 d653 Git blobs 一致。Direct 的两处计数替换（warmups 8→16、reps 64→128）从 pinned parent Git blob 独立重做，与 raw derived `direct_worker.cpp` 字节完全相同，include `direct_optix.cpp` 也匹配：parent SHA `078570a19000221890bd5421676c8d4857fd2196c5b7daae60eec7d511ffd165`；derived SHA `f673cc72d375fbc571353ce0906d3f1dceb8a58c142926b4fc5d38357e66f5ec`；两代 Direct binary SHA 同为 `4194550a54b157bfbb926f70da54d622a68619019d0ff3455645bffbb4652e0f`。这些证明 derivation/custody，不替代语义／计时边界判断。

### 9.4 Receipt 与失败链的可签认范围

32 个 A workers 均只持久记录一次 separate diagnostic receipt；triangle 为 1 successful launch／16,384 raygen，relation 为 2 successful launches／8,192 raygen。各 worker 都有 128 个 durations，但没有 128 个详细 timed operation receipts。可直接查看 [Ada triangle raw worker:47][raw-receipt] 及同文件 136 的 `latest_output_sha256:null`；worker 的 `output_sha256` 本身正确且非空，不能混为一谈。按当前程序 output validators，全部 workers 成功；这不能反向证明原书面逐次 physical receipt 条款已满足。

本轮另实际查到并重哈希的 adverse archives：

| retained transaction | archive SHA-256 | formal worker 文件数 |
| --- | --- | ---: |
| 8f7b640a Ada failure | `412454f05b6bebbc0419f2468a7a7462248a5a1c613b53bd675dc99107d8f707` | 80 |
| c4351f612 Ampere failure | `0997542ff5d3638baba4771b3f83776fe1c69043dc29c48d1634af9494e20b83` | 80 |
| 12ab7b49c Ampere failure | `182043089d16d36cda9f613c86d3592b3bbe7b7bcaa1bb843ab9ff4441acfe60` | 80 |
| a4dd1d5d Ada failure | `76e3c1a01891a66dd7505fde079c4746ee43ce99245a8dbf12c56943e054f885` | 80 |
| a4dd1d5d preformal Direct-build failure | `c06586766e3808d98c86aa05578885e9be687514d3bd724139a6122770ac6789` | 0 |
| a4dd1d5d preformal safe-directory failure | `c92dc5530ceeaf6862b9c6461772c9c1549405cbf083355eea853017a75f9bf5` | 0 |

历史 c4351 Ada pass (`f487f42580ac8cb81c202fe867b976ba7a267b9ca7ccffb980c626d775b112c8`) 与 a4dd1 Ampere pass (`a1b8300ab32ec8a846e82d1e6efde29c234718748415287293d76a903b25d824`) 也重哈希一致；它们没有进入最终 d653 两代的 schedule。a4dd1 Ada triangle 的 1.249928 失败仍保留，不能拿该源码的 Ampere pass 与 d653 Ada pass 组成成功。

最早 `d29c0b79...` post-import failure 与 `fde22b987...` authority failure 在报告中有引用，但本轮遍历 `/Users/rl2025/RTDL_evidence` 的 `.tar.gz` inventory 未取得原 archive，故不签认已逐份核验完整失败链。这个范围说明不证明它们在全机丢失；artifact 必须提供准确位置／原包，或披露只能审阅其存留记录。最终 Ampere 初次错误 cwd 的 launcher invocation 按 retained report 在创建 worker 前失败，应标作已披露的 invocation error，不能伪装成正式 sample retry；本轮未独立重演该远程启动。

**性能判决：数值 gates 与已保存样本结构 PASS；原书面 receipt invariants 不能签认为原样 PASS。** 保留两项任务在两代精确 source 上的 limited public-path observations，追加 §4 P1-1 的协议偏离裁决后方能用于相应窄主张。

## 10. Endpoint 与 adaptivity 判决（Q14–17）

新的 implementation-entry endpoint 是可辩护的实际用户路径：在 implementation-specific import 之前开始，到第一个 exact result 被验证结束。[worker:216][endpoint] 记录并校验 `total = import + gap + post_import`，没有把 gap 消失掉。旧 pinned PyOptix import 会创建 CUDA context，而 RTDL import 保持 lazy；所以旧 post-import endpoint 的起始生命周期状态不同。[lifecycle repair:117][lifecycle-repair] 显式版本化这一修正并保留旧诊断，是必要条件。

本轮直接从 Ada archive 保存的 `pyoptix-source.tar.gz` 读取源码，`src/optix/__init__.py:25` 导入 `_optix`，`src/main.cpp:2331–2332` 在模块初始化调用 `cudaFree(0)` 和 `pyoptix::init()`，支持该 import side effect 的源码解释。本轮没有再次执行其八个 fresh-process CUDA probe，也不把 repair report 的 485.4 ms 等诊断当成本次独立测量。

这不使旧 adverse result 变成不存在，也不使新 endpoint 变成纯语言／编译器 speedup。若主文报告 entry 优势，应并排保留 import／gap／post-import 分解及四个仍不利的旧 ratios。first-ever build/sign/cache-fill 和 deployment/prepare 也须独立交代，不能用 AOT 缓存命中代表首次从源码部署。

保留失败、独立新注册和完全新样本，比丢弃坏行强得多；但多次看到任务结果后继续修改实现，最终两个正式运行仍是**对已反复优化任务的 fresh engineering-gate validation**。不能称 outcome-blind confirmatory trial、unseen-workload test 或普遍 overhead 估计。

“整个修复链 thresholds/workload/arms/timer/estimator/sample-count 从未变”也不应不加时间范围地写：历史中已有 instrumentation estimator/replicate 修正和显式 lifecycle endpoint successor。对最终 d653 两代，合同一致；对后段 prepared-replay 实现修复，相关 workload/arm/timer/gates 保持；对更早历史，则逐项列版本化变更和保留失败。最后两代不与旧 c4351f612 或 a4dd1d5d 的有利结果拼接。

我接受双 endpoint 的描述性分析与该任务上的工程门槛结果。保留失败和冻结门槛限制选择空间，但不能数学上消除多轮实现选择造成的 adaptivity。八个 block 才是 ratio 汇总单位，128 次 steady repeats 不能被写成 128 个独立机器／任务复现。

## 11. Provider 双故障、lazy receipt 与 failure semantics 判决（Q11–12、Q22–24）

同步成功边界仍有源码支持：[native:5444][native-status] 先同步控制状态；检测 error/overflow 后，在 scalar D2H 前返回；成功才复制 scalar 并再次同步。public fast replay 检查 native return、compact status 和提供的 oracle；formal worker 再比较 frozen output/hash。故意让 mock native 返回错误 scalar 或非零 compact status 仍会被拒绝；不能把 receipt 缺口写成“没有任何正确性检查”。

本轮额外控制检查：closed owner→RX037/native calls=0；reentrant→RX040/0；other thread→RX039/0；nonzero compact status→RX035/1。指定 `tests.goal5851_triangle_fused_replay_test` 为 7/7 PASS。这些是当前 Python/ABI mock 验证，不是新 GPU 结果。

以下是本轮 root 也重放的最小 lazy-receipt probe。它使用现有 fixture，native 完全 mock；计时数值不作为性能数据：

```python
import ctypes
from unittest.mock import patch
from tests.goal5851_triangle_fused_replay_test import _batch, _owner, _publish_success
from rtdsl import v4_rtdlexe as r
from experiments.goal5848_strong_baseline import worker
from experiments.goal5848_strong_baseline.workloads import triangle_workload
from experiments.goal5848_strong_baseline.contracts import TRIANGLE_TASK

expected = triangle_workload().expected_reduced_u64
batch = _batch(expected)
owner = _owner(batch)
def replay(*args):
    _publish_success(args, value=expected)
    receipt = ctypes.cast(args[7], ctypes.POINTER(r._FastPathReceipt))[0]
    receipt.status_before_output = 0
    return 0
owner._execute_replay = replay
prepared = r.PreparedRTDLExecutable(
    family=r._TRIANGLE, executable_identity_sha256="a" * 64, owner=owner)
with patch.object(r, "_validate_fast_operation_receipt",
                  wraps=r._validate_fast_operation_receipt) as check:
    summary, latest = worker._sample(
        lambda: prepared.execute(batch),
        lambda result: worker._validate_rtdl_result(TRIANGLE_TASK, result, expected),
        warmups=1, repetitions=2)
    print(len(summary["samples_ns"]), check.call_count, latest.device_status["ok"])
    try:
        dict(latest.device_status)
    except r.RTDLExecutableError as error:
        print(error.code, check.call_count)
```

在兼容 Python 3.12、`PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1` 下得到：`2 0 True`，然后 `RX035_DEVICE_STATUS_INVALID 1`；发布对象 `traversal_receipt=None, output_sha256=None`。这证明详细 receipt 没有被真实 worker 的 output validator 自动验证。fake native 必须属于可信计算基之外的注入假设，不能据此称真实 archive 中 GPU 实际违规。

双故障的独立复现使用现有 `Goal5847AotProviderInitializationTest._resources/_deployment_and_loaded/_patches`，在 `begin_provider_initialization` 完成后注入 `_validate_native_provider_descriptor=ValueError('ORIGINAL_DESCRIPTOR_FAILURE')` 与真实 release 内部 `_remove_native_cache_lease=RuntimeError('SECONDARY_RELEASE_FAILURE')`。依次 `bind`、`close`、`close` 得到：

```text
bind: SECONDARY_RELEASE_FAILURE; is_original=False; state=BINDING; releases=1
close: SECONDARY_RELEASE_FAILURE; state=CLOSED; refs_cleared=True
active_lease_retained=True; release_phase=PROVENANCE_UNREGISTERED
third close: releases still 2, no retry
```

它是实在的实现缺陷，但没有发布成功输出，也不在正式 prepared timer 内。**本次最小处置是明确删除全面复合失败 cleanup／retry ownership 保证，保留经验证的普通单故障与同步状态边界。** 不需要以“不惜重跑两代”作为有限论文必备条件。若作者选择修代码，已有两代只能证明 d653；任何新源码应显式区分，不能把修复后代码与旧时间混称同一精确实现。

同理，receipt 问题可以通过明确承认协议偏离并缩小本次性能／执行证明主张来处理，不能把“详细字段只是 bookkeeping”当作原协议已经履行的替代论证。原书面 invariant 的目的就是要求该证据边界；重新分类必须明示为本轮裁决，不是追认原样合规。

## 12. Artifact、custody 与 replay 判决（Q19–21）

本轮按要求运行最低验证集合，环境为 `/Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python`，均使用 `PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1`：

| 命令尾部 | 本轮结果 | 判断 |
| --- | --- | --- |
| `-m unittest discover -s tests -p 'goal5848*_test.py'` | 128/128 PASS，11.532 s | 当前 focused evidence |
| `-O -m unittest discover -s tests -p 'goal5848*_test.py'` | 128/128 PASS，11.521 s | 关键拒绝不只依赖 Python assert |
| `-m unittest tests.goal5851_triangle_fused_replay_test` | 7/7 PASS | 当前 replay/mock ABI 范围 |
| `-m unittest tests.goal5838_core_seal_and_selection_test` | 9 tests，8 pass／1 error | sealed file drift 首见 `v4_family_schema.py` |
| `-m unittest tests.goal5832_protocol_shape_algebra_test` | 23 tests，22 pass／1 error | `goal5831.source_authorities[1] byte count drift` |
| `scripts/goal5837_freeze_owner_grouped_classification.py --verify-stored` | exit 1 | `AUTHORITY_CURRENT_INPUT_MISMATCH` |
| `scripts/goal5843_build_final_authority.py --verify-stored` | exit 1 | `preregistration differs from canonical builder` |
| `scripts/goal5838_build_final_authority.py --verify-stored` | PASS | 历史 authority，非当前三文件 byte-identical |
| `scripts/goal5840_build_final_authority.py --verify-stored` | PASS | 有限结构证据 scope |

未再跑 broad all-history discovery。self-review 报告其 13,638 tests、756 failures、6,214 errors、600 skips；本轮没有取得该完整原始日志逐错归类，故不将这些计数列为本轮独立验证事实，也不接受把全部 6,970 errors/failures 无条件称为 harmless。已重放的四种历史失败有明确原因，但不足以归因整套红色测试。

必须分成：当前源码 CPU gate；对应 frozen commit 的历史 replay；NVIDIA/Linux/GPU 平台 gate；可选 app/reproduction 数据依赖。各层写清环境、退出码和已知例外。不能只给一个很窄的绿色测试命令却暗示全部仓库健康；也不能要求 deadline 前修好所有历史缺件作为当前 V4 的先决条件。

Goal5832 自报 `BROKEN_BAD_OBJECT_HEAD_NO_COMMIT_CLAIM`，不能杜撰完整历史 commit；Goal5838 有可用历史 commit 和本轮核对的 seal，但其 7,181,936-byte DSO 不在 Git；Goal5840 的 DSO 和 raw capsule 也有 off-Git 边界。Goal5837/5843 的当前重建读了改变后的输入，应在 exact snapshot 解释，不能重封旧 authorities 获得表面绿色。

当前两代原始 archive 的可读性和完整性是实质进展；它们应成为精确离线复核 payload。逐 worker／gate 的 portable 重算与 full-authority pod-absolute 路径限制可以并存。包装若只承诺前者且给可复现命令，已经足够支持相应有限数字主张；不能宣称完整 relocation 无条件成立。没有给每个 timed sample 的 receipt 是源合同范围问题，不能由重新打包生成缺失证明。

## 13. Manuscript claim ledger（Q25–28）

“supported”是本轮技术裁决，仍需由项目吸收 review、追加差异裁决并冻结 claim ledger；不自动改写 authority 的 `external_review_complete:false` 或发布权限。

| 当前位置／主题 | 分类 | 必要最终表述 |
| --- | --- | --- |
| Abstract 44–52；intro 128–141；contrib 145–163 | **supported only after rewrite** | bounded whole-protocol compiler；stable facade 两 fixed constructors 与后继 schema/provider routes 分开；全 V4 bounded primitive presence 为 4/6 build-input kinds、4/4 leaf kinds，非 feature-complete OptiX |
| 54–65、164–169、1017–1028 的 19 leaves／5 fault realizations／3+1+1 residual | **支持历史限定，不能升级计数** | 具体历史 source/inputs/profile；不因新 goals 加进这些分母。未在本轮重演这些 GPU faults，保留其原 authority 范围 |
| 70–72、1111–1115 的 unbiased new-application=0 | **supported，应保留** | 与一次有限 topology composition exam 并列，不能机械改为 1 |
| 538–545、632–638 的全局排除 curves/spheres/new topology | **supported only after rewrite** | 对旧 stable route 的限制可保留；全 V4 已有有限 sphere/curve routes，arbitrary verified IR 仍不支持 |
| 609–623、936–940 的 stable fixed constructor=2、template=1、human=0 | **supported，应保留类别** | 不能把 owner-grouped successor 加成 stable constructor=3；不能把 topology 当新 Paper App |
| 651–678、934–939 的 geometry 分母和零 frozen-core exam | **supported only after rewrite** | 分母平台 enum=6/leaf=4；kind presence 按所选 facade/全 V4 明标；历史 narrow prospective exam=1 |
| 452–454、711–720 的 production projections 共 TCB | **supported，应保留并增补** | production 仍共源；另介绍 Goal5840 offline independent finite checker，不能把前者改写成后者 |
| 587–599、625–630、723–728 的每次 identity／status／receipt 保证 | **supported only after rewrite** | loaded image identity 与 per-call native/compact status；详细 receipt lazy，formal worker 单独 diagnostic；不得说每次磁盘重哈希或逐执行完整证明先于 output |
| 828–887 的 reuse/TCB；859–866 的新 topology 必改 shared core | **supported only after rewrite** | 真实 leaf compilation 与特定 lowerers；Goal5838 历史框架不变反例，不能泛化成所有未来 topology 可免改核心 |
| 890–943 的 9 systems／13 lanes／6 batches | **历史有界 support** | 作者移植／选定输入，非第三方实现或完整论文复现；可压缩到辅助 reuse evidence，不能作为泛化样本量 |
| 947–1010 的 evaluation questions／discipline／claim-map | **必须重写** | 增加 bounded composition、finite checker、五 arms／两代；删除 current experiment 的旧 18 blocks／bootstrap CI／1.05 steady-vs-PyOptix 主门槛定义 |
| 1117–1207 的性能整节及表 | **必须替换或明确降为历史** | 用 §9 的同源四行／全部 blocks／实际 estimator；A/D median≤1.20，A/C entry≤1.20且worst≤1.35；不同来源数字不能拼成同一试验 |
| 1211–1223／1538–1540 的 responsibility 与非 usability | **支持限定** | 可以说责任转移和具体声明拒绝；保留 human=0，无 ease／productivity superiority |
| 1241–1257、1350–1357 的 prior-work boundary | **supported only after rewrite** | 更新 RTDL scope；不虚构所有 prior systems 全无语义约束，保留未执行系统不作 fault-survival 声称 |
| 1387–1453 的 survey／population | **可保留为背景或压缩** | corpus 不是 defect prevalence；本轮不为其全部文献数字重新背书，也不要求在 deadline 前做 census |
| 1455–1488 的 artifact／324 workers／7,128 timings | **必须重写** | 交付实际最终 payload、raw recount 和路径／历史缺件范围；不能让旧 compact artifact 代表新五-arm证据 |
| 1492–1515 的“未来 frozen-core test”、零 prospective | **必须重写** | 已完成一次 narrow exam，未知拓扑／人类作者／真实 prevalence 仍开放；不设新实验为本次稿件必要前提 |
| 1529–1536 的一张 RTX4000Ada、无第二 target、Direct 无 gate | **必须重写** | d653 上 RTX4090 Ada 与 RTX3090 Ampere；A/D有median gate、无worst-block gate；仍无 universal hardware claim／OWL timing |
| 1544–1573 的 conclusion | **必须重写** | 重申编译准入贡献和有限观察，公开 receipt 偏离／双故障／checker／adaptivity 限制；不用旧 setup 差异解释新结果 |
| root README 79–86、paper README、final-sprint header | **必须同步更新当前状态** | 不否定未重跑 portfolio 的旧 adverse cohort；写清两项精确任务新状态、协议差异裁决与仍缺 artifact/claim approval |

明确 forbidden：topology-generic lowering；unbiased new-application 成功；Goal5840 general semantic proof；RTDL intrinsically faster than Direct／PyOptix；旧 9.53x 作为语言速度优势；post-import parity；两机器 raw time 相除；全部原 Goal5848 receipt invariants 已原样满足；所有 native forks 均 fail-before-entry；双故障总能保留 root cause／ownership；所有测试绿色；任意目录 full authority replay；内部 PASS 或本报告等于已获外部 consensus。

主文必须保留的 adverse／limitations：旧 post-import 四项不利 ratio、适应性修复链的失败、原逐执行 receipt 条款偏离、有限两任务／两 GPU／八 block 外推范围、strong C 非最优下界及 instrumentation qualification 仅 A、特定 lowerer TCB、Goal5840 finite structure、double-fault／native-fork 边界、human/prevalence=0、artifact 历史和绝对路径限制。正文篇幅不允许全部性能谱系展开时，至少主文明确上述限制并指向准确的追加 lineage；不能只给有利最终表。

## 14. 最小可信修订计划：最多五项

1. **先追加协议—实现差异裁决及 claim ledger。** 明确 Goal5848 §8(4)/(6) 未按字面闭合；纠正 self-review 的逐样本后验 receipt 说法。将可用证据限定为 d653 的机器数值门槛、逐次 output oracle、同步 native/compact status、独立 diagnostic/witness。不得修改旧 protocol、seal 或补造 receipt；若不接受缩范围，则撤下对应正向性能／证明主张。
2. **完成一轮整稿 bounded rewrite。** 使用 §13 ledger；论文动态保证同时限定 double-fault、native-fork、lazy receipt；更新五 arms／两代／estimators、历史 narrow exam、finite checker。保留 still-correct 的 stable constructors=2、unbiased new-application=0、human=0。无需新应用、census、usability study、通用 lowerer 或性能优化。
3. **交付最小匿名、可离线复核 artifact。** 包含最终 archive 或明确可取的 exact payload、portable manifest/worker recount 入口、原始失败索引及 exact-source 映射。将 current/historical/platform/optional tests 分层，补 Goal5837/5843 expected failures；不承诺已未完成的任意路径 full-authority rebuild，不重封历史 bytes。
4. **集中修正文档的 custody 与测量事实。** Ada 63位 hash→真实64位 hash；追加 Direct worst-block 历史措辞 erratum；明确 qualification 只测 A；更新 root/paper README 与 sprint 状态。逐一比较它们与机器合同，不用 report 反向覆盖 raw evidence。
5. **冻结后做已提交工具的最终稿件／提交检查。** 确认来源映射、匿名字段／路径／引用、11页主文、实际 PDF 渲染、链接、artifact 可访问性和所选 gate。记录 review 吸收与授权状态，不把本轮发现藏进内部记录。若另选源码修复，只能在冻结前，且旧两代证据继续严格绑定 d653；本审查不建议因此启动新的性能开发。

## 15. 最终判决

**`PROCEED_ONLY_AFTER_LISTED_BLOCKERS_ARE_FIXED`。**

有可辩护的 CGO 论文核心：受限 Python 的真实编译链、whole-protocol admission 的职责组织、一次有限 prospective composition、分别实现的有限 target checker，以及现在可由 raw bytes 重建的同源两代公开路径成本。没有理由因缺少任意拓扑编译、人类研究或 prevalence census 就取消这一有限方向。

但当前稿不能提交，本轮也不接受不加限定的“原 Goal5848 全部安全门槛完成”。**机器 PASS 不能修复书面 receipt 不变量与实际 public fast path／formal worker 的差距。** 必须先完成明确的偏离裁决与主张缩小，再完成论文和 artifact。数值结果保留，原 authority 不改；不允许用修改当前报表、补造 receipt 或把另一轮 diagnostic 说成逐次计时证明来关闭问题。

如果项目采用上述有限主张并完成五项交付，技术上可以继续投稿；这不等于录用预测，也不自动授予 public/manuscript claim 权限。若坚持完整逐执行证明、普遍低开销或拓扑通用性，则现有证据不足，应删除相关主张或放弃这版投稿，而非在截止前用额外工程掩盖范围差异。

[cfr]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/call_for_review_post_goal5851_cgo2027_20260906.md
[self]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/strict_self_review_since_last_claude_goal5848_goal5851_20260906.md
[claude]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md
[adjudication]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_claude_cgo_adjudication_20260905.md
[final-report]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5851_cross_generation_final_report_20260906.md
[paper]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex
[paper-readme]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/README.md
[custody]: /Users/rl2025/rtdl_v4_restricted_python_design/KNOWN_STALE_CUSTODY_CHECKS.md
[parallel-review]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/review_post_goal5851_cgo2027_20260906.md
[collision]: /Users/rl2025/rtdl_v4_restricted_python_design/case_studies/linear_rtccd_owner_grouped/README.md:71
[paper-abstract]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:50
[paper-shape]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:651
[paper-perf]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:1124
[paper-conclusion]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:1564
[written-invariants]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5848_strong_baseline_post_import_20260905/GOAL5848.md:274
[lazy-receipt]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:5343
[replay]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6274
[sample]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/worker.py:168
[output-validator]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/worker.py:268
[diagnostic]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/worker.py:482
[rtdl-contract]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/contracts.py:627
[self-receipt]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/strict_self_review_since_last_claude_goal5848_goal5851_20260906.md:627
[bind-fault]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:3078
[close-fault]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:3096
[authority-path]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5848_build_transaction_authority.py:190
[repair-final]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5851_triangle_exact_replay_repair_20260906.md:327
[pyoptix-relation]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5802_premeasurement/pyoptix_scalar_arm.py:1241
[row-reuse]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:5855
[pyoptix-triangle]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5802_premeasurement/pyoptix_scalar_arm.py:1504
[pid-hook]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:239
[pid-check]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6184
[bad-hash]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/call_for_review_post_goal5851_cgo2027_20260906.md:228
[self-hash]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/strict_self_review_since_last_claude_goal5848_goal5851_20260906.md:308
[repair-errata]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5851_triangle_exact_replay_repair_20260906.md:180
[checker-effects]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5840_independent_target_checker.py:561
[checker-flow]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5840_independent_target_checker.py:1182
[instrumentation]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/contracts.py:218
[instrumentation-arm]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5848_build_transaction_authority.py:571
[schema]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_family_schema.py:1210
[generic]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_generic_family_lifecycle.py:367
[sphere-compiler]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_sphere_any_hit_count_optix_compiler.py:123
[sphere-wrapper]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_sphere_any_hit_count_wrapper_codegen.py:287
[challenge]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5838_generic_core_exam_20260902/CHALLENGE_TABLE.json:405
[g5838-builder]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5838_build_final_authority.py
[g5838-prereg]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5838_generic_core_exam_20260902/PREREGISTRATION.md:50
[g5840-builder]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5840_build_final_authority.py
[g5840-hostile]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_INTERNAL_HOSTILE_SELF_REVIEW.md:45
[task-contracts]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/contracts.py:121
[endpoint]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/worker.py:216
[lifecycle-repair]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5850_lifecycle_endpoint_repair_20260906.md:117
[native-status]: /Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:5444
[ada-raw]: /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass
[ampere-raw]: /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_d653fe4_pass
[cross-raw]: /Users/rl2025/RTDL_evidence/goal5848/goal5851_cross_generation_d653fe4_complete
[raw-receipt]: /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass/formal-transaction/workers/G5848_S053_B05_BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1_A_RTDL_AOT_PUBLIC.json:47
