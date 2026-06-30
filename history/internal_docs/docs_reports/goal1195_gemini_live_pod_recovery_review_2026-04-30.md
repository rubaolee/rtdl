# Goal1195 Misnamed External Review: Goal1194 Live Pod Recovery

Date: 2026-04-30
Reviewer: Claude (Sonnet 4.6), not Gemini
Scope: Evidence-readiness review only — not release authorization, not public speedup authorization

Attribution note: this file name is misleading. The local Gemini attempt was
blocked by model capacity. Claude wrote this review while responding to a
Gemini-named handoff prompt. This file must not be counted as Gemini review or
3-AI consensus evidence.

---

## Verdict: ACCEPT

The recovery trail is acceptable as evidence-readiness for public-wording review under the Goal1193 intake contract. The two-AI consensus report may proceed.

---

## Question-by-Question Findings

### Q1. Is the final bundle acceptable as schema/parity/timing evidence for all six app pairs?

**Yes.**

The final intake (`goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30`) reports:

- `valid: true`
- `artifact_count: 12`, `valid_schema_artifact_count: 12`
- All 12 artifacts: `exists=true`, `valid_schema=true`, `timing_floor_met=true`
- `not_ready_apps: []`
- `public_wording_review_ready_pair_count: 6`

Every artifact has zero `missing_required_paths`, zero `failed_truth_paths`, and no parse errors. The intake JSON and the matching markdown table are internally consistent. All six pairs clear the 0.1-second timing floor.

One minor discrepancy: the final intake JSON reports `archive_exists: false` and `sha256_file_exists: false`. This is because the intake tool searched for a tgz adjacent to the `final_recovery2/` directory tree rather than at the bundle path cited in the recovery report (`goal1194_live_pod_2026-04-30/goal1194_goal1192_public_wording_evidence_batch_final.tgz`, SHA256 `620607286c7f50e5b162de1ada6c5f18b522b662e95e83b91e31fded0752e6e5`). The artifacts themselves are present and validated at the correct paths. This is a non-blocking path-lookup mismatch in the archive check, not a missing artifact.

**Conclusion:** The final bundle satisfies the Goal1193 intake contract for all six app pairs.

---

### Q2. Are the live executor dependency fixes (`cuda-nvcc-13-0`, `libembree-dev`) acceptable bootstrap fixes?

**Yes. They do not invalidate the prior Goal1194 packet.**

The two fixes installed on the live pod were:

- `cuda-nvcc-13-0`: the CUDA compiler binary `/usr/local/cuda/bin/nvcc` was absent from the pod image. Installing the missing system package restores the expected compile-time environment.
- `libembree-dev`: the Embree headers (`embree4/rtcore.h`) were absent, causing native strict baseline compilation failures. Installing the missing header package restores the expected compile-time environment.

Neither fix alters application logic, benchmark contracts, artifact field schemas, timing methodology, or public wording boundaries. The original Goal1194 packet was architecturally correct; the pod simply lacked two packages that a canonical RTX build environment requires. Installing missing system packages that the design assumes are present is a routine bootstrap fix, not a methodology change.

**Conclusion:** Bootstrap fixes accepted. Goal1194 packet not invalidated.

---

### Q3. Does the Jaccard first-run failure require keeping Jaccard out of public speedup wording?

**The first-run failure does require a caution annotation on Jaccard, but Jaccard is not a candidate for positive speedup wording in any case.**

The failure trail is:

| Stage | OptiX phase (sec) | Schema valid | Parity |
|---|---:|---|---|
| First run (partial intake) | 2.019 | False | fail |
| Recovery run chunk-512 (recovery intake + final intake) | 1.621 | True | pass |

The first-run `polygon_jaccard_safe_chunk_optix.json` failed parity (`parity_vs_cpu=fail`). Targeted probes identified chunk-sensitive or nondeterministic behavior. The recovery artifact at chunk-512 passed schema and parity.

However, the raw ratio in the accepted final bundle is `embree_over_optix = 0.549`, meaning Embree took ~0.89 s and OptiX took ~1.62 s. **OptiX is measurably slower than Embree for Jaccard on this evidence.** There is no positive speedup claim available for Jaccard regardless of the recovery outcome.

The recovery trail is adequately documented (partial intake → recovery intake → final intake, with the chunk-sensitivity diagnosis preserved). For evidence-readiness purposes, the final chunk-512 artifact is acceptable: schema-valid, parity-valid, timing-floor-clear.

**Required annotation (not a block):** Any public-wording document that lists Jaccard must note (a) the first-run parity failure and its documented cause, and (b) that the final evidence shows OptiX is slower than Embree on the measured phase. Jaccard must not be cited in any positive RTX speedup context.

---

### Q4. Does the final evidence support only evidence-readiness, not release or public speedup authorization?

**Yes. The evidence supports evidence-readiness only.**

The raw phase ratios (Embree / OptiX) across the six pairs are:

| App | Raw ratio | Interpretation |
|---|---:|---|
| `database_analytics` | 0.792 | OptiX slower |
| `graph_analytics` | 0.500 | OptiX slower |
| `road_hazard_screening` | 4.014 | OptiX faster (~4×) |
| `polygon_pair_overlap_area_rows` | 0.839 | OptiX slower |
| `polygon_set_jaccard` | 0.549 | OptiX slower |
| `hausdorff_distance` | 13.728 | OptiX faster (~13.7×) |

Four of six apps show OptiX slower than Embree on the measured phase. Only `road_hazard_screening` and `hausdorff_distance` show an OptiX advantage. Even for those two, any public claim must be strictly scoped to the measured prepared/native RT sub-path and must not imply whole-app speedup, default-mode speedup, or universal RTX acceleration.

The recovery report itself repeats this boundary clearly, and the intake boundary field reads: "This intake validates copied Goal1192 evidence artifacts only. It does not run cloud, does not authorize release, and does not authorize public RTX speedup wording by itself."

The Goal1195 protocol requires a two-AI consensus report before any public status or documentation updates. That gate is still open and must be cleared.

**Conclusion:** Evidence supports readiness for public-wording review. It does not authorize release or public speedup claims.

---

## Summary of Required Fixes / Conditions

None blocking. The following conditions apply before public-wording documents are finalized:

1. **Archive path discrepancy** — the final intake's archive check found no tgz because it searched the wrong relative path. Confirm the bundle tgz and its SHA256 are stored at the path cited in the recovery report and update the intake or bundle placement so a future re-check resolves. Non-blocking for evidence-readiness; must be resolved before any downstream tooling relies on the archive field.

2. **Jaccard caution annotation** — any public-wording document listing Jaccard must note the first-run parity failure, the chunk-sensitivity explanation, and that the final evidence shows OptiX is slower. Jaccard must not appear in positive speedup lists.

3. **Per-app scope constraint** — public wording for `road_hazard_screening` and `hausdorff_distance` (the only apps with raw ratio > 1.0) must be limited to the specific measured sub-path. Wording must not generalize to whole-app, default-mode, or workload-class speedup.

4. **Two-AI consensus gate** — this review represents one AI slot. The second AI review and the consensus report must be completed before public documentation is updated.

---

## Review Status

- Evidence-readiness: **ACCEPT**
- Release authorization: not reviewed here; not granted by this evidence
- Public speedup authorization: not reviewed here; not granted by this evidence
- Next required step: second AI review slot + two-AI consensus report
