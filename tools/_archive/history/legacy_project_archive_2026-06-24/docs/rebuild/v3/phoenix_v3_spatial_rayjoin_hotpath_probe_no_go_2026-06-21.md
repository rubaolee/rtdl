# Phoenix V3 Spatial RayJoin Hotpath Probe No-Go

Status: `spatial_rayjoin_hotpath_probe_no_go_author_gap_not_closed`.

This packet records a fresh same-POD hotpath sweep for the Spatial RayJoin point-location topology-stream gap. It does not promote M7 and does not authorize any public speedup claim.

## Protocol

- Dataset: `data/rayjoin_public_cdb/br_county.cdb`
- GPU: `NVIDIA RTX 4000 Ada Generation, 550.127.05`
- Query repeat: `50`
- Warmup: `5`
- Sample repeat: `2`
- Exact authority count: `47262`
- Same-dataset RayJoin author Query timer: `1.865660 ms`

## Legal Route Sweep

| Route | Point order | Count | Hot query ms | RT traversal ms | M7 |
| --- | --- | ---: | ---: | ---: | --- |
| exact_prepared_points_executor | y_then_x | 47262 | 23.262223 | 0.366391 | no |
| relation_status_corrected_executor_validated | morton_xy | 47262 | 6.590802 | 6.437929 | no |
| relation_status_corrected_executor_validated | morton_xy | 47262 | 6.526185 | 6.286488 | no |
| relation_status_corrected_executor_validated | natural | 47262 | 5.927980 | 5.890282 | no |
| relation_status_corrected_executor_validated | x_then_y | 47262 | 6.645916 | 6.461468 | no |
| relation_status_corrected_executor_validated | y_then_x | 47262 | 5.406518 | 5.349101 | no |

## Best Legal Route

- Route: `relation_status_corrected_executor_validated`
- Point order: `y_then_x`
- Hot query: `5.406518 ms`
- Same-dataset author Query: `1.865660 ms`
- RayJoin author speedup vs best legal RTDL hotpath: `2.898x`

Interpretation: the best exact RTDL route is still slower than the same-dataset RayJoin author Query timer, so the Spatial gap remains open.

## Rejected Route

- Route: `device_filtered_prepared_points_validated`
- Failure: `validated_candidate_exactness_mismatch`
- Observed count: `47570`
- Exact count: `47262`
- Delta: `308`

This route is not legal V3 evidence because the validated device-side count does not equal the exact prepared count.

## Claim Boundary

- `release_authorized: false`
- `m7_promotion_authorized: false`
- `m7_qualified_release_rows_added: 0`
- `rtdl_beats_rayjoin_claim_authorized: false`
- `paper_reproduction_claim_authorized: false`

## Required Before M7

- A same-contract route with exact stable row count 47262 that is not slower than the RayJoin author Query basis.
- Author result-count parity or public wording that explicitly refuses count-equivalence claims.
- External AI review and Codex consensus after any new promotable evidence.
- Public wording review that keeps paper reproduction and RTDL-beats-RayJoin claims false unless the same-dataset basis supports them.

## Goal-Level Decision Self-Audit

Decision: Keep Spatial RayJoin point-location topology stream as no-go for Phoenix V3 after fresh same-POD hotpath sweep.

1. Was I foolish?
   No. I used the verified POD, same dataset, exact count authority, and did not promote a route that failed the author-speed or exactness bar.
2. If yes, what actions made the decision foolish?
   The foolish actions would be to call a 5.4 ms route a success against a 1.86566 ms author timer, or to hide the device-filtered 47570 != 47262 mismatch.
3. Was there another path that would have avoided getting stuck on one idea?
   I could have jumped to a new app family immediately, but this remaining release-breadth gap had a concrete reopen bar and needed one bounded re-test.
4. Can I now try a different path that actually solves the problem?
   Stop spending V3 release confidence on this Spatial route unless a real generic traversal optimization is designed; move to the next engine target or record this as future research.
