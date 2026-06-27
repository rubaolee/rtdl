# V4 Goal4702 Specialized Tier-3 Reliability Matrix Protocol

Status: frozen protocol, not run

- validation: `passed`
- total attempts: `20`
- attempts per variant: `5`
- success floor: `0.95`
- next goal: `Goal4703 specialized Tier-3 reliability matrix POD run`

## Callback Variants

- `custom_scalar_reduce_weighted_sum`
- `custom_score_affine`
- `custom_threshold_flag`
- `custom_minmax_score`

## Datasets

- `dense_hits`
- `sparse_hits`
- `no_hit_empty_reduction`

## Requirements

- correctness: 100% exact or tolerance-bounded parity for every variant x dataset row
- cache: same callback PTX/toolchain/symbol must reuse the same deterministic cache key; changed PTX or toolchain fingerprint must produce a different key
- failures: every failed attempt must carry a Goal4698 stage-specific error code before the result can be reviewed

## Boundary

This protocol authorizes only Goal4703 reliability execution. It does not authorize public Tier-3 support, arbitrary callback support, raw OptiX callbacks, release wording, or performance claims.
