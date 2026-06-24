# Goal1082 Facility Same-Scale Baseline Intake

Date: 2026-04-29

Verdict: **BLOCK**

Valid: `true`

## Result

| Check | Value |
| --- | --- |
| `same_scale` | `True` |
| `decision_matches` | `False` |
| `covered_count_matches` | `False` |
| `public_claim_authorized` | `False` |

## Evidence

- RTX threshold-reaching count: `8898102` / `10000000`.
- CPU oracle covered count: `10000000` / `10000000`.
- RTX timing row skipped validation: `True`.
- RTX query median: `0.11103759799152613` seconds.
- CPU reference total: `156.35385558300186` seconds.

## Reason

The same-scale CPU oracle says all 10,000,000 customers are covered, but the RTX timing row with validation skipped reports only 8,898,102 threshold-reaching queries. The facility RTX public wording remains blocked until a corrected same-scale RTX validation run passes. The likely engineering cause is coordinate precision at 2.5M copies: x coordinates reach about 15 million while the radius is 1.0, which is unsafe for float-oriented RT traversal without tiling, recentering, or another precision-aware mapping.

## Next Actions

- Do not publish a facility RTX speedup ratio from the current 2.5M timing row.
- Add or use a precision-aware tiled/recentered facility benchmark mapping before the next cloud run.
- Rerun same-scale OptiX with validation enabled or with a reviewed validation-equivalent artifact.

## Boundary

Goal1082 is an intake/audit of one same-scale facility baseline. It does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

