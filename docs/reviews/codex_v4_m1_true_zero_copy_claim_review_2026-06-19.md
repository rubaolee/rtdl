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

## Reviewer Consensus

Two independent reviewers reached the same decision:

- Reviewer Meitner: no promotion. Pointer identity and hot-query evidence are
  positive, but prepare, full no-host-stage evidence, stream ordering, parity,
  and negative tests are incomplete.
- Reviewer Ohm: no promotion. The hot query uses the caller stream, but prepare
  is not caller-stream ordered and still uses the default stream/GAS path.

## Blocking Reasons

1. Prepare is not caller-stream ordered.

   The V4 Python prepare surface accepts/captures stream metadata, but the
   current prepared scene path does not pass the caller stream into native
   fixed-radius search preparation. The device-search AABB pack and GAS build
   still use default stream behavior and synchronize before returning.

2. No transfer-counter or equivalent no-host-stage evidence covers both prepare
   and query.

   The reproducible smoke proves pointer identity and audits the hot query
   source path. It does not yet provide CUPTI/transfer-counter/equivalent
   evidence across the entire prepare-plus-query route. Scalar launch parameter
   upload is acceptable, but search/query/output column staging must be proven
   absent.

3. Correctness parity is too small.

   The CuPy smoke has a deterministic three-query case. Promotion needs a parity
   matrix against CPU/reference behavior across radius, threshold, empty, miss,
   boundary, and randomized cases.

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

- Prepare path either uses the caller stream or rejects nonzero prepare streams
  until an explicit prepared-scene stream contract exists.
- Evidence packet covers both prepare and hot query.
- Transfer-counter or equivalent no-host-stage evidence proves no host staging
  of search, query, or output columns.
- Native metadata or an equivalent audit echoes/records the exact consumed
  pointer identities.
- Stream-order proof covers producer stream, prepare stream, query stream, and
  consumer stream behavior.
- Correctness parity matrix covers deterministic, randomized, empty, miss,
  boundary, radius, and threshold cases.
- Fail-closed matrix remains active for host arrays, mixed devices,
  non-contiguous/sliced columns, bad ranks, bad output dtype/shape/device, and
  unsupported layout/stream cases.
