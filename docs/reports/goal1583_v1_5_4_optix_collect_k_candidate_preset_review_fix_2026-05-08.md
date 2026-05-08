# Goal 1583: Candidate Preset Review Fix

## Verdict

Claude reviewed the Goal1580-Goal1582 candidate-preset work and judged the opt-in preset safe, but not safe for default promotion or public speedup claims. The review found one low-severity harness contamination risk, which is now fixed.

## External Review

- Review file: `docs/reviews/goal1580_1582_collect_k_candidate_preset_claude_review_2026-05-08.md`
- Reviewer verdict: safe as opt-in candidate preset, not safe to promote by default, and public speedup claims are not justified now.

## Fix

The first fix made the Goal1579 runner candidate-preset subprocess explicitly remove both rejected pointer-diagnostic env vars before setting `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`:

- `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC`
- `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC`

This closes the contamination path where a parent shell could accidentally combine the candidate preset with rejected diagnostics.

Pod hostile-env validation then showed the same parent-shell contamination risk also affected normal baseline/alias profiles. The runner now starts every profile subprocess by clearing the full collect-k profile isolation key set, including:

- all positive-bundle individual flags,
- the one-flag candidate preset,
- the derived-carry alias diagnostic flag,
- both rejected pointer-carry diagnostic flags.

After isolation, the runner explicitly opts in only the intended mode: baseline bundle, alias bundle, or candidate preset.

The runner also raises the candidate-preset smoke default from a single repeat to `5` repeats via `--candidate-preset-repeats`.

## Validation

- Local tests: `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1580_v1_5_4_optix_collect_k_fastest_candidate_preset_test tests.goal1579_v1_5_4_optix_collect_k_next_arch_runner_test`
- Result: `Ran 9 tests`, `OK`.
- Clean pod hostile-env validation at `cd070a77456473966aa9933f1ab08238dfb9361a`: parent environment included `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC=1`, `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC=1`, and `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`.
- Pod static tests: `Ran 9 tests`, `OK`.
- Pod runner static tests: `Ran 17 tests`, `OK`.
- Pod runner output: `goal1579_next_arch_validation_recorded`.
- Pod acceptance: baseline accepted/parity/topology `True`, alias accepted/parity/topology `True`, candidate preset accepted/parity/topology `True`.
- Candidate preset artifact: `/tmp/goal1583_harness_isolation2_candidate_preset.json`.
- Candidate preset stage medians: `49153=0.211230 ms`, `65536=0.217762 ms`, `65537=0.265763 ms`.

## Remaining Blockers

Default promotion still needs more evidence:

- Additional independent pod sessions for timing stability.
- At least one non-Ada NVIDIA architecture.
- Wider row-width coverage if promotion scope expands beyond current row-width-2 evidence.
- External review after the final evidence package is assembled.

## Claim Boundary

This fix does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
