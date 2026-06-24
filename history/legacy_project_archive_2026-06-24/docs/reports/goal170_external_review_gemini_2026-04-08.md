# Goal 170 External Review: Gemini

## Verdict

Goal 170 is **complete, honest, and bounded**; it successfully delivers
verified Linux GPU demo artifacts while explicitly maintaining that the Windows
Embree path remains the primary visual standard.

## Findings

- **Vulkan Correctness Fix:** Applied a host-count replacement in
  [rtdl_vulkan.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp)
  so the 3D hit-count result matches the exact host count for the bounded demo
  path.
- **Denser Validation:** The Vulkan follow-up test in
  [goal169_vulkan_orbit_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal169_vulkan_orbit_demo_test.py)
  increases the compare surface beyond the original tiny one-frame check.
- **Honest Bounding:** Goal 170 keeps the Linux GPU artifact line clearly
  secondary to the Windows Embree public movie path and does not overclaim large
  Linux production-movie readiness.
- **Artifact Verification:** The saved summaries and review notes support the
  claim that the bounded Linux Vulkan and OptiX demo artifacts match
  `cpu_python_reference`.

## Summary

Goal 170 provides the first saved Linux GPU artifacts for the RTDL 3D demo
line, including a real correctness fix for the Vulkan native backend and a
bounded artifact package for both Linux GPU-facing backends. It is consistent
with the project’s honesty-first reporting model.
