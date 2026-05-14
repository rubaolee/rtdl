# Goal1956 Claude Debt Review - RawKernel Control-App Perf Path

Reviewer: Claude (Anthropic), independent of authoring.
Date: 2026-05-14
Independence: this review is being performed by Claude in place of Gemini Pro (currently unavailable). It is grounded in the on-disk repository state at `HEAD = 2854e109` and is read-only.
Scope (commits): `06316813` (local Linux RawKernel perf smoke), `32a9aadd` (RawKernel control-app pod runner), `2854e109` (external review handoff). Handoff source: `docs/handoff/GOAL1956_EXTERNAL_REVIEW_RAWKERNEL_CONTROL_PERF_2026-05-13.md`.
Verdict: `accept-with-boundary`.

## Method

- Re-read each file enumerated by the Goal1956 handoff plus surrounding context (`goal1911_v2_readiness_aggregator.json`, `goal1950_gemini_final_v2_release_review_2026-05-13.md`, `goal1954_gemini_review_goal1953_rawkernel_control_apps_2026-05-13.md`, `goal1953_control_apps_cupy_rawkernel_v2_decision_2026-05-13.md`).
- Inspected the five Goal1955 local-Linux JSON artifacts and their headline ratios.
- Read the diffs of the three referenced commits and the structure of `scripts/goal1956_rawkernel_control_app_pod_runner.sh`.
- This is a read-only audit; no source files or tests were modified.

## Answers To The Five Handoff Questions

### 1. Does Goal1955 correctly preserve the v2 user-decision boundary?

Yes, consistently. Three places carry the explicit fairness language:

- `examples/rtdl_control_apps_cupy_rawkernel.FAIRNESS_NOTE` declares it once and threads it into every per-app payload;
- `scripts/goal1955_rawkernel_control_app_perf.build_payload` writes the same disclaimer plus the explicit `comparison_is_not_absolutely_fair: True` and `requires_pod_for_release_timing: True` boundary booleans into the perf JSON;
- the local Linux report's "Boundary" section says verbatim that v2 uses Python+CuPy RawKernel+RTDL while v1.8 is Python+RTDL with no user native extension, "explicit user decision", "not v2.0 release performance evidence".

The Goal1954 Gemini review of Goal1953 already accepted this on the implementation side; Goal1955 carries that contract forward without dilution.

Verdict on Q1: `accept`.

### 2. Does the graph RawKernel correction properly remove artificial global-atomic contention without changing authored graph summary semantics?

Yes — and the test `goal1953_control_apps_cupy_rawkernel_v2_test.test_graph_rawkernel_uses_closed_form_summary_without_global_atomic_contention` enforces this contract. The new kernel is a single-thread closed-form write of the six replicated-graph statistics:

```text
out[0] = 2*copies; out[1] = 2*copies; out[2] = 1;
out[3] = copies;   out[4] = 3*copies; out[5] = copies; out[6] = 3*copies;
```

These numbers come straight from the authored replicated-graph contract on which `_graph_cpu_continuation` is built. The CPU and CuPy paths agree by construction, and both match `rtdl_graph_analytics_app`'s `cpu_python_reference` oracle in the local artifact (`matches_v1_8_python_rtdl_oracle: true`).

Boundary I flag: the closed-form kernel is mathematically valid for the workload as authored (replicated graph summary is by definition a closed-form function of `copies`), but the resulting `v2_median_s ≈ 6.1e-5 s` for 1000 copies is essentially CuPy launch + sync overhead — not graph-traversal work. The local report acknowledges this in the "Interpretation" section ("v2 continuation can produce large speedups when the non-RT portion is a compact aggregation"), but a casual reader of just the table could misread the `0.000004x` headline ratio as "RawKernel made graph_analytics 250,000x faster". The fairness note disclaims this, and any future external use of this number should attach the same context.

Verdict on Q2: `accept`. Boundary: closed-form kernel is correct for the authored workload but does not constitute graph-traversal acceleration evidence.

### 3. Does the local Linux GTX 1070 report avoid overclaiming release-grade evidence?

