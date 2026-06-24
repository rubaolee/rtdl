# Codex V4.0 M1 True Zero-Copy Wording Consensus

Date: 2026-06-19.
Status: accepted 2+AI release-gating decision.

## Decision

Keep `v4_true_zero_copy_claim_authorized` false for the V4 M1 route
`fixed_radius_count_threshold_2d`.

The current evidence is strong enough for:

- caller-owned CuPy CUDA input columns;
- caller-owned CuPy CUDA output columns;
- prepare plus query on a nonzero caller CUDA stream;
- native pointer echo for search, query, and output columns;
- CuPy parity matrix against CPU reference cases;
- LD_PRELOAD transfer-counter evidence showing no observed host-stage copy of
  named search/query/output columns in the warmed prepare-plus-query window.

It is not strong enough for unqualified public true-zero-copy wording because
the measured route still has internal device-to-device AABB/BVH staging and
synchronizes before return.

## Reviewer Consensus

Reviewer A: keep the public V4 true-zero-copy flag false. Allowed wording is
no observed host-stage copy of named columns. Forbidden wording includes
end-to-end zero-copy, no copies, async, and speedup claims.

Reviewer B: keep the public V4 true-zero-copy flag false. The release-safe
short wording is: zero-copy device-column handoff with no observed host staging
of named columns, not end-to-end true zero-copy.

## Allowed Wording

Allowed:

- V4.0 M1 has a CuPy fixed-radius count/threshold GPU operator route over
  caller-owned CUDA columns.
- The route borrows caller-owned CUDA input columns and writes caller-owned
  CUDA output columns.
- Prepare and query can run on a nonzero caller CUDA stream.
- The route synchronizes before return; async completion is not claimed.
- The checked LD_PRELOAD probe observed no host-stage copy of named
  search/query/output columns in the warmed prepare-plus-query window.
- The probe observed 136 bytes of host-to-device launch/setup traffic and
  98,304 bytes of internal device-to-device AABB/BVH staging.

Short allowed phrase:

`zero-copy device-column handoff with no observed host staging of named columns`

## Forbidden Wording

Forbidden:

- `v4_true_zero_copy_claim_authorized = true`;
- public true-zero-copy wording without qualification;
- end-to-end zero-copy;
- no copies;
- no staging;
- no host-to-device copies;
- async, non-blocking, or returns before GPU work completes;
- RT-core speedup, RTX speedup, or faster-from-this-evidence claims;
- all fixed-radius routes;
- PyTorch or Numba validation for this route without separate evidence.

## Required Fence

The V4 metadata should prefer the explicit public-safe field:

`named_cuda_columns_no_host_stage_authorized`

The older/narrower native-field wording may remain for compatibility only if it
is fenced by `v4_true_zero_copy_claim_authorized = false` and by explicit
internal device-staging disclosure.

## Remaining Gates

- Public true-zero-copy wording review must define whether internal
  device-to-device AABB/BVH staging is compatible with the term. The current
  consensus says no; use no-host-stage named-column wording instead.
- Stream-order proof still needs to cover producer stream, prepare stream,
  query stream, and consumer stream behavior beyond synchronous same-stream
  execution.
- Async remains blocked until the route returns an event/dependency or another
  explicit completion contract and stops synchronizing before return.
- RTX RT-core speed claims remain blocked until measured on suitable RTX
  hardware with route-specific baselines.
