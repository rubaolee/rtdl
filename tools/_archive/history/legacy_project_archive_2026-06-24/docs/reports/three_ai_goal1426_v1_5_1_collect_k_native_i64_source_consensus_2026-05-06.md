# 3-AI Consensus: Goal 1426 v1.5.1 COLLECT_K_BOUNDED Native I64 Source Implementation

## Verdict

Codex, Claude, and Gemini agree that Goal 1426 is acceptable as a source-level
implementation step.

The Embree and OptiX source trees now contain app-name-free native
`COLLECT_K_BOUNDED` `int64` collector symbols:

- `rtdl_embree_collect_k_bounded_i64`
- `rtdl_optix_collect_k_bounded_i64`

## Consensus Basis

Codex implemented and validated the source-level symbols and boundary updates.

Claude review:

- `docs/reports/claude_goal1426_v1_5_1_collect_k_native_i64_source_review_2026-05-06.md`
- Verdict: `ACCEPT`
- Blocking issues: none

Gemini review:

- `docs/reports/gemini_goal1426_v1_5_1_collect_k_native_i64_source_review_2026-05-06.md`
- Verdict: `ACCEPT`
- Blocking issues: none

Implementation report:

- `docs/reports/goal1426_v1_5_1_collect_k_native_i64_source_implementation_2026-05-06.md`

External review request:

- `docs/handoff/goal1426_external_review_request_2026-05-06.md`

## Accepted Scope

The accepted source-level behavior is:

- accept row-major `int64` candidate-id rows
- canonicalize rows by lexicographic sort and deduplication
- report the complete canonical row count through `emitted_count_out`
- fail closed on insufficient output capacity by setting `overflowed_out = 1`
  before copying rows
- reject invalid row widths, invalid buffers, and row-buffer size overflow
- keep the native ABI app-name-free

## Still Blocked

This consensus does not authorize stable promotion or public claims beyond the
source-level implementation step.

Still pending:

- built-library symbol validation
- polygon-pair adapter routing through the generic ABI
- Embree/OptiX generic ABI parity tests
- stable primitive promotion review
- speedup, zero-copy, whole-app, release, or broad workload wording

## Validation

Windows focused slice:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 37 tests` / `OK`.

Linux focused slice on `192.168.1.20`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 37 tests` / `OK`.
