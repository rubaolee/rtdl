# Goal2526 cuDF GPU Dataframe Baseline For RayDB-Style RTDL

Date: 2026-05-23

## Verdict

Yes: RAPIDS/cuDF can do the lightweight GPU baseline job for this benchmark
slice.

Goal2526 installs cuDF in an isolated pod venv and runs the same RayDB-style
tiny fixture contract as a GPU dataframe workload. The result is correctness
parity with the RTDL CPU-reference rows and diagnostic GPU-dataframe timing.

This is not a SQL engine, not a SQL-engine baseline, not a DBMS baseline, and
not public speedup evidence.

## Pod Evidence

Pod:

```text
ssh root@213.173.108.13 -p 15902 -i ~/.ssh/id_ed25519_rtdl_codex
hostname: 57449dd4f93c
GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
```

Install:

```text
venv: /tmp/rtdl_goal2524_venv
pip package: cudf-cu12==26.4.0
cudf: 26.04.000
cupy: 14.1.0
```

Artifact:

- `docs/reports/goal2526_cudf_gpu_dataframe_baseline_pod_2026-05-23.json`

Runner:

```bash
python3 scripts/goal2526_cudf_gpu_dataframe_baseline.py \
  --repeats 500 \
  --output docs/reports/goal2526_cudf_gpu_dataframe_baseline_pod_2026-05-23.json
```

## Contract

The cuDF runner:

- loads the eight-row fixture once into a cuDF GPU DataFrame;
- applies the same predicates as the RTDL app;
- groups by `region_id`;
- computes `count`, `sum`, `min`, `max`, and decomposed
  `avg_as_sum_count`;
- compares compact grouped rows against the CPU reference.

Correctness:

```text
all_match_cpu_reference: true
```

## Diagnostic Timing

500 repeats on the pod:

| Case | Median ms | Boundary |
| --- | ---: | --- |
| cuDF device sync | 3.193166 | Filter + groupby aggregate, then CUDA stream synchronize |
| cuDF compact host rows | 1.1451525 | Convert compact grouped output to host rows |
| cuDF end-to-end | 4.340234 | Device sync plus compact host-row materialization |

Comparison with earlier pod diagnostics:

| Baseline | Median ms | Boundary |
| --- | ---: | --- |
| Python reference | 0.00914 / 0.00881 | In-process tiny fixture reference from Goals2523/2524 |
| PostgreSQL | 0.096 | Server-side combined SQL contract from Goal2523 |
| DuckDB | 1.215755 | Embedded single grouped SQL query from Goal2524 |
| cuDF | 4.340234 | GPU dataframe query plus compact host rows |

Interpretation: cuDF is the correct lightweight GPU baseline, but for an
eight-row fixture its GPU dataframe overhead dominates. This is expected. The
result is useful as a boundary check, not as a broad GPU-performance conclusion.

## Claim Boundary

This diagnostic result does not authorize public speedup, whole-DBMS,
authors-code, RayDB reproduction, true-zero-copy, or SQL-engine claims.

Allowed:

- cuDF can express the same RayDB-style tiny fixture contract.
- cuDF returns exact row parity for the five grouped result modes.
- On this pod and this tiny fixture, cuDF end-to-end diagnostic median was
  `4.340234 ms`.

Blocked:

- public speedup wording;
- SQL engine or DBMS claim;
- RayDB or authors-code comparison;
- true zero-copy claim;
- general GPU dataframe performance claim.

## Engineering Conclusion

For the RayDB-style app, our external baseline ladder is now:

1. PostgreSQL for independent SQL correctness and CPU DBMS diagnostic timing.
2. DuckDB for embedded analytical SQL diagnostic timing.
3. cuDF for lightweight GPU dataframe diagnostic timing.

We do not need HeavyDB, OmniSci, Crystal, or another server-style GPU database
for this benchmark slice unless later goals require full DBMS behavior.
