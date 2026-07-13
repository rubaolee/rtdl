# Call For Review: Goal5087 Unified Paper-App Skeleton

Date: 2026-07-07

## Requested Verdict Label

```text
approve_goal5087_unified_paper_app_skeleton
```

## Review Scope

Please review:

```text
history/internal_docs/goal5087_unified_paper_app_skeleton_result_2026-07-07.md
Paper-reproduction-apps/README.md
Paper-reproduction-apps/PAPER_APP_TEMPLATE.md
Paper-reproduction-apps/paper_app_manifest.schema.json
```

## Context

v2.14.5 is generalizing from two paper apps:

- RayJoin
- RT-BarnesHut

Goal5085 created a shared public status model. Goal5086 audited the public RTDL
API surface. Goal5087 adds a repeatable paper-app template and manifest schema
so future paper apps declare their RTDL surface, app-owned assets, reproduction
scope, performance regime, and forbidden claims up front.

## Review Questions

1. Does the template capture the right minimum directory structure for future
   paper apps without forcing a disruptive rewrite of existing apps?
2. Does the template require a clear separation between RTDL public APIs and
   app-owned paper-specific code?
3. Does the manifest schema capture reproduction scope, comparator policy,
   input policy, output policy, and performance regime?
4. Does the schema make forbidden broader claims explicit enough to prevent
   accidental overclaiming?
5. Does the README update present the template as a reader-facing contract,
   not as a runtime input format?
6. Does this goal avoid promoting experimental APIs, app comparators, or output
   formatting into RTDL core?
7. Is Goal5088, third validation candidate selection, the right next step?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 7 review questions
