---

## Review: Goal1626 v1.6.x OptiX Collect-K Midcount Micro-Probe

---

### Verdict

**Evidence supports the interpretation. Claim boundary is appropriately conservative. Next direction is technically reasonable.** One minor artifact inconsistency requires attention before this note is treated as canonical.

---

### Supported Points

**Numerical accuracy.** All three rows in the interpretation table match the artifacts exactly:

| Count | Baseline total_ms | Gated total_ms | Delta | Verified |
|------:|------------------:|---------------:|------:|:--------:|
| 65537 | 0.382622 | 0.350152 | −0.032470 | ✓ |
| 98305 | 0.358881 | 0.358191 | −0.000690 | ✓ |
| 131072 | 0.367112 | 0.363302 | −0.003810 | ✓ |

Payload-copy counts and parity flags match in both round artifacts and the summary JSON.

**Mechanistic claim for count 65537.** The baseline round shows `carry_payload_copies: 5` with `carry_copy_ms: 0.051592 ms`. The gated round shows `carry_payload_copies: 0` with `carry_copy_ms: 0.026652 ms`. The ~25 µs carry-copy saving accounts for essentially the entire 32 µs total delta. The gate's effect is traceable to a single mechanism.

**Noise-level dismissal of counts 98305 and 131072.** At 98305, gated has the same four payload copies as baseline — the gate does not fire differently, so the 0.69 µs delta has no causal story and is correctly treated as noise. At 131072, both modes have zero payload copies; the 3.8 µs delta is likewise unsupported by any topology difference.

**Next-direction recommendation.** The stage profiles strongly support targeting merge/sync. Summing `merge_launch_ms + merge_sync_ms` per count: ~0.201 ms at 65537 (53% of baseline total), ~0.225 ms at 98305 (63%), ~0.242 ms at 131072 (66%). The dominant cost is not carry-copy at any of the three counts tested, and grows as a share with count — the direction is well-grounded in the data.

**Claim boundary.** All six `claim_flags` are `false` in both the summary JSON and both round artifacts. The textual prohibitions in the "Claim Boundary" section of the interpretation note are consistent with those flags.

---

### Concerns

**1. Goal ID mismatch in the summary artifact (minor but should be corrected).**
`goal1626_v1_6_x_optix_collect_k_midcount_micro_probe_2026-05-09.json` contains `"goal": "Goal1625"` and its `claim_boundary` text reads *"Goal1625 is internal same-host OptiX collect-k threshold-4 diagnostic evidence"*. The file name, the interpretation note title, and the runner reference all say Goal1626. This looks like the summary JSON was templated from a Goal1625 artifact without updating the `goal` and `claim_boundary` fields. It does not affect the numerical evidence, but creates an identity ambiguity if the artifact is cited later.

**2. Single-round, single-repeat limitation not stated explicitly.**
With `rounds=1, repeats=1`, each data point is one timing measurement. The note correctly treats the 65537 delta as signal (because it is mechanistically explained by the payload-copy count drop) and the other two as noise, which is sound reasoning. However, the note does not mention that temporal variance is unquantified. A future reader without the JSON context could mistake the three deltas as independently-comparable values. A one-sentence caveat — e.g., *"all deltas are single-sample; no variance estimate is available"* — would strengthen the guardrail.

**3. Carry-copy operation vs. carry-payload-copy distinction slightly elided.**
At count 65537 in gated mode, `carry_copies` remains 5 (structural operations still execute), but `carry_payload_copies` drops to 0 (data volume per copy is reduced). The interpretation says the gate "removes carry payload copies," which is correct, but a reader might infer the structural copy work is eliminated entirely. The saving is from reduced per-copy data volume, not from eliminating the 5 copy kernel calls. Not a material error, but worth a word of precision if this note is referenced in architectural discussions.

**4. The "8 seconds" wall-clock claim is not verifiable from the artifacts.**
The introduction states the run "completed in 8 seconds." None of the four JSON files record a wall-clock total. This is almost certainly accurate (sub-ms operation times × 3 counts × 2 modes), but it is unverified by the artifacts as written.

---

### Recommendation

Accept the interpretation as internal evidence. Before filing it as a canonical reference:

1. Correct `"goal": "Goal1625"` → `"Goal1625"` → `"Goal1626"` and the `claim_boundary` text in the summary JSON to avoid future citation confusion.
2. Optionally add a single-sentence statistical caveat (n=1 per count, no variance estimate).

Do not promote threshold-4 or `COLLECT_K_BOUNDED` from this evidence — the note's own "Next Work" section and claim flags already enforce this correctly. The proposed pivot to merge/sync investigation is the right next step given the stage profiles.
