# Goal3321 - RayJoin PIP Validated-Domain Preflight

Date: 2026-06-04

## Purpose

Goal3320 showed that the fast prepared point / closed-shape scalar-count route is not universally valid across CDB topology. It is exact on validated simple-chain slices, but full county-style inputs can mismatch the exact oracle.

Goal3321 adds an app-level preflight API:

```python
preflight_rayjoin_pip_fast_count_domain(...)
```

The preflight checks a selected generic fast PIP count route against the exact prepared count before the route is treated as safe for a dataset domain.

## Contract

The preflight returns a structured dictionary with:

- selected `count_mode`;
- `device_filtered_boundary_mode`;
- `query_axis`;
- `scalar_count_pipeline`;
- `point_order_mode`;
- input sizes;
- `exact_count`;
- `fast_count`;
- `matches_exact`;
- `status`;
- `fallback_required`;
- `fallback_reason`;
- metadata for prepared point columns or point-id count columns when applicable;
- claim-boundary flags, all false.

When `require_match=True`, a mismatch raises:

```text
validated-domain preflight rejected fast PIP count route
```

## Pod Smoke

A clean-from-Git A5000 pod smoke validated the preflight at commit
`4b72d290b2c3f7fea309e79ad13ce9bbfc5459f1`.

Artifact:

- `docs/reports/goal3321_rayjoin_pip_preflight_pod_smoke_2026-06-04.json`

Rows:

| Label | Dataset | Exact count | Fast count | Status |
| --- | --- | ---: | ---: | --- |
| `soil_pass` | `br_soil_start256_count512.cdb` | 1471 | 1471 | `validated_fast_route_allowed` |
| `county_fail` | `br_county_start256_count512.cdb` | 1417 | 1429 | `fast_route_rejected` |

This confirms the intended behavior: the helper makes the known safe route
usable and the known unsafe county slice fail closed with structured fallback
metadata.

## Boundary

This is Python benchmark-app policy over generic RTDL primitives. It does not add RayJoin-specific native logic and does not expand the engine ABI. The native engine still sees only prepared point / closed-shape count primitives.

The purpose is to make the Goal3320 boundary operational:

- validated domain: fast route may be used as a checked route;
- mismatched domain: fallback is required;
- future broad CDB support requires a richer generic face/topology-aware closed-shape membership primitive.

## Claim Boundary

- `release_authorized`: false
- `public_speedup_claim_authorized`: false
- `rt_core_speedup_claim_authorized`: false
- `true_zero_copy_claim_authorized`: false
- `rtdl_beats_rayjoin_claim_authorized`: false
- `rayjoin_paper_reproduction_claim_authorized`: false
