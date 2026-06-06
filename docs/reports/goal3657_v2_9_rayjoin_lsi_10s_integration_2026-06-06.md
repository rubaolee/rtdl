# Goal3657 v2.9 RayJoin LSI 10s Integration

Date: 2026-06-06

Status: v2.9 internal performance supplement; not release or public speedup
authorization.

## Purpose

Goal3598 reframed RayJoin from one noisy app row into contract-specific
evidence. Goal3654 adds the missing long-run RayJoin-query-exec comparison for
the LSI visible-count contract.

This supplement integrates that new evidence without changing the old boundary:
RayJoin is still not a single whole-app speedup claim, and RTDL still does not
claim full RayJoin paper reproduction.

## Evidence Threads

| Evidence | Comparator | Contract | Reading |
| --- | --- | --- | --- |
| Goal3595 | CuPy dense CUDA-core same-contract baseline | bounded public-CDB PIP/LSI/overlay counts | Mixed route: CuPy wins simple PIP scalar count; RTDL/OptiX strongly wins LSI and overlay traversal/count contracts on the 512 public-CDB slice. |
| Goal3650 | RayJoin `query_exec` | public 4096 county/soil LSI visible count | Short repeated same-slice check: counts match at `4977`; RTDL/RayJoin query ratio `0.569x`. |
| Goal3654 | RayJoin `query_exec` | public 4096 county/soil LSI visible count | 10-second-class long run: counts match at `4977`; RayJoin process wall median `12.94s`; RTDL hot-loop total median `10.31s`; RTDL/RayJoin query ratio `0.284x`. |

## Current RayJoin Position

| Contract | Best current route | Best current evidence | Status |
| --- | --- | --- | --- |
| PIP positive assignment count | CuPy dense CUDA-core route | Goal3595: CuPy `0.000437917s`, RTDL/OptiX exact prepared count `0.000802434s`, OptiX+CuPy refiner `0.002150856s` | RTDL needs a better generic exact closed-shape membership-count or boundary-selection primitive before claiming this route. |
| LSI visible segment-pair count | RTDL/OptiX prepared-left generic segment-pair route | Goal3654: count `4977 == 4977`, RTDL query `0.100411ms`, RayJoin query `0.353115ms`, ratio `0.284x`; 10-second-class totals present on both sides | Current strongest RayJoin-positive RTDL evidence. |
| Overlay active pair-dependency count | RTDL/OptiX prepared shape-pair active-count route | Goal3595: RTDL/OptiX vs CuPy `91.742x` on the 512 public-CDB slice | Strong contract evidence, but still not full polygon overlay materialization. |

## Interpretation

Goal3654 changes the RayJoin reading in one important way: the LSI result is no
longer a sub-millisecond or synthetic-only positive. It is now a public-CDB,
same-slice, long-run comparison against the upstream RayJoin binary for the
visible count contract.

The improvement comes from a generic primitive, not a RayJoin-specific engine
shortcut:

- prepared right segment-pair acceleration structure;
- prepared left segment set uploaded once;
- dense left-id count device column;
- Python app layer owns RayJoin interpretation and left-id remapping.

The remaining RayJoin gap is also now sharper: PIP scalar membership still
belongs to CuPy in the recommended mixed route until RTDL has a better generic
closed-shape membership-count primitive.

## v2.9 Integration Decision

For v2.9 internal performance tracking:

- replace the old fragile `spatial_rayjoin_optix_prepared_full_route` reading
  with contract-specific RayJoin rows;
- use Goal3654 as the current LSI evidence row;
- keep Goal3595 as the mixed-route CuPy-vs-RTDL route-selection evidence;
- do not collapse PIP, LSI, and overlay into one RayJoin scalar speedup.

This is enough RayJoin progress for the current v2.9 lane unless an external
review flags a blocker. Further work should target either the exact PIP
membership primitive or a second-GPU confirmation, not another tiny LSI tuning
round.

## Boundary

This supplement does not authorize:

- public v2.9 release wording;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app RayJoin speedup wording;
- RayJoin paper reproduction wording;
- true zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3657_v2_9_rayjoin_lsi_10s_integration_test tests.goal3654_rayjoin_lsi_10s_prepared_left_long_run_test tests.goal3598_v2_9_rayjoin_performance_first_addendum_test
```
