I have all the material I need. Here is the review:

---

## Goal1627 Diagnostic Gate Review

### Verdict

**Low synchronization risk; evidence narrow but accurately bounded; claim boundary conservative.**

The diagnostic gate is correctly implemented for the specific precondition set it asserts. The performance signal is real and internally consistent. It should not be promoted beyond the `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC` flag without broader coverage.

---

### Supported Points

**Synchronization safety argument holds.**

All kernels in the COLLECT_K_BOUNDED multi-tile merge loop run on the same default CUDA stream (`nullptr`). The default stream is serialized: work submitted in order executes in order, with no inter-kernel memory hazards. The per-level `cuStreamSynchronize(nullptr)` that is skipped was not providing a GPU-ordering guarantee — it was providing a *host barrier* to allow either:
- (a) host reads of per-level count data, or
- (b) per-level wall-clock timing.

The gate correctly requires **both** `use_device_prefix_compact` and `use_device_level_counts`, which eliminate (a): level output sizes are computed on-device via prefix scan and per-pair counts stay on device until the final level. No host read of GPU-produced data occurs between intermediate levels when those flags are active. Eliminating (b) — timing granularity — is acceptable under a diagnostic that explicitly trades per-level sync-ms fidelity for total-time measurement.

**Final level always synchronizes.**

The `can_defer_merge_sync` condition gates on `current_rows.size() != 2`. When the merge loop reaches the final pair (`current_rows.size() == 2`), `can_defer_merge_sync` is always false regardless of the env flag, and `cuStreamSynchronize(nullptr)` is unconditionally issued at line 1780. The non-batched else branch (line 1902) is unaffected and always syncs. The default path (no env gate) is structurally identical to the pre-patch state.

**Artifacts internally consistent with the claim.**

- `all_parity_passed: true` in both JSON artifacts; `same_candidate_rows`, `same_valid_count`, `same_overflowed_flag` all true for all 3 counts across 5 repeats.
- Defer JSON shows `sync_ms: 0` for all non-final levels and non-zero `sync_ms` only at the final level — consistent with the gate logic.
- Final-level `launch_ms` in the defer run is substantially higher than no-defer (e.g., count=65537 level-5 launch: ~0.062–0.072 ms defer vs ~0.035–0.045 ms no-defer). This is the expected pattern: queued work resolves in the final launch measurement window, not a regression.
- Median total improvement is present in all three counts: −0.057 / −0.036 / −0.026 ms.

**Test coverage matches the implementation.**

The test file validates: (1) all guard condition subexpressions exist in source (`use_batched_compact_level`, `current_rows.size() != 2`, `use_device_prefix_compact`, `use_device_level_counts`, `if (!can_defer_merge_sync)`), (2) report claim-boundary wording, and (3) artifact parity + total-time improvement across counts.

---

### Concerns

**1. Deferred sync between penultimate and final level: correctness relies entirely on stream ordering.**

Between non-final and final levels, the host never reads back per-level data (because of the device-counts path), so the safety argument is correct. However, this assumption is fragile if either `use_device_prefix_compact` or `use_device_level_counts` is ever relaxed without revisiting the deferral gate. The current gate conditions capture this precisely, but the relationship between the two conditions and the deferral safety is not commented in the source.

**2. Timing fidelity loss in diagnostic mode.**

When `can_defer_merge_sync` is true, `level_profile.sync_ms` is never set — it remains at whatever default value it is initialized to (0 from the JSON). `profile.merge_sync_ms` accumulates only the final-level sync. This means any downstream consumer of per-level `sync_ms` data under the diagnostic flag gets uninformative numbers for non-final levels. The report acknowledges "waiting moves into measured launch time" but doesn't state that per-level `sync_ms` is no longer a reliable latency signal in this mode.

**3. Evidence is narrow.**

One GPU model (A4500), one candidate preset (`COLLECT_K_FASTEST_CANDIDATE`), three counts, 5 repeats. The three counts are all in the same rough range (~65K–131K). The improvement narrows with count size (−16% → −11% → −7%), suggesting the deferred sync benefit may shrink at larger counts where GPU work dominates sync overhead. No coverage of non-A4500 hardware, non-FASTEST_CANDIDATE presets, or the carry-payload-copy path under deferral.

**4. The test checks source text, not behavior.**

The unit test does a string-search for guard subexpressions. It confirms the strings exist but does not verify that the guard logic is evaluated in the right order or that the gate is actually skipping the sync in the fast path. A behavioral test with CUDA mock or actual hardware run (the runner the report references) is needed for execution-path confidence.

---

### Recommendation

Keep the gate behind `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC`. The synchronization argument is correct for the guarded precondition set, and the claim boundary is appropriately conservative. Before considering this for a stable gated bundle:

1. Add a brief comment at the `can_defer_merge_sync` block explaining *why* both `use_device_prefix_compact` and `use_device_level_counts` are required for correctness — a future reader changing either flag needs to know they're load-bearing for sync safety, not just feature flags.
2. Run the diagnostic against at least one additional GPU tier and one larger count range (e.g., 256K–1M) before asserting the gain is consistent across the hardware fleet.
3. Acknowledge in the diagnostic mode's documentation that `level_profile.sync_ms` is zero for non-final levels and should not be used for per-level GPU latency analysis when the gate is enabled.
