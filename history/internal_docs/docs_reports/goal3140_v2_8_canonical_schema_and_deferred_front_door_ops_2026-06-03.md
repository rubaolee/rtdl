# Goal3140: v2.8 Canonical Schema and Deferred Front-Door Ops

Date: 2026-06-03

Status: Claude low-debt closure implemented and pod-smoked

## Purpose

Goal3138 accepted Goals3132, 3136, and 3137 with boundaries, then left three
low debts:

- post-Goal3137 canonical ranked-summary schemas needed real pod evidence;
- `compact_mask_i64` needed an explicit v2.8 front-door deferral rationale;
- `segmented_min_f64` and `segmented_max_f64` needed either smoke evidence or
  an explicit deferral rationale.

Goal3140 closes those debts without expanding the partner-front-door surface.

## Code Change

Changed:

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/v2_8_typed_result_stream.py`
- `src/rtdsl/__init__.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `scripts/goal3140_v2_8_canonical_schema_pod_smoke.py`

New metadata:

- `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_DEFERRED_OPERATIONS`
- `unsupported_operation_reason` in dry-run partner requests
- one-based `grouped_topk_f64` rank convention in typed-stream semantics

## Deferred Operations

| Operation | v2.8 Front-Door State | Rationale |
| --- | --- | --- |
| `compact_mask_i64` | deferred | reference-only in v2.8 because it is order-preserving mask compaction, not a grouped partner-consumer operation |
| `segmented_min_f64` | deferred | lower-level partner operation exists, but v2.8 front-door support waits for explicit partner-consumer smoke evidence |
| `segmented_max_f64` | deferred | lower-level partner operation exists, but v2.8 front-door support waits for explicit partner-consumer smoke evidence |

## Local Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3139_numba_kernel_cache_contract_test
Ran 25 tests in 0.015s
OK
```

Compile:

```text
py -3 -m py_compile src\rtdsl\v2_8_segmented_typed_stream_adapter.py src\rtdsl\__init__.py src\rtdsl\v2_8_typed_result_stream.py scripts\goal3140_v2_8_canonical_schema_pod_smoke.py
OK
```

## Pod Canonical-Schema Smoke

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
- repo path: `/root/rtdl_v28_goal3132`
- measured commit: `a44de908fae81f7fc83c6809f4f152c1f6aa70d9`

Artifact:

`docs/reports/goal3140_pod_artifacts/v2_8_canonical_schema_pod_smoke_2026-06-03.json`

Pod cases:

| Case | Partner | Canonical Keys | Status |
| --- | --- | --- | --- |
| `grouped_argmin_f64_numba` | Numba | `group_ids`, `item_ids`, `scores`, `missing_group_ids` | passed |
| `grouped_argmax_f64_numba` | Numba | `group_ids`, `item_ids`, `scores`, `missing_group_ids` | passed |
| `grouped_topk_f64_torch` | Torch | `group_ids`, `item_ids`, `scores`, `ranks`, `row_offsets`, `missing_group_ids` | passed |

The top-k smoke also confirmed the one-based rank convention:

```text
ranks: [1, 1]
```

## Claim Boundary

Goal3140 authorizes no release, public speedup wording, broad RT-core wording,
true-zero-copy wording, hidden dispatch, automatic partner selection,
app-specific native-engine behavior, or user-defined shader injection.
