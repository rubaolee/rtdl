# RTDL 通过 X-HD 得到的验证与改进 —— 产品视角资产清单

Date: 2026-07-10
视角：目的不是复现 X-HD，而是用它作为高压 driving workload 来验证并完善 RTDL。
下表只登记"对 RTDL 语言/系统有价值"的产出，附各自的验证强度与可复用去向。

---

## A. 新增/沉淀的通用能力（app-neutral，已导出）

### A1. 通用最近/witness/归约流水线
- 能力：`pairwise_l2_distance_candidate_rows` → `nearest_witness` → `max_nearest_distance_witness`（逐点最近邻 + witness + max-min 归约）。Hausdorff 被降级为对其的一层薄 wrapper。
- 验证强度：**强**。小规模 exact-reference 精确对拍；并有**非-Hausdorff 消费者**（设施选址/最差服务半径）独立证明通用性；fail-closed 契约有测试。
- 可复用去向：任何最近邻/覆盖半径/单侧 Chamfer/facility-location/kNN(k=1) 类查询。

### A2. 网格 / cell-MBR 空间查询骨架
- 能力：grid-cell 描述符、cell-MBR 候选/frontier 行、nearest-state seed/frontier 契约、原生 3D cell-MBR OptiX 遍历前门、坐标矩阵前门约定。
- 验证强度：**中强**。在 43.7 万 × 54.3 万点真实规模跑通并与作者值一致；但大规模无独立 exact oracle（见"验证边界"）。
- 可复用去向：大规模空间近邻/范围查询、需要 GPU/RT 加速的点-点/点-网格 workload。

### A3. global-bound early break（通用最大-最近归约提前中止）
- 能力：对"结果=各源最近距离之最大值"类归约，全局上界已知即可提前中止大量查询。opt-in、默认关。
- 验证强度：**中**。最终值精确并对作者 2.4e-9；但**约 93.5% 早止源的逐点 witness 为近似**（已如实标注，禁止当 exact witness）。
- 可复用去向：directed-Hausdorff、覆盖半径、最差服务点等"只要最大值"的归约；**不可**用于需要精确逐点 witness 的场景。

### A4. 真实规模验证本身
- 能力：把 RTDL 从"小规模 exact-reference"推到 40 万+点级可扩展路线（fresh ~0.85s）。
- 验证强度：**强（作为可扩展性证据）**。
- 可复用去向：为未来任何大规模 paper-app 提供"这套积木能扛真实数据量"的信心基线。

---

## B. 被验证/被打磨的设计原则与治理资产

### B1. "app 建立在通用系统之上，核心不含 app 逻辑"——经硬测通过
- 结论：X-HD 诱惑很强，但 Hausdorff 未进核心；app 只拥有数据加载/作者 wrapper/容差/比较器。核心只进通用几何与数据流机器。
- 价值：对 RTDL 定位的一次真实压力测试通过。

### B2. "通用 API 必须有非-app 消费者才算通用"——再次执行
- 价值：防止"app 专用东西改个通用名冒充系统能力"；已成为可复用的准入规则（Goal5128 示范）。

### B3. 性能诚实与 claim-boundary 纪律——已磨硬、可复用
- 内容：相位分离（fresh/warm/full-incl-load）、跨口径拒报比值、拒绝 warm 头条、拒绝把"值吻合"当"精确数据集复现"、directed vs symmetric 判别 fixture。
- 价值：一套成熟的 paper-app 治理资产，可直接套用到未来任何复现型 workload。

---

## C. 未产出通用价值的部分（诚实登记）

### C1. `-lb` 作者 offload 流反向工程
- 事实：约 164 个路线/`-lb` 目标里的一大块，试图逐字节复现作者 2713 万行负载均衡流；行/hash 至今不对齐，且承认可能需"作者专属选项语义"。
- 通用产出：**几乎为零**。唯一正向价值是一个负面边界结论——"该流是实现/app 专属，不该塞进通用模型，应 fail-close"。
- 教训（产品级）：当 driving workload 的某部分开始要求复现其**实现细节**且沉淀不出通用能力时，应尽早识别为 app 专属并止损，而非投入上百目标硬啃。

---

## D. 验证强度的总体边界（须清醒）

- 正确性 = "小规模 exact-reference 精确" + "大规模与作者一致"；**大规模无独立 exact oracle**。
- 快路线逐点 witness 有近似（仅最大值精确）。
- Level-B 仅一个公开工作负载（Dragon→HappyBuddha, directed）；非跨类别代表性。
- 故"已验证"应读作：**值级正确 + 通用性有非-app 背书**，非"每个细节都被独立精确校验"。

---

## E. 净结论

赚到的真资产：一套**经真实规模验证、且有独立非-app 消费者背书**的通用空间近邻/归约能力（A1–A3）+ 可扩展性信心（A4）+ 一套成熟的通用性与性能诚实治理纪律（B1–B3）。
代价与教训：`-lb` 线（C1）证明了"识别 app 专属、及时止损"这条产品纪律的重要性——这是本项目给 RTDL 流程最值钱的一课。
