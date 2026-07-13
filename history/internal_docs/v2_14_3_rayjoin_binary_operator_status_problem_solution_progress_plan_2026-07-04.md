# v2.14.3 RayJoin Binary Operator Status: Problem, Solution, Progress, Current State, Plan

Date: 2026-07-04

## 1. Problem

The original RayJoin Section 5.7 reproduction line measured RTDL through a
paper-style text-output program. That was useful for correctness, but it was
the wrong performance lens for RTDL as a spatial data pipeline system.

The slow path had several distinct causes:

1. **Text writer cost**

   The paper text-output route writes the author's exact output-chain text
   format. In the RTDL app this was Python string/object work, while the author
   implementation is C++/CUDA/OptiX. This writer cost is mostly not RT/GPU
   work. It measures Python-vs-C++ serialization more than RTDL's spatial
   operator value.

2. **Wrong benchmark shape for a database-style operator**

   In a real spatial pipeline, overlay should be a middle operator:

   ```text
   binary/columnar input -> RTDL spatial operator -> binary/columnar output -> downstream operator
   ```

   It should not necessarily dump a huge paper text file. The text route
   remains important as a correctness anchor, but it is not the best way to
   measure RTDL's value as a pipeline operator.

3. **Misread LSI cost**

   Earlier measurements showed `lsi_public_rows_sec` around 0.8 seconds. That
   was initially treated as a hot-path LSI cost. Goal4958 showed that this was
   wrong: the first `run_pair_id_rows()` includes first-use LSI session/cache
   work. A second exact pair-id replay on the same prepared query is around
   0.0009 seconds.

4. **Existing device-column assets are not exact pair-id output**

   Current RTDL has useful segment-pair device-column assets, but they are not
   exact planar-map LSI pair-id columns:

   - `candidate_device_columns` gives candidate pair streams, not exact LSI
     witness rows.
   - `left_id_count_device_columns` gives grouped counts by left id, not exact
     `{left_id, right_id}` pairs.

   These cannot be substituted for exact pair-id rows without breaking
   correctness.

5. **Generic-system boundary**

   RTDL must remain a generic RT/dataflow system. RayJoin is an app on top of
   RTDL, not a reason to hide RayJoin-specific overlay semantics inside core.
   Any new core primitive must be generic, such as exact planar-map LSI
   `{left_id, right_id}` device columns. RayJoin text-output chains are app
   semantics.

## 2. Solution

The corrected direction is:

> Treat RayJoin overlay as a writer-free binary pipeline operator, not as a
> standalone text-output program.

The route now has two separate roles:

1. **Paper text route**

   Used for correctness and paper reproduction boundaries. This is the route
   that can compare byte-for-byte output-chain text where applicable.

2. **Numeric/binary operator route**

   Used to measure RTDL as a pipeline operator. It produces a binary/columnar
   descriptor/fingerprint for downstream consumers instead of writing the paper
   text file.

The implementation principles are:

- Use public RTDL planar-map LSI and point-location/PIP primitives.
- Keep RayJoin composition in the app layer.
- Use Numba/CUDA for numeric reprojection and xsect ordering.
- Use Numba compiled code for columnar group construction.
- Keep all claims explicitly bounded:
  - no cold-start claim for prepared-hot numbers;
  - no paper text-output speed claim for binary route;
  - no byte-equality claim for numeric/binary route;
  - no broad RayJoin-system speedup claim;
  - no Layer 4 fusion claim;
  - no claim that exact LSI pair-id device columns already exist.

## 3. Progress

The optimization line produced several concrete stages.

| Stage | Result | Meaning |
|---|---:|---|
| Original numeric binary route | ~2.92s | Python object/sort/group work remained heavy. |
| Goal4956 columnar CPU route | ~2.31s | Removed part of object materialization and moved toward columnar arrays. |
| Goal4957 device-columnar + compiled group | ~0.90s | CUDA reprojection/sort plus compiled group construction reduced the hot path substantially. |
| Goal4958 cached LSI replay | **0.08594s median replay body** | Separates first-use LSI compute from replay; this is not a fresh-overlay same-denominator author comparison. |

Goal4958 POD:

```text
host: root@213.173.108.15 -p 10689
workspace: /root/rtdl_goal4955
GPU: NVIDIA RTX 4000 Ada Generation
```

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

The ratio above is the script's arithmetic field, not an authorized headline.
It compares a cached/replay RTDL body that excludes first exact LSI computation
against an author overlay-compute baseline that includes overlay computation.
The fair fresh-overlay comparison remains approximately:

```text
RTDL fresh binary route: ~0.90s
AuthorPatch overlay compute: 0.0421s
fresh-route ratio: ~21x slower
```

Stable semantic fingerprint:

```text
lsi_row_count = 20860
pair_count = 28815
total_groups = 64459
total_point_rows = 673371
```

CUDA sort validation:

```text
map0_order_matches_cpu_longdouble_reference = true
map1_order_matches_cpu_longdouble_reference = true
writer_free_hot_sec = 0.0861542196944356
ratio_vs_author = 2.046418520057853
```

The important correction is that first-use LSI work is now separated:

```text
prepare_lsi_session_sec ~= 0.26s
lsi_public_rows_warmup_sec ~= 0.51-0.53s
lsi_prepared_replay_rows_sec ~= 0.00091s
```

## 4. Current State

