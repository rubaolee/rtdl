# Claude External Review: Goal3056 v2.6 Pre-Release Public Doc Cleanup

Date: 2026-06-02
Reviewer: Claude (Sonnet 4.6), acting as an independent external reviewer
Verdict: **accept**

This review is read-only and independent from Codex authoring. It does not
authorize a v2.6 release, package-install wording, broad RT-core speedup
wording, broad CuPy/Numba acceleration wording, true-zero-copy wording, hidden
partner auto-selection, or app-specific native-engine behavior.

---

## Files Inspected

- `docs/reports/goal3056_v2_6_pre_release_public_doc_cleanup_audit_2026-06-02.md`
- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `docs/backend_maturity.md`
- `docs/current_main_support_matrix.md`
- `docs/partner_acceleration_boundaries.md`
- `docs/app_example_quickstart.md`
- `docs/tutorials/README.md`
- `docs/tutorials/v2_app_building.md`
- `docs/tutorials/partner_optix_column_anyhit.md`
- `docs/rtdl_feature_guide.md`
- `docs/application_catalog.md`
- `examples/README.md`
- `examples/v2_0/README.md`
- `tests/goal3056_v2_6_pre_release_public_doc_cleanup_audit_test.py`

---

## Review Question 1: One coherent learner story

All fourteen current-facing documents now present a consistent two-lane
narrative: v2.3 is the latest released source-tree evidence package and
v2.6 is the active internal pre-release lane.

Specific evidence from each primary doc:

- **`README.md`**: "The current released version is `v2.3`" and "The active
  internal pre-release lane is `v2.6`" appear in the opening paragraph. The
  v2.6 lane description is summarised in plain bullet points and clearly
  labelled not a release tag.
- **`docs/README.md`**: "RTDL v2.3 is the released source-tree
  Python+partner+RTDL app-portfolio surface. The active internal v2.6
  pre-release lane keeps source-tree usage, preserves the
  no-broad-speedup/no-package-install boundary, and adds current
  partner-choice guidance."
- **`docs/current_architecture.md`**: "RTDL v2.3 is the current source-tree
  Python+partner+RTDL release. The active internal v2.6 pre-release lane
  preserves the same v2.x language boundary... The current released version
  remains `v2.3`; v2.6 is not a release tag yet."
- **`docs/current_main_support_matrix.md`**: "Current released version is
  `v2.3`. Active pre-release docs target: v2.6 source-tree partner-choice
  guidance."
- **`docs/backend_maturity.md`**: "Status: current v2.x release plus v2.6
  pre-release backend maturity guide."
- **`docs/partner_acceleration_boundaries.md`**: "v2.3 is the current
  released source-tree Python+partner+RTDL evidence package. The active v2.6
  lane is internal pre-release work... v2.6 is not a release tag yet."
- **`docs/tutorials/README.md`**: "This page is intentionally single-surface.
  It teaches the current v2.x source tree: v2.3 is the latest released
  evidence package, while v2.6 is the active internal pre-release lane."
- **`examples/README.md`**: "The latest released evidence package is v2.3,
  and active v2.6 pre-release partner guidance is documented inside the same
  source-tree example family."

No doc contradicts this story. No doc presents v2.6 as released.

**Finding: passes cleanly.**

---

## Review Question 2: Stale wording removed

The audit report lists nine forbidden phrases. I verified their absence across
all fourteen current-facing documents:

| Phrase | Status |
| --- | --- |
| `partner_optix_zero_copy_anyhit` | Absent from all fourteen docs |
| `Triton-first` | Absent |
| `Triton first` | Absent |
| `default Triton` | Absent |
| `auto-select Triton` | Absent |
| `zero-cost` | Absent |
| `compile-time zero-copy` | Absent |
| `current v2.3 release` | Absent |
| `v2.3 users first` | Absent |

