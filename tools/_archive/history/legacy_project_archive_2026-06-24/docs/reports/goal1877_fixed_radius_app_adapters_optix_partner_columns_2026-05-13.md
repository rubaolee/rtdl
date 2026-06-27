# Goal1877 - Fixed-Radius App Adapters Over OptiX Partner Columns

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1877 adds app-level Python adapters over the generic Goal1875 OptiX
fixed-radius partner bridge:

- `service_coverage_gap_flags_optix_partner_device_columns(...)`
- `event_hotspot_flags_optix_partner_device_columns(...)`

The native engine still sees only:

`generic_fixed_radius_count_threshold_2d_device_columns`

App semantics stay in Python:

- service coverage uses `threshold=1`, then inverts covered flags to produce
  uncovered flags;
- event hotspot screening includes the self-neighbor, so the native threshold is
  `hotspot_threshold + 1`.

## Boundary

This goal does not create accepted v2.0 performance rows by itself. The app
adapters now exist, but they still require pod timing artifacts and external
review before the two fixed-radius apps can be used as v2.0 performance
evidence.

No v2.0 release claim, whole-app speedup claim, broad RT-core speedup claim,
arbitrary partner acceleration claim, or package-install claim is authorized.

## Pod Evidence

Pod:

- SSH target: `root@213.192.2.116 -p 40189`
- key used by Codex: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- checkout: `/root/rtdl`
- base commit before Goal1877 patch: `95907895`

Validation:

- `PYTHONPATH=src:. python3 -m unittest tests.goal1877_fixed_radius_app_adapters_optix_partner_columns_test tests.goal1875_fixed_radius_optix_partner_device_columns_test`
- Torch CUDA service/hotspot smoke
- CuPy CUDA service/hotspot smoke

Observed service coverage fixture:

- nearby clinic counts: `[1, 0, 1]`
- uncovered flags: `[0, 1, 0]`

Observed event hotspot fixture:

- neighbor counts including self: `[2, 2, 1]`
- hotspot flags: `[1, 1, 0]`

Both Torch and CuPy matched those expected outputs.

## Next Step

Run pod timing for both fixed-radius app adapters against the v1.8 prepared
fixed-radius baseline and the Goal1873 partner-reference path.
