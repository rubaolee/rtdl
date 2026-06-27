I now have everything I need. Here is the full review.

---

## Goal2653 RayDB Paper-Shaped RT Benchmark Closeout — Review

### Criterion 1: Forbidden claims

**Result: Pass.**

All seven forbidden categories are explicitly called out in the closeout, the catalog boundary column, the README, the perf-script `claim_boundary` fields, and the in-app `engine_boundary`/`claim_boundary` strings. Specific checks:

- **Whole-app speedup**: blocked in closeout §Claim Boundaries, catalog boundary column ("no whole-app … claim"), README ("not a whole-app speedup claim"), and Goal2652 §Fairness Boundary.
- **Public speedup**: blocked at the top of every report ("public speedup wording remains unauthorized until the normal external-review gate explicitly accepts the exact claim text").
- **Authors-code comparison**: explicitly not authorized. `authors_code_comparison: False` is emitted in every result path of the benchmark app.
- **DBMS / SQL / Crystal / PostgreSQL / DuckDB / cuDF comparison**: explicitly listed as unauthorized in the closeout.
- **SSB paper reproduction**: explicitly listed as unauthorized.
- **Package-install support**: explicitly listed as unauthorized.
- **True zero-copy**: explicitly listed as unauthorized; `true_zero_copy_authorized: False` is emitted in the partner-resident experimental path.
- **Torch/CuPy as the fair comparison row**: the closeout correctly separates `optix_torch` into a distinct line and designates `embree_host` vs `optix_host` as the RT-vs-Embree claim row.

No violations found.

---

### Criterion 2: Internal performance statement accurately bounded

**Result: Pass with one noted discrepancy (non-blocking).**

The allowed statement in §Performance Evidence:

> "steady-state prepared OptiX RT queries are 27.7x faster than prepared Embree queries for grouped count and 104.0x faster for grouped sum on the RTX A5000 pod"

All six boundary elements are satisfied:

| Boundary element | Evidence |
|---|---|
| Generated 2M RayDB-style fixture | Goal2652 args: `--fixture-kind generated --generated-rows 2000000 --generated-groups 128 --generated-revenue-mod 64` |
| Steady-state prepared-query phase only | Duration-driven protocol; table descriptor, workload build, scene/GAS build, payload prep, and ray-batch prep are all *outside* the timed loop |
| Same app-owned lowering | Both `embree_host` and `optix_host` pass through `_make_paper_rt_encoded_packed_workload()` + same `prepare_paper_rt_encoded_table_descriptor()` |
| Same generic grouped ray/triangle reduction | `prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d()` on both backends |
| RTX A5000 pod | Driver `565.57.01`, pod `root@194.68.245.16 -p 22072` |
| Embree host vs OptiX host | `ray_batch_mode=host` for both; Torch row excluded from the claim |

**Arithmetic check:**
- Count: 4.7154 ms / 0.1704 ms = **27.67x** — reported as 27.7x ✓
- Sum: 98.5329 ms / 0.9476 ms = **104.00x** — reported as 104.0x ✓

**Non-blocking discrepancy — Goal2651 vs Goal2652 sum speedup:**
Goal2651 (single-run median, after table descriptor) reports OptiX vs Embree sum as **91.2x** (0.096972s / 0.001064s). Goal2652 (10s duration, 10,499 OptiX iterations) reports **104.0x** (98.5329ms / 0.9476ms). That is a 14% difference on the key sum number. This is likely legitimate run-to-run variance on the shared pod between two separate measurement sessions, and Goal2652's multi-thousand-iteration protocol is statistically more reliable. However, the two reports are both in the repo and any external reviewer will notice this discrepancy. The closeout should acknowledge that Goal2652 supersedes Goal2651 as the designated closeout measurement and that the difference is within expected single-pod variance, not a contradiction.

---

### Criterion 3: Native engines remain app-agnostic

**Result: Pass.**

- `grep` across all files in `src/native/` for `raydb`, `RayDB`, `SSB`, `sql`, `SQL`, `database`, `table`, `query_plan` returns **zero matches** in the Embree scene, OptiX workloads, OptiX core, and OptiX API files. (The `stable_sort` / `table` hits in HipRT were `hiprtFuncTable` — unrelated C++ API struct, not a semantic match.)
- The `grouped_sum` string found in `rtdl_embree_scene.cpp:1147` is part of the *columnar payload* path (old Goal2520 path), not the paper-shaped path. The paper-shaped path uses `rtdl_embree_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction` — a generic name with no domain vocabulary.
- `generic_primitives.py` uses the app-agnostic symbol `generic_ray_triangle_primitive_grouped_i64_reduction_3d` throughout.
- The benchmark app's `engine_boundary` and `claim_boundary` strings confirm the contract: "Python owns RayDB query encoding and result interpretation. Native execution uses a generic ray/triangle primitive-id grouped i64 reduction with no RayDB, SQL, table, SSB, or database vocabulary."
- `prepare_paper_rt_encoded_table_descriptor()` is marked `app_owned_descriptor: True` and its `engine_boundary` string explicitly states the RTDL native layer sees only "generic typed rays, triangles, group ids, payload values, and reductions."

