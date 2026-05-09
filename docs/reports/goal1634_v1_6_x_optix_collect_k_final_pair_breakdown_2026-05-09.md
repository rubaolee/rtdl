# Goal1634 v1.6.x OptiX Collect-K Final-Pair Breakdown

## Verdict

`final_pair_mark_sync_identified`

Goal1634 adds internal stage-profile instrumentation for the production final-pair collect-k path and records a short A4500 probe. The measured bottleneck is the final-pair mark/sync stage, not materialize, compact, or host prefix.

## Scope

- Code change: profile-only instrumentation in `src/native/optix/rtdl_optix_api.cpp`; no kernel selection or result semantics are changed.
- Probe summarizer update: `scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py` now summarizes the new fields and remains compatible with older JSONL records.
- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Probe environment:
  - `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`
  - `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`
- Probe command: `python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py --library build/librtdl_optix.so --repeats 3 --counts 262144 --json-out docs/reports/goal1634_final_pair_breakdown_262144_repeats3.json --md-out docs/reports/goal1634_final_pair_breakdown_262144_repeats3.md`.

## Result

For `candidate_count=262144`, `tile_count=128`, and `merge_levels=7`, median stage fields were:

| field | median_ms |
| --- | ---: |
| final_pair_materialize_launch_ms | 0.003450 |
| final_pair_mark_sync_ms | 0.320651 |
| final_pair_prefix_host_ms | 0.016580 |
| final_pair_compact_launch_ms | 0.004040 |
| merge_launch_ms | 0.434324 |
| merge_sync_ms | 0.014311 |
| total_ms | 0.640851 |

The final-pair mark/sync stage dominates the final-pair breakdown. The earlier fused materialize+mark probes from Goal1632 and Goal1633 are therefore not the right production path to integrate.

## Next Work

The next optimization attempt should target final-pair mark/sync behavior directly. Candidate directions include reducing the synchronization boundary around final block counts, moving final count/prefix handling further onto device, or designing a final-pair-specific mark/count path that avoids the current expensive wait.

Any such change must remain opt-in until it has parity evidence, stage-profile evidence, a focused collect-k sweep, and external review.

## Claim Boundary

This is internal profiling and bottleneck-localization evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
