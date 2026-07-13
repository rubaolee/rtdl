# Goal5419 - X-HD Figure 5 Level-B Same-POD Graphics Matrix

## Verdict

```text
completed_figure5_level_b_same_pod_graphics_matrix__level_b_only_no_ratio
```

Goal5419 executes the three Goal5418 primary graphics rows on the same POD:

```text
dragon_happy
thai_happy_scaled
thai_asian_scaled
```

This is a Level-B same-source graphics matrix. It is **not** Figure 5
reproduction, not exact paper dataset reproduction, and not an
author-vs-RTDL performance ratio.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5419.figure5_level_b_same_pod_graphics_matrix.v1
same_pod_execution_claimed = true
matrix_rows_executed = 3
route_result_count = 6
matched = true
```

POD:

```text
host = 213.173.108.24
port = 13502
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

POD access used only:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<remote command>"
```

No naked SSH was used.

## Important Precondition Fixed Before Execution

Before executing Goal5419, the Goal5418 packet was corrected so every RTDL
graphics command carries:

```text
--translate-each-input-to-min-bound
```

This preprocessing is required by the established public-graphics gates.  A
preliminary Dragon/HappyBuddha smoke without the flag returned the wrong scalar
HDResult (`0.0778348243`).  With the flag, the smoke returned the expected
value:

```text
0.12572988629271128
```

The Goal5418 packet and tests now assert:

```text
required_rtdl_preprocessing = ["translate_each_input_to_min_bound"]
```

## Matrix

All author reruns match the paper-branch author-log scalar within `1e-6`, and
all RTDL routes match the same-POD author rerun scalar within `1e-6`.

| Case | Author HDResult | Author AvgTime ms | Author process wall s | RTDL route | RTDL HDResult | Abs diff vs author | RTDL route wall s | RTDL process wall s | Input load s | Exact witnesses |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| dragon_happy | 0.12572988867759705 | 8.128 | 1.934 | cell-mbr-fast-scalar | 0.12572988629271128 | 2.3849e-09 | 0.540 | 2.243 | 0.689 | false |
| dragon_happy | 0.12572988867759705 | 8.128 | 1.934 | cell-mbr-exact-witness | 0.12572988629271128 | 2.3849e-09 | 0.617 | 2.283 | 0.689 | true |
| thai_happy_scaled | 0.21912431716918945 | 26.817 | 2.345 | cell-mbr-exact-witness | 0.2191243235042005 | 6.3350e-09 | 5.017 | 6.880 | 0.646 | true |
| thai_happy_scaled | 0.21912431716918945 | 26.817 | 2.345 | cell-mbr-fast-scalar | 0.2191243235042005 | 6.3350e-09 | 1.099 | 3.035 | 0.664 | false |
| thai_asian_scaled | 0.28763842582702637 | 19.281 | 2.437 | cell-mbr-exact-witness | 0.2876384148709406 | 1.0956e-08 | 10.805 | 12.748 | 0.478 | true |
| thai_asian_scaled | 0.28763842582702637 | 19.281 | 2.437 | cell-mbr-fast-scalar | 0.2876384148709406 | 1.0956e-08 | 12.536 | 14.557 | 0.473 | false |

## Interpretation

This is useful Figure-5-like evidence because the matrix runs author and RTDL on
the same POD and separates the denominators that had previously been mixed:

```text
author Running.AvgTime
author process wall
RTDL route wall
RTDL process wall
RTDL input load
per_source_witness_exact
```

It still does **not** authorize a ratio:

```text
author Running.AvgTime is an internal author algorithm timer;
author process wall includes author process/runtime overhead;
RTDL route wall is app route timing;
RTDL process wall includes Python process and app overhead.
```

These are side-by-side columns, not a single denominator.

## Observations

- `cell-mbr-fast-scalar` is the fastest RTDL route for `dragon_happy` and
  `thai_happy_scaled`.
- `cell-mbr-fast-scalar` is **slower** than `cell-mbr-exact-witness` on
  `thai_asian_scaled` because that workload produces enough continuation work
  that global-bound early break is not a free win.
- `cell-mbr-fast-scalar` has `per_source_witness_exact=false`; it can support
  scalar directed-HD equality, not exact per-source witness reproduction.
- `cell-mbr-exact-witness` has `per_source_witness_exact=true`; it is the
  correct route when witness exactness is part of the claim.

## Claim Boundary

Authorized:

- same-POD Level-B graphics scalar matrix;
- same-source public graphics value matching for three cases;
- side-by-side denominator columns;
- route-local RTDL timing columns;
- exact-witness vs fast-scalar witness-contract distinction.

Not authorized:

- Figure 5 reproduction;
- exact paper dataset reproduction;
- author-vs-RTDL performance ratio;
- author RT-core algorithm equivalence;
- full X-HD paper reproduction;
- treating fast-scalar as exact witness reproduction.

## Validation

Commands:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight

py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<Goal5419 matrix command>"

py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 download \
  /tmp/xhd_goal5419/results/xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json \
  Paper-reproduction-apps\x-hd-paper\results\xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json

$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5419_figure5_level_b_same_pod_graphics_matrix_test \
  tests.goal5418_figure5_level_b_same_pod_matrix_readiness_test \
  tests.goal5417_figure5_level_b_same_pod_matrix_plan_test \
  tests.goal5416_full_reproduction_priority_refresh_test
```

Result:

```text
Ran 22 tests
OK
```

The local Python launcher prints the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still pass.

## Recommended Next

```text
Goal5420_figure5_level_b_matrix_consolidation_and_next_decision
```

Goal5420 should decide whether to:

1. stop after this same-POD Level-B graphics matrix and send it for review;
2. add a separate bounded-geo matrix packet using the partner/Triton runner
   family; or
3. return to exact dataset acquisition / Figure 7-11 blockers.

It should not publish a ratio unless a separate denominator review authorizes
one.
