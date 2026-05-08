# Goal 1559 COLLECT_K Level Graph Update Probe

## Verdict

CUDA graph executable kernel-node parameter update completed for the real collect-k compact-level sequence in this diagnostic probe.

## Scope

- Probe: capture one collect-k compact-level graph, update kernel node parameters, replay target topology.
- Sequence: materialize, mark, device-prefix, compact.
- Library: `build/librtdl_optix.so`
- Repeats: `5000`

## Result

| initial pairs | target pairs | segment capacity | direct ms | graph-update ms | direct us/replay | graph-update us/replay | direct/graph-update | nodes | first pair count |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 2048 | 58.728800 | 50.801607 | 11.745760 | 10.160321 | 1.156x | 4 | 4096 |
| 1 | 16 | 2048 | 86.580558 | 76.446273 | 17.316112 | 15.289255 | 1.133x | 4 | 4096 |

Best direct-over-updated-graph speedup: `1.156x`.

## Claim Boundary

Diagnostic collect-k graph executable parameter update only; not a production COLLECT_K_BOUNDED optimization and not a public speedup claim.
