# V4 Current Agent Refresh Runbook

Date: 2026-06-26
Status: current working-memory refresh for V4 Goals4647-4720

## Current Release Authorization Update - 2026-06-27

Read this before any final V4 tag or review-debt decision.

Latest public-surface/Gemini-debt closure:

- rollup:
  `future/v4/reviews/v4_gemini_review_debt_rollup_for_antigravity_2026-06-27.md`
- Antigravity rollup review:
  `future/v4/reviews/antigravity_v4_gemini_review_debt_rollup_2026-06-27.md`
- closure record:
  `future/v4/reviews/v4_external_review_debt_closure_record_after_antigravity_rollup_2026-06-27.md`

Latest verdict:

```text
approve_current_external_debt_closed_except_specific_claim_blocks
```

Interpretation:

- Do not retry Gemini CLI for this debt.
- Do not retry Antigravity for Goal4777 unless a future reviewer names a new,
  exact blocker.
- The Goal4777 public-surface debt is closed.
- The public docs/tutorial P0 fixes are externally approved.
- Remaining Barnes-Hut/paper-reproduction and Tier-3/callback items are
  specific-claim boundaries only, not V4.0 public-tag blockers.

- Consolidated Gemini/Antigravity review-debt packet:
  `future/v4/reviews/v4_gemini_full_coverage_review_debt_for_antigravity_2026-06-27.md`
- Antigravity review result:
  `future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md`
- Release-owner intake:
  `future/v4/v4_goal4773_antigravity_review_intake_and_release_owner_status_2026-06-27.md`

Antigravity verdict:

```text
approve_close_gemini_debt_and_allow_v4_0_public_tag
```

Interpretation:

- The Gemini review debt seat is closed.
- The bounded V4.0 public tag is externally authorized under the current
  framing: Python eDSL/operator-pushdown release candidate, V2/V3 superset,
  complete 10-app NVIDIA RT-core matrix, two material V4/V2.14 hot-path
  candidate wins, and parity/control elsewhere.
- Goal4720-4754 older release-candidate debts are superseded by Goal4756 and
  Goal4759 unless a future reviewer identifies a unique blocker.
- Barnes-Hut paper-reproduction debts remain open only for public
  paper-reproduction wording, V2/V3/V4 author-semantics speed tables, no-copy
  tree-build wording, and related expanded claims. They do not block the
  bounded V4.0 tag.
- Tier-3/callback debts do not block the bounded V4.0 tag because arbitrary
  callbacks, raw OptiX callbacks, and Tier-3/PTX public support remain
  explicitly excluded from V4.0.

Do **not** create a git tag on the current dirty worktree's stale committed
`HEAD`. The next release-closing task is clean packaging: collect the intended
V4 release content into a clean commit/release branch, verify a clean checkout
and wheel smoke, then tag that commit.

Packaging/staging update:

- Goal4774 dirty-tree packaging audit:
  `future/v4/v4_goal4774_release_packaging_audit_2026-06-27.md`
- Goal4775 file-level release staging manifest:
  `future/v4/v4_goal4775_release_staging_manifest_2026-06-27.md`
- Goal4775 pathspec:
  `future/v4/v4_goal4775_release_stage_pathspec_2026-06-27.txt`

Goal4775 is the first usable staging boundary. It expands `git status -uall`
per file, stages compact V4 source/docs/tests/evidence, excludes raw
stdout/stderr/build/external artifacts, and holds Phoenix V3 history out of the
V4 public tag. Do **not** replace it with `git add .`.

## Why This Exists

The agent must not repeatedly rediscover known tool paths, key paths, review
failure modes, or V4 claim boundaries. Read this file before each major V4 goal
or final tag decision.

## Hard Operational Facts - Read Before Any POD Or App-Matrix Work

- Current RTX POD access from Windows/Codex:

  ```bash
  ssh root@194.68.245.170 -p 22089 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
  ```

  The default `~/.ssh/id_ed25519` is the wrong key for this POD and will fail
  with `Permission denied (publickey,password)`. Do not rediscover this.

- Equivalent historical POD keys that have also worked:

  ```bash
  ~/.ssh/id_ed25519_rtdl_codex_pod
  ~/.ssh/id_ed25519_rtdl_codex
  ```

- Current POD facts verified 2026-06-26:

  ```text
  host: 0256b71980f1
  gpu: NVIDIA RTX A5000
  driver: 570.195.03
  v2 root: /root/rtdl_v2_14_tag
  v3 root: /root/rtdl_v3_0_2_tag
  v4 root: /root/rtdl_v4_candidate_pod
  python: /root/rtdl_v4_venv/bin/python
  ```

- Local Linux `ssh 192.168.1.20` works but has `NVIDIA GeForce GTX 1070`; it is
  not an RTX/RT-core performance box and must not be used for final RT-core
  benchmark claims.

- When old tags use the V4 compatibility OptiX library, set both env vars:

  ```bash
  RTDL_OPTIX_LIB=/root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so
  RTDL_OPTIX_LIBRARY=/root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so
  ```

  The old loaders may require `RTDL_OPTIX_LIB`; using only
  `RTDL_OPTIX_LIBRARY` is insufficient.

- The existing full app runner copies the V4 candidate library into old tag
  trees as:

  ```text
  /root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so
  /root/rtdl_v3_0_2_tag/build/librtdl_optix.v4compat.so
  ```

  Use the runner helper `_env_for(...)` when possible because it sets both
  `RTDL_OPTIX_LIB` and `RTDL_OPTIX_LIBRARY`.

- Do not use Embree as the primary denominator for V4/V2.14 app claims. Embree
  is only a CPU/control reference. RTDL's project claim is NVIDIA RT-core
  programming. Any V2.14/V3/V4 comparison intended for users must prefer
  NVIDIA OptiX/RT-core routes when those routes exist.

- Hausdorff warning: `scripts/v4_goal4669_full_app_level_pod_benchmark.py`
  hardcodes the V2.14 Hausdorff row to `--backend embree`. That row explains the
  `201581x` denominator outlier and is not acceptable as the primary V2.14
  RT-core denominator. V2.14's CLI uses `--backend optix` with
  `--optix-summary-mode directed_threshold_prepared` for its strict RT-core
  threshold route; it does not accept V4's `optix_device_max_nearest` backend
  spelling. Before presenting Hausdorff to users, either rerun a valid
  RT-core-only denominator or explicitly mark the old Embree row as a control
  outlier.

- Public app matrices must not contain `n/a`. If a ratio is missing, write the
  exact blocker instead: "no complete V4 app route", "same OptiX primitive
  already existed in V2.14", "design no-go", or "RT-core-only denominator rerun
  required".

- V4 is a superset release line, not an enemy of V2.14/V3. Existing mature
  V2.14/V3 RT-core app routes must be exposed or explicitly carried as V4
  compatibility routes unless a documented removal decision says otherwise.
  Do not confuse these two claims:
  - allowed and required: "V4 supports this app through an inherited V2.14/V3
    RT-core route";
  - only allowed with fresh evidence: "V4 is faster because of a new generic
    V4 operator/runtime mechanism".
  Spatial RayJoin and Contact Manifold must not be described as simply "no V4
  route" when the intended current-version obligation is compatibility. The
  precise status is "V4 compatibility route must inherit/support the existing
  V2.14/V3 RT-core route; no new V4 generic performance route is proven yet."

- Goal-level mistake audit for this note:
  - Was I foolish? Yes.
  - Foolish action: I used the default SSH key and then the wrong old-tag OptiX
    env var while investigating a release-critical benchmark issue.
  - Better path: read/update this refresh runbook first, then use the recorded
    POD key and runner helpers.
  - Different path now: treat this section as mandatory preflight for every
    later POD/app-matrix action.

## Current Goal4720 Snapshot

The current V4 state is no longer the old 8-surface bounded-only record. It is:

- `v4_python_edsl_operator_pushdown_release_candidate_machine_gate_converged`.
- `10` measured generic operator/workflow surfaces.
- `0` current candidate surfaces.
- measured partners: `cupy`, `numba`, `rtdl_native`, `torch`.
- current release label:
  `RTDL V4 Python eDSL/operator-pushdown release candidate: 10 measured generic RT-core operator surfaces including constrained custom predicate early-exit at serious scale; broad legacy all-app speedup remains unauthorized`.
- formal public tag remains blocked by external 3-AI review debt.
- broad legacy all-app high-performance wording remains blocked.

Never revert the front door, quickstart, catalog gate, or tests back to `8`
measured surfaces or `1` candidate unless a later explicit goal removes a
surface with evidence and records that decision.

## Current V4 Goal Chain

Use:

- `future/v4/v4_goals_4647_4658_revised_partner_promotion_and_app_gate_2026-06-25.md`
- `future/v4/v4_goals_4647_4658_claude_amendments_and_final_recheck_2026-06-25.md`
- `future/v4/v4_current_goal4660_and_forward_goals_2026-06-25.md`

Current completed goals:

- Goal4647: V2.14 partner inventory and boundary ledger
- Goal4648: partner promotion contract and numeric bars
- Goal4649: CuPy grouped-vector-sum certification gate
- Goal4650: fixed Numba continuation certification gate
- Goal4651: partner catalog promotion and regression gate
- Goal4652: app route binding or blocker declaration
- Goal4653: full app-level protocol freeze
- Goal4654: serious full app-level POD benchmark, complete with blockers
- Goal4655: benchmark analysis with partner-migration and native-provenance locks
- Goal4656: public docs and machine claim-boundary correction after Goal4655
- Goal4657-4658: bounded current-state release/reframe work was superseded by
  continued high-performance V4 engineering at the user's instruction
- Goal4659-4669: Hausdorff official V4 route, adaptive CuPy argmax, protocol
  refresh, and serious full app-level rerun; result is one true app win only
- Goal4670: RTDBSCAN second-win diagnostic; result is no second true V4 win
- Goal4671: RTDBSCAN native grouped-union feasibility; result is no-go for
  RTDBSCAN as the second true V4 app-level win
- Goal4672 prerequisite: V2.14 per-app primitive audit; result is that V2.14
  already had a primitive or explicit mixed partner route for every promoted
  benchmark app. Do not count front-door migration, partner certification, or
  same-primitive productization as a V4 speed win.
- Goal4672 target selection: no clean existing app second-win target was found.
  Goal4673 must select/design a new generic runtime lever or a material
  same-primitive improvement target before any POD run.
- Goal4673: selected `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` as the next generic
  runtime lever. POD was not authorized by that gate.
- Goal4674: passed the static/protocol gate for the aggregate-frontier
  device-column native symbols and V2.14 denominator. Authorized only Goal4675
  local runner work.
- Goal4675: implemented the local V4 prepared runner
  `v4_aggregate_frontier_device_columns_2d_prepared_runner`. Antigravity
  accepted the local runner and authorized Goal4676 protocol/POD work only.
- Goal4676: serious focused POD benchmark passed on
  `root@194.68.245.170 -p 22089`, RTX A5000. Key ratios:
  - V4 frontier-only hot over V2.14: `302.998x`;
  - V4 full hot over V2.14: `310.024x`;
  - V4 full wall over V2.14: `200.826x`;
  - V4 full hot over V3.0.2 control: `0.998x`.
  This is V2.14 host-frontier bottleneck removal, not a V4-over-V3 speed win.
- Goal4677: promoted `v4_aggregate_frontier_device_columns_2d_prepared_runner`
  from candidate to measured V4 route with measured partners `rtdl_native` and
  `cupy`; `torch` and `numba` remain unmeasured for that surface. Current V4
  front door has 9 measured surfaces. Release and
  whole-app high-performance wording remain unauthorized.
- Goal4678: deferred `v4_fixed_radius_ranked_summary_3d_prepared_runner` out of
  the current candidate front door because Goal4660/4661 serious rows were
  parity or below parity and did not move the RTNN app-level bar. Current V4
  front door now has 9 measured surfaces and 0 open candidate surfaces.
- Goal4679: selected `SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR`
  as the next V4 target under a strict same-primitive/productization-or-material
  improvement classification. This is not a clean new V4 speed lever because
  V2.14 already had prepared shape-pair active-count routes. Goal4679 does not
  authorize POD or release wording.
- Goal4680: created the local/static V4 frontdoor and protocol gate for
  `v4_shape_pair_relation_active_count_2d_prepared_left_executor`. The wrapper
  stays out of the measured/candidate catalog until POD evidence exists. The
  gate freezes the V2.14 strongest same-primitive denominator and bars, and
  local validation passed with 39 tests OK.
