# External Critical Review: Phoenix V3 Hausdorff Threshold-Summary (repeat=5) - Row-Scoped M7 Candidate

Reviewer: External AI (Claude), 2026-06-21

Scope: Row-scoped M7 promotion for the 1,048,576-points-per-side row only.

## 1. Verdict

Approve with required amendments: two P0 fixes must precede packet update.

The candidate wording is scoped correctly and the largest row does show genuine
phase-total improvement under the same-contract test. However, two gaps in the
evidence packet are blocking before the
`row_scoped_public_speedup_claim_authorized` flag can be flipped, and three P1
issues should be addressed in the same pass.

## 2. Does The Evidence Satisfy Row-Scoped M7 For The Largest Row?

Conditionally yes, subject to P0 fixes.

The row at 1,048,576 points per side satisfies the structural requirements:

| Check | Result |
| --- | --- |
| Same-contract, both backends, same mode/threshold/repeat/warmup | Pass |
| Oracle correctness match | Pass |
| Same decision | Pass |
| Query speedup, 1.685x | Pass |
| Phase-total speedup, 1.264x | Pass |
| Wrapper speedup, 1.589x | Pass |
| RTX pod, not simulated, `--require-rt-core` | Pass |
| repeat=5/warmup=1, not repeat=1 | Pass |

What the evidence does not provide:

- Per-repeat timing breakdown or standard deviation. Five repeats averaged is
  not the same as five stable repeats. The packet reports mean values only. A
  1.264x phase-total win that is noisy could fall below 1.0x on any individual
  run. This is P0.
- Definition of oracle. `both_match_oracle: true` asserts correctness but the
  oracle is never defined in either the `.md` or `.json`. If the oracle is
  Embree itself, it is a same-decision check, not an independent ground-truth
  check. If it is a reference exact computation, the packet should say so. This
  is P0.

## 3. Do Mixed Small/Mid Rows Block Broader Wording?

Yes, absolutely.

| Row | Query win | Phase-total | Block reason |
| --- | --- | --- | --- |
| 65,536 pts/side | 1.891x | 0.583x regression | `phase_total_regression` |
| 262,144 pts/side | 1.831x | 0.995x parity | `phase_total_parity_not_win` |
| 1,048,576 pts/side | 1.685x | 1.264x | M7 candidate |

The 65,536-point row shows OptiX taking 1.77 s phase-total vs. Embree's 1.03 s,
a 72% overhead penalty. This is consistent with OptiX BVH setup cost dominating
at small scale. This pattern also reveals a structural risk for the large-row
claim: the phase-total win at 2^20 is achieved despite the same overhead, and
the overhead does not vanish. Any smaller real-world workload routed through
this path will regress.

The mixed-row evidence also reveals a decreasing query-speedup trend with scale
from 1.891 to 1.831 to 1.685. Extrapolation is speculative, but the trend is
not in favour of the claim strengthening at larger scales.

Broader wording, including "OptiX is faster for Hausdorff threshold-summary,"
is not supportable. The small-row regression alone kills it.

## 4. P0 / P1 Fixes Required

### P0 - Blocking

P0-1: Missing per-repeat variance data.

The `.json` `pairs` array reports single averaged values per configuration.
There are no `repeat_times`, `stddev`, or `min/max` fields. A 1.264x
phase-total speedup from a high-variance signal cannot be called stable. Either
add the per-repeat breakdown to the evidence artifact or report `stddev` in the
JSON. If the underlying artifact already contains this, surface it here.

P0-2: Oracle definition absent.

`both_match_oracle: true` is asserted in every row but the oracle is not defined
anywhere in the packet. Add an `oracle_definition` field to the JSON and
explain in the `.md` what ground truth is being compared against. If it is just
same-decision between OptiX and Embree, the field name "oracle" is misleading
and should be renamed or clarified.

### P1 - Should Fix In Same Pass

P1-1: Single-pod provenance.

All evidence is from `root@213.173.108.14 -p 11592`. The claim wording
correctly says "on an RTX 4000 Ada pod" singular, but the limitation should be
explicitly noted.

P1-2: Threshold specificity not called out as a scope limiter.

`threshold=0.4` should also appear in the JSON `not_scope` list. Performance on
a threshold-summary route is threshold-dependent. Add: `threshold values other
than 0.4`.

P1-3: Prepared mode semantics not explained.

`directed_threshold_prepared` implies BVH preparation is amortised or pre-built.
The small-row phase-total regression suggests scene prep is still counted in
phase-total. The packet should clarify what "prepared" excludes.

## 5. Exact Allowed Wording If P0 Fixes Are Resolved

```text
RTDL V3 includes a generic Hausdorff threshold-summary route where prepared
OptiX fixed-radius threshold decisions are 1.685x faster in query time and
1.264x faster in phase-total time than the same-contract Embree route at
1,048,576 points per side, threshold 0.4, repeat=5/warmup=1, on an RTX 4000 Ada
pod. Smaller rows in the same rerun are query wins but not phase-total wins.
```

This wording is acceptable as-is provided the P0 fixes are completed and the
evidence packet is updated to support it. No loosening of any qualifier is
permitted.

## 6. Exact Forbidden Wording

```text
RTDL computes full Hausdorff faster.
Hausdorff V3 is faster end to end.
X-HD is reproduced.
V3 is faster than V2.
OptiX is faster for all Hausdorff scales.
OptiX is faster for Hausdorff threshold-summary.
OptiX threshold decisions are faster at all sizes.
```

Additionally forbidden:

- Citing only the 1.685x query speedup without disclosing the 1.264x
  phase-total figure.
- Citing only the phase-total figure without naming the specific row and
  threshold.
- Using "RTX" as shorthand for "any RTX GPU"; must say "RTX 4000 Ada"
  specifically.

## Summary

The largest row is a genuine, honestly represented speedup at the tested scale
and threshold. The candidate wording is appropriately narrow. Two P0 gaps, no
variance data and no oracle definition, must be closed before the authorization
flags change. The mixed small/mid rows are correctly blocked and must not
contaminate the claim scope. If the P0 fixes are clean, this row-scoped M7
claim is approvable without further external review.
