# Goal 128 Linux Runbook

Date: 2026-04-06
Status: ready for external execution

## Goal

Run the `segment_polygon_anyhit_rows` external validation package on a Linux
host that has:

- RTDL backends available
- PostGIS available
- `psycopg2` available

## PostGIS validation

From the repo root:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal128_segment_polygon_anyhit_postgis_validation.py \
  --copies 64 \
  --db-name rtdl_postgis \
  --output-dir build/goal128_postgis_x64
```

This should produce:

- `goal128_segment_polygon_anyhit_postgis_validation.json`
- `goal128_segment_polygon_anyhit_postgis_validation.md`

## Linux large-scale performance package

From the repo root:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal128_segment_polygon_anyhit_linux_large_perf.py \
  --db-name rtdl_postgis \
  --perf-iterations 3 \
  --output-dir build/goal128_linux_large_perf
```

This should produce:

- `goal128_segment_polygon_anyhit_linux_large_perf.json`
- `goal128_segment_polygon_anyhit_linux_large_perf.md`

## Expected datasets

The package uses deterministic county-derived tiled datasets:

- `x64`
- `x256`
- `x512`
- `x1024`

## What to publish back into the repo

Copy the final artifacts into a dated report directory under:

- `docs/reports/`

and then write the final Goal 128 closure report that summarizes:

- parity vs PostGIS
- backend timings on Linux
- current honesty boundary
