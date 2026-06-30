# Claude Hidden-Star Demo Review — 2026-04-09

## Verdict

The hidden-star stable Earth demo is structurally sound. The light→surface shadow
construction correctly eliminates the instability that came from surface→light rays on
a triangle-mesh sphere. RTDL genuinely participates in both the camera-hit and shadow
stages; there is no boundary dishonesty. Three issues need attention before treating
this as a fully clean handoff: stale subdirectory paths throughout the design report,
a Q/A doc whose performance artifact links still point to the old smooth-camera line,
and a shadow test suite that cannot exercise actual occlusion correctness.

## Findings

**1. Design report carries wrong file paths (stale, not cosmetic)**

`goal168_hidden_star_stable_rtdl_shadow_demo_2026-04-09.md` lists source paths as:

- `examples/rtdl_hidden_star_stable_ball_demo.py`
- `examples/goal168_hidden_star_stable_ball_demo_test.py`

The actual locations are:

- `examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py`
- `tests/goal168_hidden_star_stable_ball_demo_test.py`

The Recommended Copy Set at the bottom of the report, the reproduction commands, and
the "New Demo File" section all carry the same wrong subdirectory. A newcomer following
the report cannot locate the source or run the tests without already knowing the layout.

**2. `current_milestone_qa.md` performance section still points to smooth-camera artifacts**

The "What is the current strongest RTDL result?" section (lines 29–34) names the
preserved local counterpart as `win_embree_smooth_camera_true_onelight_hd_1024_uniform_192f_6s.mp4`
and links the OptiX and Vulkan supporting artifacts to smooth-camera build paths, not
hidden-star paths. The "What is RTDL doing in Python?" section in the same file
correctly names `rtdl_hidden_star_stable_ball_demo.py` as the primary baseline. These
two sections now contradict each other on which demo is primary.

**3. `release_facing_examples.md` hierarchy is inverted relative to the README**

The section heading "RTDL Plus Python App Demo" still labels `rtdl_lit_ball_demo.py`
as the demo, with the hidden-star demo appearing only as an unlabeled sanity-check
command below it. The README and docs/README now declare the hidden-star demo as the
primary 3D demo source. The `release_facing_examples.md` hierarchy contradicts that.

**4. Shadow tests are too weak to catch a broken shadow implementation**

`test_render_two_frames_rtdl_shadow_emits_shadow_rays` confirms:

- `shadow_mode` is recorded correctly in the summary
- shadow query seconds > 0.0
- at least one frame has shadow_rays > 0

It does not assert that shadow mode changes any pixel, nor that any pixel is ever
reported as occluded. For the convex-sphere scene it cannot: a front-facing point on
a convex sphere is always unoccluded by the sphere itself, so `shadow_lookup` will
never return a hit count > 0 under correct geometry. The report explicitly states the
RTDL-shadow result is byte-for-byte identical to the analytic result. This means a
regression that always returns 0 hits or always returns 1 hit would pass every current
test while silently producing wrong shading in any non-trivial scene.

**5. Demo code is correct; no shading inversion bugs found**

The visibility logic in `_render_stable_frame` (lines 224–232) is correct:

- hit in `shadow_lookup` → occluded → 0.0
- no hit, `shadow_candidates` facing > 0 → lit → 1.0
- `shadow_candidates` facing ≤ 0 → back-facing → 0.0

The `tmax` clamping `max(0.0, distance - max(3e-3, distance * 1e-5))` provides
reasonable self-hit avoidance for the scene geometry. No correctness bug was found in
the shadow ray construction or in `_light_facing_visibility`.

**6. CLI default and wrapper defaults diverge silently**

`main()` and the `render_hidden_star_stable_ball_frames()` signature both default to
`shadow_mode="analytic"`. The Vulkan and OptiX convenience wrappers default to
`shadow_mode="rtdl_light_to_surface"`. This is intentional but not documented at the
function level. A caller using the base function directly for a quick test will get
analytic shadows and may not realize RTDL is not in the shadow path.

**7. Heavy import coupling to `rtdl_spinning_ball_3d_demo.py`**

The demo imports eight names from `rtdl_spinning_ball_3d_demo`. Any rename or
signature change there silently breaks this file. There is no interface contract.
This is a maintainability risk, not a current bug.

## Summary

Accept the demo as the primary 3D demo source. The design change is correct and the
RTDL/Python boundary is honestly represented. Three things should be fixed before this
handoff is considered clean: (1) update all file paths in the design report to use
`examples/visual_demo/` and `tests/`; (2) update the `current_milestone_qa.md`
performance artifact links to point to hidden-star build outputs rather than
smooth-camera outputs; (3) add a shadow-correctness test using a scene with a real
occluder — even a second small sphere placed between the light and Earth at a
known position — so that the RTDL shadow path is exercised end-to-end rather than
only confirming that shadow rays were dispatched.
