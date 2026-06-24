# Goal4222 RT-DBSCAN Blocked vs Unblocked Profile Map

Date: 2026-06-09

Status: internal evidence accepted with boundary

## Purpose

Goal4222 follows the Goal4219 target map and spends NVIDIA pod time only where
it can answer a generic route-policy question:

Should RT-DBSCAN's current grouped-stream profile prefer the unblocked canonical
single-pass shape, or the blocked grouped-stream variant?

This is not app micro-tuning. It compares two generic RTDL/OptiX grouped-stream
execution shapes across three fixture families and two scales, while preserving
the same app-level RT-DBSCAN component-signature contract.

## Hardware And Source

- Hardware: ephemeral RTX cloud validation pod; live SSH endpoint and local key
  names intentionally redacted from tracked evidence.
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.08`
- Source commit: `63289bbc`
- Runner: `scripts/goal4222_rtdbscan_blocked_vs_unblocked_profile_map.py`
- Artifact root: `docs/reports/goal4222_rtdbscan_blocked_vs_unblocked_profile_map_rtx4000ada/`

## Result

All six dataset/scale pairs passed. Every row reports the canonical
`single_pass_candidate_root_rebased` boundary policy. The unblocked shape wins
all tested profiles:

| Dataset | Points | Unblocked sec | Blocked sec | Blocked / Unblocked | Pass Counts |
| --- | ---: | ---: | ---: | ---: | --- |
| `clustered3d` | 65,536 | `0.098313` | `0.435857` | `4.433x` | 1 vs 16 |
| `clustered3d` | 262,144 | `1.277518` | `6.676138` | `5.226x` | 1 vs 64 |
| `road3d` | 65,536 | `0.041502` | `0.151374` | `3.647x` | 1 vs 16 |
| `road3d` | 262,144 | `0.475172` | `2.371092` | `4.990x` | 1 vs 64 |
| `ngsim_dense` | 65,536 | `0.015974` | `0.050199` | `3.143x` | 1 vs 16 |
| `ngsim_dense` | 262,144 | `0.158542` | `0.755904` | `4.768x` | 1 vs 64 |

## Interpretation

The blocked grouped-stream variant is not the right default for the current
tested profiles. It introduces repeated grouped-stream passes and is slower by
`3.1x` to `5.2x`.

The design consequence is simple:

- Keep `single_pass_candidate_root_rebased` unblocked grouped stream as the
  current default route shape.
- Keep blocked grouped stream explicit and profile-specific.
- Spend future runtime work on broader evidence or a visible advisor, not on
  hidden automatic dispatch.

## Boundary

This packet does not authorize release action, public speedup wording,
whole-app acceleration wording, broad RT-core wording, RT-DBSCAN
paper-reproduction wording, true-zero-copy wording, automatic partner selection,
AMD performance wording, or app-specific native-engine logic.
