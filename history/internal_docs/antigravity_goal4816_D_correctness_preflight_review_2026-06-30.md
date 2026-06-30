# Goal4816-D RayJoin Correctness Preflight And Smoke Plan Review

- **Date:** 2026-06-30
- **Reviewer:** Antigravity (AI Coding Assistant)
- **Review Target:** [goal4816_D_rayjoin_correctness_preflight_smoke_plan_2026-06-30.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4816_D_rayjoin_correctness_preflight_smoke_plan_2026-06-30.md)
- **Verdict:** `approve_goal4816_D_correctness_preflight_authorize_smoke_execution`

---

## Verdict Description
The correctness preflight and smoke plan for **Goal4816-D** is approved. The plan strictly adheres to the role constraints, ensuring the executor acts strictly as an RTDL user/application author. It avoids performance benchmarking and prohibits runtime or native modifications to [src/rtdsl/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl) or [src/native/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native). The environment preflight checks, route separation, exit labels, and artifact specifications are comprehensive and sufficient to support an auditable correctness-smoke execution.

---

## Findings

### P2 Findings (Minor / Informational)
- **F-01: Verification of Input Provenance for county x zipcode data:**
  The county x zipcode data is listed as `same_source_regenerated_cdb` unless exact provenance is re-established. Smoke testing must ensure that if the output doesn't match the historical exact output, it is correctly classified as a diagnostic check rather than an exact reproduction failure, which is properly planned.
- **F-02: Missing Author Output Mitigation:**
  If the author output does not exist or is missing, the plan properly instructs the executor to report `author_baseline_missing_for_input` and avoid claiming reproduction. This is a crucial fail-safe.
- **F-03: Explicit Route Labeling in Artifacts:**
  The plan mandates that every artifact must explicitly include the route label (`bundled_helper_bounded_available_input_reproduction_not_generic` or `generic_primitive_numba_attempt`). This ensures auditability and prevents mixing helper-based validation with generic-language capability validation.

---

## Answers to the 10 Specific Questions

### 1. Does the plan correctly keep the executor in RTDL-user mode rather than RTDL developer mode?
Yes. The plan explicitly specifies that "The executor is an RTDL user/application author, not an RTDL developer." It permits using released package behavior and writing user-side reproduction scripts or notebooks outside [src/rtdsl/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl) and [src/native/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native).

### 2. Does it prevent runtime/native/release-surface modification?
Yes. It explicitly forbids patching RTDL runtime/native code, adding or exposing a new RayJoin primitive, and modifying any tracked files under [src/rtdsl/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl) or [src/native/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native). Any modifications will trigger an immediate halt and report `blocked_by_dirty_runtime_tree`.

### 3. Does it correctly avoid authorizing performance benchmarking?
Yes. The plan states upfront that it does not authorize performance benchmarking, optimization, or runtime edits. It forbids timing interpretation or speedup claims for both Route 1 and Route 2.

### 4. Does it define environment checks strongly enough for Windows/local Linux/POD portability?
Yes. It lists all key environment and system facts that must be recorded (OS, Python, RTDL path, git commit/status, CUDA/Numba availability). It mandates the use of `pathlib.Path` and environment variables for cross-platform portability.

### 5. Does it correctly require route labels and prevent bundled-helper evidence from being reported as generic user-language reproduction?
Yes. It defines explicit, distinct route labels (`bundled_helper_bounded_available_input_reproduction_not_generic` and `generic_primitive_numba_attempt`) and forbids claiming bundled helper output as generic language reproduction.

### 6. Does the first smoke route correctly focus on bundled-helper correctness over available inputs without speedup claims?
Yes. The first route focus is purely on whether the environment and inputs support correctness validation using [run_rayjoin_overlay_rtdl_from_cdb_paths](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py) backend correctness checks (byte equality or topology hash diagnostics), and explicitly bans speedup or timing comparisons.

### 7. Does the second smoke route correctly frame generic primitive + Numba as a gap probe rather than full overlay reproduction?
Yes. It frames Route 2 as a capability probe/gap check (`generic_primitive_numba_attempt`) to see how far a user can get without private helpers. It forbids private helpers or claiming scalar counts as overlay, expecting it to be blocked by the `generic_route_blocked_by_public_lsi_row_coordinate_gap`.

### 8. Are the artifact requirements sufficient for later external audit?
Yes. The plan defines a precise set of output files (`environment.json`, `input_manifest.json`, `author_command.txt`, `rtdl_command_or_script.py`, `correctness_summary.json`, `correctness_summary.md`, output files/hashes, raw logs) which must detail the route label, input provenance, and checking status.

### 9. Are the exit labels honest and complete?
Yes. The exit labels (`bundled_helper_correctness_smoke_pass_not_generic`, `bundled_helper_correctness_smoke_inconclusive_missing_author_output`, `generic_primitive_numba_smoke_blocked_by_public_lsi_row_coordinate_gap`, etc.) cover all expected execution paths and potential blocking scenarios, ensuring complete reporting.

### 10. Should the next execution goal be authorized as a correctness smoke, or must Goal4816-D be amended first?
The next correctness-smoke execution goal is authorized to proceed. The plan outlined in [goal4816_D_rayjoin_correctness_preflight_smoke_plan_2026-06-30.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4816_D_rayjoin_correctness_preflight_smoke_plan_2026-06-30.md) is comprehensive, maintains user-space constraints, and requires no further amendments before execution.

---

## Authorization Statement
The next correctness-smoke execution goal is **authorized** to proceed using the plan set out in [goal4816_D_rayjoin_correctness_preflight_smoke_plan_2026-06-30.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4816_D_rayjoin_correctness_preflight_smoke_plan_2026-06-30.md). This authorization is strictly for correctness validation under RTDL user mode.

---

## Non-Authorization Block
This review does **NOT** authorize:
1. Performance runs, timing comparisons, scaling benchmarks, or speedup claims.
2. Modifying files under [src/rtdsl/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl), [src/native/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native), or the v2.14 release surface.
3. Claims of full 8/8 Section 5.7 reproduction.
4. Treating private, internal, or underscored RTDL functions as public, generic APIs.
5. Reporting bundled-helper results as generic user-language evidence.
