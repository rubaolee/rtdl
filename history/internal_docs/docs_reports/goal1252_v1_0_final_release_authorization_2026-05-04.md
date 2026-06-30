# Goal1252 v1.0 Final Release Authorization

Date: 2026-05-04

## Decision

VERDICT: AUTHORIZE RELEASE ACTION

RTDL `v1.0` is authorized for the release action: update the live version
marker from `v0.9.8` to `v1.0`, convert the v1.0 release package from draft
candidate wording to released wording, commit the release action, and create
the annotated `v1.0` tag after the release-action commit.

## Scope Authorized

This authorization is narrow. It authorizes the v1.0 proof-release surface
already documented and reviewed:

- app-shaped RTDL proof release, not the final v2.0 performance architecture;
- `18` app inventory rows;
- `12` reviewed bounded NVIDIA RTX public wording rows;
- blocked public speedup wording remains blocked for `graph_analytics` and
  `polygon_pair_overlap_area_rows`;
- not-reviewed public speedup wording remains not reviewed for
  `database_analytics` and `polygon_set_jaccard`;
- Vulkan, HIPRT, and Apple RT remain selected proof surfaces, not new v1.0
  public speedup promotions;
- app-specific native continuations are accepted v1.0 proof machinery and are
  explicitly handed off to v1.5 for generic primitive replacement.

## Evidence

- Goal1248 v1.0 release-candidate package consensus:
  `docs/reports/goal1248_two_ai_v1_0_release_candidate_package_consensus_2026-05-04.md`
- Goal1249 release-candidate audit consensus:
  `docs/reports/goal1249_two_ai_v1_0_release_candidate_audit_consensus_2026-05-04.md`
- Goal1250 release-surface documentation audit consensus:
  `docs/reports/goal1250_two_ai_v1_0_release_surface_doc_audit_consensus_2026-05-04.md`
- Goal1251 full local discovery consensus:
  `docs/reports/goal1251_two_ai_v1_0_full_local_discovery_consensus_2026-05-04.md`
- Full local discovery result:
  `2422` tests run, `196` skipped, `0` failures, `0` errors.

## User Authorization

The user instructed Codex to proceed with the v1.0 release path after the
Goal1251 full-discovery gate. This record converts that instruction into the
repo-local release authorization artifact required before changing `VERSION`
or tagging.

## Explicit Non-Claims

This authorization does not authorize:

- new public speedup wording;
- whole-app speedup wording beyond separately reviewed rows;
- broad all-app NVIDIA RT-core speedup wording;
- claiming that `--backend optix` alone proves RT-core speedup;
- claiming that app-specific native continuations have already been removed;
- claiming v1.0 is the final v2.0 performance system.

## Required Release Action

The release action must:

- update `VERSION` to `v1.0`;
- update live public docs to say the current released version is `v1.0`;
- convert the v1.0 release package from draft candidate to released state;
- preserve all claim boundaries above;
- run focused release-action tests before commit;
- commit the release action before tagging;
- tag only the release-action commit.