- Goal4681: ran the focused shape-pair relation POD benchmark on a generated
  4096-shape same-primitive CDB input. Correctness/count parity passed and V4
  hot-path row-stream materialization was false, but speed bars failed:
  V4/V2.14 hot `0.963x`, V4/V2.14 wall `0.605x`, V4/V3.0.2 hot `0.977x`.
  This route is no speed credit and must not be promoted to measured catalog.
- Goal4682: closed shape-pair relation active count as no-promotion and selected
  `AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D` only as a Goal4683 design/audit
  gate. Goal4682 does not authorize implementation or POD. The new target must
  be killed if it is just V2.14 bounded collect-k rebranded.
- Goal4683: killed `AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D` as a V4.0
  high-performance target before implementation/POD. Audit found V2.14 already
  has bounded collect-k native/OptiX/Embree surfaces, while the current tree
  already has exact-witness partner device-column adapters. Continuing would
  risk rebranding existing V2.14/current work as a V4 speed win. No
  implementation, POD, release wording, or partner-migration speed credit is
  authorized.
- Goal4684: reset the high-performance V4 target search. No clean existing
  Tier-2/app target remains for near-term formal high-performance V4: RTDBSCAN
  is no-go/modest, RTNN/ranked summary is deferred for serious-scale parity,
  shape-pair failed speed bars, contact/witness was killed by the V2.14
  collect-k audit, aggregate-frontier is a V2.14 bottleneck/productization win
  but parity with V3.0.2, and Goal4672 already showed all promoted benchmark
  apps had V2.14 primitive or partner routes. The selected next architecture
  track is `TIER3_WRAPPER_DIRECT_CALLABLE_ABI_SPIKE`, spike-only and not release
  support.
- Goal4685: froze the Tier-3 wrapper/direct-callable ABI protocol gate. This
  goal does not authorize implementation or POD. It requires the next real
  spike to compose Numba scalar callback PTX with a semantic OptiX traversal
  shell or direct-callable ABI; repeating the old bare-helper PTX
  `optixModuleCreate` probe is explicitly forbidden. Planner boundary remains:
  scalar Numba callbacks are spike-only, action-shaped callbacks are rejected,
  all Tier-3 support/release/speed claims false.
- Goal4686: implemented the local Tier-3 semantic wrapper/direct-callable ABI
  scaffold and dry-run script. Generated evidence:
  `future/v4/evidence/v4_goal4686_tier3_wrapper_abi_scaffold_2026-06-25.json`,
  `.md`, and `.cu`. The scaffold includes semantic entries
  `__direct_callable__rtdl_tier3_scalar_reduce`,
  `__raygen__rtdl_tier3_probe`, `__miss__rtdl_tier3_probe`, and
  `__closesthit__rtdl_tier3_probe`, with callback symbol contract
  `rtdl_user_scalar_reduce`. It is local scaffold only: no POD, no compile
  proof, no link proof, no launch proof, no Tier-3 support claim.
- Goal4687: POD symbol extraction and semantic wrapper compile probe passed.
  Evidence:
  `future/v4/evidence/v4_goal4687_tier3_wrapper_compile_probe_2026-06-25.json`
  and `.md`. Numba PTX generation succeeded, the real callback symbol was
  extracted, the wrapper source was specialized to that symbol, and `nvcc`
  compiled wrapper PTX successfully. This is compile-only progress:
  `optix_module_link_attempted: false`, `pipeline_launch_attempted: false`.
  No Tier-3 support/release/speed claim is authorized.
- Goal4688: POD semantic wrapper module-link and pipeline probe passed.
  Evidence:
  `future/v4/evidence/v4_goal4688_tier3_module_link_probe_2026-06-25.json`
  and `.md`. Numba C-ABI callback PTX was composed with the semantic OptiX
  wrapper PTX; `optixModuleCreate`, raygen/miss/hitgroup/direct-callable
  program groups, and `optixPipelineCreate` all succeeded. The required wrapper
  compile flag is `--keep-device-functions`; without it nvcc emits the direct
  callable as an internal `.func` and OptiX cannot create the callable program
  group. The raygen entry is intentionally empty in Goal4688; a normal C call
  from raygen to the direct callable makes pipeline creation fail with an
  unresolved external. Goal4689 owns the first real launch/callable invocation.
  This is still spike-only: `pipeline_launch_attempted: false`, no callback
  correctness, no overhead, no Tier-3 public support, no release claim.
- Goal4689: POD semantic wrapper minimal launch/correctness probe passed.
  Evidence:
  `future/v4/evidence/v4_goal4689_tier3_minimal_launch_probe_2026-06-25.json`
  and `.md`. The pipeline launched with `optixDirectCall<void>(0)`, the pipeline
  log reported `direct callable call(s): 1`, `optixLaunch` returned `0`, and the
  output value was `5`, matching the expected Numba callback result
  `state + hit_distance * weight` for `(1.0, 0, 2.0, 3.0)`. This proves one
  scalar direct-callable callback shape can launch correctly. It still does not
  prove overhead, arbitrary callback support, action callbacks, app-level speed,
  or release readiness.
- Goal4690: Tier-3 callback overhead protocol froze the next measurement before
  timing. Evidence:
  `future/v4/evidence/v4_goal4690_tier3_overhead_protocol_2026-06-25.json`
  and `.md`. Primary ratio:
  `direct_callable_loop_median_ms / direct_device_function_loop_median_ms`.
  Frozen parameters: 1,000,000 inner iterations per launch, 5 warmup launches,
  30 measured launches, pass `<=1.50x`, hard kill `>2.00x`, correctness
  required. The primary denominator is the same Numba callback called as a
  direct device function; inline formula is context only. No timing claim yet.
- Goal4691: Tier-3 callback overhead POD measurement completed and classified
  yellow, not pass. Evidence:
  `future/v4/evidence/v4_goal4691_tier3_overhead_measurement_2026-06-25.json`
  and `.md`. All correctness checks passed. Medians:
  inline formula context `25.3571 ms`, direct device-function same Numba
  callback denominator `137.03 ms`, OptiX direct-callable path `228.916 ms`.
  Primary ratio `1.6705538933080346x`, above the `<=1.50x` pass threshold and
  below the `>2.00x` hard-kill threshold. Classification:
  `yellow_overhead_between_pass_and_kill`. This does not authorize Tier-3
  public support or performance claims.
- Goal4692: Tier-3 support decision after the yellow overhead result. Evidence:
  `future/v4/evidence/v4_goal4692_tier3_support_decision_2026-06-25.json`
  and `.md`. Decision: do not promote OptiX SBT direct-callable support from
  the current `1.67x` overhead evidence. Do not hard-kill Tier-3 because the
  same Numba callback worked as a faster direct device-function denominator.
  Pivot next to `module_specialized_direct_device_callback_in_hit_program`.
  Public Tier-3 support remains unauthorized.
- Goal4693: specialized direct-device callback inside an OptiX hit-program probe
  passed on POD. Evidence:
  `future/v4/evidence/v4_goal4693_specialized_hit_callback_probe_2026-06-25.json`
  and `.md`. The probe built a custom-primitive GAS, launched `optixTrace`,
  executed intersection and closesthit programs, and called the Numba C-ABI
  callback as a normal device function from closesthit. Output was `5`, expected
  `5`, correctness passed. The module/pipeline logs show raygen `trace call(s):
  1`, closesthit/intersection semantic entries, and `direct callable call(s): 0`.
  This proves the specialized hit-callback path exists without SBT direct
  callable overhead. It is still not public Tier-3 support or a performance
  claim.
- Goal4694: specialized hit callback overhead protocol frozen. Evidence:
  `future/v4/evidence/v4_goal4694_specialized_hit_overhead_protocol_2026-06-25.json`
  and `.md`. Primary ratio:
  `hit_direct_device_callback_trace_loop_median_ms / hit_inline_formula_trace_loop_median_ms`.
  Frozen parameters: 100,000 trace iterations per launch, 3 warmups, 20 measured
  launches, pass `<=1.50x`, hard kill `>2.00x`, correctness required. No timing
  claim yet.
- Goal4695: specialized hit callback overhead POD measurement passed the
  focused gate. Evidence:
  `future/v4/evidence/v4_goal4695_specialized_hit_overhead_measurement_2026-06-25.json`
  and `.md`. Medians: inline hit formula trace-loop `218.1055 ms`, direct
  device Numba callback in closesthit `225.8535 ms`. Primary ratio
  `1.0355240926982583x`, classification
  `pass_hit_overhead_gate_not_support`. This justifies continuing the
  specialized direct-device callback productization track, but still does not
  authorize public Tier-3 support, arbitrary callbacks, app-level speed claims,
  or release.
- Goal4696: specialized Tier-3 productization decision completed. Evidence:
  `future/v4/evidence/v4_goal4696_tier3_productization_decision_2026-06-25.json`
  and `.md`. Decision: productize only a constrained candidate surface for
  `module_specialized_direct_device_callback` with supported shape
  `pure_scalar_return_numba_cabi_device_function`. Rejected shapes:
  arbitrary Python callback, action/side-effect callback, external memory
  mutation callback, and dynamic SBT direct-callable hot path. Required before
  public support: stable API contract, negative validation, compile/cache/error
  reporting, at least one app-route validation, and external 3-AI review. This
  is not public Tier-3 support, not app-level speed evidence, and not release
  authorization.
- Goal4697: constrained specialized Tier-3 API contract scaffold completed.
  Evidence:
  `future/v4/evidence/v4_goal4697_specialized_tier3_api_contract_2026-06-25.json`
  and `.md`. Added explicit internal contract planner for
  `module_specialized_direct_device_callback`, accepting only Numba C-ABI
  device-function scalar callback shapes (`custom_scalar_reduce`,
  `custom_score`, `custom_threshold`, `custom_minmax`) and rejecting arbitrary
  Python callbacks, action/side-effect callbacks, external memory mutation,
  dynamic SBT direct callable hot path, and non-scalar signatures. The ordinary
  V4 public planner remains closed for Tier-3 support. Local validation: 25
  tests OK plus py_compile. This is not public Tier-3 support and not release
  authorization.
- Goal4698: specialized Tier-3 compile/cache/error-reporting scaffold
  completed. Evidence:
  `future/v4/evidence/v4_goal4698_specialized_tier3_compile_cache_2026-06-25.json`
  and `.md`. Added deterministic cache key over contract version, callback
  symbol, callback PTX hash, toolchain fingerprint hash, OptiX ABI, compute
  target, and wrapper strategy. Added fail-closed compile planning:
  accepted scalar candidate reaches `compile_cache_ready_not_executed`,
  rejected callbacks stop at `rejected_before_compile`, incomplete inputs stop
  at `compile_input_incomplete`, and compile/link failures classify by stage
  such as `optix_module_create`. Local validation: 10 tests OK plus py_compile.
  This is not public Tier-3 support, not app-level speed evidence, and not
  release authorization.
- Goal4699: specialized Tier-3 app-route validation protocol frozen. Evidence:
  `future/v4/evidence/v4_goal4699_specialized_tier3_app_route_protocol_2026-06-25.json`
  and `.md`. Selected route:
  `ray_triangle_any_hit_weighted_sum_scalar_reduce` against existing surface
  `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`. Correctness
  denominator: existing Tier-2 built-in weighted-sum device-output route.
  Primary performance denominator: existing Tier-2 built-in weighted-sum fused
  route on the same fixture. Context denominator: legacy host-scalar/materialized
  weighted-sum route from Goal4633. Frozen sizes: 32768, 131072, 262144 rays;
  warmup 3; repeat 10. Pass requires exact parity and
  callback/Tier-2 median ratio `<=1.20x` at every size; hard kill any size
  `>1.50x`; callback must also remain at least `1.20x` faster than the context
  host-scalar route. This protocol exists to prevent a fake win against only a
  slow baseline. Not public Tier-3 support and not release authorization.
