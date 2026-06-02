# Handoff: Claude Review for Goal3062 v2.6 Native Tutorial Validation

Please perform a read-only review of Goal3062 and write your review to:

`docs/reviews/goal3063_claude_review_goal3062_v2_6_native_tutorial_validation_2026-06-02.md`

## Context

Goal3062 closes the native runnable tutorial/example gate left open by the
Goal3058/3061 v2.6 documentation audit and 3-AI consensus. It validates the
curated v2.6 release-candidate tutorial/example command surface on a Linux pod
with Embree, OptiX/RT, and CuPy available.

Primary files to inspect:

- `docs/reports/goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.md`
- `docs/reports/goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.json`
- `docs/reports/goal3062_v2_6_native_tutorial_example_pod_validation_logs_2026-06-02/`
- `tests/goal3062_v2_6_native_tutorial_example_pod_validation_test.py`
- `docs/release_facing_examples.md`
- `docs/reports/goal3061_v2_6_doc_total_audit_3ai_consensus_2026-06-02.md`

## Checks Requested

Please answer these questions explicitly:

1. Does the JSON evidence support a complete `21/21` pass on the corrected
   curated pod validation run?
2. Does the evidence cover portable Python, Embree, OptiX/RT, and CuPy partner
   paths without stale failed-command logs being treated as passing evidence?
3. Is the public docs fix from `--partner cupy --backend optix` to
   `--partner cupy-cuda --backend optix` correct for the current parser?
4. Does the report preserve release boundaries and avoid authorizing v2.6,
   package-install claims, broad RT-core speedup claims, automatic partner
   selection, or general zero-copy/device-residency claims?
5. Are the tests strong enough to prevent accidental regression of the evidence
   shape and public command spelling?

## Validation Commands

If you run tests, use:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3062_v2_6_native_tutorial_example_pod_validation_test tests.goal3061_v2_6_doc_total_audit_3ai_consensus_test tests.goal3058_v2_6_release_candidate_doc_total_audit_test tests.goal3056_v2_6_pre_release_public_doc_cleanup_audit_test
```

Expected local result from Codex: `Ran 17 tests ... OK`.

Broader slice:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3062_v2_6_native_tutorial_example_pod_validation_test tests.goal3061_v2_6_doc_total_audit_3ai_consensus_test tests.goal3058_v2_6_release_candidate_doc_total_audit_test tests.goal3056_v2_6_pre_release_public_doc_cleanup_audit_test tests.goal3054_v2_6_partner_choice_guidance_test tests.goal3050_partner_choice_docs_test tests.goal3052_partner_choice_pod_refresh_test tests.goal2806_v2_5_internal_readiness_packet_test
```

Expected local result from Codex: `Ran 35 tests ... OK`.

## Required Verdict Vocabulary

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

For release discipline, `accept-with-boundary` is expected unless you find a
blocking defect. This review should not authorize the v2.6 release by itself.
