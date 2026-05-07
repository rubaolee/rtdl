# 3-AI Consensus: Goal 1425 v1.5.1 COLLECT_K_BOUNDED Native Generic ABI Contract

## Verdict

ACCEPT.

The v1.5.1 `COLLECT_K_BOUNDED` track now has an accepted app-name-free native
ABI contract for a generic row-major `int64` bounded collector.

This consensus is contract-only. It does not claim that Embree or OptiX already
implements the ABI, and it does not authorize stable primitive promotion,
public speedup wording, zero-copy wording, whole-app claims, release-tag action,
or a release.

## Reviewed Scope

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `src/rtdsl/__init__.py`
- `tests/goal1425_v1_5_1_collect_k_native_generic_abi_contract_test.py`
- `docs/reports/goal1425_v1_5_1_collect_k_native_generic_abi_contract_2026-05-06.md`

## AI Reviews

- Codex: implemented and validated the contract on Windows and Linux.
- Claude: `ACCEPT` in
  `docs/reports/claude_goal1425_v1_5_1_collect_k_native_generic_abi_contract_review_2026-05-06.md`.
- Gemini: `ACCEPT` in
  `docs/reports/gemini_goal1425_v1_5_1_collect_k_native_generic_abi_contract_review_2026-05-06.md`.

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 32 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`90a6ec090f93fda9d50d2517973f12decf13aa18`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 32 tests` / `OK`.

## Boundary

Accepted ABI contract:

- backend symbols: `rtdl_embree_collect_k_bounded_i64`,
  `rtdl_optix_collect_k_bounded_i64`
- generic row-major `int64` candidate-id rows
- explicit `row_width`
- explicit `row_capacity`
- canonical bounded output
- fail-closed overflow

Still blocked:

- native implementation
- stable primitive promotion
- public speedup wording
- zero-copy wording
- whole-app claims
- release-tag action
