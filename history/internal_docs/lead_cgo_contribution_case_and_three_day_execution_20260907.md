# CGO 贡献主线、已有证据与三天执行指令

日期：2026-09-07 America/New_York。依据用户指令：“还有三天……给出方案解决……事在人为，我们就去解决！”

**本轮锁定的主线：把固定 RT 输出契约对 callback effects、遍历动作和结果消费的约束，落实为可检查的编译关系。** 共享准入与专用 lowerer 是实现这项设计的分工；五项检查、哈希和状态机是其机制。论文的中心应呈现这些具体关系如何影响合法程序、生成代码和结果边界。

这是一份已经包含论证初稿、源码追溯和本轮局部验证的执行材料。它补充既有七项整改指令；不重新实施已完成的七项，也不宣称新颖性已获独立认可。主 AI 已产出 P‴，本轮在其基础上集中加强中心论证，不另起大工程。

## 1. 当前身份与范围

已读 P‴ 作者整改及其论证文件：文稿 commit `c26c88a69382d9786c2f5f77c6cdc6763fc51e7c`，tree `b45bae5d83ec9c803657b28132c677d514897bb3`，PDF SHA-256 `2840d348459d2cdeba02cda3a4b17547ce83bc208876736f805a2f5682c3d303`。本轮读到的控制 HEAD 随主 AI 工作推进至 `b608f9aa5e4e04d083d8a2963d552e00287b47cd`。这不是对 P‴ 的完整 R7 最终字节审查。

M `d653fe4ad170c5b51fee309d653c9565944dcf2e`、E `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`、F2 `9771facece4ccd807e26c15b21892b9d0a701d32` 继续保全。下文核心源码和两个测试模块与 M 的 diff 为零。

本轮只增加文献／已有源码的分析、论文文字与图表、已有工具构建及已有检查重放。无新 GPU 实验、无新测试或可执行修改；2026-09-08 00:00 ET 开发硬冻结不变。主 AI 独占实际正文、引用和候选状态；本审查只写此文件，不覆盖主 AI 正在处理的交付。

## 2. 主审裁定：把贡献具体到“输出契约—effect—硬件解释”

“跨表示放进一个对象”“前后端分离”“执行前验证”均有很近的先例，单靠这些概括无法解决增量问题。P‴ 已承认这些限制；下一步要把已有实现中更具体的编译内容搬到论文中心。

**核心候选主张：** 对支持的固定 ray-query family，最终结果契约约束哪些 callback effects 可以组合，并规定逻辑 effect 如何由可信拓扑 lowerer 实现。角色层面合法的操作，可能因该路线的结果义务而被拒绝；逻辑上的事件接受，也可能由物理交点拒绝来实现。编译器把这些选择与数据含义、物理设置、可执行身份和运行时失败条件连接起来。

这是有限领域设计主张。当前实现使用固定 family 规则，不从任意输出公式自动推导新 effect 系统，也不证明任意生成程序的语义。约束与解释的存在有源码支持；其相对已有工作的研究价值须由具体对照和独立审查判断。

可供其他编译系统借鉴的设计认识是：**在硬件接管遍历的系统里，应用观察到的结果契约可以作为组织 callback 合法性和硬件动作解释的依据；应分别核查角色可用性、路线结果义务及可信 lowerer 的实现。** 跨其他加速器的适用性是设计启示，未作实证泛化。

## 3. 三个具体见证：主线现在已有材料支撑

### W1：角色合法，不等于当前完整关系路线可接受

说明性场景：一次查询有两个满足条件的应用对象，完整关系应包含两条结果。允许第一条命中后提前终止，会与该结果要求冲突。此场景用于说明义务，不声称本轮运行过产生错误结果的 GPU 程序。

实际实现有两层不同的检查：

- [角色 effect 集合](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_callback_ir.py:572) 允许 `ANY_HIT` 返回 `ACCEPT_CONTINUE`、`IGNORE` 或 `TERMINATE`。
- [固定 bounded-relation 检查](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_bounded_relation.py:241) 递归收集 return effects，要求集合恰为 `{ACCEPT_CONTINUE}`，否则以 `any_hit_effect` 拒绝。该 target 明确不替其他 outcomes 发明关系输出语义。

**可写结论：** 该固定路线有超出角色合法性的输出相关约束，实际检查位置明确。