- Goal4700: specialized Tier-3 app-route POD implementation/run completed on
  `root@194.68.245.170 -p 22089`, RTX A5000. Evidence:
  `future/v4/evidence/v4_goal4700_specialized_tier3_app_route_pod_2026-06-25.json`
  and `.md`, plus `future/v4/evidence/v4_goal4700_pod_run_2026-06-25.log`.
  Classification: `pass_app_route_gate_not_public_support`. Rows:
  - 32768 rays: parity true, callback/Tier-2 `0.7445223616221324x`,
    legacy-host/callback `2.9850275425570643x`.
  - 131072 rays: parity true, callback/Tier-2 `0.8513881142887039x`,
    legacy-host/callback `1.9018490908790582x`.
  - 262144 rays: parity true, callback/Tier-2 `0.89139416400604x`,
    legacy-host/callback `1.5134843075596194x`.
  Interpretation: first app-route evidence that the constrained specialized
  Tier-3 callback path can pass a frozen gate against the existing Tier-2
  built-in fused route, not just against a slow host-materialized context
  route. This still does not authorize public Tier-3 support, arbitrary
  callbacks, raw OptiX callback support, app-level speed claims, or release.
- Goal4701: specialized Tier-3 support-candidate packet completed. Evidence:
  `future/v4/evidence/v4_goal4701_specialized_tier3_support_candidate_2026-06-25.json`
  and `.md`. Candidate label:
  `specialized_numba_scalar_callback_support_candidate`. Scope:
  module-specialized Numba C-ABI scalar device callback called as a direct
  device function from an RTDL-generated OptiX hit-program route. This packages
  Goals4696-4700 as support-candidate evidence only. Missing before public
  support: external 3-AI review of Goals4696-4700, 20 compile/link/launch
  attempts across at least 4 accepted scalar callback variants, dense/sparse/no-hit
  correctness datasets, cache reuse/error-reporting tests under repeated
  compiles, bounded user docs wording, and final release/support authorization.
  Public Tier-3 support remains false.

Current next goal:

- Goal4702: specialized Tier-3 reliability matrix protocol completed pending
  3-AI review debt. Evidence:
  `future/v4/evidence/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.json`
  and `.md`. The protocol freezes 20 total attempts across 4 callback variants
  (`custom_scalar_reduce_weighted_sum`, `custom_score_affine`,
  `custom_threshold_flag`, `custom_minmax_score`), 5 attempts per variant,
  dense/sparse/no-hit correctness datasets, a `>=0.95` compile/link/launch
  success floor, deterministic cache-key checks, and Goal4698 stage-specific
  failure classification. Local validation: evidence generation passed,
  py_compile passed, and `6 tests OK`. This does not authorize public Tier-3
  support, arbitrary callbacks, raw OptiX callback support, release wording, or
  performance claims.
- Goal4703: specialized Tier-3 reliability matrix POD run. Required output:
  execute the frozen Goal4702 matrix on POD, report all 20 attempts, correctness
  rows for dense/sparse/no-hit datasets, cache behavior, failure stages if any,
  and a pass/fail classification. Do not rerun aggregate-frontier unless an
  external reviewer rejects the Goal4676 denominator.
- Goal4703 completed pending 3-AI review debt. Evidence:
  `future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_pod_2026-06-25.json`
  and `.md`. POD: `root@194.68.245.170 -p 22089`, RTX A5000, driver
  570.195.03. Result: `pass_reliability_gate_not_public_support`, 20/20
  compile/link/launch attempts passed, correctness passed for dense/sparse/no-hit
  datasets, cache checks passed, no stage failures. Important note: separately
  recompiled Numba PTX hashes varied across attempts; this is recorded as a
  future source-level cache-canonicalization hardening item, while Goal4702's
  artifact-level cache contract passed. This still does not authorize public
  Tier-3 support, arbitrary callbacks, raw OptiX callback support, release
  wording, or performance claims.
- Goal4704: specialized Tier-3 support wording and docs gate. Required output:
  convert Goals4696-4703 into bounded internal/support-candidate wording,
  enumerate remaining hardening gates, and keep public support/release/performance
  claims false until external 3-AI review authorizes otherwise.
- Goal4704 completed pending 3-AI review debt. Evidence:
  `future/v4/evidence/v4_goal4704_specialized_tier3_support_wording_2026-06-25.json`
  and `.md`. `claim_boundary_v4()` now exposes the candidate label/status while
  keeping `tier3_callback_claim_authorized: false` and
  `tier3_specialized_callback_public_support_authorized: false`. Allowed wording
  is limited to `specialized Tier-3 support candidate`; prohibited wording
  includes arbitrary callbacks, raw OptiX callbacks, public Tier-3 API,
  release-ready callback support, and performance wins. Local validation:
  evidence generation passed, py_compile passed, and `7 tests OK`.
- Goal4705: source-level PTX canonicalization and repeated compile
  cache-stability gate. Required output: decide whether to canonicalize Numba PTX
  or explicitly document artifact-level caching only, then add a validation gate
  so repeated source-level callback compiles cannot silently degrade support
  ergonomics.
- Goal4705 completed pending 3-AI review debt. Evidence:
  `future/v4/evidence/v4_goal4705_source_ptx_cache_stability_pod_2026-06-25.json`
  and `.md`. Implementation updated
  `src/rtdsl/v4_goal4698_specialized_tier3_compile_cache.py` with
  `canonicalize_v4_goal4698_callback_ptx_for_cache`, normalizing NumbaEnv
  `B2vN` token drift for cache-key hashing. Raw PTX hash remains audit metadata
  but no longer participates in key serialization. POD result: all 4 callback
  variants had raw PTX hash drift across repeated compile, canonical hash stable,
  cache key stable, changed PTX changed key, and changed toolchain changed key.
  Classification: `pass_source_level_cache_stability_gate_not_public_support`.
  Local validation: dry-run passed, py_compile passed, and `10 tests OK`.
- Goal4706: specialized Tier-3 negative validation and user-doc example gate.
  Required output: validate that rejected callback shapes fail closed with clear
  errors, provide a bounded internal/example doc for accepted scalar callbacks,
  and keep all public support/release/performance flags false pending 3-AI
  review.
- Goal4706 completed pending 3-AI review debt. Evidence:
  `future/v4/evidence/v4_goal4706_negative_validation_docs_gate_2026-06-25.json`
  and `.md`. Example:
  `future/v4/examples/v4_specialized_tier3_scalar_callback_candidate_example.py`.
  Negative rows rejected before compile: arbitrary Python callback,
  action/side-effect callback, external memory mutation callback, dynamic SBT
  direct-callable hot path, and non-scalar variable-length output. Accepted
  example reaches `compile_cache_ready_not_executed` while public support,
  release, and performance flags remain false. Local validation: evidence
  generation passed, py_compile passed, and `9 tests OK`.
- Goal4707: specialized Tier-3 external-review packet and debt consolidation.
  Required output: one reviewer-friendly packet for Goals4696-4706, list all
  open review debts, list exact non-authorizations, and ask reviewers whether
  the candidate may proceed toward public-support authorization gates.
- Goal4707 completed pending external review. Packet:
  `future/v4/v4_goal4707_specialized_tier3_external_review_packet_2026-06-25.md`.
  Debt ledger:
  `future/v4/reviews/v4_goal4707_specialized_tier3_review_debt_ledger_2026-06-25.md`.
  Forward message:
  `future/v4/reviews/v4_goal4707_forward_message_to_reviewer_2026-06-25.txt`.
  Requested verdicts: `accept_candidate_continue_public_support_hardening`,
  `accept_candidate_with_required_amendments`, or
  `reject_candidate_keep_spike_only`. This still does not authorize V4 release,
  public Tier-3 support, arbitrary callbacks, raw OptiX callbacks, app-level
  speed claims, or high-performance V4 wording.
- Goal4708 completed pending 3-AI review debt. Evidence:
  `future/v4/evidence/v4_goal4708_app_value_route_selection_2026-06-25.json`
  and `.md`. Decision:
  `do_not_count_specialized_tier3_candidate_as_app_level_high_performance_evidence`.
  The specialized Tier-3 weighted-sum route is an operator/support-candidate
  result only; it is not bound to a promoted benchmark app and cannot count as a
  formal V4 app-level speed win. Local validation: evidence generation passed,
  py_compile passed, and `8 tests OK`.
- Goal4709: formal high-performance V4 app-level target selection outside the
  Tier-3 candidate. Required output: select a real app-level target, freeze why
  it could produce a genuine V4-over-V2/V3 win, and block POD spend unless the
  selected route is not just partner migration, same-primitive repackaging, or
  an operator-only claim.
- Goal4709 completed pending 3-AI review debt. Evidence:
  `future/v4/evidence/v4_goal4709_formal_hp_app_target_selection_2026-06-25.json`
  and `.md`. Selected app target:
  `ray_triangle_custom_scored_accumulation`. Existing targets rejected:
  `rt_dbscan`, `raydb_style`, `triangle_counting`, `librts_spatial_index`,
  `hausdorff_xhd`, `rtnn`. POD is not authorized by Goal4709; only Goal4710
  protocol freeze is authorized. Local validation: evidence generation passed,
  py_compile passed, and `7 tests OK`.
- Goal4710: ray-triangle custom scored accumulation app-level protocol freeze.
  Required output: freeze V2.14/V3.0.2/V4 denominators, callback variants,
  dense/sparse scales, correctness gates, numeric bars, and kill conditions
  before any POD run.
- Goal4710 completed pending 3-AI review debt. Evidence:
  `future/v4/evidence/v4_goal4710_custom_scored_app_protocol_2026-06-25.json`
  and `.md`. Primary callbacks: `affine_score`, `threshold_score`,
  `minmax_score`. `weighted_sum` is control only. Scales: `262144`, `524288`.
  Regimes: dense/sparse/no-hit. Bars: geomean over V2.14 `>=1.50x`, geomean
  over V3.0.2 `>=1.20x`, every primary callback `>=1.10x` over V3.0.2 in dense
  and sparse regimes. Goal4710 authorizes only Goal4711 focused POD benchmark,
  not app-level speed claims or release wording. Local validation: evidence
  generation passed, py_compile passed, and `6 tests OK`.
- Goal4711: ray-triangle custom scored accumulation focused POD benchmark.
  Required output: run the frozen protocol on POD, record V2.14/V3.0.2
  denominator discovery before V4 timing, produce callback x regime x scale
  rows, classify against Goal4710 bars, and preserve all non-authorization
  flags unless bars pass and external review later authorizes wording.

## Tool Facts To Stop Relearning

### Claude CLI

Known path:

```text
C:\Users\Lestat\.local\bin\claude.exe
```

Known working call shape:

```powershell
$Prompt | & "C:\Users\Lestat\.local\bin\claude.exe" --print --dangerously-skip-permissions --add-dir $Root > $Out 2> $Err
```

Current state as of 2026-06-25:

```text
You've hit your weekly limit - resets Jun 28, 7pm (America/New_York)
```

Rule:

- Until Jun 28, 2026 7pm America/New_York, do not retest Claude availability
  for every goal. The weekly-limit state is already known.
- For goals completed before that reset time, record Claude review debt directly
  using the known limit message and continue with available seats.
- After the reset time, do one bounded attempt only when review is required.
- Do not loop on Claude availability.

### Antigravity CLI

Known path:

```text
C:\Users\Lestat\AppData\Local\agy\bin\agy.exe
```

Known call shape:

```powershell
& "C:\Users\Lestat\AppData\Local\agy\bin\agy.exe" -p $Prompt --dangerously-skip-permissions --add-dir $Root --print-timeout 5m > $Out 2> $Err
```

Current observed failure mode:

- command exits `0`;
- stdout file length is `0`;
- stderr file length is `0`;
- this is not a review verdict.

Rule:

- Do one bounded attempt only when review is required.
- Empty stdout/stderr is review debt, not approval.
- Do not spend repeated cycles learning the CLI again.

### Gemini CLI

Current instruction:

- Do not call Gemini CLI until the user says the Google policy/auth issue is
  fixed.

### POD SSH

For the current V4 POD supplied by the user:

```text
ssh root@194.68.245.170 -p 22089 -i ~/.ssh/id_ed25519
```

Observed fact:

- plain `~/.ssh/id_ed25519` may fail for Codex shell.
- the historically correct key in this workspace is:

```text
C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

Working call shape:

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@194.68.245.170 -p 22089 -i $env:USERPROFILE\.ssh\id_ed25519_rtdl_codex_current_pod "hostname; python3 --version; nvidia-smi --query-gpu=name,driver_version --format=csv,noheader"
```

Known environment from Goal4649:

