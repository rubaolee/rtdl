# Antigravity Goal 178/179 Continuation

Continue from the current smooth camera-orbit state.

## Repo

- `/Users/rl2025/rtdl_python_only`

## Reminder

- reread `/Users/rl2025/refresh.md`
- every goal closure still needs `2+` AI consensus

## Goal 178

### Scope

- smoother demo composition
- fixed lights
- moving camera on a front arc
- Windows Embree HD movie as the main delivery target

### Implemented Files

- `/Users/rl2025/rtdl_python_only/examples/rtdl_smooth_camera_orbit_demo.py`
- `/Users/rl2025/rtdl_python_only/tests/goal178_smooth_camera_orbit_demo_test.py`

### Docs

- `/Users/rl2025/rtdl_python_only/docs/goal_178_smooth_camera_orbit_demo.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal178_smooth_camera_orbit_demo_2026-04-08.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal178_smooth_camera_orbit_demo_review_2026-04-08.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL178_GEMINI_ONE_SENTENCE_HANDOFF.md`

### Verified State

Local:

- `PYTHONPATH=src:. python3 -m unittest tests.goal178_smooth_camera_orbit_demo_test`
- result:
  - `Ran 7 tests`
  - `OK`
  - `2 skipped`

Windows:

- `py -3 -m unittest tests.goal178_smooth_camera_orbit_demo_test`
- result:
  - `Ran 7 tests`
  - `OK`
  - `2 skipped`

Windows one-frame smoke:

- output:
  - `C:\Users\Lestat\rtdl_python_only_win\build\goal178_windows_smooth_diag`
- backend `embree`
- `64 x 64`
- `jobs = 12`
- completed successfully

### Finished Windows Production Artifact

Local artifact directory:

- `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f`

Finished files:

- `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/win_embree_smooth_camera_hd_1024_uniform_320f.mp4`
- `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/frame_160.png`
- `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/summary.json`

Finished run facts:

- backend `embree`
- `1024 x 1024`
- `320` frames
- `jobs = 12`
- `phase_mode = uniform`
- `temporal_blend_alpha = 0.10`
- wall clock:
  - `1439.1826636000042 s`
- `query_share = 0.34155148723036616`

## Goal 179

### Scope

- prove the new smooth camera-orbit demo on Linux GPU backends
- keep artifacts small and compare-clean

### Claude-Written Code

- `/Users/rl2025/rtdl_python_only/tests/goal179_smooth_camera_linux_backend_test.py`

Claude wrote the initial test file; Codex removed one unused import and then validated it.

Saved report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal179_claude_code_draft_2026-04-08.md`

### Docs

- `/Users/rl2025/rtdl_python_only/docs/goal_179_linux_smooth_camera_backend_previews.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal179_linux_smooth_camera_backend_previews_2026-04-08.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal179_linux_smooth_camera_backend_previews_review_2026-04-08.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL179_GEMINI_ONE_SENTENCE_HANDOFF.md`

### Verification

Local combined slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal178_smooth_camera_orbit_demo_test tests.goal179_smooth_camera_linux_backend_test`
- result:
  - `Ran 11 tests`
  - `OK`
  - `6 skipped`

Linux host:

- `lestat@192.168.1.20`

Linux builds:

- `make build-vulkan`
  - `VULKAN:0`
- `make build-optix`
  - `OPTIX:0`

Linux combined slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal178_smooth_camera_orbit_demo_test tests.goal179_smooth_camera_linux_backend_test`
- result:
  - `Ran 11 tests`
  - `OK`

### Linux Preview Artifacts

OptiX:

- `/Users/rl2025/rtdl_python_only/build/goal179_optix_smooth_preview/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal179_optix_smooth_preview/frame_004.png`

Vulkan:

- `/Users/rl2025/rtdl_python_only/build/goal179_vulkan_smooth_preview/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal179_vulkan_smooth_preview/frame_004.png`

Both previews:

- `192 x 192`
- `8` frames
- `phase_mode = uniform`
- `temporal_blend_alpha = 0.10`
- frame `0` compare backend:
  - `cpu_python_reference`
  - `matches = true`

## Next Steps

1. get Gemini review for Goal 179 using:
   - `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL179_GEMINI_ONE_SENTENCE_HANDOFF.md`
2. optionally get a combined Claude/Gemini review for the smooth-camera slice using:
   - `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL178_179_CLAUDE_ONE_SENTENCE_HANDOFF.md`
3. write review notes / Codex consensus
4. commit the bounded Goal 178/179 slices
