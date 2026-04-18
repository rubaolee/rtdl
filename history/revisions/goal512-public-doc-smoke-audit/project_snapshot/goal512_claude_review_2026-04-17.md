# Goal 512 External AI Review

Date: 2026-04-17

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **PASS**

## v0.8 Status Wording

The wording guard is correct and complete. The negative checks block both
`"released v0.8"` and `"in-progress \`v0.8\`"`. The positive check requires
`"accepted \`v0.8\` app-building"` to survive in the combined public surface.
The change in `docs/release_facing_examples.md` from "in-progress" to "accepted
`v0.8` app-building line on `main`" uses language that is neither a released
claim nor a stale in-progress claim — it is the right phrase for this stage.

## Goal507 / Goal509 Boundary Guards

The boundary assertions are well-chosen. Requiring `"per-edge hit-count"`,
`"full N-body"`, `"Vulkan is not exposed"`, `"GTX 1070"`, and
`"RT-core hardware speedup"` to survive in the combined text means any future
wording pass that silently softens or removes the honesty guardrails will be
caught. The `release_facing_examples.md` text already carries the correct
per-app boundary language (robot Vulkan rejection, Barnes-Hut partial-app
caveat, Hausdorff app-scoped GPU CLI caveat). The performance-report Markdown
links tie claims to concrete evidence documents.

## Local Markdown Link Resolution

The resolver approach is correct. It strips fragment suffixes before checking
path existence, skips external URLs and pure-fragment anchors, and resolves
relative to each document's own parent directory. Fragment validity within
documents is not checked, but that is an acceptable scope limit for a smoke
audit — broken anchors do not produce 404s for readers reaching the right file.

## Overclaiming Assessment

The public docs do not overclaim. The v0.8 app line is explicitly bounded as
"accepted on `main` over existing RTDL features," not a released version. All
three Goal499 apps carry explicit boundary bullets (what RTDL does not yet
expose, what Goal509 rejected, what timing numbers do and do not cover). No
general GPU CLI claim is made from the Hausdorff-specific backend evidence.

## No Issues Found

The audit scope (10 public docs), the three test methods, and the single wording
fix together form a coherent and sufficient guard. No changes are recommended.