---

### Criterion 4: Docs/catalog consistency after replacing old partner-resident rows

**Result: Mostly pass, with two non-blocking clarity issues.**

**What's correct:**
- The catalog now has two RayDB rows (count: 27.7x, sum: 104x) sourced from Goal2652, with boundary columns that correctly exclude setup phases and prohibit SQL/DBMS/authors-code/whole-app claims.
- The old single partner-resident row is gone from the catalog's promoted benchmark table.
- The catalog footnote correctly notes 10 promoted apps, with RayDB counting as two rows.

**Non-blocking issue A — README mixes two incompatible measurement protocols without calling it out:**
The README §Current RT-Core Evidence presents both:
1. The old 1.427x/1.386x numbers ("The first same-contract full prepared-run comparison") — these include workload build (~0.5-0.9s) and scene/payload preparation (~0.1-0.5s), measured as a single full run with no steady-state repetition.
2. The current 27.7x/104.0x from Goal2652 — prepared-query-only, 10s steady state.

A reader who does not already know the protocol will not understand why the same 2M-row fixture can show 1.4x in one paragraph and 27.7x three paragraphs later. The README should add a one-line note clarifying that the 1.427x/1.386x are **whole-run** timings (setup included, single iteration) while the 27.7x/104.0x are **prepared-query-only** timings (setup excluded).

**Non-blocking issue B — Old Goal2527/2528 fused-stats numbers retained without backend disambiguation:**
The README still contains the Goal2527/2528 evidence: "the fused full-contract medians were 1.601686ms, 1.986026ms, and 2.425149ms for 1M, 5M, and 10M rows." These come from the **old** `optix_partner_resident_experimental` backend (columnar payload, fused sum/count, partner-resident CUDA tensors) — a completely different backend and primitive from the current `paper_rt_optix` path. Both produce correct grouped aggregates but via very different lowering strategies. The README does not say "this was the old partner-resident backend, not the current paper-shaped path." An external reader comparing 0.17ms (Goal2652, 2M rows, count only) to 1.6ms (Goal2528, 1M rows, fused count+sum+min+max) without context could draw wrong conclusions. A one-line clarification is needed.

**Minor cosmetic issue:** The catalog uses `104x` while the closeout and Goal2652 use `104.0x`. Trivially inconsistent precision; harmless.

---

### Summary: Blocking vs Non-Blocking Issues

**Blocking issues: None.**

**Non-blocking issues:**

1. **Goal2651 vs Goal2652 sum speedup discrepancy (91.2x vs 104.0x, 14%).** The closeout does not acknowledge that Goal2651 reports a substantially different sum speedup. Add one sentence designating Goal2652 as superseding and attributing the gap to different protocols and pod state at measurement time.

2. **README mixes whole-run and prepared-query-only protocols without labeling them.** The 1.427x/1.386x numbers need a parenthetical "(whole-run including setup, single iteration)" to prevent confused comparison with the 27.7x/104.0x steady-state numbers.

3. **README retains Goal2527/2528 fused-stats numbers without tagging them as the old partner-resident backend.** Add a one-line note: "These are from the old `optix_partner_resident_experimental` columnar payload path (Goal2527/2528), not the current paper-shaped `paper_rt_optix` path."

---

### Final Verdict: **Accept with fixes**

The claim discipline is sound. All forbidden categories are explicitly blocked. The 27.7x count and 104.0x sum prepared-query numbers are arithmetically correct and correctly bounded to the six required constraints. The native engines are demonstrably app-agnostic. The catalog is consistent with the Goal2652 evidence.

**The one claim that is acceptable as written:**

> For the generated 2M-row RayDB-style fixture, using the same app-owned paper-shaped lowering and the same generic RTDL grouped ray/triangle reduction contract, steady-state prepared OptiX RT queries on the RTX A5000 pod are **27.7x faster** than prepared Embree queries for grouped count and **104.0x faster** for grouped sum. This measures the prepared-query phase only; table descriptor construction, workload buffer build, scene/GAS build, payload preparation, and ray-batch preparation are excluded from this timing.

**What remains forbidden even after this accept:**
- Any claim comparing these numbers to PostgreSQL, DuckDB, cuDF, Crystal, or any DBMS query time.
- Any claim comparing these to the RayDB authors' code or paper results.
- Any whole-app speedup claim over RayDB end-to-end (setup is still Python-dominant).
- Public-facing wording of any speedup number until the external review gate produces a consensus file with exact approved text.
- Any attribution of the Torch/CuPy path as the Embree-vs-RT baseline.

**Required fixes before publishing the closeout externally:** Issues 2 and 3 above (README clarifications). Issue 1 (Goal2651 acknowledgment) is recommended but lower priority since Goal2651 is an intermediate report, not the closeout document.
