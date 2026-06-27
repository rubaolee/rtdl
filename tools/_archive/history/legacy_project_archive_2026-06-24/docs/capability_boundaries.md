# RTDL Capability Boundaries

Status: suspended for V3 rebuild on 2026-06-20.

The old capability-boundary page contained stale V3 release wording. It has
been moved to:

`docs/history/quarantine_v3_v4_reset_2026-06-20/docs__capability_boundaries.md`

## Current Rule

During rebuild, RTDL claims only the code and evidence that the active gate can
prove now.

Allowed rebuild wording:

- RTDL is a Python-hosted language/runtime for RT-shaped query kernels;
- Python owns app semantics, labels, files, policies, and final decisions;
- RTDL owns supported primitive contracts, backend dispatch, and evidence for
  named rows;
- NumPy, CuPy, Numba, or user code may own explicit continuation work when the
  row documents that boundary.

Blocked wording until the rebuild gate proves otherwise:

- current V3 release;
- broad RT-core acceleration;
- whole-app speedup;
- arbitrary partner acceleration;
- package-install promise;
- stable SDK or generated bindings;
- general zero-copy or device-residency claims.

Use [V3 Rebuild Control](rebuild/v3/README.md) as the current authority.
