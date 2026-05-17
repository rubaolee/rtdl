# Goal2250: Gemini Review of Goal2248/2249 Prepared Closed-Shape Membership

## Independent Gemini Review

This is an independent Gemini review, distinct from any Codex review.

## Review Questions and Findings

### 1. Does the native ABI remain app-agnostic, using point/closed-shape/membership vocabulary rather than RayJoin/PIP/polygon app-specific names?

**Finding:** Yes, the native ABI remains app-agnostic. The native functions exposed, such as `rtdl_optix_prepare_point_closed_shape_membership_2d`, `rtdl_optix_run_prepared_point_closed_shape_membership_2d`, and `rtdl_optix_destroy_prepared_point_closed_shape_membership_2d`, consistently use generic terms like "point," "closed-shape," and "membership." This naming convention avoids any RayJoin, PIP, or polygon-specific terminology, aligning with the stated design principle of an app-agnostic native interface.

### 2. Does the Python runner correctly route same-query PIP OptiX through the prepared closed-shape membership path while preserving the RayJoin row contract at the Python layer?

**Finding:** Yes, the Python runner correctly routes and preserves the contract. The pod evidence artifact (`goal2249_rayjoin_pip_prepared_closed_shape_same_query_pod_2026-05-17.json`) explicitly records `"implementation_path": "prepared_closed_shape_membership_2d_optix"` and `"input_preparation_path": "prepared_shape_scene_and_prepacked_points_once_per_run_stream"`. The Python test (`tests/goal2249_rayjoin_pip_prepared_closed_shape_pod_evidence_test.py`) validates these paths and asserts that `same_contract_with_rayjoin_query_exec` is true, confirming that the RayJoin row contract is maintained through the Python harness, which maps generic membership rows back to `point_id` / `polygon_id` fields.

### 3. Is the pod evidence correctly tied to the pushed commit and does it support only the narrow claim made in the report?

**Finding:** Yes, the pod evidence is correctly tied to the specified commit and supports only narrow claims. Both the pod evidence JSON artifact and the accompanying Markdown report explicitly reference the commit `9e8c60ef6ae6a1311940b76861fc9a665a52dcc5`. The report includes a clear "Boundary" section that disclaims broader implications, and the Python test actively verifies that the `claim_boundary` within the JSON artifact prevents overclaiming on performance, general applicability, or release readiness.

### 4. Does the boundary avoid overclaiming full RayJoin reproduction, RTDL beating RayJoin, paper-scale speedup, broad PIP acceleration, or v2.0 release readiness?

**Finding:** Yes, the boundary successfully avoids overclaiming. The "Boundary" section of the `goal2249_rayjoin_pip_prepared_closed_shape_pod_evidence_2026-05-17.md` report explicitly states that it does not authorize claims regarding full RayJoin reproduction, RTDL beating RayJoin, paper-scale speedup, broad PIP acceleration, or v2.0 release readiness. The `test_claim_boundary_remains_narrow` in the corresponding test file programmatically confirms that these overclaiming flags are set to `false` in the pod evidence JSON.

## Verdict

**Verdict: accept**