# Goal5847 AOT Startup Preregistration

Status: `FROZEN_BEFORE_FORMAL_GPU_TRANSACTION`

Frozen at 2026-09-05T14:33:51Z, before any formal worker was launched.
The machine-readable authority is `PREREGISTRATION.json`, whose internal
preregistration seal is
`ae3fd31e2d862b55bea54f9d2e55f1346453ae1e5ed11cb24daddc4b0589e511`.

## Question

Can one signed, family-bound, deploy-only RTDL artifact produce the same exact
4,096-row bounded-relation result as pinned PyOptix consuming precompiled PTX,
without RTDL loading or invoking NVRTC, while preserving true OptiX traversal
evidence, fail-closed admission, and Goal5845 prepared-steady performance?

## Frozen Implementation

- Source commit: `11096b168eadccff0511c6e9e8f57234c58ce10a`
- Source tree: `76e942b63df3e55c2a8337b77f13be4d220a3fad`
- Minimal AOT DSO SHA-256:
  `90657541102ee20b78d27143b7634f7a47aa12283e087cdbd9a985a72b040bd9`
- Relation artifact SHA-256:
  `eef2c1fc2f7e2edd4316d4c020a5655be96660fcce97146caded49a270465d23`
- Triangle artifact SHA-256:
  `d8054ff58a7ff36be2d4a557f3abf4098fcabff73d17dd5f92fa04dd5b420a2b`
- PyOptix commit: `3144f224c0fd18733925faf3d8fb82c7376b8dcf`
- PyOptix tree: `0bf0ec24efb4a43f129aee25dd265aa8149374e3`
- Precompiled PTX SHA-256:
  `7f79eb31ff6eedaf25c24e0910bf2989b576b13a883a4a2e5c840f72b6203b2d`

## Frozen Design

- Eight balanced blocks, with arm order alternating by block.
- One fresh process per arm per block, for 16 workers total.
- Each worker performs 16 warmups and retains all 128 measured steady samples.
- The primary estimand starts in the controller immediately before process
  spawn and ends after the first exact-correct result.
- The secondary estimand starts after each implementation import and ends at
  the same first exact-correct result.
- Steady timing covers complete same-output execution; correctness validation
  occurs outside each timed action for both arms.
- Git and hardware instrumentation occur after the primary endpoint.
- No exploratory timing sample may be pooled into the formal transaction.

## Frozen Gates

- Median within-block primary RTDL/PyOptix ratio: at most `0.50x`.
- Worst primary block ratio: at most `0.75x`.
- Median within-block post-import ratio: at most `3.0x`.
- Worst post-import block ratio: at most `4.0x`.
- Pooled steady RTDL/PyOptix median ratio: at most `0.20x`.
- Pooled RTDL steady median / Goal5845 reference (`366,340 ns`): at most
  `1.25x`.
- Every worker, exact oracle, identity, compiler-absence, and true-OptiX gate
  must pass; all 1,024 samples per arm must be retained.

## Claim Boundary

This is internal engineering work. It does not authorize public or manuscript
performance wording, arbitrary-workload or cross-hardware generalization,
production signing claims, external-review claims, or consensus claims.
PyOptix consumes precompiled PTX and the harness does not invoke a source
compiler, but its CuPy dependency stack may still map NVRTC. RTDL must show
zero runtime-compiler attempts, zero compiler modules, and zero NVRTC mappings.

