# Claude Review: Phoenix V3 RTDBSCAN Repeated Runner Route M3.4

Date: 2026-06-22
Reviewer: Claude
Packet: `docs/reviews/call_for_review_phoenix_v3_rtdbscan_repeated_runner_route_m3_4_2026-06-22.md`

## Verdict

```text
approve_route_contract_not_release
```

Explicit claim boundary declarations:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_rerun_authorized: false
focused_m3_4_pod_ab_authorized: true
```

## Review Summary

Claude approved M3.4 as correct local route-contract wiring. The route now calls
`rt.run_radius_graph_component_signature_3d_prepared_session(...)` once with:

```text
warmup_count=warmup
measured_repeat_count=repeat - warmup
retain_repeat_outputs=True
```

Claude found no RTDBSCAN-specific native logic, no DBSCAN ABI, and no hidden
app-specific shortcut. The route remains based on the generic primitive:

```text
fixed_radius_graph_component_signature_3d
```

## Timing / Accounting Notes From Review

Claude judged the timing fields acceptable for focused A/B, with one reporting
requirement:

```text
runner elapsed_override = median(measured_repeat_seconds[i] + column_signature_sec[i])
legacy elapsed_override = median(perf_counter window including native call + signature)
```

These are comparable, but the focused A/B report must state this explicitly.

Claude also noted that the legacy non-runner comparison path is the existing
`else` branch using:

```text
rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d
```

Because the current mode guard routes the Numba column-signature mode through
the runner, the focused A/B must compare two code states or otherwise force the
legacy non-runner branch intentionally and document that.

## Authorization Boundary

Claude authorizes only a focused M3.4 same-pod A/B:

```text
focused_m3_4_pod_ab_authorized: true
```

This does not authorize:

```text
release
public speedup wording
broad V3-over-V2 wording
full all-app pod rerun
second Set-A material win before measurement
```

## Stop / Redirect Rule

If focused M3.4 A/B is below:

```text
runner_vs_legacy < 0.98x
```

then the RTDBSCAN thread should stop and redirect to AABB generalization or
typed continuation.

For material Set-A candidacy, the relevant bar remains:

```text
runner_vs_legacy >= 1.15x
```