- GPU: NVIDIA RTX A5000
- driver: 570.195.03
- Python: 3.12.3
- CuPy in venv: `/root/rtdl_v4_venv`
- remote minimal workspace used earlier: `/root/rtdl_goal4649`
- current full candidate workspace: `/root/rtdl_v4_candidate_pod`
- V2.14 tag archive workspace: `/root/rtdl_v2_14_tag`
- V3.0.2 tag archive workspace: `/root/rtdl_v3_0_2_tag`
- Goal4654 serious evidence on POD:
  `/root/v4_goal4654_serious_20260625_2`
- Goal4654 serious evidence copied locally:
  `future/v4/evidence/v4_goal4654_serious_20260625_2/`
- Goal4654 Antigravity verdict:
  `accept_goal4654_complete_with_blockers_proceed_goal4655`

Rule:

- Use the correct key first.
- Do not burn time retrying the wrong key.
- Only use POD when a goal requires hardware evidence; Goals4650 and 4651 did
  not require new POD runs because they reused reviewed evidence.

## Goal4654 Facts To Preserve

- Serious app-level rows were run for `rt_dbscan`, `raydb_style`,
  `triangle_counting`, and `librts_spatial_index` across V2.14, V3.0.2, and V4.
- All main rows returned `0`, all JSON parsed, all hot metrics were present.
- Scorecard:
  - `rt_dbscan`: V4/V2.14 `1.070x`, V4/V3.0.2 `1.084x`.
  - `raydb_style`: V4/V2.14 `0.994x`, V4/V3.0.2 `1.000x`.
  - `triangle_counting`: V4/V2.14 `15.548x`, V4/V3.0.2 `1.117x`.
  - `librts_spatial_index`: V4/V2.14 `0.999x`, V4/V3.0.2 `1.001x`.
- V2.14 and V3.0.2 OptiX native libraries could not be built on the POD because
  OptiX SDK headers are absent.
- Old-version OptiX rows used a declared V4 compatibility native library.
- RTDBSCAN large performance rows used `--no-validation`; same-route 2048-point
  parity companion rows passed.
- Antigravity accepted Goal4654 as complete with blockers and directed Goal4655.
- Do not turn Goal4654 into public speed wording. Goal4655 must preserve the
  native-provenance blocker and partner-migration lock.

## Goal4655 Facts To Preserve

- Decision label:
  `bounded_operator_v4_only__app_level_high_performance_not_supported`.
- Formal high-performance V4 is not supported by Goal4654/4655 evidence.
- App classifications:
  - `rt_dbscan`: `modest_runtime_gain_below_formal_bar`.
  - `raydb_style`: `parity_not_v4_speed_win`.
  - `triangle_counting`: `historical_route_evolution_plus_modest_v4_increment`.
  - `librts_spatial_index`: `parity_not_v4_speed_win`.
- Blocking reasons:
  - `old_version_optix_uses_v4_compatibility_native_library`.
  - `most_full_app_rows_do_not_pass_frozen_speed_bar`.
  - `insufficient_independent_true_v4_app_wins`.
- Antigravity accepted Goal4655 and directed Goal4656 docs/tutorial rewrite.
- Goal4656 must rewrite public/user docs around bounded operator V4 truth, not
  broad whole-app high-performance claims.

## Goal4656 Facts To Preserve

- Goal4656 completion report:
  `future/v4/v4_goal4656_public_docs_machine_boundary_correction_2026-06-25.md`.
- Antigravity accepted Goal4656:
  `future/v4/reviews/antigravity_v4_goal4656_public_docs_machine_boundary_review_2026-06-25.md`.
- Completion/debt record:
  `future/v4/reviews/goal4656_completion_consensus_and_review_debt_2026-06-25.md`.
- Current front door:
  `v4_bounded_operator_front_door_goal4655_corrected`.
- Current scope gate:
  `v4_bounded_operator_scope_goal4655_corrected` at Goal4656 time; superseded
  by Goal4677 and then Goal4678 current scope gate
  `v4_bounded_operator_scope_goal4678_no_open_candidates`.
- Current machine truth:
  - `formal_release_authorized: false`
  - `release_authorized: false`
  - `bounded_operator_surface_available: true`
  - `app_level_high_performance_authorized: false`
  - `goal4655_decision_label:
    bounded_operator_v4_only__app_level_high_performance_not_supported`
- Goal4643/Goal4644 publication records are superseded for current truth by
  Goal4655 and then Goal4677.
- Goal4656 verification passed:
  `59 tests OK`.
- Next Goal4657 should seek final authorization for the honest current state.
  Expected current verdict is `bounded_operator_v4_release_only`, not formal
  app-level high-performance V4.

## Goal4659 Facts To Preserve

- Goal4659 report:
  `future/v4/v4_goal4659_hausdorff_official_v4_route_evidence_2026-06-25.md`.
- Evidence directory:
  `future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/`.
- Machine summary:
  `future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/summary.json`.
- Code changes:
  - `src/rtdsl/partner_adapters.py`: `global_argmax_u32_f64_partner_columns`
    now supports `partner="torch"` through a generic Torch masked reduction.
  - `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`:
    `--backend optix_device_max_nearest --partner torch` uses the official
    V4 point-group front door.
- POD evidence on `root@194.68.245.170 -p 22089`, RTX A5000:
  - 65,536 points/side: V4 Torch official hot path `3.309x` faster than
    V3.0.2 CuPy device-max route; correctness passed.
  - 262,144 points/side: V4 Torch official hot path `1.260x` faster than
    V3.0.2 CuPy device-max route; correctness passed.
  - 262,144 points/side: V2.14 Embree directed-summary primary metric
    `823.278458s`; V4 hot metric `0.002525s`; correctness passed. This is a
    route-class win, not a single universal V4 claim.
  - 1,048,576 points/side, unnormalized: V3.0.2 CuPy and V4 Torch both failed
    exact oracle parity with observed distance `0.32015618681907654` vs expected
    `0.30000000000000004`.
  - 1,048,576 points/side, V4 coordinate-normalized
    `--coordinate-normalization-span 1000000`: correctness passed, distance
    `0.2999999523162842`, `3` chunks per directed pass, hot metric
    `0.015843737870454788s`, prepare `12.314798556268215s`.
  - Span sweep: `1000000` passed; `1200000`, `1500000`, `1800000`, and
    `2000000` failed with observed distance `0.32015618681907654`.
- Correct interpretation:
  - Goal4659 is real V4 app-route progress for `hausdorff_xhd`.
  - It does not authorize final V4 release, broad app-level speedup wording, or
    unrestricted exact Hausdorff claims.
  - The unnormalized 1M-row failure is a native precision/fixture contract issue:
    `float32_computed_float64_output` with large absolute tiled coordinates.
  - Coordinate-normalized chunking repairs exactness but is not a speed win.
  - Next engineering should address prepare overhead and decide whether
    coordinate normalization or higher-precision native distance is the public
    route before any release promotion.

## Goal4660/4661 RTNN Facts To Preserve

- Goal4660/4661 report:
  `future/v4/v4_goal4660_4661_rtnn_ranked_summary_candidate_evidence_2026-06-25.md`.
- Machine summary:
  `future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json`.
- V4 candidate surface:
  `v4_fixed_radius_ranked_summary_3d_prepared_runner`.
- Candidate status:
  `candidate_goal4660_needs_pod_scorecard_not_release`.
- Denominator boundary:
  V2.14/V3.0.2 use closest old `prepared_optix_ranked_summary`; they do not
  expose V4 `prepared_execution_ranked_summary`, so this is not an exact
  same-runner V2/V3/V4 comparison.
- Serious hot-path results:
  - 65,536 points: V4/V2.14 `1.145x`, V4/V3.0.2 `1.066x`.
  - 262,144 points: V4/V2.14 `0.999x`, V4/V3.0.2 `1.005x`.
  - 1,048,576 points: V4/V2.14 `0.994x`, V4/V3.0.2 `0.993x`.
- Decision:
  `rtnn_candidate_does_not_move_app_level_bar`.
- Interpretation:
  RTNN candidate route exists and validates, but it is hot-path parity at
  serious scales. It is not formal high-performance V4 evidence and must not
  trigger broad speed wording or a full all-app rerun by itself.

## Goal4662 Route Matrix Facts To Preserve

- Goal4662 report:
  `future/v4/v4_goal4662_app_route_binding_after_hausdorff_rtnn_2026-06-25.md`.
- Machine evidence:
  `future/v4/evidence/v4_goal4662_app_route_binding_after_hausdorff_rtnn_2026-06-25.json`.
- Hausdorff current route status:
  `official_v4_route_with_coordinate_normalized_correctness_boundary`.
- RTNN current route status:
  `candidate_ranked_summary_present_but_app_bar_not_moved`.
- Focused validation:
  `43 tests OK`.
- Broader V4 boundary validation:
  `73 tests OK`.
- Non-authorization:
  Goal4662 does not authorize V4 release, formal high-performance V4 wording,
  whole-app speedup wording, unrestricted Hausdorff exactness, or exact
  same-runner RTNN speedup wording.

## Goal4663 Protocol Refresh Facts To Preserve

- Goal4663 report:
  `future/v4/v4_goal4663_app_level_protocol_refresh_after_changed_routes_2026-06-25.md`.
- Machine evidence:
  `future/v4/evidence/v4_goal4663_app_level_protocol_refresh_after_changed_routes_2026-06-25.json`.
- Decision:
  `protocol_refreshed__no_full_all_app_rerun_triggered`.
- Reason:
  Hausdorff route truth changed but remains correctness-bound; RTNN candidate
  route exists but is performance-failed at serious scales.
- Current run decision:
  do not spend POD time on another full all-app rerun from the current changed
  rows. Next useful work must be a real performance-engineering route that can
  move a serious app-level bar.
- Broader V4 boundary validation:
  `73 tests OK`.

## Goal4658 Final Recheck Facts To Preserve

- Goal4658 report:
  `future/v4/v4_goal4658_final_recheck_guardrails_completion_audit_2026-06-25.md`.
- Machine audit:
  `future/v4/evidence/v4_goal4658_final_recheck_guardrails_completion_audit_2026-06-25.json`.
- Review debt record:
  `future/v4/reviews/goal4658_completion_review_debt_and_no_release_authorization_2026-06-25.md`.
- Decision:
  `bounded_operator_v4_only__formal_high_performance_not_supported`.
- Status:
  `goal4658_final_recheck_complete_no_release_authorization`.
- Validation:
  `77 tests OK`.
- Meaning:
  The revised Goal4647-4658 chain is complete as a bounded-operator / partner
  unification investigation and guardrail pass, not as a formal app-level
  high-performance V4 release.
- Review state:
  3-AI consensus is not complete; Claude is still known unavailable until the
  weekly-limit reset, Antigravity empty output is debt not approval, and release
  or tag remains unauthorized.

## Goal4664 Next Performance Target Facts To Preserve

- Goal4664 report:
  `future/v4/v4_goal4664_next_performance_target_selection_2026-06-25.md`.
- Machine evidence:
  `future/v4/evidence/v4_goal4664_next_performance_target_selection_2026-06-25.json`.
- Decision:
  `select_hausdorff_for_goal4665_focused_formal_candidate_run`.
- Selected app:
  `hausdorff_xhd`.
- Why:
  Hausdorff has an official generic V4 route and exploratory correctness-passing
  262,144 points/side evidence at `1.260x` hot-path speedup over V3.0.2 CuPy.
- Why not RTNN:
  RTNN serious rows are parity/slower and continuing it as a performance target
  would be fake progress.
- Why not all-app:
  current changed rows cannot overturn Goal4655; focused frozen target first.
- Validation:
  `46 tests OK`.
- Goal4665 frozen primary bars:
  V4/V3.0.2 hot speedup >= `1.20x`, V4/V2.14 primary metric speedup >= `1.20x`,
  correctness parity required, no Hausdorff-specific native kernel.

## Goal4665 Hausdorff Focused Run Facts To Preserve

- Goal4665 report:
  `future/v4/v4_goal4665_hausdorff_focused_formal_candidate_run_2026-06-25.md`.
- Machine summary:
  `future/v4/evidence/v4_goal4665_hausdorff_focused_20260625/summary.json`.
- Decision:
  `hausdorff_formal_candidate_fails_focused_bar`.
- Same-hardware POD:
  `root@194.68.245.170:22089`, RTX A5000.
- Fresh frozen results:
  - 65,536 points/side: correctness passed; V4/V3.0.2 hot `1.278x`; prepare
    floor failed at `0.479x`.
  - 262,144 points/side: correctness passed; V4/V3.0.2 hot `0.649x`; prepare
    floor failed at `0.711x`; this is the serious-row formal bar failure.
  - 1,048,576 points/side: V4 coordinate-normalized span `1000000` correctness
    passed; this is a correctness-boundary probe, not a speed claim.
