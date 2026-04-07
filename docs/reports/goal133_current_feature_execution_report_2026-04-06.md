# Goal 133 Report: Current Feature Execution

Date: 2026-04-06
Status: accepted

## Scope

This report explains how the current RTDL v0.2 feature line is executed today.

The feature line is:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

These are the two closed segment/polygon workload families that currently define
the strongest v0.2 technical surface.

## What the feature does

### `segment_polygon_hitcount`

Input:

- probe segments
- build polygons

Output:

- one row per segment
- emitted fields:
  - `segment_id`
  - `hit_count`

Meaning:

- count how many polygons each segment intersects

### `segment_polygon_anyhit_rows`

Input:

- probe segments
- build polygons

Output:

- one row per true hit pair
- emitted fields:
  - `segment_id`
  - `polygon_id`

Meaning:

- materialize the segment/polygon spatial join rows directly

## RTDL execution shape

Both families use the same high-level RTDL shape:

1. `input`
2. `traverse`
3. `refine`
4. `emit`

Concrete kernel shape:

```python
segments = rt.input("segments", rt.Segments, role="probe")
polygons = rt.input("polygons", rt.Polygons, role="build")
candidates = rt.traverse(segments, polygons, accel="bvh")
hits = rt.refine(candidates, predicate=...)
return rt.emit(hits, fields=[...])
```

The two current predicates are:

- `rt.segment_polygon_hitcount(exact=False)`
- `rt.segment_polygon_anyhit_rows(exact=False)`

So the current feature is still an RTDL workload in the standard sense:

- accelerated candidate generation
- exact refine on candidate pairs
- emit either aggregated rows or raw join rows

## How it is executed today

## 1. Representative datasets are loaded first

The execution path does not start from ad hoc SQL or ad hoc backend data.

It starts from the shared representative dataset layer:

- [baseline_runner.py](/Users/rl2025/rtdl_python_only/src/rtdsl/baseline_runner.py)

Supported current dataset shapes:

- authored minimal case
- fixture-backed county subset
- derived tiled county subset:
  - `derived/br_county_subset_segment_polygon_tiled_xN`

The current large deterministic family is built by:

- loading the fixture-backed county subset
- tiling the same base segments and polygons `N` times
- using deterministic offsets:
  - `step_x = 30.0`
  - `step_y = 20.0`

So the large-scale tests use deterministic repeated geometry, not random scenes.

## 2. The same dataset feeds all runtime backends

The loaded representative case is then executed through:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`
- `vulkan`

depending on the current goal or validation path.

That is how RTDL keeps the comparison honest:

- same workload
- same inputs
- same expected emitted shape

## 3. Current backend execution reality

The current segment/polygon families are not best described as “pure RT-core
magic.”

The strongest current execution story is:

- candidate reduction through the accepted candidate-index redesign
- backend-aligned exact refine
- emitted rows verified against PostGIS

Important backend notes:

### CPU

- trusted practical fallback
- now strong on large deterministic rows after the candidate-index redesign

### Embree

- strong CPU baseline
- prepared reuse supported
- strong on large Linux rows

### OptiX

- strong Linux backend
- current wins come from accepted algorithmic candidate reduction and alignment
- this is not the same as claiming full universal RT-core-native maturity

### Vulkan

- correctness/portability backend
- must work
- must not be very slow
- currently competitive on the accepted Linux rows for these two families
- not treated as the flagship optimized backend

## 4. PostGIS is the independent correctness anchor

The current feature line is checked against PostGIS, not only against RTDL’s own
reference code.

That path is implemented in:

- [goal114_segment_polygon_postgis.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal114_segment_polygon_postgis.py)
- [goal128_segment_polygon_anyhit_postgis.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal128_segment_polygon_anyhit_postgis.py)

And the SQL artifact is now saved here:

- [v0_2_segment_polygon_postgis_workloads.sql](/Users/rl2025/rtdl_python_only/docs/sql/v0_2_segment_polygon_postgis_workloads.sql)

## PostGIS table-building path

The current validation flow does this:

1. open PostGIS connection
2. drop and recreate per-goal schema
3. create raw segment table
4. create raw polygon table
5. bulk-load both with `COPY FROM STDIN`
6. build typed geometry tables
7. create GiST indexes on both geometry tables
8. `ANALYZE`
9. run the workload SQL
10. compare RTDL backend rows against the PostGIS result

So yes, the tested PostGIS path uses indexes:

- GiST on segments
- GiST on polygons

## Exact PostGIS workload queries

### `segment_polygon_hitcount`

```sql
SELECT
    s.id::BIGINT AS segment_id,
    COUNT(p.id)::BIGINT AS hit_count
FROM rtdl_v0_2_postgis.segments AS s
LEFT JOIN rtdl_v0_2_postgis.polygons AS p
    ON ST_Intersects(s.geom, p.geom)
GROUP BY s.id
ORDER BY s.id;
```

Important detail:

- `LEFT JOIN` keeps zero-hit segments in the output

### `segment_polygon_anyhit_rows`

```sql
SELECT
    s.id::BIGINT AS segment_id,
    p.id::BIGINT AS polygon_id
FROM rtdl_v0_2_postgis.segments AS s
JOIN rtdl_v0_2_postgis.polygons AS p
    ON ST_Intersects(s.geom, p.geom)
ORDER BY s.id, p.id;
```

Important detail:

- plain `JOIN` omits zero-hit segments and emits only true hit pairs

## Where the current strong evidence comes from

The strongest current operational evidence is on Linux:

- Linux is the primary v0.2 development and validation platform
- this Mac is only a limited local platform for:
  - Python reference
  - C/oracle
  - Embree

The large accepted stress audit is:

- [goal131_v0_2_linux_stress_audit_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal131_v0_2_linux_stress_audit_2026-04-06.md)

Current accepted large-row conclusion:

- both workload families remain parity-clean against PostGIS through `x4096`
- both remain strongly competitive on the accepted Linux platform

## Current honesty boundaries

The feature is real and strong, but its claims are still bounded.

What RTDL v0.2 can honestly claim now:

- the two segment/polygon workload families are real
- they are executed across the current backend surface
- they are validated against indexed PostGIS
- they scale strongly on the accepted Linux validation platform

What RTDL v0.2 does not need to claim here:

- exact computational geometry
- universal backend maturity on all platforms
- that every current win is proof of a fully mature RT-core-native traversal
  story

## Short conclusion

The current feature line is executed as:

- one RTDL kernel shape
- one shared representative dataset layer
- multiple backend runs over the same data
- one indexed PostGIS correctness anchor
- one Linux-first large-scale validation flow

That is the current real execution model behind the feature, not just a loose
design idea.
