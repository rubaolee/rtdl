# CGO 2027 post-Goal5851 具体整改执行计划

日期：2026-09-06。交付对象：负责后续实施的主 AI。状态：**计划已提出，整改尚未执行**。

**执行目标：保留 d653 两代同源的有限实测结果，明确原 receipt 约束与实际实现的差异，交付论证一致的 11 页以内匿名正文、可重算的对应 artifact，以及逐项有证据的整改关闭记录。** 不以新增应用、继续性能优化、赶做人类研究或把历史检查改绿作为前提。

本计划落实 [Codex 独立审查][codex]、[Claude 审查][claude] 和 [意见吸收记录][absorption]，对接既有 [Goal5852–5856 冲刺顺序][sprint]。后续主 AI 应执行本计划并交付实际结果，不能以“已写计划”“已接受审查”替代整改。

## 0. 控制边界与交付原则

### 0.1 三个身份必须分开

| 身份 | 本轮基准 | 后续要求 |
| --- | --- | --- |
| 正式实验源码 M | `d653fe4ad170c5b51fee309d653c9565944dcf2e`；tree `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` | 两代正式结果永远绑定 M；E arm 仍绑定明确的冻结前代，不能把它误判为混源。 |
| 当前审查 HEAD | `04bd1d54f4641f12b6cf8e19a9e9eef5767a2021` | 启动时重取，不假定它仍是 HEAD。当前四份审查／吸收文件未跟踪，先保留和分类，不执行 `git add -A`。 |
| 投稿工具／文稿快照 F/P | 尚未产生 | F 是冻结前完成并提交的离线包装／核算工具快照，P 是最终论文与文档快照。不得将 F/P 宣称为两代 GPU 实际测过的 commit。 |

本次路径优先保持所有已测实现和实验执行文件不变。可以在冻结前为现有证据增加最小离线导出／核算／封包工具，但必须明确它们只读原数据、不启动 GPU、不修改原 gate；单列新增工具身份与验证结果。这不构成新的性能实验或旧 authority 重封。

**2026-09-08 00:00 America/New_York 是不可越过的开发冻结。** 此后不能修改 `src/`、`include/`、`experiments/`、`scripts/`、`tests/`，也不能将新的程序藏在 Markdown、临时目录或 artifact 中绕过冻结。已提交工具可以运行，文稿、bibliography、主张收缩、证据复制／哈希和包装重放可以继续。若本计划所需的新离线工具尚未冻结，先缩小交付承诺；不得在 9 月 9 日才开发它们。

### 0.2 何谓完成

每项整改至少记录：问题 ID、负责者、输入版本／hash、实际改动文件、验证命令、退出码及日志位置、完成状态、剩余范围、独立复核结论。状态只用：`OPEN`、`IN_PROGRESS`、`CLOSED_WITH_EVIDENCE`、`CLOSED_BY_CLAIM_REMOVAL`、`REJECTED_WITH_SOURCE_EVIDENCE`。

不允许单写“已处理”“Claude 同意”“全部 PASS”。删除主张可以关闭对应投稿问题，但不能将底层缺陷状态改为已修复。新裁决不改写任何历史 authority 的 `external_review_complete`、`public_or_manuscript_claim_authorized` 或旧 PASS 字段。

本计划不请求现在上传或联系外部人员。执行 AI 先完成可供审查的具体论文、包和清单；真实对外发送／投稿只在已有明确授权下进行。审查 AI 的意见如实标识，不充当外部人类作者研究。

## 1. 任务分工、依赖和时间表

主 AI 负责裁决、单一 `main.tex` 编辑所有权、合并与最终验收。可并行安排：证据核算助手只处理 raw→表；artifact 助手只处理新 staging 和离线工具；独立复核助手只读检查最终差异。禁止多个助手同时改正文。

时间均为 America/New_York，属于建议执行目标；硬冻结不随延误后移。无需为了等待日历日期而闲置，满足依赖即可提前完成。

| ID | 工作包 | 前置 | 建议最晚交付 | 完成后允许推进 |
| --- | --- | --- | --- | --- |
| R0 | 状态快照、工具和原始证据入口确认 | 无 | 9 月 6 日 17:00 | R1、R2、R3 并行 |
| R1 | receipt 差异裁决＋逐句 claim ledger | R0 | 9 月 6 日 21:00 | 写入对应正向论文措辞的内部候选稿 |
| R2 | 现有证据重算表＋最小离线工具冻结 | R0 | 9 月 7 日 18:00 | R4 性能正文、R6 artifact |
| R3 | 当前控制文档、勘误与历史 custody 分层 | R0、R1 | 9 月 7 日 18:00 | Goal5852 准确冻结记录 |
| R4 | 整稿重写与图表同步 | R1，数值部分依赖 R2 | 9 月 8 日 18:00 | R7 最终稿审查 |
| R5 | Goal5852 不可逆冻结 | R1–R3，所有新工具已提交 | 9 月 7 日 22:00；硬限 9 月 8 日 00:00 | 此后只有许可的文稿／包装／复核工作 |
| R6 | 匿名 artifact、干净目录离线重放 | R2、R3、R5 | 9 月 9 日 12:00 | R7 最终包审查 |
| R7 | 最终字节的两份独立审查与逐项关闭 | R4、R6 | 9 月 9 日 22:00 | R8 投稿门检查 |
| R8 | PDF／匿名／主张／上传字节终验 | R7 | 9 月 10 日 12:00 形成可提交包 | 按授权提交并保留回执 |

如果收到计划时某个建议时间已过，立即顺序执行对应项；不得跳过实质验收来填补时间表。若原始证据、匿名性或核心主张在截止前不能达到完成标准，应移除受影响主张并重做一致性检查；若移除后中央贡献已不可辩护，明确报告不满足提交门槛。

