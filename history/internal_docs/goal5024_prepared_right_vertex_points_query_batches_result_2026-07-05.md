# Goal5024 - Prepared Right-Vertex Query Points for RayJoin Query Batches

## Purpose

Attack the remaining query-batch writer-free binary route floor without changing RTDL core or turning RayJoin into a hidden core primitive.

The target was the repeated `vertex_pip_map1_in_map0` cost in full overlay distinct chain batches. Goal5023 showed later batches around `0.77-0.78s`, with `vertex_pip_map1_in_map0` alone around `0.316-0.338s`.

## Boundary

- App route only: `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`.
- No `src/rtdsl/**` or `src/native/**` changes.
- No paper-text writer route claim.
- No cold CLI one-shot claim.
- No author-performance or 10x headline.
- Regime: same-process prepared LSI base session, distinct chain-contiguous full overlay query batches.

## Failed Candidate: BBox Filtering

I first tested a simple app-layer bbox filter for `vertex_pip_map1_in_map0`: only query right vertices inside the current left batch bbox, then scatter excluded points to face id `0`.

Candidate reduction looked tempting:

| Batch | Right Points In Left-Batch BBox | Fraction |
|---:|---:|---:|
| 0 | 7,673,981 / 9,993,104 | 0.768 |
| 1 | 6,822,058 / 9,993,104 | 0.683 |
| 2 | 2,971,749 / 9,993,104 | 0.297 |

But it is not semantically safe. A direct diagnostic on batch 2 found:

```text
inside_count   = 2,971,749
outside_count  = 7,021,355
outside_nonzero_face_ids = 11,128
top outside nonzero face ids = 2770:9030, 2656:1201, 2703:874, 2662:20, 2633:3
```

The full overlay result also changed descriptor pairs on batch 2:

```text
baseline descriptor_pair_count = 4438
bbox-filter descriptor_pair_count = 4434
```

Conclusion: global bbox filtering is a correctness no-go for this face-id contract. It was not kept in the code.

Artifact: `history/internal_docs/rtdl_goal5024_bbox_filter_vertex_pip_top4.json`

## Implemented Route

The right dataset vertices are identical across chain-contiguous left query batches. The app now has an opt-in:

```text
--prepared-query-batch-right-vertex-points
```

With `--prepared-lsi-base-session --query-chain-batches N`, it prepares the unchanged right-side vertex query-point buffer once using the same global scale bounds, then reuses that prepared buffer for `map1_in_map0` PIP across distinct left chain batches.

Compatibility was verified before implementation:

```text
Prepared right points from batch0 locator reused with batch2 locator:
face-id arrays equal = True
diff count = 0
nonzero_reuse = 1,475,002
nonzero_normal = 1,475,002
```

## Code and Test Changes

- Added CLI flag `--prepared-query-batch-right-vertex-points`.
- Added session preparation timings:
  - `session_prepare_query_batch_right_vertex_point_locator_sec`
  - `session_prepare_query_batch_right_vertex_points_sec`
- Reused `_prepared_vertex_points_map1_in_map0` inside each batch route.
- Added source-structure regression coverage in `tests/goal5021_prepared_lsi_base_session_test.py`.

Local validation:

```text
py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
py -3 -m unittest tests.goal5021_prepared_lsi_base_session_test
Ran 7 tests - OK
```

## Main 3-Batch Result

Command regime: top4 County x Zipcode, `--prepared-lsi-base-session --query-chain-batches 3`, writer-free binary route.

Baseline artifact: `history/internal_docs/rtdl_goal5023_full_overlay_distinct_chain_batches_top4.json`

Prepared-right-vertex artifact: `history/internal_docs/rtdl_goal5024_prepared_right_vertex_points_top4.json`

| Batch | Baseline `writer_free_hot_sec` | Prepared Right Vertices | Delta | Descriptor Pairs |
|---:|---:|---:|---:|---:|
| 0 | 3.8347s | 3.5308s | -0.3039s | 7190 |
| 1 | 0.7666s | 0.4594s | -0.3071s | 7592 |
| 2 | 0.7832s | 0.4480s | -0.3352s | 4438 |

`vertex_pip_map1_in_map0` dropped from:

```text
0.3668 / 0.3166 / 0.3382s
to
0.0171 / 0.0172 / 0.0134s
```

The measured body sum improved:

```text
3-batch body sum: 5.3844s -> 4.4382s
saved:            ~0.946s
```

The route adds one-time session preparation:

```text
right vertex point locator: 0.745s
right vertex points:        0.320s
extra session prep:         ~1.065s
```

So for only 3 batches, the optimization is near break-even if the new session prep is charged to this short run. It is not a 3-query headline win.

## 6-Batch Amortization Result

To test whether this is a real query-many win, I ran the same top4 input split into six distinct chain-contiguous full overlay batches.

Artifacts:

- `history/internal_docs/rtdl_goal5024_query6_baseline_top4.json`
- `history/internal_docs/rtdl_goal5024_query6_prepared_right_points_top4.json`

Summary:

| Metric | Baseline | Prepared Right Vertices |
|---|---:|---:|
| Median batch body | 0.7576s | 0.4393s |
| Best batch body | 0.7054s | 0.4323s |
| Sum of 6 batch bodies | 6.1415s | 4.1964s |
| Saved body time | - | 1.9451s |
| Extra right-vertex session prep | - | 1.0448s |
| Net after charging extra prep | - | ~0.9003s win |

Per-batch details:

| Batch | Baseline Body | Prepared Body | Baseline `map1_in_map0` PIP | Prepared `map1_in_map0` PIP | Descriptor Pairs |
|---:|---:|---:|---:|---:|---:|
| 0 | 2.378s | 2.007s | 0.316s | 0.017s | 6316 |
| 1 | 0.705s | 0.437s | 0.307s | 0.012s | 2756 |
| 2 | 0.754s | 0.441s | 0.320s | 0.015s | 4723 |
| 3 | 0.796s | 0.432s | 0.336s | 0.013s | 3058 |
| 4 | 0.761s | 0.445s | 0.339s | 0.013s | 2873 |
| 5 | 0.746s | 0.433s | 0.311s | 0.013s | 2987 |

This is a real query-many win for this regime: distinct full overlay batches, not same-query replay.

## Interpretation

What this proves:

- Reusing prepared right vertex query points across distinct left query batches is semantically valid under the tested global scale-bounds route.
- It removes about `0.30-0.34s` per batch from `vertex_pip_map1_in_map0`.
- It becomes net positive once enough distinct batches amortize the one-time right-vertex preparation cost; the 6-batch run already wins by about `0.90s` after charging that extra prep.

What this does not prove:

- It does not improve cold CLI one-shot performance.
- It does not improve the paper text route.
- It does not prove author parity.
- It does not remove the first-batch LSI workspace cost.
- It does not make the route fully device-resident.

## Exit Label

`completed_prepared_right_vertex_points_query_batch_win__bbox_filter_no_go`
