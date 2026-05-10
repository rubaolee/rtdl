The review of the Goal1660 performance reports and scripts is complete.

### Verdict
**Status:** **Release Blocked**
The reporting is honest and technically sound, but the data confirms significant performance regressions in `v1.6.11` compared to `v1.0`.

### 1. Honesty of Reporting (16 Accepted vs. 20 Excluded)
The reporting is **honest and accurate**.
*   **Math:** With 18 public apps, there are 36 possible app/engine pairs. The report correctly identifies 16 comparable pairs (mostly OptiX) and excludes 20.
*   **Rationale:** Classifying 20 rows as "excluded/unsupported" is the correct engineering decision. These scripts either lack a `--backend` selector or are hardcoded for OptiX. Reporting them as "failures" would be misleading; they are simply outside the current automated benchmarking scope.

### 2. `--backend` vs. `--mode` Correction
The correction is **correct and necessary**.
*   In the RTDSL ecosystem, `--mode` is overloaded to handle execution state (e.g., `run`, `dry-run`, `optix-only-test`), whereas `--backend` is the canonical selector for engine-switching (Embree vs. OptiX).
*   The script logic in `_engine_selector` correctly prevents "decorative" comparisons where a script might ignore a flag and run the same engine twice, which would produce fake parity.

### 3. Release and Public Speedup Status
**Blocked.**
*   **Regressions:** The measured data shows `v1.6.11` is slower than `v1.0` in 13 out of 16 accepted pairs.
    *   `database_analytics` (OptiX): **9.0% slower** (1.090 ratio).
    *   `segment_polygon_anyhit_rows`: **13.8% slower** (1.138 ratio).
    *   `robot_collision_screening`: **8.2% slower** (1.082 ratio).
*   **Claim Validity:** Claims of "broad RTX acceleration" or "v1.6.11 speedups" are currently indefensible.
*   **Coverage Gap:** The lack of Embree comparisons for 17/18 apps means we cannot verify if the regressions are engine-specific or general overhead in the `v1.6.11` core.

### Blockers
1.  **Performance Parity:** The ~5-14% regressions in OptiX rows must be diagnosed and resolved before `v1.6.11` can be tagged.
2.  **Telemetry/Overhead Audit:** The fact that both `database_analytics` backends (Embree faster, OptiX slower) moved in opposite directions suggests a possible change in how OptiX buffers or host-device transfers are managed in the new version.
3.  **App Profiler Updates:** To unblock the 20 excluded rows, the app profiler scripts need to be updated to support a standard `--backend` flag.

No file edits were performed. The current `not_release_ready` verdict in the documents is the only responsible conclusion.
