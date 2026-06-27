# Goal4302: Claude Whole-Project Critical Review and Improvement Suggestions

**Reviewer:** Claude (independent read-only review, no code changes)
**Date:** 2026-06-11
**Scope:** Current `main` after v2.10/v2.11 cleanup, Embree CPU + current partner reference work
**Verdict:** `accept-with-boundary`

---

## Executive Verdict

The Python+RTDL+partner architecture is coherent and the app-agnostic engine boundary is consistently enforced. The v2.10/v2.11 claim discipline is honest and the v2.11 Embree CPU packet (Goal4298/4299) is correctly scoped. The project is not ready for a public release claim, but it is also not stuck — there is a clear next set of work. The `accept-with-boundary` verdict reflects:

1. The architecture is sound and the core evidence chain is intact.
2. Several structural hygiene issues (version string, Numba status label, legacy source tree, RTNN gap) create discoverability and consistency problems without affecting correctness.
3. Performance leadership on NVIDIA RT cores is real but currently limited to a small number of workloads with strong evidence. Several benchmarks are "adequate" rather than "compelling."

---

## Findings — Ordered by Severity

### F1 — HIGH: Numba status label contradicts benchmark matrix recommendations

**File:** `src/rtdsl/numba_partner_continuation.py:25`

```python
NUMBA_PARTNER_CONTINUATION_STATUS = V2_5_STATUS_PREVIEW_NOT_PROMOTED
```

The `numba_partner_continuation.py` module labels its own status as `V2_5_STATUS_PREVIEW_NOT_PROMOTED`, but the benchmark partner reference matrix (`docs/learn/benchmark_partner_reference_matrix.md`) actively recommends Numba for at minimum four workloads: spatial rayjoin (PIP/LSI scalar count), RT-DBSCAN (component continuation), Barnes-Hut (block-reduction force reference), and now RTNN CPU (top-k partner reference). A user reading the code will see "preview not promoted"; a user reading the matrix will see "current reference path." This is the most confusing discrepancy in the project.

Either specific Numba operations should be promoted to `stable_behavior` (e.g., `segmented_count_i64`, `grouped_argmin_f64`), or the benchmark matrix should add an explicit "preview_recommended" qualification for each recommended row. The current state asks users to trust the matrix while the code tells them the partner is experimental.

### F2 — HIGH: Legacy files populate `src/rtdsl/` alongside the current API

The `src/rtdsl/` directory contains 60+ files that are goal-tagged historical artifacts rather than current API surfaces:

```
src/rtdsl/goal23_reproduction.py
src/rtdsl/goal112_segment_polygon_perf.py
src/rtdsl/paper_reproduction.py
src/rtdsl/rayjoin_artifacts.py
src/rtdsl/section_5_6_scalability.py
src/rtdsl/v1_5_benchmark_evidence.py
src/rtdsl/v1_5_migration_inventory.py
src/rtdsl/rtnn_baselines.py, rtnn_comparison.py, rtnn_cunsearch.py ...  (6 rtnn_* files)
```

A new contributor browsing `src/rtdsl/` will find `goal112_segment_polygon_perf.py` next to `primitive_hierarchy.py` and `partner_adapters.py`. There is no way to tell which files are the current API without reading every file. This is a significant onboarding barrier and a maintenance hazard (legacy files may reference stale contracts).

### F3 — HIGH: RTNN has no Embree front door — permanent packet asymmetry

**Context:** `docs/reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md`

RTNN is the only benchmark app in the v2.11 Embree packet that cannot use Embree. The honest Numba reference fills the slot, but this creates a permanent asymmetry: every v2.11/v2.x Embree packet will require the RTNN exception row. More practically, RTNN is a neighbor-search benchmark — fixed-radius rows are an Embree strength. The `prepared_optix_ranked_summary` mode runs on OptiX, but no corresponding Embree fixed-radius ranked-summary front door exists. This is not a claim problem; it is a coverage gap.

### F4 — MODERATE: VERSION file and README describe v2.10 while v2.11 lane is active

**Files:** `VERSION:1`, `README.md:14`