- Meaning:
  Hausdorff does not currently provide formal high-performance V4 evidence.
  Do not trigger full all-app rerun from this result.
- Validation:
  `50 tests OK`.
- Next engineering need:
  reduce V4 Torch route overhead, certify a V4 CuPy continuation/front door for
  the same generic route, or select another stronger app-level target.

## Goal4669 Full App Rerun Facts To Preserve

- Goal4669 report:
  `future/v4/v4_goal4669_full_app_level_rerun_after_hausdorff_2026-06-25.md`.
- Raw POD summary:
  `future/v4/evidence/v4_goal4669_serious_20260625/summary.json`.
- Machine analysis:
  `future/v4/evidence/v4_goal4669_app_level_benchmark_analysis_2026-06-25.json`.
- Same-hardware POD:
  `root@194.68.245.170:22089`, RTX A5000.
- Decision:
  `bounded_operator_v4_only__app_level_high_performance_not_supported`.
- App-level results:
  - RTDBSCAN: V4/V2.14 hot `1.086x`, V4/V3.0.2 hot `1.083x`; modest,
    below formal bar.
  - RayDB-style: V4/V2.14 hot `0.974x`; regression vs no-regression floor.
  - Triangle counting: V4/V2.14 hot `4.055x`, V4/V3.0.2 hot `0.948x`;
    regression vs V3.0.2.
  - LibRTS spatial index: V4/V2.14 hot `1.003x`, V4/V3.0.2 hot `1.004x`;
    parity, not a V4 speed win.
  - Hausdorff XHD: V4/V2.14 primary wall `114.824x`, V4/V3.0.2 hot `2.546x`;
    true V4 app candidate win.
- Hausdorff 1M coordinate-normalized correctness probe passed:
  `coordinate_normalization_used: true`, chunk count `3`, `matches_oracle: true`.
- Meaning:
  V4 now has one true app candidate win, not a formal high-performance release.
  The next useful goal is a second independent app-level win, not release
  wording.

## Goal4670 RTDBSCAN Second-Win Diagnostic Facts To Preserve

- Goal4670 report:
  `future/v4/v4_goal4670_rt_dbscan_second_win_diagnostics_2026-06-25.md`.
- Raw POD summary:
  `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/summary.json`.
- Review debt:
  `future/v4/reviews/goal4670_completion_review_debt_no_release_authorization_2026-06-25.md`.
- Same-hardware POD:
  `root@194.68.245.170:22089`, RTX A5000.
- Decision:
  `rt_dbscan_diagnostics_complete_no_second_true_v4_win_yet`.
- True V4 candidate row:
  `v4_default_numba_signature` measured `1.079x` vs V2.14 hot and `1.076x`
  vs V3.0.2 hot in the updated diagnostic, below the `1.20x` second-win bar.
- Direct-side-effect probe:
  `1.116x` vs V2.14 hot and `1.113x` vs V3.0.2 hot, still below the bar.
- Direct-side-effect plus disabled same-root culling:
  `1.166x` vs V2.14 hot and `1.163x` vs V3.0.2 hot. This is the best true
  grouped-union probe so far, but still below the `1.20x` bar.
- Negative controls:
  no-same-root-culling regressed to `0.944x`/`0.941x`; blocked grouped-stream
  regressed to `0.326x`/`0.325x`.
- Historical/non-counting fast rows:
  measured all-true direct-status and declared all-items direct-status are
  extremely fast on the all-predicate fixture, but they are not true V4 wins.
  They are special-contract historical/external-proof-required route classes.
- Meaning:
  RTDBSCAN is not currently the second independent app-level V4 win. The only
  honest RTDBSCAN continuation is a real generic native grouped-union
  improvement; otherwise choose another app-level target. Do not count
  direct-status rows toward formal high-performance V4.

## Goal4671 RTDBSCAN No-Go Facts To Preserve

- Goal4671 report:
  `future/v4/v4_goal4671_rtdbscan_native_grouped_union_feasibility_2026-06-25.md`.
- Evidence:
  `future/v4/evidence/v4_goal4671_rtdbscan_grouped_union_telemetry_20260625/summary.json`.
- Decision label:
  `rt_dbscan_grouped_union_no_go__pivot_required_for_second_true_v4_app_win`.
- Best telemetry variant:
  `same_root_off_direct_on`.
- Best telemetry variant median native:
  `3.8223892115056515s`.
- Best telemetry counters:
  - candidate hits: `34359607296`;
  - direct side-effect hits: `34359607296`;
  - reported hits: `0`;
  - root-find invocations: `69111888446`;
  - root link steps: `70391445886`;
  - links per root find: about `1.0185`.
- Interpretation:
  path compression/root halving is not a credible 20% class generic lever on
  this shape because the parent chain is already shallow; the remaining cost is
  the candidate/root-find count imposed by the current grouped-union contract.
- Boundary:
  RTDBSCAN is a bounded modest-gain route, not formal high-performance V4
  evidence. Pivot instead of polishing it.

## Goal4672 V2.14 Primitive Audit Facts To Preserve

- Goal4672 prerequisite report:
  `future/v4/v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.md`.
- Machine evidence:
  `future/v4/evidence/v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.json`.
- Decision label:
  `v2_14_primitives_preexisting__existing_app_target_selection_requires_new_runtime_lever`.
- Key finding:
  V2.14 already had a primitive or explicit mixed partner route for all 10
  promoted benchmark apps in the current V4 set.
- Critical correction:
  `robot_collision` is not a clean second true V4 win target by default because
  V2.14 already had prepared RTDL/OptiX any-hit collision flags and scalar
  count, including device-buffer modes.
- Concrete examples:
  - `raydb_style` V2.14 already used
    `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`;
  - `triangle_counting` V2.14 already used
    `ray_triangle_weighted_any_hit_sum_3d`;
  - `librts_spatial_index` V2.14 already used `aabb_index_query_2d`;
  - `rt_dbscan` V2.14 already used OptiX count-threshold plus grouped-union and
    a CuPy component-signature continuation.
- Next-target rule:
  Existing app rows can contribute to formal high-performance V4 only if V4 has
  a generic runtime lever absent in V2.14, or if the experiment is explicitly a
  material same-primitive improvement over V2.14 under a frozen app protocol.
  Otherwise the work is productization/parity, not a V4 speed win.

## Goal4672 Target Selection Facts To Preserve

- Goal4672 report:
  `future/v4/v4_goal4672_next_target_selection_after_v2_14_audit_2026-06-25.md`.
- Machine evidence:
  `future/v4/evidence/v4_goal4672_next_target_selection_after_v2_14_audit_2026-06-25.json`.
- Decision label:
  `no_clean_existing_app_second_target_found__new_generic_runtime_lever_required`.
- Selected existing app target:
  none.
- POD run authorization:
  false.
- Why:
  all plausible existing app targets either reuse V2.14 primitives, fail current
  app-level bars, are deferred/app-identity risks, or have no current V4 route.
- Goal4673 must not start with a POD run. It must first choose/design a generic
  runtime lever or material same-primitive improvement and freeze V2.14/V3/V4
  denominators, correctness, and numeric bars.

## Goal4711 Custom-Scored App Facts To Preserve

- Goal4711 report:
  `future/v4/v4_goal4711_custom_scored_app_focused_pod_2026-06-26.md`.
- Evidence:
  `future/v4/evidence/v4_goal4711_custom_scored_app_pod_2026-06-26.json`
  and `.md`.
- Decision label:
  `fail_focused_app_gate_not_high_performance`.
- Same-hardware POD:
  `root@194.68.245.170:22089`, RTX A5000.
- Target:
  `ray_triangle_custom_scored_accumulation`.
- Denominator discovery was completed before V4 timing. V2.14 and V3.0.2 did
  not expose specialized custom-callback routes. They did expose weighted-sum
  routes, which remain control-only.
- Correct denominator used in the full run:
  `materialized_hit_id_plus_device_callback_reduce_fallback`. It traces the same
  OptiX geometry, materializes hit IDs on device, then evaluates the callback
  and reduces in a separate device kernel. It does not get V4 callback-in-hit
  fusion.
- Important mistake and repair:
  an initial smoke runner incorrectly gave fallback callback-in-hit execution by
  materializing contributions. That was fixed before the full Goal4711 run.
- Full matrix:
  24 rows, callbacks `weighted_sum` control plus primary `affine_score`,
  `threshold_score`, `minmax_score`, regimes `dense_hits`, `sparse_hits`,
  `no_hit_empty_reduction`, scales `262144` and `524288`, repeat `7`, warmup
  `2`. Correctness passed for all rows.
- Primary custom-callback performance:
  geomean V4 over V2.14 denominator `1.029x`; geomean V4 over V3.0.2
  denominator `1.029x`; minimum primary V3 speedup `1.014x`.
- Per-callback geomeans:
  `affine_score 1.033x`, `threshold_score 1.030x`, `minmax_score 1.024x`.
- Result:
  failed frozen bars (`>=1.50x` vs V2, `>=1.20x` vs V3, and `>=1.10x`
  per primary callback). Do not count Goal4711 as formal high-performance V4
  evidence. Do not trigger all-app, release wording, public Tier-3 support, or
  arbitrary/raw OptiX callback claims from this result.
- Review debt:
  `future/v4/reviews/v4_goal4711_custom_scored_app_focused_pod_review_debt_2026-06-26.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4711_custom_scored_app_focused_pod_2026-06-26.md`.
- Next engineering must pivot/reselect/redesign a runtime lever. Re-running
  Goal4711 or polishing wording is not progress unless a new mechanism changes
  the cost model.

## Goal4712 Next-Lever Facts To Preserve

- Goal4712 report:
  `future/v4/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.md`.
- Evidence:
  `future/v4/evidence/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.json`
  and `.md`.
- Decision label:
  `custom_predicate_early_exit_multi_hit_selected_protocol_required`.
- Controlling fact:
  Goal4711's post-hit custom-scored accumulation target failed with only
  `1.029x` primary geomean and `1.014x` minimum primary V3 speedup. Do not keep
  polishing that target as a formal high-performance V4 proof.
- Rejected next patterns:
  post-hit scalar accumulation polish, weighted-sum/control rows, global atomic
  scalar accumulation, and rerunning the same target without a changed cost
  model.
- Selected next target:
  `custom_predicate_early_exit_multi_hit`.
- Why:
  unlike post-hit accumulation, a predicate callback can affect traversal-side
  control flow. V4 can reject or terminate inside any-hit before materializing
  every candidate. V2/V3 fallback must materialize all hit IDs or hit attributes
  and then run a separate device predicate/filter/reduction.
- Boundary:
  user callback remains pure scalar/boolean; RTDL owns actions such as
  `terminate_on_first_accept` or `count_until_threshold`; no external mutation
  and no app-identity kernel.
- Goal4712 does not authorize POD. Next goal is Goal4713 protocol freeze.
- Review debt:
  `future/v4/reviews/v4_goal4712_next_lever_after_custom_scored_failure_review_debt_2026-06-26.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.md`.

## Goal4713 Protocol Facts To Preserve

- Goal4713 report:
  `future/v4/v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.md`.
- Evidence:
  `future/v4/evidence/v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.json`
  and `.md`.
- Decision:
  `protocol_frozen_not_run`.
- Target:
  `ray_triangle_custom_predicate_early_exit_multi_hit`.
- Primary regimes:
  `dense_early_accept_k8`, `dense_early_accept_k32`,
  `sparse_early_accept_k32`.
- Control regimes:
  `dense_late_accept_k32`, `dense_reject_all_k32`, `no_hit_empty`. These
  cannot support the primary speed claim.
- Scales:
  `65536` and `131072`.
- Frozen bars:
  primary early-accept geomean V4 over V3.0.2 `>=1.50x`; primary early-accept
  geomean V4 over V2.14 `>=1.50x`; every primary early-accept row `>=1.20x`
  over V3.0.2; controls correctness-preserving and no worse than `0.95x`
  geomean over V3.0.2.
- Critical kill:
  if V4 cannot prove early termination occurred in primary regimes, the run is
  invalid.
- Boundary:
  user callback pure boolean/scalar; RTDL owns termination/filter/count action;
  no app-identity kernel; no arbitrary/raw OptiX callback support.
