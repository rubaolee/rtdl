# Goal2781 Grouped Vector-Sum Adapter Review (2026-05-31)

## Review Questions

1.  **Does `grouped_vector_sum_2d_partner_columns` remain generic and app-agnostic?**
    *   **Answer:** Yes. Analysis of `src/rtdsl/partner_adapters.py` shows generic input/output contracts (`caller_supplied_grouped_vector_rows_2d`, `generic_grouped_vector_sum_f64x2`) and explicit disclaimers in the metadata against app-specific logic or advanced claims. The test `test_generic_adapter_is_exported_without_app_specific_engine_path` explicitly verifies its export without app-specific engine paths, reinforcing its generic and app-agnostic nature.

2.  **Does the Triton branch route through the declared generic operation `grouped_vector_sum_f64x2` without replacing RTDL/OptiX traversal?**
    *   **Answer:** Yes. In `src/rtdsl/partner_adapters.py`, the Triton implementation explicitly routes through `run_triton_partner_continuation` with the operation name `"grouped_vector_sum_f64x2"`. The metadata for this operation includes `"native_engine_row_contract": "not_called_partner_continuation_only"`, confirming that it does not replace RTDL/OptiX traversal. This routing and contract adherence are also verified in `tests/goal2781_grouped_vector_sum_adapter_test.py`.

3.  **Do the Torch/CuPy branches preserve same-contract partner-owned column behavior without implying that Torch is the neutral buffer protocol?**
    *   **Answer:** Yes. `src/rtdsl/partner_adapters.py` shows separate implementations for Torch and CuPy, each utilizing their respective library's tensor operations and data structures. The `_partner_module` function correctly dispatches to the appropriate backend. `src/rtdsl/__init__.py` imports `CuPyAdapter` and `PyTorchAdapter` as distinct, equally supported partners. There is no indication in the code or metadata that Torch is implicitly treated as a neutral buffer protocol; rather, both are treated as specific partner implementations adhering to a common functional contract.

4.  **Is the negative pod performance evidence recorded honestly, especially the finding that current Triton is correct but 4x-17x slower than Torch?**
    *   **Answer:** Yes, the negative pod performance evidence is recorded honestly. The report `docs/reports/goal2781_grouped_vector_sum_adapter_2026-05-31.md` explicitly states, "This is intentionally recorded as negative performance evidence for the current Triton preview kernel." It presents a clear table showing Triton's median execution times are 4.093x to 16.586x slower than Torch for various input sizes, while confirming that correctness passed for all cases. The summary notes that Torch's scatter-add remains the better choice until Triton improves, demonstrating transparency in reporting.

5.  **Are all public speedup, RT-core, true-zero-copy, whole-app, and release claims still blocked?**
    *   **Answer:** Yes. The metadata within `src/rtdsl/partner_adapters.py` consistently sets flags such as `rt_core_speedup_claim_authorized`, `v2_5_release_authorized`, and `whole_app_speedup_claim_authorized` to `False` for `grouped_vector_sum_2d_partner_columns` and related functions. The report `docs/reports/goal2781_grouped_vector_sum_adapter_2026-05-31.md` explicitly lists these as "This goal does not authorize: no public speedup claim; no true zero-copy claim; no RT-core speedup claim; no v2.5 release readiness." This is further confirmed by assertions in `tests/goal2781_grouped_vector_sum_adapter_test.py`.

6.  **Are the tests sufficient for this narrow adapter wiring slice?**
    *   **Answer:** Yes, the tests in `tests/goal2781_grouped_vector_sum_adapter_test.py` are sufficient for this narrow adapter wiring slice. They verify the generic nature and proper export of the adapter, confirm the Triton branch's routing and non-replacement of RTDL/OptiX traversal, ensure functional equivalence between Triton and Torch implementations (same-contract behavior), and validate the explicit blocking of various public claims in the metadata and report. Given the scope of an "adapter wiring slice," these checks provide adequate coverage.

## Expected Verdict

`accept-with-boundary`