`VERSION` says `v2.10`. The README says "v2.10" throughout in the current-surface section. But Goal4298 has already defined and validated the v2.11 Embree CPU packet. Tests reference `CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION = "rtdl.v2_11.current_embree_cpu_partner_reference.goal4298.v1"`. The project is operating at two version labels simultaneously. This is not a correctness problem, but a user who reads the README and then encounters v2.11 references in the source will be confused.

### F5 — MODERATE: `continuation.fixed_radius_graph` is OptiX-only; RT-DBSCAN Embree uses Python fallback

**File:** `src/rtdsl/primitive_hierarchy.py`, `continuation.fixed_radius_graph` node, `backends=("optix",)`

The v2.11 Embree RT-DBSCAN row uses `route_class: embree_cpu_rt_plus_python_continuation`, meaning the component-labeling step falls back to Python rather than using the device continuation. The OptiX path uses the `fixed_radius_graph` device continuation. Users who compare Embree and OptiX RT-DBSCAN outputs get structurally different execution paths, not just different hardware. This is not a claim problem, but it means the Embree RT-DBSCAN row does not stress-test the same architecture as the OptiX row.

### F6 — MODERATE: `continuation.predicate_aware_boundary_union` is candidate-only with OptiX backend

**File:** `src/rtdsl/primitive_hierarchy.py`, `continuation.predicate_aware_boundary_union` node, `backends=("optix",)`, `partner_ops=("numba_grouped_stream_component_labels", "cupy_direct_status_union_preview")`

This primitive is referenced by Goal4190 for RT-DBSCAN boundary-policy work. It lists both Numba and CuPy partner_ops, but CuPy's entry is labeled "preview" and the node status is `candidate_behavior`. The RT-DBSCAN "counts only mixed route" work appears to depend on a primitive that has no stable path and no Embree or CPU reference backend. Future DBSCAN improvement work cannot use this as a stable foundation.

### F7 — MODERATE: `candidate.closed_shape_topology_membership_count_2d` is CPU reference + planned OptiX only

**File:** `src/rtdsl/primitive_hierarchy.py`, `candidate.closed_shape_topology_membership_count_2d` node, `backends=("cpu_python_reference", "planned_optix")`

This is a critical primitive for the spatial rayjoin PIP path, which produces the strongest OptiX speedup evidence (~260x for LSI overlap). The primitive remains at `candidate_behavior` with no stable OptiX path. The `planned_optix` backend tag means native OptiX execution is not currently available. The spatial rayjoin benchmark's strongest evidence depends on a candidate-status primitive.

### F8 — MODERATE: `libRTS_spatial_index` Embree row takes 132s — impractical for regular regression

**Context:** Goal4298 local Linux artifact — `librts_spatial_index_embree_cpu_aabb_index` wrapper elapsed ~132s

At 132s per run, the librts spatial index benchmark cannot serve as a routine CI regression row. The current artifact captures this as the "slowest row" but does not separate a fast smoke-test row from a full-scale performance row. This makes the v2.11 Embree packet impractical to run on a regular schedule.

### F9 — LOW: README "What You Write" example uses `rt.ray_triangle_any_hit()` predicate that differs from actual API

**Files:** `README.md:76`, `examples/current/getting_started/rtdl_hello_world.py:50`

The README kernel example uses:
```python
hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit())
return rt.emit(hits, fields=["ray_id", "hit"])
```

The actual hello_world uses `rt.ray_triangle_hit_count(exact=False)` and the `"hit_count"` field name. The README example may be aspirational or slightly outdated. A new user trying to run the README snippet will fail or get a different result than expected.

### F10 — LOW: `Lib/` and `before_3958.txt` appear as untracked in git status

**Context:** git status output in the conversation header

The root-level `Lib/` directory (likely a Windows Python standard library extract) and `before_3958.txt` are untracked. `Lib/` should be in `.gitignore` if it is not. `before_3958.txt` has no obvious meaning from its name; if it is a temporary diagnostic artifact it should be deleted or documented.

### F11 — LOW: AMD HIPRT functional pod validation artifact is still pending

**File:** `docs/reports/goal3786_current_benchmark_adequacy_after_hiprt_closeout_2026-06-07.md`

