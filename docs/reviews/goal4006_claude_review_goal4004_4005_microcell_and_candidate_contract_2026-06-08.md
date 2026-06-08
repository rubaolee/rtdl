# Goal4006 Claude Review: Goal4004-4005 Microcell Rejection And Candidate Contract

Date: 2026-06-08
Reviewer: Claude (read-only review)

## Verdict

`accept`

Goal4004 correctly rejects the corrected microcell route as a performance
route while preserving it as a correctness lesson, and Goal4005 correctly
exposes `partition_convergence_hybrid` as a fail-closed candidate strategy
with a complete claim-flag closure and a sufficient requirements list for the
eventual native implementation.

## 1. Does Goal4004 correctly reject the old corrected microcell route?

Yes. The report verdict is `reject-as-performance-route`, and the artifacts
back it up exactly:

| Profile | Grouped `elapsed_sec` | Microcell `elapsed_sec` | Ratio | Report claim |
| --- | ---: | ---: | ---: | --- |
| `clustered3d` | `0.11726472526788712` | `5.8857751339674` | `50.19x` | `50.19x slower` ✓ |
| `road3d` | `0.07013893872499466` | `1.6549725234508514` | `23.60x` | `23.60x slower` ✓ |
| `ngsim_dense` | `0.04672687128186226` | `1.3504003956913948` | `28.90x` | `28.90x slower` ✓ |

I recomputed each ratio directly from the JSON `elapsed_sec` fields and they
match the report table to the reported precision. The `signature` blocks
(`cluster_sizes`, `core_count`, `noise_count`) are byte-identical between the
`*_grouped.json` and `*_microcell.json` pairs for all three profiles, which
substantiates the "signature match: yes" column and the
`cell_graph_granularity: clique_safe_microcell` /
`cell_graph_fast_path_active: true` metadata the test asserts on
(`tests/goal4004_..._test.py:24-25`).

The report's framing is balanced rather than purely negative: it explicitly
preserves the route "as a correctness lesson" (the clique-safe-microcell fix
for the unsafe radius-cell assumption, §Interpretation) while stating plainly
that it "is not a performance route" and "should not be promoted as the next
RT-DBSCAN default." That is the right call — the evidence shows a 23x-50x
slowdown at the actual benchmark radii, which rules out promotion on
performance grounds even though correctness (signature parity) holds.

## 2. Does Goal4005 correctly expose `partition_convergence_hybrid` as fail-closed?

Yes. In `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`:

- `V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_STRATEGIES = ("grouped_stream",)`
  (line 27) — the only runtime-executable strategy remains `grouped_stream`.
- `V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CANDIDATE_STRATEGIES = ("partition_convergence_hybrid",)`
  (lines 28-30) is a separate list, and `_unsupported_reason` (lines 474-484)
  treats candidate strategies as "not unsupported" but distinct from supported
  ones, so the planner can route them to the candidate branch instead of
  raising immediately.
- `plan_v2_8_fixed_radius_graph_component_continuation` (lines 258-297) returns
  `status: "candidate_requires_native_implementation"`,
  `runtime_executable: False`, `native_abi_added: False`, and a fully-closed
  flag block (`fallback_selected` … `true_zero_copy_claim_authorized`, all
  `False`) for the candidate branch — matching
  `tests/goal4005_..._test.py:31-45`.
- `prepare_v2_8_fixed_radius_graph_component_continuation_3d` (lines 314-339)
  raises `ValueError(str(metadata.get("unsupported_reason", metadata["status"])))`
  whenever `metadata["status"] != "accepted_preview"`. For the candidate
  branch there is no `unsupported_reason` key, so the raised message is
  exactly `"candidate_requires_native_implementation"`, matching the
  `assertRaisesRegex` in `tests/goal4005_..._test.py:50-56`. This is a clean
  fail-closed path — the candidate strategy is visible in
  `describe_v2_8_fixed_radius_graph_component_front_door()` (so callers can
  discover it and its requirements) but cannot be prepared or executed.

