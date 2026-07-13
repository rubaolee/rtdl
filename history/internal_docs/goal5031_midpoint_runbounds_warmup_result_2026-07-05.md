# Goal5031 Midpoint / Run-Bounds Warmup Result

Date: 2026-07-05

## Purpose

Goal5030 reduced device-carrier first-batch cost from `1.628664s` to `0.643663s`, but the first batch still had visible first-call costs in:

- midpoint device-query point generation;
- device run-bound generation;
- descriptor consumer / carrier construction.

Goal5031 extends the tiny dummy CUDA warmup to cover:

- `_compute_run_bounds_device(...)`;
- `_midpoint_device_query_points_kernel(...)`.

This is still app-layer warmup only. It does not replay top4 query batches and does not change RTDL core/native semantics.

## Artifacts

- `history/internal_docs/rtdl_goal5031_query6_device_carrier_midpoint_runbounds_warmup_top4.json`
- `history/internal_docs/rtdl_goal5031_query6_cpu_carrier_current_control_top4.json`

## Regime

Same regime as Goals5027-5030:

- top4 County x Zipcode;
- six distinct chain-contiguous full-overlay query batches;
- prepared LSI base session;
- writer-free binary descriptor route;
- no paper-text output;
- no cold CLI claim;
- no author-performance denominator.

## Result

Structural anchors remain stable:

- total LSI rows across six batches: `428322`;
- first-batch LSI rows: `127926`;
- descriptor pair counts match the same sorted set across routes.

### Body Time Matrix

| Route | First batch | Median | Best | Worst | Six-batch sum | Later-batch sum | Later-batch median |
|---|---:|---:|---:|---:|---:|---:|---:|
| Historical Goal5027 CPU carrier | 0.201693s | 0.170494s | 0.143194s | 0.201693s | 1.034264s | 0.832571s | 0.168883s |
| Current CPU-carrier control | 1.031112s | 0.153969s | 0.132356s | 1.031112s | 1.770692s | 0.739580s | 0.153956s |
| Goal5030 device carrier | 0.643663s | 0.140243s | 0.118276s | 0.643663s | 1.318018s | 0.674355s | 0.139702s |
| Goal5031 device carrier | 0.382333s | 0.134121s | 0.115801s | 0.382333s | 1.039078s | 0.656745s | 0.133086s |

## Interpretation

Goal5031 made device-carrier competitive.

Compared to Goal5030:

- first batch improves from `0.643663s` to `0.382333s`;
- six-batch sum improves from `1.318018s` to `1.039078s`;
- later-batch sum improves from `0.674355s` to `0.656745s`.

Compared to the contemporaneous CPU-carrier control:

- device-carrier wins six-batch sum: `1.039078s` vs `1.770692s`;
- device-carrier wins later-batch sum: `0.656745s` vs `0.739580s`;
- device-carrier wins median: `0.134121s` vs `0.153969s`.

Compared to the older best CPU-carrier artifact:

- device-carrier is effectively at parity: `1.039078s` vs `1.034264s`;
- device-carrier still wins later-batch sum: `0.656745s` vs `0.832571s`;
- CPU-carrier older artifact still has a smaller first batch: `0.201693s` vs `0.382333s`.

So the honest conclusion is:

> Device-carrier is no longer a loser. It has reached parity / candidate-default territory for this prepared query-batch regime, but the default switch needs an N-run stability matrix because CPU first-batch behavior is variable across artifacts.

## Remaining Work

Before making device-carrier the default:

1. Run an N-run matrix on the same POD for CPU-carrier and device-carrier under the same code and same regime.
2. Report median six-batch sum, first batch, later-batch sum, and structural anchors.
3. Switch default only if device-carrier wins the N-run matrix or if product policy explicitly favors the steadier later-batch route.

## Claim Boundary

This does not authorize:

- cold CLI one-shot speedup;
- paper-text route speedup;
- author parity;
- 10x;
- broad zero-copy claims;
- using historical best-only comparisons as a default-switch proof.

It authorizes:

- saying the device-carrier route has reached parity / candidate-default status for the prepared LSI base-session query-batch regime;
- running the N-run default-decision matrix next.

## Exit Label

`completed_midpoint_runbounds_warmup__device_carrier_at_parity_pending_n_run_default_gate`