The old OptiX tutorial file
`docs/tutorials/partner_optix_zero_copy_anyhit.md` is deleted (confirmed
by git status showing `D docs/tutorials/partner_optix_zero_copy_anyhit.md`
and file absence at that path). Every reference that previously pointed to
that filename now points to `partner_optix_column_anyhit.md`.

Triton is uniformly described as "paused" throughout the current-facing
surface. No hidden default partner language was found.

**Finding: passes cleanly.**

---

## Review Question 3: Current partner model correctly stated

The five-element partner model is stated correctly and consistently:

**Primitive first:**
`docs/current_architecture.md`, `docs/partner_acceleration_boundaries.md`,
`docs/current_main_support_matrix.md`, and the tutorials all lead with
"Use a fused generic native RTDL primitive when it exactly expresses the work."

**Explicit user partner choice second:**
`docs/current_main_support_matrix.md`: "users choose supported partners
explicitly, while benchmark recommendations must be backed by same-contract
evidence and never by hidden defaults."
`docs/partner_acceleration_boundaries.md`: "Users choose supported partners
explicitly. RTDL guidance may recommend a partner only when same-contract
evidence supports that recommendation."

**CuPy as the mature CUDA-array lane:**
`docs/backend_maturity.md` table: CuPy row — "Current v2.x partner model
for device arrays and explicit user kernels where needed."
`docs/current_main_support_matrix.md`: "CuPy is the mature CUDA-array lane."
`docs/current_architecture.md`: "CuPy remains the mature CUDA-array and
library-continuation partner."

**Numba as the measured custom-continuation lane:**
`docs/backend_maturity.md` table: Numba row — "v2.6 pre-release
custom-continuation lane. Recommended only for measured custom CUDA-style
continuation rows; never auto-selected."
`docs/current_main_support_matrix.md`: "Numba is the current v2.6
custom-kernel lane."
`docs/rtdl_feature_guide.md`: "Numba as the active v2.6 pre-release lane for
selected measured custom CUDA-style continuations."
`docs/partner_acceleration_boundaries.md`: "Numba is the v2.6 custom
CUDA-style continuation lane for selected measured contracts such as compact
masks and grouped reductions."

**Triton paused:**
`docs/current_architecture.md`: "Triton is paused for recommended paths until
same-contract timing proves a win."
`docs/backend_maturity.md` table: Triton row — "Paused recommendation lane.
Preview/history surface only until same-contract timing proves a useful path."
`docs/current_main_support_matrix.md`: "Triton remains paused until
same-contract timing wins."
`docs/partner_acceleration_boundaries.md`: "Triton remains paused for
recommended paths until same-contract timing proves it should return."

The model is consistent across every doc that describes partners.

**Finding: passes cleanly.**

---

## Review Question 4: No overclaims in edited current-facing files

Each doc was scanned for the six blocked claim categories.

**Package-install:** No doc claims installability. `README.md` explicitly
says "do not read any current or pre-release doc as a package-install
promise."

**Broad RT-core speedup:** No doc makes this claim. `docs/app_example_quickstart.md`
lists "NVIDIA RT-core speedup" under "What this does not show."
`docs/current_main_support_matrix.md` non-claims section states "broad speedup
across all workloads" is off-limits. `examples/README.md` states "Selecting
`--backend optix` does not automatically make a public RT-core speedup claim."

**Whole-app acceleration:** Not claimed. All benchmark rows in
`docs/application_catalog.md` carry explicit "do not claim" columns (e.g.
"No claim that every Hausdorff input beats every CUDA implementation").

**Arbitrary partner-program acceleration:** `docs/partner_acceleration_boundaries.md`
carries an explicit "Blocked wording" section listing "RTDL accelerates
arbitrary PyTorch code," "RTDL accelerates arbitrary CuPy code," and "RTDL
accelerates arbitrary Numba code" as forbidden. The feature guide says
"This is not an automatic speedup promise."

