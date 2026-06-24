# Goal1627 v1.6.x OptiX Collect-K Deferred Merge Sync Diagnostic

## Verdict

`defer_merge_sync_diagnostic_candidate_recorded`

An opt-in OptiX diagnostic gate was added for the experimental
`COLLECT_K_BOUNDED` device-pointer path:
`RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`.

The default path is unchanged. The diagnostic only skips the per-level host
`cuStreamSynchronize(nullptr)` for batched, non-final merge levels when device
prefix compact and device level counts are active. Kernel ordering remains on
the same stream; later dependent work or final synchronization still provides
completion ordering.

## Scope

- Repository base commit for pod measurement:
  `b4016c14` plus the local diagnostic patch.
- GPU: `NVIDIA RTX A4500`, driver `550.127.05`, `20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Runner: `scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py`.
- Counts: `65537 98305 131072`.
- Repeats: `5`.
- Mode comparison:
  - no-defer: `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`
  - defer: `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` plus
    `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`

## Results

| Count | No-defer total ms | Defer total ms | Delta ms | No-defer merge sync ms | Defer merge sync ms | No-defer merge launch ms | Defer merge launch ms | Payload copies no-defer/defer | Parity |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 65537 | 0.349581 | 0.292479 | -0.057102 | 0.090643 | 0.007640 | 0.112693 | 0.140925 | 0/0 | true |
| 98305 | 0.333231 | 0.296739 | -0.036492 | 0.125745 | 0.008060 | 0.091803 | 0.171646 | 1/1 | true |
| 131072 | 0.359061 | 0.332810 | -0.026251 | 0.144505 | 0.008760 | 0.096343 | 0.204776 | 0/0 | true |

## Interpretation

The diagnostic reduces measured per-level merge synchronization time
substantially. Some of that waiting moves into measured launch time, which is
expected because queued work still has real dependencies. Even after that
movement, the median native stage total improves for all three tested counts.
When the diagnostic is enabled, non-final merge-level `sync_ms` is intentionally
zero and should not be interpreted as per-level GPU latency; only the total
stage timing and final synchronization remain meaningful for A/B comparison.

This is a promising implementation direction for the merge/sync bottleneck
identified after Goal1625 and Goal1626. It is not yet a stable default because
the evidence is narrow: one GPU model, one candidate preset, three counts, and
the experimental collect-k path only.

## Next Work

1. Keep the diagnostic behind
   `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC`.
2. Run the focused collect-k tests and at least one RTX pod regression slice
   with the diagnostic enabled before considering it for a gated candidate
   bundle.
3. Ask Claude and Gemini to review the synchronization-safety argument and
   evidence before promoting the diagnostic beyond internal measurement.

## Claim Boundary

This report is internal v1.6.x performance diagnostic evidence only. It does
not authorize public speedup wording, true zero-copy wording, stable
`COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup
claims, release tags, or release action.
