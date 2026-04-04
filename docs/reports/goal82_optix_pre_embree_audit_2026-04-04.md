# Goal 82 Report: OptiX Pre-Embree Audit

Date: 2026-04-04
Status: complete

## Scope

This audit is the stopgate before Embree follow-up work.

It reviews the published OptiX performance path through:

- focused local validation on the current Mac workspace
- focused Linux validation on a clean clone at published head `b04033b`
- Linux reruns of the accepted long OptiX surfaces

## Validation Slices

### Local

Static validation:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m py_compile \
  src/rtdsl/datasets.py \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/embree_runtime.py \
  scripts/goal50_postgis_ground_truth.py \
  scripts/goal69_pip_positive_hit_performance.py \
  scripts/goal71_prepared_backend_positive_hit_county.py \
  scripts/goal77_runtime_cache_measurement.py \
  tests/goal80_runtime_identity_fastpath_test.py \
  tests/goal69_pip_positive_hit_performance_test.py \
  tests/goal71_prepared_backend_positive_hit_county_test.py \
  tests/goal50_postgis_ground_truth_test.py \
  tests/optix_embree_interop_test.py
```

Focused unit slice:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal76_runtime_prepared_cache_test \
  tests.goal28c_conversion_test \
  tests.goal69_pip_positive_hit_performance_test \
  tests.goal71_prepared_backend_positive_hit_county_test \
  tests.goal50_postgis_ground_truth_test \
  tests.optix_embree_interop_test \
  tests.goal79_linux_performance_reproduction_matrix_test
```

Result:

- `52` tests
- `OK`

### Linux Clean Clone

Clone:

- `/home/lestat/work/rtdl_goal82_audit`
- head: `b04033b`

Static validation and focused unit slice matched the local commands above.

Result:

- `52` tests
- `OK`

## Long-Surface Reruns

### Prepared Boundary

Linux clean-clone rerun on the accepted long exact-source surface:

- artifact:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal82_optix_pre_embree_audit_artifacts_2026-04-04/prepared/summary.json`
- package:
  - execution-ready / prepacked
- row count: `39073`
- parity: exact on both reruns

Measured:

- PostGIS:
  - `3.139067540 s`
  - `3.142702609 s`
- OptiX prepared `.run()`:
  - run 1: `3.429287890 s`
  - run 2: `1.147425041 s`

Audit interpretation:

- the first prepared rerun did **not** beat PostGIS on this clean-clone audit
  rerun
- the second prepared rerun did beat PostGIS strongly
- so the prepared-boundary win is still real as a warmed repeated prepared-run
  result, but it is not stable enough to describe as an unconditional first-run
  prepared win

### Repeated Raw-Input Boundary

Linux clean-clone rerun on the accepted long exact-source surface:

- artifact:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal82_optix_pre_embree_audit_artifacts_2026-04-04/raw/summary.json`
- package:
  - repeated raw-input end-to-end
- row count: `39073`
- parity: exact on all reruns

Measured:

- PostGIS:
  - `3.235889516 s`
  - `3.257689920 s`
  - `3.224879186 s`
- OptiX:
  - first run: `3.573603315 s`
  - repeated run 2: `1.151226476 s`
  - repeated run 3: `1.090809764 s`

Audit interpretation:

- this reproduces the published Goal 81 story closely
- the first raw-input call is still slower than PostGIS
- repeated raw-input calls clearly beat PostGIS

## Audit Conclusion

The OptiX slice is strong enough to proceed to Embree work, with one important
clarification:

- the strongest current OptiX performance claim is **Goal 81**
  - repeated raw-input end-to-end wins on the accepted long exact-source
    county/zipcode surface
- the prepared-boundary story remains useful, but should be read as a warmed
  repeated prepared-run win rather than a guaranteed cold prepared first-run
  win

So the audit outcome is:

- focused local validation: clean
- focused Linux validation: clean
- raw-input long exact-source win: reproduced
- prepared-boundary long exact-source win: partially reproduced, with a colder
  first-run caveat

That is sufficient to move on to Embree, because the stack-level feasibility
and performance story now rests on the stronger raw-input end-to-end surface.
