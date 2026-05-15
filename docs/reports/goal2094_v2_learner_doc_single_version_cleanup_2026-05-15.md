# Goal2094 v2 Learner Doc Single-Version Cleanup

Date: 2026-05-15

## Rule Applied

Learner/user-oriented docs should describe one current surface: v2.0-facing
Python+partner+RTDL as a pre-release candidate. Older version history and goal
archaeology should live outside the normal learner path, with links to history
or release-report archives.

## File-by-File Findings And Operations

| File | Finding | Operation |
| --- | --- | --- |
| `README.md` | Front page still described v1.8 as the current release and used v1.8 section headings. | Reframed as v2.0-facing pre-release candidate; removed v1.8 learner framing; linked to clean v2.0 candidate note and legacy history note. |
| `docs/README.md` | Docs index mixed current learner path with v1.8/v2.0 roadmap and older report links. | Rewrote current promise as v2.0-facing; removed older release report links from performance starter list; routed history to legacy note. |
| `docs/quick_tutorial.md` | Tutorial named the v1.8 split in the learner path. | Changed to current v2.0-facing split without older-version context. |
| `docs/current_architecture.md` | Architecture page was mostly chronological release history from older versions. | Replaced with compact v2.0-facing architecture: Python app, RTDL language, partner adapter, native backend, evidence layer. |
| `docs/capability_boundaries.md` | Capability page embedded older release facts and version chronology. | Replaced with current v2.0-facing capability and boundary page. |
| `docs/public_documentation_map.md` | Documentation map linked older release evidence in normal reading rows and repeated v1.8 wording. | Replaced with v2.0-facing map; older releases routed to legacy note. |
| `docs/rtdl_feature_guide.md` | Feature guide contained long v0.x/v1.x release chronology and goal evidence. | Replaced with current feature guide focused on kernel shape, output contracts, partner columns, and current app families. |
| `docs/app_example_quickstart.md` | Quickstart contained goal-number command detail and generic history routing. | Replaced advanced partner row with tutorial link; routed older evidence to legacy note. |
| `docs/application_catalog.md` | Catalog included v1.8 scope, older goal evidence, v0.x DB/graph language, and historical claim notes. | Replaced with current v2.0-facing app catalog and output guidance. |
| `docs/rtdl/README.md` | Language index tied ITRE and IR text to older version framing. | Updated descriptions to current Python apps and v2.0-facing partner boundary. |
| `docs/rtdl/ir_and_lowering.md` | IR page described v1.8 tightening and v2.0 as future improvement. | Reframed as current engine-boundary and v2.0 partner runtime direction. |
| `docs/rtdl/dsl_reference.md` | API reference included v0.4 contract notes and goal report references. | Removed older-version markers and moved evidence language to report archive wording. |
| `docs/rtdl/itre_app_model.md` | ITRE page was centered on v0.8 app mapping and language-pressure history. | Replaced with current ITRE model including partner-owned output contracts and v2.0 pressure points. |
| `docs/rtdl/workload_cookbook.md` | Cookbook headings and status notes included v0.4 and goal driver details. | Removed older-version headings; kept current recipe semantics and support-matrix boundaries. |
| `docs/tutorials/README.md` | Tutorial ladder described partner tutorials as v2.0/preview in mixed terms. | Normalized wording to current partner-owned column path. |
| `docs/tutorials/partner_anyhit.md` | Partner tutorial said v2.0 remained blocked on technical evidence now superseded by later work. | Reframed as conservative Embree partner path and current consensus-gate boundary. |
| `docs/tutorials/partner_optix_zero_copy_anyhit.md` | Tutorial was evidence/report-like with goal IDs and artifact names in the learner path. | Replaced with current OptiX partner-column tutorial and clean claim boundary. |
| `docs/release_reports/v2_0_pre_release_candidate.md` | Needed a clean learner-facing status page without goal-number naming. | Added concise v2.0 pre-release candidate note and pointed audit detail to release-report archive. |
| `docs/release_reports/v2_0_pre_release_candidate_after_goal2086.md` | Existing audit-detail report is appropriate for release reports, not learner path. | Left as historical/audit detail; learner docs now link to the clean alias page. |
| `docs/history/legacy_learner_doc_version_notes.md` | No single parking page existed for older learner-doc version context. | Added a dedicated legacy note that points older-release readers to history and release-report archives. |

## Validation

The focused learner/user doc set was scanned for older-version and goal-number
markers:

- `v0.`
- `v1.`
- `v0_`
- `v1_`
- `released v...`
- `current released`
- `Goal123` / `Goal 123`

The scan is expected to be clean for the learner/user target set. Release
reports, benchmark reports, reviews, and history archives are intentionally not
part of that learner-path scan.

