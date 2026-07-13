# Goal5087 Unified Paper-App Skeleton Result

Date: 2026-07-07

## Verdict Label

```text
completed_unified_paper_app_skeleton_and_manifest_contract
```

## Purpose

Goal5087 turns the Goal5085 status model and Goal5086 API-surface audit into a
repeatable paper-app structure.

The goal is to prevent future paper-reproduction work from relying on
conversation-only discipline. Every new paper app should declare:

- the RTDL public APIs it exercises,
- the experimental APIs it touches,
- app-owned assets,
- reproduction scope,
- comparator/input/output policy,
- performance regime,
- forbidden broader claims.

This goal adds documentation and a manifest schema only. It does not alter
RayJoin or RT-BarnesHut runtime behavior.

## Implementation

Added:

```text
Paper-reproduction-apps/PAPER_APP_TEMPLATE.md
Paper-reproduction-apps/paper_app_manifest.schema.json
```

Updated:

```text
Paper-reproduction-apps/README.md
```

## Template Contract

The template requires each paper app README to include:

- Paper and artifact
- RTDL program
- App-owned code
- Reproduction scope
- Performance scope
- Boundary

The required directory shape is:

```text
Paper-reproduction-apps/<paper-name>/
  README.md
  data/
    README.md
    manifest.json
  scripts/
  results/
    README.md
```

Existing apps do not need to be mechanically rearranged in this goal. The
template is a forward contract for new apps and for future cleanup of existing
apps.

## Manifest Schema

The schema requires top-level sections:

```text
paper
rtdl_program
reproduction_scope
boundaries
```

The schema explicitly models:

- `public_apis_exercised`,
- `experimental_apis_exercised`,
- `app_owned_assets`,
- reproduction status,
- comparator/input/output policy,
- performance regimes,
- forbidden claims.

## Claim Boundary

This goal does not:

- claim another paper app has been reproduced,
- validate current RayJoin or RT-BarnesHut performance,
- make experimental APIs release-ready,
- promote app-owned comparator or output logic into RTDL core,
- change public RTDL runtime behavior.

## Verification

Public-surface leak scan across:

```text
Paper-reproduction-apps/README.md
Paper-reproduction-apps/PAPER_APP_TEMPLATE.md
Paper-reproduction-apps/paper_app_manifest.schema.json
Paper-reproduction-apps/rt-barneshut-paper/README.md
src/rtdsl/aggregate_hierarchy.py
src/rtdsl/__init__.py
```

Patterns:

```text
Goal[0-9]+
call_for_review
Antigravity
Claude
Gemini
review debt
verdict
```

Result:

```text
0 matches
```

## Next Recommended Goal

Goal5088 should select the third validation candidate.

Selection should prefer a paper/app that exercises a different RTDL system
surface than RayJoin and RT-BarnesHut, so the next app tests whether v2.14.5 is
generalizing the language rather than deepening one app family.
