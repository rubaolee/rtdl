# Goal1112 Robot Timing-Only Chunk Linux Probe

Date: 2026-04-29

## Result

Status: ACCEPT FOR NEXT RUNNER/INTAKE UPDATE

The Goal1111 timing-only Robot Embree mode completed one real 200k-pose Linux chunk successfully. This confirms the Goal1110 blocker was per-chunk CPU-oracle validation, not Embree timing itself.

## Command

```text
/usr/bin/time -v env PYTHONPATH=src:. python3 scripts/goal839_robot_pose_count_baseline.py --backend embree --pose-count 200000 --obstacle-count 4096 --iterations 3 --worker-count 8 --pose-id-start 1 --skip-validation --output-json docs/reports/goal1085_robot_chunked_embree_baseline/chunk_0_timing_only.json
```

## Artifact Summary

| Field | Value |
| --- | ---: |
| `status` | `timing_only` |
| `correctness_parity` | `null` |
| `validation.skipped` | `true` |
| Pose count | `200,000` |
| Obstacle count | `4,096` |
| Iterations | `3` |
| Native any-hit query | `0.557197 s` |
| Backend scene prepare | `9.150581 s` |
| Pose/ray generation + pack | `2.405793 s` |
| Wall clock | `0:20.63` |
| Max RSS | `1,191,920 KB` |
| Exit status | `0` |

## Estimate

At roughly `20.63 s` per chunk, 180 chunks would take about `61.9 minutes` if chunk cost remains stable. This is feasible for a non-cloud Linux/Windows run, unlike the previous validated-per-chunk contract where one chunk exceeded 12 minutes and was terminated.

## Artifacts

- `docs/reports/goal1112_robot_timing_only_chunk/chunk_0_timing_only.json`
- `docs/reports/linux_goal1112_logs/goal1112_robot_chunk0_timing_only.log`

## Next Move

Update Goal1085/Goal1086 to formalize two artifact classes:

- validation chunks: small/medium chunks with `correctness_parity: true`;
- timing chunks: all 180 production chunks with `status: timing_only`.

Only after the revised intake and 2+ AI review should we run all 180 chunks.

## Boundary

This probe does not authorize public RTX speedup claims. It proves timing-only chunk execution is feasible and remains separate from correctness validation.
