# Goal4004 Microcell Route Refresh After Grouped-Union Telemetry

Date: 2026-06-08

## Verdict

`reject-as-performance-route`

Goal4004 retested the existing corrected microcell component route after the
Goal3999-4002 grouped-union evidence. The purpose was to check whether the
project already had a safe partition-like implementation that could replace the
current grouped stream.

It does not. The corrected microcell route preserves output signatures, but it
is much slower than the current RTDL/OptiX grouped-stream route at the actual
RT-DBSCAN benchmark profiles.

Artifacts:

- `docs/reports/goal4004_microcell_route_refresh_pod/clustered3d_grouped.json`
- `docs/reports/goal4004_microcell_route_refresh_pod/clustered3d_microcell.json`
- `docs/reports/goal4004_microcell_route_refresh_pod/road3d_grouped.json`
- `docs/reports/goal4004_microcell_route_refresh_pod/road3d_microcell.json`
- `docs/reports/goal4004_microcell_route_refresh_pod/ngsim_dense_grouped.json`
- `docs/reports/goal4004_microcell_route_refresh_pod/ngsim_dense_microcell.json`

## Pod Setup

- GPU: NVIDIA RTX 4000 Ada Generation
- Source commit: `0ca3d6273d57cf3e7f2b2d31d35b4f7149b268a7`
- Point count: `65,536`
- Warmup: `1`
- Repeat: `5`
- Validation: disabled for timing; grouped-stream and microcell output
  signatures compared.

## Results

| Profile | Radius | Grouped-stream sec | Microcell sec | Microcell / grouped | Signature match | Microcell status |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `clustered3d` | `0.055` | `0.117265` | `5.885775` | `50.19x slower` | yes | `clique_safe_microcell` |
| `road3d` | `0.030` | `0.070139` | `1.654973` | `23.60x slower` | yes | `clique_safe_microcell` |
| `ngsim_dense` | `0.012` | `0.046727` | `1.350400` | `28.90x slower` | yes | `clique_safe_microcell` |

## Interpretation

The old microcell route remains useful as a correctness lesson: the unsafe
radius-cell assumption was fixed with clique-safe microcells, and the route can
match grouped-stream output signatures on the measured profiles.

But it is not a performance route. It shifts too much work into the partner
microcell graph continuation and does not exploit the current prepared OptiX
grouped-stream path efficiently. It should not be promoted as the next RT-DBSCAN
default or used as evidence that the dense grouped-union problem is solved.

The new hybrid primitive direction is narrower:

- keep the RTDL/OptiX grouped-stream route as the current best baseline;
- do not reuse the old partner microcell path as the promoted route;
- design a native/device-resident partition assist that summarizes safe
  partition pairs while leaving ambiguous boundary work to RT traversal;
- preserve same-contract output signatures and deterministic component policy.

## Boundary

Goal4004 is a route-refresh/negative performance result. It does not authorize
release, public speedup wording, broad RT-core speedup wording, whole-app
acceleration wording, paper-reproduction wording, true-zero-copy wording,
automatic partner/backend selection, or app-specific native-engine logic.
