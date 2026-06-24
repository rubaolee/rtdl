# Goal670: Claude HIPRT Performance Optimization Review

Date: 2026-04-20

Reviewer: Claude (claude-sonnet-4-6)

Playbook: `docs/reports/goal669_cross_engine_performance_optimization_lessons_2026-04-20.md`

Verdict: **ACCEPT WITH NOTES**

---

## Current HIPRT Performance State

### Cold One-Shot Baseline (Goal 560, GTX 1070, small fixtures)

All 18 v0.9 workloads pass CPU reference parity. Timings cluster around
`0.37–0.57s` per call for every workload regardless of problem difficulty,
because each call pays the same fixed overhead:

- Orochi CUDA context and device initialization
- HIPRT context creation
- geometry build and upload
- ORORTC JIT kernel compilation
- result copy-back and Python materialization

Embree cold calls: `0.000175–0.023s`. HIPRT cold calls: `0.367–0.572s`. The
gap is dominated by JIT and context overhead, not traversal.

### Prepared Path Performance (Goals 565–568)

After Goals 565–568, prepared paths separate one-time build cost from
repeated-query cost. All numbers are from the Linux GTX 1070 host via
HIPRT/Orochi CUDA mode.

| Workload | One-shot HIPRT | Prepared build | Prepared query | Speedup vs one-shot |
|---|---:|---:|---:|---:|
| 3D ray/triangle hit count | 0.5655s | 0.5238s | 0.00206s | 274x |
| 3D fixed-radius neighbors | 0.5981s | 0.5481s | 0.00353s | 169x |
| BFS discover (dedupe=True) | 0.6699s | 0.7238s | 0.02046s | 33x |
| triangle match | 0.5744s | 0.7238s | 0.00220s | 261x |
| conjunctive_scan (100k rows) | 1.9107s | 1.8256s | 0.00184s | 1039x |
| grouped_count (100k rows) | 1.8340s | 1.8193s | 0.00229s | 801x |
| grouped_sum (100k rows) | 1.8227s | 1.7908s | 0.00245s | 746x |

Pattern: HIPRT prepared query times are millisecond-class on all measured
workloads. Prepared build times remain `0.5–1.8s` (one-time cost).

### Any-Hit Early Exit (Goal 639)

Native early-exit any-hit kernels exist for 2D and 3D ray/triangle:

```cpp
if (hit.hasHit()) {
    any_hit = 1u;
    break;
}
```

The kernel exits correctly after the first accepted hit. However, there is no
prepared any-hit path. Whole-call timing on unprepared any-hit shows no
measured speedup versus hit-count because both paths pay the same JIT/context
overhead (`0.609s` hit-count vs `0.614s` any-hit, 1500 rays, 150 triangles).

---

## What Is Already Optimized

1. **Prepared 3D ray/triangle hit count** (Goal 565) — proven, Linux-validated.
2. **Prepared 3D fixed-radius and kNN nearest-neighbor** (Goal 566) — same
   kernel handles both because kNN uses the same fixed-radius traversal body.
3. **Prepared graph CSR for BFS and triangle match** (Goal 567) — triangle
   match uses one GPU thread per seed; BFS uses deterministic serial kernel for
   global dedupe.
4. **Prepared DB table for conjunctive_scan, grouped_count, grouped_sum**
   (Goal 568) — per-row ray dispatch; aggregation still on host.
5. **Native any-hit early-exit kernel** (Goal 639) — structurally correct;
   benefit only visible after prepared path combines it.

---

## Top Optimization Opportunities

Ranked by expected value and implementation risk, using the Goal 669 playbook.

### 1. Prepared 2D Ray/Triangle (High value, Low risk)

**What:** Mirror the Goal 565 prepared-3D pattern for 2D ray/triangle hit
count and any-hit.

**Why high value:** The 2D visibility/collision path is a primary RTDL use
case. Goal 560 showed 2D hit count cold-call time at `0.379s`. A prepared 2D
path would bring it to sub-5ms, matching 3D behavior. Combined with the Goal
639 any-hit early-exit kernel, a prepared 2D any-hit path would be the best
available HIPRT visibility primitive.

**Implementation:** Add `PreparedRayHitcount2D` struct (analogous to
`PreparedRayHitcount3D`) and add a corresponding `PreparedRayAnyhit2D` struct.
The 2D kernel uses a custom intersection function (`intersectRtdlTriangle2D`)
and `hiprtGeomCustomTraversalAnyHit`, so function-table setup is required.

**Risk:** Low. Pattern is fully established by Goal 565. Custom intersection
function already exists in `rtdl_hiprt_kernels.cpp`.

### 2. Prepared Any-Hit (High value, Low risk)

**What:** Add prepared path for `ray_triangle_any_hit` (2D and 3D) that
combines prepared geometry reuse with the Goal 639 early-exit kernel.

