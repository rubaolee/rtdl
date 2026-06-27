# Handoff: Claude Review For Goal3668 v2.9 Closeout And Next-Direction Refresh

Date: 2026-06-06

Claude is needed for strict 3-AI next-version roadmap consensus. Please perform
an independent read-only review and write the review to:

`docs/reviews/goal3670_claude_review_goal3668_v2_9_closeout_next_direction_refresh_2026-06-06.md`

## Context

Goal3619/3622 proposed a contract-and-residency-first next-version direction,
but Claude review was blocked by quota. Since that packet, RayJoin PIP changed:

- Goal3658: RTDL/OptiX tuned device predicate made the one-shot/sequential
  validated-domain PIP count exact and faster than the prior project-owned
  CuPy dense baseline, while still slower than RayJoin `query_exec`.
- Goal3660: RTDL/OptiX persistent prepared-point batch executor produced
  strong batched repeated-request throughput on the 512 public-CDB slice.
- Goal3663: The same batch contract held on a 4096 public-CDB slice.
- Goal3665: The fast route now has a validated-domain preflight guard; the
  full-county `count16545` probe fails exactness (`47264 != 47262`) before
  RayJoin timing starts.
- Goal3668: Codex refreshed the closeout/next-direction packet to remove the
  stale "PIP is CuPy-owned" reading and to add topology-aware closed-shape
  membership/correction as a first-class next-version target.
- Goal3669: Gemini independently reviewed Goal3668 and returned `accept`.

## Files To Read

- `docs/reports/goal3668_v2_9_closeout_and_next_direction_refresh_2026-06-06.md`
- `docs/reviews/goal3669_gemini_review_goal3668_v2_9_closeout_next_direction_refresh_2026-06-06.md`
- `tests/goal3668_v2_9_closeout_and_next_direction_refresh_test.py`
- `docs/reports/goal3602_v2_9_benchmark_status_after_resident_evidence_2026-06-06.md`
- `docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md`
- `docs/reviews/goal3666_gemini_review_goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md`
- `docs/research/future_version_to_do_list.md`
- Optional background: `docs/reports/goal3619_next_version_major_direction_consensus_packet_2026-06-06.md` and `docs/reports/goal3622_next_version_direction_consensus_status_2026-06-06.md`

## Questions

1. Is Goal3668 a correct update to the old Goal3619/3622 direction after the
   RayJoin PIP work?
2. Is it technically honest to close v2.9 tuning here unless a task fixes
   correctness, offers a large material end-to-end gain, creates reusable
   generic capability, or supplies missing same-contract evidence?
3. Are the first next-version targets right: `segment_pair_*` contracts,
   topology-aware closed-shape membership/correction, typed resident primitive
   outputs, and deterministic grouped reductions/witness contracts?
4. Does Goal3668 avoid public release/speedup/RTDL-beats-RayJoin/true-zero-copy
   claims?
5. Does it preserve user-chosen partners and app-agnostic native-engine rules?
6. What must change before Codex can write final 3-AI next-version consensus?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Please state explicitly that this is an independent Claude review,
distinct from Codex and Gemini, and that it authorizes no release/public claims.

