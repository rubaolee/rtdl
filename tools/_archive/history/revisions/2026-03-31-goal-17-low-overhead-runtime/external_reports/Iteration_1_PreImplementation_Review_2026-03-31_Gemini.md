I will begin by reading the Goal 17 plan, specification, and pre-implementation report, along with the architectural context and performance evidence, to evaluate the proposed runtime overhead reduction strategy.

I will now examine the current implementation of the Embree runtime, the native C++ interface, and the `lsi` and `pip` workloads to determine the feasibility of introducing the proposed low-overhead changes.

I will now examine `src/rtdsl/runtime.py` to understand the implementation of `_normalize_records` and confirm the overhead associated with input normalization.

1. **Decision**: `Consensus to begin implementation.`

2. **Short reasoning**:
The current RTDL Embree runtime is heavily bottlenecked by Python's host-path overhead, with `pip` being ~37x slower than a pure native implementation. The proposed Goal 17 strategy correctly identifies that while the Python DSL is excellent for authoring, it is the wrong data plane for high-performance execution. By introducing a "prepare once, run many" pattern and native-ready packed buffers for `lsi` and `pip`, we can decouple the control plane from the data path, which is the necessary architectural shift to close the performance gap while keeping the user-facing DSL unchanged.

3. **Acceptance criteria**:
*   **Performance Milestone**: The new low-overhead path must be measurably faster than the current RTDL Embree path. Ideally, the `lsi` overhead should drop significantly (targeting < 2x native) and `pip` should see an order-of-magnitude improvement.
*   **DSL Integrity**: RTDL kernel definitions must remain unchanged; the optimization should be an implementation detail or an optional "prepared" API call.
*   **Correctness Parity**: The new packed-input path must pass the same correctness tests as the current CPU and Embree runtimes.
*   **API Ergonomics**: Introduction of a `prepare_embree(kernel)` (or similar) API that returns an execution object capable of binding packed buffers and dispatching to the backend without re-normalization.
*   **Transparent Reporting**: A final report that quantifies the remaining gap to pure native C++ and identifies any remaining bottlenecks (e.g., result rematerialization).
