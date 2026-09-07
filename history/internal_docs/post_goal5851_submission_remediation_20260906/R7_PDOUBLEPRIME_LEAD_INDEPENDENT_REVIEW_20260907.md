# P″ 最终字节独立主审报告

日期：2026-09-07 America/New_York。

**结论：当前 P″ 仍须修订并复审。发现 1 项 major、6 项 minor；其中包括一项直接影响 CGO 贡献定位的近邻文献遗漏。没有发现需要推翻两代有限性能观察、修改冻结实现或重做 GPU 实验的证据。**

本次是用户要求的只读审查。文献、架构和性能分工合成为这一份主审意见，不算三份独立审查，不构成两票接受。仅新增本报告，未修改作者稿件、代码、既有 authority、claim ledger 或完成状态，也未触发主 AI 的下一轮整改。

## 1. 精确受审身份

完整读取 `R7_PDOUBLEPRIME_FINAL_BYTES_REVIEW_REQUEST.md`，从 Git 对象抽取受审字节并核对当前文件。开始审查时 HEAD 是 `5334f0fc5deda053f54dbad12d09f4c43016875c`，工作树干净；受审文稿身份是下表的 P″，不是 HEAD 的所有控制记录。

| 对象 | 精确身份 |
| --- | --- |
| P″ commit | `b28076ad568d3b7b36cfa48b0c5846accff3cb95` |
| P″ tree | `2a63fecbcf09727dbe4e38f83edb253d80fa3cab` |
| P″ parent | `50ca45521013f56b141402f4902a3af189b469f9` |
| M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` |
| E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` |
| F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` |
| 两处 PDF，均 143,803 bytes | `a8d3194b07fbf0105b59944e8044da1769b9ca8877f92d3a93aa44f605b6aa84` |
| main.tex，36,994 bytes | `f75b29160f015d7c5de3dd0eae560e54df2933f5e065ec97170c2ac9f0f92186` |
| references.bib，20,196 bytes | `a8c62657c74a42f39926974c4b655e0b83149beb1b548d1a0fa647115a82e6ab` |
| source bundle，20,540 bytes | `5f2bbc858b0b783983d773e09d46be92b0b47ebc6f87e079c1dd855ac42f55df` |
| F2 artifact，180,308 bytes | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

五份 novelty 文件在 P″ 中的 SHA 均命中请求。当前 `EXECUTION_REPORT.md` 已有提交后的身份登记，因而不等于 P″ 内的 precommit 版本；当前 ledger 也新增了 P″ 身份。这些后续差异已单独阅读，没有把 HEAD 行号冒充 P″ 行号。本报告的主文、N1/N2/N3 定位均与 P″ 相同；claim 以 P″ 的稳定 ID 标识。

P″ 相对 parent 在 `src/`、`include/`、`experiments/`、`scripts/`、`tests/` 和 F2 artifact 模板目录均无差异；所审实现源码仍对应 M。

## 2. Findings

### R7-PDP-01 — major：实测专门化路线未在 typed-effect 方法与性能解释中披露

**位置：** PDF p3 review 行 251–260，[main.tex:260](/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:260)；N2 [PROTOCOL_WITNESS_AND_DERIVATION.md:150](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/PROTOCOL_WITNESS_AND_DERIVATION.md:150)；N3 [CGO_CONTRIBUTION_ARGUMENT.md:65](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/CGO_CONTRIBUTION_ARGUMENT.md:65)。主文 pp5–6 的性能解释须同步限定。

**证据：** 论文只描述 IR → ABI → Numba leaf → wrapper 校验 effect/status tag → 硬件操作。然而当前被测两条标准路线使用了受信任的精确 IR 专门化：

- Triangle 在 [wrapper:129](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:129) 以精确 IR digest 及 U64 reducer 识别 count intrinsic；[463 行](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:463) 将通用叶调用转入独立 diagnostic entry；[486 行](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:486) 起的快速 entry 直接执行 traversal、计数与 checked reduction，any-hit 直接更新 payload，不逐次调用该 Numba 叶并检查其 effect tag。非诊断调用衔接 [runtime:6304](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6304)、[runtime:6412](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6412)。
- Relation 在 [wrapper:55](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py:55) 要求 exact standard callback IR；[293 行](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py:293) 起的 intersection 直接计算 overlap、报告 item ID；[343 行](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py:343) 起的 any-hit 直接计数、写行和更新 payload。前面构造的相应叶调用字符串没有插入这些 fused entry。

这不证明 app-specific dispatch、绕过全部验证或输出错误。标准 IR 专门化可以是合法的编译实现；问题是稿件没有解释它，读者会把实测开销归给另一条通用执行机制。

**必须修正：** 主文 §3.2/§3.5 与方法部分明确列出通用／诊断路径和精确标准 IR 的 trusted fused/intrinsic 路径。说明哪些静态、身份、compact-status、overflow 和输出检查仍在，哪些逐叶调用／effect-tag 操作已被专门化替代。N2 不能只摘取随后被替换的通用代码而不交代生成器分支。保留原性能数值，将其明确绑定这些实际专门化路线。

**完成标准：** 读者无需读取私有代码即可知道 A/D 测量对应哪种实现；不把通用 callback 执行成本与已专门化标准路线成本混为一谈。本项不要求修代码、撤销数值或新增实验。

**Affected claims：** `METHOD-TYPED-EFFECT-TRUSTED-LOWERING-023`、`ARCH-TCB-TOPOLOGY-LOWERING-003`；007–010 的数值保留，实施机制解释必须限定。

### R7-PDP-02 — minor：native-load gate 没有区分 app-free runtime 预热与具体路线

**位置：** PDF p1 review 行 99–101，[main.tex:106](/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:106)；p2 的 mutation 描述及 p4 [main.tex:465](/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:465)；N2:139–142、N3:47–50，claim 022 的 candidate sentence。

**证据：** [materialize:1045](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_callback_lifecycle.py:1045) 可以先启动 warmup，五项 decision 到 [1151 行](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_callback_lifecycle.py:1151) 才生成。warmup 在 [1275 行](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_callback_lifecycle.py:1275) 加载 runtime DSO；具体 [1187 行](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_callback_lifecycle.py:1187) 执行 `ctypes.CDLL`，前后仍核对原生库身份。公开 `begin_native_initialization` 也允许在构造 route 前启动。正式 AOT [worker:302](/Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/worker.py:302) 同样先开始 provider 初始化，再 `load_rtdlexe`。

这是 app-free runtime DSO／driver 预热，不是未经准入就把当前 callback PTX 建成 OptiX module 或发起 launch。既有 mutation test 的 loader-not-called 结果属于关闭 overlap 的配置，不能升格成所有路径的通用 native-load 顺序。

**必须修正：** 将核心表述限定为 decision 控制 materialized route 的发布及后续 per-route preparation／使用；说明精确身份的 app-free runtime 可提前加载、预热。测试结果保留并标明配置。同步修订 022、N2/N3 和新版本请求。

**Affected claims：** `NOVELTY-PROTOCOL-ADMITTED-EXECUTABLE-022`、`ARCH-STATIC-ADMISSION-IDENTITY-002`。

### R7-PDP-03 — minor／研究论证缺口：protocol-carrying executable 未比较 PCC 这一直接近邻

**位置：** PDF p1 核心 contribution、p6 [main.tex:645](/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:645)；N3 §2、§3、§4.3–4.4；N1 的方法先例表；bibliography。

**证据：** 新论点强调可执行体携带条件、消费者验证后装载／执行、把应用抽象边界与机器表示连接。Necula/Lee 的 OSDI 1996 *Safe Kernel Extensions Without Run-Time Checking* 已明确提出携带安全证明的 native binary、consumer 定义策略并验证后装载执行，策略也可约束 data-abstraction integrity；原文直接以整数表示的 file descriptor 为例。[原论文 Introduction](https://www.usenix.org/legacy/publications/library/proceedings/osdi96/full_papers/necula/html/node1.html)、[Proof-Carrying Code 节](https://www.usenix.org/legacy/publications/library/proceedings/osdi96/full_papers/necula/html/node2.html)。

这些原文并不证明 PCC 已实现 RTDL 的全部五项具体 RT 关系；它们说明“可执行体携带可检验条件并受装载控制”这一组织本身已有很近的先例。仅比较 typestate／FFI，再说这些工作没有写出同一个五项组合，还不足以解释该命名和组织的增量。

**必须修正：** 增加一段直接对照及一级引用，明确 PCC 的 proof/policy checking 与 RTDL 的可信 schema、有限声明／投影一致性、拓扑 TCB 的区别。进一步说明 RTDL 具体领域模型和实施取舍的价值；不能把较弱保证本身写成新意。certifying compilation／translation validation 可作为紧邻阅读线索，按真实来源判断是否需要引用，不要求扩大为穷尽调查。

**完成标准：** 读者看到已有“携带证据的可执行体”方法以及 RTDL 的真实增量／限制。一个有依据的段落和对照项即可；不要求证明对方原则上做不到，不要求新定理或新实验。

**Affected claims：** 022、`RELATED-WORK-EXACT-GUARANTEE-BOUNDARY-024`。

### R7-PDP-04 — minor：N2/N3 再次混淆两种公开执行接口的 publication 检查

**位置：** [N2:121](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/PROTOCOL_WITNESS_AND_DERIVATION.md:121)、N2:133–143；[N3:55](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/CGO_CONTRIBUTION_ARGUMENT.md:55)。该问题在支撑文档，主文 p4 §3.6 与 p5 Figure 1 的当前计时／oracle 表达可保留。

**证据：** N2 引用 `v4_callback_lifecycle.py` 的 `ProtocolExecutionResult` 路径，在该路径上描述 identity、output digest、traversal receipt 的检查；N3 将其无接口限定地概括为 public result 构造前的检查。实测 public A 的 [runtime:6254](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6254) 是不同的 `RTDLExecutionResult` 路径：[6289 行](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6289) 返回 output、None、identity、deferred compact status 等。完整 detailed receipt 与 worker output/digest oracle 的检查、暂存和留存范围不能由前一接口代替。

**必须修正：** N2 加入接口／调用路径列，把通用 lifecycle 的完整检查链与 measured AOT prepared 路径分开；N3 按主文 §3.6 和 R1 裁决限定 publication。身份绑定、同步 native/compact status、可选 expected-output、返回后 worker oracle、另次 detailed diagnostic 分别列明。

**Affected claims：** 022、`METHOD-RECEIPT-SCOPE-015`、002。原逐执行 detailed-receipt 条款仍为未履行；本项是修正支持文档，不能重开旧条款为已完成。

### R7-PDP-05 — minor：把输出基数当成所有候选都做计数

**位置：** PDF p5，[main.tex:475](/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:475)，尤其 477；本次 review request §7。

**证据：** 冻结 [CHALLENGE_TABLE.json:130](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5838_generic_core_exam_20260902/CHALLENGE_TABLE.json:130) 已有 `terminate_on_first_accepted_hit`、`per_query_bool`、`bool`。完整十行是 3 count/continue、3 filtered-count、4 terminate/Boolean。共同 `count_relation=query_count` 仅表示每查询一个结果。

**必须修正：** 改为每查询一个结果，其中六条计数、四条首次命中终止的 Boolean 路线。保留 sphere count/continue 为选中项、curve terminate 为未选候选，以及原 2 launches／12/12 结果。请求中的同一错误追加勘误，不修改冻结表。

**Affected claims：** `EVAL-G5838-PROSPECTIVE-COMPOSITION-004`、`EVAL-G5838-CANDIDATE-SELECTION-005`。

### R7-PDP-06 — minor：无输出陈述错误覆盖 native-fork probe

**位置：** PDF p7 review 行 694–695，[main.tex:688](/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex:688)。

**证据：** “Neither unrepaired path produced output” 将双故障路径的无输出扩大到 native fork。既有 [Codex 审查:148](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_review_post_goal5851_cgo2027_20260906.md:148) 记录 `ctypes.CDLL(None).fork()` 后同一 public execute 在 mock native 下被接受。它不是 GPU 执行证据，也不是可以宣称该路径必定不返回输出的证据。

**必须修正：** 分开写：双故障 mock 没有 public output；两种缺陷未见于保留的成功 GPU workers；native-fork probe 使用 mock native 并显示 process gate 可被绕过。保留 unsupported inherited-owner 范围。

**主审纠正：** 我此前旧 P 报告的指令 D 也建议过不准确的合并无输出句；本项同时纠正我的旧措辞，不能全部归责于主 AI。旧报告保留，本报告作为追加纠正。

**Affected claims：** `LIMIT-PROVIDER-DOUBLE-FAULT-018`、`LIMIT-SUPPORTED-PROCESS-FORK-019`。

### R7-PDP-07 — minor：SlangPy“当前 stable 0.42.0”的来源身份不成立

**位置：** PDF p8 reference [9]，[references.bib:87](/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/references.bib:87)；[N1:67](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/RELATED_WORK_BOUNDARIES.md:67)。

**证据：** 被链接的当前官方 stable 文档／[changelog](https://slangpy.shader-slang.org/en/stable/changelog.html) 已列 0.43.1（2026-07-15）、0.43.0（2026-07-13），均早于本次记载的 09-06 检索。0.43 涉及 reflection/binding、pipeline cache 和 device cleanup 等相关改动。不能把动态 stable URL 同时登记为已核查的 0.42.0 固定来源。

**必须修正：** 选择实际使用的历史 0.42.0 可定位来源并准确标为历史版本，或更新当前版本身份并核查受影响能力。无需安装或运行 SlangPy；不能仅改版本数字却继续假定旧来源范围。

**Affected claim：** 024。

## 3. N0–N5 的验收判断及研究价值

| 阶段 | 本次判断 |
| --- | --- |
| N0 | 输入与所有权、M/E/F2/P′ 保全成立；后续文档快照与 P″ 的区别已说明 |
| N1 | 做了实质一级来源整理；承认强近邻能力、UNKNOWN 与撤销综述空缺推理均正确；PCC 近邻和 SlangPy 来源身份仍需修正 |
| N2 | 同宽错误已正确降为说明性例子，trusted schema／同编译器 TCB／CP005 身份范围披露清楚；遗漏专门化、预热与两种 publication 路径 |
| N3 | 已从“对手不能／新通用理论”降为有限系统设计，方向诚实；具体方法描述及近邻增量论证尚不完整 |
| N4 | 实际论文已修改，非仅交计划；当前仍受上述 findings 影响，不能称独立验收完成 |
| N5 | 新 PDF/source 身份、版面、源码包构建及原 evidence 包重放可接受；最终字节裁决仍是退回 |

我接受“存在有限编译／准入系统设计和真实实现”的事实判断。源码不是只有 hash/schema：类型/effect 检查、ABI、生成代码、AOT decision 传递和执行 gate 实际存在。AOT exporter 要求并重验五项 decision，loader 再核验声明／投影；不能误判为只存了一份无人执行的计划。

但用户最关心的两点仍须严格区分：

1. **现有工作保证的边界：** 已找到若干明确职责边界；多数“同一五项共同保证”比较仍是 UNKNOWN。当前没有建立“已有努力都做不了”，稿件也不再应作这种主张。
2. **CGO 增量：** 当前可捍卫的是具体 RT 领域模型、有限跨表示一致性和执行边界组织；新颖性强弱仍是研究评价，不能由“这些文献没有逐字写出相同五项组合”决定。PCC 近邻补齐后，需要让读者判断真实增量；不要求新理论、穷尽对手或追加实战。

因此，本轮不能被汇报成“科学贡献已证成，剩下只有格式”。也没有证据足以宣告这个有限系统方向毫无价值或要求放弃投稿。当前官方 CGO 范围包含 compiler abstraction、reliability 和跨层设计，但范围匹配不等于新颖性被接受。[CGO 2027 征稿要求](https://2027.cgo.org/track/cgo-2027-papers)

## 4. 性能、原七项和全部 claim 的处理

本次分工从 P″ 精确 artifact Git blob 独立计算，未导入包内 verifier/controller：160 worker 的整数中位数、20,480 样本，及七类比较 × 四个 GPU/task 组 × 八块数组全部匹配 summary。主文 Table 5/6 的数值与舍入正确；A/D 最大块 1.211025、A/C post 最大块 2.377129；1,024 instrumentation、20 AOT、8 competence 的分母正确。没有跨机器 raw-time 比值。

旧 R7-LEAD-01、02、03、05、06、07 已在当前主文／追加勘误中落实。旧 04 的主要 scope 已改，仍有 PDP-06 的合并句问题。旧 R4、旧 R7 request、旧主审报告未被重写。此次新增发现不能被旧 finding 的关闭矩阵覆盖。

| Claim ID 后缀及对象 | 本次处理 |
| --- | --- |
| 001 有限 compiler/admission | 保留设计／实现事实，按 01 说明实际 lowering 分支 |
| 002 静态身份／生命周期 | 保留绑定事实，按 02/04 限定具体阶段与接口 |
| 003 topology TCB | 保留，按 01 补齐 fused/intrinsic TCB |
| 004 prospective composition | 保留有限历史结果，按 05 修候选语义 |
| 005 candidate/selected | 选中身份正确，按 05 修计数／Boolean 分类 |
| 006 finite checker | 数量、有限性及 early-return miss 可保留 |
| 007 Ada triangle A/D | 数值保留；按 01 补实现解释 |
| 008 Ada relation A/D | 数值保留；按 01 补实现解释 |
| 009 Ampere triangle A/D | 数值保留；按 01 补实现解释 |
| 010 Ampere relation A/D | 数值保留；按 01 补实现解释 |
| 011 A/C dual endpoint | 数值和 diagnostic／import 限定可保留 |
| 012 A/E steady/first | 回退披露与首结果 post hoc/non-gating 可保留 |
| 013 C/B competence | 四组有限观察可保留，不是全局最优 |
| 014 instrumentation A-only | 正文已正确区分计时政策与 paired overhead 测量 |
| 015 receipt scope | 主文可保留；N2/N3 按 04 修路径混淆 |
| 016 adaptivity | 同任务调试、非 unseen、端点修订已披露 |
| 017 AOT deployment | 数值及 prepared 端点之外的限定可保留 |
| 018 provider double fault | 保留缺陷与无输出事实，按 06 避免扩到 fork |
| 019 native fork | 保留 hook／unsupported 范围，按 06 修无输出句 |
| 020 artifact portability | 精确 F2 离线重算范围可保留 |
| 021 human authoring/prevalence | 零独立 evidence 的披露正确 |
| 022 protocol executable | 机制存在；按 02/03/04 修范围和近邻比较 |
| 023 typed-effect lowering | 按 01 修，当前通用机制说明不能覆盖实测专门化 |
| 024 related-work boundary | 保留谨慎 UNKNOWN 框架，按 03/07 补来源／近邻 |

这些保留判断均不改变 24 项 `claim_authorized=false`，更不是最终接收票。原 R1 五个绑定值保持不变：机器数值合同通过；原逐执行 detailed receipt 要求未履行；最终 GPU 样本未观察到错误输出；prepared A/D 观察可保留；entry 正向性能主张不允许。

## 5. 精确 PDF、封包和构建验证

直接从受审 Git 对象提取并渲染原 PDF，检查全部八页；未用重建 PDF 替换受审 PDF。八页均为 612×792 pt Letter，正文和引用可读，有 review 行号及页码。未发现裁切、重叠、缺字或最终未解析引用；图 1 的 public return、steady 停表、worker oracle、first-result 结束顺序正确。

12 个字体均嵌入且有 ToUnicode。PDF 有 84 个 annotations/links；文本、Info metadata 和链接未发现所扫描的用户／私有路径／内部 Goal／密钥等标识。无附件、表单或 JavaScript。PDF 未标记结构标签，未据此虚构 PDF/UA 声明。机械版式在已核 CGO 要求范围内可接受，真实提交表单尚未执行。

源码包只有三个规范化目录及 `main.tex`、`references.bib` 两个普通文件，uid/gid 为 0、owner/group 名为空、mtime 一致；提取文件逐字节等于 P″。从带空格的仓库外路径，使用缓存 Tectonic 构建成功并产生八页 PDF。日志有字体请求、underfull 和首轮待解析引用警告；后续自动轮次完成引用解析，未发现 Overfull 或 Missing character。没有把“构建成功”写成完全无 warning，也没有要求重建 PDF 的时间戳等于原 PDF。

F2 包的九成员、权限／owner／timestamp 和 hash 均正确，包内 verifier 与冻结工具身份一致。新仓库外目录使用原包运行：

```text
/usr/bin/python3 -I verify.py --artifact-root .
/usr/bin/python3 -I -O verify.py --artifact-root .
```

两次退出码为 0，stderr 为空，stdout 字节相同，SHA-256 为：

`c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`

状态为 `PASS__OFFLINE_PROJECTION_RECOUNT`。第一次审查调用把 stdout/stderr 日志放进解包根，触发了该包预期的 unexpected-member 拒绝；该目录保留，重新解包并把日志放到包外后通过。这是审查调用位置错误及有效拒绝，不能当作 artifact 缺陷，也没有为得到通过而关闭成员检查。

审计临时目录：`/tmp/rtdl-pdoubleprime-lead-wNV6TJ`，包含精确 blob 提取、hash/inventory、原 PDF 页面、PDF QA、外部构建日志和独立 replay 输出。它不属于提交包。当前 packet 只支持 evidence recount，不支持新颖性研究、说明性 witness、产品安装或 GPU rerun 的复现。

## 6. 复审出口

本报告给出的必要修正均是文献／方法／范围陈述及其控制记录修正，不授权改变 M/E/F2、重做实验或提交。后续如用户要求整改，应保留本次 P″ 和报告，以实际修改后的新 PDF／bibliography／source 身份再次复审；原九成员 F2 包无需因此改变。

本轮审查结束，主 AI 的后续执行与用户接下来的问题／命令分开。当前精确 P″ 不能获得最终接受。

REVISE_AND_REREVIEW_CHANGED_BYTES
