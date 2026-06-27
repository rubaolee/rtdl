# Goal 50 Timing Analysis

## Question

Why did Goal 50 take so long to finish, even though the final accepted PostGIS query times were often much smaller than the RTDL backend runtimes?

## Short Answer

Goal 50 took a long time because the expensive part was not just running the final accepted PostGIS queries. The total wall-clock time included:

- provisioning and validating the PostGIS environment
- loading and indexing large bounded real-data packages
- repeated full-package reruns while closing exact `pip` semantics gaps
- full-matrix RTDL result generation and hashing
- backend-by-backend parity validation across:
  - C oracle
  - Embree
  - OptiX
- review and consensus work after the measurements

So the final accepted query timings describe only the last clean execution state, not the total effort required to reach a PostGIS-clean result.

## What The Final Accepted Timings Actually Show

### County ⊲⊳ Zipcode `top4_tx_ca_ny_pa`

- PostGIS load: `86.199871356 s`

`lsi`

- PostGIS query: `34.032305237 s`
- C oracle: `89.336466250 s`
- Embree: `80.270740817 s`
- OptiX: `53.290038755 s`

`pip`

- PostGIS indexed positive-hit query: `0.430007831 s`
- C oracle full-matrix truth: `24.416985234 s`
- Embree full-matrix truth: `16.812840088 s`
- OptiX full-matrix truth: `19.255055544 s`

### BlockGroup ⊲⊳ WaterBodies `county2300_s10`

- PostGIS load: `1.001984315 s`

`lsi`

- PostGIS query: `0.231961607 s`
- C oracle: `0.228627974 s`
- Embree: `0.222838373 s`
- OptiX: `0.893340557 s`

`pip`

- PostGIS indexed positive-hit query: `0.008412973 s`
- C oracle full-matrix truth: `0.149648431 s`
- Embree full-matrix truth: `0.117168097 s`
- OptiX full-matrix truth: `0.647711122 s`

## Why Goal 50 Took So Long

### 1. The first major cost was data loading and index build, not just query execution

The accepted `county_zipcode` package has:

- `9,982,960` left segments
- `1,705,027` right segments
- `10,144` probe points
- `1,612` polygons

Just loading those chain-derived geometries into PostGIS and building the indexed tables cost:

- `86.199871356 s`

That load cost is independent of whether the final query is fast.

### 2. `pip` parity required full-matrix RTDL truth, not just positive-hit comparison

The PostGIS side can answer `pip` efficiently as an indexed positive-hit join:

- `geom &&`
- `ST_Covers(...)`

But RTDL returns the full point x polygon matrix with `contains = 0/1`.

For `county_zipcode`, that means:

- `10,144 x 1,612 = 16,352,128` truth rows

So even though the PostGIS hit query itself is only about `0.43 s`, the RTDL side still has to:

- compute the same truth semantics
- materialize the full row set
- hash that full result for exact parity

That is why the accepted RTDL `pip` times are still in the `16-24 s` range.

### 3. Most of the total elapsed time came from semantic debugging reruns, not the final accepted measurements

Goal 50 did not succeed on the first try. The actual path included:

- an earlier invalid remote PostGIS run that was rejected because `lsi` SQL did not yet use the required indexed `geom &&` predicate
- several county/zipcode reruns while narrowing `pip` mismatches
- one shared RTDL `pip` bug from degenerate repeated-closing edges
- one shared RTDL `pip` bug from over-loose endpoint tolerance on short edges
- final boundary/topology mismatches that required switching accepted `pip` refine semantics to GEOS prepared-polygon `covers(point)`
- separate remote rebuild and validation work for:
  - oracle
  - Embree
  - OptiX

So the long wall-clock duration of Goal 50 mostly reflects the time required to turn PostGIS from a comparison target into a strict external correctness oracle.

### 4. OptiX validation added additional remote bring-up work

After the GEOS-based `pip` alignment was proven in the oracle and Embree paths, the same semantics had to be carried into OptiX host-side refine.

That required:

- updating the OptiX native path
- remote rebuild with GEOS-linked host code
- dedicated positive-hit set verification before the full accepted rerun

That extra step was necessary because OptiX had to be proven equal to the same PostGIS truth set, not just equal to earlier RTDL behavior.

### 5. Review and consensus are part of the goal duration

Goal 50 was not allowed to close on raw measurements alone. The finished state also required:

- report writing
- Gemini review
- Codex consensus

That review time is small compared with the geometry/debugging work, but it is still part of the real goal duration.

## What This Means

### The final accepted PostGIS comparison is much cheaper than the whole goal

If we rerun the already-correct accepted comparison path now, without rediscovering semantics bugs, the time should be much lower than the total original Goal 50 wall-clock effort.

That is because the expensive one-time work is already done:

- PostGIS environment is installed
- harness exists
- SQL strategy is fixed
- RTDL `pip` semantics are aligned with PostGIS on the accepted packages

### The dominant steady-state costs are different by workload

For `lsi` on the large county/zipcode package:

- both PostGIS and RTDL spend real time on the join itself
- OptiX currently has the best accepted RTDL runtime on this package

For `pip` on the large county/zipcode package:

- PostGIS query time is tiny because it answers an indexed positive-hit join
- RTDL times remain much larger because RTDL emits and hashes the full truth matrix

So the apparent speed gap in accepted `pip` timings is partly an execution-model difference, not just a raw backend-performance difference.

## Bottom Line

Goal 50 took a long time because it was a correctness-calibration goal, not just a benchmark run.

The real time was spent on:

- loading large geometry packages into PostGIS
- building indexed tables
- generating full-matrix RTDL truth rows
- rerunning the large county/zipcode package several times
- fixing exact `pip` semantic mismatches until PostGIS and all RTDL backends matched exactly

After those fixes, the final accepted steady-state comparison is much cleaner and cheaper than the total effort needed to get there.