## 2. R0：建立可恢复的执行入口

### 操作

1. 读当前 [AGENTS.md][agents] 顶部 override、[冲刺文档][sprint]、三份本轮审查。读取相关 `memory/` 当前状态；旧 Goal 状态按确切源码／证据核对，不能沿用冲刺文档仍写的 `c4351f612...` 为最终两代来源。
2. 记录以下只读输出与 UTC／ET 时间；确认没有另一个 AI 同时改相同文件。

```bash
cd /Users/rl2025/rtdl_v4_restricted_python_design
git status --short
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git branch --show-current
git diff --name-status d653fe4ad170c5b51fee309d653c9565944dcf2e..HEAD
```

3. 创建后续执行记录目录（这是拟建输出，不是已完成证据）：
   `/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/`。
   至少维护 `STATUS.json`、`PROTOCOL_SCOPE_ADJUDICATION.md`、`CLAIM_LEDGER.json`、`EVIDENCE_INDEX.json`、`FREEZE_RECORD.md`、`VALIDATION_LOG.md`、`FINAL_CLOSURE_REPORT.md`；只有实际形成的文件才能列为 delivered。
4. 确认两个原始目录和 cross authority 可读：
   - `/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass/`
   - `/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_d653fe4_pass/`
   - `/Users/rl2025/RTDL_evidence/goal5848/goal5851_cross_generation_d653fe4_complete/`
   记录实际 archive／manifest／authority 路径。仅“另一个报告写有 hash”不算当前 payload 已找到。
5. 立即做工具适用性盘点：当前 `paper/cgo2027/artifact/` **不存在**；不能从旧 README 推定旧包仍在。检查 Python 3.12、Tectonic、PDF 提取和渲染工具实际路径。先构建一次现有稿到新临时输出目录，以尽早发现 TeX 依赖缺口；此构建只检查环境，不算新稿完成。

### 完成标准

R0 日志有真实快照、每个原始入口的存在性、当前 dirty 文件处置清单、可用构建路径。没有覆盖或删除原审查和 evidence；不存在把未跟踪 scratch 误当 committed 外部共识的情况。

## 3. R1：先完成 receipt 协议差异裁决

### 必读位置

- [原 Goal5848 §8][protocol]，尤其 (4)、(6)、(8)，同时考虑“full forensic expansion 可显式留在普通快路径外”不能自动免除决策性 receipt 条件。
- [public fused replay][replay]、`_FastPathReceipt`、`_DeferredFastOperationReceipt`、`_DeferredCompactDeviceStatus`。
- [worker 采样][sample]、逐输出 validator、另一次 diagnostic，以及 [验收合同][evidence-validator]。
- [Codex 最小 mock 与源码证据][receipt-review]；本次两个审查版本和 [吸收记录 §5][absorption]。

### 必做交付

在 `PROTOCOL_SCOPE_ADJUDICATION.md` 中建立如下矩阵，并给每行源码及 raw 定位，不能只写总括句：

| 义务／字段 | 实际建立／检查阶段 | 现有证据可以支持什么 | 不可声称什么 |
| --- | --- | --- | --- |
| 协议角色、效果、资源合同、静态身份 | compile／admission／materialize／bind 的相应阶段 | 精确已实现静态规则与 loaded-image identity | 每次 execute 都重新读磁盘 DSO/PTX 并重哈希；hash 证明语义正确 |
| native return、compact device status | public 执行成功返回前，同步检查 | 该支持路径的同步错误拒绝 | 所有详细物理 receipt 字段也已全部验证 |
| relation counts／capacity、triangle scalar | 各自 family 的同步检查；scalar oracle 存在时检查 | 各 family 的具体拒绝和正式 exact output 对照 | 两 family 的结构证明完全相同；所有普通用户都提供 oracle |
| 正式逐次输出 oracle／hash | steady `_sample` 外层在 action 后验证；first-result 必须另按其边界记账，可能包含该检查 | 正式结果逐次符合冻结输出合同 | 所有该验证都在 public return 之前；所有验证都在所有端点计时外 |
| 详细 operation receipt | 普通快路径按需展开／验证 | 实际消费时的验证语义 | 全部 timed samples 已逐次展开、保存完整证明 |
| launches、raygen、traversable、output digest、monotonic identity | 分别列 raw compact 对象、缓存状态与另一次 diagnostic 中实际有什么 | 只保留逐字段真实存在／验证／持久化范围 | 将另一轮 diagnostic 作为 128 个 timed execution 的完整物理轨迹 |

附件必须逐字段列出 `_FastPathReceipt` 的 27 个 ABI 字段，以“执行前／返回前／显式观察时／正式归档留存”为列。字段清单如下，实际条件查 `v4_rtdlexe.py:3951` 定义及 `:5005` validator；不能用字段名称代替检查证据：

```text
schema_version, optix_launch_count, host_blocking_boundary_count,
control_d2h_bytes, output_d2h_bytes, status_before_output,
output_d2h_after_status_failure, role_counters_materialized,
prepared_input_reused, dynamic_device_upload_call_count,
dynamic_accel_build_count, dynamic_explicit_sync_count,
dynamic_blocking_upload_call_count, dynamic_device_upload_bytes,
dynamic_input_generation, semantic_compaction_launch_count,
semantic_compaction_key_capacity, semantic_compaction_scratch_bytes,
callback_status_kernel_launch_count, checked_product_kernel_launch_count,
compact_control_finalizer_kernel_launch_count,
total_auxiliary_cuda_kernel_launch_count, execution_parameter_h2d_bytes,
execution_parameter_h2d_copy_call_count, stream_ordered_memset_call_count,
status_d2h_copy_call_count, output_d2h_copy_call_count
```

