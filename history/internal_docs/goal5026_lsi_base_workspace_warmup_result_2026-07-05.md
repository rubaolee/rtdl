# Goal5026 - LSI Base Workspace Warmup Result

Date: 2026-07-05

## Verdict

`completed_lsi_base_workspace_warmup_moves_first_batch_lsi_to_session__not_6_batch_net_throughput_win`

Goal5026 added a prepared-session warmup route for the exact LSI base workspace used by the writer-free RayJoin 5.7 binary query-batch route.

The result is real and useful, but bounded:

- It moves the first measured batch's LSI workspace setup out of the query body.
- It improves prepared-service first-query body latency.
- It does not erase the cost; it charges about `1.612s` to session preparation.
- On a 6-batch run, the body improves by about `0.852s`, so the total including this new session warmup is not a throughput win yet.

This is not a cold CLI result, not a paper-text route result, not author parity, and not a 10x claim.

## Implementation

Changed file:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

New CLI:

```bash
--prepared-lsi-base-workspace-warmup
```

Requirements:

- `--prepared-lsi-base-session`
- `--query-chain-batches > 0`
- `--bounded-exact-lsi-device-columns`

Behavior:

1. During prepared LSI base-session setup, create a tiny unmeasured left query slice:

```python
warmup_left = _slice_dataset_by_chain_range(left, start_chain=0, end_chain=1)
```

2. Run the existing generic prepared-base exact LSI device-column producer once:

```python
produce_lsi_bounded_exact_device_columns_from_prepared_base(...)
```

3. Immediately close the returned device columns.

4. Record only timing fields into `session_phase_seconds`.

This does not replay the measured query batch. The warmup uses a tiny unmeasured query only to initialize reusable base LSI workspace.

## Validation

Local:

```text
py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
py -3 -m unittest tests.goal5021_prepared_lsi_base_session_test
```

Result:

```text
9 tests OK
```

POD command:

```bash
python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb \
  --right Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb \
  --summary history/internal_docs/rtdl_goal5026_query6_lsi_base_workspace_warmup_top4.json \
  --device-columnar \
  --native-lexsort \
  --bounded-exact-lsi-device-columns \
  --bounded-exact-lsi-capacity 1000000 \
  --point-location-device-face-columns \
  --prepared-lsi-base-workspace-warmup \
  --prepared-query-batch-right-vertex-points \
  --prepared-query-batch-segment-arrays \
  --fast-scaled-point-pack \
  --compiled-group \
  --generic-lsi-prewarm \
  --prepared-lsi-base-session \
  --query-chain-batches 6 \
  --repeat 1
```

Artifact:

- `history/internal_docs/rtdl_goal5026_query6_lsi_base_workspace_warmup_top4.json`

## Key Numbers

Same top4 County x Zipcode input; writer-free binary query-batch route; 6 chain-contiguous full-overlay query batches.

### Before: Goal5025 Native Lexsort

Artifact:

- `history/internal_docs/rtdl_goal5025_query6_prepared_right_points_segments_native_lexsort_top4.json`

```text
body_sum:        3.012616s
later_body_sum:  1.187455s
median_body:     0.244431s
first_batch:     1.825161s
first_batch_lsi: 1.595264s
first_carrier:   0.070978s
```

### After: Goal5026 LSI Base Workspace Warmup

Artifact:

- `history/internal_docs/rtdl_goal5026_query6_lsi_base_workspace_warmup_top4.json`

```text
body_sum:          2.160384s
later_body_sum:    1.173854s
median_body:       0.242220s
best_body:         0.211524s
worst_body:        0.986529s

session_warmup:    1.612296s
warmup_lsi_phase:  1.611603s
warmup_traversal:  0.0000757s
```

Per-batch:

| batch | writer-free body | LSI phase | sort map1 | carrier |
|---:|---:|---:|---:|---:|
| 0 | 0.986529s | 0.055278s | 0.101373s | 0.780675s |
| 1 | 0.211524s | 0.038096s | 0.098875s | 0.053687s |
| 2 | 0.242869s | 0.041576s | 0.102930s | 0.057557s |
| 3 | 0.250489s | 0.041874s | 0.104419s | 0.063171s |
| 4 | 0.227402s | 0.042140s | 0.102721s | 0.056448s |
| 5 | 0.241571s | 0.042268s | 0.101003s | 0.065218s |

## Interpretation

The first measured query body's LSI phase moved:

```text
1.595264s -> 0.055278s
```

That is the win.

But the route added:

```text
session_prepare_lsi_base_workspace_warmup_sec = 1.612296s
```

So this is a prepared-service latency shift:

- Better measured first-query body latency.
- Similar later-batch steady state.
- Not yet a 6-batch net throughput win after charging session prep.

For 6 batches:

```text
body saving:              3.012616s - 2.160384s = 0.852232s
new session warmup cost:  1.612296s
net including warmup:     about 0.760s worse
```

For a long-lived prepared service, this can be useful if the session warmup is done before user-facing query latency, or if many query batches amortize it. For a one-shot run, it is not a win.

## Genericity And Boundary

This is app-layer orchestration around an existing generic prepared-base LSI producer.

It does not:

- add a RayJoin-specific RTDL core primitive;
- add paper-text writer logic to RTDL core;
- claim author performance parity;
- claim cold CLI improvement;
- claim 10x.

It does:

- explicitly mark the route as `prepared_lsi_base_workspace_warmup`;
- record the warmup under session preparation;
- keep the measured query batches distinct from the tiny unmeasured warmup query.

## Remaining Mountains

The next large items visible in this regime:

1. Carrier first-call / cache variance:
   - Goal5026 batch 0 carrier was `0.780675s`, while later batches were about `0.05-0.07s`.
   - This may be a remaining warmup/JIT/signature issue.

2. Persistent sort floor:
   - `sort_map1_device_columnar_sec` remains about `0.10s` per batch.
   - Native lexsort helped only modestly.

3. LSI per-batch floor:
   - Later LSI is now about `0.038-0.042s` per batch.
   - This is far smaller than the original first-batch workspace setup, but still part of steady state.

## Recommended Next Goal

Next goal should attack carrier first-call variance before chasing smaller sort deltas:

```text
Goal5027: carrier first-call warmup / signature parity audit
```

Required test:

- same top4 6-batch query route;
- compare without/with carrier-specific warmup;
- report both body-only and session-prep-charged totals;
- fail closed if this only shifts cost into prep with no useful prepared-service latency benefit.
