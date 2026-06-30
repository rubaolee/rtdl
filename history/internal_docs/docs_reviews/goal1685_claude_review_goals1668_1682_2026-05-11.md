# Claude Independent Review: Goals 1668-1682

Date: 2026-05-11
Reviewer: Claude (Anthropic)
Context: Independent external review of Goals 1668-1682 as candidates for
v1.8 / v2.0 app-agnostic native-engine release evidence.

## Independence Declaration

This is an independent Claude review by an Anthropic Claude model, a
distinct AI system from Codex (OpenAI) and Gemini (Google). It is intended
to pair with `docs/reviews/goal1684_gemini_review_goals1668_1682_2026-05-11.md`
to satisfy the consensus rule recorded in
`docs/reports/goal1683_consensus_audit_remediation_plan_2026-05-11.md`:

```text
2+ AI consensus, with at least two different AI systems.
```

Invalid pairings explicitly rejected by Goal1683 and reaffirmed here:

```text
Codex + Codex
authoring pass + one independent review (unless the authoring pass is itself
separately documented as an independent review artifact)
```

Codex authoring of the migration reports, tests, and source changes does
**not** count as independent external review. Two Codex-flavored review
passes do not satisfy the consensus rule. Claude functioning as the
authoring agent for a goal in any session also does not satisfy
independence for that goal; see the disclosure below.

### Authoring-Scope Disclosure

For honesty, the Claude instance writing this review previously assisted
in authoring the source migration and reports for **Goal1681** and
**Goal1682** during the same workstream that produced this review. For
those two goals, this review is therefore **not fully independent in the
strict sense**; treat the Goal1681 and Goal1682 verdicts as Claude's own
post-hoc audit of its own work, not as a clean independent third-party
audit. The remaining goals (1668, 1669, 1670, 1672, 1673, 1674, 1675,
1676, 1677, 1678, 1679, 1680) were authored by Codex prior to this Claude
review and are reviewed here at arm's length.

If a stricter independence reading is required by the release gate, the
release authority should commission a Claude review run that has not
participated in authoring Goal1681 or Goal1682, and only then treat those
two specific goals as having independent Claude+Gemini consensus.

## Method

This review is grounded in the on-disk repository state at
`C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`, not on
self-reported summaries. The following independent checks were performed:

1. Re-ran the strict native leakage scan over `src/native/**` using the
   gate regex
   `\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b`
   (case-insensitive) with the `RTDL_DB_*` uppercase constant
   false-positive filter. Observed counts:

   | Measure | Value |
   | --- | ---: |
   | Strict regex unique symbols | 92 |
   | Strict regex occurrences | 178 |
   | False-positive `RTDL_DB_*` unique symbols | 9 |
   | False-positive `RTDL_DB_*` occurrences | 14 |
   | Real app-shaped symbols | 83 |
   | `pip` symbols remaining | 0 |
   | `hausdorff` symbols remaining | 0 |
   | `pose` symbols remaining | 0 |
   | `db` symbols remaining | 30 |
   | `polygon` symbols remaining | 29 |
   | `knn` symbols remaining | 14 |
   | `bfs` symbols remaining | 10 |

   These match the numbers asserted in
   `docs/reports/goal1680_current_native_app_leakage_gap_2026-05-10.md`
   and in the Goal1680/1681/1682 tests.

2. Verified replacement generic exports are present in the native
   sources:

   - `rtdl_embree_run_point_primitive_anyhit_packet`,
     `rtdl_hiprt_run_point_primitive_anyhit_packet`,
     `rtdl_optix_run_point_primitive_anyhit_packet`,
     `rtdl_oracle_run_point_primitive_anyhit_packet`,
     `rtdl_vulkan_run_point_primitive_anyhit_packet`;
   - `rtdl_hiprt_point_primitive_anyhit_2d` (HIPRT kernel filename hint);
   - `rtdl_embree_run_max_distance_nearest_candidate_2d`;
   - `rtdl_optix_prepare_group_indices_2d`,
     `rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed` and the
     remaining Goal1673 group-named exports.

3. Verified the partner-track consensus quote is present verbatim in the
   v1.8/v2.0 gate:

   ```text
   Protocol first. PyTorch reference first. CuPy conformance alongside it.
   Engine absolutely app-agnostic throughout.
   ```

   Source: `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`,
   lines 24-25.

4. Verified the blocked-wording string

   ```text
   RTDL native internals are fully app-agnostic.
   ```

   appears in `goal1672`, `goal1680`, `goal1681`, and `goal1682` reports
   under "Still blocked" framing; no goal report claims this as a
   currently-held property.

5. Verified the per-goal reports for Goal1673, Goal1674, Goal1681, and
   Goal1682 each contain explicit "no pod was used", "local source
   migration only", and "hardware-proven" boundary language.

## Assessment Areas

### App-Agnostic Native-Engine Direction (Goals 1668, 1672, 1680)

