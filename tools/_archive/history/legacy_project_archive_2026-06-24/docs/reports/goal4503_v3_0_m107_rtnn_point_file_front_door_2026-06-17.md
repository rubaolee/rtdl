# Goal4503 / V3 M107 RTNN Point-File Front Door

## Conclusion

The RTNN benchmark app now exposes the M106 full-batch prepared aggregate route through `--point-file`. On the Goal4500 KITTI-1M CSV, the app front door infers 1,000,000 points, skips synthetic generation, runs one full query batch, and matches the M106 aggregate signature while measuring the same hot-query class.

## Command

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode prepared_optix_ranked_summary --point-file /workspace/data/kitti/rtdl_goal4500/kitti_1m_points.csv --radius 1.0 --k 50 --repeat 5 --query-batch-size 1000000
```

## Front-Door Row

| Field | Value |
| --- | ---: |
| raw JSON | `docs/reports/goal4503_rtnn_kitti_1m_app_point_file_repeat5_2026-06-17.json` |
| external_point_file_used | `True` |
| generated_input.source | `external_point_file` |
| generated_input.generated | `False` |
| point_count | 1,000,000 |
| query_batch_size | 1,000,000 |
| runner result mode | `ranked-summary-aggregate-prepared-query-batch-float32` |
| runner batch_count | 1 |
| median query | 0.154s |
| cold load+pack+prepare+query | 4.833s |

## M106 Consistency

- App front-door query / M106 runner query: 1.001x.
- App front-door cold total / M106 runner cold total: 1.002x.
- Signature delta app minus M106: `{'row_count': 0, 'bounded_neighbor_count': 0, 'nearest_id_checksum': 0, 'kth_id_checksum': 0, 'sum_distance_delta': -2.0489096641540527e-08}`.

## Boundaries

- This proves the app front door reaches the current full-batch aggregate route; it does not change the author-output or paper-reproduction boundary.
- The route still returns ranked-summary aggregates, not author RTNN's full K-id output buffer.
- Public speedup wording remains blocked.
