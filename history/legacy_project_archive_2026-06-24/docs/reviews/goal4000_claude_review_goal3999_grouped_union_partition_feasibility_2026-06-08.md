# Goal4000: Claude Review of Goal3999 Grouped-Union Partition Feasibility

Date: 2026-06-08
Reviewer: Claude (independent, read-only)
Subject commit: `45a63d9c` "Goal3999 probe grouped union partition feasibility"

## Findings by Severity

No correctness, accounting, or boundary defects were found. All checks below
passed.

### Info

1. **Radius separation is correct and matches the live benchmark config.**
   `docs/reports/goal3999_grouped_union_partition_feasibility.json` rows with
   `purpose=current_benchmark_default_radius` carry `clustered3d=0.055`,
   `road3d=0.030`, `ngsim_dense=0.012`. These match
   `DEFAULT_DATASET_CONFIG` in
   `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
   exactly (lines 22-25). The single `purpose=stress_radius_not_current_benchmark_default`
   row is `clustered3d` at `radius=0.5`, labeled `stress row, not default` in
   the report table, and the report explicitly warns it "must not be confused
   with the current benchmark default." The `0.5` figure also matches every
   `radius` value found in the cited Goal3996/Goal3998 context artifacts
   (`docs/reports/goal3996_grouped_union_extended_telemetry_sweep_pod.json`,
   `docs/reports/goal3998_grouped_union_source_root_payload_negative_probe_2026-06-08.md`),
   so the "stress lens" framing is faithful to its origin.

2. **Partition accounting is internally consistent and the upper-bound
   identity holds for every row.** I hand-checked the JSON arithmetic for all
   four `(profile, purpose)` rows and all `cell_factor_rows` within them:
   - `safe_full_pair_upper + safe_skip_pair_upper + ambiguous_pair_upper ==
     total_pair_upper` (e.g., clustered3d `radius_x_0.25`:
     `92,419,359 + 1,751,306,033 + 303,725,488 = 2,147,450,880`, which equals
     `total_pair_upper = C(65536,2)`).
   - `near_pair_upper == safe_full_pair_upper + ambiguous_pair_upper` holds in
     every row.
   - `decided_pair_upper == safe_full_pair_upper + safe_skip_pair_upper` and
     `0 <= decided_pair_ratio <= 1` in every row.
   These are exactly the invariants `tests/goal3999_grouped_union_partition_feasibility_test.py::test_partition_accounting_is_consistent`
   asserts, and the test passes against the committed artifact. The "all pairs
   upper bound" therefore is fully accounted for by the three-way partition —
   no leakage or double counting.

3. **The classification method (AABB min/max distance vs. `radius_sq`) is
   sound and the "far" cell-pair shortcut is provably safe.** `safe_full` uses
   `_aabb_max_distance_sq <= radius_sq` (every point pair in the two cells is
   within radius), `safe_skip` uses `_aabb_min_distance_sq > radius_sq`
   (every point pair is outside radius), and the remainder is `ambiguous`.
   Cell pairs outside the enumerated neighbor offset (`max_offset =
   ceil(radius/cell_size) + 1`) are folded into `safe_skip` via
   `far_safe_skip_*`; the minimum possible gap between cells at offset
   `> max_offset` is `(max_offset) * cell_size >= (ceil(radius/cell_size)+1) *
   cell_size > radius`, so this shortcut cannot misclassify a near pair as far.
   The script also raises `RuntimeError` if the derived far-skip count would be
   negative, which is a correct sanity guard, and it never fired (`status:
   "pass"`).

4. **The hybrid-primitive conclusion is supported by the probe's own numbers,
   not asserted beyond them.** At the *actual* benchmark radii with the best
   (`radius/4`) cell size, ambiguous-of-near-pair ratios are `76.67%`
   (clustered3d), `70.05%` (road3d), and `53.50%` (ngsim_dense) — all
   majority-ambiguous, meaning a "build cells, union cells" route would still
   need a large fine-grained fallback or would lose exactness at boundaries.
   At the same time, `safe_skip_pair_ratio` is large (`81.6%`, `94.3%`,
   `99.2%`), so partitioning *is* a strong candidate-pruning signal even
   though it cannot decide most of the near-boundary work outright. This is
   exactly the asymmetry that motivates "device-resident partitions for safe
   summaries + RT traversal for ambiguous boundary pairs," and the report
   states that conclusion as a *direction*, not a result — it explicitly
   labels itself "design evidence only," disclaims native ABI additions, new
   runtime measurements, and performance claims, and the JSON's
   `interpretation_boundary` block backs that up
   (`cpu_feasibility_probe_only: true`, `native_abi_added: false`,
   `performance_claim_authorized: false`, `release_authorized: false`).

5. **No forbidden overclaim language found.** The only occurrences of
   "release," "speedup," "RT-core," "zero-copy," "paper-reproduction,"
   "automatic," and "app-specific" in the report are inside the boundary
   paragraph that explicitly *disclaims* each of them (lines 113-116). The
   "Next Generic Primitive Direction" section keeps strictly to engine-neutral
   vocabulary (fixed-radius pairs, partitions, components, roots, union
   events, convergence/root metadata) and explicitly names DBSCAN,
   clusters, epsilon/min-points, and app labels as things that must stay out
   of native ABI names — matching the engine-boundary policy already recorded
   in `docs/research/future_version_to_do_list.md:134-137`.

6. **The `future_version_to_do_list.md` summary (lines 119-127) is a faithful,
   compressed restatement** of the report's numbers (`76.67%`, `70.05%`,
   `53.50%`, the three current radii, and the `0.5` stress-only framing) — no
   drift between the long-form report and the roadmap entry.

## Verdict

**`accept`**

## Required Before Next Step

None blocking. The probe is CPU-only, scoped, internally consistent, and its
conclusion (pursue a generic hybrid device-resident-partition + RT-traversal
primitive, not a plain grid rewrite) is the conclusion the data actually
supports. Two non-blocking notes for whoever picks up the next native-design
goal:

1. The probe uses a single fixed seed (`20260608`) and a single point count
   (`65,536`). The report does not claim generality beyond this fixture (it
   calls itself "a CPU feasibility probe over the generated fixture"), but the
   *next* native-implementation goal should re-derive the safe/ambiguous split
   on the actual prepared device partitions (not a CPU AABB approximation)
   before sizing the hybrid primitive's fallback path, since real cell
   occupancy and AABB tightness will differ from this synthetic fixture.
2. The "Next Generic Primitive Direction" list (report lines 96-109) is a
   reasonable design sketch but is still speculative about where the
   safe/ambiguous boundary should be drawn at runtime (static cell-size choice
   vs. adaptive). That choice should be evidence-driven in the implementation
   goal rather than carried over from this probe's `radius/4` "best" pick,
   which was selected purely to minimize ambiguity in this fixture and is not
   asserted as a universal default.
