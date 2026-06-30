# Goal 114 Segment-Polygon Large-Scale PostGIS Validation

Date: 2026-04-05
Author: Codex
Status: accepted

## Final conclusion

Goal 114 is finished.

Accepted claim:

- `segment_polygon_hitcount` now has an external large-scale correctness check
  against PostGIS
- the family matches PostGIS exactly on the accepted large deterministic case
  for:
  - `cpu`
  - `embree`
  - `optix`
- this gives the feature a materially stronger correctness story than Goal 110
  alone

Explicit honesty boundary:

- Goal 114 strengthens correctness evidence
- it does **not** claim a new RT-backed traversal design
- it does **not** move the family out of the current audited `native_loop`
  boundary

## What was added

Implementation files:

- `src/rtdsl/goal114_segment_polygon_postgis.py`
- `scripts/goal114_segment_polygon_postgis_validation.py`
- `tests/goal114_segment_polygon_postgis_test.py`

Supporting code-surface change:

- `baseline_runner` now supports generic deterministic segment/polygon tiled
  datasets of the form:
  - `derived/br_county_subset_segment_polygon_tiled_xN`

## Large deterministic case

Accepted large case:

- dataset:
  - `derived/br_county_subset_segment_polygon_tiled_x256`
- segments:
  - `2560`
- polygons:
  - `512`

This is substantially larger than the Goal 110 derived case:

- Goal 110 derived:
  - `40` segments
  - `8` polygons
- Goal 114 accepted large case:
  - `2560` segments
  - `512` polygons

So Goal 114 validates the same family at a scale that is:

- `64x` larger in segment count
- `64x` larger in polygon count

relative to the Goal 110 `x4` derived case.

## PostGIS comparison contract

PostGIS query shape:

- load segments as `LINESTRING`
- load polygons as `POLYGON`
- compute:
  - `COUNT(p.id)` per segment
  - using `LEFT JOIN ... ON ST_Intersects(s.geom, p.geom)`

Output contract compared exactly:

- `segment_id`
- `hit_count`

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
- PostGIS version:
  - `3.4 USE_GEOS=1 USE_PROJ=1 USE_STATS=1`

## Results

### Large case x64 sanity pass

Dataset:

- `derived/br_county_subset_segment_polygon_tiled_x64`
- segments: `640`
- polygons: `128`

Observed:

- PostGIS digest:
  - `bdfe3c868dbae0278436b1451dd5760564f57359096986e0bf95951dc57f507b`
- `cpu` parity vs PostGIS:
  - `true`
- `embree` parity vs PostGIS:
  - `true`
- `optix` parity vs PostGIS:
  - `true`

### Accepted large case x256

Dataset:

- `derived/br_county_subset_segment_polygon_tiled_x256`
- segments: `2560`
- polygons: `512`

PostGIS:

- time:
  - `0.050333689 s`
- row count:
  - `2560`
- SHA256:
  - `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099`

RTDL backends:

- `cpu`
  - time: `0.581763063 s`
  - row count: `2560`
  - parity vs PostGIS: `true`
  - SHA256: `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099`
- `embree`
  - time: `0.588157317 s`
  - row count: `2560`
  - parity vs PostGIS: `true`
  - SHA256: `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099`
- `optix`
  - time: `0.389945515 s`
  - row count: `2560`
  - parity vs PostGIS: `true`
  - SHA256: `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099`

## What this means

### 1. The feature is now more than an internal closure story

Goal 110 already established internal RTDL parity on accepted closure cases.

Goal 114 adds:

- exact external agreement with PostGIS
- on a much larger deterministic case

That is a real strengthening step.

### 2. All three checked backends remained exact on the accepted large case

The important result is not the raw timing.

The important result is:

- `cpu`
- `embree`
- `optix`

all produced the exact same per-segment hit counts as PostGIS on the accepted
large case.

### 3. This still does not change the architectural honesty boundary

The family is now better validated.

But Goal 114 does not change:

- lowering
- candidate generation
- runtime architecture

So the correct status is:

- stronger external correctness evidence
- same current architectural honesty boundary

## Validation

### Local development checks

Executed locally:

```bash
python3 -m py_compile \
  src/rtdsl/goal114_segment_polygon_postgis.py \
  scripts/goal114_segment_polygon_postgis_validation.py \
  tests/goal114_segment_polygon_postgis_test.py

cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal114_segment_polygon_postgis_test
```

Observed result:

- `3` tests
- `OK`

### Capable-host execution

Executed on `lx1`:

```bash
cd /home/lestat/work/rtdl_goal114_clean
OPTIX_PREFIX=$HOME/vendor/optix-dev make build-optix
PYTHONPATH=src:. RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_PTX_COMPILER=nvcc RTDL_NVCC=/usr/bin/nvcc \
python3 scripts/goal114_segment_polygon_postgis_validation.py \
  --copies 256 \
  --backends cpu,embree,optix \
  --db-name rtdl_postgis \
  --output-dir build/goal114_x256
```

Observed result:

- all three backends returned exact parity vs PostGIS
- the output artifact set was written under:
  - `build/goal114_x256/`

## Final status

Goal 114 is finished.
