# Goal5847 AOT Startup Successor Preregistration V2

Status: `FROZEN_BEFORE_FORMAL_GPU_TRANSACTION`

Frozen at 2026-09-05T14:40:41Z, after preserving terminal Attempt 01 and
before launching any successor formal worker. The machine-readable authority
is `PREREGISTRATION_V2.json`, with internal seal
`34b977a163a21090d0820b1f6b2dafc6e9723ff9d7635d75bd0afa85bdd8d433`
and file SHA-256
`d72f38459bcfa283373a43258a000498c574cb37a428334485b86cf36ae93975`.

## Successor Boundary

Attempt 01 remains terminal and unpooled. V2 changes only the controller's
receipt recount: it invokes the canonical strict traversal-receipt verifier
against the full nested receipt schema. The verifier binds exact provider,
output, route, program bundle, two successful launches, and 8,192 raygen
invocations. A unit test proves a valid full receipt passes and a nested launch
count mutation remains rejected even after the forged receipt is re-sealed.
The archived Attempt 01 receipt also passes the repaired verifier.

## Frozen Implementation And Inputs

- Source commit: `f5e337feef6829e063c6aff06f4e8bd6d5466b3b`
- Source tree: `c276d64342bf17fee77b7ab0cf66ef5060c73341`
- Minimal AOT DSO SHA-256:
  `6f695bc006114087aa85303f1faeb3f8d1dd2ffb8fab2256206ce6b3e42ec6a4`
- Candidate manifest file SHA-256:
  `b002957fe9405ee97ab76a05656ceeea594514e0c8adcc59a16fc83d0923233d`
- Candidate manifest internal seal:
  `6198d9dd8534bf16d90636e390c3aef7015f7b7f71e752324be96f2324001508`
- Relation artifact SHA-256:
  `7ee22c3baeb3f253e47b0fc58323c259b38ba11d1d79e031101e27eddb05ef47`
- Triangle artifact SHA-256:
  `e945c9d65c1ff4ecf95e3a189af7170c287aa6b07d4919ab1435b6a7abe54e4f`
- PyOptix commit/tree:
  `3144f224c0fd18733925faf3d8fb82c7376b8dcf` /
  `0bf0ec24efb4a43f129aee25dd265aa8149374e3`
- Precompiled PTX SHA-256:
  `7f79eb31ff6eedaf25c24e0910bf2989b576b13a883a4a2e5c840f72b6203b2d`

The experimental design, exact task, pass gates, compiler-absence facts, and
claim boundaries are unchanged from V1. Eight balanced blocks create 16 fresh
workers; each arm retains 1,024 steady samples with no discards. No Attempt 01
or exploratory sample is eligible for V2.

