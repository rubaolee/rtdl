# R7 主审：精确最终字节审查与整改指令

日期：2026-09-06。审查对象：`R7_FINAL_BYTES_REVIEW_REQUEST.md` 指定的 P、PDF 和九成员证据包。

**有限数值观察及离线包通过本次核查；当前 PDF 不予原字节放行。需要关闭 3 项 major、4 项 minor，然后对新 PDF 字节重新审查。整改限定为稿件、图示和控制记录，不要求修改 M、F2 或重跑 GPU。**

本报告是主审的一份独立意见。架构、边界及性能助手是本次审查的内部技术分工，不构成另外两份独立响应。本报告不关闭 R7，不修改 claim authorization，不代表外发或投稿许可。

以下仓库路径均相对于本仓库根；PDF 页码为实际交付 PDF 页码，正文行号为 P 的 `paper/cgo2027/main.tex` 行号。控制请求在 P 之后加入，不能声称该请求本身属于 P。

## 1. 实际受审身份及只读边界

先逐一读取 Git 对象并计算 SHA-256，再审读八份控制记录及稿件。四个 commit/tree 与请求全部一致：

| 对象 | Commit | Tree |
| --- | --- | --- |
| M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| P | `c6020fd63097b35b5294778cf54c2fb84c879ad6` | `dc4b78ba3ec0f7816f87b87fdd74353c806caced` |

