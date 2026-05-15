# Claude Review of Goal2075 Generic Tiled AABB Candidate-Summary Primitive

**Date:** 2026-05-15

**Reviewer:** Claude (claude-sonnet-4-6) — independent external review, distinct from Codex and from the Gemini Flash review attempt that failed with model capacity exhaustion.

**Commit reviewed:** `da947663 Goal2075 add generic tiled AABB candidate summary`

**Handoff document:** `HANDOFF_GOAL2075_CLAUDE_REVIEW.md`

---

## Scope

This review answers four questions from the handoff:

1. Does Goal2075 implement a generic partner-side tiled AABB candidate-pair payload primitive rather than polygon/app-specific native engine customization?
2. Does the polygon `cupy_extent` control path now use that generic primitive while preserving public CLI compatibility?
3. Are the claim boundaries correct — no v2.0 release authorization, no arbitrary polygon overlay claim, no whole-app/broad RT-core speedup claim, and fresh pod timing still required before matrix promotion?
4. Are the tests sufficient for source-level wiring, given that pod timing is unavailable?

Files read: `src/rtdsl/partner_adapters.py`, `src/rtdsl/__init__.py`, `examples/rtdl_control_apps_cupy_rawkernel.py`, `docs/reports/goal2075_generic_tiled_aabb_candidate_summary_2026-05-15.md`, `tests/goal2075_generic_tiled_aabb_candidate_summary_test.py`, `docs/reports/goal2032_polygon_tiled_extent_candidate_discovery_2026-05-14.md`, `docs/reports/goal2068_final_v2_0_release_matrix.md`.

---

## Question 1 — Generic Partner-Side Primitive vs. App-Specific Native Engine Logic

**Finding: Confirmed.**

`aabb_tiled_candidate_pair_payload_2d_partner_columns` is defined at `src/rtdsl/partner_adapters.py:432`. The design is app-agnostic:

- Input contract is plain column dicts (`min_x, min_y, max_x, max_y, area`) with no polygon type dependency.
- Partner dispatch uses the existing `_partner_module` helper, supporting both `torch` and `cupy`.
- The nested tile loops (`for left_start in range(...)` / `for right_start in range(...)`) are in pure partner math — no RTDL engine call, no native kernel, no OptiX hit program.
- `_metadata` embeds `"native_engine_row_contract": "not_called_partner_reference_only"`, `"partner_reference_contract": "generic_tiled_aabb_candidate_pair_payload_2d"`, and `"bounded_materialization": True`.
- The downstream summary adapter `aabb_pair_overlap_summary_2d_partner_columns` (also in `partner_adapters.py`) consumes the output without any polygon-specific knowledge.

The native RTDL engine is not given polygon-specific reduction logic. The primitive is a partner-side utility callable for any 2D AABB workload, not a polygon specialization.

---

## Question 2 — `cupy_extent` Path Rewired to Generic Primitive, CLI Compatibility Preserved

**Finding: Confirmed with one structural note.**

`_partner_pair_payload_table_cupy_extent` (`examples/rtdl_control_apps_cupy_rawkernel.py:702`) now calls `aabb_tiled_candidate_pair_payload_2d_partner_columns` from `rtdsl`, forwarding the three environment-variable-controlled tile parameters:

```python
payload_columns = aabb_tiled_candidate_pair_payload_2d_partner_columns(
    _axis_aligned_extent_columns(left),
    _axis_aligned_extent_columns(right),
    partner="cupy",
    tile_rows=_cupy_extent_tile_rows(),
    right_tile_rows=_cupy_extent_right_tile_rows(),
    free_tile_blocks=_cupy_extent_free_tile_blocks(),
)
```

The routing condition `candidate_backend == "cupy_extent" and partner == "cupy"` at line 901 is intact. `POLYGON_EXTENT_RAWKERNEL_SOURCE` is confirmed absent (grep returns no matches). The CLI name `cupy_extent` is preserved as documented.

**Structural note (not a blocker):** `_positive_candidate_pairs_cupy_extent` (line 733), the validation/oracle path that returns a Python set of pair tuples, still uses the private `_cupy_extent_candidate_indices` helper (line 667) rather than delegating to the generic adapter. This is a partial migration: the performance payload path is fully rewired, but the oracle correctness path retains an app-local copy of the tiling logic. The two paths serve structurally different roles (payload dict vs. Python set), so this is not incorrect, but it leaves `_cupy_extent_candidate_indices` alive as dead-code-by-design that could diverge from the generic adapter silently. A future cleanup goal should migrate or remove it.

---

## Question 3 — Claim Boundaries

