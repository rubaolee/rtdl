# Goal 112 Segment-Polygon Performance Maturation

Date: 2026-04-05
Author: Codex
Status: accepted

## Final conclusion

Goal 112 is finished.

Accepted claim:

- `segment_polygon_hitcount` now has an explicit measured performance matrix on:
  - authored minimal
  - fixture-backed county subset
  - derived tiled county case
- the matrix covers:
  - `cpu`
  - `embree`
  - `optix`
- all measured `current_run` rows stayed parity-clean against
  `cpu_python_reference`
- all measured `prepared_reuse` rows stayed parity-clean against
  `cpu_python_reference`
- the family's performance story is now better characterized, not newly
  promoted to RT-core maturity

Final honesty judgment:

- Goal 112 closes as performance characterization and prepared-path
  clarification for the Goal 110 family
- it does **not** claim that the workload has moved out of the current audited
  `native_loop` boundary
- no further fix is worth taking now based on the measured current bottlenecks

## Measurement contract

Timed matrix:

- `cpu`
  - `current_run`
- `embree`
  - `current_run`
  - `prepared_bind_and_run`
  - `prepared_reuse`
- `optix`
  - `current_run`
  - `prepared_bind_and_run`
  - `prepared_reuse`

Correctness context only:

- `cpu_python_reference`

Meaning of timing boundaries:

- `current_run`
  - direct `run_<backend>(...)`
- `prepared_bind_and_run`
  - pre-created prepared kernel plus timed `bind(...).run()`
- `prepared_reuse`
  - one prepared bound execution reused across timed `.run()`

## Host and software

Capable host:

- host: `lx1`
- OS: `Linux 6.17.0-20-generic`
- distro family: `Ubuntu 24.04`
- CPU: `Intel(R) Core(TM) i7-7700HQ CPU @ 2.80GHz`
- threads: `8`
- Python: `3.12.3`
- GPU: `NVIDIA GeForce GTX 1070`
- NVIDIA driver: `580.126.09`

## Final matrix summary

### Authored minimal

- `cpu current_run`
  - mean `0.0000558 s`
- `embree current_run`
  - mean `0.0000533 s`
- `embree prepared_bind_and_run`
  - mean `0.0000180 s`
- `embree prepared_reuse`
  - mean `0.0000099 s`
- `optix current_run`
  - mean `0.0000698 s`
- `optix prepared_bind_and_run`
  - mean `0.0000164 s`
- `optix prepared_reuse`
  - mean `0.0000095 s`

Interpretation:

- current-run behavior is already close across `cpu` and `embree`
- prepared paths materially reduce overhead for both RT backends
- prepared reuse is the best path for both `embree` and `optix`

### Fixture-backed county subset

- `cpu current_run`
  - mean `0.0000744 s`
- `embree current_run`
  - mean `0.0000520 s`
- `embree prepared_bind_and_run`
  - mean `0.0000233 s`
- `embree prepared_reuse`
  - mean `0.0000168 s`
- `optix current_run`
  - mean `0.0000477 s`
- `optix prepared_bind_and_run`
  - mean `0.0000208 s`
- `optix prepared_reuse`
  - mean `0.0000156 s`

Interpretation:

- both RT backends beat the current `cpu` path on this accepted fixture case
- prepared paths again reduce overhead materially
- both prepared RT backends are now within the same small timing band

### Derived tiled county x4

- `cpu current_run`
  - mean `0.0003151 s`
- `embree current_run`
  - mean `0.0003151 s`
- `embree prepared_bind_and_run`
  - mean `0.0001888 s`
- `embree prepared_reuse`
  - mean `0.0001927 s`
- `optix current_run`
  - mean `0.0001464 s`
- `optix prepared_bind_and_run`
  - mean `0.0001240 s`
- `optix prepared_reuse`
  - mean `0.0001113 s`

Interpretation:

- on the largest accepted Goal 112 case, `optix` is the fastest current path
- `embree current_run` and `cpu current_run` are effectively tied here
- `embree` still benefits from preparation, but much less dramatically than on
  the smaller cases
- `optix prepared_reuse` is the fastest measured boundary in the matrix

## What this means

### 1. Prepared paths are worth keeping

Prepared execution is not cosmetic for this family.

For both `embree` and `optix`:

- `prepared_bind_and_run` beats `current_run` on every accepted case
- `prepared_reuse` is best or effectively tied for best on every accepted case

So Goal 112 justifies keeping prepared-path support visible in the family story.

### 2. No single backend dominates every interpretation

- `optix` is strongest on the larger derived case
- `embree` is competitive and clearly benefits from preparation
- the family is not stuck in a uniformly slow state

### 3. The family is still not RT-core-matured

The timings are better characterized, but the lowering/runtime story has not
changed:

- the accepted family still sits under the current `native_loop` honesty
  boundary

So the correct claim is:

- better measured
- prepared-path behavior understood
- not a proof of RT-core-native maturation

## Concrete outcome required by Goal 112

Goal 112 required either:

- one measured fix
- or one clearly justified “no fix worth taking now” conclusion

The accepted outcome is:

- no fix worth taking now

Reason:

- the current matrix already shows the main useful behavior:
  - parity-clean execution
  - measurable prepared-path win
  - no repeatable capable-host regression demanding immediate repair
- the family's remaining limitation is architectural honesty, not one obvious
  removable overhead

So another small tuning pass would likely add churn without changing the
correct high-level conclusion.

## Validation

### Local harness/tests

Executed locally:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal112_segment_polygon_perf_test
```

Observed result:

- `2` tests
- `OK`

### Capable-host measurement run

Executed on `lx1`:

```bash
cd /home/lestat/work/rtdl_python_only
PYTHONPATH=src:. python3 - <<'PY'
from pathlib import Path
from rtdsl.goal112_segment_polygon_perf import run_goal112_segment_polygon_perf
from rtdsl.goal112_segment_polygon_perf import write_goal112_artifacts

payload = run_goal112_segment_polygon_perf(iterations=3)
write_goal112_artifacts(payload, Path("build/goal112_segment_polygon_perf"))
PY
```

Observed high-level result:

- all `cpu`, `embree`, and `optix` records were `available: true`
- all `current_run` records were `parity: true`
- all prepared-reuse parity checks were `true`
- `prepared_bind_and_run` was timed as a combined bind-plus-run boundary and was
  not separately row-validated in the harness

## Final status

Goal 112 is finished.
