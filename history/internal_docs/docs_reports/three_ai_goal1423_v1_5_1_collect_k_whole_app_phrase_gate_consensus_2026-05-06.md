# 3-AI Consensus: Goal 1423 v1.5.1 COLLECT_K_BOUNDED Whole-App Phrase Gate

## Verdict

ACCEPT.

The v1.5.1 `COLLECT_K_BOUNDED` release gate may mechanically require
`no whole-app claims` as part of its candidate-document phrase scan.

This consensus does not authorize stable primitive promotion, public speedup
wording, zero-copy wording, whole-app claims, release-tag action, or a release.

## Reviewed Scope

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1420_v1_5_1_collect_k_release_surface_gate_test.py`
- `tests/goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test.py`
- `docs/reports/goal1423_v1_5_1_collect_k_whole_app_phrase_gate_2026-05-06.md`

## AI Reviews

- Codex: implemented and validated the patch on Windows and Linux.
- Claude: `ACCEPT` in
  `docs/reports/claude_goal1423_v1_5_1_collect_k_whole_app_phrase_gate_review_2026-05-06.md`.
- Gemini: `ACCEPT` in
  `docs/reports/gemini_goal1423_v1_5_1_collect_k_whole_app_phrase_gate_review_2026-05-06.md`.

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 23 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`d693bd6a089c5c6fa2b4ea2be95adcb472803f31`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 23 tests` / `OK`.

## Boundary

This is restrictive gate hardening only:

- documented experimental public-candidate only
- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release-tag action
