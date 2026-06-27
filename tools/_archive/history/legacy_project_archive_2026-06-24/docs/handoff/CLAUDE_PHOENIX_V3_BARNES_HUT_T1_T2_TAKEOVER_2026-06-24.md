# Claude Takeover: Phoenix V3 Barnes-Hut T1/T2

Date: 2026-06-24
Audience: Claude / next primary AI
Scope: Phoenix V3 only. No V4, no embedding, no C ABI, no release wording.
Status: handoff after user lost confidence in Codex process churn.

## Read first

This is not a review packet. It is an execution handoff. The next agent should
not create another audit/review/promotion milestone before moving a named
scorecard blocker.

Required context:

- `docs/handoff/STOP_THE_CHURN_PHOENIX_V3_HIT_THE_BLOCKER_2026-06-24.md`
- `docs/rebuild/v3/v3_engineering_targets_fused_barnes_hut_trunk_2026-06-24.md`
- `docs/reviews/phoenix_v3_revised_m72_plan_target_the_blocker_2026-06-24.md`
- Evidence: `docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_blocker_bound_pod_20260624_091320/summary.json`

Hard rule: progress means a named scorecard blocker moves on same-contract,
same-hardware evidence, with `runtime_executed: true`,
`host_materialization_in_hot_path: false`, and `win_source` recorded.

## Current truth

Phoenix V3 is not release-ready. The serious paired V2.14 vs Phoenix V3 run was
only about `1.012x` geomean, so broad "V3 is faster than V2.x" wording is not
authorized.

The immediate blocker is Barnes-Hut / aggregate-tree, frozen as:

- blocker id: `set_a_barnes_hut_app_geomean_0_844x`
- current scorecard value: about `0.844x`
- target: move toward or above parity by productized runtime trunk work, not by
  explaining the number away.

The most recent Barnes-Hut focused POD result is useful but insufficient:

- path: `prepared_execution_session_runner`
- evidence dir:
  `docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_blocker_bound_pod_20260624_091320`
- checks: no failures in the M72 harness
- runner vs existing fused Numba control geomean: `0.9997602284020717`
- historical slow OptiX-frontier reference vs runner geomean:
  `12.75587197083642`
- honest interpretation: the runner preserves the current fused partner speed,
  but does not move the real scorecard blocker by itself. The 12.75x number is
  against a known historical no-go reference and must not be sold as the V3 win.

Side evidence exists for RTNN scorecard-bound runs, but it is not the current
priority:

- `docs/rebuild/v3/evidence/phoenix_v3_rtnn_scorecard_bound_shell_262144_20260624_1030`
- `docs/rebuild/v3/evidence/phoenix_v3_rtnn_scorecard_bound_clustered_262144_20260624_1030`
- shell 262144: hot about `0.991x`, cold about `1.671x`, runner wall about
  `1.353x`
- clustered 262144: hot about `0.996x`, cold about `1.596x`, runner wall about
  `1.041x`

Do not continue RTNN until Barnes-Hut T1/T2 is resolved.

## Important correction: the native RT fused path is not implemented

The design target mentions native RT fused traversal:
`rtdl_optix_prepare/run/destroy_aggregate_tree_fused_weighted_vector_sum_2d`.
The symbols exist, but the native implementation currently fails closed.

Verified hook points:

- `src/native/optix/rtdl_optix_api.cpp:4254`
  `rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d`
- `src/native/optix/rtdl_optix_api.cpp:4284`
  prepare throws:
  `AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE native OptiX traversal is not implemented yet`
- `src/native/optix/rtdl_optix_api.cpp:4291`
  `rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d`
- `src/native/optix/rtdl_optix_api.cpp:4319`
  run throws:
  `AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE native OptiX run path is not implemented yet`
- `src/rtdsl/optix_runtime.py:2760`
  Python wrapper `prepare_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_optix`
  exists, but it will hit the native fail-closed path.
- `src/rtdsl/aggregate_tree_reference.py:1172`
  native RT fused contract is still the contract/status source.

This means T2 is not just Python routing if the intended source of the win is
RT traversal. There are two honest paths:

1. Implement the native RT fused traversal in C++/OptiX and then route it through
   the V3 runner.
2. Admit that Barnes-Hut's current productized V3 path is a Numba CUDA fused
   partner trunk, not an RT-core fused traversal, and use T1 to decide whether
   this can still move the blocker.

Do not imply native RT fused traversal is already live.

## Current live Barnes-Hut productized path

The path that actually runs today is the Numba CUDA fused partner path:

- app front door:
  `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py:2448`
