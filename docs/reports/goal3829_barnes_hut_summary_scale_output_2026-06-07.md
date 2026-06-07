# Goal3829 Barnes-Hut Summary Scale Output

Date: 2026-06-07

Status: implemented locally; A5000 scale-profile refresh pending.

## Purpose

Goal3828 proved that file-backed stdout prevents false timeouts for JSON-heavy
benchmark apps. Barnes-Hut still emitted about 893 KB of force rows for the
8192-body Numba scale profile, even though the scale registry only needs to
prove the computation and preserve checksums.

Goal3829 makes the Barnes-Hut scale profile use bounded summary output:

- the app-level partner exact-force path now always records force checksums,
- the benchmark wrapper exposes `--force-output-mode full|force_summary`, and
- the current scale-profile registry uses `--force-output-mode force_summary`
  for the 8192-body Barnes-Hut Numba row.

## Boundary

This is output/materialization hygiene for benchmark execution. It does not
change the Numba force kernel. It does not add RT-core acceleration to
Barnes-Hut force computation, and does not authorize release action, public
speedup wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, or app-specific
native-engine logic.

## Next Validation

Refresh the Goal3828 A5000 scale-profile artifact at the current commit and
verify that `barnes_hut_numba_scale_default_8192` still passes while emitting a
small summary payload instead of full per-body force rows.
