# RTDL 基于 Embree 的 RayJoin 实验复现报告

_生成时间：2026-04-01。此文档为 Goal 23 最终英文报告的中文说明版。_

## 摘要

本报告总结了我们在 **无 NVIDIA GPU** 条件下，基于 **RTDL + Intel Embree** 对 RayJoin 论文实验结构所做的本地有界复现工作。  
当前目标不是声称已经精确复现论文中的原始大规模结果，而是建立一个：

- 可执行
- 可重复
- 对当前机器友好
- 对实验边界诚实

的本地研究基线。

本轮已经完成并输出了：

- Table 3 的部分本地有界替代结果
- Figure 13 的 `lsi` 有界类比实验
- Figure 14 的 `pip` 有界类比实验
- Table 4 的 overlay-seed 类比结果
- Figure 15 的 overlay speedup 类比结果
- 最终报告与图表产物

同时，尚未获取或转换完成的数据集家族，被明确标注为 `missing` 或 `source-identified but unexecuted`，避免产生“已经完整复现 RayJoin”的误解。

## 1. 实验背景

RayJoin 论文的核心评估对象，是建立在光线追踪风格加速结构之上的空间连接工作负载。  
RTDL 的目标是提供一个 Python 风格的 DSL，用统一的语言表达这类工作负载，并在不同后端上执行。

在当前阶段：

- 最终目标仍然是 NVIDIA GPU / OptiX
- 但由于当前没有可用的 NVIDIA 机器
- 因此我们先在 **Embree CPU 后端** 上完成语言、运行时、数据管线、表格与图表生成能力

所以，Goal 23 的定位是：

**在本地 Mac 上，以 Embree 为执行后端，尽可能有界地复现 RayJoin 的实验结构，并生成研究论文风格的表格、图和报告。**

## 2. 当前系统与语言形态

RTDL 当前已经具备以下核心能力：

- Python 风格 DSL 编写 workload
- `CompiledKernel` 形式的语言级 IR
- 面向后端的 RayJoin 风格计划表示
- CPU 参考执行路径
- Embree 执行路径
- `dict`、`raw`、`prepared raw` 三种结果/执行模式

在 Goal 23 中，Figure 13 / Figure 14 的可扩展性实验使用的是：

- **prepared raw** 执行路径

原因是此前 Goal 19 已经证明：

- `dict` 路径和纯 C/C++ Embree 相比仍然过慢
- `raw` 和 `prepared raw` 路径已经可以接近纯 C/C++ Embree

因此 Goal 23 的实验结果，代表的是当前 RTDL 在本地 Embree 阶段的“最佳执行形态”，而不是旧的高开销 Python dict 热路径。

## 3. 本轮实验做了什么

本轮实验不是单一 benchmark，而是一个完整的有界复现包，主要包括以下几部分。

### 3.1 Table 3 有界替代结果

已执行的本地替代行来自：

- `County ⊲⊳ Zipcode` / `lsi`
- `County ⊲⊳ Zipcode` / `pip`

具体又分为：

- `fixture-subset`
- `derived-input`

也就是说，我们使用了：

- 已检入仓库的小型 fixture 子集
- 以及在其基础上做的确定性放大版本

来构造当前本地可执行的 Table 3 有界类比结果。

### 3.2 Figure 13：LSI 可扩展性类比

Figure 13 的本地配置是：

- 固定 build side：`R = 100000`
- probe side：`S = 100000, 200000, 300000, 400000, 500000`

输出包括：

- query time 曲线
- throughput 曲线

### 3.3 Figure 14：PIP 可扩展性类比

Figure 14 的本地配置是：

- 固定 build side：`R = 100000`
- probe side：`S = 2000, 4000, 6000, 8000, 10000`

输出包括：

- query time 曲线
- throughput 曲线

### 3.4 Table 4 与 Figure 15：Overlay 类比

当前 overlay 结果使用的是：

- `overlay-seed analogue`

也就是：

- 不是论文原始全量 overlay 数据对
- 而是当前 RTDL 本地可执行的一组 overlay 种子输入及其确定性放大版本

它们生成了：

- Table 4 的本地有界类比结果
- Figure 15 的 overlay speedup 类比图

## 4. 数据集情况

当前数据集状态必须分开理解。

### 4.1 已经可执行的数据

当前已经能在本地稳定运行的是：

