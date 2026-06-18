# RTDL v3.0.2 Release Requirements Trace

Status: release-process trace for `v3.0.2`.

This file records how v3.0.2 inherits the V3.0 major-release requirements and
adds the patch-release requirement that V4 preparatory material stays out of
the current user front door.

## Older Requirements Found

| Source | Requirement pattern | V3.0 response |
| --- | --- | --- |
| `docs/history/release_reports/v1_0/README.md` | Current version named, release package, support matrix, audit/report links, release gate state. | V3.0.2 package names `v3.0.2`, includes support matrix, evidence links, gates, and closeout. |
| `docs/history/release_reports/v1_0/release_statement.md` | Clear allowed claims and must-not-claim section. | V3.0 release statement separates allowed claims from blocked wording. |
| `docs/history/release_reports/v1_0/tag_preparation.md` | Final authorization, version marker update, tag commands, boundary. | V3.0 tag preparation records authorization, version update, commands, and boundary. |
| `docs/history/release_reports/v2_0/README.md` | Source-tree major release statement, evidence list, smoke commands, release boundary. | V3.0 README keeps the same shape and updates evidence to Goal4536/4538/4614. |
| `docs/history/release_reports/v2_14/README.md` | Planned documents, gates, row-scoped thesis, non-claims. | V3.0 includes a larger release packet and keeps row-scoped performance wording. |
| `docs/history/release_reports/v2_14/publication.md` | Checklist before publication and blocked wording. | V3.0 publication note records the checklist and blocked wording. |
| `docs/history/release_reports/v2_14/final_closeout.md` | Final verdict, completed steps, verification, transition rule. | V3.0 final closeout records verdict, steps, verification threshold, and V4 transition rule. |

## V3.0.2 Release Checklist

- [x] Release package exists under `docs/release_reports/v3_0_2/`.
- [x] Release statement is concise and claim-bounded.
- [x] Support matrix explains programming surfaces, app routes, engines, and
  non-claims.
- [x] Public wording boundaries are locked.
- [x] Publication note records authorization and current gates.
- [x] Tag preparation records version update and tag commands.
- [x] Final closeout records completed work and V4 deferrals.
- [x] Front page and docs index point to V3.0.2.
- [x] Current claim-boundary pages are polished for V3.0.2.
- [x] Source-tree doctor validates the V3.0.2 release package.
- [x] V4 preparatory embedding/C ABI/SDK/zero-copy artifacts are excluded from
  V3.0.2 release criteria and validated separately by `v4_prep`.

## Release Principle

Patch releases can be useful without widening scope. V3.0.2 keeps V3.0 proud
and bounded: it preserves the current route matrix and user-facing source-tree
story while preventing scope drift into embedding, packaging, SDK, zero-copy,
generated-binding, external-runtime, or paper-reproduction claims.
