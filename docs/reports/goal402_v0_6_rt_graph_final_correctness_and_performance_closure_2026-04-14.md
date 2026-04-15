# Goal 402 Report: v0.6 RT Graph Final Correctness And Performance Closure

Date: 2026-04-14

## Conclusion

The corrected RT `v0.6` graph line is now closed as a bounded correctness and
performance package.

The main claim that is now supported is:

- RTDL can implement graph workloads through the RT kernel path.
- The graph path is correct on the validated bounded and large-batch slices.
- The graph path is performance-credible on real public datasets, especially on
  OptiX and Vulkan.

## Primary report artifacts

- Main final validation report:
  - [graph_rt_validation_and_perf_report_2026-04-14.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/graph_rt_validation_and_perf_report_2026-04-14.md)
- Earlier consolidated report:
  - [v0_6_rt_graph_correctness_and_performance_report_2026-04-14.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/v0_6_rt_graph_correctness_and_performance_report_2026-04-14.md)
- Windows benchmark handoff imported into repo:
  - [windows_codex_rt_graph_benchmark_handoff_2026-04-14.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/windows_codex_rt_graph_benchmark_handoff_2026-04-14.md)

## Correctness closure

### Bounded all-engine correctness

Goal 400 already closed bounded PostgreSQL-backed correctness for:

- Python
- native/oracle
- Embree
- OptiX
- Vulkan
- PostgreSQL

Reference review:

- [gemini_goal400_v0_6_postgresql_backed_all_engine_correctness_gate_review_2026-04-14.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal400_v0_6_postgresql_backed_all_engine_correctness_gate_review_2026-04-14.md)

### Large-batch correctness

The large-batch Embree `triangle_count` regression that had remained open was
fixed by separating the endpoint mark buffers in the Embree triangle probe path.

Imported fix surface:

- [rtdl_embree_api.cpp](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_api.cpp)

Imported regression coverage:

- [goal396_v0_6_rt_graph_triangle_embree_test.py](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal396_v0_6_rt_graph_triangle_embree_test.py)

Focused local verification after sync:

- `python3 -m unittest tests.goal396_v0_6_rt_graph_triangle_embree_test -v`
  - `Ran 5 tests`
  - `OK`

The imported final validation report states that large-scale correctness matched
across:

- `cpu`
- `embree`
- `optix`
- `vulkan`
- `postgresql`

on the tested public dataset slices.

## Performance closure

The strongest reported large-public-dataset anchors from the imported final
report are:

### `soc-LiveJournal1`, triangle probe, 5M canonical undirected edges

- Embree: `3.518s`
- OptiX: `0.555s`
- Vulkan: `0.552s`
- PostgreSQL query: `100.87s`

### `com-Orkut`, triangle probe, 5M canonical undirected edges

- Embree: `3.595s`
- OptiX: `1.869s`
- Vulkan: `1.872s`
- PostgreSQL query: `0.976s`

### `soc-LiveJournal1`, BFS, 1M directed-edge slice in the imported final report

- Embree: `0.297s`
- OptiX: `0.139s`
- Vulkan: `0.139s`
- PostgreSQL query: `0.316s`

### `com-Orkut`, BFS, 5M directed-edge benchmark handoff anchor

- Embree: `1.077s`
- OptiX: `0.202s`
- Vulkan: `0.202s`
- PostgreSQL query: `0.575s`

## Practical interpretation

The defensible performance statement is:

- RTDL graph is not a toy or an obviously uncompetitive path.
- OptiX and Vulkan are the main RTDL graph backends to carry forward.
- Embree is functionally important and correct, but slower on the larger graph
  kernels.
- PostgreSQL remains a useful correctness and external-baseline anchor, but can
  be much slower on some triangle workloads.

The statement that remains too strong and should still be avoided is:

- RTDL graph beats specialized graph systems in general.

That is not what the evidence shows.

## Final version-level answer

For the corrected RT `v0.6` graph line, the answer to "can we do graph?" is:

- yes

More precisely:

- RTDL can express graph workloads through RT-kernel traversal/intersection.
- correctness is closed on the validated slices.
- performance is credible enough to justify the approach.
