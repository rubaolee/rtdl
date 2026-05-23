Warning: Basic terminal detected (TERM=dumb). Visual rendering will be limited. For the best experience, use a terminal emulator with truecolor support.
Warning: 256-color support not detected. Using a terminal with at least 256-color support is recommended for a better visual experience.
Ripgrep is not available. Falling back to GrepTool.
**Verdict:** Accepted.

**Exact Number Check:**
Verified against `summary.json` raw data and the `docs/reports/goal2476_same_root_culling_ab_toggle_2026-05-21.md` table. All report numbers are accurate rounded representations of the artifact data:

*   **32768 iterations:**
    *   **Total Median (On/Off):** 0.044802s / 0.053457s (Raw: `0.04480182...` / `0.05345690...`)
    *   **Native Median (On/Off):** 0.024914s / 0.032739s (Raw: `0.02491376...` / `0.03273943...`)
*   **65536 iterations:**
    *   **Total Median (On/Off):** 0.107093s / 0.122379s (Raw: `0.10709266...` / `0.12237898...`)
    *   **Native Median (On/Off):** 0.068098s / 0.083150s (Raw: `0.06809800...` / `0.08314966...`)

**Any Blockers:** None. The signatures match (`"signatures_match": true`) in both runs, and the performance delta is consistent across both total and native metrics.
