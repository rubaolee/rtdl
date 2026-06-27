# Goal1612 v1.6.3 Backend Prepared Host-Output Bridge Foundation

Date: 2026-05-09

## Verdict

Goal1612 starts the `v1.6.3` backend bridge for prepared host-output
measurement.

The deliverable is a source-tree runner that uses the Goal1610/Goal1611
phase/copy schema for:

- `fake_native`, always runnable for local regression coverage;
- `embree`, when a local Embree backend library is available;
- `optix`, when a local OptiX backend library is available.

This is backend-readiness evidence, not public performance evidence.

## Files

- script:
  `scripts/goal1612_v1_6_3_backend_prepared_host_output_bridge.py`
- test:
  `tests/goal1612_v1_6_3_backend_prepared_host_output_bridge_test.py`
- default artifact:
  `docs/reports/goal1612_v1_6_3_backend_prepared_host_output_bridge_2026-05-09.json`

## Acceptance Rule

The default package requires only `fake_native`. Real backends may skip locally
when their native libraries are unavailable. A skipped required backend makes
the package not accepted, and an unexpected backend error is recorded as a
`fail` record.

This lets Windows, macOS, Linux, and pods use the same runner without hiding
backend availability problems.

## Local Scope

The local Windows artifact may include real Embree evidence if the Windows
Embree backend loads successfully. OptiX may skip on Windows when
`librtdl_optix` is not built. That skip is not a failure unless OptiX is listed
as required for the run.

## Claim Boundary

Goal1612 does not authorize:

- performance claims;
- public speedup wording;
- whole-app speedup wording;
- broad RTX/GPU wording;
- true zero-copy wording;
- stable `COLLECT_K_BOUNDED` promotion;
- partner tensor handoff claims;
- package-install claims;
- release tags or release action.

## Next Step

Run this bridge on Linux and future NVIDIA pods with `--required-backends`
matching the intended evidence scope. Keep timing diagnostic-only until
separately reviewed backend evidence supports narrower wording.
