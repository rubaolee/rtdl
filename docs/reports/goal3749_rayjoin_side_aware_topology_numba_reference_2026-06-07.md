# Goal3749 RayJoin Side-Aware Topology Numba Reference

## Purpose

Goal3749 starts closing the remaining RayJoin Numba-reference gap from
Goal3747. The target is the generic side-aware owner-face membership filter:
given candidate point/shape columns, topology face columns, and explicit
caller-supplied owner face/side policy, keep only the rows that satisfy that
policy.

The existing promoted fast RayJoin route remains primitive-first RTDL/OptiX.
This Numba helper is a reference continuation for user custom logic, not a
replacement for the native segment-pair or shape-pair executors.

## Implementation

- Added `filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba`.
- The helper uses Numba CUDA JIT to compute the keep mask and owner face/side
  outputs.
- It reuses the existing generic Numba compact-mask primitive to compact row
  indices.
- It host-prepares sorted owner/topology lookup columns, then uses binary
  search inside the Numba CUDA filter kernel. This keeps the user-facing
  operation generic while avoiding the old O(candidate rows x owner/topology
  rows) lookup shape.
- It supports both public-id lookup and ordinal lookup, matching the CuPy and
  Python columnar semantics.
- It is exported from `rtdsl.__init__` and listed in the owner-face priority
  pipeline contract.

## A5000 Same-Contract Timing Probe

Artifact:
`docs/reports/goal3749_rayjoin_side_aware_topology_numba_a5000/summary.json`

Scope: same-contract partner continuation only. The probe compares
`filter_closed_shape_membership_candidate_columns_by_owner_face_side_cupy` with
the new no-RawKernel Numba helper on synthetic side-aware topology columns. It
includes each adapter call's host preparation work and records keep-count
parity. This is not a whole RayJoin app timing and not an RT-core speedup claim.

| Candidate rows | Topology rows | Owner rows | CuPy best s | Numba best s | Numba/CuPy |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16,384 | 4,096 | 4,096 | 0.066093 | 0.006677 | 9.899x |
| 65,536 | 8,192 | 8,192 | 0.112891 | 0.010790 | 10.462x |
| 262,144 | 16,384 | 16,384 | 0.228969 | 0.013859 | 16.521x |
| 1,048,576 | 32,768 | 32,768 | 0.441605 | 0.024823 | 17.790x |

All rows preserve keep-count parity. The result is important because it closes
one remaining RayJoin custom-continuation reference gap with a high-performance
Numba implementation, instead of asking users to write CuPy RawKernel code for
this topology policy.

## Boundary

This is a no-RawKernel Numba reference for app-owned topology policy.
It is not a public speedup claim, not RayJoin paper reproduction, not hidden
partner selection, and not app-specific native-engine logic. The promoted RayJoin route
still remains primitive-first RTDL/OptiX; this helper improves the user-custom
logic path when side-aware topology policy is needed outside the native
primitive.
