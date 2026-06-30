# Goal4001 Actual-Radius Grouped-Union Extended Telemetry

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal4001 reran the Goal3992/3996 extended grouped-union telemetry on the
actual RT-DBSCAN benchmark radii instead of the radius-`0.5` stress row.

This confirms the current grouped-union primitive is already using the right
simple mode: same-root culling is mandatory. It also shows the remaining
performance floor more precisely: the default path culls almost every
radius-qualified candidate, but it still has to traverse those candidates and
read component roots to prove they can be skipped.

Artifacts:

- `docs/reports/goal4001_actual_radius_exttelemetry_pod/clustered3d_65536.json`
- `docs/reports/goal4001_actual_radius_exttelemetry_pod/road3d_65536.json`
- `docs/reports/goal4001_actual_radius_exttelemetry_pod/ngsim_dense_65536.json`

## Pod Setup

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `45a63d9cf14368099c5ba9017b8f9a9c8bc84005`
- Build: `make build-optix -j2`
- Point count: `65,536`
- Repeats per mode: `3`

## Results

Default mode is same-root culling on and direct side effects off.

| Profile | Radius | Default native sec | Radius candidates | Same-root culled | Reported candidates | No-cull sec | No-cull / default | Direct-side-effect sec | Direct / default |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | `0.055` | `0.099711` | `273,911,978` | `273,831,259` | `80,719` | `0.105354` | `1.057x` | `0.095312` | `0.956x` |
| `road3d` | `0.030` | `0.032590` | `85,627,372` | `85,460,087` | `167,285` | `0.036428` | `1.118x` | `0.030560` | `0.938x` |
| `ngsim_dense` | `0.012` | `0.009808` | `12,299,418` | `12,224,299` | `75,119` | `0.011556` | `1.178x` | `0.009843` | `1.004x` |

## Interpretation

The actual benchmark radii still produce large radius-qualified candidate
streams, but same-root culling removes almost all of them before any-hit union:

- `clustered3d`: `80,719 / 273,911,978` candidates reported after culling;
- `road3d`: `167,285 / 85,627,372` candidates reported after culling;
- `ngsim_dense`: `75,119 / 12,299,418` candidates reported after culling.

Disabling same-root culling is slower on all three profiles. This confirms that
the next optimization should not turn same-root culling off or replace it with
a stale source-root payload.

Direct side effects are a useful but small mode knob. They avoid any-hit reports
and are faster for `clustered3d` and `road3d`, and effectively neutral on
`ngsim_dense`. This is not a large enough lever to close the remaining dense
grouped-union problem by itself.

The combined Goal3999 + Goal4001 lesson is now sharper:

1. Uniform partitions can summarize/skip some work but leave substantial
   ambiguous boundary work.
2. Same-root culling removes nearly all radius candidates, but only after
   paying traversal and root-read cost for those candidates.
3. Direct side effects trim any-hit overhead but do not reduce candidate/root
   work.

The next real primitive should therefore reduce candidate/root-read work, not
just move the union side effect. A promising generic direction is a
device-resident partition/convergence hybrid:

- use safe partition summaries for definitely-within-radius cell pairs;
- keep RT traversal for ambiguous boundary cell pairs;
- preserve exact component-root convergence metadata;
- optionally test direct side effects as an execution option after same-contract
  validation.

## Boundary

Goal4001 is diagnostic telemetry. It does not authorize release, public speedup
wording, broad RT-core speedup wording, whole-app acceleration wording,
paper-reproduction wording, true-zero-copy wording, automatic partner/backend
selection, or app-specific native-engine logic.
