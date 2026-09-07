# CGO 2027 文献证据与编译贡献：主 AI 执行指令

日期：2026-09-06 America/New_York。起草时读取的 HEAD：`50ca45521013f56b141402f4902a3af189b469f9`，工作树干净。

依据：用户已指定本审查为 lead，并于本轮要求“给主 ai 写清楚这些行动”。用户明确的优先级是：先从已有成果的论文中取得作者自己说明的能力与保证边界，再回答 RTDL 对 CGO 的编译研究贡献。文献已经足够支持的差异，不要求追加对手实战。

**主 AI 现在执行 N0–N5，交付实际论证、修改后的论文和执行报告。不要用另一份宏观计划、接受指令的回复或重复询问是否开始代替执行。本文规定工作与验收，不预先宣布新颖性成立。**

## 1. 与既有整改、冻结和复审的关系

本文件是新增的新颖性论证执行入口，继承 [Post-Goal5851 统一执行指令](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/lead_execution_directive_post_goal5851_20260906.md)。仅在本轮工作优先级、文献取证方法及贡献论证上补充要求，不撤销 R0–R8 的科学范围、验收与授权边界。

- R0–R3、R5 已有关闭记录；不重新实施四项旧计划修正，不重开性能优化。
- 当前作者整改候选 P′ 为 `818c2ed284cde8acae9a09b531b8bfed3bf925ee`，PDF SHA-256 为 `9bce71368ff0398efbc0d24685a80939fc691288663074ebf72ec9b20619013b`。它仍有零份独立接受意见。本文不是对 P′ 的复审结论。
- M 保持 `d653fe4ad170c5b51fee309d653c9565944dcf2e`；E 保持 `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`；F2 保持 `9771facece4ccd807e26c15b21892b9d0a701d32`。
- 本轮只做一级文献检索与阅读、已有源码和证据的只读追溯、论文／参考文献／说明文档修改，以及运行已提交工具进行构建、封包和验证。不修改生产、编译器、native、测试、实验、workload、arm、timer、estimator、threshold 或 F2 工具；不新增 GPU 实验，不安装和移植对手系统。
- `2026-09-08 00:00 America/New_York` 硬冻结不变。本文不授权任何新的可执行修改，包括嵌入文档或临时目录的程序。证据不够时缩小主张，不能改代码后沿用 M 的结果。
- 新颖性整改产生新的 PDF 字节，就建立新的文稿候选 P″（以实际 commit/tree/hash 为准），并在最终 R7 复审中使用新字节。旧 P/P′ 的报告和请求保留为历史，不改名冒充新版本审查。
- 不改变发送论文、上传或正式投稿的既有授权边界。

本轮执行目录固定为：

`/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/post_goal5851_submission_remediation_20260906/novelty/`

## 2. 本轮必须回答的两个问题

**问题 A：已有工作的实际保证，是否覆盖我们宣称接管的具体义务？**

不能把“对手可以实现应用算法”“对手自动生成 RT 管线”“对手保证某项跨阶段关系”混为一谈。本文要比较第三类问题，同时准确承认前两类能力。不能用语言表达能力差异或手写代码行数代替保证差异。

**问题 B：接管这些义务的表示和方法，对编译研究新增了什么？**

“已有工作没有承诺 Q”只支持问题定位；RTDL 实现了 Q，也不自动证明方法新颖。必须说明新增的编译对象、跨表示关系或实现方法，和已有组件、接口、类型、链接及运行时检查研究之间的实质差异。

暂用以下核心 thesis 组织论证，完成 N1–N3 后据证据修订：

> RTDL 将有限 RT 路线中分散于回调、物理表示和运行时的协议义务组织为一个共同接受编译与准入检查的单元，并将这些约束连接到生成接口、装载身份和执行发布条件。

“共同接受检查的协议单元”不意味着 canonical plan 可以直接执行，也不意味着从任意协议图自动综合正确 lowerer。具体拓扑 lowerer 和 wrapper 的信任边界必须写在同一论证中。

## 3. N0：建立真实执行入口

