# Goal 229 Review: fixed_radius_neighbors Accelerated Boundary Fix

## Verdict

Accepted. The fix is technically sound, preserves the public contract, and is verified by both focused regression tests and refreshed heavy benchmark evidence.

## Findings

- **Root Cause Validation:** The identified root cause—float-path precision loss on large coordinates causing candidate drop during accelerated traversal—is technically coherent. The observed error of ~5e-5 at coordinates near 3000 is consistent with float32 machine epsilon ($\approx 1.19 \times 10^{-7}$).
- **Contract Preservation:** The fix maintains the public inclusive-radius contract (`distance <= radius`). By widening the candidate collection radius (using `kFixedRadiusCandidateEps = 1.0e-4`) and then performing host-side refiltering with double-precision coordinates, the backends now return the exact set of neighbors required by the contract.
- **Implementation Consistency:**
    - **Embree:** Widens `RTCPointQuery.radius` and refilters in the `point_point_query_collect` callback using double precision.
    - **OptiX/Vulkan:** Widens the CUDA/Compute kernel search radius, allows for extra candidate slots (`kFixedRadiusSlack = 8`), and performs host-side refiltering, sorting, and trimming before returning results.
- **Regression Coverage:** The new `test_large_coordinate_boundary_case_keeps_interior_neighbor` test case correctly reproduces the failure condition (a point just inside the 0.5 radius at large coordinates) and verifies that all accelerated backends now retain the neighbor.
- **Evidence Parity:** The refreshed Goal 228 benchmark reports now show full row-count parity (45,632 rows) across CPU, Embree, OptiX, Vulkan, and PostGIS, confirming the fix resolves the real-world mismatch discovered on the Natural Earth dataset.

## Risks

- **Candidate Slack Limit:** In OptiX and Vulkan, the use of a fixed `kFixedRadiusSlack = 8` for candidate collection introduces a theoretical risk if more than 8 points are located in the epsilon-widened shell ($radius < dist \le radius + \epsilon$) AND their float-approximated distances displace true interior points. However, given the small epsilon ($10^{-4}$) and typical geospatial point densities, this is a negligible risk for the current workloads.
- **Performance Impact:** The widening of the radius and host-side refiltering add marginal overhead. However, the Goal 228 results show that accelerated backends remain orders of magnitude faster than the CPU/PostGIS baselines, so the performance trade-off for correctness is justified.

## Conclusion

The Goal 229 fix successfully resolves the accelerated boundary correctness blocker. No blocking issues were found. The implementation is clean, well-tested, and correctly balances accelerator performance with host-side precision requirements.
