# V4 Goal4636C AABB Index All-Ops POD Gate Evidence

This directory contains the POD evidence used by Goal4636C and promoted through
Goal4637.

Raw result:

- `m30_all_ops.json`

Important provenance note: the raw JSON was produced by the older M30 LibRTS
prepared all-ops runner, so it contains historical labels such as
`Goal4427 V3.0 M30`. Goal4637 does not promote those labels. The promoted V4
claim is narrower:

- generic primitive: `AABB_INDEX_QUERY_2D`
- V4 surface: `v4_aabb_index_query_2d_all_ops_count_prepared_runner`
- scope: RTDL native prepared runner
- measured hardware: RTX A5000 POD
- comparison: same-contract-family Embree control vs OptiX prepared query set
- claim boundary: operator coverage only, not LibRTS paper reproduction,
  authors-code comparison, whole-app speedup, broad V4 speedup, or release
  authorization

Key gate values:

- count parity: pass
- accepted contract family: pass
- Embree / OptiX query median: `264.822x`
- Embree / OptiX query total: `115.007x`
