# 以新 DSL 为论文主轴：Owner 最新定向与执行收口

日期：2026-09-07 America/New_York。

用户最新定向：主论文介绍一门面向 **repurposed RT** 的新 DSL；whole-protocol 属于其中贡献，编程模型、IR、code generation 与 V4 apps 都应构成论文贡献。

**Lead 采纳并执行这一主线。论文的研究对象是 RTDL 这门 DSL 及其编译系统。结果契约与 whole-protocol 检查解释其设计特点，不能取代完整语言、编译和应用故事。** 我此前把论文中心收窄到 contract/admission，导致语言和应用价值退到背景；本指令纠正这一组织取舍。

## 1. 与既有指令的关系

本指令在论文 theme、贡献组织和章节安排上优先于之前的 contract-first／单一 contract-design 表述，包括 `lead_cgo_contribution_case_and_three_day_execution_20260907.md` 和 `lead_three_question_argument_closure_20260907.md` 中与之不一致的组织建议。其 W1/W2/W3、文献事实、逐项证据边界和检查标准继续有效，作为 DSL 各设计要点的说明。

用户没有要求每个组件都是新理论，也没有授权自动把所有已有功能计为独立原创。编程模型、IR、代码生成和案例可作为一门 DSL 的多项系统贡献；每项仍须交代它在该领域解决的问题、具体设计决定、已有先例与证据。

M/E/F2、已关闭整改、不利数据、原始 authority、2026-09-08 00:00 ET 硬冻结及外发授权边界保持不变。不开发新语言功能、不新增应用、不做新 GPU 实验、不更改 F2 工具或包。主 AI 独占正文、bibliography 与控制状态。本轮仅新增本 lead 指令。

读取时控制 HEAD 为 `8b4475893a7a4486fb89fa35f1ce2470fb2d13f4`，主 AI 正在改动正文及输出 PDF／source 包。不得覆盖或回退其改动；在下一份明确身份的候选中合并本方向。旧最终字节接受票仅绑定旧 PDF／F2，不自动转移。

## 2. 标题、身份和研究问题

建议标题：

> RTDL: A Restricted-Python DSL for Repurposed Ray Tracing

建议摘要的身份句：

> We present RTDL, a domain-specific language based on restricted Python for expressing bounded non-rendering computations on ray-tracing hardware.

紧接着解释：应用作者提供 RT formulation、数据／几何、受限回调和结果含义；语言表示类型化的角色、数据和效果；编译器检查支持的协议组合，通过可信拓扑 lowerer 生成目标代码；运行时负责准备复用、身份绑定及接口对应的失败检查。

研究问题应从应用作者遇到的 RT 编程负担进入：如何在一个受限高层语言及编译流程中表达并实现这些非渲染计算，同时使分布于回调、数据、遍历和结果消费的义务明确可检查？whole-protocol 是 DSL 回答这一问题的重要方式。

不要宣称自动寻找高效 RT 映射、任意 Python、通用拓扑生成、完整应用正确性证明或已证实的易用性。

## 3. 四项贡献及可直接采用的贡献段

### C1：面向 repurposed RT 的 DSL 与编程模型

说明用户怎样表达 immutable records、受限角色方法、typed effects、数据与结果要求，以及 static input／batch 的区别。突出应用语义与 compiler-owned OptiX mechanics 的职责分工。

证据入口：`src/rtdsl/v4_callback_frontend.py:76`、`src/rtdsl/v4.py`、`src/rtdsl/v4_public_builtin_triangle.py`。现有 quickstart 可提供语言样例，但其 CPU-only 解释检查不能冒称 GPU 程序运行证据。

### C2：类型化 IR 与 whole-protocol 编译检查

展示 IR 怎样表示角色、类型、effects、numeric/resource contracts 与 linkage，以及这些表示如何参与跨角色、语义／物理 ABI、continuation 和 identity 检查。用 W1 解释结果约束如何增加准入决定，用同宽 application-ID witness 说明表示一致性检查。

证据入口：`v4_callback_ir.py:583`、`v4_callback_abi.py:344`、`v4_protocol_contract.py`、`v4_bounded_relation.py:241`。不把 IR 字段表当作全部贡献；必须展示字段改变编译决定的例子。Canonical plan 仍非可执行，trusted schema 不等于自动理解应用语义。

### C3：代码生成、特化和运行时实现

呈现受限源码 → typed Callback IR → ABI／Numba leaves → 可信拓扑 wrappers／目标 PTX → binding／prepare／execute 的具体流程；区分通用叶路径与实测 exact-IR 特化。用 W2 解释逻辑效果如何落实到硬件动作，用 W3 解释程序改变时为什么退出固定 intrinsic。

