# Goal4302: Whole-Project Critical Review and Improvement Suggestions

**Reviewer:** Claude (Fable 5, independent read-mostly external review)
**Date:** 2026-06-11
**Scope:** Current `main` state after v2.10/v2.11 cleanup, Embree CPU + current partner reference work (HEAD `bf12a82b`, `VERSION` = v2.10)
**Requested by:** `docs/handoff/HANDOFF_CLAUDE_GOAL4302_WHOLE_PROJECT_CRITICAL_REVIEW_2026-06-11.md`

---

## Executive Verdict: `accept-with-boundary`

The Python + RTDL + partner architecture is coherent, the app-agnostic engine
rule is genuinely enforced, claim discipline is exemplary, and the ten-app
benchmark matrix is real executable evidence rather than slideware. That earns
acceptance of the current direction as an internal development surface.

The boundary is fourfold. First, the project's central marketing premise —
"write high-performance hardware-RT programs much more easily" — is only
half-true today: users get easy access to a catalog of pre-built generic
primitives, not an easy way to express *new* RT programs; the kernel DSL and
the performance path are two different languages. Second, RT-core value is
demonstrated convincingly in roughly half of the ten benchmark apps; the rest
currently pressure-test partner continuation or run at scales where timing
signals are sub-millisecond. Third, process/evidence weight (≈56% of tracked
files are reports) has grown past the point where it accelerates the project.
Fourth, there is an operational security lapse (private SSH key in the repo
root, pod address + key name in a tracked report) that must be fixed before
any wider sharing of this tree.

Nothing here authorizes a release, a tag, or any public performance wording.

---

## Findings (ordered by severity)

### F1 — HIGH (operational security): private SSH key in repo root; live pod connection details in tracked docs

- A private-key-shaped file was observed at the repository root and began
  with an OpenSSH private key header. It was untracked but also **unignored**
  (`.gitignore` has no rule for it), so one careless `git add -A` commits it.
  Root-level archives (`rtdl_v0_4.tar.gz`, 19 MB) and any future tree tarballs
  risk carrying it.
- `docs/reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md:22-23`
  is git-tracked and records a live pod SSH command plus a local key filename.
  Reports also publish the local Linux host address
  (`docs/reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md`).

Even if these pods are ephemeral rentals, the pattern is wrong: evidence
reports should record hardware class and driver, not connection strings and
key file names. Action: rotate the key, move it out of tree, add ignore +
secret-scan rules, and adopt a report-redaction convention. This is the only
finding I would treat as blocking for any external distribution of the tree.

### F2 — HIGH (strategic): the advertised language and the performance path are two different things

The front page (`README.md`, "What You Write") teaches
`input -> traverse -> refine -> emit` via `@rt.kernel`. That surface is small
and clean (`src/rtdsl/api.py`, 279 lines; `kernel` at line 54). But:

- Only 4 of the 10 promoted research benchmark apps express any part of their
  hot path through `rt.kernel`/`traverse`/`refine`/`emit` (grep over
  `examples/current/research_benchmarks/`). The Hausdorff app keeps a
  ceremonial k=1 kernel at lines 24–26 but its serious route is
  `rt.prepare_generic_fixed_radius_count_threshold_2d(...)`
  (`rtdl_hausdorff_distance_app.py:241`) — a named, fixed-contract prepared
  primitive, not a lowered kernel.
- The real performance surface is the primitive/adapter catalog:
  `src/rtdsl/partner_adapters.py` is **10,424 lines with 246 functions**, plus
  `numba_partner_continuation.py` (1,847 lines). Each contract × partner pair
  (Torch/Triton/CuPy/Numba) is hand-written.

Consequence for the top strategic priority ("easy RT programming"): a user
whose problem matches a cataloged contract has a great experience — far easier
than OptiX/CUDA. A user whose problem does *not* match must either (a) wait
for the engine team to ship a new generic primitive, or (b) fall back to
partner code, which is exactly the C++/CUDA-adjacent work RTDL promises to
remove. The kernel DSL does not bridge this gap because its lowering only
reaches the small set of teaching predicates.

This is not fatal — "curated generic RT primitive catalog with first-class
partner interop" is a legitimate and defensible product. But the project must
decide whether the DSL becomes real (kernels lower to the same prepared
high-performance routes) or whether docs stop implying that the kernel
language is how performance work gets expressed. Right now learner docs teach
one thing and benchmark apps do another, and that gap will be the first thing
a sophisticated external user notices.

