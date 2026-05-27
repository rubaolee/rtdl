# Goal2633 Barnes-Hut Same-Contract Matrix Closure

Date: 2026-05-27

This internal note closes the immediate Barnes-Hut comparison-contract gap in
the Goal2626 Embree-vs-OptiX matrix. The old matrix compared Embree
fixed-radius candidate rows against OptiX prepared node-coverage threshold
decisions. Those are not the same contract.

## Change

- The Barnes-Hut app now exposes the prepared node-coverage threshold decision
  for both Embree and OptiX through the generic
  `FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)` primitive.
- The benchmark wrapper has a new `embree_node_coverage_prepared` mode.
- The Goal2626 matrix now compares:
  - `barnes_hut_embree_node_coverage`
  - `barnes_hut_optix_node_coverage`
- Both rows use the same primary metric:
  `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec`.

## Pod Evidence

Pod command supplied by the user:

```text
ssh root@203.57.40.101 -p 10165 -i ~/.ssh/id_ed25519
```

Working key used from this Mac:

```text
/Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Validation was run from a clean Git checkout:

```text
commit eabbe337a370ba9ce7ed8c381848bf94fcb8da69
git status --short: clean
GPU: NVIDIA RTX A5000, driver 565.57.01, 24564 MiB
CUDA: 12.6
OptiX SDK: /root/vendor/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64
```

Commands validated:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2530_barnes_hut_benchmark_app_promotion_test \
  tests.goal2626_benchmark_embree_optix_baseline_test

PYTHONPATH=src:. python3 scripts/goal2626_benchmark_embree_optix_baseline.py \
  --scale standard \
  --only-app barnes_hut \
  --artifact-dir /root/rtdl_goal2627/barnes_goal2633_standard \
  --timeout-sec 900
```

Artifact copies:

- `docs/reports/goal2633_barnes_hut_same_contract_pod/summary.json`
- `docs/reports/goal2633_barnes_hut_same_contract_pod/summary.md`

## Standard Result

| Route | Primary metric | Time |
| --- | ---: | ---: |
| Embree prepared node coverage | `query_fixed_radius_threshold_reached_count_sec` | `0.0356091s` |
| OptiX prepared node coverage | `query_fixed_radius_threshold_reached_count_sec` | `0.00874006s` |
| OptiX speedup vs Embree | | `4.07x` |

This is not a full RT-BarnesHut force-aggregation claim. It is the same-contract
node-coverage threshold subpath only.

## Remaining Boundary

The broader Barnes-Hut pressure point is still the hierarchical aggregate
frontier plus weighted force accumulation. RTDL has reference contracts for
that behavior, but the promoted Embree/OptiX comparison is now intentionally
narrower and same-contract. A future improvement should lower the generic
aggregate-frontier contract itself to native/partner execution without adding a
Barnes-Hut-specific native force formula.
