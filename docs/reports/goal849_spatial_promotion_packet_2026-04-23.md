# Goal849: Spatial Prepared-Summary Promotion Packet

Date: 2026-04-23

## Purpose

Package the existing local evidence for the two partial-ready spatial apps so they can enter a future consolidated RTX batch without ambiguity.

## service_coverage_gaps

- Performance class: `optix_traversal_prepared_summary`
- Benchmark readiness: `needs_real_rtx_artifact`
- Current maturity: `rt_core_partial_ready`
- Target maturity: `rt_core_ready`
- Required OptiX mode: `gap_summary_prepared`
- Claim scope: prepared OptiX fixed-radius threshold traversal for coverage-gap compact summaries
- Promotion blocker: local phase-contract and required baseline work are complete, but no real RTX phase artifact has been recorded for this app yet
- Promotion condition: real RTX optix-mode phase artifact must exist and be reviewed before readiness or maturity promotion

Dry-run timings:

- `input_build`: `1.0333023965358734e-05`
- `cpu_reference_total`: `9.325006976723671e-05`

Dry-run result keys:

- `clinic_count`
- `covered_household_count`
- `household_count`
- `uncovered_household_count`
- `uncovered_household_ids`

## event_hotspot_screening

- Performance class: `optix_traversal_prepared_summary`
- Benchmark readiness: `needs_real_rtx_artifact`
- Current maturity: `rt_core_partial_ready`
- Target maturity: `rt_core_ready`
- Required OptiX mode: `count_summary_prepared`
- Claim scope: prepared OptiX fixed-radius count traversal for hotspot compact summaries
- Promotion blocker: local phase-contract and required baseline work are complete, but no real RTX phase artifact has been recorded for this app yet
- Promotion condition: real RTX optix-mode phase artifact must exist and be reviewed before readiness or maturity promotion

Dry-run timings:

- `input_build`: `1.425005029886961e-05`
- `cpu_reference_total`: `0.00016441696789115667`

Dry-run result keys:

- `event_count`
- `hotspot_count`
- `hotspots`

## Boundary

This packet proves local claim-path readiness and completed same-semantics baseline coverage only. It does not promote either app to ready_for_rtx_claim_review and does not authorize a public RTX speedup claim.