**证据等级：** 源码追溯；本轮没有找到或新增“含 terminate 的完整公开源程序经全入口被拒绝”的执行见证。不得写成新实测拒绝率。也不能把当前实现拒绝 `IGNORE` 推广为所有完整枚举算法原则上都不能过滤事件。

### W2：逻辑接受，物理上需要忽略交点

triangle 的逻辑 `ACCEPT_CONTINUE` 更新计数／payload 后，[通用 wrapper](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:418) 调用 `optixIgnoreIntersection()`，防止物理接受交点缩短遍历区间而遗漏后续事件。[实测 count 专门化](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:517) 同样在检查 overflow、递增并写回 payload 后调用该操作。

这条规则与 geometry delivery 设置共同起作用：[native triangle GAS](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:1921) 使用 `OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL`；另有专用 duplicate、capacity 和 overflow 规则。不要只画一个 `ignore` 箭头便声称完整性已普遍证明。

[NVIDIA 作者答复](https://forums.developer.nvidia.com/t/confusion-about-optixignoreintersection/301806)已经明确解释接受交点会缩短 `tmax`、payload 应先于 ignore/terminate 更新，以及计数需要防止同一 primitive 重复调用。因此**这些硬件技巧归功于已有 OptiX 方法**。RTDL 的候选增量在于把结果契约、逻辑 effect、geometry 设置和 lowerer 行为明确连接，并在其有限编译接口内实施，而非发明 all-hit 遍历。

**可写结论：** 逻辑 effect 不能按名字一一翻译为硬件动作；其实现取决于这条路线承诺的结果。这里有真实 lowering 代码，而不只是字段相等检查。

### W3：相同角色形状，源码语义改变时必须退出标准专门化

已有 [编译测试](/Users/rl2025/rtdl_v4_restricted_python_design/tests/goal5759_v4_triangle_reduction_target_test.py:72) 将计数 callback 中 `payload.count + 1` 改为 `payload.count + 2`。角色／程序形状仍相同，前端验证仍通过，IR identity 改变；生成器随后使用通用 leaf 路径，不再选 standard-count intrinsic。

本轮重放该既有测试成功。它实际执行了 source parse、IR verification、contract/ABI construction 和 wrapper generation；没有 GPU 执行，也没有制造错误 scalar。若把修改后的程序仍映射为固定 `+1` intrinsic 会改变计数含义，这是分析，不是已运行的错误结果。

**可写结论：** 实测专门化的选择边界具体依赖程序语义身份，不能仅由 callback 角色或 ABI 形状决定。该 recognizer 和专门化仍为 TCB，精确 hash 不是语义保持证明，测试不证明任意专门化都正确。

这项证据使“程序转换与优化边界”有可核查的实际内容。它是本轮重放的既有组件检查，不冒充原 20,480 个 GPU 样本或原 preregistered mutation 分母。

## 4. 论文中应出现的一张表

放在 Protocol Mismatch／Design 的交界处，正文可据篇幅压成三行。保留原 item-ID 同宽例子，但将其定位为另一种关系约束，不再单独承担整篇论文的增量论证。

| 可观察结果义务 | 仅凭阶段／机器类型不能决定的事项 | RTDL 已实施的具体约束／转换 | 证据边界 |
| --- | --- | --- | --- |
| 当前完整 bounded relation | any-hit 的局部合法 `TERMINATE`／`IGNORE` 是否符合该固定路线 | family verifier 仅接受规定的 `ACCEPT_CONTINUE` returns；capacity failure 禁止发布部分关系 | 源码规则；capacity 的既有 CPU 检查；非一般枚举理论 |
| triangle all-hit count | 逻辑“接受”是否应物理接受交点；同 primitive 是否会重复 delivery | 先更新 payload，再物理 ignore；要求单次 delivery 设置及 checked overflow | 真实通用／实测专门化源码；底层技巧已有 |
| 标准 count 的专门化 | 同 ABI 的 `+1` 与 `+2` 能否共享固定 count intrinsic | exact-IR 条件；改变源码后退回通用 lowering | 本轮通过既有 source-to-wrapper 测试，未执行 GPU |
| 规范关系中的 application ID | `primitive_index:u32` 与 `item_id:u32` 的来源含义 | 可信 schema 声明、compiled contract projection、CP002 不一致拒绝 | 既有字段 mutation／mock；不自动推断应用意图 |

这张表回答“编译器究竟额外知道什么、因此改变了什么”。不使用“对手全部失败”的列，也不把职责归属不同等同于对手没有能力实现。

## 5. 最强近邻：三组直接对照即可

| 近邻已建立的内容 | RTDL 要具体展示的额外领域工作 | 最终措辞边界 |
| --- | --- | --- |
| PCC 已建立消费者策略、携带证明的 native binary 及验证后准入；[原文 §2](https://www.usenix.org/legacy/publications/library/proceedings/osdi96/full_papers/necula/html/node2.html) | 固定 RT 结果义务如何选定 effects、物理遍历解释和失败条件 | RTDL 没有 PCC proof certificate；不主张准入思想新，也不把更弱保证说成优势 |
| Shader Components／[Slang 2018](https://graphics.cs.cmu.edu/projects/slang/he18_slang.pdf)已有接口、组合、特化及目标布局；[当前 capability 文档](https://docs.shader-slang.org/en/stable/external/slang/docs/user-guide/05-capabilities.html)沿调用和接口检查 target/stage/API/hardware 条件 | W1/W2 所示的结果相关谓词：该 fixed route 是否允许提前终止，以及逻辑 acceptance 如何实现 | Slang 不仅是函数内检查；其明示 capability 谓词成立不蕴含该结果谓词成立，但不证明 Slang 无法扩展表达它 |
| [Furr/Foster FFI 检查](https://www.cs.tufts.edu/~jfoster/papers/cs-tr-4627.pdf)已跨语言追踪表示、offset/tag，并处理 GC effect／登记义务 | RT 事件、结果枚举／归约、capacity continuation 与 traversal wrapper 的具体关系 | 跨表示和生命周期检查不是新范式；比较具体领域模型和实现，而非否定已有丰富语义 |

论文／N1 原有 OWL、Luisa、Dr.Jit、CrossRT 和 SlangPy 能力承认继续保留，不重新扩展竞品列表。新检索仅围绕 W1–W3 的同一命题核对直接近邻。发现相同机制的强先例就引用，并把贡献定位到实际剩余设计／实施经验；不换词掩盖。

在 Slang 比较里，最有用的逻辑是**两个保证的谓词不同**：阶段/target 可用性不自动决定某条路线需要保留哪些命中。该差异能由定义和 W1 解释；不依赖“作者没有使用我们那五个词”。

## 6. 可直接采用的论文论证初稿

以下英文是作者侧建议稿。主 AI 按真实源码核对并加入现有引用，替换抽象的“joint five-seam condition”中心段；不要作为额外口号堆叠。

### 6.1 Introduction 的中心段

> In repurposed ray tracing, the promised result constrains both callback effects and the interpretation of traversal operations. Stage legality alone does not express those constraints. For example, an any-hit effect can be legal for its role yet incompatible with a route that must return a complete relation. In RTDL's implemented triangle-count route, logically accepting an event records its contribution and then physically ignores the intersection, preserving traversal of later events. These choices depend jointly on the result contract, callback behavior, and target-specific execution.
>
> RTDL makes these relations explicit for fixed ray-query families. Family admission restricts callback effects and checks declared data and physical contracts against compiler-produced representations. Trusted topology-specific lowerers implement the traversal interpretation, including exact-program specializations for the measured standard routes. Binding and runtime checks connect the admitted artifacts to prepared execution and execution-dependent failures. The design separates what can be checked from metadata, what the lowerer must implement, and what can only be checked during execution; it provides no general semantic proof.

### 6.2 贡献项

> Our core contribution is a concrete result-route contract design for restricted Python on RT hardware: it connects output requirements to admissible effects, traversal interpretation, physical settings, and result-publication conditions. We implement the design with trusted family-specific lowering and guarded standard-route specializations. We evaluate its finite rejection and transformation behavior, the extent and cost of one sealed-core extension, and the prepared execution cost of two exact tasks on two GPU generations.

紧接这段仍保留现有 non-claims 和主要 adverse 结果；不得用“whole correctness”替代“fixed relationships”。

### 6.3 Design 中的转换例子

> The distinction between a logical event and a physical intersection is visible in the triangle lowerer. An `ACCEPT_CONTINUE` effect updates the application payload, then invokes `optixIgnoreIntersection()`. The native geometry setup separately requires single any-hit delivery, and the reduction checks overflow. These established OptiX mechanisms implement the route's counting convention; RTDL does not invent the mechanisms. Their combination is part of the trusted route implementation. The measured intrinsic performs the same event-counting actions directly, while an existing compiler test changes `+1` to `+2`, remains well typed, and switches generation to the general leaf path. This test checks specialization selection, not GPU equivalence or a general optimization theorem.

### 6.4 经验结论

> The extension study identifies a boundary of reuse rather than automatic backend synthesis. In its historical sealed snapshot, three shared files remained unchanged while the selected sphere route required 2,635 lines of topology-specific code and changes elsewhere in the compiler. Shared admission and lifecycle interfaces were reused in that instance; the new lowerer still carried substantial implementation and validation obligations. The later prepared measurements concern different, explicitly specialized standard routes and do not measure an extension-productivity benefit.

四段分别完成问题、方法、程序转换、经验认识，允许合并删重。方法中心应在第一页可辨认，转换例子和比较在主文可见，不依赖审稿人阅读内部证据包。

## 7. 将既有结果变成针对设计问题的评价

无需新增实验，重新组织现有 Evaluation 的问题与回答：

| 问题 | 已有证据 | 可回答到哪里 |
| --- | --- | --- |
| RQ1：哪些本地合法或表示兼容的组合需要额外限定？ | W1 源码、W2 lowering、CP002 字段 mutation、capacity 拒绝；各证据等级分列 | 展示实现的检查／转换；不是缺陷普查或完整 soundness |
| RQ2：专门化在哪种程序变化下失效？ | W3 `+1→+2` 前端通过、生成切换的既有组件测试；relation exact-standard guard | 有限识别边界；不是新优化理论或 GPU 语义证明 |
| RQ3：共享机制实际复用了什么，新增工作是什么？ | Goal5838 历史三文件零改、2 launch／12 oracle，约 2,635 LOC 和另 23 additions／5 deletions；Goal5840 有限检查及漏检 | 一次受约束扩展观察；无架构替代组、工时节省或任意拓扑泛化 |
| RQ4：当前具体实现的运行代价是多少？ | M 两代 160 workers／20,480 samples，prepared A/D 1.077–1.175x 及所有 lifecycle 反向结果 | 两精确任务的观测代价；不证明抽象本身低开销，也不做跨代 raw-time 比 |

Goal5844 的历史表示开销对照可作背景或讨论；不强塞成第五项主要证据，不把其动态 stamp 检查替 Goal5851 的逐次 receipt 背书。原 4,096 timed A／32 separate diagnostics 的缺口继续明确。

## 8. 本轮已执行的四项检查与未覆盖情况

运行已提交程序，未编写新测试，未执行 GPU：

```text
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1
/Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python -m unittest -v
  tests.goal5759_v4_triangle_reduction_target_test.Goal5759TriangleReductionTargetTests.test_count_intrinsic_requires_the_exact_standard_callback_ir
  tests.goal5760_v4_bounded_relation_test.Goal5760BoundedRelationTests.test_schema_and_wrapper_are_deterministic_app_neutral_true_optix
  tests.goal5760_v4_bounded_relation_test.Goal5760BoundedRelationTests.test_capacity_overflow_rejects_partial_result
  tests.goal5760_v4_bounded_relation_test.Goal5760BoundedRelationTests.test_duplicate_policy_is_explicit_and_canonical
```

上方为一条命令的分行展示；实际 invocation 把环境设置、解释器和四个 selectors 放在同一命令中。结果：**4/4，exit 0，Ran 4 tests in 0.018s，OK**。含 `true_optix` 的测试名不代表本次使用了 GPU；它检查生成文本／结构。

源码／测试 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| `src/rtdsl/v4_bounded_relation.py` | `4ac50a83ffb80400c6b950150a5702633b3cafa0e43b0b54527f7db44949467a` |
| `src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py` | `f7d1f07b4462a6713a4bcda7aaf64f3a480575f1034059f3fbe61d640044eecb` |
| `tests/goal5759_v4_triangle_reduction_target_test.py` | `3d44b0285afba026333e81abd4f262232db075b5b8150871c9fc14bab767101f` |
| `tests/goal5760_v4_bounded_relation_test.py` | `faa1550b98990c771c20b516b808258edc96b5d0de49c9caca6bf5a9dd4b99fd` |

同一 `git diff --exit-code M HEAD` 检查上述文件及 callback IR 返回 0。该记录不替代原 authority，也不把选择性四项检查包装成整个套件通过。

## 9. 从现在起的执行顺序和三天完成线

所有时间为 America/New_York；都是最晚完成线，提前完成即进入下一步。以 09/09 晚形成可交付包为内部目标，不利用官方最后时刻拖延。[CGO 官方页面](https://2027.cgo.org/track/cgo-2027-papers)列第二轮日期 09/10 和 AoE，并允许正文至多 11 页、references excluded；实际 R8 仍需核对认证表单。保持当前类别，不擅改 Tool／Practical 类型。

| 完成线 | 主 AI 必须交什么 | Lead 的验收问题 |
| --- | --- | --- |
| **09/07 12:00** | 将本文主线和 W1–W3 实际证据写入 N2/N3；N1 增补三组同题对照；列出可保留主张 | 是否有明确的输出义务、实际检查与实际转换？是否仍只讲五项合取？是否把源码推断假装成执行？ |
| **09/07 18:00** | 合并到 Abstract／Introduction／Design／Evaluation／Related Work；交完整新 PDF、source、change map 与逐句 claim 对应 | 第一页是否能回答“研究对象、具体设计、为何要这种检查、证据和代价”？七项旧整改是否保留？ |
| **09/08 12:00** | 第一轮完整新字节独立意见；作者同时完成可独立执行的格式／引用／匿名检查 | 审稿意见必须针对真实新字节。若指认同一方法已存在，按具体来源进一步收窄，而非换名字宣称新颖 |
| **09/08 18:00** | 修正文稿必要问题，形成最后候选，重新记录 PDF/source 身份并交回复审 | 保留 09/08 00:00 开发冻结；此阶段仍只有文稿及既有工具，不再加入实验或改变 M/F2 |
| **09/09 12:00** | 争取完成两份针对最终 pair 的独立接受；未收到就如实 pending | 过期旧票、作者自查、团队分工均不能充当新票 |
| **09/09 20:00** | 在既有授权范围内完成 R8；最终包、表单检查、上传后核对／回执按真实状态登记 | 缺授权、缺接受或未上传时不写 submitted；剩余时间为处理意外缓冲 |

**范围停止点：09/07 12:00 后不再扩增贡献种类和新近邻列表。** 必要反证随时处理，但处理方式是精确修订受影响句子。不要用第三任务、重新调性能、人类研究或新增 soundness theorem 替代本次论证。

第一版合稿建议给中心例子和对照合计约 0.75–1.25 页空间，从重复架构／相同限制的多次解释中腾出；若仍需要，使用合规页数。所有强制 adverse 披露保留。八页是旧候选结果，不是必须维持的科学约束。

## 10. 文稿验收与真实停止标准

主 AI 在既有 novelty 执行目录新增 `CONTRIBUTION_CASE_RESPONSE_20260907.md`，不要再提交一个只有“将要做”的计划。逐项填：

1. 最终核心贡献一句话；具体依赖 W1／W2／W3 中哪些事实。
2. 每个见证的源码／已有检查／本轮重放／历史 GPU 身份和证据等级。
3. 最强近邻已覆盖什么，本文还具体实现和评价什么；UNKNOWN 保留在哪里。
4. 已进入正文的实际新句、位置和新 PDF 页码；N1/N2/N3/ledger/change map 已同步。
5. 所有成本、TCB、原 receipt 缺口及不利结果是否仍准确。
6. 新候选 commit/tree/PDF/source hashes，F2 是否仍为 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8`，剩余 R7/R8 项。

旧 P‴ 保留身份，新内容生成新候选；仍沿用已有 R7/R8 过程。不重跑未变 F2 的整套 R5，不改 24 项 claim 授权，不把这份 lead 论证建议当独立接受。

**我对“本轮解决到位”的标准：审稿人看到的是一个由输出义务驱动的具体 RT 编译设计，有实际约束、转换、专门化边界和对应证据；不再需要从五项机制名称自行猜测研究贡献。** 若某个更强结论没有证据，就删除那个结论，继续交付已成立的系统设计论证。这个标准能靠三天内的具体工作完成；研究新颖性强度及录用仍由真实独立审查决定。
