# Call For Review: Phoenix V3 M29 Barnes-Hut V2.14 / Current Surface Classification

Date: 2026-06-23

Please critically review this M29 report:

`docs/reports/phoenix_v3_m29_barnes_hut_v2_14_current_surface_classification_2026-06-23.md`

Evidence:

`docs/rebuild/v3/evidence/phoenix_v3_m29_barnes_hut_surface_Cv7ppr/`

Classifier:

`scripts/v3_phoenix_m29_barnes_hut_surface_classification.py`

M28 consensus:

`docs/reviews/codex_claude_phoenix_v3_m28_set_a_trunk_family_freeze_2ai_consensus_2026-06-23.md`

## Requested Verdict Labels

Use exactly one:

- `approve_m29_classification`
- `approve_with_amendments`
- `blocked_needs_more_evidence`
- `reject_overclaim`

## Questions

1. Is the classification `v2_14_has_cpu_fused_or_typed_stream_only` supported by
   the evidence?
2. Is it correct not to run additional timing rows after this classification?
3. Does the report avoid falsely claiming same-contract V3-over-v2.14 speedup?
4. Is the dirty v2.14 working tree handled adequately by the relevant-file
   clean check?
5. Does M29 properly carry forward the M28 amendments about
   `runtime_sourced_material_gain`, skipped validation, "generic" scope, and
   `git_commit: null` provenance?
6. Does this result support moving to M30 for the second Set-A family, while
   keeping all-app forbidden?

## Required Output

Save your review to:

`docs/reviews/claude_phoenix_v3_m29_barnes_hut_surface_classification_review_2026-06-23.raw.md`

Include:

- one verdict label;
- blocking findings, if any;
- required amendments, if any;
- explicit answers to the six questions;
- a non-authorization block stating that your review authorizes no release, no
  all-app run, no public speedup claim, no broad V3-over-V2 claim, no RT-core
  speedup claim, no true-zero-copy claim, and no V4 work.