The current v2.14.3 RayJoin binary route is a writer-free pipeline-operator
prototype with both fresh and cached/replay measurements.

It proves:

- RTDL public primitives plus Numba/CUDA can express and execute the RayJoin
  Section 5.7 numeric/binary overlay route.
- The cached/replay body can run in about 0.086 seconds on the public
  County x Soil sample after exact LSI pair ids have already been computed
  once.
- The fresh writer-free binary route remains around 0.90 seconds, about 21x
  slower than the patched author overlay compute baseline of 0.0421 seconds.
- The earlier diagnosis that LSI exact pair rows cost around 0.8 seconds on the
  hot path was wrong; that was first-use/warmup cost.
- Existing device-column candidate/count APIs cannot be promoted as exact
  pair-id output.

It does not prove:

- Cold-start runtime is 0.086 seconds.
- Paper text-output runtime is 0.086 seconds.
- The numeric/binary route is byte-equal to the paper text output.
- Broad RayJoin-system speedup.
- Layer 4 traversal fusion.
- Exact LSI pair-id device columns already exist in RTDL core.
- Same-denominator 2.04x comparison against the author overlay compute.

Relevant files:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `Paper-reproduction-apps/rayjoin-paper/README.md`
- `tests/goal4956_columnar_xsect_pipeline_test.py`
- `history/internal_docs/goal4958_prepared_hot_lsi_replay_and_exact_device_output_audit_2026-07-04.md`
- `history/internal_docs/call_for_review_goal4958_prepared_hot_lsi_replay_2026-07-04.md`
- `history/internal_docs/goal4955_artifacts/goal4958_prepared_lsi_replay_run1.json`
- `history/internal_docs/goal4955_artifacts/goal4958_prepared_lsi_replay_run2.json`
- `history/internal_docs/goal4955_artifacts/goal4958_prepared_lsi_replay_run3.json`
- `history/internal_docs/goal4955_artifacts/goal4958_prepared_lsi_replay_validate.json`

Local verification:

```text
py -m unittest tests.goal4955_projected_descriptor_pipeline_test \
  tests.goal4956_columnar_xsect_pipeline_test \
  tests.goal4947_lsi_pair_columns_numba_handoff_test

Ran 8 tests in 0.112s
OK (skipped=2)
```

Public RayJoin app/README leak scan:

```text
rg -n "Goal[0-9]+|goal[0-9]+|history/internal_docs|call_for_review|verdict" \
  Paper-reproduction-apps/rayjoin-paper/README.md \
  Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py

no matches
```

## 5. Plan

### 5.1 Review Gate

Goal4958 has been sent for external/subagent review. The review was still
pending at the time this status document was written.

Review must check:

- prepared-hot timing boundary;
- correctness of the cached/replay 0.08594s boundary and rejection of a 2.04x
  same-denominator headline;
- rejection of candidate/count device-column substitutions;
- no RTDL core/native edits;
- no overclaiming.

### 5.2 Representative Input Confirmation

Run the same fresh and cached/replay binary routes on one larger representative
input if available.

Purpose:

- confirm whether the fresh ~0.90s and cached/replay ~0.086s separation holds;
- measure whether the fresh ~21x gap vs AuthorPatch changes with scale;
- keep the same semantic fingerprint discipline.

### 5.3 Decide On Generic Exact LSI Device Pair Columns

If further performance is needed, the most natural generic primitive is:

```text
exact planar-map LSI pair ids -> device columns {left_id, right_id}
```

This would be a core/native feature, so it needs a separate goal and review.
It must remain generic:

- allowed: exact `{left_id, right_id}` pair-id device columns;
- forbidden: RayJoin output-chain or overlay-specific semantics in core.

### 5.4 Consolidate Paper App Documentation

The RayJoin paper-reproduction app should clearly expose three modes:

1. Paper text correctness route.
2. Numeric/binary route.
3. Prepared-hot binary operator route.

Each mode should state what it proves and what it does not prove.

### 5.5 Keep Performance Claims Honest

Allowed claim:

> The writer-free prepared-hot RayJoin binary operator route reaches about
> 0.086 seconds on a cached/replay run after exact LSI pair ids have already
> been computed once. The fresh writer-free binary route remains around 0.90
> seconds, about 21x slower than the patched author overlay compute baseline,
> with stable numeric fingerprint.

Forbidden claims:

- cold-start runtime is 0.086 seconds;
- text-output reproduction runtime is 0.086 seconds;
- fresh overlay runtime is 0.086 seconds;
- broad RayJoin speedup;
- full paper Section 5.7 hidden-input reproduction;
- RTDL beats AuthorPatch;
- RTDL is only 2.04x slower than AuthorPatch on a same-denominator fresh
  overlay comparison;
- exact LSI device columns already exist.

## Summary

The important outcome is not just a faster number. The project clarified the
right benchmark:

```text
RTDL as a writer-free spatial pipeline operator, with fresh and cached/replay
measurements kept separate
```

Under that benchmark, the RayJoin app has moved from roughly 2.92 seconds to
roughly 0.90 seconds on a fresh writer-free binary route, while preserving a
stable binary/semantic fingerprint. A cached/replay body after exact LSI has
already been computed is roughly 0.086 seconds, but that is not a fresh-overlay
comparison. The remaining fresh-route gap to the patched author compute
baseline is still about 21x, and the main next bottleneck is exact LSI
computation/device output.
