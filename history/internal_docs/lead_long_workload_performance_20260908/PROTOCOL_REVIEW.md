# 两天大工作量性能协议独立审查

日期：2026-09-08，America/New_York。审查者：lead 的独立协议协作者。

**结论：现工具不能原样执行新要求；最小可执行目标是四个旧 operation units 的修复前后对照，加一个真实的大整图任务。建议采用 240 个 fresh workers 的核心矩阵。性能目标是验收条件，不是准许报道的筛选条件。**

本文件是供主 AI 实现和注册的具体协议，不是已完成预注册、GPU 结果或提交授权。按本轮新增用户授权，必要实现和新实验可以继续；旧冻结不阻止本项 successor。旧 M/E/F2、c5c8be48b 及更早失败和全部证据保持不变，不改原 PREREGISTRATION，不混旧样本。只新增本审查文档；没有修改实验、执行项目代码或使用 GPU。

## 1. 独立只读检查到的实际支持与缺口

读取时 HEAD 为 2aad4f022386811789a56091d824bd41733ba4f6。下述源码是该工作树读取快照；运行新事务必须另锁新 source/worker/config/recount 身份。

| 现有事实 | 精确出处 | 新协议需要什么 |
| --- | --- | --- |
| complete 在共享 loader 完成后才开始；first_result 在 prepare 后开始；prepared 每次单独执行并计时 | scripts/v4_paper_apps_pyoptix_worker.py:571–613 | 新建 domain_full 与 prepared_public 标识和 schema；不能只改旧端点显示名称 |
| Particle loader 读取已生成的三角面、front/back 关系和查询 NPY | experiments/v4_paper_apps_pyoptix/inputs.py:26–67 | domain_full 要覆盖领域网格到 RT 表示的必要转换，不能从这些缓存开始冒称完整领域流程 |
| Graph loader 已建立分段 RT-Graph CSR；worker 不传 dataset 参数，硬用 com-dblp 默认值 | inputs.py:70–103；worker.py:283–290 | 新输入的 dataset、原始图身份、oracle、分段规则必须进入 config；方向化、去重、CSR 和几何构造各归属明确 |
| LibRTS loader 读取 11,544,398 行索引缓存，解析 100,000 条 WKT 查询；索引缓存构造没有计入 | inputs.py:167–209；scripts/goal5776_real_scale_inventory.py:103–106 | 完整端点不能从 NPZ 索引缓存出发；查询解析也不能暗放 timer 外 |
| controller/recount 固定四 units、三个旧 endpoints、两臂；config 固定 prepared 32/4/4/4 和一次 warmup | controller.py:30–36,450–457；make_config.py:248–258；recount.py:92–118 | 新矩阵、两 endpoints、三臂、输入版本和验收目标均需实际纳入新 schema 和独立 recount |
| 旧 PASS 只判断正确性/身份与完整记录；performance_threshold_present 为 false | controller.py:515–542；recount.py:344–353；旧 CONFIG | 保留旧意义；新报告分开 evidence_valid 与 performance_target_met，不能把旧 PASS 改写为性能通过 |
| timeout 是 controller CLI，默认 7200 秒，不在旧 config 内 | controller.py:95–126,580；旧 CONFIG | 冻结每单元/端点 timeout 与总预算；不能 240 个 worker 各留两小时 |
| worker 在内存保存 samples；后续调用或 close 异常时 main 的 FAIL 对象没有带回先前局部样本 | worker.py:579–607,673–688 | 每调用持久化原始计时/状态；失败不能抹掉此前已观察数据 |
| controller 主要在末尾生成完整 summary；超时分支仅接收字符串 stdout | controller.py:113–119,494–510,544–570 | worker zero 前写不可变完整计划，逐 worker/call 写 journal；保留 bytes/str 输出及超时/缺失 JSON 状态 |

现有强 C 是公共 PyOptiX 加手写 CUDA/PTX，不能改称 Numba 基线。已有 exact-output dry-run、交替顺序、输入/源码/环境绑定、无重试替换、独立 recount 的思想应保留，但旧 192-worker schema 不证明新事务完整。

## 2. 问题、臂和两个端点

问题：在相同应用算法、领域输入、数值/输出契约和 GPU 上，修复后的公共 V4 能否把完整领域流程及真实可复用执行都控制在强 PyOptiX 的合理开销范围内？真实大任务是否也成立？

三臂：A0 是 c5c8be48b 的修复前 V4 实现；A1 是本轮冻结的修复后 V4；C 是本轮单独审查并冻结的胜任公共 PyOptiX。A0 可以通过只改变数据注入/计时的外部 harness 接入新输入，但不得修改其执行器、缓存、编译路线或算法。每个臂绑定各自源码/库/生成物和共同 harness 身份；不要把三套代码装进一个含糊的 source_commit 字段。

