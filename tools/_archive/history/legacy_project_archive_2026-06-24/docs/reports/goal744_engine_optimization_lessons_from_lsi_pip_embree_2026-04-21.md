# Goal 744: Engine Optimization Lessons From LSI/PIP Embree Work

## Purpose

Goal743 gives us a clean performance lesson from RTDL's original workloads. The point is not only that Embree became faster. The point is that the experiment shows how to structure optimization work for the next engines: OptiX first, then HIPRT and Vulkan, then Apple RT where the API can support the feature honestly.

## Core Lesson

RT hardware or RT runtimes can accelerate candidate discovery, traversal, and bounded refinement. They cannot make bad app interfaces free.

The sharpest signal is dense LSI. On macOS, one million dense LSI rows took `1.341152 s` through auto dict mode but only `0.017217 s` through prepared raw mode. That is about `77.90x` difference caused mostly by row materialization/interface overhead. Linux and Windows show the same pattern.

So future engine optimization must always ask two questions separately:

1. Is the engine really doing the traversal/refinement work?
2. Is the app forcing the engine result through an unnecessarily expensive Python row interface?

## Optimization Rules We Should Reuse

| Rule | Why it matters | Engines affected |
|---|---|---|
| Separate traversal timing from Python materialization. | Otherwise a fast RT kernel can look slow because Python dict rows dominate. | OptiX, Vulkan, HIPRT, Apple RT, Embree |
| Prefer positive-hit or sparse result modes. | Full matrix or dense pair output grows faster than users usually need. | All engines |
| Add compact app outputs: flags, counts, summaries, raw buffers. | Apps often need decisions, not every witness row. | All engines |
| Use prepared scenes and repeated launches. | One-shot build plus query timing hides the actual repeated-query benefit. | OptiX, Vulkan, HIPRT, Apple RT |
| Keep deterministic hashes for large tests. | Large correctness cannot always depend on slow Python brute-force references. | All engines |
| Report 1-thread/auto/raw separately where meaningful. | It shows whether parallelism or interface overhead is the bottleneck. | Embree now; analogous stream/block/raw modes for GPU engines |
| Do not call an app accelerated just because an engine flag exists. | The app must route its RT part through the backend and expose honest timing. | All engines |

## OptiX Implications

OptiX is still the top-priority backend for v1.0 because users expect NVIDIA RT-core acceleration. The LSI/PIP Embree work says OptiX optimization should not start by returning large Python row lists.

Recommended OptiX actions:

1. Implement or polish native traversal kernels for the root spatial cases that are app-relevant: sparse LSI, positive-hit PIP, ray/triangle any-hit, and fixed-radius candidate counting.

2. For every OptiX app, expose at least one compact output mode before claiming performance: count, flag, summary, or native buffer.

3. Add phase counters inside native OptiX paths: build/pack, BVH build/update, launch, device result compaction, host copy, Python materialization.

4. Treat row-emitting modes as debug/audit modes unless the application truly needs witness rows.

5. RTX cloud benchmarks should compare:
   - full row mode,
   - compact summary mode,
   - raw/native buffer mode,
   - and an external baseline where one exists.

Practical target: make OptiX flagship apps show RT-core traversal speed in compact modes first, then improve full-row modes later.

## Vulkan Implications

Vulkan should follow the same app-interface discipline, but the priority is slightly different. Vulkan is third priority: correct, portable, and not slow; highly optimized when practical.

Recommended Vulkan actions:

1. Avoid full row materialization as the default performance story.

2. Use GPU-side compaction for positive hits and summary rows.

3. Prefer storage-buffer outputs with counts/offsets over per-row Python dict conversion.

4. Benchmark Vulkan against OptiX on the same NVIDIA GPU only after output shape is matched.

5. Preserve explicit classifications when Vulkan is compute-through-Vulkan rather than hardware RT traversal.

Practical target: Vulkan should be a strong portable backend for compact spatial candidates and summaries, not a dumping ground for huge host-side row lists.

## HIPRT Implications

HIPRT has two special risks: memory scaling and backend translation overhead on NVIDIA hardware. The LSI/PIP lesson reinforces that HIPRT should avoid huge row materialization unless required.

Recommended HIPRT actions:

1. First verify that each app path really calls HIPRT and does not silently fall back.

2. Add compact outputs before increasing problem scale.

3. Track memory explicitly: primitive count, BVH size, output buffer size, and temporary scratch.

4. On NVIDIA-through-HIPRT/Orochi, do not confuse “HIPRT API path works” with “AMD GPU performance is validated.”

5. If HIPRT OOM appears on graph/spatial workloads, shrink or compact output buffers before changing algorithms.

Practical target: HIPRT should be correctness-complete and memory-honest first, then performance-tuned once the output contract is compact.

## Apple RT Implications

Apple RT is fourth priority and has a different boundary: if Apple MPS/Metal RT does not expose the needed hardware/API behavior for a feature, RTDL should not fake it.

Recommended Apple actions:

1. Use Apple RT for the features it naturally supports: ray/triangle and closest/any-hit style geometry.

2. For LSI/PIP-style work, clearly distinguish hardware RT traversal from native-assisted or Metal-compute paths.

3. Optimize the app-facing interface first: prepared scenes, compact outputs, and no unnecessary Python dict rows.

4. Avoid broad claims that DB/graph/spatial joins are Apple RT hardware-accelerated unless the implementation actually uses Apple RT traversal.

Practical target: Apple should be excellent for the subset where Apple RT is real, and explicit for everything else.

## App Design Lessons

The best app shape is not “return all rows and let Python figure it out.” The best app shape is:

1. RTDL input describes the build/probe geometry.
2. Engine traversal finds candidates or hits.
3. Engine refinement removes false positives.
4. Engine emits the smallest result the app needs.
5. Python performs orchestration and final business logic.

Good app outputs:

- per-segment hit flags,
- per-query hit counts,
- positive-hit rows only,
- top-k summaries,
- density/core flags,
- collision pose flags,
- aggregate overlap summaries.

Risky app outputs:

- full Cartesian matrices,
- dense pair rows when only counts are needed,
- Python dict rows for every witness in a performance benchmark,
- one-shot build/query timings presented as repeated-query speed.

## Standard Benchmark Policy For Future Engines

Every serious engine optimization report should include this matrix:

| Measurement | Required? | Reason |
|---|---|---|
| Correctness parity | yes | No speed claim without parity. |
| Native traversal mode | yes | Proves the backend does the RT work. |
| Compact output mode | yes | Shows realistic app performance. |
| Full row mode | yes, if public | Quantifies materialization cost. |
| Prepared/repeated mode | yes | Shows real app reuse behavior. |
| External baseline | when available | Prevents self-comparison only. |
| Hardware/API boundary | yes | Prevents false RT-core or hardware claims. |

## Bottom Line

The LSI/PIP Embree work gives us a reusable optimization doctrine:

- make the backend do real RT traversal,
- make the app request compact results,
- measure raw/native and app-visible paths separately,
- and never hide output-materialization costs inside vague “engine performance.”

This should become the default performance review lens for OptiX, HIPRT, Vulkan, and Apple RT.