- Goal4713 does not authorize POD. Next goal is Goal4714 local runner and POD
  smoke gate.
- Review debt:
  `future/v4/reviews/v4_goal4713_custom_predicate_early_exit_protocol_review_debt_2026-06-26.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.md`.

## Goal4714 Smoke Facts To Preserve

- Goal4714 report:
  `future/v4/v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.md`.
- Evidence:
  `future/v4/evidence/v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.json`
  and `.md`.
- Decision:
  `pass_smoke_gate_not_timing_not_release`.
- POD:
  `root@194.68.245.170:22089`, RTX A5000.
- Smoke ray count:
  `4096`.
- Rows:
  `dense_early_accept_k8`, `dense_early_accept_k32`, `dense_reject_all_k32`,
  `no_hit_empty`.
- Correctness:
  all rows passed.
- Early termination evidence:
  `dense_early_accept_k8` V4 any-hit invocations `4096` vs fallback
  `32768`; `dense_early_accept_k32` V4 any-hit invocations `4096` vs fallback
  `131072`. Controls behaved as expected: reject-all `131072` vs `131072`,
  no-hit `0` vs `0`.
- Meaning:
  unlike Goal4711, this route changes the cost model by reducing candidate
  work in primary regimes. This authorizes Goal4715 focused timing gate only.
- Goal4714 does not authorize release, performance claims, public Tier-3
  support, arbitrary callbacks, raw OptiX callbacks, or all-app benchmarking.
- Review debt:
  `future/v4/reviews/v4_goal4714_custom_predicate_early_exit_smoke_pod_review_debt_2026-06-26.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.md`.

## Goal4715 Timing Facts To Preserve

- Goal4715 report:
  `future/v4/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.md`.
- Evidence:
  `future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.json`
  and `.md`.
- Decision:
  `pass_focused_timing_gate_not_release`.
- POD:
  `root@194.68.245.170:22089`, RTX A5000.
- Denominator discovery:
  V2.14 and V3.0.2 tag roots had no custom predicate any-hit early-exit route.
  Selected denominator:
  `materialized_all_hit_ids_plus_device_predicate_reduce_fallback`.
- Boundary:
  the fallback traces the same OptiX geometry, materializes all hit layers to
  device, then runs predicate/reduce in separate device kernels. It does not
  receive V4 any-hit predicate early termination.
- Classification:
  primary V4/V3 geomean `3.608025018751732x`, primary V4/V2 geomean
  `3.608025018751732x`, minimum primary V4/V3 row `1.9761904761904763x`,
  control geomean `1.5585401086027044x`.
- Primary rows:
  `dense_early_accept_k8`: `1.976x` at 65,536 and `1.987x` at 131,072;
  `dense_early_accept_k32`: `6.701x` at 65,536 and `8.131x` at 131,072;
  `sparse_early_accept_k32`: `2.769x` at 65,536 and `3.724x` at 131,072.
- Correctness:
  all rows passed.
- Meaning:
  unlike Goal4711 post-hit custom scoring, this route changes the cost model
  and the timing win is real in the focused gate. This authorizes
  productization and broader app-level validation only.
- Goal4715 does not authorize release, formal high-performance wording,
  whole-app speedup wording, all-app benchmark claims, public Tier-3 support,
  arbitrary callbacks, or raw OptiX callbacks.
- Review debt:
  `future/v4/reviews/v4_goal4715_custom_predicate_early_exit_timing_pod_review_debt_2026-06-26.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.md`.

## Goal4716 Productization Facts To Preserve

- Goal4716 report:
  `future/v4/v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.md`.
- Evidence:
  `future/v4/evidence/v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.json`
  and `.md`.
- Product module:
  `src/rtdsl/v4_custom_predicate_early_exit.py`.
- Tests:
  `tests/v4_goal4716_custom_predicate_early_exit_productization_test.py`.
- Decision:
  `custom_predicate_early_exit_productized_as_measured_v4_surface_not_release`.
- New measured V4 surface:
  `v4_ray_triangle_custom_predicate_early_exit_3d_numba`.
- Generic primitive:
  `RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_3D`.
- Measured catalog surface count:
  `10`.
- Measured partner:
  `numba`.
- Accepted callback shapes:
  `pure_boolean_numba_cabi_device_function`,
  `boolean_numba_cabi_device_function`.
- RTDL-owned actions:
  `terminate_on_first_accept`, `filter_accept_flags`.
- Fail-closed boundaries:
  arbitrary Python callbacks, raw OptiX callbacks, shared mutation, dynamic
  allocation, variable-length output, app-identity kernels, and non-Numba
  partner front doors are not authorized.
- Validation:
  local focused tests `19 OK`; remote Linux/POD productization tests `10 OK`;
  evidence generation `status: passed`.
- Goal4716 does not authorize release, formal high-performance wording,
  whole-app speedup wording, all-app benchmark claims, public Tier-3 support,
  arbitrary callbacks, or raw OptiX callbacks.
- Review debt:
  `future/v4/reviews/v4_goal4716_custom_predicate_early_exit_productization_review_debt_2026-06-26.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.md`.
- Next:
  Goal4717 should broaden this measured surface into serious app/app-like
  benchmark coverage. Do not jump directly to release wording.

## Goal4717 Serious-Scale Validation Facts To Preserve

- Goal4717 report:
  `future/v4/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_2026-06-26.md`.
- Evidence:
  `future/v4/evidence/v4_goal4717_custom_predicate_early_exit_serious_scale_pod_2026-06-26.json`
  and `.md`.
- Decision:
  `custom_predicate_early_exit_serious_scale_pass_not_release`.
- POD:
  `root@194.68.245.170:22089`, RTX A5000, driver `570.195.03`.
- Scales:
  `262144` and `524288` rays, warmups `2`, repeat `5`.
- Denominator discovery:
  V2.14 and V3.0.2 tag roots had no custom predicate any-hit early-exit route.
  Selected denominator:
  `materialized_all_hit_ids_plus_device_predicate_reduce_fallback`.
- Primary serious-scale results:
  - V4/V2.14 geomean: `4.632757911153888x`;
  - V4/V3.0.2 geomean: `4.632757911153888x`;
  - minimum primary V4/V3.0.2 row: `2.054686620906942x`;
  - maximum primary V4/V3.0.2 row: `9.673329274891774x`;
  - primary row count: `6`;
  - correctness all passed.
- Control rows:
  V4/V3.0.2 control geomean `1.6303665522050805x`; these are context rows,
  not the primary public speed claim.
- Meaning:
  V4 has a real operator-pushdown performance source for constrained custom
  predicate early-exit: RTDL evaluates a Numba C-ABI predicate in the any-hit
  traversal path and owns the early-termination action, avoiding all-hit
  materialization for primary regimes.
- Goal4717 does not authorize release, formal high-performance wording,
  whole-app speedup wording, all-app benchmark claims, public Tier-3 support,
  arbitrary callbacks, raw OptiX callbacks, or non-Python embedding/C ABI
  claims.
- Review debt:
  `future/v4/reviews/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_review_debt_2026-06-26.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4717_custom_predicate_early_exit_serious_scale_validation_2026-06-26.md`.
- Next:
  Goal4718 should map this measured surface into the V4 app-level
  benchmark/release matrix and decide what public V4 claim it can support. Do
  not jump directly to a broad all-app speedup claim.

## Goal4718 Release Matrix Facts To Preserve

- Goal4718 report:
  `future/v4/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`.
- Evidence:
  `future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.json`
  and `.md`.
- Scope gate evidence:
  `future/v4/evidence/v4_0_scope_gate_current.json`.
- Decision:
  `v4_python_edsl_operator_pushdown_release_candidate_pending_docs_and_final_review`.
- Measured V4 surface count:
  `10`.
- New workflow row:
  `ray_triangle_custom_predicate_early_exit_multi_hit`.
- New API surface:
  `v4_ray_triangle_custom_predicate_early_exit_3d_numba`.
- Serious-scale speed evidence:
  - V4/V2.14 primary geomean: `4.632757911153888x`;
  - V4/V3.0.2 primary geomean: `4.632757911153888x`;
  - minimum primary V4/V3.0.2 row: `2.054686620906942x`;
  - correctness all passed.
- Release matrix interpretation:
  V4 is now a Python eDSL/operator-pushdown release candidate, but public tag
  and final release wording are still not authorized until Goal4719 docs/examples
  cleanup and final review.
- Critical boundary:
  legacy promoted-app all-suite high-performance remains unsupported by
  Goal4669. Do not claim broad all-app speedup or that all benchmark apps are
  faster.
- Validation:
  py_compile passed for Goal4718/front-door/scope files; Goal4718 evidence
  validation passed; scope gate validation passed; focused tests `30 OK`.
- Review debt:
  `future/v4/reviews/v4_goal4718_release_matrix_after_custom_predicate_review_debt_2026-06-26.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`.
- Next:
  Goal4719 public docs, tutorials, examples, and release wording cleanup. Do
  not tag before user-facing docs/examples are consistent and tested.

## Goal4719 Public Docs/Examples Facts To Preserve

- Goal4719 report:
  `future/v4/v4_goal4719_public_docs_examples_release_candidate_cleanup_2026-06-26.md`.
- New runnable example:
  `examples/v4/custom_predicate_early_exit_planning.py`.
- Public docs updated:
  `README.md`, `docs/current_v4_status.md`,
  `docs/app_level_benchmark_summary.md`, `docs/learn/performance_wording.md`,
  `examples/README.md`, `tutorials/current/05_measurement_boundaries.md`,
  `future/v4/README.md`, and `future/v4/tier2_operator_catalog.md`.
- Decision:
  `public_v4_docs_examples_match_goal4718_release_candidate_boundary`.
- Public docs now lead with:
  V4 is a Python eDSL/operator-pushdown release candidate with `10` measured
  generic operator/workflow surfaces; custom predicate early-exit is the
  current V4-only workflow win; broad legacy all-app speedup remains false.
- Validation:
  public docs/examples tests `21 OK`; current public user-path stale-string
  scan found no old 9-surface/bounded-only/Goal4654 wording matches.
- Review debt:
  `future/v4/reviews/v4_goal4719_public_docs_examples_release_candidate_cleanup_review_debt_2026-06-26.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4719_public_docs_examples_release_candidate_cleanup_2026-06-26.md`.
- Next:
  Goal4720 final V4 release decision packet, machine release gate update, and
  broad local validation.

## Goal4720 Release-Candidate Machine-Gate Facts To Preserve

- Goal4720 report:
  `future/v4/v4_goal4720_release_candidate_guardrail_convergence_2026-06-26.md`.
- Catalog regression gate evidence:
  `future/v4/evidence/v4_goal4720_catalog_regression_gate_dry_run_2026-06-26.json`
  and `.md`.
- Reviewer packet:
  `future/v4/reviews/call_for_review_v4_goal4720_release_candidate_guardrail_convergence_2026-06-26.md`.
- Review debt:
  `future/v4/reviews/v4_goal4720_release_candidate_guardrail_convergence_review_debt_2026-06-26.md`.
- Machine state converged:
  front door, scope gate, catalog, release-decision module, examples, public
  docs, and tests all agree on `10` measured surfaces and `0` candidates.
- Validation:
  - targeted release-state tests: `34 OK`;
  - full V4 local suite: `435 OK`;
  - catalog regression dry-run: `passed`;
  - compile check: passed.
- Decision:
  V4 is a Python eDSL/operator-pushdown release candidate, not a broad legacy
  all-app speedup release and not a final public tag until external review debt
  is closed.
- Next:
  Goal4721 external review packet/debt closure, Goal4722 clean-tree/release
  packaging gate, Goal4723 final tag decision after review.

## Goal4722 Package Gate Facts To Preserve

- Goal4722 report:
  `future/v4/v4_goal4722_clean_package_release_gate_2026-06-26.md`.
- Review packet:
  `future/v4/reviews/call_for_review_v4_goal4722_clean_package_release_gate_2026-06-26.md`.
- Review debt:
  `future/v4/reviews/v4_goal4722_clean_package_release_gate_review_debt_2026-06-26.md`.
- Public no-CUDA examples passed:
  quickstart, callback planner tier2/scalar/complex, and custom predicate
  early-exit planning.
- Current public-path stale wording scan found no matches for old 8/9-surface
  or near-OptiX/geomean-headline phrases.
- Broad scan over all `future/v4` still finds old wording in historical
  goal/review/design artifacts; do not rewrite historical evidence records.
