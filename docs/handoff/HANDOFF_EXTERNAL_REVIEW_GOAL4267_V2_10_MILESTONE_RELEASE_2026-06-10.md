# Handoff: External Review For Goal4267 v2.10 Milestone Release

Date: 2026-06-10

## Task

Perform an independent read-only release review of the exact v2.10 milestone
packet and write a formal review file.

## Required Output Paths

Claude should write:

`docs/reviews/goal4268_claude_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md`

Gemini should write:

`docs/reviews/goal4269_gemini_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md`

## Primary Files To Review

- `docs/reports/goal4267_v2_10_milestone_release_packet_2026-06-10.md`
- `tests/goal4267_v2_10_milestone_release_packet_test.py`
- `docs/reports/goal4266_large_scale_cupy_numba_partner_comparison_2026-06-09.md`
- `docs/reports/goal4266_large_scale_partner_comparison/summary.json`
- `tests/goal4266_large_scale_partner_comparison_test.py`
- `docs/learn/partner_choice_for_custom_logic.md`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/reports/goal4257_v2_10_release_candidate_packet_draft_2026-06-09.md`
- `docs/reports/goal4254_v2_10_public_claim_wording_candidate_2026-06-09.md`
- `docs/reports/goal4258_public_claim_wording_repair_closure_2026-06-09.md`
- `docs/reports/goal4261_major_performance_target_map_after_claim_wording_closure_2026-06-09.md`
- `docs/reports/goal4262_exact_head_release_prep_pod_validation_2026-06-09.md`

## Validation Command

Run or inspect this focused gate:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4267_v2_10_milestone_release_packet_test tests.goal4265_partner_guidance_user_facing_cleanup_test tests.goal4266_large_scale_partner_comparison_test tests.goal4257_v2_10_release_candidate_packet_draft_test tests.goal4254_v2_10_public_claim_wording_candidate_test tests.goal4258_public_claim_wording_repair_closure_test
```

Codex has run it locally and observed:

```text
Ran 20 tests in 1.210s
OK
```

## Review Questions

1. Is Goal4267 a correct final milestone packet for v2.10, given the current
   restricted source-tree release scope?
2. Does the packet correctly incorporate Goal4266 and avoid misleading
   subsecond or missing-partner rows in learner-facing guidance?
3. Do the learner docs now state the user-facing partner decision clearly:
   primitive-first when possible, CuPy for current performance on the measured
   large-scale custom continuations, and Numba for no-RawKernel Python-source
   reference constraints?
4. Does the packet preserve all blocked claims: package-install readiness,
   universal speedup, broad RT-core guarantee, whole-app guarantee,
   RTDL-beats-RayJoin wording, paper reproduction, true zero-copy,
   automatic backend/partner selection, AMD/HIPRT performance, Embree+Numba CPU
   partner, app-specific native engine logic, and universal CuPy-vs-Numba
   winner claims?
5. Is it acceptable that the last runtime/performance commit is `0c842eb0` and
   the final release-packet delta is documentation/governance only?
6. What, if anything, must be fixed before Codex writes the 3-AI consensus file
   and creates/pushes the `v2.10` tag?

## Allowed Verdicts

Use exactly one:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

## Boundary

This review may accept the packet as a milestone-release input, but it must not
create or move tags and must not authorize any blocked public claim. The final
release action requires Codex synthesis plus both external reviews.
