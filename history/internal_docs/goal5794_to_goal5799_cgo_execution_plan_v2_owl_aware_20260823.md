# Goals 5794–5799：OWL-aware Callback-Protocol IR CGO 执行计划 v2

日期：2026-08-23  
CGO 2027 R2 截止：2026-09-10  
不可侵占的写作期：2026-09-03 至 2026-09-09  
目标：standard research paper  
本文件状态：**controlling**；supersedes `goal5794_to_goal5799_cgo_execution_plan_20260823.md` 的执行授权，但不删除旧文件

## 一句话研究问题与贡献门

> Can a compiler make the whole callback protocol—not individual OptiX programs or host API calls—the checked compilation unit for a bounded class of repurposed RT-core applications, and thereby reject cross-program defects that remain possible even when a mature library already owns pipeline, SBT, acceleration-structure, buffer, and launch composition?

RTDL 的论文贡献不再包含“帮用户构造 SBT/pipeline/GAS/lifecycle”本身，因为 OWL 已经覆盖这些成熟 composition responsibilities。论文只争取证明五个 residual mechanisms：

1. role/effect closure；
2. payload/attribute ABI + ownership；
3. physical/geometry binding consistency；
4. device status + continuation；
5. checked-program/executable identity。

五项中任何一项若不能通过 mutation-liveness 与 semantic-necessity 两道试验，就不得进入核心贡献。整个计划不宣称 arbitrary-app generalization、formal soundness、ease/productivity 或 universal speedup。

## 评价对象：四个 execution arms

| ID | Arm | 冻结目的 | 允许的比较 |
|---|---|---|---|
| A | Direct CUDA/OptiX | 低层 reference implementation | 完整手工路径的 correctness/performance；不是主 responsibility headline。|
| B | Current NVIDIA PyOptiX | 主要工程 baseline | Python host bindings 下的实际 device-authoring path、protocol responsibility 与 lifecycle-separated performance。|
| C | Current NVIDIA OWL | 成熟 composition baseline | 承认 OWL 已接管的 SBT/AS/program/pipeline/buffer/launch 工作；测 residual whole-protocol defects。|
| D | RTDL public Callback-Protocol API | candidate system | 五项 compiler-owned contract 的有效性与成本。|

`PyOptiX + OWL` 不被假设为一个天然组合产品。若 exact-source inspection 没有证明二者可正常组合，则 B 与 C 是两个独立 baseline arms；论文不能写成一个虚构的“PyOptiX+OWL”实现。

## 三张责任表必须分开

1. **Composition ownership**：GAS/IAS、program groups、pipeline、SBT、buffers、launch setup、refit/compact、lifecycle。该表的作用是承认 OWL 已有能力，不是 RTDL novelty score。
2. **Protocol-contract ownership**：五项 residual mechanisms。该表以 OWL→RTDL 的差异为 headline，PyOptiX 同列作工程背景。
3. **Device-language path**：每个 role 到底由 CUDA C++、Python/Numba、RTDL restricted source、generated PTX 或其他路径编写。它只披露 language change，不与 protocol ownership 相加，也不产生“更少代码/更简单”的分数。

所有表都必须有 `remains application-owned` 列：算法、semantic oracle、problem-to-ray/geometry mapping、precision、tie-break、resource budget、声明的 trusted physical partners。

## Goal5794 — Exact PyOptiX/OWL freeze、matched S0 与 preimplementation coverage

时间：2026-08-23 至 2026-08-24  
允许动作：read-only source/network investigation、隔离环境准备、官方 smoke、无 timing 的功能检查  
禁止动作：正式 measurement、隐式 driver upgrade、为适配 baseline 改写 scientific task

### 5794-A：Exact baseline 与 environment

冻结：

- PyOptiX repository commit/tag、PyPI version、sdist/wheel SHA-256、build flags；
- OWL repository commit、source archive SHA-256、build flags；
- direct CUDA/OptiX reference source；
- OptiX SDK、CUDA toolkit、driver、compiler、Python、CuPy/cuda-python；
- GPU model、compute capability、memory 与 modern RT-core status；
- A/B/C/D 可否在完全相同环境执行；不能时明确 incompatibility，不做跨机器 performance ratio。

当前 local Linux `192.168.1.20` 只允许继续做 read-only/functionality 工作。已知它是 GTX 1070 / CC 6.1 / driver 580.126.09，不能承担 modern RT-core performance。不得擅自升级。Goal5798 前必须冻结一台 modern RTX host，并让所有可执行 arms 使用同一环境。

