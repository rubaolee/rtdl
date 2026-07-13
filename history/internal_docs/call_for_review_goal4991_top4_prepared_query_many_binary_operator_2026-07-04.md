# Call For Review - Goal4991 Top4 Prepared/Query-Many Binary Operator

Date: 2026-07-04

Reviewer requested: Claude and Antigravity

## Documents To Review

- `history/internal_docs/goal4991_top4_prepared_query_many_binary_operator_result_2026-07-04.md`
- `history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4990_repeat_protocol_top4.json`
- `history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4970_top4_cdb_summary.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

## Context

Goal4990 proved the prepared/query-many repeat protocol on the public County x Soil sample. Goal4991 rebuilds the larger top4 County x Zipcode representative input on the POD and runs the same protocol.

The goal is to verify scale behavior and identify the next real bottleneck without overclaiming fresh one-shot performance or author parity.

## Key Evidence

Top4 input:

```text
top4_county:   441 features, 1,705,027 edges
top4_zipcode: 7,035 features, 9,982,960 edges
```

Repeat protocol result:

```text
warmup writer_free_hot_sec       = 4.411411
measured writer_free_hot_sec     = 2.480488, 2.373019, 2.417124
median writer_free_hot_sec       = 2.41712380386889
median_lsi_phase_sec             = 1.5675766840577126
median_downstream_floor_sec      = 0.8060348182916641
lsi_row_count                    = 428322
descriptor_pair_count            = 15014
lsi_pair_input_device_resident   = true
lsi_pair_host_to_device_copy     = false
```

## Review Questions

1. Does Goal4991 correctly reuse the Goal4990 repeat protocol on the larger top4 input?
2. Is the top4 input provenance sufficient for a representative current-source benchmark?
3. Does the result correctly preserve warmup vs measured boundaries?
4. Is it correct to say this does **not** authorize a fresh one-shot headline?
5. Does structural consistency support the measured repeat evidence?
6. Does the result support saying carrier construction is no longer the largest top4 steady-state floor?
7. Does the result support making `lsi_bounded_exact_pair_id_device_columns_sec` the next target?
8. Should the next goal be an LSI producer decomposition on top4 before any new optimization implementation?

## Requested Verdict Label

```text
approve_goal4991_top4_prepared_query_many_binary_operator__decompose_lsi_next
```
