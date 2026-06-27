---

## Verdict

Three concrete code-level causes are most likely responsible for the mild end-of-shot flicker, in descending order of impact: (1) the analytic-sphere / Embree-mesh silhouette mismatch causing edge pixels to strobe as the camera finishes its arc, (2) the `cos/sin(phase*tau)` secondary camera motion reaching its maximum rate-of-change on the final frames, causing the specular highlight to sweep unevenly, and (3) the fixed `1e-3` shadow-ray origin offset producing inconsistent self-shadow results near the UV sphere's high-density pole triangles, which come into view at end-of-shot camera angle.

---

## Findings

**1. Analytic-sphere / mesh silhouette mismatch strobes edge pixels (highest impact)**

In `_render_smooth_frame` (smooth_camera_demo.py:200–209), a pixel is added to `pending_hits` only if it passes both the Embree mesh hit test (`hit_lookup.get(ray.id, 0) > 0`) AND the analytic `_ray_sphere_intersection`. These two disagree at the sphere silhouette: some mesh triangles slightly overhang or underhang the analytic sphere boundary. As the camera sweeps to azimuth ≈ +42° (phase → 1.0), the silhouette band moves continuously across the image. Borderline pixels at the current silhouette position are toggling between "sphere pixel → shaded" and "sphere pixel → skipped (returns `None`) → remains background," producing a one-pixel-wide flickering rim on the ball edge. This is a binary flip, not a gradual change, making it perceptible even when subtle.

**2. `cos(phase*tau)` + `sin(phase*tau)` secondary motion rate peaks at final frame**

`_camera_eye_for_phase` (smooth_camera_demo.py:114–121):
```python
distance = 6.28 - 0.16 * math.cos(phase * math.tau)   # tau = 2π
height   = center[1] + 0.28 + 0.06 * math.sin(phase * math.tau)
```
Both terms complete a full 2π oscillation over the 320-frame shot. The derivative of the `sin` term is `0.06 * 2π * cos(phase * 2π)`, which equals `0.06 * 2π * 1.0` at phase=1.0 — the maximum rate. So in the final ~40 frames (phase 0.875–1.0), camera height is rising at its fastest pace while camera distance is simultaneously converging to its minimum (6.12). This combined camera pull-in-and-rise changes the half-vector H for the `(N·H)**52.0` specular (line 505) faster per frame at the end than anywhere in the mid-shot, causing the sharp specular highlight to jump more noticeably between consecutive frames in the closing segment.

**3. Fixed `1e-3` shadow-ray offset inconsistent near UV sphere poles**

`_make_shadow_rays` (orbiting_star_demo.py:167–174) offsets the shadow ray origin by exactly `1e-3` world units along the surface normal, regardless of local triangle size. The UV sphere mesh at 80 latitude × 160 longitude bands produces triangles near the poles that are significantly smaller than equatorial triangles — their edge length can be an order of magnitude below 1e-3 at the poles. At end-of-shot camera angle (azimuth ≈ +42°, above equator), the top-hemisphere pole region is more directly visible. Shadow rays from hit points in that region can fail to clear the tiny pole triangles, sporadically self-shadowing pixels that should be lit. Because this depends on which specific triangles are grazed by the offset origin, it is sensitive to the exact floating-point hit_point value and varies frame-to-frame as the camera moves.

---

## Summary

The dominant flicker source is the dual hit-test architecture in `_render_smooth_frame`: Embree tests the triangle mesh while shading uses the analytic sphere, and their silhouette boundaries don't coincide. Pixels at the mismatch zone binary-flip each frame as the camera moves. A secondary contributor is the `cos/sin(phase*tau)` secondary motion, which is smooth throughout most of the shot but reaches peak velocity exactly at the last frame (phase=1.0), making the specular highlight sweep fastest in the closing segment. The shadow self-intersection offset adds scattered pole-area self-shadowing that is angle-dependent and thus exacerbated when the top-hemisphere is facing the camera at the end of the arc.
