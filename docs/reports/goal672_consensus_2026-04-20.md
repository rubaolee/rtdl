# Goal 672 Consensus

Date: 2026-04-20

## Verdict

ACCEPT.

## Basis

- Codex implemented and tested the OptiX prepacked 2-D ray buffer API locally and on Linux.
- Claude completed a detailed implementation review and returned `APPROVED`.
- Gemini Flash returned `LIMITED ACCEPT`, agreeing that the claim boundary is honest while noting it did not complete full code inspection in the CLI session.

## Consensus Claim

Goal 672 is a valid performance improvement for the narrow repeated-query contract:

- prepared 2-D OptiX any-hit triangle scene,
- prepacked/uploaded 2-D ray batch,
- scalar blocked-ray count output,
- repeated calls over the same ray batch.

The benchmark evidence supports a speedup on the tested Linux OptiX host:

- existing unprepared any-hit row output median: `0.005031049 s`
- Goal 671 prepared scene with unpacked rays median: `0.008270310 s`
- Goal 672 prepared scene plus prepacked rays median: `0.000075006 s`

## Non-Claims

Do not claim this speedup for:

- one-shot queries,
- changing ray batches,
- full emitted-row output,
- all OptiX workloads,
- Vulkan, HIPRT, Embree, or Apple RT.

Goal 672 does not supersede Goal 671's finding that prepared scene plus unpacked rays is slower than existing row output on the dense probe.

