# Goal 1426 v1.5.1 COLLECT_K_BOUNDED Native I64 Source Implementation

## Verdict

The app-name-free native `COLLECT_K_BOUNDED` `int64` collector symbols now exist
in Embree and OptiX source.

This is source-level implementation only. It does not claim built-library
validation, does not route polygon-pair collection through the generic adapter
yet, and does not authorize stable primitive promotion, public speedup wording,
zero-copy wording, whole-app claims, release-tag action, or a release.

## Implemented Source Symbols

- `rtdl_embree_collect_k_bounded_i64`
- `rtdl_optix_collect_k_bounded_i64`

Both symbols accept row-major `int64` candidate-id rows, canonicalize them by
lexicographic sort plus deduplication, set `emitted_count_out` to the complete
canonical row count, and fail closed by setting `overflowed_out` before copying
any rows when the canonical row count exceeds `row_capacity`.

## Still Pending

- built-library symbol validation on Windows/Linux native builds
- polygon-pair adapter routing through the generic ABI
- Embree/OptiX parity tests against the generic ABI
- renewed 3-AI stable-promotion review

## Validation

Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 37 tests` / `OK`.

Linux:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1423_v1_5_1_collect_k_whole_app_phrase_gate_test tests.goal1422_v1_5_1_collect_k_post_link_gate_alignment_test tests.goal1421_v1_5_1_collect_k_public_doc_link_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test
```

Result: `Ran 37 tests` / `OK`.

Manual direct `g++` native-build probing on Linux was inconclusive because the
current native C++ files are not standalone direct-compile units in simple
per-file `g++` invocation order. This does not satisfy built-library validation;
that remains explicitly pending.
