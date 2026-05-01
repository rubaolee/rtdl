# Goal1158 Gemini Verdict: Graph Raw Summary Contract Review

Date: 2026-04-30
Verdict: **ACCEPT**

## Analysis

### 1. Removal of Python Dict-Row Materialization
Goal1158 successfully implements the raw native row view contract for graph BFS and triangle-count summary modes. The changes in `examples/rtdl_graph_bfs.py` and `examples/rtdl_graph_triangle_count.py` correctly invoke `run_embree` and `run_optix` with `result_mode="raw"` when `output_mode="summary"`. The resulting native row views are processed by new direct summarization helpers in `src/rtdsl/oracle_runtime.py` (`summarize_bfs_row_view` and `summarize_triangle_row_view`), bypassing Python dictionary materialization entirely.

### 2. Preservation of Correctness and Honesty Boundaries
The implementation preserves existing correctness as evidenced by the regression suite results provided in the contract. Honesty boundaries are strictly maintained:
- Both graph examples include `_enforce_rt_core_requirement` logic that blocks `--require-rt-core` for the OptiX path until cloud-gated.
- The return payloads explicitly set `rt_core_accelerated: False` for these paths.
- The `honesty_boundary` and `ray_tracing_note` fields in the unified app and examples accurately describe the current state of acceleration.

### 3. RTX Speedup Wording
The goal correctly adheres to the restriction on public RTX speedup wording. The contract and code comments emphasize that this is a local macOS/Embree improvement with mocked OptiX evidence, and that public promotion is blocked until a real RTX pod run validates the performance.

### 4. Required Fixes
No fixes are required. The implementation is clean, the tests are focused and verify the contract (as shown in `tests/goal1158_graph_raw_summary_contract_test.py`), and the unified app benefits from the improvements without introducing premature claims.

## Verdict Summary
The changes are strictly within the bounded scope of Goal1158. They provide a meaningful optimization for local graph analytics development by removing unnecessary host-side overhead while maintaining a clear and honest boundary regarding future RTX acceleration.
