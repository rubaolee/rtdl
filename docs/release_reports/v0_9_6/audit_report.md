# RTDL v0.9.6 Audit Report

Status: released as `v0.9.6`.

Date: 2026-04-21

## Audit Scope

This audit checks whether the post-`v0.9.5` current-main optimization work is
packaged coherently as the `v0.9.6` release.

The release includes:

- native/native-assisted any-hit completion for Vulkan and Apple
  RT;
- Apple RT prepared/prepacked scalar visibility-count optimization;
- OptiX prepared/prepacked scalar 2D any-hit count optimization;
- HIPRT prepared 2D any-hit reuse;
- Vulkan prepared 2D any-hit plus packed-ray support;
- public documentation refresh;
- public history catch-up and stale history database repair;
- local and Linux release-gate evidence through Goal684.

## Test Audit

Recorded release-gate evidence:

- full local discovery after release packaging: `1274` tests OK, `187` skips
- public command truth audit: valid, `250` commands across `14` docs
- public entry smoke: valid
- focused public release-doc tests: `20` tests OK
- focused history regression: `4` tests OK
- `git diff --check`: clean

Recorded Linux backend evidence:

- fresh OptiX, Vulkan, and HIPRT backend builds passed on `lx1`
- focused native Linux suite: `30` tests OK, `2` Apple RT skips
- all Linux performance sanity paths returned expected count `4096`

## Documentation Audit

The public docs now distinguish:

- the previous released `v0.9.5` tag boundary;
- native/native-assisted backend improvements after `v0.9.5`;
- prepared/prepacked repeated visibility/count performance evidence;
- scalar-count versus full emitted-row output;
- GTX 1070 evidence versus RT-core evidence;
- HIPRT/Orochi CUDA on NVIDIA versus AMD GPU validation.

## Flow Audit

The release flow is complete:

- implementation reports exist for Apple RT, OptiX, HIPRT, and Vulkan
  optimization goals;
- closure and documentation refresh were accepted by Codex, Claude, and Gemini;
- local broad gate passed;
- fresh Linux backend gate passed;
- history catch-up passed and was accepted by Codex, Claude, and Gemini;
- post-history release gate passed and was accepted by Codex, Claude, and
  Gemini;
- final local candidate gate passed and was accepted by Codex, Claude, and
  Gemini;
- release-level flow audit passed and was accepted by Codex, Claude, and
  Gemini;
- maintainer authorized release after public docs and flow audit were updated.

## Known Non-Claims

This release rejects these claims:

- RTDL is broadly faster for DB or graph workloads because of the
  visibility/count work;
- one-shot direct calls inherit prepared/prepacked speedups;
- Apple RT full emitted-row output beats Embree;
- the GTX 1070 measurements prove RT-core speedup;
- HIPRT is validated on AMD GPU hardware;
- Apple DB or graph workloads use Apple MPS ray-tracing traversal;
- unreviewed single-developer-only release action.

## Audit Verdict

No release blocker is known in code, docs, tests, or flow.
