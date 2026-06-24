# Goal1117 Robot Profiler Provenance

Date: 2026-04-29

## Verdict

ACCEPT for local pre-cloud hardening. The Robot OptiX phase profiler now records
the same provenance fields needed by the current-source RTX rerun packet:
`source_commit`, `generated_at`, and `host`.

## Why This Matters

Goal1116 runs Facility/Barnes through `goal887_prepared_decision_phase_profiler.py`,
which already records source and host provenance. Robot runs through
`goal760_optix_robot_pose_flags_phase_profiler.py`, which previously omitted
that provenance. That omission would make Robot artifacts weaker for
same-source comparison and public wording review.

## Changes

- Added `source_commit`, `generated_at`, and `host` to Robot profiler payloads.
- Reused the same precedence as other profilers:
  - `RTDL_SOURCE_COMMIT`
  - `git rev-parse HEAD`
  - `.rtdl_source_commit`
- Updated Goal760 tests to require the provenance fields.

## Verification

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal760_optix_robot_pose_flags_phase_profiler_test tests.goal1116_current_source_rtx_rerun_packet_test -v
```

Result: 8 tests OK.

Command:

```text
python3 -m py_compile scripts/goal760_optix_robot_pose_flags_phase_profiler.py scripts/goal1116_current_source_rtx_rerun_packet.py
git diff --check
```

Result: OK.

## Boundary

This goal does not change Robot execution semantics, does not run cloud, does
not authorize release, and does not authorize any public RTX speedup claim.
