# 论文三问：具体写法与收口验收

日期：2026-09-07 America/New_York。

依据：用户要求落实“编译器额外知道什么，因此拒绝或生成了什么，相对最强已有方法新增在哪里”。本文件补充既有三天贡献指令，仅规定论证的最后收口，不重新开启工程、GPU 实验或已关闭整改。

读取的控制 HEAD：`8b4475893a7a4486fb89fa35f1ce2470fb2d13f4`。新稿标题已经是 `Result-Route Contracts for Restricted Python on RT Hardware`，已加入 Table 1、W1/W2/W3 和 RQ1–RQ4。下述检查针对这些真实内容；不能把建议稿或本次阅读检查登记为新 PDF 的 R7 接受。

## 1. 当前判断

| 问题 | 现稿位置 | 当前判断 | 收口动作 |
| --- | --- | --- | --- |
| 编译器额外知道什么？ | main.tex 101–117、147–175、288–296 | 已有明确答案：固定 family 的结果要求决定额外的 effect／数据／失败规则。 | 强调其来源是已实现的显式 family 规则；不是自动推断应用意图。 |
| 因此拒绝或生成什么？ | 288–325、531–547 | 已有具体答案：relation effect 限制、triangle payload 后 ignore、精确 IR 控制特化选择。 | 把每个决定与产生它的契约放在相邻句子；证据分别标明 source trace／component test／既有 GPU 观察。 |
| 相对最强方法新增在哪里？ | 732–762 | 已承认强先例；“谓词不同”仍不能独立承担方法增量。 | 用一句话说明实现的连接，用一句话说明牺牲的通用性和证据能评价的范围。不要扩大竞品列表或借 source silence 宣告胜利。 |

已有内容满足同一含义时保留原文，不要求逐字套用本文件，不新增平行理论或第二套贡献名称。

## 2. 用一个清楚的因果链组织例子

统一解释顺序：**结果要求 → 显式规则 → 编译决定 → 可核查证据 → 保证边界**。

用“两次符合条件的命中”作为小型说明场景即可；必须标注为 illustrative。完整关系与 triangle count 是两个实际 family 的分别实例化，不能伪装成同一已执行程序只改一个契约就运行两种输出。

### A. 拒绝：完整关系的结果义务

1. 结果要求：当前固定关系路线应返回应有的规范行，容量失败不得把部分关系当成正常结果发布。
2. 已有能力：角色规则允许 any-hit 使用 continue、ignore、terminate。
3. 额外规则：当前 bounded-relation family 收集 return effects，并只接受规定的 `ACCEPT_CONTINUE` 集合。
4. 决定：角色合法不足以使该路线被接受；不受支持的 effect 被 family verifier 拒绝。
5. 证据：`src/rtdsl/v4_callback_ir.py:572`、`src/rtdsl/v4_bounded_relation.py:241`。当前是源码追溯；capacity 另有已运行的 CPU 检查。不能写成已经执行完整坏程序／GPU 反例，也不能把拒绝 IGNORE 推广为所有枚举算法都不得过滤。

### B. 生成：triangle all-hit 的硬件解释

