# Goal3056 v2.6 Pre-Release Public Doc Cleanup Audit

Status: source-tree cleanup complete; external review pending.

Date: 2026-06-02

## Purpose

This cleanup prepares the public learner path for the active v2.6 internal
pre-release lane without pretending v2.6 has been released.

The corrected public story is:

- v2.3 remains the latest released source-tree evidence package.
- v2.6 is the active internal pre-release lane for explicit partner-choice
  guidance.
- RTDL primitives remain the first choice when a fused generic primitive exactly
  expresses the work.
- Users choose partners explicitly; RTDL does not auto-select partners.
- CuPy is the mature CUDA-array/library-continuation partner.
- Numba is the v2.6 lane for selected measured custom CUDA-style continuations.
- Triton is paused for recommended paths until same-contract timing proves it
  should return.
- No package-install, true-zero-copy, broad RT-core, whole-app speedup, or
  arbitrary partner-program acceleration claim is authorized by these docs.

## File-by-File Findings And Operations

| File | Finding | Operation |
| --- | --- | --- |
| `README.md` | Front page described v2.3 only and did not mention active v2.6 partner-choice work. | Added released-vs-pre-release wording, v2.6 partner-choice summary, CuPy/Numba guidance links, and explicit non-claims. |
| `docs/README.md` | Docs index said learner docs explain only v2.3. | Reframed the docs door as one coherent v2.x surface: v2.3 released evidence plus v2.6 internal pre-release guidance. |
| `docs/current_architecture.md` | Architecture page still used v2.5 closeout phrasing and did not clearly state v3.0 residency boundary. | Rewrote partner architecture around the active v2.6 primitive-first rule, CuPy/Numba roles, Triton pause, and v3.0 residency-first scope. |
| `docs/backend_maturity.md` | Backend table lacked the current Numba role and kept v2.3-specific proof-backend wording. | Added Numba and Triton partner rows, updated partner interpretation, and normalized proof-backend wording to current release boundaries. |
| `docs/current_main_support_matrix.md` | Matrix used v2.5 closeout language and a broad partner-continuation row. | Updated the boundary to v2.6 pre-release, explicit partner choice, CuPy mature lane, Numba custom-kernel lane, and Triton paused status. |
| `docs/partner_acceleration_boundaries.md` | Current learner-facing page carried a long historical v2.4/v2.5 timeline and old Triton planning text. | Replaced the timeline with a compact v2.6 partner-choice rule and moved old context behind historical report links. |
| `docs/app_example_quickstart.md` | Advanced OptiX tutorial link used a misleading `zero_copy` filename and casual zero-copy wording. | Updated the link to `partner_optix_column_anyhit.md` and tightened the claim boundary to true-zero-copy/non-claim wording. |
| `docs/tutorials/partner_optix_column_anyhit.md` | Tutorial content was current but the old filename implied product-wide zero-copy. | Renamed from `partner_optix_zero_copy_anyhit.md`, added v2.6 partner-choice link, and made the true-zero-copy non-claim explicit. |
| `docs/tutorials/README.md` | Tutorial ladder described v2.3 only and linked the old OptiX filename. | Updated to v2.x plus active v2.6 pre-release guidance, added partner-choice links, and switched to the clean OptiX tutorial filename. |
| `docs/tutorials/v2_app_building.md` | Partner layer omitted Numba and linked the old OptiX tutorial filename. | Added selected Numba continuations, pointed readers to the v2.6 partner-choice guide, and updated the OptiX tutorial link. |
| `docs/tutorials/db_workloads.md` | DB tutorial had v2.3-only learner wording. | Reframed as current v2.x learning and pointed custom continuations to the v2.6 partner-choice guide. |
| `docs/tutorials/feature_quickstart_cookbook.md` | Several notes said performance wording must come only from a v2.3 evidence packet. | Replaced those notes with current reviewed-evidence wording. |
| `docs/tutorials/nearest_neighbor_workloads.md` | Nearest-neighbor tutorial used v2.3-only evidence wording. | Replaced it with current reviewed-evidence wording. |
| `docs/tutorials/partner_anyhit.md` | Partner-runtime warning omitted Numba. | Added Numba to the list of app/partner runtimes that must not become the engine. |
| `docs/rtdl_feature_guide.md` | Feature guide did not mention the v2.6 Numba custom-continuation lane. | Added selected Numba continuations to the columnar partner feature surface and partner features list. |
| `docs/application_catalog.md` | Catalog partner examples and output guidance omitted Numba. | Added Numba to partner continuation examples and measured-continuation output guidance. |
| `examples/README.md` | Examples index described v2.3 users first and omitted Numba from partner continuation boundaries. | Reframed as current v2.x plus v2.6 pre-release guidance and added Numba to partner examples/non-claims. |
| `examples/v2_0/README.md` | Example tree described v2.3 only and omitted Numba. | Reframed the tree as current v2.x with v2.6 partner-choice guidance and added Numba to partner examples. |
| `tests/goal1842_partner_zero_copy_docs_update_test.py` | Historical test still required the old zero-copy tutorial filename and stale preview wording. | Updated the regression to protect the new partner-column tutorial boundary. |
| `tests/goal2094_v2_learner_doc_single_version_cleanup_test.py` | Learner-doc test still scanned the old OptiX tutorial filename. | Updated the current learner-doc set to the new tutorial filename. |
| `tests/goal2096_v2_tutorial_directory_cleanup_test.py` | Tutorial cleanup test still required the old OptiX tutorial filename. | Updated the tutorial cleanup ledger expectation to the new filename. |

## Audit Checks

The current-facing doc scan no longer finds:

- `partner_optix_zero_copy_anyhit`
- `Triton-first`
- `Triton first`
- `default Triton`
- `auto-select Triton`
- `zero-cost`
- `compile-time zero-copy`
- `current v2.3 release`
- `v2.3 users first`

The remaining v2.3 references are release-evidence links or released-version
statements. The remaining v2.5 references are historical report links in the
partner boundary doc. The current learner rule is v2.6 pre-release guidance, not
v2.5 planning.

## Boundary

This goal is documentation cleanup only. It does not release v2.6, authorize a
tag, change package metadata, authorize broad speedup wording, or turn Numba,
CuPy, PyTorch, or Triton into automatic hidden defaults.