### F3 — HIGH (engineering): `partner_adapters.py` monolith and N×M hand-written contract growth

`src/rtdsl/partner_adapters.py` (10,424 lines) contains, in one module:
generic grouped reductions, AABB pair summaries, columnar predicate
reduction with embedded CUDA C source strings (`_cupy_columnar_predicate_reduce_batch_fused`,
line 1540), Hausdorff-specific partner columns (`directed_hausdorff_2d_partner_columns`,
line 3651), radius-graph component solvers in three variants
(CuPy grid / Numba grid / chunked adjacency, lines 4388–6362), and prepared
session classes. Every new contract currently costs one hand-written
implementation per partner, with copy-pasted validation, metadata, and
claim-flag blocks (claim-boundary metadata appears in 71 of the 150
`src/rtdsl` modules, and the nine-flag `*_claim_authorized` boolean block is
copy-pasted across the registry dataclasses, e.g.
`current_benchmark_front_doors.py` and
`current_embree_cpu_partner_reference.py`).

This is the single biggest velocity constraint on the "generic primitives"
strategy. Without a shared partner-column runtime layer (dtype/device
validation, group-id contracts, launch shape, metadata emission) and some
templating for the segmented-reduction family, the catalog cannot grow at the
rate the ten benchmark apps generate demand. The implicit 0-based
`group_ids` contract flagged in Goal4300 is a symptom: cross-function
contracts live in convention, not in a type.

### F4 — MEDIUM-HIGH (project health): process artifact weight is now a tax on the product

- 11,616 of 20,858 git-tracked files (≈56%) live under `docs/reports/`.
- 2,579 test files, a large share being one-goal registry/metadata/claim-flag
  tests (`tests/goal42*`, `goal43*`) that assert dataclass fields and command
  strings rather than runtime behavior.
- 12 goal-numbered historical modules still live inside the product package
  (`src/rtdsl/goal112_segment_polygon_perf.py` … `goal23_reproduction.py`),
  violating the project's own "history lives in history/" rule at the source
  level.
- Root-level debris: `before_3958.txt` (1 MB), `rtdl_v0_4.tar.gz` (19 MB),
  `Lib/` (28 MB site-packages), `scratch/` (4 GB, ignored), a `Makefile`
  alongside `run_review_tests.py`.

The claim-discipline machinery is genuinely good — fail-closed runners,
forbidden-flag scans, per-row boundaries — but its marginal unit has shifted
from protection to friction. Each small goal now ships a registry dataclass +
validator + runner + test + report + review, mostly boilerplate. The risk is
twofold: contributor velocity, and learner trust (a newcomer cannot tell
living surface from archaeology without the curated indexes).

### F5 — MEDIUM: RT-core value is demonstrated in ~5 of 10 benchmark apps; the rest are partner or coverage evidence

Reading `docs/learn/benchmark_evidence_index.md` ("Current Ten-App Rows") and
`docs/reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md`
("Packet Result"):

- **Strong RT evidence:** spatial_rayjoin LSI/overlay route signals (`262.5x`,
  `212.2x`), robot_collision prepared traversal (median 40.9 µs over 49,900
  runs), rtnn prepared ranked summary, raydb prepared grouped count,
  librts AABB index. These genuinely exercise prepared RT traversal at
  defensible repeat counts.
- **Mixed/weak:** spatial_rayjoin one-shot PIP is **0.249x** (slower than the
  comparison route) and only repeated-batch PIP reaches 1.307x; Barnes-Hut's
  promoted front-door row is `barnes_hut_numba_exact_force` — a Numba force
  kernel reference, i.e. partner evidence, with RT relegated to a
  node-coverage pressure mode; triangle_counting carries the accepted
  segmented/streamed-lowering limitation; hausdorff's threshold query is
  7.7 ms at `--copies 8` scale; contact_manifold and rtnn key signals are
  0.29 ms / 0.21 ms medians, where launch overhead and timer noise dominate.

The ten apps are doing their *language pressure-test* job well (they forced
the prepared-state, bounded-collect, grouped-reduction, and boundary-policy
primitives into existence). But as *NVIDIA RT-core evidence* the portfolio is
currently 5 strong / 3 mixed / 2 weak, and internal docs should say so in one
place instead of letting the "ten benchmark apps" framing imply ten RT wins.

