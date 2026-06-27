Now I have everything. Here is the review.

---

## Verdict

**PASS as a preparation artifact. NOT cleared for tag or release.**

The matrix does what it is designed to do: it inventories all 18 public apps, enforces a fail-closed gate, is honest about pod need, does not overclaim speedup, and correctly quarantines `collect-k` and `python_partner_rtdl`. Four required changes must be resolved before this can serve as the final pre-pod gate.

---

## Strengths

**All-app coverage is real, not nominal.** `validate_manifest()` cross-checks `covered_apps` against `rt.public_apps()` at runtime and fails hard on any mismatch. The two frozen apps (`apple_rt_demo`, `hiprt_ray_triangle_hitcount`) are explicitly excluded with documented rationale — not silently absent.

**Fail-closed triple lock holds.** `release_authorized: false`, `tag_authorized: false`, and `public_claim_allowed_from_this_manifest_alone: false` on every single entry. The validator enforces the first two; the test enforces all three. The script cannot emit a valid artifact without these flags.

**Pod need is accurately characterized.** `pod_needed_now: false` and `pod_required_for_final_perf_evidence: true` appear in the JSON, the MD, the preflight report, and the tests — consistently. There is no ambiguity about where the release gate sits.

**No speedup overclaiming.** `whole_app_speedup` and `broad_rtx_or_gpu_acceleration` are explicitly blocked. Per-app notes on legacy-customized surfaces ("measure honestly but do not use as app-generic proof") actively prevent cherry-picking. `python_interface_dominated` is called out for `database_analytics`, `polygon_pair_overlap_area_rows`, and `polygon_set_jaccard` — this is honest and will prevent surprise when pod numbers are flat for those apps.

**`collect-k` quarantine is explicit and mechanically enforced.** `stable_collect_k_bounded_promotion` is blocked. `segment_polygon_anyhit_rows` and `polygon_set_jaccard` are both tagged `experimental_primitive_blocked`. Notes on each say "do not promote collect-k from this alone" / "keep chunk boundary explicit."

**Purity taxonomy is meaningful.** The four-level classification (`pure_python_rtdl_ready`, `legacy_engine_customized`, `experimental_primitive_blocked`, `frozen_or_demo_only`) correctly separates apps that can carry a public purity claim from those that cannot.

**Per-entry structure is substantive.** Each active entry has tailored scope, multi-source baseline (CPU + Embree + third party where applicable), specific acceptance criteria, and a fully-parameterized pod command. This is not boilerplate — `robot_collision_screening` at 200K poses is different from `service_coverage_gaps` at 20K copies in meaningful ways.

**Local preflight passed cleanly.** 16/16 commands, 0 failures, 2 frozen apps correctly excluded. Preflight and perf-matrix are cross-referenced by filename in both the MD and the test.

---

## Risks

**`python_interface_dominated` apps will produce weak pod evidence.** `database_analytics` and `polygon_pair_overlap_area_rows` are both classified this way. When pod numbers come back flat or noisy for these apps, the release discussion must not treat them as OptiX failures or successes — they are interface-latency measurements. The matrix doesn't define what the team should do with such numbers post-pod. This could stall the consensus gate.

**No numeric pass/fail threshold for the pod gate.** Acceptance criteria use qualitative language ("strict parity," "summary parity," "phase timing"). There is no statement of the form "OptiX traversal time ≤ Embree baseline on ≥N apps constitutes a pass." Without this, the post-pod decision is undefined and will require ad-hoc judgment under pressure.

**`3ai_consensus` is an opaque gate.** `release_tag_action_before_perf_evidence_and_3ai_consensus` is blocked but the definition of what constitutes 3AI consensus is nowhere in the manifest. For a public release, the gate criteria need to be written down before the pod runs, not after.

**`all_public_apps_covered: true` is frozen in the emitted JSON.** `build_manifest()` computes this dynamically against `rt.public_apps()` at generation time. If the public-apps list changes after the artifact is written, the JSON silently reads `true` while the list has drifted. The test re-runs `build_manifest()` live, so it would catch this — but only if the test suite is re-run.

---

## Required Changes

**1. Add `true_zero_copy` to `validate_manifest()`'s explicit blocked-claim check.**

`tests/goal1659_v1_6_11_perf_matrix_test.py:43` checks `true_zero_copy` as a required blocked claim. `scripts/goal1659_v1_6_11_perf_matrix.py:279-283` checks only four claims and does not include it. This asymmetry means a future edit could remove `true_zero_copy` from the JSON without the validator catching it — only the test would. The validator is the production gate; it must be at least as strict as the test.

```python
# validate_manifest(), line ~279 — add to the tuple:
for claim in (
    "whole_app_speedup",
    "broad_rtx_or_gpu_acceleration",
    "true_zero_copy",          # <-- missing
    "stable_collect_k_bounded_promotion",
    "python_partner_rtdl",
):
```

**2. Distinguish `outlier_detection` and `dbscan_clustering` pod commands, or document explicitly that they share a fixture.**

`scripts/goal1659_v1_6_11_perf_matrix.py:182-195` — the pod commands for these two apps are byte-for-byte identical except for `--output-json`. Neither passes a `--scenario` flag. If `goal757_optix_fixed_radius_prepared_perf.py` does not internally distinguish the two scenarios by some other mechanism, then both entries are measuring the same code path and one of them provides no independent coverage. Either add a `--scenario` argument to one or both, or add a note to each entry stating "same fixture as `<other_app>`; independent coverage is via separate output record only" — and be honest in post-pod reporting that these are not independently validated workloads.

**3. Explain `--skip-validation` in notes for `facility_knn_assignment` and `robot_collision_screening`.**

`scripts/goal1659_v1_6_11_perf_matrix.py:110,200` — both pod commands include `--skip-validation`. The current notes explain what is out of scope but not why validation is suppressed for the performance run. One sentence each is enough: for facility, something like "validation skipped because ranked-KNN output is out of scope and would trigger unrelated checks"; for robot, "validation separated per acceptance criteria to isolate traversal timing from mesh correctness." Without this, a reader of the pod results has no basis to know whether a suppressed assertion is a deliberate scope exclusion or an overlooked correctness gap.

**4. Define a numeric or binary pod-gate decision rule before the pod runs.**

The matrix defers the actual release decision to post-pod consensus, but gives no written criterion. Before the pod is started, add a `pod_pass_criteria` block to the manifest (and a corresponding validation check) that states the minimum bar — e.g., "OptiX traversal time < Embree baseline on ≥10 of 16 active apps, no regression on pure-Python-RTDL apps." The exact numbers can be debated, but they must be written down before the evidence exists, not after. Without this, `3ai_consensus` is undefined and the gate can expand indefinitely.
