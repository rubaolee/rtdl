# Goal599: v0.9.2 Apple RT Public Doc Refresh

Date: 2026-04-19

Status: ACCEPTED with Codex + Gemini doc consensus

## Goal

Refresh public-facing RTDL docs after the v0.9.2 Apple RT performance work so new users see a coherent Apple RT story:

- `v0.9.1` remains the current released Apple closest-hit slice.
- Current `main` carries v0.9.2 candidate Apple RT full-surface dispatch and native-slice performance work.
- Apple RT is real Apple Metal/MPS RT for the native slices.
- Apple RT still is not a broad backend-maturity or speedup claim.

## Files Updated

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`

## Content Changes

The refresh replaces stale post-`v0.9.1` language with current v0.9.2 candidate wording:

- Goal582: all 18 predicates are callable through `run_apple_rt`.
- Native Apple MPS RT slices are 3D closest-hit, 3D hit-count, and 2D segment-intersection.
- Non-native predicates remain explicit `cpu_reference_compat` paths.
- Goal596: prepared Apple RT closest-hit reuse exists for repeated closest-hit queries.
- Goal597: 3D hit-count now uses masked chunked nearest-hit traversal.
- Goal598: 2D segment-intersection now uses masked chunked nearest-hit traversal plus analytic refinement.

The refresh also updates the performance honesty boundary:

- Apple RT segment-intersection improved locally from 0.092515083 s to 0.031314438 s on the dense 128x128 fixture.
- The same segment fixture remains about 4.17x slower than Embree.
- Hit-count remains slower than Embree.
- Closest-hit timing in the repeatable harness can be unstable and is not public speedup wording.
- Embree remains the only backend RTDL currently describes as broadly mature/optimized.

## Audits Run

Stale phrase audit:

```bash
rg -n 'post-`v0\.9\.1`|post-v0\.9\.1|native_mps_rt_3d_else_cpu_reference_compat|currently unoptimized|no prepared Apple RT reuse' \
  README.md docs/README.md docs/release_facing_examples.md docs/tutorials/README.md \
  docs/rtdl_feature_guide.md docs/backend_maturity.md docs/quick_tutorial.md \
  examples/README.md docs/current_architecture.md docs/capability_boundaries.md \
  docs/release_reports/v0_9/support_matrix.md
```

Result:

```text
no matches
```

Public doc smoke audit:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal512_public_doc_smoke_audit_test -v
```

Result:

```text
Ran 3 tests in 0.006s
OK
```

Whitespace audit:

```bash
git diff --check
```

Result:

```text
pass
```

## External Review

Gemini external doc review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal599_external_doc_review_2026-04-19.md`
- Verdict: ACCEPT

## Codex Verdict

ACCEPT. The public docs now present v0.9.2 Apple RT as useful and actively improving for Apple developers while preserving the release and performance honesty boundaries.
