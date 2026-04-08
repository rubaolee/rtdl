Verdict

Pass. The NumPy fast path is correct and the upper-right-to-lower-left light travel is preserved by the existing `_frame_light` geometry.

Findings

1. NumPy fast path background: `_make_background_image_numpy` mirrors `_background_pixel` faithfully; the gradient, vignette, nebula, bloom, and floor terms are preserved and rounded to `uint8`.
2. NumPy fast path shading: `_shade_pending_hits_numpy` is a vectorized translation of `_shade_hit`, including Lambert, Fresnel, specular, and shadow lookup behavior.
3. Light path direction: `_frame_light` still uses `diag = math.cos(angle)` to move the light from high-right to low-left as phase advances across the visible half of the orbit.
4. Real issue found during review: the render path was copying the background into a plain Python list before dispatching, which made the NumPy shading path unreachable. That issue was fixed after review by preserving the NumPy array copy in `_render_orbit_frame`.

Summary

The diagonal upper-right-to-lower-left sweep is preserved, and the optional NumPy host-side fast path is the right direction for the Earth-like demo. The one substantive issue found in review was that the fast path was initially dead code due to an early list conversion; after preserving the array copy in `_render_orbit_frame`, the path became reachable and suitable for execution.