### 2.1 domain_full：从内存领域输入到完整公共输出

启动状态是 fresh process，未 import 实现特有模块、未创建 CUDA context、未 prepare scene/query。允许在 timer 外读取并核验相同的原始文件字节；磁盘读取本身不计时，不能将读取时顺便发生的领域解析或编码也排除。计时从共同的内存原始领域表示开始，包含解析、必要的领域编码、几何/索引/CSR 构造、实现 imports/context、prepare、全部应用轮次、同步、输出物化，以及约定的 method-owned close。

允许作为输入的最低层状态必须逐 app 精确登记：

| App/unit | 安全端点名称和输入起点 | 必须计入 |
| --- | --- | --- |
| Particle | 原始四面体网格与固定粒子状态上的完整单次 cell-transition 流程 | 需要的类型转换、面去重/方向、邻接/front/back、ray 编码、GAS、所有查询和完整有序 U32x3 输出；不称 50,000 步 tracking |
| RT-2A1 | 原始图边输入到完整 checked-U64 triangle count | 图解析、去重/方向化、CSR、所有确定性分段几何和查询、各段遍历/归约、最终总数；不能只取前几段 |
| LibRTS point/range | 原始空间几何与领域查询到完整 checked-U64 containment count | 几何解析/MBR 或索引列构造、查询解析/编码、GAS、查询、设备归约及 scalar；不称输出完整 join relation |

共用预处理实现是允许的，但每个 fresh arm 必须在自己的完整计时内执行，不能由 controller 先做一次后同时免费赠送给两臂。旧输入的新领域解码/编码链必须重建旧执行输入的精确内容和身份；若不能重建，就明确不是原输入的直接修复前后对照。预期 oracle 可独立预先计算，不向执行器提供答案作为计算捷径。

**代码构建策略必须在观察 A1 性能前冻结。** 强 C 不得被人为降级：既有可复用 PTX、正常设备归约、pipeline/GAS/查询储存复用应保留。双方有相同的只读代码预编译许可，且不许预创建 scene/GAS/查询来冒充代码编译。逐臂登记实际的 task-code readiness；若 A 的普通公共 API 仍在 prepare 内编译，计入 domain_full 并与 C 的预编译状态在同一表披露，不能称代码状态相同或把差异归因于语言本身。若另要证明共同 source-ready 构建成本，单独注册双方从代码源开始的诊断；不能为了让完整比值接近一而强迫 C 反复编译。原 C 预编译、V4 Particle/Graph 编译计时内的旧结果继续保留。

### 2.2 prepared_public：保留合法准备状态后的一个公共应用执行

timer 前双方完成允许的静态准备和一次固定 warmup。timer 内恰好一次公共 application action，从调用到完整结果可消费；所有动态处理、实际同步、D2H、公共接口原有检查均在内。

登记可复用对象：代码/模块/pipeline/SBT、静态 geometry/GAS 或有界分段策略、query columns、输出/状态/归约 scratch，以及其容量和所有权。没有 meaningful public prepared 接口就标 N/A；禁止把私有 native launch 冒充公共执行。静态事实可以被缓存，输出不得被 memoize。每次必须有真正遍历和新结果形成的证据。

Particle 仍返回整批有序 U32x3；RT-2A1 一次 action 执行整个图的全部分段并返回一总数；LibRTS 一次 action 消费全部注册查询并返回一 checked scalar。图分段是算法/内存策略，不是 benchmark 重复；每段的不同数据身份及最终覆盖数必须可核。

两端点使用相同公共输出/检查政策。不能删除 V4 正常的验证以加速。独立重型 oracle 可以在 timer 后，但这必须新注册、对三臂一致，并保留逐次验证记录；不得再将其称为 first correct result。建议新主端点继续保留旧 worker 的同步状态、输出 oracle 比较、digest 与 compact evidence projection，从而减少口径变化。

## 3. 一秒门槛：只按强 C 选真实工作，不按 A 输赢选

一秒定义为 **强 C 的一个完整 prepared_public action 的直接 wall time 至少 1.000 秒**。不是若干样本的和，不是 warmup/prepare/import/编译，不是循环同一 execute 的总时长，也不是 first_result 的懒初始化。一次 action 可以含真实多轮/分段算法，必须处理不同且有语义必要的数据，最后产生完整目标输出。

