# Goal4829: County x Zipcode Prefix Compare After Comparator Restore

Date: 2026-06-30

## Purpose

After Goal4828 found that the RTDL comparator had been over-corrected, this goal tested whether restoring the author-source internal comparator while preserving the author-reply `t_reported` perturbation restores agreement with the deterministic author baseline.

This is still correctness-only. It is not a performance result.

## Method

The full RTDL output path is too heavy for the current harness because it builds a full Python list of output chains before writing a 2.4GB output file. To avoid another blind full-output run, I wrote an internal diagnostic user app:

`history/internal_docs/goal4829_prefix_compare_user_app.py`

It does not edit RTDL source. It monkey-patches only the current Python process to stop output-chain assembly after `N` chains, writes the prefix, and compares that prefix against the deterministic author baseline.

Command run on the POD:

```bash
RTDL_OPTIX_LIB=/workspace/rtdl_goal4820_sos_fix/build/librtdl_optix.so \
PYTHONPATH=src \
python3 history/internal_docs/goal4829_prefix_compare_user_app.py \
  --left /workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb \
  --right /workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb \
  --author-output /workspace/rtdl_goal4820_sos_fix/artifacts/goal4828_county_zipcode_author_deterministic/author_deterministic_county_zipcode_overlay.txt \
  --output-dir /workspace/rtdl_goal4820_sos_fix/artifacts/goal4829_prefix_compare_after_comparator_restore \
  --max-chains 20
```

## Result

Artifact:

`/workspace/rtdl_goal4820_sos_fix/artifacts/goal4829_prefix_compare_after_comparator_restore/summary.json`

Key result:

- `prefix_match`: `true`
- `first_diff`: `null`
- `max_chains`: `20`
- RTDL prefix file: `/workspace/rtdl_goal4820_sos_fix/artifacts/goal4829_prefix_compare_after_comparator_restore/rtdl_prefix_20.txt`
- RTDL prefix bytes: `1112`

The corrected build now matches the deterministic author baseline for the first 20 output chains. This specifically confirms that the earlier line-25 mismatch:

- Author: `9 2 8 9 1 2`
- RTDL over-corrected build: `9 2 8 9 5 6`

was repaired by restoring the author-source internal comparator semantics.

## Core-Stage Evidence From The Same Run

The same prefix run reported:

- LSI intersections: `965844`
- Vertex PIP:
  - map0 points in map1: `17325792`
  - map0 positive faces: `14129276`
  - map1 points in map0: `47862092`
  - map1 positive faces: `41353115`
- Midpoint PIP:
  - map0 midpoints in map1: `123082`
  - map0 positive faces: `97957`
  - map1 midpoints in map0: `141510`
  - map1 positive faces: `109468`

Timing notes:

- Prefix diagnostic wall: `475.694s`
- RTDL internal `total_sec`: `139.089s`
- Output-chain prefix assembly: `0.460s`
- Prefix write: `0.030s`

The wall/internal timing discrepancy is expected for this diagnostic because the top-level script includes full CDB load and external setup not counted in the internal `total_sec`.

## Interpretation

Positive:

- The author deterministic baseline exists.
- The corrected RTDL build passes the official public County x Soil byte-equality sample.
- The corrected RTDL build matches the deterministic author baseline for the first 20 County x Zipcode output chains.
- The earlier first-diff regression caused by over-correcting the internal comparator is fixed.

Still not proven:

- Full County x Zipcode byte equality is not yet proven.
- Full Section 5.7 eight-pair reproduction is not proven.
- Performance remains unauthorized.

Current blocker:

- Need a scalable full-output comparison strategy. The current Python full-output path materializes a giant list before writing and is too fragile for repeated 2.4GB byte-level runs under the current harness.

## Recommended Next Step

Proceed to a stronger correctness comparison in this order:

1. Extend prefix comparison to larger bounded prefixes only if the runtime cost is acceptable.
2. Prefer a streaming/incremental output hash path that avoids storing all output chains in a Python list before writing.
3. Only after full byte equality is proven should performance runs be authorized.

Forbidden:

- No performance claims yet.
- No claim of full Section 5.7 reproduction yet.
- No comparison against the old nondeterministic Goal4806 author output as truth.
- No RayJoin-only hidden kernels.
