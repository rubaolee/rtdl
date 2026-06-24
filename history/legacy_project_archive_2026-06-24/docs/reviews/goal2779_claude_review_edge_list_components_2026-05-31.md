# Goal2779 Independent Review — Edge-List Components

Date: 2026-05-31
Reviewer: Claude (claude-sonnet-4-6), independent read-only
Verdict: **accept-with-boundary**

---

## Scope

This review covers Goal2779's addition of the `edge_list_components_i64` operation
to the v2.5 partner continuation surface. Files read:

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/__init__.py`
- `tests/goal2662_v2_5_partner_continuation_contract_test.py`
- `tests/goal2671_v2_5_preview_gate_test.py`
- `tests/goal2676_v2_5_triton_partner_pivot_test.py`
- `tests/goal2677_v2_5_triton_segmented_minmax_preview_test.py`
- `tests/goal2779_v2_5_triton_edge_list_components_preview_test.py`
- `docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md`

---

## Question 1 — Is `edge_list_components_i64` generic and not DBSCAN/app-specific?

**Confirmed.**

The operation is declared in `partner_continuation_protocol.py` lines 138–147:

```python
RtdlPartnerContinuationOperation(
    name="edge_list_components_i64",
    category="component_labeling",
    input_names=("source_ids", "target_ids", "node_count", "max_iterations"),
    output_names=("component_ids",),
    behavior=(
        "label connected components over an undirected int64 edge list; "
        "source and target node ids must be in [0, node_count); labels use "
        "the smallest node id in each component"
    ),
)
```

All four input names are graph-topology terms with no application domain meaning.
`app_specific_semantics_allowed=False` is the dataclass default and is enforced in
`RtdlPartnerContinuationSpec.__post_init__()` (line 271) by raising `ValueError` if
set. The operation name passes `_validate_operation_name()` (line 998–1004), which
rejects any name containing tokens from `V2_4_FORBIDDEN_NATIVE_APP_TOKENS`. The
report (line 14–15) explicitly states "This is not a DBSCAN primitive. It labels
connected components over a caller-supplied undirected edge list. App code owns the
meaning of the edges and any cluster policy."

Test evidence: `goal2662` line 71–73 checks
`components["category"] == "component_labeling"` and that the behavior string
contains "source and target node ids." Test `goal2779` line 23–26 confirms the
operation is in `V2_5_PARTNER_CONTINUATION_OPERATION_NAMES` and
`V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS` and absent from
`V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS`.

---

## Question 2 — Does the reference label components by smallest node id?

**Confirmed.**

`_edge_list_components_i64()` in `partner_continuation_protocol.py` lines 872–914:

1. Initializes `parent = list(range(node_count))` — each node's root starts as itself
   (the smallest possible label).
2. On each union: `low = min(source_root, target_root); parent[high] = low` — always
   merges the higher root toward the lower one (lines 901–903).
3. Path-compression loop (lines 905–913) iterates until no node's parent differs from
   its root, ensuring final labels are fully propagated.
4. Output: `{"component_ids": [find(node) for node in range(node_count)]}` — the
   root of each node's tree, which is the smallest node id reachable through union
   steps.

Concrete test in `goal2779` lines 38–46 verifies:

- Edges `[0→1, 1→2, 3→4, 6→7]` on 8 nodes produce
  `component_ids = [0, 0, 0, 3, 3, 5, 6, 6]`.
- Component `{0, 1, 2}` → label 0 ✓
- Component `{3, 4}` → label 3 ✓
- Singleton `{5}` → label 5 ✓
- Component `{6, 7}` → label 6 ✓

The same case is independently covered in `goal2662` lines 238–239. The label
semantics are correct.

---

## Question 3 — Does the Triton preview mirror the reference shape with min-label propagation kernels and no RawKernel?

**Confirmed, with one observable difference in convergence design (see Q6).**

`run_triton_edge_list_components_i64()` in `triton_partner_continuation.py`
lines 800–866:

- Initializes `component_ids = torch.arange(node_count, ...)` — mirrors the
  reference's `parent = list(range(node_count))` initialization.
- Iterates exactly `max_iterations` times, each iteration calling:
  1. `_triton_edge_list_component_relax_i64_kernel` (lines 1576–1590): loads source
     and target labels, computes `low = tl.minimum(source_labels, target_labels)`,
     then `tl.atomic_min(component_ids + sources, low, ...)` and
     `tl.atomic_min(component_ids + targets, low, ...)`. This is direct min-label
     propagation over edges.
  2. `_triton_edge_list_component_compress_i64_kernel` (lines 1594–1604): loads
     parent and grandparent labels, stores `new_parent = tl.minimum(parents,
     grandparents)` — one step of path compression per iteration.
- Output: `{"component_ids": component_ids}` — same single-output shape as reference.
- Descriptor records `"algorithm": "fixed_iteration_min_label_propagation"` and
  `"component_label": "smallest_node_id_in_component"` (lines 100–103 of
  `triton_partner_continuation.py`), consistent with the reference.

No `RawKernel` is present. Kernels use `@__import__("triton").jit`, the standard
Triton kernel pattern. Test `goal2779` lines 48–55 explicitly searches the source
for `_triton_edge_list_component_relax_i64_kernel`,
`_triton_edge_list_component_compress_i64_kernel`, `tl.atomic_min(component_ids`,
`fixed_iteration_min_label_propagation`, and asserts `"RawKernel" not in source`.

The Triton preview produces the same result as the reference when `max_iterations`
is adequate (verified by pod test: `goal2779` line 57–72 skips if no CUDA,
otherwise runs with `max_iterations=8` on an 8-node graph and asserts
`[0, 0, 0, 3, 3, 5, 6, 6]`). Pod run confirmed on RTX A5000, Torch 2.8.0+cu128,
Triton 3.4.0, 6 tests in 2.799s OK.

---

## Question 4 — Is the support matrix honest?

**Confirmed.**

Evidence from `v2_5_partner_support_matrix.py`:

The matrix builder `v2_5_partner_support_cells()` (lines 108–198) applies this rule
for every operation:
- `python_reference` always gets `reference_contract` (lines 111–120).
- `triton` gets `preview_not_promoted` if the operation is in
  `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`; otherwise `unsupported_fail_closed`
  (lines 121–144).
- `numba` gets `preview_not_promoted` only for the two operations in
  `V2_5_NUMBA_PREVIEW_OPERATIONS` (`segmented_count_i64`, `segmented_sum_f64`);
  otherwise `unsupported_fail_closed` (lines 145–167).
- `cupy_conformance` gets `preview_not_promoted` only for
  `hit_stream_grouped_ray_id_primitive_i64`; otherwise `descriptor_only`
  (lines 168–197).

`edge_list_components_i64` is in `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`
(line 226 of `partner_continuation_protocol.py`) and absent from
`V2_5_NUMBA_PREVIEW_OPERATIONS` and `V2_5_CUPY_PREVIEW_OPERATIONS`. Therefore:

| Partner | Status in matrix |
|---|---|
| `python_reference` | `reference_contract` |
| `triton` | `preview_not_promoted` |
| `numba` | `unsupported_fail_closed` |
| `cupy_conformance` | `descriptor_only` |

Test `goal2779` lines 28–33 asserts exactly this via `plan_v2_5_partner_support()`.
`validate_v2_5_partner_support_matrix()` (lines 234–291) additionally checks that
no cell sets `promoted_performance_path`, `rt_traversal_replacement_allowed`,
`public_speedup_claim_authorized`, or `true_zero_copy_claim_authorized` to True.
The `V25PartnerSupportCell.__post_init__()` (lines 54–79) enforces these constraints
at construction time.

---

## Question 5 — Are all forbidden claims absent?

**Confirmed. No forbidden claims are present or introduced.**

All five claim categories are governed by constants and constructor guards:

**Public speedup claim:**
`V2_5_PREVIEW_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED = False`
(`partner_continuation_protocol.py` line 44). Enforced in
`validate_v2_5_partner_preview_gate()` line 451 (errors if not False). Triton run
result includes `"rt_core_speedup_claim_authorized": False` (line 1379 of
`triton_partner_continuation.py`).

**Public release tag:**
`V2_5_PREVIEW_RELEASE_TAG_AUTHORIZED = False` (line 43). Enforced in preview gate
validator line 449.

**True zero-copy:**
Every group-id bounds validation metadata block explicitly sets
`"true_zero_copy_claim_authorized": False`. For `edge_list_components_i64`
specifically, the bounds-check metadata says: "This is not a zero-copy validation
path" (`triton_partner_continuation.py` line 1419–1421).

**RT traversal replacement:**
`V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED = False` (line 40). `RtdlPartnerContinuationSpec.__post_init__()`
raises `ValueError("v2.5 partners must not replace RTDL/OptiX RT traversal")` if
`replaces_rt_traversal=True` (line 264–265). Triton run result includes
`"replaces_rt_traversal": False` (line 1381).

**DBSCAN cluster quality:**
Not claimed anywhere in source or report. The report (line 55–58) explicitly says
"This is not a public speedup claim, release claim, true-zero-copy claim, DBSCAN
cluster-quality claim, or whole-app benchmark result."

**RawKernel:**
`V2_5_RAWKERNEL_REQUIRED_ALLOWED = False` (line 41). Enforced by spec validator
and at construction time. Verified absent from Triton source by test.

---

## Question 6 — Blockers and follow-ups before DBSCAN-style app adapters

Six items, ordered by severity:

**1. Convergence correctness risk — caller-supplied `max_iterations` (HIGH)**

The Triton preview runs a fixed number of relax+compress iterations with no
convergence detection. The reference implementation detects convergence via a
`changed` flag (lines 905–913 of `partner_continuation_protocol.py`); the Triton
runner does not. If a DBSCAN-style app adapter passes a `max_iterations` value
smaller than the actual component diameter, the output labels will be silently
incorrect — not all nodes will have converged to the minimum label. The descriptor
records the convergence contract (`"convergence_contract": "caller_supplied_max_iterations_must_cover_component_diameter"`
in `triton_partner_continuation.py` line 102) but the Triton kernel does not detect
or report a convergence shortfall.

Before any app adapter promotes this operation past preview status, a convergence
detection mechanism is needed: either a device-side convergence flag read back after
each iteration (cheap but requires a host sync), or a post-run validation pass that
checks whether any node's label still changes. The current behavior is safe only
when the caller can statically bound the diameter (e.g., known-sparse graphs with
small diameter).

**2. Path compression depth — one level per iteration (MEDIUM)**

The compress kernel (`_triton_edge_list_component_compress_i64_kernel`) performs
only one level of grandparent shortcutting per call (lines 1598–1603). Full path
flattening (root lookup) is not done atomically on the GPU. As a result, more
iterations are required to propagate labels compared to a reference union-find with
full path compression. The practical diameter bound for an app adapter must be
treated as ≥ twice what a reference union-find would need, which may not be obvious
to the adapter author.

**3. Benchmark promotion gate — not satisfied (MEDIUM)**

`V2_5_BENCHMARK_INTEGRATION_VALIDATED = False` is explicitly set (line 46 of
`partner_continuation_protocol.py`). Pod validation confirmed correctness on an RTX
A5000 with 6 tests, but that is not a benchmark. Promotion requires: (a) a canonical
DBSCAN-style app adapter built on this operation, (b) large-scale pod benchmark
evidence comparing against the legacy CuPy component path, and (c) the
`V2_5_BENCHMARK_INTEGRATION_VALIDATED` gate to be explicitly updated.

**4. External 3-AI consensus — not complete (MEDIUM)**

`"external_3ai_consensus_complete": False` in the preview gate (confirmed by
`goal2671` line 24). This gate must be satisfied before any v2.5 continuation
operation is promoted to a public-facing performance claim, including this one.

**5. App adapter not yet written (LOW — by design)**

The operation is explicitly described as "clos[ing] the component-labeling
operation-shape gap for future app adapters." No DBSCAN-style adapter exists yet.
This is expected at this stage, but the blocker is real: the app adapter is required
before DBSCAN-style benchmark promotion.

**6. `atomic_min` with `sem="relaxed"` — semantics are correct but sensitive (LOW)**

The relax kernel uses `sem="relaxed"` for `tl.atomic_min`. Label values are
monotonically non-increasing (can only decrease), so relaxed atomics produce
correct final convergence as long as enough iterations are run. However, the
guarantee relies entirely on the iteration count. If the convergence gap in item 1
is not addressed, the relaxed-ordering choice means there is no in-kernel signal
that propagation is incomplete.

---

## Summary

| Question | Finding |
|---|---|
| 1. Generic, not DBSCAN-specific | Confirmed |
| 2. Reference labels by smallest node id | Confirmed, with test evidence on concrete graph |
| 3. Triton mirrors reference shape, min-label kernels, no RawKernel | Confirmed |
| 4. Support matrix honest | Confirmed |
| 5. No forbidden claims | Confirmed |
| 6. Blockers for app adapters | 6 items; convergence detection is the primary risk |

**Verdict: accept-with-boundary**

The operation shape, reference implementation, Triton preview kernel, and support
matrix are all correct and internally consistent. No forbidden claims (speedup,
release, zero-copy, RT traversal replacement, DBSCAN quality, RawKernel) are present
or inferable from the surface. The code contracts actively enforce these
prohibitions.

The boundary condition for this accept: the Triton preview must not be promoted
past `preview_not_promoted` until a convergence-detection mechanism is in place.
App adapters that consume `edge_list_components_i64` must document their
`max_iterations` derivation and the maximum graph diameter they expect. The
benchmark promotion gate (`V2_5_BENCHMARK_INTEGRATION_VALIDATED`) must remain `False`
until a canonical app adapter, convergence policy, and large-scale pod evidence
exist. All of these are already tracked by the existing gate constants; this review
confirms they are wired correctly and enforced.
