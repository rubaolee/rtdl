# Goal 391 Review: v0.6 RT-Kernel BFS Oracle Truth Path

Date: 2026-04-14
Status: accepted

## Overview

Goal 391 establishes the first bounded native/oracle execution path for the RTDL graph-kernel line. This transition is critical for moving beyond Python-only reference execution while maintaining the rigorous row parity standards established in earlier milestones.

## Technical Analysis

### Native ABI and Oracle Implementation

The additions to `src/native/oracle/rtdl_oracle_abi.h` and `src/native/oracle/rtdl_oracle_api.cpp` are clean and consistent with the existing oracle patterns:

- **Data Structures**: `RtdlFrontierVertex` and `RtdlBfsExpandRow` provide a compact representation for graph frontier expansion.
- **CSR Validation**: The implementation in `rtdl_oracle_run_bfs_expand` includes exhaustive validation of the CSR structure (offsets, column indices, vertex bounds), which is essential for stability when crossing the Python/C++ boundary.
- **Expansion Logic**: The BFS step correctly implements visited filtering and optional deduplication. The deterministic sort by `(level, dst_vertex, src_vertex)` ensures stable parity against the Python reference.

### Python Runtime Integration

The updates to `src/rtdsl/oracle_runtime.py` and `src/rtdsl/runtime.py` correctly surface the new native capability:

- **Binding**: `ctypes` bindings for the new BFS structs and function are correctly defined.
- **Normalization**: `_normalize_records` now handles `graph_csr`, `vertex_frontier`, and related graph types, allowing `run_cpu(...)` to accept both logical objects and raw mappings.
- **Control**: The explicit check in `_validate_oracle_supported_inputs` correctly permits `bfs_discover` while continuing to block `triangle_match`, adhering to the goal's honesty boundary.

### Verification

The verification suite is comprehensive:

- **Parity**: `tests/goal391_v0_6_rt_graph_bfs_oracle_test.py` proves that `run_cpu(...) == run_cpu_python_reference(...)` for various frontier and graph configurations.
- **Error Handling**: Tests confirm that native-layer validation errors (e.g., invalid vertex IDs) are correctly propagated back to Python as `RuntimeError`.
- **Regressions**: The goal maintains the integrity of the Python-only graph path (Goal 389) and core project quality.

## Conclusion

The implementation of Goal 391 is successful. It provides a solid foundation for further native graph-kernel expansion (e.g., triangle count) and eventual lowering to GPU backends. The code quality, validation rigor, and parity verification meet the project's standards.
