# Goal1458 v1.5.2 Public Docs Link Proposal

## Verdict

Proposal drafted for external review only. No public docs links are added by
this file.

## Background

Goal1457 accepted the v1.5.2 release-surface candidate docs as a reviewed,
unlinked candidate package. The next decision is whether the public
documentation spine may link to that package while preserving the same cautious
claim boundary.

## Proposed Link Locations

If and only if the public-docs-link review accepts, the smallest public-docs
change would be:

- In `README.md`, add `v1.5.2 Prepared Host-Output Candidate Docs` immediately
  after the existing `v1.5.1 COLLECT_K_BOUNDED Candidate Docs` link.
- In `README.md` Current Status, add one bounded row for v1.5.2 prepared
  host-output candidate docs.
- In `docs/README.md` New User Path, add
  `v1.5.2 Prepared Host-Output Candidate Docs` immediately after the existing
  v1.5.1 candidate-doc entry.
- In `docs/README.md` Release Packages, add the same v1.5.2 package link after
  v1.5.1.
- In `docs/README.md` Current Boundary, add one sentence saying v1.5.2 remains
  an experimental prepared host-output evidence candidate, not a stable
  primitive promotion.

## Required Link Wording

Use this exact label if accepted:

```text
v1.5.2 Prepared Host-Output Candidate Docs
```

Use this exact status wording if accepted:

```text
v1.5.2 candidate docs record reviewed prepared host-output evidence for
COLLECT_K_BOUNDED; still no prepared-buffer reuse claim, no public speedup
wording, no zero-copy wording, no whole-app claims, no stable primitive
promotion, and no release tag action.
```

## Still Blocked

- Do not call v1.5.2 released.
- Do not create, move, or publish a release tag.
- Do not claim prepared-buffer reuse is proven.
- Do not claim true zero-copy.
- Do not claim public speedup.
- Do not claim whole-app speedup.
- Do not promote `COLLECT_K_BOUNDED` to stable.

## Review Question

May the public docs spine add the proposed links and exact bounded status
wording, or should v1.5.2 remain unlinked until more evidence exists?
