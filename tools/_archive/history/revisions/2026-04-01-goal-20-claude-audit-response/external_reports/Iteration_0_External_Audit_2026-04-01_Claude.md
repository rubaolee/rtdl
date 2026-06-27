# RTDL Project Audit Report

---

## What It Is

A Python-hosted DSL for non-graphics ray tracing spatial queries. Users define kernels declaratively; the system compiles them to optimized native backends (currently CPU reference and Embree).

---

## Architecture

```
User Python code (@rt.kernel)
        ↓
Frontend (api.py, types.py) — validation, geometry layouts, type system
        ↓
IR (ir.py) — CompiledKernel, RayJoinPlan
        ↓
Lowering (lowering.py) — workload-specific backend plans
        ↓
Runtime Execution: cpu (reference.py) | embree (embree_runtime.py)
```

---

## Supported Workloads (6)

| Workload | Description | Acceleration |
|---|---|---|
| `lsi` | Line segment intersection | BVH |
| `pip` | Point-in-polygon | BVH |
| `overlay` | LSI + PIP composition | BVH |
| `ray_tri_hitcount` | Ray vs. triangle hits | BVH |
| `segment_polygon_hitcount` | Segment vs. polygon hits | **CPU loop** |
| `point_nearest_segment` | Nearest segment query | **CPU loop** |

---

## Strengths

**Architecture & Design**
- Clean layer separation (frontend → IR → lowering → runtime), each independently testable
- Frozen dataclasses throughout — immutability by design, prevents accidental mutation
- JSON-serializable IR with schema validation (`rayjoin-plan-v1alpha1.json`)
- Role distinction (build vs. probe) clearly maps to BVH construction semantics

**API**
- Pythonic decorator-based kernel definition reads naturally
- Informative error messages with specific guidance
- Multiple execution paths for different use cases:
  - **dict**: easy, Python-friendly, slower
  - **raw**: fast, direct native row access
  - **prepared**: compiled-once for repeated execution

**Testing & Validation**
- 18 test files covering all major paths
- Cross-backend parity tests (CPU reference vs. Embree) — critical for correctness
- Golden file tests for generated code regression
- Fixture-based tests enable reproducibility with real geographic data

**Performance**
- Raw and prepared paths are within ~5–10% of native C++ + Embree
- Dict path is slower but acceptable for development/debugging

---

## Issues

### Critical

**1. Two workloads use CPU loops instead of BVH**
`segment_polygon_hitcount` and `point_nearest_segment` fall back to `native_loop` acceleration. For large datasets this significantly underperforms, defeating the purpose of the ray tracing backend. These should be prioritized for BVH-based implementation.

---

### High Priority

**2. No exact/robust geometry mode**
Only `float_approx` precision is implemented; `exact=True` is explicitly rejected at lowering time. The fixed 1e-7 epsilon is insufficient for high-precision geographic or CAD workloads. No per-query precision control.

**3. Extensibility doesn't scale**
Adding a new workload requires coordinated changes across at minimum: `api.py`, `lowering.py`, `codegen.py`, `runtime.py`/`embree_runtime.py`, and `reference.py`. There is no plugin/registry pattern — the architecture will become difficult to maintain beyond ~8–10 workloads.

**4. Embree coupling is fragile**
- 1135-line `embree_runtime.py` with heavy ctypes pointer management
- Hardcoded library paths (Homebrew macOS); no portable discovery mechanism initially (partially fixed)
- No abstraction layer — swapping Embree for another library requires rewriting this file
- Error handling via C string buffers is error-prone

---

### Medium Priority

**5. Silent output truncation**
When the output buffer overflows (atomic increment design), results are silently truncated. No warning, no error — potential silent data loss in production.

**6. No batch or kernel fusion support**
All execution is single-kernel and synchronous. No way to amortize BVH construction across multiple queries or fuse related kernels. This limits throughput for multi-step workloads.

**7. No CI/CD or cross-platform testing**
Tests appear to run manually on macOS + Homebrew Embree. No evidence of automated testing, Linux support, or Windows compatibility.

---

### Low Priority

**8. Code duplication**
- Pack/unpack functions (`pack_segments`, `pack_points`, etc.) follow identical patterns across 5 geometry types — a factory or metaclass approach would reduce this
- Lowering functions across workloads share boilerplate that could use a template method pattern

**9. Incomplete type coverage**
Type hints are present but incomplete. No `py.typed` marker, no pydantic models for IR validation, limited IDE support for compiled plan objects.

**10. Missing documentation**
- No formal semantics for predicates (e.g., exact definition of "contains" at boundary)
- No troubleshooting guide for CPU/Embree parity mismatches
- No guidance on when to choose raw vs. dict vs. prepared paths

---

## Recommended Priorities

| Priority | Action |
|---|---|
| 1 | Implement BVH-based execution for `segment_polygon_hitcount` and `point_nearest_segment` |
| 2 | Refactor workload handling to a plugin/registry pattern |
| 3 | Fix silent truncation — raise error or warning on buffer overflow |
| 4 | Abstract the Embree binding into a backend interface |
| 5 | Add exact/robust arithmetic mode |
| 6 | Set up CI with automated cross-backend parity tests |
