# Handoff: Goal3668 v2.9 Closeout And Next-Direction Refresh Review

Date: 2026-06-06

Please perform a read-only independent Gemini review of Goal3668 and write the
review to:

`docs/reviews/goal3669_gemini_review_goal3668_v2_9_closeout_next_direction_refresh_2026-06-06.md`

## Context

Goal3619/3622 proposed the next-version direction, but that packet became
stale in one important way: it described RayJoin PIP as CuPy-owned. Goals3658,
3660, 3663, and 3665 changed that reading.

Goal3668 refreshes the v2.9 closeout/next-direction position:

- RTDL/OptiX now has validated-domain PIP one-shot/sequential improvement over
  the prior project-owned CuPy dense baseline.
- RTDL/OptiX has strong batched repeated-request PIP throughput on 512 and
  4096 public-CDB slices.
- Full-county PIP still fails exactness (`47264 != 47262`) and now fails before
  RayJoin timing via the Goal3665 preflight guard.
- Therefore the next-version direction remains contract-and-residency first,
  but topology-aware closed-shape membership/correction joins segment-pair
  contracts as a first-class target.

Files to inspect:

- `docs/reports/goal3668_v2_9_closeout_and_next_direction_refresh_2026-06-06.md`
- `tests/goal3668_v2_9_closeout_and_next_direction_refresh_test.py`
- `docs/reports/goal3602_v2_9_benchmark_status_after_resident_evidence_2026-06-06.md`
- `docs/research/future_version_to_do_list.md`
- `docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md`
- `docs/reviews/goal3666_gemini_review_goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md`

## Review Questions

1. Does Goal3668 correctly update the RayJoin PIP reading after Goals3658,
   3660, 3663, and 3665?
2. Does it fairly state the v2.9 closeout decision: stop small current-version
   tuning unless the task fixes correctness, offers a large material gain,
   creates reusable generic capability, or supplies missing evidence?
3. Does the updated next-direction target list make sense: segment-pair
   contracts, topology-aware closed-shape membership/correction, typed resident
   primitive outputs, and deterministic grouped reductions/witness contracts?
4. Does it avoid public release/speedup/RTDL-beats-RayJoin/true-zero-copy
   claims?
5. Does it preserve the rule that strict next-version roadmap consensus is not
   final until Claude review is obtained and reconciled?

## Validation

Codex local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3668_v2_9_closeout_and_next_direction_refresh_test tests.goal3602_v2_9_benchmark_status_after_resident_evidence_test tests.goal3665_rayjoin_pip_fast_domain_preflight_guard_test
```

Result: 12 tests OK.

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Please explicitly state this is independent Gemini review, distinct
from Codex, and that it authorizes no public release or public speedup claims.
