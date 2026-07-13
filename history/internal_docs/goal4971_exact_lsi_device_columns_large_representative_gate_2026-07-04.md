# Goal4971 Exact LSI Device Columns Large Representative Gate

Date: 2026-07-04

## Purpose

Test whether the existing exact planar-map LSI device-column route becomes useful
on the large `top4_county_zipcode_arcgis_same_source` Section 5.7 representative
input from Goal4970.

This is intentionally **not** a new ABI design goal. Goal4964 already implemented:

```python
PreparedOptixPlanarMapLsi2DQuery.run_pair_id_device_columns()
```

and the app measurement flag:

```bash
--exact-lsi-device-columns
```

Goal4964 proved correctness but found a public-sample performance no-go:

```text
host exact pair-id rows:       0.893045s
exact pair-id device columns:  0.987424s
```

Goal4970 then created a much larger representative `County x Zipcode` top4
input and measured the normal fresh binary route:

```text
fresh binary/device-columnar hot: 7.757310s
LSI public rows:                  4.066679s
```

Goal4971 asks whether exact LSI device columns improve the large-input fresh
route, or whether the public-sample no-go holds at scale.

## Work

Run:

```bash
python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left .../top4_county.cdb \
  --right .../top4_zipcode.cdb \
  --summary .../rtdl_binary_exact_lsi_device_columns_section57_overlay.json \
  --pair-name top4_county_zipcode_arcgis_same_source \
  --cache-dir .../rtdl_packed_cache \
  --device-columnar \
  --validate-device-order \
  --compiled-group \
  --exact-lsi-device-columns
```

Compare against Goal4970:

| Route | Expected comparator |
|---|---:|
| host exact pair-id rows, binary fresh | `7.757310s` writer-free hot |
| exact LSI device columns, binary fresh | measured by Goal4971 |

## Correctness Gates

The exact-device-column route must match the Goal4970 normal binary route:

```text
lsi_row_count = 428322
xsect_sorted_counts = {side0: 428322, side1: 428322}
vertex positive counts = {side0_in_side1: 812721, side1_in_side0: 4527305}
device sort validation = true for both maps
```

No text byte-equality claim is required for this binary route. The text
correctness anchor remains Goal4970's byte-equal RTDL text and Numba/text routes.

## Genericity Gates

The route must remain generic:

- output columns are only generic `left_id/right_id` pair-id columns
- no RayJoin output-chain, face, text, AuthorOfficial, or polygon-format
  semantics in core
- `rtdsl.rayjoin_overlay` remains forbidden
- no public performance claim if the route is slower

## Exit Labels

Use one:

- `exact_lsi_device_columns_large_input_speedup_confirmed`
- `exact_lsi_device_columns_large_input_no_go_confirmed`
- `blocked_by_runtime_or_correctness_failure`

If no-go is confirmed, the next performance target is exact planar-map LSI
compute/predicate/traversal, not row-residency wrappers.
