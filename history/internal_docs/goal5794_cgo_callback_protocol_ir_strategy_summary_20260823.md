# Goal5794：RTDL V4 面向 CGO 的 Callback-Protocol IR 战略总结

日期：2026-08-23  
目标会议：CGO 2027 第二轮，论文截止 2026-09-10  
论文类型选择：standard research paper，而不是 tool paper  
本文性质：内部结论与工作边界；不是投稿稿件，也不是外部送审附件

## 一句话结论

RTDL 的核心学术贡献不应再表述为“Python 写 OptiX”“覆盖了若干 paper app”“比 V2 快”或“能判断任意新应用是否适合 ray tracing”。真正需要证明的贡献是：

> **对于其 admitted bounded subset，RTDL 提出 Callback-Protocol IR，把 repurposed ray-tracing application 的完整 traversal protocol——而不是单个 kernel/shader——提升为编译、检查和物化的单位；编译器接管已声明且受支持的 callback roles、跨 role effects、payload/attribute ABI 与所有权、物理 geometry configuration contract、trusted wrapper/pipeline/SBT 组合、post-traversal continuation、device failure status 和 executable identity。应用仍然拥有 algorithm、semantic oracle 和显式 trusted physical partners。**

工程上最重要的对手是当前 NVIDIA PyOptiX。PyOptiX 给用户完整的 OptiX host API 和构造任意 OptiX 应用所需的机制；RTDL 不能说 PyOptiX“做不了”这些应用。RTDL 必须证明的增量是：

> **PyOptiX 让程序员拥有和拼接 callback protocol；RTDL 让编译器拥有、检查并生成这个 protocol。**

学术上，Slang、Dr.Jit 与 CrossRT 分别代表 capability-aware shader compilation、traced whole-program rendering JIT，以及 algorithm-to-backend translation。我们的安全主张不是它们“不能实现 RTDL”，而是：

> **这些工作的已发表抽象没有建立本文所述的 compiler-owned、non-graphics callback-protocol contract；任何声称同等性质的实现，都需要建立等价的额外 protocol obligations。**

这个主张目前有完整系统和丰富功能证据，但还缺两组决定 CGO 成败的新证据：一组是与当前 PyOptiX 的公平、同任务能力/性能比较；另一组是 Callback-Protocol IR 关键机制的可执行消融。

## 1. 我们究竟解决什么问题

OptiX 已经允许用户自由编写 ray-generation、intersection、any-hit、closest-hit、miss 等程序，并由 host 侧构造 GAS、module、program group、pipeline、SBT 与 launch。对于传统 rendering，这种自由是优势；对于把 traversal repurpose 为图算法、空间关系、计数、邻域搜索或层次查询的应用，真正的“程序”却分散在多个位置：

- host 侧的 geometry、GAS、pipeline、SBT 与 launch 参数；
- 多个 callback 之间共享的 payload/attribute 编码与所有权；
- callback 的允许读写 effect、必需写 effect 和执行顺序；
- built-in triangle 或 custom AABB 的物理语义；
- traversal 完成后的 reduction、continuation 与 failure propagation；
- 被检查的 source/IR 与最终执行的 PTX/native 是否仍为同一程序。

这些接缝如果由应用手工维护，代码可以通过 Python/CUDA/OptiX 的局部类型与 API 检查，却仍可能形成一个整体上错误的 protocol：例如两个 callback 对同一 payload slot 解释不同、一个 role 没有产生下游必需状态、geometry contract 与 callback 假设不一致、device failure 被 continuation 当成有效输出，或者审核过的 IR 与实际执行程序不一致。

RTDL 要解决的不是“自动发现任意算法如何映射到 ray tracing”。它解决的是更窄、但可实现和可验证的问题：

> 当开发者已经选择用 traversal 表达一个 repurposed computation 时，如何把分散在 callbacks、ABI、physical setup 和 continuation 中的整体协议变成一个 compiler-owned contract，并在 code generation 前 fail closed。

## 2. 方案原理

### 2.1 编译单位：完整 callback protocol

RTDL 的 source language 定义七个 language roles：

1. `bounds`
2. `make_ray`
3. `intersection`
4. `any_hit`
5. `closest_hit`
6. `miss`
7. `finalize`

