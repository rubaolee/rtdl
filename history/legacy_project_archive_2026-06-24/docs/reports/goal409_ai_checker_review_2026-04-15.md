Date: 2026-04-15
Reviewer role: primary checker
Ledger reviewed: `docs/reports/goal409_repo_file_status_ledger_2026-04-15.csv:1`
Master report reviewed: `docs/reports/goal409_repo_wide_file_status_audit_2026-04-15.md:1`

---

## Summary judgment

The first-pass ledger is a credible **inventory baseline**: it covers all tracked files, and its broad separation of obvious historical material from implementation/test surfaces is usable as a starting point.

It is **not yet credible as a status-truth ledger** for cleanup or release-surface decisions.

The main issue is not missing files; it is overreliance on path-only heuristics. That produces several materially wrong or weak classifications in exactly the high-risk slices the audit was supposed to challenge: front-door versioning, live-vs-historical docs, and example surfaces that are explicitly preserved rather than primary.

---

## Finding 1 — Critical: `VERSION` is stale and the ledger understates the risk

`VERSION` currently says `v0.4.0`, while the repo front door and docs index both say the current released version is `v0.6.1`; see `VERSION:1`, `README.md:23`, `docs/README.md:77`, and the Goal 409 scope in `docs/reports/goal409_repo_wide_file_status_audit_2026-04-15.md:7`.

That means the ledger’s treatment of `VERSION` as merely “live; confirm not stale” is too weak. This is a concrete correctness failure in a machine-readable root file, not a soft wording-review case.

**Required correction**
- `VERSION` freshness should be marked stale/incorrect, not “confirm not stale.”
- Misleading-content risk should be elevated to high, because it directly contradicts the live release story.
- Action should be `revise immediately`, not `inspect further`.

---

## Finding 2 — Critical: the master report’s status totals do not match the ledger

The master report says the ledger split is `3094 historical / 840 live / 51 transitional / 1 unclear`; see `docs/reports/goal409_repo_wide_file_status_audit_2026-04-15.md:34`.

The actual CSV totals are `3133 historical / 802 live / 51 transitional / 0 unclear` when counted from `docs/reports/goal409_repo_file_status_ledger_2026-04-15.csv:1`.

This mismatch matters because it means the package already contains an internal inconsistency between the summary report and the per-file ledger. Before anyone builds on the audit, the report must be regenerated or corrected to match the ledger actually checked into the repo.

**Required correction**
- Recompute and restate the status totals in the master report from the checked-in CSV.
- Remove the phantom `unclear` status unless a real row carries it.

---

## Finding 3 — High: all `doc` files were blanket-labeled `live`, which is structurally wrong

The ledger assigns all 404 `doc`-category files to `live`. That is not sustainable against the repo’s own documentation taxonomy.

The docs index explicitly says the tree contains both live docs and preserved history, and it separates “Historical And Maintainer Material” from the live reading path; see `docs/README.md:3`, `docs/README.md:63`, and `docs/README.md:132`.

Concrete false-live examples:
- `docs/archive/README.md:1` says the directory preserves historical entry points and “is not the live release surface.”
- `docs/wiki_drafts/README.md:1` says those files are “historical draft artifacts.”
- `docs/engineering/handoffs/V0_4_FINAL_RELEASE_HANDOFF_HUB.md:1` says it is an archived release handoff and “not the live source of truth.”
- `docs/current_milestone_qa.md:1` opens with “Archived Milestone Q/A” and says it is preserved historical context.
- `docs/goal_*.md` are explicitly described as reference material rather than the primary current-state narrative in `docs/README.md:132`.

This is the biggest structural defect in the ledger. The path heuristic appears to have treated almost every `docs/*.md` file outside `docs/reports/` and `docs/handoff/` as live, even when the content self-identifies as archival or historical.

