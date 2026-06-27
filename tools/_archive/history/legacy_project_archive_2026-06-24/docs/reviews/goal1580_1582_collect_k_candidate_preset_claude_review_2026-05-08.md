Now I have all the material needed. Here is my independent review.

---

## RTDL v1.5.4 OptiX `COLLECT_K_BOUNDED` — Candidate-Preset Independent Review

---

### Verdict

| Question | Finding |
|---|---|
| Safe as opt-in candidate preset (`RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`)? | **Yes, with one minor harness defect to acknowledge** |
| Safe to promote to default? | **No — measurement instability on count 49153 is unresolved to statistical satisfaction** |
| Public speedup claims justified now? | **No — evidence base is explicitly, correctly, and consistently bounded to opt-in micro-benchmark only** |

---

### Correctness / Parity

**C++ preset implementation is correct.**

The 9 positive-bundle functions at `rtdl_optix_api.cpp:640–705` each follow the pattern `collect_k_use_fastest_candidate() || collect_k_env_enabled("<flag>")`. The two rejected pointer-carry functions (`collect_k_use_carry_pointer_diagnostic` at line 687, `collect_k_use_carry_pointer_device_counts_diagnostic` at line 692) deliberately do **not** include `collect_k_use_fastest_candidate()` — this is correctly verified by the structural test `test_candidate_preset_does_not_enable_rejected_pointer_diagnostics`.

The dependency chain is consistent between C++ and the Python topology model:
- In C++ (line 1515–1516): `use_device_level_counts = collect_k_use_device_level_counts() && use_derived_level_descriptors && use_device_prefix_compact`
- In the Python probe (`expected_topology`, line 164–168): the identical three-way guard is applied

Since the preset enables all three of those prerequisites, the derived-carry-alias path activates correctly and the topology model stays in sync.

Parity (`same_candidate_rows`, `same_valid_count`, `same_overflowed_flag`) passed on all 11 sweep counts in both the baseline and alias runs, and on all three counts in the candidate preset smoke.

**One harness defect (low severity, latent):**

In `goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py:53–70`, the `_profile_env()` function, when running with `use_candidate_preset=True`, explicitly pops all `PROFILE_ENV` keys and `RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC`, then sets only `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`. However, it does **not** explicitly pop `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC` or `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC`. If those keys are present in the parent pod environment, they propagate into the candidate preset subprocess and activate the rejected diagnostics alongside the preset. This is not a problem in standard pod usage but is a real contamination vector in any test harness that sets these vars for earlier test phases.

---

### Performance Evidence

**What is strong:**

- Goal1581 5-repeat sweep: 9 of 11 counts show alias faster than baseline. The two largest odd-carry cases (`49153`: −9.8µs, `65537`: −50.2µs) are the most structurally meaningful since they involve carry payload copies. The carry payload copy count drops from 3→1 at 49153 and 5→0 at 65537 — these are structural wins, not noise.
- Goal1582 isolated 9-repeat single-session run for count 49153: alias −7µs, candidate preset −9µs relative to baseline. Carry copies reduced 3→1 in both modes.
- All three Goal1581 candidate preset smoke points (49153, 65536, 65537) pass parity and topology.

**What is not strong:**

- The Goal1581 9-repeat targeted rerun of count 49153 produced alias **+53µs slower** than baseline (0.2737ms vs 0.2206ms). The absolute magnitude of this flip (~60µs on a ~220µs total) is large enough to matter. The team characterizes this as session/process noise, and Goal1582 provides one contradicting clean session. But the evidence record now shows **one positive run and one negative run** for the critical 49153 point, plus one positive confirmation — a 2:1 ratio of positive sessions is not enough to call this definitively noise.
- The candidate preset smoke in Goal1579 uses `repeats=1`. A single-repeat timing carries no statistical weight; any JIT-warmup, power-state, or scheduling artifact can dominate.
- **GPU coverage is a single device**: NVIDIA RTX 4000 Ada Generation (Ada Lovelace, SM 8.9). The optimization involves CUB tile sort (blocking factor 2048 vs 4096), batched compact level, and device-side prefix scan — all of which have measurably different behavior on Turing (SM 7.x), Ampere (SM 8.0/8.6), and Hopper (SM 9.0) due to warp size, L2 bandwidth, and shared-memory scheduling differences.
- Only `row_width=2` is profiled. The topology model handles `row_width=1` on a different branch; the candidate preset's behavior on `row_width=1` or wider rows is untested.

---

### Claim Boundary

The claim boundary is correctly stated and consistently enforced across all three reports, the probe code (`goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py:342–356`), and the test suite (`test_report_preserves_claim_boundary`). All six `claim_flags` are locked to `False` and validated at runtime. This is a well-structured boundary: the machine-checked flags prevent any artifact from being accidentally cited as broader authorization.

The reports' self-assessment is accurate. Nothing observed in this review requires walking back their stated constraints.

---

### Required Next Steps

**Blocking for default promotion:**

1. **Resolve the 49153 measurement instability with three independent pod sessions.** Goal1582 is one clean session; Goal1581 targeted rerun is one noisy session. A minimum of one additional independent 9-repeat run on the same commit is needed before the team can claim the negative result is definitively noise rather than real regression at that count under certain GPU state conditions.

2. **Expand GPU coverage to at least one non-Ada architecture before promotion discussion.** The most informative additions would be Ampere (A100/A10) and Turing (T4), which are the most common deployment targets. A speedup on Ada with CUB-based tile sort does not guarantee parity or speedup on older SM versions.

3. **Increase candidate preset smoke repeats from 1 to at least 5.** A single-repeat smoke is insufficient for any timing claim. Even as an acceptance gate (not a measurement claim), `repeats=1` can pass or fail based on a single cold-launch artifact.

**Required before public speedup language or default promotion:**

4. **Add `row_width=1` (and optionally `row_width=4`) coverage to the probe sweep.** The current evidence covers only `row_width=2`.

5. **Fix the carrier-pointer env-var contamination path in `_profile_env`.** Add explicit `env.pop("RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC", None)` and `env.pop("RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC", None)` in the `use_candidate_preset=True` branch of `goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py:53`.

6. **Whole-application context measurement before any user-visible claims.** The micro-benchmark measures the isolated primitive. For any real latency claim, a trace showing the fraction of total frame/query time this primitive represents is required. Without it, even a confirmed 10% speedup on the primitive could be sub-microsecond at the application level.

**Summary:** The opt-in candidate preset is correctly implemented, correctly bounded, and safe to expose. It should not be promoted to default, and no public speedup wording is warranted, until items 1–3 above are resolved.
