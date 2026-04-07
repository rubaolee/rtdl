---

## Verdict

One confirmed correctness/honesty defect (`spin_speed` is a dead variable), one latent brittleness in the orbit demo's shadow-ray ID scheme, and the summary.json is internally consistent. No security issues. The C++/ctypes ABI is correct.

---

## Findings

**1. `spin_speed` has zero effect — silent lie in summary JSON** (spinning_ball_3d_demo.py:663–664)

```python
spin_phase = phase * spin_speed   # computed but never used
lights = _frame_lights(phase)     # uses un-scaled phase
```

`spin_phase` is a dead variable. `_frame_lights` always receives the raw `phase`, so `spin_speed=1.1` (CLI default, test argument, and reported in `summary["spin_speed"]`) changes nothing in the output. Every call to `render_spinning_ball_3d_frames` with any `spin_speed` produces identical frames. The test at `goal164_spinning_ball_3d_demo_test.py:237` asserts `summary["spin_speed"] == 1.1` but never verifies the frames differ from `spin_speed=1.0`.

**2. Orbit demo shadow-ray IDs reuse primary ray IDs — brittle but currently safe** (orbiting_star_ball_demo.py:253–270)

`_make_shadow_rays` passes `base_id=ray.id`, so each shadow ray has `id == primary_ray.id`. With exactly one light this is a bijection and the lookup `shadow_lookup.get(ray.id, 0)` is correct. However there is no guard against adding a second light — doing so would immediately produce ID collisions in `shadow_rows`, silently producing wrong shadow factors for adjacent pixels.

**3. Struct packing is consistent and correct** (embree_runtime.py:94–132, rtdl_embree.cpp:59–92)

Both `_RtdlTriangle3D` and `_RtdlRay3D` carry `_pack_ = 1` in Python and `#pragma pack(push, 1)` in C++. Computed sizes (76 B / 60 B) agree on both sides. The 2D types omit packing deliberately and also agree.

**4. summary.json metrics are internally honest** (build/win_embree_earthlike_final_1024/summary.json)

- `triangle_count: 36480` = 2×192 (poles) + 94×2×192 (bands) = correct for lat=96, lon=192.
- `hit_pixels: 804722` constant across all 24 frames is correct — the camera and mesh are static; only shadow rays change per frame.
- `query_share ≈ 0.146`: `(5.556 + 121.822) / (5.556 + 121.822 + 744.835) = 0.1460` — matches the formula.
- `wall_clock_seconds ≈ 142 s` with `jobs=12` across 24 frames is coherent (~2 parallel batches of 12, each dominated by Python shading).

**5. `rtdl_embree_run_ray_hitcount_3d` implementation is correct** (rtdl_embree.cpp:1483–1548)

Uses `RTC_GEOMETRY_TYPE_USER` with per-triangle bounds + intersect callbacks, loops `rtcIntersect1` per ray, deduplicates hits by triangle ID via `seen_triangle_ids`. Functionally correct for hit-count semantics. (No vectorized batch calls, but that is a performance matter, not a correctness one.)

---

## Summary

The single actionable defect is `spin_speed` being silently ignored: the variable `spin_phase` is computed and discarded, while `_frame_lights` receives the raw `phase`. The CLI flag, the summary JSON field, and the test assertion all claim the parameter is meaningful, but no frame is ever affected by it. Fix: pass `spin_phase` to `_frame_lights`. The orbit demo shadow-ray ID scheme is functionally correct for one light but will silently corrupt results if a second light is added; adding an assertion on light count or using `ray.id * len(lights) + light_index` (as the spinning ball demo correctly does) would harden it. All other code and summary metrics reviewed are accurate.