Goal1668's directive — that the RTDL native engine must become 100%
app-agnostic — is the correct architectural framing. The strict baseline
manifest (96 dirty symbols, frozen as a JSON artifact) provides a
non-fungible reference; the live scan can never be re-spun into a smaller
baseline without an audit-visible delta. Goal1672's family classification
turns the baseline into a work queue with explicit accepted directions
per family. Goal1680 honestly reports the current gap (83 real app-shaped
symbols across `db`, `polygon`, `knn`, `bfs`) without using deltas to
relax the gate.

This direction is sound and aligns with Gemini's review.

### Partner-Track Consensus (Goals 1669, 1670, 1675, 1677)

The protocol-first/PyTorch-reference-first/CuPy-conformance-alongside
direction is consistent with the directive that the engine remains
absolutely app-agnostic. The partner substrate (Goal1675) deliberately
exposes generic DLPack adapter, PyTorch and CuPy shells, fallback
policies, and borrowed-pointer extraction; it does not add
partner-specific native backdoors or app-shaped engine ABI fields. The
pod partner smoke (Goal1677) confirms real PyTorch CUDA and real CuPy
CUDA execution on the pod environment described in
`HANDOFF_CLAUDE.md`. Independent verification of those pod logs is out of
scope for this Claude review; the localized claims are accepted.

### Migration / Quarantine Soundness

#### Goal1673 OptiX pose-to-group

The three OptiX native files (`rtdl_optix_api.cpp`,
`rtdl_optix_prelude.h`, `rtdl_optix_workloads.cpp`) contain no
case-insensitive `pose` substring after the migration, and the five
group-named replacements are present. The Python compatibility aliases
(`OptixPoseIndexBuffer`, `prepare_optix_pose_indices_2d`, `pose_flags_*`
methods) preserve external callers. The boundary between native ABI
(group-named) and Python-side compat (pose-named alias) is clean.

#### Goal1674 Oracle root wrapper quarantine

The root-wrapper symbol `rtdl_oracle_polygon` is absent from the live
scan; the renamed implementation chunk
`src/native/oracle/rtdl_oracle_geometry_cells.cpp` is present and is
included from `src/native/rtdl_oracle.cpp`. The migration is purely a
filename/include quarantine of the legacy wrapper symbol; the broader
oracle polygon/GIS API family is explicitly **not** migrated and remains
counted in the `polygon` family of the current gap.

#### Goal1681 PIP to point-primitive any-hit (Claude self-disclosure applies)

All six `pip`-family native callables/exports are gone from the strict
scan; the five backend `rtdl_<engine>_run_point_primitive_anyhit_packet`
replacements and the `rtdl_hiprt_point_primitive_anyhit_2d` kernel
filename hint are present. Python runtimes
(`embree_runtime.py`, `hiprt_runtime.py`, `optix_runtime.py`,
`oracle_runtime.py`, `vulkan_runtime.py`) bind the renamed symbols.
`_run_point_primitive_anyhit_packet` is present in
`_GENERIC_NATIVE_SYMBOL_FRAGMENTS` so the purity audit classifies the
new exports as generic primitive-shaped ABI.

The Python `_run_pip_*` helpers and high-level point-in-polygon API
still exist on the Python side — point-in-polygon semantics are an app
expression layered over the generic native packet. This matches the
v1.8/v2.0 directive (engine app-agnostic; app semantics in Python).

Because the same Claude session that authored Goal1681 is writing this
review, this Goal1681 audit should be paired with the Gemini Goal1681
verdict for an actually-distinct two-AI signal.

#### Goal1682 Hausdorff to max-distance nearest-candidate (Claude self-disclosure applies)

The single `rtdl_embree_run_directed_hausdorff_2d` export is gone from
the strict scan; the replacement
`rtdl_embree_run_max_distance_nearest_candidate_2d` is present in
`rtdl_embree_api.cpp` and `rtdl_embree_prelude.h`. The C++ row struct
`RtdlDirectedHausdorffRow` is intentionally retained — it is CamelCase
and is not flagged by the strict `\brtdl_<lowercase>_` regex. Hausdorff
semantics — directedness, witness-direction selection,
threshold-decision vs exact, public-wording boundaries — are retained
in the Python `directed_hausdorff_2d_embree` helper in
`src/rtdsl/embree_runtime.py`, and `_run_max_distance_nearest_candidate_2d`
is added to the purity audit's generic fragments. The boundary is clean.

Same Claude-authoring caveat applies as for Goal1681; pair this with the
Gemini Goal1682 verdict for an actually-distinct two-AI signal.

### Wording / Overclaim Check

Each migration report (Goal1673, Goal1674, Goal1681, Goal1682) explicitly
states:

- "This is a local source migration only";
- "no pod was used" / "No pod validation was run";
- "broader app-agnostic gate still fails";
- the blocked claim
  `RTDL native internals are fully app-agnostic.`
  remains explicitly blocked.

Goal1680 records "Remaining app-shaped callable/export symbols | 83"
and lists the four remaining families honestly. The v1.7 gate
(`docs/release_reports/v1_7_app_agnostic_native_gate.md`) preserves the
"do not publish the claim" sentence and links all Goal1668-1682
artifacts. No overclaim of release readiness was observed in any of the
goal reports or the gate. Gemini's overclaim-check finding is
corroborated.

