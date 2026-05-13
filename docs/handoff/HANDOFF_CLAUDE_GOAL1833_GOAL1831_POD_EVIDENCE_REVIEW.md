# Claude Task: Review Goal1831 Pod Evidence Update

You are Claude performing an independent review distinct from Codex. Please audit the completed Goal1831 pod evidence and write your review to:

`docs/reviews/goal1833_claude_review_goal1831_pod_evidence_2026-05-13.md`

Review these files:

- `docs/reports/goal1831_optix_ray_column_true_zero_copy_slice_2026-05-13.md`
- `docs/reports/goal1831_optix_ray_column_true_zero_copy_pod_validation.json`
- `tests/goal1831_optix_ray_column_true_zero_copy_slice_test.py`
- `scripts/run_goal1828_optix_device_column_pod_validation.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`

Questions:

1. Does the RTX A4500 pod artifact prove that the narrow ray-column true-zero-copy path executed successfully (`observed_count == expected_count == 1`)?
2. Do the artifact and report correctly avoid whole-primitive true-zero-copy, broad speedup, whole-app, arbitrary partner, package-install, and v2.0 release claims?
3. Is the status `accept-with-boundary` appropriate for Goal1831 after the pod artifact?
4. What still blocks v2.0?

Use only these verdict values:

- `accept`
- `accept-with-boundary`
- `reject`
- `needs-more-evidence`

Expected verdicts:

- Goal1831 pod evidence: likely `accept-with-boundary`
- v2.0 release readiness: `needs-more-evidence`

Please explicitly state that you are Claude and that this is an independent review, not Codex authoring.
