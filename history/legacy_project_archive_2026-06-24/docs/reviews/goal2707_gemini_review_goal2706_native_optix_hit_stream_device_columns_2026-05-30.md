# Gemini Review for Goal2706 Native OptiX Hit-Stream Device Columns

**Date:** 2026-05-30
**Reviewer:** Gemini Agent
**Verdict:** accept-with-boundary

## Review Analysis:

The Goal2706 implementation successfully delivers the initial native OptiX producer for the CUDA-resident hit-stream columns ABI, as defined in Goal2704. The changes align with the stated purpose of removing host row materialization from the hit-stream handoff path.

Here's a detailed breakdown addressing the review questions:

1.  **Does the new native C ABI remain generic and app-agnostic?**
    The new native C ABI, though implemented for OptiX and static triangle scenes as a producer, appears to remain generic at the C ABI level for data consumption. It focuses on providing fundamental `ray_ids` and `primitive_ids` data, which can be integrated into various applications. The implementation's specificity lies in the OptiX production aspect rather than limiting the ABI's generality for consumer applications.

2.  **Does the native OptiX path actually avoid downloading/sorting host hit rows in the new device-column method?**
    Yes, the report explicitly confirms that the native OptiX path avoids downloading and sorting host hit rows. The new dedicated OptiX any-hit pipeline writes `ray_ids` and `primitive_ids` arrays directly to CUDA-resident memory. The `host_rows: False` output from the local Linux functional smoke test further validates this.

3.  **Does the owner/release path look adequate for experimental native CUDA buffers, with obvious risks called out?**
    The implementation includes a native owner object and a corresponding Python `_OptixNativeHitStreamDeviceColumnsOwner` for freeing CUDA arrays through a defined release entrypoint. The "Boundary" section of the report clearly outlines the experimental nature of this work and calls out specific limitations regarding zero-copy wording, public speedup claims, v2.5 release promotion, and Triton end-to-end performance claims. This demonstrates an adequate and responsible approach to managing experimental buffers and communicating associated risks.

4.  **Does the Python binding preserve claim boundaries by keeping `native_device_column_output_proven_on_hardware=False` and zero-copy/speedup claims unauthorized?**
    Yes, the Python binding strictly adheres to the defined claim boundaries. The report explicitly states that `native_device_column_output_proven_on_hardware=False` is maintained until pod evidence is collected, and it explicitly prohibits "true zero-copy wording" and "public speedup wording."

5.  **What risks must be checked on the next RTX pod run before promotion?**
    The primary risk before promotion is the lack of performance and correctness validation on actual RTX pod hardware. Goal2707 is tasked with addressing this by building OptiX, executing `ray_triangle_hit_stream_device_columns(...)`, feeding the results into the gather/partner planner path, measuring phase timings against the host-row bridge, and recording same-pointer/no-host-stage evidence. These steps are crucial to confirm performance benefits and ensure correct integration and behavior in a production-like environment before any further promotion or public claims.

## Conclusion:

The Goal2706 implementation is well-executed and thoughtfully managed with respect to its experimental nature. The core functionality of avoiding host row materialization is achieved, and appropriate mechanisms for managing CUDA buffers and preserving claim boundaries are in place. The next steps for validation on RTX pod hardware (Goal2707) are clearly defined and critical for eventual promotion.
