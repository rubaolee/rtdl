# Goal678/679 External Review — Claude

Date: 2026-04-20

Verdict: **ACCEPT**

## Summary

The Goal678 local gate and Goal679 Linux GPU gate together constitute sufficient
release-gate evidence for the current cross-engine prepared/prepacked
visibility/count optimization round. The claim boundaries are honest and
consistently applied across every document reviewed.

## Gate Completeness

Goal678 covers all required local checks:

- Full unittest discovery: `1266` tests OK, `187` skips. Skips are expected
  optional backend tests absent on the local macOS host.
- Public command truth audit: `250` commands across `14` docs, valid.
- Public entry smoke: valid.
- Focused public-doc consistency tests: `10` tests OK.
- `git diff --check`: clean.
- Flow audit: coherent six-step chain from Goal669 through Goal677.

Goal679 covers the required Linux backend gate:

- Fresh sync to `/tmp/rtdl_goal679` with stale build artifacts excluded.
- All three backends rebuilt successfully from that synced source:
  OptiX `(9, 0, 0)`, Vulkan `(0, 1, 0)`, HIPRT `(2, 2, 15109972)`.
- Focused native correctness suite: `30` tests OK, `2` Apple RT skips (correct
  and expected — Apple RT is a macOS backend).
- Performance sanity: all three backends returned the expected any-hit count
  (`4096 / 4096`) for both direct and prepared/prepacked paths. The prepared
  path was faster than the direct path for all three backends.

No gap was found between the local gate and the Linux gate. The JSON artifact
for Goal679 is internally consistent with the Markdown report and the summary
in the review request.

## Boundary Verification

The following boundaries are explicitly stated and consistently applied in every
primary and supporting document:

- **No RT-core claim.** The GTX 1070 has no NVIDIA RT cores. Every document
  that references the Linux OptiX or Vulkan timing marks this boundary. The
  claim is restricted to backend integration and repeated-query behavior on this
  host.
- **No AMD GPU claim.** The HIPRT measurements are HIPRT/Orochi CUDA running on
  the NVIDIA GTX 1070, not on AMD hardware. Every document that cites the HIPRT
  speedup carries this boundary explicitly.
- **Workload scope.** The performance results are for repeated 2D visibility /
  any-hit / blocked-ray count workloads. No document extends them to DB
  workloads, graph workloads, one-shot calls, or full emitted-row output.
- **Output contract.** The prepared/prepacked paths use narrower output
  contracts (scalar counts or compact yes/no rows) relative to full materialized
  row dictionaries. The benefit is conditional on the app being able to consume
  that narrower contract.
- **Vulkan condition.** The Vulkan win requires prepacked rays. The claim is not
  that prepared tuple-ray calls are faster without prepacking.
- **Apple RT scope.** Apple RT is not re-validated by the Linux gate. The
  earlier local Apple M4 gates cover it, and the Linux report acknowledges this
  explicitly.

None of these boundaries are violated anywhere in the reviewed documents.

## Preceding Consensus

Goal674 (HIPRT prepared 2D any-hit) and Goal676/677 (cross-engine closure and
doc refresh) were accepted by Codex, Claude, and Gemini. Goal675 (Vulkan
prepared 2D any-hit plus packed rays) was accepted by Codex and Gemini; the
Claude CLI stalled without producing a verdict file. Goal678/679 build
correctly on that prior consensus; no reopened issue was found.

## No Blockers

No file, command, or claim requires correction. The release-gate evidence is
sufficient for the current optimization round.
