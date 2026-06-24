# Goal861 Spatial Required Baseline Collection

Date: 2026-04-23

## Purpose

Goal861 records the first successful local collection of the required
same-semantics baseline artifacts for the two spatial prepared-summary apps:

- `service_coverage_gaps`
- `event_hotspot_screening`

This goal is the operational follow-through on Goal859 and Goal860.

## Collected Artifacts

- `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_cpu_oracle_summary_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_embree_summary_path_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_cpu_oracle_summary_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_embree_summary_path_2026-04-23.json`

Collected scale:

- `service_coverage_gaps`
  - `copies: 200`
  - `iterations: 3`
- `event_hotspot_screening`
  - `copies: 2000`
  - `iterations: 3`

This is allowed because both Goal835 rows have `scale: null`; the contract
requires same semantics and phase separation, not a single fixed local scale.

## Gate Result

Goal860 after collection:

- status: `needs_real_rtx_artifact`
- required valid artifacts: `4`
- required missing artifacts: `0`
- required invalid artifacts: `0`

Generated gate outputs:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.generated.md`

## Interpretation

This changes the blocker classification for both apps:

- previous blocker: missing required local baselines
- current blocker: missing real RTX phase artifact

So the next requirement is no longer more local baseline tooling. It is
collection of:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal811_service_coverage_rtx.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal811_event_hotspot_rtx.json`

from a real OptiX-capable RTX host.

## Boundary

This goal does not promote either app into active RTX claim review by itself.
It only proves that the required local baseline side is complete.

Optional SciPy baseline artifacts remain missing and non-blocking.

## Verification

Collected artifacts were checked through:

```text
PYTHONPATH=src:. python3 scripts/goal860_spatial_partial_ready_gate.py \
  --output-json docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.json \
  --output-md docs/reports/goal860_spatial_partial_ready_gate_2026-04-23.generated.md
```

Result:

```text
Status: `needs_real_rtx_artifact`
required valid artifacts: `4`
required missing artifacts: `0`
required invalid artifacts: `0`
```

## Verdict

Goal861 is complete. The spatial prepared-summary pair is now baseline-complete
locally and is blocked only on real RTX artifact collection.
