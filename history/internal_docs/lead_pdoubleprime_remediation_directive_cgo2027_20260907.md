# P″ 七项审查问题的具体解决方案与主 AI 执行指令

日期：2026-09-07 America/New_York。

依据：用户要求“给出问题解决方案”，以及此前由本审查担任 lead、主 AI 负责实施的分工。本文件交付整改方案；不表示正文已经修改、finding 已经关闭或新颖性已经获得独立认可。

**裁定路线：保留真实实现和两代有限性能观察，修正方法、来源、贡献定位及控制记录。七项均可在当前文献／文稿整改范围内处理，不需要修改 M/E/F2，不需要新 GPU 实验。主 AI 的实施交付必须是修订后的实际稿件与证据映射，不能用另一份宏观计划代替。**

本指令补充既有 N0–N5 和 R0–R8；只重开受影响的文稿／文献项。仍受 2026-09-08 00:00 America/New_York 硬冻结及原对外授权边界约束。当前工作范围即使在冻结前也不含新可执行开发。

## 1. 输入、交付和所有权

受审 P″ 为 commit `b28076ad568d3b7b36cfa48b0c5846accff3cb95`、tree `2a63fecbcf09727dbe4e38f83edb253d80fa3cab`，PDF SHA-256 为 `a8d3194b07fbf0105b59944e8044da1769b9ca8877f92d3a93aa44f605b6aa84`。保全它和[主审报告](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/R7_PDOUBLEPRIME_LEAD_INDEPENDENT_REVIEW_20260907.md)，不修改原报告来消除 finding。

本文定位以 P″ 为准；正文移动后按语句和小节定位，并登记新 PDF 页码。以下缩写只用于本文：

| 简称 | 实际文件 |
| --- | --- |
| 正文 | [main.tex](/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex) |
| 引用 | [references.bib](/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/references.bib) |
| N1 | [RELATED_WORK_BOUNDARIES.md](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/RELATED_WORK_BOUNDARIES.md) |
| N2 | [PROTOCOL_WITNESS_AND_DERIVATION.md](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/PROTOCOL_WITNESS_AND_DERIVATION.md) |
| N3 | [CGO_CONTRIBUTION_ARGUMENT.md](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/CGO_CONTRIBUTION_ARGUMENT.md) |
| 修改映射 | [MANUSCRIPT_CHANGE_MAP.md](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/MANUSCRIPT_CHANGE_MAP.md) |
| Ledger | [CLAIM_LEDGER.json](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/CLAIM_LEDGER.json) |
| 状态 | [STATUS.json](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/STATUS.json) |
| 验证日志 | [VALIDATION_LOG.md](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/VALIDATION_LOG.md) |

主 AI 独占正文／引用／ledger／状态编辑。可分工只读核对文献和源码；分工结果合为作者自查，不算多份独立接受票。所有已有未提交文件先分类保留，不批量 `git add -A`。

后继文稿称 **P‴（P-triple-prime）**，交付以下新控制文件，放在既有 remediation 目录：

- `R7_PTRIPLEPRIME_REMEDIATION_REPORT.md`：七项执行回报、关闭证据和未解决项。
- `R7_PTRIPLEPRIME_FINAL_BYTES_REVIEW_REQUEST.md`：实际新 commit/tree/PDF/source/F2 身份与复审范围。
- `R8_PTRIPLEPRIME_LOCAL_PREFLIGHT_REPORT.md`：本次真正执行的局部验收及继承记录。

文件名是预定交付名称，不是完成声明。旧请求、旧 R8 和旧 execution report 的受审版本须可恢复；当前可变文档更新时明确 supersession。P″ 请求中的事实错误通过新报告的 erratum 表纠正，保持原请求字节不变。

## 2. PDP-01：披露实测专门化，并将数值绑定实际路径

**执行位置：** 正文 §3.2（旧 260–267 行）、§3.5、Introduction 第二项 contribution、Performance methodology；N2 §6；N3 implementation method、比较表和 evidence matrix；claims 003、023，以及 007–010 的机制限定。

