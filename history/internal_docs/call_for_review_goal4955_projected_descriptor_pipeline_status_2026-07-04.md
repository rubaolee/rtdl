# Call For Review: Goal4955 Projected Descriptor Pipeline Result

Date: 2026-07-04

Please review:

- `history/internal_docs/goal4955_v2_14_3_rayjoin_numba_pipeline_goal_2026-07-04.md`
- `history/internal_docs/goal4955_projected_descriptor_pipeline_status_2026-07-04.md`
- `history/internal_docs/goal4955_projected_descriptor_pipeline_measure.py`
- `history/internal_docs/goal4955_projected_descriptor_non_rayjoin_proof.py`
- `history/internal_docs/goal4955_projected_descriptor_non_rayjoin_proof.json`
- `tests/goal4955_projected_descriptor_pipeline_test.py`
- `history/internal_docs/goal4955_artifacts/goal4955_pod_comparison_summary_v4.json`
- `history/internal_docs/goal4955_artifacts/baseline_goal4954e_rerun_*.json`
- `history/internal_docs/goal4955_artifacts/projected_descriptor_minimal_run_*.json`

## POD Result Summary

The new POD was reachable and the measurement gate completed.

Median writer-free hot path:

| Route | Median seconds | Speedup vs rerun baseline |
|---|---:|---:|
| Goal4954-E rerun baseline | 2.947452 | 1.000000x |
| projected descriptor, first/list route | 2.599655 | 1.133786x |
| projected descriptor, online-dedupe route | 2.646901 | 1.113548x |
| projected descriptor, minimal descriptor route | 2.597365 | 1.134786x |

Frozen useful bar:

```text
>=1.15x
```

Actual best speedup:

```text
1.134786x
```

Therefore the requested exit is **not** a performance win.  The honest label is:

```text
v2_14_3_pipeline_no_go_pre_fusion_exhausted
```

## Requested Verdict

`approve_goal4955_no_go_pre_fusion_projection_route_below_bar`

or

`block_goal4955_until_amended`

## Review Questions

1. Does the proposed projected descriptor route correctly implement projection
   pushdown / late materialization rather than a RayJoin-specific RTDL core
   primitive?
2. Does the route preserve the boundary that RTDL remains generic and RayJoin
   remains an app?
3. Is it acceptable that the current implementation lives under
   `history/internal_docs` as an internal measurement prototype before any
   productization decision?
4. Does the non-RayJoin synthetic proof adequately show that the projected
   descriptor carrier idea is not inherently RayJoin-only?
5. Does the projected-vs-full carrier unit test adequately protect descriptor
   semantics while dropping geometry payload columns?
6. Does the script correctly avoid claiming paper byte equality for the numeric
   projected route?
7. Is the Numba usage appropriately limited and honestly described as CPU
   `njit` descriptor aggregation, not CUDA device-resident continuation?
8. Are the local checks and POD checks sufficient to trust the implementation
   and measurement artifacts?
9. Is the result correctly interpreted as a real small improvement that is
   below the frozen useful bar, rather than as a v2.14.3 performance win?
10. Should Goal4955 close as
    `v2_14_3_pipeline_no_go_pre_fusion_exhausted`, with the code kept as
    internal evidence only unless a later goal finds a stronger route?

## Non-Authorization

This review should not authorize:

- public high-performance claims;
- v3/v4 surface revival;
- Layer 4 traversal callback/fusion;
- RayJoin-specific RTDL core primitives;
- paper byte-equality claims for the numeric projected binary route.
- marking the active v2.14.3 performance goal complete on a sub-threshold
  `1.134786x` result.
