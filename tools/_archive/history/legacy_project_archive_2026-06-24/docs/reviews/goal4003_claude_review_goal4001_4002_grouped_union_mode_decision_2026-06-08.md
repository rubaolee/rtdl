# Goal4003 Claude Review: Goal4001/Goal4002 Grouped-Union Mode Decision

Date: 2026-06-08
Reviewer: Claude (read-only review)

## Verdict

`accept`

Both reports' numeric claims are reproducible from their own artifacts, the
interpretive chain (same-root culling mandatory → direct side effects are a
small knob → the real cost is candidate/root-read work) is internally
consistent across Goal3989/3996/3999/4001/4002, and both claim boundaries are
closed. The recommended next direction (generic device-resident
partition/convergence hybrid) follows from the accumulated evidence rather than
being asserted fresh.

## 1. Goal4001 interpretation check

Verified directly against
`docs/reports/goal4001_actual_radius_exttelemetry_pod/*.json`:

- `clustered3d`: telemetry `[..., 273911978, 273831259, 0, 80719]` →
  `same_root_culled / radius_candidates = 99.97%`, reported `= 0.029%` of
  candidates. Default median native `0.099711s`; no-cull median
  `0.105354s` (ratio `1.057x`, matches report); direct-side-effect median
  `0.095312s` (ratio `0.956x`, matches report).
- `road3d` and `ngsim_dense` rows reproduce the same pattern
  (`1.118x` / `0.938x` and `1.178x` / `1.004x` respectively); all four ratios
  in the report table check out against `median_native_elapsed_sec`.
- The `same_root_off_direct_off` variant always has the highest median in all
  three profiles — same-root culling is strictly faster than disabling it at
  these radii, supporting "same-root culling is mandatory."
- The `same_root_on_direct_on` variant reports `reported_intersection_candidates
  = 0` and a nonzero `direct_side_effect_candidate_hits`, confirming the
  any-hit report path is fully bypassed when direct side effects are enabled —
  consistent with the claimed mechanism.

The inference that "the remaining bottleneck is candidate traversal/root-read
work rather than reported any-hit union" is sound: culling removes ~99.97% of
candidates yet the no-cull→cull speedup is only `1.06x`–`1.18x`, and bypassing
any-hit reporting entirely (direct side effect, `reported = 0`) buys at most
`~6%`. Both levers operate on the small tail (reporting/union), while the
dominant cost — traversing ~270M/85M/12M radius-qualified candidates and
reading their component roots to decide whether to cull — is untouched by
either knob. The report's three-point lesson (uniform partitions leave
ambiguous work; same-root culling pays traversal/root-read cost; direct side
effects trim any-hit overhead only) is a fair synthesis, not an overreach.

## 2. Goal4002 app-level rejection check

Verified against `docs/reports/goal4002_direct_side_effect_app_probe_pod/*.json`:

- `signature` blocks are byte-identical between `_default` and `_direct` for
  all three profiles (`cluster_sizes`, `core_count`, `noise_count`), and
  `metadata.grouped_union_direct_side_effect_enabled` flips correctly
  (`false`/`true`) — the correctness claim ("Signature match: yes") holds.
- End-to-end ratios reproduce: `clustered3d 0.117675/0.120874 = 0.974x`,
  `road3d 0.069539/0.069482 = 1.001x`, `ngsim_dense 0.047535/0.045522 = 1.044x`.
  These match the report table and the test's directional assertions
  (`< 1.0`, `> 0.99`, `> 1.0`).
- The reconciliation with Goal4001 is correct: the raw native ratios
  (`0.956x/0.938x/1.004x`) are smaller in magnitude and more uniformly
  favorable than the app-level ratios (`0.974x/1.001x/1.044x`), because the app
  path adds prepared-adapter and column-signature work that dilutes the native
  delta and, for `ngsim_dense`, flips the sign. A `+2.6%` best case and
  `-4.4%` worst case is correctly characterized as "too small and too mixed to
  justify changing the default."

Rejecting promotion to default while keeping the option for explicit
experimentation is the right call given this evidence — there is no profile
where the win is large enough to risk a default-route change, and one profile
where it actively regresses.

## 3. Claim-boundary cleanliness

