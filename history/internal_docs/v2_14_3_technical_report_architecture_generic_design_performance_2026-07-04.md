# RTDL v2.14.3 Technical Report: Architecture, Generic Design, And Performance

Date: 2026-07-04

## 一句话结论

v2.14.3 是一个**有界的 RayJoin paper-reproduction 性能与架构整理版本**。

它完成的不是“追平作者 C++/CUDA/OptiX 程序”，而是把 RTDL 对 RayJoin Section 5.7 的实现从“跑完后写论文文本文件的独立 app”推进到“writer-free binary overlay operator”的架构方向上，并用通用 RTDL primitives、Numba partner、列式/二进制中间数据流证明了这条路线可以显著降低 Python 文本 writer 和 Python 数据打包造成的成本。

最终性能结论必须有边界：

- top4 County x Zipcode representative 输入上，writer-free binary route 从 `7.851s` 改进到 `4.220s` fresh/cold evidence，约 `1.86x`；
- 同进程重复完整路线约 `3.62-3.67s`，但仍包含 LSI 生产成本，只能作为 secondary steady-process evidence；
- top4 author overlay-compute denominator 没有测量，因此不报告 top4 作者性能比值；
- v2.14.3 不 claim author-performance parity；
- 主要剩余瓶颈是 exact planar-map LSI producer setup/ensure 约 `2.69-2.76s`。

## 背景：为什么要做 v2.14.3

RayJoin 论文复现工程暴露了一个重要事实：

RTDL 如果被当成“跑完整 RayJoin app 并输出作者论文文本文件”的工具来衡量，会被 Python 文本 writer、输出格式化、对象构造和 host-side assembly 绑定住。这个场景里，RT/GPU 的价值会被大量与 RT 无关的文本 sink 成本掩盖。

因此 v2.14.3 的核心架构修正是：

```text
不要只把 RayJoin overlay 当成一个最终输出文本文件的独立程序；
要把它当成空间数据流管线中的 writer-free binary operator。
```

这不是换一个好看的 benchmark，而是更符合 RTDL 作为语言/系统的定位：

```text
RTDL 提供通用 RT primitives 和列式中间结果；
应用或下游 operator 消费二进制/列式结果；
只有最终用户真的需要论文文本格式时，才进入 app-owned writer。
```

## v2.14.3 的架构设计

v2.14.3 形成了两条明确分层的路线。

### 路线 A：paper text-output correctness route

用途：

- 作为 RayJoin paper reproduction 的 byte-equality correctness anchor；
- 证明 RTDL 能用公开 primitives 和 app-layer logic 产出 AuthorOfficial comparator 一致的论文输出；
- 不作为性能主路线。

形态：

```text
public planar-map LSI
-> public directed point-location / PIP
-> app-layer overlay assembly
-> paper text output-chain writer
```

