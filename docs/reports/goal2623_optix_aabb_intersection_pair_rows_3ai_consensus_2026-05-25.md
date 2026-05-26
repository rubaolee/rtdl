# Goal2623 OptiX AABB Pair Rows 3-AI Consensus

Date: 2026-05-25

## Scope

This consensus covers Goal2623: generic OptiX native row output for
`AABB_INDEX_QUERY_2D` `range_intersection_rows`, exposed through:

- `rtdsl.aabb_intersection_pair_rows_2d(..., backend="optix", row_capacity=...)`
- `rtdsl.collect_aabb_intersection_pair_rows_2d_optix(...)`
- native ABI
  `rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows`

The scope does not include native contact/collision/manifold semantics, whole-app
public speedup claims, or a stable external API promise beyond the current
internal benchmark/reconstruction surface.

## Evidence

Implementation and documentation:

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/aabb_index.py`
- `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `examples/v2_0/research_benchmarks/contact_manifold/README.md`
- `docs/rtdl_primitive_catalog.md`
- `docs/application_catalog.md`
- `docs/reports/goal2623_optix_aabb_intersection_pair_rows_2026-05-25.md`

Tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2580_optix_aabb_index_native_symbol_test \
  tests.goal2622_contact_manifold_generic_aabb_discovery_test \
  tests.goal2623_optix_aabb_pair_rows_test
```

Local Mac result:

```text
Ran 18 tests in 0.039s
OK (skipped=3)
```

Pod result on RTX A5000:

```text
Ran 18 tests in 0.694s
OK
```

Pod pressure evidence:

- OptiX row path matches the deterministic grid oracle at 512, 4,096, 16,384,
  and 65,536 witnesses.
- The explicit overflow probe raises
  `failure_mode=fail_closed_overflow`.
- The 65,536 grid case has 4,294,967,296 possible pairs and 65,536 emitted
  candidate rows.

## External Reviews

Claude:

- Initial review:
  `docs/reports/goal2623_claude_optix_aabb_pair_rows_review_2026-05-25.md`
- Verdict: `ACCEPT WITH ISSUES`
- Issues: document pre-dedup capacity rule, add GPU overflow regression test,
  add `RtdlAabbPairRow` layout assertions.
- Follow-up review:
  `docs/reports/goal2623_claude_optix_aabb_pair_rows_followup_review_2026-05-25.md`
- Follow-up verdict: `ACCEPT`
- Follow-up conclusion: all three low-severity issues were resolved with
  concrete code/test/doc changes.

Gemini:

- Review:
  `docs/reports/goal2623_gemini_optix_aabb_pair_rows_review_2026-05-25.md`
- Verdict: `ACCEPT`
- Gemini confirmed app-agnosticism, fail-closed overflow behavior,
  documentation accuracy, and sufficient testing.

Codex:

- Implemented the generic native ABI, Python wrapper, app integration, docs, and
  tests.
- Ran local tests, pod rebuild/tests, and pod pressure tests.
- Confirmed no collision/contact-specific native engine logic was added.

## Consensus Decision

3-AI consensus is reached.

Goal2623 is accepted as an internal benchmark/runtime improvement:

- `AABB_INDEX_QUERY_2D` now has a generic OptiX
  `range_intersection_rows` path.
- The row output is app-agnostic `(query_id, indexed_id)`.
- Capacity overflow is fail-closed.
- The OptiX public dispatch requires explicit `row_capacity`, avoiding implicit
  all-pairs output-buffer allocation.
- The contact-manifold benchmark can use this generic path before app-owned
  exact refinement and `COLLECT_K_BOUNDED`.
- No native contact/collision/manifold ABI or semantics are introduced.

## Remaining Boundary

This does not authorize public whole-app speedup wording. It authorizes the
narrow internal claim that RTDL has a generic OptiX AABB pair-row emitter with
fail-closed capacity semantics and pod-backed parity evidence for the
contact-manifold benchmark path.