先阅读当前 `STATUS.json`、`CLAIM_LEDGER.json`、`PROTOCOL_SCOPE_ADJUDICATION.md`、`R7_PPRIME_FINAL_BYTES_REVIEW_REQUEST.md` 和 P′ 的整改报告，再读当前 `paper/cgo2027/main.tex` 与 `references.bib`。这些文件均在项目根或既有整改目录下。

创建本轮 `EXECUTION_REPORT.md`，记录：实际开始时间、HEAD/dirty 状态、上述文件的身份、M/E/F2/P′ 身份、N0–N5 状态，以及每个交付文件的唯一编辑者。主 AI 独占正文和 bibliography；助手可以分工取证和审阅，不并发编辑正文。

在既有 `STATUS.json` 中追加本轮工作入口和真实 pending 状态，不覆写历史 R-stage 结论。对其记录的当前文件 hash 在实际修改后更新引用；原快照 hash 保留历史含义。`claim_authorized` 和独立审查计数不因作者完成整改而改变。

**N0 完成标准：** 主 AI 能从执行报告直接定位本轮输入、文件所有权及各项待办；没有把后续取证、改稿或复审预填为完成。

## 4. N1：交付作者声明的保证边界表

交付 `RELATED_WORK_BOUNDARIES.md`。它必须是逐命题证据表，并附来源卡和简短检索记录，不能只有相关工作散文。

### 4.1 覆盖范围

按以下三组覆盖最近工作；可以把相关版本放在同一来源卡中，但不能只挑最弱的 Python binding：

1. **RT 接口和构建管理：** PyOptiX、OWL；涉及具体低层义务时核查 OptiX、DXR 或 Vulkan 对应官方规范。
2. **更接近编译贡献的系统：** Shader Components 2017、Slang 2018 及相关当前 capabilities/reflection 文档，LuisaRender／LuisaCompute，Dr.Jit，CrossRT。检查 SlangPy、LuisaCompute 当前验证机制是否改变所拟比较；在查证前不把其存在或缺失写成结论。
3. **更接近方法的研究：** typestate、interface automata／session-style protocol、typed linking／FFI。优先阅读现有 bibliography 中被引用的原论文，并沿最接近工作的引用查找直接相关研究。

RT-core repurposing 论文另列为应用／算法背景。只有当它们确实提供与本研究相近的编程或编译抽象时才进入方法对照；不得把应用论文没有做通用编译器当作 RTDL 击败了它。综述用于发现候选，具体能力判断回到原论文或作者官方材料。

这是有限、可说明的最近工作调查，不要求穷尽一切文献。记录检索日期、查询词、选入／排除理由、已查版本与未解决候选。有限调查不能产生“所有现有努力均做不到”的结论。

优先把直接影响核心 Q 的少数最强近邻查深；其余工作给出有依据的相关性与能力说明即可。不要求每篇论文都提供负面陈述，不为凑数量延长调查，也不把背景工作强行做成竞争失败案例。

### 4.2 每条证据必须包含的字段

| 字段 | 要求 |
| --- | --- |
| ID／系统／版本 | 稳定 ID；论文年份和当前实现版本分开；动态文档记录访问日期和可获得的版本身份 |
| 精确命题 Q | 一次只写一项保证，例如字段语义来源一致性；不写笼统“整个协议安全” |
| 一级来源 | 作者论文、官方规范或作者维护文档；URL、PDF 印刷页与文件页、节号／锚点 |
| 原文及语境 | 短摘录，记录相邻段落位置；每个来源直接引用累计最多 25 个英文词 |
| 已有能力 | 明确承认该系统已有的类型、阶段、布局、资源或构建管理能力 |
| 证据类别 | AUTHOR_BOUNDARY／DOCUMENTED_CAPABILITY／DERIVED_INFERENCE／UNKNOWN |
| 可支持的结论 | 精确到来源限定的对象和版本；推断显式标注 |
| 不能支持的结论 | 防止把非目标、可选策略或论文沉默扩张为原则上不能实现 |
| RTDL 对应项 | N2 中的义务 ID、实际机制、证据和适用范围；尚未对上就写未建立 |
| 论文措辞 | 可保留的英文句子，及必须删除或收窄的原句 |