| 交付物 | 实测 bytes | 实测 SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 138969 | `4529946fff21edd2e5634792397d5e3af0213f6c2ab2c4ebdf001b9246f73453` |
| `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

工作区这两个文件均与 P 的 Git blob 相同；两份 PDF 副本也逐字节相同。请求第 3 节所列八份记录的 P blob、工作区文件和声明 SHA-256 全部吻合。当前工作区 HEAD 为 `ed84dc05a422cd30be3f3b1ab8b4b0445c90924a`，它与 P 的区别是后续请求、预检、状态及 source bundle 等记录，未替换受审 PDF 或 artifact。

`git diff M P -- src include experiments` 为空。F2 至 P 没有可执行工具变化；M 至 F2/P 的三个可执行新增仍为冻结 verifier、exporter 和证据测试。F2 不是 GPU 测量源码。本次未修改这些文件、任何候选交付物、原始 authority、历史审查、STATUS 或 CLAIM_LEDGER。

附加核对：HEAD 的 `output/source/rtdl-cgo2027-source.tar.gz` SHA-256 为 `159df8db4fd4ae801f3c7f71a012259023c255dcd3a7a866805cfe310c4f95f2`；其中两个普通文件与 P 的 `main.tex`、`references.bib` 相同。此包不是 P 中原有的九成员证据包，本次没有把它混为同一交付物。

## 2. 对 R1 五项绑定的直接裁决

**接受下列五项，均保持其有限适用范围：**

```text
machine_numerical_contract_passed = true
original_written_per_execution_receipt_requirement_fulfilled = false
wrong_output_observed_in_final_gpu_samples = false
public_prepared_a_over_direct_observation_retainable = true
implementation_entry_positive_performance_claim_allowed = false
```

源码确有 native/compact status 同步失败拒绝，也存在提供 expected output 时的公共路径检查。实验 worker 对每次返回值另做输出及 digest 验证。直接检查原始两代 32 个 A worker，均各有 128 个 steady samples、一份单独 diagnostic receipt，且 `latest_output_sha256=null`。因此 4096 次计时 A 调用不能称为 4096 份完整逐次 receipt；32 份另外执行的诊断也不能回填为计时调用的证明。

依据为 `PROTOCOL_SCOPE_ADJUDICATION.md` 的逐字段矩阵，以及 `worker.py:168–186,268–273,476–502`、`v4_rtdlexe.py:5308–5487,5870–5879,6284–6290`。没有新发现证明最终 GPU 样本发生错误输出。本次文稿退回不撤销真实同步检查，也不把未履行 receipt 条款重写为已履行。

## 3. Material findings：必须逐项回应和关闭

表中非 `accept` 项均尚未关闭。Severity 与 disposition 分别描述重要程度及处理方式；数字观察被接受不等于相关文稿用语自动获准。

| ID | Severity | Disposition | 精确位置 | Evidence | Required action | Claim IDs affected |
| --- | --- | --- | --- | --- | --- | --- |
| R7-LEAD-01 | major | `reject_with_source_evidence` | PDF p5 Figure 1；`main.tex:387–403`；另见 p4 §3.6、`main.tex:361–368` | 图中把 experiment oracle 放在 public result 之前。实际 `worker.py:180–183,476–483` 是公共 action 返回并停止 steady timer 后，worker 才检查结果。另一方面 `v4_rtdlexe.py:5870–5879,6286–6289` 的可选 expected-output 检查确实在公共返回前。图混淆了两个不同边界。 | 按下文指令 A 重画运行时与实验验证两条路径，并同步改 Figure Description。不得把所有 oracle 都说成返回后，也不得把 worker 的 digest 检查画进公共计时调用。 | `ARCH-STATIC-ADMISSION-IDENTITY-002`；`METHOD-RECEIPT-SCOPE-015` |
| R7-LEAD-02 | major | `claim_descope` | PDF pp5–7 §5.4、§5.6、Table 6；`main.tex:497–529,560–587,670–675` | A/E 首结果在正文和表注中没有明确的 post hoc、non-gating 定性；ledger 的 `...-012` 及 R2 §5 却明确要求。两个端点只写 confounded，没有定义起止点、C import 已建立 CUDA context 而 A lazy 的关键不对称。`worker.py:210–227,361–379,453–473` 及生命周期修订记录可核对实际端点。 | 按指令 B 补一段精确方法定义，并在 Table 6 就地标明 A/E 首结果为事后非门槛诊断。保留 A/C entry 的历史 registered criterion，不能把所有 first-result 都改称事后。保留全部不利值。 | `PERF-AC-DUAL-ENDPOINT-011`；`PERF-AE-STEADY-AND-FIRST-RESULT-012`；`METHOD-ADAPTIVITY-TWO-TASKS-016` |
| R7-LEAD-03 | minor | `claim_descope` | PDF p5 §5.3；`main.tex:483–495`，尤其 487 | 所谓 “partially evaluates generated target structure” 对实际方法描述过强。`scripts/goal5840_independent_target_checker.py:561–695` 提取函数窗口、词法遮蔽、检查锚点及出现次序，然后返回预定 effect map；不是对程序控制流或效果语义作 partial evaluation。相邻有限性和 early-return 披露已正确，因此不撤销 20/15 结果。 | 将该句换成下文指令 C 的具体结构检查描述；保留 finite 与 early-return 限制。不得因内部函数名含 partial_evaluation 就沿用这个方法名称。 | `EVAL-G5840-FINITE-CHECKER-006` |
| R7-LEAD-04 | major | `claim_descope` | PDF p2 §2.3、p7 Internal validity；`main.tex:186–191,675` | native fork 绕过的是 Python at-fork hook；之后仍可能通过公共 `execute` 到达 native，并不需要再绕过公共 API。源码 `v4_rtdlexe.py:239–260,6184–6188` 比较缓存 PID。另 `3078–3092` 可覆盖主异常，`3111–3119` 在 release 前清引用并置 CLOSED，失败时可能失去清理重试所有权。正文只说 diagnostic provenance degraded，未完整落实 ledger 018/019。 | 按指令 D 明确排除所有不调用 Python hook 的 native fork 后继承 owner 使用，即使随后调用公共 API；同时写出 secondary fault 可覆盖主异常、失去 cleanup retry ownership。将 “we did not observe this event” 限定到成功保留的 GPU workers，不能否认已存在的 mock 复现。 | `LIMIT-PROVIDER-DOUBLE-FAULT-018`；`LIMIT-SUPPORTED-PROCESS-FORK-019`；`ARCH-STATIC-ADMISSION-IDENTITY-002` |
| R7-LEAD-05 | minor | `claim_descope` | PDF p1 Abstract；`main.tex:36–38`，对照 `645–659` | 摘要称 current artifact 支持两个 public constructors；实际交付 artifact 只有离线证据及重算器，没有 RTDL 产品安装或实现源码。§8 的包范围正确。 | 将 “current artifact” 改为 “current implementation”。检查全文 artifact 一词的指代，避免把历史实现和本次九成员证据包混用。 | `ARCH-CENTRAL-BOUNDED-COMPILER-001`；`ARTIFACT-PORTABILITY-020` |
| R7-LEAD-06 | minor | `claim_descope` | PDF pp5–7；`main.tex:512,558,592–594,665–668` | Direct 是被测具体实现，并没有最优下界证明；“lower-bound implementation” 超出 A/D 数据。prepared 公共端点包含 Python/native/status 等开销，不能称 prepared kernel endpoint；E 不是 M 的直接父版本。此外正式 A/B/C/E 都有 instrumentation 开关，缺少的是其他 arm 的 paired overhead qualification。 | 分别改为 named direct reference implementation、prepared public-execution endpoint、frozen predecessor control E。把 “do not … symmetrically instrument” 改为 “do not measure paired overhead for the other arms”，区分开关政策与实测资格。明确观察不证明最小 Direct 延迟或内在语言开销；数值不变。 | `PERF-AD-ADA-TRIANGLE-007`；`PERF-AD-ADA-RELATION-008`；`PERF-AD-AMPERE-TRIANGLE-009`；`PERF-AD-AMPERE-RELATION-010`；`PERF-AE-STEADY-AND-FIRST-RESULT-012`；`METHOD-INSTRUMENTATION-A-ONLY-014`；`METHOD-AOT-DEPLOYMENT-017` |
| R7-LEAD-07 | minor | `reject_with_source_evidence` | `R4_MANUSCRIPT_REWRITE_AND_RENDER_REPORT.md:71,95–96`；`R7_FINAL_BYTES_REVIEW_REQUEST.md:120–124` | R4 声称实际主文明确标了 A/E 的 post hoc/non-gating，受审 PDF 并无此限定。R7 请求又把所有 first-result rows 一概定为事后非门槛；这不符合 A/C entry 曾是 registered criterion 的事实。 | 在新版本记录追加针对旧 P 的勘误；新稿真正修好后才更新完成状态。R7 请求限定为 “A/E first-result rows are post hoc and non-gating”；A/C entry 分别说明历史门槛和现行论文降为诊断。不能静默改写旧 P 的受审记录。 | `PERF-AC-DUAL-ENDPOINT-011`；`PERF-AE-STEADY-AND-FIRST-RESULT-012` |

### 指令 A：把两个 oracle 的位置画清楚

图 1 的 publication 路径至少表达以下区别，可按版式拆为两行：

```text
Public execution:
native status → compact status → supplied expected-output check, if present
→ public return / steady timer ends

