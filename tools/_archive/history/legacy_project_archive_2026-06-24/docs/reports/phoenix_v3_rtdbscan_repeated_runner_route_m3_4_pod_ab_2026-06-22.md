# Phoenix V3 RTDBSCAN Repeated Runner Route M3.4 POD A/B

Date: 2026-06-22
Status: `m3_4_rtdbscan_repeated_runner_parity_not_material_not_release`
Scope: Phoenix V3 generic runtime evidence only.

## Summary

M3.4 completed the focused same-RT-hardware pod A/B authorized by Claude for
the RTDBSCAN component-signature repeated runner route.

Evidence directory:

```text
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_4_pod_ab_20260622_204719
```

Remote source:

```text
/root/rtdl_v3_rebuild_20260620/phoenix_v3_rtdbscan_m3_4_pod_ab_20260622_204719
```

Hardware:

```text
NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
```

Result:

```text
geomean_runner_vs_legacy_speedup: 0.997557675600175
geomean_runner_vs_embree_speedup: 2.941644953697829
legacy_parity_recovered: true
material_set_a_candidate: false
runner_metadata_present_all_runner_samples: true
runner_repeated_execution_all_runner_samples: true
all_claim_flags_false: true
```

Interpretation:

```text
M3.4 proves that the repeated runner route can preserve parity with the
incumbent legacy OptiX route, but it does not produce a material Set-A win.
RTDBSCAN should stop as the current candidate for the second productized-path
material probe.
```

## Protocol

The focused A/B compared three variants:

```text
legacy_grouped_stream_numba_column_signature
runner_grouped_stream_numba_column_signature
embree_core_flags_numba_prepared_grid_column_signature
```

Run parameters:

```text
dataset: clustered3d
point_counts: 65536, 262144
repeat: 7
warmup: 2
samples_per_variant_per_scale: 3
```

Measurement note required by Claude:

```text
runner elapsed_override = median(measured_repeat_seconds[i] + column_signature_sec[i])
legacy elapsed_override = median(perf_counter window including native call + signature)
```

The relevant incumbent is the legacy OptiX grouped-stream path, not Embree.

## Harness Fix

The first attempt failed before measurement because the generated legacy app
was placed in the evidence output directory and could not discover repo root
from `Path(__file__).parents`.

Failed harness attempt:

```text
remote_dir: /root/rtdl_v3_rebuild_20260620/phoenix_v3_rtdbscan_m3_4_pod_ab_20260622_204539
failure: StopIteration while discovering ROOT
```

Fix:

```text
scripts/v3_phoenix_rtdbscan_runner_m3_4_pod_ab.py
```

The generated legacy app now keeps the legacy non-runner branch but binds
`ROOT` to the explicit repo root so the generated app remains auditable in the
evidence directory.

This was a harness fix only. It does not affect runner implementation or
performance classification.

## Validation Before Pod Run

Remote focused tests passed on the pod after exact file sync:

```text
PYTHONPATH=src:. python -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_rtdbscan_component_signature_optimization_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test

Ran 18 tests
OK
```

Remote script syntax check:

```text
python -m py_compile scripts/v3_phoenix_rtdbscan_runner_m3_4_pod_ab.py
remote_py_compile_ok
```

## Scale Results

| Point Count | Legacy OptiX Median sec | Runner OptiX Median sec | Embree Control Median sec | Runner vs Legacy | Runner vs Embree |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.095824532 | 0.095725194 | 0.389886409 | 1.001x | 4.073x |
| 262,144 | 1.262692161 | 1.270199418 | 2.698612787 | 0.994x | 2.125x |

Geomean:

```text
runner_vs_legacy: 0.997557675600175
runner_vs_embree: 2.941644953697829
```

## Classification

The prior stop/redirect rule was:

```text
runner_vs_legacy >= 1.15x: material Set-A candidate
runner_vs_legacy >= 0.98x and < 1.15x: parity-preserving route progress only
runner_vs_legacy < 0.98x: stop as regression and redirect
```

M3.4 lands in the middle bucket:

```text
parity-preserving route progress only
```

Therefore:

```text
second_material_set_a_probe_obtained: false
focused_material_productized_probe_count: still 1 / 2
full_all_app_pod_rerun_authorized: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Why This Matters

M3.1 showed that the first productized RTDBSCAN runner route was much slower
than the incumbent legacy OptiX path:

```text
M3.1 runner_vs_legacy: 0.5038x
```

M3.2 fixed generic fingerprint/overhead cost and recovered parity:

```text
M3.2 runner_vs_legacy: 0.9930x
```

M3.3/M3.4 removed the per-repeat runner call loop by adding a repeated
prepared-session runner and wiring it into the real route. The same-pod result
is:

```text
M3.4 runner_vs_legacy: 0.9976x
```

This confirms that the M3.3/M3.4 runner shape is no longer grossly wrong, but
it also confirms that this route does not unlock material performance beyond
the existing legacy OptiX incumbent.

## Next Action

Stop RTDBSCAN as the immediate second Set-A material-probe path. Do not keep
spending Phoenix V3 time on RTDBSCAN micro-optimizations unless they land in a
shared typed-continuation contract used by multiple probes.

Redirect to one of:

```text
AABB runner generalization
productized typed continuation runner
device-resident internal phase contract
```

Recommended next target:

```text
AABB runner generalization
```

Reason: AABB M2.1 is already the first material productized-path focused win,
so proving the same mechanism on a second AABB-style workload is the shortest
generic-runtime route to a second credible Set-A probe.

## Boundary

This report does not authorize:

- V3 release;
- public speedup wording;
- broad V3 faster than V2 wording;
- RTDBSCAN paper reproduction claims;
- full DBSCAN acceleration claims;
- full all-app pod rerun;
- V4 / C ABI / embedding work.

## Goal-Level Decision Audit

Decision: classify M3.4 RTDBSCAN repeated-runner pod A/B as parity progress,
not material Set-A evidence, and redirect away from RTDBSCAN as the immediate
second material probe.

1. Was I foolish?
   No. This decision follows the preregistered threshold and compares against
   the relevant incumbent legacy OptiX route.
2. If yes, what actions made the decision foolish?
   The foolish action would have been to quote the `2.94x` runner-vs-Embree
   geomean as success while hiding the `0.9976x` runner-vs-legacy result.
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. The correct path is to stop RTDBSCAN micro-tuning after parity and
   redirect to a generic runtime mechanism with better evidence leverage.
4. Can I now try a different path that truly solves the problem?
   Yes. The next path is AABB runner generalization or productized typed
   continuation, both of which target reusable V3 engine mechanisms rather than
   an app-specific RTDBSCAN patch.

## Sources

- `docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_4_pod_ab_20260622_204719/summary.json`
- `docs/reviews/claude_phoenix_v3_rtdbscan_repeated_runner_route_m3_4_review_2026-06-22.md`
- `docs/reports/phoenix_v3_repeated_prepared_session_runner_m3_3_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_repeated_runner_route_m3_4_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2_pod_ab_2026-06-22.md`
