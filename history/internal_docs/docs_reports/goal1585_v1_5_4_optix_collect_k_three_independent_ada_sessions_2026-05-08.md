# Goal 1585: OptiX Collect-K Three Independent Ada Sessions

## Verdict

Three independent committed-state Ada pod sessions all preserved parity and expected topology for the baseline, alias, and candidate-preset paths. The prior `49153` negative timing point did not recur: `49153` alias improved over baseline in all three targeted 9-repeat sessions and all three 5-repeat sweep sessions.

This materially strengthens the Ada evidence for the opt-in candidate preset, but it still does not clear default promotion because all three sessions are on the same Ada GPU architecture.

## Run Scope

- Commit: `e0f53f31c0f51adbe3dddf246cd5f922fe08933a`
- Pod checkout: `/root/rtdl_goal1545_pod`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Runner: `scripts/goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py`
- Per-session command shape: `--repeats 5 --targeted-repeats 9 --candidate-preset-smoke --candidate-preset-repeats 5`
- Compact JSON artifact: `docs/reports/goal1585_v1_5_4_optix_collect_k_three_independent_ada_sessions_2026-05-08.json`
- Pod raw prefixes: `/tmp/goal1585_session1`, `/tmp/goal1585_session2`, `/tmp/goal1585_session3`

## Acceptance

Each session reported:

- Baseline accepted: `True`
- Alias accepted: `True`
- Baseline parity: `True`
- Alias parity: `True`
- Baseline topology: `True`
- Alias topology: `True`
- Candidate preset accepted/parity/topology: `True`

## Sweep Targets

| Session | Count | Baseline ms | Alias ms | Delta ms | Baseline payload copies | Alias payload copies | Parity |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 49153 | 0.216941 | 0.210189 | -0.006752 | 3 | 1 | True |
| 1 | 65536 | 0.212853 | 0.211621 | -0.001232 | 0 | 0 | True |
| 1 | 65537 | 0.285131 | 0.265924 | -0.019207 | 5 | 0 | True |
| 2 | 49153 | 0.218565 | 0.212272 | -0.006293 | 3 | 1 | True |
| 2 | 65536 | 0.212523 | 0.212403 | -0.000120 | 0 | 0 | True |
| 2 | 65537 | 0.304297 | 0.264782 | -0.039515 | 5 | 0 | True |
| 3 | 49153 | 0.218665 | 0.211020 | -0.007645 | 3 | 1 | True |
| 3 | 65536 | 0.211651 | 0.213064 | 0.001413 | 0 | 0 | True |
| 3 | 65537 | 0.283427 | 0.266966 | -0.016461 | 5 | 0 | True |

## Targeted Reruns

| Session | Count | Baseline ms | Alias ms | Candidate preset ms | Alias delta ms | Candidate delta ms | Payload copies baseline/alias/candidate |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 49153 | 0.220487 | 0.213415 | 0.234825 | -0.007072 | 0.014338 | 3/1/1 |
| 1 | 65536 | 0.211851 | 0.213654 | 0.213235 | 0.001803 | 0.001384 | 0/0/0 |
| 1 | 65537 | 0.282826 | 0.264281 | 0.267176 | -0.018545 | -0.015650 | 5/0/0 |
| 2 | 49153 | 0.237610 | 0.214236 | 0.213364 | -0.023374 | -0.024246 | 3/1/1 |
| 2 | 65536 | 0.211401 | 0.212383 | 0.213194 | 0.000982 | 0.001793 | 0/0/0 |
| 2 | 65537 | 0.283377 | 0.263820 | 0.266375 | -0.019557 | -0.017002 | 5/0/0 |
| 3 | 49153 | 0.220698 | 0.216260 | 0.215508 | -0.004438 | -0.005190 | 3/1/1 |
| 3 | 65536 | 0.212653 | 0.211421 | 0.213625 | -0.001232 | 0.000972 | 0/0/0 |
| 3 | 65537 | 0.284590 | 0.262678 | 0.266896 | -0.021912 | -0.017694 | 5/0/0 |

## Interpretation

The repeated Ada evidence supports the derived carry alias mechanism for carry-heavy odd counts:

- `49153`: alias reduced carry payload copies from `3` to `1` and improved in all three targeted alias sessions.
- `65537`: alias and candidate preset reduced carry payload copies from `5` to `0` and improved in all targeted sessions.
- `65536`: no carry payload copy is removed, so the small positive/negative deltas are expected neutral noise.

The candidate preset occasionally trails the explicit alias bundle at `49153` in session 1, but it preserves topology and parity and improves in sessions 2 and 3. This is still evidence for a candidate validation path, not a release claim.

## Claim Boundary

This report does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action. Default promotion still requires non-Ada NVIDIA validation and final external review.