对该 raw 对象而言，成功返回前有字段暂存不等于详细 validator 已运行；正式 worker 没有逐样本保存它。还要另列 ABI 不含的 actual raygen、traversable 和 monotonic execution 字段。`dynamic_input_generation > 0` 不能替代逐次执行序列；worker 确实计算输出 hash，缺的是逐样本 hash 与完整物理 receipt 的持久绑定，不能改写成“从未计算 output hash”。

裁决必须明确写出：**登记机器数值门槛通过；原书面逐次 receipt 条款不能签认为原样履行；已保存数据仍可作为附有该偏离披露的有限 public-path 性能观察。** 若主 AI 反对任一事实，必须给匹配 M 源码和现有 raw 的反证，不能引用 PASS 字符串作为反证。

建议正文范围句（据最终裁决调整，可直接起草）：

> We evaluate the public prepared path with synchronous native and compact-status checks and per-call output-oracle checks in the experiment. Detailed execution-receipt validation is deferred, and the retained timing workers contain a separate diagnostic receipt rather than a complete per-sample physical trace. These measurements therefore do not establish the original preregistered per-execution receipt requirement.

为每项预期论文主张分配稳定 ID。`CLAIM_LEDGER.json` 每行包含：`claim_id`、最终候选句、`scope`、精确 source/evidence hash、验证阶段、限制、论文 section／table、`disposition`、复核人及版本。至少覆盖：中央编译器贡献、静态准入、TCB、prospective exam、finite checker、四个 A/D 行、双端点、A/E 启动回退、A-only instrumentation、AOT、artifact replay、human/prevalence=0。

### 完成标准

1. 原§8(4)/(6) 与实际路径逐项对应；self-review 关于计时后逐样本物化 receipt 的不实说法有明确纠正。
2. 数值结果、实验验证边界、书面协议合规性分别判断；`original_written_receipt_requirements_fulfilled` 不被写成 true。
3. 保留 native／compact／output 检查事实；未将 mock 注入说成正式 GPU 真实违规。
4. 主文至少有一处直接可读的偏离披露，相关摘要／结论不得仍承诺“全部原安全保证”“fully checked”而不定义范围。
5. 不改旧协议／authority，不补造 missing receipt，不修源码后沿用旧 timing 为修复版证据。
6. 独立复核者能从矩阵复查结论。若此处不能形成可辩护的窄主张，撤下对应正向性能／逐次证明主张；底层缺陷留作后续工程。

**R1 的完成是范围裁决完成，不是底层 receipt 缺陷修复完成。**

## 4. R2：固定新表、核算方法与离线工具

### 4.1 最少输出四组表

表一作为主性能表，所有比值在同一机器内计算：

| GPU／任务 | A/D steady median | A/D 最大 block：描述值 | A/C entry median | A/C post-import median |
| --- | ---: | ---: | ---: | ---: |
| Ada triangle | 1.175066 | 1.211025 | 0.642180 | 1.559788 |
| Ada relation | 1.076852 | 1.092253 | 0.653826 | 1.749327 |
| Ampere triangle | 1.133636 | 1.142675 | 0.618362 | 1.637468 |
| Ampere relation | 1.094795 | 1.118811 | 0.681393 | 1.837415 |

表二必须明确是新增事后派生比较：

| GPU／任务 | A/E steady：原登记 | A/E post-import：非 gating | A/E entry：非 gating |
| --- | ---: | ---: | ---: |
| Ada triangle | 0.903016 | 1.169262 | 1.079554 |
| Ada relation | 0.584438 | 1.305383 | 1.192358 |
| Ampere triangle | 0.922388 | 1.162775 | 1.137637 |
| Ampere relation | 0.608228 | 1.261676 | 1.216714 |

表三为八行 import／gap／post-import／entry 描述分解，数值与 [吸收记录 §3.3][absorption] 对照；表四保留四组 post-import block 范围和全部 32 个 A/D block ratios。Ampere relation 的 post-import 最大 block 必须是 **2.377129**。可将完整数组放匿名 supplement，主文要显式披露不利方向和这一最大值。

### 4.2 estimator 和分母不可自行改动

- 每代 2 tasks × 5 arms × 8 blocks = 80 formal workers，每 worker 128 steady samples；每代五 arms 共 10,240，两代共 20,480。A 单代只有 2,048，两代 4,096；warmups 不混入。
- 128 整数 ns 的 median 是排序后中间两项整数均值；每 block 的 ppm 为 `(numerator_ns * 1000000 + denominator_ns // 2) // denominator_ns`；八 block ratios 的 median 也用整数均值。最后才格式化为小数。
- A/D：steady median ≤1.20，**没有 A/D worst-block gate**。A/C entry：median ≤1.20，max block ≤1.35。A/E steady 和 C/B steady 按原 ≤1.05 gate；不追认 A/E entry gate。
- 原 post-import 为强制不利 diagnostic；新 A/E 首结果和 import 百分比分解为事后描述。不得将它们冒充预注册 primary，或新增 CI／bootstrap 并伪装为原 estimator。
- instrumentation qualification 每代 512 workers 只覆盖 A；A/B/C policy 一致另列。C/B competence、AOT qualification 和 output checks 各自指出实际证据分母。
- E 是不同的明确 predecessor，不与 A/B/C/D 冒称同一 source。不同 GPU 的 raw time 不互相相除。

### 4.3 现有工具不能冒用

