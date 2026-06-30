# External Review Handoff: Goal3155-3158 RT-DBSCAN Front-Door Chain

Please review `docs/reports/goal3159_rt_dbscan_front_door_chain_review_packet_2026-06-03.md` and write an independent review of the Goal3155-3158 chain.

Requested review output paths:

- Claude: `docs/reviews/goal3159_claude_review_rt_dbscan_front_door_chain_2026-06-03.md`
- Gemini: `docs/reviews/goal3159_gemini_review_rt_dbscan_front_door_chain_2026-06-03.md`

Focus questions:

1. Does the v2.8 fixed-radius graph component front door stay app-agnostic?
2. Does the RT-DBSCAN benchmark app route through the front door while keeping app semantics outside the engine?
3. Does typed producer metadata record real device-resident evidence without claiming true zero-copy?
4. Are the v2.8 runtime-gap matrix and reports honest about remaining work and claim boundaries?
5. What should be the next engineering target after this chain?

Required verdict: one of `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Do not authorize release, public speedup, broad RT-core speedup, true-zero-copy, paper reproduction, automatic partner selection, or app-specific native engine logic.