这七个是语言角色，不应错误地称为“七个 OptiX callback entry points”。实际 OptiX entry roles 是 raygen、intersection、any-hit、closest-hit 和 miss；trusted raygen wrapper 调用相应 language leaves，并负责 launch/trace/finalization 边界。

### 2.2 静态闭合的 protocol obligations

Callback-Protocol IR 将以下内容放入一个可检查对象：

- 每个 role 允许的 effect shapes，以及适用时的 mandatory-role/topology requirements；
- payload 与 attribute 的类型、slot、读写权限和所有权；
- resource limits；当前实现明确限制为最多 32 个 payload slots、8 个 attribute slots、trace depth 1、callable depth 0；
- callback 与 custom AABB / built-in triangle 物理 geometry contract 的一致性；
- trusted wrapper、pipeline、SBT 与 continuation 的组合关系；
- device failure status 是否在 host continuation 前被检查；
- source、IR、effect projection、physical authority 与 executable identity 的绑定。

### 2.3 生成与执行

受限 source 被解析为 typed IR，而不是作为任意 Python 导入执行。对于 admitted/supported composition，验证通过后，编译器生成受控 device leaves 和 wrapper，物化受支持的 OptiX program groups/pipeline/SBT，并通过准备—执行—关闭生命周期运行。应用仍然提供 algorithm、semantic oracle 与任何显式 trusted physical partner。CPU interpreter 提供独立于 GPU route 的 role-level reference semantics，但它不是任意应用语义的证明。

### 2.4 为什么这种方法有用

它改变的不是“Python 能不能调用 OptiX”，而是谁对 protocol 接缝负责：

- 在 PyOptiX/OptiX 中，应用可以手工正确地完成这些工作；正确性责任主要属于应用作者。
- 在 RTDL 中，开发者声明受限 roles 与 contracts；编译器必须拒绝未闭合的 effect、ABI、physical binding、status 或 identity，并生成其余 protocol machinery。

因此论文要测的是“责任转移”和“可复现地阻止哪类整体协议错误”，而不是用 LOC 代替易用性，也不是用 Python 语法代替编译器贡献。

## 3. 与 PyOptiX 的准确区别

截至 2026-08-23，NVIDIA 的 `otk-pyoptix` 官方仓库将自身描述为 OptiX host API 的完整 Python bindings；README 给出 OptiX 9.1 的 `pip install pyoptix` 安装路径。NVIDIA 2022 年还公开展示过 PyOptiX/Numba 编写 Python ray-generation、closest-hit 和 miss device programs。因此，下列主张全部禁止：

- “RTDL 是第一个 Python OptiX system”；
- “RTDL 首次允许 Python-authored callbacks”；
- “RTDL 首次把 Python 编译到 PTX”；
- “PyOptiX 不能实现 repurposed applications”。

公平比较如下：

| 维度 | 当前 PyOptiX 的强项 | RTDL 要证明的不同点 | 当前状态 |
|---|---|---|---|
| API 范围 | 完整 OptiX host API；低层能力广 | 有意受限的 repurposed-app protocol | PyOptiX 更广 |
| 用户自由度 | 用户可手工组合任意 module/program group/pipeline/SBT | 编译器只接受并生成闭合 protocol | RTDL 更窄 |
| device authoring | 官方当前 examples 使用正常 OptiX device-program 路径；历史官方 demo 已证明 Numba callbacks | 受限 source 先进入 typed/effect IR，再生成 device code | 差异不能写成 Python vs CUDA |
| callback 接缝 | proposed direct PyOptiX baseline 将 payload/SBT/trace/program bindings 作为 application-owned code | role/effect/ABI/ownership 由 compiler contract 约束 | 责任差异仍需 source-backed 实证 |
| physical setup | proposed direct PyOptiX baseline 将 GAS、geometry、pipeline choices 作为 application-owned code | typed physical contract 与 trusted wrapper 共同约束 | 已有实现；需 matched-task 证明 |
| failure/continuation | proposed direct PyOptiX baseline 由应用实现 | status envelope 与 continuation ordering 进入 protocol | 需可执行负例 |
| 可扩展性 | 接近 OptiX 的全部表达能力 | 当前仅 bounded subset | PyOptiX 明显更强 |
| 性能 | 尚无与 RTDL 的 matched measurement | 不预设胜负；分离 cold/preparation/prepared execution | **未知** |
| 易用性 | 尚无 functionally matched user study | 只允许报告结构性责任，不允许“更容易” | **未知** |