**Why high value:** Without a prepared path, the any-hit early exit has zero
measured benefit because setup dominates. With a prepared path, early exit
provides a real query-time reduction versus hit-count for sparse-hit scenes.

**Implementation:** Add `PreparedRayAnyhit3D` struct analogous to
`PreparedRayHitcount3D` but compiling the `RtdlRayAnyhit3DKernel` instead.
For 2D, add `PreparedRayAnyhit2D` using the 2D custom intersection path.

**Risk:** Low. The kernel logic already exists (Goal 639). Only the prepared
wrapper is missing.

### 3. Prepared 2D Nearest-Neighbor (Medium value, Low risk)

**What:** Add a prepared 2D fixed-radius context analogous to the Goal 566
prepared 3D context.

**Why medium value:** 2D NN is a real workload, but the 3D prepared path
already proves the pattern. The payoff is coverage parity, not a novel
mechanism.

**Risk:** Low. The `intersectRtdlPointRadius2D` kernel and AABB expansion
logic for 2D points are already in `rtdl_hiprt_kernels.cpp`.

### 4. Native GPU Aggregation for grouped_count and grouped_sum (Medium value, Medium risk)

**What:** Move the aggregation step for `grouped_count` and `grouped_sum` from
Python host-side into a GPU reduction kernel launched after the row-discovery
pass.

**Why medium value:** Goal 568 shows prepared query times already at `2ms`
for 100k rows. Host-side aggregation adds Python dict iteration over matched
rows. For very large groups or very large tables, this becomes the bottleneck.

**Risk:** Medium. Requires a second kernel pass or atomic reduction into a
device group-key array. Text group keys are already encoded to integer domains
at prepare time, so device-side groupby on integer keys is feasible. Must
preserve exact parity with Python reference aggregation semantics.

### 5. Shared HiprtRuntime Across Prepared Contexts (Medium value, Medium risk)

**What:** Each `PreparedXxx` struct currently creates its own `HiprtRuntime`
(Orochi context + HIPRT context). A shared context pool or passed-in context
would reduce per-prepared-object overhead.

**Why medium value:** For apps that hold many prepared objects simultaneously
(e.g., multiple prepared scenes plus a prepared NN set plus a prepared DB
table), the current design multiplies context creation and device memory
overhead.

**Risk:** Medium. Context sharing requires lifetime management. The current
design is simple and correct; refactoring to shared contexts must not introduce
use-after-free or context mismatch.

### 6. Prepared Spatial Overlay and Polygon Workloads (Medium value, Medium risk)

**What:** Add prepared paths for `segment_intersection`, `point_in_polygon`,
`overlay_compose`, `segment_polygon_hitcount`, and `point_nearest_segment`.

**Why medium value:** These are all in the 18-workload matrix and all pay
the same `0.38–0.42s` cold-call overhead (Goal 560). Prepared versions would
bring them to millisecond-class.

**Risk:** Medium. These use complex custom intersection kernels
(`intersectRtdlSegment2D`, `intersectRtdlOverlayCandidate2D`,
`intersectRtdlSegmentPolygon2D`). The overlay kernel also has nested
polygon-polygon LSI checks that may dominate at large polygon counts.

### 7. Deterministic Parallel BFS (Low value, High risk)

**What:** Replace the serialized global-dedupe BFS traversal with a
two-pass deterministic reduction (e.g., sort-and-reduce or prefix sum over
candidate rows).

**Why low value now:** BFS prepared query is `20ms` vs `0.6ms` reference CPU
and `5ms` OptiX on this fixture. BFS is not a typical high-frequency RTDL
workload and the current deterministic dedupe requirement constrains design
choices.

**Risk:** High. Deterministic parallel BFS requires careful correctness
preservation. A nondeterministic atomic race path exists but cannot be used for
CPU parity. This is future work, not near-term optimization.

### 8. PTX / Kernel Cache to Disk (Low value, Medium risk)

**What:** Cache compiled ORORTC/PTX output to disk and skip recompilation on
subsequent process restarts.

**Why low value:** Prepared paths already amortize JIT cost across repeated
queries within a process. Cross-process caching only helps the cold-start case.
The current `hiprtBuildTraceKernelsFromBitcode` path with `false` (non-cached)
flag already compiles from source.

**Risk:** Medium. Requires stable cache key derivation and invalidation on
source/driver changes.

---

## Workload-Specific Recommendations

### Ray/Visibility Workloads

Current state:
- 3D hit count: prepared path exists (Goal 565).
- 3D any-hit: native early-exit kernel exists (Goal 639); no prepared path.
- 2D hit count: no prepared path.
- 2D any-hit: native early-exit kernel exists (Goal 639); no prepared path.

