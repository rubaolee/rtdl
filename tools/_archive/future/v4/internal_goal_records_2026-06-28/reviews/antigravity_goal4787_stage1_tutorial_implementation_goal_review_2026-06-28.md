# Antigravity Review: Goal4787 Stage 1 Tutorial Implementation Goal

- **Date:** 2026-06-28
- **Verdict:** `approve_goal4787_with_required_amendments`

This is the full review result for the Stage 1 tutorial implementation plan defined in [goal4787_stage1_tutorial_implementation_goal_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/engineering/goal4787_stage1_tutorial_implementation_goal_2026-06-28.md) based on [call_for_review_goal4787_stage1_tutorial_implementation_goal_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reviews/call_for_review_goal4787_stage1_tutorial_implementation_goal_2026-06-28.md).

---

## Required Review Answers

### 1. Are the output files explicit enough to make implementation auditable?
**Yes, with minor amendments.** The plan lists 22 sequential markdown pages under `tutorials/current/` and 32 tutorial program Python scripts under `examples/tutorial_programs/`. However, there is a minor discrepancy:
- [contact_manifold_lowering.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/contact_manifold_lowering.py) exists in the filesystem and is listed in the tutorial program index [README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/README.md), but is omitted from the target program outputs table in [goal4787_stage1_tutorial_implementation_goal_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/engineering/goal4787_stage1_tutorial_implementation_goal_2026-06-28.md) and is not mapped to any tutorial page.
Once this is amended (see [Required Amendments](#required-amendments) below), the file list will be fully explicit and auditable.

### 2. Are hello world and sorting preserved instead of replaced?
**Yes.** 
- **Hello World:** The restored kernel-based tutorial [02_hello_world.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/02_hello_world.md) and program [hello_world.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/hello_world.py) from [goal4784_restore_original_hello_world_kernel_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/engineering/goal4784_restore_original_hello_world_kernel_2026-06-28.md) are preserved.
- **Sorting:** The Ray-Hit Sorting tutorial [03_sorting_rows.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/03_sorting_rows.md) and program [sorting_rows.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/sorting_rows.py) from [goal4785_restore_goal97_sorting_tutorial_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/engineering/goal4785_restore_goal97_sorting_tutorial_2026-06-28.md) are preserved.

### 3. Does the plan avoid app-specific teaching before language concepts?
**Yes.** The sequence of lessons (01–14) teaches general RTDL primitives, concepts, relations, operators, and continuations. Domain-specific lowerings (graph triangle counting, robotics collision, RayDB, and Hausdorff composition) are deferred to lessons 15–18. The final mapping to the 10 benchmark apps as exams is kept at the very end in lesson 22.

### 4. Does the plan force old-material inspection before rewriting?
**Yes.** The writing rules established in [goal4786_stage1_tutorial_backlog_for_benchmark_apps_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/engineering/goal4786_stage1_tutorial_backlog_for_benchmark_apps_2026-06-28.md) (requiring comparison with old archived files and preservation of working code logic) are explicitly inherited by the implementation rules.

### 5. Are the tutorial page filenames coherent and user-facing?
**Yes.** The files use a simple, sequential two-digit prefix (e.g., `04_relations_and_operators.md` to `22_benchmark_app_bridge.md`) and snake_case topic names. They focus on language concepts rather than internal tracker issues or version identifiers.

### 6. Are any required benchmark-app prerequisites missing?
**Yes, contact lowering is unmapped to a tutorial page.** While [contact_manifold_lowering.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/contact_manifold_lowering.py) exists in the repository, the plan does not schedule a tutorial page for "contact lowering" to explain it, even though "contact lowering" is explicitly listed as a prerequisite for **Contact manifold** in the backlog matrix. This is addressed in the [Required Amendments](#required-amendments).

### 7. Are any planned files unnecessary or harmful?
**No.** All planned files map to concrete topics. Stale tutorial pages (e.g., `05_prepare_run_continue.md`, `06_measure_a_program.md`, `07_benchmark_apps.md`, `08_choose_a_partner.md`, `09_benchmark_harness_protocol.md`) are explicitly marked to be rewritten or archived to avoid user confusion.

### 8. Is the proposed Goal4788-Goal4793 batching appropriate, or should it be split differently?
**Yes.** The proposed batching is appropriate and grouped by concept families:
- **Goal4788:** Foundation cleanup (Lessons 04-06)
- **Goal4789:** Spatial primitives (Lessons 07-09)
- **Goal4790:** Ray & continuation core (Lessons 10-13)
- **Goal4791:** App-lowering concepts (Lessons 14-18)
- **Goal4792:** Boundaries and partner arrays (Lessons 19-22)
- **Goal4793:** Final audit

### 9. Does the plan include sufficient Linux validation and external review gates?
**Yes.** Every script must compile and run on Linux with `PYTHONPATH=src:.`. Goal4788 requires generating audit and validation logs (`docs/engineering/goal4788_stage1_tutorial_file_audit_2026-06-28.md`, `docs/engineering/goal4788_stage1_tutorial_linux_validation_2026-06-28.md`, and `docs/engineering/goal4788_stage1_tutorial_link_validation_2026-06-28.md`), and each implementation batch requires external review before closure.

### 10. May implementation begin after this plan is approved?
**Yes.** Approval allows implementation to begin starting with Goal4788.

---

## Required Amendments

To resolve the discrepancy regarding [contact_manifold_lowering.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/contact_manifold_lowering.py):

1. **Add program to implementation table:** Add `examples/tutorial_programs/contact_manifold_lowering.py` to the table of "Public Tutorial Program Outputs" in [goal4787_stage1_tutorial_implementation_goal_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/engineering/goal4787_stage1_tutorial_implementation_goal_2026-06-28.md).
2. **Map to a tutorial page:** Add a corresponding tutorial page for contact manifold lowering (e.g., `tutorials/current/15_contact_manifold_lowering.md` and shift subsequent page numbers: graph triangle counting to `16`, robot collision to `17`, raydb to `18`, and hausdorff to `19`).
3. **Include in Goal4791:** Ensure the contact manifold lowering tutorial page and its program audit/validation are explicitly covered within the scope of the **Goal4791** batch.
