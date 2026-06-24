# Goal2220: Gemini Independent Review of Goal2219 OptiX PIP Device Prefilter Pod Evidence

As an independent external AI reviewer, distinct from Codex, I have reviewed the evidence presented for Goal2219 regarding the OptiX PIP device prefilter.

## Review Findings:

1.  **Default Path Parity:** The evidence confirms that the default path, with no `RTDL_OPTIX_PIP_DEVICE_PREFILTER` environment variable set, preserves CPU/Embree/OptiX parity on `8686` rows. The "Result" table shows `8686` rows for all backends (`cpu`, `embree`, `optix`) with `true` parity against the CPU reference. This satisfies check 1.

2.  **Narrow Engineering Claim Support:** The report supports the claim of improved RTDL OptiX PIP performance. The median OptiX time for Goal2219 is `0.121710 s`. The "Delta" section indicates a `33.75x` speedup over Goal2209 (implying an original time of approximately `4.108 s`) and a `5.08x` speedup over Goal2213 (implying an original time of approximately `0.618 s`). This confirms the improvement from previous goals to the current `0.121710 s`. This satisfies check 2.

3.  **Candidate Reduction Claim Support:** The "Phase Telemetry" section clearly shows the candidate reduction: conservative GPU candidates decreased from `2797698` (before default prefilter) to `8793` (after default prefilter), while emitted rows remained consistent at `8686` in both cases. This satisfies check 3.

4.  **No Overclaiming:** The "Claim Boundary" section explicitly states that the evidence does not authorize claims such as "RTDL beats RayJoin," "broad RT-core speedup claims," "paper-scale RayJoin reproduction," or "v2.0 release readiness." The "Interpretation" section further reinforces that the result is "still not a RayJoin paper reproduction" and is "much slower than RayJoin's specialized RT query phase." This demonstrates appropriate bounding of claims and satisfies check 4.

5.  **Potential for Misleading Wording:** The report is careful in its language. While "default path" is used, the "Claim Boundary" section clearly distinguishes it from "release-ready" and advises against public performance narratives without further review. No specific wording was found that, in context, could mislead a public performance narrative beyond what is already addressed by the explicit claim boundaries. This satisfies check 5.

## Verdict: `accept`

The evidence provided for Goal2219 thoroughly supports the narrow engineering claim, demonstrates parity across backends, and clearly defines the boundaries of its claims. The report is well-structured and transparent about its implications.
