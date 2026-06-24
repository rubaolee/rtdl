# Call For Review: Phoenix V3 Grouped-Reduction Scalar-Broadcast Optimization

Reviewer: Claude or Gemini.

Date: 2026-06-20.

## Review Target

Please critically review the V3 grouped_sum scalar-broadcast optimization and
updated candidate wording:

```text
src/rtdsl/optix_runtime.py
examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py
docs/rebuild/v3/phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.json
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.json
tutorials/current/07_grouped_sum_prepared_query.md
tests/v3_phoenix_grouped_reduction_scalar_broadcast_optimization_test.py
tests/v3_phoenix_grouped_reduction_sum_m7_candidate_wording_test.py
```

Raw pod artifacts:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_scalar_broadcast_probe_20260620
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620
```

## Local Verification

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal671_optix_prepared_anyhit_count_test tests.v3_phoenix_grouped_reduction_scalar_broadcast_optimization_test tests.v3_phoenix_grouped_reduction_sum_m7_candidate_wording_test tests.v3_release_wording_gate_test tests.v3_rebuild_tutorial_surface_test
36 tests OK, 5 skipped

py -3 scripts/v3_phoenix_grouped_reduction_sum_m7_candidate_wording.py
status: sum_only_actual_repeat100_candidate_wording_not_release

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []

py -3 scripts/run_test_matrix.py --group v3_rebuild
33 modules / 146 tests OK
```

## Evidence Summary

The optimization allows `pack_rays_3d_from_arrays` to validate and broadcast
scalar float fields, then updates RayDB-style grouped_sum lowering to pass
scalar `dx`, `dy`, `dz`, and `tmax` values instead of allocating four full-length
constant arrays for a 76,087,296-ray batch.

This is a generic typed-buffer packing optimization. It is not an app-specific
native engine and does not change the native grouped-reduction primitive.

Current actual repeat100 rows:

| Row | Hot OptiX/Embree | Actual repeat100 loop | Actual cold plus loop | Classification |
| --- | ---: | ---: | ---: | --- |
| 262,144 rows / 1,024 groups | 203.022x | 200.353x | 27.917x | candidate, not M7 |
| 524,288 rows / 2,048 groups | 158.970x | 157.642x | 2.983x | large cold prepare cost, not M7 |

All rows matched CPU reference and kept public/release flags false.

## Review Questions

1. Is scalar-field broadcast in `pack_rays_3d_from_arrays` a safe generic V3
   optimization?
2. Does the RayDB grouped_sum lowering change stay within V3 boundaries, or is
   it too app-specific?
3. Is it correct to make scalar-broadcast repeat100 the current candidate
   evidence source for both 262,144 and 524,288 rows?
4. Should the 262,144-row sum case remain only a candidate pending final
   public-row review?
5. Should the 524,288-row row stay blocked/not-M7 because cold-plus-loop is
   still only 2.983x?
6. What P0/P1 fixes are required before any grouped_sum row can be promoted?

## Expected Verdict Format

Please return:

```text
Verdict: approve / approve-with-fixes / reject
P0 findings:
P1 findings:
Candidate decision:
Suggested wording changes:
Can any row be M7-qualified now?
Can any public speedup wording be published now?
```

Be strict. A "no" answer to the last two questions is acceptable.
