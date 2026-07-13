# Goal4981 Result: Reversed Side-Order Promotion No-Go

Date: 2026-07-04

## Verdict Requested

`completed_reversed_side_order_promotion_no_go__restore_diagnostic_only`

## Summary

Goal4981 attempted to promote the Goal4980 `1,0` side order for the writer-free binary descriptor route.

The promotion is **not authorized**.

Follow-up control runs showed that the Goal4980 apparent `1,0` win was a process/cache warmup artifact. The first large carrier side-builder call is slow; later carrier side-builder calls are fast. Reversing the side order does not eliminate the first-large-call cost in a fresh process; it only moves that cost to whichever side runs first.

Therefore the code was reverted to keep the default side order as `0,1`. The `--compiled-group-side-order` flag remains available as a diagnostic only.

## Code Decision

Kept:

- `--compiled-group-side-order 0,1|1,0`
- explicit claim boundary:
  - `compiled_group_side_order`
  - `compiled_group_side_order_scope`
  - `paper_text_order_claim_authorized = false`

Reverted:

- default side order remains `0,1`
- no promotion of `1,0` as binary route default

Changed files:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4981_reversed_side_order_binary_route_test.py`

No RTDL core/native files were changed.

## Local Validation

Commands:

```text
py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
$env:PYTHONPATH='src'; py -m unittest tests.goal4981_reversed_side_order_binary_route_test tests.goal4979_grouped_carrier_side_work_metrics_test tests.goal4978_grouped_carrier_decomposition_test tests.goal4977_fast_scaled_point_pack_test
```

Result:

```text
Ran 9 tests in 0.004s
OK
```

## POD Evidence

Artifacts:

- `history/internal_docs/goal4981_reversed_side_order_binary_route_artifacts_2026-07-04/default_side_order_summary.json`
- `history/internal_docs/goal4981_reversed_side_order_binary_route_artifacts_2026-07-04/default_side_order_second_summary.json`
- `history/internal_docs/goal4981_reversed_side_order_binary_route_artifacts_2026-07-04/explicit_side_order_0_1_after_default_summary.json`
- comparison artifacts from Goal4980:
  - `history/internal_docs/goal4980_grouped_carrier_side_order_artifacts_2026-07-04/side_order_0_1_summary.json`
  - `history/internal_docs/goal4980_grouped_carrier_side_order_artifacts_2026-07-04/side_order_1_0_summary.json`

## Control-Run Results

| Run | Side order | Writer-free hot | Downstream floor | Carrier total | side0 builder | side1 builder |
|---|---:|---:|---:|---:|---:|---:|
| Goal4980 first run | `0,1` | 4.251859s | 1.579240s | 0.773479s | 0.692401s | 0.069559s |
| Goal4980 second run | `1,0` | 3.526743s | 0.903088s | 0.104935s | 0.019657s | 0.073979s |
| Goal4981 fresh default | `1,0` | 4.147890s | 1.516779s | 0.724693s | 0.019798s | 0.694081s |
| Goal4981 second default | `1,0` | 3.568428s | 0.915056s | 0.107456s | 0.019954s | 0.076442s |
| Goal4981 after default | `0,1` | 3.533511s | 0.894767s | 0.104763s | 0.023869s | 0.069853s |

## Interpretation

The decisive pattern:

```text
fresh first side-builder call: ~0.69s
later side-builder calls:      ~0.02-0.08s
```

The slow cost attaches to the first large side-builder call in a fresh process, not to side0 specifically and not to side order specifically.

Goal4980's `1,0` result was fast because it was the second full process in the sequence after prior runs had warmed the relevant cache / code / pages. Goal4981's fresh default `1,0` run made side1 slow instead:

```text
Goal4981 fresh 1,0:
  side1 first = 0.694081s
  side0 second = 0.019798s
```

Then subsequent runs were fast regardless of order:

```text
second 1,0 carrier = 0.107456s
later 0,1 carrier  = 0.104763s
```

So the correct conclusion is not "reverse side order wins." The correct conclusion is:

> Carrier side-builder has a first-large-call warmup/cache/page effect. Once warmed, both side orders are fast.

## Structural Consistency

Across the relevant control runs, these anchors match:

- `lsi_row_count`
- `xsect_sorted_counts`
- `vertex_positive_counts`
- `downstream_consumer`
- `scale_bounds`

The no-go is not a correctness failure. It is a performance-causality correction.

## Next Direction

The next useful goal should target the real issue:

```text
explicit carrier side-builder warmup / first-large-call elimination
```

Candidate next goal:

1. Add an explicit app-owned carrier-builder warmup pass that exercises the same Numba side-builder signature before measured hot route.
2. Alternatively, run a side-builder dry-run on small/representative buffers before timed route.
3. Measure whether writer-free hot in a fresh process moves from ~4.15s to ~3.55s without changing side order semantics.
4. Keep the paper-text route separate.

This should be treated as warmup protocol / benchmark harness work unless it can be justified as a real product route for repeated query workloads.

## Claim Boundary

Authorized:

- Side-order reversal is diagnostic only.
- The first-large-call carrier cost is real and should be isolated.
- Do not promote `1,0` as default based on Goal4980 alone.

Not authorized:

- No reversed-side-order default promotion.
- No paper byte-equality claim.
- No author-performance headline.
- No RTDL core promotion.
- No RayJoin-specific native/core primitive.
- No Layer 4 fusion.

## Exit Label

`completed_reversed_side_order_promotion_no_go__restore_diagnostic_only`