证据入口：`v4_callback_numba_codegen.py:659`、各 `*_optix_wrapper_codegen.py`、`v4_rtdlexe.py`。不能把 Numba／OptiX 的已有能力说成 RTDL 发明；不能把当前两个特化路径的成本当成任意用户程序的成本。

### C4：V4 应用表达、案例与评估

应用贡献要展示真实的 domain-to-DSL 映射、不同计算模式如何复用语言／编译构件，以及实现成本和限制。应用数量本身不证明泛化，但也不能因为性能重点只有两个任务就把应用 portfolio 从语言论文中抹掉。

建议贡献段，数字仅在对应来源已绑定后加入：

> We make four contributions. First, we design RTDL, a restricted-Python DSL and programming model for bounded repurposed ray-tracing computations. Second, we develop a typed callback representation and whole-protocol admission checks that connect roles, result obligations, data contracts, and executable identity. Third, we implement compilation through a deterministic ABI, trusted topology-specific lowering, guarded standard-route specializations, and a prepared execution runtime. Fourth, we present project-authored V4 application mappings and case studies, together with bounded correctness, reuse, and performance evidence that identifies both the capabilities and the costs of the implementation.

该段表示四项 DSL／系统工作，不宣称四项基础性首创。每项后文必须有实际内容和可定位证据。

## 4. 恢复 V4 apps，但按真实证据组织

早期审查入口 `call_for_review_since_last_claude_goal5830_goal5848_20260905.md:400` 记录九个 project-authored ports、十三条 selected lanes，涉及基础 callback 路径及六种 application-neutral composition batches。这组历史 V4 证据应作为应用章节的检索起点，不能被“两项最终性能任务”替代。

**先纠正应用名称索引：** 上述 CFR 把 Hausdorff 与 X-HD 分开列举，漏写 LibRTS。实际 `scripts/goal5773_build_evidence.py:50` 起的九个源码入口与 `scripts/goal5787_build_cgo_integration.py:42` 起的责任表一致，九项为：

| 历史 V4 port | 可供 DSL 论文解释的计算／组合模式 |
| --- | --- |
| Particle tracking | tetrahedral closest-face transition、restricted closest-hit state update |
| Triangle counting | 应用选择 RT-1A2／RT-2A1、per-hit reduction、segmented reduction |
| RayDB | partitioned traversal、grouped exact-I64 aggregate |
| LibRTS | AABB point/range containment、count reduction |
| X-HD | directed Hausdorff、max-of-nearest witness |
| RTNN | multiround distance-window、ranked top-k |
| RT-DBSCAN | radius-graph emission、grouped continuation、component partition |
| Spatial RayJoin | planar overlay、typed columnar carrier、grouped exact reduction |
| RT-BarnesHut | hierarchy-frontier callback、aggregate state、force reduction |

这张表来自实际保留的源码索引和构建脚本，没有重新执行九个应用。十三 lanes 的最终分配以恢复的原 authority 为准，不能通过手数应用别名生成。

主 AI 先从既有审查及 authority 恢复一个应用矩阵，不重新执行实验。逐行列出：应用及原工作归属、实际 V4 入口／历史源码身份、计算模式、用户提供内容、复用的 IR／lowering／continuation、已有输出／true-OptiX 证据、证据范围与性能来源。

本次只读发现当前 checkout 没有 `Paper-reproduction-apps/` 和 `docs/`，但若干 Goal577x tests 引用历史 `v4_whole_app.py`；这些路径痕迹不能单独证明可运行，也不能据此抹掉旧审查记录。必须使用已有 Git 对象、保留归档、精确 authority 或先前独立审查的明确继承范围定位证据。不可恢复的条目保持待核实／仅映射级，不补写代码伪装历史原件。

现成恢复索引为 `scripts/goal5787_build_cgo_integration.py:20` 起的 PINS。其固定 Goal5785 execution source 包 SHA-256 `75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41`、raw evidence 包 `2b6d808f566886b74469bbe4cf32fc6d426d2a91858237a7e939883f9b89394a`、evaluation `af630fa74ff6b60d1917234b7998e703d8ee60cf91c47cf4ef49ccebf065846a`。本轮没有找到并重验这三个原件；这里只记录如何检索与校验，不把脚本中的预期哈希当成已恢复的文件。

注意：`examples/current/apps/README.md` 自称 v2.x。旧 v2 应用不能直接计入 V4；历史九个 V4 ports 也不能因为它们较早而被误判成该 v2 目录。

