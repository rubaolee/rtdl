# Goal622: v0.9.4 Version Policy

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash) and explicit user approval.

## Decision

Do not release or tag `v0.9.3` separately.

The next public release target is `v0.9.4`.

## Current Release Facts

Existing public tags:

- `v0.9.0`
- `v0.9.1`

Current released version:

- `v0.9.1`

Current mainline state:

- post-`v0.9.1` Apple RT work is already beyond the earlier `v0.9.2` and
  `v0.9.3` scopes
- `v0.9.2` was a candidate line, not a tagged release
- `v0.9.3` was an internal native-coverage milestone, not a tagged release

## Policy

Treat:

- `v0.9.2` as untagged internal candidate evidence
- `v0.9.3` as untagged internal milestone evidence
- `v0.9.4` as the next public release target

## Why

The current `main` already combines:

- `v0.9.2` Apple RT full-surface compatibility and performance/overhead evidence
- `v0.9.3` expanded Apple MPS RT geometry/native-assisted coverage evidence
- `v0.9.4` Apple Metal compute DB/graph backend expansion work

Releasing `v0.9.3` now would create a stale public version boundary that does
not match the current code. The cleaner release story is one public `v0.9.4`
release after final test, doc, and audit gates.

## Public Documentation Rule

Until `v0.9.4` is authorized and tagged:

- public docs must continue to say the current released version is `v0.9.1`
- public docs may say `v0.9.4` is the next public release target
- public docs must not imply `v0.9.2` or `v0.9.3` were released
- `v0.9.2` and `v0.9.3` reports should be treated as evidence artifacts feeding
  `v0.9.4`

## Files Updated By This Policy Step

- `/Users/rl2025/refresh.md`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`

## Remaining Release-Doc Work

This policy step does not complete the full `v0.9.4` release documentation.

Before release, we still need:

- a `docs/release_reports/v0_9_4/` package
- full public-doc refresh for README, tutorials, examples, architecture, support
  matrix, backend maturity, and capability boundaries
- full macOS/Linux/Windows test gate as applicable
- final audit and external review

## Codex Verdict

Accept this policy as the correct versioning path.

Reason: it preserves truthfulness about tags while avoiding a stale `v0.9.3`
public release boundary.

## External Review

Gemini 2.5 Flash returned:

```text
ACCEPT

Rationale: The policy is honest as it clearly distinguishes untagged internal
milestones from actual releases. It is release-safe by maintaining public
documentation accuracy to `v0.9.1` until the next official `v0.9.4` release,
preventing user confusion.
```
