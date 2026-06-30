# Gemini Review of Goal2704 Native Hit-Stream Output ABI Contract

**Verdict: accept**

Date: 2026-05-30
Reviewer: Gemini Agent

## Review Questions & Answers

1.  **Does Goal2704 define a generic native CUDA hit-stream column ABI without app or benchmark-specific vocabulary?**
    *   **Answer:** Yes. The `GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_FIELDS` and `GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_SYMBOLS` defined in `src/rtdsl/hit_stream_handoff.py` utilize generic types (`uint64`, `int32`, `float64`) and generic column names (`ray_ids_device_ptr`, `primitive_ids_device_ptr`, `row_count`, etc.). The `describe_v2_5_native_hit_stream_output_abi` function explicitly sets `native_engine_app_specific_vocab_allowed` to `False`. The provided test `test_native_output_abi_is_generic_and_claim_bounded` also verifies the absence of app/benchmark-specific vocabulary.

2.  **Does `prepare_native_device_hit_stream_columns_from_abi(...)` correctly keep native raw CUDA pointers in an experimental, claim-bounded state?**
    *   **Answer:** Yes. The `RtdlNativeDeviceHitStreamOutput` class, used by `prepare_native_device_hit_stream_columns_from_abi`, explicitly sets `true_zero_copy_authorized: False` and `public_speedup_claim_authorized: False` in its `to_metadata` method. It also includes a `claim_boundary` message indicating that "true zero-copy or performance claims" are not authorized without further "pod evidence". The `ownership_lifetime_model` is set to `"native_owner_state_machine_required_before_promotion"`, reinforcing its experimental and unproven status.

3.  **Does the metadata preserve the boundaries that true zero-copy, public speedup, and native promotion remain unauthorized until pod evidence proves same-pointer/no-host-stage behavior and native cleanup?**
    *   **Answer:** Yes. Across `RtdlNativeDeviceHitStreamOutput.to_metadata()`, `RtdlHitStreamColumnHandoff.to_metadata()`, and `describe_v2_5_native_hit_stream_output_abi()`, the flags `true_zero_copy_authorized` and `public_speedup_claim_authorized` are consistently set to `False`. Furthermore, clear `claim_boundary` messages are present, explicitly stating the prerequisites for any such claims, including "pod evidence proving same-pointer/no-host-stage behavior and lifetime cleanup." The conditional `native_device_column_output_proven_on_hardware` flag acknowledges proof of output but does not equate it to true zero-copy authorization.

4.  **Does `optix_runtime.py` merely name the future symbol without pretending the native implementation exists?**
    *   **Answer:** Yes. `src/rtdsl/optix_runtime.py` defines `OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_DEVICE_COLUMNS_SYMBOL` as a string constant. There is no Python-side implementation or binding that actively calls or emulates this native symbol. The test `test_optix_runtime_names_the_future_symbol_but_does_not_bind_it_yet` explicitly confirms this behavior, and the `docs/reports/goal2704_native_hit_stream_output_abi_contract_2026-05-30.md` report also confirms this.

5.  **Are there any risks before Goal2705 starts native C++/OptiX work?**
    *   **Answer:** The primary risk is the potential for misinterpretation or over-claiming of the current state, as Goal2704 strictly defines a contract and does not provide native implementation or performance evidence. However, this risk is well-mitigated by the thorough and explicit boundaries set within the code and documentation, which consistently forbid claims of true zero-copy or public speedup until "pod evidence" and native cleanup are established. The Python-side validation within `prepare_native_device_hit_stream_columns_from_abi` and `RtdlRawCudaColumn` also helps reduce risks associated with potentially malformed native inputs. The project is transparent about the "Current Native Blocker" and the scope of "Next Work" in the report, which is critical for managing expectations.

## Summary

Goal2704 successfully defines a generic native CUDA hit-stream column ABI contract. It meticulously maintains clear boundaries, explicitly forbidding premature claims of true zero-copy or public speedup, and requiring robust native implementation and pod evidence for promotion. The Python `optix_runtime.py` correctly names the future symbol as a placeholder without any active binding or emulation. The risks are well-managed through explicit contractual terms and validation. This goal effectively sets the stage for Goal2705's native C++/OptiX work while preventing unwarranted assumptions or claims about the current state.
