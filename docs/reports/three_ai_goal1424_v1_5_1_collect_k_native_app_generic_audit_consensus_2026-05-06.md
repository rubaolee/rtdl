# 3-AI Consensus: Goal 1424 v1.5.1 COLLECT_K_BOUNDED Native App-Generic Audit

## Verdict

ACCEPT.

`COLLECT_K_BOUNDED` is app-generic at the contract, Python reference, and
result-validator layers, but stable primitive promotion remains blocked because
the current native Embree and OptiX collection entrypoints are still
polygon-pair-specific.

This consensus does not authorize stable primitive promotion, public speedup
wording, zero-copy wording, whole-app claims, release-tag action, or a release.

## Reviewed Scope

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `src/rtdsl/__init__.py`
- `tests/goal1424_v1_5_1_collect_k_native_app_generic_audit_test.py`
- `docs/reports/goal1424_v1_5_1_collect_k_native_app_generic_audit_2026-05-06.md`

## AI Reviews

- Codex: implemented and validated the audit on Windows and Linux.
- Claude: `ACCEPT` in
  `docs/reports/claude_goal1424_v1_5_1_collect_k_native_app_generic_audit_review_2026-05-06.md`.
- Gemini: `ACCEPT` in
  `docs/reports/gemini_goal1424_v1_5_1_collect_k_native_app_generic_audit_review_2026-05-06.md`.

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 27 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`f72ecd79fc3b7624f562b4cdd01c611825214375`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 27 tests` / `OK`.

## Boundary

The accepted state is:

- contract/Python/result-validator layers are app-generic
- current native Embree and OptiX collection symbols are polygon-pair-specific
- stable primitive promotion remains blocked
- an app-name-free native `COLLECT_K_BOUNDED` ABI is required before stable
  promotion review
