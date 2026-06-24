# Claude External Review: Phoenix V3 Step 1 RTDBSCAN Runtime-Trunk Probe

Date: 2026-06-22
Reviewer: Claude, independent external reviewer
Packet:

- `docs/reports/phoenix_v3_step1_rtdbscan_runtime_trunk_probe_pod_ab_2026-06-22.md`
- `docs/rebuild/v3/evidence/phoenix_v3_step1_rtdbscan_trunk_probe_20260622_211934/summary.json`
- `docs/reviews/call_for_review_phoenix_v3_step1_rtdbscan_runtime_trunk_probe_2026-06-22.md`

## Verdict

```text
verdict: approve_blocked_not_release
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
external_embedding_or_zero_copy_claim_authorized: false
all_app_pod_spend_authorized: false
```

## Findings

### F1 - Performance mandate not met

Runner vs legacy OptiX grouped-stream geomean is `0.9949x`
(`0.9952x` at 65K and `0.9946x` at 262K). Material Set-A credit
requires a gain sourced from the productized runtime path. This probe is
parity/slightly slower against the correct incumbent, so it cannot count as a
material Set-A performance probe.

Claude's structural explanation: the legacy grouped-stream route already
avoids hot-path host materialization and already has internal device residency
between its phases. The productized runner makes that path auditable and
repeatable, but it does not remove a large cost that the incumbent still paid.

### F2 - Report table needed a legacy-vs-Embree control row

Claude flagged that the table's `runner vs Embree control geomean: 2.927729x`
could be misleading unless paired with the legacy-vs-Embree control baseline.
From `summary.json`, legacy vs Embree is `2.942860x`. Therefore the runner is
not creating the OptiX-over-Embree win; the legacy path already had it. Any
later use of the `2.93x` number as V3 credit would be a measurement-integrity
violation.

### F3 - Step-1 execution credential confirmed

Claude confirmed these as credentialed Step-1 structural facts:

- `runtime_trunk_executes_end_to_end: true` on all runner samples
- `internal_device_residency_between_rtdl_phases: true` on all runner samples
- `hot_path_host_materialization: false` on all runner samples
- `runner_schema: rtdl.v3.phoenix.prepared_execution_session_runner.m3_3`
- signatures matched across samples and variants

These facts are worth keeping, but they are not release evidence.

### F4 - Setup overhead should be tracked later

Claude noted that `runner_route_adapter_batch_call_sec` is large relative to
payload timing, although it is correctly excluded from the measured-repeat
timing under this probe protocol. This is not a blocker for this probe, but it
should be characterized later if Phoenix V3 is positioned as capability or
quality work where first-result latency matters.

## Direct Answers

1. RTDBSCAN proves runtime-trunk execution and internal residency visibility,
   but not material performance. Correct.
2. Runner vs legacy OptiX grouped-stream is the correct incumbent comparison.
   Runner vs Embree is only a control and cannot be counted as Set-A credit.
3. RTDBSCAN should be stopped as the immediate material-probe candidate unless
   a new physical mechanism is introduced, such as fusing fixed-radius query
   and component-union accumulation.
4. RayJoin is the strongest next candidate, with Barnes-Hut second. The next
   probe should first profile whether the legacy path materializes an
   inter-phase intermediate to host.
5. One RTDBSCAN parity result does not yet force capability/quality framing.
   That caveat becomes live if a second Set-A family with a real performance
   source also produces parity.

## Non-Authorization

This review authorizes no Phoenix V3 release, no public speedup wording, no
broad V3-over-V2 wording, no true-zero-copy wording, no external embedding or
external zero-copy wording, no all-app pod spend, and no use of RTDBSCAN
`2.93x vs Embree` as a material Set-A win.

## Authorized Next Work

Claude authorizes recording the RTDBSCAN Step-1 structural credential and
closing RTDBSCAN as the immediate material probe. The next controlled action is
a RayJoin Step-1 probe, but only after a cheap legacy-path host-materialization
check confirms that RayJoin has an actual inter-phase host round-trip that the
runtime trunk can eliminate.