Recommendations:
- Highest priority: add prepared 2D hit count and 2D any-hit.
- Second priority: add prepared 3D any-hit.
- When comparing any-hit vs hit-count performance, use prepared paths for both
  and report scenes at different hit densities.
- A scalar blocked-ray count path (analogous to Apple RT Goal 666) would be a
  natural next step after prepared any-hit is in place: early-exit kernel +
  device-side atomic count + no row materialization.

### Nearest-Neighbor Workloads

Current state:
- 3D fixed-radius and kNN: prepared path exists (Goal 566).
- 2D fixed-radius and kNN: no prepared path.

Recommendations:
- Add prepared 2D NN following the Goal 566 pattern.
- Both 2D and 3D kNN currently use a 64-element stack on the device; `k_max >
  64` silently returns 0 results. This should either raise an error in the
  Python layer or use dynamic device memory for larger k.
- For neighbor density use cases (count only), add a prepared count-only path
  that does not materialize neighbor IDs and distances.

### Graph Workloads

Current state:
- BFS and triangle match: prepared path exists (Goal 567).
- BFS deterministic dedupe is serialized to a single thread.

Recommendations:
- Triangle match is in good shape (261x speedup, close to OptiX/Vulkan on
  small fixture).
- BFS is correct but still slow relative to CPU/OptiX/Vulkan on this fixture.
  Profile whether the bottleneck is the serial dedupe kernel, the device-to-host
  transfer, or Python row materialization before attempting a new BFS design.
- Do not use HIPRT graph workloads for large dense graphs until the OOM risk
  (noted in Goal 669 playbook as prior evidence) is profiled at production scale.

### DB-Style Workloads

Current state:
- conjunctive_scan, grouped_count, grouped_sum: prepared path exists (Goal 568).
- Aggregation for grouped workloads is host-side after GPU row discovery.

Recommendations:
- The `2ms` prepared query time for 100k rows is already compelling. Pursue
  device-side aggregation only if profiling shows host aggregation dominating at
  larger table sizes or larger group-key cardinalities.
- DB match kernel currently maps each row to its own AABB at `x=row_index` and
  queries that AABB to find itself; this is self-referential but structurally
  correct. A future optimization could replace this with a simple flat CUDA
  kernel for the scan pass, bypassing HIPRT traversal for predicate filtering
  where BVH provides no spatial acceleration benefit.
- String predicates are bounded by the prepared text encoding domain; document
  this clearly in user-facing API.

### Spatial Overlay / Polygon Workloads

Current state:
- All spatial overlay and polygon workloads (LSI, PIP, overlay, segment-polygon,
  point-nearest-segment) are one-shot only with `0.37–0.42s` cold-call time.

Recommendations:
- Prepared polygon geometry reuse would bring these to millisecond-class,
  matching the pattern of other prepared workloads.
- The overlay kernel (`RtdlOverlay2DKernel`) performs a full LSI and PIP test
  inside the custom traversal loop, meaning candidate discovery and exact
  refinement happen in one kernel. Consider separating AABB candidate discovery
  from exact intersection computation for large polygon counts.
- Polygon input is complex; any prepared path must handle vertex-buffer device
  upload and polygon-ref device upload separately.

---

## Mechanism Honesty Boundaries

### HIPRT on NVIDIA Through Orochi vs AMD GPU

All performance evidence across Goals 560, 565, 566, 567, 568, and 639 was
collected on:

- Host: `lx1`, Linux
- GPU: NVIDIA GeForce GTX 1070
- Backend: HIPRT/Orochi CUDA mode (`ORO_API_CUDA`, `hiprtDeviceNVIDIA`)

The `create_runtime()` function in `rtdl_hiprt_prelude.h` explicitly detects
the device name and sets `hiprtDeviceNVIDIA` or `hiprtDeviceAMD` accordingly.
This is correct and legitimate use of HIPRT through Orochi. It is not AMD GPU
validation.

**Allowed:** HIPRT backend is available and performant on NVIDIA/CUDA/Orochi.

**Disallowed:** Do not claim AMD GPU validation, AMD RDNA RT-unit performance,
or any AMD-specific behavior from these results.

### GTX 1070 Has No Hardware RT Cores

NVIDIA hardware RT cores begin with Turing (RTX 2000 series). GTX 1070 is
Pascal. All traversal in these results is shader-based CUDA traversal, not
hardware-accelerated BVH traversal. HIPRT uses its own BVH implementation
executed as CUDA code on this hardware.

**Allowed:** Prepared HIPRT traversal is fast enough for repeated-query
workloads on CUDA hardware without RT cores.

**Disallowed:** Do not claim RT-core acceleration from these results.

### Float Precision on Device