**Required correction**
- Reclassify `docs/archive/**` as historical.
- Reclassify `docs/wiki_drafts/**` as historical.
- Reclassify explicit archival docs such as `docs/current_milestone_qa.md:1` and `docs/engineering/handoffs/V0_4_FINAL_RELEASE_HANDOFF_HUB.md:1` as historical.
- Revisit the blanket `docs/goal_*.md -> live` rule; these should not all be treated as live current-state docs.

---

## Finding 4 — High: the example surface is too coarsely classified

All 58 files under `examples/` are marked `live`, but the repo itself distinguishes four different example roles; see `examples/README.md:3`.

That README explicitly separates:
- release-facing first-run examples in `examples/README.md:10`
- preserved generated output in `examples/README.md:35`
- internal/historical artifacts in `examples/README.md:41`

The subdirectory READMEs reinforce the split:
- `examples/generated/README.md:1` says these are preserved generated bundles and “not the main first-run entry points.”
- `examples/internal/README.md:1` says these files are preserved for internal history, experiments, and audit support, and are not the primary release-facing path.

So the problem is not that every file in `examples/generated/` or `examples/internal/` must become historical; some are still useful and some are exercised by tests. The problem is that the ledger currently collapses release-facing, reference, generated-preserved, and internal-preserved material into one undifferentiated live example surface.

**Required correction**
- Split example judgments at least into release-facing vs preserved-supporting.
- Do not present `examples/generated/**` and `examples/internal/**` as equivalent to the first-run public examples listed in `examples/README.md:12`.

---

## Finding 5 — Medium: the generated slice is conservative in the right direction, but the example-generated slice is not

The `generated/` tree is correctly treated as transitional and regeneration-sensitive. That part of the ledger is conservative enough to build on.

The mismatch is that preserved generated artifacts under `examples/generated/**` are treated as ordinary live examples even though the repo describes them as preserved generated output; see `examples/generated/README.md:1` and `examples/README.md:35`.

**Required correction**
- Keep `generated/**` conservative.
- Apply similar provenance-aware caution to `examples/generated/**` instead of treating it as ordinary live example surface.

---

## Finding 6 — Medium: tracked build artifacts are broadly classified correctly, but one subset needs a stronger misleading-content note

The blanket `build/** -> transitional` call is directionally correct. These are tracked outputs, not stable implementation sources.

However, `build/system_audit/views/file_status.csv` and its companion summary are more dangerous than ordinary demo frames or GIFs because they can be mistaken for the current audit ledger. They need a stronger note that they are prior/generated audit outputs, not the live Goal 409 source of truth.

**Required correction**
- Keep `build/**` transitional.
- Escalate the misleading-content warning for `build/system_audit/**` specifically.

---

## Credibility verdict

The first-pass ledger is credible enough to build on **as a complete tracked-file inventory**.

It is **not yet credible enough to rely on as the repo’s live/historical truth model** without correction, because:
- a front-door root file is factually stale,
- the summary report does not match the checked-in ledger totals,
- and the `doc`/`example` slices are overclassified as live in ways the repo’s own READMEs contradict.

---

## Recommended correction set

1. Correct `VERSION` immediately and mark it stale/incorrect until fixed.
2. Regenerate the master-report status totals from the actual CSV.
3. Replace the blanket `doc -> live` heuristic with content-aware exceptions for:
   - `docs/archive/**`
   - `docs/wiki_drafts/**`
   - explicit archived docs
   - at least a large subset of `docs/goal_*.md`
4. Split `examples/**` into release-facing vs preserved/internal/generated-supporting instead of treating all 58 files as one live surface.
5. Keep `generated/**` and `build/**` conservative, but add a stronger misleading-content warning for `build/system_audit/**`.

---

## Final checker conclusion

The ledger is a good first-pass file universe and a usable starting scaffold, but it is still too heuristic-heavy to serve as the repo-wide file-status truth without revision.

My checker verdict is:

**Build on it as an inventory baseline, not as a final classification ledger.**
**Required before relying on it:** fix `VERSION`, reconcile the report totals, and reclassify the overbroad live `doc` and `example` slices.