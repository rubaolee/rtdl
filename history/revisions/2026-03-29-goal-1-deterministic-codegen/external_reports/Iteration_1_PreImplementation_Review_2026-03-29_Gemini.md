# Pre-Implementation Review Report: Goal 1 - Deterministic Codegen

**Date:** 2026-03-29
**Reviewer:** Gemini-CLI

## 1. Scope Assessment

The objective of Goal 1 is to make backend planning and code generation deterministic, explicit, and testable. The scope outlined in `Goal_1_Spec_2026-03-29_Codex.md` focuses on:

1.  **Stronger backend plan contract:** `plan.json` should have stable, explicit fields.
2.  **Deterministic generated artifacts:** Code and metadata should be stable for the same input.
3.  **Golden tests:** Snapshot-style expectations for generated artifacts.
4.  **Stronger negative validation:** Invalid kernels should fail early with clear messages.

The "Non-Goals" section clearly delineates what is *not* part of this phase, preventing scope creep (e.g., no real OptiX runtime execution, no broad workload expansion).

**Conclusion:** The scope is well-defined and appropriately limited for a pre-GPU stage, focusing on the compiler's intermediate representation and code generation stability. It aligns with the idea of strengthening RTDL as a compiler artifact.

## 2. Missing Requirements

The specification is comprehensive, but a few details could be enhanced for clarity and robustness:

*   **Explicit JSON Schema for `plan.json`:** While the spec mentions a "stronger backend plan contract," it doesn't explicitly state the need for a formal schema (e.g., JSON Schema) for `plan.json`. This would provide explicit, machine-readable validation for plan consumers and tests, ensuring the contract is indeed "stable" and "explicit." Without a formal schema, relying solely on human review or brittle code-based checks might allow the contract to subtly diverge over time.
*   **Version Control for Golden Files:** The spec mentions "checked-in golden files." It would be beneficial to explicitly state a strategy for managing these golden files under version control, particularly how updates to the golden files will be handled (e.g., specific review process, tools for generation/comparison).
*   **Strategy for JSON Key Order:** The spec calls for "deterministic JSON serialization ordering." While Python 3.7+ preserves dictionary insertion order, this is not explicitly stated as the mechanism, nor is there a requirement for code to explicitly sort keys during serialization if the input dictionary's insertion order isn't guaranteed (e.g., if constructed from arbitrary sources). Ensuring consistent key order for `json.dumps` (e.g., using `sort_keys=True` or an OrderedDict if strict stability across Python versions/implementations is desired) should be a specific requirement.

## 3. Determinism Risks

Based on the code review:

*   **JSON Serialization Key Order:** In `src/rtdsl/codegen.py`, `json.dumps(metadata, indent=2)` is used. While the current `metadata` dictionary *appears* to have a stable insertion order in the provided example (`plan.json`), relying solely on Python's dictionary insertion order guarantee (which is guaranteed from Python 3.7+) without explicitly sorting keys via `sort_keys=True` in `json.dumps` or using an `OrderedDict` could be a portability or future-proofing risk. If the order of keys in the `metadata` dictionary varies across Python versions or environment, the `plan.json` would not be byte-stable.
*   **Floating-Point Determinism in CUDA:** While the goal focuses on *codegen* determinism (the generated `.cu` file itself), the `_render_device` function in `codegen.py` contains floating-point literals (e.g., `1.0e-7f`, `0.0f`). If the values of these literals were derived from computations that could vary due to floating-point precision issues or non-deterministic inputs, it could lead to non-deterministic generated code. However, in the current implementation, these appear to be hardcoded constants, mitigating this risk for codegen but not for runtime behavior.
*   **Path/Environment Dependence:** The output directory generation `Path(output_dir).mkdir(parents=True, exist_ok=True)` is generally safe. However, if any generated content were to include absolute paths, timestamps, or environment variables in the output files (`.cu`, `.cpp`, `.json`), this would introduce non-determinism. The current rendering functions (`_render_device`, `_render_host`, `_render_readme`) do not appear to incorporate such elements, but this should be watched closely in future changes.

