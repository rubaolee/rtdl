# Goal5490 LibRTS Numeric WKT Loader Probe

## Status

```text
no_go__numeric_numpy_wkt_loader_not_demonstrated_faster__keep_app_owned_experimental
```

## Objective

Test whether the remaining LibRTS WKT load phase can be reduced by replacing
the app-owned per-coordinate Python numeric conversion with a NumPy
`fromstring`-based parser. This probe deliberately stays in the paper app;
RTDL core receives only `Aabb2DColumns` and does not learn WKT syntax.

## Implementation

`run_exact_point_contains_prepared_phase_columns_repeat.py` now accepts
`--loader regex|numpy`. The default remains the existing regex loader. The
experimental numeric loader uses NumPy to parse coordinate bodies and emits
the same validated `Aabb2DColumns` contract. A local test compares all five
columns on polygon and multipolygon fixtures.

## POD evidence

Same exact `dtl_cnty` geometry/query files and the same author count were used.
Both loaders produced `136475`, and all three numeric-loader query repeats
matched that count.

| route | WKT/column load | index prepare | query-1 wall | query-2 wall | query-3 wall |
|---|---:|---:|---:|---:|---:|
| Goal5489 regex | 27.994 s | 0.443 s | 0.369 s | 0.220 s | 0.218 s |
| Goal5490 NumPy | 28.069 s | 0.391 s | 0.810 s | 0.218 s | 0.220 s |

These are separate POD runs, so the small load difference is not a controlled
regression claim. It is enough to reject a positive speedup claim: the numeric
replacement did not demonstrate a material improvement on this case. The
first query also varied with runtime state and is not used for a performance
claim.

## Decision

Do not run the expensive 6.7GB `lakes.bz2` file through this numeric variant
solely to search for a favorable result. Keep the variant available as an
app-owned diagnostic, with the regex loader as the default. The dominant
`406.570s` lakes WKT phase remains an app ingestion problem; it is not evidence
that a WKT parser belongs in RTDL core.

## Claim boundary

Authorized:

- numeric-loader schema parity on the local fixture;
- same-input count agreement on `dtl_cnty`;
- a no-go for this parser replacement as a demonstrated speedup.

Not authorized:

- an end-to-end speedup;
- author-vs-RTDL ratio or parity;
- a claim that NumPy WKT parsing is generally faster;
- full paper/Figure 6 reproduction;
- device zero-copy or Embree evidence.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5490_dtl_cnty_numeric_loader.json
```