1. 结果要求：保留应计入的命中贡献。
2. 逻辑动作：接受一个事件并继续。
3. 目标实现：检查并更新 payload，再调用 `optixIgnoreIntersection()`；结合 single-any-hit delivery 设置及 checked overflow。
4. 证据：`v4_triangle_reduction_optix_wrapper_codegen.py:418`、517，native triangle GAS 1921。已存在于通用 wrapper 和实测特化路径；没有新增 GPU 执行。
5. 归属：OptiX 的动作、调用顺序和防重复技巧已有。引用 [NVIDIA 作者解释](https://forums.developer.nvidia.com/t/confusion-about-optixignoreintersection/301806)，不把硬件技巧包装为 RTDL 发明。RTDL 要呈现其与结果契约和逻辑 effect 的实际连接。

### C. 特化边界：程序改变时生成决定改变

1. 已有测试将 `payload.count + 1` 改为 `+2`；角色形状不变，前端仍接受。
2. IR 身份改变，生成器不再选固定 count intrinsic，回到通用 leaf 路径。
3. 证据：`tests/goal5759_v4_triangle_reduction_target_test.py:72` 已有 source-to-wrapper 检查及此前重放记录。
4. 结论：具体特化的选择边界可检查。该测试不证明 GPU 等价、任意语义分析或新优化算法。不能因为使用 hash 就说编译器理解了所有等价程序。

这三个例子分别承担“拒绝、生成、特化选择”，共同支撑一个领域设计。它们不是三个基础性突破。

### D. 给出通用路径与实测特化之间的语义连接

正文应让读者看见同一标准 count 行为的两种实现：通用路径由叶函数形成 increment-and-continue 效果，wrapper 检查后写 payload 并 ignore；标准特化把该已知行为直接放进生成的入口，保留适用 overflow／失败检查。精确 IR guard 只负责选择已知程序；可信 lowerer 负责兑现其结果义务。对齐这两条路径的实际代码动作，不能把“哈希相同”当作二者等价的证明。

必要时在特化段中加入：

> For the exact standard count program, the specialized entry implements the known increment-and-continue behavior directly, while the general path obtains it through the leaf ABI and wrapper. The IR guard selects that trusted implementation; it does not establish semantic equivalence, and both the recognizer and the specialized lowering remain in the TCB.

这两句只解释已实现的可信分工，不主张自动 partial evaluation 或机械验证。已有正文若已清楚表达同一关系，无需重复增加段落。

## 3. 第三问采用“先例—具体取舍—证据”的比较

[Slang capabilities](https://docs.shader-slang.org/en/stable/external/slang/docs/user-guide/05-capabilities.html) 已表达并检查 stage／target／API／hardware 条件，包括调用及接口关系。PCC 已建立消费者策略与执行前证明验证。对这些已有内容直接承认。

然后说明 RTDL 采用的具体取舍：通过有限、显式的 family 规则，把结果要求连接到 effect admission、可信 lowering 与接口发布检查；为此保留大量可信拓扑实现并限制可接受程序。现有证据评价这个实现是否存在、哪些有限检查生效、一次扩展复用了什么，以及确切路径的成本。

必要时在 related work 的 Slang 比较后加入以下两句，或用等义文字合并现有段落：

> The proposed contribution is the implemented connection from fixed result obligations to effect admission, trusted lowering, and publication checks, rather than the difference between guarantee predicates alone. This design uses explicit family rules and guarded specializations at the cost of restricted expressiveness and topology-specific trusted code; our evidence evaluates that implementation and its costs without establishing superiority over richer prior frameworks.

这段是设计增量的主张，不是新颖性的证明。最终论证必须让审稿人能判断该增量是否值得 CGO，而非要求接受作者的自我定性。如果近邻原文已有相同连接，应引用并重定位剩余贡献，不能换术语逃避比较。

## 4. 正文和证据的摆放

| 位置 | 读者必须取得的信息 | 完成标准 |
| --- | --- | --- |
| 摘要／引言 | 一句话身份；一个角色合法却不满足当前结果路线的例子；一个核心设计贡献。 | 不读内部材料也能说出额外约束改变了什么决定。 |
| 第 2 节／Table 1 | 上述三个例子的契约、决定、证据类别相邻。 | 每行都包含一个具体 reject／generate／select 动词及其条件。 |
| 第 3 节 | 规则来自哪里、在哪里执行、哪些 lowering 仍受信任。 | 不把 family 规则写成自动语义推导；不把 identity equality 写成正确性证明。 |
| 评估 | RQ1 对应规则，RQ2 对应特化边界，RQ3 对应有限复用及新增代码，RQ4 对应确切路径成本。 | 每项结论能回指已有证据，分母和证据级别不互相借用。 |
| Related work | 最强近邻的已知保证、RTDL 的具体取舍、未建立的优势。 | 无“没写同一句话，所以不能做／所以首创”的推理。 |
| 最终 PDF | 上述论证、来源、性能和不利观察均保留且可读。 | 新 PDF 独立完成精确字节审查；旧 P‴ 接受票不转移。 |

不增加硬件、工作负载、基线或新实验；不再次运行已经充分通过且输入未变的检查。缺少证据时降低句子的证据等级或删除该句。

## 5. 读者检查与停止条件

让未读内部论证的读者仅凭摘要、引言、Table 1、设计和 related work 回答三问，并指出正文依据。此检查只判断可理解性，不能判断文献是否穷尽、不能证明新颖性，也不计为 R7 接受票。

本轮实际完成一次无对话历史的限域阅读检查。读者能够给出三问的核心回答，且未把近邻 UNKNOWN 说成无法实现；其指出的最大断点是“已检查的 effects 如何连接到绕过通用 tag 检查的 exact-IR 特化”。上文 D 给出最小解释文本。该读者对语义 mutation 的摘要还省略了 overlap-disabled 限定，因此不能把这次检查记成所有边界理解均已通过；正文继续保留该条件，后续复述亦须准确。

完成标准是三问均有准确且可定位的回答；读者明确知道：规则是固定 family 的、OptiX 技巧有先例、特化测试不是 GPU 等价、近邻系统的能力不因未声明而被否定。随后检查最强先例的比较是否与原文一致，以及主张是否超出已有证据。

若上述条件满足，停止为“措辞更强”继续改稿，进入最终 R7/R8。若第三问只能回答“用了不同名字／多加几项检查”，只收口该段的具体设计取舍，或把主张收窄为有限系统设计／实施经验；不借截止期制造根本突破。

本文不修改主 AI 正文或控制状态。主 AI 负责按现稿缺口合并最小必要改动；lead 负责检查论证与证据一致性，以及新最终字节的后续审核。
