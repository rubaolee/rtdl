# Goal5300 - X-HD ThaiStatuette -> AsianDragon RTDL Level-B Comparison

Date: 2026-07-09

## Verdict

```text
completed_level_b_thai_asian_rtdl_comparison__scalar_matched_no_ratio
```

## Scope

Goal5300 extends the Goal5298 author-only graphics precheck to a second
value-matched Stanford graphics case:

```text
ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3
```

This is Level-B same-source public-data evidence. It is not exact paper dataset
reproduction, not full Figure 5 reproduction, and not an author-vs-RTDL
performance ratio.

## Author Baseline

Source: Goal5298 author-only graphics precheck.

```text
author HDResult        = 0.28763842582702637
paper-log HDResult     = 0.28763845562934875
paper-log abs diff     = 2.9802322387695312e-08
author Running.AvgTime = 18.692 ms
author process wall    = 2.3879314661026 s
points A/B             = 4,999,996 / 3,609,600
```

The author rerun matches the paper-branch author-log scalar value within the
existing `1e-6` Level-B tolerance.

## RTDL Routes

Both RTDL routes were executed on the current POD through
`scripts/current_pod_ssh.py`, using:

```text
RTDL_OPTIX_LIB=/tmp/rtdl_goal5236/build/librtdl_optix.so
input1=/tmp/xhd_goal5298/data/thai_statuette_scaled_1e-3.ply
input2=/tmp/xhd_goal5298/data/asian_dragon_scaled_1e-3.ply
--translate-each-input-to-min-bound
--grid-shape 32,32,32
--max-inline-points 512
```

Results:

```text
cell-mbr-exact-witness:
  HDResult                  = 0.2876384148709406
  abs diff vs author         ~= 1.10e-08
  route wall                 = 10.764273278415203 s
  total                      = 11.779786556959152 s
  process wall               = 12.701385200023651 s
  per_source_witness_exact   = true
  frontier_row_count         = 0
  candidate distance evals   = 74,991,882,950

cell-mbr-fast-scalar:
  HDResult                  = 0.2876384148709406
  abs diff vs author         ~= 1.10e-08
  route wall                 = 12.505260519683361 s
  total                      = 13.526285588741302 s
  process wall               = 14.527451686561108 s
  per_source_witness_exact   = false
  global early-break count   = 3,900,606
  frontier_row_count         = 4,661,813
  candidate distance evals   = 10,532,778,633
```

Unexpected but important: on this pair, the exact-witness route is faster than
the fast-scalar route. The fast-scalar path still matches the scalar directed-HD
value, but it produces millions of frontier rows and spends most of its route
time in nearest continuation. Therefore `cell-mbr-fast-scalar` is not a
universal performance promise; it is a scalar-value route whose benefit is
workload-dependent.

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_exact_witness_process_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_fast_scalar_process_pod.json
tests/goal5300_xhd_thai_asian_rtdl_comparison_test.py
```

## Validation

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_level_b_rtdl_comparison_matrix_2026-07-09.json
py -m unittest tests.goal5300_xhd_thai_asian_rtdl_comparison_test
```

## Claim Boundary

Allowed:

```text
Goal5300 is a Level-B same-source RTDL comparison for one public Stanford
graphics case. Both RTDL routes match the Goal5298 author rerun scalar HDResult
within 1e-6.
```

Not allowed:

```text
exact paper dataset reproduction;
Figure 5 reproduction;
full X-HD paper reproduction;
author-vs-RTDL performance ratio;
author RT-core algorithm equivalence;
exact per-source witness claim for the fast-scalar route.
```

## Recommended Next Work

The Level-B graphics line now has RTDL comparisons for:

```text
Dragon -> HappyBuddha
ThaiStatuette scaled -> HappyBuddha
ThaiStatuette scaled -> AsianDragon scaled
```

Recommended next action is a consolidated Goal5298-5300 review packet for the
current graphics Level-B evidence. Do not upgrade this to Figure 5 reproduction:
it is still graphics-only, public same-source, and lacks exact paper dataset
identity and same-denominator performance review.
