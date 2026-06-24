# Goal4223 RayJoin Public-CDB Contract Scale Map

Date: 2026-06-09

Status: internal evidence accepted with boundary

## Purpose

Goal4223 answers the remaining Goal4219 RayJoin question with broader
same-contract evidence, not app micro-tuning:

Do the RayJoin-style contracts keep the same route preference when the bounded
public-CDB slices vary in size?

The measurement compares explicit user-visible routes:

- Numba CUDA JIT scalar-count partner code.
- RTDL/OptiX prepared generic primitive routes.

It does not build an automatic dispatcher and it does not report a single
whole-RayJoin score.

## Hardware And Source

- Hardware: ephemeral RTX cloud validation pod; live SSH endpoint and local key
  names intentionally redacted from tracked evidence.
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.08`
- Source commit used by pod run: `63289bbc`
- Runner: `scripts/goal4223_rayjoin_public_cdb_contract_scale_map.py`
- Artifact root: `docs/reports/goal4223_rayjoin_public_cdb_contract_scale_map_rtx4000ada/`

The pod workspace was at the same runtime implementation baseline used by
Goals4215/4218, plus the copied Goal4223 wrapper. That keeps the comparison
aligned with the current route-policy evidence chain.

## Results

All seven contract/scale rows passed count parity.

| Contract | Case | Candidate Pairs | Numba sec | RTDL/OptiX sec | RTDL/OptiX vs Numba | Recommended Route |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| PIP one-shot count | `pip_county512` | 246,272 | `0.000527` | `0.001884` | `0.280x` | Numba |
| LSI scalar count | `lsi_county256_soil256_count128` | 12,334,176 | `0.002301` | `0.000090` | `25.468x` | RTDL/OptiX |
| LSI scalar count | `lsi_county256_soil256_count256` | 44,938,225 | `0.008147` | `0.000087` | `94.015x` | RTDL/OptiX |
| LSI scalar count | `lsi_county256_soil256_count512` | 136,411,275 | `0.023323` | `0.000089` | `262.052x` | RTDL/OptiX |
| Overlay active-count | `overlay_county128_soil128` | 14,036 | `0.006502` | `0.000097` | `66.754x` | RTDL/OptiX |
| Overlay active-count | `overlay_county256_soil256` | 56,876 | `0.029695` | `0.000094` | `314.373x` | RTDL/OptiX |
| Overlay active-count | `overlay_county512_soil512` | 233,766 | `0.052441` | `0.000552` | `95.042x` | RTDL/OptiX |

## Interpretation

The broader slice map reinforces the Goal4218 contract split:

- PIP one-shot count remains better as simple Numba partner code on these
  bounded public-CDB slices.
- LSI scalar count strongly favors the prepared RTDL/OptiX segment-pair count
  primitive as candidate-pair volume grows.
- Overlay active-count strongly favors the prepared RTDL/OptiX shape-pair
  active-count primitive across the tested slice sizes.

This is exactly the kind of evidence we want for the language/runtime: RTDL
should expose strong generic primitives and let users choose the partner route
when the primitive is not the right shape.

## Boundary

Goal4223 does not authorize release action, public speedup wording, whole-app
RayJoin wording, RayJoin paper-reproduction wording, broad RT-core wording,
true-zero-copy wording, automatic partner selection, AMD performance wording,
or app-specific native-engine logic.
