# Goal 319 Report: v0.5 Cross-Platform Embree Correctness Matrix

Date:
- `2026-04-12`

Goal:
- close the bounded cross-platform correctness claim for Embree on the 3D
  nearest-neighbor trio

Verification surface:
- `tests.goal298_v0_5_embree_3d_fixed_radius_test`
- `tests.goal299_v0_5_embree_3d_bounded_knn_test`
- `tests.goal300_v0_5_embree_3d_knn_test`

Why this surface is sufficient:
- it already checks Embree row parity against `run_cpu_python_reference(...)`
- it already checks prepared-path parity against direct Embree execution
- it already checks raw-row field shape
- it already checks deterministic tie ordering for 3D `knn_rows`

Results:

## Linux

Already closed in the published `v0.5` Embree goals:
- Goal 298
- Goal 299
- Goal 300

## local macOS

Command:
- `PYTHONPATH=src:. python3 -m unittest tests.goal298_v0_5_embree_3d_fixed_radius_test tests.goal299_v0_5_embree_3d_bounded_knn_test tests.goal300_v0_5_embree_3d_knn_test`

Observed result:
- `Ran 10 tests`
- `OK`

## Windows

Probe workspace:
- `C:\Users\Lestat\work\rtdl_v05_crossplat_probe`

Environment notes:
- current repo snapshot copied from the Mac worktree
- Python:
  - `3.11.9`
- Embree:
  - `(4, 4, 0)`

Command:
- `py -3 -m unittest tests.goal298_v0_5_embree_3d_fixed_radius_test tests.goal299_v0_5_embree_3d_bounded_knn_test tests.goal300_v0_5_embree_3d_knn_test`

Observed result:
- `Ran 10 tests`
- `OK`

Conclusion:
- Embree 3D correctness is now bounded and verified on:
  - Linux
  - local macOS
  - Windows
- this justifies the narrower support-matrix statement that Windows and local
  macOS are part of the current bounded Embree correctness surface

Important honesty boundary:
- this goal does not claim Windows/macOS performance parity with Linux
- this goal does not claim Windows/macOS large-scale nearest-neighbor
  performance closure
