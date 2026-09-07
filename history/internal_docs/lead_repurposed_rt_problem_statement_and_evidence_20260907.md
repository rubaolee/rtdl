# Repurposed RT 的编译问题：新增文献证据、问题定义与正文执行指令

日期：2026-09-07 America/New_York。性质：lead 的定向文献调查、问题论证和下一候选稿执行指令；不是最终字节接受、第三方系统故障实验或投稿授权。

用户要求：论文以新 DSL 为主轴；把 whole-protocol 放到更高层面，调查 repurposed RT 的发展是否带来值得独立提出、由 RTDL 解决的新问题，并补充证据。

本文件补充 [DSL 主线指令](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/lead_dsl_first_submission_directive_20260907.md)。四项贡献、应用恢复、M/E/F2、已关闭 R 阶段、不利证据和硬冻结保持原样。本轮没有改实现、实验或主 AI 独占的正文、bibliography、控制状态。

## 1. Lead 裁定：采用更高层问题，但准确界定“新”

**论文应以“面向 repurposed RT 的 DSL”回答一个明确的编译问题：当几何命中被用来实现邻域、关系、计数等应用结果时，怎样让声明的结果义务贯穿回调、数据解释、遍历动作和结果返回，并实际约束检查与生成？**

新的调查支持这个问题的重要性及反复出现的事实，也发现了必须承认的强先例。因此允许“我们识别、系统化并实现一种面向结果协议的 DSL 设计”；目前不允许“我们首次发现语义映射需要一致”“传统 rendering 没有协议问题”“此前没有非渲染 RT 编程抽象”。

特别需要分清四层：

| 命题 | 本轮裁定 | 对论文的作用 |
| --- | --- | --- |
| RT 硬件正被用于更多非渲染计算 | 有原论文及有明确检索范围的综述支持 | 解释为什么现在需要研究这种 DSL |
| 几何事件必须服从应用的结果含义 | 多篇原论文明确展示；综述也已概括 | 建立共同问题，归功于已有工作 |
| RTDL 将选定结果义务连到 effect 准入、可信 lowering 和接口对应的返回检查 | 有当前实现入口与既有有限证据支持 | 作为 DSL／IR／代码生成的具体设计贡献 |
| RTDL 首次提出这一广义问题，或先例均不可能表达相同保证 | 未建立，且已有宽泛反例 | 不写进正文，不以论文沉默补证 |

**研究增量的候选表述是新的具体语言与编译设计，不是一个已经证实的历史优先权结论。** 这不要求把论文退回一篇只有断言、哈希和审计的文章：编程模型、IR、代码生成及 V4 应用仍是正文主干。

## 2. 为什么 rendering 与 repurposing 的差异值得讨论

不能把二者分成“渲染容许错、计算不能错”。渲染有透明度、体积、随机估计、身份及生命周期问题；非渲染也有近似搜索和近似模拟。区别要放在**结果契约由谁定义、由什么抽象承载**。

一些 rendering DSL 在材料／散射／闭包等领域语义下工作，由 renderer 解释结果并组织光照计算（R2 的 OSL 是明确实例）。Repurposed RT 应用则可能把同一命中解释为一条数据库记录、一项邻域候选或一次聚合贡献。结果的逻辑身份、交付次数、过滤条件、终止条件和归约规则必须随任务明确下来。这个责任在已有应用或库中已经有解法；RTDL 研究怎样在自己的受限可编程接口中把选定义务变成共同表示及编译决定。

以下比较是说明性的结果契约对照，不声称这些操作只属于某一个领域：

| 结果契约 | 对命中的解释 | 对遍历／输出的约束 |
| --- | --- | --- |
| 不透明遮挡布尔查询 | 已找到遮挡物即可确定结果 | 可以早停 |
| 完整关系枚举 | 每个满足条件的逻辑 pair 都属于结果 | 必须保证覆盖，不能仅因已有一个结果早停；按指定身份处理重复 |
| 限定数量的范围查询 | 满足谓词、至多 K 项是接口约定 | 达到 K 是否可停取决于契约 |
| nearest-K | 结果必须按距离选择 | 先遇到 K 项通常不足以确定结果 |
| checked count／sum | 每个有效逻辑事件贡献一次 | 遍历交付、过滤、重复策略和数值范围必须一致 |

