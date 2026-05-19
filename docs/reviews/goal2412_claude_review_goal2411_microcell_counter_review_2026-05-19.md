# Goal2412 Claude Review: Goal2411 Microcell Counter-Review

Date: 2026-05-19

Reviewer: Claude (external, independent)

Verdict: **accept**

---

## Summary

Codex's counter-review is correct. A radius-sized cell is not clique-safe in 3-D,
and my Goal2409 review missed that gap. The microcell fix at
`microcell_size = radius / sqrt(3)` is mathematically sound. The corrected
Candidate B' should replace the radius-cell version in the implementation
contract without further qualification.

---

## Q1: Is the Same-Cell Disconnection Argument Valid?

Yes. The argument is geometrically exact.

When `cell_size = radius`, the body diagonal of a cubic cell is:

```
sqrt(3) * radius ≈ 1.732 * radius
```

Two points can therefore share a cell while being up to `1.732 * radius` apart,
which exceeds the radius threshold. Codex's concrete example is correct and
minimal:

```
radius = 1.0
p0 = (0.00, 0.00, 0.00)   → cell (0, 0, 0)
p1 = (0.99, 0.99, 0.99)   → cell (0, 0, 0)
distance(p0, p1) = 0.99 * sqrt(3) ≈ 1.714 > 1.0
```

Both points are core (if `min_neighbors = 1`, each is within radius of the
other... wait — they are not within radius of each other — so they would each
need another neighbor in range to be core). Under any `min_neighbors` that
allows both to be core via other cluster members, the fast path that assigns
them the same component label because they share a cell is wrong.

The case generalizes: two dense disconnected subclusters can both fit inside one
radius-sized cell if their internal density is high enough to make every point
core, while the gap between the subclusters exceeds radius. My Goal2409 review
required cross-cell point-pair existence checks but said nothing about
intra-cell connectivity. That was the gap. Codex is right to have flagged it.

---

## Q2: Is the Microcell Fix Sound?

Yes. The fix is geometrically proven.

With `microcell_size = radius / sqrt(3)`, the body diagonal is:

```
sqrt(3) * (radius / sqrt(3)) = radius
```

Any two points inside the same microcell are within distance `radius` of each
other (corner-to-corner is exactly `radius`, interior pairs are strictly less).
The clique-safe invariant holds: assigning all points in a microcell to the same
component node is correct.

The neighbor stencil widens to cover all microcells that could contain a
cross-microcell pair within radius:

```
neighbor_range = ceil(radius / microcell_size) = ceil(sqrt(3)) = 2
stencil size: 5 x 5 x 5 = 125 microcells
```

This is larger than the original 26-neighbor (3x3x3 minus center) stencil but
is required for completeness. Any cross-microcell point pair within radius falls
within this stencil.

The cell-pair existence check requirement from Goal2409 still applies and must
be preserved: union two microcells only after confirming at least one actual
point pair with `dist^2 <= radius^2`. The wider stencil does not change that
requirement; it changes which microcell pairs are candidates to check.

---

## Q3: Does the Fix Invalidate Any Part of Goal2409 Review or Goal2410 Contract?

The correctness guards from Goal2409 remain valid and carry over. The microcell
version satisfies all four:

1. **Cross-pair existence check** — still required, unchanged.
2. **All-core gate exactness** — still required, unchanged.
3. **Mutual exclusion of fast and fallback paths** — still required, unchanged.
4. **Cell-size invariant in code** — now tightened: the invariant is
   `microcell_size = radius / sqrt(3)`, not `cell_size = radius`. Code and
   comments must record `radius / sqrt(3)` explicitly.

The implementation contract from Goal2410 is superseded only where it names the
radius-cell design. Every other clause — app-agnostic boundary, metadata
requirements, fallback behavior, pod evidence requirements, pass/fail policy —
carries forward unchanged.

---

## Q4: Performance Risk Assessment

