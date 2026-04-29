# Goal1114 Robot Split Embree Baseline Completion

Date: 2026-04-29

## Verdict

ACCEPT for local/Linux non-OptiX baseline evidence. This goal completes the
Robot Collision Screening Embree baseline in split validation/timing mode:
one small correctness validation chunk plus 180 full-scale timing-only chunks.

This does not authorize a public RTX speedup claim. It is baseline evidence for
later same-source RTX comparison and wording review.

## Scope

- App: `robot_collision_screening`
- Path: `prepared_pose_flags`
- Baseline: `embree_anyhit_pose_count_or_equivalent_compact_summary`
- Validation chunk: 1,000 poses / 128 obstacles, CPU-oracle checked
- Timing chunks: 180 chunks, each 200,000 poses / 4,096 obstacles / 3 iterations
- Total timed pose count: 36,000,000
- Linux scratch path: `/tmp/rtdl_goal1114_robot_split`

## Results

| Item | Result |
|---|---:|
| Validation chunks | 1 |
| Validation status | `ok` |
| Validation correctness parity | `true` |
| Timing chunks | 180 / 180 |
| Timing status | `timing_only` |
| Total timing pose count | 36,000,000 |
| Native Embree any-hit sum | 92.24968472972978 s |
| Native Embree any-hit median chunk | 0.5073218619800173 s |
| Backend scene prepare sum | 269.61262179224286 s |
| Backend scene prepare median chunk | 1.4870285960496403 s |
| Pose/obstacle generation sum | 647.4258873854997 s |
| Ray pack sum | 40.85195774270687 s |
| Runner wall clock | 38:12.49 |
| Max RSS | 1,197,172 KB |

## Important Fix During Run

The first resumed Linux timing run failed at chunk 21. The cause was not Embree
correctness; it was a native-artifact ABI issue in the robot baseline collector:
large global pose IDs produced semantic ray IDs near and beyond native row-ID
limits. The fix adds compact per-chunk ray IDs for scaled native chunks while
preserving global pose IDs in `ray_metadata`.

The fix is intentionally bounded:

- Public/default scaled robot app behavior remains unchanged unless
  `compact_ray_ids=True` is requested.
- Baseline collectors use compact ray IDs to keep native row IDs ABI-safe.
- Postprocess accepts either semantic ray IDs or positional native row IDs.

## Artifacts

- `docs/reports/goal1085_robot_chunked_embree_baseline/validation_chunk_0.json`
- `docs/reports/goal1085_robot_chunked_embree_baseline/timing_chunk_*.json`
- `docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json`
- `docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.md`
- `docs/reports/linux_goal1114_logs/robot_validation_chunk_0.log`
- `docs/reports/linux_goal1114_logs/robot_timing_chunks_0_179.log`
- `docs/reports/linux_goal1114_logs/robot_timing_chunks_0_179_retry.log`
- `docs/reports/linux_goal1114_logs/robot_timing_chunks_0_179_compact_retry.log`

## Boundary

This result proves that the non-OptiX Robot baseline can be collected at the
36M-pose contract scale without the previous CPU-oracle feasibility block. It
does not prove a public NVIDIA RT-core speedup. Public claims still require
same-source RTX reruns, phase-aligned comparison, and public wording review.
