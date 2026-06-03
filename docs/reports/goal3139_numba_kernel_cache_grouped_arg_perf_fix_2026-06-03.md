# Goal3139: Numba Kernel Cache Grouped-Arg Performance Fix

Date: 2026-06-03

Status: implemented, pod-measured, not a release claim

## Purpose

Goal3136 localized the v2.8 Numba grouped-arg slowdown to the current Numba
partner implementation rather than the v2.8 front-door wrapper. The suspicious
symptom was a nearly constant 0.135-0.20 second floor even as row count changed.

Goal3139 addresses the likely cause: grouped-arg execution rebuilt Numba CUDA
dispatchers by calling kernel factory functions on each run. A tiny generic
kernel cache now reuses CUDA dispatcher objects by CUDA module identity and
factory name.

## Code Change

Changed:

- `src/rtdsl/numba_partner_continuation.py`
- `tests/goal3139_numba_kernel_cache_contract_test.py`
- `scripts/goal3139_numba_kernel_cache_pod_probe.py`

The cache is app-agnostic. It does not alter grouped-arg semantics, partner
choice, native engine behavior, validation policy, or output schema.

## Local Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3139_numba_kernel_cache_contract_test tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal3006_numba_grouped_argmin_argmax_preview_test
Ran 30 tests in 0.017s
OK (skipped=1)
```

Compile:

```text
py -3 -m py_compile src\rtdsl\numba_partner_continuation.py tests\goal3139_numba_kernel_cache_contract_test.py scripts\goal3139_numba_kernel_cache_pod_probe.py
OK
```

## Pod

User supplied:

```text
ssh root@157.157.221.29 -p 24317 -i ~/.ssh/id_ed25519
```

The working key was:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\id_ed25519_rtdl_codex
```

Environment:

- host: `4463b4adb79b`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- driver: `580.65.06`
- repo path: `/root/rtdl_v28_goal3132`
- measured commit: `a83cd178259c53467118c9c641958af0a9fc82c2`

Artifact:

`docs/reports/goal3139_pod_artifacts/numba_kernel_cache_timing_2026-06-03.json`

## Timing Result

Median steady-state seconds over five repetitions:

| Rows | Operation | Layer | Default Compact | No-Validate Dense |
| ---: | --- | --- | ---: | ---: |
| 65,536 | `grouped_argmin_f64` | direct | 0.001808 | 0.001063 |
| 65,536 | `grouped_argmin_f64` | front door | 0.001929 | 0.001187 |
| 65,536 | `grouped_argmax_f64` | direct | 0.001760 | 0.000972 |
| 65,536 | `grouped_argmax_f64` | front door | 0.001975 | 0.001183 |
| 262,144 | `grouped_argmin_f64` | direct | 0.002040 | 0.000984 |
| 262,144 | `grouped_argmin_f64` | front door | 0.002232 | 0.001155 |
| 262,144 | `grouped_argmax_f64` | direct | 0.002000 | 0.000973 |
| 262,144 | `grouped_argmax_f64` | front door | 0.002231 | 0.001145 |
| 1,048,576 | `grouped_argmin_f64` | direct | 0.003123 | 0.001027 |
| 1,048,576 | `grouped_argmin_f64` | front door | 0.003377 | 0.001210 |
| 1,048,576 | `grouped_argmax_f64` | direct | 0.003110 | 0.001014 |
| 1,048,576 | `grouped_argmax_f64` | front door | 0.003418 | 0.001185 |

Compared with Goal3136 front-door default-compact medians, the same path moved
from about `0.190-0.202s` to about `0.0019-0.0034s` across the measured sizes.
This is internal same-path diagnostic evidence, not public speedup wording.

## Interpretation

The Numba grouped-arg slowdown was primarily repeated dispatcher construction,
not the v2.8 front-door contract itself. After caching, the front-door overhead
is small relative to the direct Numba call.

Remaining boundaries:

- First-use warm time is still visible when a new kernel specialization is first
  compiled.
- Numba still warns about low occupancy for the small grid sizes in this probe.
- No release, whole-app, RT-core, zero-copy, or broad partner-performance claim
  is authorized by this report.

## Claim Boundary

Goal3139 authorizes no release, public speedup wording, broad RT-core wording,
true-zero-copy wording, hidden dispatch, automatic partner selection,
app-specific native-engine behavior, or user-defined shader injection.
