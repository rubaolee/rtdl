# Gemini Review: Goal2829 Fixed-Radius Graph Same-Stream Partials (2026-05-31)

## Review Goal

Perform an independent read-only review of Goal2829 Fixed-Radius Graph Same-Stream Partials.

## Files Inspected

- `docs/reports/goal2829_fixed_radius_graph_same_stream_device_partials_2026-05-31.md`
- `docs/reports/goal2829_fixed_radius_graph_same_stream_device_partials_pod/goal2829_summary.json`
- `tests/goal2829_fixed_radius_graph_same_stream_device_partials_test.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`

## Review Questions and Answers

### 1. Does Goal2829 preserve the app-agnostic native boundary, with no RTNN-specific or paper-specific ABI?

**Answer:** Yes. The native ABI, specifically `rtdl_optix_launch_fixed_radius_ranked_summary_aggregate_batch_graph_device_partials_3d`, is defined in `src/native/optix/rtdl_optix_api.cpp` and implemented in `src/native/optix/rtdl_optix_workloads.cpp`. Its parameters (graph handle, device pointers, stream pointers, etc.) are generic to OptiX operations. The headers (`rtdl_optix_prelude.h`) also define general-purpose OptiX related structures and functions. There is no evidence of RTNN-specific or paper-specific terminology or structures in the native C++ code or its public ABI.

### 2. Does the new native launch path really avoid producer-side `cuStreamSynchronize` and host partial-row download before the partner consumer?

**Answer:** Yes.
- The `docs/reports/goal2829...md` document explicitly states: "deliberately does not call `cuStreamSynchronize`" and "deliberately does not download partial rows." It also lists `producer_host_synchronization_used: false` and `host_partial_materialization_before_consumer: false` in the contract metadata.
- The inspection of `src/native/optix/rtdl_optix_workloads.cpp` for `launch_fixed_radius_ranked_summary_aggregate_batch_graph_device_partials_3d_optix` confirms that there are no calls to `cuStreamSynchronize` or data download operations.
- The test `tests/goal2829_fixed_radius_graph_same_stream_device_partials_test.py` also asserts this behavior.

### 3. Does the Python method `replay_same_stream_device_partials_summary_cupy()` expose an explicit opt-in path rather than making CUDA graph replay or partner consumption the default?

**Answer:** Yes. The `replay_same_stream_device_partials_summary_cupy()` method in `src/rtdsl/optix_runtime.py` is a distinct function within the `PreparedOptixFixedRadiusRankedSummaryAggregateBatchGraph3D` class, separate from the default `replay()` method. This design requires explicit invocation, making it an opt-in path. The `docs/reports/goal2829...md` also confirms this in its Purpose and Claim Boundary sections.

### 4. Does the CuPy consumer use the graph-owned partial device buffer and same native CUDA stream in a way that supports the narrow event/same-stream v2.5 continuation claim?

**Answer:** Yes.
- The `replay_same_stream_device_partials_summary_cupy()` method in `src/rtdsl/optix_runtime.py` retrieves `partials_device_ptr` and `cuda_stream_ptr` directly from the native call.
- It then uses `cupy.cuda.ExternalStream` to wrap the `cuda_stream_ptr` and `cupy.cuda.UnownedMemory` for `partials_device_ptr`.
- These CuPy objects are then passed to the CuPy kernel for reduction, ensuring the use of the graph-owned device buffer and the same native CUDA stream.
- The `docs/reports/goal2829...md` document and the assertions in `tests/goal2829_fixed_radius_graph_same_stream_device_partials_test.py` corroborate this.

### 5. Does the pod evidence support only the narrow parity claim against `graph.replay()` for the 4096-point, 4-request smoke?

**Answer:** Yes. The `docs/reports/goal2829_fixed_radius_graph_same_stream_device_partials_2026-05-31.md` document, specifically the "Pod Validation" section, and the `goal2829_summary.json` file both confirm that the validation was for a 4096-point, 4-request smoke test. The results showed exact parity between `graph.replay()` and `graph.replay_same_stream_device_partials_summary_cupy()` for key metrics like `query_count`, `bounded_neighbor_count`, `nearest_id_checksum`, `kth_id_checksum`, and `sum_distance`.

### 6. Are claim boundaries strict: no public RTDL-beats-CuPy, RTDL-beats-RTNN-paper, paper-reproduction, whole-app speedup, broad true-zero-copy, arbitrary partner, broad RT-core, or v2.5 release claims?

**Answer:** Yes. The `docs/reports/goal2829...md` document contains a dedicated "Claim Boundary" section that explicitly disclaims all the mentioned broad claims: "This does not authorize broad true-zero-copy, arbitrary partner continuation, public RTDL-beats-CuPy, public RTDL-beats-RTNN-paper, whole-app speedup, broad RT-core speedup, paper reproduction, or v2.5 release claims." The test file `tests/goal2829_fixed_radius_graph_same_stream_device_partials_test.py` also includes assertions to verify these claim boundaries.

### 7. Is the next-step recommendation reasonable: move toward typed primitive-payload column descriptors and partner-neutral lifetime ownership?

**Answer:** Yes. The "Next Step" section in `docs/reports/goal2829...md` clearly outlines this recommendation. It emphasizes generalizing the proof from a fixed aggregate summary consumer to a richer typed primitive-payload column handoff, addressing the challenge of publishing typed payload column descriptors and lifetime ownership in a partner-neutral way. This is a reasonable and logical progression for expanding the framework's capabilities responsibly.

## Verdict

`accept-with-boundary`
The implementation, tests, and documentation consistently demonstrate that Goal2829 achieves its narrow objective within well-defined boundaries. The solution preserves the app-agnostic native boundary, avoids producer-side stream synchronization and host partial-row downloads, and provides an explicit opt-in Python path for CuPy consumers to leverage the graph-owned device buffer and same native CUDA stream. The pod evidence supports the narrow parity claim, and all claim boundaries are strictly enforced. The recommended next steps are reasonable and align with a responsible development strategy. No correctness, contract, or claim-boundary problems were found.