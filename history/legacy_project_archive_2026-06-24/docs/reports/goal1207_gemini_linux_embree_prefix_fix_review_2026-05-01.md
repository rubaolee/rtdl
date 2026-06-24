# Goal1207 Gemini Review: Linux Embree Prefix Fix

Date: 2026-05-01
Reviewer: Gemini CLI

## Verdict: `ACCEPT`

## Review Summary

The fix correctly addresses the issue where `RTDL_EMBREE_PREFIX` was ignored on Linux. By moving the environment variable check to the top of `_default_embree_prefix`, the runtime now consistently honors user overrides across all supported platforms before falling back to platform-specific defaults.

## Detailed Analysis

### 1. Is this fix correct and narrow?
Yes. The change in `src/rtdsl/embree_runtime.py` is minimal and precisely targets the reported issue. Moving `os.environ.get("RTDL_EMBREE_PREFIX")` to the beginning of `_default_embree_prefix` is the standard pattern for environment-based overrides in this codebase.

### 2. Does it preserve existing default behavior when `RTDL_EMBREE_PREFIX` is unset?
Yes. The logic fallthrough ensures that:
- Darwin still defaults to `/opt/homebrew/opt/embree`.
- Windows still uses its multi-candidate search under `~/vendor`.
- Linux (and other systems) still default to `/usr`.

### 3. Is the test sufficient for this environment-selection bug?
Yes. `tests/goal1207_linux_embree_prefix_env_test.py` covers:
- Linux override via `RTDL_EMBREE_PREFIX`.
- Darwin override via `RTDL_EMBREE_PREFIX`.
- Linux default behavior (regression test).

The tests pass successfully.

## Validation Results

```bash
PYTHONPATH=src:. python3 -m unittest tests/goal1207_linux_embree_prefix_env_test.py
Ran 3 tests ... OK
```
