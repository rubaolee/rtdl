# Gemini Review: Goal3517 Prepared Execution Pattern

**Reviewer:** Gemini CLI
**Date:** 2026-06-05

**Goal:** Goal3517 Prepared Execution Pattern

**Review File:** `docs/reviews/goal3519_gemini_review_goal3517_prepared_execution_pattern_2026-06-05.md`

## Inspection Points and Findings:

### 1. The workflow is explicit: `prepare -> pack/cache -> warm -> run steady-state -> explain timings`.

**Findings:**
The explicit workflow is clearly defined in `src/rtdsl/prepared_execution.py` via `PREPARED_EXECUTION_WORKFLOW`. The `docs/learn/prepared_execution_pattern.md` also explicitly states and explains this five-step workflow. The `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py` script demonstrates this by including steps for payload preparation/caching, warming up device columns, running the main executor, and generating an artifact with detailed timings. The `tests/goal3517_prepared_execution_user_pattern_test.py` directly asserts this workflow sequence. The `docs/reports/goal3517_prepared_execution_user_pattern_2026-06-05.md` reiterates the workflow explicitly.

### 2. Phase timing is separated: setup, cache load/write, warmups, steady-state stream, planner, executor, and validation oracle.

**Findings:**
`src/rtdsl/prepared_execution.py` defines `PREPARED_EXECUTION_REQUIRED_PHASES` (`prepare`, `cache_load`, `warmup`, `steady_state_stream`, `planner`, `executor`, `validation`) and uses `PreparedExecutionReport` to enforce this separation. The `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py` script's `timing_sec` dictionary explicitly breaks down execution into granular phases such as `payload_cache_load`, `active_relation_device_columns_warmup_secs`, `device_tile_task_planning`, `cupy_tile_task_executor`, and `exact_oracle` (validation). The `docs/learn/prepared_execution_pattern.md` table details the mapping of these steps to timing fields, and `tests/goal3517_prepared_execution_user_pattern_test.py` asserts that all required phases are present and timed separately. The `docs/reports/goal3517_prepared_execution_user_pattern_2026-06-05.md` also explicitly lists these phases and their purpose.

### 3. Partner choice remains explicit; there is no hidden Triton/CuPy/Numba/Torch selection.

**Findings:**
`src/rtdsl/prepared_execution.py` explicitly uses `explicit_partner` in `PreparedExecutionReport` and raises an error if `automatic_partner_selection_allowed` is true. `src/rtdsl/__init__.py` imports various partner-specific modules, indicating explicit integration. `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py` explicitly imports and uses `cupy` and prepares `rayjoin_optix` components, and the `interpretation` field of its artifact states "Partner choice is explicit in executor_metadata.partner." The `docs/learn/prepared_execution_pattern.md` and `docs/reports/goal3517_prepared_execution_user_pattern_2026-06-05.md` both explicitly state that "The user still chooses the backend and partner" and "hidden partner selection" is not authorized. `tests/goal3517_prepared_execution_user_pattern_test.py` asserts that `automatic_partner_selection_allowed` is false and explicitly checks for "optix" and "cupy" as backend/partner. The `goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json` artifact explicitly lists "cupy" as the partner in multiple metadata sections.

### 4. The native engine remains generic and app interpretation stays in Python or examples.

**Findings:**
`src/rtdsl/prepared_execution.py`'s `PreparedExecutionReport` raises a `ValueError` if `app_specific_engine_logic_allowed` is true, enforcing genericity. The `docs/learn/prepared_execution_pattern.md` explicitly states, "The native engine remains generic. Application interpretation stays in Python examples or user code..." This is reinforced by `docs/reports/goal3517_prepared_execution_user_pattern_2026-06-05.md`. The `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py` is itself a Python application that orchestrates calls to the `rtdsl` library, demonstrating the "app interpretation stays in Python or examples" aspect. The `goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json` artifact's `interpretation` field describes the execution of a "prepared ... tile-task plan" with comparison to an "external Shapely/GEOS oracle," indicating generic engine use and Python-based interpretation. `tests/goal3517_prepared_execution_user_pattern_test.py` also asserts that `app_specific_engine_logic_allowed` is false.

### 5. Claim boundaries remain false and no public/release/performance wording is newly authorized.

**Findings:**
`src/rtdsl/prepared_execution.py` explicitly defines `PREPARED_EXECUTION_CLAIM_BOUNDARY` which enumerates disallowed claims (e.g., release, public speedup wording, true zero-copy wording). The `PreparedExecutionReport` raises `ValueError` if any such claims are attempted. The `docs/learn/prepared_execution_pattern.md` and `docs/reports/goal3517_prepared_execution_user_pattern_2026-06-05.md` both list "Boundaries" that explicitly state what the prepared execution does not authorize. The `tests/goal3517_prepared_execution_user_pattern_test.py` rigorously asserts that all claim-related flags (`release_authorized`, `public_speedup_claim_authorized`, etc.) are `False` in the `PreparedExecutionReport` and that validation rejects any attempt to authorize them. The `goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json` artifact consistently shows `false` for all authorization flags in its top-level and nested `claim_boundary` fields.

### 6. The no-new-pod choice is reasonable for this normalization-only goal, with current-HEAD pod confirmation deferred to Goal3521 if needed.

**Findings:**
The prompt explicitly states that this is a "normalization-only goal." The `docs/reports/goal3517_prepared_execution_user_pattern_2026-06-05.md` report directly confirms this: "No new pod run was required because the goal consumes existing Goal3511 pod evidence and does not alter the measured execution path." The goal focuses on defining and reporting on an existing execution pattern and consuming existing artifacts (like `goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json`), rather than implementing new functionality that would necessitate a fresh pod run. The deferral of a current-HEAD pod confirmation to Goal3521 further supports this reasoning.

## Verdict:
accept-with-boundary
