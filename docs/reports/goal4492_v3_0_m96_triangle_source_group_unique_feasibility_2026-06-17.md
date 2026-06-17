# Goal4492 / V3 M96 Triangle Source-Group Unique Feasibility

## Conclusion

Goal4492 checks whether Triangle Counting's remaining unique/count boundary can be solved by a single small bounded local unique-count kernel over source groups.

The answer is no. On `com-lj` and `soc-LiveJournal1`, a 16K source-group bound covers most two-hop rows, but on `com-orkut` it covers only 69.43%. A 65K bound covers more than 98% of two-hop rows on all three paper-scale inputs, but that is too large for a simple small local kernel to be the default answer.

The next credible optimization is hybrid/two-pass: compact small source groups into a local unique-count path, and keep the heavy tail on the existing sort/RLE fallback. This preserves the app-agnostic primitive contract because the grouping policy stays in partner construction and the RT traversal remains generic prepared ray/triangle weighted any-hit.

## Evidence

Hardware: RTX 4000 Ada pod, driver 550.127.08.

Artifacts:

- `docs/reports/goal4492_v3_0_m96_triangle_source_group_unique_feasibility_2026-06-17.json`
- `docs/reports/goal4492_v3_0_m96_triangle_source_group_unique_feasibility_2026-06-17.jsonl`

The scan builds the same CuPy directed CSR/two-hop-count summary used by the current segmented RT-2A1 route. It does not run RT traversal and does not change the current route.

| Dataset | Sources | Directed edges | Two-hop rows | Max source rows | p99 | p99.9 |
|---|---:|---:|---:|---:|---:|---:|
| `com_lj` | 3,212,032 | 33,895,259 | 928,731,472 | 69,880 | 3,492 | 12,008 |
| `soc_livejournal1` | 4,256,557 | 42,260,523 | 1,383,299,326 | 96,990 | 4,529 | 17,795 |
| `com_orkut` | 3,004,674 | 117,117,316 | 8,579,930,671 | 118,057 | 35,063 | 61,411 |

| Dataset | <=4K rows | <=8K rows | <=16K rows | <=65K rows |
|---|---:|---:|---:|---:|
| `com_lj` | 77.06% | 88.20% | 93.73% | 99.85% |
| `soc_livejournal1` | 67.26% | 80.38% | 89.85% | 99.38% |
| `com_orkut` | 41.68% | 58.14% | 69.43% | 98.44% |

## Reading

A small bounded local source-group kernel would help the easy majority on `com_lj`, but it would leave too much of `com_orkut` on the old path. The data argues for a mixed implementation, not a single replacement.

Claim boundary:

- feasibility only;
- route changed: false;
- public speedup claim authorized: false;
- native engine customization: false;
- app-specific native engine callback: false.
