# Goal 1565 COLLECT_K Fused Materialize+Mark Probe

## Verdict

Diagnostic-only fused materialize+mark timing and parity probe.

## Scope

- Reference: existing materialize, mark, prefix, compact block.
- Candidate: memset marks/block_counts, fused materialize+mark with atomics, prefix, compact.
- Library: `build/librtdl_optix.so`
- Repeats: `2000`

## Result

| pairs | segment capacity | reference ms | fused ms | reference us/replay | fused us/replay | reference/fused | mismatches | first pair count |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2048 | 21.779221 | 23.854242 | 10.889610 | 11.927121 | 0.913x | 0 | 2048 |
| 4 | 2048 | 23.453294 | 32.061004 | 11.726647 | 16.030502 | 0.732x | 0 | 2048 |
| 16 | 2048 | 34.205898 | 45.865233 | 17.102949 | 22.932617 | 0.746x | 0 | 2048 |

## Claim Boundary

Diagnostic fused materialize+mark probe only; not a production COLLECT_K_BOUNDED optimization and not a public speedup claim.