核心工程论点只能是：对于 RTDL 支持的 protocol 子集，用户少拥有若干容易出错的跨-callback responsibilities，而且这些 responsibilities 确实被 compiler checks/generation 接管。若最终只是一个更窄的 PyOptiX wrapper，或者用户仍需进入 internal provider/loader/PTX/SBT 路径，则论文核心失败。

## 4. 与 Slang、Dr.Jit、CrossRT 的非敌对学术定位

| 工作 | 它解决的问题 | 不应抢夺的贡献 | RTDL 的不同层次 |
|---|---|---|---|
| Slang | 跨 target/stage/API extension/hardware feature 的 capability inference 与 enforcement；也支持 OptiX target | target capability、shader typing、cross-platform shader language | published capability model 判断代码对目标/阶段是否合法；RTDL 研究完整 non-graphics callback/payload/SBT/continuation protocol 是否闭合。Slang 可以成为 RTDL 的 leaf compiler |
| Dr.Jit | trace 高层 Python/C++ rendering computation，进行全局简化、专门化、依赖分析和 CPU/GPU JIT | traced whole-program optimization、differentiable rendering、global specialization | RTDL 不做 Dr.Jit 式全局 tracing/optimization；它显式表示并闭合 restricted callback protocol |
| CrossRT | 从 hardware-agnostic OO C++ algorithm translation 到多种 RT API/hardware，支持 fallback、megakernel/wavefront，并覆盖 SDF、Gaussian splatting 等 CG/CV workloads | mapping discovery、cross-platform translation、editable generated implementations | CrossRT 解决 algorithm-to-backend translation；RTDL 提供一个 translator 或人可以 target 的 protocol IR，负责 cross-role effects、ABI、physical/status/continuation/identity closure |
| PyOptiX/OptiX | 暴露完整 NVIDIA RT mechanism 与 host control | Python binding、OptiX programmability、arbitrary manual pipeline construction | RTDL 在其上增加 compiler-owned protocol contract，并牺牲表达范围换取静态闭合与生成 |

最清楚的组合关系是：

```text
application algorithm
        |
        |  optional mapping/translation (CrossRT-like problem)
        v
RTDL Callback-Protocol IR
        |
        |  optional leaf compilation (Slang/Numba-like problem)
        v
PyOptiX / OptiX host and runtime mechanisms
```

Dr.Jit 位于相邻的 whole-program rendering tracing/optimization 方向，而不是这个 stack 中必须替代的一层。

论文的 related-work 句子应固定为：

> Their cited published abstractions do not establish this compiler-owned non-graphics callback-protocol contract; RTDL must demonstrate the additional contract layer empirically.

不能写成“Slang/Dr.Jit/CrossRT 都不能解决我们的应用”。

## 5. 当前证据：有什么，缺什么

### 5.1 已经有的系统证据

- V4 已在 9 个 applications、13 条 paper lanes 上产生 exact output 与 behaviorally true-OptiX execution evidence。这里是 13 条 paper lanes，不是“13 个功能路径”。
- Goal5785 的现代 RTX cohort 有 464/464 exact 且 behaviorally true-OptiX workers、34 条独立 V2-direct/V4 rows。
- 按 row-local median，V4 是 16/34 pass、18/34 fail；cold 为 4/15，prepared 为 12/19。按 95% CI 分类是 11 clear V4 wins、10 clear V4 losses、13 uncertain。准备成本单独报告，不免费。
- 九个应用都有 source-backed physical-owner preparation / traversal-receipt structural shift；native runtime loader 由 registered V4 interface 封装为 8/9。RayDB 是唯一 private `_load_optix_library` 例外，但它不是手工组装 pipeline/SBT 的证据。
- Callback IR 已实现七个 language roles、closed effects、typed ABI、资源上限、CPU semantics、fail-closed validation 和 executable binding。

### 5.2 不能混淆的有限证据