### 5794-B：Device-authoring path 是一等结果

逐 role 记录 PyOptiX 与 OWL 官方/normal-practice 路径，特别是 custom intersection：

- raygen；
- miss；
- closest-hit / any-hit；
- custom intersection；
- bounds；
- post-traversal continuation。

如果 current PyOptiX 使用 Python host + CUDA device source/NVRTC，就原样使用。2022 Numba demo 仅按其实际覆盖的 raygen/closest-hit/miss 描述，不能外推 intersection。任何 language difference 与 protocol transfer 分开报告。

### 5794-C：两个 matched repurposed tasks

**Task A — `CUSTOM_AABB_CLOSED_RELATION_COUNT_V1`**

- geometry mechanism：custom AABB + custom intersection；
- roles：bounds、make-ray、intersection、hit role、miss、finalize；
- shared semantics：固定 input encoding、relation predicate、precision、capacity/overflow policy、canonical row order、tie-break 与 output schema；primary output 是 canonical relation rows；若论文展示 scalar count，A/B/C/D 都只能从相同 rows 派生 `len(rows)`；
- RTDL execution path 必须使用 composed generated executable 的 bounded-relation family；禁止用 `v4_aabb_relation_count_lowering` 冒充 Callback-IR execution，因为该旧路径虽绑定 callback authority，却经 private loader 执行 legacy `aabb_index`；
- baseline 可使用正常 CUDA intersection，不把 device-language 差异算作协议优势；本轮不新增 direct-device-scalar-count wrapper/native ABI。

冻结 semantics/fixtures：

- callback/oracle authority：`v4_box_relation_callback.py::{BOX_RELATION_SOURCE, compile_callback, physical_schema, exact_closed_aabb_relation}` 与 `v4_bounded_relation*` generated path；
- primary existing fixture：LibRTS tiny，oracle canonical rows 数量 8；main capacity 8；overflow witness capacity 7 且 partial rows 不得被 application consumer 接收；
- boundary fixture：edge/corner/one-f32-below 命中，one-f32-above 不命中；输入只做一次 binary32 round trip；
- diagnostic fixture：primitive `id=10` 为 `x=0..4,y=0..1`，primitive `id=20` 为 `x=0..1,y=0..4`；query `id=100` 为 `x=2..3,y=.25..75`，query `id=101` 为 `x=.25..75,y=2..3`；正确 rows 为 `[(100,10),(101,20)]`；
- IDs 为 U32；rows lexicographic unique；per-query count/min-U32（miss=`U32_MAX`）；total count checked-U64；status 必须先于 result consumption。

**Task B — `BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1`**

- geometry mechanism：OptiX built-in triangles；
- roles：make-ray、hit/miss、checked reduction/finalize；
- shared semantics：固定 input、triangle/query mapping、precision、duplicate/tie policy、checked-U64/status、output schema；
- RTDL 使用已闭合的 generated triangle-reduction executable family，经新增 public facade；
- A/B/C 使用同一算法、数据与 oracle，不以不同 reduction algorithm 换取性能。

冻结 semantics/fixtures：

- callback/schema authority：`v4_triangle_standard_library.py::{COUNT_SOURCE, compile_count_callback, weighted_hit_count_schema}` + triangle-reduction prepared runtime；
- independent oracle：`scripts/goal5758_m1_independent_oracles.py` 的 checked-U64 oracle，不导入任何 GPU arm；
- diagnostic geometry：相同 XY footprint、分别位于 `z=1,2,3` 的三枚 triangles；另有两枚位于 `x=3,z=1` 的 coincident triangles；
- 四条避开 edge/tie 的 `+z` rays，预期 per-ray counts `[3,2,0,1]`；weights `[1,3,5,7]`；checked weighted scalar `16`；
- `tmin/tmax` 固定覆盖上述 layers；no backface culling；coincident primitives 分别计数；payload U64；trace depth 1；callable depth 0；overflow fail closed。

两个 tasks 都是 designed matched case studies，不是 unseen、blind 或 generalization exams。

### 5794-D：Mechanism × task coverage matrix

下表必须在实现前冻结。表中 `L` 与 `B` 是两套独立实验，不能混称一个消融：

- `L = mutation-liveness`：只改 mechanism declaration，device/host executable bytes 不变；重算所有 mutable seals/pins/bundle identities；full verdict 必须 `ACCEPT→REJECT`；
- `B = behavioral ablation`：构造 coherent invalid program/continuation，所有身份按真实 bytes 重封；full 只因该机制拒绝，only-that-mechanism ablated system 必须 accept、launch success，并产生预注册 wrong output/invariant。

