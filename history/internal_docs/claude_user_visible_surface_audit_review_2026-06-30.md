# Claude Review — User-Visible Surface Audit (v2.14 cleanup)

Date: 2026-06-30
Reviewer: Claude (independent external reviewer)
Under review: `history/internal_docs/call_for_review_claude_user_visible_surface_audit_2026-06-30.md`
and the claimed cleanup of `README.md`, `docs/`, `tutorials/`, `examples/`.

## Verdict

```text
verdict: approve_user_visible_surface_audit
P0: none
P1: none
P2/Note: 2 (below)
```

The public v2.14 surface is clean, coherent, and properly isolated from
internal/experimental material. **I re-ran the leak scans myself rather than
trusting the claimed "no matches," and the claims held up** — a notable contrast
to the v3.0 build/test leak and the Goal4806 misleading recheck, where claimed
cleanliness did not survive verification. Credit where due: this cleanup is
verifiable and accurate.

## What I independently verified (not trusting the report)

- **Process/AI/V3-V4 leak scan** (`Goal\d+|Claude|Gemini|Antigravity|Codex|verdict|V4.0|V3.0|v4.0|v3.0|Phoenix|exp-project|call_for_review`) across `docs/`, `tutorials/`, `examples/`, and `README.md`: **no matches** in any of them. (The main AI's scan command excluded the root `README.md` from my first pass; I scanned it separately — also clean.)
- **Stale internal-path scan** (`docs/(reports|reviews|handoff|audit|research|history)|rebuild/v3|future/v4|examples/(internal|generated|legacy_or_backend_proofs|benchmark_apps)`) in `docs/`: **no matches**.
- **VERSION** = `v2.14`; README states "current v2.14 source-tree RTDL surface." ✅
- **`docs/` no longer contains** reports/reviews/handoff/audit/research/history subdirs — they were moved out. ✅
- **Isolation honestly disclosed:** README layout table labels `exp-project-1/` as "Isolated post-v2.14 experimental project record; not part of the current user surface," and links `history/` once as "you do not need this." Good navigation, not a leak.
- **Link integrity:** every primary link target exists — `history/README.md`, `docs/release_reports/v2_14/{README,public_rt_vs_embree_comparison,public_wording_boundaries}.md`, `docs/learn/current_claim_boundaries.md`, `docs/learn/source_tree_doctor.md`, `docs/public_documentation_map.md`, `tutorials/current/README.md`, `examples/current/README.md`. No broken primary links.
- **Per-file audit exists** (`history/internal_docs/user_visible_file_audit_2026-06-30.md`).
- **Performance wording is conservative:** the README's RayJoin/OptiX wording is "near parity in one public CDB slice," "narrow OptiX-over-Embree win," "does not become a RayJoin-system speedup claim," "mixed engineering evidence rather than broad RT-core wins." Correct and evidence-gated.

## Answers to the nine questions

1. **Scope matches the requirement?** Yes — README + docs/tutorials/examples in scope; src/tests/scripts/history/exp-project-1 correctly excluded.
2. **Per-file audit gives one row per file with the four answers?** The audit file exists for 182 files; I spot-checked the primary entrypoints, did not byte-verify all 182 rows (see Note 2).
3. **Remaining public-surface leakage (V3/V4, goal numbers, AI/process language, old internal paths, old example paths)?** **None found** in my independent scans.
4. **`docs/release_reports/v2_14/` clean as a public package?** The package files exist and are referenced as a release package, not an internal closeout; no process leaks found. Acceptable.
5. **`history/` and `exp-project-1/` sufficiently separated yet preserved?** Yes — at top level, honestly labeled, linked only as optional/maintainer material.
6. **README navigation comfortable for a new user?** Yes — it leads with the DSL idea, Start-Fast, then conservative boundaries; churn is isolated to one honest "you don't need this" history pointer.
7. **Files that should be moved out of the user surface?** None found.
8. **Broken links / stale refs / misleading performance claims missed?** No broken primary links; performance claims are conservative and correctly caveated. See Note 1 on RayJoin.
9. **Does the evidence support approving the v2.14 public surface?** Yes.

## P2 / Notes (non-blocking)

- **Note 1 (RayJoin wording — keep it scoped):** "RayJoin" legitimately appears in the README as a public benchmark with conservative wording. Given the open Goal4806 finding (released V4 cannot do generic-language Section 5.7, and Section 5.7 paper reproduction is unproven), confirm the v2.14 RayJoin wording stays scoped to the public CDB slice and **never implies full RayJoin Section 5.7 paper reproduction**. It currently does not — keep it that way.
- **Note 2 (scope of my verification):** I verified the leak classes comprehensively across the public surface, plus primary entrypoints and link targets. I did **not** byte-verify all 182 audited files or all 88 link-checked files individually. My confidence is high (pattern scans cover the leak classes), not exhaustive. If you want a hard guarantee, a second pass should diff the per-file audit's "remediation" column against the actual files.

## Non-authorization

This approval covers only the cleanliness/coherence/separation of the public
v2.14 documentation and example surface. It does not authorize V3/V4 release
claims, new benchmark/performance claims, paper-reproduction claims, runtime/source
changes, or package-install promises beyond the source-tree v2.14 surface.
