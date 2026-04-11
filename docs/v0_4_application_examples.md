# RTDL v0.4 Application Examples

This page shows how the current nearest-neighbor release features can be used
as small applications rather than only as bare workload kernels.

All three examples are bounded and correctness-first:

- RTDL handles the geometric neighbor query
- Python handles grouping, summaries, and app-specific decisions
- PostgreSQL/PostGIS scripts are provided as transparent comparison shapes

Run commands from the repository root:

```bash
PYTHONPATH=src:.
```

## Service Coverage Gaps

- code: [examples/rtdl_service_coverage_gaps.py](../examples/rtdl_service_coverage_gaps.py)
- SQL: [docs/sql/v0_4_service_coverage_gaps_postgis.sql](sql/v0_4_service_coverage_gaps_postgis.sql)

Question:

- which households do not have any clinic within the accepted service radius?

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_service_coverage_gaps.py --backend cpu_python_reference --copies 2
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_service_coverage_gaps.py --backend cpu_python_reference --copies 2
```

## Event Hotspot Screening

- code: [examples/rtdl_event_hotspot_screening.py](../examples/rtdl_event_hotspot_screening.py)
- SQL: [docs/sql/v0_4_event_hotspot_screening_postgis.sql](sql/v0_4_event_hotspot_screening_postgis.sql)

Question:

- which events sit inside dense local clusters?

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_event_hotspot_screening.py --backend cpu_python_reference --copies 2
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_event_hotspot_screening.py --backend cpu_python_reference --copies 2
```

Important boundary:

- this app removes `query_id == neighbor_id` after the RTDL query
- that self-edge cleanup is part of the application rule, not a separate RTDL
  predicate today

## Facility K-Nearest Assignment

- code: [examples/rtdl_facility_knn_assignment.py](../examples/rtdl_facility_knn_assignment.py)
- SQL: [docs/sql/v0_4_facility_knn_assignment_postgis.sql](sql/v0_4_facility_knn_assignment_postgis.sql)

Question:

- what is each customer’s primary depot and fallback set?

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_facility_knn_assignment.py --backend cpu_python_reference --copies 2
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_facility_knn_assignment.py --backend cpu_python_reference --copies 2
```

## Optional SciPy Comparison

If SciPy is installed, all three examples also support:

```bash
PYTHONPATH=src:. python examples/rtdl_service_coverage_gaps.py --backend scipy
PYTHONPATH=src:. python examples/rtdl_event_hotspot_screening.py --backend scipy
PYTHONPATH=src:. python examples/rtdl_facility_knn_assignment.py --backend scipy
```

## Honest Summary

- these are real app-shaped uses of the `v0.4` workload line
- they are still bounded examples, not final benchmark claims
- the strongest current story is:
  - clean nearest-neighbor contracts
  - RTDL-plus-Python application composition
  - transparent SQL comparison paths
