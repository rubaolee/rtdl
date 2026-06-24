# Phoenix V3 RTNN Neighbor Symbol-Cache Focused Evidence

Date: 2026-06-22
Status: `focused_generic_runtime_hygiene_validated_no_material_speedup`

## Summary

This packet records a focused Phoenix V3 runtime hygiene fix for the RTNN
prepared 3-D ranked-summary route. It is intentionally classified as
`no_material_speedup`: the patch is valid generic runtime work, but the pod
evidence does not move V3 toward the major-version performance bar.

The fix is generic runtime work:

- `src/rtdsl/optix_runtime.py`
  - `PreparedOptixFixedRadiusNeighbors3D` now caches the loaded OptiX library
    and optional native symbols used by prepare/run/aggregate/count/close.
- `src/rtdsl/embree_runtime.py`
  - `PreparedEmbreeFixedRadiusNeighbors3D` now caches optional native symbols
    used by create/run/aggregate/destroy.
- `tests/goal4351_embree_rtnn_ranked_summary_parity_test.py`
  - Adds regression tests proving prepared Embree and OptiX ranked-summary
    handles look up hot native symbols once while allowing repeated runs.

This is not an RTNN-specific shortcut, does not change the ranked-summary
contract, and does not authorize V3 release or broad V3-over-V2 speedup wording.

## Evidence

Remote patch validation:

```text
pod: root@213.173.108.14 -p 11592
hardware: NVIDIA RTX 4000 Ada Generation
remote run dir: /root/rtdl_v3_rebuild_20260620/phoenix_v3_rtnn_neighbor_symbol_cache_focused_20260622_142004
local evidence dir: docs/rebuild/v3/evidence/phoenix_v3_rtnn_neighbor_symbol_cache_focused_20260622_142004/
patched current hashes:
  src/rtdsl/optix_runtime.py 0f49224823d39e8b36591d56fc0bbecfa476513555b7d97e3aad6d534ecd7c46
  src/rtdsl/embree_runtime.py e7967d9ad7d6409d56b9a766b5240c592dc4a25e49b9c987d901ce98c68318aa
  tests/goal4351_embree_rtnn_ranked_summary_parity_test.py cdcc157a4d1d7ed12b0e3ff3771e00ff3a99415ed7d5d441088bba0cacc6d0ab
artifact hashes:
  v2_14_goal2636_rtnn_stress/summary.json 2c7b035dd7c9d3ac14d3f52792de8daf25a0d47f3fe6969cf7415b34466ccd1b
  current_patched_goal2636_rtnn_stress/summary.json 7438fdbb51b6503a627c328a86fbf5992c9048ee7f220109e0d1ef4f55ec05d6
```

Local focused tests:

```text
PYTHONPATH=src py -3 -m unittest \
  tests.goal4351_embree_rtnn_ranked_summary_parity_test \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.v3_phoenix_aabb_prepared_query_cache_test \
  tests.v3_phoenix_major_performance_mandate_gate_test \
  tests.v3_release_wording_gate_test

Ran 32 tests in 0.052s
OK (skipped=2)
```

Remote targeted test:

```text
PYTHONPATH=src python3 -m unittest tests.goal4351_embree_rtnn_ranked_summary_parity_test

Ran 5 tests in 0.002s
OK
```

Focused run:

```text
V2.14:
  scripts/goal2636_strengthen_benchmark_rows.py --tier stress --only-app rtnn --case-repeat 5
Patched current:
  scripts/goal2636_strengthen_benchmark_rows.py --tier stress --only-app rtnn --case-repeat 5
```

## Focused Results

Metric: `primary_metric_sec`, sourced from `elapsed_sec`.

| case | backend | V2.14 sec | patched V3 sec | patched V3 vs V2.14 |
| --- | --- | ---: | ---: | ---: |
| `rtnn_embree_uniform_65536_ranked_summary` | Embree | 0.114483 | 0.113981 | 1.004x |
| `rtnn_optix_uniform_65536_ranked_summary` | OptiX | 0.105459 | 0.104813 | 1.006x |
| `rtnn_embree_clustered_65536_ranked_summary` | Embree | 0.640965 | 0.596361 | 1.075x |
| `rtnn_optix_clustered_65536_ranked_summary` | OptiX | 0.171046 | 0.170208 | 1.005x |
| `rtnn_embree_shell_65536_ranked_summary` | Embree | 0.120750 | 0.124607 | 0.969x |
| `rtnn_optix_shell_65536_ranked_summary` | OptiX | 0.108046 | 0.108092 | 1.000x |
| `rtnn_embree_uniform_262144_ranked_summary` | Embree | 0.462165 | 0.474858 | 0.973x |
| `rtnn_optix_uniform_262144_ranked_summary` | OptiX | 0.421333 | 0.428646 | 0.983x |
| `rtnn_embree_clustered_262144_ranked_summary` | Embree | 11.998322 | 12.027364 | 0.998x |
| `rtnn_optix_clustered_262144_ranked_summary` | OptiX | 1.380053 | 1.376287 | 1.003x |
| `rtnn_embree_shell_262144_ranked_summary` | Embree | 1.621688 | 1.647720 | 0.984x |
| `rtnn_optix_shell_262144_ranked_summary` | OptiX | 0.548288 | 0.542497 | 1.011x |

Aggregate:

```text
same-case rows: 12
geomean patched V3 vs V2.14: 1.001x
rows faster by >5%: 1
rows within +/-5%: 11
rows slower by >5%: 0
```

## Interpretation

- The symbol-cache patch is valid hot-path hygiene and has regression tests.
- It does not materially improve RTNN performance at stress scale.
- It does not close the V3 major-version performance gap.
- RTNN's real remaining issue is not repeated `ctypes` symbol lookup. The
  heavier problem remains the ranked-summary contract and host-side/materialized
  summary pathway versus the earlier blocked full-batch/device-resident
  experiments.
- Because the full-batch float32 route was previously classified
  `not_m7`/review-blocked, it must not be smuggled into V3 as a performance win.

## Release Impact

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

This report should be used as a guardrail: do not spend more Phoenix time
expecting RTNN symbol lookup caching to rescue V3. Move to larger reusable
runtime-contract work or another proven bottleneck.

## Decision Audit

Decision: accept the RTNN prepared-neighbor symbol-cache patch as tested runtime
hygiene, but classify it as no-material-speedup and do not count it as V3
release progress.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? None. The foolish action
   would have been claiming the 1.066x single 65k Embree clustered row as RTNN
   solved while ignoring the 1.001x 12-row geomean.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could have skipped this small hot-path hypothesis and immediately
   targeted a larger contract-level RTNN redesign, but that would have left an
   easy suspected overhead unmeasured.
4. Can I now try a different path that actually solves the problem? Yes. Treat
   RTNN symbol caching as closed and move to larger generic runtime work:
   prepared execution/accounting reductions that affect many rows, or a
   contract redesign only if it stays within V3 and passes review.
