# Antigravity Technical Review: V4 Goal4675 Aggregate-Frontier Prepared Runner

Date: 2026-06-25
Reviewer: Antigravity (independent external review)

## Verdict

`accept_goal4675_local_runner_continue_goal4676_protocol`

---

## Answers to Review Questions

### 1. Does Goal4675 correctly productize `v4_aggregate_frontier_device_columns_2d_prepared_runner` as a generic V4 candidate surface rather than an app-specific Barnes-Hut or force-law surface?
**Yes.** The runner `V4AggregateFrontierDeviceColumns2DPreparedRunner` is productized in `src/rtdsl/v4_aggregate_frontier.py` around the generic `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` primitive. It delegates directly to `prepare_aggregate_frontier_device_columns_2d_optix` and `PreparedOptixAggregateFrontierDeviceColumns2D.run_device_columns`. It does not introduce any Barnes-Hut, force-law, or other application-identity symbols. Furthermore, the pushdown recognizer in `src/rtdsl/v4_operator_catalog.py` fails closed for unmeasured/app-identity native kernels.

### 2. Does the runner preserve the Goal4674 hot-path boundary: no host frontier row materialization before downstream continuation?
**Yes.** The runner explicitly checks and returns the status of host materialization in its metadata:
*   `host_materialization_in_hot_path` is hardcoded to `False`.
*   `frontier_columns_materialized_on_host` and `row_offsets_materialized_on_host` are fetched from output metadata and default to `False`.
*   `device_resident_frontier_columns_required` is set to `True`.
*   `host_frontier_materialization_before_partner_forbidden` is set to `True`.
Small host outputs are strictly limited to `row_count`, `attempted_count`, `overflow`, and `phase_timings`.

### 3. Does the metadata expose enough phase/residency accounting for Goal4676 to make an honest same-hardware performance decision?
**Yes.** The runner includes `phase_accounting` in the return dictionary, which exposes:
*   `aggregate_frontier_traversal_seconds`
*   `downstream_partner_seconds`
*   `host_frontier_materialization_seconds`
*   `phase_accounting_is_first_class: True`
This gives the benchmark orchestrator enough granularity to isolate the GPU traversal time from the downstream partner continuation time, preventing partner migration overhead or benefits from distorting the V4 operator timing during evaluation in Goal4676.

### 4. Does the V4 catalog/frontdoor/scope gate correctly mark this as candidate, not measured, not release-authorized, and not public-speed-authorized?
**Yes.**
*   In `src/rtdsl/v4_operator_catalog.py`, `v4_aggregate_frontier_device_columns_2d_prepared_runner` is registered under `V4_TIER2_CANDIDATE_OPERATOR_SURFACES` with status `"candidate_goal4675_local_runner_not_pod_measured"` and partner claim status `"candidate_not_pod_measured_not_release"`.
*   In `src/rtdsl/v4.py`, the unified front-door claim boundary has all release/speedup/zero-copy authorization flags set to `False` for candidates.
*   In `src/rtdsl/v4_scope.py`, the runner is registered under `V4_0_CANDIDATE_SURFACES`. The `v4_0_scope_gate` is validated to ensure all speedup and release authorization flags are strictly `False`.

### 5. Do the tests cover the local contract without pretending to be POD evidence?
**Yes.** The tests in `tests/v4_goal4675_aggregate_frontier_prepared_runner_test.py` utilize mock objects (`FakePreparedFrontier` and `FakeFrontierOutput`) to verify API boundaries, error handling for invalid backends/partners, closed runner behavior, metadata inclusion, and planner routing. They assert the correctness of local contracts and local metadata structures without claiming or simulating actual physical POD performance.

### 6. Is Goal4676 the correct next step, and should it remain the first point where same-hardware V2.14/V4 speed claims can be evaluated?
**Yes.** Goal4675 only productizes the local API wrapper and implements static mock/dry-run checks. Actual performance benchmarking on physical hardware comparing V4 vs the V2.14 aggregate-frontier denominator, including correctness and timing verification under identical environments, must occur in Goal4676.

### 7. Does this review preserve all non-authorization boundaries?
**Yes.** All non-authorization boundaries are preserved and explicitly detailed below.

---

## Authorization Boundaries

*   **V4 Release**: Do **NOT** authorize.
*   **POD Outside Goal4676 Protocol**: Do **NOT** authorize.
*   **Public Speedup Wording**: Do **NOT** authorize.
*   **Whole-App High-Performance Wording**: Do **NOT** authorize.
*   **RT-Core Speedup Wording**: Do **NOT** authorize.
*   **True-Zero-Copy**: Do **NOT** authorize.
*   **Tier-3 Callback/PTX**: Do **NOT** authorize.
*   **Raw OptiX Callbacks**: Do **NOT** authorize.
*   **C ABI**: Do **NOT** authorize.
*   **Embedding**: Do **NOT** authorize.
*   **Non-Python Hosts**: Do **NOT** authorize.
*   **Automatic Partner Selection**: Do **NOT** authorize.
*   **App-Identity Kernels**: Do **NOT** authorize.

We only authorize the preparation of Goal4676-focused POD protocol/benchmark work.