## 4. Validation/Test Risks

The current testing infrastructure (`tests/rtdsl_py_test.py`) has the following risks:

*   **Reliance on Substring Checks for Generated Code:** The `test_lower_and_codegen` function uses `self.assertIn` for verifying parts of `device_source` and `metadata`. This approach is brittle and incomplete. A minor change in whitespace, variable naming, or reordering of non-semantically-significant code sections would break these checks, yet a significant semantic change might go undetected if the checked substrings are still present. This directly contradicts the "Golden tests" requirement.
*   **No Full File Golden Comparison:** There are no tests that perform a byte-for-byte or semantically normalized comparison of the generated `device_kernels.cu`, `host_launcher.cpp`, and `plan.json` against "checked-in golden files." This is the primary gap in meeting the "Deterministic generated artifacts" and "Golden tests" requirements.
*   **Limited Negative Testing:** While `test_lower_rejects_missing_segment_id` and `test_lower_rejects_exact_precision_claim` are good starting points, the scope of negative testing is still narrow compared to the types of invalid inputs mentioned in the spec (e.g., unsupported geometry combinations, unsupported emit fields, unsupported acceleration choices, invalid roles or duplicate role declarations).

## 5. Recommended Changes

To address the identified gaps and risks, the following changes are recommended:

1.  **Implement Robust Golden Testing Framework:**
    *   **Action:** Introduce a golden testing mechanism. For each supported kernel input, store expected `plan.json`, `device_kernels.cu`, and `host_launcher.cpp` files as golden references.
    *   **Mechanism:** When tests run, generate the artifacts and compare them (byte-for-byte for `.cu` and `.cpp`, semantically for `.json` if key order is not strictly enforced, otherwise byte-for-byte as well) against the golden files.
    *   **Tools:** Consider using a library like `pytest-golden` or a custom golden file management utility.
    *   **Location:** Golden files should be placed in a dedicated `tests/golden/` directory, organized by kernel name.

2.  **Enhance `plan.json` Deterministic Serialization:**
    *   **Action:** Explicitly enforce sorted keys for `plan.json` output.
    *   **Mechanism:** Modify `json.dumps` call in `src/rtdsl/codegen.py` to `json.dumps(metadata, indent=2, sort_keys=True)`. This ensures byte-stable JSON output regardless of Python version or dictionary construction order.

3.  **Introduce JSON Schema for `plan.json`:**
    *   **Action:** Define a JSON Schema for the `plan.json` structure.
    *   **Mechanism:** Create a `plan_schema.json` file. Add a test case that validates the generated `plan.json` against this schema. This ensures the structure and types of the plan remain consistent.

4.  **Expand Negative Testing Coverage:**
    *   **Action:** Add dedicated test cases for each type of invalid input outlined in the spec ("invalid kernels," "unsupported geometry combinations," "unsupported emit fields," etc.).
    *   **Mechanism:** Use `unittest.assertRaisesRegex` to verify that specific `ValueError` or `TypeError` exceptions are raised with clear, expected error messages.

5.  **Refine `_choose_roles` Function (Minor):**
    *   **Action:** Although currently deterministic, the `_choose_roles` logic in `src/rtdsl/lowering.py` could be slightly clearer about its fallback.
    *   **Mechanism:** Add a comment explaining the default selection (e.g., "Default to right as build, left as probe if no explicit roles or ambiguous roles"). This doesn't change behavior but enhances clarity.

## 6. Final Recommendation

Goal 1 is critical for establishing the compiler's reliability and testability. The current codebase demonstrates a strong foundation with immutable IR and structured generation logic.

**Overall Recommendation: Proceed with implementation, focusing on the recommended changes.**

The most crucial next step is the implementation of a robust golden testing framework, coupled with strict JSON serialization for `plan.json`. This will directly address the core "deterministic generated artifacts" and "golden tests" requirements and significantly de-risk future development by catching unintended changes in the generated output early. The addition of a JSON schema and expanded negative tests will further solidify the compiler's robustness.
