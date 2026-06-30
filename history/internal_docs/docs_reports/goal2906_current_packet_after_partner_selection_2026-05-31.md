# Goal2906: Current Packet After Measured Partner Selection

Date: 2026-05-31
Status: accepted as internal current-packet evidence

## Purpose

Goal2906 reruns the current seven-app canonical packet after Goal2905 made Barnes-Hut choose its measured fastest vector-sum partner instead of treating Triton as the mandatory continuation path.

## Pod Packet

Artifact directory:

`docs/reports/goal2906_current_packet_after_partner_selection_pod/`

Summary:

- source commit: `1756dce2386cd086aa91edce8e2656ce8d8899f2`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- seven-app canonical packet: `7 / 7` passed
- packet elapsed time: `422.873 s`
- claim-boundary violations: none
- dirty artifacts: none

## Triage Result

Triage artifact:

`docs/reports/goal2906_current_packet_after_partner_selection_triage_2026-05-31.json`

Barnes-Hut is no longer a current target:

- OptiX membership speedup vs Embree: up to `150.232x`
- selected vector-sum partner: `torch`
- selected vector-sum partner median: `0.000938 s`
- Triton/Torch vector-sum ratio: `4.400x`
- classification: `current_path_acceptable_with_measured_partner_selection`

RTNN is recorded as near-parity/distribution-dependent after the triage rule from Goal2907:

- weakest row: `uniform`, `0.980x` CuPy/RTDL
- stronger rows: `clustered`, `2.456x`; `shell`, `1.985x`
- classification: `current_path_acceptable_near_parity_distribution_dependent`

The only remaining target in this packet artifact is Hausdorff, because this packet predates the Goal2907 repeat-stability default and used repeat-3 timing:

- packet ratio: `1.401x` RTDL/CuPy
- Goal2907 repeat-9 direct probe: `1.056x` RTDL/CuPy

## Interpretation

The packet confirms the v2.5 partner-selection principle:

- if Torch/CuPy wins a generic continuation, use it explicitly;
- keep Triton visible as a preview until it wins same-contract timing;
- do not add app-specific native engine logic just to force a partner choice.

It also shows why short-row performance evidence needs stable repeat counts. Hausdorff was not regressed semantically; the repeat-9 probe keeps the same exact RTDL/OptiX path in the near-parity band.

## Boundary

This is not release consensus and not a v2.5 release packet.

It does not authorize public speedup claims, broad RT-core claims, whole-app speedup claims, true-zero-copy claims, automatic Triton selection, package-install claims, or paper-reproduction claims.
