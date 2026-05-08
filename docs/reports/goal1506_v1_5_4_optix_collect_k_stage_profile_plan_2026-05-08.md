# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Plan

## Verdict

Local source review only. This note does not add new GPU measurements, does not authorize public speedup wording, and does not change the experimental status of `COLLECT_K_BOUNDED`.

The next pod run should measure stage costs inside the OptiX row_width=2 tiled path before attempting another performance optimization.

## Current Evidence Baseline

- The committed Goal1502/Goal1503/Goal1504 artifacts validate real-NVIDIA parity, bounds behavior, dynamic row-width behavior, INT64_MAX pair behavior, and fail-closed overflow behavior for the experimental Python OptiX `COLLECT_K_BOUNDED` device-pointer bridge.
- Goal1503 records bounded row_width=2 tiled scaling through `131072` candidates.
- Goal1505 indexes those artifacts and keeps all public claim authorization flags false.

## Source-Level Execution Shape

For `row_width == 2` and `4097 <= candidate_count <= 131072`, `rtdl_optix_collect_k_bounded_i64_device(...)` uses the bounded tiled path in `src/native/optix/rtdl_optix_api.cpp`.

The current path uses:

- `tile_size = 4096`.
- One row_width=2 sort kernel launch per tile.
- One stream synchronization after all tile sort launches.
- A device-to-host metadata download for every tile's emitted count and overflow flag.
- A merge tree where each pair of sorted segments is merged by one single-thread merge kernel.
- One stream synchronization after each merge level.
- A device-to-host metadata download for every merge pair's emitted count and overflow flag.
- Device-to-device copies for carried odd segments and for the final output copy.

For `131072` candidates, this means:

- `32` sort kernel launches.
- `31` merge kernel launches.
- `0` odd-segment carry copies.
- `1` final device-to-device output copy.
- `126` tiny device-to-host metadata fields downloaded across the tile and merge levels.
- `6` host synchronization points for tile metadata plus five merge levels.

For `65537` candidates, this means:

- `17` sort kernel launches.
- `16` merge kernel launches.
- `4` odd-segment carry copies.
- `1` final device-to-device output copy.
- `66` tiny device-to-host metadata fields downloaded across the tile and merge levels.
- `6` host synchronization points for tile metadata plus five merge levels.

## Why This Is The Next Measurement Target

The final measured path is correctness-clean, but the high-count medians remain large enough that end-to-end timing alone is not diagnostic.

The likely cost buckets to measure separately are:

- Tile sort time.
- Merge kernel time by level.
- Host synchronization and metadata download time.
- Final device-to-device output copy time.
- First-call PTX compile/module-load overhead versus warmed steady-state calls.

This note intentionally says "likely cost buckets" rather than assigning blame. The next pod measurement should decide where the time actually goes.

## Proposed Pod Instrumentation

Add a temporary or guarded profiling mode that records CUDA event timings around:

- All tile sort launches plus the following synchronization.
- Each merge level's launches plus the following synchronization.
- Metadata downloads after tile sort and after each merge level.
- Final device-to-device copy.
- Total native function duration after modules are already loaded.

The profiling output should be saved as a JSON artifact under `docs/reports/` with:

- GPU name, driver, OptiX SDK tag, git commit, and library path.
- Candidate counts at least `4097`, `65537`, and `131072`.
- Repeats at least `5` after one warmup call.
- Per-stage median/min/max timing.
- Parity and overflow checks identical to Goal1503/Goal1504.
- Claim flags all false.

## Optimization Ideas To Test After Profiling

Do not implement these as claims before measurement. They are hypotheses for the next pod round:

- Reduce host metadata round trips by keeping merge counts/overflow flags device-resident across levels.
- Parallelize the merge kernel instead of using one thread per pair.
- Fuse adjacent merge levels when segment sizes make fusion practical.
- Avoid final device-to-device copy when the final source can be returned or when the destination already matches the final buffer.
- Evaluate a fixed-output-capacity path that can fail closed earlier without fully materializing over-capacity rows.

## Claim Boundary

This is a profiling plan for an experimental OptiX primitive path. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, experimental public promotion, release action, or any new GPU performance claim.