**Release readiness:** v2.6 is consistently framed as "not a release tag yet"
and "internal pre-release." No doc presents v2.6 as released.

**General true-zero-copy:** `docs/tutorials/partner_optix_column_anyhit.md`
explicitly lists "a general true-zero-copy product guarantee" under "Not
allowed." `docs/current_main_support_matrix.md` non-claims section states
"true zero-copy unless the exact measured path proves device-resident
handoff." `docs/current_architecture.md` says "Full residency-first,
partner-neutral device-memory composition remains a v3.0 roadmap item."

**Finding: no overclaims found.**

---

## Review Question 5: No remaining stale links to old filename

The old file `docs/tutorials/partner_optix_zero_copy_anyhit.md` does not
exist at that path. The new file `docs/tutorials/partner_optix_column_anyhit.md`
exists and contains:

- "a general true-zero-copy product guarantee" in the Not Allowed section
- "[Choosing A Partner For Custom Logic](../learn/partner_choice_for_custom_logic.md)"
  link to the v2.6 partner-choice guide

References updated in:

- `docs/tutorials/README.md`: uses `partner_optix_column_anyhit.md` in both
  the step ladder and the Python+Partner+RTDL learning track.
- `docs/app_example_quickstart.md`: "Advanced OptiX partner path" row links
  to `tutorials/partner_optix_column_anyhit.md`.
- `docs/tutorials/v2_app_building.md`: "Read Next" section links
  `partner_optix_column_anyhit.md`.

No references to `partner_optix_zero_copy_anyhit` remain in any of the
fourteen current-facing documents.

**Finding: old filename fully removed; no stale links remain.**

---

## Audit Report Consistency

The `docs/reports/goal3056_v2_6_pre_release_public_doc_cleanup_audit_2026-06-02.md`
correctly describes the scope and all file-by-file operations. The
"Audit Checks" section lists all nine forbidden phrases as confirmed absent,
which matches my independent inspection. The boundary statement is accurate:
"This goal is documentation cleanup only. It does not release v2.6, authorize
a tag, change package metadata, authorize broad speedup wording, or turn
Numba, CuPy, PyTorch, or Triton into automatic hidden defaults."

---

## Test Alignment

The test `tests/goal3056_v2_6_pre_release_public_doc_cleanup_audit_test.py`
has four methods:

1. `test_report_records_file_by_file_operations` — verified the audit report
   contains all required phrases and all fourteen file paths.
2. `test_current_docs_use_clean_v26_boundary` — verified all five targeted
   phrases are present in the correct files (confirmed in Review Question 1
   and 3 above).
3. `test_stale_current_facing_phrases_are_removed` — scans all fourteen docs
   for nine forbidden phrases; independent inspection found zero occurrences.
4. `test_optix_partner_tutorial_uses_clean_filename_and_boundary` — old path
   absent, new path present, two key phrases confirmed in the new tutorial.

All four test methods are consistent with the reviewed state of the source
tree.

---

## Minor Observations (non-blocking)

The audit report mentions `docs/tutorials/db_workloads.md`,
`docs/tutorials/feature_quickstart_cookbook.md`,
`docs/tutorials/nearest_neighbor_workloads.md`, and
`docs/tutorials/partner_anyhit.md` as also edited. These are not in the
fourteen `CURRENT_FACING_DOCS` covered by the test scan and were not in the
handoff's primary read list. Since those tutorials are not in the forbidden-
phrase test surface and the audit report documents their cleanup, their
omission from the main test gate is a known bounded scope choice, not a gap.

---

## Summary

Goal3056 delivers a clean, coherent public learner surface for the active v2.6
internal pre-release lane. All fourteen current-facing documents agree on the
v2.3 released / v2.6 pre-release story, state the five-element partner model
correctly, contain none of the nine forbidden stale phrases, and carry no
overclaims. The old zero-copy tutorial filename is gone and all references
point to the correctly named and correctly bounded replacement.

**Verdict: accept**
