Goal 169 review handoff for Gemini.

Repository:
- `/Users/rl2025/rtdl_python_only`

Scope:
- Review the current RTDL `v0.3` Goal 169 backend status package for honesty, scope discipline, and repo accuracy.
- Goal 169 has two backend targets:
  - Vulkan orbit-demo rendering on Linux
  - OptiX 4K-oriented orbit-demo rendering on Linux

Important boundaries:
- RTDL remains the geometric-query core.
- Python handles scene setup, shading, frame composition, and output.
- This is not a claim that RTDL has become a general rendering engine.
- The current premier public movie artifact is still from the Windows Embree line, not from Goal 169.
- The ongoing Windows 4K Embree `jobs=8` render is separate non-closure work and should not be treated as Goal 169 evidence.

Files to review:
- `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_orbiting_star_ball_demo.py`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal169_vulkan_orbit_demo_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal169_optix_orbit_demo_test.py`
- `/Users/rl2025/rtdl_python_only/build/goal169_vulkan_orbit_smoke/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal169_optix_orbit_smoke/summary.json`

Evidence summary:
- Linux host: `lestat@192.168.1.20`
- Vulkan Linux smoke summary:
  - `/Users/rl2025/rtdl_python_only/build/goal169_vulkan_orbit_smoke/summary.json`
  - `backend = vulkan`
  - `compare_backend.backend = cpu_python_reference`
  - `matches = true`
- OptiX Linux smoke summary:
  - `/Users/rl2025/rtdl_python_only/build/goal169_optix_orbit_smoke/summary.json`
  - `backend = optix`
  - `compare_backend.backend = cpu_python_reference`
  - `matches = true`

Local verification already established:
- `python3 -m compileall examples/visual_demo/rtdl_orbiting_star_ball_demo.py tests/goal166_orbiting_star_ball_demo_test.py tests/goal169_vulkan_orbit_demo_test.py tests/goal169_optix_orbit_demo_test.py src/rtdsl/optix_runtime.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal169_vulkan_orbit_demo_test tests.goal169_optix_orbit_demo_test`
- Result:
  - `Ran 17 tests`
  - `OK`
  - `6 skipped`

What to evaluate:
- whether the package stays honest about what Goal 169 does and does not prove
- whether the backend claims are properly bounded by the evidence
- whether the status story cleanly separates:
  - Linux Vulkan/OptiX backend closure work
  - Windows Embree 4K movie work
- whether repo accuracy and scope discipline remain strong

Please return exactly three short sections titled:
- `Verdict`
- `Findings`
- `Summary`
