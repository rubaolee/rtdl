# Goal 1440 External Review Request

Please review the current uncommitted Goal1440 patch.

## Scope

Goal1440 starts v1.5.2 technical work by adding an app-generic collect result-buffer metadata contract. This follows the accepted v1.5.1 architecture consensus that `COLLECT_K_BOUNDED` defines bounded row semantics, while zero-copy/reduced-copy work requires an explicit buffer ownership and metadata contract.

This patch does not implement true zero-copy and does not claim speedup.

## Files To Review

- `src/rtdsl/v1_5_2_collect_buffers.py`
- `src/rtdsl/__init__.py`
- `tests/goal1440_v1_5_2_collect_buffer_contract_test.py`
- `docs/reports/goal1440_v1_5_2_collect_buffer_contract_foundation_2026-05-07.md`

## Validation

Focused Windows collect/v1.5.1 gate slice:

```text
Ran 51 tests in 0.113s
OK
```

Import smoke:

```text
rt.V1_5_2_COLLECT_BUFFER_STATUS == "python_rtdl_buffer_contract_foundation"
collect_k_result_buffer_descriptor(... )["shape"] == (2, 2)
```

`git diff --check` passed with only expected Windows LF-to-CRLF warnings.

## Review Questions

1. Does this correctly define a metadata-only collect result-buffer contract without claiming true zero-copy?
2. Does it preserve the v1.5.1 collect-k claim boundary and avoid stable promotion, speedup wording, whole-app claims, and release action?
3. Are the descriptor validations sufficient for this first v1.5.2 foundation slice?

Please answer with `ACCEPT`, `ACCEPT WITH NOTES`, or `REJECT`, and list precise blockers if rejected.
