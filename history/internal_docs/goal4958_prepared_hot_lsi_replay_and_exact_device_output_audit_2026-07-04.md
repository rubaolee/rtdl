# Goal4958 Prepared-Hot LSI Replay And Exact Device Output Audit

Date: 2026-07-04

## Verdict

`completed_cached_lsi_replay_measurement__fresh_overlay_remains_about_0_90s__exact_device_pair_columns_missing`

Goal4958 found and fixed a measurement-accounting mistake in the v2.14.3
RayJoin binary route: `lsi_public_rows_sec` mixed first-use LSI session/cache
work with the subsequent exact pair-id replay. Reusing the same prepared public
LSI query makes a second exact pair-id replay roughly 0.0009 seconds on the
public County x Soil sample.

This does **not** mean a fresh overlay computation costs 0.086 seconds. The
fresh binary overlay cost remains approximately Goal4957's 0.90 second class:

```text
prepare_lsi_session_sec      ~= 0.26s
lsi_public_rows_warmup_sec   ~= 0.51s
cached/replay binary body    ~= 0.086s
total fresh prepared run     ~= 0.86s ~= Goal4957 ~0.90s
```

The app now exposes the cached/replay timing explicitly through
`--prepared-lsi-replay`. It is useful for studying amortized repeated execution
on the same prepared pair, but it must not be compared as a same-denominator
fresh overlay computation against the author's 0.0421 second overlay compute.

## Files Changed

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `Paper-reproduction-apps/rayjoin-paper/README.md`
- `tests/goal4956_columnar_xsect_pipeline_test.py`

No files under `src/rtdsl/**` or `src/native/**` were edited.

## What Changed

`section57_overlay_columnar_binary.py` now supports:

```bash
--prepared-lsi-replay
```

This mode:

1. Builds the public planar-map LSI session.
2. Runs one exact `run_pair_id_rows()` warmup in the same prepared query.
3. Feeds the second exact `run_pair_id_rows()` replay into the numeric binary
   overlay route.
4. Records `prepare_lsi_session_sec` and `lsi_public_rows_warmup_sec` outside
   `writer_free_hot_sec`.
5. Uses `lsi_prepared_replay_rows_sec` inside `writer_free_hot_sec`.

This keeps the old cold/default route available and makes the prepared-hot
route explicit.

## POD Evidence

POD:

```text
root@213.173.108.15 -p 10689
workspace: /root/rtdl_goal4955
GPU: NVIDIA RTX 4000 Ada Generation
```

Command shape:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt \
  --right Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil \
  --device-columnar \
  --compiled-group \
  --prepared-lsi-replay \
  --author-overlay-compute-sec 0.0421 \
  --summary /tmp/goal4958_prepared_lsi_replay_runN.json
