# Goal1090 Robot Embree Local Baseline Runbook

Date: 2026-04-29

Valid: `true`

Goal1090 is a non-cloud robot baseline execution runbook. It does not run the heavy baseline, does not create cloud resources, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.

## Host Policy

- Host: `non_cloud_linux_or_windows_preferred`
- Not pod work: `True`

## Scale Contract

- `total_pose_count`: `36000000`
- `chunk_count`: `180`
- `chunk_pose_count`: `200000`
- `obstacle_count`: `4096`
- `pose_id_start_formula`: `chunk_index * 200000 + 1`
- `resume_controls`: `['RTDL_GOAL1085_START_CHUNK', 'RTDL_GOAL1085_END_CHUNK', 'RTDL_GOAL1085_SKIP_EXISTING']`

## Steps

| Step | Heavy | Purpose | Command |
| --- | --- | --- | --- |
| `smoke_one_small_embree_chunk` | `False` | Verify local Embree/native baseline plumbing before starting the heavy 180-chunk run. | `PYTHONPATH=src:. python3 scripts/goal839_robot_pose_count_baseline.py --backend embree --pose-count 1000 --obstacle-count 128 --iterations 1 --worker-count 1 --pose-id-start 1 --output-json build/goal1090_robot_embree_smoke.json` |
| `run_one_real_chunk` | `True` | Run one claim-scale chunk and confirm it writes the expected chunk artifact. | `RTDL_GOAL1085_START_CHUNK=0 RTDL_GOAL1085_END_CHUNK=0 RTDL_GOAL1085_SKIP_EXISTING=1 bash scripts/goal1085_robot_chunked_embree_baseline_runner.sh` |
| `intake_after_partial_or_full_run` | `False` | Aggregate present chunks and report missing/invalid chunk indices without authorizing claims. | `PYTHONPATH=src:. python3 scripts/goal1086_robot_chunked_embree_baseline_intake.py` |
| `run_remaining_chunks_when_host_is_available` | `True` | Complete the same-total-work non-cloud Embree baseline over all 36M pose ids. | `RTDL_GOAL1085_SKIP_EXISTING=1 bash scripts/goal1085_robot_chunked_embree_baseline_runner.sh` |
| `final_intake` | `False` | Produce complete aggregate evidence after all 180 chunks exist. | `PYTHONPATH=src:. python3 scripts/goal1086_robot_chunked_embree_baseline_intake.py` |

## Boundary

Goal1090 is a non-cloud robot baseline execution runbook. It does not run the heavy baseline, does not create cloud resources, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.
