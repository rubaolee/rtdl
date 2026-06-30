# 3-AI Consensus: Goal 1421 v1.5.1 COLLECT_K_BOUNDED Public Doc Link

## Verdict

ACCEPT.

The v1.5.1 `COLLECT_K_BOUNDED` candidate docs may be linked from the public
documentation spine as a documented experimental public-candidate surface only.
This consensus does not authorize stable primitive promotion, public speedup
wording, zero-copy wording, whole-app claims, release-tag action, or a release.

## Reviewed Scope

- `README.md`
- `docs/README.md`
- `docs/public_documentation_map.md`
- `tests/goal1421_v1_5_1_collect_k_public_doc_link_test.py`
- `docs/reports/goal1421_v1_5_1_collect_k_public_doc_link_patch_2026-05-06.md`

## AI Reviews

- Codex: implemented and validated the patch on Windows and Linux.
- Claude: `ACCEPT` in
  `docs/reports/claude_goal1421_v1_5_1_collect_k_public_doc_link_review_2026-05-06.md`.
- Gemini: `ACCEPT` in
  `docs/reports/gemini_goal1421_v1_5_1_collect_k_public_doc_link_review_2026-05-06.md`.

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 18 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`ff0161489edf4b52be69a3c057f4ecbb7fbb9982`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 18 tests` / `OK`.

## Boundary

Accepted public wording is limited to discoverability for the candidate package.
The linked surface remains:

- documented experimental public-candidate only
- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release-tag action
