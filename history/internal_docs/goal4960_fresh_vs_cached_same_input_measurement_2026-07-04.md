# Goal4960 Fresh Vs Cached Replay Same-Input Measurement

Date: 2026-07-04

## Exit Label

`completed_same_input_fresh_vs_cached_measurement__fresh_route_0_889s__cached_replay_0_087s`

## Purpose

Run the RayJoin Section 5.7 writer-free binary route on the same public
County x Soil input under two explicit timing modes:

1. **Fresh route**: one normal route execution, including first exact public LSI
   pair-row computation inside `writer_free_hot_sec`.
2. **Cached/replay route**: one exact LSI warmup on the same prepared query,
   then a second exact pair-row replay used inside `writer_free_hot_sec`.

This goal exists to prevent another denominator mix-up.

## POD

```text
host: root@213.173.108.15 -p 10689
workspace: /root/rtdl_goal4955
GPU: NVIDIA RTX 4000 Ada Generation
```

Inputs:

```text
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt
```

Command shape:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left .../br_county_clean_25_odyssey_final.txt \
  --right .../br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil \
  --device-columnar \
  --compiled-group \
  --author-overlay-compute-sec 0.0421 \
  --summary /tmp/goal4960_fresh_runN.json
```

Cached/replay adds:

```bash
--prepared-lsi-replay
```

## Artifacts

- `history/internal_docs/goal4955_artifacts/goal4960_fresh_run1.json`
- `history/internal_docs/goal4955_artifacts/goal4960_fresh_run2.json`
- `history/internal_docs/goal4955_artifacts/goal4960_fresh_run3.json`
- `history/internal_docs/goal4955_artifacts/goal4960_cached_replay_run1.json`
- `history/internal_docs/goal4955_artifacts/goal4960_cached_replay_run2.json`
- `history/internal_docs/goal4955_artifacts/goal4960_cached_replay_run3.json`
- `history/internal_docs/goal4955_artifacts/goal4960_fresh_vs_cached_same_input_summary.json`

## Results

| Mode | Run | writer_free_hot_sec | Ratio field vs 0.0421s | LSI first/warm | LSI replay | Groups |
|---|---:|---:|---:|---:|---:|---:|
| fresh | 1 | 0.889023 | 21.117x | 0.795467 | n/a | 64459 |
| fresh | 2 | 0.914924 | 21.732x | 0.819967 | n/a | 64459 |
| fresh | 3 | 0.869626 | 20.656x | 0.784056 | n/a | 64459 |
| cached/replay | 1 | 0.093773 | 2.227x | 0.519383 | 0.000938 | 64459 |
| cached/replay | 2 | 0.086828 | 2.062x | 0.527234 | 0.000906 | 64459 |
| cached/replay | 3 | 0.087069 | 2.068x | 0.524916 | 0.000935 | 64459 |

Median:

```text
fresh_median_writer_free_hot_sec = 0.8890228355303407
fresh_median_ratio_vs_author = 21.116931960340633

cached_replay_median_writer_free_hot_sec = 0.08706910163164139
cached_replay_median_ratio_arithmetic_not_same_denominator = 2.0681496824617907
```

Stable fingerprint in all six runs:

```text
pair_count = 28815
total_groups = 64459
total_point_rows = 673371
```

## Interpretation

Goal4960 confirms Claude's review of Goal4958:

- The fair fresh-route comparison is about `0.889s / 0.0421s`, or about
  `21.1x` slower than AuthorPatch overlay compute.
- The cached/replay route is about `0.087s`, but this excludes the first exact
  LSI computation and is not a same-denominator author comparison.
- The original fresh-route improvement remains real:

```text
~2.92s -> ~0.89s
```

That is roughly a 3.3x improvement over the original numeric binary route.

## What This Proves

- The corrected fresh/cached measurement boundary is stable on the public
  County x Soil sample.
- The writer-free binary route has materially improved from the original
  numeric binary route.
- The remaining fresh-route bottleneck is the first exact LSI pair-row
  computation, not replay.

## What This Does Not Prove

- It does not prove that RTDL is 2x behind AuthorPatch on a fresh overlay.
- It does not prove cold-start speed.
- It does not prove paper text-output speed.
- It does not prove hidden Section 5.7 full-suite performance.
- It does not prove exact LSI pair-id device columns exist.

## Next

Goal4961 should identify one larger representative Section 5.7 input. If one
is available, Goal4962 should run the same fresh/cached split on that input.
