# Goal3164: v2.8 Front-Door Chain Review Packet

Date: 2026-06-03

Status: `ready_for_external_review`

## Scope

This packet asks an external reviewer to audit the v2.8 front-door work from
Goal3155 through Goal3163:

| Goal | Purpose | Clean pod evidence |
| --- | --- | --- |
| Goal3155 | Add fixed-radius graph component front door | `7d2c9ccc` report update |
| Goal3156 | Route RT-DBSCAN grouped-stream benchmark path through the v2.8 front door | `d1572f4c` report update |
| Goal3157 | Refresh RT-DBSCAN runtime-gap matrix row | `ebe1b5ce` report update |
| Goal3158 | Add typed producer metadata for fixed-radius graph components | `9498aa46` report update |
| Goal3159 | Package initial RT-DBSCAN front-door review packet | `0b65feba` report update |
| Goal3160 | Add generic max-of-nearest-distance alias for Hausdorff exact partner path | `08e51409` report update |
| Goal3161 | Refresh Hausdorff runtime-gap matrix row | `1f0124f5` report update |
| Goal3162 | Add RayDB grouped-reduction typed-stream front door | `838c608b` report update |
| Goal3163 | Refresh RayDB runtime-gap matrix row | `f1c43a68` report update |

## What To Review

1. **Generic front-door discipline**
   - RT-DBSCAN should route through a generic fixed-radius graph component front
     door, while DBSCAN interpretation remains in the app.
   - Hausdorff should use the generic
     `directed_max_of_nearest_distance_2d_partner_columns(...)` alias, while the
     old `directed_hausdorff_2d_partner_columns(...)` API remains as a
     compatibility alias.
   - RayDB unfused continuation should use
     `execute_grouped_reduction_typed_stream_partner_columns(...)`, while fused
     primitive-first grouped reductions remain preferred when they exactly match.
2. **Compatibility**
   - Existing Goal3143/Goal1975/Goal2044/Goal2046 Hausdorff compatibility tests
     should still pass.
   - Existing Goal2994/Goal2995 RayDB v2.6 Numba compatibility paths should still
     exist and pass.
3. **Claim boundaries**
   - None of these goals authorizes release, public speedup claims, broad
     RT-core claims, true-zero-copy claims, automatic partner selection, hidden
     dispatch, or app-specific native-engine logic.
4. **Pod evidence**
   - The reports record clean pod validations for the new executable paths.
   - The pod evidence is intentionally correctness/contract evidence, not a new
     public performance-claim packet.
5. **Remaining gaps**
   - Hausdorff still needs reusable typed RT nearest-witness producer streams.
   - RayDB still needs native typed producer/residency evidence and broader
     partner conformance for unfused continuations.
   - RT-DBSCAN still needs broader partner conformance and larger
     device-resident continuation coverage.

## Requested Review Output

Please write an independent review to:

```text
docs/reviews/goal3164_external_review_v2_8_front_door_chain_2026-06-03.md
```

Use one of the project verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

The expected conservative verdict is likely `accept-with-boundary`: the
front-door work is real and pod-validated, but v2.8 release/performance claims
remain blocked until a separate release packet and 3-AI consensus.

## Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal3155_fixed_radius_graph_component_front_door_test \
  tests.goal3156_rt_dbscan_v2_8_front_door_route_test \
  tests.goal3157_v2_8_runtime_gap_rt_dbscan_front_door_refresh_test \
  tests.goal3158_fixed_radius_graph_typed_producer_metadata_test \
  tests.goal3159_rt_dbscan_front_door_chain_review_packet_test \
  tests.goal3160_hausdorff_generic_max_nearest_front_door_alias_test \
  tests.goal3161_v2_8_runtime_gap_hausdorff_generic_alias_refresh_test \
  tests.goal3162_raydb_grouped_reduction_typed_stream_front_door_test \
  tests.goal3163_v2_8_runtime_gap_raydb_typed_stream_refresh_test
......................ss.........s..
----------------------------------------------------------------------
Ran 36 tests in 0.070s

OK (skipped=3)
```
