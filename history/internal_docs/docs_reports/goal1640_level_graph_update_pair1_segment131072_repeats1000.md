# Goal 1559 COLLECT_K Level Graph Update Probe

## Verdict

CUDA graph executable kernel-node parameter update completed for the real collect-k compact-level sequence in this diagnostic probe.

## Scope

- Probe: capture one collect-k compact-level graph, update kernel node parameters, replay target topology.
- Sequence: materialize, mark, device-prefix, compact.
- Library: `build/librtdl_optix.so`
- Repeats: `1000`

## Result

| initial pairs | target pairs | segment capacity | direct ms | graph-update ms | direct us/replay | graph-update us/replay | direct/graph-update | nodes | first pair count |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 131072 | 119.258329 | 116.440828 | 119.258329 | 116.440828 | 1.024x | 4 | 262144 |

Best direct-over-updated-graph speedup: `1.024x`.

## Claim Boundary

Diagnostic collect-k graph executable parameter update only; not a production COLLECT_K_BOUNDED optimization and not a public speedup claim.
