Now I have all the information I need. Here is the review:

---

## Goal1630 Review: OptiX Collect-K Extended 128-Tile Diagnostic

### Verdict

**Accepted with minor notes.** The implementation is correctly structured as an opt-in diagnostic, capacity guards are sound, evidence is internally consistent, and claim boundaries are explicit and conservative. No blocking issues.

---

### Supported Points

**Opt-in gate is correctly wired end-to-end.**
The C++ `collect_k_extended_128_tile_diagnostic()` (line 765) reads the env var at call time. The Python `_expected_native_path()` helper (script lines 224–232) mirrors this exactly, including the `not in (None, "", "0")` idiom. The Goal1630 test exercises the boundary at 131072, 131073, 262144, and 262145 with the var both absent and set — the four cases cover the exact decision points.

**Default boundary is untouched.** The base constants (`kCollectKRowWidth2BaseMaxTiledCandidates = 131072`, `BaseMaxTileSegments = 64`, `BaseMaxPrefixBlocks = 512`) are unchanged. Goal1629's test independently confirms count=131073 still resolves to `dynamic_row_width_single_thread_fallback` without the diagnostic flag.

**Capacity guards are in the right places.**
- Line 1142–1143: tile count checked against `max_tile_segments` before the workspace allocation call.
- Line 1440–1441: `pair_count > max_tile_segments || total_blocks > max_prefix_blocks` checked inside the merge loop lambda before every kernel launch. Both throw descriptive errors, not silent undefined behavior.

**Workspace arithmetic is consistent.**
For 128 tiles / 262144 candidates, the `ensure()` request is `(262144, 128, 1024)`. Allocations scale correctly: `temp_stage_{a,b}` at `sizeof(int64_t) * 262144 * 2` = 4 MB each, `final_merged_rows` another 4 MB, `final_marks` 1 MB — roughly 13 MB total, trivial for the A4500's 20 GB.

**Merge topology is arithmetically correct.**
The probe JSON shows 128 tiles → 7 levels → output capacities doubling at each level (4096 → 8192 → … → 262144). Binary tree reduction from 128 to 1 requires exactly ceil(log2(128)) = 7 levels. The final level's `output_capacity = 262144` and `output_segments = 1` is consistent. All three artifacts agree on topology = `{tile_count:128, merge_levels:7, merge_launches:27}`.

**Parity holds in all artifacts.**
`same_candidate_rows = true`, `same_valid_count = true`, `same_overflowed_flag = true` in all 7 steady-state records across the three JSON files. `emitted_count = 131072` matches `unique_mod = 262144 // 2 = 131072` from the probe's `_make_rows()`, so the output is mathematically expected.

**Defer < no-defer total timing.**
Defer median stage total = 0.629871 ms, no-defer = 0.682102 ms (delta −0.052 ms). The difference is driven by merge_sync_ms collapsing from ~0.316 ms to ~0.015 ms, which matches the deferred-sync design intent. The `assertLess` in the test is grounded in the artifact values rather than re-running hardware.

**Claim boundaries are explicit and redundant.**
All six `claim_flags` are `False` in every JSON artifact. The report, each artifact's `claim_boundary` field, and the test all independently assert: no public speedup wording, no stable primitive promotion, no release action, no whole-app or broad GPU claims.

---

### Concerns

**1. Workspace memory retention on env-var toggle-off (minor, safe).** `ensure()` (lines 826–829) returns early if the existing workspace is already at least as large as requested. If the diagnostic is first enabled (workspace grows to 128-tile capacity), then disabled, subsequent calls with `use_reusable_workspace=true` will pass `ensure(131072, 64, 512)`, which satisfies the "already large enough" condition — the workspace stays at 128-tile size for the process lifetime. No correctness impact (writes stay within bounds), but device memory is not reclaimed. This is acceptable for a diagnostic but should be documented or enforced by "do not toggle mid-process."

**2. `ensure()` release path does not abort on partial `cuMemFree` failure (minor, pre-existing).** Lines 800–818 free all 18 device pointers in sequence regardless of prior failure, then unconditionally zero the struct with `*this = {}`. A failed `cuMemFree` mid-sequence would leak device memory and leave the struct inconsistent. This is a pre-existing pattern in the base path, not introduced here, but it is now exercised on a larger allocation.

**3. Single GPU, single scale point.** All three artifacts are from one A4500 run at count=262144 only. The report correctly names this ("one GPU model, one extended scale point"), but the test's `assertLess` on timing is necessarily brittle if the artifacts are ever regenerated on a different machine. The test would need to be updated to match new artifact values.

**4. Acceptance probe is repeats=1.** The `goal1630_extended_128_tile_262144_probe.json` has `repeats=1`, so `stage_max_ms = stage_median_ms = stage_min_ms` (all identical). The report cites `0.613750 ms` as the stage median, which is accurate but represents a single observation. The repeats=5 artifacts provide the statistical backing; the report correctly uses both.

**5. No execution-path test for 262145 → fallback in native C++.** The Python boundary test (test line 46–48) checks the helper function logic, but no test executes the native library with count=262145 to confirm it actually falls through to the fallback. Acceptable for a diagnostic stage, but the native guard is only covered by text-search (`self.assertIn(..., text)`) rather than a live invocation.

---

### Recommendation

Accept as-is. The implementation is correctly opt-in, the guards are in the right order, the workspace arithmetic scales cleanly from 64→128 tiles, and the claim boundaries are redundantly enforced at three layers (source constants, artifacts, report). Before considering any promotion beyond internal diagnostic status, address concern #1 (document the "do not toggle mid-process" constraint or add a once-flag to `use_extended_128_tile_diagnostic()`) and collect evidence from at least one additional GPU architecture as the Next Work section already calls for.