`AUTHOR_BOUNDARY` 只用于作者明确说明的非目标、保证限制或用户职责。`DOCUMENTED_CAPABILITY` 用于肯定能力；不能借它的有限描述推导排他性结论。基于材料的覆盖推断用 `DERIVED_INFERENCE`，找不到依据用 `UNKNOWN`。

### 4.3 已核查线索：可以从这里开始，不能直接扩张结论

| 来源 | 明确陈述或阅读位置 | 当前可支持的范围 |
| --- | --- | --- |
| [Slang 2018](https://graphics.cs.cmu.edu/projects/slang/he18_slang.pdf#page=9)，§5 | “Slang does not enforce any policy as to when a renderer performs the tasks supported by its API services.” | API 服务的执行时机由应用选择；不证明无生命周期检查 |
| [Slang Shader Cursors](https://shader-slang.org/docs/shader-cursors/)，Manually Bind Parameters 节 | 明确说明工具不规定应用的参数绑定策略；同文也介绍布局、反射与参数组织能力 | 支持职责划分，不能否定其 ABI／布局能力 |
| [OWL 作者 README](https://github.com/NVIDIA/OWL#a-simple-owl-example) | “the user also still has to set up the programs, create frame buffer and launch data” | 用户仍承担部分程序／launch 配置；不能说 OWL 不管理 SBT 或不能扩展检查 |
| [DXR 规范](https://microsoft.github.io/DirectX-Specs/d3d/Raytracing.html)，PAQ 的 Local working copy | “It is the responsibility of the developer to ensure that shaders honor the specified PAQs” | 特定 payload 访问义务仍由开发者承担；必须同时承认规范已有检查和警告，且核对 RTDL 是否覆盖同一 Q |
| [LuisaRender 2022](https://luisa-render.com/static/paper/paper.pdf)，§5.3.3、§6.1 | 自动资源依赖分析、OptiX pipeline／SBT／参数／launch 管理 | 这是必须保留的既有能力，禁止把自动管线管理当作 RTDL 独创 |
| [Dr.Jit 2022](https://d38rqfq1h7iukm.cloudfront.net/media/papers/Jakob2022DrJit.pdf#page=12)，§4.2 | 开发者仍需处理微分过程中的细节 | 该限制针对微分算法，不能挪用成 RTDL 协议保证的空缺证据 |
| [CrossRT v1](https://arxiv.org/pdf/2409.12617v1#page=24)，§6 | 作者说明用户最终仍会调试或修改生成代码；§3.7 讨论手工扩展 | 支持其手工扩展边界；不否定其 host/device 代码生成与分析能力 |

必须重新确认最终引用的版本和上下文。不能把 Slang 的“用户负责兼容性”截出来，同时删去其随后介绍 capability 检查的段落。旧论文的非目标不自动代表当前系统仍缺失同项能力。

### 4.4 纠正一条已有不成立的推理

[2026 RT-core 综述](https://arxiv.org/html/2603.28771v1)讨论的问题包括何时能通过 RT 映射获得计算收益。RTDL 当前并不自动发现盈利映射，因此不能拿这一空缺证明自己的方法新颖。综述没有讨论某种编译抽象，也不是该抽象不存在的证据。

在本轮执行报告中追加纠正，并修正当前稿件中受影响的句子；保留历史审查原件。尤其不得继续沿用 `review_goal5794_callback_protocol_ir_pyoptix_and_related_work_strategy_20260823.md` 中“把综述未列编程抽象当作肯定空缺证据”的旧建议。

**N1 完成标准：** 三组最近工作都有明确处理结果；所有拟写进论文的能力否定有范围匹配的证据或已撤下；文献足够时该项可以直接关闭。不得要求主 AI 为作者已明确限定的同一 Q 再跑一遍对手，也不得把 UNKNOWN 伪装成否定结果。

## 5. N2：交付一个贯穿例子和事实来源表

交付 `PROTOCOL_WITNESS_AND_DERIVATION.md`。优先采用当前稿件已有的 `u32 primitive_index`／`application item_id` 错配；如其历史执行证据无法取得，就明确降为说明性例子，不补造实战记录。

### 5.1 必须逐步展示

1. 应用期望：物理位置 0、1 对应应用 ID 10、20，输出应保留应用 ID。
2. 生产者、attribute slot、消费者与结果的对应；错误组合为什么能保留合法的机器类型和布局，却输出错误含义。
3. 一个相邻的正确组合；明确两者唯一相关变化，不能把完全不同程序作为控制。
4. RTDL 的声明来自哪里，目标描述实际读取什么对象，哪些字段来源由可信 contract 声明，在哪个实际入口比较；没有端到端源码拒绝证据时明确缺失。
5. 从 typed callback effect 到 ABI 字段／effect tag，再到 wrapper 状态检查和硬件操作的一条短 lowering 链。优先摘录实际代码；伪代码必须标明，不写成已经执行的程序。

### 5.2 为每项关键事实制作来源表

字段至少是：义务 ID、声明值及来源、目标侧提取函数、该函数实际读取的对象、比较点、失败行为、可信前提、已有正／负证据及身份、未覆盖情况。

以下是只读追溯入口，正式报告须核对实际文件／commit，不能只抄行号：

- `src/rtdsl/v4_callback_lifecycle.py`：`_compiled_role_effects`、`_declared_attribute_ownership`、`_compiled_attribute_ownership`、`_compiled_protocol_facts`、`_materialized_protocol_contract_decision`。
- `src/rtdsl/v4_protocol_contract.py`：声明／投影的规范化和逐项比较。
- `src/rtdsl/v4_callback_ir.py`、`v4_callback_abi.py`、`v4_callback_numba_codegen.py`、`v4_callback_optix_wrapper_codegen.py`：IR 验证到实际代码生成与执行检查。

必须区分四种来源：编译器从程序结构导出；用户／provider 声明；固定拓扑规则；身份哈希。固定 attr0 的语义名字不是自动推断应用含义。目标事实来自同一编译器的另一表示，只能叫分开推导，不能称两个独立信任根。对同一对象复制后再比较，不能当作独立正确性验证。

对 executable identity 必须说明绑定了哪些实际字节、在哪里检查；哈希相等只说明身份一致，不证明语义正确。检查点还必须按源码区分生成／装载／launch 前、公开返回前、公开返回后 worker oracle，不能把实验 oracle 写成所有调用的编译器保证。

### 5.3 三种证据分开登记

| 证据 | 能说明什么 | 不能替代什么 |
| --- | --- | --- |
| 声明／投影字段 mutation 被拒绝 | 指定检查对该不一致敏感 | 真实源程序经过公共编译入口被拒绝 |
| 已有真实源程序经公共入口被拒绝 | 该具体前端到拒绝点的路径生效 | 对任意程序成立的正确性定理 |
| 既有对照执行得到错误输出 | 特定程序、版本和输入上的失败见证 | 缺陷普遍性、其他系统原则上无法处理 |

每格提供已有文件、commit／hash 和结果；不存在或无法读取就写明，不把旧报告摘要升级成此次独立重现。对不能独立核实的历史 PyOptiX／OWL 执行结果，主文撤下未经支持的“已执行”措辞，或在证据等级和可得性允许的精确范围内表述。

**N2 完成标准：** 读者能看清“要求 → 表示 → 目标事实 → 拒绝点”中每个已建立或缺失的环节，并能辨认每个信任前提；原文、推断、说明性例子、历史执行和本轮核查不混淆。如果只能追到可信 contract／projection 的一致性，以准确披露该边界、缺口及相应 claim 降级作为完成，不要求补出源程序到拒绝的实证。不得用新增测试或新 GPU 实战补齐本轮缺口。

## 6. N3：交付 CGO 编译贡献论证

交付 `CGO_CONTRIBUTION_ARGUMENT.md`。开头用一页左右给出可供论文直接采用的论证，再附必要的比较表和审稿质疑答复。

### 6.1 贡献分层

以“一项核心设计贡献＋实现方法＋有限验证证据”为初始组织方式，最终数量服从证据。

| 候选内容 | 初始定位 | 必须证明或承认的内容 |
| --- | --- | --- |
| 跨角色、跨表示协议作为共同准入单元 | 待论证的核心方法贡献 | 新增哪些关系、为何需要共同表示、与最近组件／接口／链接工作的增量 |
| 受限 callback 返回 typed effect，由受控拓扑骨架执行硬件操作 | 实现该设计的方法 | 真实程序转换和权限边界；专用 lowerer／wrapper 留在 TCB |
| 角色检查、ABI 展平、哈希、状态机、模板生成 | 采用的既有技术 | 逐项明确，不分别包装成原创发明 |
| 冻结核心后的扩展、有限 checker、mutation、性能和 artifact | 可行性与可信度证据 | 各自有限范围；不能替代新颖性论证 |

必须回答：**去掉 RT 名称后，论文给编译研究留下了什么可以复用的表示、设计认识或方法？** 不能只说“做成统一系统”或“检查了五种事情”。同时不要求证明这种方法已经跨后端实证通用；超出 RT 的迁移只能按已证明范围写成设计启示。

### 6.2 必须正面回答的审稿问题

1. 现有局部类型、capability 和布局检查已经做了什么？N2 的错误关系具体落在哪个未由这些既有保证推出的部分？
2. typestate、interface automata 或 session-style 方法可以表示哪些部分？RTDL 做出了什么特定建模或实现选择？不要声称 typestate 只能管一个对象。
3. 为什么不只是给 OWL／Slang 或普通 wrapper 增加几个断言？共同协议表示和 lowering 提供了什么实际价值？若当前实现只能证明特定 wrapper 的配置一致性，就据此收窄贡献。
4. 与 typed linking／FFI 的关系是什么？哪些语义／物理信息在已有边界里已能表达，RTDL 额外关联了哪些对象？哈希检查本身新增了什么、又没有新增什么？
5. 它是新的通用分析算法或类型定理吗？若不是，明确把新意放在可证实的设计／方法层，不能用数学记号让读者误以为已有 soundness theorem。
6. “先声明语义名字、再比较语义名字”是否循环自证？用 N2 事实来源表回答；目标侧事实不支持更强结论时必须降级。

**不要求证明通用形式体系或普通程序原则上不可能实现等价机制。** 要求说明已有研究已解决什么、直接采用后还需要做什么，以及 RTDL 的具体增量是否有研究价值。只凭对手作者将某项责任留给应用，不能跳过这一论证。

### 6.3 保留与降级规则

- 有具体方法增量且当前实现和证据支持：保留相应有边界的核心贡献；不自动增加“首次／唯一”字样。
- 只证明具体领域中的系统整合和实现：按系统设计／实现／经验贡献如实写作，说明价值；不能据此自行更换投稿类别。
- 关键差异仍未建立：相关独占性主张删除或保持内部 pending；继续完成其他独立工作，向 lead 报告缺口。研究结论不利也是有效执行结果。

**N3 完成标准：** 每项保留贡献能连到 N1 的最近工作比较和 N2 的实际机制；六个问题都有有依据的回答。不能以测试数量多、投入时间长或 prepared 性能好作为方法新颖性的替代证据。

## 7. N4：落实到论文、引用和 claim ledger

主 AI 在 N1–N3 的结论形成后直接修改论文，不停在备忘录阶段。

| 位置 | 必须完成的改动 |
| --- | --- |
| Abstract／Introduction | 审核“现有 Python 接口不建立整个 admitted execution”等否定句的证据；把问题、方法和有限范围写清楚 |
| Contributions | 按 N3 的实际结论重组，区分设计、实现和证据；不强凑独立创新数量 |
| Protocol Mismatch | 使用 N2 的贯穿例子；“executed”“wrong output”“before launch”逐词核对证据 |
| Design／lowering | 呈现声明与目标事实来源、真实程序转换、拒绝／发布边界和 TCB；避免重复宏观架构描述 |
| Related Work | 用 N1 的保证和编译单元对照替换空泛的“我们关注不同”；明确承认强近邻已有能力 |
| Generality／Threats／Conclusion | 与限定后的贡献一致；迁移启示与已实证范围分开 |
| Bibliography | 校正标题、作者、年份、版本、页码和链接；动态官方文档不得冒充同行评审论文 |

交付 `MANUSCRIPT_CHANGE_MAP.md`：逐项记录原句、新句、N1/N2/N3 证据 ID、修改文件及位置、对应 claim ID、最终 PDF 页码。对贡献和相关工作增加稳定 claim ID，更新现有 `CLAIM_LEDGER.json`；新增项目仍保持未获最终审查授权。

不得为腾出版面删去既有强制披露：原逐次 detailed receipt 要求未履行；4,096 次 timed A 与 32 份独立诊断 receipt 的区别；prepared timer 与 worker oracle 顺序；post-import 全部不利且最差 block `2.377129x`；相对 E 的 entry 约 8%–22%、post-import 约 16%–31% 回退及其 post hoc/non-gating 性质；生命周期／导入混淆；native-fork、provider 双重失败和有限 checker 的范围；零独立人类 authoring 证据。

Goal5838 的一次冻结核心扩展不能变成任意拓扑泛化，约 2,635 行拓扑专用代码及相关编译器修改成本必须保留。Goal5840 的有限结构检查不能变成语义正确性证明。证据 artifact 的 offline recount 不等于可安装产品或 GPU rerun。

**N4 完成标准：** 内部备忘录中的修正已经出现在实际稿件中；每个重要否定与贡献句可追溯；旧不利证据和 R7 的已知问题没有因重写重新出现。

## 8. N5：生成新候选，提交实际执行回报和复审材料

1. 用已有已提交的构建工具生成实际 PDF，检查全部页面、引用、版面、匿名及主张范围；不添加新程序来制造验收。
2. 记录 P″ 的实际 commit/tree、正文／bibliography／PDF／source bundle hashes。使用明确的新输出位置或保全旧版本，不能覆盖后失去 P′ 的可恢复身份。
3. F2 evidence artifact 保持原 SHA-256 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8`；核查身份并沿用既有成功重放记录，不无故重跑完整性能或原始实验。若重新封包或引用了不同包，按既有规则验证真实配对，不能沿用旧 hash。
4. 文稿新增加的协议见证不在九成员 evidence artifact 内时，明确其证据位置和可得性；不能让读者误以为该包重现了新颖性或所有协议实验。不能为此擅改 F2 模板或打包程序。
5. 更新本轮 `EXECUTION_REPORT.md`、既有 `STATUS.json` 和 append-only validation log，列出实际完成／未完成事项及证据。新的 final-bytes review request 必须绑定 P″，并映射仍适用的旧 finding。
6. 将候选交回既有 R7/R8 流程。作者自查、助手分工或本文的发出都不算两份独立最终审查；不能自行写为 consensus、accepted 或 submitted。

执行报告必须包含以下表格，填写事实，不写“详见代码”代替定位：

| 项目 | 状态 | 交付文件／身份 | 关键结论与证据 | 剩余缺口及受影响 claim |
| --- | --- | --- | --- | --- |
| N0 输入与状态 | 实填 | 实填 | 实填 | 实填 |
| N1 最近工作边界 | 实填 | 实填 | 实填 | 实填 |
| N2 贯穿例子与来源 | 实填 | 实填 | 实填 | 实填 |
| N3 CGO 贡献论证 | 实填 | 实填 | 实填 | 实填 |
| N4 实际稿件修改 | 实填 | 实填 | 实填 | 实填 |
| N5 字节交付与复审 | 实填 | 实填 | 实填 | 实填 |

报告最后逐条回答：目前留下哪几项贡献；哪些已有工作边界由作者原文直接支持；哪些比较仍属推断或未知；CGO 方法增量是什么；删除了哪些过强主张；新 PDF 和包是什么身份；还欠哪些独立复审。

**执行顺序：N0 → N1/N2 并行 → N3 汇合 → N4 改稿 → N5 交付。** 文献与源码反证随时修正结论。只有受影响的 claim 缺证时保持该项 pending，其余工作继续。主 AI 的下一份回复应是这一执行报告及真实交付文件，而不是再次征求开始许可。