Experiment validation:
returned value → worker output-and-digest oracle → accepted sample / worker success

Separate diagnostic:
post-loop diagnostic execution → retained detailed receipt (one per A worker)
```

这是信息结构要求，不是要求把代码或实验 timer 改成图示。first-result 端点的计时止于 worker 输出验证之后，必须在方法中与 steady timer 区分。图注及 `\Description` 都要与实际顺序一致。正文应把 “original design goal” 具体表述为未履行的原 preregistered per-execution detailed-receipt requirement，避免将正式条款弱化成可选愿望。

**完成标准：**读者能从图及其邻近说明区分 native/compact gate、调用者提供的 expected output、公共返回、steady 停表、worker oracle、单独 diagnostic；不能推导出逐次完整 receipt 已验证或 worker 验证位于公共返回前。

### 指令 B：补齐端点定义及 A/E 事后比较身份

建议直接加入可核对的英文句子，并按实际变量名复核后排入正文：

> Implementation-entry time starts immediately before implementation-specific imports and ends after the first result and worker output validation. Post-import time starts after those imports and ends at the same validation boundary. Pinned PyOptiX initializes CUDA context state during import, whereas RTDL initializes it lazily later in the lifecycle; the two measurements therefore include different lifecycle work. A/E first-result comparisons are post hoc, non-gating diagnostics; only prepared A/E was a registered regression gate.

再交代 steady 是每个 prepared public action 的计时，worker 额外验证在该计时之外。Table 6 表注必须带 A/E 首结果的事后非门槛限定；不要只放 supplement。A/C entry 曾有登记门槛且机器数值通过，但本稿不将其作为正向或 confirmatory 结论，这两件事须同时保持。

**完成标准：**四项 A/C post-import 不利方向、2.377129x 最大块的正确舍入、四项 A/E 首结果回退仍在主文；Table 6 读者无需查私有 ledger 即知道哪些比较是事后诊断。不能新增门槛、把诊断算作门槛失败、或以本轮重述改写原登记历史。

### 指令 C：checker 的正向方法名必须与实现相称

建议替换为：

> It checks selected lexical patterns and ordering constraints in generated target code rather than accepting compiler labels as authority.

保留其另外读取 ABI、PTX、symbol、receipt 等有限证据的说明，以及 3 route groups、4 modes、5 property classes、20 registered instances、15 unique mutations 和 early-return 局限。内部函数名无需改动；本轮不修 checker。

**完成标准：**方法描述不再让读者误以为它构建通用 CFG、解释效果语义或证明所有路径的 status-before-use；同时不把独立结构检查错误降格为完全没有价值。

### 指令 D：生命周期限制必须覆盖真实反例

建议同段表达：

> The fork guard covers Python-managed forks that invoke the registered at-fork hook. A native fork that bypasses that hook can evade the cached-PID guard even when the child later uses the public API; inherited owners after such forks are outside the supported contract. Secondary bind/close failures can replace the primary exception and can lose cleanup retry ownership. These defects produced no public output and were not observed in the retained successful GPU workers; they remain unrepaired.

**完成标准：**不再把反例限定为绕过 public API；明确 hook 条件和 retry ownership 缺陷；mock 反例、无最终 GPU 错误输出、有限支持范围三者不混淆。

## 4. 数值与包验证：哪些已经通过

独立重算没有导入 controller 或包内 `verify.py`。对投影的全部 160 个 worker 重新计算整数中位数，逐个与保存值比较；全部 20480 个 steady samples 被计入。随后计算七类比较在四个 GPU/task 组合上的八块数组，与 summary 比较，均一致。使用的公式为整数 worker median、每块 nearest-ppm ratio，再取八块 ratio 的整数中位数；没有跨机器 raw-time ratio。

| GPU/task | A/D median | A/D max | A/C entry | A/C post median | A/C post max | A/E entry | A/E post |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4090 Relation | 1.076852 | 1.092253 | 0.653826 | 1.749327 | 1.865823 | 1.192358 | 1.305383 |
| 4090 Triangle | 1.175066 | 1.211025 | 0.642180 | 1.559788 | 1.639385 | 1.079554 | 1.169262 |
| 3090 Relation | 1.094795 | 1.118811 | 0.681393 | 1.837415 | 2.377129 | 1.216714 | 1.261676 |
| 3090 Triangle | 1.133636 | 1.142675 | 0.618362 | 1.637468 | 1.652853 | 1.137637 | 1.162775 |

Table 5 的 A、D 毫秒值与由 worker medians 计算的汇总一致，Table 6 的显示舍入也一致。1024 个 Arm-A instrumentation observations、20 个 AOT durations、8 个非正式 competence workers 的分母及相应估计也吻合。A/D 的 max 只作观察值，无登记最大块门槛。未发现需要改动表内数值或丢弃行的理由。

对精确 archive 的两个全新外部解包目录分别运行普通与 `-O` 模式，共四次：

```text
PYTHONNOUSERSITE=1 /usr/bin/python3 -I verify.py --artifact-root .
PYTHONNOUSERSITE=1 /usr/bin/python3 -I -O verify.py --artifact-root .
```

四次退出码均为 0、stderr 为空，stdout 字节相同，SHA-256 均为 `c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`，状态均为 `PASS__OFFLINE_PROJECTION_RECOUNT`。projection、summary、manifest self-seals 分别为：

```text
fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca
54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105
4a62601b0e421033e67169ed3f89818c6cf62b8acc7723df9cc3ca4c8a46fc32
```

实际只有以下九个普通文件；全部 mode 0444、uid/gid 0、空 owner/group 名、mtime 0，无链接或意外成员：

```text
CLAIM_SCOPE.md
DEPENDENCIES.md
EXPECTED_RESULTS.md
README.md
REPLAY_MATRIX.md
data/performance_projection.json
data/recount_summary.json
manifest.json
verify.py
```

包内 verifier 与 F2/P 中的源码逐字节相同。逐成员名称和内容匿名扫描未发现作者身份、私有路径、内部 Goal 标记或实际机器/访问端点泄漏。自封印及固定投影身份是完整性和确定重算约束，不是第三方硬件见证。包不提供 GPU 重跑、产品安装、完整历史 authority 恢复；正文 §8、§9 对此的范围描述可接受。

本次还从 P 的四个精确 Git blobs 建立仓库外 focused source capsule，实际运行证据测试：normal 14/14、`-O` 14/14，均无跳过。尝试完整本地 clone 时曾因 promisor object 缺失失败，未把失败目录当作干净 checkout，亦未声称本次重做了完整远端 F2 rehearsal。本次 focused capsule 不替代 R5 已记录的完整 128/128 normal、128/128 optimized 和 7/7 演练；本次请求的九成员包独立重放不依赖该 clone。

临时审计记录：`/var/folders/85/mj9yv2ts6ddcphbndl3992kh0000gn/T/rtdl-r7-independent-artifact-r5vwc613/r7-artifact-results.json`，其中含四次输出 SHA、逐成员 SHA 和两次测试退出信息。该临时记录不是提交包内容。

## 5. 全部 21 项 ledger 与实际稿件的映射裁决

本表的 `accept` 只接受限定事实及其证据，不改变 ledger 的 `claim_authorized=false`。存在关联 finding 的条目必须先修正文稿映射，再讨论最终授权。

| Claim ID | 实际 PDF／正文位置 | 本次 disposition 与限制 |
| --- | --- | --- |
| ARCH-CENTRAL-BOUNDED-COMPILER-001 | pp1–4，95–114、197–346 | `accept` 有限 compiler/admission 事实；摘要指代按 R7-LEAD-05 修正。 |
| ARCH-STATIC-ADMISSION-IDENTITY-002 | pp3–5，262–368、Figure 1 | `claim_descope`，静态身份绑定成立；按 01/04 校正 publication 与 fork 范围。 |
| ARCH-TCB-TOPOLOGY-LOWERING-003 | pp3–5、7，330–346、Figure 1、684–689 | `accept`，非可执行 canonical plan、topology-specific TCB 已明确。 |
| EVAL-G5838-PROSPECTIVE-COMPOSITION-004 | pp4–5，463–479 | `accept`，一个十行作者定义域内的历史 composition；不是无偏新应用。 |
| EVAL-G5838-CANDIDATE-SELECTION-005 | p5，463–469 | `accept`，sphere/count/continue 是 selected，curve/terminate 只是 eligible。 |
| EVAL-G5840-FINITE-CHECKER-006 | p5，481–495 | `claim_descope`，数量及 finite scope 接受；方法名按 03 修正。 |
| PERF-AD-ADA-TRIANGLE-007 | pp5–6 Table 5 | `accept` 1.175066/1.211025；按 06 删除 Direct 最优下界暗示。 |
| PERF-AD-ADA-RELATION-008 | pp5–6 Table 5 | `accept` 1.076852/1.092253；同上。 |
| PERF-AD-AMPERE-TRIANGLE-009 | pp5–6 Table 5 | `accept` 1.133636/1.142675；同上。 |
| PERF-AD-AMPERE-RELATION-010 | pp5–6 Table 5 | `accept` 1.094795/1.118811；同上。 |
| PERF-AC-DUAL-ENDPOINT-011 | pp5–7 §5.4、§5.6、Table 6 | `claim_descope`，全部值接受；按 02 明确定义，不准正向 entry claim。 |
| PERF-AE-STEADY-AND-FIRST-RESULT-012 | pp6–7 §5.6、Table 6 | `claim_descope`，值接受；按 02/07 落实事后非门槛限定。 |
| PERF-CB-COMPETENCE-013 | p6，589–591 | `accept`，0.221–0.654 的精确路径观察；未称全球最优。 |
| METHOD-INSTRUMENTATION-A-ONLY-014 | pp6–7，592–594、668 | `accept` A-only qualification；按 06 区分 paired overhead 资格与正式 instrumentation 开关。 |
| METHOD-RECEIPT-SCOPE-015 | pp4–7，361–368、Figure 1、596–598、689 | `claim_descope`，4096/32 及未履行正确；按 01 修正两个 oracle 的阶段。 |
| METHOD-ADAPTIVITY-TWO-TASKS-016 | pp5、7，523–527、671–674 | `accept` 已披露同任务调试及修订端点；按 02 补齐比较身份。 |
| METHOD-AOT-DEPLOYMENT-017 | pp5–6，555–558 | `accept`，20 observations、58.3–78.2 ms 和 1.04–2.02% 正确；按 06 改 endpoint 名。 |
| LIMIT-PROVIDER-DOUBLE-FAULT-018 | pp2、7，186–189、675 | `claim_descope`，按 04 加上 cleanup retry ownership，不止异常诊断。 |
| LIMIT-SUPPORTED-PROCESS-FORK-019 | pp2、7，189–191、675 | `claim_descope`，按 04 写 hook 条件，不能以 public API 为反例排除条件。 |
| ARTIFACT-PORTABILITY-020 | pp6–7 §8、Artifact scope | `accept` 精确包离线重算及范围；按 05 修摘要冲突。 |
| LIMIT-HUMAN-AUTHORING-PREVALENCE-021 | pp4、7，427、677–682 | `accept`，human authoring、代表性 prevalence、无偏新应用证据均未虚增。 |

架构核对包括 AST allowlist、typed IR、受支持 leaf codegen、静态 identity/lifecycle 路径及历史 Goal5838/5840 authorities。`v4_family_schema.py:1427` 的 plan 不可执行不能据此推导整个系统没有编译链；存在前端和 topology-specific codegen。当前将其限定为共同 admission 表面及受信具体 lowerers，是技术上有意义的主张，但不是通用拓扑编译、formal soundness 或相对所有相关系统的优越性证明。

2,635 行已用历史 Git numstat 独立重算：八个新 sphere 模块为 619+560+384+373+293+266+107+33 行；另 shared sphere compiler 为 23 additions+5 deletions，主要涉及 NVRTC 路径配置/import。包含空行及文档的物理行数不能冒充 28 行冻结语义核心修改。三个冻结文件不变、十行分母、2 launches、12/12 oracle 的历史结论可保留。

## 6. PDF、匿名、引文与当前官方要求

实际渲染并阅读全部八页，未以重新编译的其他 PDF 替代。PDF 是 612×792 pt US Letter，正文结束于第 7 页，参考文献延至第 8 页；有页码和 review 行号，表格及图示在黑白下可读，未见裁切或重叠。单个 1.90399pt output-routine vbox 警告已在交付记录披露；视觉检查没有对应可见损坏，因此不把它列为退回理由，也不将它报告为“零 overfull”。

文本、Info/XMP、69 个 annotations/links 及文件名检查未发现私有作者身份、路径或访问端点；没有嵌入文件、JS 或表单。12 个字体均嵌入且有 ToUnicode，语言为 en。PDF **没有结构标签**；源码有 Figure Description，不能据此宣称 PDF/UA 或完整屏幕阅读器可访问性认证。此点作为披露，不虚构本次 CGO 投稿规则中的强制 tagged-PDF 条款。

当前官方页要求 11 页正文上限、Letter、ACM sigplan、匿名 PDF、页码和 review 行号，supplement 单独匿名提交；本候选在这些机械项目上符合。R8 的真实表单和上传并未因此完成。[CGO 2027 官方投稿要求](https://2027.cgo.org/track/cgo-2027-papers)

对实际出现的 18 条参考文献逐项检索作者/出版方页面、论文或注册元数据；可访问来源未显示实质伪造或错引，OptiX 9 PDF 的访问缺口单列如下。主要核验入口包括 [GPUVerify 原论文](https://spiral.imperial.ac.uk/server/api/core/bitstreams/ea675cd4-b326-46bf-8537-d0e439365c99/content)、[Interface Automata 注册元数据](https://api.crossref.org/works/10.1145/503209.503226)、[CrossRT 作者页面](https://arxiv.org/abs/2409.12617)、[Furr/Foster 原论文](https://www.cs.tufts.edu/comp/150FP/archive/jeff-foster/safe-foreign-pldi.pdf)、[Shader Components 作者页](https://graphics.cs.cmu.edu/projects/shadercomp/)、[Slang 作者记录](https://graphics.cs.cmu.edu/?p=1674)、[Multiparty Session Types 元数据](https://api.crossref.org/works/10.1145/2827695)、[Dr.Jit 作者页](https://rgl.epfl.ch/publications/Jakob2022DrJit)、[OptiX 2010 元数据](https://api.crossref.org/works/10.1145/1778765.1778803)、[Linking Types 出版记录](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SNAPL.2017.12)、[Typestate 作者机构记录](https://research.ibm.com/publications/typestate-a-programming-language-concept-for-enhancing-software-reliability)、[LuisaRender 作者页](https://luisa-render.com/)。CrossRT 原作者页确实显示 Garifullin Albert，未因姓名次序与另一数据库不同而判错。

接口资料核对 [Vulkan](https://docs.vulkan.org/spec/latest/chapters/interfaces.html)、[DXR](https://microsoft.github.io/DirectX-Specs/d3d/Raytracing.html)、[NVIDIA PyOptiX](https://github.com/NVIDIA/otk-pyoptix)、[NVIDIA OWL](https://github.com/NVIDIA/OWL)、[Slang capabilities](https://shader-slang.org/slang/user-guide/capabilities)。所引 [OptiX 9 官方 PDF](https://raytracing-docs.nvidia.com/optix9/guide/optix_guide.250130.A4.pdf) 本轮 web 抓取失败，不能声称本轮完成了该外部 PDF 全文复核，也不能据此断言地址失效。此有限外部访问缺口不构成当前稿的已证实引用错误。

## 7. 主 AI 现在应执行的工作与验收出口

1. 主 AI 独占稿件修改，直接完成 R7-LEAD-01 至 06；逐条引用本报告 ID 回报实际 diff。不要再写宏观计划、争论是否开始、增加 GPU 实验，或借文稿修正去修 runtime/checker。
2. 完成 R7-LEAD-07 的追加勘误及新版本 ledger/PDF 映射。旧 P、旧 PDF、原报告以及本次审查保留可恢复身份；不要将旧文件在历史上重标为已经过新字节验收。
3. 构建新 PDF，生成新候选 P′。重新记录 commit/tree、main.tex、references.bib、PDF、source bundle 的实际 hashes；逐页检查新 PDF。本文所列行号随后会变化，回报必须提供新位置。
4. 九成员 artifact 无需因上述文稿问题改字节；若保持它不变，必须核对仍为 `916cedbb...` 并重新登记新 PDF 与旧 artifact 的精确配对。不得将文稿版本变化冒充 F2 或 M 变化。
5. 以新配对申请最终审查，提供 7 项 finding 的关闭矩阵：旧问题、实际新句/图、定位、证据、是否改变 PDF/package bytes。两份实际独立响应必须覆盖最终交付字节；本次对旧 P 的退回意见不能算新 P′ 的通过意见。
6. 全部 material findings 关闭或受影响主张明确撤下、最终两份独立响应收到后，才允许依控制流程推进 R7/R8 状态。公开 claim authorization 和真实上传/投稿仍各有其门槛；未上传不得写 submitted。

没有发现需要推翻两代 GPU 有限数值观察、修改 F2 工具或废弃整个 bounded-admission 方向的证据。当前不接受原 PDF 字节，原因是图示和方法/限制表述尚未完整忠实于已经掌握的源码及裁决，而非包重放或性能数值失败。

REVISE_AND_REREVIEW_CHANGED_BYTES
