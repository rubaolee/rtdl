Now I have enough context. Here is my review:

---

## Verdict

The `_stable_fill_light` function and its integration into `_frame_lights` are correctly implemented and the core tests are well-placed. However, the test suite has three meaningful blind spots around the new fill light: its color is not verified, its rendering-suppression path in `_overlay_star_and_ground` is untested, and its contribution to shading (via shadow rays) is not covered in isolation.

---

## Findings

**What is correct and well-tested**
- `test_stable_fill_light_is_fixed_and_hidden` correctly pins the position, asserts intensity > 0, and verifies both `display_alpha == 0.0` and `ground_alpha_scale == 0.0` — the two flags that suppress all visual overlay drawing.
- `test_frame_lights_returns_two_warm_yellow_lights_plus_fill` correctly asserts `len == 3`, the intensity ordering (`fill < secondary < primary`), and warm color of the stars.
- `test_frame_lights_are_horizontally_mirrored_on_equator` correctly pins the fill position as constant across all phases.
- `test_summary_records_two_light_setup` confirms `light_count == 3` round-trips through JSON.

**Gaps**

1. **Fill color not verified.** The fill is intentionally a cool blue `(0.34, 0.38, 0.52)` to contrast the warm stars. No test checks the color at all — a future accidental warm fill would go unnoticed.

2. **`_overlay_star_and_ground` early-exit for hidden lights is untested.** `display_alpha == 0.0` triggers an immediate `return` at line 229, meaning the fill never draws a disc or ground ellipse. This contract has no direct unit test.

3. **`ground_alpha_scale == 0.0` suppresses ground ellipse — not tested in isolation.** The `outer_alpha` and `inner_alpha` computations multiply by `ground_alpha_scale`, so the fill contributes zero ground painting. There is no test that exercises this path with `ground_alpha_scale=0` while `display_alpha > 0` (the case where a light is visible but has no ground footprint).

4. **Fill still casts shadow rays.** The fill has `intensity == 0.72 > 0`, so `_render_orbit_frame` does emit shadow rays for it. No test verifies the fill's `shadow_rays` count contribution separately from the two star lights — a future zero-intensity fill would silently skip shadow rays.

5. **`_stable_fill_light` is not verified to be phase-invariant via `_frame_lights`.** It takes no arguments and is always the same, but a test explicitly asserting `_frame_lights(0.0)[2] == _frame_lights(0.5)[2] == _frame_lights(1.0)[2]` makes the phase-invariance contract explicit.

---

## Summary

The fill light's position/intensity/alpha flags are pinned, but its **color**, **overlay-skip path**, **ground-alpha-zero path**, and **shadow-ray contribution** are all uncovered.
