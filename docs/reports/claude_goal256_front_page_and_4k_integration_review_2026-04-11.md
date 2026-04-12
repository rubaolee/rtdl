# Goal 256: Front Page and 4K Integration Review

Date: 2026-04-11  
Reviewer: Claude (claude-sonnet-4-6)

---

## Verdict

**Pass.** The front page is honest and well-framed, the 4K video is integrated cleanly, and the boundary between RTDL compute work and Python application work is stated consistently across README, documentation, and code. The Goal 256 code, reports, and tests are release-appropriate.

---

## Findings

### Front page language and scope (README.md)

The opening paragraph is correctly scoped:

> RTDL is a language/runtime for expressing workloads that can be accelerated by ray tracing, including workloads that map well to ray-tracing cores on modern GPUs.

The language goal is not incorrectly constrained to spatial workloads. The README includes the explicit clarification:

> the language goal is broader than spatial workloads alone.

The "Current Limits" section reinforces the honest boundary:

> the current released surface is strongest on geometric and nearest-neighbor workloads

That distinction — language goal vs. currently released surface — is present and accurate.

### 4K video integration

The video is surfaced at three levels in README.md:

1. A primary text link under "See It Quickly" as the first item in that list.
2. A 240px thumbnail linked to YouTube immediately below.
3. A second labeled text link below the thumbnail.

The YouTube URL (`https://youtu.be/d3yJB7AmCLM`) is consistent across all three occurrences and matches the URL in the work report.

The placement is professional. The thumbnail image reference (`docs/assets/rtdl_visual_demo_thumb.png`) uses a relative path that will resolve correctly from the repository root on GitHub.

The "What The Video Shows" section makes the RTDL/Python boundary explicit and pre-empts the obvious reader misread:

> It is not a product pivot toward graphics. It is a proof that RTDL can act as the query engine inside a larger Python application.

No overclaim is made. RTDL is not called a renderer anywhere.

### Hidden-star example (rtdl_hidden_star_stable_ball_demo.py)

The `crossed_dual_hidden` scene is correctly supported. `_scene_lights()` returns both the yellow (horizontal) and red (vertical) lights, and the unsupported scene name raises `ValueError` cleanly.

The stable shadow design is correct. `_make_light_to_surface_shadow_ray` fires from the light toward the surface point with a `tmax` that stops just short of the target:

```python
tmax = max(0.0, distance - max(3.0e-3, distance * 1.0e-5))
```

This avoids the surface self-hit instability documented in the work report. The bias is conservative enough (minimum 3mm or 1e-5 relative) to be safe across float32 mesh scales.

Shadow batching at `_SHADOW_RAY_BATCH_SIZE = 100_000` is appropriate for memory-bounded 4K renders. The batch flush loop is correct and clears the batch after each dispatch.

The numpy fast-path for image writes (`image[py, px] = colors`) is guarded properly with `hasattr(image, "shape")`, so the pure-Python fallback is exercised when numpy is absent.

Frame offset and phase offset are correctly threaded through to `_render_stable_frame` via the task tuple, enabling the chunk driver to produce continuous phase progression across chunks.

One minor asymmetry: `query_seconds` is attributed only to `frame_index == 0` in the per-frame summary, all other frames record `0.0`. This is intentional (primary rays are shared across the chunk), but it means top-level query-time aggregation in the chunk driver is correct only if this attribution is understood. The current aggregation in `render_hidden_star_stable_ball_frames` uses `query_seconds` directly (not summed from frames), so it is correct.

### Chunked video driver (render_hidden_star_chunked_video.py)

The chunk loop is correct. `frame_number_offset=chunk_start` and `phase_index_start=chunk_start` with `phase_index_total=total_frames` ensure phase continuity across chunks.

PPM files are deleted immediately after appending to the writer:

```python
writer.append_data(imageio.imread(frame_path))
frame_path.unlink()
```

