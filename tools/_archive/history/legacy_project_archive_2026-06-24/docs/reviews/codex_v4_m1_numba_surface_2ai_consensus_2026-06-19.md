# RTDL V4 M1 Numba Surface Boundary Consensus

Date: 2026-06-19

Status: accepted release-boundary consensus for V4 M1 engineering evidence.

Reviewers:

- Nietzsche
- Gibbs

Question:

Should the new V4 M1 Numba evidence close the release-candidate blocker
`full_numba_partner_surface`, or should that blocker remain open while only
bounded M1 `DeviceNDArray` wording is authorized?

## Verdict

Keep `full_numba_partner_surface.closed = false`.

The new evidence is stronger than the original smoke test and does authorize
bounded wording for the V4 M1 fixed-radius route with Numba `DeviceNDArray`
columns through `__cuda_array_interface__`. It does not authorize broad "full
Numba support", arbitrary Numba program acceleration, or "Numba partner surface
validated" wording.

## Accepted Evidence

`docs/reports/v4_0_m1_fixed_radius_numba_partner_surface_probe_2026-06-19.json`
is accepted as bounded M1 evidence for:

- fixed-radius count/threshold route only;
- Numba `DeviceNDArray` columns through `__cuda_array_interface__`;
- parity across the report's positive cases;
- same nondefault Numba stream propagation;
- Numba consumer checksum on the same stream;
- V4 plan pointer identity and native pointer echo;
- caller-owned output columns;
- prepared-handle reuse while caller-owned search columns remain alive.

## Boundary

The evidence remains narrow:

- one V4 M1 route;
- one protocol path;
- one CUDA/Numba runtime snapshot;
- same-stream only;
- positive prepared-handle lifetime only;
- no cross-stream event/wait contract;
- no arbitrary Numba kernel/program acceleration claim;
- no public speedup, async, true-zero-copy, PyTorch, or DLPack route claim.

## Required Follow-Up For Full Surface Closure

Before `full_numba_partner_surface` can close, V4 needs a defined public Numba
surface contract and evidence beyond the single M1 fixed-radius route:

- broader route/API coverage;
- default and nondefault stream matrix;
- cross-stream contract only if explicitly claimed;
- dtype, rank, stride, device, and zero-length negative/compatibility cases;
- prepared-handle lifetime misuse/fail-closed behavior;
- multiple Numba allocation patterns;
- docs and claim-scan guards for the exact public wording;
- ideally at least one additional CUDA/Numba environment if approaching release
  candidate status.

## Actions Taken

- Keep `full_numba_partner_surface` open.
- Record bounded Numba M1 `DeviceNDArray` fixed-radius route evidence.
- Tighten the blocker manifest's `required_evidence` so future reviewers do not
  mistake the bounded route evidence for broad Numba support.
- Prefer public wording of the form: "Numba `DeviceNDArray` fixed-radius route
  via `__cuda_array_interface__`."
