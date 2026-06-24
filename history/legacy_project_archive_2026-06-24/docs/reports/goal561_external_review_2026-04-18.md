# Goal 561 External Review: v0.9 Public Docs Refresh

Date: 2026-04-18

Reviewer: Claude Sonnet 4.6 (external review pass)

## Verdict

ACCEPT

## Files Reviewed

- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `docs/capability_boundaries.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- `docs/tutorials/README.md`
- `examples/README.md`
- `docs/release_reports/v0_9/support_matrix.md`

## Summary

All reviewed public-facing documents now consistently and honestly describe the
v0.9 HIPRT candidate state. The specific patterns checked:

### Stale one-workload-preview language

None found. No document describes HIPRT as a narrow single-workload preview or
as limited only to 3D ray/triangle. The former "preview" and "one workload only"
framing is absent from all reviewed files.

### Accurate 18-workload matrix description

Every document that mentions the current HIPRT scope states that `run_hiprt`
covers the 18-workload Linux parity matrix. All nine public docs and the v0.9
support matrix are consistent on this count. The support matrix itself lists
all 18 workloads explicitly.

### `prepare_hiprt` boundary

All references to `prepare_hiprt` correctly describe it as currently limited to
the prepared 3D `ray_triangle_hit_count` path. No document claims broader
prepared HIPRT coverage. The distinction between `run_hiprt` (broad 18-workload)
and `prepare_hiprt` (narrow 3D prepared path) is stated consistently.

### Non-claims

All documents reviewed carry the correct set of explicit non-claims:

- no AMD GPU validation
- no RT-core speedup claim from the tested GTX 1070 path
- no HIPRT CPU fallback
- no released `v0.9.0` claim before the full pre-release test/doc/audit gate

These appear in `README.md`, `docs/current_architecture.md`,
`docs/capability_boundaries.md`, `docs/rtdl_feature_guide.md`,
`docs/release_facing_examples.md`, and the v0.9 support matrix.

### Release claim boundary

No document claims HIPRT is already released as `v0.9.0`. The consistent
language is "active `v0.9` candidate" or "active v0.9 HIPRT candidate." The
v0.9 support matrix is correctly titled as a candidate package, not a release
package.

### v0.9 candidate package

The new `docs/release_reports/v0_9/support_matrix.md` is correctly scoped. It
states the current candidate evidence (18 workloads, 72 parity checks, 0
failures), documents the validated platform, carries all required non-claims,
and links to the accepted Goal 560 evidence artifacts.

## Minor Observation (Non-Blocking)

`docs/release_facing_examples.md` line 72 uses the phrase "optional experimental
HIPRT build" in a setup-command note. The word "experimental" here describes the
optional nature of the build step rather than the old "Experimental HIPRT"
preview framing that was removed. It does not contradict the "active v0.9
candidate" language used consistently elsewhere in the same file, and it does
not constitute a stale claim or release overclaim. No change required.

## Conclusion

The public documentation refresh is accurate and consistent. The docs now
reflect the current honest state of the v0.9 HIPRT candidate: `run_hiprt` Linux
parity across 18 workloads, `prepare_hiprt` limited to the prepared 3D
ray/triangle path, no AMD GPU validation, no RT-core speedup, no CPU fallback,
and no released v0.9.0 claim. The goal is accepted.
