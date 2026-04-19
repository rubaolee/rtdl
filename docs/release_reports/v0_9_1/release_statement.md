# RTDL v0.9.1 Release Statement

RTDL `v0.9.1` releases the first bounded Apple RT backend slice.

The release adds `run_apple_rt` for 3D `ray_triangle_closest_hit` workloads on
macOS Apple Silicon through Apple Metal/MPS `MPSRayIntersector`.

The release is intentionally narrow. It does not claim full Apple backend
parity, prepared Apple RT reuse, non-macOS support, or measured Apple hardware
speedup. The correct public interpretation is: Apple RT is now a real RTDL
backend path for one closest-hit workload, with the same honesty boundaries
recorded in the support matrix.

The release keeps the broader `v0.9.0` HIPRT matrix unchanged.
