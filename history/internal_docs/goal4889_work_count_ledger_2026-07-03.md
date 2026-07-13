# Goal4889 Work-Count Ledger

Date: 2026-07-03

Machine-readable ledger:

```text
history/internal_docs/goal4889_work_count_ledger_2026-07-03.json
```

## Result

Existing evidence is enough to prove comparable **query/launch counts**, but not
enough to prove comparable **candidate/test counts**.

Decision label:

```text
work_count_unavailable__instrumentation_required
```

## Comparable Query Counts

| Stage | RTDL | AuthorPatch | Match? |
| --- | ---: | ---: | --- |
| LSI query segments | 14,430,155 | 14,430,155 | yes |
| Vertex PIP map0 query points | 14,788,065 | 14,788,065 | yes |
| Vertex PIP map1 query points | 992,505 | 992,505 | yes |
| Midpoint PIP map0 query points | 1,707 | 1,707 | yes |
| Midpoint PIP map1 query points | 2,752 | 2,752 | yes |

This rules out the shallow explanation that RTDL is simply launching orders of
magnitude more rays.

## Hot-Path Time Gap At Same Query Counts

| Stage | RTDL | AuthorPatch | Gap |
| --- | ---: | ---: | ---: |
| LSI | about 5.7-6.3 s | about 4.8 ms | about 1,180x-1,310x |
| Vertex PIP map0 | 9.784 s native traversal | about 20.9 ms | about 468x |
| Vertex PIP map1 | 1.530 s native traversal | about 7.3 ms | about 210x |

These ratios are not public performance claims. They are internal diagnostic
evidence for where the next engineering work must look.

## Missing Candidate/Test Denominators

| Stage | RTDL candidate/test count | AuthorPatch candidate/test count |
| --- | --- | --- |
| LSI | missing for public grouped-range row route | missing from existing logs |
| Vertex PIP | missing from timing ABI | missing from existing logs |
| Midpoint PIP | missing from timing ABI | missing from existing logs |

## What The Ledger Supports

Supported:

- The hot-path gap is not caused by extra RTDL ray/query launch count.
- The decisive missing denominator is candidate/test work per launched query.
- Existing artifacts cannot choose between:
  - more candidate tests in RTDL; or
  - similar candidate tests but a much slower native path per test.

Not supported:

- claiming the next work must definitely be data-flow fusion/compiler;
- claiming the next work must definitely be native kernel tuning;
- claiming prepared/session/row-buffer work can reach the author hot path.

## Current Best Inference

The most likely source is still inside the native traversal layer, not Python
or host materialization:

```text
RTDL vertex PIP traversal total ~= 11.31 s
RTDL LSI row route             ~=  5.7-6.3 s
host/device point upload/download is near-zero
```

But "native traversal layer" is not specific enough. The next probe must say
whether that native traversal time is:

1. candidate explosion; or
2. per-candidate kernel/path inefficiency.
