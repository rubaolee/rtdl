# Goal1462 v1.5.3 Typed Host Input Buffer

## Verdict

Added an explicit typed contiguous host input-buffer path for
`COLLECT_K_BOUNDED` candidate rows. This makes Python-to-native input storage
visible to RTDL metadata and tests, but it is not a true zero-copy path and not
a speedup claim.

## Scope

- Function: `prepare_collect_k_i64_host_input_buffer(...)`
- Validator: `validate_collect_k_i64_host_input_buffer(...)`
- Layout: row-major dense candidate-id rows
- Dtype: int64
- Device: CPU host memory
- Copy boundary: `typed_contiguous_host_buffer`

## Boundary

The path still copies user rows into ctypes host storage. It does not authorize
true zero-copy wording, public speedup wording, whole-app claims, stable
primitive promotion, partner tensor handoff, or release action.

## Validation

Run:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1462_v1_5_3_typed_host_input_buffer_test
```
