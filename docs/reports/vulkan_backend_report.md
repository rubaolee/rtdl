# Vulkan RT Backend: Design, Implementation, and Revision History

**Project:** rtdl-latest  
**Author:** Rubao Lee  
**Date:** 2026-04-02  
**Target hardware:** NVIDIA GeForce GTX 1070, driver 580.126.09, host 192.168.1.20  

---

## 1. Motivation

The rtdl project already had two GPU backends — OptiX (NVIDIA-only, requires CUDA) and Embree (CPU-only). The goal of this work was to add a third backend using **Vulkan KHR ray-tracing extensions**, providing a path to GPU acceleration on any Vulkan-capable driver without a CUDA dependency.

Key requirements:
- Same C ABI as the OptiX backend (identical struct layouts, same six workloads, same `rtdl_vulkan_` prefix convention)
- Same Python public API as `optix_runtime.py` (swap `optix` → `vulkan` throughout)
- Target `VK_KHR_ray_tracing_pipeline` + `VK_KHR_acceleration_structure` (KHR, not NV)
- Runtime GLSL → SPIR-V compilation via **shaderc** (mirrors NVRTC's role for OptiX)
- Build with a single `make build-vulkan` invocation

---

## 2. Architecture

### 2.1 Files added

| File | Role |
|---|---|
| `src/native/rtdl_vulkan.cpp` | C++ backend (~1,800 lines); all GPU logic, GLSL shaders embedded as strings |
| `src/rtdsl/vulkan_runtime.py` | Python ctypes binding; mirrors `optix_runtime.py` |
| `Makefile` (modified) | Added `build-vulkan` target and Vulkan SDK detection |
| `src/rtdsl/__init__.py` (modified) | Re-exports `run_vulkan`, `prepare_vulkan`, `VulkanRowView`, etc. |

### 2.2 C ABI

The C ABI is identical in struct layout to `rtdl_optix.cpp`. Every function is prefixed `rtdl_vulkan_`:

```c
// Input geometry (same as OptiX)
struct RtdlSegment    { uint32_t id; double x0, y0, x1, y1; };
struct RtdlPoint      { uint32_t id; double x, y; };
struct RtdlPolygonRef { uint32_t id, vertex_offset, vertex_count; };
struct RtdlTriangle   { uint32_t id; double x0,y0,x1,y1,x2,y2; };
struct RtdlRay2D      { uint32_t id; double ox,oy,dx,dy,tmax; };

// Entry points (8-arg form; last two are error_out, error_size)
int rtdl_vulkan_run_lsi(..., char* error_out, size_t error_size);
int rtdl_vulkan_run_pip(..., char* error_out, size_t error_size);
int rtdl_vulkan_run_overlay(..., char* error_out, size_t error_size);
int rtdl_vulkan_run_ray_hitcount(..., char* error_out, size_t error_size);
int rtdl_vulkan_run_segment_polygon_hitcount(..., char* error_out, size_t error_size);
int rtdl_vulkan_run_point_nearest_segment(..., char* error_out, size_t error_size);
void rtdl_vulkan_free_rows(void* rows);
```

All C++ exceptions are caught at each entry point; the error message is written to `error_out` and the function returns non-zero.

### 2.3 Singleton Vulkan context

A global `VkContext` is initialized lazily via `std::call_once`:

```cpp
struct VkContext {
    VkInstance       instance;
    VkPhysicalDevice phys_dev;
    VkDevice         device;
    VkQueue          queue;
    uint32_t         queue_family;
    VkCommandPool    cmd_pool;
    VkFunctions      fns;         // extension function pointers
    VkPhysicalDeviceRayTracingPipelinePropertiesKHR rt_props;
    uint32_t         handle_size, handle_align;
};
```

Device selection prefers a discrete GPU that advertises both `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`. Seven device extensions are enabled:

```
VK_KHR_acceleration_structure
VK_KHR_ray_tracing_pipeline
VK_KHR_deferred_host_operations
VK_KHR_buffer_device_address
VK_EXT_descriptor_indexing
VK_KHR_spirv_1_4
VK_KHR_shader_float_controls
```

Extension function pointers are loaded via `vkGetDeviceProcAddr`; base Vulkan functions come from `-lvulkan` at link time.

### 2.4 Acceleration structure strategy

All six workloads use **custom AABB geometry** (`VK_GEOMETRY_TYPE_AABBS_KHR`) for the BLAS, allowing custom intersection shaders to perform exact 2D geometric tests. Each AABB is padded by `kAabbEps = 1e-4f` in the XY plane and spans `z ∈ [−0.5, 0.5]`.

The TLAS is rebuilt per call (no persistent scene). A two-level hierarchy (BLAS + TLAS) is used uniformly across all workloads.

### 2.5 Per-workload RT pipelines

Each workload has its own RT pipeline, built lazily on first use via `std::call_once`. Pipelines are cached for the lifetime of the process. The pipeline builder compiles GLSL to SPIR-V at runtime using **shaderc**:

```cpp
static RtPipeline build_rt_pipeline(
    VkContext* ctx,
    const char* rgen_glsl, const char* rmiss_glsl,
    const char* rint_glsl,  const char* rahit_glsl,
    const char* rgen_name,  const char* rmiss_name,
    const char* rint_name,  const char* rahit_name,
    uint32_t binding_count);
```

Each pipeline has three shader groups: raygen (index 0), miss (index 1), hitgroup (index 2: rint + rahit).

### 2.6 Shader Binding Table

The SBT is a single buffer with three entries aligned to `shaderGroupHandleAlignment`. Handles are copied from the pipeline with `vkGetRayTracingShaderGroupHandlesKHR`.

### 2.7 Descriptor sets

Each workload call allocates a transient descriptor set (one pool per call, destroyed after submission). Bindings follow a standard layout:

| Binding | Contents |
|---|---|
| 0 | TLAS (`accelerationStructureEXT`) |
| 1 | Output buffer (std430) |
| 2 | Atomic counter (uint) |
| 3 | Uniform params (nprobes, capacity) |
| 4 | Probe geometry buffer (float[]) |
| 5 | Build geometry buffer (float[]) |

### 2.8 Workload implementations

#### LSI (segment-segment intersection)
- **Build:** AABB per right segment.
- **Probe:** One ray per left segment. Origin = segment start, direction = `end − start` (unnormalized), tmax = 1.0. The unnormalized direction encodes the segment endpoint in parametric form.
- **Intersection shader:** Full Cramér's-rule segment-segment test. Passes `(buildIdx, ix, iy)` as `hitAttributeEXT`.
- **Anyhit shader:** Atomically writes `GpuLsiRecord` to output buffer; calls `ignoreIntersectionEXT` to continue past this hit and find all intersections.

#### PIP (point-in-polygon)
- **Build:** AABB per polygon (tight bounding box over all vertices).
- **Probe:** Vertical ray (dir = (0,1,0), tmax = 1e30) per point.
- **Intersection shader:** Ray-cast parity test over all polygon edges; reports intersection if odd crossing count.
- **Anyhit shader:** Writes to pre-allocated `GpuPipRecord[npoints × npolygons]` array indexed by `(probeIdx × npolygons + primIdx)`. Calls `ignoreIntersectionEXT`.

#### Overlay (polygon-polygon)
- **Build:** AABB per right polygon.
- **Probe:** One ray per (left polygon, edge) pair; direction encodes the edge (same unnormalized trick as LSI).
- **Intersection shader:** Full LSI test of probe edge against all right polygon edges.
- **Anyhit shader:** Sets `output[lpidx × right_count + rpidx].requires_lsi` atomically; calls `ignoreIntersectionEXT`.

#### RayHitCount
- **Build:** AABB per triangle.
- **Intersection shader:** Möller–Trumbore ray-triangle intersection in 2D (expanded to 3D with z=0 plane).
- **Anyhit shader:** Atomically increments per-ray hit counter; calls `ignoreIntersectionEXT`.

#### SegmentPolygonHitcount
- Structurally identical to LSI but probes are segments and build geometry is polygon edge AABBs. Anyhit increments per-segment hit counter.

#### PointNearestSegment
- Does not map to ray traversal (requires global nearest-neighbor search). Implemented as a **Vulkan compute shader**: one workgroup per point, each thread tests a subset of segments, result reduced with shared memory. Dispatched via `vkCmdDispatch`.

### 2.9 GPU ↔ CPU data flow

All geometry is converted from double-precision (Python/CPU) to float32 (GPU) during upload. Output records are copied back to a host-visible buffer after `vkQueueWaitIdle` and handed to Python as a ctypes pointer. Python calls `rtdl_vulkan_free_rows` to release the allocation.

---

## 3. GLSL vs CUDA translation notes

| CUDA / OptiX | GLSL / Vulkan |
|---|---|
| `optixGetLaunchIndex().x` | `gl_LaunchIDEXT.x` |
| `optixGetPrimitiveIndex()` | `gl_PrimitiveID` |
| Payload registers | `rayPayloadEXT` / `rayPayloadInEXT` |
| Hit data | `hitAttributeEXT` struct |
| `optixReportIntersection(t, kind)` | `reportIntersectionEXT(t, kind)` |
| `optixIgnoreIntersection()` | `ignoreIntersectionEXT;` (statement, not function call) |

The most important structural difference: **Vulkan intersection shaders cannot read or write the ray payload** (unlike OptiX). The probe index is recovered inside the intersection shader via `gl_LaunchIDEXT.x`, and intersection-specific data (build primitive index, intersection coordinates) is communicated to the anyhit shader via a `hitAttributeEXT` struct.

---

## 4. Build system

`make build-vulkan` invokes `g++` with:

```makefile
VULKAN_CXXFLAGS = -std=c++17 -O3 -shared -fPIC -I$(VULKAN_INCLUDE)
VULKAN_LDFLAGS  = -L$(VULKAN_LIB_DIR) -lvulkan $(SHADERC_LINK)
```

`VULKAN_SDK` defaults to `/usr`. The Makefile probes for `libshaderc.so` (shared, preferred) before falling back to `libshaderc_combined.a` (static archive).

---

## 5. Revision history

### R0 — Initial generation
**What:** Complete first-draft C++ backend and Python binding generated in one pass, based on the OptiX backend as a reference.

**Key design decisions made:**
- AABB geometry for all six workloads (mirrors OptiX custom primitives)
- shaderc for runtime SPIR-V compilation (mirrors NVRTC)
- `hitAttributeEXT` struct to work around Vulkan's restriction that intersection shaders cannot access ray payload
- Compute shader for PointNearestSegment (not a ray-tracing problem)
- `VK_NO_PROTOTYPES` was initially included to load all Vulkan symbols dynamically

### R1 — Remove `VK_NO_PROTOTYPES`; fix bootstrapping loop
**Problem:** With `VK_NO_PROTOTYPES` defined, base Vulkan calls like `vkCreateInstance` and `vkEnumeratePhysicalDevices` were undefined at link time. Attempting to load `vkGetInstanceProcAddr` via itself was circular.

**Fix:** Removed `#define VK_NO_PROTOTYPES`. Base Vulkan functions are provided by `-lvulkan`. Only extension functions (KHR suffix) are loaded via `vkGetDeviceProcAddr`.

### R2 — Fix `PFN_vkGetPhysicalDeviceProperties2KHR` type mismatch
**Problem:** `VkFunctions` declared `vkGetPhysicalDeviceProperties2` as `PFN_vkGetPhysicalDeviceProperties2KHR` (KHR suffix), which is a distinct typedef.

**Fix:** Changed to `PFN_vkGetPhysicalDeviceProperties2` (core 1.2 type, promoted from KHR).

### R3 — Remove stale `VkContext` fields
**Problem:** `VkContext` retained `get_inst_proc` and `get_dev_proc` fields from an earlier design that loaded all symbols dynamically. These were never initialized in the final design and wasted space.

**Fix:** Removed both fields.

### R4 — Initialize `rt_props` before use
**Problem:** `ctx->rt_props.sType` was set but the rest of the struct was uninitialized. Also, the fallback path for `vkGetPhysicalDeviceProperties2` was missing.

**Fix:** Added `ctx->rt_props = {};` before setting `sType`; added fallback to call the core `vkGetPhysicalDeviceProperties2` directly if the function pointer is null.

### R5 — Switch from `libshaderc_combined.a` to `libshaderc.so` (deployment fix)
**Problem:** On the test host (Ubuntu), linking `librtdl_vulkan.so` against `libshaderc_combined.a` produced an undefined symbol `_ZN7glslang8TProgram10getInfoLogEv` at load time. The static archive did not pull in all glslang symbols when embedded in a shared library.

**Fix:** Updated Makefile to prefer `-lshaderc` (shared library) over `-lshaderc_combined`. The Makefile now probes for `libshaderc.so` first.

### R6 — Fix `ignoreIntersectionEXT()` syntax error in all anyhit shaders
**Problem:** All five anyhit shaders wrote `ignoreIntersectionEXT();` (with parentheses). The shaderc GLSL compiler rejected this at runtime:

```
GLSL compile error (lsi.rahit): lsi.rahit:26: error: '' : syntax error,
  unexpected LEFT_PAREN, expecting SEMICOLON
```

**Root cause:** In GLSL ray tracing (`GL_EXT_ray_tracing`), `ignoreIntersectionEXT` and `terminateRayEXT` are **statements** (like `discard` in fragment shaders), not function calls. They take no parentheses.

**Fix:** Changed all five occurrences from `ignoreIntersectionEXT();` to `ignoreIntersectionEXT;`.

**Shaders affected:** kLsiRahit, kPipRahit, kOverlayRahit, kRhcRahit, kSphRahit.

### R7 — Fix `VK_GEOMETRY_OPAQUE_BIT_KHR` blocking anyhit invocation
**Problem:** After fixing R6, the library compiled and loaded successfully and Vulkan initialization succeeded, but all workloads returned 0 results. The GLSL shaders appeared correct, yet no output was written.

**Root cause:** `build_aabb_blas()` set `geom.flags = VK_GEOMETRY_OPAQUE_BIT_KHR`. For opaque geometry, Vulkan **skips the anyhit shader entirely**: the intersection shader reports a hit, the driver commits it immediately (without calling anyhit), and the ray terminates at the closest hit. Because all output writes happen inside the anyhit shader, nothing was ever written to the result buffers.

**Fix:** Changed to `geom.flags = 0` (non-opaque). With non-opaque geometry:
1. Intersection shader reports a candidate hit.
2. Anyhit shader is invoked.
3. Anyhit writes the result to the output buffer.
4. Anyhit calls `ignoreIntersectionEXT` to reject the hit and continue traversal.
5. All intersections are found, not just the first.

**Verification:** After this fix, a two-segment LSI test (`(−1,0)→(1,0)` crossing `(0,−1)→(0,1)`) correctly returned 1 hit at `(0.0000, 0.0000)`. A multi-segment test and a PIP test also passed:

```
LSI: 2 hits
  left=0 right=10 @ (0.0000, 0.0000)
  left=0 right=11 @ (0.5000, 0.0000)

PIP: 2 rows
  pt=0 poly=0 contains=1   (point inside square)
  pt=1 poly=0 contains=0   (point outside square)
```

---

## 6. Known limitations and future work

- **No persistent scene caching.** BLAS and TLAS are rebuilt on every call. For repeated queries against the same build geometry, caching the BLAS would eliminate most GPU upload time.
- **Output buffer capacity is capped.** LSI output is pre-allocated to `left_count × right_count` records. Pathological inputs with near-complete intersection could truncate results (excess hits are silently dropped; the atomic counter simply stops writing past capacity).
- **PointNearestSegment uses brute-force compute.** The current compute shader is O(npoints × nsegments). A spatial index (e.g., a BVH over segments queried per point) would scale better.
- **Float32 only on GPU.** All geometry is converted to float32 before GPU upload. High-precision inputs near floating-point resolution limits may accumulate rounding error.
- **Single queue, synchronous execution.** All work is submitted to one queue with `vkQueueWaitIdle`. Pipelining multiple workloads or overlapping CPU/GPU work would improve throughput.