The two rejected default strategies (`direct_side_effect_default`,
`microcell_graph`) are also recorded in
`V2_8_FIXED_RADIUS_GRAPH_COMPONENT_REJECTED_DEFAULT_STRATEGIES` (lines 31-34)
and surfaced both in `describe_...` and in the candidate plan payload — this
correctly encodes the Goal4002 (reject direct-side-effect default) and Goal4004
(reject microcell route) outcomes as durable contract state, not just narrative
in reports.

## 3. Are all claim flags and hidden-dispatch/auto-partner flags closed?

Yes, on both sides:

- **Goal4004 pod artifacts**: every `claim_boundary` block in all six JSON
  files (`{clustered3d,road3d,ngsim_dense}_{grouped,microcell}.json`) has
  `paper_dataset_reproduction: false`, `paper_speedup_claim_authorized: false`,
  and `native_dbscan_abi_added: false`. I spot-checked the full set via grep
  across all six files and the `ngsim_dense_microcell.json` excerpt confirms
  the same closure pattern propagates through nested metadata blocks
  (`paper_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`,
  `whole_app_speedup_claim_authorized`, `true_zero_copy_authorized`,
  `v2_0_release_authorized`, all `false`).
- **Goal4005 candidate plan**: `fallback_selected`, `hidden_dispatch_allowed`,
  `automatic_partner_selection_allowed`, `app_specific_engine_logic_allowed`,
  `release_authorized`, `public_speedup_claim_authorized`,
  `rt_core_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`,
  and `true_zero_copy_claim_authorized` are all hard-coded `False` in the
  candidate-branch dict literal (lines 280-288), and
  `describe_v2_8_fixed_radius_graph_component_front_door()` separately closes
  `automatic_partner_selection_allowed`, `hidden_dispatch_allowed`, and
  `app_specific_engine_logic_allowed` at the front-door description level
  (lines 215-217). The `V28FixedRadiusGraphComponentPlan.__post_init__`
  (lines 89-101) additionally enforces — at the dataclass level, for the
  *supported*-strategy path — that none of these flags can be set `True`,
  raising `ValueError` if they are. The closure is therefore defense-in-depth
  across both the candidate path and the executable path, not just an
  artifact-level convention.

Both reports' "Boundary" sections list the same closed set
(release/public-speedup/RT-core/whole-app/paper-reproduction/true-zero-copy/
automatic-partner/app-specific-engine-logic, plus hidden-dispatch for Goal4005),
and the corresponding test fragments (`tests/goal4004_..._test.py:54-56`,
`tests/goal4005_..._test.py:69-70`) assert those exact strings are present in
the reports and source. I confirmed the strings are present as required.

## 4. Are the candidate requirements sufficient before native implementation?

The seven requirements in `V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_REQUIREMENTS`
(lines 35-43) map directly onto the specific failure modes the evidence chain
identified, and I don't see a missing load-bearing item:

| Requirement | Traces back to |
| --- | --- |
| `device_resident_partition_aabb_and_count_columns` | Goal3999 (cell-AABB classification was CPU-only; needs to become a device-resident input) |
| `safe_full_partition_pair_summary_without_pair_materialization` | Goal3999 (`safe_full` pairs identified, but a real primitive must summarize them without materializing every pair — avoiding the candidate-stream blowup Goal4001 measured: 273M candidates for `clustered3d`) |
| `ambiguous_boundary_pair_rt_traversal` | Goal3999 (53-77% of near-pair work remains ambiguous and needs RT traversal, not a plain-grid shortcut) |
| `same_contract_parity_against_grouped_stream` | Goal4004 (the only credible bar for "is this route safe to consider promoting" is signature parity with the current baseline — exactly what sank `direct_side_effect_default` as a *default* in Goal4002 despite being "correct") |
| `deterministic_component_root_policy` | Goal4001 (same-root culling is mandatory; a hybrid must not destabilize root determinism) |
| `explicit_convergence_and_staleness_counters` | Goal3998/Goal3999 (the rejected stale-source-root-payload idea showed that convergence/staleness must be explicit, not implicit) |
| `actual_benchmark_radius_pod_evidence` | Goal3996/3998 vs Goal3999/4001 (the project already learned that `clustered3d`/`0.5` stress numbers do not generalize to the actual benchmark radii — any future claim must be measured at `0.055`/`0.030`/`0.012`, the same discipline Goal4004 itself used) |

