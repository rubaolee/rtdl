# Goal5040 - Fair AuthorOfficial vs RTDL Top4 Performance Comparison

Date: 2026-07-05

Exit label: `completed_fair_top4_author_rtdl_comparison__binary_route_1_76x_author_core__text_route_5_29x_post_read`

## Purpose

Run a fair comparison against `AuthorOfficial` after the v2.14.3 prepared query-batch work.

The owner request was explicit: do not keep optimizing; compare using the same data, the same patched author version, and clearly matched performance boundaries.

This goal therefore compares three separate regimes instead of reporting one blended number:

1. full paper text-output wall time;
2. post-read paper text-output time;
3. writer-free / binary operator-style core time.

## Input And Comparator

Input:

```text
Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb
Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb
```

Author comparator:

```text
AuthorOfficial = pinned RayJoin source 02bf622 + project patches
```

Author binary:

```text
Paper-reproduction-apps/rayjoin-paper/_work/author_official/release/bin/polyover_exec
```

The author build required one additional CMake compatibility flag on the POD:

```text
-DCMAKE_CUDA_ARCHITECTURES=89
```

This is build configuration for CUDA 12.8 / CMake 3.28 and does not change RayJoin algorithm logic.

## Commands

Author command shape:

```text
polyover_exec
  -poly1 top4_county.cdb
  -poly2 top4_zipcode.cdb
  -serialize=<run>/serialize
  -grid_size=15000
  -mode=rt
  -v=1
  -fau
  -xsect_factor=0.1
  -enlarge=3.5
  -check=false
  -output=<run>/overlay.txt
```

RTDL paper text command shape:

```text
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section57_overlay.py
  --left top4_county.cdb
  --right top4_zipcode.cdb
  --pair-name top4_county_zipcode
  --dataset-label representative_current_source
  --output <run>/overlay.txt
  --author-output <author-run>/overlay.txt
  --summary <run>/summary.json
```

RTDL prepared binary route evidence comes from Goal5039 artifacts:

```text
history/internal_docs/rtdl_goal5039_vertex_nohost_1_top4.json
...
history/internal_docs/rtdl_goal5039_vertex_nohost_5_top4.json
```

## Artifacts

Pulled local artifacts:

- `history/internal_docs/author_top4_fair_1_summary.json`
- `history/internal_docs/author_top4_fair_1_stdout.txt`
- `history/internal_docs/author_top4_fair_1_stderr.txt`
- `history/internal_docs/rtdl_top4_text_fair_1_run_summary.json`
- `history/internal_docs/rtdl_top4_text_fair_1_summary.json`
- `history/internal_docs/fair_top4_phase_calculation_2026-07-05.json`

Remote large outputs were not copied into git:

- author output: `139,098,488` bytes
- RTDL text output: `139,098,488` bytes

Both outputs had the same SHA-256:

```text
076227b072340e754b7f2cb54de3c37d8054e2a393e87fdb8a4f7368a297b690
```

So the RTDL paper text route is byte-equal to AuthorOfficial on this top4 input.

## Result 1 - Full Paper Text-Output Wall Time

Single-run wall time on the same POD:

| Route | Wall time | Output bytes | Byte-equal |
|---|---:|---:|---:|
| AuthorOfficial paper text route | 113.011s | 139,098,488 | baseline |
| RTDL paper text route | 79.931s | 139,098,488 | yes |

Ratio:

```text
RTDL wall / Author wall = 79.931 / 113.011 = 0.707x
```

In this full wall-time regime, RTDL is faster. This is not a clean core-compute result because the author run spends about `100.555s` reading/parsing the two CDB maps.

## Result 2 - Post-Read Paper Text-Output Time

To avoid letting map-read cost dominate the conclusion, compare the post-read paper text route:

Author phases from `polyover_exec`:

```text
Load Data:                    2.823s
Init:                         0.376s
Build Index:                  0.136s
Intersection edges:           0.00697s
Map 0 PIP:                    0.01557s
Map 1 PIP:                    0.06018s
Compute output polygons:      0.10431s
Write to file:                8.660s
```

Author post-read total:

```text
12.182s
```

RTDL post-read text route:

```text
RTDL non-load compute, excluding writer: 38.879s
RTDL output-chain writer:               25.504s
RTDL post-read text total:              64.383s
```

Ratio:

```text
RTDL post-read text / Author post-read text = 64.383 / 12.182 = 5.29x slower
```

This is the fairest paper-text-output performance comparison. RTDL is byte-equal, but the app-layer Python text route is still much slower after input read is removed.

## Result 3 - Writer-Free / Binary Operator-Style Core

The optimized v2.14.3 route is not the paper text writer. It is the prepared query-batch, writer-free binary route.

Important correction:

```text
0.046956s is the median per query batch.
It is not the whole top4 six-batch total.
```

The whole top4 prepared binary route must use the sum across six distinct query batches. Goal5039 artifacts give:

```text
median full six-batch sum = 0.328842s
```

Author core-compute phases, excluding map read, load/init/build, and file write:

```text
Intersection edges:           0.00697s
Map 0 PIP:                    0.01557s
Map 1 PIP:                    0.06018s
Compute output polygons:      0.10431s
Author core total:            0.18704s
```

Closest writer-free comparison:

```text
RTDL prepared binary six-batch total / Author core total
= 0.328842 / 0.187042
= 1.76x slower
```

This is the best current apples-near-apples core-style comparison, but it is not perfect parity of semantics: the author core still computes output polygons for the text route, while RTDL computes binary descriptor summaries for downstream pipeline use.

## Corrected Performance Statement

The previous shorthand:

```text
47ms
```

must be read as:

```text
47ms = median single query-batch hot body
329ms = median sum for the six-batch top4 prepared binary route
```

Do not use `47ms` as the full top4 runtime.

## Summary Matrix

| Regime | AuthorOfficial | RTDL | Fair interpretation |
|---|---:|---:|---|
| Full paper text wall, same output | 113.011s | 79.931s | RTDL faster, but dominated by author CDB read |
| Post-read paper text, same output | 12.182s | 64.383s | RTDL `5.29x` slower |
| Core-style writer-free / binary | 0.187s | 0.329s | RTDL `1.76x` slower; closest current binary operator comparison |

## Claim Boundary

Authorized:

- RTDL paper text output is byte-equal to AuthorOfficial on top4.
- Full wall-time text route on this run is `79.931s` RTDL vs `113.011s` AuthorOfficial.
- Post-read paper text route is `5.29x` slower for RTDL.
- Prepared binary route full top4 six-batch sum is about `0.329s`, not `47ms`.
- Closest current writer-free/core-style comparison is RTDL `1.76x` slower than AuthorOfficial core phases.

Not authorized:

- no claim that RTDL full top4 runtime is `47ms`;
- no claim that the binary descriptor route is byte-equivalent to the paper text output;
- no claim that RTDL beats AuthorOfficial core compute;
- no claim that the full-wall RTDL win proves RTDL core is faster, because author CDB read dominates that wall time;
- no claim that this is a multi-run median for AuthorOfficial. The top4 author text run was a single successful run because each full text-output run takes about two minutes.

## Conclusion

The fair answer is:

```text
RTDL is byte-correct.
For full text-output wall time on this single top4 run, RTDL is faster because author CDB read dominates.
For paper-text work after input read, RTDL is still 5.29x slower.
For the optimized writer-free binary route, the correct full-top4 number is 0.329s, which is 1.76x slower than the author core phases.
```

The engineering result is good, but the headline must be corrected: `47ms` is a per-batch median, not the whole top4 operator runtime.
