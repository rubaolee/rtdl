# Goal 566: HIPRT Prepared 3D Nearest-Neighbor Performance Review

Date: 2026-04-18

## Verdict

**ACCEPT**

## Review Details

The prepared HIPRT 3D fixed-radius nearest-neighbor implementation, tests, Linux performance JSON, and v0.9 support-matrix updates for Goal 566 have been reviewed for correctness, honesty of performance claims, and v0.9 documentation consistency.

### Correctness

The implementation correctly extends the prepared-execution model to 3D fixed-radius nearest-neighbor search, as described in `src/native/rtdl_hiprt.cpp`, `src/native/rtdl_hiprt_fixed_radius_neighbors_3d.cu`, and `src/rtdsl/hiprt_runtime.py`. The approach of using a prepared context for efficient repeated queries is technically sound.

Testing through `tests/goal548_hiprt_fixed_radius_3d_test.py` (and the `goal566_hiprt_prepared_nn_test.py` mentioned in the report) verifies parity with the CPU reference across multiple query batches, demonstrating that the implementation yields correct results.

### Honest Performance Claims

The performance claims, as detailed in `docs/reports/goal566_hiprt_prepared_nn_perf_linux_2026-04-18.json` and `docs/reports/goal566_hiprt_prepared_nn_perf_2026-04-18.md`, are honest and well-bounded:

- **Speedup:** A significant speedup of ~169.30x for repeated queries is demonstrated when comparing one-shot HIPRT to prepared HIPRT queries, after an initial preparation phase. This accurately reflects the benefits of the prepared execution model for recurring workloads.
- **Honesty Boundary:** The reports explicitly state the limitations: the speedup applies to repeated queries, is specific to 3D fixed-radius nearest neighbors, and does not claim coverage for 2D neighbors, KNN ranking, graph CSR, DB tables, AMD GPUs, or RT-core acceleration. It also acknowledges that Embree performs faster for one-shot CPU-oriented fixtures. This clear articulation of scope and limitations is commendable.

### v0.9 Doc Consistency

The updates are consistent with the overall v0.9 documentation. `docs/release_reports/v0_9/support_matrix.md` correctly references Goal 566's performance reports and integrates its scope and limitations into the broader v0.9 support matrix. This ensures that users and developers have a unified and accurate understanding of HIPRT's capabilities within the v0.9 release candidate.

The overall approach demonstrates a thorough understanding of the problem space, a robust implementation, and transparent communication regarding performance and feature boundaries.
