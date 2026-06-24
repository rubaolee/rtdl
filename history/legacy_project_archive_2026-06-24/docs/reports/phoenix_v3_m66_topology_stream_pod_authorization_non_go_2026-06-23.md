# Phoenix V3 M66 Topology-Stream POD Authorization Non-Go

Status:
`m66_topology_stream_pod_authorization_rejected_continue_barnes_hut_pre_audit_no_pod_no_release`

M66 started as a candidate no-execution authorization packet for another
topology-stream focused POD run after M65. After rereading the existing Step-2
RayJoin evidence, the correct decision is **not** to authorize a new RayJoin
topology-stream POD run.

## What Changed Locally

The topology-stream M3 POD runner was hardened so any future reviewed run is
fail-closed:

- Authorization token updated to:
  `M66_SOURCE_SIGNATURE_GATED_TOPOLOGY_STREAM_M3_POD_AUTHORIZED`
- `--run-preflight` added.
- `current_topology_stream_source_signature` preflight added.
- Current preflight tests added:
  - `tests.v3_phoenix_prepared_execution_session_runner_test`
  - `tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test`
  - `tests.v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test`
  - `tests.v3_phoenix_m65_topology_stream_step3_audit_negative_hardening_gate_test`
- `--execute` now runs preflight before samples.
- If preflight fails, the runner emits `STATUS_FAILED` and does not call the
  workload.

## Local Validation

Focused runner tests passed:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test
Ran 7 tests
OK
```

Source-signature check passed:

```text
failed: []
```

## Why No New RayJoin Topology-Stream POD Run Is Authorized

The same candidate shape already has serious focused POD evidence:

- Report:
  `docs/reports/phoenix_v3_step2_rayjoin_point_location_runner_pod_ab_2026-06-22.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_step2_rayjoin_point_location_runner_review_2026-06-22.md`

That run used the serious public CDB county dataset, compared the productized
runner against the correct incumbent OptiX route, and reached a structural-only
no-go:

| Metric | Result |
| --- | ---: |
| Runner vs legacy hot query | `0.973465x` |
| Runner vs legacy total repeat | `0.973754x` |
| Runner vs legacy process wall | `0.794180x` |

The review diagnosis is still controlling: this PIP scalar-count wrapper calls
the same native executor as the legacy route, and the incumbent already removed
the host-download phase that the runner could otherwise eliminate. It is
therefore a structural runner credential, not a material V3 performance source.

## Decision

Do not spend POD on another RayJoin PIP/topology-stream scalar-count wrapper
run unless a new design first proves a real multi-phase physical cost that the
runner can remove.

The next runtime-trunk work should follow the existing Claude recommendation:
Barnes-Hut frontier/vector-accumulation pre-audit, starting locally. The
pre-audit must answer whether the incumbent has a non-zero phase the runner can
compress before any focused POD authorization is requested.

## Goal-Level Decision Audit

Decision: reject the initial M66 RayJoin topology-stream POD authorization path
and redirect to Barnes-Hut pre-audit.

1. Was I foolish? Partly, but corrected before POD. Creating M66 as a possible
   topology-stream POD authorization before rereading the 2026-06-22 RayJoin
   no-go evidence risked repeating work.
2. If yes, what actions made the decision foolish? The risky action was
   extrapolating from M65 local audit hardening to a new POD run, even though
   prior focused evidence already showed this RayJoin wrapper has no material
   performance source.
3. Was there another path? Yes: reread current status and prior focused POD
   reports before drafting authorization. That is now the controlling path.
4. Can I now try a different path that actually solves the problem? Yes. Keep
   the runner safety hardening, record no authorization for this repeat, and
   redirect to a local Barnes-Hut phase-structure pre-audit.

## Non-Authorization

This M66 packet does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- focused POD spend
- public speedup wording
- broad V3-over-V2 claim
- whole-app speedup claim
- paper reproduction claim
- RTDL-beats-RayJoin claim
- true-zero-copy claim
- future-version host integration work
- external device-buffer interop claim
- low-level host interface work
- watch-row closure
