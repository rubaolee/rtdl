# Goal724: Service Coverage Embree Gap Summary Mode

Date: 2026-04-21

## Objective

Continue Embree app optimization after Goal723. `service_coverage_gaps` was a candidate because the core question is whether a household has at least one clinic within the service radius. The existing row mode is still needed for clinic ids, distances, and clinic load counts, but the gap-only result can use count-threshold early exit.

## Implementation

Updated:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_service_coverage_gaps.py`

New Embree-only option:

- `--embree-summary-mode rows|gap_summary`

The default remains `rows`.

The new `gap_summary` mode uses:

- `rt.fixed_radius_count_threshold_2d_embree(households, clinics, radius=RADIUS, threshold=1)`

This returns one row per household and stops counting once at least one clinic is found. It reports:

- `coverage_summary_rows`
- `uncovered_household_ids`
- `covered_household_count`

It intentionally leaves these row-mode fields empty:

- `rows`
- `nearby_clinics_by_household`
- `clinic_loads`

## Correctness Evidence

Local macOS:

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal724_service_coverage_embree_summary_test

Ran 2 tests in 0.020s
OK
```

Linux `lestat@192.168.1.20`, isolated checkout `/tmp/rtdl_goal724`:

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal724_service_coverage_embree_summary_test

Ran 2 tests in 0.014s
OK
```

The tests verify:

- the app exposes `gap_summary`;
- summary mode finds the same uncovered household ids as row mode;
- covered household count matches row mode;
- row-specific clinic-id/load fields are intentionally empty in summary mode;
- summary row count equals household count.

## Performance Evidence

Harness:

- `/Users/rl2025/rtdl_python_only/scripts/goal724_service_coverage_summary_perf.py`

Mac JSON:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal724_service_coverage_summary_perf_local_2026-04-21.json`

Linux JSON:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal724_service_coverage_summary_perf_linux_2026-04-21.json`

Linux median timing, 3 repeats:

| Copies | Households | Clinics | Row count | Summary rows | Row mode | Gap summary | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1024 | 4096 | 3072 | 5118 | 4096 | 0.0339s | 0.0209s | 1.62x |
| 4096 | 16384 | 12288 | 20478 | 16384 | 0.1078s | 0.0987s | 1.09x |

Mac median timing, 3 repeats:

| Copies | Households | Clinics | Row count | Summary rows | Row mode | Gap summary | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 1024 | 768 | 1278 | 1024 | 0.0089s | 0.0031s | 2.83x |
| 1024 | 4096 | 3072 | 5118 | 4096 | 0.0164s | 0.0122s | 1.35x |
| 4096 | 16384 | 12288 | 20478 | 16384 | 0.0571s | 0.0558s | 1.02x |

## Interpretation

This is a useful but bounded app-level optimization. It is strongest when the app only needs the gap result and can stop after the first matching clinic. The speedup fades at larger scale on the current synthetic fixture because row count is only modestly larger than household count.

The full row mode remains necessary for clinic-load analysis and inspectable clinic-neighbor details.

## Release Boundary

Allowed claim:

- `service_coverage_gaps` has an Embree gap-summary mode for covered/uncovered household detection.
- Linux speedup is measured at `1.62x` for 4096 households and `1.09x` for 16384 households on the current fixture.

Not allowed:

- Do not claim this replaces row mode.
- Do not claim speedup for clinic-load reporting.
- Do not generalize the speedup beyond gap-only output and the measured fixtures.
