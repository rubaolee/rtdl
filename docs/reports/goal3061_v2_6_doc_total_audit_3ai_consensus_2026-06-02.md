# Goal3061 v2.6 Documentation Total Audit 3-AI Consensus

Date: 2026-06-02

Status: 3-AI consensus for the Goal3058 v2.6 release-candidate documentation
total audit. This consensus accepts the documentation cleanup with release-gate
boundaries; it does not push the v2.6 release button.

## Inputs

| AI | Artifact | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal3058_v2_6_release_candidate_doc_total_audit_2026-06-02.md` | `accept-with-boundary` |
| Claude | `docs/reviews/goal3059_claude_review_goal3058_v2_6_doc_total_audit_2026-06-02.md` | `accept-with-boundary` |
| Gemini | `docs/reviews/goal3060_gemini_review_goal3058_v2_6_doc_total_audit_2026-06-02.md` | `accept-with-boundary` |

## Consensus Verdict

`accept-with-boundary`

The three-AI consensus accepts the v2.6 documentation cleanup as a coherent
release-candidate doc surface:

- current learner/user/current-research docs present one v2.6
  release-candidate story;
- old v0/v1/v2.5 research/proposal/transition material has been moved into
  `docs/research/archive/`;
- live docs no longer route learners through old technical app notes, old
  release packages, stale Triton-first wording, or legacy backend proof apps;
- the per-file audit covers 86 current-facing files and the archived research
  files with status, old problem, action, and explanation;
- current-plus-research-archive local Markdown links were checked with
  `103 checked / 0 broken`;
- local portable tutorial/example smoke passed with `ALL_PORTABLE_SMOKE_OK`;
- focused doc/partner tests pass locally.

## External Review Agreement

Claude found no blocking issues and explicitly verified:

- 86 current-facing audit entries;
- 16 moved research files plus the new archive index;
- live research navigation points to the archive instead of old live dirs;
- the v2.3 reference in the front page is previous-release archive context;
- release remains blocked until native tutorial/example validation and final
  release consensus.

Gemini found no blocking issues and explicitly accepted:

- the coherent v2.6 release-candidate surface;
- the archive separation for older research/proposal/transition material;
- the file-by-file audit table;
- the no-overclaim/no-stale-link cleanup;
- the remaining release boundaries.

## Boundaries

This consensus does not authorize:

- tagging or publishing v2.6;
- package-install claims;
- broad RT-core or whole-app speedup claims;
- automatic partner-selection claims;
- general zero-copy/device-residency claims;
- treating archived research/proposal/history files as current user guidance.

## Remaining Release Gates

Before a final v2.6 release decision:

1. Run native tutorial and example commands on a configured Linux/pod surface,
   including Embree and OptiX where available.
2. Keep current docs synchronized with any final runnable-validation findings.
3. Produce the final v2.6 release consensus record after the runnable gate and
   any remaining release checks pass.

## Validation

Local focused gate:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3058_v2_6_release_candidate_doc_total_audit_test tests.goal3056_v2_6_pre_release_public_doc_cleanup_audit_test
```

Result: `Ran 8 tests ... OK`.

Local broader docs/partner slice:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3058_v2_6_release_candidate_doc_total_audit_test tests.goal3056_v2_6_pre_release_public_doc_cleanup_audit_test tests.goal3054_v2_6_partner_choice_guidance_test tests.goal3050_partner_choice_docs_test tests.goal3052_partner_choice_pod_refresh_test tests.goal2806_v2_5_internal_readiness_packet_test
```

Result: `Ran 26 tests ... OK`.
