# Goal 1444 v1.5.2 Native Prepared Collect Execution Envelope

## Verdict

ACCEPTED as a narrow v1.5.2 Python+RTDL native-symbol execution envelope.

This is not native prepared-buffer reuse, not native pointer handoff, not true zero-copy, not a public speedup claim, not a whole-app speedup claim, not stable `COLLECT_K_BOUNDED` promotion, and not a release action.

## Implemented

- Added `run_native_collect_k_bounded_rows_with_prepared_result_buffer(...)`.
- The helper validates a `prepared_result` descriptor before native-symbol execution.
- The helper resolves and checks the backend from the prepared descriptor or explicit argument.
- The helper runs the existing app-name-free native generic i64 collector path through `collect_native_i64_rows_with_backend_symbol(...)`.
- The helper uses the prepared descriptor capacity and row width.
- The helper binds completion through `complete_prepared_collect_k_result_buffer_descriptor(...)`.
- The helper returns an envelope containing the native collect result and validated result-buffer metadata.
- The envelope explicitly declares `execution_mode="native_generic_symbol_prepared_descriptor_envelope"`.
- Exported the helper through `rtdsl`.
- Added `tests/goal1444_v1_5_2_native_prepared_collect_execution_envelope_test.py`.

## Validation

Windows focused command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1444_v1_5_2_native_prepared_collect_execution_envelope_test tests.goal1443_v1_5_2_prepared_collect_execution_envelope_test tests.goal1442_v1_5_2_prepared_collect_completion_test tests.goal1441_v1_5_2_prepared_collect_buffer_descriptor_test tests.goal1440_v1_5_2_collect_buffer_contract_test
```

Result:

```text
Ran 25 tests in 0.007s
OK
```

## Boundary

This helper gives native generic collector calls the same prepared-descriptor envelope as the Python reference path. That is useful because backend execution can now be represented as: prepared metadata, native generic symbol call, completion bind, and validated result-buffer descriptor.

The current implementation still marshals input and output through the existing Python ctypes wrapper inside `collect_native_i64_rows_with_backend_symbol(...)`. It does not pass a prepared host or device buffer pointer into native code, does not prove buffer reuse, does not prove GPU-resident output, and does not authorize zero-copy or performance wording.