Codex correctly identifies the risk. The stencil is 125 microcell offsets vs 27
for the radius-cell design. Combined with more microcells per unit volume
(roughly `sqrt(3)^3 ≈ 5.2x` more cells per unit volume), the cell-pair scanning
work for the same point set is substantially larger.

The risk is real but acceptable because:

1. The radius-cell design was not just slower — it was incorrect. There is no
   prior speedup to defend.
2. The microcell scan is still cell-level, not point-level. If microcells are
   dense (many points per microcell), the union-find work per cell pair remains
   small relative to the point-level work it replaces.
3. The Goal2410 abort condition applies without modification: if microcell
   scanning degenerates to scanning nearly the same number of point pairs as the
   existing CuPy grid continuation, abort Candidate B' quickly and declare an
   inconclusive result. Do not tune.

If Candidate B' is correct but slower, the abort pivot is still Candidate A
(prepared CuPy grid hardening), which does not depend on cell-graph design at all.

---

## Q5: Required Tests

Codex's four functional test cases are necessary and sufficient. I accept them
as stated. The implementation must pass all four before any pod timing run:

1. **Same-cell disconnection:** `radius = 1.0`, `min_neighbors = 1`,
   `points = [(0,0,0), (0.99,0.99,0.99)]` — expected two separate components,
   not one merged label.

2. **Two dense subclusters inside one radius-sized cell, separated > radius** —
   expected two components.

3. **Mixed-core input** — expected fallback to
   `radius_graph_components_3d_cupy_grid_partner_columns` and
   `signatures_match = true` against CPU reference.

4. **Dense all-core clustered input** — expected microcell fast path activates,
   `signatures_match = true`.

Test 1 is the critical regression guard for the correctness hole. It must run on
every CI pass, not only when CuPy is available; a CPU-fallback version with a
CPU reference must also be included so the test is not silently skipped in
headless environments.

One additional static assertion must be present:

- The implementation must not contain any code path that asserts or assumes
  radius-sized cells are internally connected. Any such comment or assert is a
  correctness error.

---

## Q6: Naming

Codex's preference for the explicit public name is correct:

```python
radius_graph_components_3d_cupy_microcell_graph_partner_columns(...)
```

```text
optix_rt_core_flags_cupy_microcell_graph_components_3d
```

The original `cell_graph` name should not be retained as a public alias for the
microcell implementation. A future radius-cell design would be a different
primitive with a different correctness profile. Keeping `microcell` in the name
makes the granularity auditable from the benchmark mode string alone.

Required metadata fields (carry forward from Goal2410, with two additions):

- `adapter`
- `partner`
- `cell_graph_fast_path_active`
- `cell_graph_granularity = "clique_safe_microcell"`  ← new, required
- `microcell_size_policy`                              ← new, required
- `neighbor_cell_range`                               ← new, required
- `fallback_adapter` when fallback occurs
- `component_label_policy`
- claim-boundary flags set conservatively

---

## Recommendation: Next Implementation Target

Implement the corrected Candidate B' as the Goal2409 target:

```python
radius_graph_components_3d_cupy_microcell_graph_partner_columns(...)
```

with `microcell_size = radius / sqrt(3)`, a 5x5x5 stencil, exact cross-microcell
point-pair existence checks, and the all-core gate preceding the fast path.

Before any pod timing, pass all four functional tests above, with the same-cell
disconnection test running in CI without GPU.

Apply the Goal2410 abort condition without relaxation: if the microcell path's
cross-pair scan workload at 131k dense clustered points is within measurement
noise of the current CuPy grid continuation, declare Candidate B' inconclusive
and pivot immediately to Candidate A prepared CuPy grid hardening.

---

## Boundary

This review does not authorize a release claim, broad RT-DBSCAN speedup claim,
paper reproduction claim, or v2.x closure. It accepts the correctness correction
and updates the implementation target. The engine must remain app-agnostic; no
DBSCAN-native ABI and no hard-coded cluster expansion inside OptiX.
