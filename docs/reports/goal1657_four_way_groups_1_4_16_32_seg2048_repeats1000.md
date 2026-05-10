# Goal1657 v1.6.x OptiX Collect-K Four-Way Merge Probe

## Verdict

`diagnostic_four_way_merge_probe_recorded`

## Scope

- Reference: two binary compact-level merge blocks over four sorted segments.
- Candidate: one four-way materialize+mark block plus prefix and compact.
- Library: `build/librtdl_optix.so`
- Repeats: `1000`

## Result

| groups | segment capacity | reference ms | four-way ms | reference us/replay | four-way us/replay | reference/four-way | mismatches | first group count |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2048 | 28.105750 | 26.291391 | 28.105750 | 26.291391 | 1.069x | 0 | 2048 |
| 4 | 2048 | 32.214820 | 32.567389 | 32.214820 | 32.567389 | 0.989x | 0 | 2048 |
| 16 | 2048 | 53.450896 | 60.102464 | 53.450896 | 60.102464 | 0.889x | 0 | 2048 |
| 32 | 2048 | 76.026628 | 103.894742 | 76.026628 | 103.894742 | 0.732x | 0 | 2048 |

## Claim Boundary

Diagnostic four-way collect-k merge probe only; not a production COLLECT_K_BOUNDED optimization and not a public speedup claim.
