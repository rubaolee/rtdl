### Goal 101 Consensus

Goal 101 is accepted.

Review trail:

- Codex:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-codex-review-goal101-final-package.md`
- Gemini:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-gemini-review-goal101-final-package.md`
- Claude:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-claude-review-goal101-final-package.md`

Reviewer outcome:

- Codex: `APPROVE`
- Gemini: `APPROVE`
- Claude: `ACCEPT WITH ONE MINOR FLAG`

Claude's minor flag was valid and was fixed before publish:

- `compile_to_ptx_with_nvcc(...)` now forwards `extra_opts`, so the fallback
  path no longer drops compile options that were supplied to the NVRTC path

Post-fix confirmation:

- Linux clean-clone `build-optix` rerun: `pass`
- Linux clean-clone `examples/rtdl_hello_world_backends.py --backend optix`:
  `pass`

Accepted conclusion:

- the onboarding hello-world/tutorial slice is now real and coherent
- the Linux OptiX failure for the backend-switching hello-world example is
  repaired
- the fix remains compatible with the clean-clone full regression matrix