### F6 — MEDIUM: scale adequacy is uneven; the goal4266 1-second floor is not applied to the main packet

`docs/reports/goal4266_large_scale_cupy_numba_partner_comparison_2026-06-09.md`
established exactly the right rule: calibrate repeats until aggregate hot time
exceeds a 1.25 s floor, flag `subsecond_hot_total_rows`, refuse decision-grade
reads below the floor. The main ten-app scale-profile packet does not follow
it — several rows report sub-millisecond medians (see F5) and front-door
commands run at smoke scale by design (`--copies 8`, `--box-count 1024`,
`--dataset tiny` in `src/rtdsl/current_embree_cpu_partner_reference.py` and
`current_benchmark_front_doors.py`). Front doors as smoke tests are fine; the
problem is that the scale-profile packet — the thing internal planning reads —
mixes floor-respecting rows with sub-floor rows without a per-row flag.

### F7 — MEDIUM: v2.11 Embree CPU lane is coherent but has two wobbles

The packet itself (`src/rtdsl/current_embree_cpu_partner_reference.py`,
`scripts/rtdl_v2_11_embree_cpu_partner_reference_runner.py`) is well built:
import-time and runtime validators agree, the runner fails closed on
forbidden flags and unparseable stdout, and the local Linux artifact is clean
(10/10). Two issues:

- `librts_spatial_index_embree_cpu_aabb_index` runs ≈132 s wall / 43.9 s
  median query inside a *compatibility* packet whose other rows are seconds.
  A fallback-coverage packet should be scale-balanced; this row burns pod/CI
  time without adding coverage information.
- The RTNN "no Embree front door" exception is honestly labeled
  (`route_class: numba_cpu_partner_reference_no_embree_front_door`) but is
  structural debt: the validator at
  `current_embree_cpu_partner_reference.py:431-437` hard-codes RTNN as the
  permitted exception. A small Embree fixed-radius ranked-summary mode in the
  RTNN app would remove the special case entirely.

Strategically, Embree CPU does **not** currently risk distracting from NVIDIA
RT-core leadership — it is correctly framed as compatibility/fallback
evidence and explicitly not Intel-GPU or performance wording. The risk to
watch is timeout/scale creep turning it into a parallel performance lane.

### F8 — MEDIUM: learner on-ramp friction is the top "easy RT programming" UX gap

- Everything requires `PYTHONPATH=src:.` and every example carries a
  six-line `ROOT = next(parent ...)` sys.path bootstrap header
  (e.g. `examples/current/getting_started/rtdl_hello_world.py:7-9`). This is
  the very first thing a new user touches, and it reads as scaffolding.
  An *internal* editable install (`pip install -e .`) would remove all of it
  without making any package-install promise — the claim boundary blocks
  wording, not engineering.
- Boundary prose is repeated so densely that it competes with teaching
  content. `README.md` states claim disclaimers four separate times before
  the user reaches "Start Fast"; tutorials and example READMEs repeat the
  same paragraphs. One canonical boundary page plus one-line links would
  protect the same claims at a fraction of the reading cost.
- The good parts deserve note: `rtdl_hello_world.py` is a genuinely good
  first program; the tutorial ladder (8 steps) is correctly ordered; the
  primitive discovery workflow (`find_primitive`, faceted +
  deterministic-semantic search in `src/rtdsl/primitive_discovery.py`) is a
  real differentiator versus raw OptiX — no equivalent exists in the
  CUDA/OptiX world.

### F9 — LOW-MEDIUM: app-agnostic boundary holds at the native layer; wording leakage is minor

I found no app-named native ABI surfaces; the hierarchy
(`src/rtdsl/primitive_hierarchy.py`) keeps app semantics in
`APP_OWNED_BOUNDARY_EXCLUSIONS` (lines 91–101), and benchmark apps own their
interpretation. Remaining leakage is mild and Python-side: goal-numbered
modules in `src/rtdsl/` (F4), app-flavored adapter names like
`directed_hausdorff_2d_partner_columns` in the generic adapters module
(defensible as a generic metric contract, but it sits one rename away from
app branding), and engine-package modules like `db_postgresql.py` /
`graph_postgresql.py` that are baseline/oracle tooling living in the product
namespace rather than a `baselines/` sub-package.

### F10 — LOW: version and naming confusion at the edges

