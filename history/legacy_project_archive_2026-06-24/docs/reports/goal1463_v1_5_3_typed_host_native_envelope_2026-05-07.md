# Goal1463 v1.5.3 Typed Host Native Envelope

## Verdict

Added a native execution envelope that uses an explicit typed ctypes host input
buffer together with the existing caller-owned prepared host output buffer.
This avoids wrapper-internal candidate-row reflattening for this path, but it
does not claim true zero-copy or speedup.

## Scope

- Function:
  `run_native_collect_k_bounded_with_typed_host_buffers(...)`
- Input:
  `prepare_collect_k_i64_host_input_buffer(...)`
- Output:
  `prepare_collect_k_result_buffer_descriptor(...)` plus caller-owned ctypes
  output storage.
- Backend scope:
  app-name-free native collect symbols such as
  `rtdl_embree_collect_k_bounded_i64` and `rtdl_optix_collect_k_bounded_i64`
  where available.

## Boundary

The envelope still uses host ctypes storage. It is a reduced-copy candidate
path because input and output buffers are explicit and reusable at the Python
wrapper boundary. It does not authorize true zero-copy wording, public speedup
wording, whole-app claims, stable primitive promotion, partner tensor handoff,
or release action.

## Validation

Run:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1463_v1_5_3_typed_host_native_envelope_test
```