| 现有文件 | 本次处置 |
| --- | --- |
| [Goal5817 performance projection][old-projection] | 写死 324 workers、旧三 arms、18 rows；仅保留历史用途。 |
| [Goal5817 manuscript validator][old-validator] | 写死旧稿句子与数值；不能拿它验新版，不能为通过它恢复旧句。 |
| [Goal5817 manifest builder][old-manifest] | 固定旧 payload 列表；不能称其覆盖新版缺失项。 |
| [Goal5822 packer][packer] | deterministic tar／manifest 逻辑可复用，但默认目录不存在、黑名单不完整；只验证归档字节不等于验证新论文。不得覆盖旧包。 |
| [Goal5822 PDF sanitizer][pdf-sanitizer] | 可处理新副本，但原标题固定、旧身份黑名单有限，依赖 assert，必须普通 Python；与最终标题不一致时需冻结前解决或不用该工具。 |
| [当前合同的 evaluate_complete_transaction][formal-evaluator] | 可复用标准库 formal 重算、schedule、worker seal 和输出检查；不覆盖完整 preregistration／文件 custody／process stdout／512 instrumentation／AOT，全层状态必须分开。 |
| [当前 cross builder][cross-builder] | 可核验两份单代 authority/recount 的同 source／不同 GPU、seals 和逻辑；不是再次检查 raw workers，输出绑定输入绝对路径。 |

优先复用 `strict_json_loads`、worker validator、schedule、`evaluate_complete_transaction` 完成内部复算，并复用 packer 的 `build_bytes`／`verify_archive`。新桥接层补精确成员集合／hash、process 关联、instrumentation／AOT 分组和 source pins；不开发通用 full-authority rebase。若缺少适配新数据的匿名导出／验证入口，**现在就在冻结前完成最小新工具，而不是修改旧历史验证器**。拟新增文件范围限于：

1. `/Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5852_build_submission_evidence.py`：只读原证据，显式参数传入 Ada／Ampere／cross 根，验证输入身份与计数，输出匿名数值投影、表和私有 provenance map。拒绝覆盖既有输出根。
2. `/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/artifact_post_goal5851/verify.py`：标准库离线 replay；不导入 RTDL，不访问原用户目录，不启动 GPU，重算数值并验证 manifest。这个程序属于需在冻结前提交的工具，不能以目录属于 paper 为由延后开发。
3. `/Users/rl2025/rtdl_v4_restricted_python_design/tests/goal5852_submission_evidence_test.py`：仅测新离线桥接／完整性和失败拒绝，不改现有 runtime／experiment tests。

以上是**拟新增接口**，当前尚不存在，不得在完成记录中写成已经执行的命令。实现时 CLI 至少公开 `--help`、显式输入、显式新输出；主 AI 在 README 写入实际 CLI 后，必须照其原文重放。

### 完成标准

1. 对现有 raw 重建 160/160 worker medians；四组主表、四组 A/E 派生比较、全部 block arrays 与上述精度一致。输入不是两个报告表的相互抄写。
2. 私有投影审计逐项确认全部 20,480 个 steady ns 值、全部首结果分解字段原样保留；匿名化只影响批准的身份／路径字段。样本、arm、block、threshold、endpoint 不变。
3. 私有证据索引包含原文件 hash→投影文件 hash 的映射、删除／替换字段规则、计数及源版本。新投影不冒充原 archive byte identity。
4. 新离线工具在缺 worker、重复 cell、缺 sample、修改单个 ns、错 source（E 的合法 predecessor 例外）、错 gate 类型／阈值、错 projection hash 的注入下都拒绝；这些新检查必须真正命中错误条件，不能仅比较预置 PASS 文本。
5. 单独实现在不导入 controller 汇总函数的情况下重算并比对；模板表不是唯一 oracle。记录两次相同输入的确定性输出及实际 hash。
6. 需要纳入包的 A-only instrumentation、AOT、competence 数字均附可核算数据；缺某层就撤下该层“包内可复现”的承诺，不得靠未交付文件支撑 artifact claim。
7. **冻结前先完成一次成功的最小端到端演练**：原 raw→匿名导出→封包→脱离仓库的新目录解包→标准库 verifier；取消项目 `PYTHONPATH`，使用含空格路径，确认无隐藏作者路径／依赖。拒绝测试通过不能代替成功链可用。R6 再核验最终文稿／包字节。
8. 9 月 7 日目标时间前新工具及其拒绝测试提交、推送、记录 commit，并从该快照完成演练。未达到则在 R5 前明确降级方案和受影响主张。

## 5. R3：修正当前控制文档，历史只追加勘误

### 具体编辑位置

1. [AGENTS.md][agents] 顶部新增当前审查吸收 override：保留 d653 原测量身份和历史机器结果；指向 R1；限定 per-call receipt、native-fork、双故障、A-only qualification；写明 review received 不等于稿件／artifact 已复核或外部人类证据非零。
2. [冲刺文档][sprint] 追加 post-Goal5851 状态记录，明确 `c4351f612...` 是历史单代，当前 final M 是 d653；旧章节保留历史时态。R5 的分支选择需附 R1 限定，不能沿用“全部原协议无偏离通过”的推论。
3. [KNOWN_STALE_CUSTODY_CHECKS.md][custody] 加入 Goal5837、Goal5843 的 current-tree failure 原因、准确命令和 exact snapshot 条件。保留 Goal5832 没有可用完整历史 Git commit、Goal5838/5840 off-Git bytes 的区别。
4. 在执行记录中的追加勘误清单列：CFR／self-review 的 Ada 63 位 hash；repair report 将 A/D worst block 误称 1.35 gate；self-review 逐样本 receipt 说法；错误的三 arms ON/OFF qualification 推论；两固定构造器和 unbiased exam=0 的错误“纠正”。注明原文件／段落及替代说法，不重写原审查或历史 authority。
5. root [README][root-readme] 与 [paper README][paper-readme] 同步 current scope：不把新两任务结果宣布为旧全部 portfolio 全面闭债，不把旧压缩包说成新 artifact。
6. 更新 `/Users/rl2025/rtdl_v4_restricted_python_design/memory/progress.md`、`memory/decisions.md`、`memory/todo.md` 的当前入口；实际完成和 pending 分开，指向执行状态。只做必要追加，不整理全历史。

