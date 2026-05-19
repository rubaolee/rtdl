# Goal2382 Copilot Non-Consensus Review: Goal2381 Ranked Rows

Date: 2026-05-19

Reviewer: GitHub Copilot CLI. This is a non-consensus sanity review only. It
does not replace a Claude or Gemini review for RTDL consensus accounting.

Verdict: `accept-with-boundary`

## Findings

Goal2381 wires the native, Python, runner, pod-runner, report, and test surface
for prepared fixed-radius 3D ranked witness rows. The implementation remains
app-agnostic: the new ABI names use fixed-radius neighbor terminology rather
than RTNN- or app-specific naming.

The `RtdlKnnNeighborRow` layout is asserted on the C++ side and the Python
runtime uses the matching ctypes row view. The pod artifacts report
`ok: true`, `result_mode: ranked-raw`, `exact_refine: 0.0`, and
`device_ranked_witness_rows: true`.

## Boundaries

The report correctly keeps the claim narrow:

- no RTNN paper-equivalence claim;
- no RT-core neighbor-search claim;
- no arbitrary ANN claim;
- no broad nearest-neighbor acceleration claim.

The clean pod rerun shows that the 262,144-row case beats the old Goal2371
host-refined path, while the 65,536-row case should not be treated as a speedup
because setup/upload variability dominates it.

## Residual Risks

- The ranked continuation is bounded to `k_max <= 64`.
- Performance remains distribution- and hardware-sensitive.
- The next larger design need is still device-resident grouped/ranked
  continuation or reduction, not another app-specific native path.
