# Goal755 Scaled DB Phase Profiler Plan

## Purpose

The current DB app remains classified as `python_interface_dominated`. Before changing the DB runtime, Goal755 should produce scaled phase evidence rather than optimizing blindly.

## Scope

Extend `/Users/rl2025/rtdl_python_only/scripts/goal693_db_phase_profiler.py` with a `--copies` option so the unified database app can be profiled beyond the tiny tutorial fixture.

The profiler should report:

- input construction time;
- backend selection;
- native prepared dataset build time;
- query/materialization time for `conjunctive_scan`, `grouped_count`, and `grouped_sum`;
- close time;
- Python postprocess time where applicable;
- total app wall time.

## Linux Evidence

Run the scaled profiler on `lestat-lx1` for:

- `cpu_reference` or `cpu_python_reference` where applicable;
- `embree`;
- `optix`;
- `vulkan` if available.

The first target is diagnostic, not a speedup claim. The output should identify the dominant DB app bottleneck and recommend the next optimization.

## Honesty Boundary

This goal does not make an RTX RT-core speedup claim. GTX 1070 evidence remains native/backend behavior evidence only. If OptiX is tested on GTX 1070, report it as OptiX backend evidence, not RT-core acceleration evidence.

## Acceptance Criteria

- `--copies` is implemented and tested for `regional_dashboard`, `sales_risk`, and `all`.
- Existing profiler behavior remains backward compatible when `--copies` is omitted.
- Linux scaled JSON evidence is written under `/Users/rl2025/rtdl_python_only/docs/reports/`.
- The final report recommends the next DB optimization based on measured phases.
- At least 2-AI consensus is recorded for the plan or finish review.
