# Goal 1425 v1.5.1 COLLECT_K_BOUNDED Native Generic ABI Contract

## Verdict

An app-name-free native `COLLECT_K_BOUNDED` ABI contract is defined for the
v1.5.1 Python+RTDL track.

This is a contract only. It does not claim that Embree or OptiX already
implements the ABI, and it does not authorize stable primitive promotion,
public speedup wording, zero-copy wording, whole-app claims, release-tag action,
or a release.

## ABI Shape

Backend-specific symbols:

- `rtdl_embree_collect_k_bounded_i64`
- `rtdl_optix_collect_k_bounded_i64`

Prototype template:

```c
int {symbol}(const int64_t* candidate_rows, size_t candidate_count,
             size_t row_width, int64_t* rows_out, size_t row_capacity,
             size_t* emitted_count_out, uint32_t* overflowed_out,
             char* error_out, size_t error_size)
```

The ABI uses row-major `int64` candidate-id rows, an explicit `row_width`,
an explicit row capacity, canonical bounded output, and fail-closed overflow.
The validator checks all ABI pointer/count/error parameters in the prototype,
including `emitted_count_out`, `overflowed_out`, `error_out`, and `error_size`.

## Required Follow-Up

- add Embree generic `int64` row collector
- add OptiX generic `int64` row collector
- route polygon-pair candidate collection through the generic adapter
- prove existing polygon-pair parity is unchanged

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
