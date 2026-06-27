# Independent Gemini Review for Goal3665 RayJoin PIP Fast-Domain Preflight Guard

Date: 2026-06-06

This is an independent Gemini review, distinct from Codex, and it authorizes no
public release or public speedup claims.

## Review of Goal3665

Goal3665 introduces a crucial safeguard in the benchmark workflow to prevent
incorrect fast-path results from proceeding to RayJoin timing. The changes correctly
integrate `device_predicate_eps` into the preflight mechanism and ensure the
runner fails closed when an invalid domain is detected.

### Questions Addressed:

1.  **Does the change correctly scope `device_predicate_eps` into the preflight without leaking the environment after the call?**
    Yes, the `preflight_rayjoin_pip_fast_count_domain` function in
    `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
    utilizes the `_temporary_env` context manager to set
    `RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS`. This ensures the
    environment variable is localized to the preflight call and restored
    afterward, preventing environment leakage. Unit tests in
    `tests/goal3321_rayjoin_pip_validated_domain_preflight_test.py` explicitly
    validate this scoping behavior.

2.  **Does the runner guard happen before RayJoin timing and fail closed on the invalid full-county domain?**
    Yes, the runner guard is implemented to execute before RayJoin timing. In
    `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`, when the
    `--rtdl-pip-require-validated-fast-domain` flag is used, the runner calls
    `preflight_rayjoin_pip_fast_count_domain` with `require_match=True`. If a
    mismatch between the fast count and exact count is detected, this raises a
    `RuntimeError`, causing the runner to terminate before `run_rayjoin_process_samples`
    (which initiates RayJoin timing) is invoked. The "Pod Smoke Results" in
    `docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md`
    confirm this behavior, showing the preflight rejected the full-county
    domain before RayJoin timing commenced.

3.  **Does the report clearly state that the A5000 smoke is functionality evidence, not clean-source performance evidence?**
    Yes, the report unequivocally states this in multiple locations. The
    "Evidence" section of `docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md`
    explicitly says: "It is intentionally recorded as functionality smoke, not
    clean-source performance evidence." Additionally, the
    `docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_a5000/summary.json`
    includes `"scope": "pod smoke for optional RayJoin PIP fast-domain
    preflight guard; not performance evidence"` and
    `"clean_source_performance_evidence": false`.

4.  **Does the work preserve the app-agnostic native-engine boundary?**
    Yes, the work preserves the app-agnostic native-engine boundary. The code
    (`rtdl_rayjoin_v2_spatial_join_app.py`) explicitly states: "The engine sees
    generic point/closed-shape count primitives. RayJoin CDB topology policy
    remains in Python preflight/fallback logic." The
    `docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md`
    also reiterates this in its "Purpose" and "Interpretation" sections.

5.  **Does it avoid release/public speedup/RTDL-beats-RayJoin claims?**
    Yes, the work meticulously avoids such claims. All `claim_boundary`
    dictionaries in the relevant Python files
    (`rtdl_rayjoin_v2_spatial_join_app.py` and
    `goal3244_rayjoin_same_slice_repeated_count_runner.py`) explicitly set
    claims like `release_authorized`, `public_speedup_claim_authorized`, and
    `rtdl_beats_rayjoin_claim_authorized` to `False`. The "Boundary" section of
    the markdown report also lists numerous claims that Goal3665 does not
    authorize.

## Verdict

`accept`

Goal3665 is well-scoped, correctly implemented, and thoroughly documented. It
addresses a critical safety concern in the benchmark workflow by ensuring that
fast-path optimizations are only applied when their correctness is validated for
the given input domain, thereby preventing misleading performance measurements
on invalid domains. The explicit boundary statements and clear distinction
between functionality and performance evidence are highly commendable.

## Boundary

This independent Gemini review of Goal3665 does not authorize:

-   public v2.9 release wording;
-   public speedup wording;
-   broad RT-core speedup wording;
-   whole-app RayJoin speedup wording;
-   RayJoin paper reproduction wording;
-   RTDL-beats-RayJoin wording;
-   true zero-copy wording;
-   automatic partner/backend selection;
-   app-specific native-engine logic.
