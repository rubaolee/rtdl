# Goal4972 — Bounded Single-Pass Exact LSI Producer

Date: 2026-07-04

## Purpose

Goal4971 showed that exact LSI device-column output is real and useful on a larger representative
RayJoin Section 5.7 slice, but it did not close the remaining cost:

- normal public LSI rows: `lsi_public_rows_sec ~= 4.31s`
- exact pair-id device columns: `lsi_exact_pair_id_device_columns_sec ~= 2.75s`
- downstream device copy: `~= 0.0035s`

That result means row-residency/copy is not the root problem. The remaining cost is inside exact
LSI production. One suspected cost is that the current exact-device route still performs an exact
count pass before exact emission.

Goal4972 tests a narrow generic optimization:

> Let the caller provide an output capacity and emit exact accepted `{left_id, right_id}` device
> columns in one bounded pass. If capacity is insufficient, fail closed with overflow.

## Work

1. Add a native bounded exact planar-map LSI pair-id device-column entrypoint.
2. Add a Python public/internal wrapper for `PreparedOptixPlanarMapLsi2D`.
3. Add a RayJoin paper-reproduction route that uses the bounded exact LSI producer while preserving
   all downstream correctness gates.
4. Run the top4 County x Zipcode same-source representative matrix on the POD.
5. Compare against Goal4971 exact-device route.

## Genericity Rules

- The native output is only `{left_id, right_id}` plus row count/capacity metadata.
- The core must not know RayJoin output chains, faces, map0/map1 overlay semantics, or author text
  format.
- The bounded API is a generic planar-map LSI pair stream. RayJoin is only one consumer.
- Overflow must fail closed; no truncation is allowed.

## Verification Gates

- Small OptiX smoke: one crossing segment pair emits one row with the expected ids.
- Top4 representative correctness:
  - exact LSI row count must remain `428322`
  - side0/side1 xsect row counts must remain `428322`
  - vertex PIP positives must remain `812721 / 4527305`
  - device sort/order validation must pass
- Performance comparison:
  - compare bounded exact LSI time against Goal4971 `2.7495402842760086s`
  - compare full fresh writer-free hot time against Goal4971 `5.903873108327389s`

## Exit Labels

- `bounded_single_pass_exact_lsi_speedup_confirmed`
- `bounded_single_pass_exact_lsi_no_go`
- `blocked_by_correctness_or_overflow`
- `blocked_by_runtime_build_failure`

## Not Authorized

- No broad RayJoin performance claim.
- No comparison against author as a final headline.
- No app-specific native RayJoin kernel.
- No Layer 4 traversal fusion claim.
- No public release wording change from this goal alone.
