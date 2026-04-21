# Goal 730: Facility KNN Compact Output

Date: 2026-04-21

## Scope

Goal 730 improves `examples/rtdl_facility_knn_assignment.py` for app cases that
only need primary depot assignment or depot-load summaries.

The public default remains unchanged:

- `--output-mode rows`
- K=3 nearest-depot fallback choices
- full emitted rows and `choices_by_customer`

New compact modes:

- `--output-mode primary_assignments`
- `--output-mode summary`

Both compact modes run a K=1 RTDL KNN kernel instead of the K=3 fallback-choice
kernel. This avoids unnecessary rank work and avoids returning fallback-choice
rows when the app does not need them.

## Correctness

Implemented checks:

- compact primary assignments match the rank-1 assignments derived from K=3
  rows on the CPU Python reference path
- compact summary depot loads match the rank-1 loads derived from K=3 rows
- Embree compact primary assignment matches CPU Python reference
- invalid copy counts and invalid output modes are rejected

Focused test command:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal730_facility_knn_compact_output_test
```

Local result:

- 4 tests passed

Linux Embree result:

- 4 tests passed

## Performance Evidence

Measurement:

- `run_case(...)` plus `json.dumps(...)`
- Embree backend
- three repeats per case
- copies 256, 1024, 4096

Local macOS result:

| Copies | Customers | Rows median | Primary median | Primary speedup | Summary median | Summary speedup | Primary JSON reduction | Summary JSON reduction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 1,024 | 0.0278s | 0.0100s | 2.77x | 0.0106s | 2.61x | 21.45x | 57.46x |
| 1024 | 4,096 | 0.1970s | 0.1371s | 1.44x | 0.1380s | 1.43x | 21.01x | 57.88x |
| 4096 | 16,384 | 3.1398s | 2.1559s | 1.46x | 2.1372s | 1.47x | 19.71x | 55.67x |

Linux result:

| Copies | Customers | Rows median | Primary median | Primary speedup | Summary median | Summary speedup | Primary JSON reduction | Summary JSON reduction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 1,024 | 0.0324s | 0.0179s | 1.81x | 0.0160s | 2.02x | 21.46x | 57.48x |
| 1024 | 4,096 | 0.2877s | 0.2005s | 1.44x | 0.1941s | 1.48x | 21.01x | 57.89x |
| 4096 | 16,384 | 3.5068s | 2.7864s | 1.26x | 2.7565s | 1.27x | 19.71x | 55.67x |

Raw JSON evidence:

- `docs/reports/goal730_facility_knn_compact_output_perf_local_2026-04-21.json`
- `docs/reports/goal730_facility_knn_compact_output_perf_linux_2026-04-21.json`

## Boundary

This is a compact-output and K=1 primary-assignment optimization. It is not a
claim that the full K=3 fallback-choice workload is faster, and it is not an
OptiX, Vulkan, HIPRT, or Apple RT claim.

Use `rows` mode when the app needs fallback choices or distances. Use
`primary_assignments` or `summary` when the app only needs primary depot IDs or
depot-load counts.
