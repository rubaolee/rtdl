# Goal4095 Partition Convergence Phase Breakdown

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4095 measures where the explicit non-skip partition-convergence preview
still spends time after Goals4088 and 4093.

The answer is important for the next runtime-design step: the remaining cost is
not one small local operation. It is split between repeated pair-status scans,
other producer work, and signature bookkeeping. The next serious improvement
therefore needs a fused/native producer or equivalent generic runtime primitive,
not another thin wrapper around the current CuPy preview.

## Pod Setup

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `c56596f8e3c81a323c48034cce3e9bdc4a5b38ad`
- Point count: 65,536
- Pair mode: `device_count_then_emit_non_skip`
- Profiles: `clustered3d`, `road3d`, `ngsim_dense`

Artifacts:

- `docs/reports/goal4095_partition_convergence_phase_breakdown_pod.json`
- `docs/reports/goal4095_partition_convergence_phase_breakdown_pod.stdout.txt`

## Phase Results

Median seconds from measured runs:

| Profile | Pair rows | Build total | Count probe | Emit | Other build work | Pair-kernel share | Other-build share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 10,960,581 | 0.091420 | 0.012967 | 0.027208 | 0.051245 | 43.9% | 56.1% |
| `road3d` | 6,830,362 | 0.082552 | 0.011849 | 0.020631 | 0.050071 | 39.3% | 60.7% |
| `ngsim_dense` | 11,585,223 | 0.201295 | 0.052201 | 0.066741 | 0.082352 | 59.1% | 40.9% |

Median component-signature replay:

| Profile | Signature total | Ambiguous point union | Other signature work | Ambiguous-union share |
| --- | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.049362 | 0.011809 | 0.037530 | 23.9% |
| `road3d` | 0.041956 | 0.004389 | 0.037567 | 10.5% |
| `ngsim_dense` | 0.041421 | 0.002300 | 0.039122 | 5.6% |

## Interpretation

Goal4093 reduced materialized rows, but the current implementation still:

- runs a count probe and an emit pass over the same partition-neighborhood
  search space;
- performs substantial uninstrumented producer work around cell sorting, unique
  cell discovery, AABB reductions, status-count scans, and typed-stream
  assembly;
- materializes pair rows before the component continuation;
- then spends most replay time outside the ambiguous point-union kernel.

That explains why non-skip mode is useful but not default-worthy. It reduces
memory pressure and modestly improves build time, yet it cannot erase the
two-pass producer and replay bookkeeping shape.

## Next Runtime Direction

The next serious RT-DBSCAN performance target should be a generic fused/native
fixed-radius grouped-union producer that can:

- classify partition-pair status and consume safe-full/ambiguous work without a
  full materialized pair table;
- avoid the count-probe plus emit double pass when possible;
- preserve same-contract correctness for component labels/signatures;
- keep `ngsim_dense` from regressing;
- remain app-agnostic and user-explicit about partner choice.

## Boundary

This report is internal phase-breakdown evidence. It does not promote
`partition_convergence_hybrid`, authorize release, public speedup, broad RT-core,
whole-app, paper-reproduction, hidden-dispatch, automatic partner selection,
app-specific engine logic, native ABI addition, or true-zero-copy claims.