All 10 benchmark apps are labeled "ready for AMD functional pod" but `docs/reports/goal3784_amd_hiprt_functional_pod_validation.json` does not exist. The multi-platform RT story requires this artifact before any AMD claim can be made.

### F12 — LOW: `partner_adapters.py` has 12 module-level mutable cache globals

**File:** `src/rtdsl/partner_adapters.py:31-41`

```python
_CUPY_COLUMNAR_PREDICATE_BATCH_KERNELS = {}
_CUPY_AABB_PAIR_OVERLAP_SUMMARY_2D_KERNEL = None
...
_NUMBA_RADIUS_GRAPH_COMPONENTS_3D_GRID_KERNELS = None
```

Lazy initialization via module-level globals works but creates hidden global state. The cache is process-wide; any test that mutates it will affect subsequent tests. This is not a correctness bug in normal single-process use, but it is a maintenance concern and makes the module harder to test in isolation.

---

## Strategic Diagnosis

**What is strong:** The architecture is the right one. Python owns the app; RTDL owns the kernel; the native engine is app-agnostic. The primitive hierarchy is the most carefully designed part of the system — the layering (execution_residency → traversal → row_emission → bounded_materialization → reduction → continuation) is coherent and the boundary between app-owned and engine-owned logic is consistently enforced. The claim discipline is excellent: multiple layers of runtime guards, test assertions, and report metadata all prevent accidental overclaiming.

**What is muddy:** The communication gap between the code-level status labels (Numba: "preview not promoted") and the user-facing matrix recommendations (Numba: "current reference path") is the biggest single coherence problem. It is not a safety risk, but it is a trust risk — users will wonder whether the project knows what state it is in. This needs resolution before any public wording about Numba.

**Where the RT-core story is real:** Spatial rayjoin LSI overlap count (~260x over dense partner), hausdorff exact-frontier, and RT-DBSCAN threshold flags plus Numba component continuation. These are the three strongest cases where NVIDIA RT hardware is clearly the right accelerator and RTDL's traversal primitive is doing real work.