All HIPRT device structs use `float` (single precision):
`RtdlHiprtRay3DDevice`, `RtdlHiprtRay2DDevice`, `RtdlHiprtTriangle2DDevice`,
`RtdlHiprtPoint3DDevice`, etc. Host structs and Python use `double`. Conversion
happens at pack/upload time.

**Implication:** For workloads with large absolute coordinate values or
precision-sensitive geometry (e.g., UTM coordinates, high-density collision
meshes), device float precision may diverge from double reference values. Test
fixtures currently use normalized or small-range inputs.

**Required disclosure:** Float precision boundary must be documented in
HIPRT-specific performance claims, especially for geospatial or robotics apps
that use large coordinate systems.

### kNN k_max > 64 Silent Failure

`RtdlFixedRadiusNeighbors3DKernel` and `RtdlFixedRadiusNeighbors2DKernel` both
contain:

```cpp
if (k_max > 64u) {
    counts[index] = 0u;
    return;
}
```

Apps that request `k_max > 64` silently receive zero results. This is not
documented in the Python API and is a correctness boundary, not a performance
boundary.

**Required action before release claims:** Either raise a Python-level error
for `k_max > 64`, or extend the kernel to use dynamic device memory.

---

## Risks and Blockers

### Risk 1: OOM at Large Scale (Blocker for Large-Scale Claims)

Goal 669 playbook records: "previous large graph evidence showed
`std::bad_alloc`." This OOM risk has not been systematically profiled for large
prepared contexts. Before claiming prepared graph, DB, or large-NN performance
at production scale, device memory growth for large inputs must be measured.

**Action required before production scale claims:** Run large-fixture memory
profiling (`oroMemGetInfo` or `nvidia-smi`) for prepared graph CSR and prepared
DB table at representative production sizes.

### Risk 2: No AMD GPU Validation

HIPRT is primarily positioned for AMD GPU support. All evidence is
NVIDIA/Orochi. Until an AMD GPU result exists, HIPRT performance claims must
not generalize to AMD hardware.

**Action required before AMD claims:** Run the same prepared-path benchmark
on an AMD GPU through the `hiprtDeviceAMD` path and report separately.

### Risk 3: Prepared Context Isolation

Each `PreparedXxx` struct creates its own `HiprtRuntime` (Orochi device context
+ HIPRT context). Apps that hold many prepared objects concurrently may exhaust
device contexts or fragment device memory. This risk is not measured.

**Action required before multi-prepared-object apps:** Profile device context
count and peak device memory for apps holding multiple concurrent prepared
objects.

### Risk 4: kNN Silent Zero-Result at k_max > 64

Described above under mechanism boundaries. This is a correctness blocker for
any claim that HIPRT supports arbitrary kNN queries.

### Risk 5: BFS Prepared Query Still 20ms vs 5ms OptiX

Prepared BFS is correct but 4x slower than OptiX and 30x slower than CPU
Python reference on the tested small fixture. For apps where BFS query
frequency is high, HIPRT BFS is not yet competitive in the prepared state.
Claims about HIPRT BFS performance should be bounded to the measured fixture.

---

## Verdict

**ACCEPT WITH NOTES** for using this report as a HIPRT optimization roadmap.

### What Is Accepted

The roadmap is technically grounded. The playbook principles from Goal 669
transfer directly to HIPRT:

- Prepared contexts eliminate the dominant JIT/setup overhead.
- Output-contract reduction (count vs rows) is the next high-value step after
  prepared paths are in place for all workloads.
- The prepared pattern is proven and validated on Linux for ray/triangle, 3D
  NN, graph CSR, and DB table workloads.
- Performance numbers are bounded, honest, and properly cite the hardware
  mechanism.

The most valuable near-term optimizations are prepared 2D ray/triangle,
prepared 2D any-hit, and prepared 2D NN — all low-risk extensions of existing
patterns.

### Notes That Qualify the Accept

1. **OOM at large scale is unquantified.** No claim about large-scale HIPRT
   performance should be made before device memory growth is profiled.

2. **kNN k_max > 64 is a silent correctness bug** that must be fixed (error or
   dynamic memory) before any kNN performance claim is considered correct.

3. **AMD GPU validation is absent.** All evidence is NVIDIA/Orochi. The roadmap
   is valid for NVIDIA CUDA targets; it is not yet a validated roadmap for the
   AMD hardware HIPRT is primarily designed for.

4. **Float precision boundary must be disclosed** in any HIPRT performance
   claim targeting precision-sensitive workloads.

5. **BFS prepared performance is not competitive with Embree/OptiX/Vulkan**
   on the tested fixture. Claims about HIPRT BFS performance should be bounded
   to the one-shot-vs-prepared speedup narrative, not backend-vs-backend
   comparisons.

None of these notes block the roadmap. They are disclosure requirements for
claims derived from the roadmap.