Both reports carry explicit "Boundary" sections with the standard non-claim
list (no release, no public/RT-core/whole-app speedup wording, no
true-zero-copy, no automatic partner selection, no app-specific native-engine
logic), and both are backed by `claim_boundary`/`metadata` fields in the JSON
artifacts that the corresponding tests assert are `false`
(`performance_claim_authorized`, `release_authorized`,
`public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`,
`true_zero_copy_claim_authorized`, `app_specific_engine_logic_allowed`,
`automatic_hidden_dispatcher`, `automatic_partner_selection_allowed`). No
wording in either report exceeds what the artifacts support — both are framed
as diagnostic telemetry / app probes, not performance or release claims.

## 4. Is the recommended next direction reasonable?

Yes. The "generic device-resident partition/convergence hybrid" is not a fresh
guess — it is the convergent recommendation of the whole Goal3987→4002 chain:

- Goal3989 already showed atomics are not the bottleneck; candidate
  traversal/root-reads are.
- Goal3998 showed a stale-source-root shortcut breaks correctness
  (candidates jumped `1.84M → 543.65M`, default path slowed `1.079x`) — ruling
  out cheap root-cache snapshots as *the* answer.
- Goal3999's CPU partition-feasibility probe found uniform grids leave
  `~70–77%` of near-pairs ambiguous at radius/4 cell size — ruling out a plain
  grid rewrite but showing partial partition signal exists.
- Goal4001/4002 close the loop by showing neither same-root toggling nor
  direct side effects touch the dominant traversal/root-read cost.

A hybrid that uses safe partition summaries to skip definitely-within-radius
pairs, keeps RT traversal only for the ambiguous boundary, and preserves exact
component-root convergence is the only direction left standing that addresses
the actual measured bottleneck rather than another small mode knob. This is a
reasonable, evidence-driven recommendation — though it is still a design
direction, not a validated solution, and the reports correctly stop short of
claiming it will work.

## 5. Design risks the next native-implementation goal should guard

1. **Same-root culling must remain on by default and stay exact.** Goal4001
   reconfirms it is mandatory for performance; any partition/hybrid design must
   not implicitly disable or weaken it, and must not reintroduce a
   stale-root-snapshot shortcut (Goal3998's correctness failure mode —
   candidate counts exploded and the path got slower).
2. **Partition summaries must be provably safe (no false negatives).**
   Goal3999 found ~70–77% of near-pairs remain ambiguous at radius/4 grid
   resolution — the "definitely-within-radius" classification must never
   misclassify a true neighbor pair as safe-skip, or the union-find result
   silently corrupts. The boundary/ambiguous set must be conservative by
   construction and exhaustively covered by RT traversal.
3. **Exact convergence/component-root semantics under concurrency.** The
   eventual primitive still needs correct atomic-union convergence under
   concurrent root updates — the same hazard that sank the Goal3998 snapshot
   approach. A partition layer that defers some unions must not create new
   staleness windows for root reads.
4. **Keep the native ABI generic.** The `future_version_to_do_list.md` "Engine
   boundary" note is explicit: the primitive may speak of pairs, groups,
   component roots, unions, partitions, and convergence counters, but must not
   encode DBSCAN/epsilon/min-points or other app-specific vocabulary in native
   names — a real risk once "partition" and "convergence" concepts get added
   to the OptiX path.
5. **Direct side effects, if folded into the hybrid, need an explicit
   ordering/visibility contract.** It bypasses any-hit reporting
   (`reported_intersection_candidates = 0`, work moves to
   `direct_side_effect_candidate_hits`); any combination with partition-skipped
   work must define how/when those side effects become visible relative to
   the union-find convergence the partition layer also touches.
6. **Benchmark at actual app radii, not stress radii.** Goal3999 already
   flagged that the `0.5` stress radius used in Goal3996 is not representative
   of the real benchmark radii (`0.055/0.030/0.012`); any new primitive's
   acceptance evidence should continue to use the actual-radius profiles Goal4001
   established, to avoid re-deriving a radius-mismatched conclusion.

## Required before next step

None — this is diagnostic groundwork, and both reports already say so. The
items above are guardrails for whoever implements the partition/convergence
hybrid primitive next, not blockers on accepting Goal4001/Goal4002 as written.
