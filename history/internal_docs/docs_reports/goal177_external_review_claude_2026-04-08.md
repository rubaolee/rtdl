# Goal 177 External Review: Claude

## Verdict

The symmetric two-star equator geometry and uniform phase-mode logic are
correctly implemented and almost entirely well-tested, but one existing test —
`test_numpy_and_scalar_shading_match_for_same_hit` — was not updated to match
the new multi-light API and will fail with a `TypeError` at runtime.

## Findings

- Symmetric two-star equator full-pass:
  - `_frame_light` places the primary star at `x = 68 − 136·phase`
  - `_secondary_frame_light` places the secondary at `x = −68 + 136·phase`
  - both remain locked to `y = 0.08, z = 11.8`
  - the pair is exactly x-mirrored on the equatorial plane
  - the primary remains slightly stronger than the secondary
- Uniform phase mode:
  - `_orbit_phase_samples(..., mode="uniform")` uses linear spacing
  - the uniform-mode test checks the exact expected tuple
  - summary round-trip coverage also persists `phase_mode`
- Stale test, now fixed:
  - `test_numpy_and_scalar_shading_match_for_same_hit` originally called the
    old single-light API with removed `light=` and `shadow_factor=` parameters
  - the test has been updated to the current multi-light API:
    - `lights=(_frame_light(0.15),)`
    - `shadow_lookup={}`
    - `light_count=1`

## Summary

The core production code is clean: equator-symmetric dual-star sweep and
uniform-mode linear sampling both match their intended behavior. Claude found
one real stale-test issue in the NumPy/scalar parity test, and that issue has
been fixed locally before final closure.
