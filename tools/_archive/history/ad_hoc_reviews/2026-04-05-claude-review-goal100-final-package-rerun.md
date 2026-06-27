## Release-Validation Review: Goal 100 Package

---

## 1. Verdict: APPROVE-WITH-NOTES

The package is honest, the fresh-gate results are clean, and the carry-forward logic is sound. Two minor transparency gaps prevent a clean APPROVE but do not block release.

---

## 2. Findings

**What is solid:**

- **Head traceability** is consistent. `e15ee77` appears in the top-level `summary.json`, the main report, and the `optix_raw` and `embree_prepared` artifact JSONs. No ambiguity about which commit is being validated.
- **Fresh-gate coverage is real.** 293 tests (full matrix) + 15 (milestone slice) + 23 (Vulkan slice) + Goal 51 parity ladder + OptiX raw 3-run + Embree prepared 2-run were all executed on the fresh Linux clone `/home/lestat/work/rtdl_goal100_clean`. That is a substantive gate.
- **Carry-forward justification is concrete.** The `git diff --name-only c43f538 e15ee77 -- src/rtdsl src/native` evidence is cited explicitly and limits the changed files to `rtdl_optix.cpp` and `optix_runtime.py`. The carry-forward is therefore scoped correctly to backends whose runtime code did not change.
- **OptiX raw cold/warm distinction is correctly framed.** The first run (7.04s > PostGIS 3.21s) is not claimed as a performance win; only parity is claimed. The report explicitly says "correctness parity, not a cold-run performance win." This is honest.
- **Date discrepancy on optix_raw is explained.** The artifact carries `2026-04-04` because the Linux host wrote the date at execution time; the packaging date is `2026-04-05`. The report explains this directly.
- **Skipped test is correctly classified.** The `test_frozen_k5_slice_is_parity_clean_when_local_snapshot_exists` skip is a fixture-availability skip, not a correctness failure. 1 skip in 293 is not a concern for release.
- **Goal 51 artifact is complete.** All 8 targets show `parity: true`; records match targets 1:1.

**Two gaps:**

**Gap 1 — Goal 51 artifact lacks a `validated_head` field (minor).**
The `goal51/summary.json` carries no `validated_head` or `git_sha` field. The provenance link to `e15ee77` is established only by the report narrative and directory placement. The report acknowledges this directly. It holds for audit purposes but is a self-attestation gap in the artifact file itself.

**Gap 2 — `embree_raw` carry-forward is in the JSON but absent from the narrative (minor).**
`summary.json` lists `embree_raw` (from `goal83_embree_long_exact_source_repair_artifacts_2026-04-04`) as a same-head carried artifact. The report's "Same-head artifact consistency checks" section narrates the Vulkan and OptiX carry-forwards explicitly with the git-diff justification, but does not mention the embree_raw carry-forward in prose. It is not hidden — it is in the JSON — but the parallel carry-forward rationale (no Embree native code changed across that range) is not stated in the report.

---

## 3. Agreement and Disagreement

**Agree with all pass/fail calls.** The full-matrix and slice gates passed cleanly. Parity is preserved across all fresh-run backends. The carry-forward scope is justified by diff evidence.

**Agree with the honest-conclusion framing.** The report correctly does not claim this is a ground-up rerun of every published benchmark. The distinction between "freshly rerun" and "same-head carried" is explicit and structurally enforced by the artifact directory layout.

**One framing note, not a disagreement:** The report describes Embree and Vulkan under the same paragraph heading ("Embree and Vulkan long-row position") and then explicitly lists only Vulkan in the carry-forward paths. A reader scanning the carry-forward list in the JSON would find `embree_raw` there but not in the corresponding narrative. This is internally consistent but could mislead a fast reader who stops at the prose.

---

## 4. Recommended Next Step

**The package can proceed to final release audit as-is.** No re-run is required.

Before closing the 3-AI review cycle, consider one low-cost fix in the report: add a single sentence under the "Embree and Vulkan long-row position" paragraph explicitly naming `embree_raw` (Goal 83 artifact) as a same-head carry for the same reason as Vulkan — no Embree native code changed in the `c43f538`→`e15ee77` range. This would make the narrative fully parallel with the JSON and close the prose gap without touching any artifact files.

The Goal 51 validated_head gap is noted for future artifact schema hardening but does not require action before this release.