候选选择阶段先提交候选顺序、来源/规模、生成方式和 seed、输出契约、内存/时限和 C 实现身份；只执行 C 校准，不看 A0/A1 比值。对每个候选使用三个 fresh C processes，每个一次 warmup 加一次单独计时的完整 action，选三次均至少一秒的最小候选。建议校准预留余量但不得事后加上有利 A 的选择标准。保留全部候选，包括快于一秒、OOM、超时及不正确的候选。

选择后冻结确切输入与独立 oracle，再做三臂正确性 dry-run。A 的失败意味着该候选对 A 失败，不得换一个 A 表现更好的输入。若强 C 后续被优化，必须用新 C 重新进行 C-only 资格校准；不得留着变弱的旧 C 来保住一秒。

最小自然大输入优先级是：com-dblp 作为旧 anchor；然后 cit-Patents（已登记 oracle 7,515,023）；再 soc-LiveJournal1（285,730,264）。出处是 scripts/goal5776_real_scale_runtime_inputs.py:57–66。运行前仍须独立核原始输入文件/来源/哈希与 oracle，不把旧登记或本地没有原始数据的 compact archive 当数据已到位。保持 RT-2A1、完整图、既定分段规则和 checked-U64 输出。

Particle 及 LibRTS 的大输入不是现成能力：Particle 生成器 scripts/goal5776_prepare_particle_mesh.py:137–143 用 resize 重复 cell，weights 仅按四种位置循环；只增 AUTHOR_QUERY_COUNT 会产生重复点，不能充当新大任务。LibRTS loader 硬编码 100,000 条查询且没有在本次只读检查中找到已验证的大查询生成器。不得复制同一查询块数千次。新增真实粒子/空间查询必须有独立生成来源或可信种子、实际不同查询、分布/重叠/命中密度说明、完整 oracle、内存预算；未实现就报告缺项。改变选择性来放大工作时，须称新的选择性 workload，不能说只是原任务等比例扩容。

正式新大输入的八个 C block 中，每个 block 的三次单次样本中位数都须达到一秒；另外报告全部逐次样本和最小值。任何 block 不到一秒，资格标为未建立，不删除该 block、增加 repetitions、取时长总和或换输入；八块性能结果仍照实保留。性能达标和一秒资格是两个独立布尔值。

## 4. 最小矩阵与精确样本数

核心矩阵用一个 GPU、一个冻结 A1/C 和原 A0：

| 数据单元 | 输入 | 臂 | 端点 | blocks | fresh workers |
| --- | --- | --- | --- | ---: | ---: |
| Particle、com-dblp RT-2A1、LibRTS point、LibRTS range | 四个旧输入身份、完整旧输出 | A0/A1/C | domain_full、prepared_public | 各 8 | 192 |
| RT-2A1 | 上述 C-only 规则选出的一个真实大图 | A0/A1/C | 同上 | 各 8 | 48 |
| 合计 | 五个 data units | 三臂 | 两端点 | 80 个三臂 blocks | **240** |

每个三臂 block 的 C 只跑一次，同时形成 A0/C、A1/C 与 A1/A0，三者不是独立重复。预先固定八次三臂顺序，例如 A0,A1,C；C,A1,A0；A1,C,A0；A0,C,A1；C,A0,A1；A1,A0,C；A0,A1,C；C,A1,A0。A0/C、A1/C 各四次 A-first、四次 C-first；每臂均 fresh process，同一 GPU 串行，不能并行竞争。跨 unit/endpoint 的轮转日程也先冻结，避免全部旧数据集中在机器状态不同的一段时间。

domain_full 每 worker 一次、无 warmup。旧输入 prepared 每 worker 一次 warmup，Particle 32 次、另外三项各 4 次，保持原采样密度；新大图 prepared 一次 warmup、三次逐次计时。于是：120 个 domain_full 主样本；1,128 个 prepared 主样本；120 个不混入估计的 warmup；合计 1,248 个主样本，仍只有 80 个独立三臂 blocks。dry-run、校准和诊断另外编号，不计入正式统计。

若用户目标要求每一个 operation unit 都有独立的一秒大输入，则增加 Particle 和 LibRTS 两操作的大输入，完整矩阵为 384 workers；未建立的三行必须在覆盖分母中保留。核心 240-worker 成功最多支持“四个旧单元的修复与一个新大图”，不能把它写成所有三 apps 都完成一秒大工作量，更不能把原九 app 分母改成三。其余六 app 的缺基线/未执行状态继续存在。

## 5. 验收与防止大任务掩盖固定开销

每个 unit/input/endpoint，先按 worker 内样本中位数形成每 block 的 A1/C；主估计为八个配对 block 比值的中位数，worst 为八个 block 的最大比值。不能用独立全体 arm median 相除，也不把 32 个同进程样本当 32 个独立进程。