- Goal5789 的 15 条 registered-lane inventory 是 semantic/physical admission 结果：6 `COMPATIBLE`、9 fail-closed `UNKNOWN`、0 `INCOMPATIBLE`。15 条都 target-capable 且 instance-admissible；9 个 UNKNOWN 缺独立 semantic authority，并仍各有 physical/composition gap。它不是性能结果，也不是“9 条功能没跑通”。
- Callback authority binding 证明执行 program identity 与 projection 一致，不证明 application semantics 正确。Particle 与 RTXRMQ 曾共享 byte-identical callback program，这正说明 identity 不等于语义区分。
- hostile matrix 应报告为 143 negative mutations、15 baselines、1 passing TCB control；不能说“159 个精确 rejection”。
- verifier 不证明任意用户逻辑的全局 confluence 或 order-independence。
- Goal5793 prospective-generalization branch 因 frozen live-provider protocol 的 terminal infrastructure failure 而停止；新问题上的 generalization exams 仍是 0。这可以作为研究诚实性的披露，不能替代系统贡献证据。

### 5.3 当前最危险的缺口

1. **稳定公共 GPU API 未闭合。** `rtdsl.v4` 当前稳定 authoring surface 只有 parse/verify、CPU role execution、ABI/proof；generic `prepare -> execute -> close` 不在稳定 callback-authoring namespace。`rtdsl.v4_prepared_provider` 以及 `open_v4_callback_provider` / `V4VerifiedCallbackProvider` 是 advanced/internal。
2. **与当前 PyOptiX 的 matched comparison 为 0。** 既有 V2-direct/V4 performance 不能代替 PyOptiX baseline。
3. **Callback-Protocol IR 的机制价值缺少最简洁的同任务消融。** 历史上 `roles[].effects` 曾经是 inert leaf，说明“字段存在”绝不等于“机制有效”。
4. **usability study 为 0，functionally matched CUDA/OptiX/PyOptiX baseline 为 0。** 不能声称 easier、simpler、less code、more productive 或 better than CUDA/OptiX。

## 6. 对两个最高风险 concern 的当前回答

### Concern 1：只在试过的地方有效，一泛化就干不了

当前评分：**防止夸大 8/10，正面泛化证据 0/10。**

我们已经停止使用 RTXRMQ held-out、registered-family、arbitrary-new-app 等不成立的语言；Goal5793 返回 terminal undischarged，也没有偷修 provider 后继续抽样。这防住了欺骗，但没有产生新应用 generalization evidence。

下一阶段不再幻想“证明任意新 app”。CGO 贡献改为一个明确边界的 compiler abstraction，并用以下证据证明它不是只对旧 app 的装饰：

- 两个预先冻结、双方都能表达的 matched repurposed tasks；
- custom-AABB 与 built-in-triangle 两种物理 geometry mechanisms；
- 同一公开 API，不允许 app-specific internal escape；
- 五项 protocol mechanisms 的可执行消融和 valid controls；
- 九应用/十三 paper-lane 作为多样性证据，但不外推为任意新 app。

这不能证明 universal generalization；它能证明方法跨两个不同 physical mechanisms 和多个 protocol shapes 工作，并明确给出不支持的边界。这是 compiler paper 可辩护、而非虚假的范围。

### Concern 2：花里胡哨，用户实际还不如直接 PyOptiX/CUDA/OptiX

当前评分：**没有虚假易用性 claim 8/10，正面可用性证据 2/10。**

最大事实不是性能，而是公共 API 仍未闭合。只要用户需要进入 internal provider/loader/PTX/SBT route，RTDL 就不能声称真正接管 protocol。Goal5795 因此是 submission-critical，不是 polish。

下一阶段不做虚假的 LOC 或开发时间比较。我们将对同一两个任务，逐项审计：用户必须手写的 callback ABI contracts、cross-role state contracts、lifecycle transitions、failure propagation、pipeline/SBT/GAS glue 和 identity checks。每个声称由 RTDL 接管的项目必须能定位到 validator 或 generated code。性能单独测量，PyOptiX 赢也完整报告。

## 7. 投稿前必须得到的新增证据

1. 冻结当前 PyOptiX exact version/commit、OptiX/CUDA/driver/Python 环境，并运行其官方 smoke，确认 baseline 真实可用。
2. 将 RTDL 的 generic callback `materialize -> prepare -> execute -> close` 提升为稳定公共 API，两个 matched apps 均不得调用 private loader/provider/PTX/SBT route。
3. 实现两个 matched non-rendering tasks：
   - custom-AABB spatial relation/count；
   - built-in-triangle query/reduction。