**Where the RT-core story is weak or absent:** Barnes-Hut (CuPy is still faster overall), triangle counting (the segmented-lowering limitation blocks paper scale), contact manifold (adequate but no published GPU speedup evidence), and raydb_style (the "fused columnar grouped reduction" story is not clearly differentiated from just using CuPy's own groupby). Four of ten benchmark apps do not yet make a clear case for RTDL's RT-core advantage.

**The Embree CPU path is a good fallback story.** It is not distracting from NVIDIA RT-core leadership if it is positioned correctly: Embree proves the same RTDL contract works on CPU, enabling development and testing without a GPU pod. The risk is positioning Embree as an alternative to OptiX rather than as a development/testing aid. The current docs are careful about this, but the v2.11 narrative should continue to emphasize this distinction.

**The user experience is still challenging for new users.** The tutorial ladder is well-structured but requires 8 steps, source-tree setup with PYTHONPATH, knowledge of three execution backends, and an understanding of partner selection before a user can write a non-trivial program. There is no "RTDL vs. writing CUDA directly" motivation page. The `src/rtdsl/` source tree is not organized for discoverability.

---

## Prioritized Improvement Plan

### Goal A (next, no special hardware): Resolve Numba status label vs. benchmark matrix discrepancy

**What to build:** Audit the `numba_partner_continuation.py` operations that are actively recommended in the benchmark matrix. Promote `segmented_count_i64`, `segmented_sum_f64`, `grouped_argmin_f64`, `grouped_argmax_f64`, `compact_mask_i64`, and `grouped_vector_sum_f64x2` to `stable_behavior` in the hierarchy (or a new `partner_stable` status tier). Update the module-level status constant. Leave `grouped_topk_f64` at preview until device-resident implementation exists.

**Why it matters:** The gap between "preview not promoted" code and "current reference path" docs is the most damaging coherence issue for user trust. Fixing it costs nothing and immediately improves credibility.

**Acceptance tests:** `NUMBA_PARTNER_CONTINUATION_STATUS` reflects the current actual stability tier. Each promoted operation is independently listed in the primitive hierarchy with correct `status` and `backends` fields. Benchmark matrix wording matches code status.

**Hardware needed:** None.
**AI consensus:** No (single AI is sufficient for status label cleanup).

---

### Goal B (next, no special hardware): Archive legacy `src/rtdsl/` goal files

**What to build:** Move all goal-tagged, version-tagged, and paper-reproduction files in `src/rtdsl/` that are not part of the current public API to `src/rtdsl/history/` or delete them. Target candidates: `goal23_reproduction.py`, `goal112_*`, `goal114_*`, `goal116_*`, `goal118_*`, `goal128_*`, `goal139_*`, `goal228_*`, `paper_reproduction.py`, `rayjoin_artifacts.py`, `section_5_6_scalability.py`, `v1_5_*.py`, `v1_6_*.py`, `rtnn_baselines.py`, `rtnn_comparison.py`, `rtnn_cunsearch*.py`, `rtnn_duplicate_audit.py`, `rtnn_kitti*.py`, `rtnn_manifests.py`, `rtnn_matrix.py`, `rtnn_perf_audit.py`, `rtnn_reproduction.py`, `jaccard_performance_diagnostics.py`, `evaluation_matrix.py`, `evaluation_report.py`, `baseline_benchmark.py`, `baseline_contracts.py`, `baseline_summary.py`, `baseline_runner.py`.

**Why it matters:** A new contributor browsing `src/rtdsl/` needs to distinguish the current API from historical experiment files. The current mix is unsustainable as the codebase grows.

**Acceptance tests:** `ls src/rtdsl/*.py` shows only current API-relevant files. Historical files are accessible via history path. No tests that were passing before are broken.

**Hardware needed:** None.
**AI consensus:** No (mechanical archiving, not design decision).

---

### Goal C (next, no special hardware): Fix README predicate name and add v2.11 context

**What to build:** Fix `README.md:76` so the "What You Write" kernel example uses the actual current predicate name (`rt.ray_triangle_hit_count(exact=False)`) and field name (`"hit_count"`). Update the "v2.10 Source-Tree Surface" section to reflect that the v2.11 Embree CPU packet (Goal4298) is the current extension lane. Update `VERSION` to `v2.11` or use `v2.10+v2.11-dev` to avoid the dual-label confusion.

**Why it matters:** The README is the first thing a new user reads. A broken example predicate name and inconsistent version labels undermine confidence.

**Acceptance tests:** `README.md` kernel example runs as shown. `VERSION` file is consistent with the state described in current docs. No test assertions use version-specific strings that would break.

**Hardware needed:** None.
**AI consensus:** No.

---

### Goal D (local Linux): Add RTNN Embree front door

**What to build:** Add an Embree-backed `--mode embree_fixed_radius_ranked_summary` path to the RTNN benchmark app that exercises the generic prepared Embree fixed-radius rows plus a host-side or partner-side top-k continuation. Register this in the v2.11+ Embree packet registry as the RTNN Embree row, replacing the Numba exception.

**Why it matters:** RTNN is the only benchmark without Embree coverage. Closing this gap makes all 10-row Embree packets structurally uniform and removes the recurring "RTNN exception" documentation burden.

**Acceptance tests:** RTNN has an Embree front door that produces a valid JSON artifact with `uses_embree: True` and `requires_embree_library: True`. The v2.11 Embree packet no longer requires the Numba exception clause. The new row passes local Linux execution.

**Hardware needed:** Local Linux (not GPU required for Embree).
**AI consensus:** No (single implementation goal).

---

### Goal E (CUDA hardware): Implement `grouped_topk_f64` device kernel for Numba

**What to build:** Implement a proper device-resident Numba grouped top-k kernel that replaces the current host-side ranking in the RTNN Numba path. The kernel should accept `(group_ids, item_ids, scores, k)` and return ranked `(group_ids, neighbor_ids, distances, rank)` columns on device. This is the explicit "v2.11 reference debt" identified in Goal4299.

**Why it matters:** The current RTNN Numba path uses host materialization for the ranking step (`host_rank_materialization_used: True`). This is honest but means the Numba path is not genuinely device-resident for the critical ranking operation. A real device-side top-k unblocks Numba as a credible alternative to the CuPy path for ranked-neighbor workloads.

**Acceptance tests:** `host_rank_materialization_used` becomes `False` in the RTNN Numba row output. New kernel is listed in the primitive hierarchy as `stable_behavior` with `backends=("numba_cuda",)`. A same-contract comparison against the CuPy path shows competitive or better performance. No regression in existing Numba tests.

**Hardware needed:** CUDA GPU.
**AI consensus:** Recommend 2-AI for the kernel correctness design.

---

### Goal F (local Linux): Add Embree component-labeling continuation to `continuation.fixed_radius_graph`

**What to build:** Extend the `fixed_radius_graph` continuation to support an Embree CPU path. Currently this node is `backends=("optix",)` only, which means RT-DBSCAN on Embree uses Python-level components rather than the device continuation. Adding an Embree path gives both the Embree and OptiX RT-DBSCAN rows the same architectural shape (RT traversal + device continuation + result contract).

**Why it matters:** The structural difference between Embree and OptiX RT-DBSCAN paths makes it hard to attribute performance differences to hardware rather than architecture. A uniform continuation path removes this confound.

**Acceptance tests:** `continuation.fixed_radius_graph` node gains `"embree"` in its `backends` tuple. RT-DBSCAN Embree row changes `route_class` from `embree_cpu_rt_plus_python_continuation` to `embree_cpu_rt_primitive`. Test parity between Embree and CPU reference component labels.

**Hardware needed:** Local Linux.
**AI consensus:** No.

---

### Goal G (local Linux): Add small-scale `librts_spatial_index` regression row

**What to build:** Add a small-scale Embree CPU row for librts_spatial_index (e.g., 10K points, completes in <10s) as the routine regression row. The current 132s row becomes the performance evidence row. Register both in the packet: regression row for daily CI, evidence row for periodic pod runs.

**Why it matters:** A 132s CI step is 13× too slow for routine regression. The current packet has no fast gate for this benchmark.

**Acceptance tests:** New small-scale row completes in <10s on local Linux. Performance evidence row is preserved but flagged as `require_long_run=True` so CI can skip it. v2.11 packet validates both rows.

**Hardware needed:** Local Linux.
**AI consensus:** No.

---

### Goal H (NVIDIA pod): Promote `candidate.closed_shape_topology_membership_count_2d` to `stable_behavior`

**What to build:** Implement a native OptiX path for the closed-shape topology membership count primitive. This is the primitive underlying spatial rayjoin PIP count, which is one of the strongest RTDL benchmark stories. Current status is `candidate_behavior` with `backends=("cpu_python_reference", "planned_optix")`.

**Why it matters:** The spatial rayjoin ~260x speedup claim for LSI overlap count depends on a candidate-status primitive. Promoting it to `stable_behavior` with a real OptiX implementation makes the claim solid.

**Acceptance tests:** `candidate.closed_shape_topology_membership_count_2d` node status changes to `stable_behavior`. `backends` gains `"optix"`. A new pod artifact confirms correctness and measures speedup against the CPU reference. Claim boundary is updated to reflect the stable promotion.

**Hardware needed:** NVIDIA pod.
**AI consensus:** 2-AI recommended for the primitive contract design.

---

### Goal I (NVIDIA pod): AMD HIPRT functional pod validation

**What to build:** Run the Goal3785 AMD HIPRT runner against all 10 benchmark apps on an AMD GPU pod. Produce `docs/reports/goal3784_amd_hiprt_functional_pod_validation.json`.

**Why it matters:** All 10 apps are labeled "ready for AMD functional pod" but no artifact exists. The multi-platform RT story is incomplete without this evidence.

**Acceptance tests:** `goal3784_amd_hiprt_functional_pod_validation.json` exists with `all_pass: true` or explicit per-app pass/fail status. Any failures are documented and tracked.

**Hardware needed:** AMD GPU pod.
**AI consensus:** No (execution task, not design decision).

---

### Goal J (no special hardware): Write "RTDL vs. writing CUDA directly" motivation page

**What to build:** A concise motivation document (≤2 pages) showing the same spatial query written as: (a) raw CUDA C++/OptiX, (b) CuPy with manual BVH, (c) RTDL with `cpu_python_reference`. Focus on the lines-of-code difference, backend swap, and what RTDL owns versus the user. Place it in `docs/learn/rtdl_vs_direct_cuda.md` and link from the README.

**Why it matters:** The project has extensive boundary documentation but no clear "why" for users evaluating it. A new user needs to see: "Here is the thing you would have to write in CUDA. Here is what RTDL replaces." The absence of this page is the most common evaluator complaint for new DSL/runtime projects.

**Acceptance tests:** New doc exists at `docs/learn/rtdl_vs_direct_cuda.md`. README links to it. The CUDA snippet compiles and the RTDL snippet runs with `cpu_python_reference`. 2-AI review of the comparison for accuracy.

**Hardware needed:** None.
**AI consensus:** 2-AI recommended for the CUDA comparison accuracy.

---

### Goal K (no special hardware): Strengthen triangle counting with segmented-lowering implementation

**What to build:** Implement the segmented/streamed lowering for the triangle counting benchmark that allows processing of the full SIGMETRICS 2025 paper dataset. The current accepted limitation is that large graphs cannot run due to unbounded row materialization. The `candidate.streamed_graph_lowering` node in the hierarchy is the design direction.

**Why it matters:** Triangle counting is listed as a benchmark, but the "largest-dataset scalability accepted as a segmented/streamed-lowering follow-up" limitation means it cannot fully reproduce the paper-target workloads. This is the largest unsatisfied benchmark claim.

**Acceptance tests:** Triangle counting app successfully processes the full paper dataset using segmented/streamed lowering. Capacity overflow no longer occurs on large graphs. New report documents the segmented path with pod artifact.

**Hardware needed:** NVIDIA pod for performance evidence; local Linux for correctness.
**AI consensus:** 2-AI for the segmented-lowering contract design.

---

## Do Not Do Yet

1. **Do not claim package-install support** (`pip install rtdl` is not a product surface).
2. **Do not claim zero-copy/device-residency as a general RTDL product feature.** Evidence exists only for specific measured paths.
3. **Do not claim AMD GPU performance** until Goal I artifact exists.
4. **Do not claim Intel GPU performance** — no Intel Arc/Xe evidence exists in the project.
5. **Do not promote `continuation.predicate_aware_boundary_union` to stable** without DBSCAN boundary-policy evidence on a real dataset at scale with full correctness audit.
6. **Do not attempt full paper reproduction for RTNN, RayJoin, RT-DBSCAN, or SIGMETRICS triangle counting.** The project's value is language/runtime design pressure, not paper reproduction.
7. **Do not add Apple Silicon GPU backend** until the Intel/AMD/NVIDIA story is more complete. The `cpu_python_reference` path works on Apple Silicon; that is enough for development use.
8. **Do not create app-specific native ABI symbols** for any of the 10 benchmark apps. The engine must stay app-agnostic.
9. **Do not move Triton from internal partner to recommended user path** without same-contract evidence against CuPy and Numba. Triton imports exist in `partner_adapters.py` but the benchmark matrix does not recommend Triton for any current app.
10. **Do not publish speedup numbers without naming the exact workload, backend, partner, hardware, dataset, and artifact path.** A number without all six is not a public claim.

---

## Safe Public Wording

### Currently safe (if carefully scoped):

- "RTDL is an open-source Python-hosted DSL for RT-shaped spatial query kernels."
- "RTDL uses the `input → traverse → refine → emit` kernel contract with explicit backend selection."
- "RTDL v2.10 runs from the source tree with `PYTHONPATH=src:.` on Linux, macOS, and Windows."
- "The current benchmark portfolio includes 10 apps demonstrating RT-shaped workloads in spatial search, neighbor ranking, density clustering, collision screening, aggregate summary, and graph analytics."
- "Selected RT-heavy spatial join workloads (LibRTS-style LSI overlap count) show large OptiX speedups over Embree CPU on the same command surface. See the exact artifact before quoting a number."
- "RTDL v2.11 Embree CPU coverage covers 9 of 10 current benchmark apps. RTNN uses a Numba CPU partner reference because the current RTNN app has no Embree front door."
- "The RTDL engine must stay app-agnostic. App names, domain semantics, and cluster labels belong in Python application code, not in native engine ABI names."
- "CuPy is the current performance recommendation for measured large-scale grouped reduction and compact-mask continuations. Numba is the current no-RawKernel Python-source reference lane for selected generic continuations."

### Blocked claims — must not be made now:

| Blocked claim | Why blocked |
|---|---|
| `pip install rtdl` | Not a package; source-tree only |
| "RTDL provides zero-copy device residency" | Not a general product; specific measured paths only |
| "RTDL accelerates your CuPy/Numba programs" | RTDL accelerates the RTDL primitive you call, not arbitrary partner code |
| AMD GPU performance wording of any kind | No AMD pod artifact exists |
| Intel GPU performance wording of any kind | No Intel GPU evidence |
| Paper reproduction for RTNN, RayJoin, RT-DBSCAN, SIGMETRICS triangle counting | Not the project's claim; reproductions require matching paper system contracts |
| "RTDL is faster than [any system] for [any workload]" without exact artifact | Speedup without exact contract, hardware, and artifact is not a public claim |
| "Automatic partner selection" | Not implemented; users choose partners explicitly |
| "Broad RT-core acceleration across all workloads" | Evidence exists only for specific measured paths |

---

## Questions For Main AI

1. **Numba status promotion:** The code labels Numba as `V2_5_STATUS_PREVIEW_NOT_PROMOTED` but the benchmark matrix treats it as the current reference path for 4 workloads. Is the intent to promote specific Numba operations (e.g., `segmented_count_i64`, `grouped_argmin_f64`) to `stable_behavior` in v2.11, or to add a new `partner_recommended_preview` status tier? This needs a decision before the matrix wording can be made consistent.

2. **RTNN Embree front door:** Is there a structural reason RTNN currently lacks an Embree path, or is it simply that no one has added it? The app uses `prepared_optix_ranked_summary` which requires OptiX. A prepared Embree fixed-radius ranked-summary should be straightforward. Is this on the v2.11 roadmap?

3. **`Lib/` and `before_3958.txt` in git status:** The untracked `Lib/` directory is likely a Windows Python path extract and should be in `.gitignore`. `before_3958.txt` has no obvious purpose. What are these, and should they be cleaned up?

4. **`continuation.fixed_radius_graph` OptiX-only:** Is the design intent that RT-DBSCAN on Embree CPU will always use Python-level component tracking, or is there a plan to bring the device continuation to Embree? If it is permanent, the docs should say so clearly. If it is planned, it belongs in the improvement roadmap.

5. **LibRTS scale and CI:** The 132s Embree run at current scale is impractical for CI. What is the intended scale policy — should there be a fast regression row (10K points, <10s) and a separate performance evidence row? Or is 132s acceptable because this benchmark is never expected to be in daily CI?

6. **`src/rtdsl/` archiving policy:** There are 60+ legacy goal-tagged and version-tagged files in the primary source module alongside the current API. Is there a written policy for when these get archived? The project would benefit from a clear rule: e.g., "any file that is not imported by the public `rtdsl/__init__.py` surface and postdates v1.6 gets archived after one milestone."

7. **Barnes-Hut "CuPy remains faster overall":** The benchmark matrix note says CuPy remains the faster overall path for Barnes-Hut. Is this an accepted design trade-off (RTDL provides the RT aggregate-frontier primitive, CuPy wins on end-to-end) or an unresolved deficit? If it is a trade-off, the benchmark description should say "RTDL owns the tree traversal; force-vector continuation is CuPy's domain." If it is a deficit, what is the plan?

8. **`candidate.closed_shape_topology_membership_count_2d` promotion path:** This primitive underlies the spatial rayjoin PIP path, which is one of the strongest benchmarks. Its `planned_optix` status is a meaningful gap. What is the evidence threshold needed to promote it to `stable_behavior`? Is there a target goal number?