`VERSION` = v2.10, the active lane is v2.11, the working folder is named
`rtdl_v0_4_release_prep_review`, and front-door registry versions still carry
`goal3823`/`v2_8` lineage strings (`V2_8_PROMOTED_BENCHMARK_APPS` imported
by v2.11 modules). Internally consistent once understood, but each new
reviewer pays a decoding cost. A short `docs/versioning.md` (what v2_8
constants mean in v2.11 code, why the folder name is historical) would be
cheap. The Goal4300 minor observations (RTNN host-rank debt, implicit
group-id contract) remain open and are tracked correctly.

---

## Strategic Diagnosis

The project has successfully built the *hard discipline* layer: an
app-agnostic native engine, fail-closed claim boundaries, reproducible
evidence packets, and a benchmark portfolio that genuinely pressure-tested the
runtime into growing real primitives (prepared state, bounded collect-k,
grouped reductions, boundary policies). Most projects never achieve this; it
is the right foundation for credible public performance claims later.

What it has not yet built is the *product promise*: the distance between
"RTDL makes RT programming easy" and what exists is the distance between a
compiler and a catalog. Today RTDL is, honestly described, a *curated generic
RT primitive catalog with disciplined backend dispatch and first-class partner
interop*, fronted by a small teaching DSL that does not reach the performance
surface. Meanwhile, effort allocation has inverted: the process machinery
(registries, per-goal tests, reports — 56% of the tracked tree) now consumes
more marginal effort than the runtime capability it protects, and the
hand-written N×M partner adapter pattern caps how fast the catalog can grow.

The strategic fork is explicit: either (A) invest in making the kernel DSL
lower to the prepared high-performance routes — making the language claim
true — or (B) embrace the catalog identity, rewrite the front-door story
around primitive discovery + composition, and spend the freed effort on
catalog breadth and partner-runtime infrastructure. Both are viable; the
current docs uncomfortably promise (A) while the engineering delivers (B).
The NVIDIA RT-core story is real but concentrated: prepared, repeated-query,
traversal-dominated workloads win; one-shot and continuation-dominated
workloads do not, and the project's own evidence says so — that honesty
should be promoted from buried report lines to a first-class internal matrix.

---

## Prioritized Improvement Plan

Ordered by leverage. "Consensus" follows project convention: hygiene = none,
runtime/contract changes = 2-AI, promoted-benchmark status or public-wording
changes = 3-AI.

Lane classification: **current release-hardening** = P1, P5, P6, P8, P9, P10
(make the existing v2.10/v2.11 surface safe, honest, and navigable);
**near-term engineering** = P2, P3, P7, P12; **long-term / research-direction**
= P4, P11 (these decide the v3.x story and must not block v2.x hardening).

### P1. Secret and connection-detail scrub (release-hardening)
- **Build:** Rotate the local working key material; remove it from the tree; add
  `.gitignore` rules for keys/archives; add a tracked-tree secret-scan test
  (private-key headers, live root SSH command strings, raw IPs) over `docs/`, `scripts/`,
  root; redact pod addresses/key names from tracked reports in favor of
  hardware-class metadata.
- **Why:** F1; one `git add -A` away from credential leakage; blocks any
  external sharing of the tree.
- **Acceptance:** scan test passes on full tracked tree; key absent; rotated
  key confirmed working on pods; goal4215-style reports record GPU/driver
  only.
- **Hardware:** none. **Consensus:** none (hygiene), report to Main AI.

### P2. Shared partner-column runtime layer (refactor, no behavior change)
- **Build:** Extract from `partner_adapters.py` a single typed layer for
  partner module resolution, device-column validation (dtype, device,
  contiguity), explicit `GroupIdContract` (0-based positional vs caller IDs —
  closes the Goal4300 implicit-contract note), launch-shape helpers, and one
  shared `ClaimBoundaryFlags` dataclass replacing the 9-flag copy-paste
  blocks. Split `partner_adapters.py` into per-family modules
  (`adapters/grouped_reductions.py`, `adapters/radius_graph.py`, …) with a
  compatibility re-export.
- **Why:** F3; this is the bottleneck on catalog growth, the top
  highest-leverage runtime improvement available without new hardware
  evidence.
- **Acceptance:** all existing tests pass unchanged; no module >2,000 lines;
  new contract addition requires implementing only the kernel body per
  partner; group-id contract is an explicit type checked at runtime.
