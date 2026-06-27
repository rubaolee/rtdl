# Goal 576: v0.9 Archive Link Audit

Date: 2026-04-18

## Verdict

ACCEPT as non-blocking archive debt. The current public v0.9 docs pass the
focused release-facing audit. The broader all-Markdown audit found historical
link misses in archived handoff, archived goal, and old review/report files.

## Why This Goal Exists

After Goal 575, the release-facing docs were clean, but a broader audit across
all Markdown files was run to check whether old history and handoff material
still had navigable links after the repository's history/archive moves.

## Current Public Doc Audit

The focused release-facing audit checks:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal575_v0_9_final_release_gate_after_closest_hit_2026-04-18.md`

Result:

```json
{
  "valid": true,
  "stale_hits": [],
  "missing_links": []
}
```

## Broad Archive Link Audit

The broader audit checked `2534` Markdown files under:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs`
- `/Users/rl2025/rtdl_python_only/examples`

Result:

- missing links: `84`
- misses with basename candidates in the repo: `82`

Representative classes:

- old handoff files linking to root-level `docs/goal_*.md` files that now live
  under `/Users/rl2025/rtdl_python_only/docs/history/goals/archive`
- archived goal files with relative links that were correct before the archive
  move but now resolve from the archive directory
- old external review/report files linking to historic paths, generated build
  artifacts, or local PDFs

## Release Judgment

This is not a v0.9 release blocker because:

- current public entry points and v0.9 release-facing docs pass link and stale
  wording checks
- the 84 misses are not on the public v0.9 user path
- old review and handoff files are evidence artifacts, not live tutorials or
  user-facing setup instructions
- mechanically rewriting old evidence artifacts may make history appear cleaner
  than it was at the time of writing

## Follow-Up

Recommended post-release or v0.10 maintenance:

- create an archive-link-normalization script that rewrites only links with a
  unique basename match and records every rewrite
- leave links to deleted/generated artifacts as explicit historical references
  unless the original artifact is restored
- keep the focused public-doc audit as the release gate for user-facing docs
