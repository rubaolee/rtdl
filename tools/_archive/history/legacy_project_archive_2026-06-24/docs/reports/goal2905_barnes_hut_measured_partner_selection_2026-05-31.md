# Goal2905: Barnes-Hut Uses Measured Partner Selection

Date: 2026-05-31
Status: implemented pending clean current-commit pod artifact

## Purpose

Goal2902 marked `barnes_hut` as a performance target because the Triton grouped vector-sum preview was slower than Torch on the measured shape. That was a useful warning, but it was not the right app-level conclusion for v2.5.

The v2.5 principle is user-selectable partners. If Torch is faster for a generic grouped vector sum, the app should select Torch as the current performance path and keep Triton as an explicit preview, not pretend that Triton must be the default.

## Change

The Barnes-Hut consolidated harness now records:

- `selected_partner`
- `selected_partner_median_sec`
- `selected_partner_reason`
- `triton_preview_promoted`

The v2.5 triage script now treats Barnes-Hut as current-path acceptable when a measured non-Triton partner is selected for the vector continuation. Triton remains visible, measured, and unpromoted.

## Design Boundary

This does not remove Triton and does not make Torch a hidden requirement. It makes partner choice explicit:

- RTDL/OptiX handles the generic RT membership/frontier stage.
- The selected partner handles the generic grouped vector-sum continuation.
- Triton remains available for explicit experiments, but it is not auto-selected until it wins same-contract timing.

No native app-specific engine logic is added.

## Next Validation

Run a clean pod artifact after this change lands and refresh the current packet triage. If the measured Torch selection remains stable, Barnes-Hut should no longer appear as a current severe performance target.
