# Gemini Review: Goals4065-4067 RT-DBSCAN Partition Preview Chain

Date: 2026-06-09
Verdict: `accept`

## Overview

I have performed an independent read-only review of the Goal4065-4067 chain on
current `main`. This chain introduces a "prepared" CuPy partition-convergence
summary preview to the RT-DBSCAN benchmark app and adds a generic
`device_count_then_emit` pair enumeration mode to reduce memory pressure in the
partition-summary stream.

## Assessment

### 1. App-Agnostic Native-Engine Boundary

Goals4065-4067 successfully preserve the app-agnostic native-engine boundary.
The new functionality in `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
is strictly generic fixed-radius graph/partition/pair enumeration logic. The
`RawKernel` implementations and the higher-level `front_door` functions avoid
DBSCAN-specific vocabulary (e.g., "core", "border", "noise") and instead adhere
to the `fixed_radius_graph_component` contract.

### 2. Honest App Integration

The RT-DBSCAN app integration is honest. It exposes explicit benchmark modes:

- `partner_cupy_partition_convergence_component_signature_3d`
- `partner_cupy_prepared_partition_convergence_component_signature_3d`

And a new user-selected option:

- `--partition-pair-enumeration {mode_default,host,device_bounded_offsets,device_count_then_emit}`

There is no hidden dispatch or automatic partner choice for these candidate
modes. The app correctly reports these modes as `graph_component_contract_only`
and `full_dbscan_semantics: False`.

### 3. Goal4066 Memory-Pressure Improvement

Goal4066 correctly frames `device_count_then_emit` as a memory-pressure
improvement. The implementation performs an initial count-only device probe to
determine the exact number of pairs before allocating the typed result stream.
Pod evidence in `docs/reports/goal4066_pair_count_then_emit_timing_pod.json`
demonstrates a capacity reduction of 111x to 657x for representative point
clouds, with a negligible timing overhead (median ~1.04x). This is a well-balanced
trade-off for memory-constrained environments.

### 4. Goal4067 Defaults

Goal4067 correctly preserves existing defaults. The `--partition-pair-enumeration`
option defaults to `mode_default`, which leaves the choice to the underlying
engine primitive (currently `device_bounded_offsets` for the CuPy preview).
The explicit `device_count_then_emit` selection is opt-in and correctly
propagates through the "prepared" handle pattern.

### 5. Claim Boundaries

All claim boundaries remain strictly closed. Metadata flags such as
`release_authorized`, `public_speedup_claim_authorized`, and
`rt_core_speedup_claim_authorized` are consistently `False`. The
`V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY` string is correctly
propagated to all result metadata.

## Path to v2.x Promotion

Before this partition-preview lane can be promoted to a default v2.x route, the
following blockers (identified in `front_door.py`) must be addressed:

- **Universal Timing:** Resolve mixed timing results from Goal4041 to ensure the
  hybrid route is a consistent win.
- **Native Handle:** Promote the prepared native partition handle beyond the
  current CuPy/Numba preview stage.
- **Fusion:** Fuse the separate ambiguous classifier kernel to further reduce
  host-observed overhead.
- **Resident Labels:** Address the host-side label materialization that currently
  breaks the end-to-end device-resident output flow.

## Conclusion

The Goal4065-4067 chain is a high-quality addition to the RT-DBSCAN research
benchmarks, providing valuable evidence for the partition-convergence hybrid
candidate while maintaining rigorous engineering standards and claim boundaries.
