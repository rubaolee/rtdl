# Gemini Review: Goal4039-4041 Route And Partition Evidence

Date: 2026-06-08

## Verdict

**accept**

This is a Gemini review distinct from Codex.

## Summary

The Goal4039-4041 chain successfully refreshes benchmark route evidence and advances the design for device-resident fixed-radius graph component labeling.

- **Goal4039** performs a critical environment repair for the Numba CUDA toolchain and refreshes RayJoin evidence. It maintains a rigorous separation of subroute results (PIP one-shot vs. repeated PIP, LSI, and Overlay), ensuring that performance claims remain contract-specific and do not overclaim whole-app speedups.
- **Goal4040** introduces `partition_point_ordinals` to the partition-summary contract and adds a CuPy-based ambiguous-union continuation. This design remains generic and app-agnostic, providing a clear path for resident fixed-radius graph component labeling without adding app-specific logic to the native engine.
- **Goal4041** provides an honest and technically sound interpretation of the timing evidence for the new device path. It correctly identifies the path as a design win for residency rather than a universal performance win, specifically noting losses on small-ambiguity clustered inputs and recommending against default promotion.

## Review Questions

### 1. Does Goal4039 correctly separate RayJoin subroutes instead of overclaiming a single whole-app speedup?

Yes. The report `docs/reports/goal4039_rayjoin_representative_profile_fixed_numba_toolchain_2026-06-08.md` explicitly breaks down the RayJoin representative profile into specific contracts:
- **PIP one-shot scalar count:** Favors Numba (0.230x speedup).
- **LSI scalar count:** Strongly favors RTDL/OptiX (262.393x).
- **Overlay active count:** Strongly favors RTDL/OptiX (210.183x).
- **Repeated PIP requests:** Favors the RTDL/OptiX prepared batch executor.

The interpretation explicitly states that route choice remains visible and user-controlled, and that this refresh does not authorize whole-app speedup wording.

### 2. Does Goal4040 keep the fixed-radius component path generic and app-agnostic while adding `partition_point_ordinals` and the `cupy_partition_points` ambiguous-union continuation?

Yes. The implementation in `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py` maintains the "fixed_radius_graph_component_labels_3d" operation as a generic primitive. The addition of `partition_point_ordinals` to the `make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract` is a natural extension of the partition summary. The `cupy_partition_points` execution mode for ambiguous unions is a generic device-side implementation of the component-label continuation, not tied to any specific application like DBSCAN.

### 3. Does Goal4041 correctly interpret the timing evidence as a useful device-resident continuation, not a universal speed win and not a default promotion?

Yes. The report `docs/reports/goal4041_partition_device_ambiguous_union_timing_2026-06-08.md` provides a nuanced interpretation:
- It identifies that the device path is a "design problem" solution (keeping classification resident) rather than a "performance problem" solution.
- it explicitly concludes that the path "should remain an optional resident continuation, not a promoted default route."
- It correctly identifies the overhead of extra kernel launches as the reason for losses on clustered data with few ambiguous pairs.

### 4. Are all claim boundaries intact: release, public speedup, broad RT-core, whole-app, hidden-dispatch, automatic partner selection, app-specific engine logic, native ABI addition, and true-zero-copy claims?

Yes. Every artifact inspected (reports, scripts, and code) contains explicit and consistent disclaimers. The `V28FixedRadiusGraphComponentPlan` and `CurrentBenchmarkRouteDecision` data classes in the source code rigorously enforce these boundaries by raising errors if unauthorized flags are set. The timing script `scripts/goal4041_partition_device_ambiguous_union_timing.py` also encodes these boundaries in its JSON output schema.

## Next Engineering Target

Based on the Goal4041 interpretation, the next best engineering targets are:
1. **Fusing resident continuations:** Combine safe-full and ambiguous partition classification into a single device component-label pass to reduce kernel launch overhead.
2. **Prepared native/partner routes:** Move the device-resident classification into a prepared route where launch costs can be amortized over many requests.
3. **Generic route evidence:** Move beyond one-off RayJoin tuning towards larger generic route evidence (as suggested in Goal4039).