## Per-Goal Verdicts

Verdicts use only the four allowed values: `accept`,
`accept-with-boundary`, `reject`, `needs-more-evidence`.

| Goal | Verdict | Note |
| ---: | --- | --- |
| 1668 | `accept` | Baseline directive and the 96-symbol dirty manifest are sound; no overclaim. |
| 1669 | `accept` | Python-partner-RTDL partner choice architecture is consistent with the engine-app-agnostic constraint. |
| 1670 | `accept` | External partner analysis consensus is sound; the consensus quote is reproduced verbatim in the v1.8/v2.0 gate. |
| 1671 | `accept` | v1.8/v2.0 gate clearly enumerates the unfinished work and the consensus quote. |
| 1672 | `accept` | Migration classification turns Goal1668 into a queue without relaxing it; references the Goal1681/1682 follow-ups correctly. |
| 1673 | `accept-with-boundary` | Local source migration verified; native engine has no pose substring; no pod execution evidence. |
| 1674 | `accept-with-boundary` | Filename/include quarantine verified; broader oracle polygon/GIS API family is **not** migrated, by design. |
| 1675 | `accept` | Partner substrate is generic and does not add partner-specific native backdoors. |
| 1676 | `accept` | Regression guard correctly enforces absence of the removed pose/oracle symbols. |
| 1677 | `accept-with-boundary` | Pod partner smoke claims real PyTorch+CuPy CUDA execution; this Claude review did not re-execute the pod logs. |
| 1678 | `accept-with-boundary` | Pod Embree build claim accepted as reported; pod logs not re-executed in this review. |
| 1679 | `accept` | Broad pod triage correctly explains that the 65 failures / 31 errors are historical pinning and OptiX-dependent tests, not a v1.8 release pass; conservatively reported. |
| 1680 | `accept` | Current-gap snapshot matches live scan counts (92 / 178 / 83 / families {db:30, polygon:29, knn:14, bfs:10}). |
| 1681 | `accept-with-boundary` | Self-review caveat applies; native scan confirms zero `pip` symbols and presence of the five replacement exports plus the HIPRT kernel filename hint. Pair with Gemini Goal1681 verdict for distinct-AI consensus. |
| 1682 | `accept-with-boundary` | Self-review caveat applies; native scan confirms zero `hausdorff` symbols and presence of the replacement Embree export. Pair with Gemini Goal1682 verdict for distinct-AI consensus. |
| Overall v1.8/v2.0 release readiness | `needs-more-evidence` | 83 real app-shaped symbols remain across `db`, `polygon`, `knn`, `bfs`; no pod execution evidence for the renamed exports; OptiX SDK headers / `librtdl_optix.so` still missing for pod build. |

## Release-Gate Position

Claude affirms the following remains **blocked**:

- the wording `RTDL native internals are fully app-agnostic.`;
- public release wording that implies the v1.8 Python+RTDL or v2.0
  Python+partner+RTDL surface is hardware-proven on the migrated exports
  without the corresponding pod runs;
- treating any Goal1671-1682 result as final v1.8/v2.0 release evidence
  before distinct-AI review has been recorded for that specific goal;
- treating Codex+Codex as 2-AI consensus;
- treating an authoring pass as independent review;
- treating any Claude review that participated in authoring Goal1681 or
  Goal1682 as a strict independent review for those two goals
  specifically.

Release readiness can advance when:

1. the `db`, `polygon`, `knn`, and `bfs` families are migrated or
   mechanically quarantined outside the release-surface scan;
2. a pod with OptiX SDK headers or a compatible `librtdl_optix.so`
   produces native rebuild + runtime smoke evidence on the renamed
   exports across each backend (Embree, HIPRT, OptiX, Oracle/CPU,
   Vulkan);
3. distinct-AI independent review artifacts exist for any goal used as
   release evidence — and, for Goal1681 and Goal1682 specifically, that
   pair includes a Claude review that did not participate in authoring.

## Final Conclusion

The architectural direction across Goals 1668-1682 is approved. Localized
source migrations and quarantines for Goal1673, Goal1674, Goal1681, and
Goal1682 are technically sound and conservatively worded. Counts in
Goal1680 match a live scan of `src/native`. The partner-track consensus
is recorded verbatim in the gate. No overclaim of release readiness was
observed.

Full v1.8 / v2.0 release readiness remains **`needs-more-evidence`**:
83 real app-shaped native symbols remain across `db`, `polygon`, `knn`,
and `bfs`, and pod/hardware execution evidence on the renamed exports
has not been produced.

This review, paired with
`docs/reviews/goal1684_gemini_review_goals1668_1682_2026-05-11.md`,
satisfies the distinct-AI consensus requirement for Goals 1668, 1669,
1670, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, and 1680. For
Goal1681 and Goal1682 specifically, see the Authoring-Scope Disclosure
above; a fully independent Claude review (one that did not participate
in authoring) is recommended before treating those two goals as having
strict Claude+Gemini consensus.
