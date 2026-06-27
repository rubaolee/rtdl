# RTDL V2.14 vs V3.0.2 Pod Evidence Report

Status: formal pod comparison evidence; not release promotion.

Run date: 2026-06-20 UTC. User request date: 2026-06-19 America/New_York.

Artifact directory:
`docs/reports/v2_14_vs_v3_0_2_pod_comparison_2026-06-20_artifacts/`

## Hard Verdict

V3.0.2 does not need to be deleted and rewritten based on this pod run.

What the evidence supports:

- V2.14 remains the stronger historical performance baseline. It gives an
  11-row same-contract RTDL/OptiX-vs-Embree matrix with per-row speedups.
- V3.0.2 is stronger as the current user-facing source-tree release surface:
  source-tree doctor passes, the canonical `v3_current` matrix passes, and the
  ten current benchmark-app routes run successfully at scale on the RTX pod.
- V3.0.2 is not supported as a broad public speedup release. Its current scale
  runner explicitly blocks release authorization, broad RT-core wording, public
  speedup wording, true-zero-copy wording, automatic partner selection wording,
  and paper-reproduction wording.

The cleanest statement is:

> V2.14 proves row-scoped performance claims. V3.0.2 proves the cleaned current
> ten-app user surface and route-health contract. V3.0.2 improves the product
> shape and user safety over V2.x, but it does not replace V2.14 as the
> broadest performance evidence packet.

## Goal-Level Decision Audit

1. 我是否愚蠢了？

Yes, partly. The previous mistake was treating "V3 has been released" as if it
were enough to answer "V3 is better than V2.x" without first producing a fresh,
formal V2/V3 pod comparison.

2. 如果是，我做了哪些动作使得我的决策成为愚蠢的？

I mixed release wording, doc cleanup, and performance evidence. I also wasted
time on a wrong SSH key and on an initially wrong CUDA environment split before
using the historical pod key and the correct CuPy/Numba CUDA-path split.

3. 是不是有别的可能性使得我不用愚蠢在某一个思路上？

Yes. The better path was to run a same-pod V2.14/V3.0.2 evidence packet first,
classify failures by type, and only then decide whether V3 needed repair or
rewrite.

4. 我是否可以开始尝试不同路径，而真正解决问题？

Yes. This report is that different path: artifact-first, claim-boundary-first,
and explicit about what passed, what failed, and what is not proven.

## Pod And Toolchain

Remote pod:

- Host: `root@213.173.108.14 -p 11592`
- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 550.127.05
- VRAM: 20475 MiB
- Compute capability: 8.9
- Python: 3.12.3
- Git: 2.43.0
- OptiX headers: 8.0.0 from `/workspace/vendor/optix-dev-8.0.0`
- CUDA toolkit: `/usr/local/cuda`
- Embree: 4.3.0

Python packages in both V2 and V3 venvs:

- NumPy 1.26.4
- CuPy 13.6.0, smoke result `28`
- Numba 0.60.0, smoke result `[1, 2, 3, 4, 5, 6, 7, 8]`
- Shapely 2.1.2
- SciPy 1.17.1
- NetworkX 3.6.1
- Pytest 9.1.1

CUDA-path detail needed for this pod:

- `RTDL_NVCC=/usr/local/cuda/bin/nvcc`
- `CUDA_PATH=/usr/local/cuda`
- `CUPY_CUDA_PATH=/usr/local/cuda`
- `CUDA_HOME=<venv site-packages>/nvidia/cuda_nvcc` for Numba's CUDA 12.4 NVVM
- `PATH=<numba nvcc prefix>/bin:/usr/local/cuda/bin:$PATH`
- `LD_LIBRARY_PATH=<numba nvcc prefix>/nvvm/lib64:/usr/local/cuda/targets/x86_64-linux/lib:...`

Why this matters: setting `CUDA_HOME=/usr/local/cuda` made CuPy happy but made
Numba emit unsupported PTX for this driver. Setting only the Numba CUDA prefix
made CuPy miss system CUDA headers. The split above passed both CuPy and Numba
smoke tests.

## Formal Run Status

Source artifact: `status.tsv`

| Step | Return code | Elapsed |
| --- | ---: | ---: |
| V2.14 venv setup | 0 | 60s |
| V3.0.2 venv setup | 0 | 240s |
| V2.14 OptiX build | 0 | 60s |
| V2.14 Embree probe | 0 | 30s |
| V3.0.2 OptiX build | 0 | 60s |
| V3.0.2 Embree probe | 0 | 30s |
| V2.14 human-scale same-contract matrix | 1 | 450s |
| V3.0.2 source-tree doctor | 0 | 30s |
| V3.0.2 `v3_current` test matrix | 0 | 30s |
| V3.0.2 current scale profile all | 0 | 180s |

The only nonzero return code is V2.14's final validation gate. The V2 programs
themselves did not crash: all 33 V2 benchmark commands returned 0.

## V2.14 Evidence