预注册验收：八个 blocks 正确、完整、有同一输入/源码/环境绑定，A1/C median <= 1.20，且每个 block <= 1.35。**这两个目标同时适用于旧输入与新大输入的两个端点。** 整体通过要求所有已注册核心 A1/C 单元通过；任何一项慢、错误、OOM、超时或未完成，整体目标没有完成。照常报道全部结果，不能将目标写成“低于门槛才报告”。

A0 是改进对照，不要求其通过 A1/C 性能门槛；如 A0 在新 harness/新大输入失败，完整保留失败，A1/C 仍可单独成立，但该行不能给出有完整八块的 A1/A0 改进量。

为防“只放大任务就掩盖原问题”：

- 四个旧输入必须原样保留；输出/精度/算法不得改变。缺旧输入复测或旧输入仍远慢，不能宣称旧性能债已解决。
- 在每个相同输入上同时给出 A0、A1、C 的绝对毫秒、A1/A0、A1/C、A1-C 绝对差额；旧与新输入不得跨规模计算修复 speedup。
- 同时要求 domain_full 与 prepared_public 达标；公共预处理或编译占据数秒而让 total ratio 接近一，不替代 prepared 达标。
- 另给 mutually exclusive 的领域编码/几何、代码编译、runtime/scene prepare、execute、close 诊断，以及 upload/download bytes、launch/segment 数、输出大小和缓存驻留对象。未直接计时的阶段标未测，不能从总量相减推断因果。
- A1 的真实修复应在相同旧输入显示差额下降或可追溯工作被删除/复用；若只有大输入比值改善，而相同输入 A1/A0 没有改善，只能称固定开销被摊薄。只靠两规模不能拟合可靠的普遍固定/线性成本定律。
- 不削弱 C：不加逐命中 Python continuation、无必要 D2H、重复编译/分配、不同输出义务或低效布局来制造通过。已有必要的强 C 优化保持开启，C 改动独立审查。

状态字段分开：evidence_valid、output_contract_passed、large_workload_qualified、performance_target_met、coverage_complete、same_input_improvement_observed。失败不是缺失值零时间；有限样本内达标不是总体最坏时延保证。

## 6. 成本、timeout/OOM 与两天排程

T0 是主 AI 确认新任务开始的记录时间，不把旧午夜冻结当新的 deadline。建议：T0–4h 检查 raw 数据/现有资源和测量合同；4–10h 完成 C-only 校准和输入冻结；并行实现通用修复；10–22h 完成公共路线与完整端点适配、正确性 dry-run、离线故障/重算检查并提交 source/config；22–40h 正式矩阵；40–48h 独立 recount、保管/不利行核查、报告和主 AI 自审。实际没完成就给失败/缺项，不为凑两天预填成功。

在所有 A0/A1 计时暴露前，按 C-only 校准记录计算每 unit/endpoint 的 common timeout：max(120 秒, 8 × 该 worker 计划的 C 端最慢校准 wall cost)，向上取整，最高 900 秒。prepared worker 成本包含 timer 外的 load/prepare、warmup、注册的全部独立 calls 和 close，不能拿单次 1 秒乘一个小系数直接当整进程时限。三臂同一 timeout；记录 CLI 与 config 一致性。

正式预算的可执行准入检查是 sum(注册 workers × 对应 timeout) 不超过 16 小时，另留两小时机器/打包缓冲。若超过，按预先基于 C 的资源条件判定核心计划在两天内不可保证，先报告不可行；不能看到 A 很慢后缩小输入、砍块、删旧输入或改时限。实际预算可低于 worst-case，但必须报告预计值与这个最坏上界。GPU 型号/UUID/显存、主机 RAM、磁盘预算及授权资源信息全部在 worker zero 前填写，不能使用猜测值。

OOM 准入依据预先的输入规模/布局估算与 C-only dry-run：建议峰值注册上限为可用 GPU/RAM 的 80%，具体 bytes 先固定。若 A 超过相同资源条件，这是 A 的失败，不能为了让它通过改查询、容量或 output。timeout/OOM 不是慢样本的删去理由，不给“仅成功样本”的通过率。基础设施失效可以中止整个事务并保留部分数据，新的重跑须新事务，不替换原 block；若物理环境损坏使后续 worker 不能运行，将余下计划标 NOT_RUN_INFRASTRUCTURE，不能算完成八块。