exact diagnostic reason id 在任何 attack run 前由 current checker probe 冻结；若当前实现使用不同 reason 名，允许更新 preregistration 中的名字，不允许在看到 outcome 后改变判定语义。

| Mechanism | Primary task | L：只改声明 | B：coherent accepted-invalid | Nearby valid controls | Required wrong result / invariant |
|---|---|---|---|---|---|
| Role/effect closure | Task B | 清空 any-hit 的 payload-write / accept-continue effects；完整重封；executable 固定 | device any-hit 从 `count+1; continue` 改成 `count+1; terminate`，但 declaration 仍声称 continue；source/executable identities 按真实新 bytes 更新 | 原 full program；可选的 terminate + existence-semantics 合法配对 | expected `[3,2,0,1]`, weighted `16`；ablated 得 `[1,1,0,1]`, weighted `11`。|
| Payload/attribute ABI + ownership | Task A | attr0 declaration 的 producer meaning 从 application `item_id:u32` 改为 `primitive_index:u32`；slot/type width 不变；executable 固定 | intersection 实际报告 `optixGetPrimitiveIndex()` 0/1，而 consumer/task declaration 仍解释为 item ID 10/20；所有 source/executable identities coherent | attr0 实际且声明都为 application item ID | expected `[(100,10),(101,20)]`；ablated 得 `[(100,0),(101,1)]`；避免 UB/OOB，把错误限定为同型 semantic ownership。|
| Physical/geometry binding | Task A | physical declaration 中交换同为 f32 的 `query.lower.x` / `.y` host projection；wrapper/executable 固定 | actual wrapper/SBT mapping 交换 query x/y arrays；declaration/callback 保持原 mapping；wrapper identity 与所有 seals 更新，避免 identity mechanism 先拦 | unswapped physical mapping | expected `[(100,10),(101,20)]`；ablated 得 `[(100,20),(101,10)]`；不能以 geometry enum mismatch 代替。|
| Device status + post-traversal continuation | Task A tiny | continuation declaration 从 `REQUIRE_COMPLETE_BEFORE_CONSUME` 删除/改成 `ALLOW_PARTIAL`；executable 固定 | capacity 7 触发 overflow，host continuation 忽略 status 并排序/返回已写 prefix；host executable identity coherent | 同一 host path，capacity 8，COMPLETE，8 exact rows | invariant `status=OVERFLOW` 且 `application_result_consumed=true`；returned row count 7≠8；不预称具体缺哪行。|
| Checked program↔executable identity | Task B | authority A 的 checked-executable projection 指向 B，而 device bytes 仍 A；所有 mutable seals 重算 | A=`count+1` 合法且 expected 16；B=`count+2` 合法且 expected 32；把真实 B executable 与 task/certificate A 配对，外围 file identities/pins 全按 B 重算，只让不可变 checked-A projection 失配 | A/A=16 与 B/B=32 均 full accepted，构成 reject-all guard | identity-ablated 正常 launch，counts `[6,4,0,2]`, weighted `32`≠task-A authority expected `16`。|

每个 B-case 必须同时满足：OptiX validation PASS、CUDA last-error SUCCESS、process exit 0、baseline exception none；否则不能把结果归因于 RTDL mechanism。CPU oracle 只作 outcome detector，不是一个“先行拒绝的 baseline validator”。每行保存 full exact primary reason、ablated acceptance receipt、wrong output/invariant 与 nearby-valid receipt。

对 PyOptiX/OWL 的预期是“它们不拥有这些高层 cross-program semantics”，但这只是 pre-run hypothesis。每一行必须由 pinned source 或 frozen execution 验证；若 OWL 实际阻止某 defect，该行不得继续称为 RTDL-over-OWL residual。

### 5794-E：Related work freeze

建立四个互不树敌的学术轴：

- PyOptiX：host-language/API binding baseline；
- OWL：OptiX composition/lifecycle abstraction baseline；
- Slang / Dr.Jit / CrossRT：相邻 compiler/IR/language systems，逐项说明层次与 scope，不说“它们不行”；
- RT-core repurposing：从 2026 review 的 59-paper bibliometric corpus、35-paper systematic subset、32 distinct problems 出发，审查代表性 physics、geometry、database、AI、graph works 采用了什么 programming layer。

只允许的 gap claim：在被审查的 sources 中，未发现一个把 repurposed application 的完整 callback protocol、physical binding、status/continuation 与 executable identity 一并作为 checked compilation unit 的系统。若发现反例，立即改 thesis。

