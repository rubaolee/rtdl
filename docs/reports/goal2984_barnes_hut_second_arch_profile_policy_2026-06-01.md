# Goal2984 Barnes-Hut Second-Architecture Profile Policy

Date: 2026-06-01

Status: runner profile added; no release authorization

## Purpose

Goal2984 addresses the release-gap finding shared by the Goal2981 Claude and
Gemini reviews: the RTX 4000 Ada second-architecture packet attempt in Goal2977
was clean for six app harnesses, but did not finish the canonical Barnes-Hut row
because the 8192-body Embree CPU baseline behaved as a single-core bottleneck.

The fix is an explicit runner policy, not an app-specific engine shortcut:

- the default Goal2855 packet runner still uses the full Goal2803 Barnes-Hut
  profile: `512:16`, `2048:32`, and `8192:32`;
- a new named runner profile, `second_arch_bounded`, runs the same Goal2803
  harness with `512:16` and `2048:32` only;
- packet plans and summaries record the selected Barnes-Hut profile and its
  boundary string;
- the bounded profile is not a release shortcut unless a future release packet
  explicitly scopes the second-architecture claim to that bounded tier.

## Design

The Goal2855 runner now exposes:

```text
--barnes-hut-case-profile default
--barnes-hut-case-profile second_arch_bounded
```

`default` remains the CLI default and preserves the full three-case canonical
profile.

`second_arch_bounded` makes the Goal2977 workaround first-class and auditable.
It lets a second-architecture packet finish the seven-harness run without
silently pretending that the 8192-body Embree baseline was measured on that
machine.

## Why This Is Acceptable

Goal2977 already measured the bounded Barnes-Hut rows on RTX 4000 Ada:

| Bodies | Embree total median sec | OptiX total median sec | OptiX total speedup | Rows match |
| ---: | ---: | ---: | ---: | --- |
| 512 | `3.041` | `0.506` | `6.009x` | true |
| 2048 | `59.564` | `3.802` | `15.668x` | true |

The missing 8192 row is a CPU-baseline practicality issue, not an OptiX/RTDL
correctness failure. The bounded profile preserves that distinction in the
machine-readable runner output.

## Boundary

Goal2984 does not authorize:

- v2.5 release or release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- Triton preview auto-selection;
- paper reproduction claims;
- app-specific native engine customization.

Before any release packet uses the bounded profile, the release text must state
which architectures use the full Barnes-Hut profile and which use the bounded
second-architecture profile. External reviewers must then decide whether that
scope is acceptable.

## Validation

```text
PYTHONPATH=src;. py -3 -m py_compile scripts\goal2855_v2_5_current_canonical_harness_packet_runner.py src\rtdsl\v2_5_internal_readiness.py tests\goal2984_barnes_hut_second_arch_profile_policy_test.py
PYTHONPATH=src;. py -3 -m unittest tests.goal2984_barnes_hut_second_arch_profile_policy_test tests.goal2855_v2_5_current_canonical_harness_packet_runner_test tests.goal2983_claude_review_intake_goal2981_v2_5_closeout_test tests.goal2982_gemini_review_intake_goal2981_v2_5_closeout_test tests.goal2806_v2_5_internal_readiness_packet_test
```
