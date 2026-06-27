# Goal 1557 COLLECT_K Level Graph Replay Probe

## Verdict

The real collect-k compact-level kernel chain is graph-replayable in this diagnostic probe.

## Scope

- Probe: actual four-kernel collect-k compact-level sequence.
- Sequence: materialize, mark, device-prefix, compact.
- Library: `build/librtdl_optix.so`
- Repeats: `5000`

## Result

| pairs | segment capacity | direct ms | graph ms | direct us/replay | graph us/replay | direct/graph | first pair count |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2048 | 54.443597 | 45.854471 | 10.888719 | 9.170894 | 1.187x | 4096 |
| 4 | 2048 | 58.961368 | 50.866699 | 11.792274 | 10.173340 | 1.159x | 4096 |
| 16 | 2048 | 85.732588 | 76.409591 | 17.146518 | 15.281918 | 1.122x | 4096 |

Best direct-over-graph speedup: `1.187x`.

## Claim Boundary

Diagnostic collect-k compact-level graph replay only; not a production COLLECT_K_BOUNDED optimization and not a public speedup claim.
