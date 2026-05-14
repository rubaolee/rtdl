# Goal1954 - Gemini Review of Goal1953 RawKernel Control-App v2 Decision

Status: accept

Date: 2026-05-13

## Review of Goal1953

This review assesses the implementation, testing, and documentation surrounding the decision to allow the four former control apps to use CuPy `RawKernel` continuations as their v2.0 app versions.

### 1. Does the implementation preserve the user decision accurately?

**Verdict:** Yes.
The `examples/rtdl_control_apps_cupy_rawkernel.py` implementation accurately reflects the user decision to allow the four specified applications (`database_analytics`, `graph_analytics`, `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`) to utilize CuPy `RawKernel` continuations for their v2.0 versions. The code includes dedicated `RawKernel` sources and the `FAIRNESS_NOTE` as mandated. The test `test_example_defines_four_control_app_rawkernel_sources` in `tests/goal1953_control_apps_cupy_rawkernel_v2_test.py` confirms the presence of these elements.

### 2. Does the CPU fallback prove local app-result parity without overclaiming performance?

**Verdict:** Yes.
The `cpu_fallback` mode implemented in `rtdl_control_apps_cupy_rawkernel.py` correctly establishes local app-result parity by comparing results against v1.8 Python+RTDL oracles without invoking CuPy. The `claim_boundary` explicitly marks `cpu_fallback_is_correctness_only`, preventing any overestimation of performance. The `test_cpu_fallback_all_apps_match_v1_8_oracles` in the test suite verifies this parity and the correctness-only nature of the fallback.

### 3. Are the four app summaries compared to appropriate v1.8 Python+RTDL oracles?

**Verdict:** Yes.
As confirmed in `goal1953_control_apps_cupy_rawkernel_v2_decision_2026-05-13.md`'s "App Contracts" table, and verified in the implementation (`rtdl_control_apps_cupy_rawkernel.py`), each of the four applications is compared against its respective v1.8 Python+RTDL oracle using `"cpu_python_reference"`. The test `test_cpu_fallback_all_apps_match_v1_8_oracles` further validates these comparisons, ensuring accurate baselining.

### 4. Does the report correctly block speedup claims until real CuPy pod timing is collected?

**Verdict:** Yes.
The `goal1953_control_apps_cupy_rawkernel_v2_decision_2026-05-13.md` report explicitly states the `implemented-local-contract-pod-timing-needed` status and clearly outlines "Still blocked until pod timing" for performance claims. The `rtdl_control_apps_cupy_rawkernel.py` output structure also contains a `claim_boundary` that sets `whole_app_speedup_claim_authorized_without_measurement` to `False` and `requires_pod_for_cupy_timing` to `True` when running with CuPy. This aligns perfectly with the requirement to defer speedup claims.

### 5. Are the claim boundaries consistent with Goal1952 and `docs/partner_acceleration_boundaries.md`?

**Verdict:** Yes.
The claim boundaries established in `goal1953_control_apps_cupy_rawkernel_v2_decision_2026-05-13.md`, particularly the fairness note and the conditions for making speedup claims, are entirely consistent with the principles detailed in `docs/reports/goal1952_partner_rawkernel_and_user_continuation_boundary_2026-05-13.md` and `docs/partner_acceleration_boundaries.md`. All documents consistently differentiate between allowed user usage of `RawKernel` and official RTDL acceleration claims, which require specific implementation, measurement, and review. The implementation's `fairness_note` and `claim_boundary` dynamically reflect these constraints.

## Final Verdict

**accept**