**Finding: Correct and explicit at multiple levels.**

The report (`goal2075_generic_tiled_aabb_candidate_summary_2026-05-15.md`) states:

- Status: `implemented-pending-fresh-pod-timing` — not released, not promoted.
- Not allowed: v2.0 release authorization; arbitrary polygon overlay; full witness-row materialization; broad RT-core or whole-app speedup claims; matrix promotion without fresh pod timing.
- Prior Goal2032 ratios are explicitly documented as development evidence from a dirty source label and are not reused as current release evidence.

The adapter's `_metadata` dict reinforces this at call time:

```python
"rt_core_speedup_claim_authorized": False,
"v2_0_release_authorized": False,
"whole_app_speedup_claim_authorized": False,
```

The Goal2068 final matrix (`goal2068_final_v2_0_release_matrix.md`) shows `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` remain `pod-evidence-collected-bounded` with explicit OOM evidence at 4096 copies. Goal2075 does not change those matrix entries — it prepares the source tree for the next pod run that would produce current-commit evidence. The boundary between "source is now clean" and "matrix is now promoted" is correctly maintained.

All four specific boundary checks pass:
- No v2.0 release authorization: **pass**
- No arbitrary polygon overlay claim: **pass** (report says "not arbitrary polygon overlay" and notes arbitrary polygon overlay is not solved)
- No whole-app/broad RT-core speedup claim: **pass**
- Fresh pod timing still required: **pass** (stated explicitly in report and in the "next pod command shape" section)

---

## Question 4 — Test Sufficiency for Source-Level Wiring

**Finding: Adequate for stated scope, with a functional gap that should be acknowledged.**

Three tests are present in `tests/goal2075_generic_tiled_aabb_candidate_summary_test.py`:

1. `test_generic_tiled_aabb_candidate_payload_is_public` — verifies the function definition exists in `partner_adapters.py`, that key implementation strings are present (loop structure, `free_all_blocks` call, contract literals), and that the function is imported and listed in `__init__.py`'s `__all__`.

2. `test_polygon_cupy_extent_path_uses_generic_adapter` — verifies the call site in the example file, the env-var names, and the absence of `POLYGON_EXTENT_RAWKERNEL_SOURCE`.

3. `test_report_records_solution_and_pod_boundary` — verifies that the report text contains required claim and boundary strings.

All three tests operate as file-text assertions. This is the appropriate strategy when GPU/pod infrastructure is unavailable: the tests cannot exercise the tiling computation, but they can verify the source-level wiring is in place and the boundary documentation is correct.

**Gap (minor, acknowledged by design):** There are no functional unit tests for the adapter's overlap detection, tile boundary arithmetic, or empty-input edge cases. A future goal should add CPU-only unit tests (e.g. using NumPy or small CuPy arrays) that exercise: empty left/right inputs, single-element inputs, non-overlapping AABBs, touching-but-not-overlapping AABBs, and tile boundary straddling. These can run without a GPU and would protect against silent regressions in the tiling loop.

The tests as written are sufficient for the stated scope ("source-level wiring, given that pod timing is unavailable") and match the scope claimed in the report.

---

## Summary of Findings

| Question | Result | Notes |
| --- | --- | --- |
| Generic partner-side primitive (not polygon/native engine) | **Confirmed** | App-agnostic column contract, pure partner math, `native_engine_row_contract: not_called` |
| `cupy_extent` path rewired, CLI compatibility preserved | **Confirmed with note** | Performance path fully delegated; oracle path retains private helper — partial migration |
| Claim boundaries correct | **Confirmed** | All four boundary conditions explicitly held at report and metadata levels |
| Tests adequate for source-level wiring | **Adequate for stated scope** | Functional unit tests for overlap logic are a follow-up gap |

---

## Verdict

**`accept-with-boundary`**

The implementation is structurally sound. The generic primitive is correctly designed, published, and wired into the `cupy_extent` performance path. The claim boundaries are explicit and consistent across the report, the adapter metadata, and the matrix. The tests are adequate for source-level verification given the pod constraint.

Two items should be tracked as follow-up (neither blocks acceptance):

1. The `_positive_candidate_pairs_cupy_extent` oracle path still uses private `_cupy_extent_candidate_indices` rather than the new generic adapter, leaving a silent divergence risk. A cleanup goal should migrate or remove it.

2. Functional unit tests for the tiling loop and overlap detection are absent. A future goal should add CPU-runnable tests for edge cases and tile boundary correctness.

The polygon rows in the final v2.0 matrix remain at `pod-evidence-collected-bounded` and must not be promoted without fresh pod timing on this commit. This review does not authorize v2.0 release.