Ada 正确 archive SHA-256：`c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced`。

### 完成标准

新会话只读当前 AGENTS、README、memory 就能知道下一项、最终 M、原 receipt 限定和 artifact 实际状态；不会继续旧 c435 两代配对、宣称现稿可投或把全部历史 red checks 一律当正常。所有勘误有原位置和依据；原 authority／archive hash 未变化。

## 6. R4：整稿逐 section 重写

下列定位以当前 [main.tex][paper] 行号为起点；编辑后用 section／label 重新定位，不能机械保持行号。先写新论证骨架，再替换对应段落与图表；不要在旧论证上不断追加互相矛盾的 caveat。

| 当前定位 | 主 AI 实际要改什么 | 可判定完成标准 |
| --- | --- | --- |
| Abstract 40–80；Introduction 124–174 | 重写 thesis、问题和贡献列表；定位 bounded whole-protocol compilation/admission。R1 通过后才填精确范围的性能观察。 | 一句中央 thesis、最多四项贡献；无 arbitrary topology／intrinsic speedup／全协议原样证明承诺。 |
| Callback IR 274–545 | 保留 typed roles/effects/resource 实际机制；区分 production admission、trusted lowering、另行独立 checker。 | 不能把 production projector 改叫独立 checker；每个概念有实际阶段和责任。 |
| Admission 549–605；lifecycle 607–638；judgment 680–728 | 建立静态→materialize/bind→同步执行→按需 receipt→独立 diagnostic 的阶段说明，替换逐次 rehash／完整 receipt 保证。 | R1 范围句在主文可见；详细 receipt 和 output oracle 的计时／发布阶段准确。 |
| Terminology 640–678；capability 925–943 | 将 stable facade 和全 V4 分母分行；增加历史 bounded composition 事实。 | stable constructors=2；stable 2/6、2/4 如保留必须限定；全 V4 kind presence=4/6、4/4；composition=1，unbiased new-application=0，external human=0。 |
| Architecture figure 730–798；implementation/TCB 819–887 | 图中分开共享 schema/admission、特定拓扑 lowerer、runtime gate、offline checker；修改必须改 shared core 的全称句。 | 图、caption、正文一致；可信 lowerer 在 frozen core 外；hash 不被当作语义证明。 |
| Evaluation 945–1115 附近 | 分设 prospective composition 与 finite target-structure subsections；压缩旧 reuse 叙事。 | Goal5838：10 行作者定义域、7×四角色＋3×六角色、约 2,635 行实现成本、12 oracle rows／2 launches、exact historical source；不改称无偏新应用。Goal5840：3 routes／4 modes／5 property classes／20 applications／15 unique mutations，并写 early-return 限制。 |
| Performance 1124–1207 | 整段替换旧三-arm／324 workers／7,128 timings／18-block CI；使用 R2 的两任务五 arms 两代合同。 | 主表、caption、摘要数字、supplement 一致；A/D median gate 与 worst 描述分清；A/E 启动回退、post-import adverse 和 import 含义可见。 |
| Programming responsibility 1209–1223；Related work 1225–1453 | 保留具体责任比较；讨论 native typed payload／OWL 已有能力与 RTDL 的剩余贡献。 | 无人类易用性／生产率优势，无未经调查的真实缺陷流行率；不使用“所有现有工具都不能…”无证全称句。 |
| Artifact 1455–1488 | 改写为 R6 真正提供的文件、offline recount 和 source／GPU 重跑边界。 | 每个“提供／可重放”对应包内真实文件及已执行命令；匿名 projection 与 original archive 清楚区分。 |
| Threats 1490–1540 | 加入 receipt 偏离、double-fault、Python-hook 进程范围、checker 局限、两任务适应性工程、残留 arm 差异和历史 bytes 条件。 | 不把问题全部藏 supplement；不把新结果泛化到未重跑 cohort；人类／prevalence 的零仍在。 |
| Conclusion 1542–1573；paper README | 最后重写，仅总结已经在正文建立的主张；写实际 build 和 artifact 入口。 | 与 abstract／ledger 同范围，无旧稿状态或新引入的数字／保证。 |

### 不可做的机械升级

旧 19 leaves、3+1+1 residual 等有自己的历史分母，不能把 Goal5838/5840 加进去；两 fixed constructors 仍是两，不改成三。Goal5840 的 20 是 property applications，不是 20 个独立语义属性；15 mutations 不代表所有故障。旧 Goal5845 9.53x 仅是当时命名 arms 的观察，不能借本次 C/B≈0.22 回推成“被夸大 4.5 倍”。

### 正文篇幅建议

正文最多 11 页，以 10.5 页内容为目标留排版余量：问题／贡献约 1.25 页，模型／IR／准入约 2.5 页，lowering／runtime／TCB 约 1.5 页，有限 extension／checker 约 1.25 页，性能约 2 页，related work／limits／conclusion 约 2 页。数值为写作预算，不是修改字号和间距的理由。完整失败谱系与逐 block 数组进匿名 supplement，核心限制留在主文。

### 完成标准