Yes. Every observable channel — markdown narrative, JSON `claim_boundary`, per-app `fairness_note`, the perf script's top-level "fairness_note", and the user-facing `Status: local-linux-smoke-complete` — explicitly disclaims release-grade evidence. The report's "Next Gate" section reiterates: pod runs, `--partner cupy`, `--candidate-backend optix`, seconds-scale workloads, bounded timeouts, recorded GPU/driver/CUDA/source commit, and independent review *before* any broad v2 performance claim.

Two minor things I want recorded as light debt, not blockers:

(a) The local polygon rows show v2 is **slower than v1.8 by 14.7x–19.4x at 256 copies** (`polygon_pair_overlap_area_rows`: 0.612s vs 0.032s; `polygon_set_jaccard`: 0.408s vs 0.028s). The report correctly attributes this to candidate/mask construction time under `cpu_all_pairs` and defers timing to pod-with-OptiX, but the JSON `v2_vs_v1_8_ratio` values 19.39 and 14.71 are eye-popping in isolation. Any forensic reader of the polygon artifacts without the narrative will need the report to interpret them.

(b) `goal1955_local_linux_graph_1m_v2_only_cupy_rawkernel_2026-05-13.json` has `all_match_v1_8_python_rtdl_oracle: false` because `matches_v1_8_python_rtdl_oracle` is `None` when v1.8 is skipped (the perf script's aggregator coerces `bool(None) → false`). The markdown narrative correctly identifies this as a v2-only probe done because the v1.8 oracle exceeded local timeout. The JSON's `false` is not wrong — there is no oracle agreement to assert — but it is a minor signal/narrative mismatch that a strict aggregator could misread.

Verdict on Q3: `accept-with-boundary`. The report does not overclaim; (a) and (b) are debt items, not gate failures.

### 4. Does Goal1956 provide a sufficiently controlled pod runner?

Largely yes. The pod runner concretely provides every element the handoff lists:

| Element | Mechanism |
| --- | --- |
| Progress logging | `[goal1956] <iso-date> start/done <name>` written to `${OUT_DIR}/progress.log` and per-step `*.log` |
| Timeouts | `STEP_TIMEOUT_SECONDS` (default 1800 s) wraps every step via `timeout --preserve-status`; `0` disables |
| CuPy probe | Auto-install fallback on missing `cupy`, then a Python probe writing `cupy_probe.json` with version + device name |
| OptiX build | `make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}"` once, exporting `RTDL_OPTIX_LIBRARY` |
| Source label propagation | `SOURCE_COMMIT_LABEL` defaults to `git rev-parse HEAD`, threaded through `--source-commit-label` to every per-app run; summary script asserts every artifact's label matches |
| Per-app artifacts | Four `${OUT_DIR}/<app>.json` outputs plus a top-level `summary.json` |
| Bounded summary | The inlined Python summary block fails closed if any artifact has a label mismatch or `all_match_v1_8_python_rtdl_oracle != true`, and writes a `claim_boundary` block with `v2_0_release_authorized=False`, `whole_app_speedup_claim_authorized=False`, `broad_rt_core_speedup_claim_authorized=False`, `local_linux_gtx1070_is_release_perf_evidence=False` |

The Goal1956 unit test enforces the runner contract surface: presence of `STEP_TIMEOUT_SECONDS`, `date -Iseconds`, `progress.log`, `make build-optix`, `cupy-cuda12x`, `RTDL_OPTIX_LIBRARY`, `--source-commit-label`, `summary.json`; all four control apps; the OptiX-vs-cpu polygon backend switch; and the three release-authorization booleans set to `False`.

Boundary items I want recorded:

(i) **OPTIX_PREFIX default is `/root/vendor/optix-sdk`**, which is one of multiple paths past pod handoffs have used. A previous handoff noted `make build-optix` failing because OptiX SDK headers were missing at `/opt/optix/include/optix.h`. Whoever runs this pod must set `OPTIX_PREFIX` to whatever the actual pod has, or the build step will fail closed and the polygon-with-OptiX timing will not be produced. Worth a one-line `README.pod-runner` note saying "set OPTIX_PREFIX before running."

(ii) **The runner does an unconditional `pip install cupy-cuda12x` if CuPy is missing.** That is correct on a network-connected pod but will fail late on an isolated pod. It also pulls a CUDA-12.x wheel; pods running CUDA 11 would need a different wheel. Worth a sanity note in the script header.

(iii) **`RUN_POLYGON_WITH_OPTIX=1` is binary** — when 0, polygon falls back to `cpu_all_pairs` (the same slow path the local smoke ran). There is no `embree` option in the runner even though the perf script supports it (`--candidate-backend embree`). If OptiX is unavailable on the pod but Embree is, the runner has no fallback that would still demonstrate RT-accelerated candidate discovery; that's a small gap.

(iv) The summary script asserts `all_match_v1_8_python_rtdl_oracle` at the artifact level. That's the right fail-closed behavior for the pod gate, but it means a v2-only run (analogous to the local 1M graph probe) is not expressible in the pod summary; if the pod ever needs a v2-only timing scale, the summary script will need a `--skip-v1-8` aware code path.

(v) `_polygon_summary_inputs` and `_polygon_masks` run on CPU/NumPy in O(polygons × cells); at `POLYGON_COPIES=2048` and growing cell sets this may dominate runtime and obscure where any kernel speedup lives. The runner doesn't surface a per-phase breakdown beyond the `run_phases` keys that the per-app payload already carries, but at this scale the phase timings should be checked at pod-review time to ensure the OptiX candidate-discovery saving is visible.

Verdict on Q4: `accept-with-boundary`. The runner satisfies every element the handoff names; (i)–(v) are debt items for the next iteration of the pod runner, not gate blockers.

### 5. Are any public or report statements accidentally authorizing v2.0 release, broad RT-core speedup, whole-app acceleration, arbitrary CuPy acceleration, or package-install claims?

No. I checked the handoff, the local report, the pod runner inlined summary, the perf script's `build_payload`, and the example's `run_all_control_apps`. Every channel writes some variant of the four release-block booleans:

- `v2_0_release_authorized: False` (pod runner summary)
- `whole_app_speedup_claim_authorized: False` (pod runner summary)
- `whole_app_speedup_claim_authorized_without_review: False` (perf script)
- `whole_app_speedup_claim_authorized_without_measurement: False` (example)
- `broad_rt_core_speedup_claim_authorized: False` (pod runner summary)
- `local_linux_gtx1070_is_release_perf_evidence: False` (perf script + pod runner)
- `requires_pod_for_release_timing: True` (perf script)
- `requires_pod_for_cupy_timing: True` (example)
- `cpu_fallback_is_correctness_only: True` (example)
- `comparison_is_not_absolutely_fair: True` (perf script)
- `counts_as_v2_app_version` is gated on `partner == "cupy"` (example, perf script)

The Goal1911 readiness aggregator (`status: blocked`) plus the existing Goal1950 Gemini final review (`accept-with-boundary`, boundary = "final v2.0 release consensus missing", "explicit user-requested release action missing") frame the broader picture: these RawKernel artifacts do not move the v2.0 release gate; they only fill the next evidence slot.

Light debt item (not a release blocker): the three claim-boundary vocabularies across example / perf script / pod runner use **three different key-name conventions** for the same concepts. Future aggregators will need a small normalization layer if they want a single boolean view across artifacts.

Verdict on Q5: `accept`.

## Debt And Risk Register

| Item | Severity | Origin | Notes |
| --- | --- | --- | --- |
| Graph closed-form kernel headline ratio is a measurement-vs-formula artifact | Low | `06316813` | Acknowledged in report and fairness_note; risk is downstream misquoting of `0.000004x`. |
| Local polygon ratios show v2 14–19x slower at 256 copies | Low | `06316813` | Correctly attributed to `cpu_all_pairs` candidate discovery; pod runner fixes this with `--candidate-backend optix`. |
| `all_match_v1_8_python_rtdl_oracle: false` on v2-only graph artifact | Low | `06316813` | Narrative says v2-only probe; JSON boolean from `bool(None)` coercion. Strict aggregators may misread. |
| `source_commit` empty in local artifacts | Resolved | `06316813` | Acknowledged; pod runner injects `--source-commit-label` and the summary script enforces label match. |
| Pod runner assumes `OPTIX_PREFIX=/root/vendor/optix-sdk` | Medium | `32a9aadd` | Pod operator must set this to the pod's actual OptiX SDK path or the build step fails. Recommend a one-line setup note. |
| Pod runner does `pip install cupy-cuda12x` if missing | Low | `32a9aadd` | Fails late on isolated/CUDA-11 pods. |
| `RUN_POLYGON_WITH_OPTIX` is binary; no Embree fallback in the runner | Low | `32a9aadd` | Perf script supports `embree`; runner could expose it for partial RT acceleration when OptiX is absent. |
| Summary script fail-closed on `all_match_v1_8_python_rtdl_oracle` | Low (intentional) | `32a9aadd` | Correct as a pod gate; future v2-only pod probes will need a `--skip-v1-8` aware summary path. |
| `_polygon_summary_inputs` is CPU/NumPy O(polygons × cells) | Medium | pre-existing | At `POLYGON_COPIES=2048` the host-side mask build may dominate runtime; pod review must inspect `run_phases` to confirm OptiX candidate-discovery saving is visible. |
| Three different claim-boundary key vocabularies across artifacts | Low | example / perf script / pod runner | Future aggregator will need a normalization mapping. |
| Risky list compaction uses sha256 + head/tail | Low | `06316813` | Reproducible but not directly auditable; matches the deterministic v1.8 hash, so still usable. |
| Source archive used for local Linux smoke has no `.git` | Resolved | local-only | Pod runner uses `git rev-parse HEAD` so this gap is gone on the pod path. |

## Independence Disclosure

Claude (Anthropic) is a distinct AI system from Codex (OpenAI) and Gemini (Google). This review is performed at arm's length from the authoring of the three commits and the handoff. It pairs with the existing `goal1954_gemini_review_goal1953_rawkernel_control_apps_2026-05-13.md` (accept) and `goal1950_gemini_final_v2_release_review_2026-05-13.md` (accept-with-boundary) for a Claude + Gemini distinct-AI signal on the Goal1953 + Goal1955 + Goal1956 chain. Per the consensus rule, this single Claude review is not a substitute for the **final v2.0 release consensus**, which Goal1911 still lists as missing.

## Final Verdict

`accept-with-boundary`.

The work satisfies what the handoff asked: it preserves the user-approved v2 fairness boundary, removes the spurious global-atomic contention from the graph continuation without changing authored semantics, avoids overclaiming on the local Linux GTX 1070 evidence, and supplies a controlled pod runner with progress logging, per-step timeouts, a CuPy probe, an OptiX build, source-label propagation, per-app artifacts, and a fail-closed bounded summary. No claim-boundary leak was found; release-authorization booleans are uniformly `False` across artifacts.

The boundary covers:

1. The local Linux numbers are not release evidence; pod evidence with `--partner cupy` plus `--candidate-backend optix` is still required, especially for the two polygon rows.
2. The graph closed-form headline ratio (`v2_vs_v1_8 ≈ 4e-6`) is a launch-overhead-versus-Python-reduction comparison, not a graph-traversal acceleration claim; downstream copy must not strip the fairness_note.
3. OPTIX_PREFIX / CuPy-install / Embree-fallback debt items in the pod runner should be addressed before the next pod cycle but do not block the current packet.
4. The broader v2.0 release gate (Goal1911) remains `blocked` on missing final Claude v2.0 release review and missing final v2.0 release consensus; this Goal1956 review does not satisfy that gate by itself.

If pod evidence is collected against this runner and a final distinct-AI consensus is recorded over Goals 1946 + 1947 + 1955 + 1956 evidence, the gate can move from `blocked` toward a `release-authorized` state — at which point the Goal1911 aggregator's remaining blockers need a fresh re-read.
