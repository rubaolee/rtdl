# Goal4146 - Direct-Status Redundant Sync Removal

Date: 2026-06-09

Verdict: implementation-complete-pod-needed

## Purpose

Goal4146 targets a structural overhead in the RT-DBSCAN direct-status route:
host synchronization in the convergence loop.

The direct-status union loop launched the union kernel, launched the parent
compression kernel, then explicitly synchronized the current stream immediately
before reading `changed[0].item()`. The scalar `.item()` read already
synchronizes the stream. The explicit synchronize was therefore redundant for
the direct-status convergence check.

## Change

Remove the explicit `cupy.cuda.get_current_stream().synchronize()` from
`_cupy_direct_partition_status_union_component_roots` while preserving the
existing `changed[0].item()` convergence check.

## Boundary

This is a generic fixed-radius direct-status convergence-loop cleanup. It does
not alter convergence semantics, component labels, route selection, partner
selection, partition-cell-factor selection, native ABI, or app-specific engine
logic.

Pod timing is required before making any performance conclusion.
