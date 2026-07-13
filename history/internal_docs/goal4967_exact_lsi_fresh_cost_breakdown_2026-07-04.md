# Goal4967 Exact LSI Fresh Cost Breakdown

Date: 2026-07-04

## Exit Label

`completed_exact_lsi_breakdown__fresh_cost_is_workspace_first_use__hot_lsi_compute_is_small`

## Purpose

Goal4965 identified fresh exact planar-map LSI as the next bottleneck after the
Goal4964 exact device-column no-go.

Goal4967 breaks that cost down before implementing another optimization. The
question was:

> Is the `~0.8s` exact LSI phase dominated by exact traversal/predicate,
> count+emit double-pass output, host materialization/copy, or first-use
> workspace/cache construction?

## Implementation

The RayJoin binary-operator measurement app now records native segment-pair LSI
phase timings in the summary JSON:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

New summary key:

```json
"native_lsi_timings": { ... }
```

This exposes existing native timing fields:

```text
candidate_count_pass
candidate_write_pass
candidate_download
exact_refine
raw_candidate_count
emitted_count
```

For the exact device-column route, it also records:

```text
native_output_traversal_seconds
native_output_row_count
native_output_candidate_event_count
```

No native performance optimization was implemented in this goal. This goal is
measurement and interpretation only.

## POD Environment