### Goal5794 完成门

- exact PyOptiX 与 OWL identities/archives/hash 可复核；
- normal device-authoring path 已按 role 冻结；
- two-task spec 与 independent CPU oracle 固定；
- mechanism×task matrix 每个 primary cell 可执行；
- responsibility rubric 分成三张表；
- no formal timing；
- 输出 Goal5794 result/technical report，并成为 Goal5795 的 controlling S0。

## Goal5795 — 闭合 bounded public Callback-Protocol lifecycle

时间：2026-08-24 至 2026-08-26 18:00 America/New_York  
性质：submission-critical product implementation

### 准确能力边界

本 Goal 不尝试在两天内造一个任意 OptiX callback runtime。它为两个已闭合 standard families 提供同一个 app-neutral public facade：custom-AABB bounded relation 与 built-in-triangle reduction。公开能力必须写成 bounded family support，而不是 arbitrary callback support。

当前 `rtdsl.v4` 只公开 parse/verify、single-role CPU interpretation 与 ABI；没有 target/materialize/prepare/GPU execute/close。`CallbackProgramSpec` 与 `AnyHitProofAuthority` 等必需类型也未形成完整公开 surface。`v4_prepared_provider` 是 advanced/internal、sphere-only，不能作为两任务公共 API。

### 最小 public lifecycle

通过 documented stable namespace 提供：

```text
parse/construct program
  -> verify(program, physical_plan)
  -> materialize(target)
  -> prepare(resources)
  -> execute(inputs)
  -> result + status + identities
  -> close()
```

要求：

- public typed program、physical plan、target 与 proof inputs；
- app-neutral family selection，不含 paper/app registry name；
- prepared object context manager、deterministic close、double-close/use-after-close rejection；
- CPU interpreter 与 GPU route 接受同一个 public program object；
- status 在 application result 暴露前 fail closed；
- source/IR/effect/physical/generated executable/loaded executable identities 可查询并绑定；
- public prepared object 的 `close()` 必须真实 idempotent；existing internal owners 的 double-close 行为不作为 public contract 泄漏；
- matched apps 不导入 `_load_optix_library`、`v4_prepared_provider`、paper-app modules 或 hand-written private PTX/SBT route。

### 必须测试

- clean install + public-import-only；
- Task A 与 Task B public Linux smoke；
- exact CPU/GPU result；
- deterministic close、double-close、use-after-close、foreign-context；
- status failure propagation；
- coherent identity mismatch rejection；
- private/internal import scan；
- task-name perturbation，证明 facade 不靠 registry name 分支。

### Aug 26 stop gate

若 2026-08-26 18:00 前两个任务任一仍需 private/internal path：

- CGO 2027 standard-research plan `NO_GO`；
- 不开启 Goal5798 formal timing；
- 单独成功的一条可继续作为工程诊断，但不能把 two-task evaluation 改写成 one-task success；
- 不使用旧九应用或旧 V2/V4 数据替代；
- 转 CGO 2028 first available round，继续闭合 API。

## Goal5796 — A/B/C/D matched implementations、correctness 与 responsibility

时间：2026-08-26 至 2026-08-28  
依赖：Goal5794 S0 + Goal5795 两条 public smoke

### 实现约束

- 四臂使用相同 algorithm、input、precision、tie-break、resource budget 与 output；
- independent CPU oracle 不导入任何 GPU arm；
- B/C 使用其正常最佳实践；不得故意手写已有库通常接管的工作；
- D 只使用 Goal5795 public API；
- exact-output correctness 在 performance 之前；
- freeze source、generated code、compile flags、layout 与 execution identities；
- 若 full runnable OWL arm 在 schedule 内确实不可行，最小替代是 source-backed OWL responsibility analysis，显式标记 `analysed_not_implemented`；此时不得给出虚构 OWL performance。

### 交付物

- A/B/C/D implementations 或明确的 OWL analysed-only status；
- shared fixtures + independent oracle；
- exact correctness receipts；
- composition / protocol / device-language 三张 source-backed tables；
- `remains application-owned` 与 baseline diagnostic-experience columns；
- application table，其中 RayDB 行显式标注 historical private-loader escape；
- limitations ledger。

### 完成门

- Task A/B 所有 registered fixtures 对所有可执行 arms exact；
- 两种 geometry mechanisms 均覆盖；
- OWL 已有 composition 责任未被记入 RTDL novelty；
- 每个 RTDL compiler-owned 项能定位到 validator/generated code；
- 每个 baseline application-owned 项能定位到 source 或官方行为；
- 没有 usability/productivity inference。