- **Hardware:** local Linux (CUDA pod for a confirmation run of the Numba/CuPy
  suites). **Consensus:** 2-AI.

### P3. Generic Numba `grouped_topk_f64` device kernel
- **Build:** The device-side grouped top-k named as v2.11 debt in Goal4299,
  retiring `reference_host_rank_after_device_score_rows`; same
  distance-then-candidate-id tie-break; wire into
  `top_k_nearest_points_2d_partner_columns(partner="numba")`.
- **Why:** Declared debt; makes the Numba lane credible as more than a
  reference; first consumer of the P2 layer.
- **Acceptance:** parity vs CPU oracle and vs CuPy path including ties;
  `host_rank_materialization_used: False`; goal4266-style ≥1.25 s aggregate
  same-repeat comparison row vs CuPy.
- **Hardware:** CUDA pod (Numba). **Consensus:** 2-AI.

### P4. Kernel-DSL bridge pilot: lower two benchmark hot paths through `@rt.kernel`
- **Build:** Make the kernel DSL lower to the *same* prepared native routes
  the benchmarks use, for exactly two contracts where the gap is most
  visible: fixed-radius count/threshold (Hausdorff route) and prepared
  fixed-radius neighbor rows (RT-DBSCAN route). The benchmark apps gain a
  `--front-door kernel_dsl` mode proving the lowered plan hits the identical
  prepared path.
- **Why:** F2; this is the decisive experiment for the strategic fork — if
  two contracts can be bridged cleanly, the language claim is salvageable;
  if not, docs should be re-centered on the catalog identity (see Questions).
- **Acceptance:** same-contract result parity; lowered-route timing within
  10% of the direct prepared-primitive route on the same pod packet; no new
  native symbols.
- **Hardware:** NVIDIA pod for OptiX confirmation; local Linux for
  Embree/CPU. **Consensus:** 3-AI (design-level surface decision).

### P5. Apply the 1-second aggregate floor to the ten-app scale-profile packet
- **Build:** Port goal4266 repeat-calibration into
  `scripts/goal3828_current_benchmark_scale_profile_runner.py`; every row
  either exceeds the floor on its key timing signal or is explicitly tagged
  `smoke_scale_only`; rerun the pod packet.
- **Why:** F5/F6; sub-millisecond medians are currently readable as evidence
  by accident.
- **Acceptance:** refreshed packet with zero untagged sub-floor rows;
  evidence index regenerated.
- **Hardware:** NVIDIA pod. **Consensus:** 2-AI.

### P6. Internal RT-core honesty matrix for the ten apps
- **Build:** One internal doc + machine-readable registry classifying each
  promoted app: where RT traversal wins (prepared/repeated), where partner
  continuation dominates, where evidence is mixed (e.g. one-shot PIP 0.249x
  vs LSI 262.5x), and what same-contract baseline each claim rests on.
  Reposition `barnes_hut_numba_exact_force` explicitly as partner evidence
  or pair it with an RT-led promoted row.
- **Why:** F5; the strongest defense against future overclaim is the project
  saying first, precisely, where RT does not win.
- **Acceptance:** all ten apps classified with artifact links; evidence index
  links the matrix; claim-scan tests extended to block citing partner-led
  rows as RT evidence.
- **Hardware:** none new (reads existing artifacts); pod only if rows must be
  refreshed. **Consensus:** 3-AI (touches promoted-benchmark interpretation).

### P7. Learner on-ramp: internal editable install + bootstrap removal
- **Build:** Minimal `pyproject.toml` enabling `pip install -e .` for
  source-tree development; delete per-example sys.path headers; update
  doctor to verify either mode; keep all package-install claim scans (the
  boundary blocks *public install promises*, not engineering).
- **Why:** F8; first-contact friction is the cheapest "easy RT programming"
  win available.
- **Acceptance:** examples and tests run without `PYTHONPATH` after
  documented setup; claim-boundary scans still pass; docs updated in one
  pass.
- **Hardware:** none. **Consensus:** 2-AI (because wording near the
  package-install boundary must stay scoped).

### P8. RTNN Embree front door
- **Build:** Embree fixed-radius ranked-summary mode in
  `rtdl_rtnn_benchmark_app.py`, mirroring the prepared OptiX contract;
  switch the v2.11 packet RTNN row to `embree_cpu_rt_primitive` and delete
  the hard-coded exception at
  `current_embree_cpu_partner_reference.py:431-437`.
