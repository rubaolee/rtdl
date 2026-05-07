# 3-AI Consensus: Goal 1422 v1.5.1 COLLECT_K_BOUNDED Post-Link Gate Alignment

## Verdict

ACCEPT.

The v1.5.1 `COLLECT_K_BOUNDED` gate and candidate package may record the
Goal1421 public-doc-link acceptance as a discoverability-only state.

This consensus does not authorize stable primitive promotion, public speedup
wording, zero-copy wording, whole-app claims, release-tag action, or a release.

## Reviewed Scope

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1420_v1_5_1_collect_k_release_surface_gate_test.py`
- `tests/goal1422_v1_5_1_collect_k_post_link_gate_alignment_test.py`
- `docs/release_reports/v1_5_1/README.md`
- `docs/release_reports/v1_5_1/collect_k_bounded.md`
- `docs/release_reports/v1_5_1/release_surface_gate.md`
- `docs/reports/goal1422_v1_5_1_collect_k_post_link_gate_alignment_2026-05-06.md`

## AI Reviews

- Codex: implemented and validated the patch on Windows and Linux.
- Claude: `ACCEPT` in
  `docs/reports/claude_goal1422_v1_5_1_collect_k_post_link_gate_alignment_review_2026-05-06.md`.
- Gemini: `ACCEPT` in
  `docs/reports/gemini_goal1422_v1_5_1_collect_k_post_link_gate_alignment_review_2026-05-06.md`.

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 21 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`d3fc7f636e6c9f7249adb60f8cd89a4ae5cea7a5`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 21 tests` / `OK`.

## Boundary

The accepted state is limited to post-link metadata/doc alignment:

- documented experimental public-candidate only
- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release-tag action
