Verdict

The code is structurally sound and the Python/RTDL responsibility boundary is honest — RTDL handles BVH traversal and hit counts, Python owns everything else. There are no catastrophic bugs, but one reproducible visual defect, one numpy/pure-Python shading divergence, and several test gaps that leave correctness assumptions unverified.

---

## Findings

**1. Light-sprite position mismatch when `spin_speed != 1.0` (spinning ball demo)**
`render_spinning_ball_3d_frames` computes `spin_phase = phase * spin_speed` and passes it to `_frame_lights` for shading, but then calls `_overlay_lights(image, phase=phase, ...)`. Inside `_overlay_lights`, `_frame_lights(trail_phase)` and the final disc paint also use the unscaled `phase`. At the default `spin_speed=1.1` the light sprites are visually shifted relative to their shading positions every frame. No test catches this because no test compares light-position consistency between shading and compositing.

**2. Numpy and pure-Python shading paths produce different pixels**
`_shade_pending_hits_numpy` uses `midnight=(0.03, 0.08, 0.24)` and `deep_blue=(0.06, 0.19, 0.54)`. The pure-Python `_shade_hit` (called in both demos) uses `midnight=(0.04, 0.07, 0.18)` and `deep_blue=(0.08, 0.14, 0.34)`. The `numpy_fast_path` flag is surfaced in the summary, but there is no parity test. The frames produced when `numpy` is available differ visually from the cpu-reference path, which undermines the compare-backend cross-check.

**3. Pole-cap winding inconsistency in `make_uv_sphere_mesh`**
At the north-pole band (`lat_index == 0`), `phi0 = 0` so `p00 == p01` (degenerate top edge). The cap triangle is `(p00, p10, p11)`. For the south-pole band, it is `(p00, p10, p01)`. Mid-band quads are `(p00, p10, p11)` + `(p00, p11, p01)`. The winding is consistent enough for hit-count queries, but if a future RTDL kernel uses face normals or back-face culling the degenerate poles may produce undefined results. No test asserts winding correctness.

**4. `_run_backend_rows` lives in an example file**
Backend dispatch (`cpu_python_reference` / `embree` / `optix` / `vulkan`) is defined inside `examples/visual_demo/rtdl_spinning_ball_3d_demo.py` and re-imported by the orbiting-star demo and both test files. This couples library-level routing to an example, makes the function harder to test in isolation, and means adding a new backend requires editing example code.

**5. Missing test coverage**
- No test verifies numpy vs. pure-Python pixel parity (finding 2 above goes undetected).
- No test exercises `jobs > 1` (multi-process path).
- No test for the spin_phase/phase overlay mismatch (finding 1).
- Integration tests validate PPM headers and hit-pixel counts but not pixel values, so color regressions are invisible.
- `from examples.visual_demo.rtdl_spinning_ball_3d_demo import ...` implies `examples/` is a package; no `__init__.py` appears in the bundle, which will cause `ModuleNotFoundError` unless the tests are run from the repo root with a specific invocation.

---

## Summary

The RTDL responsibility split is correct: the kernel is a clean two-step `traverse` → `refine` → `emit` declaration and Python never reimplements traversal logic. The main actionable issues are: (a) fix `_overlay_lights` to accept and use `spin_phase`, (b) reconcile the numpy shading coefficients with the reference path or add an explicit parity test that asserts pixel-level equivalence up to a tolerance, and (c) move `_run_backend_rows` into the library. Test coverage should be extended with a pixel-diff smoke test for the numpy path and a two-worker sanity render.