4. 两边使用同一算法、输入、精度、tie-break、资源预算与独立 CPU oracle；先 exact-output，再计时。
5. 建立 protocol-seam responsibility rubric，报告 compiler-owned 与 user-owned obligations，不用 raw LOC 充当 productivity。
6. 对 effects、ABI/ownership、physical wrapper/binding、status/continuation、identity binding 做单因素可执行消融：full RTDL 拒绝；消融版错误接收并产生可归因 violation；同时有合法 control，防止只会拒绝。
7. 在 preregistered designated Linux host、同一 GPU、同一 OptiX/driver/input 上分别报告 fresh-process cold、preparation、prepared execution 和 memory；任何 preparation 都不免费。
8. 论文 related work 逐句由 PyOptiX、Slang、Dr.Jit、CrossRT primary sources 支撑；不使用“不能解决”的绝对句式。

## 8. CGO claim ceiling

如果上述证据成立，论文可以主张：

> RTDL introduces a Callback-Protocol IR that makes a complete traversal-driven protocol the unit of high-level compilation for a bounded class of repurposed OptiX applications. On two matched non-rendering tasks and nine existing applications, the implementation transfers specified cross-callback protocol responsibilities from application code to compiler checks and generation, rejects demonstrated protocol violations before launch, and preserves exact outputs. Its performance relative to PyOptiX is reported by lifecycle phase and is mixed/whatever the measurements show.

即使全部完成，也仍然禁止：

- arbitrary-new-app、universal、complete、formally verified 或 semantic soundness；
- “支持所有 paper/app family”；
- “比 PyOptiX/CUDA/OptiX 更容易”而没有用户研究；
- “比 PyOptiX 更快”而没有 matched evidence；
- 把 CrossRT 写成 rendering-only；
- 把 Slang capability 或 Dr.Jit tracing 说成无关或无效；
- 把 artifact governance 本身当成学术 novelty。

## 9. 现在的处境

RTDL 不是“没有系统”：九应用功能实现、现代 RTX exact execution、完整 Callback IR 和 mixed performance 都是真实成果。RTDL 也不是“已经达到 CGO”：目前 reviewer 最容易给出的拒稿理由仍是“PyOptiX + validation glue；没有公平 baseline；公共 API 不完整；机制价值没有消融”。

因此，离 CGO 的距离不是再做一次大规模旧应用审计，也不是再尝试证明无法证明的 universal generalization。距离恰好是四件事：

1. 闭合公共 API；
2. 做公平的 PyOptiX matched comparison；
3. 用消融证明 Callback-Protocol IR 的不可删减价值；
4. 用非敌对 related work 把这个层次讲清楚。

这四件事正是 Goals 5794–5799 的唯一主线。

## 10. Primary sources（访问于 2026-08-23）

- NVIDIA, current PyOptiX repository: https://github.com/NVIDIA/otk-pyoptix
- NVIDIA, Numba extension for PyOptiX demonstration: https://developer.nvidia.com/blog/writing-ray-tracing-apps-in-python-using-numba-for-pyoptix/
- Slang capability system: https://shader-slang.org/slang/user-guide/capabilities
- Slang OptiX target support: https://docs.shader-slang.org/en/stable/external/slang/docs/cuda-target.html
- Dr.Jit paper: https://arxiv.org/abs/2202.01284
- CrossRT paper: https://arxiv.org/abs/2409.12617
- CGO 2027 call for papers: https://conf.researchr.org/track/cgo-2027/cgo-2027-papers

## 11. Local evidence anchors

- `docs/v4/nine_app_coverage.md`
- `docs/v4/README.md`
- `docs/v4/callback_ir_v1.md`
- `docs/v4/api_reference.md`
- `history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816.json`
- `history/internal_docs/goal5785_v6_rtx4000ada_final_technical_report_20260816.md`
- `history/internal_docs/goal5792_local_completion_technical_report_20260820.md`
- `history/internal_docs/goal5792_source_backed_responsibility_audit_result_v3_20260820.json`
- `history/internal_docs/goal5789_primary_source_related_work_matrix_20260816.md`
- `history/internal_docs/goal5789_novelty_boundary_and_claim_kill_gates_20260816.md`
- `history/internal_docs/review_goal5793_x3_provider_search_terminal_failure_20260822.md`
