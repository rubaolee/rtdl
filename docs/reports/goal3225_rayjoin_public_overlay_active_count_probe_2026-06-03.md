# Goal3225: RayJoin Public Overlay Active-Count Probe

Date: 2026-06-03

## Purpose

Goal3225 extends the current-best Spatial RayJoin count/parity evidence from
fixture-level overlay coverage to bounded public RayJoin-style Brazil
county/soil CDB slices.

This is deliberately a narrow active-count probe. It checks that the prepared
OptiX shape-pair relation count route matches the CPU reference
`active_seed_count` contract on public overlay inputs. It does not claim full
row overlay continuation, paper-scale reproduction, or external RayJoin
performance parity.

## Artifact

- `docs/reports/goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.json`
- `docs/reports/goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.stdout`

Pod metadata:

- Commit: `92e16b8649f99aa62fbca0d0c97466a7a2f8eaa3`
- GPU: `NVIDIA A40, 570.211.01`
- CUDA driver query: present
- nvcc version: present
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Warmups: `1`
- Repeats: `5`
- Status: `pass`

| Case | Public Slice | Expected Active Seeds | Observed Counts | Median Prepared Count (s) |
| --- | --- | ---: | --- | ---: |
| `overlay_county128_soil128` | county 0:128 + soil 0:128 | 1 | `[1, 1, 1, 1, 1]` | 0.022716183215379715 |
| `overlay_county256_soil256` | county 0:256 + soil 0:256 | 9 | `[9, 9, 9, 9, 9]` | 0.05908652022480965 |

## Interpretation

Goal3225 is useful because it closes the immediate public-data gap for the
overlay count route after Goal3223 moved the fixture-level overlay row from a
zero-count case to a nonzero authored fixture.

The active-count contract is intentionally different from full row overlay
continuation:

- CPU reference computes the full overlay dependency summary and exposes
  `active_seed_count`.
- Prepared OptiX count route returns `overlay_active_pair_dependency_count`.
- The probe compares those two matching count contracts.

The native engine remains app-agnostic. It sees the generic
`SHAPE_PAIR_RELATION_FLAGS_2D`/prepared shape-pair relation count contract;
RayJoin interpretation remains in Python.

The refreshed `92e16b86` pod artifact also normalizes the claim-boundary
schema at every artifact level: top-level, per-row, and per-measurement blocks
all use the same six canonical false claim flags.

## Boundary

This report does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The row overlay continuation path remains deferred Tier B work. The full
RayJoin paper-scale comparison remains open.
