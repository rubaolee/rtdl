# Goal4121 - RT-DBSCAN Explicit Route Choice Advisor

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4121 adds a user-visible route-choice advisor for the RT-DBSCAN benchmark app.

After Goal4117 repaired the repeated direct-status route with explicit `partition_cell_factor` choices, the next risk was usability: users need to know which explicit route/factor to choose without RTDL silently choosing for them.

## What Changed

The benchmark app now exposes:

- `explain_rt_dbscan_explicit_route_choice(dataset, repeated_component_signature=...)`;
- CLI flag `--explain-route-choice`;
- CLI flag `--repeated-component-signature`.

For repeated component-signature workloads, the advisor lists the measured direct-status option first:

| Dataset | Mode | Partner | Tested factor |
| --- | --- | --- | ---: |
| `clustered3d` | `partner_cupy_prepared_direct_status_union_component_signature_3d` | CuPy | 0.25 |
| `road3d` | `partner_cupy_prepared_direct_status_union_component_signature_3d` | CuPy | 0.25 |
| `ngsim_dense` | `partner_cupy_prepared_direct_status_union_component_signature_3d` | CuPy | 0.5 |

For one-shot/default use, the advisor keeps the grouped-stream Numba route as the conservative option.

## Boundary

This is not a dispatcher. The advisor returns options and evidence references only. It does not run a route, select a partner, select a factor, authorize release, authorize public speedup wording, authorize broad RT-core wording, add app-specific engine logic, or claim true zero-copy.
