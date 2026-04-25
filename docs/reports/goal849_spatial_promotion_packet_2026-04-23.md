# Goal849: Spatial Prepared-Summary Promotion Packet

Date: 2026-04-23

## Purpose

Package the existing local evidence for the two partial-ready spatial apps so they can enter a future consolidated RTX batch without ambiguity.

## service_coverage_gaps

- Performance class: `optix_traversal_prepared_summary`
- Benchmark readiness: `ready_for_rtx_claim_review`
- Current maturity: `rt_core_ready`
- Target maturity: `rt_core_ready`
- Required OptiX mode: `gap_summary_prepared`
- Claim scope: prepared OptiX fixed-radius threshold traversal for coverage-gap compact summaries
- Promotion blocker: Goal917 covers the bounded prepared gap-summary path only; row output, nearest-clinic output, and whole-app service-coverage optimization remain outside the claim
- Promotion condition: real RTX optix-mode phase artifact has been reviewed for this bounded path; next step is claim-review packaging, not another per-app pod run

Dry-run timings:

- `input_build`: `9.625102393329144e-06`
- `cpu_reference_total`: `8.450006134808064e-05`

Dry-run result keys:

- `clinic_count`
- `covered_household_count`
- `household_count`
- `uncovered_household_count`
- `uncovered_household_ids`

## event_hotspot_screening

- Performance class: `optix_traversal_prepared_summary`
- Benchmark readiness: `ready_for_rtx_claim_review`
- Current maturity: `rt_core_ready`
- Target maturity: `rt_core_ready`
- Required OptiX mode: `count_summary_prepared`
- Claim scope: prepared OptiX fixed-radius count traversal for hotspot compact summaries
- Promotion blocker: Goal917 and Goal919 cover the bounded prepared count-summary path only; neighbor-row output and whole-app hotspot analytics remain outside the claim
- Promotion condition: real RTX optix-mode phase artifact has been reviewed for this bounded path; next step is claim-review packaging, not another per-app pod run

Dry-run timings:

- `input_build`: `8.958973921835423e-06`
- `cpu_reference_total`: `0.00012258300557732582`

Dry-run result keys:

- `event_count`
- `hotspot_count`
- `hotspots`

## Boundary

This packet tracks the two spatial prepared-summary apps. Service coverage now has a reviewed RTX artifact for its bounded gap-summary path; event hotspot now has a reviewed RTX artifact and same-scale Embree baseline parity for its bounded count-summary path. The packet does not authorize a public RTX speedup claim.

