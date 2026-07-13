# Goal5021: Prepared LSI Base Session Route

Date: 2026-07-05

## Purpose

Continue the v2.14.3 RayJoin performance push by attacking the largest remaining
writer-free route cost: the LSI producer workspace cost.  Goal5020 productized a
generic tiny LSI prewarm and moved the warm-process fresh fast-pack route to
about `2.386s` median.  Its LSI phase was still about `1.535s`, dominated by
per-input workspace work.

Goal5021 tests and productizes a narrower prepared route:

- prepare the LSI right/base planar-map session once;
- for each measured overlay route, build a fresh LSI query object;
- do not reuse the same prepared query output;
- do not prepare the full PIP/operator session.

This is designed to test whether the large grouped-range workspace can be
legitimately amortized by a prepared base session without falling back to
same-query replay.

## Regime

The reported performance is:

- top4 County x Zipcode representative input;
- writer-free binary route;
- warm long-lived process;
- prepared LSI base/right session;
- fresh LSI query object per measured route;
- one warmup route excluded from medians;
- not cold CLI one-shot;
- not prepared operator replay;
- not true query-many, because the measured runs still use the same top4 query
  batch rather than distinct query batches.

## Work Performed

### 1. Add Prepared Base Session Route

Implemented:

- `--prepared-lsi-base-session`
- `produce_lsi_exact_device_columns_from_prepared_base(...)`
- `produce_lsi_bounded_exact_device_columns_from_prepared_base(...)`

The route prepares `base.prepare_planar_map_lsi_2d_optix(right.lsi_segments)`
once, then calls `lsi.prepare_query(left.lsi_segments)` inside each measured
route.  It is mutually exclusive with `--prepared-operator-session`.

### 2. Make Repeat Artifacts Auditable

Repeat rows now include `lsi_extended_timings`, so the report can show whether
LSI cost is pipeline compile, grouped range, scaled cache, OptiX launch, or
device allocation.  This prevents future claims from hiding the real native
phase composition behind a single LSI number.

### 3. Preserve Claim Boundaries

The summary claim text now distinguishes:

- ordinary same-process warm fresh route;
- prepared LSI base-session measurement;
- full prepared operator-session body measurement.

The prepared LSI base-session route explicitly says it is not a cold CLI
one-shot headline and not a true query-many result unless distinct query batches
are provided and measured.

## Validation

Local:

```text
PYTHONPATH=src py -3 -m py_compile \
  Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py

PYTHONPATH=src py -3 -m unittest \
  tests.goal5021_prepared_lsi_base_session_test

Ran 4 tests in 0.001s
OK
```

POD:

```text
python -m unittest tests.goal5021_prepared_lsi_base_session_test

Ran 4 tests in 0.001s
OK
```

POD artifact:

- `history/internal_docs/rtdl_goal5021_prepared_lsi_base_session_top4.json`

Command shape:

```text
python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left .../top4_county.cdb \
  --right .../top4_zipcode.cdb \
  --device-columnar \
  --bounded-exact-lsi-device-columns \
  --bounded-exact-lsi-capacity 1000000 \
  --point-location-device-face-columns \
  --fast-scaled-point-pack \
  --compiled-group \
  --generic-lsi-prewarm \
  --prepared-lsi-base-session \
  --warmup-runs 1 \
  --repeat 3
```

## Result

### Topline For This Regime

```text
median writer_free_hot_sec: 1.031s
median LSI phase:           0.127s
median downstream floor:    0.901s
best writer_free_hot_sec:   1.028s
worst writer_free_hot_sec:  1.047s
```

Structural anchors stayed stable:

```text
lsi_row_count:          428322
descriptor_pair_count:  15014
```

### Comparison To Prior Route Windows

| Route / Regime | writer-free route window | Claim boundary |
|---|---:|---|
| v2.14.3 canonical fast-pack | ~4.22s | warm-process fresh, no prepared base |
| Goal5020 generic LSI prewarm | 2.386s median | warm-process fresh route window, prewarm separate |
| Goal5021 prepared LSI base session | 1.031s median | prepared base/right LSI session, fresh query object per measured route |

This is a large real improvement for the prepared-base regime: about `4.1x`
versus the prior `~4.22s` canonical fast-pack window and about `2.3x` versus
Goal5020.

### Why It Moved

The measured rows show the LSI phase changed from workspace dominated to
scaled-cache dominated:

```text
warmup LSI:
  lsi phase:            1.812s
  grouped_range_ensure: 1.048s
  scaled_cache_ensure:  0.760s

measured LSI median:
  lsi phase:            0.127s
  grouped_range_ensure: ~0.0000005s
  scaled_cache_ensure:  ~0.123s
  optix launch:         ~0.0022s
```

Interpretation: prepared LSI base session successfully amortizes the expensive
grouped-range workspace.  The remaining LSI cost is mostly scaled-cache work
for the query side plus small allocation/launch overhead.

## What This Does Not Prove

This does not prove:

- cold CLI one-shot speedup;
- true query-many on distinct query batches;
- author parity;
- 10x;
- that full device-resident carrier should be restarted;
- that point-location session preparation should be hidden inside this number.

Point-location prepare times are still reported in `key_phase_seconds`, but are
not part of `writer_free_hot_sec`; the route window remains the writer-free
binary operator body definition used in prior v2.14.3 reports.

## Current Honest State

Prepared LSI base session is the first large win after Goal5020:

- it attacks the correct mountain, not a millisecond boundary;
- it uses public generic LSI preparation;
- it keeps RayJoin as an app;
- it does not reuse the same prepared query output;
- it produces stable structural anchors;
- it moves the measured prepared-base route window to about `1.03s`.

The next hard check is true query-many: run at least two distinct same-domain
query batches against one prepared base session and measure whether the
`~0.127s` LSI behavior persists without same-input repetition.

## Exit Label

```text
completed_prepared_lsi_base_session_route__grouped_range_amortized__true_query_many_still_unproven
```
