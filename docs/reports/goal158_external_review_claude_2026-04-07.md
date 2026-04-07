---

## Verdict

**Pass.** The Goal 158 package is repo-accurate, doc-consistent, and the honesty boundary is held everywhere. No substantive issues found.

---

## Findings

**Repo accuracy**
- `rtdl_lit_ball_demo.py` is real, compilable Python. The kernel inside it uses `rt.ray_triangle_hit_count(exact=False)` and the correct `rt.Rays`/`rt.Triangles` types, matching the predicate signature shown in the `ray_tri_hitcount` feature home and the existing `rtdl_ray_tri_hitcount.py` canonical example.
- All five backend names in `_select_runner` (`cpu_python_reference`, `cpu`, `embree`, `optix`, `vulkan`) match the repo-wide runner API.
- All doc links to the demo file resolve to the actual path.

**Doc consistency**
- The RTDL-plus-Python message appears independently in all seven target docs (README, docs/README, quick_tutorial, release_facing_examples, v0_2_user_guide, rtdl_feature_guide, ray_tri_hitcount README) with no contradictory wording.
- The `ray_tri_hitcount` feature home correctly labels the demo as "App-style variant" rather than a peer canonical workload.

**Honesty boundary**
- The demo's own argparse description states the boundary inline: *"RTDL provides per-scanline ray/triangle hit relationships; Python computes the visible span and brightness."*
- Every referencing doc includes an explicit disavowal (e.g., "not a claim that RTDL v0.2.0 is a full rendering system").
- The `ray_tri_hitcount` README "Try Not" list specifically calls out "claiming a full rendering system just because Python can turn the RTDL result into an image."
- Code structure enforces the story: one `runner(...)` call, then all rendering math is pure Python.

**Minor issues (no blocking)**
1. `docs/README.md` line 65 and `docs/features/ray_tri_hitcount/README.md` use absolute paths (`/Users/rl2025/rtdl_python_only/examples/...`) for markdown links while the same files use relative paths for all other links.
2. `docs/release_facing_examples.md` line 72 run-command uses `cd /Users/rl2025/rtdl_python_only` (hardcoded) while every other run-command block on the same page uses `cd /path/to/rtdl_python_only`.

---

## Summary

The package satisfies all four review criteria. The RTDL-plus-Python story (RTDL = geometry-query core, Python = surrounding logic) is stated clearly and consistently across every doc entry point. The lit-ball demo is scoped properly — as a user-level application demo, not a renderer — at both the code and doc level, with explicit boundary statements repeated in each referencing document. The only defects are cosmetic: a handful of hardcoded absolute paths in links and one run-command, which should be made relative or replaced with `/path/to/rtdl_python_only` for portability.
