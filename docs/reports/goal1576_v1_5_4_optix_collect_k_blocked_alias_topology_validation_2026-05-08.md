# Goal 1576: OptiX COLLECT_K_BOUNDED Blocked Alias Topology Validation

## Verdict

`RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1` passes blocked-alias topology validation on the RTX 4000 Ada pod.

The validation specifically exercises tile counts where an odd carry would be unsafe to alias at some levels. In those levels, the guard preserves the normal payload copy. In safe carry levels, it aliases the payload and reduces `carry_payload_copies`.

This strengthens the diagnostic but still does not promote it to production default or authorize public speedup wording.

## Scope

- Repository commit measured on pod: `76fe82b35e32b9162d360c880db92b3e2ed7a4e3`.
- Pod: `root@157.157.221.29 -p 22942`, NVIDIA RTX 4000 Ada Generation, driver `550.127.05`.
- CUDA/OptiX: CUDA `12.8`, OptiX SDK at `/root/vendor/optix-sdk`.
- Counts: `12289`, `20481`, `28673`, `45057`.
- Tile size: `2048` via `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1`.

## Results

| Case | Tile Count | Path | Accepted | Parity | Stage total ms | carry_copies | carry_payload_copies |
|---:|---:|---|---|---|---:|---:|---:|
| 12289 | 7 | Baseline | Yes | Yes | 0.137962 | 1 | 1 |
| 12289 | 7 | Alias diagnostic | Yes | Yes | 0.138042 | 1 | 1 |
| 20481 | 11 | Baseline | Yes | Yes | 0.229374 | 2 | 2 |
| 20481 | 11 | Alias diagnostic | Yes | Yes | 0.164161 | 2 | 1 |
| 28673 | 15 | Baseline | Yes | Yes | 0.164231 | 1 | 1 |
| 28673 | 15 | Alias diagnostic | Yes | Yes | 0.162077 | 1 | 1 |
| 45057 | 23 | Baseline | Yes | Yes | 0.209907 | 2 | 2 |
| 45057 | 23 | Alias diagnostic | Yes | Yes | 0.204257 | 2 | 1 |

All runs produced accepted Goal1506-style evidence with profile topology matching expected.

## Interpretation

Tile counts `7` and `15` exercise blocked-only carry behavior in this merge tree. The alias diagnostic correctly leaves `carry_payload_copies` unchanged at `1`, proving it did not alias an unsafe carry.

Tile counts `11` and `23` exercise mixed behavior: one unsafe carry remains a payload copy, while one safe carry is aliased. The diagnostic correctly reduces `carry_payload_copies` from `2` to `1`.

This validates the core safety rule from Goal1573:

- alias only when the next segment count is odd, so the carry remains unpaired, or
- alias when the next segment count is `2`, because final merge uses explicit row pointers,
- otherwise copy the payload to restore derived-layout contiguity.

## Next Gate

Before production promotion, the remaining gaps are:

- additional GPU architecture validation,
- a bounded wider even/odd sweep that avoids oversized timeout cases,
- a final decision on whether diagnostic flags should be collapsed into a default fastest-path preset.

No public speedup claim, stable primitive promotion, or release action is authorized by this report.

## Artifacts

- `docs/reports/goal1576_v1_5_4_optix_collect_k_blocked_alias_baseline_profile_2026-05-08.json`
- `docs/reports/goal1576_v1_5_4_optix_collect_k_blocked_alias_baseline_profile_2026-05-08.md`
- `docs/reports/goal1576_v1_5_4_optix_collect_k_blocked_alias_diagnostic_profile_2026-05-08.json`
- `docs/reports/goal1576_v1_5_4_optix_collect_k_blocked_alias_diagnostic_profile_2026-05-08.md`