- 一部分 fixture 子集
- 一部分 deterministic derived inputs
- Goal 23 中使用的 synthetic scalability inputs
- `County ⊲⊳ Zipcode` 的当前本地替代执行行

这些足够支持：

- Figure 13
- Figure 14
- Table 3 的部分 bounded analogue
- Table 4 / Figure 15 的 bounded analogue

### 4.2 已识别但尚未执行的数据家族

目前仍然只是“已找到公开来源或已冻结获取方案”，但还未形成本地可执行输入的数据家族包括：

- `Block ⊲⊳ Water`
- 各洲 `Lakes ⊲⊳ Parks` 配对

换句话说：

- 我们已经知道这些数据应从哪里来
- 也定义了未来的 deterministic bounded preparation policy
- 但当前尚未把它们全部转换成 RTDL/Embree 可执行格式

因此它们在报告中被明确标注为：

- `missing`
- 或 `source-identified`

## 5. 当前实验边界

这轮结果必须以正确方式理解。

### 5.1 这轮已经做到的

- 构建了 RayJoin 风格实验矩阵
- 冻结了本地 `5-10 分钟` 运行预算
- 实现并运行了 LSI / PIP 的 bounded scalability analogue
- 生成了 Table 3 / Table 4 / Figure 13 / Figure 14 / Figure 15 对应的本地类比产物
- 输出了结构化 JSON、Markdown、SVG 等报告产物

### 5.2 这轮没有声称做到的

- 没有声称已经完整复现 RayJoin 论文所有原始实验
- 没有声称已经获取并转换完论文全部真实数据集
- 没有声称 overlay 已达到论文中的完整多边形物化版本
- 没有声称已经得到 GPU RT hardware 上的最终结果

所以正确表述应当是：

**我们已经完成了 RayJoin 实验结构在本地 Embree 后端上的一个有界、诚实、可重复的研究基线复现。**

## 6. 主要实验结果应如何解读

### 6.1 对系统能力的意义

这轮实验说明：

- RTDL 语言已经不仅仅是编译器草图
- 它已经可以承载一套真实的实验流程
- 包括 workload 表达、后端执行、benchmark、表格、图和最终报告输出

### 6.2 对性能工作的意义

这轮实验与当前低开销执行路径的演进方向相衔接：

- 若使用旧的 `dict` 路径，RTDL 的主机端开销较大
- 若使用 `raw` / `prepared raw` 路径，RTDL 更适合承载当前 Embree 阶段的实验执行

因此，Goal 23 的 Figure 13 / Figure 14 结果，建立在当前更合理的低开销执行路径之上。

### 6.3 对未来 NVIDIA 阶段的意义

当前 Embree 复现工作的价值在于：

- 先把 DSL、IR、runtime contract、dataset pipeline、artifact pipeline 做扎实
- 等拿到 NVIDIA 机器后，再把最终 GPU backend 接入

这样后续 GPU 阶段更像是：

- 替换执行后端

而不是：

- 从头重做语言、实验系统和报告系统

## 7. 后续工作

基于当前状态，后续主要方向是：

1. 获取并转换剩余的 RayJoin 数据集家族
2. 补齐 Table 3 的更多真实 bounded local rows
3. 继续提升 overlay fidelity
4. 在 Embree 阶段尽量完整覆盖 RayJoin workload/experiment structure
5. 等 NVIDIA 机器可用后，把当前 DSL 与实验系统迁移到 OptiX/GPU backend

## 8. 结论

Goal 23 标志着项目进入了一个更成熟的阶段：

- 我们不仅有 DSL
- 不仅有 Embree backend
- 还已经有了论文风格的实验组织、图表生成、结果报告与边界说明

当前最准确的结论是：

**RTDL 已经能够在本地 Embree 后端上，对 RayJoin 的实验结构做出一套有界、可执行、可复查、并且对边界诚实的复现。**

这为下一阶段两条路线都打下了基础：

- 继续补全 Embree 阶段的数据集和实验覆盖
- 将来切换到 NVIDIA GPU 后端做最终目标中的真实 RT-core 复现

## 9. Fidelity 标签说明

- `fixture-subset`：仓库中已经检入的小型公开子集
- `derived-input`：从当前可用输入做确定性缩减或放大得到的输入
- `synthetic-input`：通过确定性生成器构造的合成输入
- `overlay-seed analogue`：当前 RTDL overlay 路径上的类比输入，不等同于论文中的完整多边形物化 overlay
