---

## Goal2621 Bounded Contact-Witness Benchmark Candidate Review

**Verdict: ACCEPT** (as benchmark candidate; not promoted benchmark)

---

### Engine App-Agnostic: YES — Clean Boundary

The engine boundary is enforced at every layer:

- `PRIMITIVE = "COLLECT_K_BOUNDED"` and `rt.collect_k_bounded_rows(..., row_width=3)` are the only engine calls. No collision-specific symbol is invoked.
- `scope_payload()["engine_boundary"]["native_collision_logic_allowed"]` is `False`.
- `app_owned_contact_summaries()` computes centroid midpoints entirely in Python after row collection, labeled `"owner": "python_app_contact_summary_not_native_engine"`. This is correct placement.
- Test `test_app_source_does_not_call_collision_specific_native_symbols` (line 53) asserts the source string contains no `collect_shape_pair_candidates_bounded`, `rtdl_embree_*`, or `rtdl_optix_*` symbols — a static guard against regression.
- The primitive catalog entry at `rtdl_primitive_catalog.md:225` correctly records: "collision/contact semantics stay in Python app code."

---

### COLLECT_K_BOUNDED Overflow Semantics: YES — Exact Fail-Closed

`scope_payload()` declares three non-negotiable properties (app.py:62-65):

```
policy: "fail_closed_before_result_materialization"
partial_rows_returned_on_overflow: False
silent_truncation_allowed: False
```

Test `test_overflow_fails_closed_without_partial_rows` (test:49-51) directly exercises this: `witness_capacity=2` against 3 witness rows triggers a `RuntimeError` containing `partial_result_returned=False`. The report (report:52) confirms the exact message was observed. There is no early-truncation path, no quiet shortfall. The overflow contract is tight and tested.

---

### Missing Gates Before Promoted-Benchmark Wording

The candidate documents its own gate list correctly in `scope_payload()["promotion_gates"]` and `application_catalog.md:51`. Gates open as of this review:

| Gate | Status |
|---|---|
| Deterministic Python fixtures | **Done** — tiny + grid fixtures, oracle verified |
| Generic collect-k fail-closed tests | **Done** — 6 tests pass |
| Claude review | **This review** |
| Gemini review | Exists (`docs/reports/goal2621_gemini_bounded_contact_witness_review_2026-05-25.md`) |
| Embree parity (same row schema + overflow contract) | **Blocked** |
| OptiX parity (NVIDIA pod, same contract) | **Blocked** |
| External baseline comparison (CUDA/BVH or physics-library) | **Blocked** — CPU-only timing is a correctness smoke, not a performance gate |
| 3-AI consensus file | **Blocked** — requires the above to close first |

The `baseline_comparison_payload` (app.py:336) already acknowledges this limitation in its `claim_boundary` field, which is the correct self-limiting posture.

---

### Required Fixes

**None required before accepting as candidate.** One observation worth flagging:

**`build_fixture` "overflow" alias (app.py:153):** `"overflow"` silently maps to `tiny_fixture()`. The CLI exposes `--dataset overflow` as a choice, but a reader seeing it would not know it yields the tiny fixture. The overflow is triggered entirely by `witness_capacity`, not by a dedicated fixture. This is harmless and the behavior is verified by test, but it will surprise future contributors. Consider renaming the CLI choice to `tiny` only (or adding a minimal inline note at the `build_fixture` branch) — nothing more.

**No other bugs found.** The 2-D triangle intersection oracle (`triangles_intersect`, app.py:201) is geometrically correct for the tiny fixture: queries 10 and 11 (group 0) land inside scene triangles 0 and 1, query 30 (group 2) lands inside scene triangle 2, and query 20 (group 1) is distant — matching the expected rows `((0,10,0),(0,11,1),(2,30,2))`. The grid fixture is scaled correctly and one-to-one. The contact summaries use only post-collection Python metadata with no engine re-entry.

---

### Summary

The app correctly exercises `COLLECT_K_BOUNDED` as a generic primitive, keeps all contact/collision vocabulary in Python, enforces exact fail-closed overflow, and honestly self-describes as a candidate. No structural or contract defects were found. The three hard gates remaining (Embree parity, OptiX parity, external baseline) are the correct blockers for promoted-benchmark wording, and the documentation captures them precisely.
