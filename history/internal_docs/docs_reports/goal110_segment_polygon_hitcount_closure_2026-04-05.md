# Goal 110 Segment-Polygon-Hitcount Closure

Date: 2026-04-05
Author: Codex
Status: accepted

## Final conclusion

Goal 110 is closed as a v0.2 workload-family expansion.

Accepted claim:

- `segment_polygon_hitcount` is now a first-class RTDL workload family with
  deterministic authored, fixture-backed, and derived cases
- it is parity-clean across the accepted closure backends:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
- prepared-path checks exist and pass for:
  - Embree
  - OptiX
  on the authored and fixture-backed cases

Explicit honesty boundary:

- Goal 110 closes as workload-family closure and semantic/backend closure
- it does **not** claim RT-backed maturity for this family
- the accepted package still sits under the current audited local
  `native_loop` honesty boundary

## What was added during Goal 110

Goal 110 now includes:

- one user-facing example:
  - `examples/rtdl_segment_polygon_hitcount.py`
- deterministic representative cases:
  - `authored_segment_polygon_minimal`
  - `tests/fixtures/rayjoin/br_county_subset.cdb`
  - `derived/br_county_subset_segment_polygon_tiled_x4`
- explicit semantic tests for:
  - endpoint inside polygon counts as a hit
  - boundary touch counts as a hit
  - edge crossing counts as a hit
  - zero-hit segments remain in output
  - overlapping polygons count independently
- backend closure tests for:
  - `cpu`
  - `embree`
  - `optix`
- prepared-path equivalence tests for:
  - Embree
  - OptiX

## Acceptance items and how they were satisfied

### 1. First-class workload-family documentation

Satisfied by:

- `docs/goal_110_v0_2_segment_polygon_hitcount_closure.md`
- `docs/rtdl_feature_guide.md`
- `examples/rtdl_segment_polygon_hitcount.py`

### 2. Authored minimal parity

Satisfied on the accepted closure suite by exact row equality on:

- `segment_id`
- `hit_count`

Backends:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`

### 3. Fixture-backed county-derived parity

Satisfied on:

- `tests/fixtures/rayjoin/br_county_subset.cdb`

Backends:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`

### 4. Derived deterministic parity beyond the basic fixture

Satisfied on:

- `derived/br_county_subset_segment_polygon_tiled_x4`

Backends:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`

### 5. Exact row comparison contract

All acceptance parity is expressed on exact equality of:

- `segment_id`
- `hit_count`

### 6. Prepared-path checks

Satisfied by:

- authored minimal prepared-path equality
- fixture-backed county prepared-path equality

For:

- Embree
- OptiX

### 7. Explicit technical comparison against `lsi`

Satisfied by:

- `docs/reports/goal110_segment_polygon_hitcount_comparison_and_significance_2026-04-05.md`

### 8. Significance proof

Satisfied by the accepted `4x` scale criterion:

- fixture:
  - segments `10`
  - polygons `2`
- derived:
  - segments `40`
  - polygons `8`

So the derived case provides exact `4x` probe/build scale over the basic county
fixture.

### 9. Example plus release-facing report

Satisfied by:

- `examples/rtdl_segment_polygon_hitcount.py`
- this final closure report

## Final validation

### Local Mac sanity pass

Validated locally:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal110_segment_polygon_hitcount_semantics_test \
  tests.goal110_baseline_runner_backend_test \
  tests.goal110_segment_polygon_hitcount_closure_test
```

Observed result:

- `14` tests
- `OK`
- `6` skipped

Known note:

- the existing local Mac native-oracle build still emits the known `geos_c`
  linker noise before the skipped native paths

### Linux capable-host closure

Host:

- `lestat-lx1`
- Ubuntu Linux
- OptiX SDK path: `/home/lestat/vendor/optix-dev`

Executed:

```bash
cd /home/lestat/work/rtdl_python_only
OPTIX_PREFIX=$HOME/vendor/optix-dev make build-optix
PYTHONPATH=src:. RTDL_OPTIX_PTX_COMPILER=nvcc RTDL_NVCC=/usr/bin/nvcc \
python3 -m unittest \
  tests.goal110_segment_polygon_hitcount_semantics_test \
  tests.goal110_baseline_runner_backend_test \
  tests.goal110_segment_polygon_hitcount_closure_test
```

Observed result:

- `14` tests
- `OK`

### Derived-case example confirmation on primary closure backends

Executed on `lestat-lx1`:

- `python3 examples/rtdl_segment_polygon_hitcount.py --backend embree --dataset derived/br_county_subset_segment_polygon_tiled_x4`
- `python3 examples/rtdl_segment_polygon_hitcount.py --backend optix --dataset derived/br_county_subset_segment_polygon_tiled_x4`

Observed high-level result for both:

- row count: `40`
- rows matched the accepted reference shape
- the first repeating pattern remained:
  - segment ids `1`, `11`, `21`, `31` -> `hit_count = 2`
  - all other rows in each tile block -> `hit_count = 1`

## OptiX repair recorded during Goal 110

During capable-host closure, the OptiX path initially failed parity on the
fixture-backed and derived cases by returning all-zero hit counts.

The cause was:

- the previous OptiX `segment_polygon_hitcount` path attempted a GPU traversal
  story that did not satisfy the boundary-inclusive segment/polygon semantics on
  the accepted county-derived data

The accepted repair was:

- keep the family under the audited local `native_loop` honesty boundary
- route the OptiX `segment_polygon_hitcount` execution through the exact
  host-side counting contract for this phase

That repair is consistent with the accepted Goal 110 honesty note and restores
parity without overclaiming RT-backed maturity.

## Final status

Goal 110 is finished.

It provides:

- one real v0.2 workload-family expansion beyond the v0.1 RayJoin-heavy slice
- deterministic correctness closure
- accepted backend closure on:
  - `cpu`
  - `embree`
  - `optix`
- a clear honesty boundary for what this family does and does not yet prove
