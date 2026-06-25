# Call For Review: V4 Goal4639 Serious Release Scorecard POD Gate

Please critically review Goal4639 completion. This is a review of the serious
POD release scorecard result, not a request for final V4 release authorization.

## Requested Verdict Labels

Choose exactly one:

- `approve_goal4639_scorecard_pass_continue_goal4640`
- `approve_with_required_amendments_before_goal4640`
- `reject_goal4639_scorecard_do_not_continue_release_path`

## Controlling Inputs

- Goal list:
  `future/v4/v4_formal_high_performance_release_hardening_goals_4633_4644_2026-06-25_owner_review.md`
- Frozen scorecard:
  `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`
- Goal4638 review record:
  `future/v4/reviews/goal4638_formal_release_scorecard_freeze_review_record_2026-06-25.md`

## Goal4639 Artifacts

- `scripts/v4_goal4639_release_scorecard_pod_gate.py`
- `src/rtdsl/v4_goal4639_release_scorecard.py`
- `src/rtdsl/v4_goal4639_release_scorecard_decision.py`
- `tests/v4_goal4639_release_scorecard_test.py`
- `tests/v4_goal4639_release_scorecard_decision_test.py`
- `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.json`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/run.log`

Updated release-decision integration:

- `src/rtdsl/v4_release_decision.py`
- `tests/v4_goal4632_release_decision_test.py`

## Result To Review

Goal4639 ran the frozen Goal4638 scorecard on the RTX A5000 POD.

Summary:

- recommendation: `release_candidate_possible_pending_3ai`
- strong families: `4/4` passed
- measured surfaces: `8/8` passed
- partial controls: `4/4` passed
- deferred/excluded rows: `2`
- failed surfaces: `0`
- strong representative ratio geomean: `5.1848067367961095x`

Surface representative ratios:

- fixed-radius count-threshold: `1.69721x`
- closest-hit grouped argmin: `1.25677x`
- any-hit flags: `5.67055x`
- primitive grouped-i64 reduction: `1.38362x`
- point-group nearest witness: `389.707x`
- any-hit weighted sum: `1.48181x`
- fixed-radius graph component-union: `1.20294x`
- AABB all-ops count: `164.716x`

## Verification

POD run:

```bash
PYTHONPATH=src:. python3 scripts/v4_goal4639_release_scorecard_pod_gate.py \
  --output-dir future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25
```

Local tests after pulling POD evidence:

```powershell
py -m unittest tests.v4_goal4639_release_scorecard_decision_test tests.v4_goal4639_release_scorecard_test tests.v4_goal4632_release_decision_test
```

Result: `11 tests OK`.

Full local V4 sweep:

```powershell
py -m unittest @modules
```

Result: `160 tests OK`.

## Review Questions

1. Did Goal4639 actually run the frozen Goal4638 scorecard, rather than a
   weaker or post-hoc scorecard?
2. Are the surface/family pass results consistent with the frozen floor table?
3. Is `release_candidate_possible_pending_3ai` the correct scorecard
   recommendation while still withholding release/RC authorization?
4. Are the partial and deferred rows handled honestly, especially
   `spatial_rayjoin` and `barnes_hut`?
5. Is the updated `v4_release_decision.py` honest: Goal4639 is no longer a
   blocker, but final release remains blocked by docs cleanup, clean-tree
   reproducibility, review debt, and final 3-AI authorization?
6. Are there any amendments required before proceeding to Goal4640?

## Non-Authorization

This review must not authorize V4 release, V4 release-candidate wording, broad
V4 speedup claims, whole-app speedup claims, all-benchmark speedup claims,
public true-zero-copy claims, Tier-3 callback support, raw OptiX callback
support, CuPy performance claims, C ABI, embedding, non-Python host claims, or
app-specific native kernels.
