# Goal 577: v0.9.0 Release Action

Date: 2026-04-18
Status: accepted for release commit and tag action

## User Authorization

The user authorized the release action with:

```text
GO
```

This goal converts the accepted v0.9 release candidate into the `v0.9.0`
release after the documented test, doc, audit, and consensus gates.

## Preconditions Checked

- current branch: `main`
- latest released tag before this action: `v0.8.0`
- no existing `v0.9.0` tag was present before the release action
- Goal575 final v0.9 gate: accepted
- Goal576 archive-link audit: accepted as non-blocking archive debt
- current public v0.9 docs pass focused stale-wording and link checks

## Release Conversion

The release-facing docs and metadata were converted from candidate wording to
release wording:

- `/Users/rl2025/rtdl_python_only/VERSION` now says `v0.9.0`
- `/Users/rl2025/rtdl_python_only/README.md` now states current released
  version is `v0.9.0`
- `/Users/rl2025/rtdl_python_only/docs/README.md` now points users to the v0.9
  support matrix and release package
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md` now
  records a released `v0.9.0` package
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`
  now records status as released as `v0.9.0`
- live architecture, feature, tutorial, examples, and capability-boundary docs
  now describe HIPRT as released under the v0.9 support matrix rather than as
  an unreleased candidate

Historical Goal reports and pre-release report names remain unchanged because
they are evidence artifacts from the time they were written.

## Final Validation

Local full unit discovery:

```text
python3 -m unittest discover -s tests
Ran 239 tests in 61.735s
OK
```

Focused release-facing doc audit:

```json
{
  "valid": true,
  "stale_hits": [],
  "missing_links": []
}
```

Whitespace check:

```text
git diff --check
pass
```

## Release Boundary

The `v0.9.0` release claim is:

RTDL v0.9.0 releases HIPRT `run_hiprt` parity coverage for the accepted
18-workload Linux matrix, prepared HIPRT reuse evidence for selected repeated
query paths, and exact bounded RTXRMQ-style closest-hit support on CPU
reference, `run_cpu`, and Embree.

The `v0.9.0` release claim does not say:

- HIPRT is AMD-GPU validated
- HIPRT has a CPU fallback
- GTX 1070 timings prove RT-core speedup
- OptiX, Vulkan, or HIPRT support `ray_triangle_closest_hit`
- RTDL is a renderer, DBMS, arbitrary SQL engine, arbitrary workload compiler,
  or universal performance-speedup system

## Tag Plan

After this report receives the required review trail, create a release commit
and annotated tag `v0.9.0`, then push `main` and the tag.
