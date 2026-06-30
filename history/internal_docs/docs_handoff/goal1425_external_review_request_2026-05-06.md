# Goal 1425 External Review Request

Please review the v1.5.1 `COLLECT_K_BOUNDED` native generic ABI contract patch.

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `src/rtdsl/__init__.py`
- `tests/goal1425_v1_5_1_collect_k_native_generic_abi_contract_test.py`
- `docs/reports/goal1425_v1_5_1_collect_k_native_generic_abi_contract_2026-05-06.md`

## Intended Patch

The patch defines a contract-only app-name-free native ABI for
`COLLECT_K_BOUNDED`:

```c
int {symbol}(const int64_t* candidate_rows, size_t candidate_count,
             size_t row_width, int64_t* rows_out, size_t row_capacity,
             size_t* emitted_count_out, uint32_t* overflowed_out,
             char* error_out, size_t error_size)
```

Backend symbols:

- `rtdl_embree_collect_k_bounded_i64`
- `rtdl_optix_collect_k_bounded_i64`

The patch must preserve this boundary:

- contract only; native implementation is still pending
- documented experimental public-candidate only
- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release-tag action or release

## Validation To Check

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 32 tests` / `OK`.

Linux `192.168.1.20`, checkout `/home/lestat/work/rtdl_v1_5_linux_check`,
same patch applied over `origin/main` at
`90a6ec090f93fda9d50d2517973f12decf13aa18`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Recorded result: `Ran 32 tests` / `OK`.

## Requested Verdict

Return one of:

- `ACCEPT`
- `ACCEPT WITH NOTES`
- `BLOCK`

If blocking, identify the exact blocker only. Do not speculate.
