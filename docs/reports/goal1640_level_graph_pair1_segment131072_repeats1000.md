# Goal 1557 COLLECT_K Level Graph Replay Probe

## Verdict

The real collect-k compact-level kernel chain is graph-replayable in this diagnostic probe.

## Scope

- Probe: actual four-kernel collect-k compact-level sequence.
- Sequence: materialize, mark, device-prefix, compact.
- Library: `build/librtdl_optix.so`
- Repeats: `1000`

## Result

| pairs | segment capacity | direct ms | graph ms | direct us/replay | graph us/replay | direct/graph | first pair count |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 131072 | 119.210037 | 107.027736 | 119.210037 | 107.027736 | 1.114x | 262144 |

Best direct-over-graph speedup: `1.114x`.

## Claim Boundary

Diagnostic collect-k compact-level graph replay only; not a production COLLECT_K_BOUNDED optimization and not a public speedup claim.
