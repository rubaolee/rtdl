Goal 169 review handoff for Claude.

Repository:
- `/Users/rl2025/rtdl_python_only`

Scope:
- Review the current RTDL `v0.3` Goal 169 backend package for repo accuracy and code correctness.
- Goal 169 has two backend targets:
  - Vulkan orbit-demo rendering on Linux
  - OptiX 4K-oriented orbit-demo rendering on Linux

Important boundaries:
- RTDL remains the geometric-query core.
- Python handles scene setup, shading, frame composition, and output.
- This is not a claim that RTDL has become a general rendering engine.
- The ongoing Windows 4K Embree `jobs=8` render is separate ongoing work, not closure evidence for Goal 169.

Files to review:
- `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_orbiting_star_ball_demo.py`
- `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_spinning_ball_3d_demo.py`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal169_vulkan_orbit_demo_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal169_optix_orbit_demo_test.py`
- `/Users/rl2025/rtdl_python_only/build/goal169_vulkan_orbit_smoke/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal169_optix_orbit_smoke/summary.json`

Linux evidence already established:
- Host: `lestat@192.168.1.20`
- Fresh Linux goal directories:
  - `/home/lestat/work/rtdl_v03_vulkan_goal169`
  - `/home/lestat/work/rtdl_v03_optix_goal169`
- Vulkan:
  - `make build-vulkan` succeeded
  - `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal169_vulkan_orbit_demo_test` passed
  - one-frame orbit render on `vulkan` vs `cpu_python_reference` matched
- OptiX:
  - `make build-optix` succeeded
  - `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal169_optix_orbit_demo_test` passed
  - one-frame orbit render on `optix` vs `cpu_python_reference` matched

Local verification already established:
- `python3 -m compileall examples/visual_demo/rtdl_orbiting_star_ball_demo.py tests/goal166_orbiting_star_ball_demo_test.py tests/goal169_vulkan_orbit_demo_test.py tests/goal169_optix_orbit_demo_test.py src/rtdsl/optix_runtime.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal169_vulkan_orbit_demo_test tests.goal169_optix_orbit_demo_test`
- Result:
  - `Ran 17 tests`
  - `OK`
  - `6 skipped`

What to evaluate:
- whether the code changes are coherent and repo-accurate
- whether the backend/runtime changes are honestly represented by the evidence
- whether the new tests actually cover the new backend surface meaningfully
- whether there are any correctness, regression, or overclaim risks

Please return exactly three short sections titled:
- `Verdict`
- `Findings`
- `Summary`
