# Goal2632 Spatial RayJoin Prepared Full-Route Closure

Date: 2026-05-27

This internal note closes the immediate Spatial RayJoin gap from the Goal2629
optimization audit: the promoted benchmark matrix was timing the generic
OptiX fallback for the full RayJoin-style route, while the serious prepared
OptiX route covered only PIP and LSI.

## Change

- `prepared_optix` now covers all three benchmark workloads: PIP, LSI, and
  overlay-seed pair-dependency flags.
- Overlay-seed uses the existing generic
  `prepare_shape_pair_relation_flags_optix` primitive. No RayJoin-specific
  native engine symbol or app-specific native logic was added.
- The Goal2626 matrix now uses
  `spatial_rayjoin_optix_prepared_full_route` for the OptiX row, with
  `prepared_query_total_sec` as the primary metric.
- The Embree row remains the same generic front door and is compared against
  the OptiX backend-query total under
  `rayjoin_all_backend_query_summary`.

## Pod Evidence

Pod command supplied by the user:

```text
ssh root@203.57.40.101 -p 10165 -i ~/.ssh/id_ed25519
```

Working key used from this Mac:

```text
/Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Validation was run from a clean Git checkout on the pod:

```text
commit 4960079ebe4d72689da49a5bf05cfd824b36a887
git status --short: clean
GPU: NVIDIA RTX A5000, driver 565.57.01, 24564 MiB
CUDA: 12.6
OptiX SDK: /root/vendor/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64
```

Commands validated:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2327_rayjoin_prepared_route_contract_test \
  tests.goal2626_benchmark_embree_optix_baseline_test

PYTHONPATH=src:. python3 scripts/goal2626_benchmark_embree_optix_baseline.py \
  --scale quick \
  --only-app spatial_rayjoin \
  --artifact-dir /root/rtdl_goal2627/spatial_goal2632_quick \
  --timeout-sec 900
```

Artifact copies:

- `docs/reports/goal2632_rayjoin_prepared_full_route_pod/summary.json`
- `docs/reports/goal2632_rayjoin_prepared_full_route_pod/summary.md`

## Quick Smoke Result

| Route | Primary metric | Time |
| --- | ---: | ---: |
| Embree generic full route | `workloads.total_elapsed_sec` | `0.0199522809s` |
| OptiX prepared full route | `prepared_query_total_sec` | `0.0005352600s` |
| OptiX speedup vs Embree | | `37.276x` |

This is a functional and path-selection result, not a public performance
claim. The default RayJoin fixture is tiny and overlay-seed is zero-row on that
fixture. A serious second-scale RayJoin performance row still needs a larger
RayJoin/CDB fixture or a scale-aware benchmark route.

## Boundary

- The native engine sees generic point/closed-shape, segment-pair, and
  shape-pair prepared contracts.
- RayJoin policy, RayJoin paper interpretation, and full polygon overlay
  materialization remain in the app layer or out of scope for this benchmark.
- This closes the "missing prepared continuation for the full route" as an
  overlay-seed pair-dependency benchmark route. It does not claim full RayJoin
  reproduction or whole-app RayJoin speedup.
