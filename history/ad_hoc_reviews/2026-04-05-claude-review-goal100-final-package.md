---

## Release-Validation Review: Goal 100

### 1. Verdict

**APPROVE-WITH-NOTES**

The package is honest, the carry-forward boundary is clearly disclosed, and the fresh-clone Linux gate is a genuine high-signal test. Two findings require acknowledgment before the package is considered fully closed; neither blocks release.

---

### 2. Findings

**F1 (Moderate) — Embree artifact location/label inconsistency**

The file at `.../goal100_release_validation_rerun_artifacts_2026-04-05/embree_prepared/summary.json` carries `"host_label": "lestat-lx1-goal100"` and `"date": "2026-04-05"`. That label and date indicate a fresh run on the Goal 100 clone. Yet the master `summary.json` classifies Embree under `same_head_carried_artifacts` and points to the Goal 83 artifact path (`goal83_embree_long_exact_source_repair_artifacts_2026-04-04`). One of these is wrong:

- If Embree was freshly rerun, the master summary and narrative should say so (this is good news, not a problem).
- If the file is a copy of the Goal 83 result, then `host_label` and `date` were updated in the copy, which is misleading.

This must be resolved. A reviewer cannot determine whether Embree was actually freshly validated or not.

**F2 (Minor) — Skipped test not identified**

The full-matrix run reports `293 tests, 1 skipped`. For a release gate, the identity of the skipped test should be named (even one line). "1 skipped" alone is not auditable.

**F3 (Minor) — OptiX raw cold-run framing**

The narrative says "parity preserved on all reruns" immediately after listing the cold-run timing of OptiX at 7.045 s vs PostGIS at 3.209 s. "Parity" is defined in the artifact as correctness (row count + SHA256 match), and all three runs do have `parity_vs_postgis: true`. But the sentence sits in a timing context and could be read as a performance claim. A parenthetical — *"(correctness parity; OptiX cold-start is slower than PostGIS)"* — would prevent misreading.

**F4 (Informational) — OptiX raw date is 2026-04-04, report date 2026-04-05**

The `optix_raw/summary.json` is dated the day before the report. The host label `lestat-lx1-goal100` confirms it is a Goal 100 run. No action needed; noted for auditors.

---

### 3. Agreement and Disagreement

**Agrees with the package:**

- The overall structure is correct. The `same_head_carried_artifacts` field in the master JSON is the right mechanism for distinguishing fresh from carried items; it is used properly for OptiX (Goals 98/99) and Vulkan (Goals 87/88).
- The narrative "honest conclusion" section accurately characterizes the gate as high-signal rather than exhaustive, and explicitly states what was not rerun. That language satisfies the Goal 100 acceptance criterion on honesty.
- The Goal 51 Vulkan parity ladder (8 targets, all `parity: true`) is clean and verifiable.
- The clean Linux full-matrix result (293 OK, 1 skipped) on a fresh clone at a named commit (`e15ee77`) is a genuine, repeatable gate, not a local-only artifact.
- The performance characterization of OptiX raw-input (cold vs. warm) is correctly attributed to "runtime-owned cache measurement," not a prepared/optimized scenario.

**Disagrees with or flags:**

- Cannot agree that Embree is cleanly classified as "same-head carried" while an artifact in the Goal 100 directory is labeled as a Goal 100 run. These two facts are in direct conflict. The package cannot simultaneously claim Embree was not rerun and publish an Embree artifact bearing the Goal 100 host label and today's date (F1 above).

---

### 4. Recommended Next Step

1. **Resolve F1 first.** Check whether Embree was actually rerun on `lestat-lx1-goal100`. If yes: move it from `same_head_carried_artifacts` to the fresh-run section of both the report and master JSON. If no (file was copied and metadata updated): correct the date/host_label in the copy to match its actual source, or remove the misleading copy.

2. **Name the skipped test** in the report (one line under the full-matrix result).

3. **Add the parenthetical on OptiX raw cold-run parity** to prevent ambiguity.

Once F1 is resolved and F2/F3 addressed (or explicitly waived by the owner), this package should be re-submitted for 3-AI sign-off. Claude's conditional approval is on record pending those items.
tep

This package can proceed to v0.1 release with the following actions before or alongside final publication:

1. **(Required for audit hygiene)** Add a note to the Goal 100 report explaining the `optix_raw` date discrepancy (e.g., "run executed late 2026-04-04 UTC, committed 2026-04-05").
2. **(Recommended)** Add a `validated_head` field to `goal51/summary.json`, or note in the report that the artifact's provenance is established by its directory path alone.
3. **(Recommended)** Name and explain the 1 skipped test in the report.
4. **(Optional, strengthens future audits)** Add a `git log --oneline <base>..e15ee77 -- src/rtdsl/backends/` or equivalent output as a footnote to justify the Embree/Vulkan carry-forward.

None of these are blockers. The core release gate — clean Linux clone, 293 tests passing, Goal 51 Vulkan parity, OptiX raw-input parity confirmed — is solid and honestly presented.
