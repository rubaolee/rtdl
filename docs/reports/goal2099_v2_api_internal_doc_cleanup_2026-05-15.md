# Goal2099 v2 API And Internal Doc Cleanup

Status: complete.

Purpose: apply the v2.0 single-version learner-doc rule to API, feature, and
internal architecture docs. Active docs now describe the current v2.0
pre-release candidate surface only. Older API/internal material was moved to an
archive area or reduced to current-facing links.

## File-by-File Findings And Operations

| File | Finding | Operation |
| --- | --- | --- |
| `README.md` | Needed current API/support links after matrix cleanup. | Added direct links to the engine feature contract and app engine matrix, and retitled the archive link. |
| `docs/README.md` | History/audit section still used old-facing wording and had a duplicate report link. | Rephrased archive wording and removed the duplicate report link. |
| `docs/backend_maturity.md` | Mixed current backend guidance with old release timing and backend history. | Rewritten as a current v2.0 backend maturity page with Embree/OptiX release focus and partner boundaries. |
| `docs/current_main_support_matrix.md` | Mixed the current matrix with many older release boundaries and report links. | Rewritten as a compact v2.0 current support matrix and non-claim guide. |
| `docs/app_engine_support_matrix.md` | Current app table was buried in old release, readiness, and wording history. | Rewritten around the machine-readable app matrix plus concise v2.0 reading rules. |
| `docs/runtime_overhead_architecture.md` | Described early host-path overhead goals as if they were current architecture. | Rewritten as a current v2.0 overhead model: rows, compact summaries, streaming witness pages, and partner continuation. |
| `docs/features/README.md` | Indexed current features while also teaching old release chronology. | Rewritten as a v2.0 feature-home index and reading order. |
| `docs/features/engine_support_matrix.md` | Status line referenced an old release boundary. | Updated status to current v2.0 pre-release candidate. |
| `docs/features/db_workloads/README.md` | Presented old DB benchmark reports as current user evidence. | Reframed DB workloads around current columnar payload support and moved old comparisons to archive context. |
| `docs/features/fixed_radius_neighbors/README.md` | Status line used old version language. | Updated to current v2.0 workload-line wording. |
| `docs/features/knn_rows/README.md` | Status line used old version language. | Updated to current v2.0 workload-line wording. |
| `docs/features/lsi/README.md` | Linked an old goal report from the active feature page. | Replaced with current engine support contract link. |
| `docs/features/pip/README.md` | Taught old trust-anchor context in the active feature page. | Replaced with current support/performance matrix guidance. |
| `docs/features/polygon_pair_overlap_area_rows/README.md` | Linked old PostGIS/report artifacts and old bounded-claim wording. | Replaced with current support/app links and current claim wording. |
| `docs/features/polygon_set_jaccard/README.md` | Linked old SQL/report artifacts in the active page. | Replaced with current support/app links. |
| `docs/features/ray_tri_anyhit/README.md` | Status note named an old release. | Rephrased as current-source behavior. |
| `docs/features/ray_tri_hitcount/README.md` | Described the feature relative to an old workload-growth line. | Rephrased as current feature scope. |
| `docs/features/reduce_rows/README.md` | Section heading and text named an old release. | Rephrased as current scalar reduction primitives. |
| `docs/features/segment_polygon_anyhit_rows/README.md` | Linked old SQL and named old goal artifacts in active user guidance. | Replaced with current support link and current artifact-coverage wording. |
| `docs/features/segment_polygon_hitcount/README.md` | Linked old SQL and named old goal artifacts in active user guidance. | Replaced with current support link and current bounded traversal wording. |
| `docs/features/visibility_rows/README.md` | Described helper availability by old release. | Rephrased as current helper behavior. |
| `docs/rtdl/dsl_reference.md` | Included compatibility spelling guidance in the main syntax contract. | Removed old spelling from the learner-facing contract. |
| `docs/rtdl/itre_app_model.md` | Linked archive context with old-facing label text. | Retargeted link label to neutral version archive notes. |
| `docs/rtdl/llm_authoring_guide.md` | Still described the implemented surface as an old preview. | Updated to current v2.0 support wording. |
| `docs/rtdl/workload_cookbook.md` | Mentioned historical validation drivers in active learner guidance. | Rephrased as outside the active learner path. |
| `docs/current_architecture.md` | Linked archive context with old-facing label text. | Retargeted link label to neutral version archive notes. |
| `docs/architecture_api_performance_overview.md` | Entire file was an old architecture/performance overview. | Moved to `docs/history/legacy_api_internal_docs/architecture_api_performance_overview.md`. |
| `docs/rtdl/minimal_itre_extension_demo_kernels.md` | Internal proposal sketch, not current RTDL API reference. | Moved to `docs/history/legacy_api_internal_docs/minimal_itre_extension_demo_kernels.md`. |
| `docs/wiki_drafts/*` | Preserved old wiki drafts lived in an active docs directory. | Moved to `docs/history/legacy_api_internal_docs/wiki_drafts/`. |
| `docs/history/legacy_api_internal_docs/README.md` | No archive landing page existed for moved API/internal material. | Added an archive index and current-doc pointers. |
| `docs/history/version_archive_notes.md` | Active docs needed a neutral archive link target. | Added a neutral version archive pointer while preserving older note files for audit compatibility. |

## Regression Gate

`tests/goal2099_v2_api_internal_doc_cleanup_test.py` scans the active API,
feature, architecture, and internal RTDL doc set for old release markers, old
goal references, and old-history labels. It also verifies that the archived
API/internal files are no longer in the active doc paths.

## Boundary

This cleanup changes documentation organization and wording only. It does not
authorize the v2.0 release. The final release still requires the required
external consensus gate.
