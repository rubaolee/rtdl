# Goal2500: RayDB-Style Backend Matrix Runner

Date: 2026-05-22

## Verdict

Goal2500 adds a repeatable backend matrix runner for the RayDB-style columnar
aggregate benchmark slice. The runner records diagnostic timing and correctness
metadata for the exact contract paths built in Goals2495-2499.

This is evidence plumbing only. It does not authorize performance wording.

## Runner

Script:

```bash
PYTHONPATH=src:. python scripts/goal2500_raydb_style_backend_matrix.py \
  --backends cpu_python_reference embree optix \
  --repeats 5 \
  --output docs/reports/goal2500_raydb_style_backend_matrix_local_2026-05-22.json
```

The runner:

- runs CPU reference modes `count`, `sum`, `min`, `max`, and
  `avg_as_sum_count`;
- runs Embree modes `count` and `sum` when `rt.embree_version()` is available;
- runs OptiX modes `count` and `sum` when `rt.optix_version()` is available;
- skips unavailable backends with a recorded reason;
- records `matches_cpu_reference`;
- records the `lowering_plan` metadata from Goal2499;
- records median/min/max/sample elapsed seconds as diagnostic values.

## Local Smoke Result

Local output was generated at:

- `docs/reports/goal2500_raydb_style_backend_matrix_local_2026-05-22.json`

Observed local status:

- `cpu_python_reference`: `ok`, all modes matched the CPU reference contract;
- `embree`: `ok`, count/sum matched the CPU reference contract;
- `optix`: `skipped`, local Mac environment could not load `libcuda.so.1`.

These local timings are tiny-fixture diagnostics only and are not comparable
public performance evidence.

## Claim Boundary

The JSON payload includes this boundary:

```text
Backend matrix for the generic columnar grouped aggregate contract only.
Timings are diagnostic and do not authorize public speedup, whole-app,
authors-code, true zero-copy, SQL-engine, or DBMS claims.
```

## How To Use With Pod

When a CUDA/OptiX pod is available, run the same command from a checkout of the
current branch and preserve:

- exact SSH host/port/key;
- `git rev-parse HEAD`;
- CUDA/driver/OptiX environment;
- the JSON payload under `docs/reports/`.

Only after pod execution can we say whether the OptiX count/sum path has fresh
runtime parity evidence. Even then, timing rows remain diagnostic unless
separately reviewed for public wording.
