# Goal 475: v0.7 External Input Manifest

Date opened: 2026-04-16

## Objective

Create a current external-input manifest for the v0.7 line so external reviews,
test reports, preserved tester reports, research source papers, and validation
artifacts are indexed from one place.

## Scope

- Index user-provided source-paper PDFs used for v0.7 scope decisions.
- Index preserved external tester reports.
- Index Claude/Gemini/external-style AI reviews for v0.7 goals.
- Index test/performance/audit result artifacts for v0.7 validation.
- Verify the Goal 439 external tester intake ledger still contains T439-001
  through T439-012.
- Obtain 2-AI consensus before closure.

## Non-Goals

- Do not stage, commit, tag, push, merge, or release.
- Do not copy external PDFs into the repo.
- Do not reinterpret external reports beyond their accepted goal boundaries.

## Acceptance Criteria

- `scripts/goal475_external_input_manifest.py` runs successfully.
- Generated JSON and CSV manifests exist.
- The manifest reports no missing paths and no Goal 439 ledger gaps.
- At least one Claude or Gemini review accepts the manifest.
