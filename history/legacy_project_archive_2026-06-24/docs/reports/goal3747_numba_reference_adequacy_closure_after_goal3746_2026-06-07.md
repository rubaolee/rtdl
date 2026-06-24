# Goal3747 Numba Reference Adequacy Closure After Goal3746

## Purpose

Goal3747 refreshes the v2.9 benchmark adequacy matrix after the two Numba
reference gaps from Goal3740 were addressed:

- Goal3742/3744: RT-DBSCAN Numba grid component labeling plus OptiX-to-Numba
  threshold/core-flag bridge.
- Goal3746: Barnes-Hut Numba CUDA JIT exact-force reference.

## Current Result

Only one Numba-reference pressure point remains: `spatial_rayjoin`, where the
closed-shape/topology policy still needs a Numba app-continuation reference.

| App | Previous Numba status | Current status |
| --- | --- | --- |
| `rt_dbscan` | Needed component-continuation reference | Covered by Goal3742/3744 |
| `barnes_hut` | Needed force-vector continuation reference | Covered by Goal3746 |
| `spatial_rayjoin` | Needed closed-shape/topology continuation reference | Still open |

The Barnes-Hut Numba path is not promoted as faster than CuPy. The A5000
artifact records `0.754x` to `0.893x` versus the CuPy RawKernel path across
1024-8192 bodies. It is accepted because it is correct, CUDA-resident, and gives
users a no-RawKernel reference implementation.

## Boundary

Goal3747 does not authorize release action, public speedup wording, broad
RT-core claims, hidden partner selection, or app-specific native-engine logic.
It only updates the internal adequacy status after measured Numba reference
coverage improved.

