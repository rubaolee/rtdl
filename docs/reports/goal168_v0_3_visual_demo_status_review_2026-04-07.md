Goal 168 review note

Historical status package.

This package captured the early `v0.3` visual-demo state around the original
Windows Embree `softvis` recommendation. It was later superseded by the
smooth-camera acceptance and final closure packages:

- [goal181_smooth_camera_flagship_acceptance_2026-04-08.md](/Users/rl2025/rtdl_python_only/docs/reports/goal181_smooth_camera_flagship_acceptance_2026-04-08.md)
- [goal184_v0_3_final_status_package_2026-04-09.md](/Users/rl2025/rtdl_python_only/docs/reports/goal184_v0_3_final_status_package_2026-04-09.md)

Package intent

- summarize the current v0.3 visual-demo state in one repo-accurate package
- keep the v0.2 release line distinct from the v0.3 demo line
- identify the recommended current public artifact clearly
- keep the backend story honest:
  - polished public movie currently strongest on Windows Embree
  - bounded 3D RTDL ray/triangle backend closure already established on Linux
    across:
    - `embree`
    - `optix`
    - `vulkan`

Verification basis

- focused tests:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal164_spinning_ball_3d_demo_test tests.goal166_orbiting_star_ball_demo_test`
  - `Ran 17 tests`
  - `OK`
  - `6` skipped

External review coverage

- Claude review:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal168_external_review_claude_2026-04-07.md`
- Gemini review:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal168_external_review_gemini_2026-04-07.md`

Closure note

- Claude found one real wording inconsistency in the first report draft:
  - the report briefly named `cpu_python_reference` in the already-closed
    backend list while the rest of the package intentionally named only the
    three target backends
- that wording was corrected before final review closure
- this preserved package remains useful as an intermediate status checkpoint,
  but it is no longer the final `v0.3` status surface
