# Goal 214: v0.4 Application Examples And SQL Comparisons

## Result

Goal 214 is complete.

The `v0.4` nearest-neighbor line now has three application-style examples, a
dedicated user-facing documentation page, and three runnable PostgreSQL/PostGIS
comparison scripts.

New application examples:

- `examples/rtdl_service_coverage_gaps.py`
- `examples/rtdl_event_hotspot_screening.py`
- `examples/rtdl_facility_knn_assignment.py`

New comparison SQL:

- `docs/sql/v0_4_service_coverage_gaps_postgis.sql`
- `docs/sql/v0_4_event_hotspot_screening_postgis.sql`
- `docs/sql/v0_4_facility_knn_assignment_postgis.sql`

New public doc:

- `docs/v0_4_application_examples.md`

New bounded performance harness:

- `scripts/goal214_v0_4_application_perf.py`

## Application Set

### 1. Service Coverage Gaps

Workload core:

- `fixed_radius_neighbors`

Application question:

- which households do not have any clinic within the accepted service radius?

Application-layer summary:

- uncovered household IDs
- grouped clinic choices by household
- clinic load counts

### 2. Event Hotspot Screening

Workload core:

- `fixed_radius_neighbors`

Application question:

- which events sit inside dense local clusters?

Application-layer summary:

- drop self-neighbor rows
- count local neighbors per event
- emit hotspot IDs above a threshold

### 3. Facility K-Nearest Assignment

Workload core:

- `knn_rows`

Application question:

- what is each customer’s primary depot and fallback choice list?

Application-layer summary:

- grouped ordered choices per customer
- primary depot per customer
- primary depot load counts

## Local Verification

Commands run:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal214_v0_4_application_examples_test \
  tests.goal208_nearest_neighbor_examples_test \
  tests.goal207_knn_rows_external_baselines_test \
  tests.goal201_fixed_radius_neighbors_external_baselines_test
python3 -m compileall examples docs scripts/goal214_v0_4_application_perf.py
PYTHONPATH=src:. python3 scripts/goal214_v0_4_application_perf.py \
  --apps service_coverage_gaps event_hotspot_screening facility_knn_assignment \
  --backends cpu_python_reference cpu \
  --copies 2 4 \
  --iterations 1 \
  --output-dir build/goal214_local_smoke
```

Results:

- `Ran 26 tests`
- `OK`
- `compileall`: `OK`
- local performance harness smoke: `OK`

## Linux Validation

Host:

- `lestat@192.168.1.20`

Environment facts:

- Python `3.12.3`
- Embree available: `4.3.0`
- SciPy not installed on this host
- PostgreSQL installed
- PostGIS extension available but not pre-enabled in the default database

### Remote test slice

Command:

```bash
ssh lestat-lx1 '
  cd /home/lestat/work/rtdl_python_only &&
  PYTHONPATH=src:. python3 -m unittest \
    tests.goal214_v0_4_application_examples_test \
    tests.goal207_knn_rows_external_baselines_test \
    tests.goal201_fixed_radius_neighbors_external_baselines_test
'
```

Result:

- `Ran 22 tests`
- `OK`

### PostGIS script execution

All three new SQL scripts were executed successfully on Linux in a temporary
database after enabling the `postgis` extension in `rtdl_goal214`.

Validated behaviors:

- service coverage script emitted expected radius rows and the uncovered
  household
- hotspot script emitted self-filtered event-neighbor rows and hotspot counts
- facility KNN script emitted ordered `neighbor_rank` rows

### Bounded Linux performance run

Command:

```bash
ssh lestat-lx1 '
  cd /home/lestat/work/rtdl_python_only &&
  PYTHONPATH=src:. python3 scripts/goal214_v0_4_application_perf.py \
    --apps service_coverage_gaps event_hotspot_screening facility_knn_assignment \
    --backends cpu embree \
    --copies 64 256 1024 \
    --iterations 5 \
    --output-dir build/goal214_linux_perf
'
```

Artifacts:

- `build/goal214_linux_perf/summary.json`
- `build/goal214_linux_perf/summary.md`

Headline medians:

| App | CPU 64 | CPU 256 | CPU 1024 | Embree 64 | Embree 256 | Embree 1024 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| service coverage gaps | 1.475 ms | 6.147 ms | 33.729 ms | 1.394 ms | 5.636 ms | 22.964 ms |
| event hotspot screening | 3.233 ms | 14.717 ms | 98.188 ms | 3.040 ms | 11.117 ms | 50.322 ms |
| facility KNN assignment | 3.513 ms | 32.860 ms | 528.789 ms | 13.200 ms | 182.263 ms | 2771.369 ms |

## Good Aspects

- The new `v0.4` line now looks like a real application substrate rather than
  only a pair of raw workload demos.
- `fixed_radius_neighbors` maps cleanly to multiple application shapes:
  coverage screening and hotspot screening both read naturally.
- The PostGIS comparison path is now concrete and runnable under `psql`, not
  just described abstractly.
- On Linux, the Embree path is healthy for the two radius-based applications:
  it is roughly on par at the small end and clearly better by the `1024` copy
  case.
- The docs surface is cleaner now because users can see:
  workload example -> application example -> SQL comparison path.

## Bad Aspects

- SciPy is not installed on the Linux host, so the Linux comparison story is
  currently RTDL CPU vs RTDL Embree plus executable PostGIS SQL, not RTDL vs
  SciPy on that machine.
- PostGIS had to be enabled manually in a temporary database; it was not
  ready-to-run out of the box on the validation host.
- The current `knn_rows` Embree path is the clear weak spot:
  for facility assignment it is substantially slower than the native CPU path
  at every measured scale in this bounded run.
- The service-coverage CPU `64`-copy run had a large first-run outlier
  (`3216 ms` max versus `1.475 ms` median), so the right reading is the median,
  not the worst single sample.
- These applications are correctness-first and illustrative; they are not yet a
  polished end-user product package or a paper-style performance claim.

## Honest Summary

Goal 214 improved the `v0.4` story materially.

The nearest-neighbor line now has:

- user-facing application examples
- matching PostgreSQL/PostGIS implementations
- Linux validation on real backends
- an honest performance reading

The strongest current application surface is the radius-neighbor line.
`knn_rows` is functionally correct and application-usable, but its Embree
performance needs work before it can be presented as a strong accelerated
backend story.
