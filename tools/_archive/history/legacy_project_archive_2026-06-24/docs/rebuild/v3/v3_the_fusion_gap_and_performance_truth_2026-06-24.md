# V3 性能真相与融合鸿沟 (The Fusion Gap)

## 1. 为什么 V3 到不了 OptiX 性能：融合鸿沟 (The Fusion Gap)

手写 OptiX RT 程序快，主要依靠两点：
1. **硬件加速**：RT 核硬件做 BVH 遍历。这一点 RTDL V3 已经在使用了（基于同一套 OptiX）。
2. **内核融合 (Fusion)**：在手写 OptiX 中，命中逻辑 (any-hit/closest-hit) 在光线遍历的**同一次 launch、同一个寄存器上下文中、on-device** 就把应用的逻辑（App Continuation）执行完了。**没有中间结果落内存，没有第二次 Kernel 启动。**

RTDL V3 的现有架构（Python 托管 + app-agnostic 原生引擎 + partner continuation）恰好为了“通用纯洁性”而**丢掉了第 2 点**。V3 的执行流是：先遍历（OptiX 一次 launch）→ 吐出 candidate 流（落 device/host 内存）→ 再跑**另一个** kernel (CuPy/Numba) 做应用逻辑。即：**遍历和应用逻辑被切成了两个 kernel，中间夹着一个物理化的缓冲区。**

> **结论：** V3 性能目前等同于 V2 (Parity) 的根本原因在于两者都必须将中间结果物化。它们都到不了手写 OptiX 的性能，因为手写 OptiX 是将“遍历”和“应用逻辑”融合在一次 launch 中、实现零中间开销。**“到 OptiX 性能的距离”就等于这个“融合鸿沟”。**

## 2. “同时使用 CUDA 核与 RT 核”的硬件真相

“同时使用 CUDA 核与 RT 核”并不是在编排层可以做到的魔法。它本质上就是**一个 Fused OptiX Shader 的定义**：在同一次 launch 里，RT 核执行硬件遍历，同时 SM/CUDA 核运行 shader 里的应用数学逻辑。协同进行、on-device、零中间物化。

- **融合模型**：RT 核 + CUDA 核**同时**协作 → 带来 OptiX 级性能。
- **Python 编排模型 (V3)**：RT 核遍历 (Launch 1) → 写缓冲 → CUDA 核 Continuation (Launch 2) → **先后**使用，并非同时。这只能达到 Parity 级性能，而非 OptiX 级。

**在编排层永远无法做到“同时”，只能做到“先后+缓冲”。只有内核融合才能做到“同时干活”。**

## 3. 与“App-agnostic 纯洁性”的根本冲突

这是最需要认清的架构取舍：
**近 OptiX 性能 = 把“具体应用的 continuation”融进“遍历内核”。**
而项目先前的铁律“原生引擎必须完全 app-agnostic（对应用完全无感知）”**恰恰禁止**了这一行为。

> 你不可能同时拥有 **(a) 完全 app-agnostic 的原生引擎** 和 **(b) 近 OptiX 性能**——因为后者来源于将具体逻辑融入遍历内核。要实现融合性能，就必须让渡出一部分架构上的“纯洁性”。

V3 试图在编排层保持纯洁性，其必然代价就是性能永远停留在 Parity 阶段。这不是 bug，而是那条架构铁律推导出的必然结果。

## 4. 真实的方案分层 (The Honest Paths)

基于以上诊断，项目的未来路径必须诚实地分为三层：

### 方案 A：降级目标（现成、可发、主打能力）
接受“Python 拿到 RT 核 + parity 级性能，但不近 OptiX”。
**定位**：让用户无需编写 OptiX/C++ 就能从 Python 环境中调用 RT 核（这在业界本身也是罕见且有价值的产品）。这就是 **V3 即将进行的能力发布 (Phase H)**。

### 方案 B：追求近 OptiX 性能的融合路线（打破纯洁性、硬核方向）
如果要达到接近 OptiX 的性能，必须做融合。
- **B-i: Fused Native Primitives (由 RTDL 自己写)**
  将“遍历 + 常用 continuation 模式”在**一次 OptiX/CUDA launch 里固化融合**。例如：`fixed-radius-count-and-reduce`、`knn-and-aggregate`、`traverse-and-sum/min/max`。
  **优势**：这些原语按*计算模式*泛化，而非按具体应用，能覆盖大量常规需求。**这是真正能达到近 OptiX 性能的安全路径**，因为它本质上就是手写的 Fused OptiX，只是由 RTDL 封装好供 Python 调用。
  **代价**：每个模式都需要扎实的 C++/CUDA/OptiX 工程，并且需要可控地打破“app-agnostic”的绝对纯洁性。
- **B-ii: Device-Callable / PTX 注入 (由用户写)**
  允许用户从 Python 传递自定义 Fused 逻辑（Reverse PTX Linkage）。
  **定位**：作为更长远的彩蛋，由于 ABI 匹配脆弱、Triton 不适配等问题，它不适合作为早期的性能地基。

### 方案 C：分离内核 Partner（兜底）
即现在的 V3 编排路线。提供完全的通用性，但只有 Parity 级性能，作为“融合模式未覆盖到”的 fallback 退路。

**性能分层总结：**

| 路径 | 谁写融合 | 性能档位 |
|---|---|---|
| Fused native primitive (B-i) | RTDL 编写 | **≈ 近手写 OptiX** |
| Device-callable PTX 注入 (B-ii) | 用户编写 | 接近 OptiX（适用面窄/较脆弱） |
| 分离内核 partner (C / 现 V3) | 无融合 (编排) | **Parity，非 OptiX** |

## 5. 对 V3 性能来源的重构认知

- **V3 作为编排层 (Orchestration)**：**没有性能来源**。这点已被 Barnes-Hut 和 RTNN 等用例的测评证明。
- **V3 作为融合层 (Fusion)**：**从未被真正测试过。** 项目因为逃避风险（Competent-avoidance：融合难、不可切分、风险高），将融合推迟，转而一直试图在“编排层”寻找 OptiX 性能。**找错了层。性能在内核里 (fusion)，不在编排里。** 连“编排 vs 融合”这个架构选择本身，都在潜意识中为了逃避硬核工程：编排可切、安全；融合难、吓人。

## 6. 唯一可证伪的性能实验：下一步的方向

要解决“Python + RT 核 + 近 OptiX 性能”的原始技术疑难，务实的路是 RTDL 自己写一小批 Fused Native Primitives。

这引出了**唯一真正能产生性能、且具备可证伪性的实验**，和之前的所有实验都不同：
> 编写**一个** Fused 原生原语（例如将 `fixed-radius-count-and-reduce` 融合在一次 OptiX launch 中）。
> **同合约对量两个基线**：
> 1. 分离内核 Partner 路线 (现 V3)
> 2. 手写 OptiX
> 
> 如果这个 Fused Primitive 能逼近手写 OptiX，且显著超越分离内核路线，**那才是 V3.x 真正的性能来源**。

这是“真正进入内核”的实验，而非在编排层的又一次打转。它与当前的能力发布（Phase H）互不冲突：能力发布是诚实地兑现现成的 Parity 成果，而 Fused Primitive 实验则是通往极致性能时唯一正确的下一步方向。