- **Why:** F7; converts a permanent labeled exception into uniform 10/10
  Embree coverage and removes special-case validator logic.
- **Acceptance:** packet validator has no app-specific branches; local Linux
  rerun 10/10; RTNN Embree row parity vs CPU oracle.
- **Hardware:** local Linux. **Consensus:** 2-AI.

### P9. Evidence archive split and report curation
- **Build:** Move pre-v2.10 reports (the bulk of 11,616 files) into
  `history/` or a dedicated archive branch/repo with a tombstone index; keep
  a curated current-evidence set; relocate the 12 `goal*`-numbered modules
  out of `src/rtdsl/` (compat shims if imported); remove root debris
  (`before_3958.txt`, `rtdl_v0_4.tar.gz`, `Lib/`) from the working tree.
- **Why:** F4; restores signal-to-noise for contributors, reviewers, and
  clones.
- **Acceptance:** all current-doc links resolve (link-check test);
  `src/rtdsl/` contains no goal-numbered modules; tracked-file count for
  current docs reduced by an agreed target; full test suite passes.
- **Hardware:** none. **Consensus:** 2-AI (history-preservation rules).

### P10. Boundary-prose deduplication
- **Build:** One canonical claim-boundary page; replace repeated paragraphs
  in `README.md`, tutorials, and example READMEs with one-line links; add a
  scan test that flags duplicated boundary paragraphs (the inverse of the
  current scans: protect claims *and* readability).
- **Why:** F8; the same protection at a fraction of the reading cost; the
  current density actively hurts the "easy" goal.
- **Acceptance:** each learner page carries at most one boundary block;
  existing claim-scan tests still pass.
- **Hardware:** none. **Consensus:** none (wording mechanics), 2-AI sign-off
  on the canonical page text.

### P11. One declared whole-app, mid-scale measurement on the strongest app
- **Build:** For spatial_rayjoin (overlay/LSI route) — the portfolio's
  strongest RT evidence — produce one explicitly-declared *whole-app
  boundary* measurement (data load → RTDL → continuation → output) at
  public-CDB representative scale, against the same-contract CPU/CUDA
  baseline, with the goal4266 floor discipline.
- **Why:** Every current artifact times routes or phases; the first
  carefully-scoped *whole-app* row is what future narrow public wording will
  need, and doing it on the strongest app first sets the template.
- **Acceptance:** artifact declares the whole-app boundary per
  `docs/performance_model.md` table; floor respected; 3-AI review of any
  wording derived from it; no public claim emitted from this goal itself.
- **Hardware:** NVIDIA pod. **Consensus:** 3-AI.

### P12. Process-weight calibration for low-risk goals
- **Build:** A documented two-tier goal protocol: hygiene/doc/refactor goals
  ship with test + changelog line only (no registry dataclass, no dedicated
  report, no consensus); runtime/contract/evidence goals keep the full
  packet ceremony. Define the tier rules in `docs/audit/`.
- **Why:** F4; the boilerplate cost per goal is now the main drag on
  iteration speed, and uniform ceremony causes ceremony inflation rather
  than safety.
- **Acceptance:** tier rules documented; next five hygiene goals demonstrate
  the light path; claim-scan coverage unchanged.
- **Hardware:** none. **Consensus:** 3-AI once (on the protocol itself), then
  none per light-tier goal.

---

## Do Not Do Yet

- **Public packaging / PyPI** — P7's editable install is internal ergonomics
  only; the no-package-install boundary stays until a real release decision.
- **AMD HIPRT performance work** — the Goal3784 functional pod validation
  artifact still does not exist; collecting AMD *performance* evidence before
  AMD *functional* evidence inverts the ladder.
- **Automatic partner selection** — measured-selection helpers exist
  (`measured_grouped_vector_sum_2d_partner_selection`), but promoting
  auto-selection contradicts the user-chosen-partner rule and would multiply
  the claim surface. Keep selection explicit.
- **Embedding-based semantic primitive search** — the deterministic preview
  (`find_primitive_semantic`) is sufficient; an ML search adds a dependency
  and nondeterminism for marginal gain at the current ~60-node catalog size.
- **An eleventh benchmark app** — the ten are adequate pressure; new apps add
  evidence burden without new language lessons until P4/P6 conclude.
- **v3.0 residency-first re-architecture** — premature before P2 (adapter
  layer) and P4 (DSL bridge) settle what the runtime surface actually is.