将现有“The executable path…”的单一路径段改为以下结构；可按版面润色，但事实不可减掉：

> General callback lowering flattens typed effects into ABI fields and tags. Generated Numba leaves produce these values, and trusted wrappers check their status and effects before issuing hardware operations. The evaluated standard routes also use trusted specializations guarded by exact callback IR: triangle counting uses direct count/reduction entries, while bounded relation fuses intersection and row emission. These replace generic leaf calls and per-leaf effect-tag checks at the specialized roles. Static schema, ABI, and identity admission remain in place, as do runtime failure checks and the applicable capacity, overflow, and supplied expected-output checks. The specializations are part of the TCB.

性能方法补一句，并让结果段引用该实现范围：

> The reported prepared latencies measure these specialized standard routes, not the cost of executing every role through the general Numba-leaf ABI.

N2 增加三行 lowering 对照，不能只展示随后被生成器替换的通用代码：

| 路径 | 进入条件和实际执行 | 必须附的源码依据 |
| --- | --- | --- |
| 通用 callback／相关 diagnostic entries | 验证后的 typed effect → ABI／tag → Numba leaf → wrapper 检查 → 硬件动作；注明示例对应哪个拓扑／entry | 实际 codegen 和最终生成的 entry，不能把模板中未使用字符串当运行代码 |
| 实测 triangle | exact IR 与相应 U64 reducer 条件；direct count/reduction entries；说明哪些通用 entry 改为 diagnostic | [triangle wrapper:129](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:129)、[463](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:463)、[486](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:486)，以及 [runtime:6254](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6254)／6304／6412 的调用衔接 |
| 实测 relation | exact standard IR；fused intersection、计数／行输出及 continuation | [relation wrapper:55](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py:55)、[293](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py:293)、[343](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py:343)，以及对应 runtime/native 调用点 |

表中另加“保留检查／替代检查／信任前提”列。triangle 的 overflow、relation 的 capacity 等按实际路线填写，不声称每一类检查在所有路线都存在。目标源码、IR 身份、选择条件和实测入口都要可追溯到 M；无需重新运行生成器或 GPU。

**验收：** 正文直接说明被测路径，N2 给出完整分支证据，023 不再无条件声称所有执行都逐叶检查 tag。数值及 timer 不变。不得把精确 IR hash 当语义保持证明，不得由本次披露新添“通用优化算法”“专门化已被形式证明”或定量因果加速贡献。

## 3. PDP-02：将 runtime 预热、路线准入和执行 gate 分开

**执行位置：** 正文 contribution 第一项、§2.2 mutation 句、§3.6 lifecycle、Evaluation 的 target-projection mutation 句；N2 failure-behavior／timeline／mutation 配置；N3 §1／§2／§4.3／§5；claims 002、022。

第一项 contribution 使用有边界的表述：

> A protocol-carrying admitted executable: one decision checks five cross-artifact relations before a materialized route is returned, and the accepted identity is carried through per-route preparation and publication checks.

§3.6 补充：

> The exact app-free native runtime may be loaded and warmed before route admission, including concurrently with AOT artifact verification. Admission still gates acceptance of the materialized or loaded route and its subsequent per-route preparation.

两处 mutation 表述均明确测试配置，例如：

> With native-initialization overlap disabled, the integrated projection mutations were rejected before the native-library loader was called.

保持其他 mutation 计数和原 reason code，不扩大此句覆盖的实际测试集。依据 [begin_native_initialization:477](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_callback_lifecycle.py:477)、[materialize:1045](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_callback_lifecycle.py:1045)、decision 1151、runtime DSO 加载 1187／1275，以及 [正式 worker:302](/Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/worker.py:302)。

**验收：** 准入前允许的是精确身份的 app-free runtime 加载／预热；未经准入的 route 不因此获得 preparation／launch 授权。删除所有无配置限定的“共同 decision 必先于任何 native DSO load”概括；不能通过删去 runtime 身份检查的描述来修正。每个“before load”指明加载对象和接口。

## 4. PDP-04：按接口和时间点修正 publication 证据

这一项与 01／02 同批完成，避免 N3 再次概括过度。

