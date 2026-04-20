# Goal 645 Claude Review: v0.9.5 Public Release Docs

Date: 2026-04-19
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

No release-blocking documentation, test, or honesty-boundary findings.

## Documents Reviewed

- `docs/reports/goal645_v0_9_5_public_release_docs_and_package_2026-04-19.md`
- `README.md`
- `docs/README.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- `docs/release_reports/v0_9_5/README.md`

## Findings

### Version consistency

All six documents agree: current released version is `v0.9.5`. No stale
`v0.9.4` or "candidate" wording found in public-facing surfaces.

### New surface description consistency

All documents describe the v0.9.5 surface identically:

- `rt.ray_triangle_any_hit(exact=False)` emits `{ray_id, any_hit}` rows.
- `rt.visibility_rows_cpu(...)` / `rt.visibility_rows(..., backend=...)` emit
  `{observer_id, target_id, visible}` rows.
- `rt.reduce_rows(...)` is a deterministic Python standard-library helper over
  emitted rows — not a native backend reduction or speedup claim.

### Backend boundary honesty

All documents consistently and correctly state:

- OptiX, Embree, and HIPRT have native early-exit any-hit implementations.
- Vulkan and Apple RT use compatibility dispatch (hit-count projection to
  `any_hit`); no native early-exit performance claim is made for either.
- `reduce_rows` is explicitly bounded as a Python helper with no backend
  acceleration claim.

No document was found to contradict or soften these boundaries.

### Validation evidence (from prep report)

- 14 public release doc/example tests: OK.
- Truth audit: `valid: true`, 248 commands, 14 public docs.
- Tutorial/example harness: 65 passed, 0 failed, 26 skipped.
- Whitespace audit: clean.
- Stale wording grep: no matches in public docs (only regression test strings
  inside `tests/goal645_v0_9_5_release_package_test.py`).

### Release package completeness

`docs/release_reports/v0_9_5/README.md` is present and links to a full set of
supporting artifacts: release statement, support matrix, audit report, tag
preparation guide, and all goal-level reports. The package index in both
`README.md` and `docs/README.md` correctly links to these v0.9.5 artifacts.

### No overclaiming observed

All performance language is properly bounded. No document claims native
early-exit for Vulkan or Apple RT. The OptiX dense-hit micro-result disclaimer
("encouraging but bounded; there is no broad any-hit speedup claim yet") is
present in README.md and consistent with other documents. `reduce_rows` is
never described as accelerated native computation.

## Release-Blocking Findings

None.

## Summary

The v0.9.5 public release documentation describes a single consistent state
across all reviewed surfaces. Honesty boundaries are correctly stated and do not
contradict each other. Validation evidence is recorded and passes. This package
is clear to tag.
