# Antigravity Review: Goal4912 Persistent Planar-Map Workspace Design Gate

**Date**: 2026-07-03
**Verdict**: `approve_goal4912_productize_in_process_workspace_api`
**Reviewer**: Antigravity (External Technical Reviewer)

---

## Executive Summary

Goal4912 defines the product and API design gate for introducing a generic, persistent, in-process planar-map workspace API ([PlanarMapWorkspace2DOptix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4912_persistent_workspace_design_plan_2026-07-03.md#L157)) in RTDL. This API lets applications build and prepare native locator states and query handles once, then run repeated, high-performance point-location and overlay queries cheaply.

Based on the evidence from prior experimental goals:
- [Goal4902](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4902_reusable_point_location_session_report_2026-07-03.md) proved that reusable point-location sessions reduce overlay hot-body times from `11.320s` to `6.915s`.
- [Goal4904](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_pip_replay_report_2026-07-03.md) showed that prepared LSI query sessions drop the LSI pair-id row phase from `1.814s` to `0.006s` in hot replay.
- [Goal4910](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4910_direct_descriptor_writer_result_2026-07-03.md) confirmed that Python-level writer optimizations have reached diminishing returns (warm hot body at `3.918s`, writer at `1.840s`).
- [Goal4911](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4911_point_location_prepare_tradeoff_report_2026-07-03.md) verified that simple grouping mode knob tuning is exhausted.

Rather than pursuing fragile, hardware-specific, cross-process OptiX GAS caching or continuing marginal Python timing optimizations, the design correctly switches to productizing in-process session reuse. This provides a clean programming model that amortizes setup latency for repeated queries.

We approve the design as proposed and recommend authorizing Goal4913 to implement the workspace API.

---

## Detailed Answers to the Eight Review Questions

### 1. Does the plan correctly use Goal4902, Goal4904, Goal4910, and Goal4911 evidence?
**Yes.** The plan correctly incorporates and references the specific metrics from prior goals:
- **[Goal4910](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4910_direct_descriptor_writer_result_2026-07-03.md)**: Reuses the best prepared-hot repeat results (hot body = `3.918s`, writer = `1.840s`, LSI replay = `0.006s`, vertex PIP = `1.080s`) to establish the baseline performance and correctness benchmarks.
- **[Goal4902](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4902_reusable_point_location_session_report_2026-07-03.md)**: Leverages the session reuse validation data, confirming a drop in hot-body latency from `11.320s` (rebuild within each run) to `6.915s` (session reuse).
- **[Goal4904](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_pip_replay_report_2026-07-03.md)**: Reuses the prepared LSI query replay metrics, showing that LSI traversal overhead drops from `1.814s` to `0.006s` during hot replay.
- **[Goal4911](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4911_point_location_prepare_tradeoff_report_2026-07-03.md)**: Incorporates the grouping-mode tradeoff matrix (`default`, `legacy fixed8`, `adaptive`, `block_merge64`), confirming that the current defaults are optimal and simple knob sweeps are exhausted.

### 2. Is the chosen direction correct: productize an in-process workspace/session API rather than run more group-mode or writer micro-tuning?
**Yes.**
- **Knob Sweeping Exhaustion**: As proven by [Goal4911](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4911_point_location_prepare_tradeoff_report_2026-07-03.md), the default grouping knobs are already optimal, and other modes degrade execution time or fail to yield speedups.
- **Python Writer Exhaustion**: [Goal4910](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4910_direct_descriptor_writer_result_2026-07-03.md) demonstrated that Python-layer direct descriptor tricks yield only minor improvements (`~0.095s` total hot body speedup). Squeezing fractions of a second in Python-only code has hit a wall of diminishing returns.
- **Strategic Workspace Focus**: Since setup costs (like point-location BVH/GAS build time taking `~4s` or more) represent the bulk of the remaining cold-start latency, the only way to solve this bottleneck is to allow the application to build these structures once and reuse them. Productizing a persistent workspace session API resolves this overhead cleanly for repeated-query workloads, turning experimental session reuse into a supported product API.

### 3. Is it correct to defer cross-process OptiX GAS/build-artifact caching as a later R&D goal?
**Yes.** Cross-process OptiX GAS serialization involves saving compiled GPU acceleration structures to disk. This mechanism is highly sensitive to the CUDA runtime version, driver versions, GPU device architecture, and local system memory allocators.
- Implementing this now would add significant native backend complexity and potential stability regressions, with high maintenance risks.
- In-process workspace/session reuse has already been measured and proven to provide substantial speedups safely within the same process.
- Deferring cross-process caching allows the team to deliver a clean, stable workspace API surface first. Once the API lifecycle is established and hardened, cross-process persistence can be developed as a separate, isolated backend R&D task.

### 4. Is the proposed API generic planar-map RTDL infrastructure rather than a RayJoin-specific hidden route?
**Yes.** The proposed class (`PlanarMapWorkspace2DOptix`) and its constructor (`prepare_planar_map_workspace_2d_optix`) use generic geometric terminology. The API targets standard RTDL primitives (CDB input layers, LSI query handles, and directed point-location/PIP sessions) rather than hidden, RayJoin-specific shortcuts. The design explicitly prohibits importing or depending on `rtdl.rayjoin_overlay`, ensuring the workspace remains a reusable, general-purpose building block for any planar-map query application.

### 5. Does the plan preserve the boundary that app logic and Numba/CuPy continuations stay outside RTDL core?
**Yes.** The workspace API exposes standard primitive query components (such as LSI query and point-location handles) and accepts user-provided application layers via explicit callbacks/arguments (`continuation` and `output_writer`). This design prevents application-specific schemas or custom formatters from polluting the native RTDL engine, keeping the core libraries focused entirely on accelerated geometric indexing while app code runs in user space.

### 6. Is the implementation scope for Goal4913 tight enough?
**Yes.** The scope is well-defined and focused:
- It defines the [PlanarMapWorkspace2DOptix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4912_persistent_workspace_design_plan_2026-07-03.md#L157) class as a context manager.
- It specifies exact unit test criteria (resource cleanup, repeated query execution, correctness, and no imports of `rtdl.rayjoin_overlay`).
- It limits integration to updating the existing paper-reproduction harness to use the workspace instead of manual handles.
- It enforces internal-only documentation to prevent premature marketing or release claims.
This ensures the implementation is simple packaging of already-proven mechanics.

### 7. Is the acceptance bar honest, especially that it does not require a new speedup and primarily productizes already-proven session reuse?
**Yes.** The acceptance bar is honest and realistic. It acknowledges that the goal is not to invent a magic new speedup, but rather to package and productize a performance pattern already demonstrated in [Goal4902](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4902_reusable_point_location_session_report_2026-07-03.md) and [Goal4904](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_pip_replay_report_2026-07-03.md).
- The criteria require correctness (byte-equality to `AuthorOfficial`), public boundary validation (no `rayjoin_overlay` imports), generality of the API names, separation of setup/hot timing, and a safety constraint that the hot-body execution does not regress by more than 5% compared to [Goal4910](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4910_direct_descriptor_writer_result_2026-07-03.md).
- This focuses on engineering quality, correctness, and API design rather than hyper-optimizing transient timing numbers.

### 8. Should Goal4913 be authorized to implement the in-process workspace API?
**Yes.** Implementing the in-process workspace API is the most logical next step. It consolidates the experimental performance findings into a stable, usable, and clean programming model for RTDL clients.
- Since it leverages already-validated capabilities (session reuse and prepared query replay), the technical risk is minimal, and the software quality improvement is high.

---

## Authorization Boundaries

Approval of Goal4912 is subject to the following strict boundaries and does **not** authorize:

1. **Raw OptiX Callback Exposure**: Internal GPU compiler callbacks and raw OptiX context pointers must remain hidden.
2. **RayJoin-Specific Hidden Kernels**: The workspace must not wrap or hide specialized, non-generic kernels designed solely for RayJoin.
3. **Cross-Process OptiX GAS Serialization**: No caching or serialization of OptiX GAS/build artifacts to disk is authorized under this step.
4. **Broad RTDL/RayJoin Performance Claims**: No new or generalized speedup claims may be published.
5. **Public Release Wording Changes**: Wording changes to public release documents, READMEs, or user-facing documentation are not authorized.
6. **Resurrection of V3/V4 Claims**: Any claims referencing obsolete V3/V4 paper performance figures remain unauthorized.
