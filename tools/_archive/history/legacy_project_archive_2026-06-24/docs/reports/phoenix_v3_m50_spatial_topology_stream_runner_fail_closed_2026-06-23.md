# Phoenix V3 M50 Spatial Topology-Stream Runner Fail-Closed Gate

Date: 2026-06-23

Status: `m50_spatial_topology_runner_fail_closed_not_pod_not_release`

M50 hardens the existing Spatial/RayJoin topology-stream M3 POD runner after
M49 refreshed the blocker queue. M49 says Spatial/RayJoin may continue only as
generic topology-stream residency / full-M3 accounting work, not route tuning,
not paid POD, and not all-app. The runner therefore must fail closed.

## Change

The CLI entry point in
`scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py` now:

- defaults to a dry-run packet and does not call the RayJoin workload;
- requires `--execute` for any real run;
- requires the explicit token
  `M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED` when `--execute` is used;
- records all claim/authorization flags as false in both dry-run and real-run
  packets;
- keeps M7 promotion at zero.

This means historical commands that only pass `--output` now produce a dry-run
planning packet instead of spending POD.

## Why This Was Needed

M49 correctly blocked RayJoin route tuning, but the old runner could still be
invoked directly from the CLI and start the workload. That mismatch creates a
process bug: the docs say no POD, while the script still had a real-run default.

M50 fixes the script so the code enforces the current review boundary.

## Current Validation

Focused validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test tests.v3_phoenix_m49_current_blocker_queue_gate_test
Ran 7 tests
OK
```

Compile check:

```text
PYTHONPATH=src;. py -3 -m py_compile scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py
OK
```

Full rebuild validation after registering the M50 gate:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 123
Ran 636 tests in 75.939s
OK
```

This is local contract/gate evidence only. It is not POD evidence, release
authorization, all-app authorization, or a public performance claim.

## Non-Authorization

This report does not authorize:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no whole-app speedup claim
- no paper reproduction claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim

## Goal-Level Decision Audit

Decision: make the Spatial/RayJoin topology-stream M3 runner dry-run by default
and require an explicit reviewed execution token before any real run.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   leaving a real-run default in place after M49 said this path is not
   authorized for route tuning or POD.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Documentation alone could warn users not to run it, but that leaves the
   dangerous behavior in code.
4. Can I now try a different path that actually solves the problem? Yes. The
   runner itself now enforces dry-run by default, so future work must obtain
   explicit review authorization before it can execute.
