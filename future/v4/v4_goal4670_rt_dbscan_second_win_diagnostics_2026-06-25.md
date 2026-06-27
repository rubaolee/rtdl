# V4 Goal4670 - RTDBSCAN Second-Win Diagnostics

Date: 2026-06-25

Status: focused POD evidence collected; no second true V4 app-level win yet

Decision label:
`rt_dbscan_diagnostics_complete_no_second_true_v4_win_yet`

## Bottom Line

Goal4670 tested whether `rt_dbscan` can become the second independent
app-level V4 performance win after Goal4669 found only one true app win
(`hausdorff_xhd`).

The answer is currently no.

The current true V4 runtime route remains a modest improvement, not a formal
high-performance win:

- default V4 grouped-stream Numba signature: `1.084x` vs V2.14 hot,
  `1.081x` vs V3.0.2 hot in the first diagnostic and `1.079x`/`1.076x`
  in the updated diagnostic;
- direct-side-effect probe: up to `1.116x` vs V2.14 hot, `1.113x` vs V3.0.2
  hot;
- direct-side-effect plus disabled same-root culling: `1.166x` vs V2.14 hot,
  `1.163x` vs V3.0.2 hot;
- formal second-win bar: both ratios must be at least `1.20x`.

Two direct-status rows are extremely fast on this all-predicate fixture, but
they are not counted as true V4 wins because they are historical or
external-proof-required route classes, not new V4 runtime/operator wins.

## Evidence

POD evidence root:

`future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/`

Machine summary:

`future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/summary.json`

Runner:

`scripts/v4_goal4670_rt_dbscan_second_win_diagnostics.py`

Hardware:

- GPU: `NVIDIA RTX A5000`
- Driver: `570.195.03`
- Dataset: `clustered3d`
- Point count: `262144`
- Radius: `3.0`
- Min neighbors: `4`
- Repeat/warmup: `5/1`

## Results

| Variant | Class | Hot sec | V4/V2.14 hot | V4/V3.0.2 hot | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| `v4_default_numba_signature` | true V4 runtime candidate | `1.555727` | `1.079x` | `1.076x` | Below `1.20x`; not a second win. |
| `v4_direct_side_effect_probe` | generic native toggle probe | `1.504056` | `1.116x` | `1.113x` | Slightly better, still below `1.20x`. |
| `v4_direct_side_effect_no_culling_probe` | generic native toggle probe | `1.439977` | `1.166x` | `1.163x` | Best true grouped-union probe so far, still below `1.20x`. |
| `v4_no_same_root_culling_negative_probe` | negative control | `1.784431` | `0.941x` | `0.938x` | Worse; same-root culling remains needed outside the direct-side-effect combination. |
| `v4_blocked_grouped_stream_negative_probe` | negative control | `5.161767` | `0.325x` | `0.324x` | Much worse; blocked grouped-stream stays rejected. |
| `v4_cupy_column_signature_historical_route` | historical partner route | `1.685777` | `0.996x` | `0.993x` | Not a V4 speed win. |
| `v4_measured_all_true_direct_status` | all-predicate explicit route | `0.001184` | `1417.729x` | `1413.801x` | Fast, but condition-specific and not counted as true V4 win. |
| `v4_declared_all_items_direct_status` | external-proof historical route | `0.001243` | `1351.196x` | `1347.453x` | Fast, but requires caller proof and is not a new RT-core V4 win. |

## Interpretation

The real bottleneck for the true V4 route remains the native grouped-union pass:

- default grouped native: `1.532986s`;
- direct-side-effect grouped native: `1.474611s`;
- direct-side-effect plus no-culling grouped native: `1.426273s`;
- CuPy historical route grouped native: `1.544464s`.

The Numba signature work is small (`~0.017s`). The score cannot be moved by
polishing Python-side signature materialization.

The only meaningful RTDBSCAN path to a true second V4 win would be a generic
native grouped-union improvement that reduces the main traversal/union cost by
roughly another `3-4%` beyond the best direct-side-effect/no-culling probe.
Without that, this app should not be used as V4 high-performance evidence.

## Non-Win Rows

The direct-status rows must not be misused.

They show that RTDBSCAN has very fast special contracts when the predicate is
known to be all true. That is a useful capability, but it does not prove formal
V4 high performance because:

- the route is not the same as the current default V4 grouped-stream route;
- the declared variant requires external proof from the caller;
- the route class existed in historical work and cannot be counted as a new V4
  runtime/operator win without a separate V2.14/V3 availability audit;
- `rt_core_accelerated` is false for the declared all-items subpath.

## Decision

Goal4670 does not authorize:

- V4 release;
- formal high-performance V4 wording;
- broad app-level V4 speedup wording;
- using direct-status rows as the second true V4 win;
- automatic route selection;
- app-specific native DBSCAN kernels.

## Next Action

Do one of two things:

1. If staying on RTDBSCAN, inspect and modify the generic native grouped-union
   implementation only. The target is a real `>=1.20x` true V4 row, not a
   `1.11x` wording improvement.
2. If native grouped-union cannot plausibly move another `8-10%`, stop spending
   Goal4670 time on RTDBSCAN and select a different app-level target.

The next target must remain generic-runtime/operator work, not an app-identity
kernel and not release wording.

## Goal-Level Decision Audit

1. Was the decision stupid?

   It would be stupid to count the direct-status rows as V4 performance wins
   just because the numbers are large.

2. What actions would make it stupid?

   Treating an external-proof historical route as a new V4 runtime win, or
   lowering the `1.20x` bar to accept the `1.11x` direct-side-effect probe.

3. Is there another path?

   Yes. Either improve generic native grouped-union enough to clear the frozen
   bar, or move to another app-level target with a credible V4 lever.

4. Can we try a different path to solve the real problem?

   Yes. The real problem is lack of a second independent app-level V4 win. If
   RTDBSCAN cannot provide it, the work must pivot to another fused-operator
   app route instead of manufacturing a claim.