`CLAIM_LEDGER.json` 中每个正文／图表主张都有最终定位；无“待填”“旧结果临时代替新结果”；每个数字附 task／arm／regime／GPU／estimator／证据范围。独立 reviewer 能在不读内部历史的情况下理解论文，且不会推导出任何已撤回主张。

## 7. R5：冻结的是实际字节与可用主张

`FREEZE_RECORD.md` 必须记录 M、E、F 的完整 commit/tree、所需上游／submodule 身份、工具版本、干净状态、pushed 状态、原 evidence hashes、R1 与 ledger hashes，以及冻结 UTC／ET。

对现有冲刺二分支，明确分开：`machine_numerical_result` 可以保留两代登记机器 PASS；`original_written_receipt_requirements_fulfilled` 仍为 false；`submission_claim_scope` 指向 R1 的有限观察。需要新的审查限定文字就追加，不修改旧实验门槛或原 authority。若不能保留这一有限观察，使用撤下正向主张分支，并同步正文／artifact。

完成 F 后比较 M→F 的差异：已测 `src/`、`include/`、`experiments/` 和原实验 scripts/tests 必须 byte-identical。允许的新增离线文件单独列 whitelist；不能把存在新工具的 F 说成“所有 scripts/tests 自 M 以来零变化”。不自动提交其他 AI 的 scratch；只将明确的交付文件纳入，保留其他文件但如实报告是否 clean。

**冻结完成标准：**所有要在后两天运行的新程序已经提交并可从 F 获取，而且已完成 R2 的匿名导出／封包／陌生目录成功重放；ledger 范围已明确；没有“明天再写个 verifier”的隐含开发。此后代码缺陷只导致主张撤下／缩小，不能以 cleanup 很小为理由修复并沿用原数据。

## 8. R6：匿名 artifact 与可迁移性必须真做

### 8.1 两层证据不能混称

**私有 custody 层**保留原 archive、stdout/stderr、真实路径／UUID、Git 身份、authorities 和审查记录，字节不改。**匿名交付层**可以是明确的派生投影：使用中性 task／arm／机器别名，去除用户名、路径、内部 Goal／review 标识、网络／pod endpoint 等，但完整保留测量 endpoint、对应数值和关联结构。原始包 hash 与匿名包 hash 必须分开；不能声称删改后的文件仍是原 hash-bound raw。

若原始字节可匿名且可分发，可直接纳入；若存在身份或分发限制，在包内提供能支撑相应主张的投影／源码，并明确未交付原件的范围。审查报告、memory、AGENTS、私有 provenance map 不进入公开匿名包。不能通过改写旧原件、重封 authority 或删除不利行解决匿名问题。

### 8.2 新 staging，保留旧历史

使用新目录 `/Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/artifact_post_goal5851/`，不要覆盖旧命名包或历史 anonymization gate。至少实际交付：

- `README.md`：quick start、依赖、硬件需求、可重放和不可重放范围；所有命令从解包根可执行。
- `manifest.json`：路径、长度、SHA-256；声明匿名派生 schema，不能冒用原 authority schema。
- `data/`：用于全部保留论文数字的完整投影，包含两代、五 arms、所有 blocks／steady samples／首结果分解；资格实验若有包内复现主张，也提供其数据。
- 冻结的 `verify.py` 与必要源码／合同：离线计算不依赖作者电脑，也不导入被测 compiler。
- `EXPECTED_RESULTS.md`、`CLAIM_SCOPE.md`、`REPLAY_MATRIX.md`：具体数值、支持范围、明确 expected-red／not-provided／GPU-required。
- `LICENSES/` 或等价清单：仅包含有清楚分发依据的依赖；未打包专有组件有可获取说明和已验证范围，不宣称完全离线重建 GPU 环境。

### 8.3 清洁重放

先从 F 的全新干净 checkout 取得冻结工具／源码，P 仅作为明确文稿／文档 overlay。然后把匿名包解到两个不同绝对路径，其中一个含空格；在独立环境断开网络、取消项目 `PYTHONPATH`，只按包中 README 执行。不得借用当前仓库中的 raw、`/workspace`、用户 venv 或未列依赖使其通过。

每次记录输入 package hash、工具 hash、实际 cwd、命令、退出码、输出 hash。同输入的确定性 artifact 构建必须两次字节相同；两个独立解包目录的数值重算结果必须相同。不要承诺普通 TeX PDF 自然可复现为相同 bytes；PDF 最终以实际 reviewed bytes 的 hash 固定。

**portable raw recount 与 full-authority replay 分开验收。** 当前单代 full authority 不仅会读 `/workspace`，还要求原 artifact／Python 路径及原 RTDL、predecessor、PyOptix Git 工作树 clean；原包没有包含这些完整工作树和 venv。提供 fresh M checkout 或一条 symlink 不等于重建原环境。本轮默认交付分层离线验证，不把恢复完整原 pod 环境作为任务。若确有该环境并重放成功，另列其严格前提；否则 README 明示不能完成 full historical authority reconstruction。

cross 文件输出包含输入绝对路径：同一输入路径两次输出应相同；搬迁后应比较逻辑字段与 seals 的正确重算，不能强求新 cross 文件与历史 hash 相同。原存储 authority/recount 的字节相等检查则仍按原 bytes 执行，不能混同。

数字重算和产品使用也分开：标准库 offline recount 不等于产品安装成功。如保留“可运行 RTDL”的 artifact 承诺，还须冻结依赖 wheelhouse，或明确并验证 source-tree fallback 和预装依赖；没有缓存的 `pip install -e .` 不叫离线安装。产品 CPU quickstart 可采用现有 `/Users/rl2025/rtdl_v4_restricted_python_design/examples/current/v4_restricted_callback_quickstart.py`，实际预期为 `verified_cpu_semantics` 且 `gpu_execution_claimed:false`；这不是 GPU 实证。包中未包含可执行源码时，直接标为 evidence-recount package，撤下产品可运行承诺。

