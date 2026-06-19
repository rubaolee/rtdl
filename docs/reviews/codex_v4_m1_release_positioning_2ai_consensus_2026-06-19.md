# Codex V4 M1 Release Positioning 2-AI Consensus

Date: 2026-06-19
Status: accepted release-positioning decision
Scope: V4.0 M1 after fixed-radius CuPy route evidence

## Decision

Do not promote V4.0 to the current user release/front door yet.

Keep `v3.0.2` as the current source-tree release. Label V4 as:

> experimental V4.0 M1 evidence / active engineering preview, not current release.

This decision was reviewed by two independent agents:

- Franklin: do not promote V4.0; keep v3.0.2 current; add a V4 M1 experimental status packet and release-positioning guard.
- Leibniz: do not promote V4.0; keep v3.0.2 current; add a V4 M1 experimental status page and guard against premature current-release wording.

## Why

V4 M1 is real, but it is not release-positioned yet.

What V4 M1 has:

- one experimental CuPy route: `fixed_radius_count_threshold_2d`;
- caller-owned CUDA `ids`, `x`, `y` input columns;
- caller-owned CUDA `query_ids`, `neighbor_counts`, and `threshold_flags` output columns;
- nonzero caller CUDA stream propagation through prepare and query, synchronously;
- pointer echo, parity, no-host-stage probe, and raw benchmark-probe evidence;
- a 32-test `v4_active` gate on latest validated head `95b724159e9e6e0e1ab734850ceede2c3a7ca692`.

What V4 M1 does not have:

- no release identity;
- no `v4.0.0` version marker;
- no current release packet;
- no release-candidate closeout;
- no stable SDK or package-install claim;
- no public true-zero-copy claim;
- no async/nonblocking claim;
- no RTX/RT-core speedup claim;
- no PyTorch, Numba, JAX, or DLPack route evidence.

## P0 Blockers To Current Release Promotion

1. There is no V4 release packet, tag-preparation record, closeout, or front-door validation contract.
2. The V4 design packet remains an engineering design/review contract, not a release note.
3. The evidenced product route is one CuPy route only, not a validated whole Python GPU ecosystem surface.
4. Public true-zero-copy remains blocked by internal device staging and the synchronous contract.
5. Async remains blocked because the route synchronizes before return.
6. Speed wording remains blocked because current benchmark evidence is raw route timing on GTX 1070, not RTX/RT-core hardware evidence.
7. Before any future release action, evidence must be refreshed and bound to the final release-candidate commit.

## Allowed Wording

- "V4.0 M1 has an experimental CuPy fixed-radius count/threshold GPU operator route."
- "The route borrows caller-owned CUDA input columns and writes caller-owned CUDA output columns."
- "Zero-copy device-column handoff with no observed host staging of named columns."
- "Nonzero caller CUDA streams are propagated through prepare and query; the route synchronizes before return."
- "The benchmark probe records raw route-scoped timings only and does not authorize public speedup wording."

## Forbidden Wording

- "V4.0 is the current release."
- "Stable V4 SDK."
- "Package install", "PyPI", or "wheel" support.
- "Generated bindings" or "public multi-language C ABI release."
- "True zero-copy", "end-to-end zero-copy", "no copies", "no staging", or "no H2D copies."
- "Async", "nonblocking", or "returns before GPU work completes."
- "RT-core speedup", "RTX speedup", "RTDL is faster", or broad performance claims.
- "CuPy/Numba/PyTorch validated" unless separate route evidence exists for each named framework.

## Required Actions From This Consensus

- Keep `README.md`, `docs/README.md`, `docs/release_reports/README.md`, `VERSION`, and `pyproject.toml` on `v3.0.2`.
- Do not create `docs/release_reports/v4_0/` as a current release package yet.
- Add a compact V4 M1 experimental status packet under engineering docs.
- Link that packet from engineering/audit context, not the learner front door.
- Add a guard so V4 cannot be named current release while M1 claim flags remain blocked.

## Next Release-Track Gates

V4 can be reconsidered for current release/front-door promotion only after a release-candidate gate exists and is validated. At minimum, that gate must include:

- release packet;
- version marker decision;
- latest-candidate evidence refresh;
- current docs/front-door update plan;
- no stale V3/V4 contradiction;
- explicit claim-boundary review;
- 2+AI consensus or maintainer override for promotion.
