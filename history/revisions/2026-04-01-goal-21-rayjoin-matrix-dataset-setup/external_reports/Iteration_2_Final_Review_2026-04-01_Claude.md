---

## Findings

**Criterion 1 — Frozen deliverables**

All four required deliverables are present in `goal_21_rayjoin_matrix_dataset_frozen.md`:
- Artifact matrix (Section 1): all five paper targets mapped with workload, reproduction status, and notes.
- Dataset provenance (Section 2): all eight dataset families listed with preferred provenance, current status, and local plan.
- Local profile policy (Section 4): concrete numeric profiles for Figure 13 (`lsi`) and Figure 14 (`pip`); Table 3 and overlay cases correctly defer per-pair profiles to Goal 22, contingent on dataset acquisition.
- Goal 22 blocker handoff (Section 6): eight numbered blockers across dataset, evaluation, and reporting categories.

Minor: Section 3 introduces a fourth fidelity label `fixture-subset` beyond the three in the program and setup docs. This is additive, documented, and sensible — not a contradiction.

**Criterion 2 — `5–10 minute` constraint honesty**

The constraint is carried consistently through all three documents. Concrete estimates (4–5 min, 3–5 min) are bounded within the range. Table 3 and overlay profiles defer to Goal 22 with explicit per-pair caps (`~2 min` each, total `~10 min` and `~5 min` respectively) rather than claiming precision on data that doesn't yet exist. Honest.

**Criterion 3 — `overlay` analogue boundary**

The boundary is stated in three places: the artifact matrix note, Section 5 (semantic boundaries), and the Table 4/Figure 15 profile policy. The implementation report repeats the requirement that later reports must use the label `overlay-seed analogue`. Unambiguous.

**Criterion 4 — Goal 21 acceptance bar**

All five items from the acceptance bar in `goal_21_rayjoin_matrix_dataset_setup.md` are satisfied: every paper-target artifact is mapped, every mapped case has a dataset status and provenance label, every locally runnable case has a reduced-size profile, and every unresolved blocker is named explicitly.

---

## Decision

Goal 21 delivered exactly what its setup document required. The frozen matrix is complete, the provenance ledger is honest about missing data, the profile policy is bounded and coherent, and the Goal 22 blocker list is scoped and numbered. There is no ambiguity about what Goal 22 must do or how Goal 23 will consume the output. No corrections required before handoff.

Goal 21 accepted by consensus.
