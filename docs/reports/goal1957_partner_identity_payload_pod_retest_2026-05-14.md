# Goal1957 Partner Identity-Payload Pod Retest

Date: 2026-05-14

Status: pod evidence accepted with boundary

## Environment

- Pod: `root@213.173.105.14 -p 20710`
- GPU: NVIDIA L4
- Driver: 550.127.05
- CuPy: 14.0.1
- OptiX headers: `/root/vendor/optix-sdk-v8.0.0`
- Built library: `build/librtdl_optix.so`
- Source label: `0fb6e049ac211d29ad4307d20a2972d1755d1b89`
- Runner output: `docs/reports/goal1957_partner_identity_payload_pod_optix_v800/`

## Retest Result

The Goal1957 identity-payload table removed the dense CPU cell-mask handoff from
the polygon CuPy continuation. The retest used the same L4/OptiX v8 setup as the
Goal1956 run and kept `--partner cupy`, `--candidate-backend optix`, `repeats=3`,
and `warmups=1`.

| app | copies | backend | Goal1956 v2 median s | Goal1957 v2 median s | v2 continuation improvement | Goal1957 v1.8 median s | Goal1957 v2/v1.8 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `database_analytics` | 100000 | `cpu_all_pairs` | 1.095086 | 1.023833 | 1.070x | 5.002953 | 0.205x |
| `graph_analytics` | 1000 | `cpu_all_pairs` | 0.000031 | 0.000030 | 1.017x | 9.658294 | 0.000003x |
| `polygon_pair_overlap_area_rows` | 2048 | `optix` | 2.626271 | 0.244991 | 10.720x | 0.172353 | 1.421x |
| `polygon_set_jaccard` | 2048 | `optix` | 2.486790 | 0.153636 | 16.186x | 0.144597 | 1.063x |

All four rows reported `matches_v1_8_python_rtdl_oracle=true`.

## Interpretation

This confirms the diagnosis in `goal1957_partner_identity_payload_contract`:
the severe polygon slowdown was caused by the partner handoff shape, not by RTDL
candidate discovery alone. Compact identity-preserving payload columns cut the
polygon continuation cost by about 10.7x and 16.2x compared with the previous
dense-mask v2 path.

The result is still a bounded checkpoint:

- `polygon_pair_overlap_area_rows` remains slower than v1.8 on this pod
  (`1.421x` v2/v1.8), though no longer catastrophically slower.
- `polygon_set_jaccard` is near parity (`1.063x` v2/v1.8), not a clean speedup.
- The extent reducer is exact for the authored axis-aligned control apps, not a
  general arbitrary polygon overlay implementation.
- This is not true zero-copy; Python still prepares NumPy payload columns before
  CuPy receives them.
- The graph headline ratio remains a closed-form continuation result, not a
  generic graph traversal acceleration claim.

## Claim Boundary

The pod runner kept all public authorization flags false:

- `v2_0_release_authorized=false`
- `whole_app_speedup_claim_authorized=false`
- `broad_rt_core_speedup_claim_authorized=false`
- `local_linux_gtx1070_is_release_perf_evidence=false`

## External Review

Claude reviewed the contract in
`docs/reviews/goal1957_claude_review_partner_identity_payload_contract_2026-05-14.md`
with verdict `accept-with-boundary`. The review accepted the diagnosis and first
implementation slice, while requiring the exact boundary above: do not reuse this
extent kernel as a claim for non-rectangular polygon overlay, and do not claim
zero-copy or release readiness.

