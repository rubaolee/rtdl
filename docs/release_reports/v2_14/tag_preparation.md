# RTDL v2.14 Tag Preparation

Status: tag checklist completed for source-tree tag `v2.14`.

Intended tag: `v2.14`

## Completed Before Tagging

- `VERSION` is updated to `v2.14`.
- `pyproject.toml` project version is updated consistently.
- The v2.14 benchmark-app boost packet is complete.
- Fresh current-head pod evidence is collected.
- Public wording packet has zero unexplained rows.
- External reviews accept the release boundary, including Goal4390 Claude
  `accept-with-boundary` with required fixes applied.
- The v2.13 bridge addendum is visible so readers understand what v2.14
  supersedes.
- Maintainer explicitly authorizes publication and tagging.

## Current Gate

Local Windows focused gate: 59 tests OK.

Pod Linux focused gate: 59 tests OK.

## Tag Command

```bash
git tag -a v2.14 -m "RTDL v2.14 benchmark cleanup and row-scoped comparison release"
```
