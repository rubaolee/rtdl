# Goal3195: Compact Grouped-Count Timing Probe

Date: 2026-06-03

## Purpose

Goal3195 is an internal timing probe for the Goal3193 compact resident
grouped-count columns.

The question was narrow: when the desired result is per-left segment hit counts,
how much host-row materialization can the compact resident grouped-count path
avoid compared with the exact row path?

This is not a public speedup claim, not a RayJoin paper reproduction claim, and
not a release gate.

## Setup

Pod artifact:

- `docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.json`
- Commit under test: `3483020a`
- GPU pod used the current OptiX build from the Goal3193 chain.
- Workload: authored all-crossing 2D segment pairs.
- Scales: `512 x 512`, `1024 x 1024`, `2048 x 2048`.

The exact path ran:

- `prepared.run(left_segments)`
- Python `Counter(left_id)` over exact host rows.

The compact path ran:

- `prepared.candidate_device_columns(...)`
- `grouped_count_by_left_id_compact_device_columns(group_capacity=n)`
- CuPy validation copy of compact `group_key[]` and `count[]` only.

The compact resident grouped-count columns were validated against the exact row
oracle at every scale.

## Results

| Scale | Exact Host Rows (s) | Compact Resident Columns + Validation Copy (s) | Internal Ratio |
| --- | ---: | ---: | ---: |
| 512 x 512 | 0.3426668830215931 | 0.004587551578879356 | 0.013387787983556826 |
| 1024 x 1024 | 1.4432955030351877 | 0.011956045404076576 | 0.008283851351946661 |
| 2048 x 2048 | 5.909632220864296 | 0.01623670384287834 | 0.002747498192113162 |

At `2048 x 2048`, the exact row path materialized 4,194,304 exact host rows.
The compact path kept the grouped result as 2,048 compact resident count rows
and copied only the compact validation columns back to host for this probe.

## Interpretation

The result is exactly the design signal we wanted:

- exact witness rows are expensive when the app only needs grouped counts,
- compact resident grouped-count columns avoid the large host-row surface,
- the new primitive path gets more valuable as the pair stream grows,
- the current result is still a primitive-path timing probe, not a public
  benchmark claim.

## Boundaries

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `rayjoin_paper_reproduction_claim_authorized: False`

This probe does not prove:

- final Spatial RayJoin semantics,
- broad RayJoin paper parity,
- whole-app speedup,
- true zero-copy,
- release readiness.
