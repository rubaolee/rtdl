# Goal 1510: Non-Pod App Classification And Pod Readiness

## Verdict

No GPU pod was available. The useful non-pod work is to prepare the app
classification and next-pod evidence path so the next paid GPU window can be
used immediately for measurement instead of planning.

This report does not add new GPU measurements, does not authorize public speedup
wording, does not authorize broad RTX wording, does not authorize true zero-copy
wording, and does not promote `COLLECT_K_BOUNDED` out of experimental status.

## Deliverables

- `docs/technical_app_notes/app_primitive_classification.md` classifies the app
  examples by primitive pattern, maturity, ownership boundary, and risk.
- `docs/technical_app_notes/app_implementation_matrix.md` already contains the
  v1.0-versus-current comparison table and detailed app notes.
- `scripts/goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh` remains
  the next-pod runner for OptiX `COLLECT_K_BOUNDED` stage profiling.

## Local Work Queue

The following work remains useful without a GPU pod:

1. Add deeper per-app notes for representative groups:
   reduction-first, split-contract, candidate-refinement, and bounded-collection
   blocked apps.
2. Add doc guards that prevent app notes from drifting into whole-app speedup,
   true zero-copy, or broad RTX claims.
3. Keep the Goal1506/Goal1508 pod runner and tests synchronized with any
   collect-k implementation changes.
4. Prepare review prompts for Claude/Gemini only when a claim boundary,
   roadmap change, or release decision is being proposed.

## Next Pod Work Queue

When a suitable NVIDIA pod is available:

1. Clone or update from Git and record `git rev-parse HEAD`.
2. Probe OS, driver, CUDA, `nvcc`, OptiX headers, and GPU name.
3. Install or link a driver-compatible OptiX SDK if headers are missing.
4. Run:

```bash
OPTIX_PREFIX=/root/vendor/optix-sdk bash scripts/goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh
```

5. Accept Goal1506 evidence only if the preflight says all requested counts are
   profile candidates and the profile probe reports parity, complete profile
   records, expected native path, and expected topology.
6. Treat local/fallback smoke output as instrumentation debugging only, not
   performance evidence.

## Acceptance Gates

Accepted pod evidence must include:

- GPU name and driver.
- OptiX SDK path or tag.
- Git commit.
- Candidate counts at least `4097`, `65537`, and `131072`.
- At least five measured repeats after warmup.
- Parity pass.
- No unexpected overflow.
- Expected row_width=2 tiled native path for the measured counts.
- Expected tile count, merge levels, sort launches, merge launches, carry
  copies, final copies, and metadata fields.
- Stage timing artifacts in JSON, Markdown, and JSONL form.
- Claim flags all false.

## Possible Troubles

- A pod GPU may expose too little opt-in shared memory for the row_width=2 tiled
  path. In that case, the run is a fallback smoke only.
- A pod driver may not match the latest OptiX SDK. Use a compatible SDK tag
  rather than assuming the newest tag works.
- End-to-end time may still be dominated by host synchronization, metadata
  downloads, or single-thread merge kernels. The stage profile should identify
  the actual bottleneck before optimization.
- Reduction-first apps may look ready while row-producing apps remain blocked
  on bounded collection. Keep these contracts separate.
- Copy reduction is not zero-copy. Python-owned host data still has a real
  transfer boundary for GPU execution.

## Claim Boundary

Goal1510 is planning and documentation work. It does not authorize release
action, public speedup wording, whole-app acceleration claims, broad RTX claims,
partner tensor handoff claims, true zero-copy wording, stable primitive
promotion, or experimental public promotion.

