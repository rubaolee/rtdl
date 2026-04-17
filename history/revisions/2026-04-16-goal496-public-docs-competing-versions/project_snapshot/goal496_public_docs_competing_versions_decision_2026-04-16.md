# Goal 496: Public Docs Competing-Version Decision Report

Date: 2026-04-16

Goal: review public docs that real users see and choose, for each doc class, the
version that best makes RTDL useful, attractive, comprehensive, and aligned with
the authoring goal of roughly 10x less burden for writing modern ray-tracing
workloads.

## Decision Rule

Two competing versions were considered for each public surface:

- Version A: status-first release bookkeeping. This version emphasizes exact
  release state, backend status, goal history, and audit evidence.
- Version B: user-value-first product documentation. This version first
  explains why RTDL helps: one compact kernel shape, backend-specific traversal
  plumbing hidden by RTDL, and Python kept as a thin application layer.

The selected rule is:

- public front doors use Version B first, with Version A boundaries preserved
  nearby
- release reports and support matrices remain Version A because users need
  precise bounded claims there
- historical docs remain explicitly historical rather than being rewritten as
  current architecture

## File Decisions

| Public file or surface | Version A candidate | Version B candidate | Choice | Reason |
| --- | --- | --- | --- | --- |
| `README.md` | Accurate release/status front page | Stronger front page explaining 10x authoring-burden reduction and the kernel mental model | B | First-time users need the product reason before the release ledger |
| `docs/README.md` | Index by document category | Guided evaluation path with current architecture, quick tutorial, examples, and exact support matrix | B | Reduces onboarding search cost and points to exact boundaries |
| `docs/current_architecture.md` | Reuse historical architecture overview | New current architecture page for live v0.7 state | B | Historical architecture was stale by design; a current public architecture entry is clearer |
| `docs/quick_tutorial.md` | First-run commands and kernel anatomy | First-run commands plus explicit "what plumbing you avoid writing" | B | Tutorial should teach the burden-reduction model immediately |
| `docs/tutorials/README.md` | Tutorial ladder only | Tutorial ladder framed around one kernel shape and backend reuse | B | Better explains why the ladder exists |
| `docs/release_facing_examples.md` | Long release-by-release example list | Add "choose by job" table before detailed commands | B | Users can choose an example by problem before reading all history |
| `examples/README.md` | Flat file list | Add purpose table showing what input data becomes what output data | B | Makes examples navigable from an app-builder perspective |
| `docs/rtdl_feature_guide.md` | Feature inventory | Feature inventory plus practical promise and honesty boundary | B | Keeps the high-level guide useful for evaluators |
| `docs/features/README.md` | Workload home list | Workload-shape chooser plus feature list | B | Users select features by workload shape, not by internal release order |
| `docs/tutorials/db_workloads.md` | Commands and backend boundaries | Add data-to-data table and non-DBMS boundary | B | DB-style workloads need especially clear transformation semantics |
| `docs/tutorials/graph_workloads.md` | Commands and kernels | Add data-to-data table and orchestration boundary | B | Clarifies bounded graph steps versus whole-algorithm host logic |
| `docs/release_reports/v0_7/*` | Exact release/support claims | Product narrative | A | Release package must remain precise and bounded |
| `docs/architecture_api_performance_overview.md` | Historical architecture report | Rewrite as current docs | A retained as historical | Avoids corrupting preserved history; current architecture moved to a new file |

## Applied Public-Doc Changes

- Added a front-page "Why RTDL Is Useful" section to `README.md`.
- Added `docs/current_architecture.md` as the live architecture page.
- Added current architecture links to `README.md` and `docs/README.md`.
- Added a ten-minute evaluation path to `docs/README.md`.
- Added authoring-burden context to `docs/quick_tutorial.md`.
- Added product framing to the tutorial index and feature guide.
- Added choose-by-job and choose-by-workload-shape tables to public example and
  feature surfaces.
- Added data-transformation tables for graph and DB tutorials.

## Honesty Boundary

The new wording treats "10x reduction" as an authoring-burden target, not as a
universal runtime performance claim. Runtime performance remains bounded by the
release reports, Linux evidence, backend availability, and workload-specific
support matrices.

## Verdict

The better public-doc version is Version B for front-page/tutorial/example/
architecture surfaces, with Version A retained for release reports, support
matrices, and historical audit material.