Source artifact:
`v2.14_human_scale_same_contract/summary.json`

V2.14 ran 33 benchmark commands across 11 app rows. All app rows reported
`correct=true` and `reasonability_verdict=reasonable`.

V2.14 validation status: `reject`

Validation error:

```text
spatial_rayjoin_pip: aggregate outside 1-10s band (optix=0.199635, embree=0.367846)
```

This is a benchmark-duration calibration failure, not a correctness failure.
The `spatial_rayjoin_pip` row ran too quickly to satisfy the 1-10s aggregate
target window.

| V2.14 app | Correct | Comparison status | OptiX per iter ms | Best Embree per iter ms | Embree/OptiX |
| --- | --- | --- | ---: | ---: | ---: |
| barnes_hut | true | clean backend swap prepared phase | 8.494265 | 22.040021 | 2.595x |
| contact_manifold | true | clean backend swap prepared phase | 123.732712 | 152.284447 | 1.231x |
| hausdorff_xhd | true | clean backend swap prepared phase | 9.349482 | 21.880426 | 2.340x |
| librts_spatial_index | true | clean backend swap prepared phase | 0.564061 | 73.758140 | 130.763x |
| raydb_style | true | clean backend swap prepared phase | 0.595957 | 8.981220 | 15.070x |
| robot_collision | true | clean backend swap traversal phase only | 0.117343 | 1.251332 | 10.664x |
| rt_dbscan | true | mostly clean Numba continuation, same native handoff differs | 12.026995 | 16.302750 | 1.356x |
| rtnn | true | clean backend swap prepared phase | 105.716038 | 115.681019 | 1.094x |
| spatial_rayjoin_lsi | true | clean backend swap prepared phase | 0.079997 | 0.480592 | 6.008x |
| spatial_rayjoin_pip | true | clean backend swap prepared phase | 0.097752 | 0.167537 | 1.714x |
| triangle_counting | true | clean backend swap prepared phase | 0.145786 | 6.192259 | 42.475x |

V2.14 interpretation:

- V2.14 is a valid performance baseline.
- Its evidence is row-scoped and contract-scoped.
- The only failed gate in this pod rerun is a timing-window calibration issue.
- If we need a fully `accept` V2.14 artifact, rerun only
  `spatial_rayjoin_pip` with higher repeats so both backends land inside the
  1-10s aggregate target.

## V3.0.2 Evidence

V3.0.2 source-tree doctor:

- `ok=true`
- version `v3.0.2`
- required failures: none
- optional warnings: `imageio`, `imageio_ffmpeg`
- optional CuPy: pass
- optional Numba: pass
- optional OptiX library: pass
- optional Embree library: pass

V3.0.2 canonical current test matrix:

- group: `v3_current`
- module count: 39
- result: `ok=true`
- tests: 147
- output: OK

V3.0.2 current scale profile:

- `all_pass=true`
- `json_pass_count=10`
- rows: 10
- validation: `accept`
- validation errors: none
- claim flag violations: none
- release authorization: false
- public speedup claim authorization: false
- broad RT-core claim authorization: false
- true-zero-copy claim authorization: false
- paper reproduction claim authorization: false

| V3.0.2 row | App | Status | Elapsed | Correctness signal | Important timing signal |
| --- | --- | --- | ---: | --- | --- |
| `hausdorff_xhd_scale_default_optix_threshold` | hausdorff_xhd | pass | 6.769s | `matches_oracle=true`, `oracle_decision_matches=true` | query threshold phase 0.008058s, scene prepare 1.307344s |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | spatial_rayjoin | pass | 63.392s | `all_counts_match=true` | LSI RTDL median 0.000126s vs Numba 0.022981s; overlay RTDL median 0.000197s vs Numba 0.039446s; PIP one-shot Numba wins |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | rt_dbscan | pass | 16.787s | no reference validation in this scale row | prepared grouped native 0.095011s; point count 65536 |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | robot_collision | pass | 10.521s | no probe reference in this scale row; measured signatures stable | traversal median 0.000041s, 49900 measured runs |
| `contact_manifold_optix_scale_default_grid64` | contact_manifold | pass | 5.269s | `matches_cpu_reference=true`, `complete_candidate_coverage=true` | native collect elapsed 0.000552s |
| `raydb_style_optix_count_scale_default_262k` | raydb_style | pass | 11.799s | `matches_cpu_reference=true` | elapsed 0.000920s |
| `barnes_hut_numba_scale_default_8192` | barnes_hut | pass | 11.023s | `validation_skipped=true`; partner exact-force route | Numba force kernel median 0.009405s |
| `librts_spatial_index_optix_scale_default_32768` | librts_spatial_index | pass | 6.772s | CPU reference skipped in this scale row | query median 0.045152s |
| `rtnn_prepared_optix_scale_default_65536` | rtnn | pass | 8.524s | runner payload `ok=true` | prepared aggregate median 0.000273s, query count 65536 |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | triangle_counting | pass | 6.588s | `triangle_count_matches_oracle=true` | query median 0.161506ms, scene prepare 297.886260ms |