This list reads as the minimum closing set rather than an arbitrary wish list:
each item corresponds to a concrete prior negative result (a route that was
rejected *because* this property was missing or unverified). I would not add
or remove anything based on the evidence reviewed.

## 5. What must the next native implementation goal guard against?

Based on the full evidence chain (Goal3999 → Goal4001 → Goal4002 → Goal4004 →
Goal4005), the next native-implementation goal should specifically guard
against:

1. **Re-litigating already-rejected shapes.** Don't resurrect a plain
   uniform-grid/"build cells, union cells" route (Goal3999 showed 41-77%
   ambiguous-pair residue), a stale source-root payload (Goal3998), or the
   old clique-safe microcell graph continuation (Goal4004, 23x-50x slower) —
   these are now recorded as `rejected_default_strategies` /
   correctness-only lessons, and any new design should cite *why* it differs.
2. **Claiming victory on stress-only radii.** Goal3999 explicitly separated
   the `clustered3d`/`0.5` stress row from the actual benchmark defaults
   (`0.055`/`0.030`/`0.012`); the `actual_benchmark_radius_pod_evidence`
   requirement exists precisely so a future report can't generalize from the
   stress profile the way Goal3996/3998 initially did.
3. **Turning off same-root culling or weakening root determinism** to gain
   speed — Goal4001 measured that disabling it is *slower* on all three
   profiles (1.06x-1.18x), so any hybrid must keep
   `deterministic_component_root_policy` intact.
4. **Treating "correct" as sufficient for promotion.** Goal4002 is the
   cautionary tale: `direct_side_effect_default` was *correct*
   (signature-matching) but mixed/marginal in end-to-end performance
   (-4.4% to +2.6%), and was rightly rejected as a default. The
   `same_contract_parity_against_grouped_stream` requirement must be paired
   with an actual performance bar against the grouped-stream baseline, not
   just signature equality — otherwise the project risks promoting another
   "correct but not actually faster" route.
5. **Materializing full pair lists for "safe" partition pairs.** The
   `safe_full_partition_pair_summary_without_pair_materialization` wording is
   important — Goal4001 showed the candidate-stream size itself
   (hundreds of millions of candidates) is the bottleneck; a hybrid that
   "summarizes" safe pairs by enumerating them would just relocate the same
   problem.
6. **Claim-boundary drift once a native ABI is actually added.** The current
   contract closes `native_abi_added`/`hidden_dispatch_allowed`/
   `automatic_partner_selection_allowed`/etc. for the *candidate* (unbuilt)
   state. Once a native implementation lands, a fresh goal will need to
   re-derive and re-close these flags for the *executable* state — they
   should not silently inherit `False` from the candidate contract without
   re-justification (the same discipline `V28FixedRadiusGraphComponentPlan.__post_init__`
   already enforces for `grouped_stream`).

## Test And Source Verification

- `tests/goal4004_microcell_route_refresh_after_grouped_union_telemetry_test.py`
  and `tests/goal4005_partition_convergence_candidate_front_door_contract_test.py`
  were read in full; their assertions were checked against the live JSON
  artifacts, the report text, and `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
  by direct inspection (line references above) rather than executed (sandbox
  could not invoke the project's Python interpreter for this read-only
  review). The assertions line up with what the source and artifacts actually
  contain — no contradiction found between test expectations and the
  underlying data/code.
- `git log --oneline -- src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
  shows `14a802f0 Goal4005 add partition convergence candidate contract` as
  the most recent change to the front door, consistent with the claimed scope
  (a planning/contract-only change, no native ABI).

## Boundary

This review is read-only analysis. It does not authorize release, public
speedup wording, broad RT-core speedup wording, whole-app acceleration
wording, paper-reproduction wording, true-zero-copy wording, automatic
partner/backend selection, hidden dispatch, or app-specific native-engine
logic.
