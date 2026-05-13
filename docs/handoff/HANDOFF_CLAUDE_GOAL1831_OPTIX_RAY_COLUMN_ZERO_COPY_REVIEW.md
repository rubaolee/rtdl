# Claude Task: Review Goal1831 OptiX Ray-Column True Zero-Copy Slice

You are Claude performing an independent review distinct from Codex. Please audit Goal1831 and write your review to:

`docs/reviews/goal1832_claude_review_goal1831_optix_ray_column_zero_copy_2026-05-13.md`

Review these files:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `scripts/run_goal1828_optix_device_column_pod_validation.py`
- `tests/goal1823_optix_partner_device_ray_columns_partial_abi_test.py`
- `tests/goal1828_optix_device_column_pod_validation_packet_test.py`
- `tests/goal1831_optix_ray_column_true_zero_copy_slice_test.py`
- `docs/reports/goal1831_optix_ray_column_true_zero_copy_slice_2026-05-13.md`

Questions:

1. Does the native OptiX device-ray path actually remove ray-side GPU repacking by launching a specialized pipeline that reads partner-owned `ids/ox/oy/dx/dy/tmax` columns directly?
2. Is the claim boundary correct: ray-column true zero-copy may be authorized after pod execution, while whole-primitive true zero-copy remains blocked because triangle scene preparation still constructs RTDL-owned layouts/GAS inputs?
3. Are the Python metadata fields and tests sufficient to prevent overclaiming?
4. What evidence is still required before this can count toward v2.0 release readiness?

Use only these verdict values:

- `accept`
- `accept-with-boundary`
- `reject`
- `needs-more-evidence`

Expected verdicts:

- Goal1831 static/local implementation: likely `accept-with-boundary`
- Goal1831 pod/hardware evidence: likely `needs-more-evidence` until an RTX pod artifact exists
- v2.0 release readiness: `needs-more-evidence`

Please explicitly state that you are Claude and that this is an independent review, not Codex authoring.