典型脚本：

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay.py
Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py
```

top4 representative 输入上：

| Route | Time | Meaning |
|---|---:|---|
| RTDL text route | `77.37s` route elapsed | byte-equal correctness anchor, includes text writer |
| RTDL Numba text route | `70.17s` route elapsed | app-layer Numba helps selected logic, still text-writer dominated |

解释：

这条路线重要，但它不是 v2.14.3 的性能主张。它证明的是 paper reproduction correctness，不证明 RTDL 的 binary pipeline performance。

### 路线 B：writer-free binary overlay operator route

用途：

- 衡量 RTDL 作为空间数据流 operator 的性能；
- 去掉 paper text writer；
- 产出二进制/列式 descriptor summary 给下游 consumer；
- 作为 v2.14.3 性能主路线。

形态：

```text
generic planar-map LSI
-> generic directed point-location / PIP
-> columnar/device-oriented numeric continuation
-> binary grouped descriptor consumer
```

典型脚本：

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

这条路线不写论文文本 output-chain 文件，因此也不做 paper text byte-equality claim。它用结构锚点、排序验证、计数、descriptor summary 来保证语义一致性。

## 通用系统设计：RTDL 做什么，RayJoin app 做什么

v2.14.3 的重要原则是：

```text
RTDL 是通用系统；
RayJoin 是 RTDL 之上的 paper-reproduction app；
新的 v2.14.3 primitives 和公开入口必须保持通用；
遗留 RayJoin 命名/打包问题必须如实标注，不能用绝对化语言掩盖。
```

精确边界：

- v2.14.3 新增的 exact LSI pair-id device columns、writer-free binary route、columnar handoff 以及公开文档入口按通用能力设计；
- 代码树里仍存在历史遗留的 `rayjoin_cdb` 命名 native 符号，以及 `src/rtdsl/rayjoin_overlay.py` 这个 bundled helper；
- 这些遗留项不是 v2.14.3 新增的 RayJoin-only kernel，也不是本次 writer-free binary route 的公开依赖；
- 但它们意味着“RTDL core 已经完全无 RayJoin 身份痕迹”这句话不成立。正确说法是：**v2.14.3 的新增公开能力和性能路线按通用系统边界设计，遗留 RayJoin 命名和 bundled helper 需要未来重命名/迁移。**

### RTDL/core 层负责的通用能力

v2.14.3 涉及的通用能力包括：

1. **Planar-map LSI primitive**

   通用含义：

   ```text
   base planar map segments
   query planar map segments
   -> intersecting segment pair rows/counts
   ```

   v2.14.3 推进的是 exact pair-id device-column route：

   ```text
   exact LSI -> {left_id, right_id} device/columnar outputs
   ```

   这是通用空间连接/overlay 前置能力，不是 RayJoin-only kernel。

2. **Directed point-location / PIP primitive**

   通用含义：

   ```text
   directed query points / segments
   -> containing face / point-location rows/counts
   ```

   v2.14.3 使用 point-location device face columns，减少下游对 Python rows 的依赖。

3. **Columnar / binary handoff**

   通用含义：

   ```text
   primitive output rows
   -> columnar id arrays / descriptor arrays
   -> partner or downstream operator
   ```

   这条路线服务的不只是 RayJoin。非 RayJoin genericity smoke 覆盖了 projected descriptor pipeline 和 hit-stream row-buffer adapter。当前本地 gate 对 hit-stream adapter 的通用性做了静态/CPU 证据验证；随后在本地 Linux + GTX 1070 上补跑了非 RayJoin hit-stream GPU runtime smoke，`Ran 2 tests` / `OK`。这证明 runtime path 能跑通，但不是性能测试。

4. **Partner hooks**

   v2.14.3 使用 Numba 的方式包括：

   - Numba CUDA：数值 reprojection / sort 等 device-columnar continuation；
   - Numba CPU `njit`：grouped descriptor/carrier construction；
   - Numba 并不是 correctness-critical comparator 的唯一依据，而是加速/结构化 app continuation 的 partner。

### RayJoin app 层负责的应用语义

RayJoin app 保留以下责任：

1. CDB 输入、AuthorOfficial comparator、Section 5.2/5.3/5.7 workflow；
2. coordinate scaling 与 author-compatible parameters；
3. overlay-specific midpoint / output-chain logic；
4. paper text output-chain formatting；
5. representative input 与 exact available input 的标签边界。

这意味着：

```text
RTDL core 可以提供 LSI/PIP/columnar handoff；
RayJoin app 可以用这些能力实现 RayJoin；
v2.14.3 新增路线不能把“写 RayJoin output-chain 文本”这种 app-specific 语义放进 core。
```

## 关键实现内容

### 1. Exact LSI pair-id device columns

目标：

避免 generic LSI route 产出应用不需要的完整几何 rows，直接产出 `{left_id, right_id}` 这类下游所需的 id columns。

效果：

top4 representative 输入上：

```text
normal public LSI rows:       4.313502s
exact pair-id device columns: 2.749540s
LSI-stage speedup:            1.57x
```

全 route：

```text
normal fresh binary route:           7.851479s
exact LSI device-column fresh route: 5.903873s
speedup:                             1.33x
```

边界：

这个改动是真实收益，但不是最终瓶颈修复。exact route 仍花约 `2.75s` 在 LSI production 上。

### 2. Fast scaled-point host pack

前序分解发现 midpoint query point generation 不是数学慢，而是逐行 Python/ctypes pack 慢。

v2.14.3 的修复：

```text
per-row Python/ctypes object construction
-> NumPy structured-array owner + ctypes view
```

效果：

| Metric | Before | After | Speedup |
|---|---:|---:|---:|
| writer-free hot | `5.373426s` | `4.219930s` | `1.273x` |
| downstream floor | `2.671954s` | `1.478150s` | `1.808x` |
| midpoint map0 pack | `0.683992s` | `0.003442s` | `198.717x` |
| midpoint map1 pack | `0.606735s` | `0.003427s` | `177.044x` |

边界：

这不是 zero-copy，也不是真正 device-resident prepared-points route。它是低风险的 host-boundary 优化，保留既有 scaled-point ABI。

### 3. Compiled grouped carrier diagnostics

v2.14.3 分解了 grouped carrier construction：

早期现象：

```text
carrier construction around 0.65s
side0 builder seemingly much slower than side1
```

进一步控制变量后发现：

```text
慢的不是 side0；
慢的是 first large side-builder call / warmup / cache / JIT-like artifact。
```

最终策略：

- 不把 reversed side order 晋升为默认优化；
- 保留 diagnostic flag；
- 把 carrier warm-state 成本约 `0.10-0.11s` 作为 secondary/diagnostic evidence；
- 不用它制造 warm-only headline。

### 4. Correctness and genericity gates

本地 gate：

```text
Ran 85 tests
OK (skipped=1)
```

说明：

- 1 个 skip 是本地 Windows 机器缺 OptiX + Numba CUDA runtime 的 GPU 子项，且该子项正是非 RayJoin hit-stream runtime smoke；
- RayJoin paper correctness、SoS、Section 5.7 output contract、current point-location grouping contract 都通过；
- 非 RayJoin genericity smoke 的静态/CPU 部分通过，证明 row-buffer/descriptor path 的代码形态不只是 RayJoin-shaped claim；
- 该 GPU runtime 子项已在本地 Linux + GTX 1070 上补跑，`Ran 2 tests` / `OK`，作为 release-stage runtime genericity smoke；不作为性能证据。

## 性能提升总结

### top4 representative 主矩阵

Workload:

```text
top4_county_zipcode_arcgis_same_source
```

规模：

| Side | Chains | Points | Edges |
|---|---:|---:|---:|
| County top4 | 1,612 | 1,706,639 | 1,705,027 |
| Zipcode top4 | 10,144 | 9,993,104 | 9,982,960 |

结构锚点：

```text
lsi_row_count = 428322
xsect_sorted_counts side0/map0 = 428322
xsect_sorted_counts side1/map1 = 428322
vertex_positive_counts side0_in_side1 = 812721
vertex_positive_counts side1_in_side0 = 4527305
downstream descriptor pairs = 15014
downstream total groups = 428974
downstream total point rows = 5902562
```

主矩阵：

| Route | Time | Status | Meaning |
|---|---:|---|---|
| RTDL text route | `77.37s` | correctness anchor | AuthorOfficial-byte-equal paper text output |
| RTDL Numba text route | `70.17s` | correctness anchor + app-layer Numba | Still text-output dominated |
| Earlier writer-free binary route | `7.851s` | superseded baseline | Before exact LSI device columns / fast pack |
| Exact LSI device-column route | `5.904s` | intermediate | Generic pair-id device columns |
| v2.14.3 fresh/cold binary route | `4.220s` | primary result | LSI included |
| repeated full route, LSI included | median `3.669s` | secondary evidence | carrier warm-state, LSI still included |
| prepared/cached LSI replay | diagnostic only | not primary | not a fresh overlay computation |

### 合法性能结论

v2.14.3 的合法、有界性能结论是：

```text
writer-free top4 route: 7.851s -> 4.220s = 1.86x improvement
secondary steady-process evidence: 7.851s -> 3.669s = 2.14x improvement
```

不能说：

```text
v2.14.3 is author-parity
v2.14.3 is 2x from author
prepared replay is fresh overlay performance
top4 ratio vs author is known
```

原因：

top4 author overlay-compute timing 未测。已有 `0.0421s` 属于更小的 County x Soil/public-sample context，不能作为 top4 分母。

## 当前瓶颈

v2.14.3 之后，瓶颈已经很清楚：

```text
LSI producer setup/ensure work: about 2.69-2.76s
carrier warm-state: about 0.10-0.11s
native launch inside LSI extended timing: about 0.0023s
```

这说明：

1. 主要瓶颈不是 native GPU launch；
2. 主要瓶颈也不是 carrier side order；
3. 主要瓶颈是 exact planar-map LSI producer 的 setup/ensure/production path；
4. `0.000000s` LSI repeat diagnostic 无效，不能当性能证据。

LSI extended timings显示，大头来自：

| Component | Approx time |
|---|---:|
| grouped range ensure | `~1.03-1.06s` |
| scaled cache ensure | `~0.69-0.72s` |
| exact pipeline ensure | `~0.52-0.53s` |
| split kernel ensure | `~0.43-0.45s` |
| native launch | `~0.0023s` |

## 架构意义

v2.14.3 的真正价值不是最终秒数本身，而是明确了 RTDL 应该如何服务这类 app：

```text
RTDL 不应该把自己定义成“Python 版 RayJoin 文本输出程序”；
RTDL 应该定义成“空间数据流中的通用 RT/binary operator 系统”。
```

这带来三点清晰认识：

1. **Text writer 是 correctness anchor，不是性能主战场**

   paper text output 用来证明复现，但不应该拿它评价 RTDL operator 性能。

2. **Binary operator route 是 RTDL 的正确性能口径**

   下游数据库/空间管线通常消费二进制 rows/columns，而不是论文文本文件。

3. **下一步必须攻 LSI producer**

   继续优化 Python writer 或 side-order 已经不是主要方向。需要研究 exact planar-map LSI producer 的 setup/ensure 路径，或者在未来版本考虑更深的 device-resident/in-traversal 方案。

## v2.14.3 不是什么

为了防止误读，必须明确：

v2.14.3 不是：

- 完整 author-performance parity；
- full eight-pair hidden-input Section 5.7 reproduction；
- Layer 4 in-traversal fusion；
- 完整 device-resident overlay；
- 以 prepared/cached replay 冒充 fresh overlay；
- 把 RayJoin overlay 内核塞进 RTDL core 的版本。

v2.14.3 是：

- RayJoin paper-reproduction 工程线上的一个 bounded performance release；
- 一个把 RTDL 性能口径从 text-output app 转向 writer-free binary operator 的版本；
- 一个证明若干通用 primitives / columnar handoff / Numba partner 路线能显著改善性能的版本；
- 一个诚实标出剩余 LSI producer 瓶颈的版本。

## 后续建议

### v2.14.3 release staging

可以进入 release staging，但需要人工审阅：

- 哪些内部 evidence artifacts 保留；
- 哪些 tests/scripts 进入正式仓库；
- 哪些 POD run outputs 只保留摘要；
- 如何组织 `history/internal_docs`，避免污染用户入口。

### 下一性能版本

下一版本若继续性能，应聚焦：

```text
exact planar-map LSI producer setup/ensure path
```

优先问题：

1. 哪些 ensure/cache/pipeline setup 可以成为真实 product prepare-once/query-many route；
2. 哪些 setup 是 one-shot fresh overlay 不可避免成本；
3. 是否能减少 grouped range / scaled cache / exact pipeline / split kernel ensure 的重复工作；
4. 是否需要更深的 device-resident or in-traversal fusion，但这已不属于 v2.14.3。

## 最终结论

v2.14.3 是一个技术上成立、边界清楚、性能有实际进展的版本：

- 它把 RayJoin Section 5.7 的 RTDL 路线从 paper text-output app 性能陷阱中拉出来；
- 它建立了 writer-free binary operator 的正确架构方向；
- 它用 generic LSI/PIP primitives、device/columnar handoff、Numba partner 和 app-owned RayJoin logic 完成了更清晰的系统分层；
- 它在 top4 representative 输入上把 writer-free binary route 从 `7.851s` 推到 `4.220s`，并给出 `3.669s` 的 secondary steady-process evidence；
- 它没有假装追平作者，也没有用错误分母制造性能幻觉；
- 它明确指出下一阶段真正要解决的是 LSI producer，而不是继续在 writer、carrier side order 或 warm-only replay 上打转。

这就是 v2.14.3 的价值：不是终点，但它把架构和性能问题从混乱状态推进到了可解释、可验证、可继续优化的状态。
