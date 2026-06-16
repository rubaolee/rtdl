# Goal4461 V3.0 M65 Triangle Segmented RT-2A1

## Result

Goal4461 adds an explicit Triangle Counting RT-Graph 2A1 segmented route:
`rt_graph_2a1_segmented_generic_rt`.

The route builds only the CuPy directed CSR and a two-hop row-count estimate,
then reuses one generic OptiX prepared 3-D triangle scene while lowering
duplicate two-hop rays in bounded segments. It does not build the previous
global `two_hop_keys` array, does not run global `cp.unique` over all two-hop
pairs, and does not materialize the global two-hop summary columns.
In short, it uses segmented duplicate two-hop rays rather than a global
two-hop summary relation.

## Pod Evidence

Command:

```bash
PYTHONPATH=src:. python3 scripts/v3_0_m65_triangle_segmented_2a1_measure.py \
  --cliques 200000 \
  --warmup 1 \
  --repeat 3 \
  --segment-max-two-hop-rows 200000 \
  --hardware 'RTX 4000 Ada pod' \
  --output docs/reports/goal4461_v3_0_m65_triangle_segmented_2a1_200000_2026-06-16.json
```

Measured row:

| input | directed edge triangles | duplicate two-hop rays | segments | result |
| --- | ---: | ---: | ---: | --- |
| 200,000 disjoint K4 cliques | 1,200,000 | 800,000 | 4 | 800,000 / 800,000 oracle match |

Timing:

| phase | time |
| --- | ---: |
| directed CSR contract build | 671.585 ms |
| segment planning + triangle columns | 274.912 ms |
| OptiX scene prepare | 494.254 ms |
| segment ray build median | 5.611 ms |
| RT query median across 4 segments | 4.883 ms |
| total wall | 1.569 s |

The evidence records `global_two_hop_summary_materialized=false`,
`two_hop_summary_materialized=false`, and `triangle_count_matches_oracle=true`.

## Interpretation

This closes the immediate Triangle Counting memory-shape debt for RT-2A1
lowering: RTDL can now express the workload as bounded batches of generic
rays against a reusable generic triangle scene instead of requiring one global
two-hop intermediate relation.

The route preserves the current RTDL design boundary:

- Graph orientation, CSR construction, and segmentation are app/partner work.
- The native engine receives only generic `Triangle3D` device columns, generic
  `Ray3D` device columns, unit weights, and a scalar weighted any-hit summary.
- No graph-specific OptiX program, graph-specific native ABI, hidden partner
  selection, or app-specific native engine logic is added.

## Claim Boundary

This is not a triangle-counting RT-core speedup claim, not a whole-app speedup
claim, and not public benchmark wording. It is internal V3 route evidence that
the generic RT primitive path can avoid the previous global two-hop
materialization failure mode.

Remaining work before any paper-dataset performance claim:

- Run the segmented route on the RT-Graph paper datasets that previously OOMed.
- Compare the segmented route against the current CuPy global-summary route,
  the no-C++ Numba reference, cuGraph, and authors' RT-Graph code under one
  explicit timing contract.
- Decide whether a Numba segmented reference is worth building or whether the
  current direct-binary Numba global-summary path is sufficient as the no-C++
  reference for this app.

Evidence:

- `docs/reports/goal4461_v3_0_m65_triangle_segmented_2a1_200000_2026-06-16.json`