```

Artifacts:

- `history/internal_docs/goal4955_artifacts/goal4958_prepared_lsi_replay_run1.json`
- `history/internal_docs/goal4955_artifacts/goal4958_prepared_lsi_replay_run2.json`
- `history/internal_docs/goal4955_artifacts/goal4958_prepared_lsi_replay_run3.json`
- `history/internal_docs/goal4955_artifacts/goal4958_prepared_lsi_replay_validate.json`

Three-run cached/replay summary:

| Run | writer-free hot sec | vs AuthorPatch 0.0421s | prepare LSI | warmup exact rows | prepared replay rows | compiled group |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 0.087240 | 2.072x | 0.256141 | 0.520213 | 0.000906 | 0.010181 |
| 2 | 0.085938 | 2.041x | 0.272640 | 0.509616 | 0.000925 | 0.009979 |
| 3 | 0.085791 | 2.038x | 0.258690 | 0.525651 | 0.000901 | 0.009904 |

Cached/replay median:

```text
writer_free_hot_sec = 0.08593776263296604
writer_free_hot_vs_author_overlay_compute_ratio = 2.0412770221607137
```

This ratio is recorded only as the script's arithmetic field. It is **not** an
authorized same-denominator performance comparison, because the RTDL number
excludes the first LSI computation while the author baseline includes overlay
compute.

Correctness / semantic fingerprint was stable in all three runs:

```text
lsi_row_count = 20860
pair_count = 28815
total_groups = 64459
total_point_rows = 673371
```

Validation run:

```text
map0_order_matches_cpu_longdouble_reference = true
map1_order_matches_cpu_longdouble_reference = true
writer_free_hot_sec = 0.0861542196944356
ratio_vs_author = 2.046418520057853
```

## Exact Device Pair-Column Audit

Goal4958 also checked whether the current RTDL core already exposes exact LSI
`{left_id, right_id}` rows as device columns.

Result: not yet.

Existing device-column APIs found:

- `candidate_device_columns`: device-resident candidate pair stream.
- `left_id_count_device_columns`: device-resident grouped left-id counts.

Neither is a substitute for exact planar-map LSI pair-id rows:

- `candidate_device_columns` produced `candidate_event_count = 20972` on the
  same input, while exact planar-map LSI rows are `20860`.
- `candidate_device_columns.exact_relation_witness_rows_materialized` is
  explicitly `False`.
- `left_id_count_device_columns` reported `source_row_count = 20860`, but it
  only exposes grouped left-id counts, not exact `{left_id, right_id}` pairs.

Therefore no candidate/device-count route was promoted into the RayJoin app.
The app still uses the public exact `run_pair_id_rows()` route for correctness,
but now separates first-use warmup from prepared-hot replay.

## Interpretation

The earlier diagnosis that the replay path itself was slow was too pessimistic:
after the first LSI computation, exact pair-id replay is cheap. But the fresh
overlay computation still pays the first LSI computation. That cost is the
dominant remaining gap in the fair, same-denominator comparison.

Current route taxonomy:

```text
v2.14.1 / v2.14.2 numeric binary route: ~2.92s
Goal4957 device-columnar route:          ~0.90s
Goal4958 cached/replay body only:        ~0.086s
AuthorPatch overlay compute:             ~0.0421s
```

Authorized interpretation:

```text
fresh binary overlay: ~0.90s, about ~21x AuthorPatch overlay compute
cached/replay body after LSI already computed: ~0.086s
device-columnar improvement over initial numeric binary route: ~3x
```

The real progress is the ~3x fresh-route improvement from ~2.92s to ~0.90s and
the clear isolation of the next bottleneck: the first exact LSI computation
(`lsi_public_rows_warmup_sec`, about 0.51s). The cached/replay body is useful
evidence for amortized repeated execution, but it does not close the fresh
overlay gap.

## Boundaries

Authorized:

- Prepared-hot binary operator measurement.
- Public RTDL LSI/PIP plus Numba/CUDA app-layer numeric route.
- Writer-free downstream binary descriptor.
- Device CUDA reprojection and sort.
- Numba compiled group construction.
- Cached/replay measurement after exact LSI pair ids have already been
  computed once.

Not authorized:

- Cold-start speedup claim.
- Paper text-output speedup claim.
- Byte-for-byte paper text output claim for the numeric route.
- Broad RayJoin-system speedup claim.
- Layer 4 fusion claim.
- Claim that RTDL already exposes exact LSI pair-id rows as device columns.
- Claim that 0.086 seconds is a fresh overlay computation.
- Claim that 0.086 seconds is a fair same-denominator comparison to the
  author's 0.0421 second overlay compute.

## Next Work

The remaining fresh-overlay gap to AuthorPatch is still around 21x in the
current bounded sample, dominated by first exact LSI computation. The next work
should be chosen carefully:

1. Repeat both fresh and cached/replay measurements on one larger
   representative input if available.
2. Decide whether to implement exact LSI pair-id device columns in RTDL core as
   a generic primitive. This was not done here.
3. Continue only if the new work preserves the generic boundary: exact
   `{left_id, right_id}` pair columns are generic; RayJoin overlay output-chain
   semantics are not.
