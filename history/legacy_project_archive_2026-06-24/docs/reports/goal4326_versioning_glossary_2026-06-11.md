# Goal4326: Versioning Glossary

Date: 2026-06-11

## Verdict

`accept-with-boundary` for a Fable5 F10 clarity slice.

Goal4326 adds a short versioning glossary for version markers and historical
contract names. It explains why the current public source-tree surface is v2.10,
why active v2.11 reports may exist, why some Python constants still carry
`v2_8` lineage names, and why goal numbers are not product versions.

## What Changed

- Added `docs/versioning.md`.
- Linked it from `README.md`, `docs/README.md`, and `docs/learn/README.md`.
- Added `tests/goal4326_versioning_glossary_test.py`.

## Boundary

Goal4326 does not authorize any new release or public claim surface.

Goal4326 does not bump `VERSION`, create or move a tag, authorize a release,
authorize public speedup wording, authorize broad RT-core wording, authorize
package-install wording, authorize true-zero-copy wording, authorize automatic
partner selection, or authorize app-specific native-engine logic.

This is a reader-orientation cleanup only.

## Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4326_versioning_glossary_test tests.goal4248_current_public_docs_claim_boundary_scan_test
```

Observed result: 9 tests passed. The current public-doc scan includes
`docs/versioning.md`, scans 36 files, and reports zero hard blockers.
