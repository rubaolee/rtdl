# Goal972 Event-Hotspot Baseline Repair

Date: 2026-04-26

## Scope

Goal971 identified one invalid same-semantics baseline artifact:

```text
docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_embree_summary_path_2026-04-23.json
```

The artifact was valid in structure and parity, but its `benchmark_scale` used
`copies=2000` while Goal835 requires `copies=20000` for
`event_hotspot_screening / prepared_count_summary`.

## Action

Regenerated the Embree compact-summary baseline at the required scale:

```bash
PYTHONPATH=src:. python3 scripts/goal859_spatial_summary_baseline.py \
  --app event_hotspot_screening \
  --backend embree \
  --copies 20000 \
  --iterations 3 \
  --output-json docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_embree_summary_path_2026-04-23.json
```

Result:

```text
app: event_hotspot_screening
path_name: prepared_count_summary
baseline_name: embree_summary_path
benchmark_scale: copies=20000, iterations=3
correctness_parity: true
phase_separated: true
status: ok
```

Median phase timings:

| Phase | Seconds |
| --- | ---: |
| `input_build` | `0.067232` |
| `optix_prepare` | `0.000000` |
| `optix_query` | `0.256616` |
| `python_postprocess` | `0.040296` |

## SciPy Limitation

Attempted optional SciPy baselines for `service_coverage_gaps` and
`event_hotspot_screening`.

Both failed because SciPy is not installed locally:

```text
RuntimeError: SciPy is not installed; install scipy to run the cKDTree external baseline
```

These baselines remain optional/missing evidence. No dependency was installed
midstream because this repair goal is bounded to local already-available
runtime paths.

## Post-Repair Gate State

Goal836 now reports:

```text
service_coverage_gaps / prepared_gap_summary:
  cpu_oracle_summary=valid
  embree_summary_path=valid
  scipy_baseline_when_available=missing

event_hotspot_screening / prepared_count_summary:
  cpu_oracle_summary=valid
  embree_summary_path=valid
  scipy_baseline_when_available=missing
```

Goal971 regenerated successfully after the repair. Its high-level tier counts
remain:

```text
same_semantics_baselines_complete_count: 3
active_gate_limited_count: 5
baseline_pending_count: 9
public_speedup_claim_authorized_count: 0
```

The counts remain unchanged because optional SciPy baselines are still missing,
but the concrete invalid Embree baseline defect is fixed.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal971_post_goal969_baseline_speedup_review_package_test \
  tests.goal846_active_rtx_claim_gate_test

Ran 7 tests
OK
```

## Verdict

`ACCEPT` from Codex.

The invalid event-hotspot Embree baseline is repaired. No public speedup claim
is authorized. Remaining work is baseline expansion for optional SciPy and
deferred app rows, not another cloud run.
