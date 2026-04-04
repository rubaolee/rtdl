# Goal 52 RTDL-New Intake

## Objective

Review the external `rtdl-new` patchset in `/Users/rl2025/claude-work/rtdl-new`, decide what should be kept, and merge only the accepted code into the main repository after multi-AI review and consensus.

## Intake Scope

External source under review:

- `/Users/rl2025/claude-work/rtdl-new`

Primary changed code surface:

- `src/rtdsl/api.py`
- `src/rtdsl/__init__.py`
- `tests/_embree_support.py`
- `tests/test_core_quality.py`
- `scripts/run_full_verification.py`

Review docs provided with that work:

- `docs/test_quality_report.md`
- `docs/gemini_report_review.md`
- `docs/cross_review_response_to_gemini_final.md`
- `docs/consensus_rounds/round_1_gemini.md`
- `docs/consensus_rounds/round_2_claude.md`
- `docs/consensus_rounds/round_2_gemini.md`
- `docs/consensus_rounds/round_3_claude.md`
- `docs/consensus_rounds/round_3_gemini.md`
- `docs/consensus_rounds/CONSENSUS_FINAL.md`

## Initial Codex Judgment

This goal is worth doing, but only as a selective intake.

- worth keeping:
  - `contains()` alias
  - `_embree_support.py` loader fix
  - `tests/test_core_quality.py`
- not yet trustworthy as authoritative:
  - the external consensus docs, because they overstate the verified baseline and contain at least one now-stale claim about `scripts/run_full_verification.py`

## Plan

1. Write a code-intake and doc-trustworthiness report for the external patchset.
2. Send that report and this goal plan to Claude and Gemini for review.
3. Seek consensus on:
   - which code to keep
   - which docs to revise or discard
   - what must be fixed before merge
4. If consensus supports intake:
   - merge the accepted code into the main repo
   - add one direct test for `rt.contains(...)`
   - do not import stale external consensus docs as authoritative project records
5. Run tests in the main repo.
6. Write the final Goal 52 result report and consensus note.

## Acceptance Rule

- no publish until at least 2-AI consensus
- if the external docs remain inconsistent with the actual code and tests, merge may proceed for the code only, with the docs explicitly rejected or downgraded
