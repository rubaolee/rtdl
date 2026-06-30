# Goal1042 Primary Architecture Feedback: v1.5 Generic Primitives

Date: 2026-04-27

## Scope

This is the primary-project review of the proposed RTDL v1.0 -> v1.5 -> v2.0 architecture direction for decoupling C++/CUDA engines from hardcoded application logic.

Requested handoff path:

- `docs/handoff/gemini_arch_review_request_2026-04-26.md`

Local finding:

- That exact handoff file was not present in this checkout at review time.

Reviewed architecture documents available in this repo:

- `docs/reports/gemini_rtdl_v1_5_generic_primitives_design_2026-04-26.md`
- `docs/reports/gemini_rtdl_intermediate_architectural_solutions_2026-04-26.md`

Because the handoff file was missing, this review answers the four architecture questions implied by the request: primitive sufficiency, extension-mechanism soundness, roadmap sequencing, and required changes before implementation.

## Executive Verdict

Status: `accept_direction_with_required_refinements`.

The proposed v1.5 direction is technically correct: RTDL should move from app-specific engine endpoints toward generic traversal-plus-reduction primitives. This is the right architecture for preserving RTDL's main value proposition: Python expresses workload-specific lowering, while native engines execute the heavy spatial traversal and simple reductions.

However, the current proposal is too coarse to implement directly. Before coding, the primitive set and ABI must be sharpened around result shape, grouping, predicates, payload layout, validation, backend parity, and determinism.

## Question 1: Are the Five Generic Primitives Sufficient?

Short answer: mostly yes for v1.5, but the names and contracts need refinement.

The proposed primitive set is:

- `COUNT`
- `ANY`
- `MIN_DIST`
- `SUM_PAYLOAD`
- `COLLECT_K`

This set covers the core pressure points that produced current C++ technical debt:

- fixed-radius density/count summaries;
- hotspot/coverage boolean or count summaries;
- segment/polygon hit counts;
- nearest-distance and Hausdorff threshold-style decisions;
- DB-style bounded predicate scans with scalar sums;
- candidate generation for KNN/ANN-like apps.

Required refinements:

- `MIN_DIST` should be generalized to `MIN(metric)` and paired with `MAX(metric)` or a second-stage `REDUCE_OVER_PROBES(MAX)`. Hausdorff is not just one `MIN_DIST`; it is `MAX_i MIN_j d(i,j)`.
- `SUM_PAYLOAD` should be one case of a generic `REDUCE_PAYLOAD(op=SUM|MIN|MAX|COUNT, dtype=...)`; DB apps need grouped count, grouped sum, and possibly multiple payload fields.
- `ANY` must define early-exit semantics per probe: first hit is enough, but result determinism must not depend on hit ordering unless only boolean output is exposed.
- `COUNT` must define whether it counts all hits, valid refined hits, capped hits, unique target ids, or first hit per object. These are different for DB, geometry, graph, and polygon workloads.
- `COLLECT_K` is the riskiest primitive. It is useful, but it creates memory pressure and ordering/determinism obligations. v1.5 should implement bounded `COLLECT_K` only after `COUNT`, `ANY`, and scalar reductions are stable.

Recommended v1.5 minimum:

1. `ANY_HIT`
2. `COUNT_HITS`
3. `REDUCE_FLOAT(MIN|MAX|SUM)`
4. `REDUCE_INT(COUNT|SUM)`
5. `COLLECT_K_BOUNDED` as experimental

## Question 2: Are the Extension Mechanisms Sound?

Short answer: DLPack is a strong v1.5 extension path; PTX/SPIR-V plugins should not be a v1.5 default feature.

### DLPack / Zero-Copy Handoff

Accept for v1.5 design.

This is the right escape hatch when generic reductions are insufficient but app logic still belongs above RTDL. It lets RTDL emit GPU-resident hit/candidate buffers and lets CuPy, PyTorch, Numba, or Triton perform custom compute without host round-trips.

Required constraints:

- fixed schemas for hit buffers;
- explicit lifetime ownership;
- capacity/overflow reporting;
- device id and stream semantics;
- deterministic fallback when DLPack is unavailable;
- clear statement that DLPack output is candidate data, not a public speedup claim by itself.

### Drop-in PTX / SPIR-V Plugins

Defer from core v1.5, or mark as experimental only.

The idea is valuable for power users, but it creates a large ABI and security burden:

- kernel ABI versioning;
- backend-specific behavior divergence;
- driver/toolchain compatibility;
- unsafe code loading;
- reproducibility and review difficulty;
- public-claim ambiguity when user code is injected.

Recommendation: v1.5 should define the plugin ABI document, but not make plugins the primary extension mechanism. Implement DLPack first; keep native plugins behind an explicit experimental flag and exclude them from release claims.

## Question 3: Is the v1.0 -> v1.5 -> v2.0 Roadmap Correct?

Short answer: yes.

The roadmap is the right sequencing:

- v1.0: keep custom engines where needed to prove workload viability and performance.
- v1.5: decouple hardcoded app logic into generic reductions.
- v2.0: integrate compute partners or graph/JIT systems only after the primitive model is stable.

This matters because v1.0's priority is evidence and credibility, not architectural purity. Rewriting engines before v1.0 would risk destabilizing the very app demonstrations that justify RTDL.

The v1.5 target should be framed as technical-debt reduction plus performance-preserving abstraction. It should not promise that all app logic disappears. Python lowering remains application-specific by design.

v2.0 should remain a partner-ecosystem direction, not a commitment to build an in-house compiler. RTDL should avoid becoming a general CUDA graph compiler.

## Question 4: What Must Change Before Implementation?

Do not start with a broad backend rewrite. Start with a narrow, testable primitive contract.

Required pre-implementation artifacts:

- A primitive contract doc with input geometry types, payload layout, result schema, grouping rules, and overflow behavior.
- A per-app lowering matrix mapping current v1.0 app endpoints to v1.5 primitive calls.
- A backend parity matrix for OptiX, Embree, Vulkan, HIPRT, and Apple RT.
- A claim-boundary document stating that generic primitive support is not automatically a public speedup claim.
- A migration plan that keeps v1.0 app endpoints as compatibility wrappers over v1.5 primitives where possible.

Recommended first implementation slice:

1. Implement `ANY_HIT` and `COUNT_HITS` for one geometry pair already proven in OptiX and Embree.
2. Re-express `service_coverage_gaps` and `event_hotspot_screening` through the generic primitive wrapper.
3. Verify bit/row parity against the existing app-specific path.
4. Measure whether the generic path preserves native query performance.
5. Only then extend to `SUM_PAYLOAD` and `MIN_DIST`.

Do not implement `COLLECT_K`, DLPack, or plugin ABI first. They are larger surface-area features and should follow the scalar reductions.

## Final Recommendation

Adopt the direction, but tighten the architecture before coding.

The five-primitives proposal correctly identifies the path out of hardcoded C++ app logic. The strongest near-term plan is:

- v1.0: finish credible RTX app evidence with current engines.
- v1.5: introduce generic scalar traversal reductions and migrate selected app endpoints.
- v1.5 experimental: add DLPack hit/candidate buffers.
- v2.0: evaluate Triton/Numba or other compute partners for custom reductions.

The key implementation rule: every migrated app must prove three things before the old custom endpoint can be retired:

- correctness parity;
- performance parity or acceptable overhead;
- preserved public honesty boundaries.

This design is promising because it preserves RTDL's core thesis: Python should orchestrate and lower applications, but heavy traversal and simple reductions must stay inside deeply optimized native kernels.
