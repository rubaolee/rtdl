# Goal4202: RT-DBSCAN Single-Pass Reference Parity

Date: 2026-06-09

## Purpose

Goal4201 showed that the explicit two-pass boundary policy is correct-looking
but too expensive to promote as the default. Goal4202 checks the more important
possibility: after Goal4197, does the fast one-pass policy already match the
Goal4194 deterministic reference contract?

The answer is yes for the tested fixtures. Both policies match the reference
labels exactly, and the default one-pass route also matches the two-pass labels.

## Method

The tracked runner is:

`scripts/goal4202_rt_dbscan_single_pass_reference_parity.py`

For each fixture it:

1. builds CPU candidate pairs from the same points and radius;
2. runs the RTDL OptiX+Numba grouped-stream labels route;
3. uses the native-produced predicate flags as the reference predicate input;
4. calls `rt.predicate_aware_boundary_union_reference(...)`;
5. compares native labels to the deterministic reference labels.

This is intentionally small-scale because the reference candidate-pair build is
CPU `O(n^2)`. Goal4201 is the timing evidence; Goal4202 is same-contract
correctness evidence.

Artifacts:

- `docs/reports/goal4202_rt_dbscan_single_pass_reference_parity_rtx4000ada/reference_parity.json`
- `docs/reports/goal4202_rt_dbscan_single_pass_reference_parity_rtx4000ada/reference_parity.stdout`

## Results

| Dataset | Points | Candidate pairs | Predicate-true count | Reference components | Default matches reference | Two-pass matches reference | Default matches two-pass |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `tiny` | 9 | 8 | 6 | 2 | yes | yes | yes |
| `clustered3d` | 512 | 6,138 | 365 | 4 | yes | yes | yes |
| `road3d` | 1,024 | 8,778 | 790 | 1 | yes | yes | yes |
| `ngsim_dense` | 1,024 | 1,869 | 0 | 0 | yes | yes | yes |

The default route records native pass count `1`; the two-pass route records
native pass count `2`. Both use the same generic native symbol:

`rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs`

## Interpretation

Goal4197 changed the native fallback candidate write to store an observed
component root instead of a raw candidate id. The Numba label/signature
consumers already resolve the stored candidate through the final parent array.
Together, those two facts make the single-pass path behave like a final-root
boundary assignment for the tested fixtures.

That is the important performance/design insight:

- two-pass is still valuable as an explicit reference/debug policy;
- one-pass should remain the performance route;
- promotion should now focus on broader same-contract parity, not adding a
  second traversal to the default route.

## Boundary

Goal4202 does not authorize release, route promotion, public speedup claims,
whole-app speedup claims, true-zero-copy claims, automatic partner selection, or
app-specific native engine logic. It provides parity evidence for a limited
fixture set and motivates the next broader route-promotion gate.

## Next Work

Run a broader same-contract gate for the one-pass route:

- more sparse/noise-heavy fixtures;
- overlapping/fragmented cluster fixtures;
- randomized seeds;
- component-size signatures at larger scales where CPU reference labels are not
  practical;
- external review of the promotion criteria before changing default route
  status.
