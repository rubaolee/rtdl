# Goal630 Claude Review — Optional Native Skip Fix

Date: 2026-04-19
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**
Re-reviewed: 2026-04-19 (after tightened fallback inspection)

---

## What was reviewed

- `tests/_optional_native_compare.py`
- `tests/goal15_compare_test.py`
- `docs/reports/goal630_v0_9_4_goal15_optional_native_skip_response_2026-04-19.md`

---

## Core correctness

**Preflight fires before the linker is invoked.** `goal15_compare_test.py:18` calls
`skip_unless_optional_native_compare_toolchain_present()` unconditionally, before
`compare_goal15(Path(tmpdir))` at line 21. That is the required fix: the old code
could enter the compile path and crash the test runner with a raw linker error;
the new code raises `SkipTest` first.

**Real comparison mismatches are not hidden.** The assertions on lines 25–30
(`cpu_matches_native`, `embree_matches_native`, `native_total_sec > 0`) only execute
when `compare_goal15` returns a payload, meaning the native toolchain was present,
compiled, and ran. If the native binary disagrees with RTDL output, the payload
fields are False and the test fails normally. The skip path is unreachable at that
point.

**Exception fallback is correctly wired.** `skip_optional_native_compare_failure`
either raises `SkipTest` or returns `None`; the bare `raise` on line 24 re-raises the
original exception in the latter case. A non-toolchain exception from within
`compare_goal15` propagates normally.

---

## Re-review: tightened fallback (correcting prior observation)

The initial review raised a "notable observation" that the marker list would
effectively match *all* `CalledProcessError` instances because
`"returned non-zero exit status"` is always present in
`subprocess.CalledProcessError.__str__()`.

**This observation was incorrect.** Inspecting `_optional_native_compare.py:73–86`,
the string `"returned non-zero exit status"` does not appear in the markers tuple.
The markers are:

```
"geos", "embree", "pkg-config", "library not found", "cannot find -l",
"native oracle build failed", "optional native comparison build",
"-lembree4", "-lgeos_c", "goal15_lsi_native", "goal15_pip_native",
"rtdl_embree.cpp"
```

All of these are scoped to C++ native-comparison toolchain activity. A
`CalledProcessError` raised by an unrelated subprocess inside `compare_goal15`
would only convert to `SkipTest` if its message, cmd, stdout, or stderr
happened to contain one of these toolchain-specific strings — which in practice
requires a build or link step involving Embree or GEOS.

The response document (`goal630_v0_9_4_goal15_optional_native_skip_response_2026-04-19.md`)
explicitly confirms this design intent:

> The fallback classification is keyed to native-comparison toolchain markers …
> it does not skip every arbitrary subprocess failure solely because a process
> returned non-zero.

The prior concern is withdrawn. The fallback is correctly tight.

---

## Preflight coverage

| Check | Location | Assessment |
|---|---|---|
| `c++` on PATH | line 26–27 | correct |
| Embree headers | line 30, 39 | correct — checks `embree4/` include directory |
| Embree libs | lines 31–39 | correct — scans multiple platform paths, matches `libembree4.*` |
| GEOS via pkg-config | lines 42–46 | correct — tries both `geos` and `geos_c` package names |
| GEOS via lib scan | lines 48–57 | correct fallback when pkg-config absent |
| Windows exemption | line 24–25 | early return; exception fallback still applies on Windows |

---

## Summary

The fix achieves its stated goal. Missing optional toolchain → `SkipTest` before
the linker is invoked. Present toolchain → comparison runs and mismatches fail the
test. The `stdout` and `cmd` expansion in the exception helper improves diagnostics.
No masking of real RTDL correctness failures is introduced. The fallback marker
list is correctly scoped to toolchain-specific strings and does not convert
arbitrary subprocess failures into skips.

**ACCEPT**
