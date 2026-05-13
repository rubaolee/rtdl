# Handoff: Goal1821 OptiX Device-Descriptor Fail-Closed Review

Please independently review Goal1821:

- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `tests/goal1821_optix_partner_device_descriptor_fail_closed_test.py`
- `docs/reports/goal1821_optix_partner_device_descriptor_fail_closed_2026-05-13.md`
- `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`

Context:

- Goal1819 added `RtdlDevicePointerHandoff` and can observe CUDA pointer
  metadata without authorizing claims.
- Goal1821 adds a complete ray/triangle any-hit device-descriptor packet for
  OptiX and a runner that fails closed unless the future native symbol exists:
  `rtdl_optix_count_ray_primitive_anyhit_2d_device_columns`.
- It must not host-stage silently, must not claim true zero-copy, and must not
  claim direct device handoff is satisfied.

Review questions:

1. Does the packer validate all required CUDA columns and produce
   `device_descriptor_only` metadata?
2. Does the runner fail closed without silently using the host-stage path?
3. Do the report and release gate clearly state the v2.0 blocker remains open?
4. What should the next native OptiX slice prove?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. State explicitly that this is Gemini and distinct from Codex.

Write the review to:

`docs/reviews/goal1822_gemini_review_goal1821_optix_device_descriptor_fail_closed_2026-05-13.md`
