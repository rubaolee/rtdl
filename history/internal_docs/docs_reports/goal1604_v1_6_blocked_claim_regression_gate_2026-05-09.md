# Goal 1604: v1.6 Blocked-Claim Regression Gate

## Verdict

The `v1.6` Python+RTDL closure path now has a regression gate for public claim
discipline.

This gate does not publish `v1.6`, does not authorize release/tag action, and
does not change the architecture boundary. Its job is narrower: keep release
work from accidentally converting the accepted Python+RTDL architecture anchor
into unsupported claims about whole applications, arbitrary Python code, true
zero-copy, package installation, or stable `COLLECT_K_BOUNDED`.

Release readiness and release/tag authorization remain final-release-package
decisions. This gate intentionally focuses on unsupported technical claims so
it does not prevent a later explicitly authorized `v1.6` release statement.

## Guarded Claims

The gate rejects affirmative release-facing wording that would imply the
following claims (while explicitly permitting honest warnings and negations):

- RTDL optimizes arbitrary user Python code.
- RTDL provides whole-application speedup by default.
- Any `--backend optix` run is automatically a NVIDIA RT-core speedup.
- True zero-copy is supported without measured device-memory evidence.
- `COLLECT_K_BOUNDED` is stable in the `v1.6` surface.
- Partner tensor handoff is part of the Python+RTDL closure.
- Package-install usage is supported without validated packaging metadata.
- Native internals are fully app-agnostic.

## Allowed Boundary

The safe public boundary remains:

```text
v1.6 is the planned Python+RTDL architecture closure milestone. Python remains
the app/control layer. RTDL owns the supported RT-shaped primitive contract and
the bridge to Embree/OptiX execution for the listed stable primitive subpaths.
Performance claims must stay scoped to reviewed exact primitive subpaths.
```

## Test Coverage

The regression test checks:

- the machine-readable readiness gate keeps blocked flags false;
- release/tag readiness itself remains a separate final-release-package gate;
- `COLLECT_K_BOUNDED` remains pending rather than stable;
- front-door docs and current v1.6 planning artifacts avoid forbidden broad
  claims;
- release-facing docs preserve source-tree usage instead of claiming
  package-install support;
- the current architecture docs preserve the Python+RTDL vs Python+partner+RTDL
  roadmap boundary;
- Goal 1603 continues to block claims that native internals are fully
  app-agnostic.

## Result

The local blocked-claim regression slice passed on Windows:

```text
Ran 27 tests
OK
```

The broader final release validation still needs separate Windows/Linux and
real NVIDIA OptiX evidence before `v1.6` can be published.