- it builds bodies/tree, prepares Numba CUDA fused weighted vectors, and calls:
  `rt.run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(...)`
  at `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py:2495`
- productized runner:
  `src/rtdsl/prepared_execution.py:2723`
  `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session`
- current runner constraint:
  `src/rtdsl/prepared_execution.py:2754`
  it requires `partner='numba_cuda'`
- scorecard binding is already present at
  `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py:2514`
  with id `set_a_barnes_hut_app_geomean_0_844x`

Important: despite earlier strategic wording about reusing M43 CuPy grouped
reduction, the current Barnes-Hut front door is not wired to the M43 CuPy
grouped-reduction runner. It is wired to the aggregate-tree fused Numba CUDA
partner session. If Claude wants to use M43 here, that is new engineering, not
already-done work.

## Immediate job: T1 probe, then T2 decision

Do T1 before changing the architecture. The goal is to locate where the 0.844x
goes.

Create or minimally extend a focused probe, for example:

`scripts/v3_phoenix_barnes_hut_t1_phase_residency_probe.py`

The probe should compare, at serious but bounded sizes such as 32768, 65536,
and 131072 bodies:

1. historical prepared OptiX frontier + Numba reference route, as a no-go
   control only;
2. existing app front-door fused Numba CUDA control;
3. current prepared-session runner fused Numba CUDA path;
4. native RT fused OptiX attempt, expected to fail closed unless native C++ has
   been implemented.

Required JSON fields per route:

```json
{
  "route_id": "...",
  "body_count": 131072,
  "phase_seconds": {
    "prepare": 0.0,
    "traverse": 0.0,
    "accumulate": 0.0,
    "boundary": 0.0
  },
  "runtime_executed": true,
  "internal_residency_measured": true,
  "host_materialization_in_hot_path": false,
  "win_source": "residency_wall",
  "same_contract_incumbent": "set_a_barnes_hut_app_geomean_0_844x",
  "result_vs_incumbent": 0.0,
  "rt_cores_used": false,
  "native_rt_fused_symbol_available": true,
  "native_rt_fused_runtime_implemented": false,
  "native_rt_fused_failure_reason": "..."
}
```

T1 exit statement must be one sentence:

- "0.844x is dominated by hot-path host frontier/materialization", or
- "0.844x is dominated by repeated prepare/packing", or
- "0.844x is dominated by kernel/traversal time", or
- "current scorecard metric is not measuring this trunk row and needs a
  scorecard row-binding correction before claiming movement."

## POD commands

POD SSH:

```powershell
ssh root@213.173.108.14 -p 11592 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Remote working tree:

```bash
cd /root/rtdl_v3_rebuild_20260620/current
export NUMBA_CUDA_PREFIX=/root/rtdl_v3_rebuild_20260620/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export CUDA_HOME=$NUMBA_CUDA_PREFIX
export CUDA_PATH=$NUMBA_CUDA_PREFIX
export PATH=$NUMBA_CUDA_PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:${LD_LIBRARY_PATH:-}
export PYTHONPATH=src:.
/root/rtdl_v3_rebuild_20260620/.venv/bin/python <script>
```

Known GPU:

```text
NVIDIA RTX 4000 Ada Generation, driver 550.127.05
```

## Do not do these things

- Do not create another review/audit/completion/promotion document before T1/T2
  produces a measurement.
- Do not wait for Claude/Gemini/Antigravity to approve trunk implementation.
- Do not run all-app.
- Do not claim V3 release readiness.
- Do not claim broad V3-over-V2 speedup.
- Do not claim RT-core Barnes-Hut fused traversal unless the native fail-closed
  C++ path has been replaced and measured.
- Do not count the 12.75x historical no-go comparison as the blocker moving.

## If T1 shows native RT fused implementation is required

Then the next engineering target is not a review packet. It is native code:

- replace the fail-closed throws in
  `src/native/optix/rtdl_optix_api.cpp:4254-4323`;
- implement the prepared handle and run path using existing OptiX workload
  infrastructure;
- emit device-resident output columns and phase timing;
- preserve the app-agnostic contract;
- add an equivalence gate against the Numba fused partner route;
- then rerun the same T1/T2 focused measurement.

If this cannot be done within the remaining project budget, state that V3 cannot
honestly be a broad performance release on Barnes-Hut yet.

## Current responsibility split

Codex did not finish T1/T2. The most useful thing produced is this handoff plus
the verified correction that native RT fused traversal is not live. Claude should
start at T1 probe implementation, not at another plan or review.

## Non-authorization

This handoff authorizes no release, no all-app run, no public speedup wording,
no V4, no embedding, no C ABI, and no true-zero-copy claim. The release gate
remains `redo_required`.
