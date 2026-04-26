# Goal664: Large-Scale Apple RT vs Embree Performance

Date: 2026-04-20

Status: implemented benchmark fix; large-scale results recorded

## Purpose

Goal663 concluded that further blind Apple RT micro-optimizations are unlikely to close the remaining Embree gap. The next practical blocker was measurement quality: large Apple RT vs Embree runs were dominated by hidden full CPU-oracle computation before engine timing could complete.

Goal664 fixes that benchmark problem and records larger-scale Apple RT prepared-query vs Embree measurements with explicit correctness labeling.

## Harness Change

The Mac visibility/collision benchmark now supports:

```bash
--oracle-mode full
--oracle-mode backend_agreement
--oracle-mode none
```

Mode semantics:

- `full`: run the full CPU oracle and compare every backend to it.
- `backend_agreement`: skip the full CPU oracle at large scale and compare successful backends against the first successful backend's canonical any-hit rows.
- `none`: timing-only; does not establish correctness.

This keeps performance reports honest:

- small/medium correctness reports can still use `full`;
- large engine-performance reports can use `backend_agreement` without hiding CPU-oracle cost inside the benchmark;
- timing-only reports must say they are timing-only.

## Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal659_mac_visibility_collision_perf_test tests.goal578_apple_rt_backend_test tests.goal651_apple_rt_3d_anyhit_native_test tests.goal652_apple_rt_2d_anyhit_native_test && git diff --check
```

Result:

```text
Ran 15 tests in 0.067s
OK
git diff --check: clean
```

## Large Benchmark 1

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal659_mac_visibility_collision_perf.py \
  --oracle-mode backend_agreement \
  --warmups 0 \
  --repeats 2 \
  --target-sample-seconds 1 \
  --scale dense_blocked:large_dense_backend_agreement_1s,32768,4096 \
  --scale sparse_clear:large_sparse_backend_agreement_1s,32768,4096 \
  --backend apple_rt_prepared_query \
  --backend embree \
  --json-out docs/reports/goal664_apple_rt_large_backend_agreement_perf_2026-04-20.json \
  --md-out docs/reports/goal664_apple_rt_large_backend_agreement_perf_2026-04-20.md
```

Artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal664_apple_rt_large_backend_agreement_perf_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal664_apple_rt_large_backend_agreement_perf_2026-04-20.json`

Results:

| Case | Rays | Triangles | Backend | Per-query median | Correctness check |
| --- | ---: | ---: | --- | ---: | --- |
| dense blocked | 32768 | 8192 | Apple RT prepared-query | 0.025235305 s | backend agreement true |
| dense blocked | 32768 | 8192 | Embree | 0.014980764 s | backend agreement true |
| sparse clear | 32768 | 8192 | Apple RT prepared-query | 0.025134368 s | backend agreement true |
| sparse clear | 32768 | 8192 | Embree | 0.013994867 s | backend agreement true |

Ratios:

- Dense blocked: Apple RT prepared-query is `1.685x` slower than Embree.
- Sparse clear: Apple RT prepared-query is `1.796x` slower than Embree.

## Large Benchmark 2

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal659_mac_visibility_collision_perf.py \
  --oracle-mode backend_agreement \
  --warmups 0 \
  --repeats 1 \
  --target-sample-seconds 1 \
  --scale dense_blocked:xlarge_dense_backend_agreement_1s,65536,8192 \
  --backend apple_rt_prepared_query \
  --backend embree \
  --json-out docs/reports/goal664_apple_rt_xlarge_backend_agreement_perf_2026-04-20.json \
  --md-out docs/reports/goal664_apple_rt_xlarge_backend_agreement_perf_2026-04-20.md
```

Artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal664_apple_rt_xlarge_backend_agreement_perf_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal664_apple_rt_xlarge_backend_agreement_perf_2026-04-20.json`

Results:

| Case | Rays | Triangles | Backend | Per-query median | Correctness check |
| --- | ---: | ---: | --- | ---: | --- |
| dense blocked | 65536 | 16384 | Apple RT prepared-query | 0.052483096 s | backend agreement true |
| dense blocked | 65536 | 16384 | Embree | 0.031126191 s | backend agreement true |

Ratio:

- Dense blocked: Apple RT prepared-query is `1.686x` slower than Embree.

## Interpretation

Apple RT scales better than the pre-Goal662 path and the gap narrows compared with the 8192-ray / 2048-triangle small app benchmark, but it still does not beat Embree:

- Small measured case after Goal663: Apple RT about `1.925x` slower than Embree.
- Large dense case: Apple RT about `1.685x` slower than Embree.
- Extra-large dense case: Apple RT about `1.686x` slower than Embree.

The large-scale result is therefore:

> Apple RT prepared any-hit remains slower than Embree, but the gap narrows at larger dense scales and backend agreement confirms Apple RT and Embree produce the same canonical any-hit rows on the measured large cases.

## Next Engineering Decision

This result does not justify more blind micro-optimizations. The next serious choices are:

1. Add profiling instrumentation or run Metal System Trace to split CPU packing, command-buffer scheduling, GPU traversal, wait time, and result materialization.
2. Add a batched prepared API if profiling shows command-buffer scheduling/synchronization dominates.
3. Start a Metal 3 `MTLAccelerationStructure` research backend if the project explicitly wants Apple hardware RT to compete with or beat Embree.

Recommended next action:

- Do profiling before implementing batching or Metal 3, because the current benchmark evidence still cannot say whether the remaining `~1.7x` gap is GPU traversal, MPS API overhead, command-buffer sync, or Python/ctypes materialization.
