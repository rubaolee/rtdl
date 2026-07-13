# Goal5109 - RT-DBSCAN UCI 3DRoad OptiX+CuPy Semantic Gap

Date: 2026-07-07

## Verdict

```text
optix_cupy_runs_1k_but_matches_conventional_not_author_directional_contract
```

Goal5109 tests a GPU partner route that avoids the Goal5108 Numba/PTX blocker.
The route runs on the POD, but it does not match the pinned AuthorOfficial
directional-border contract on the 1K UCI 3DRoad same-source candidate.

This is a useful negative result: the remaining 3DRoad gap is not merely
"Numba cannot run on the POD." The existing generic RTDL OptiX+CuPy grouped
stream component-label route behaves like the conventional DBSCAN partition on
this input, while the pinned author binary uses an index-directional border
assignment rule.

## What Changed

The RT-DBSCAN app runner now supports:

```text
--backend optix_cupy_component_signature
```

Implemented in:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py
```

This backend calls existing generic RTDL APIs:

```text
prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(...)
radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns(...)
```

It does not add a DBSCAN-specific RTDL core primitive and does not encode the
author's `xID > primID` rule in RTDL core.

## POD Execution

POD:

```text
ssh root@213.173.108.24 -p 13502
```

The Goal5108 Numba route remains blocked by PTX version mismatch, so Goal5109
used a POD venv with CuPy installed:

```text
/tmp/rtdl_numba_compat_venv
cupy==14.1.1
```

Command:

```text
cd /root/rtdl_goal5093
PYTHONPATH=/root/rtdl_goal5093/src \
RTDL_OPTIX_LIB=/root/rtdl_goal5093/build/librtdl_optix.so \
RTDL_OPTIX_LIBRARY=/root/rtdl_goal5093/build/librtdl_optix.so \
LD_LIBRARY_PATH=/root/rtdl_goal5093/build:/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH \
/tmp/rtdl_numba_compat_venv/bin/python \
  Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py \
  --input Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/uci_3droad_1k_author_2d_zero_z.csv \
  --epsilon 0.05 \
  --min-points 100 \
  --backend optix_cupy_component_signature \
  --author-payload Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_goal5107_clean.jsonl \
  --summary Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_optix_cupy_author_directional_gate_summary.json
```

The command exits nonzero because the comparator gate correctly fails, but it
writes a summary JSON.

Summary artifact:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_optix_cupy_author_directional_gate_summary.json
```

## Result

```text
matched=false
signature_matched=false
component_partition_matched=false
core_flags_matched=true
```

RTDL OptiX+CuPy signature:

```text
{core_count=329, component_count=3, component_sizes=[102,168,181], noise_count=549}
```

AuthorOfficial directional signature:

```text
{core_count=329, component_count=3, component_sizes=[90,168,181], noise_count=561}
```

The RTDL result matches the conventional CPU-reference signature previously
observed in Goals5107-5108, not the pinned AuthorOfficial directional
signature.

Core flags still match:

```text
core_flags_matched=true
```

Therefore the fixed-radius core predicate agrees, and the mismatch is in border
assignment / component partition semantics.

## RTDL Route Metadata

The RTDL route reports:

```text
backend=optix_cupy_component_signature
partner=cupy
partner_reference_contract=generic_prepared_optix_cupy_grouped_stream_component_labels_3d
grouped_stream_policy=optix_applies_predicated_union_and_border_candidate_during_traversal
materializes_neighbor_rows=false
materializes_directed_adjacency_stream=false
rt_core_accelerated=true
```

This confirms the route exercised the generic RTDL OptiX grouped-stream
component-label pipeline with a CuPy partner. It does not confirm
AuthorOfficial parity.

## Interpretation

Goal5109 changes the diagnosis:

```text
Before: RTDL 3DRoad route may simply be blocked by Numba/PTX environment.
After: a non-Numba RTDL GPU route runs, but it follows conventional semantics,
       not the pinned author's directional border contract.
```

The author-specific rule is:

```text
callNum == 2 && xID > primID
```

That rule is not ordinary DBSCAN. It is an AuthorOfficial comparator detail.
Promoting it into RTDL core as default DBSCAN behavior would be wrong.

## What This Proves

Proved:

- The POD can run an RTDL GPU partner route for the 1K UCI 3DRoad candidate via
  OptiX+CuPy.
- The RTDL route does not match the pinned AuthorOfficial directional-border
  contract on this input.
- The mismatch is semantic, because the core flags match and only the partition
  / signature diverges.
- The generic RTDL route remains app-neutral; it does not encode author
  `xID > primID` behavior.

Not proved:

- RTDL reproduces the AuthorOfficial 1K UCI 3DRoad output.
- RTDL reproduces exact RT-DBSCAN paper inputs.
- RTDL performance is better or worse on 3DRoad.
- The author-directional rule should become a public RTDL primitive.
- The OptiX+Numba blocker is fixed.

## Claim Boundary

Allowed:

```text
Goal5109 ran the existing generic RTDL OptiX+CuPy grouped-stream component route
on the 1K UCI 3DRoad same-source candidate. It executed successfully but failed
the AuthorOfficial directional-border comparator: RTDL produced the conventional
signature [102,168,181]/549, while AuthorOfficial produced [90,168,181]/561.
```

Forbidden:

```text
RTDL matches AuthorOfficial on UCI 3DRoad.
RTDL reproduces exact RT-DBSCAN paper input/output.
The 3DRoad mismatch is only a Numba/PTX environment problem.
The author directional border policy is a generic RTDL DBSCAN semantic.
The CuPy route proves a performance claim.
```

## Tests

Command:

```text
py -m unittest tests.goal5109_rt_dbscan_optix_cupy_author_contract_gap_test tests.goal5108_rt_dbscan_author_directional_gate_test tests.goal5107_rt_dbscan_uci_3droad_contract_analysis_test tests.goal5094_rt_dbscan_authorofficial_component_signature_gate_test tests.goal5101_component_partition_helpers_test
```

Result:

```text
Ran 15 tests in 1.040s
OK
```

JSON validation:

```text
manifest.json: ok
uci_3droad_1k_optix_cupy_author_directional_gate_summary.json: ok
uci_3droad_1k_author_directional_gate_summary.json: ok
```

Coverage:

- the CuPy summary is present;
- the CuPy route reports `matched=false`;
- RTDL signature is the conventional `[102,168,181]/549`;
- AuthorOfficial signature is `[90,168,181]/561`;
- core flags match;
- the route metadata is generic OptiX+CuPy grouped stream;
- no paper reproduction or performance claim is authorized.

## Next Recommended Decision

Owner decision after Goal5109:

```text
Do not open a new author-directional SoS / border-assignment route.
The project's SoS and degeneracy protocols were settled through the RayJoin
line and are not reopened for RT-DBSCAN.
```

Therefore the honest path is:

1. Keep the current OptiX+CuPy route as the generic RTDL DBSCAN/component
   partition behavior.
2. Mark pinned AuthorOfficial directional parity on this UCI 3DRoad candidate
   as not targeted unless the author output is reinterpreted under the already
   fixed RTDL protocol.
3. Treat the `xID > primID` border rule as a pinned-author implementation
   detail, not a new RTDL language contract and not an app-specific semantic
   fork to pursue.

Do not silently relabel the generic RTDL conventional result as AuthorOfficial
reproduction.
