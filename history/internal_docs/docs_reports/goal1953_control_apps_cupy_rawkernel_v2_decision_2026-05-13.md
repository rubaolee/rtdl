# Goal1953 - Control Apps As CuPy RawKernel v2 Versions

Status: implemented-local-contract-pod-timing-needed

Date: 2026-05-13

## User Decision

The four former all-app control rows may use CuPy `RawKernel` continuations for
their v2.0 app versions:

- `database_analytics`
- `graph_analytics`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

These v2 versions may be compared against their v1.8 Python+RTDL versions,
where v1.8 means no user C/C++ extension. This is explicitly not an absolutely
fair comparison because v2.0 is allowed to use Python+CuPy+RawKernel+RTDL while
v1.8 remains Python+RTDL.

## Implementation

New harness:

`examples/rtdl_control_apps_cupy_rawkernel.py`

The harness has two partner modes:

- `--partner cpu_fallback`: local correctness mode that exercises the same app
  summaries without requiring CuPy or CUDA.
- `--partner cupy`: real v2 mode using CuPy `RawKernel` continuations.

The harness keeps the existing app entry points unchanged and adds reviewable v2
continuations around the four former control rows.

## App Contracts

| App | v2 RawKernel continuation | Local oracle |
| --- | --- | --- |
| `database_analytics` | RawKernel predicate scan, grouped counts, grouped revenue sums, and risky order id emission | `rtdl_database_analytics_app.run_app(... output_mode="compact_summary")` |
| `graph_analytics` | Generic partner metric-table reductions for BFS discovery, triangle count, and visibility-edge counts | `rtdl_graph_analytics_app.run_app(... output_mode="summary")` per scenario |
| `polygon_pair_overlap_area_rows` | RawKernel exact cell-mask intersection/union summary over RTDL candidate pairs | `rtdl_polygon_pair_overlap_area_rows.run_case(... output_mode="summary")` |
| `polygon_set_jaccard` | RawKernel exact cell-mask set-intersection continuation plus CuPy-side ratio assembly | `rtdl_polygon_set_jaccard.run_case(... output_mode="summary")` |

## Local Validation

Command:

```bash
PYTHONPATH=src:. python examples/rtdl_control_apps_cupy_rawkernel.py \
  --app all --copies 2 --partner cpu_fallback
```

Result:

```text
all_match_v1_8_python_rtdl_oracle: true
```

This validates the app-level result contracts locally. It does not produce CuPy
timing evidence.

## Claim Boundary

Allowed after pod timing:

```text
Per explicit v2.0 design decision, these four apps have v2 CuPy RawKernel
versions and may be compared against v1.8 Python+RTDL versions without user
C/C++ extension.
```

Required fairness note:

```text
This comparison is not absolutely fair: v1.8 is Python+RTDL, while v2.0 uses
Python+CuPy RawKernel+RTDL.
```

Still blocked until pod timing:

- performance ratios for the four v2 rows;
- whole-app speedup wording for these rows;
- any claim that RTDL accelerates arbitrary RawKernel code.

## Next Required Work

Run the harness on a CUDA pod with CuPy installed:

```bash
PYTHONPATH=src:. python examples/rtdl_control_apps_cupy_rawkernel.py \
  --app all --copies 100000 --partner cupy --candidate-backend optix
```

The exact `copies` value should be chosen so each row runs at a useful
seconds-scale or near-seconds-scale duration without timing out. The resulting
artifact should record:

- GPU model and driver;
- source commit;
- command;
- per-app v2 RawKernel timings;
- v1.8 Python+RTDL baseline timings under the same fixture scale;
- the fairness note above.