### 完成标准

新包真实存在，manifest 全项通过；160 formal cells、20,480 steady samples 和所有论文保留指标能够从交付数据复算；两目录离线验证成功；源数据投影对照无漏项；匿名扫描覆盖文件名、内容、压缩包成员、metadata、二进制 strings 及日志；所有报告的限制与主文相同。缺任何一项不能写“artifact ready”。

## 9. 验证矩阵与实际命令

以下既有命令可用于最终干净快照的 current regression。它们此前已经通过；只有换了干净环境、打包范围、相关代码或出现新问题时才需要重复，不对每次纯措辞编辑重跑全部测试。

```bash
cd /Users/rl2025/rtdl_v4_restricted_python_design
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest discover -s tests -p 'goal5848*_test.py'
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python -O \
  -m unittest discover -s tests -p 'goal5848*_test.py'
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest tests.goal5851_triangle_fused_replay_test
git diff --check
```

预期分别 128/128、128/128、7/7；不同平台出现 skip 必须单列，不能凑成全部执行通过。上述 venv 仅是本机开发验证入口，匿名 artifact 不得依赖这个绝对路径。

| 层 | 预期结果／处置 |
| --- | --- |
| 新离线工具的拒绝测试 | 在冻结前真实执行全部规定注入并记录拒绝；不依赖 `assert` 在 `-O` 下消失的检查。 |
| Goal5838 current seal suite | 当前曾为 8 pass／1 error；在 exact historical snapshot 检查另列，不重封原 seal。 |
| Goal5832 current shape suite | 当前曾为 22 pass／1 error；无完整可 checkout 历史 commit，不能套用统一旧 commit recipe。 |
| Goal5837 authority current verify | `AUTHORITY_CURRENT_INPUT_MISMATCH` 的已知边界，写 exact 原因及可重放前提。 |
| Goal5843 authority current verify | preregistration canonical mismatch 的历史／当前输入边界；不能用当前文件重封旧 evidence。 |
| Goal5838／5840 exact authorities | 分离 Git 中可核对 source/seal 与 off-Git DSO/raw 条件；只有实际提供并重算的 bytes 才报 byte replay。 |
| 全库 discovery | 非默认投稿门；若运行，保留所有错误并逐类解释，不能一概“历史噪声”或一概“产品坏了”。 |
| GPU replay | 与离线数字重算分开；不要求为本次文稿修改再租 GPU。未实际执行的重跑指令标为未执行，不以脚本存在冒充实证。 |

### 现有 formal 重算调用，可在 R2 固化为冻结入口

以下只调用已提交的合同函数，不运行 GPU；它验证 formal 层，**不是 full custody/authority verifier**。从 M 或经 diff 证明相关文件等同 M 的 F 执行。后续匿名包应有自己的冻结入口，不依赖此处作者绝对路径。

```bash
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python - <<'PY'
from pathlib import Path
from experiments.goal5848_strong_baseline.contracts import (
    evaluate_complete_transaction, strict_json_loads,
)
base = Path('/Users/rl2025/RTDL_evidence/goal5848')
def read(path):
    return strict_json_loads(path.read_text(), label=str(path))
for name in ('goal5851_successor_ada_d653fe4_pass',
             'goal5851_successor_ampere_d653fe4_pass'):
    root = base / name
    receipts = [read(p) for p in sorted(
        (root / 'formal-transaction/workers').glob('*.json'))]
    result = evaluate_complete_transaction(
        receipts,
        expected_source_commit='d653fe4ad170c5b51fee309d653c9565944dcf2e',
        expected_predecessor_commit='12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8',
    )
    if result != read(root / 'formal-transaction/transaction.json')['recount']:
        raise RuntimeError('stored transaction recount differs')
    if result != read(root / 'single-generation-authority.json')['recount']:
        raise RuntimeError('stored authority recount differs')
    print(name, result['status'], result['worker_count'],
          result['retained_steady_sample_count'])
PY
```

预期两行的结果部分均为 `PASS__GOAL5848_LIFECYCLE_CORRECTED_SINGLE_GENERATION_PERFORMANCE_GATES 80 10240`。此字符串只表示它所命名的机器性能门槛，不撤销 R1。

现有 cross CLI 示例（输出文件须不存在；第二次使用新输出名）：

```bash
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  scripts/goal5848_build_cross_generation_authority.py \
  --first /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass/single-generation-authority.json \
  --second /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_d653fe4_pass/single-generation-authority.json \
  --output /tmp/rtdl-post-goal5851-cross-replay-1.json
```

### PDF 构建与检查

当前环境已找到 `/opt/homebrew/bin/tectonic`，未在 PATH 找到 `pdflatex`／`bibtex`／`latexmk`。可从如下命令开始，在 R0 尽早确认实际构建：

```bash
mkdir -p /tmp/rtdl-cgo-final-build
/opt/homebrew/bin/tectonic \
  --only-cached --keep-logs --keep-intermediates \
  --outdir /tmp/rtdl-cgo-final-build \
  /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex
pdfinfo /tmp/rtdl-cgo-final-build/main.pdf
pdftoppm -png -r 120 /tmp/rtdl-cgo-final-build/main.pdf /tmp/rtdl-cgo-final-build/page
```

缓存不足时明确获取并记录构建依赖后重试，不能把 `--help` 成功写成编译成功。用可用 PDF 库提取文本并检查引用／主张；逐页查看图片，检查双栏表格、图轴、caption、断页和字体。最终日志必须没有 undefined citations/references 或待 rerun；排版无截断／重叠／未处理的 overfull 内容。

