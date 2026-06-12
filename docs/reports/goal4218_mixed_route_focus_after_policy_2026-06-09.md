# Goal4218 Mixed-Route Focus Packet After RT-DBSCAN Policy Cleanup

Date: 2026-06-09

Status: internal evidence accepted with boundary

## Purpose

Goal4218 runs the existing mixed-route focus queue on the RTX 4000 Ada pod after
the Goal4205-4212 RT-DBSCAN policy canonicalization and the Goal4215 all-app
health packet. The purpose is not broad tuning. It is a focused route-decision
check for the two benchmark apps that still most strongly exercise explicit
partner choice:

- Spatial RayJoin: Numba for bounded one-shot PIP, RTDL/OptiX for repeated PIP,
  LSI scalar count, and overlay active count.
- RT-DBSCAN: RTDL/OptiX grouped stream plus Numba component-signature
  continuation, comparing unblocked and blocked grouped-stream shapes.

This packet does not authorize release action, public speedup wording,
whole-app acceleration wording, broad RT-core wording, paper-reproduction
wording, true-zero-copy wording, automatic partner selection, AMD performance
wording, or app-specific native-engine logic.

## Hardware And Source

- Hardware: ephemeral RTX cloud validation pod; live SSH endpoint and local key
  names intentionally redacted from tracked evidence.
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.08`
- Source commit: `63289bbc`
- Runner: `scripts/goal3927_combined_pod_perf_queue.py`
- Artifact root: `docs/reports/goal4218_mixed_route_focus_after_policy_rtx4000ada/`
- Manifest: `docs/reports/goal4218_mixed_route_focus_after_policy_rtx4000ada/summary_manifest.json`

The run used the RayJoin public-CDB fixtures regenerated for Goal4215 under
`/root/rtdl/data/rayjoin_public_cdb`.

## Result Summary

The queue passed in `19.043s`, with source dirty list empty.

### Spatial RayJoin

The RayJoin row remains contract-split:

| Contract | Recommended Route | RTDL/OptiX vs Numba |
| --- | --- | ---: |
| PIP one-shot scalar count | Numba CUDA JIT scalar count | `0.253x` |
| PIP repeated requests | RTDL/OptiX prepared batch executor | `1.252x` per request |
| LSI scalar count | RTDL/OptiX prepared segment-pair count | `259.991x` |
| Overlay active count | RTDL/OptiX prepared shape-pair active count | `211.061x` |

All four contract counts matched. The result supports explicit user-visible
route choice, not automatic dispatch and not a whole-RayJoin speedup claim.

### RT-DBSCAN

Both RT-DBSCAN rows report the canonical policy
`single_pass_candidate_root_rebased`.

| Mode | Elapsed sec | Boundary pass count | Reading |
| --- | ---: | ---: | --- |
| `optix_rt_core_grouped_stream_numba_column_signature_3d` | `0.096189` | 1 | Current unblocked grouped stream remains the right default profile shape. |
| `optix_rt_core_grouped_stream_blocked_numba_column_signature_3d` | `0.436252` | 16 | Blocked stream is `4.535x` slower here; keep it explicit rather than default. |

The blocked shape can still matter for memory-bounded or profile-specific work,
but this packet says it should not be promoted as the default for the 65,536
clustered3d scale-profile row.

## Design Reading

This packet reinforces the current major engineering direction:

1. Do not hide partner selection. Users should see the contract split.
2. Prefer fused RTDL/OptiX primitives where they exist and win.
3. Use partners for unfused/custom continuation work, with Numba available as
   the no-raw-kernel reference path.
4. Keep blocked/partitioned variants explicit until a shape-specific advisor or
   larger evidence packet proves they are better for the user's profile.

The next large performance work should therefore be generic route-policy and
residency work, not app-only micro-tuning: larger same-contract route evidence,
profile-aware explicit advisors, and later AMD/HIPRT parity when hardware is
available.

## Boundary

All claim-boundary fields in the manifest remain false. Goal4218 is internal
engineering evidence only.
