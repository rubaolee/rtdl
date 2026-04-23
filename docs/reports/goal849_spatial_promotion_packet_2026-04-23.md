# Goal849: Spatial Prepared-Summary Promotion Packet

Date: 2026-04-23

## Purpose

Package the existing local evidence for the two partial-ready spatial apps so they can enter a future consolidated RTX batch without ambiguity.

## service_coverage_gaps

- Performance class: `optix_traversal_prepared_summary`
- Benchmark readiness: `needs_phase_contract`
- Current maturity: `rt_core_partial_ready`
- Target maturity: `rt_core_ready`
- Required OptiX mode: `gap_summary_prepared`
- Claim scope: prepared OptiX fixed-radius threshold traversal for coverage-gap compact summaries
- Promotion blocker: OptiX prepared summary surface exists, but no RTX phase-clean app evidence has been recorded for this app yet
- Promotion condition: real RTX optix-mode phase artifact must exist and be reviewed before readiness or maturity promotion

Dry-run timings:

- `input_build`: `8.541974239051342e-06`
- `cpu_reference_total`: `7.05420970916748e-05`

Dry-run result keys:

- `clinic_count`
- `covered_household_count`
- `household_count`
- `uncovered_household_count`
- `uncovered_household_ids`

## event_hotspot_screening

- Performance class: `optix_traversal_prepared_summary`
- Benchmark readiness: `needs_phase_contract`
- Current maturity: `rt_core_partial_ready`
- Target maturity: `rt_core_ready`
- Required OptiX mode: `count_summary_prepared`
- Claim scope: prepared OptiX fixed-radius count traversal for hotspot compact summaries
- Promotion blocker: OptiX prepared summary surface exists, but no RTX phase-clean app evidence has been recorded for this app yet
- Promotion condition: real RTX optix-mode phase artifact must exist and be reviewed before readiness or maturity promotion

Dry-run timings:

- `input_build`: `1.2125005014240742e-05`
- `cpu_reference_total`: `0.00013229204341769218`

Dry-run result keys:

- `event_count`
- `hotspot_count`
- `hotspots`

## Boundary

This packet proves local claim-path readiness only. It does not promote either app to ready_for_rtx_claim_review and does not authorize a public RTX speedup claim.

