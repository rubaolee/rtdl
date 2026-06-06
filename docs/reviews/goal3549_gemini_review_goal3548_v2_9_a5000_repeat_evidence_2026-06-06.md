# Goal3549: Independent Gemini Review for Goal3548: v2.9 A5000 Repeat Evidence

## Verdict
**accept-with-boundary**

## Review Points

### Robot Repeat Ledger Compactness
The `robot_collision` app's repeat ledger was successfully made scalar-only, dropping full `flags` and `backend_result` objects, which previously led to excessive memory consumption (16 GB RSS for v2.3 subprocess). This fix ensures more reliable steady-state measurements for long hot-query repeat protocols. The change is verified by `tests/goal3548_v2_9_a5000_same_contract_repeat_evidence_test.py`.

### A5000 Packet Truthfulness
The packet appears truthful. The measurements were conducted on a specified NVIDIA RTX A5000 GPU with a consistent driver, and the methodology included addressing a critical harness bug in `robot_collision` that affected earlier measurements. The full packet contains 11 comparison rows, all of which met their planned targets (`target_met_by_plan_pair_count = 11`). The speedup metrics, including median, geomean, minimum (`0.955x` for `rt_dbscan`), and maximum (`1.064x` for `rtnn`), are explicitly documented, providing transparency into the performance characteristics.

### RTNN Supplement
The RTNN supplement successfully addressed the observed-target miss in the main packet for the v2.3 lane. By rerunning both v2.3 and v2.8/current lanes at 12000 repeats, the observed-duration gap for RTNN was closed, confirming a supplemental speedup of `1.093x`. This approach maintains the integrity of the original full packet while providing necessary additional evidence.

### No Claim-Boundary Leaks
The claim boundary is explicitly and conservatively defined. The report clearly states that the evidence is for internal use only and does not authorize v2.9 release, public speedup claims, whole-app speedup claims, broad RT-core speedup claims, true zero-copy claims, or paper-reproduction claims. This restrictive boundary is robust and prevents misinterpretation or premature claims.

### Provenance Boundary
The provenance is well-documented. The report acknowledges that the final pod packet's artifact reports a previous Git commit due to the timing of the compact robot ledger patch application. This transparency about the specific commit states for the artifact and the underlying source code (compact-ledger source and regenerated v2.3 overlay patch) is crucial for internal evidence validation. The packet is explicitly marked as internal v2.9 evidence, not a final release packet.

### Next Risks
The report identifies clear and actionable next engineering targets:
1.  **Goal3536 Reporting**: Enhance Goal3536 to report observed target counts directly, improving clarity.
2.  **Repeat Planner Margin**: Implement a repeat planner margin to account for downward variance in primary metrics across calibration passes.
3.  **Optimize `rt_dbscan`**: Address the `rt_dbscan_optix_grouped_stream` row, which is the weakest performer at `0.955x` speedup.
4.  **`robot_collision` Overhead**: Audit and optimize the `robot_collision` app wrapper, as its wall time (5 minutes) is disproportionately high compared to its hot-query metric (15 seconds).
5.  **V2.9 Baseline Conversion**: Convert this packet into the official v2.9 baseline table, integrating these findings into the release process.

These identified risks and next steps demonstrate a proactive approach to continuous improvement and solidify the foundation for future work.