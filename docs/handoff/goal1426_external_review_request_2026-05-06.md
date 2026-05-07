# Goal 1426 External Review Request

Please independently review Goal 1426 for RTDL v1.5.1.

## Scope

Goal 1426 adds source-level, app-name-free native `COLLECT_K_BOUNDED` `int64`
collector symbols for Embree and OptiX:

- `rtdl_embree_collect_k_bounded_i64`
- `rtdl_optix_collect_k_bounded_i64`

The intended semantics are:

- accept row-major `int64` candidate rows
- canonicalize by lexicographic sort and deduplication
- report the complete canonical row count through `emitted_count_out`
- fail closed on insufficient output capacity by setting `overflowed_out = 1`
  before copying any rows
- reject invalid row widths, invalid buffers, and row-buffer size overflow
- remain generic and app-name-free

## Files To Review

- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1424_v1_5_1_collect_k_native_app_generic_audit_test.py`
- `tests/goal1425_v1_5_1_collect_k_native_generic_abi_contract_test.py`
- `tests/goal1426_v1_5_1_collect_k_native_i64_source_test.py`
- `docs/reports/goal1426_v1_5_1_collect_k_native_i64_source_implementation_2026-05-06.md`

## Validation Already Run

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

## Known Boundaries

This is source-level implementation only.

It does not claim:

- built-library symbol validation
- polygon-pair adapter routing through this generic ABI
- Embree/OptiX generic ABI parity tests
- stable primitive promotion
- public speedup wording
- zero-copy wording
- whole-app claims
- release action

Manual direct `g++` build probing was inconclusive because the native C++ source
layout is not currently validated as standalone direct-compile units in simple
per-file invocation order. Built-library validation remains pending.

## Review Questions

Please answer:

1. Does this source-level implementation satisfy the stated generic
   app-name-free i64 collector semantics?
2. Are fail-closed overflow/capacity semantics and invalid-buffer guards
   adequately represented in source and tests?
3. Does the report avoid overclaiming stable promotion, speedup, zero-copy, or
   built-library validation?
4. Are there any blocking issues before committing this as a source-level
   implementation step?
