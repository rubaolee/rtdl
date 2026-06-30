# Goal 1528: Goal1506 Pod Stage-Profile Intake

## Verdict

Accepted Goal1506 pod evidence was collected on the paid NVIDIA pod for the
OptiX `COLLECT_K_BOUNDED` row_width=2 tiled stage-profile path.

The pod run used current `main` at commit
`0274ca32d3dd76d7dfc3f4214375db93b8838908`, OptiX SDK tag `v8.0.0`
(`bef93afb12dbd00e5b8311bc9b320dd487d8cc1f`), and an `NVIDIA RTX 2000 Ada
Generation` GPU with driver `570.172.08`.

## Pod Scope

- SSH target: `root@213.173.110.196 -p 24309`
- GPU: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- CUDA reported by `nvidia-smi`: `12.8`
- OptiX SDK source: `https://github.com/NVIDIA/optix-sdk`
- OptiX SDK tag: `v8.0.0`
- RTDL commit: `0274ca32d3dd76d7dfc3f4214375db93b8838908`
- Command packet: `docs/reports/goal1527_v1_5_4_next_pod_stage_profile_packet_2026-05-08.md`

## Required Artifacts

- `docs/reports/goal1508_v1_5_4_optix_collect_k_tiled_preflight_2026-05-08.json`
- `docs/reports/goal1508_v1_5_4_optix_collect_k_tiled_preflight_2026-05-08.md`
- `docs/reports/goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.json`
- `docs/reports/goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.md`
- `docs/reports/goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.jsonl`
- `docs/reports/goal1527_v1_5_4_next_pod_stage_profile_transcript_2026-05-08.txt`

## Acceptance

Goal1508 accepted all three target counts as tiled-profile candidates. Each
case had `max_optin_shared_memory_per_block_bytes=101376`, above the
`69632` byte row_width=2 tiled requirement.

Goal1506 reported `accepted_goal1506_evidence=true`. The runner's unittest
slice passed:

```text
Ran 33 tests in 0.004s
OK
```

## Stage Timing Summary

| Candidate rows | Median wrapper ms | Median native stage total ms | Sort sync ms | Merge sync ms | Metadata ms | Final copy ms |
|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 1.778916 | 1.526860 | 0.885174 | 0.339783 | 0.023290 | 0.003450 |
| 65537 | 79.631049 | 79.377400 | 11.748100 | 67.207700 | 0.067023 | 0.002690 |
| 131072 | 180.659663 | 180.287000 | 23.397100 | 156.370000 | 0.068723 | 0.006441 |

The measured large-count bottleneck is merge synchronization time. Metadata
download and final device-to-device copy are small in this accepted package.

## Claim Boundary

This intake records accepted Goal1506 stage-profile evidence only. It does not
authorize public speedup wording, broad RTX/GPU claims, true zero-copy wording,
whole-app claims, stable `COLLECT_K_BOUNDED` promotion, or release action.