worker zero 前写全体计划、source/config/input hashes、order、timeout 和 expected sample counts。每 call 结束后、下一 call 之前 append 并 flush 原始 ns、状态、digest、紧凑证据和输出验证；纯保管写盘放在该 call timer 外，三臂一致；close 异常不抹掉已有计时。domain_full 只有一次输出，停止完整 timer 后落盘；异常路径也保留已形成的逐阶段/调用记录。controller 保存 exit/signal/OOM/timeout/完整 stdout+stderr（包括 bytes 输出），即使 worker JSON 不存在也有终态记录。超时清理整个 worker 进程组并确认无遗留 GPU/编译子进程，避免污染下一块；这不是重试。正常机器状态记录和最终 source-clean/config-unchanged 检查仍必需。

正式事务开始后任何实现、C 优化、输入、timer、repetition、warmup、oracle、估计器或门槛变化都产生新身份与完整新事务。旧/失败样本不池化，成功者不覆盖失败者。

## 7. 必要交付与不能声称什么

worker zero 前主 AI 要交付：明确批准的新 successor 范围；真实数据/生成器和全输出 oracle；C-only 候选日志与选择机械规则；A0/A1/C 物理路线/缓存/代码 readiness 表；两端点调用/计时边界；精确矩阵和样本数；共同 timeout/资源/成本预算；create-only journal 与独立 recount；源码、native/PTX、环境和配置哈希；三臂独立正确性 dry-run。需要的是这些具体对象，不能仅写“已注册”。

正式完成后交付所有候选/worker/错误日志、逐次计时、八个 block 的比值、全覆盖/失败清单、不同版本的同输入对照、独立重算和独立新附件；旧 F2 保持原字节。新论文/PDF 另走相应审查，不继承旧 byte acceptance。

即便全部数值通过，也不能声称：

1. 1.20/1.35 达标就是 V4 更快、与 PyOptiX 相等，或可保证未来最坏时延。
2. 选定一个 >=1 秒整图证明所有 apps/全部九项都可接受，或证明 Particle 全程 advection/LibRTS 完整 relation。
3. 大任务通过修复了仍失败的小任务，或比值下降证明固定开销已经删除。
4. 不同编译 readiness、物理 geometry/pipeline 路线、结果布局或缓存差异的总时间就是语言检查/Numba 的固有成本。
5. 单 GPU 结果就是跨硬件普遍性能；旧 M 两 GPU 数据不能替新 apps 提供复制。
6. 新输入、扩大查询、不同选择性或新 generator 仍是原历史 workload 字节/原协议成功。
7. 某正式 worker 失败后剩余成功样本可以重新定义性能人群；或丢失 receipt/原始计时仍算原注册完成。

最有实际价值的成功是：在相同旧输入上把真实公共流程和 prepared 的差额都压下来，同时在一个真实大任务上维持这个改进。若只能做后者，仍有规模条件下可用性的价值，但不能说已解决当前应用性能问题。

## 8. 审查快照哈希

| 读取对象 | SHA-256 |
| --- | --- |
| history/internal_docs/v4_paper_apps_pyoptix_20260907/PREREGISTRATION.md | 24029a7c238dddb941574ed315aeede279d53c15621f6a0602205a60b84b6f30 |
| evidence_c5c8be48b/CONFIG_c5c8be48b.json | 29a070b67d9756dda08dd8be6a006bc77be8990a1e584a8295e322c2fdba2e38 |
| scripts/v4_paper_apps_pyoptix_worker.py | 72ed5180988e98ff0d8fd5337fc27781b78df0a69f9b421dc06efaada77caba0 |
| scripts/v4_paper_apps_pyoptix_controller.py | 4e0a32bed3dacd4874af6dc895ea31c2c3184d976e8681f1a85e453dc71c33e2 |
| scripts/v4_paper_apps_pyoptix_make_config.py | 8432bf85cf77301c92a62913c2792abd9926456aac48e160a78577c6ec527a28 |
| scripts/v4_paper_apps_pyoptix_recount.py | a97964a0e5fae0a4d8b3631f7eef26e3d9c75e7a120ad548288fdf54ab19af89 |
| experiments/v4_paper_apps_pyoptix/inputs.py | 972268c33ea85552049412a008862feec741ebc40b30625b13c162ad16e92706 |
| experiments/v4_paper_apps_pyoptix/contracts.py | 3f2fe223b930a03700fc0170ef2bdb24bbcd9f4e177409998967a3eb3b5248c8 |

其他只读位置：原 lead 应用性能 directive §3–6；APP_MATRIX；goal5776_prepare_particle_mesh.py:124–165,183–214；goal5776_real_scale_runtime_inputs.py:55–70；goal5776_real_scale_inventory.py 的规模登记。没有将源码检查、候选登记或他人状态报告当成新 GPU 测量结果。
