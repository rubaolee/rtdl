# Goal 334: v0.5 Final External Review Round

Date: 2026-04-13
Status: planned

## Why this goal exists

The `v0.5 preview` line has reached the point where the main missing slice is
no longer internal engineering closure. The repo now needs one bounded final
external review round before final release packaging and tagging.

This goal is not:

- open-ended redesign
- historical benchmark reruns
- final release-making itself

This goal is:

- one strict reviewer pass over the current packet
- one explicit judgment of whether any real blockers remain
- one saved review artifact that can be used to decide whether Goal 335
  release-making should start

## Required reviewer inputs

The reviewer should start from the current packet and the current pre-release
session summary:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/audit_and_external_review_packet.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_v0_5_final_pre_release_session_summary_2026-04-13.md`

## Required reviewer questions

The review must answer:

1. Is the current `v0.5 preview` package honestly ready for final release
   packaging?
2. Are there any remaining real blockers at the language/runtime level?
3. Are there any remaining real blockers in the public/reviewer docs?
4. Are the Linux-vs-Windows/macOS and backend maturity boundaries stated
   clearly enough?
5. Is there any remaining overclaim risk that should be corrected before the
   final release statement is written?
6. Can the repo now move from:
   - final external review
   to:
   - final release package and tagging

## Output requirement

The external review must produce:

- a clear verdict
- concrete blockers, if any
- concrete bounded fixes, if any
- or an explicit approval to proceed to the final `v0.5` release package

## Closure standard

Goal 334 is only closed when:

- the external-style review file is saved
- Codex consensus is saved
- any findings are either fixed or explicitly accepted

## Expected next step after closure

If this review is clean, the next goal should be:

- Goal 335: final `v0.5` release package