## 10. R7：复核实际最终稿和包，不能只复核旧报告

生成自包含请求，提供 F/P/M、PDF 和 artifact hashes、R1 裁决、ledger、actual replay log、已知 limitations。请求 Claude 和另一位独立 reviewer 检查**这些字节**；此前对旧稿／旧包的审查不能自动算最终审查。主 AI 的内部助手复核也不能伪装成已经收到外部回复。

每条 finding 填：原编号、`accept`／`reject-with-source-evidence`／`claim-descope`、具体变更、最终文件定位、验证证据、未解决差异。尤其必须给 receipt 分歧直接答复；不能只写两边“总体支持投稿”然后宣布 consensus。

**完成标准：**两份实际收到的最终版本审查可追溯；所有影响当前保留主张的实质问题均关闭或主张已删；底层已知问题仍按 scope 披露。review pending 就继续标 pending。如果版本随后有实质变化，重审相应差异；不是重跑所有无关测试。

## 11. R8：官方规则、匿名终验和提交完成标准

2026-09-06 核对 [CGO 2027 官方投稿指南](https://2027.cgo.org/track/cgo-2027-papers)：正文最多 11 页，references 不限；ACM sigplan、Letter、匿名 PDF、可读黑白图、页码和 review 行号；appendix 作为匿名 supplementary material 单独提交，正文应自包含。官方页面不同段落对 appendix 的概述存在措辞差别，本计划采用具体 Submission Guidelines 的单独 supplement 路径。

[官方 HotCRP](https://cgo27.hotcrp.com/) 当前显示 R2 截止为 2026-09-10 23:59:59 AoE，即 2026-09-11 07:59:59 America/New_York。仍按项目 9 月 10 日白天提前完成，不把时区换算当额外开发窗口。主计划按 standard research submission，不因这次审查改成 Tool Paper；后者有额外 artifact 要求，不应默默切换。

最终检查实际 PDF：正文／references 分界、11 页上限、无正文内 appendix、引用可解、全文英文、图表黑白可辨；匿名性由两份独立扫描结果支持。不能仅用 `pdfinfo` 的总页数断言正文页数合规，也不能以消除合法自引来制造匿名。

`FINAL_CLOSURE_REPORT.md` 必须包含：

1. R0–R8 状态表、实际交付文件及 hashes；已关闭和剩余问题，不以计划状态代替执行状态。
2. 原书面 receipt 限定与论文最终措辞；所有被删除／缩小的主张列表。
3. 两代 raw→projection→table→PDF 的核算链、匿名包验证及确定性记录。
4. F/M 执行文件差异、P 文稿差异、冻结记录、实际测试与 expected-red 清单。
5. 两份最终审查、逐项 disposition、仍存在的判断差异及为什么不影响保留主张。
6. 最终 PDF、source bundle、supplement／artifact hash 和匿名提交位置。
7. 如已获提交授权并完成上传：上传回执／时间；系统允许时下载核对 hash。未上传则准确写“可提交包已完成，上传未执行”，不能写整个投稿已完成。

## 12. 主 AI 启动时可直接采用的执行指令

> 先执行 R0；随后并行推进 R1 的协议差异裁决、R2 的 raw 核算与匿名离线工具、R3 的状态勘误。主 AI 独占 main.tex。禁止修改已测 runtime/实验路径，禁止重封旧证据。所有新程序最晚在 2026-09-08 00:00 ET 前冻结并提交；此后仅运行已冻结工具、改稿、缩主张和包装。R1 的 receipt 差异没有明确处置前，不在论文摘要写“全部检查／原协议完全通过”。按 R4 完成整稿，按 R6 在陌生目录离线重放实际匿名包，再把最终 PDF/包交 R7 独立复核。每完成一项用文件、日志和 hash 更新 STATUS，而非只报口头进度。若命令或证据缺失，指出精确缺口并按本计划缩减承诺；不要恢复旧数字、创造 receipt 或继续扩功能来凑 PASS。最终交付 R8 的真实关闭报告。

[codex]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_review_post_goal5851_cgo2027_20260906.md
[claude]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/review_post_goal5851_cgo2027_20260906.md
[absorption]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_claude_post_goal5851_review_absorption_20260906.md
[sprint]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/cgo2027_final_sprint_goals_20260905.md:117
[agents]: /Users/rl2025/rtdl_v4_restricted_python_design/AGENTS.md
[protocol]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/goal5848_strong_baseline_post_import_20260905/GOAL5848.md:267
[replay]: /Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_rtdlexe.py:6255
[sample]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/worker.py:168
[evidence-validator]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/contracts.py:627
[receipt-review]: /Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/codex_review_post_goal5851_cgo2027_20260906.md:343
[old-projection]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5817_build_anonymous_performance_projection.py
[old-validator]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5817_validate_cgo_integration.py
[old-manifest]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5817_rebuild_anonymous_artifact_manifest.py
[packer]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5822_build_anonymous_artifact_package.py
[pdf-sanitizer]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5822_sanitize_anonymous_pdf.py
[formal-evaluator]: /Users/rl2025/rtdl_v4_restricted_python_design/experiments/goal5848_strong_baseline/contracts.py:1175
[cross-builder]: /Users/rl2025/rtdl_v4_restricted_python_design/scripts/goal5848_build_cross_generation_authority.py:80
[custody]: /Users/rl2025/rtdl_v4_restricted_python_design/KNOWN_STALE_CUSTODY_CHECKS.md
[root-readme]: /Users/rl2025/rtdl_v4_restricted_python_design/README.md
[paper-readme]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/README.md
[paper]: /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/main.tex
