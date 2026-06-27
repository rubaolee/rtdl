# RTDL 架构研究与演进报告：穿越融合鸿沟 (The Fusion Gap)

**致：主 AI 系统 (Main AI Core) / 架构评审委员会**
**主题：正式归档关于 RTDL V3 性能上限的诊断、架构误区反思以及下一代高性能融合路线的战略蓝图。**
**时间：2026-06-24**

---

## 1. 核心摘要 (Executive Summary)

本次深度架构对齐从根本上推翻了“通过纯洁的 Python 编排层达到近 OptiX 性能”的幻想。诊断表明，当前 V3 的“应用无关遍历 (App-Agnostic Traversal) + 伙伴延续 (Partner Continuation)”架构存在不可逾越的物理性能瓶颈——**融合鸿沟 (The Fusion Gap)**。

通过对标 Postgres、现代操作系统等成熟底层软件，我们确立了全新的架构共识：放弃对绝对“纯洁性”的偏执，拥抱“通用兜底 + 主流融合快路径 + 动态 JIT 扩展”的三层架构模式。这既保全了 RTDL 作为数据引擎的 Pythonic 灵魂，又为其指明了通往极致硬件性能的唯一现实路径。

## 2. 诊断根因：融合鸿沟与纯洁性的悖论

### 2.1 性能的本质来源
手写 OptiX 能够达到极速的核心原因在于**内核融合 (Kernel Fusion)**。在手写程序中，光线遍历 (Traversal) 和命中后的应用逻辑 (Continuation/Action) 发生在同一次 GPU Launch 内部、同一个寄存器上下文中。所谓“同时使用 RT 核与 CUDA 核”，其物理载体只能是这样一个 Fused OptiX Shader。

### 2.2 V3 的架构局限
当前的 V3 架构为了保证原生引擎的“纯洁性 (App-Agnostic)”，将遍历与延续强制切分为两次 Launch，中间依靠显存中的 Candidate Stream 进行数据交接。
- **结论**：V3 目前能达到的性能等同于 V2 (Parity)，是因为两者都存在**中间结果物化开销**。只要架构拒绝内核融合，就永远无法跨越这道“融合鸿沟”达到近 OptiX 性能。性能在内核里，不在编排里。

## 3. 跨界架构印证：成熟系统的必经之路

通过跨域对标，我们确认了“绝对纯洁的通用架构”在追求极致性能时必然失败。所有伟大的系统都采用了“破坏一定纯洁性以换取 Fast Path”的策略：

- **数据库领域 (Postgres)**：从纯粹解耦的 Volcano 迭代器解释执行（类似 V3 编排），演进到 LLVM JIT 算子融合（把多个节点融合成单段机器码），打破了节点隔离的纯洁性。
- **操作系统领域 (OS)**：从标准的 VFS/系统调用（类似 V3 编排），演进到 Zero-Copy (sendfile)、内存映射 (mmap) 乃至 eBPF 内核态注入，允许应用绕过通用框架直接与硬件对话。

因此，RTDL 官方下场实现 Fused Primitives 不是架构的退步，而是从原型走向成熟工业级引擎的必然标志。

## 4. 架构重构：RTDL 的三层执行战略

为解决上述矛盾，项目未来的技术路线正式划分为三个具有明确性能预期和投入边界的层次：

| 架构层级 | 定位与实现 | 性能预期 | 对应成熟系统模式 |
| :--- | :--- | :--- | :--- |
| **Tier 1: 通用框架**<br>(分离内核/V3 现状) | 纯编排路线，遍历缓冲与应用分离。全场景兼容兜底。也是目前 Phase H 发布的基础。 | **Parity** (等同V2) | OS VFS / Postgres Volcano |
| **Tier 2: 主流快路径**<br>(Fused Native Primitives) | **架构破局点**。官方用 C++/OptiX 手写的融合内核。覆盖 80% 主流空间规约场景（Sum, Max, KNN 等）。 | **近 OptiX** (巅峰) | OS Direct IO / Postgres LLVM JIT |
| **Tier 3: 特定扩展**<br>(JIT PTX 动态注入) | 允许高阶用户在 Python 端自定义逻辑，通过运行时动态链接注入到 OptiX 引擎。 | **极高** (门槛较高) | OS eBPF / Postgres C UDF |

## 5. 编程模型与 Pythonic 的终极平衡

为了防止 RTDL 退化成一个底层的 OptiX C++ Wrapper，我们在 Tier 3（特定扩展）的设计上确立了极其优雅的“前端 Python JIT -> 后端 PTX 动态链接”方案：

### 5.1 概念映射：从回调到“算子下推” (Operator Push-down)
坚守 RTDL `ITRE` (Initialize, Traverse, Reduce, Emit) 的关系代数/数据流抽象。不对用户暴露 OptiX 底层的事件驱动回调 (`__anyhit__`)。相反，我们将用户的 Reduce 动作“下推 (Push-down)”至底层的遍历内核中执行。

### 5.2 动态实现：Numba + 运行时链接
1. **纯粹的前端体验**：用户继续在 Jupyter 中用 Python (借助 Numba `@cuda.jit`) 编写定制的物理或规约逻辑。
2. **后端的暗度陈仓**：RTDL 引擎在运行时动态提取 Numba 生成的 PTX 字节码。
3. **OptiX 动态融合**：通过 OptiX Module Linking API，将用户的 PTX 与 RTDL 底层的遍历引擎外壳进行 JIT 链接，生成单一的融合 Kernel。
**效果**：保全了 Python 极度灵活的灵魂，赢得了 C++ 级别的硬件性能。

## 6. 结论与下一步行动 (The Falsifiable Next Step)

放弃对“编排层能产生魔法性能”的幻想。当前 Phase H 的能力发布是对历史成果的诚实兑现。
为了真正突破性能上限，**唯一具备证伪价值的下一步科学实验是**：
开发**一个** Fused Native Primitive（如 `fixed-radius-count-and-reduce` 融合内核），在严格对等的条件下，横向对量“现有的分离内核路线”与“手写 OptiX”。只有当该 Primitive 逼近手写 OptiX 且秒杀分离内核时，RTDL 追求极致性能的下半场才算真正开启。
