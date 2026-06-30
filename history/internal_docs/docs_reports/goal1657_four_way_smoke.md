# Goal1657 v1.6.x OptiX Collect-K Four-Way Merge Probe

## Verdict

`diagnostic_four_way_merge_probe_recorded`

## Scope

- Reference: two binary compact-level merge blocks over four sorted segments.
- Candidate: one four-way materialize+mark block plus prefix and compact.
- Library: `build/librtdl_optix.so`
- Repeats: `100`

## Result

| groups | segment capacity | reference ms | four-way ms | reference us/replay | four-way us/replay | reference/four-way | mismatches | first group count |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2048 | 2.831436 | 2.648120 | 28.314360 | 26.481200 | 1.069x | 0 | 2048 |
| 4 | 2048 | 3.213676 | 3.251166 | 32.136760 | 32.511660 | 0.988x | 0 | 2048 |
| 16 | 2048 | 5.328762 | 6.768000 | 53.287620 | 67.680000 | 0.787x | 0 | 2048 |

## Claim Boundary

Diagnostic four-way collect-k merge probe only; not a production COLLECT_K_BOUNDED optimization and not a public speedup claim.