正文 §3.6 的“The public path”改为“The measured AOT prepared path”；保留现有 Figure 1 的停表、oracle 和 diagnostic 顺序。N2／N3 可采用：

> The materialized-program interface returns `ProtocolExecutionResult` after validating execution identity, device status, output digest, and traversal receipt. The measured AOT prepared interface returns `RTDLExecutionResult` through a different path: native and compact-status failures, and any supplied expected-output mismatch, are rejected synchronously. Its ordinary fast result need not contain an output digest or detailed traversal receipt. The experiment checks returned values and digests after public return and retains detailed evidence from separate post-loop diagnostic executions.

N2 用下表替代未区分接口的“一条 public publication 链”，每行填写源码／历史证据定位：

| 接口／阶段 | 返回或留存前实际检查 | 不能据此声称 |
| --- | --- | --- |
| Materialized-program → `ProtocolExecutionResult` | 该接口执行身份、状态、digest 和 traversal receipt 验证 | 实测 AOT 的每次执行都走此接口 |
| Measured AOT prepared → `RTDLExecutionResult` | 原有绑定及 owner/process/thread/reentrancy 边界；同步 native／compact status；有提供时检查 expected output | 每次返回都含完整详细 receipt；每次重新哈希磁盘；覆盖所有 native fork |
| Worker oracle | public return 后对输出及 digest 检查；first-result endpoint 包括这一步 | 检查在 prepared steady timer 内；这是所有用户调用自动执行的编译器保证 |
| Separate diagnostic | 每 A worker 另一次 post-loop 执行，保留一份 detailed receipt | 对此前 128 次 timed calls 各自留存完整详细 receipt |

源码入口是 [通用返回路径:1572](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_callback_lifecycle.py:1572)、[AOT 返回路径:6254](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6254) 及返回位置 6289；relation 同步 capacity/status 另按实际路径填写，不能只用 triangle 例子包办两者。

**验收：** N2 §4.1／§5／§9–10、N3 §1／§2／§5 与正文及 claim 015 一致；claims 002／022 同步限定。保留 4,096 次 timed A、32 次另行 diagnostic，以及原逐次 detailed-receipt 要求未履行的判定。不要使用含混的“compiler timer 外”，直接写 prepared timer 后，first-result endpoint 内。

## 5. PDP-03：补 PCC，并让贡献建立在具体设计上

此项包含两个动作：补直接近邻；重写“为什么有研究价值”的论证。只补一条引用不算完成。

### 5.1 补一段明确比较

在 Related Work 的 typestate／FFI 段附近加入以下段落，使用 `necula1996safe` 一级引用：

> Proof-carrying code established policy-based admission of native binaries through consumer-side validation of a supplied safety proof. RTDL provides no comparable proof certificate: its family schemas, compiler-derived projections, topology-specific lowerers, and runtime remain trusted, while artifact digests establish identity rather than semantic correctness. RTDL evaluates a concrete engineering choice: making selected ray-tracing protocol relations explicit and enforcing them at specified compiler and runtime boundaries. Its proposed contribution is this domain-specific design and bounded implementation evidence, not the general idea of validation before execution.

