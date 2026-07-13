# Goals5480-5481: LibRTS Exact Point-Contains Result

## Result

The first exact official-input LibRTS correctness row is complete.

The POD shared filesystem reported ample free space but enforced a hidden quota.
Keeping the 23.06GB verified archive beside the 88.23GB full expansion failed
closed at 72GB. Goal5480 therefore introduced an evidence-bound selected-member
extractor. It reused the completed size/MD5 and safe-inventory gate, revalidated
member paths while scanning, wrote only the two requested regular files into a
staging directory, recorded size and SHA-256, and atomically promoted the
subset. It does not claim full archive extraction.

Exact members:

| Member | Bytes | SHA-256 |
|---|---:|---|
| `PPoPPAE/datasets/polygons/dtl_cnty.wkt` | 363,987,023 | `9177fdff45f24488f22157a2a1428a7cdb9d5a66a7287d4013ead52de1c7973f` |
| `PPoPPAE/datasets/queries/point-contains_queries_100000/dtl_cnty.wkt` | 3,976,199 | `95241f4e3f03c6dcea31b80e785a9729d4a4aaefeb82302e761b59d9c4fe39d3` |

Goal5481 passed those identical files to the pinned author binary and RTDL.
The author loader expands the 3,143 WKT source rows into 12,234 polygon index
records, so the app-owned RTDL loader was corrected to mirror MULTIPOLYGON
record expansion before execution.

| Field | Author | RTDL |
|---|---:|---:|
| indexed polygons | 12,234 | 12,234 |
| point queries | 100,000 | 100,000 |
| result count | 136,475 | 136,475 |

Machine verdict: `matched=true`.

RTDL used public API `expanded_aabb_point_membership_rows_2d`, backend `optix`,
with `rt_core_accelerated=true`, complete candidate coverage, and
`native_engine_customization=false`.

## Timing Boundary

The artifact records author internal query time (`0.0762ms`), RTDL app-owned
WKT load (`28.44s`), RTDL route wall (`1.76s`), and native primitive query
phase (`1.39s`). These are different denominators. No ratio is authorized.

## Not Proved

- author pair-row equality (the standard author binary exposes only count);
- Figure 6 reproduction or its full workload matrix;
- whole-paper reproduction;
- author-performance parity;
- full archive simultaneous extraction;
- Embree evidence.

## Verification

- focused local tests: 51 OK before the quota adaptation;
- subset/exact-runner tests: 13 OK, then 6 OK after MULTIPOLYGON expansion;
- POD current-source OptiX build succeeded and tiny hardware smoke returned
  `valid_count=1`, `rt_core_accelerated=true`;
- exact POD gate returned `matched=true`.

Exit label:

```text
completed_librts_first_exact_official_input_point_contains_count_gate__review_pending
```