其中，普通缓存、哈希、进程归属及资源释放是通用系统问题，不能仅因出现在 RTDL 就称为 repurposing 新产生的问题。其作用是维护已经选择的程序／契约身份与执行边界。

## 3. 新增来源卡：问题的重要性、具体义务与已有解法

调查采用原论文、作者维护材料和官方规范。标记含义：`DOCUMENTED_CAPABILITY` 为来源明确描述的能力；`AUTHOR_BOUNDARY` 为明确职责／限制；`DERIVED_INFERENCE` 为本报告综合推断；`UNKNOWN` 表示未证明。每源短引累计不超过 25 个英文词，其余是有限释义。

### B1：2026 综述——支持增长，也直接限制“首次发现”

[Meneses 等作者预印本](https://arxiv.org/html/2603.28771v1)，§2／Table 1、§3、§3.3；[期刊 DOI](https://doi.org/10.1016/j.future.2026.108739)，出版方标注 online 2026-08-03。

`DOCUMENTED_CAPABILITY`：预印本检索截止 2025-10-06，59 篇用于计量，35 篇分析 32 个问题。它报告硬件 RT 出现后研究增多。§3.3 已要求数据的几何表示、查询射线与命中产生的操作／结果相互协调。原文短引：“The three parts need to be designed coherently with each other”。

用途：趋势及已有问题认识。不能将该集合说成覆盖全部 2026 文献，更不能从综述未列某个编译抽象推断其不存在。该来源是综述；技术机制论证还须依靠下列原论文。

### A1：RayJoin——完整枚举、身份与物理继续策略

[RayJoin，ICS 2024 作者 PDF](https://gengl.me/public/publications/ics24.pdf#page=4)，§3.1／Algorithm 1，PDF pp.4–5；§3.2，pp.5–7。

`DOCUMENTED_CAPABILITY`：LSI 需要收集全部交点；payload 带查询线段身份，真实线段谓词过滤 AABB 候选，AnyHit 存结果后调用 `optixIgnoreIntersection` 继续。PIP 使用不同的最近线段／方向规则。作者还专门处理 FP64→FP32 下转换可能漏解的问题。

短引：“a ray hitting an AABB does not guarantee the ray intersects the line segment enclosed by the AABB”。

可支持：几何命中、逻辑结果和物理动作不是可互换概念；已有应用明确处理了它们。不能支持：RTDL 发明继续遍历技巧，或自动证明任意精确谓词和几何编码。

### A2：RayDB——记录交付与聚合必须联立

[RayDB，PVLDB 19(1)，出版方 PDF](https://www.vldb.org/pvldb/vol19/p43-shi.pdf#page=4)，§3.1–3.2／Algorithm 1，PDF pp.4–6（出版 pp.46–48）；§4.5，PDF p.8。

`DOCUMENTED_CAPABILITY`：离线 denormalization 后，Scan／GroupBy／Aggregation 可合成一个 RT job。多条射线可能重复命中同一记录，作者按 primitive ID 做原子 flag exchange，仅首次交付参与聚合；primitive ID 还可用作 row ID 读取其他属性。

短引：“used to ensure that triangles are not double-counted”。

可支持：身份、交付次数与数值聚合共同影响结果。必须把它视为领域查询组合先例。记录交付去重与 SQL 值相同的不同 rows 不是一回事；RTDL 的 pair 去重不自动证明所有 SQL bag 语义。

### A3：RTNN——停止条件取决于所求结果

[RTNN，PPoPP 2022 作者 PDF](https://horizon-lab.org/pubs/ppopp22.pdf#page=4)，§2.1、§3.1／Listing 1，PDF pp.2、4–5；§6.3，p.10。

`DOCUMENTED_CAPABILITY`：AABB 提供候选，intersection 程序检查实际距离。论文的 range 接口可在达到规定 K 时停止，而 nearest-K 需要维护候选优先队列。短引：“KNN search is similar except the IS shader would operate a priority queue.”

可支持：相似硬件调用的合法停止／归约策略随结果含义变化。不能把该 K 当作 RTDL overflow guard；也不能说 RTDL 自动证明 nearest-K、距离或搜索覆盖。

[作者当前仓库](https://github.com/horizon-research/rtnn)还明确提供近似 KNN，检索于 2026-09-07；这里只用于否定“所有 repurposed RT 都要求精确结果”，不把当前实现与 2022 论文混成同一版本。

### A4：RT-DBSCAN——部分义务超出 RTDL 已证范围

[RT-DBSCAN，IPDPS 2023 作者 PDF](https://arxiv.org/pdf/2303.09655#page=5)，§III.C–D／Algorithms 2–3，PDF pp.5–6；§IV。

`DOCUMENTED_CAPABILITY`：过滤候选及自身交点后分阶段构造聚类；border point 的并发归属需要原子操作，避免错误地合并 clusters。短引：“the border point could be incorrectly assigned to two clusters”。作者在 intersection 程序实现操作，禁用 AnyHit／ClosestHit。

用途：展示 RT 嵌入多阶段状态计算。不能说所有 repurposing 都围绕 AnyHit，也不能以 RTDL 的角色／ABI 验证替代并发 union-find 或 DBSCAN 正确性证明。

### A5：图三角计数——算法侧去重不能被协议检查冒领

[Xiao 等，2025 原论文](https://rubaolee.github.io/paper_pdfs/2025-rtgraph.pdf#page=9)，§3.2–3.2.2，PDF pp.9–10（出版 16:9–16:10）。

`DOCUMENTED_CAPABILITY`：先按 vertex ID 将图定向以避免重复计数，再选择几何编码、射线范围及标识映射。短引：“To avoid redundant counting, a graph must be converted to a loop-free directed version”。

用途：说明结果正确性同时需要应用算法和执行协议。图的定向／两跳关系构造由应用负责；M 的 weighted triangle reduction 不等于这些完整图算法。

### S1：LibRTS——必须正面比较的最接近先例

[LibRTS，PPoPP 2025 原论文](https://rubaolee.github.io/paper_pdfs/2025-spatial.pdf)，§1；§3.1–3.3，出版 pp.399–401；§5／Algorithm 2，p.403（PDF p.8）。

`DOCUMENTED_CAPABILITY`：作者明确针对 repurposed RT 的编程困难提供空间索引框架。它定义点／范围查询，处理过滤及双遍历重复，允许用户设备 handler 消费 query／rectangle ID，并提供 counting 与 collecting handler。

短引：“the specialized RT programming model poses challenges for using RT cores in these scenarios”。

裁定：高层 API、固定结果语义、用户回调、计数／收集均已有先例。RTDL 的比较必须具体到受限源码、typed IR、effect 准入和对应生成／返回检查。论文没有声明某项 RTDL 检查，只能记录为该项保证未建立，不能判它必然返回错误结果。

### S2：CrossRT——host/device 与 RT 映射已有编译自动化

[CrossRT v1，2024 原论文](https://arxiv.org/html/2409.12617v1)，§3.2、§3.5、§3.8–3.10。

`DOCUMENTED_CAPABILITY`：从受限 C++ 识别算法模式，生成 host/device 实现、硬件 ray-query 接口及自定义 intersection shader，并支持软件路径。RTDL 不能认领首次跨 host/device 生成或首次分离算法与硬件。本文所查章节没有建立 RTDL 所选整组结果协议保证；这属于比较范围，不能推出不可扩展。

### S3：LuisaRender——整条 RT pipeline 自动化已有先例

[LuisaRender，TOG 2022 原论文](https://luisa-render.com/static/paper/paper.pdf)，§4.5（232:10），§5.3.3／§6.1（232:12）。

`DOCUMENTED_CAPABILITY`：DSL、shader 接口检查、资源使用分析、依赖调度及 RT 检测后相应生成／pipeline／SBT／参数准备和启动。跨层自动化本身不是 RTDL 新意。比较应落实到明确的结果义务及可编程效果的准入边界。

### S4：Dr.Jit——结果使用信息驱动特化也已有先例

[Dr.Jit，TOG 2022 原论文](https://d38rqfq1h7iukm.cloudfront.net/media/papers/Jakob2022DrJit.pdf)，§3.1–3.3，pp.124:5–8。

`DOCUMENTED_CAPABILITY`：追踪 Python／C++、RT 操作及多态调用，传播常量、消除未用字段并特化。不能把“编译器知道结果需求，所以改变代码”如此宽泛的认识认领为 RTDL 独有。应写清 RTDL 的固定输出义务究竟怎样限制 effect、物理 traversal 和失败返回。

### S5：Scion——新增且必须纳入的 PLDI 2026 编译器近邻

[Scion 原论文](https://arxiv.org/pdf/2511.15028)，§1、§6–7；[作者出版页面](https://ajroot.pl/pldi2026scion.html)，PACMPL 10 (PLDI)，Article 175，DOI 10.1145/3808253。

`DOCUMENTED_CAPABILITY`：BVH 布局 DSL／compiler，将逻辑树、物理布局与 traversal 分离，支持静态良构检查和受限 round-trip 论证。它不是这里的 OptiX 结果协议设计，但直接限制“RT/BVH 领域没有语言化逻辑—物理关系”的宽泛说法。

### S6：TTA／TTA+——问题的其他解法与适用边界

[Generalizing Ray Tracing Accelerators for Tree Traversals on GPUs，MICRO 2024 作者 PDF](https://people.ece.ubc.ca/aamodt/papers/tta.micro2024.pdf)，§I–II.A，PDF pp.1–2。

`DOCUMENTED_CAPABILITY`／`AUTHOR_BOUNDARY`：作者指出把任务适配固定 RT pipeline 有困难，并提出硬件及编程接口扩展；研究聚焦 tree traversal，遍历后的领域结果处理不是主要研究对象。它提供另一种解决路径；RTDL 既不解决所有硬件限制，也不自动找到有盈利的 RT mapping。

### R1：OptiX 2010——传统 rendering 已有跨阶段事件语义

[OptiX 2010 NVIDIA 原论文](https://research.nvidia.com/sites/default/files/pubs/2010-08_OptiX-A-General/Parker10Optix.pdf)，§3.1（PDF pp.2–3）、§3.3（p.5）、§8.1（p.10）。

`DOCUMENTED_CAPABILITY`：阴影可早停，透明度需要继续遍历并累计影响，命中可能乱序，attributes 跨阶段使用。论文还明确包括 collision、AI、sound propagation 等非渲染用途。这既是重要先例，也是“传统 rendering 从不遇到此类问题”的直接反证。

[NVIDIA 官方人员解释，2024-07-31](https://forums.developer.nvidia.com/t/confusion-about-optixignoreintersection/301806)另外说明 intersection 接受会收缩距离上界，ignore／terminate 会立即返回，以及 single-anyhit flag 与重复调用的关系。此论坛资料提供 API 行为语境；正文优先引用原论文和现有官方规范，不把它作为 RTDL 的新算法证据。

### R2：OSL——用户所说“rendering 有其方案”的准确实例

[OSL 官方规范 §1.1](https://open-shading-language.readthedocs.io/en/latest/intro.html#how-osl-is-different-from-other-shading-languages)，访问于 2026-09-07，页面标示 OSL 1.16.0。

`DOCUMENTED_CAPABILITY`：surface／volume shader 产生 radiance closure，integrator 负责评估、采样并组织射线；light-path expressions 规定路径对输出的贡献，shader 网络按依赖惰性求值。它体现领域语义、受限作者接口和 renderer 职责之间的配合。

`DERIVED_INFERENCE`：RTDL 可解释为对另一类结果契约作语言设计，而不是宣称 rendering 缺少语义抽象。不能从 OSL 的这个例子推出所有 rendering pipeline 已被完整验证。

### R3：Shader Components 与 Dr.Jit——跨层组合不是新现象

[Shader Components，2017 官方研究摘要](https://research.nvidia.com/publication/2017-08_shader-components-modular-and-high-performance-shader-development)及[作者论文 §1](https://graphics.cs.cmu.edu/projects/shadercomp/he17_shadercomp.pdf)。`DOCUMENTED_CAPABILITY`：把 shader logic 与其必需参数放进同一组件，支持静态特化及匹配的参数组织。它是代码／数据／绑定共同抽象的已有解决方案；不能说 rendering 只检查孤立函数。

S4 的 Dr.Jit §3.3–3.4（pp.124:7–8）、§4.6（p.124:13）还处理隐式依赖、副作用触发的 materialization 和多阶段微分顺序。这证明依赖／状态／执行阶段也是已有 rendering 编译问题。RTDL 不据此认领一般依赖分析或微分机制。

## 4. RTDL 应抓住的具体编译问题与已实现答案

**问题定义（本报告的综合判断）：** 对一个已经由作者选定几何映射的有界程序，应用声明的结果义务依赖多个阶段共同成立。如何让一门 DSL 同时表示这些义务和用户可编写的计算，并使编译与受控执行遵守选定的结果协议？

把 whole-protocol 限定为本文支持的协议范围：角色与效果、数据及 ABI 解释、物理 traversal 配置、结果处理及对应接口的失败行为、被检查与被执行代码的身份。该词不代表整个应用算法已获正确性证明。

下面三个连接才是正文必须展开的编译内容；它们已有相应本地入口，本轮检查这些源文件相对 M 无差异。

| 编译器获得的事实 | 导致的决定 | 本地证据及解释边界 |
| --- | --- | --- |
| 当前固定 relation 构造器承诺 materialize accepted events，要求各返回分支为 `ACCEPT_CONTINUE` | 拒绝该目标尚未定义的其他返回效果 | [v4_bounded_relation.py](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_bounded_relation.py:241)。这是具体保守准入规则；不能声称所有完整关系都原则上禁止逻辑过滤或 IGNORE。 |
| 全命中计数／归约中的逻辑接受仍须保留后续交点 | 通用 wrapper 先更新 payload／event，再物理 ignore intersection | [生成器](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:418)。RayJoin 等已用该底层技巧；RTDL 的设计工作是把它放进自身 typed-effect 到可信目标实现的关系。 |
| 源程序恰好具有固定 count IR，且 reducer 属于允许集合 | 选择标准 count intrinsic，直接生成加一／溢出及继续逻辑；其他 IR 不可冒用该实现 | [精确 IR guard](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:129)、[特化目标](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:517)、[single-anyhit 配置](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:1998)。IR 身份检查绑定已选择的实现，不证明 lowerer 本身正确。 |

额外的 semantic-ID／attribute 一致性见既有 N2；身份来源依靠可信声明和实际投影，不能自动推断业务含义。材料化完整结果、实测紧凑结果、worker oracle 及事后 diagnostic receipt 继续区分；不把所有检查压成一个“返回前完整证明”。

本轮源码核查时 HEAD 为 `8dfdc810c9c23f259b20c511caf69d250f2b86ce`；上述三个源文件相对 M `d653fe4ad170c5b51fee309d653c9565944dcf2e` 的 diff 为空。主 AI 同时推进稿件，HEAD 是读取记录而非新候选的冻结身份。本轮不重复 GPU 测试，不将文献推理当作新执行证据。

## 5. 可交给主 AI 的英文引言草案

以下是新的综合写作，不是论文原文摘录。方括号是来源卡提示，合入时用现有／新增 bib key 替换。

> Ray-tracing hardware increasingly supports computations beyond image synthesis, including neighbor search, spatial joins, clustering, and database processing. These systems demonstrate that geometric traversal can serve as a substrate for diverse application results. Their success also makes the programming contract more explicit: a geometric hit may represent a candidate, a record, or a contribution to an aggregate, with different requirements for filtering, identity, repeated delivery, and termination. [A1–A4]
>
> These requirements are already visible in successful systems. RTNN gives range and nearest-neighbor search different result-maintenance rules. RayJoin records intersections while continuing traversal, and RayDB prevents repeated delivery of a record from corrupting aggregation. LibRTS provides reusable spatial queries and user handlers. Together, these works motivate a language question: how can a programmable interface make selected result obligations constrain both admissible callbacks and the generated execution protocol? [A1–A3, S1]
>
> We present RTDL, a restricted-Python DSL for bounded repurposed ray-tracing computations. Programmers supply the application mapping and restricted computation; the language represents typed roles, data, effects, and supported result contracts. Whole-protocol admission connects those representations to fixed-family constraints, while trusted topology-specific lowering implements the corresponding traversal actions and interface-specific checks. This design lets a declared result obligation change what the compiler accepts and generates. We demonstrate the language through V4 application mappings, bounded correctness and extension evidence, and an evaluation that measures the costs of the implemented routes.

传统 rendering 对比在下节或 related work 加短段，以 R1–R3 和 S4 为依据；不要在引言写“rendering has no such problem”。已有方法边界可写：

> Rendering languages and systems already provide substantial semantic abstractions and compilation machinery. RTDL addresses selected result-protocol obligations in a restricted interface for non-rendering computations; it does not infer arbitrary application semantics or prove general correctness of the supplied geometric mapping.

贡献第一项可改为：

> A restricted-Python DSL and programming model for bounded repurposed RT computations, informed by recurring obligations at the boundary between geometric events and application results.

后续三项沿 DSL 指令保留 typed IR／whole-protocol、code generation／prepared runtime、V4 mappings／case studies／evaluation。问题分析支持这些贡献，不再单独凑一个“首次发现新问题”的计数。

## 6. 主 AI 必须完成的实际改稿及完成标准

1. **改引言论证顺序。** 用发展与应用证据开篇，接“几何事件怎样成为结果”，再给 RTDL 语言身份和真实源码例子。开篇不要以 stale cache／owner lock／hash 为主要动机。完成标准：前两页能回答 target 是谁、结果义务是什么、作者在 DSL 中写什么。
2. **加入一张三行问题证据表。** 至少包括 RTNN、RayJoin、RayDB：每行写结果义务、原论文的处理、RTDL 实际承接的有限部分。完成标准：至少三篇原论文、三个有差异的义务；不把应用数学谓词和算法正确性偷换成编译保证。
3. **加强最近工作而不是选弱对手。** LibRTS 必须从“背景应用”提升到编程抽象近邻，明确承认 handler、count／collect 和查询语义；补 Scion 2026。继续保留 Slang、Luisa、Dr.Jit、CrossRT 的已有强能力。完成标准：每个排他性差异有范围匹配的证据；没有证据就用能力对照，不写“不可能”。
4. **将问题落实到 IR 与生成。** 以第 4 节三个连接贯穿源码、IR／contract、拒绝／生成和既有证据。完成标准：读者可以指出一个“角色合法但此固定目标拒绝”的例子，以及一个“逻辑接受却要物理 ignore”的生成决定；明确通用叶路径、特化、TCB 与有限验证。
5. **保留可复用的设计认识。** 说明固定功能硬件事件与应用逻辑事件不一一等价，语言需要显式约束其解释；新意在具体表示与编译实现。完成标准：去掉 RTDL 名称后，该设计选择仍可被解释；不宣称已跨领域证明通用性。
6. **完成实际稿件和候选身份。** 修改正文及 bib、正常构建并检查排版、更新一致 source 包，将新的精确 PDF 字节送现有 R7/R8。不得用本文件替代 manuscript revision。完成标准：正文主轴确为新 DSL，四项贡献及应用章节都有内容；旧字节接受不转移。

其中 rendering 对比必须至少承认 OptiX 的既有事件控制和 OSL 的 closure／integrator 分工。完成标准：任何“新问题”句子均指向本论文明确研究的编译边界，不暗示非渲染首用、语义映射首识别或所有先例能力不足。

这些工作已由用户方向授权，不需要再询问是否启动。本文不是开发授权：不增加 executable 功能、新 tests 或 GPU 试验；不改变冻结、原始证据和投稿外发门槛。已知不利成本、receipt 缺口、Arm-A-only instrumentation、固定路线范围及不可恢复历史应用证据继续披露。

## 7. 检索记录及结论的实际边界

检索日期为 2026-09-07。采用主题检索及沿最近工作追索：`ray tracing non-rendering programming compiler DSL`、`repurposed ray tracing`、`RayJoin intersection any hit`、`RayDB precision`、`RTNN correctness`、`LibRTS programming`、`Scion Bounding Volume`、`Generalizing Ray Tracing Accelerators`；并核读前述作者／官方来源。

三个并行只读分工分别审 rendering 先例、应用义务、通用系统与近年编译器，lead 合并并核对关键反例及本地机制。这是一轮有限、有方向的文献审计；不是穷尽所有项目，不是独立最终字节接受票数，也没有对先例实施 fault injection。

证据获取的具体限制：Shader Components 的本轮新增核查以官方摘要及索引可得的 §1 为主；未据未读章节作能力否定。MDL 官方索引亦有相关设计线索，但因这轮直接全文抓取失败，没有把它列为必要论证来源。动态 OSL／RTNN 文档标注检索日期；不把其当前状态倒推成原论文年代的能力。

无法从原论文建立的具体实现保证保留为 `UNKNOWN`。本轮足以关闭“没有认真找更强证据”的行动缺口；不能因此关闭历史优先权或整篇论文新颖性的外部审稿判断。
