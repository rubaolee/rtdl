# Goal591 Post-Goal590 Release State Audit

Date: 2026-04-19

Status: ACCEPTED with Claude + Gemini review consensus

## Scope

This audit closes the immediate post-Goal590 state after adding native Apple
Metal/MPS 2D `segment_intersection` and documenting backend maturity.

Checked public-facing files:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_1/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_1/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_1/support_matrix.md`

## Worktree Hygiene

Adaptive Goal589 WIP was parked before this audit:

- Hold decision committed in `/Users/rl2025/rtdl_python_only/docs/reports/goal589_adaptive_engine_hold_2026-04-19.md`
- Local stash: `stash@{0}: On main: goal589 adaptive fixed-radius WIP held 2026-04-19`

This keeps adaptive-engine work out of the Apple/backend-maturity release path.

## Documentation Findings

The first audit pass found stale root README wording:

- post-`v0.9.1` Apple native coverage listed only 3D closest-hit and 3D
  hit-count
- 2D `segment_intersection` was still implied to be compatibility-only
- backend maturity was not linked from the front page

Repairs made:

- `/Users/rl2025/rtdl_python_only/README.md` now states that 3D
  `ray_triangle_closest_hit`, 3D `ray_triangle_hit_count`, and 2D
  `segment_intersection` are native Apple Metal/MPS RT paths on current main.
- `/Users/rl2025/rtdl_python_only/README.md` links
  `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`.
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`
  now keeps the released `v0.9.1` scope intact while adding a post-`v0.9.1`
  mainline addendum for Goals 582, 583, and 590.

No change was made to the frozen `v0.9.1` release-package scope: it remains a
released closest-hit slice. Post-release Apple expansions are documented as
mainline addenda, not retroactive release claims.

## Test Evidence

Focused Apple gate:

```bash
make build-apple-rt && PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 9 tests
OK
```

Broad local unittest discovery:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 239 tests in 67.629s
OK
```

Mechanical whitespace check:

```bash
git diff --check
```

Result: no output.

## Current Honest State

- Embree is the only backend currently described as optimized/mature.
- OptiX, Vulkan, HIPRT, and Apple Metal/MPS RT are real implemented backends
  with bounded correctness evidence, but not broad optimized-backend claims.
- Apple Metal/MPS RT is native and correctness-validated for:
  - 3D `ray_triangle_closest_hit`
  - 3D `ray_triangle_hit_count`
  - 2D `segment_intersection`
- Apple Metal/MPS RT remains unoptimized on local Apple M4 measurements and is
  slower than Embree for the measured native slices.
- Adaptive native engine work is parked and not release evidence.

## Verdict

No release-blocking code, doc, or flow problem was found in this local audit.
External AI review is still required before calling Goal591 closed.

## Review Consensus

External review artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal591_claude_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal591_gemini_flash_review_2026-04-19.md`

Both reviews returned `ACCEPT`. Claude noted one stale root README line that
still listed `v0.9.0` as the current release in the "Current Release State"
section; it was corrected to `v0.9.1`, with a post-`v0.9.1` Apple RT mainline
addendum.
