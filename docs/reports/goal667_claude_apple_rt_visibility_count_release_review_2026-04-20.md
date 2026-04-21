# Goal667: Apple RT Prepared/Prepacked 2D Visibility-Count Release Review

Date: 2026-04-20

Reviewer: Claude (claude-sonnet-4-6)

Status: PASS — work is correctly implemented, bounded claims are consistent across all reviewed files

---

## Scope

Reviewed files:

- `src/rtdsl/apple_rt_runtime.py`
- `src/native/apple_rt/rtdl_apple_rt_prelude.mm`
- `src/native/apple_rt/rtdl_apple_rt_mps_geometry.mm`
- `examples/rtdl_apple_rt_visibility_count.py`
- `docs/reports/goal665_apple_rt_prepared_profile_2026-04-20.md`
- `docs/reports/goal666_mac_visibility_count_perf_2026-04-20.md`
- `README.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/current_main_support_matrix.md`
- `docs/backend_maturity.md`

---

## Source Correctness

### Native count path (`rtdl_apple_rt_count_prepared_ray_anyhit_2d`)

- Calls `run_anyhit_2d_prepared` with `emit_rows=false`. Row allocation and the `any_hits` vector are skipped; `*hit_count_out` is populated unconditionally. No memory leak from the local `rows_out`/`row_count` dummies.
- The scan loop counts `distance >= 0.0f && distance <= 1.000001f` as a hit, guarded by `valid_ray_2d`. This is the correct "any hit exists" test for the encoded MPS rays.
- `MPSIntersectionTypeNearest` is used rather than a hypothetical `MPSIntersectionTypeAny`. This is semantically correct for counting blocked rays: distance ≥ 0 means a hit occurred regardless of which one is nearest. It is a potential future optimization target (nearest-hit traversal does not terminate as early as a true any-hit kernel), but this is not a bug and is consistent with the existing 3D any-hit path documented in `current_main_support_matrix.md`.

### Python binding (`count_profile_packed`)

- ctypes argtypes: `[c_void_p, POINTER(_RtdlRay2D), c_size_t, POINTER(c_uint64), POINTER(_RtdlAppleRtAnyHitProfile), c_char_p, c_size_t]` — matches the native signature exactly.
- Returns `int(hit_count.value)` as the first element of the tuple. This is correctly labeled `blocked_count` in the example and mapped to `blocked_ray_count` in output JSON.
- `clear_ray_count = len(rays) - blocked_count` is arithmetically sound.

### Example (`rtdl_apple_rt_visibility_count.py`)

- Uses `rt.prepare_apple_rt_rays_2d` → `rt.prepare_apple_rt_ray_triangle_any_hit_2d` → `prepared.count_profile_packed`. The path through the public API is correct.
- Output fields `blocked_ray_count` and `clear_ray_count` accurately describe the scalar count semantics.
- The `except` branch prints a `skipped` status rather than a hard error, appropriate for an optional native path.

---

## Performance-Claim Honesty

Goal666 reports `apple_rt_prepared_packed_count` per-query medians of 0.00091–0.00133 s versus `embree_row_count` at 0.01474–0.01530 s on a local Apple M4 (32768 rays, 8192 triangles).

The following honesty constraints are all satisfied:

| Constraint | Status |
| --- | --- |
| Output-contract difference disclosed | Yes — Apple RT returns scalar count; Embree materializes rows |
| Setup costs (scene prepare + ray pack) reported separately | Yes — 0.027–0.076 s prepare, 0.013–0.015 s pack |
| Comparison to full-row Embree output explicitly disclaimed | Yes — Goal666 "Interpretation Rules" #4 and "Major Conclusion" |
| Per-query timing uses repeated-loop median | Yes — inner-iteration counts 103–3096 confirm warm-path measurement |
| Blocked counts cross-checked between backends | Yes — `correctness` column shows agreement |

---

## Documentation Boundary Consistency

Every reviewed doc correctly restricts the claim to scalar blocked-ray count. The key phrase "scalar blocked-ray count, not full emitted rows" (or equivalent) appears consistently in:

- `README.md` (version-status section)
- `docs/release_facing_examples.md` (table entry and introduction bullet)
- `docs/current_main_support_matrix.md` (support table row, implementation note, non-claims list)
- `docs/backend_maturity.md` (Goal666 paragraph and maturity bullet)
- `src/rtdsl/apple_rt_runtime.py` `APPLE_RT_SUPPORT_NOTES["ray_triangle_any_hit"]`
- Goal665 and Goal666 report conclusions

No doc asserts that the scalar-count result implies Apple RT beats Embree for full emitted-row output. The `non-claims` section in `current_main_support_matrix.md` explicitly prohibits that generalization.

---

## Minor Observations (Non-Blocking)

1. **`MPSIntersectionTypeNearest` vs. any-hit**: The count path uses nearest-hit traversal, which is documented for the 3D path but not explicitly called out for the 2D count path in current docs. This is not a correctness issue. A future note in `backend_maturity.md` or `current_main_support_matrix.md` could mention it as a future optimization opportunity, but it does not affect the current result or claim.

2. **`count_profile` wrapper**: The non-packed `count_profile` convenience method packs rays inline via `AppleRtRay2DBuffer(rays)`, incurring Python packing cost on every call. The performance benefit of the prepacked path is only realized through `count_profile_packed`. This is an ergonomics trade-off, not a bug, and the profile report (Goal665) clearly shows that pre-packing eliminates the dominant Python wall time.

---

## Verdict

**PASS.**

The prepared/prepacked 2D visibility-count work is correctly implemented end-to-end. The scalar `hit_count_out` from the native count entry point correctly represents the number of blocked rays. The Python binding argtypes match the native signature. The example accurately labels output fields. Performance claims are honest: setup costs are separated, the output-contract asymmetry between Apple RT (scalar count) and Embree (full rows) is disclosed, and no doc generalizes the scalar result to full emitted-row output. All reviewed documentation consistently applies the correct boundary.
