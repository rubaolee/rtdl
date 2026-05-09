# 3-AI Consensus: Goal 1604 v1.6 Blocked-Claim Regression Gate

## Verdict

Accepted as a valid `v1.6` blocked-claim regression gate.

Codex, Claude, and Gemini agree that Goal 1604 should guard unsupported
technical claims, not freeze future release authorization. Release readiness and
release/tag action remain final-release-package decisions.

## Consensus Findings

The gate correctly keeps these unsupported claims blocked:

- arbitrary user Python optimization;
- whole-application speedup;
- broad/default NVIDIA RT-core speedup from merely selecting OptiX;
- true zero-copy without measured device-memory evidence;
- stable `COLLECT_K_BOUNDED` promotion;
- partner tensor handoff as part of Python+RTDL;
- package-install support without packaging metadata;
- fully app-agnostic native internals.

The gate preserves the accepted architecture boundary:

- `v1.6` is Python+RTDL;
- `v1.7-v2.0` is Python+partner+RTDL;
- `v1.6` is an architecture anchor, not a performance freeze;
- future performance work remains top priority, especially NVIDIA RT-core and
  `COLLECT_K_BOUNDED` work.

## Review-Driven Fixes

Claude found no blockers and recommended two clarity fixes. The report's test
count now matches the 27-test local gate slice, and the test explains why
editable installs are blocked until packaging metadata exists and is validated.

Gemini initially found that release/tag flags should not be frozen by this
specific blocked-claim gate and that warning-text handling was too
prefix-oriented. The test now checks unsupported technical claim flags only,
leaves release authorization to the final release package, and uses
bidirectional context without treating generic "warning" text as safe by
itself. Gemini re-reviewed the fixed version and accepted it with no remaining
blockers.

## Validation

Windows local v1.6 gate slice:

```text
Ran 27 tests
OK
```

## Recommendation

Proceed to cross-platform source-tree validation and real NVIDIA OptiX
validation for the scoped `v1.6` primitive surface.

Do not publish `v1.6` until the final release package and final 3-AI consensus
are complete.
