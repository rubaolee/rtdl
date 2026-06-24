# Goal3536 v2.8 vs v2.3 10s Steady-State Protocol

This is an internal measurement packet. It does not authorize release or public speedup wording.

- Target measured query time per side: `10.0` sec
- Scale: `standard`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Summary: `{"geomean_speedup": null, "max_speedup": null, "median_speedup": null, "min_speedup": null, "observed_target_miss_count": 1, "observed_target_misses": [{"case_id": "rt_dbscan_optix_grouped_stream", "v23_observed_measured_sec": 0.0, "v23_target_met_by_observed_sum": null, "v28_observed_measured_sec": 0.0, "v28_target_met_by_observed_sum": null}], "ratio_count": 0, "row_count": 1, "target_met_by_observed_pair_count": 0, "target_met_by_plan_pair_count": 1}`

## Comparison Rows

| App | Case | v2.3 sec | v2.8 sec | v2.8/v2.3 | Target plan met? | Target observed met? |
| --- | --- | ---: | ---: | ---: | --- | --- |
| rt_dbscan | rt_dbscan_optix_grouped_stream |  |  |  | True/True | None/None |

## Boundary

- A row is final 10s evidence only when both sides report `target_met_by_plan = true` and the execution succeeds.
- Rows without a repeat knob are reported as partial diagnostics when wrapper repetition would exceed the wall-time guard.
- Setup, packing, and validation are kept out of the primary hot-query metric unless the underlying app exposes only a total metric.
