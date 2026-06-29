# Goal4806 V4+Numba Measurement Import Gate

Date: 2026-06-28

## Status

Local work advanced the RayJoin Section 5.7 V4+Numba path from "planner-only" to
"POD measurement import can be validated and selected fail-closed."

This is not performance evidence. It is the local gate needed before a real
RT-core POD run can be trusted.

## What Changed

- Added a measured-candidate JSON schema:
  `rtdl.v4.rayjoin.section57_numba_measured_candidates.v1`.
- The V4+Numba planner now imports measured candidates only when all of these
  are true:
  - pair id and plan id match an existing candidate,
  - candidate is already ready for measurement,
  - correctness status is `pass`,
  - measured total time is positive,
  - measurement source is `pod_runtime`,
  - topology/geometry hash match is confirmed,
  - device-column route is confirmed,
  - host materialization in the hot path is false.
- Invalid rows are rejected with explicit reasons and do not participate in
  `fastest_valid` selection.
- The public RayJoin Section 5.7 CLI, overlay matrix runner, POD runbook, and
  setup preflight can pass the measured-candidate file through the full chain.
- The setup preflight now prints a next runbook command that enables the
  Section 5.7 device-column route for measurement.

## Verification

Windows local tests:

```text
py -3 -m unittest tests.v4_goal4806_rayjoin_section57_pod_setup_test \
  tests.v4_goal4806_rayjoin_section57_pod_runbook_test \
  tests.v4_rayjoin_section57_public_entry_test \
  tests.v4_goal4806_rayjoin_numba_auto_planner_test \
  tests.goal4374_rayjoin_exact_paper_suite_test \
  tests.v4_goal4640_public_docs_cleanup_test

Ran 55 tests in 109.011s
OK
```

Public-surface leak scan:

```text
rg -n "Goal4806|goal4806|Antigravity|Claude|Gemini|review debt|parity/control" \
  README.md docs tutorials examples scripts/rayjoin_section57_pod_setup.py \
  scripts/rayjoin_section57_pod_runbook.py -g "*.md" -g "*.py"
```

Result: no matches.

## POD Boundary

The remaining performance work requires an NVIDIA RT-core POD with:

- exact RayJoin Section 5.7 CDB inputs for all 8 overlay pairs,
- RayJoin author binaries (`query_exec`, `polyover_exec`),
- rebuilt RTDL OptiX backend with current device-column symbols,
- Numba CUDA available,
- a generated measured-candidate file using the schema above.

Until that POD run exists, the V4+Numba row must remain a candidate/planning
surface, not a performance or paper-reproduction claim.
