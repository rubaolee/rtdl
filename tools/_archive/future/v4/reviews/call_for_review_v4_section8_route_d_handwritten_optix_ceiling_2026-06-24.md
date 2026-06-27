# Call For Review: V4 Section 8 Route D Hand-Written OptiX Ceiling

Date: 2026-06-24
Requested verdict labels:

- `accept_route_d_obtained_product_boundary_gap_continue`
- `reject_route_d_invalid_or_not_independent`
- `accept_route_d_but_stop_v4_performance_path`

## Review Packet

- Protocol: `future/v4/rtdl_v4_0_section8_route_d_handwritten_optix_protocol_2026-06-24.md`
- Report: `future/v4/evidence/v4_section8_route_d_handwritten_optix_ceiling_report_2026-06-24.md`
- Route D result: `future/v4/evidence/v4_section8_route_d_result_2026-06-24.json`
- Direct RTDL scalar result: `future/v4/evidence/v4_section8_rtdl_direct_prepared_scalar_hot_path_result_2026-06-24.json`
- Prior prepared summary result: `future/v4/evidence/v4_section8_prepared_hot_path_result_2026-06-24.json`
- Reference source: `future/v4/reference/route_d_fixed_radius_count_threshold_optix.cpp`
- Harness: `scripts/v4_section8_route_d_reference_validation.py`
- Local test: `tests/v4_section8_route_d_reference_validation_test.py`

## Questions

1. Does the Route D reference satisfy the independence contract?
2. Is the Route D correctness evidence sufficient for the Section 8 fixture?
3. Is the timing boundary clear enough for a ceiling reference?
4. Does the Route D result authorize near-hand-written OptiX wording for the
   current RTDL product path?
5. Is the report right that V4's next blocker is product-boundary overhead
   rather than the RT-core fused kernel?
6. Should V4 continue by building the fixed-radius array/device-array front door
   before adding any second primitive?
7. Are any release or broad speedup claims authorized?

## Codex Proposed Verdict

`accept_route_d_obtained_product_boundary_gap_continue`

Route D is now acquired and independent, but it falsifies a stronger claim:
the current RTDL Python-facing route is not near the hand-written OptiX ceiling.
The next V4 engineering target should therefore be the array/device-array front
door for this same primitive, not a second primitive and not a release.

## Non-Authorization

This packet does not authorize V4 release, broad V4 speedup wording, Tier-3
callback claims, app-specific native engine claims, or near-hand-written OptiX
wording for the current RTDL product path.
