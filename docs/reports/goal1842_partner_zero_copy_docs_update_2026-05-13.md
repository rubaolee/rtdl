# Goal1842 Partner Zero-Copy Docs Update

Date: 2026-05-13
Status: `accept-with-boundary`

## Summary

Goal1842 updates the user-facing v2.0 preview documentation after Goal1838.

The docs now explain two separate partner paths:

- the conservative host-stage `Python Partner Any-Hit` path for Embree/OptiX;
- the advanced OptiX Torch/CuPy CUDA input-plus-output zero-copy preview slice
  for the prepared 2-D ray/triangle any-hit primitive.

## Files Updated

- `README.md`
- `docs/README.md`
- `docs/app_example_quickstart.md`
- `docs/tutorials/README.md`
- `docs/tutorials/partner_optix_zero_copy_anyhit.md`
- `tests/goal1842_partner_zero_copy_docs_update_test.py`

## Boundary

The new tutorial does not claim v2.0 release readiness. It explicitly blocks:

- broad RT-core speedup;
- whole-app acceleration;
- arbitrary PyTorch/CuPy acceleration;
- package-install support;
- no-native-state claims for OptiX.

The allowed teaching claim remains narrow:

```text
OptiX prepared 2-D ray/triangle any-hit can read Torch/CuPy CUDA input columns
and write Torch/CuPy CUDA output flags without RTDL-owned input or output
staging buffers.
```

## Validation

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1842_partner_zero_copy_docs_update_test \
  tests.goal1802_partner_anyhit_docs_example_test \
  tests.goal1838_optix_partner_owned_output_flags_zero_copy_test \
  tests.goal1836_optix_cupy_whole_primitive_input_zero_copy_conformance_test
```

Expected result: pass.

## External Review Status

Gemini's Goal1841 review of the v2.0 progress packet landed at:

- `docs/reviews/goal1841_gemini_review_v2_0_progress_so_far_2026-05-13.md`

Gemini's verdicts:

- Goal1836: `accept-with-boundary`
- Goal1838: `accept-with-boundary`
- v2.0 release readiness: `needs-more-evidence`