```text
host: root@213.173.108.15 -p 10689
workspace: /root/rtdl_goal4955
app: Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

Environment:

```bash
cd /root/rtdl_goal4955
. .venv/bin/activate
export PYTHONPATH=src:.
export RTDL_OPTIX_LIB=/root/rtdl_goal4955/build/librtdl_optix.so
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal4955/build/librtdl_optix.so
```

Input:

```text
left:  Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt
right: Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt
author_overlay_compute_sec: 0.0421
```

Routes measured, three runs each:

```text
host exact pair-id rows
exact pair-id device columns
prepared-hot pair-id rows replay
```

Artifacts:

```text
history/internal_docs/goal4955_artifacts/goal4967_host_run1.json
history/internal_docs/goal4955_artifacts/goal4967_host_run2.json
history/internal_docs/goal4955_artifacts/goal4967_host_run3.json
history/internal_docs/goal4955_artifacts/goal4967_exact_run1.json
history/internal_docs/goal4955_artifacts/goal4967_exact_run2.json
history/internal_docs/goal4955_artifacts/goal4967_exact_run3.json
history/internal_docs/goal4955_artifacts/goal4967_cached_run1.json
history/internal_docs/goal4955_artifacts/goal4967_cached_run2.json
history/internal_docs/goal4955_artifacts/goal4967_cached_run3.json
```

## Results

All runs preserved the semantic fingerprint:

```text
lsi_row_count = 20860
pair_count = 28815
total_groups = 64459
total_point_rows = 673371
```

### Route Medians

| Route | Median writer_free_hot_sec | Ratio vs `0.0421s` | Key LSI phase |
|---|---:|---:|---:|
| host exact pair-id rows | `0.902216s` | `21.43x` | `lsi_public_rows_sec = 0.814622s` |
| exact pair-id device columns | `0.981147s` | `23.31x` | `lsi_exact_pair_id_device_columns_sec = 0.886504s` |
| prepared-hot pair-id rows replay | `0.098241s` | `2.33x` | `lsi_prepared_replay_rows_sec = 0.000910s` |

### Prepared-Hot Decomposition

Median prepared-hot setup/replay timings:

| Phase | Median |
|---|---:|
| `prepare_lsi_session_sec` | `0.274632s` |
| `lsi_public_rows_warmup_sec` | `0.519817s` |
| `lsi_prepared_replay_rows_sec` | `0.000910s` |

Interpretation:

```text
fresh LSI cost ~= prepare session + first-use warmup/cache construction
hot prepared LSI compute ~= microsecond-level native count/write replay
```

### Native Segment-Pair Timings

For host exact pair-id rows, native timings inside the row operation were
microsecond-level:

```text
candidate_count_pass ~= 0.00023s
candidate_write_pass ~= 0.00018-0.00023s
exact_refine         ~= 0.000018s
emitted_count        = 20860
```

For prepared-hot replay, native timings remained microsecond-level and the app
still called `query.run_pair_id_rows()` again:

```text
candidate_count_pass ~= 0.00018s
candidate_write_pass ~= 0.00018s
exact_refine         ~= 0.000016-0.000021s
emitted_count        = 20860
```

This matters: the prepared-hot route is not a pair-id result cache read. It
reruns the native pair-id count/write path over an already-built prepared
workspace.

For exact pair-id device columns, the public app measured:

```text
lsi_exact_pair_id_device_columns_sec ~= 0.886504s
device-to-NumPy copy                 ~= 0.000514s
```

The native output object also reported:

```text
native_output_traversal_seconds ~= 0.858326s
```

But the native `candidate_count_pass` and `candidate_write_pass` fields were
still microsecond-level. Therefore this route's large native-output time is
not the pair-id column copy. It is first-use native workspace/cache work inside
the device-column path.

## Findings

### F1. The previous "exact traversal dominates" wording was too coarse

The `~0.8s` fresh LSI phase is not dominated by the measured OptiX count/write
launches themselves. Those launches are around `0.0004s` combined once the
workspace is prepared.

The better current diagnosis is:

```text
fresh exact LSI cost is dominated by workspace/session first-use construction
and lazy planar-map LSI caches/grouped-range setup.
```

### F2. Single-pass exact pair-id production is not the immediate highest-leverage step

Goal4965 listed single-pass exact pair-id production as a possible next attack.
Goal4967 weakens that option.

Reason:

```text
count pass + write pass launch time is already sub-millisecond in prepared-hot state.
```

Removing one of those passes cannot recover the `~0.8s` fresh cost if the
dominant cost is first-use workspace/cache construction.

Single-pass may still be a cleanup, but it is not the next large performance
move unless a future profile contradicts this breakdown.

### F3. The prepared-hot route should be renamed conceptually

The prior packets conservatively called the `0.087-0.098s` route "cached
replay" and warned that it excluded LSI computation.

Goal4967 refines that:

```text
It excludes workspace/cache build, but it does not merely read cached pair-id
results. It reruns pair-id count/write on an already prepared workspace.
```

More precise name:

```text
prepared-hot workspace replay
```

Allowed claim:

```text
On an already prepared planar-map LSI workspace, the writer-free binary route
runs in about 0.10s on the public sample.
```

Forbidden claim:

```text
Fresh one-shot overlay is 0.10s.
```

### F4. There are now two honest performance boundaries

| Boundary | Cost | Meaning |
|---|---:|---|
| one-shot fresh operator | `~0.90s` | includes workspace/cache first use |
| prepared-hot workspace operator | `~0.10s` | excludes workspace/cache build, reruns native pair-id rows |

Which boundary is appropriate depends on the product story:

- For a one-shot script, use the fresh number.
- For a database/dataflow operator with prepared map/workspace reuse, the
  prepared-hot number is the relevant steady-state operator number.

### F5. The next optimization is workspace preparation, not pair-id copy

The next credible work should target:

1. making planar-map LSI workspace preparation explicit and measurable,
2. moving lazy first-use caches/grouped ranges into an explicit prepare step,
3. reducing or amortizing that prepare step,
4. documenting which API boundary is one-shot fresh vs prepared-hot.

If the user wants one-shot script performance, optimize workspace build.
If the user wants database/dataflow operator performance, expose the prepared
workspace contract and measure steady-state pipeline use.

## Revised Next Goals

### Goal4968: Planar-Map LSI Workspace Preparation Contract

Purpose:

- make the hidden first-use setup explicit,
- separate `prepare_base`, `prepare_query`, `build_scaled_lsi_caches`,
  `build_grouped_ranges`, and `hot_pair_id_rows`,
- expose a clean app/user contract for prepared workspace reuse.

Gate:

- no RayJoin overlay semantics in core,
- exact fingerprint preserved,
- both fresh and prepared-hot boundaries reported.

### Goal4969: Workspace Build Cost Reduction

Only open after Goal4968 shows which setup subphase dominates.

Possible attacks:

- cache scaled planar-map LSI segment arrays at dataset load/prepare time,
- build grouped ranges during explicit prepare,
- avoid repeated native allocation or pipeline ensure on first run,
- make prepare cost reusable across multiple downstream operations.

### Goal4970: Larger Representative Data Restoration

Still required. Current performance numbers are public-sample-only.

## Status Change From Goal4965

Goal4965's broad statement:

```text
exact planar-map LSI fresh compute is the next bottleneck
```

is still true at the top level.

Goal4967 refines it:

```text
the immediate bottleneck is not pair-id traversal/copy; it is first-use
workspace/cache preparation before the hot exact pair-id operation becomes
microsecond-level.
```

## Not Authorized

- No claim that fresh overlay is `0.10s`.
- No claim that RTDL is broadly faster than AuthorPatch.
- No claim that prepared-hot replay is the same boundary as fresh one-shot
  overlay.
- No claim that single-pass exact pair-id production is the next large win.
- No claim that larger representative data has been tested.
