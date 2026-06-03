# Goal3142: Numba Preview Kernel Cache Extension

Date: 2026-06-03

Status: implemented and pod-smoked

## Purpose

Goal3139 cached the Numba CUDA dispatchers used by grouped argmin/argmax and
removed the large repeated-dispatcher construction cost measured in Goal3136.
Goal3141's Claude review accepted that fix and noted one remaining opportunity:
segmented count and segmented sum still called their kernel factories directly.

Goal3142 extends the same app-agnostic cache helper to the rest of the Numba
preview kernels in `numba_partner_continuation.py`.

## Code Change

Changed:

- `src/rtdsl/numba_partner_continuation.py`

Newly cached call sites:

- segmented count
- segmented sum
- segmented min/max via `_run_numba_segmented_extreme_f64`
- compact mask count/scatter
- mask-index iota
- pairwise L2 score-row generation
- pairwise block-nearest row generation
- global argmax block reductions

The earlier Goal3139 grouped-arg cache remains unchanged.

## Validation

Local:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3139_numba_kernel_cache_contract_test tests.goal3006_numba_grouped_argmin_argmax_preview_test tests.goal2995_raydb_numba_segmented_minmax_test tests.goal3008_numba_group_argmin_global_argmax_front_door_test tests.goal3017_numba_grouped_witness_no_host_sync_fast_path_test
Ran 18 tests in 0.069s
OK (skipped=4)
```

Compile:

```text
py -3 -m py_compile src\rtdsl\numba_partner_continuation.py
OK
```

Pod:

```text
python -m unittest tests.goal3139_numba_kernel_cache_contract_test tests.goal3006_numba_grouped_argmin_argmax_preview_test tests.goal2995_raydb_numba_segmented_minmax_test tests.goal3008_numba_group_argmin_global_argmax_front_door_test tests.goal3017_numba_grouped_witness_no_host_sync_fast_path_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test
Ran 34 tests in 1.034s
OK
```

Pod environment:

- host: `4463b4adb79b`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- repo path: `/root/rtdl_v28_goal3132`
- validated commit: `7b175942`

## Interpretation

Goal3142 is a general runtime hygiene improvement for Numba preview kernels. It
does not add app-specific logic, change partner-selection policy, or alter
public operation semantics. It simply prevents repeated construction of the same
CUDA dispatcher when a caller repeatedly invokes a supported Numba continuation.

## Claim Boundary

Goal3142 authorizes no release, public speedup wording, broad RT-core wording,
true-zero-copy wording, hidden dispatch, automatic partner selection,
app-specific native-engine behavior, or user-defined shader injection.