V3.0.2 hot-path floor summary:

- `decision_grade_timing_authorized=false`
- 2 rows met targeted internal timing floors:
  `robot_collision_optix_scale_default_1024_no_probe_reference`,
  `raydb_style_optix_count_scale_default_262k`
- 8 rows are smoke/internal timing rows:
  `hausdorff_xhd`, `spatial_rayjoin`, `rt_dbscan`, `contact_manifold`,
  `barnes_hut`, `librts_spatial_index`, `rtnn`, `triangle_counting`
- subfloor or metric-missing rows: none

V3.0.2 interpretation:

- V3.0.2 passes the current release-health gates on the pod.
- The ten-app current route surface is alive at non-toy scale.
- V3.0.2 is much better than the earlier V3 leak state reviewed by Claude:
  the canonical `v3_current` group now excludes V4 prep by default, and the
  source-tree doctor validates the current V3.0.2 surface.
- V3.0.2 is not a claim-grade speedup packet. The scale runner itself refuses
  public speedup, release, broad RT-core, true-zero-copy, and paper-reproduction
  wording.

## What V3.0.2 Is Better At Than V2.x

V3.0.2 improves the product and user experience over V2.x in these evidence-backed
ways:

1. Current user surface: V3.0.2 has a source-tree doctor that checks the front
   page, current tutorials, current examples, release packet, app-author
   strategy doc, and required runtime modules.
2. Canonical validation: `scripts/run_test_matrix.py --group v3_current`
   passed 39 modules and 147 tests.
3. Ten-app current route health: the pod scale profile passed all 10 current
   benchmark-app rows with parseable JSON and no claim-flag violations.
4. Claim discipline: V3.0.2 explicitly blocks V4/embedding/SDK/zero-copy claims
   and does not let old or preparatory material masquerade as current user
   surface.
5. App-author posture: V3.0.2 exposes explicit route choice and partner policy
   instead of pretending automatic backend/partner selection exists.

## What V3.0.2 Is Not Better At Yet

V3.0.2 does not currently beat V2.14 as a performance-evidence package.

Reasons:

1. V2.14 has a same-contract OptiX-vs-Embree table across 11 app rows.
2. V3.0.2's scale profile is primarily route-health evidence, not a same-contract
   speedup matrix.
3. V3.0.2's own runner marks decision-grade public timing as unauthorized.
4. Several V3.0.2 scale rows intentionally skip reference validation or use
   internal/smoke timing classifications.

This is not a reason to delete V3.0.2. It is a reason to stop saying "V3 is
better" without naming the dimension:

- Better product surface: yes.
- Better current route-health coverage: yes.
- Better public performance evidence than V2.14: no.
- Ready for broad speedup marketing: no.

## Problems Found

P0: No P0 product failure was found in V3.0.2 by this pod packet.

P1: V3.0.2 still needs a claim-grade performance matrix if we want to present
it as a performance upgrade over V2.14.

P1: Some V3.0.2 scale rows are not full correctness proofs:

- RT-DBSCAN scale row has `no_validation` and `matches_reference=null`.
- Robot collision scale row has `no_probe_reference`.
- Barnes-Hut scale row has `validation_skipped=true` and is a partner exact-force
  route, not an RT-core Barnes-Hut claim.
- LibRTS scale row skipped CPU reference.

P2: V2.14 rerun has one duration-calibration reject:

- `spatial_rayjoin_pip` completed correctly but the aggregate times were below
  the 1-10s target band.

P2: V3.0.2 source-tree doctor has optional media-module warnings:

- `imageio`
- `imageio_ffmpeg`

## Next Actions

1. Keep V3.0.2. Do not delete/rewrite it based on this evidence.
2. Fix or rerun the V2.14 `spatial_rayjoin_pip` calibration if we need the
   historical baseline packet to end with `validation.status=accept`.
3. Add a V3.0.2 same-contract performance matrix only for rows where the route
   and correctness contracts are genuinely comparable to V2.14.
4. Add explicit doc wording: "V3.0.2 improves the current user surface and
   route-health matrix; V2.14 remains the main row-scoped speedup baseline."
5. Ask external review to validate this report before making a public-facing
   conclusion.

## Final Answer To The User Question

If the question is "Does V3.0.2 work on the pod?", the answer is yes.

If the question is "Is V3.0.2 better than V2.x?", the correct answer is:

- yes for current user surface, current docs, tutorial/example gating, source
  doctor, ten-app current route health, and claim-boundary cleanup;
- no, not yet, for broad performance evidence, where V2.14 remains stronger.

If the question is "Should we delete V3 and redo it?", the answer is no based
on this evidence. The right move is targeted repair: preserve V3.0.2, document
the honest comparison, and add a claim-grade V3 performance matrix only where
the same-contract comparison is real.
