Here is the complete verdict.

---

## Review: Goal1660 Measured Pod Summary and Corrected Matrix

### 1. Are 16 accepted measured pairs and 20 unsupported/excluded pairs honest?

**Yes, both counts are correct and verified.**

Counting directly from the pod summary JSON:

| Category | Count |
|---|---|
| `accepted_measured` | 16 |
| `excluded` | 19 |
| `shared_primitive_alias` | 1 |
| **Total excluded/unsupported** | **20** |
| **Grand total** | **36** (= 18 apps × 2 engines) |

The 16 accepted pairs are: `database_analytics/embree`, `database_analytics/optix`, `graph_analytics/optix`, and all 13 remaining OptiX-only apps that ran cleanly in both checkouts.

One subtlety: several excluded Embree rows in the raw JSON contain non-null `elapsed_sec` values (~0.20 s each with `status: "failed"`). These are script-startup failures on OptiX-only scripts that received no real engine flag — correctly excluded from the count, and correctly rendered as empty cells in the markdown. This is not a data integrity problem, but anyone reading the raw JSON should know those sub-0.21 s timings are noise, not Embree measurements.

---

### 2. Is the --backend vs --mode correction right?

**Yes, the correction is correct.**

`_engine_selector()` (script line 48–51) intentionally recognizes only `--backend` as a real engine selector and ignores `--mode`. This is right because:

- The scripts that accept `--mode` use it as an **execution mode** flag (`run` vs `dry-run`), not as an engine toggle. You cannot flip `--mode run` to `--mode embree` and get an Embree run.
- Scripts that are truly OptiX-specific (e.g. `goal933_prepared_segment_polygon_optix_profiler.py`) are identified by filename via `_script_is_optix_specific()` (line 54–61), and their OptiX rows are correctly accepted while Embree rows are excluded as decorative labels.
- Only `database_analytics` has a real `--backend embree|optix` flag, which is why it is the only app with both an Embree and an OptiX accepted row.

The corrected_optix_rows JSON confirms this: the 6 corrected entries all use `--mode run` (execution mode), and the rerun correctly produces accepted OptiX timings with `returncode: 0`.

---

### 3. Does release/public speedup remain blocked?

**Yes, and the data itself provides the reason it must stay blocked.**

The 16 measured ratios (v1.6.11 / v1.0):

| Result | Rows |
|---|---|
| v1.6.11 **faster** (ratio < 1.0) | 3: `database_analytics/embree` (0.956), `polygon_set_jaccard/optix` (0.995), `barnes_hut_force_app/optix` (0.989) |
| Essentially equal (0.99–1.02) | 5 |
| v1.6.11 **slower** (ratio > 1.02) | 8, ranging from 1.023 to **1.138** |

The largest regression is `segment_polygon_anyhit_rows/optix` at 1.138 (13.8% slower). No aggregate speedup story is supportable from this data. Claiming a public speedup would be dishonest.

The script enforces this structurally: `validate_manifest()` (lines 267–280) raises if any of `release_authorized`, `tag_authorized`, or `public_claim_authorized` is not `False`, and if `v1_6_11_release_tag_action` is missing from `blocked_claims`. The verdict label `measured_with_scope_correction_not_release_ready` is accurate.

---

### Summary Verdict

| Claim | Verdict |
|---|---|
| 16 accepted / 20 excluded counts | **Honest and verified** |
| --backend vs --mode correction | **Correct** |
| Release/public speedup blocked | **Correctly blocked; data does not support a speedup claim** |

**Blockers for release/public speedup:** (a) most OptiX rows show v1.6.11 slightly slower than v1.0 at current benchmark scale; (b) Embree cross-version comparison is missing for 17 of 18 apps due to absent engine selectors; (c) the three authorization flags are held `False` by code enforcement, not just documentation.