- Local Python packaging tools were incomplete; `py -m ensurepip --upgrade`
  installed pip/setuptools, then wheel build passed. The temporary
  `scripts/pip*.exe` and `Lib/site-packages` ensurepip artifacts were removed
  from the workspace afterward.
- Wheel artifact:
  `dist/goal4722_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`.
- Antigravity review attempt for Goals4720-4722 returned empty stdout/stderr
  even for a READY probe:
  `future/v4/reviews/antigravity_v4_goal4720_4722_release_candidate_review_empty_output_2026-06-26.md`.
- This is not final tag authorization. External review debt remains open.

## Review Rules

- Each goal completion needs 3-AI consensus or explicitly recorded review debt
  if an external reviewer is unavailable.
- Claude weekly limit and Antigravity empty output are debt, not approval.
- Do not spawn internal reviewer agents to fill consensus. That creates
  self-comforting pseudo-review, not external audit.
- When Claude/Antigravity are unavailable, record debt and continue with the
  concrete engineering goal unless the user explicitly requires a stop.
- Final release authorization must still follow the relevant final protocol.

## V4 Claim Locks

Always preserve:

- partner migration is not a V4 speed win;
- partner parity is not a V4 speed win;
- CuPy certification is surface-specific, not a blanket CuPy performance claim;
- fixed Numba certification is not arbitrary callback support;
- Tier-3 Numba/PTX is spike-only unless a later goal explicitly proves it;
- no whole-app speed claim before Goal4654/4655;
- no C ABI, embedding, true-zero-copy, non-Python host, or app-identity kernel
  claims in V4.0.

## RT-BarnesHut Author-Reproduction Facts To Preserve

- Audit report:
  `future/v4/rt_barneshut_author_reproduction_audit_2026-06-26.md`.
- Past RTDL Barnes-Hut code is not a full RT-BarnesHut paper reproduction.
  The benchmark app explicitly says `paper_reproduction: False` and
  `authors_code_comparison: False`.
- Authors' source was found and cloned:
  `https://github.com/vani-nag/OWLRayTracing`, branch `BarnesHutRT`, commit
  `2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7`.
- Authors' artifact was built and run on the NVIDIA POD at
  `/root/external/RT-BarnesHut-author` with OptiX 8 headers.
- Minimal compatibility-only author patches were used:
  add `<array>` for modern CUDA/GCC and change hard-coded GPU id `1` to `0`
  for the single-GPU POD. No algorithm/timing/force-law change.
- Author POD evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/`.
- Author runs completed:
  - Treelogy 1M: execution `0.639937s`, RT force `0.136s`.
  - Treelogy 10M: execution `3.08818s`, RT force `1.01835s`.
  - synthetic25M CSV: execution `4.57178s`, RT force `2.40888s`.
- Current RTDL V2/V3/V4 Barnes-Hut-style route is only fair within the RTDL
  2D aggregate-frontier weighted-vector contract. It is not fair to divide it
  against the authors' 3D RT-BarnesHut program.
- Goal4760 added the first same-semantics gate:
  `src/rtdsl/rt_barneshut_author_contract.py`,
  `scripts/rt_barneshut_author_contract_probe.py`, and
  `tests/v4_goal4760_rt_barneshut_author_contract_test.py`.
  It loads author treelogy/csv data, applies the author CSV scaling, builds an
  author-compatible 3D bucket-tree CPU oracle, parses author binary timings,
  and emits non-speed probe evidence.
- Goal4760 POD evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/rtdl_author_contract_4096.json`
  and `rtdl_author_contract_8192.json`; local and POD tests both passed
  `5 OK`.
- Goal4760 checksum validation:
  `tools/rtbarneshut_author_force_checksum_audit.patch` adds read-only RT
  force checksum output to the authors' binary. It does not change traversal,
  force computation, timing regions, or data semantics. On trimmed Treelogy
  probes, author RT checksum matched the RTDL CPU oracle:
  4096 relative error `1.933403535816373e-06`; 8192 relative error
  `2.450123881979025e-07`.
- Goal4760 is not the V4 RT-core performance route. It is only the author
  input/tree/force semantic gate. The route matrix is:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/rtdl_rt_barneshut_same_semantics_route_matrix_2026-06-26.json`.
- Goal4760 review debt:
  `future/v4/reviews/v4_goal4760_rt_barneshut_author_contract_gate_review_debt_2026-06-26.md`.
- Goal4761 added a V4-controlled same-semantics external author RT-core
  reference route:
  `src/rtdsl/v4_rt_barneshut_author_route.py`,
  `scripts/v4_rt_barneshut_author_route_probe.py`, and
  `tests/v4_goal4761_rt_barneshut_author_route_test.py`.
  Local tests passed `3 OK`; POD tests passed `3 OK`.
- Goal4761 POD evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_rt_barneshut_author_route_4096.json`
  and `v4_rt_barneshut_author_route_8192.json`.
  These rows execute the authors' RT-core binary on the Goal4760 same-input
  contract and validate checksum parity, but `native_v4_operator=false`.
- Goal4761 review debt:
  `future/v4/reviews/v4_goal4761_rt_barneshut_external_author_rt_core_route_review_debt_2026-06-26.md`.
- Goal4762 added a fail-closed native V4 feasibility gate:
  `src/rtdsl/v4_rt_barneshut_native_route.py`,
  `scripts/v4_rt_barneshut_native_feasibility_probe.py`, and
  `tests/v4_goal4762_rt_barneshut_native_feasibility_test.py`.
  Local and POD tests for Goals 4760/4761/4762 passed `11 OK`.
- Goal4762 evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4762_rt_barneshut_native_feasibility_2026-06-26.json`
  and
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4762_rt_barneshut_native_feasibility_pod_2026-06-26.json`.
- Goal4762 result:
  status `blocked_missing_native_3d_author_semantics_rt_core_route`.
  The existing 2D aggregate-tree fused symbols are present, but the native
  author-route symbols are missing:
  `rtdl_optix_prepare_rt_barneshut_author_3d`,
  `rtdl_optix_run_rt_barneshut_author_3d`, and
  `rtdl_optix_destroy_rt_barneshut_author_3d`.
- Never treat `aggregate_tree_fused_weighted_vector_sum_2d` as author-equivalent
  RT-BarnesHut. The required next engineering step is Goal4763: implement the
  native 3D author-semantics ABI/route and pass Goal4760 checksum parity on
  4096/8192 rows before any 1M/10M performance table.
- Goal4762 review debt:
  `future/v4/reviews/v4_goal4762_rt_barneshut_native_feasibility_gate_review_debt_2026-06-26.md`.
- Goal4763 moved the RT-BarnesHut author route one step into native code:
  `src/native/optix/rtdl_optix_prelude.h` declares
  `RtdlRtBarnesHutAuthor3DOutput` plus
  `rtdl_optix_prepare_rt_barneshut_author_3d`,
  `rtdl_optix_run_rt_barneshut_author_3d`, and
  `rtdl_optix_destroy_rt_barneshut_author_3d`.
  `src/native/optix/rtdl_optix_api.cpp` implements the ABI first slice.
- Goal4763 POD build succeeded:
  `make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0 CUDA_PREFIX=/usr/local/cuda`.
  POD tests for 4762/4763 passed `7 OK`, including dynamic export checks
  against `/root/rtdl_v4_candidate_pod/build/librtdl_optix.so`.
- Goal4763 evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4763_rt_barneshut_native_abi_first_slice_2026-06-26.json`
  and
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4763_rt_barneshut_native_abi_first_slice_pod_2026-06-26.json`.
  The POD JSON has `missing_exported_symbols=[]` for all three native ABI
  symbols.
- Critical Goal4763 claim boundary:
  `native_v4_abi_symbols_available=true` but
  `native_v4_operator_available=false`. Do not collapse these. The run path is
  intentionally fail-closed until the OptiX traversal/force kernel is
  implemented and checksum-validated.
- Goal4763 review debt:
  `future/v4/reviews/v4_goal4763_rt_barneshut_native_abi_first_slice_review_debt_2026-06-26.md`.
- Goal4764 implemented the first runnable native ABI checksum route behind
  `rtdl_optix_run_rt_barneshut_author_3d`, but it is explicitly a host fallback,
  not an RT-core/native V4 performance operator:
  `src/native/optix/rtdl_optix_api.cpp` now downloads the author-format device
  columns, runs author-compatible 3D z-order / bucket-size-32 Barnes-Hut tree /
  theta=0.5 force law on host, uploads force output back to a native-owned CUDA
  device buffer, and returns it through `RtdlRtBarnesHutAuthor3DOutput`.
- Goal4764 POD tests passed:
  `tests.v4_goal4762_rt_barneshut_native_feasibility_test`,
  `tests.v4_goal4763_rt_barneshut_native_abi_first_slice_test`, and
  `tests.v4_goal4764_rt_barneshut_native_fallback_route_test` all passed
  `12 OK` against `/root/rtdl_v4_candidate_pod/build/librtdl_optix.so`.
- Goal4764 checksum evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4764_rt_barneshut_native_fallback_4096_pod_2026-06-26.json`
  and
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4764_rt_barneshut_native_fallback_8192_pod_2026-06-26.json`.
  Both have status `native_3d_author_semantics_host_fallback_available` and
  `passes_float_output_tolerance=true`; relative checksum errors are
  `2.9873327390354115e-15` and `1.7966991826615097e-14`.
- Critical Goal4764 claim boundary:
  `native_v4_abi_symbols_available=true`,
  `native_v4_checksum_route_available=true`,
  `host_fallback_used=true`, but `native_v4_operator_available=false` and
  `rt_core_execution=false`. Do not collapse these. The timing fields are
  fallback timings, not RT-core timings.
- Goal4764 report:
  `future/v4/v4_goal4764_rt_barneshut_native_fallback_checksum_route_2026-06-26.md`.
- Goal4764 review debt:
  `future/v4/reviews/v4_goal4764_rt_barneshut_native_fallback_checksum_route_review_debt_2026-06-26.md`.
- Next required RT-BarnesHut engineering step is Goal4765:
  replace the Goal4764 host fallback with author-compatible OptiX traversal and
  force evaluation behind the same ABI, while keeping the 4096/8192 checksum
  parity probes as regression gates. No 1M/10M scale timing table before the
  RT-core route passes those small checksum gates.
- Goal4765 completed that replacement as an engineering candidate:
  `src/native/optix/rtdl_optix_api.cpp` now has an author-compatible 3D OptiX
  custom-primitive RT-core candidate behind
  `rtdl_optix_run_rt_barneshut_author_3d`; the old Goal4764 host fallback is
  only used when `RTDL_RT_BARNESHUT_AUTHOR_FORCE_FALLBACK=1`.
- Goal4765 POD build and tests passed on the RTX A5000. POD tests:
  `tests.v4_goal4762_rt_barneshut_native_feasibility_test`,
  `tests.v4_goal4763_rt_barneshut_native_abi_first_slice_test`,
  `tests.v4_goal4764_rt_barneshut_native_fallback_route_test`, and
  `tests.v4_goal4765_rt_barneshut_native_rt_core_candidate_test` passed
  `16 OK`.
- Goal4765 checksum evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_rt_core_candidate_4096_pod_2026-06-26.json`
  and
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_rt_core_candidate_8192_pod_2026-06-26.json`.
  Both have status `native_3d_author_semantics_rt_core_candidate_available`,
  `implementation_status_code=3`, `host_fallback_used=false`,
  `rt_core_execution=true`, and `passes_float_output_tolerance=true`.
  Relative checksum errors are `1.1367656829416352e-13` and
  `2.0096898862946577e-13`.