来源为 [OSDI 1996 原论文 §2](https://www.usenix.org/legacy/publications/library/proceedings/osdi96/full_papers/necula/html/node2.html)。PCC 原文不支持把它说成“只能查内存，不能涉及数据抽象”。本段是拟用改写，须在首句加实际 LaTeX 引用。

引用元数据可直接采用 [USENIX 官方记录](https://www.usenix.org/conference/osdi-96/safe-kernel-extensions-without-run-time-checking)：

```bibtex
@inproceedings{necula1996safe,
  author = {George C. Necula and Peter Lee},
  title = {Safe Kernel Extensions Without {Run-Time} Checking},
  booktitle = {USENIX 2nd Symposium on OS Design and Implementation (OSDI 96)},
  year = {1996},
  address = {Seattle, WA},
  publisher = {USENIX Association},
  month = oct,
  url = {https://www.usenix.org/conference/osdi-96/safe-kernel-extensions-without-run-time-checking}
}
```

N1 增加 PCC 方法先例行；N3 §2 可复用思想、§3 比较表、§4.3/4.4、§5 evidence matrix 同步说明它。保留现有强近邻比较；不重做穷尽综述。

### 5.2 用“一个设计、一个实现、有限证据”组织贡献

三项不声称都是独立的新理论。Introduction 与 N3 使用以下实质内容，允许合并精简：

1. **核心设计：** 对固定 RT families，以共同 route contract 显式表示角色／effect、名义属性归属、物理绑定、continuation 和 executable identity，并规定在分离的 compiler/runtime 中从哪里提取、在哪个边界比较或检查。强调声明来自可信 schema、投影来自同一编译器的另一表示。
2. **实现方法：** restricted Python、确定 effect ABI、trusted topology wrappers 和实测 exact-standard-IR 专门化；具体承诺服从第 2–4 节。类型检查、hash、模板和状态机是采用的已有技术。
3. **有限证据：** 原 mutation／一次 sealed composition／有限结构 checker／两代精确任务性能及可重放重算，连同所有反例、成本和未覆盖范围。专门化、2,635 行 topology TCB、原 receipt 缺口不能藏到贡献陈述之外。

N3 的“一页贡献论证”必须用既有 N2 贯穿例子串起下面四个问题，每项一小段并给证据 ID：

| 必答问题 | 本轮允许的回答依据 | 不足时如何处理 |
| --- | --- | --- |
| 既有组件已经解决什么？ | N1 的正面能力、明确责任边界；PCC 是验证后准入先例 | 对 exact joint guarantee 不知道就保持 UNKNOWN |
| RTDL 具体增加了什么？ | 同宽 item-ID 关系的可信声明、compiled projection、比较点、route 身份与生命周期衔接 | 只能证明有限配置／表示一致性时就用该措辞 |
| 为什么这种组织值得研究？ | 明确跨表示事实的来源、共用 decision 的实际使用点和已有有限重用；让工程义务可检查、可审计 | 不能由“正好五项不同”自动得出新颖性，也不能虚构新增拒绝能力或性能收益 |
| 代价与保证是什么？ | specialized lowerer/TCB 成本、有限拒绝证据、prepared 数据和不利 lifecycle 观察 | 没有形式语义、独立用户或通用性证据，明确写缺失 |

**验收：** 最终读者能说清 RTDL 提交的具体设计取舍及验证程度，也能看到 PCC 等已有方法。`022` 的候选贡献有 N1／N2 双向追溯，`024` 不从“未找到声明”推出“对方做不了”。主 AI 可以报告“定位修订完成”；只有独立审查才能判断该增量是否足够有力。若最后仍只支持系统整合／经验贡献，就如实缩到该层，不自行换投稿类别、伪造 novelty 或停下其他已能完成的修订。

## 6. PDP-05：修正候选路线语义

正文 §5.2 的“All … every continuation was a per-query count”替换为：

> All rows used supported primitive families and returned one value per query: six produced counts, and four produced Booleans by terminating on the first accepted hit.

保留下一句 curve eligible/unselected 与实际 sphere selected 名称，以及两次 OptiX launch、12/12 oracle。核对 [冻结 CHALLENGE_TABLE.json](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5838_generic_core_exam_20260902/CHALLENGE_TABLE.json)，表保持原件。`count_relation=query_count` 是结果基数，不是所有计算都为 count。

**验收：** 十行分母、六 count／四 Boolean、seven built-in／three custom、selected 身份同时正确；正文、claims 004／005、新请求和旧请求勘误一致。无需重新运行 prospective exam。

## 7. PDP-06：分别描述 double fault 和 native fork 的证据

正文 Threats/Internal validity 的“Neither unrepaired path produced output or appeared in retained GPU work”替换为：

> The double-fault mock returned no public result. The native-fork probe accepted a public call using a mock native implementation; it did not execute GPU work. Neither defect was observed in retained successful GPU workers.

保留之前有关 primary exception、cleanup retry、Python at-fork hook／cached PID 的描述，以及 §2.3 unsupported inherited owner 边界。依据 [旧审查 native-fork finding](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_review_post_goal5851_cgo2027_20260906.md:148)。

**验收：** claims 018／019、新执行回报和正文不再宣称 native-fork probe 必定无输出，也不把 mock 接受升级为真实 GPU fork 成功。执行回报注明：lead 旧报告曾建议合并无输出句，本次一并纠正 lead 的措辞。旧报告保留，不重做 probe，不修 runtime。

## 8. PDP-07：固定 SlangPy 来源身份，做有限能力复核

采用已核实的 [SlangPy v0.43.1 官方发布](https://github.com/shader-slang/slangpy/releases/tag/v0.43.1) 和 [精确提交](https://github.com/shader-slang/slangpy/commit/2f6c4625fdd2b3bd812ca6cd2802cf98bd89b248)：`2f6c4625fdd2b3bd812ca6cd2802cf98bd89b248`。动态 stable 文档另记真实访问日期，本次为 2026-09-07；不要将动态页面声称为固定 tag 的不可变文档。版本 changelog 与 GitHub release 的日期按各自来源登记，不强行合并。

修改引用的 0.42.0 注记。推荐把 release 作为版本身份引用、stable API 文档作为另一个带访问日期的来源；需要时拆为两个 BibTeX 项。N1 的 `RW-SC-05` 保留旧核查身份作为历史，并新增本轮来源/结论。

只复核四组直接相关能力，每组提供一级来源位置、肯定结论及尚未知的保证：

- RT pipeline、hit groups、shader table、dispatch。
- reflection／marshalling／binding 的已有检查。
- module／shader／pipeline cache 与身份相关功能的实际范围。
- device callbacks、close／cleanup、已完成 command encoder 再用的处理。

当前 [官方 API 文档](https://slangpy.shader-slang.org/en/stable/src/api_reference.html) 和 [0.43.0 changelog](https://slangpy.shader-slang.org/en/stable/changelog.html#version-0-43-0-july-13-2026) 是复核入口。后者记录了 native binding、缓存及 lifecycle 改动；只读 0.43.1 的 wheel 补丁说明不足以覆盖继承能力。

**验收：** N1、引用、正文及 claim 024 的身份一致，四组能力都有实际核查结果。已有能力正面承认，完整 Q1–Q6 缺证处继续 UNKNOWN。无需安装 SlangPy、GPU 运行或整仓源码审计；不能只改版本数字就宣告完成。

## 9. 最少且充分的联动与复验

### 9.1 文件与 finding 映射

| Finding | 必须联动 | 作者侧关闭所需证据 |
| --- | --- | --- |
| 01 | 正文 method/contribution/performance、N2、N3、003/023/007–010 | 实测入口与专门化分支表、最终 PDF 对应段落 |
| 02 | 正文 contribution/lifecycle/mutation、N2、N3、002/022 | 两种初始化顺序、测试配置、改后 gate 句 |
| 03 | 正文 contribution/Related Work、bib、N1、N3、022/024 | PCC 一级来源及对照、四问增量论证 |
| 04 | 正文路径名、N2、N3、002/015/022 | 两接口／四阶段表，timer/receipt 口径一致 |
| 05 | 正文 exam、004/005、新请求及追加勘误 | 冻结表 10 行分类和选中身份 |
| 06 | 正文 Threats、018/019、新执行回报 | mock 与 GPU 证据分离及 lead 旧句纠正 |
| 07 | bib、N1、024及有引用身份的正文 | v0.43.1/source 身份、四组有限能力复核 |

修改映射每项填写：原句、新句、文件位置、N1/N2 来源 ID、claim ID、最终 PDF 页码。不把只改内部文档的项假写成正文 finding，也不在论文里暴露内部 Goal、reviewer 或私有路径。

`STATUS.json` 记录 P″ 本次 **1 份独立 REVISE、0 份接受**；三位分工助手不另计票。新 P‴ 从 0/2 接受开始。R1–R3／R5/F2 历史已关闭项不重开；N1–N4 受影响项记录修订进度，所有 24 项 `claim_authorized=false` 保持不变。当前 README 和其他可变入口只同步真实候选、hash、复审状态；不批量改写历史权威记录。

### 9.2 实施顺序与通过条件

1. **保全和建表。** 记录开始 HEAD／工作树，保留 P″ 及两份 lead 文件；在新 remediation report 建立七行 finding 表，初始 pending。来源核对可并行：01/02/04 一组、03/07 一组、05/06 一组。
2. **先校正文义，再合并。** N2 的执行事实和 N1 的直接近邻汇合后，主 AI 一次性修改 N3、正文、bib、ledger；随后全稿搜查同义过强表述。例：“native load”“public result”“per-query count”“effect tag”“proof”“current stable”。人工判断上下文，不能把关键词存在本身当失败。
3. **保留所有强制披露。** 数值表保持原值；4,096/32、worker oracle 顺序、post-import 全部不利及 2.377129x 最大块、A/E 首结果 8%–22%／16%–31% 回退和 post hoc/non-gating、导入混淆、A-only instrumentation、有限 checker miss、2,635 行 TCB、零独立用户、artifact 范围均仍在主文。仅可去重措辞，不能为塞入 PCC 删去不利证据。
4. **使用既有构建工具生成新 PDF。** 沿用缓存 Tectonic 和既有 source-custody 封包方式，在新输出目录工作，记录实际命令／退出码／输入输出 hash。不新增 compiler、test、experiment 或 F2 工具。全文渲染检查，而非只检查改动页；确保引用解析、匿名、字体、页码、Letter 和既有 CGO 模板要求。实际页数如改变就如实登记，不为强保八页改字号／边距或压掉限制。
5. **只重验变化对象。** 新源码包仍仅含准确 `main.tex`、`references.bib` 和规范化目录；两次独立封包须字节一致，带空格的仓库外路径能构建。最终提交 PDF 两个交付位置须相同。源码重建 PDF 是 buildability 证据，不能冒充受审的那一份原 PDF。
6. **继承未变证据。** 对照 P″，确认 `src/`、`include/`、`experiments/`、`scripts/`、`tests/`、F2 模板无差异，F2 artifact SHA 仍为 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8`。保留 M、E、F2 精确身份。性能计算继承本次独立重算及原 R5/F2 记录；不重跑 GPU、prospective exam、旧全量回归或两套原 raw exporter。包未变可引用既有 normal/optimized replay；如额外 replay，日志置于包外并如实登记，不能宣称继承检查是本轮重跑。
7. **提交真实后继身份。** 主 AI 完成候选提交后从 Git blob 核对正文、bib、两处 PDF、source bundle、F2 和更新后的 N1–N3/map。记录实际 commit/tree/parent、每项 size/SHA。提交身份在后续控制记录登记，不能伪造一个 commit 预先包含自己的最终 hash。
8. **交回 R7/R8。** 新请求逐项映射本次七项和仍适用的旧 R7 findings，附三份交付记录。两份独立最终审查必须看新 PDF 与同一 F2 pair。作者自查关闭七行不等于审稿人接受；改后字节未获独立接受时保持 R7 open。外发、上传和 submitted 状态仍按既有授权与真实回执处理。

### 9.3 主 AI 执行回报的最小格式

| Finding | 状态 | 实际修改文件／新位置 | 改后关键句 | 来源／源码证据 | 新 PDF 页码 | 未解决范围及 claim |
| --- | --- | --- | --- | --- | --- | --- |
| PDP-01 至 PDP-07，各一行 | 如实填写 author-remediated 或 pending | 实填 | 实填 | 实填 | 实填或不适用 | 实填 |

再附新候选身份表、实际构建／源码包检查结果、F2／性能继承证据和剩余 R7/R8 门。说明三层贡献现在各是什么、哪些已有工作边界来自作者原文、哪些仍为 UNKNOWN，以及剩余新颖性判断。

**本方案的完成标准是：七项都有实质修改和可核查证据，新 P‴ 的全文表述与真实路径一致，再获得针对真实新字节的独立复审。补齐文档不自动证明新颖性；已有数值通过也不自动授权投稿。**
