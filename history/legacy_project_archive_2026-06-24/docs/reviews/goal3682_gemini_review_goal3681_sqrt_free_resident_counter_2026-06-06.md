# Independent Gemini Review For Goal3681

Date: 2026-06-06

## Review Status

**accept-with-boundary**

## Context

Goal3677 introduced generic relation-status filtered candidate columns and Numba count composition. Goal3679 added a prepared/resident relation-status corrected Numba counter. Goal3681 focused on optimizing the Numba boundary-contact count kernel by removing the `sqrt` function, replacing it with an equivalent squared-tolerance test, and refreshing A5000 evidence. This review validates the final state after these changes, ensuring the contract preservation and updated performance metrics.

## Review Questions & Answers

1.  **Does the sqrt-free Numba boundary-contact condition preserve the generic exact boundary-contact contract?**
    Yes, the `_numba_boundary_contact_closed_shape_count_kernel` in `src/rtdsl/closed_shape_topology.py` correctly replaces `sqrt(len2)` with `eps * eps * len2` (aliased as `eps2_len2`) for comparison checks (`cross * cross <= eps2_len2`, `dot * dot <= eps2_len2`, `beyond_end * beyond_end <= eps2_len2`). This mathematical transformation preserves the original geometric contract without relying on computationally more expensive square root operations. This change is also explicitly validated in `tests/goal3677_relation_status_filtered_exact_count_test.py`.

2.  **Does the final A5000 artifact support the report numbers: one-shot exact count around `0.00281s`, resident exact count around `0.00153s`, exact count `47262`, and scoped source dirty `false`?**
    Yes.
    -   The `docs/reports/goal3677_relation_status_exact_count_a5000/summary.json` artifact shows:
        -   `"relation_status_corrected_exact_numba_count"` median hot time: `0.0028094924055039883` (around `0.00281s`).
        -   `"resident_relation_status_corrected_exact_numba_count"` median hot time: `0.0015276181511580944` (around `0.00153s`).
        -   `"correctness.exact_count"` and `"correctness.corrected_count"` are both `47262`.
        -   `"goal3677_scoped_source_dirty"` is `false`.
    These numbers align with the `docs/reports/goal3677_relation_status_filtered_exact_count_2026-06-06.md` report.

3.  **Are claim boundaries still false and is the report still explicit that this is internal evidence, not release/public/RayJoin-reproduction evidence?**
    Yes. Both `docs/reports/goal3677_relation_status_filtered_exact_count_2026-06-06.md` and `docs/reports/goal3677_relation_status_exact_count_a5000/summary.json` explicitly state that release, public speedup claims, RayJoin paper reproduction claims, RTDL beats RayJoin claims, RT-core speedup claims, true zero-copy claims, and default-route promotion are not authorized. The report clearly defines the result as an "internal performance-engineering step."

4.  **What remains before this pattern can become a recommended public API?**
    The report identifies two main areas for improvement before this pattern can become a recommended public API:
    -   Implementation of reusable native output buffers for candidate streams.
    -   Development of a generic native/partner scalar correction primitive that avoids materializing dense boundary rows.
    The current approach is noted as not being a "final generic solution for exact scalar counts" because relation-status filtering is not sparse on the tested dataset, resulting in boundary-only output being almost the full candidate stream.

## Summary

Goal3681 successfully implemented and verified the sqrt-free Numba boundary-contact count kernel, demonstrating correct behavior and updated performance metrics. The artifact and report are consistent, and all claim boundaries are appropriately maintained, emphasizing its current status as internal evidence. The remaining challenges for public API readiness are clearly articulated, focusing on optimizing handling of dense boundary-status datasets to further improve genericity and efficiency.
