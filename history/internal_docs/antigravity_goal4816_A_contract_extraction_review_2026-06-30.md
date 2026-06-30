# Goal4816-A RayJoin Contract Extraction Review

- **Date:** 2026-06-30
- **Reviewer:** Antigravity (AI Coding Assistant)
- **Review Target:** [goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md)
- **Verdict:** `approve_goal4816_A_contract_extraction_authorize_4816_B`

---

## Verdict Description
The contract extraction performed under **Goal4816-A** is thorough, factually correct, and aligns perfectly with prior plan recommendations. It correctly isolates RayJoin-specific bundled helpers from generic RTDL primitives, captures the critical Simulation of Simplicity (SoS) tie-breaking rules and the exact-ready execution statistics from **Goal4380**, and properly frames the scope of the reproduction effort. Therefore, Goal4816-A is approved, and **Goal4816-B** is authorized to proceed.

---

## Findings

### P2 Findings (Informational / Minor Improvements)
- **F-01: User-Local Path Dependencies:** The note references local files located in the user's Downloads directory:
  - `C:\Users\Lestat\Downloads\ics24 (1).pdf`
  - `C:\Users\Lestat\Downloads\rayjoin_pip_determinism_summary.md`
  *Recommendation:* These files should eventually be archived in an in-repo location (such as `history/reference/` or `docs/`) to ensure long-term reproducibility across different workspaces and CI environments. However, since the critical quotes, formulas, and data are copied verbatim into the extraction markdown, this does not block the completion of Goal4816-A.

---

## Answers to the 10 Specific Questions

### 1. Does the note correctly distinguish full Section 5.7 polygon overlay from scalar LSI/PIP or candidate-stage continuation rows?
Yes. The note explicitly states under the "Paper Contract - Workload" section that the Section 5.7 Polygon Overlay workload combines Line Segment Intersection (LSI), Point-in-Polygon (PIP), midpoint point-location, and output-chain construction. It emphasizes that scalar LSI/PIP or candidate-stage continuation rows alone do not constitute a full reproduction of the paper's workload.

### 2. Does it correctly record the author source commit and the fact that source semantics must be read via `git show HEAD:<file>` because the POD worktree is dirty?
Yes. The note records the author source commit as `02bf6220d6d20b04af77ee20364eced75cc029c9` and explains that because the POD worktree contains debug edits from Goal4806, the only authoritative way to read the source files is via `git show HEAD:<file>`.

### 3. Does it correctly extract the LSI contract: query segment as RT ray over `[0, 1]`, exact predicate after RT candidate generation, and pair output for later overlay construction?
Yes. The note extracts these details from the paper and verifies them against the author's source code (`src/algo/rt_lsi_custom.cu`). Specifically, it captures that the query segment is cast as a ray over `[tmin, tmax] = [0, 1]`, that candidate base edges are validated by an exact LSI predicate inside the intersection shader, and that intersection pairs are generated for downstream overlay chain construction.

### 4. Does it correctly extract the PIP/point-location contract: vertical ray, closest boundary edge, face-id derivation, and query-map-dependent SoS?
Yes. The note outlines that the PIP phase casts a vertical ray upward `(0, 1, 0)`, finds the closest valid boundary edge in the opposite map, translates the closest edge to its containing face/polygon using left/right face metadata, and applies the query-map-dependent Simulation of Simplicity (SoS) endpoint rule for boundary handling.

### 5. Does it correctly incorporate the user-provided author-reply determinism summary: equal-height candidates, OptiX strict `t < tmax` pruning, and the need to encode SoS tie-break into reported `t`?
Yes. The note documents the root cause of the non-determinism (equal-height candidates reporting the same primary `t` being strictly pruned by OptiX, which leads to BVH-dependent traversal ordering issues). It incorporates the author's recommended tie-breaker logic, using normalized slopes and a perturbed `t_reported` distance to encode the SoS tie-breaker before returning the intersection distance to OptiX.

### 6. Does it correctly flag the tension that author `HEAD:rt_pip_custom.cu` has internal slope tie-break logic but still reports unperturbed `t`, while the author-reply summary requires `t_reported` perturbation for determinism?
Yes. Under the "Author-Reply Determinism Contract" section, the note highlights that the author's committed `HEAD:src/algo/rt_pip_custom.cu` shader implements the slope comparison internally but still reports the unperturbed `t` to OptiX, which does not prevent strict pruning bugs. It flags that future work must explicitly choose between replicating the committed `HEAD` behavior or implementing the clarified deterministic behavior.

### 7. Does it correctly preserve Goal4380 as bounded 2/8 available-input evidence, not full 8/8 Section 5.7 reproduction?
Yes. The note carries forward the exact benchmark results from Goal4380 (County x Zipcode and Block x Water) and clearly states that this constitutes only 2/8 of the available datasets, that the timings represent process wall time close to the author's baseline rather than full hot-compute parity, and that it does not represent full 8/8 reproduction.

### 8. Does it correctly separate `bundled_rayjoin_helper` from `existing_v2_14_primitive`, so future work cannot treat bundled RayJoin code as generic user-language capability?
Yes. In its classification section, the note designates `src/rtdsl/rayjoin_overlay.py::_run_lsi_rows`, `_run_point_location_faces`, and `_PreparedPointLocationRunner` as `bundled_rayjoin_helper` implementations rather than generic user-facing primitives. This prevents laundering these bundled helpers as generic capability claims.

### 9. Is the proposed Goal4816-B taxonomy complete enough to prevent hidden runtime edits, bundled-helper laundering, scalar-only overclaiming, and missing-input overclaiming?
Yes. The classification taxonomy consists of eight distinct categories (`existing_v2_14_primitive`, `bundled_rayjoin_helper`, `numba_partner_continuation`, `paper_app_logic`, `author_baseline_only`, `missing_input`, `missing_v2_14_capability`, and `unresolved_pip_tie_break_contract`). This granularity forces any missing, bundled, or non-deterministic behavior to flag explicitly, leaving no room for hidden patches or overclaiming.

### 10. Should Goal4816-B be authorized as the next step, or must Goal4816-A be amended first?
Goal4816-B is authorized to proceed as the next step. Goal4816-A has met all criteria, successfully extracted all paper, source, and determinism contracts, and resolved all concerns raised in the plan review. No amendments to Goal4816-A are necessary.

---

## Authorization Statement

Goal4816-B is **authorized** to proceed. Goal4816-B is strictly limited to the inventory and classification of the existing v2.14 capabilities and assets against the extracted Section 5.7 stages.

---

## Non-Authorization Block

This review does **NOT** authorize:
1. Modifying any files under `src/rtdsl/**`, `src/native/**`, or the v2.14 release surface.
2. Adding any new RayJoin-specific RTDL runtime primitives.
3. Running any POD performance or benchmark execution experiments.
4. Presenting bundled-helper output as a generic RTDL language reproduction.
5. Presenting scalar LSI/PIP or Numba candidate rows as a full polygon overlay reproduction.
6. Claiming full 8/8 Section 5.7 reproduction based on the current 2/8 evidence.
