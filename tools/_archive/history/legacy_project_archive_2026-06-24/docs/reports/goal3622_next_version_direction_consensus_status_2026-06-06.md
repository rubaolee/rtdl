# Goal3622 - Next-Version Direction Consensus Status

Date: 2026-06-06

Status: interim consensus-status packet. This is not final 3-AI consensus because Claude review is blocked by quota. This file authorizes no release, public speedup wording, RTDL-beats-RayJoin wording, broad RT-core speedup, true zero-copy, automatic partner selection, or app-specific native engine logic.

## Inputs

| Source | File / Evidence | Verdict | Status |
| --- | --- | --- | --- |
| Codex | `docs/reports/goal3619_next_version_major_direction_consensus_packet_2026-06-06.md` | `accept-with-boundary` | complete |
| Gemini | `docs/reviews/goal3620_gemini_review_goal3619_next_version_direction_2026-06-06.md` | `accept-with-boundary` | complete |
| Claude | attempted via `scratch/goal3621_claude_review.out` | none | blocked by weekly quota |

Claude output:

```text
You've hit your weekly limit - resets Jun 7, 7pm (America/New_York)
```

Therefore, strict 3-AI consensus is **pending**, not complete.

## Current Direction Accepted By Codex + Gemini

The next-version direction is:

1. Stop more current-version performance tuning unless it fixes correctness, has a credible path to a large material end-to-end gain, creates a reusable generic primitive/runtime capability, or supplies missing same-contract evidence.
2. Make the next version contract-and-residency first.
3. Formalize primitive contracts before public claims, starting with segment-pair count/intersection contracts exposed by the RayJoin work.
4. Build device-resident typed primitive outputs and status/ambiguity telemetry before claiming true zero-copy or broad data-residency wins.
5. Keep partners user-chosen; RTDL provides measured support, reference routes, and handoff contracts but does not auto-select a public default.
6. Keep shader injection parked behind primitive contracts and residency work.

## Gemini Boundary Items And Codex Clarifications

Gemini accepted the direction with boundary and asked for three clarifications before final consensus.

### 1. Partner-Compatible Handoff Contracts

Clarification:

Partner-compatible handoff contracts are not partner defaults. They are explicit data and lifetime contracts that make RTDL primitive outputs consumable by user-chosen partners.

The next-version scope should define:

- typed primitive output columns, including dtype, shape, ownership, backend, stream/event, and lifetime status;
- `__cuda_array_interface__` / DLPack-compatible descriptors where a partner can consume device memory directly;
- fallback materialization behavior when a partner cannot consume the descriptor;
- explicit route metadata: selected backend, selected partner, transfer status, residency status, fallback reason, and claim authorization flags;
- conformance tests proving that a partner route matches the same primitive contract before it becomes recommended.

This does not authorize true zero-copy. A zero-copy claim would require measured proof that the specific route uses device-resident memory without hidden transfer or carrier conversion.

### 2. Criteria For Future Primitive Contracts

Clarification:

Future primitive contracts should be formalized when at least one of these is true:

- a benchmark app repeatedly needs the same generic operation;
- multiple backends or partners need a shared correctness contract;
- ambiguity, degeneracy, tolerance, witness identity, tie-breaking, or determinism affects correctness;
- the primitive can be expressed without app/domain vocabulary in the engine;
- a formal contract unlocks a material performance path or prevents repeated app-specific rewrites.

Recommended ordering after segment-pair contracts:

1. closed-shape membership / containment / active-count contracts;
2. nearest-neighbor witness and tie-break contracts;
3. grouped continuation and deterministic reduction contracts;
4. DBSCAN/fixed-radius status and expansion contracts if they remain generic.

### 3. External Dependency Strategy

Clarification:

The next version should keep dependency handling evidence-based and fail-closed:

- record tested CUDA, driver, OptiX, CuPy, Numba, Torch, Triton, compiler, and GPU architecture versions in artifacts;
- maintain per-partner support matrices by operation, not one global "partner supported" claim;
- never promote a partner route without same-contract correctness evidence;
- never auto-select a partner solely because it is installed;
- treat unsupported versions as fallback/materialization paths, not silent performance claims.

## Pending Claude Review Questions

When Claude is available, the review should cover:

1. Whether Goal3619 plus the clarifications above are enough to become the next-version direction.
2. Whether stopping incremental current-version tuning is justified by the current RayJoin evidence.
3. Whether the segment-pair contract family is the right first formal-contract target.
4. Whether partner-compatible handoff contracts are described concretely enough without implying auto-selection or true zero-copy.
5. Whether shader injection should remain parked.
6. Whether any major performance opportunity is obvious enough to override the stop/continue rule.

## Interim Verdict

Interim verdict: `needs-more-evidence` for final 3-AI consensus, solely because Claude review is unavailable.

Codex + Gemini direction verdict: `accept-with-boundary`.

Required next action: obtain a fresh Claude review of Goal3619 and this Goal3622 status/clarification packet, then write a separate final consensus file only if all three AI positions can be reconciled.
