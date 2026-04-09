# Claude OptiX Mismatch Review

Please review the current RTDL OptiX code path for the small smooth-camera Linux support-video mismatch.

Return exactly three short sections titled:

- `Verdict`
- `Findings`
- `Summary`

Focus on whether the remaining OptiX issue looks like:

- an expected duplicate-hit / seam-count behavior
- a real backend correctness bug
- or a comparison/reporting bug in the demo layer

Files to read:

- OptiX Python runtime:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- OptiX native implementation:
  - `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`
- smooth-camera demo:
  - `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_smooth_camera_orbit_demo.py`

Measured reproduction facts:

- Linux OptiX support video artifact:
  - `/Users/rl2025/rtdl_python_only/build/goal188_optix_smooth_camera_256/summary.json`
- Linux Vulkan support video artifact:
  - `/Users/rl2025/rtdl_python_only/build/goal188_vulkan_smooth_camera_256/summary.json`

Important measured details:

- Vulkan frame `0` compare is clean against `cpu_python_reference`
- OptiX frame `0` has:
  - `matches = true`
  - `exact_matches = false`
  - `visible_mismatch_count = 0`
  - `exact_mismatch_count = 1`
- Direct row-level debugging at the exact failing frame-0 settings found:
  - exactly one differing ray
  - that ray had `2` hits in `cpu_python_reference`
  - and `3` hits in OptiX
  - visible hit / miss status was unchanged

Please judge whether the current repo posture is technically correct and what the next engineering move should be.
