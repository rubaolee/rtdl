# Goal4050 RayJoin PIP Graph Replay Quarantine

Date: 2026-06-08

Status: internal route-guidance refresh; no release or public speedup authorization.

## Purpose

Goal3842 confirmed that the generic prepared point/closed-shape batch executor is
the useful RTDL/OptiX lane for repeated RayJoin-style PIP requests, while CUDA
graph replay remained blocked by a zero-count replay failure. Goal4050 reruns a
small current-main pod probe so the route registry can stop treating graph
replay as a near-term performance lever.

## Pod Evidence

Pod:

`ssh root@213.173.108.27 -p 15138 -i ~/.ssh/id_ed25519`

Repository commit:

`15c91c6d`

Artifact:

`docs/reports/goal4050_rayjoin_pip_graph_current_negative_probe_pod.json`

The probe uses the checked-in `tests/fixtures/rayjoin/br_county_subset.cdb`
fixture with `RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE=1` and
`RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9`.

## Result

The trusted non-graph lanes remain correct:

| Lane | Observed |
| --- | --- |
| Single prepared count | `6` |
| Prepared batch count, 5 requests | `[6, 6, 6, 6, 6]` |
| Reusable prepared batch executor, 5 requests | `[6, 6, 6, 6, 6]` |

The graph lane is still not usable:

| Lane | Status |
| --- | --- |
| Graph with validation | `failed_closed`, `OptiX error: CUDA error` |
| Raw graph without validation | `prepare_or_replay_failed`, `OptiX error: CUDA error` |

This current-main failure is slightly different from the older Goal3312
zero-count replay: today the graph handle can fail during native prepare before
any replay result is exposed. Both outcomes point to the same route decision:
prepared-points CUDA graph replay is quarantined until a real OptiX-capture fix exists.

## Route Decision

The route guidance now says:

- keep the working generic prepared point/closed-shape batch executor for
  repeated PIP requests;
- keep the relation-status corrected scalar-count executor for exact scalar
  counts where that contract is selected;
- do not use prepared-points CUDA graph replay as performance evidence;
- do not spend near-term engineering cycles on graph replay unless the work is a
  direct OptiX/CUDA capture fix with hardware proof.

The next useful RayJoin work remains larger generic route evidence and
non-dense baseline policy, not another app-specific graph-replay timing probe.

## Claim Boundary

Goal4050 does not authorize:

- release action;
- public speedup wording;
- whole-app RayJoin wording;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- automatic partner/backend selection.