## Goal5797 — 五机制 liveness + semantic necessity 消融

时间：2026-08-29 至 2026-08-31 18:00 America/New_York  
依赖：Goal5796 exact frozen implementations

### 每项两道不可替代的试验

**Test 1 — mutation-liveness**

- 从 full accepted real program 出发；
- 只改该 mechanism declaration；
- coherently recompute/reseal 所有 derived identities；
- 其余 bytes/algorithm/input/backend 固定；
- full verdict 必须发生预注册的变化；
- exact mutation set、verdict delta、sole/expected reason 写入 evidence。

**Test 2 — semantic necessity**

- full system launch 前拒绝 concrete defect；
- only-this-mechanism ablation 接受；
- 执行产生 wrong result 或 protocol invariant violation；
- nearby valid control 被 full 接受且 exact；
- 证明其他 validator 没先行阻止；
- 对 PyOptiX/OWL 记录真实结果：static reject、runtime diagnostic、silent wrong、或不适用。

### 机制特定要求

- effects：必须包含历史 inert `roles[].effects` 同类 mutation；
- ABI/ownership：必须改变 producer/consumer interpretation，不只改 unused metadata；
- physical binding：必须产生错 hit/output，不接受 sole hash mismatch；
- status/continuation：必须让 invalid/incomplete status 越过 consumer boundary；
- identity：必须是 coherent resealed executable swap 并产生 wrong output。

### Aug 31 stop gate

- 任一 liveness test verdict unchanged：该机制 inert，立即删除 claim；
- effects、ABI/ownership、physical binding 任一无完整 necessity evidence：CGO 2027 core `NO_GO`；
- status 或 identity 若只证明 defensive reliability：可降为 implementation feature，但不得继续称为不可删减核心机制；
- 不增第三任务、不换 post-hoc metric、不用 hostile-case count 填空。

## Goal5798 — 同机 modern-RTX correctness 与 performance

时间：2026-09-01 至 2026-09-02 18:00 America/New_York  
依赖：Goal5794–5797 gates 全通过；Checkpoint A 已批准 exact experimental contract

### Premeasurement freeze

- exact modern RTX host/GPU、driver、OptiX、CUDA、compiler、power/clock policy；
- A/B/C/D exact source/generated code/native/PTX；
- dataset、algorithm、layout、resource budget、oracle；
- arm/task/sample run order 与 interleaving；
- fresh-process policy、warmup、sample count、statistics、CI；
- timers：cold end-to-end、module/program/pipeline/GAS preparation、prepared execute、validation/compile、memory；
- correctness failure disposition 与 no-retry/no-row-drop rule。

### 报告原则

- A/B/D（direct CUDA/OptiX、current PyOptiX、RTDL）是回答用户三个核心问题所需的 mandatory executable comparison；C/D（OWL、RTDL）在 full OWL arm 可按 frozen semantics 实现时同机测量。若 OWL 只能做到 source-backed `analysed_not_implemented`，只报告责任边界，不伪造 OWL timing，也不把它计入 performance completion denominator；
- preparation 不免费；每个 phase 分开并共同展示；
- incorrect samples 不进 performance aggregate，但完整列为 correctness failure；
- PyOptiX/OWL 更快就如实报告；
- RTDL 相近/更快只限两个 tasks、exact host 与 exact lifecycle phase；
- 不以 GTX 1070、旧 V2/V4 34-row cohort 或跨机器 ratio 补空；
- raw samples 与 independent recount 一并保存。

### Sep 2 stop gate

若无法取得同机、matched、exact 的 A/B/D comparison，就不能回答“与 PyOptiX 和 direct CUDA/OptiX 比性能如何”。在当前论文定位下 CGO 2027 `NO_GO`；不得降格为主机 microbenchmark 或把旧数据改名。若 C 已实现却未测量，同样不得给出 OWL performance claim；若 C 预先冻结为 analysed-only，则论文只能回答 OWL responsibility boundary，不能暗示测过性能。

## Goal5799 — Double-blind paper、adverse-result integration 与 claim freeze

时间：2026-09-03 至 2026-09-10  
硬规则：Sep 3 后不新增 benchmark、泛化搜索或性能优化；只修 correctness、paper/artifact defect 与 claim mismatch。

### Sep 3 Go/No-Go

必须同时满足：

