# Goal1085 Robot Chunked Embree Baseline Packet

Date: 2026-04-29

Valid: `true`

Goal1085 prepares a non-cloud robot Embree baseline runner only. It does not run the heavy baseline, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.

## Scale

- Total poses: `36000000`
- Chunk poses: `200000`
- Chunk count: `180`
- Obstacles: `4096`
- Iterations per chunk: `3`
- Resume controls: `RTDL_GOAL1085_START_CHUNK`, `RTDL_GOAL1085_END_CHUNK`, `RTDL_GOAL1085_SKIP_EXISTING`
- Timing-only control: `RTDL_GOAL1085_TIMING_ONLY=1` writes `timing_chunk_<index>.json` and uses `--skip-validation`.

## Interpretation

Chunked Embree baseline repeats a 200k-pose workload 180 times to cover the same total pose-count as the 36M RTX timing artifact without requiring one huge resident Python object graph. It is a same-total-work engineering baseline, not a same-single-launch baseline, until artifact intake and 2+ AI review decide whether the comparison boundary is acceptable. The generated runner is resumable through RTDL_GOAL1085_START_CHUNK, RTDL_GOAL1085_END_CHUNK, and RTDL_GOAL1085_SKIP_EXISTING. Each chunk uses pose-id offsets so chunk i represents pose ids i*200000+1 through (i+1)*200000.

## Command Template

```bash
PYTHONPATH=src:. python3 scripts/goal839_robot_pose_count_baseline.py --backend embree --pose-count 200000 --obstacle-count 4096 --iterations 3 --worker-count 8 --pose-id-start $(( chunk_index * 200000 + 1 )) --output-json "${output_json}" ${validation_flag}
```

## Boundary

Goal1085 prepares a non-cloud robot Embree baseline runner only. It does not run the heavy baseline, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.
