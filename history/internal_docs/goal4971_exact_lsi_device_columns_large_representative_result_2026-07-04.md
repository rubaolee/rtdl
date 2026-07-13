# Goal4971 Exact LSI Device Columns Large Representative Result

Date: 2026-07-04

## Verdict

`exact_lsi_device_columns_large_input_speedup_confirmed__but_not_a_root_bottleneck_fix`

The existing exact planar-map LSI device-column route works on the large
`top4_county_zipcode_arcgis_same_source` representative Section 5.7 input and
improves the fresh writer-free binary route:

```text
normal fresh binary route:              7.851479s
exact LSI device-column fresh route:    5.903873s
speedup:                                1.33x
```

The LSI stage itself improves:

```text
normal public LSI rows:                 4.313502s
exact pair-id device columns:           2.749540s
LSI-stage speedup:                      1.57x
```

This is a real large-input win over the normal binary route, but it is not the
root solution to the remaining RayJoin performance gap. The exact route still
spends about `2.75s` in LSI production. The next bottleneck is exact planar-map
LSI compute/predicate/traversal, not row-residency wrappers.

## POD Environment Repair

The new POD was not initially runnable. Two environment mismatches had to be
fixed before measuring RTDL:

1. Numba 0.66 generated PTX 8.7, while the installed driver JIT supported PTX
   8.4. Fixed by pinning Numba to `0.61.2` and using CUDA 12.4 NVVM from
   `nvidia-cuda-nvcc-cu12==12.4.131`.
2. The official `NVIDIA/optix-dev` repository currently provided OptiX 9.1
   headers (`OPTIX_ABI_VERSION 118`), which the POD's driver rejected. Fixed by
   rebuilding `librtdl_optix.so` against OptiX 7.7 headers
   (`OPTIX_VERSION 70700`, `OPTIX_ABI_VERSION 84`) extracted from NVIDIA's
   OptiX 7 API documentation.

After that, a minimal public LSI smoke passed:

```text
base segment:  id=1, horizontal [0,0] -> [1,0]
query segment: id=2, vertical   [0.5,-1] -> [0.5,1]
result:        ({left_id: 2, right_id: 1, x: 0.5, y: 0.0},)
```

Environment record:

```text
POD:          root@213.173.108.6 -p 10626
GPU:          NVIDIA RTX 4000 Ada Generation
Driver:       550.127.05, CUDA driver 12.4
Python:       3.12.3
Numba:        0.61.2
llvmlite:     0.44.0
NumPy:        2.2.6
OptiX header: 7.7 / ABI 84
```

## Input

Same large representative top4 County x Zipcode input as Goal4970:

```text
left / County:
  chains: 1612
  points: 1706639
  edges:  1705027

right / Zipcode:
  chains: 10144
  points: 9993104
  edges:  9982960
```

This remains a same-source representative input, not an exact paper eight-pair
input claim.

## Routes Measured

All routes used:

```text
--device-columnar
--validate-device-order
--compiled-group
```

Measured routes:

| Route | Meaning | Fresh overlay? |
|---|---|---:|
| `rtdl_binary_fresh` | normal public LSI rows + device-columnar downstream | yes |
| `rtdl_binary_exact_lsi_device_columns` | exact LSI pair-id device columns + downstream NumPy copy | yes |
| `rtdl_binary_prepared_replay` | cached prepared LSI replay diagnostic | no |

Prepared replay is retained only as a cache/replay diagnostic. It must not be
compared as a fresh overlay run.

## Correctness Gates

The exact route matches the normal route on the large representative gates:

```text
lsi_row_count:             428322
xsect_sorted_counts side0: 428322
xsect_sorted_counts side1: 428322
vertex side0_in_side1:     812721
vertex side1_in_side0:     4527305
device sort validation:    true for both maps
```

No text byte-equality claim is made for the binary route. The paper text sink
remains a separate correctness anchor from Goal4970.

## Performance Table

| Phase / route | Normal fresh | Exact LSI device columns | Prepared replay diagnostic |
|---|---:|---:|---:|
| writer-free hot | `7.851479s` | `5.903873s` | `2.636492s` |
| LSI | `4.313502s` | `2.749540s` | `0.008990s` replay |
| exact LSI device-columns to NumPy | n/a | `0.003534s` | n/a |
| reprojection device-columnar | `0.238768s` | `0.235733s` | `0.245096s` |
| sort map0 device-columnar | `0.032100s` | `0.032737s` | `0.033044s` |
| sort map1 device-columnar | `0.093929s` | `0.094498s` | `0.097044s` |
| vertex PIP map0 in map1 | `0.125642s` | `0.145777s` | `0.140592s` |
| vertex PIP map1 in map0 | `1.188992s` | `0.805516s` | `0.811696s` |
| midpoint points map0 | `0.593655s` | `0.631613s` | `0.591049s` |
| midpoint points map1 | `0.589168s` | `0.588578s` | `0.571597s` |
| grouped carrier construction | `0.644982s` | `0.584209s` | `0.106032s` |
| descriptor consumer | `0.016403s` | `0.016670s` | `0.017528s` |

## Interpretation

The large-input result answers the Goal4971 question:

- The exact LSI device-column route is no longer a pure no-go at scale.
- It gives a real `1.33x` writer-free fresh-route improvement.
- Its downstream copy cost is tiny (`0.003534s`), so residency/copy is not the
  limiting factor.
- The route still spends `2.749540s` in exact LSI production, so the remaining
  issue is the LSI computation/traversal contract itself.

The important negative result remains:

```text
row-residency alone does not close the LSI gap.
```

The next optimization target should not be another wrapper around LSI rows. It
should be the exact planar-map LSI producer itself: fewer passes, less duplicate
work, better predicate/traversal behavior, or eventually in-traversal fusion if
the owner authorizes that later.

## Claim Boundary

Authorized:

- exact LSI device columns work on the large representative Section 5.7 input
- fresh writer-free binary route improves from `7.851479s` to `5.903873s`
- LSI stage improves from `4.313502s` to `2.749540s`
- this is still a generic pair-id column route, not a RayJoin-specific core
  primitive

Not authorized:

- broad RayJoin paper performance claim
- text byte-equality claim for this binary route
- prepared replay as fresh overlay performance
- public high-performance claim
- claim that row-residency fixed the root LSI bottleneck
- claim that RTDL is close to the author fused overlay compute on this route

## Artifacts

Artifacts are stored at:

```text
history/internal_docs/goal4971_exact_lsi_device_columns_large_representative_artifacts_2026-07-04/
```

Key files:

```text
goal4970_top4_section57_matrix_summary.json
rtdl_binary_fresh_section57_overlay.json
rtdl_binary_exact_lsi_device_columns_section57_overlay.json
rtdl_binary_prepared_replay_section57_overlay.json
environment.txt
```
