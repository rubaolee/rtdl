# Goal2501: RayDB-Style OptiX Pod Validation Packet

Date: 2026-05-22

## Status

Goal2501 prepares the OptiX pod validation packet for the RayDB-style columnar
aggregate benchmark slice.

No pod evidence is claimed in this report. Local Goal2500 output shows OptiX was
skipped because the Mac environment could not load `libcuda.so.1`.

## Required Pod Setup Record

Record these fields in the final pod evidence report:

- SSH command used, including host, port, and key path;
- `git rev-parse HEAD`;
- `git status --short`;
- `python --version`;
- `nvidia-smi`;
- CUDA prefix and `nvcc --version` if available;
- OptiX header/library path used by the build;
- exact build command;
- exact test and runner commands.

## Required Commands

From a fresh checkout of the current branch:

```bash
git rev-parse HEAD
git status --short
PYTHONPATH=src:. python -m unittest tests.goal2498_raydb_style_optix_count_sum_parity_test
PYTHONPATH=src:. python -m unittest tests.goal2495_raydb_style_cpu_reference_fixture_test tests.goal2496_raydb_style_embree_lowering_decision_test tests.goal2497_raydb_style_embree_count_sum_parity_test tests.goal2498_raydb_style_optix_count_sum_parity_test tests.goal2499_raydb_style_lowering_plan_test tests.goal2500_raydb_style_backend_matrix_runner_test
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend optix --mode all
PYTHONPATH=src:. python scripts/goal2500_raydb_style_backend_matrix.py --backends cpu_python_reference embree optix --repeats 5 --output docs/reports/goal2501_raydb_style_backend_matrix_pod_2026-05-22.json
```

If the pod requires native library rebuild, first use the repository's existing
OptiX build procedure and record the command verbatim.

## Acceptance Criteria

The OptiX app payload must include:

- `"backend": "optix"`;
- `"all_match_cpu_reference": true`;
- `"native_abi_added": false`;
- `"contract": "columnar_grouped_aggregate_optix_columnar_payload"`;
- `"rt_core_accelerated": true`;
- `lowering_plan.true_zero_copy_authorized == false`;
- `lowering_plan.uses_compatibility_wrapper == true`;
- no min/max/avg native mode claim.

The matrix JSON must include:

- `cases.optix.status == "ok"`;
- `cases.optix.all_match_cpu_reference == true`;
- count and sum mode rows with `matches_cpu_reference == true`;
- the Goal2500 diagnostic claim boundary.

## Claim Boundary

Passing this packet would establish fresh OptiX runtime parity for the synthetic
count/sum contract only. It would not authorize:

- RayDB reproduction;
- authors-code comparison;
- SQL engine or DBMS behavior;
- public speedup wording;
- true zero-copy wording;
- whole-app claims;
- new app-specific native ABI.
