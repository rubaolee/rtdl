# Goal5489 LibRTS Same-Process Prepared Point-Contains Repeat

## Status

```text
implemented__POD_exact_input_matched__same_process_reuse_diagnostic__review_pending
```

## Objective

Measure first-use versus same-process reuse on the new generic columnar front
door without changing RTDL core or silently turning a warm diagnostic into a
performance headline. The app prepares one `Aabb2DColumns` index, executes the
same exact point-query file three times, and checks every result count against
the patched-author point-contains count.

## Exact input and execution

- archive: official `PPoPPAE-v2.tar.gz`, verified size and MD5;
- geometry: `dtl_cnty.wkt`, SHA-256
  `9177fdff45f24488f22157a2a1428a7cdb9d5a66a7287d4013ead52de1c7973f`;
- queries: `point-contains_queries_100000/dtl_cnty.wkt`, SHA-256
  `95241f4e3f03c6dcea31b80e785a9729d4a4aaefeb82302e761b59d9c4fe39d3`;
- author and RTDL received the same two files;
- POD: NVIDIA RTX 4000 Ada, driver `570.133.07`;
- public RTDL path: `Aabb2DColumns -> prepare_aabb_index_2d_columns ->
  prepared.count`.
- the same protocol also ran on the larger `lakes.bz2` exact input.

## Result

Author count: `136475`. All three RTDL counts matched.

| iteration | RTDL prepared-query wall | RTDL primitive query phase | count |
|---:|---:|---:|---:|
| 1 | 0.369203 s | 0.201878 s | 136475 |
| 2 | 0.219729 s | 0.070464 s | 136475 |
| 3 | 0.217744 s | 0.069054 s | 136475 |

For `lakes.bz2` (8,327,448 geometries and 100,000 queries), all three counts
matched `103189`:

| iteration | RTDL prepared-query wall | RTDL primitive query phase | count |
|---:|---:|---:|---:|
| 1 | 0.598434 s | 0.446864 s | 103189 |
| 2 | 0.221605 s | 0.072082 s | 103189 |
| 3 | 0.219831 s | 0.072148 s | 103189 |

Other app-side phases were WKT/column loading `27.994313 s` and index
preparation `0.443229 s` for `dtl_cnty`, and `406.569663 s` plus `1.274903 s`
for `lakes.bz2`. The author reruns reported internal query times `0.0852 ms`
and `0.0816 ms`; these are different denominators and are not divided into
the RTDL numbers.

## Interpretation

The same-process repeat shows a clear first-use effect in the RTDL primitive
phase on both input sizes, with subsequent calls lower in these runs. It does
**not** establish a paper performance result, author parity, or a speedup ratio.
It also does not measure a distinct query batch or a fresh-process distribution.
The WKT parser remains a large app-owned host phase (`27.994 s` for
`dtl_cnty`, `406.570 s` for `lakes.bz2`), so the result must not be summarized
as an end-to-end columnar speedup.

## Claim boundary

Authorized:

- exact-input count agreement for this case;
- generic columnar front-door execution;
- same-process prepared-query first-use/reuse diagnostic.

Not authorized:

- pointwise containment equivalence;
- Figure 6 reproduction;
- author-vs-RTDL performance ratio or parity;
- device zero-copy;
- full paper reproduction;
- Embree evidence.

## Evidence

Machine-readable result:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5489_dtl_cnty_repeat.json
Paper-reproduction-apps/librts-paper/results/librts_goal5489_lakes_bz2_repeat.json
```

Local focused tests and manifest validation passed after implementation.
