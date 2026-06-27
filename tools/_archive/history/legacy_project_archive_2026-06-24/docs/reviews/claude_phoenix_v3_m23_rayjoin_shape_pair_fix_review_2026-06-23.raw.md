## Review: Phoenix V3 M23 RayJoin Shape-Pair Fix

**Verdict: `accept_blocker_closed`**

---

### Bottom Line

The fix is narrow, correct, and the POD evidence is clean. The specific M22 correctness blocker (`rayjoin_optix_promoted_overlay_seed_tiled_x2048` TypeError) is closed. No release authorization follows from this — the claim flags remain false and the broader RayJoin reproduction gate remains open.

---

### Findings, Ordered by Severity

**[HIGH] Full RayJoin reproduction remains false — scope of closure is one row**

Closing this blocker covers the `overlay_seed` / `prepared_optix_shape_pair_active_count` path on the tiled_x2048 dataset. `full_rayjoin_reproduction: false` and `rtdl_beats_rayjoin: false` are still explicitly held. The M22 verdict was non-release; M23 inherits that verdict unless further rows are addressed.

**[MEDIUM] Regression test is AST-only, not runtime**

The AST scan verifying call sites is sound for confirming the kwarg is gone. But it does not exercise the function under its actual runtime contract. The 12 passing local tests partially cover this, but confirm only wiring and goal-row behavior — not the full shape-pair execution path under all dataset sizes or workload variants.

**[MEDIUM] Silent argument discard — intended behavior should be confirmed**

Removing `point_order_mode=args.point_order_mode` from this call means the CLI flag `--point-order-mode` is now silently ignored when `--execution-route prepared_optix_shape_pair_active_count` is selected. This is likely correct — the output contract `overlay_active_pair_dependency_count` is about pair counts, not ordering — but "silently ignored" should be confirmed intentional, not an accidental omission of handling. If the flag is irrelevant to this route, a guard or a CLI-level restriction that rejects the flag combination would be more defensive.

**[LOW] No performance regression baseline vs M22**

The focused POD output includes `prepared_query_sec` (0.000156s) and total (0.000785s) for 5 repeats. No M22 baseline is provided to confirm the fix didn't affect timing. The values are plausible for a shape-pair count, but absence of a prior baseline is a minor evidence gap.

**[LOW] Fix correct and appropriately scoped**

`point_order_mode` is a PIP-mode concern. Its presence in the `prepared_optix_shape_pair_active_count` call was a routing error, not a behavioral choice. Removing it is the right fix at the right location. The AST scan strengthens this by ensuring no other call site re-introduces the kwarg.

---

### Required Follow-Up

1. **Confirm silent-discard intent** for `--point-order-mode` on the `prepared_optix_shape_pair_active_count` route. Either document it as out-of-scope for this route or add a CLI guard.
2. **Identify remaining open RayJoin rows** for the current Phoenix V3 row set — this fix closes one; enumerate what remains before `full_rayjoin_reproduction` can be revisited.
3. **Runtime regression test** covering the shape-pair active-count workload end-to-end (not just AST wiring) is the natural next test gap to close.

---

### Non-Authorization Block

- **Release authorized:** NO
- **Public speedup claim authorized:** NO
- **Broad V3 faster than V2.x claim authorized:** NO
- **Full RayJoin reproduction:** NO
- **RTDL beats RayJoin:** NO

These are unchanged from the provided claim flags and from standing project policy. Closing this blocker is a pre-condition for further RayJoin gate progress, not a release gate itself.
