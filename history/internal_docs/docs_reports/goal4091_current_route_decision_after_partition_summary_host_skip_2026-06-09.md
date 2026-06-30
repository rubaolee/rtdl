# Goal4091 Current Route Decision After Partition Summary Host Skip

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4091 refreshes the current benchmark route registry after the Goal4085-4088
partition-summary chain. The key decision is unchanged but better justified:
RT-DBSCAN should still use the unblocked RTDL/OptiX grouped stream plus Numba
column-signature continuation as the recommended route.

Goal4088 materially improved the partition-convergence preview by skipping
unused host AABB rebuilding on device-backed enumeration, but the preview still
does not beat the recommended route for normal use.

## Route Decision

The `rt_dbscan` advisory route now records:

- current route: RTDL/OptiX fixed-radius grouped stream with Numba
  component/signature continuation;
- explicit unpromoted candidate:
  `partition_convergence_hybrid`;
- latest improvement: Goal4088 cuts partition-summary build time by 1.6x-2.3x;
- still blocked: five-run prepared reuse remains slower than the current route
  on clustered and road 65K profiles;
- next runtime action: implement a generic fused/native fixed-radius
  grouped-union work-reduction primitive that reduces candidate hits, root reads,
  and full partition-pair materialization together.

## Evidence

| Evidence | Reader meaning |
| --- | --- |
| Goal4074 | Current route timing: 0.093321s clustered, 0.036245s road; native grouped-union dominates. |
| Goal4079 | Current route still performs massive candidate and root-read work. |
| Goal4085 | Naive partition summary build was too expensive. |
| Goal4086 | Current native API cannot consume partition-pair work streams via a thin wrapper. |
| Goal4087 | Prepared reuse is a niche: clustered breaks even after about 11.04 repeated signatures; road never breaks even. |
| Goal4088 | Host-AABB skip improves build time, clustered break-even drops to 8.48, road still never breaks even. |

## What Changed

- `CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is now
  `rtdl.v2_10.current_benchmark_route_decisions.goal4091.v1`.
- The RT-DBSCAN route decision references Goals4084-4088.
- The unpromoted-candidate list explicitly includes
  `partition_convergence_hybrid default promotion after Goal4088 host-AABB skip improvement`.

## Boundary

This is advisory route metadata only. It does not authorize release action,
public speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, automatic partner selection,
AMD performance wording, hidden dispatch, or app-specific native-engine logic.
