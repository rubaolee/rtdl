# Goal 654: External Review Verdict

Date: 2026-04-20

Verdict: **ACCEPT**

## Scope

Review of:

- `docs/current_main_support_matrix.md`
- Public entry-point links in `README.md`, `docs/README.md`,
  `docs/current_architecture.md`, `docs/backend_maturity.md`
- Test file `tests/goal654_current_main_support_matrix_test.py`
- Evidence record in `docs/reports/goal654_current_main_support_matrix_2026-04-20.md`

## Release Boundary Separation

The matrix correctly separates released `v0.9.5` claims from post-release
current-`main` work in three ways:

1. The **Boundary** section states the release boundary explicitly, names
   current-main native Vulkan and Apple RT any-hit as post-release additions,
   and requires backend library rebuilds before those paths are available.
2. The **Any-Hit And Visibility Support** table entries for Vulkan, Apple RT 2D,
   and Apple RT 3D record capabilities that exist only on current `main`, not at
   the released `v0.9.5` tag.
3. The **Non-Claims** section explicitly rejects retroactive native Vulkan or
   Apple any-hit support at the released `v0.9.5` tag boundary.

The separation is unambiguous. No current-main capability is presented as a
`v0.9.5` release claim.

## Apple / HIPRT / reduce_rows Honesty Boundaries

All required honesty boundaries are present and correctly phrased:

| Boundary | Location in matrix |
| --- | --- |
| Apple RT any-hit is not programmable shader-level Apple any-hit | Implementation notes + Non-Claims |
| Apple MPS ray-tracing hardware not used for DB or graph workloads | Non-Claims |
| AMD GPU validation not claimed for HIPRT | Non-Claims |
| HIPRT CPU fallback not claimed | Non-Claims |
| RT-core speedup from GTX 1070 Linux evidence not claimed | Non-Claims |
| `reduce_rows` is a Python standard-library helper, not native backend reduction | Implementation notes + Non-Claims |
| No broad speedup claim across all engines | Non-Claims |

The Apple 2D any-hit description (MPS-prism traversal with per-ray mask
early-exit plus exact 2D acceptance) and the Apple 3D any-hit description (MPS
RT nearest-intersection existence) are consistent across the matrix, `README.md`,
`docs/current_architecture.md`, and `docs/backend_maturity.md`.

## Public Link Coverage

All four required entry points link to `current_main_support_matrix.md`:

- `README.md`: linked in the "For exact status" block and again in the
  "Current Release State" block.
- `docs/README.md`: linked in the New User Path ordered list and in the
  Live Documentation section.
- `docs/current_architecture.md`: linked in the "For exact release claims"
  block.
- `docs/backend_maturity.md`: linked in the "Implemented But Bounded" section.

The test `test_public_entry_points_link_current_main_matrix` mechanically
verifies all four paths.

## Test and Audit Evidence

The Goal654 evidence record reports:

- 10 unit tests passing (Goal654 + Goal646 front-page consistency + Goal512
  doc smoke audit) with no failures.
- Command-truth audit: 248 commands across 14 public docs, `valid: true`.
- `git diff --check`: clean.

The test file confirms four test methods covering: (1) release boundary
markers, (2) native any-hit backend phrases for all six backends, (3) all
honesty-boundary phrases, and (4) public entry-point link presence. These tests
are direct substring checks against the live files, making them reliable
regression guards against accidental reversion.

## Minor Observations (Non-Blocking)

- The `visibility_rows(..., backend=...)` table cell reads
  `"supported through \`backend="cpu"\`"` for the CPU column. This is
  accurate: `visibility_rows_cpu` is the CPU-reference form while
  `visibility_rows(...)` dispatches through any-hit. No change required.
- Evidence links in the matrix (Goals650-653) are relative paths within `docs/`.
  Their presence on disk is expected from the evidence record but was not
  independently verified here. The Goal654 report records those goals as the
  source of any-hit backend evidence.

## Summary

The matrix correctly positions current-`main` improvements as post-release
additions, preserves every required Apple/HIPRT/reduce_rows honesty boundary,
is linked from all required public entry points, and is backed by passing unit
tests and a valid command-truth audit. No factual errors or missing non-claims
were found.

Verdict: **ACCEPT**