- Goal4765 warm-run evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_rt_core_candidate_warm_repeat_8192_pod_2026-06-26.json`.
  First run in a process includes OptiX/NVRTC pipeline initialization
  (`rt_force_seconds=0.782372891`); second run reuses the loaded pipeline
  (`rt_force_seconds=0.001561678`). Do not present cold initialization as the
  warmed hot path, and do not present the warm path as a public paper speedup.
- Critical Goal4765 claim boundary:
  the route is a checksum-valid native RT-core candidate, but
  `input_columns_downloaded_for_tree_build=true`. This is not a no-copy or
  device-resident tree-build claim. Public RT-BarnesHut paper-reproduction
  wording, V2/V3/V4 author speed tables, and broad V4 speedup claims remain
  unauthorized pending scale/performance gates and external review.
- Goal4765 report:
  `future/v4/v4_goal4765_rt_barneshut_native_rt_core_candidate_2026-06-26.md`.
- Goal4765 review debt:
  `future/v4/reviews/v4_goal4765_rt_barneshut_native_rt_core_candidate_review_debt_2026-06-26.md`.
- Next RT-BarnesHut engineering step is Goal4766:
  make the route benchmark-ready by splitting cold init from warm execution in
  the formal probe, adding 32768 and 1M scale gates, and only then comparing
  against the authors' binary on the same POD/dataset.
- Goal4766 completed benchmark-readiness scale gates:
  `scripts/v4_rt_barneshut_native_benchmark_ready_probe.py` runs repeated
  same-process native candidate calls, separates cold/warm timing, and can run
  the authors' `rtbarneshut` binary on a trimmed same-input dataset without
  invoking the 1M CPU oracle.
- Goal4766 validation:
  local `tests.v4_goal4766_rt_barneshut_benchmark_ready_probe_test` passed
  `2 OK`; POD test passed `2 OK`.
- Goal4766 evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4766_benchmark_ready_32768_pod_2026-06-26.json`
  and
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4766_benchmark_ready_1m_pod_2026-06-26.json`.
- Goal4766 32768 facts:
  native warm RT-force median `0.006929028s`; authors' binary RT-force
  `0.05993s`; checksum relative error vs author RT checksum
  `6.440149235295914e-10`; all native runs status code `3`,
  `rt_core_execution=true`, `host_fallback_used=false`.
- Goal4766 1M facts:
  native warm RT-force median `0.090850561s`; authors' binary RT-force
  `0.094797s`; native warm execution median `0.7451439795s`; authors' binary
  execution `1.04442s`; checksum relative error vs author RT checksum
  `1.2294599449624855e-7`; all native runs status code `3`,
  `rt_core_execution=true`, `host_fallback_used=false`.
- Critical Goal4766 claim boundary:
  this is benchmark-readiness evidence, not public release authorization.
  Do not claim no-copy tree build: `input_columns_downloaded_for_tree_build`
  remains true. Do not publish V2/V3/V4 RT-BarnesHut speed tables or paper
  reproduction wording until external review decides whether the
  custom-primitive control geometry is acceptable or literal triangle geometry
  is required.
- Goal4766 report:
  `future/v4/v4_goal4766_rt_barneshut_benchmark_ready_scale_gate_2026-06-26.md`.
- Goal4766 review debt:
  `future/v4/reviews/v4_goal4766_rt_barneshut_benchmark_ready_scale_gate_review_debt_2026-06-26.md`.
- Next RT-BarnesHut options for Goal4767:
  run/defer a 10M Treelogy gate, ask reviewers whether custom-primitive control
  geometry is acceptable, or implement literal triangle geometry before any
  paper-facing wording.
- Goal4767 completed the 10M Treelogy gate on the RTX A5000 POD:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4767_benchmark_ready_10m_pod_2026-06-26.json`.
  Dataset: `/root/external/RT-BarnesHut-author/treelogy_synthetic_10M.txt`;
  author binary: `/root/external/RT-BarnesHut-author/build/rtbarneshut`.
- Goal4767 10M correctness:
  native force checksum `53.746751351154444`; author RT checksum `53.7468`;
  relative error `9.051486889720442e-7`; tolerance pass true.
- Goal4767 10M timing:
  native warm RT-force `0.906343331s`; author RT-force `1.01614s`.
  This is a real RT-force candidate success. However native warm full execution
  `7.130341762s` is much slower than author execution `1.61694s` because native
  preprocessing/tree build is `6.179594029s` versus author preprocessing
  `0.520493s`.
- Critical Goal4767 interpretation:
  do not claim RT-BarnesHut public speedup from the RT-force number alone. The
  route's force kernel is competitive at 10M, but the complete workflow is
  blocked by preprocessing/tree construction and still has
  `input_columns_downloaded_for_tree_build=true`.
- Goal4767 report:
  `future/v4/v4_goal4767_rt_barneshut_10m_scale_gate_2026-06-26.md`.
- Goal4767 review debt:
  `future/v4/reviews/v4_goal4767_rt_barneshut_10m_scale_gate_review_debt_2026-06-26.md`.
- Next RT-BarnesHut engineering target is Goal4768:
  attack preprocessing/tree-build cost before any paper-facing wording. Options
  are optimizing the current host preprocessing, moving metadata construction
  toward device-resident staging, or porting the authors' preprocessing more
  literally.
- Goal4768 completed the focused 10M preprocessing/profile pass:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_benchmark_ready_10m_pod_2026-06-26.json`
  and
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_10m_phase_profile_pod_2026-06-26.jsonl`.
- Goal4768 correctness still passes:
  native checksum `53.746751351154444`, author RT checksum `53.7468`,
  relative error `9.051486889720442e-7`.
- Goal4768 timing:
  native warm RT-force `0.886653679s`; author RT-force `1.0172s`;
  native warm execution `7.432850354s`; author execution `1.68573s`.
- Goal4768 corrected a Goal4767 accounting mistake:
  the authors' printed `Preprocessing Time` excludes sort/tree-build time and
  is not directly comparable to RTDL's `preprocessing_seconds`.
- Goal4768 phase profile localized the dominant native 10M bottleneck to
  host z-order sort:
  warm `sort_seconds=6.16351s`, while `dfs_metadata_seconds=0.0150561s`,
  `auto_rope_seconds=0.0111561s`, `accel_build_seconds=0.00803325s`, and
  `launch_seconds=0.647495s`.
- Goal4768 report:
  `future/v4/v4_goal4768_rt_barneshut_preprocessing_sort_bottleneck_2026-06-26.md`.
- Goal4768 review debt:
  `future/v4/reviews/v4_goal4768_rt_barneshut_preprocessing_sort_bottleneck_review_debt_2026-06-26.md`.
- Next RT-BarnesHut engineering target is Goal4769:
  either produce apples-to-apples author phase accounting by rebuilding or
  instrumenting the author path, or reduce RTDL 10M z-order sort cost with a
  checksum-preserving sort-key/data-layout improvement.
- Goal4769 completed the apples-to-apples author phase accounting path:
  the author source was temporarily rebuilt with `PRINT_ARTIFACT=false`, run on
  the same 10M Treelogy input, then restored to `PRINT_ARTIFACT=true` and
  rebuilt.
- Goal4769 author full phase evidence:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stdout.txt`
  and
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stderr.txt`.
- Goal4769 key author phases:
  sort `6.87096s`, tree build `1.71362s`, tree to DFS `0.043701s`,
  install autoropes `0.015301s`, intersections setup `0.484204s`,
  RT-force `1.12905s`, iterative step `1.76213s`, total program `10.4391s`.
- Goal4769 corrected the Barnes-Hut interpretation:
  the previous author artifact-mode `Execution time` excludes sort/tree build
  and must not be used as the full-workflow denominator. RTDL Goal4768 warm
  execution `7.432850354s` plus input download `0.0804588s` is about `7.51s`,
  faster than the author full internal `Total Program time=10.4391s` on the
  same 10M input. RTDL sort `6.16351s` is also faster than author sort
  `6.87096s`.
- Goal4769 report:
  `future/v4/v4_goal4769_rt_barneshut_author_phase_accounting_2026-06-26.md`.
- Goal4769 review debt:
  `future/v4/reviews/v4_goal4769_rt_barneshut_author_phase_accounting_review_debt_2026-06-26.md`.
- Next RT-BarnesHut/V4 release-target step is Goal4770:
  update the app matrix/release packet so Barnes-Hut is no longer described as
  a full-workflow author loss. Keep public paper-reproduction wording,
  no-copy/device-resident tree-build wording, and broad V4 release wording
  blocked until external review.
- Goal4770 completed the release-packet delta:
  `future/v4/v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.md`
  and
  `future/v4/evidence/v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.json`.
- Goal4770 policy:
  do not rewrite historical Goal4756 matrix rows; treat Goal4770 as a delta
  correcting Barnes-Hut interpretation after Goal4769 author phase accounting.
- Goal4770 current Barnes-Hut reading:
  the historical matrix keeps the aggregate-frontier row as a material
  V3/V4-over-V2.14 candidate, not a new V4-over-V3 win. Separately, the native
  RT-BarnesHut author-semantics route is checksum-valid at 10M and wins on
  comparable internal program time versus the authors' binary once sort/tree
  phases are exposed.
- Goal4770 still blocks:
  public RT-BarnesHut paper reproduction, no-copy tree-build wording,
  V2/V3/V4 public RT-BarnesHut speed table, and public V4 tag.
- Goal4770 review debt:
  `future/v4/reviews/v4_goal4770_rt_barneshut_release_packet_delta_review_debt_2026-06-26.md`.
- Goal4771 completed the local release-surface validation after Goal4770:
  `py -m unittest discover -s tests -p "v4*_test.py"` ran `632` tests in
  `83.046s` and passed `OK (skipped=1)`.
- Goal4771 report:
  `future/v4/v4_goal4771_full_v4_gate_after_barnes_hut_delta_2026-06-26.md`.
- Goal4771 evidence log:
  `future/v4/evidence/v4_goal4771_full_v4_unittest_discover_after_goal4770_2026-06-26.log`.
- Goal4771 review debt:
  `future/v4/reviews/v4_goal4771_full_v4_gate_after_barnes_hut_delta_review_debt_2026-06-26.md`.
- Goal4771 important fix:
  Goal4759 manifest script now indexes the five Goal4769/4770 Barnes-Hut delta
  artifacts, and Goal4758 local audit expects `artifact_count=27` plus those
  exact delta IDs.
- Do not claim RTDL reproduces the RT-BarnesHut paper until there is a
  same-input, same-semantics RTDL route for the authors' datasets and phase
  split, followed by V2.14/V3.0.2/V4.0 plus authors-binary comparison.
- Goal4772 completed that first fair RT-BarnesHut four-way audit for the
  10M Treelogy input:
  `future/v4/v4_goal4772_rt_barneshut_four_way_fair_compare_2026-06-26.md`
  and
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4772_four_way_fair_compare_pod_2026-06-26.json`.
- Goal4772 result:
  V4 has the same-semantics native author RT-core route and passes checksum
  (`relative_error=9.051486889720442e-7`). V2.14 and V3.0.2 have legacy
  Barnes-Hut adapters but do not expose the Goal4760 author-semantics contract
  or native author ABI symbols, so their fair result is explicit route absence,
  not `n/a` and not a timing ratio.
- Goal4772 valid Author-vs-V4 ratios:
  full internal program `1.3894144092875964x`, RT-force `1.27338331384739x`,
  sort `1.1147803767658364x`, and author sort+tree vs V4 preprocessing
  `1.3200831129438122x`.
- Goal4772 still blocks:
  public paper-reproduction wording, public V2/V3/V4 RT-BarnesHut speed table,
  broad V4 speedup wording, public V4 tag, and no-copy/device-resident
  tree-build claims.
- If the user asks for a true V2.14/V3.0.2 timing ratio under this exact
  RT-BarnesHut contract, do not fake it. The required engineering work is to
  implement or backport the Goal4760 author-semantics route into those versions,
  or to run a separate legacy-contract comparison with its own denominator.
- RayJoin line classification as of 2026-06-27:
  see
  `future/v4/v4_rayjoin_benchmark_vs_paper_reproduction_classification_2026-06-27.md`.
  RayJoin as a project family is both benchmark-app work and
  paper-reproduction work, but not through one single current app surface.
  `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
  is the current benchmark app and repeatedly blocks
  `full_rayjoin_reproduction` / `rtdl_beats_rayjoin` claims. The separate
  paper-reproduction suite is `src/rtdsl/rayjoin_paper_suite.py` plus
  `scripts/rayjoin_paper_reproduction_suite.py`, with v2.x-era bounded and
  same-query-stream evidence in history. Do not silently treat the current V4
  10-app Spatial RayJoin row as the RayJoin paper-reproduction app.

## Agent Self-Check Before Major Decisions

Before a goal-level decision, answer briefly in the goal artifact:

1. Was I being stupid?
2. If yes, what action made it stupid?
3. Is there another path that avoids getting stuck on a bad premise?
4. Can I now try the different path that actually solves the problem?

If the next action is mostly tool retry, process paperwork, or another review
wrapper, ask whether it moves the current goal's concrete exit evidence. If not,
stop and do the concrete goal work.
