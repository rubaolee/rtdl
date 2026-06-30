---

## VERDICT: ACCEPT

All four questions pass. Findings and residual risks follow.

---

### Q1 — Are current public docs consistent with v2.3 and not mixing stale versions?

**PASS — Clean.**

- The audit script scanned all **72 `current_public` Markdown files** and found **zero stale-version hits** (regex covers v0.x, v1.x, v2.0, v2.1) and **zero dead local links**.
- `README.md` consistently uses "current v2.x surface" and "current released version is `v2.3`". The `examples/v2_0/` directory name is correctly treated as a stable path identifier, not a version claim (the audit script explicitly strips that string before the regex check).
- All 72 current-public pages carry the `current_ok` state in both the JSON and Markdown reports. The JSON confirms `current_needs_fix: 0`.
- No manual spot-check of `README.md` or `docs/quick_tutorial.md` finds any raw `v0.x`/`v1.x`/`v2.0`/`v2.1` strings.

---

### Q2 — Is the historical/support classification acceptable?

**PASS — Acceptable.**

- ~6,860 files are classified `classified_non_current`. All land in explicitly declared historical directories (`docs/audit`, `docs/directives`, `docs/engineering`, `docs/handoff`, `docs/history`, `docs/reports`, `docs/reviews`). None were rewritten; they are frozen audit-trail snapshots. This is the stated policy and it is correct.
- The **103 files with dead local links** are all in non-current artifacts (historical handoffs, old release docs, archived reviews). Dead links in frozen snapshots are expected and accepted; the classification approach makes this explicit.
- `docs/README.md`'s "three doors" table correctly routes learners to `learn/` (current_public), researchers to `research/` (support_artifact/advanced), and auditors to `audit/` (historical_audit). Both `docs/learn/README.md` and `docs/research/README.md` exist and resolve.
- `docs/audit/process/current_milestone_qa.md` has 11 dead links (to renamed visual demo files and old release docs) and is correctly marked `link_debt_in_non_current_artifact` — not a problem, as it is not on the learner path.

---

### Q3 — Does the pod smoke evidence cover the current tutorial/example/demo/benchmark runnable surface?

**PASS — Adequately covered.**

- **54/54 cases pass**, returncode 0 for every entry. `missing_manifest_entries: []` — every `.py` file under `examples/v2_0/` and `examples/visual_demo/` is in the manifest. There are no uncovered public entrypoints.
- Coverage by kind: tutorial (3), example (14), app (11), partner (3), benchmark (12), learner (1), demo (7). All promoted benchmark apps are explicitly smoke-gated.
- The smoke ran from a clean pod clone at `/workspace/rtdl_goal2617_smoke/` with the stated prerequisites installed (`libgeos-dev pkg-config libembree-dev`, numpy/pillow/imageio/imageio-ffmpeg via venv). This matches the documented setup in both `README.md` and `examples/README.md`.
- Most cases use `--backend cpu_python_reference` (portable path). `partner_anyhit` uses `--backend embree` (9.4 s, clean) — confirming native Embree is present.
- `robot_collision_benchmark` at 0.270 s and `triangle_counting_contract_import` at 0.313 s are intentionally small-fixture/import-only runs; the note field documents this accurately.
- GPU/OptiX paths are **not** smoke-tested: correct and expected (CPU-only pod). The docs disclaim that `--backend optix` is not a broad speedup claim without cited hardware evidence.

---

### Q4 — Are there remaining dead-link or outdated-info risks for the current public surface?

**LOW residual risk. No blocking issues.**

Three residual risks to note:

1. **External YouTube link unverified.** `README.md:200–201` and `docs/tutorials/rendering_and_visual_demos.md` both link to `https://www.youtube.com/watch?v=d3yJB7AmCLM`. The audit script's `_is_external()` skips these — correct tooling behavior, but validity is unverified. If the video is removed, two `current_public` pages gain dead links with no automated detection. The link is to a well-known service and makes no RTDL performance claim, so this is **low severity** but is a monitoring gap.

2. **Dead links in 103 historical artifacts.** These are in frozen snapshots and are off the learner path. Acceptable by design, but a user who follows the `docs/README.md` → History Index path into `docs/history/` or `docs/handoff/` will encounter broken links. No fix required; this is an inherent trade-off of the classify-don't-rewrite approach.

3. **No CI wiring of the smoke test.** The pod smoke is a one-shot manual run. There is no evidence of a CI gate that re-runs `goal2617_surface_smoke.py` on each merge. This is a **process gap** (not a docs quality issue), but means the 54/54 clean result is a point-in-time certificate, not a continuous guarantee. Recommend wiring to CI as a future action; not a blocker for acceptance of the current audit.

---

### Required Fixes

**None.** No blocking defects found.