- **Multi-GPU / distributed execution** — no benchmark app currently
  motivates it; pure scope creep at this stage.
- **More Embree CPU performance tuning** — v2.11 is a compatibility lane;
  tuning it competes with the NVIDIA priority for no strategic gain.

---

## Safe Public Wording

Nothing in this review authorizes new public claims. Within existing policy,
the following remain safe because they are scoped and evidence-backed:

- "RTDL is a Python-hosted DSL/runtime for non-graphical ray-tracing-style
  workloads, used from the source tree, with CPU reference, Embree CPU, and
  OptiX backends for documented primitives."
- "RTDL keeps its native engine app-agnostic: application semantics live in
  Python; native symbols expose generic traversal, row, and reduction
  contracts."
- "Ten benchmark applications run executable same-command front doors across
  documented backends, with reproducible artifacts." (Coverage claim, not a
  performance claim.)
- "Selected long, RT-heavy, prepared workloads have shown large OptiX
  speedups over Embree on the same app-level command surface, per specific
  reviewed artifacts." (Only with the exact artifact reference, per
  `README.md` Performance Boundary.)
- "RTDL can interoperate with CuPy- or Numba-owned device arrays for
  documented primitive contracts; continuation code remains user-owned."

Blocked claims (unchanged, and this review re-blocks them):

- Any package-install or `pip install rtdl` wording.
- Any broad/general speedup, "makes your app faster", or whole-application
  acceleration wording — including for the ten benchmark apps as a set
  (F5: the set contains partner-led and sub-floor rows).
- Broad NVIDIA RT-core wording; any AMD or Intel GPU performance wording
  (HIPRT functional evidence absent; Embree is CPU-only evidence).
- True zero-copy / general device-residency wording.
- Paper-reproduction wording for RTNN, RayJoin, X-HD, LibRTS, RT-DBSCAN, or
  the SIGMETRICS triangle-counting target.
- Automatic partner selection or "RTDL accelerates CuPy/Numba programs".
- Any "easier than CUDA/OptiX for arbitrary RT programs" wording until the
  F2 gap is resolved — current evidence supports "easier for cataloged
  primitive contracts" only.

---

## Questions For Main AI

1. **Identity decision (F2/P4):** If the kernel-DSL bridge pilot succeeds for
   two contracts, is the intent that *all* promoted benchmark hot paths
   eventually route through lowered kernels? If the pilot fails or stalls,
   are you willing to re-center public docs on the primitive-catalog identity
   and demote the kernel DSL to a teaching/prototyping surface?
2. **Target user:** Who is the v2.x user persona — a researcher reproducing
   RT-accelerated-algorithm papers, or an application engineer who wants
   spatial queries without CUDA? P6/P7/P10 prioritization differs sharply
   between the two.
3. **Security posture (F1):** May I confirm the local working key material
   has been rotated, and should historical tracked reports containing pod
   addresses be redacted in place or superseded by a redaction note? Does any
   distributed artifact (e.g. `rtdl_v0_4.tar.gz` lineage) contain the key?
4. **Barnes-Hut positioning (F5):** Is the Numba-exact-force promoted row an
   intentional statement that Barnes-Hut is partner-evidence in this
   portfolio, or is an RT-led aggregate-frontier promoted row still the goal
   for v2.x?
5. **One-shot PIP (F5):** Is the 0.249x one-shot spatial_rayjoin PIP route
   accepted as an honest "RT does not win here" data point, or is there a
   planned runtime improvement (launch/packing overhead) that targets it?
6. **Archive appetite (F4/P9):** Is moving pre-v2.10 reports out of the main
   tree acceptable under the project's history-preservation rules, or must
   all evidence remain in-repo? If in-repo, would a git subtree/branch
   arrangement satisfy the auditors?
7. **Ceremony budget (P12):** Do you accept a two-tier goal protocol, and
   which AI-consensus level should govern the tier definition itself?
8. **Scale floors (P5):** Should the 1.25 s aggregate floor from goal4266
   become a project-wide invariant encoded in the shared runner
   infrastructure, so future packets cannot ship untagged sub-floor rows?

---

*Review boundaries respected: no release authorization, no consensus file, no
tags created or moved, no public speedup/zero-copy/package-install claims
made, no source/test/doc changes other than this review file. Copilot/Codex
models were not treated as independent external AI families.*