1. bounded public lifecycle 对两个 tasks 闭合；
2. A/B/C/D 可执行臂 exact，OWL analysed-only 若适用已明确；
3. three-table responsibility comparison source-backed；
4. headline mechanisms 通过 liveness + necessity；
5. modern-RTX matched performance 完成；
6. OWL、PyOptiX、Slang、Dr.Jit、CrossRT 与 RT-core repurposing comparisons 均由 primary sources 支撑；
7. 11-page main body 自包含；
8. paper + artifact anonymous scrub pass。

### 正文强制结构

1. Problem：whole callback protocol seam in repurposed RT applications；
2. Existing abstraction boundary：PyOptiX host binding、OWL composition、相邻 compiler systems；
3. Design：五项 Callback-Protocol IR contracts；
4. Public bounded implementation；
5. Two matched tasks and correctness；
6. PyOptiX/OWL/RTDL responsibility comparison；
7. mechanism liveness + semantic necessity；
8. lifecycle-separated performance；
9. adverse results and limitations；
10. related work。

下列 adverse results 必须在正文与相应 positive result 相邻：16/34 pass vs 18/34 fail，CI 11/10/13；6 COMPATIBLE / 9 UNKNOWN；new-app generalization exam 0；usability study 0；matched CUDA/OptiX usability baseline 0；RayDB private loader；continuation 的 positive capability 只覆盖实际执行的 `SINGLE_TRACE`、trace depth 1、callable depth 0，其余 vocabulary 只是 reserved taxonomy。不能移入 appendix 才首次出现。

### 匿名责任与 checklist

Responsible owner：`paper-and-artifact anonymization owner = project owner`  
Independent verifier：`artifact scrub verifier = Codex + reproducible scanner`

- `\documentclass[sigplan,screen,review,anonymous]{acmart}`；
- author names/affiliations removed；self-citations third person；
- PDF metadata、filenames、archive member names、git metadata scrubbed；
- owner/local username、home path、IP/hostname、Goal numbers、reviewer names、chat/audit trails removed from submission artifact；
- supplement anonymous；main text self-contained；
- black-and-white readable figures；11-page body；
- any failure = `NO_GO`。

## 只保留两个外审 checkpoint

### Checkpoint A — premeasurement design gate（最迟 Aug 31）

单一 self-contained CFR。审查 exact arms、matched tasks、public API、mechanism coverage、timers、run order 与 no-substitution rules。未明确批准则 Goal5798 worker zero 不开始。

### Checkpoint B — final evidence/claim gate（最迟 Sep 3）

单一 self-contained CFR。审查 liveness/necessity、raw performance recount、adverse-result placement、related work、anonymous scrub 和 claim ceiling。未明确批准则不提交。

普通实现、测试与文档不逐项索取授权。只有 scientific question、baseline、algorithm、dataset、timer 或 claim ceiling 改变才升级。

## Claim ceiling

### 只有证据通过后才可主张

- for the admitted bounded families, complete callback protocol is the unit of compilation；
- five specified cross-program responsibilities move from application conventions to compiler checks/generation；
- demonstrated whole-protocol defects that PyOptiX/OWL do not statically rule out are rejected before launch；
- exact outputs on the two matched tasks and separately scoped existing apps；
- measured lifecycle costs relative to exact current baselines on one modern RTX environment。

### 永久禁止

- first Python OptiX / first Python callbacks / first Python-to-PTX；
- SBT/pipeline/GAS/lifecycle composition 本身是 RTDL 独有贡献；
- OWL、PyOptiX、Slang、Dr.Jit 或 CrossRT “不能解决问题”这一无界断言；
- arbitrary-app/generalization proof、all families、formal soundness/completeness；
- 未经多 backend/code generator 评价的 `targetable IR` claim；本轮将其明确放入 future work；
- easier/simpler/less code/more productive，没有 user study；
- universal performance/no-slower、production/public/GA；
- 用 evidence governance 充当 compiler novelty。

## 当前立即动作

1. 完成 Goal5794 exact PyOptiX/OWL freeze、source-backed boundary、device-path map 与 mechanism×task S0；
2. 立即实现 Goal5795 的两-family app-neutral public facade，不碰 formal timing；
3. Aug 26 18:00 执行 public API stop gate；
4. 通过后完成 A/B/C/D matched correctness/responsibility；
5. 按 preregistered matrix 执行五项 liveness + necessity；
6. Checkpoint A 只送一个 CFR；批准后才运行 modern-RTX formal measurement；
7. Sep 3 执行 final gate并切入完整一周写作。
