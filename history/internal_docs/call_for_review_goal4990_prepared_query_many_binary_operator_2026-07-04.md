# Call For Review - Goal4990 Prepared/Query-Many Binary Operator Repeat Protocol

Date: 2026-07-04

Reviewer requested: Claude and Antigravity

## Documents To Review

- `history/internal_docs/goal4990_prepared_query_many_binary_operator_result_2026-07-04.md`
- `history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4990_repeat_protocol_public_sample.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4990_binary_repeat_protocol_test.py`

## Context

Goal4988 removed the exact/bounded LSI pair-id device-column to NumPy round trip before Numba reprojection. The next question was whether the remaining public-sample cost was an unavoidable per-query floor or first-use setup / first real working-set cost.

Goal4990 adds a first-class same-process repeat protocol:

```bash
--warmup-runs N
--repeat M
```

This is explicitly a prepared/query-many diagnostic for the writer-free binary route. It must be reported beside fresh one-shot numbers, not instead of them.

## Key Evidence

POD public County x Soil run:

```text
warmup writer_free_hot_sec      = 1.645118
measured writer_free_hot_sec    = 0.122847, 0.100514, 0.128475
median writer_free_hot_sec      = 0.12284692749381065
median_lsi_phase_sec            = 0.06355392746627331
median_downstream_floor_sec     = 0.059293000027537346
lsi_row_count                   = 20860
descriptor_pair_count           = 28815
lsi_pair_input_device_resident  = true
lsi_pair_host_to_device_copy    = false
```

Warmup rows remain visible in the artifact and are excluded from measured medians.

## Review Questions

1. Does Goal4990 correctly implement a repeat/warmup protocol without changing the default one-shot route?
2. Is it correct to classify the new `~0.123s` result as same-process prepared/query-many evidence, not a fresh one-shot headline?
3. Does the artifact preserve the warmup row instead of hiding it?
4. Does the structural evidence (`lsi_row_count = 20860`, `descriptor_pair_count = 28815`) support saying measured repeats are structurally consistent with the warmup route?
5. Does the evidence support saying carrier construction is not the steady-state floor on this public sample?
6. Does the device-column metadata continue to support the Goal4988 claim that LSI pair ids feed Numba without a pair-id NumPy bounce?
7. Is the report careful enough to avoid author parity, paper-text, warm-only, or full device-resident overclaims?
8. Should the next goal repeat this protocol on the larger top4 County x Zipcode representative input before revising the v2.14.3 performance matrix?

## Requested Verdict Label

```text
approve_goal4990_prepared_query_many_binary_operator_public_sample
```
