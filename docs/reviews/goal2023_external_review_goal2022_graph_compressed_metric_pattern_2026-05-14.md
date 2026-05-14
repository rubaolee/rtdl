# Goal2023 External Review for Goal2022 Graph Compressed Metric Pattern

Date: 2026-05-14
Reviewer: Gemini CLI Agent

## Verdict: accept-with-boundary

Goal2022 demonstrates a well-conceived and executed implementation for a generic compressed metric-table continuation contract. The new helper function `partner_metric_table_reduce_repeated_pattern` is appropriately generalized within `rtdsl/partner_adapters.py` and exposed via the public API. Its usage in the graph control app is constrained, avoiding the introduction of graph-specific semantics into the native engine. The `assume_aligned_output` parameter establishes a clear contract boundary, and the provided pod artifacts fully corroborate the documented correctness and timing claims. Furthermore, the report explicitly details a rejected experiment and rigorously bounds the claims of this work, which is critical for maintaining clarity on its scope.

---

## Questions and Answers:

### 1. Is `partner_metric_table_reduce_repeated_pattern(...)` a generic compressed metric-table continuation contract rather than graph-app customization?

**Answer:** Yes. The `partner_metric_table_reduce_repeated_pattern` function is implemented to operate on generic metric/value patterns, supporting various reduction types ('sum', 'max', 'min'). Its docstring, public exposure in `__init__.py`, and lack of graph-specific logic in `partner_adapters.py` confirm its generic nature. While used by the graph control app, the function itself is not customized for graph applications; the graph-specific interpretation occurs on the Python side, external to the helper. The Goal2022 report explicitly states: "It is a generic repeated metric-table continuation contract," and that "This does not add BFS, triangle counting, visibility, or graph traversal semantics to the native engine."

### 2. Does `assume_aligned_output=True` keep a clear contract boundary and avoid unsafe overgeneralization?

**Answer:** Yes. The `assume_aligned_output=True` parameter clearly defines a contract where input `metric_keys` are expected to align 1:1 and in order with `output_metric_keys`. This contract is enforced by a `ValueError` check (`aligned repeated metric pattern requires one value per output metric key`) if the lengths do not match, preventing accidental misuse or unsafe overgeneralization. This explicit validation ensures that the optimized execution path, which bypasses explicit key mapping, is only taken when the caller explicitly guarantees alignment.

### 3. Does the graph control app use the new helper without adding graph semantics to the native RTDL engine?

**Answer:** Yes. The `_graph_cupy_continuation` in `examples/rtdl_control_apps_cupy_rawkernel.py` utilizes `partner_metric_table_reduce_repeated_pattern` by passing generic numerical arrays (`GRAPH_SUM_METRIC_IDS`, `GRAPH_SUM_METRIC_VALUES`, etc.). The graph-specific meaning (e.g., "discovered_edge_count") is applied during Python-side interpretation of the numerical results, not embedded within the `partner_metric_table_reduce_repeated_pattern` function or any underlying low-level kernels. Test assertions explicitly confirm the absence of graph-specific raw kernels, and the report emphasizes that the work "does not add BFS, triangle counting, visibility, or graph traversal semantics to the native engine."

### 4. Do the pod artifacts support the documented correctness and timing claims?

**Answer:** Yes. The pod artifacts (`goal2022_pod_graph_host_compressed_metric_pattern_1000.json` and `goal2022_pod_graph_host_compressed_metric_pattern_100000_v2only.json`) consistently support the claims made in the Goal2022 report. Both artifacts confirm correctness by showing `matches_v1_8_python_rtdl_oracle: true` (where applicable). The performance ratios and median timings presented in the report's table precisely match the data found in the JSON files. Specifically, the significant speedup for `graph_analytics` at 1000 copies and the v2-only scaling probe at 100,000 copies with its corresponding skipped v1.8 timing are all accurately reflected.

### 5. Does the report correctly document the rejected `cp.tile(...)` experiment and keep the graph claim bounded: authored graph control row only, not broad graph traversal acceleration, not RT-core proof, not v2.0 release authorization?

**Answer:** Yes. The Goal2022 report meticulously documents the "Rejected Experiment" of using `cp.tile(...)`, providing a clear rationale for its rejection (slower at scale due to overhead). Crucially, the "Boundary" section of the report explicitly limits the scope of the claims. It states that the work is "not broad graph traversal acceleration," "does not prove arbitrary BFS, triangle counting, or visibility algorithms are accelerated by RT cores," "does not authorize a whole-app graph speedup claim," and that "v2.0 release authorization still requires the final release audit and required external consensus." These statements, also reinforced by test checks, effectively bound the claims and prevent overreach.
