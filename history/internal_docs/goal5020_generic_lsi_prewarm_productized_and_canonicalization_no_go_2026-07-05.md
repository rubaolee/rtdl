# Goal5020: Generic LSI Prewarm Productized; CPU Duplicate Canonicalization No-Go

Date: 2026-07-05

## Purpose

Continue the v2.14.3 RayJoin performance push without changing the generic
system boundary.  The owner explicitly challenged whether native CUDA/Thrust
and prepared workspace techniques were being avoided unnecessarily.  Goal5019
showed native Thrust lexsort was correct but only a small sort win.  Goal5020
therefore attacked the larger remaining costs:

1. directed point-location duplicate-half-edge canonicalization;
2. generic LSI compile/setup cost in the warm-process fresh fast-pack route.

## Regime

All performance numbers below are for the same fixed route unless stated
otherwise:

- top4 County x Zipcode representative input;
- writer-free binary route;
- warm long-lived process;
- fresh overlay route, not prepared replay;
- fast-pack route, not the stopped device-resident carrier track;
- bounded exact LSI device columns;
- point-location device face columns;
- device-columnar reprojection/sort;
- compiled CPU Numba carrier.

This is not a cold CLI one-shot claim and not a true query-many measurement.

## Work Performed

### 1. Duplicate Canonicalization Structure Audit

We first tested whether duplicate half-edge canonicalization could be reduced
from global grouping to a linear adjacent-run scan.  It cannot.

POD quick audit:

| Dataset | Segments | Adjacent duplicate pairs | Duplicate fingerprint members |
|---|---:|---:|---:|
| top4_county | 1,705,027 | 0 | 1,022,398 |
| top4_zipcode | 9,982,960 | 23 | 9,341,246 |

Interpretation: duplicate half-edge groups are overwhelmingly non-adjacent in
input order.  A local/linear adjacent-run canonicalization would be incorrect.

### 2. CPU Hash Canonicalization Probe

Two opt-in native probes were implemented on the POD and then removed from the
source tree after measurement:

- `hash`: `std::unordered_map` grouping;
- `flat_hash`: open-addressing array grouping.

Both preserved structural anchors but were slower than the existing sort path.

Artifacts:

- `history/internal_docs/rtdl_goal5020_sort_baseline_top4.json`
- `history/internal_docs/rtdl_goal5020_hash_canonical_top4.json`
- `history/internal_docs/rtdl_goal5020_flat_hash_canonical_top4.json`

| Mode | Large locator duplicate canonicalize | Small locator duplicate canonicalize | Decision |
|---|---:|---:|---|
| current sort | 1.302s | 0.186s | keep |
| `std::unordered_map` hash | 3.394s | 0.658s | no-go |
| flat open-addressing hash | 2.188s | 0.405s | no-go |

Structural anchors stayed stable in all runs:

- `lsi_row_count = 428322`
- descriptor pair count `15014`
- vertex positives `{side0_in_side1: 812721, side1_in_side0: 4527305}`

Conclusion: CPU hash is not the path.  If duplicate canonicalization must move,
the next serious route is GPU/Thrust sort/reduce or a deeper prepared-locator
reuse strategy, not host hash.

### 3. Productize Generic LSI Prewarm

Goal5007 proved with an external probe that a tiny generic LSI prewarm moves
the warm-process fresh route.  Goal5020 turns that into an app CLI option:

```text
--generic-lsi-prewarm
```

Implementation:

- Added `_generic_lsi_tiny_prewarm()` to
  `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`.
- The prewarm uses only the public generic API:
  `base.prepare_planar_map_lsi_2d_optix(...)` plus
  `query.run_bounded_pair_id_device_columns(...)` on a one-segment synthetic
  input.
- It does not import `rayjoin_overlay`, does not touch output-chain logic, and
  does not add a RayJoin-specific core primitive.
- Summary JSON records the prewarm separately under `generic_lsi_prewarm`.
- Claim boundary records:
  - prewarm time is excluded from `writer_free_hot_sec`;
  - no cold CLI one-shot speedup is authorized;
  - no true query-many or 10x claim is authorized.

Changed files:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5020_generic_lsi_prewarm_cli_test.py`

## Validation

Local:

```text
PYTHONPATH=src py -3 -m unittest \
  tests.goal5020_generic_lsi_prewarm_cli_test \
  tests.goal5019_native_lexsort_bridge_test

Ran 6 tests in 0.012s
OK

PYTHONPATH=src py -3 -m py_compile \
  Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  src/rtdsl/optix_runtime.py
OK
```

POD:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk-8.1 CUDA_PREFIX=/usr/local/cuda-12.8
OK

python -m unittest \
  tests.goal5020_generic_lsi_prewarm_cli_test \
  tests.goal5019_native_lexsort_bridge_test

Ran 6 tests in 0.009s
OK
```

## POD Performance

Single formal CLI run with `--generic-lsi-prewarm`:

Artifact:

- `history/internal_docs/rtdl_goal5020_generic_lsi_prewarm_top4.json`

```text
prewarm elapsed_sec:       1.054s
writer_free_hot_sec:       3.404s
LSI phase:                 1.756s
downstream floor:          1.648s
lsi_row_count:             428322
descriptor pair count:     15014
```

The single run had a noisy first carrier construction (`0.817s`), so a repeat
protocol was run.

Repeat protocol:

- `--generic-lsi-prewarm`
- `--warmup-runs 1`
- `--repeat 3`
- no prepared operator session

Artifact:

- `history/internal_docs/rtdl_goal5020_generic_lsi_prewarm_repeat_top4.json`

```text
prewarm elapsed_sec:            1.040s
median writer_free_hot_sec:     2.386s
median LSI phase:               1.535s
median downstream floor:        0.851s
best writer_free_hot_sec:       2.362s
worst writer_free_hot_sec:      2.602s
lsi_row_count:                  428322
descriptor pair count:          15014
```

Measured rows:

| Run | writer_free_hot | LSI phase | downstream floor |
|---|---:|---:|---:|
| measured 1 | 2.602s | 1.708s | 0.894s |
| measured 2 | 2.362s | 1.516s | 0.846s |
| measured 3 | 2.386s | 1.535s | 0.851s |

This is a real warm-process fresh improvement versus the previous canonical
fast-pack headline (`~4.22s`) and the current same-session no-prewarm probe
(`3.565s`).  It is not a cold CLI improvement if the prewarm time is charged to
a one-shot command.

## Interpretation

What moved:

- generic LSI pipeline compile/setup was moved out of the measured route
  window;
- the route now exposes the remaining per-input LSI workspace cost
  (`grouped_range_ensure` + `scaled_cache_ensure`) and downstream floor.

What did not move:

- cold process / CLI one-shot time;
- distinct-domain per-input workspace cost;
- point-location duplicate canonicalization;
- range build;
- author parity / 10x target.

Current honest state:

- `--generic-lsi-prewarm` is a valid warm-process fresh route option.
- It materially improves the route window in a long-lived process.
- CPU hash duplicate canonicalization is a no-go.
- The next large target is still prepared workspace reuse or GPU-side
  canonicalization/range construction, not more CPU hash or sort micro-work.

## Exit Label

```text
completed_generic_lsi_prewarm_productized__cpu_duplicate_hash_no_go__warm_process_fresh_route_moves
```
