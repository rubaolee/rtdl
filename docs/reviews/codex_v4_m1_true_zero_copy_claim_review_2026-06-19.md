# Codex V4.0 M1 True Zero-Copy Claim Review

Date: 2026-06-19.
Status: accepted claim-gating decision.

## Question

Can the exact V4.0 route `fixed_radius_count_threshold_2d` promote
`v4_true_zero_copy_claim_authorized` from `false` to `true`?

Route under review:

`CuPy/Numba/PyTorch CUDA point columns -> RTDL OptiX fixed-radius count/threshold -> CUDA output columns`

## Verdict

Verdict: keep `v4_true_zero_copy_claim_authorized` false.

Do not promote the claim yet.

The route is real and useful: it has a V4-prefixed Python API, borrowed CUDA
column intake, fixed-size output columns, an OptiX device-column query path, a
nonzero caller-stream query path, pointer-identity smoke evidence, and a
reproducible CuPy smoke command.

That is not enough for the public V4 true-zero-copy claim.

## After-Review Engineering Update

Prepare caller-stream support has now landed for the frozen M1 route. When a
nonzero stream is passed to `prepare_v4_fixed_radius_count_threshold_2d` or the
one-shot `run_v4_fixed_radius_count_threshold_2d`, the fixed-radius search-scene
AABB pack and OptiX GAS build are ordered on that caller stream.

This closes the specific prepare-stream blocker from the original review. It
The route metadata also now echoes the exact device pointers handed to the
native call, and the CuPy parity matrix covers supported positive cases plus
the zero-length CuPy query fail-closed boundary.
The LD_PRELOAD CUDA transfer-counter probe now covers the warmed
prepare-plus-query window and observes no device-to-host copy, no unknown copy,
and only 136 host-to-device bytes, below the small launch/setup allowance and
far below the smallest named-column size in the probe.

These updates do not promote the claim. Do not promote
`v4_true_zero_copy_claim_authorized` until the remaining evidence gates below
are satisfied.

## Reviewer Consensus

Two independent reviewers reached the same decision:

- Reviewer Meitner: no promotion. Pointer identity and hot-query evidence are
  positive, but prepare, full no-host-stage evidence, stream ordering, parity,
  and negative tests are incomplete.
- Reviewer Ohm: no promotion. The hot query uses the caller stream, but prepare
  is not caller-stream ordered and still uses the default stream/GAS path.

## Blocking Reasons

1. Prepare was not caller-stream ordered at review time. This is now closed for
   the frozen M1 route.

   The V4 Python prepare surface now passes the caller stream into native
   fixed-radius search preparation. The device-search AABB pack and GAS build
   are ordered on that stream for the M1 fixed-radius count/threshold route.

2. No transfer-counter or equivalent no-host-stage evidence covered both
   prepare and query at review time. This is now improved for the frozen M1
   route.

   The reproducible smoke proves pointer identity and audits the hot query
   source path. The new transfer-counter probe also covers the warmed
   prepare-plus-query route. It observes no host-stage copy of named
   search/query/output columns. It does observe internal device-to-device
   staging for device-resident AABB/BVH work, so public true-zero-copy wording
   remains gated pending wording review.

3. Correctness parity was too small at review time. This is now improved for
   the frozen M1 route.

   The route now has a reproducible CuPy parity matrix against CPU/reference
   behavior for smoke, miss, boundary, threshold cap, and deterministic random
   cases. Zero-length CuPy query columns are recorded as a deterministic
   fail-closed boundary because CuPy exposes a zero data pointer for that case.

4. The fail-closed matrix needs to stay broad.

   The route now tests more negative contracts, including host arrays, bad
   ranks, bad strides, bad output dtype/shape, and mixed devices. Promotion
   should continue requiring these tests and any new stream/layout negatives.

5. The evidence report is a snapshot, not the current-head gate.

   The canonical current-head gate is the reproducible command:

   ```bash
   PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_cupy_stream_smoke.py
   ```

   The checked-in JSON report records a passing snapshot and claim boundary.
   Current HEAD must rerun the script plus `v4_active` before any claim change.

## Allowed Wording Now

Allowed:

- V4.0 has a first fixed-radius count/threshold Python GPU operator route.
- The route accepts caller-owned CUDA point columns.
- The hot query writes caller-owned CUDA output columns.
- The hot query can use a nonzero caller CUDA stream and synchronizes before
  return.
- The CuPy smoke observes pointer identity and correct output for the exact
  smoke case.

Not allowed:

- true-zero-copy claim for V4.0;
- async completion claim;
- broad fixed-radius family claim;
- speedup claim;
- RTX RT-core speed claim from the GTX 1070 validation host.

## Required Before Promotion

- Prepare path uses the caller stream for the frozen M1 route and keeps that
  source-audited in the CuPy smoke gate.
- Evidence packet covers both prepare and hot query.
- Transfer-counter evidence proves no host staging of named search, query, or
  output columns for the warmed M1 route.
- Native-call metadata echoes/records the exact consumed pointer identities for
  the frozen M1 route.
- Stream-order proof covers producer stream, prepare stream, query stream, and
  consumer stream behavior.
- Public true-zero-copy wording is reviewed against the internal
  device-to-device AABB/BVH staging that the no-host-stage probe records.
- Correctness parity matrix covers supported deterministic, randomized, miss,
  boundary, radius, and threshold cases, with zero-length CuPy query columns
  documented as fail-closed.
- Fail-closed matrix remains active for host arrays, mixed devices,
  non-contiguous/sliced columns, bad ranks, bad output dtype/shape/device, and
  unsupported layout/stream cases.