This matches the documented memory/disk-bounded design.

The `imageio` import failure path (`imageio = None`) raises a clear `RuntimeError` with install instructions, which is better than an `AttributeError` at `get_writer` call time.

The top-level summary is comprehensive and written before the function returns. The video filename embeds the key configuration parameters, which makes multiple runs in the same directory non-colliding for different parameter sets.

Default CLI values match the production 4K configuration (3840×2160, 320 frames, 32 fps, 8 jobs, `crossed_dual_hidden`, `rtdl_light_to_surface`).

### Test coverage (tests/goal256_hidden_star_4k_workpack_test.py)

Two tests cover the two new paths:

- `test_crossed_dual_hidden_scene_reports_two_lights`: verifies scene name, light count, light layout string, and that at least one frame actually fired shadow rays. The last assertion guards against a regression where shadow mode is accepted syntactically but shadow rays are never constructed.
- `test_chunked_video_summary_and_chunk_cleanup`: verifies chunk count (2 for 3 frames at chunk_frames=2), total frame count in the writer, summary file presence, and that no PPM files remain after completion.

The imageio mock is correct. `_FakeImageIO.imread` returns raw file bytes (not a decoded array), which is sufficient because the test verifies frame count and cleanup, not pixel content.

The `_FakeWriter` context manager protocol matches what `imageio.get_writer()` returns, so the mock does not mask any structural misuse of the writer API.

### Report and documentation completeness

- `docs/reports/hidden_star_4k_render_work_report_2026-04-11.md`: present and detailed. Performance numbers include honest framing (Python shading dominates wall clock; RTDL query work is real but a minority share). The design rationale for the stable shadow path is documented.
- `docs/reports/goal256_hidden_star_4k_artifact_integration_2026-04-11.md`: all acceptance items from `docs/goal_256_hidden_star_4k_artifact_integration.md` are addressed. The verification section records actual test results and smoke invocations.
- README "Choose Your Path" links both demo scripts and the work report directly. The documentation chain from front page to work to code is complete.

---

## Risks

**Minor.**

1. **`render_hidden_star_stable_ball_vulkan_frames` and `_optix_frames` wrappers are untested.** These convenience functions exist in the demo module and will surface in documentation browsing, but there is no CI coverage guarding their signatures against future refactor drift. This is low risk in the short term but worth noting for a future test pass.

2. **imageio/imageio-ffmpeg as new declared dependencies.** These are added to `requirements.txt`. They pull in ffmpeg binaries via `imageio-ffmpeg`. This is appropriate for the chunked video path but adds non-trivial package weight to a fresh install. Users who only run the core workloads will also install these. Consider moving them to a separate `requirements-demo.txt` in a future pass if install footprint becomes a concern. For v0.4.0 this is acceptable.

3. **Platform coverage is Windows/Embree only for the 4K render evidence.** This is correctly disclosed in the work report ("the full 4K render evidence is Windows/Embree-based, not a cross-backend movie benchmark") and in the "Current Limits" section of the README. There is no risk of overclaiming here, but it is worth preserving that disclosure.

4. **`_render_stable_frame` uses a module-level global (`_STABLE_WORKER_STATE`) for worker state.** This is the standard `ProcessPoolExecutor` initializer pattern and is correct. However, if the single-process path is called more than once in the same process (e.g., in a test loop), the global is re-initialized on each call to `render_hidden_star_stable_ball_frames`. That is the intended behavior and is safe, but it is an implicit contract worth being aware of.

---

## Conclusion

Goal 256 is cleanly executed. The front page correctly describes RTDL as a language/runtime with goals broader than spatial workloads, while honestly scoping the current released surface. The 4K demo video is integrated prominently without overclaiming renderer capabilities. The code is well-structured, the shadow design is stable and documented, and the test coverage exercises the two new paths at appropriate depth. The work report and integration report together provide a complete and honest record of the Windows render and import. No blocking issues found.