| 材料 | 正文用途与范围 |
| --- | --- |
| 历史九个 V4 ports／十三 lanes | 表达／组合多样性和已有有限功能证据；逐条绑定确切历史身份。应用算法及原 RT mapping 归功于原工作；RTDL 的贡献是自己的语言表达／编译组合与实现经验。不是九个独立作者、十三个独立协议形状或自动迁移。 |
| 最终 M 的 relation／triangle | 当前两代正式性能证据；不能扩成全部九个应用在 M 上都达到 near-direct，也不把旧应用性能混入本次样本。当前 triangle 是 weighted all-hit reduction 任务，不能直接当作历史 graph triangle-counting 应用；relation 也不是完整数据库应用。 |
| owner-grouped linear RT-CCD | 真实有限案例、额外 root-exported closed route，继承 exact OptiX 8 30/30 功能观察；不是第三 stable constructor、完整 RT-CCD 或性能结果。 |
| selected sphere composition | 一次冻结共享层的扩展实例，2 launches／12 oracle rows；不是一个新的完整真实应用或无成本泛化。 |
| Sui-derived edge crossing | 遵守 Goal5835/5836 strict audit：bounded semantic projection，不能写成已执行 app front door 或成功完整论文复现。 |

历史应用的性能可能好坏混合。若展示或概括该组性能，须保留其适用的负面行和端点；不能只恢复应用数量、却删去与所作性能主张直接相关的不利证据。

已定位的 Goal5794 历史评审请求 99 起记载 Goal5785 的 464 个 exact／true-OptiX workers 及 34 个 V2-direct/V4 比较行，中位数判定 16 pass／18 fail。这里只把它作为恢复时必须核对的不利结果入口；既不称本轮已重算，也不把该旧比较当成最终 M 的 Direct OptiX 比较。RayDB 的历史私有 loader 例外亦须在引用其公共入口覆盖时保留。

F2 仍只重算其原来包含的匿名证据，不因论文重新介绍 V4 portfolio 而扩成全部应用重放包。应用映射／功能证据和 M 性能证据应分别可追溯。

## 5. 章节顺序与最小实际改动

1. **Introduction：** repurposed RT 的编程问题、RTDL 的语言身份、四项贡献。前两页就让读者看见 DSL 程序，而不是先读一长串审计条款。
2. **RTDL by Example / Programming Model：** 从实际支持的源码中抽取一个精简程序；逐项标注用户提供什么、编译器生成／检查什么。完整摘录保持有效，删节必须标明省略。分别标明 authorable callback surface、stable closed families 和扩展路线，不能把所有语法暗示为任意目标均可执行。
3. **IR and Whole-Protocol Checking：** 表示、关键规则、结果约束和 semantic-ABI 例子。把已有三问表放在这一设计链中。
4. **Code Generation and Runtime：** ABI、通用 lowering、可信特化、身份和生命周期。四种结果／验证路径继续分开。
5. **V4 Applications and Case Studies：** 应用矩阵，选两个证据充分且计算模式不同的实例展开；其余用紧凑表格显示实际复用。不能让 primitive microbenchmark 代替整章应用。
6. **Evaluation：** 按语言／编译规则、应用正确性和复用、有限扩展及成本组织。复用既有实验，不为章节改名制造新实验分母。
7. **Related Work / Limitations：** 分别对照语言／编程框架、IR／编译方法、repurposed RT 应用。所用机制有先例照实承认；保留所有承载主张所需的限制。

不用机械拘泥旧稿八页。CGO 2027 官方允许最多十一页正文、参考文献另计，且论文必须自包含：[官方征稿说明](https://2027.cgo.org/track/cgo-2027-papers)。优先压缩重复防御文字，为实际源码、编译流程和应用表达留出空间；不能压掉关键负面披露。这里不改变投稿类型或外发权限。

## 6. 完成标准与停止条件

- 标题／摘要／引言首先介绍 DSL，whole-protocol 清楚归位为语言／IR／编译设计的一部分。
- 四项贡献各有对应章节、具体例子和来源；“有一个 IR／生成器／应用”不作为自动首创证明。
- 至少一个真实的受支持程序，能追溯到源入口、IR／检查和生成路径。语言教学例子、mock／CPU 证据、真实 GPU 执行不混淆。
- V4 应用矩阵逐行可追溯；找不到原件时诚实标记，不能凭旧测试名称或目录名升级。历史九应用、当前两任务、sphere 扩展及 bounded collision 分母明确。
- 代码生成的通用与特化路径、TCB 成本、prepared／first-result 差异、receipt gap、Arm-A-only instrumentation 和所有适用负面证据保留。
- 新的实际 manuscript／bibliography／PDF 与 source 包形成一致候选，建立精确身份并提交 R7/R8；旧字节接受不转移。

本次主题已由用户明确选择。主 AI 不需要再次询问是否采用 DSL 主线，也不应继续仅围绕 contract 标题做小修而忽略编程模型、IR、生成和应用。完成上述可检查内容后即进入最终审查，不扩张为新的语言开发项目。
