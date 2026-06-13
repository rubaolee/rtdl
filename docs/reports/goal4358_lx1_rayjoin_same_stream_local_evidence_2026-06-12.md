# Goal4358 Local Linux RayJoin Same-Stream Evidence

Date: 2026-06-12

Status: local Linux pipeline evidence accepted; not public RT-core evidence.

## Machine

| Field | Value |
| --- | --- |
| Host | `lx1` / `192.168.1.20` |
| OS | Ubuntu 24.04.4, Linux 6.17 |
| GPU | NVIDIA GeForce GTX 1070, compute 6.1, driver 580.126.09 |
| RT cores | No |
| CUDA | 12.0 |
| Embree | 4.3.0 |
| RTDL commit | `013d477ff718d63e24b5f1a048cbf1b6ba2a234c` |

Boundary: this machine validates Linux build/runtime correctness, same-stream protocol, and Embree/OptiX plumbing. It cannot validate an NVIDIA RT-core speedup because GTX 1070 predates RT cores.

## Runner Fixes

The external RayJoin same-stream runner now works on both RTX pods and local non-RTX Linux boxes:

| Commit | Fix |
| --- | --- |
| `336cc34d` | Parameterized RayJoin CUDA arch with `RAYJOIN_CUDA_ARCH`; local run used `61`, pod default remains `86`. |
| `dce1bb14` | Added `RAYJOIN_EXTRA_CMAKE_PREFIX_PATH` so vendored `gflags`/`glog` can be used without system apt access. |
| `1771559e` | Added `glog`/`gflags` include paths to RayJoin PTX custom compile commands. |
| `8b616c1a` | Exposed PIP native phase timings so OptiX hot time can be explained by candidate write/refine phases. |
| `ae2113cd` | Replaced the regressing shared-GEOS mutex path with per-worker prepared GEOS contexts for Embree PIP count. |
| `013d477f` | Added conservative hardware classification so GTX OptiX runs are not mislabeled as RT-core accelerated. |

Focused tests passed:

```bash
py -3 -m unittest tests.goal2198_rayjoin_same_query_pod_runner_test
```

## 1k End-To-End Smoke

Artifact directory on `lx1`:

```text
/home/lestat/work/goal4358_same_stream_lx1_smoke/artifacts
```

RayJoin was built from upstream commit `02bf6220d6d20b04af77ee20364eced75cc029c9` plus the Goal2195 query-stream export patch. It exported PIP and LSI streams, and RTDL consumed those exact streams.

| Workload | Backend | Query count | Row count | Median ms | Parity |
| --- | --- | ---: | ---: | ---: | --- |
| LSI | CPU | 1,000 | 99 | 590.758 | pass |
| LSI | Embree | 1,000 | 99 | 2129.602 | pass |
| LSI | OptiX | 1,000 | 99 | 31.143 | pass |
| PIP | CPU | 1,000 | 80 | 200.673 | pass |
| PIP | Embree | 1,000 | 80 | 32.750 | pass |
| PIP | OptiX | 1,000 | 80 | 1.506 | pass |

This is a protocol smoke, not a meaningful RT-core performance comparison.

## 100k PIP Same-Stream Check

Artifact directory on `lx1`:

```text
/home/lestat/work/goal4358_same_stream_lx1_pip100k/artifacts
```

The final artifact is:

```text
goal4354_pip100k_exact_prepared_points_lx1_summary_metadata_labeled.json
```

It used the new RTDL v2.12 `exact_prepared_points` PIP count path. The Embree row below is the optimized per-worker GEOS result. Hardware metadata in the artifact marks this GTX 1070 run as `nvidia_rt_core_hardware=false` and `rt_core_accelerated=false`.

RayJoin original logs:

| RayJoin mode | Query ms | Build index ms | Adaptive grouping ms | Built-in check |
| --- | ---: | ---: | ---: | --- |
| Grid | 30.673700 | 4.173990 | n/a | n/a |
| LBVH | 49.910300 | 4.971980 | n/a | pass |
| RT | 2.602740 | 1.637940 | 1.322980 | pass |

RTDL same-stream scalar count:

| RTDL backend | RT-core hw | Route | Query count | Count | Hot median ms | Native traversal ms |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| OptiX | no | `prepared_exact_closed_shape_membership_prepared_points_scalar_count` | 100,000 | 8,686 | 14.881459 | 14.528547 |
| Embree | no | `prepared_embree_native_scalar_count` | 100,000 | 8,686 | 9.983191 | 9.194794 |

Direct comparison against RayJoin RT Query:

| Workload | Backend | RayJoin RT query ms | RTDL hot query ms | RayJoin RT / RTDL |
| --- | --- | ---: | ---: | ---: |
| PIP | OptiX | 2.602740 | 14.881459 | 0.175x |
| PIP | Embree | 2.602740 | 9.983191 | 0.261x |

Embree PIP optimization audit:

| Embree path | Hot median ms | Native traversal ms | Readout |
| --- | ---: | ---: | --- |
| Original prepared scalar count before PIP parallelization | 35.297965 | 34.579573 | Correct but underused CPU parallelism during exact GEOS refinement. |
| Shared prepared GEOS plus mutex (`a3cd002b`) | ~90.996 | n/a | Rejected regression; mutex serialized GEOS calls and added thread overhead. |
| Per-worker prepared GEOS contexts (`ae2113cd`/`013d477f`) | 9.983191 | 9.194794 | Accepted local CPU optimization; exact count remains 8,686. |

OptiX native phase medians in the hot exact-prepared-points call:

| Phase | Median ms |
| --- | ---: |
| Point pack | 0.000000 |
| Point upload | 0.000000 |
| Candidate count pass | 0.000000 |
| Candidate write pass | 9.030216 |
| Candidate download | 0.027267 |
| Exact refine | 5.451010 |
| Raw candidates | 8,794 |
| Emitted count | 8,686 |

Correctness: RTDL OptiX and RTDL Embree both returned `8,686`; RayJoin RT built-in PIP check passed. RayJoin PIP logs do not export the positive count, so the external count comparison is RTDL cross-backend plus RayJoin built-in validation.

## Interpretation

The 100k local result is reasonable for this machine:

- RayJoin RT is a purpose-built C++/CUDA/OptiX PIP implementation and is very fast even on a non-RT-core GTX 1070.
- RTDL OptiX v2.12 now reuses prepared query point columns, removing hot-call point repack/reupload, but the exact PIP route still spends about 9.03 ms in candidate write and about 5.45 ms in host exact refinement on this GTX 1070 run.
- RTDL Embree is CPU-only and exact; after per-worker prepared GEOS contexts, its hot median is about 9.98 ms, much better than the old 35.30 ms serial-refine path and faster than RTDL OptiX on this non-RT-core local box.
- RayJoin RT remains faster on this PIP100k stream because it is a specialized C++/CUDA/OptiX implementation with a 2.60 ms query phase; RTDL's local result is now a stronger CPU baseline, not a public RT-core win.
- The local result should not be worded as RT-core acceleration evidence. It says the same-stream comparison machinery and v2.12 exact-prepared-points route are ready to move to a real RTX pod.

## Next Pod Requirement

For public RT-core-vs-Embree wording, rerun the same packet on an RTX pod:

- set `RAYJOIN_CUDA_ARCH` to the pod GPU architecture;
- keep `--pip-rtdl-count-mode exact_prepared_points`;
- include Embree in the same artifact;
- report hardware explicitly and avoid using local GTX 1070 results as RT-core evidence.
