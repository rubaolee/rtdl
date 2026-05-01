# Goal1207 Gemini Review Request: Linux Embree Prefix Fix

Please review the Goal1207 fix for the Linux Embree prefix issue discovered during the Goal1204/Goal1206 pod work.

## Files To Review

- `src/rtdsl/embree_runtime.py`
- `tests/goal1207_linux_embree_prefix_env_test.py`
- `docs/reports/goal1207_linux_embree_prefix_env_fix_2026-05-01.md`

## Context

On the RTX 4090 pod, Ubuntu `libembree-dev` installed Embree 3, but RTDL's native Embree code requires Embree 4 (`embree4/rtcore.h`, `-lembree4`). Installing Embree 4 under `/opt/embree-4.4.0` did not work at first because the Linux runtime ignored `RTDL_EMBREE_PREFIX` and hardcoded `/usr`.

The fix changes `_default_embree_prefix(system)` so `RTDL_EMBREE_PREFIX` is honored before platform defaults on every OS.

## Validation

```bash
PYTHONPATH=src:. python3 -m unittest tests/goal1207_linux_embree_prefix_env_test.py
```

Result: `Ran 3 tests ... OK`

## Questions

1. Is this fix correct and narrow?
2. Does it preserve existing default behavior when `RTDL_EMBREE_PREFIX` is unset?
3. Is the test sufficient for this environment-selection bug?
4. Verdict: `ACCEPT` or `BLOCK`, with required fixes if blocked.

Please write the review to:

`docs/reports/goal1207_gemini_linux_embree_prefix_fix_review_2026-05-01.md`
