# Goal683 Consensus: v0.9.6 Candidate Final Local Gate

Status: ACCEPT

Date: 2026-04-21

## Scope

Goal683 records the final local release-candidate gate after the `v0.9.6`
candidate package was added, linked, and updated with the final full-suite
count.

Primary report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal683_v0_9_6_candidate_final_local_gate_2026-04-21.md`

External reviews:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal683_external_review_claude_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal683_external_review_gemini_flash_2026-04-21.md`

## Consensus

Codex, Claude, and Gemini Flash all accept Goal683.

Agreed verification:

- Full local suite: `1271` tests OK, `187` skips.
- Candidate package regression: `3` tests OK.
- Public command truth audit: valid, `250` commands across `14` docs.
- Public entry smoke: valid.
- `git diff --check`: clean.

Agreed boundaries:

- Current public release remains `v0.9.5`.
- `v0.9.6` remains a release candidate only and is not tagged.
- Tag/push commands remain held until explicit maintainer authorization.
- No broad DB, graph, full-row, one-shot, GTX 1070 RT-core, AMD GPU, or Apple
  RT full-row speedup claim is made.

## Tooling Note

Gemini Flash returned `ACCEPT`; its transcript also contains non-blocking CLI
stderr for keychain fallback and one transient model-capacity retry.

## Verdict

Goal683 is accepted. The `v0.9.6` release candidate is ready for maintainer
authorization, but no release tag has been created.
